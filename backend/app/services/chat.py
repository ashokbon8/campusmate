"""Chat orchestration: the end-to-end student question workflow.

Sequence implemented here:

1. Receive the student question.
2. Identify the relevant category.
3. Check whether required context is missing.
4. Ask a clarification question when needed (state: ``needs_context``).
5. Retrieve approved, currently-applicable passages (hybrid search + filters).
6. Draft an answer strictly from the retrieved evidence.
7. Validate the answer against the evidence.
8. Return the answer with citations (state: ``answered``), or
9. Escalate unsupported / conflicting questions (state: ``escalated``).
"""

from __future__ import annotations

from datetime import date
import re

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import settings
from ..models import ChatLog, KnowledgeVersion
from ..schemas import ChatContext, ChatRequest, ChatResponse, Citation
from . import answer_policy as policy
from .llm import get_llm
from .retrieval import RetrievedPassage, retrieve, source_status
from .college_data import entry_for, inferred_context, missing_college_context

SAMPLE_DISCLAIMER = (
    "This answer is based on synthetic sample notices created for the CampusMate "
    "demonstration. Confirm every date, fee and examination detail with the "
    "official college notice."
)


def _active_version_label(db: Session) -> str | None:
    version = db.scalar(
        select(KnowledgeVersion).where(KnowledgeVersion.is_active.is_(True))
    )
    return version.label if version else None


def _build_citations(passages: list[RetrievedPassage]) -> list[Citation]:
    seen: set[tuple[str, int]] = set()
    citations: list[Citation] = []
    for p in passages:
        key = (p.document.doc_uid, p.page_number)
        if key in seen:
            continue
        seen.add(key)
        doc = p.document
        citations.append(
            Citation(
                document_id=doc.doc_uid,
                document_title=doc.title,
                page=p.page_number,
                publication_date=doc.publication_date,
                effective_date=doc.effective_date,
                expiry_date=doc.expiry_date,
                version=doc.version,
                status=doc.status,  # type: ignore[arg-type]
                source_status=source_status(doc),  # type: ignore[arg-type]
                category=doc.category,
                excerpt=p.content[:280],
                open_url=doc.source_url or f"/api/documents/{doc.doc_uid}/source",
                source_format=doc.source_format,
                checked_on=doc.checked_on,
                is_sample_data=doc.is_sample_data,
            )
        )
    return citations


def _detect_conflict(passages: list[RetrievedPassage]) -> bool:
    """Flag when strong, comparable evidence disagrees on dates/numbers.

    Only passages that (a) score close to the best match and (b) belong to the
    same metadata group (category/programme/semester/subject) are compared. Two
    unrelated notices in the same result set are not treated as a conflict.
    """
    if not passages:
        return False
    best = passages[0].score
    strong = [p for p in passages if p.score >= best * 0.7]

    groups: dict[tuple, dict[str, set[str]]] = {}
    for p in strong:
        doc = p.document
        key = (doc.category, doc.programme, doc.semester, doc.subject)
        groups.setdefault(key, {}).setdefault(doc.doc_uid, set()).update(
            policy.extract_checkable_tokens(p.content)
        )

    for docs in groups.values():
        if len(docs) < 2:
            continue
        token_sets = list(docs.values())
        for i in range(len(token_sets)):
            for j in range(i + 1, len(token_sets)):
                if token_sets[i] ^ token_sets[j]:
                    return True
    return False


def answer_question(db: Session, request: ChatRequest) -> ChatResponse:
    question = request.question.strip()
    ctx = request.context
    context = {
        "programme": ctx.programme,
        "semester": ctx.semester,
        "subject": ctx.subject,
        "academic_year": ctx.academic_year,
        "division": ctx.division,
        "exam_data_mode": ctx.exam_data_mode,
    }
    sample_mode = settings.campusmate_dataset == 'demo'
    if not sample_mode:
        context = inferred_context(question, context)
    version_label = _active_version_label(db)

    # 2. Category detection ---------------------------------------------------
    category = policy.detect_category(question)

    if not sample_mode or ctx.exam_data_mode == 'demo':
        from .exams import answer_exam_question
        exam_response = answer_exam_question(db,question,context,version_label)
        if exam_response is not None:
            _log(db,question,'Examinations',exam_response.state,version_label)
            return exam_response

    # 3. Missing context ------------------------------------------------------
    missing = (policy.missing_context(category, context) if sample_mode
               else missing_college_context(question, category, context))
    if missing:
        response = ChatResponse(
            state="needs_context",
            answer=(
                "I can help with that, but I need a little more information "
                "before I look for the right notice."
            ),
            clarification_question=policy.build_clarification(category, missing),
            citations=[],
            knowledge_version=version_label,
            category=category,
            is_sample_data=sample_mode,
            ticket_suggested=False,
        )
        _log(db, question, category, response.state, version_label)
        return response

    # 5. Retrieval ------------------------------------------------------------
    retrieval_question = question
    if not sample_mode and category == 'Examinations' and context['subject']:
        # The calendar's broad exam window cannot answer an individual paper date.
        if not re.search(r'\b(window|calendar|end.sem|general)\b', question.lower()):
            retrieval_question += ' ' + context['subject']
    passages = retrieve(
        db,
        retrieval_question,
        category=category,
        programme=context["programme"],
        semester=context["semester"],
        subject=context["subject"],
        academic_year=context["academic_year"],
    )

    # 9a. No evidence -> escalate --------------------------------------------
    if not passages:
        response = ChatResponse(
            state="escalated",
            answer=(
                "I could not find an approved notice that answers this question. "
                "I will not guess. You can raise a helpdesk ticket and the right "
                "office will follow up."
            ),
            clarification_question=None,
            citations=[],
            knowledge_version=version_label,
            category=category,
            is_sample_data=sample_mode,
            ticket_suggested=True,
        )
        _log(db, question, category, response.state, version_label)
        return response

    # Curated FAQs contain a complete, reviewed answer. Do not reduce a checklist
    # to a single sentence or compare unrelated calendar events as conflicting.
    entry = entry_for(passages[0].document.doc_uid)
    conflict_candidates = ([p for p in passages if not entry_for(p.document.doc_uid)
                            or p.document.doc_uid == passages[0].document.doc_uid]
                           if entry else passages)
    if _detect_conflict(conflict_candidates):
        response = ChatResponse(
            state='escalated',
            answer='The sources appear to disagree. Please ask the college office or raise a ticket for confirmation.',
            citations=_build_citations(conflict_candidates), knowledge_version=version_label,
            category=category, is_sample_data=any(p.document.is_sample_data for p in conflict_candidates),
            ticket_suggested=True,
        )
        _log(db, question, category, response.state, version_label)
        return response
    if entry:
        passages = passages[:1]
        archival_deadline = entry['source']['historical'] and bool(re.search(
            r'deadline|last date|when.*(?:form|fill)|hall.ticket|my exam|my paper|\bdate\b|\btime\b', question.lower()))
        response = ChatResponse(
            state='escalated' if archival_deadline else 'answered',
            answer=passages[0].content,
            citations=_build_citations(passages),
            knowledge_version=version_label, category=passages[0].document.category,
            is_sample_data=False, ticket_suggested=archival_deadline,
        )
        _log(db, question, category, response.state, version_label)
        return response

    # 6. Draft from evidence --------------------------------------------------
    evidence = [p.content for p in passages]
    llm = get_llm()
    draft = llm.draft_answer(question, evidence)

    # 7. Validate against evidence -------------------------------------------
    if not draft or not policy.answer_supported_by_evidence(draft, evidence):
        response = ChatResponse(
            state="escalated",
            answer=(
                "The approved notices I found do not clearly support a specific "
                "answer, so I will not invent one. Please raise a helpdesk ticket "
                "for a confirmed response."
            ),
            clarification_question=None,
            citations=_build_citations(passages),
            knowledge_version=version_label,
            category=category,
            is_sample_data=any(p.document.is_sample_data for p in passages),
            ticket_suggested=True,
        )
        _log(db, question, category, response.state, version_label)
        return response

    # 8. Answered -------------------------------------------------------------
    response = ChatResponse(
        state="answered",
        answer=draft,
        clarification_question=None,
        citations=_build_citations(passages),
        knowledge_version=version_label,
        category=category,
        is_sample_data=any(p.document.is_sample_data for p in passages),
        ticket_suggested=False,
    )
    _log(db, question, category, response.state, version_label)
    return response


def _log(
    db: Session, question: str, category: str | None, state: str, version: str | None
) -> None:
    db.add(
        ChatLog(
            question=question[:1000],
            category=category,
            answer_state=state,
            knowledge_version=version,
        )
    )
    db.commit()
