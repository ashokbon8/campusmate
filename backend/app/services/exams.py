"""Exact admin-entered dates, explicit demo examples, and scoped calendar help."""
import json
import re
import uuid
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Admin, Document, KnowledgeVersion
from ..schemas import ChatResponse, Citation, ExamTimetableIn
from . import documents as ingestion, publishing
from .college_data import canonical_programme
from .exam_rules import canonical_subject, exam_data, exam_kind, is_exam_date_question, subject_matches, words


def load_timetable(document: Document) -> dict | None:
    try:
        data = json.loads(''.join(p.content for p in sorted(document.passages,key=lambda p:p.ordinal)))
        return data if data.get('kind') == 'exam_timetable' else None
    except (ValueError, TypeError, AttributeError):
        return None


def current_timetables(db: Session) -> list[tuple[Document, dict]]:
    active = db.scalar(select(KnowledgeVersion).where(KnowledgeVersion.is_active.is_(True)))
    stmt = select(Document).where(Document.doc_type == 'exam',Document.status == 'published')
    if active:
        stmt = stmt.where(Document.knowledge_version_id == active.id)
    result = []
    for document in db.scalars(stmt):
        data = load_timetable(document)
        if data:
            result.append((document,data))
    return result


def timetable_details(document: Document, data: dict) -> dict:
    return {**data,'document_id':document.id,'doc_uid':document.doc_uid,'version':document.version,'status':document.status}


def save_timetable(db: Session, payload: ExamTimetableIn, admin: Admin) -> dict:
    data = payload.model_dump(mode='json')
    data['programme'] = canonical_programme(data['programme'])
    data['division'] = (data['division'] or '').strip().upper() or None
    seen = set()
    for row in data['rows']:
        row['subject'] = canonical_subject(row['subject'],data['semester']) or row['subject']
        key = words(canonical_subject(row['subject'],data['semester']) or row['subject'])
        if key in seen:
            raise ValueError('Each subject may appear only once in a timetable.')
        seen.add(key)
    scope = ('programme','semester','academic_year','division','exam_kind')
    previous = next((doc for doc,old in current_timetables(db) if all(old.get(k)==data.get(k) for k in scope)),None)
    data.update(kind='exam_timetable',is_demo=False,
        title=f"Admin timetable — {data['programme']} Semester {data['semester']} {data['academic_year']}")
    document = Document(doc_uid='exam-'+uuid.uuid4().hex[:12],title=data['title'],category='Examinations',
        doc_type='exam',programme=data['programme'],semester=data['semester'],academic_year=data['academic_year'],
        version=previous.version+1 if previous else 1,status='draft',source_page=1,
        publication_date=date.today().isoformat(),uploaded_by_id=admin.id,
        replaces_document_id=previous.id if previous else None)
    db.add(document)
    db.flush()
    ingestion.index_document(db,document,[(1,json.dumps(data,ensure_ascii=False))])
    publishing.publish_document(db,document,replace_document=previous)
    return timetable_details(document,data)


def pretty_date(value: str) -> str:
    return date.fromisoformat(value).strftime('%d %B %Y').lstrip('0')


def format_row(row: dict) -> str:
    text = f"{row['subject']}: {pretty_date(row['exam_date'])}"
    if row.get('start_time'):
        hour,minute = (int(part) for part in row['start_time'].split(':')[:2])
        text += f" at {hour % 12 or 12}:{minute:02d} {'AM' if hour < 12 else 'PM'}"
    if row.get('venue'):
        text += f" — {row['venue']}"
    return text


def timetable_lines(data: dict) -> list[str]:
    tag = 'DEMO: INVENTED EXAMPLE DATES — NOT A COLLEGE NOTICE' if data.get('is_demo') else 'CUSTOM TIMETABLE — ENTERED BY A CAMPUSMATE ADMINISTRATOR'
    scope = f"{data['programme']} | Semester {data['semester']} | Academic year {data['academic_year']}"
    if data.get('division'): scope += f" | Division {data['division']}"
    return [tag,scope,*[format_row(row) for row in sorted(data['rows'],key=lambda row:row['exam_date'])]]


def citation_for(document: Document, text: str, *, custom=False) -> Citation:
    return Citation(document_id=document.doc_uid,document_title=document.title,page=1,
        publication_date=document.publication_date,version=document.version,status=document.status,
        source_status='custom' if custom else document.source_status,category='Examinations',excerpt=text[:280],
        open_url=document.source_url or f'/api/documents/{document.doc_uid}/source',source_format=document.source_format,
        checked_on=document.checked_on,is_sample_data=False)


def matches_scope(data: dict, context: dict) -> bool:
    for key in ['programme','semester','academic_year','division']:
        wanted = context.get(key)
        if not wanted:
            continue
        actual = data.get(key)
        if key == 'programme':
            if canonical_programme(actual) != canonical_programme(wanted): return False
        elif key == 'division':
            if actual and actual.upper() != wanted.upper(): return False
        elif actual != wanted:
            return False
    return True


def answer_exam_question(db: Session, question: str, context: dict, version: str | None) -> ChatResponse | None:
    if not is_exam_date_question(question):
        return None
    demo = context.get('exam_data_mode') == 'demo'
    kind = exam_kind(question)
    base = dict(category='Examinations',knowledge_version=version,is_sample_data=demo,ticket_suggested=False,
                data_origin='demo' if demo else 'college')
    schedules = [(None,table) for table in exam_data()['demo_timetables']] if demo else current_timetables(db)
    schedules = [(doc,table) for doc,table in schedules if table.get('exam_kind') == kind and matches_scope(table,context)]
    if schedules:
        # Ask for a scope that distinguishes timetables; never silently choose a class/year.
        ambiguous = [key for key in ['programme','semester','academic_year','division']
                     if not context.get(key) and len({table.get(key) for _,table in schedules}) > 1]
        if ambiguous:
            return ChatResponse(**base,state='needs_context',answer='I found more than one matching exam timetable.',
                clarification_question='Please tell me your '+', '.join(ambiguous)+'.')
        document, table = schedules[0]
        direct = [row for row in table['rows'] if subject_matches(row['subject'],None,question,row.get('aliases'))]
        requested = context.get('requested_subjects') or ([context['subject']] if context.get('subject') else [])
        selected = [row for row in table['rows'] if any(subject_matches(row['subject'],subject,aliases=row.get('aliases')) for subject in requested)] or direct
        all_subjects = bool(re.search(r'\ball\b|\btimetable\b|\bschedule\b|\bexams\b|\bexaminations\b',question.lower()))
        if not selected and not requested and all_subjects:
            selected = table['rows']
        if selected:
            origin = 'DEMO — fictional example dates. These are NOT official college exam dates.' if demo else 'According to the timetable entered by your CampusMate administrator:'
            scope = f"{table['programme']}, Semester {table['semester']}, AY {table['academic_year']}"
            if table.get('division'): scope += f", Division {table['division']}"
            body = '\n'.join(format_row(row) for row in sorted(selected,key=lambda row:row['exam_date']))
            answer = f'{origin}\n{scope}\n\n{body}'
            if demo:
                citations = [Citation(document_id=table['id'],document_title=table['title'],page=1,version=1,
                    status='published',source_status='demo',category='Examinations',excerpt=body[:280],
                    open_url='/demo-exam-timetable.html',source_format='html',is_sample_data=True)]
            else:
                citations = [citation_for(document,body,custom=True)]
                base['data_origin'] = 'admin'
            return ChatResponse(**base,state='answered',answer=answer,citations=citations)
        if demo:
            return ChatResponse(**base,state='needs_context',answer='That subject is not in the selected demo timetable.',
                clarification_question='Choose a subject from the demo table, or ask for all exam dates.')

    # Existing staff PDF/FAQ notices can supply an exact date too. Match subject
    # aliases in metadata, retaining every version/year/semester filter.
    if not demo and context.get('subject'):
        from .retrieval import retrieve
        from .college_data import entry_for
        exact = [p for p in retrieve(db,f"{context['subject']} exam",category='Examinations',
                    programme=context.get('programme'),semester=context.get('semester'),
                    subject=context.get('subject'),academic_year=context.get('academic_year'))
                 if not entry_for(p.document.doc_uid) and p.document.doc_type != 'exam'
                 and p.document.subject and canonical_subject(p.document.subject,p.document.semester) == canonical_subject(context['subject'],context.get('semester'))
                 and not p.document.is_sample_data]
        if exact:
            scopes = {(p.document.programme,p.document.semester,p.document.academic_year) for p in exact}
            if len(scopes) == 1:
                # Different dates in comparable current notices require clarification.
                from .chat import _detect_conflict
                if _detect_conflict(exact):
                    return ChatResponse(**base,state='needs_context',answer='The current subject notices disagree.',
                        clarification_question='Please check the latest authorised timetable with the examination office.',
                        citations=[citation_for(p.document,p.content) for p in exact])
                passage = exact[0]
                return ChatResponse(**base,state='answered',answer=passage.content,
                    citations=[citation_for(passage.document,passage.content)])

    if demo:
        return ChatResponse(**base,state='needs_context',answer='The sample contains B.Tech first-year Semester 1 and 2 example dates.',
            clarification_question='Select B.Tech, Semester 1 or 2, academic year 2026-27, then choose a subject.')

    # The real calendar supplies a window only, never a specific paper date.
    uid = {'end_sem':'jscoe-calendar-endsem','practical':'jscoe-calendar-practical','retest':'jscoe-calendar-retest'}.get(kind)
    document = None
    if uid:
        stmt = select(Document).where(Document.doc_uid == uid,Document.status == 'published')
        active = db.scalar(select(KnowledgeVersion).where(KnowledgeVersion.is_active.is_(True)))
        if active:
            stmt = stmt.where(Document.knowledge_version_id == active.id)
        document = db.scalar(stmt)
    citations = []
    answer = 'I do not have a published subject-wise timetable matching those details.'
    if document and matches_scope(dict(programme=document.programme,semester=document.semester,academic_year=document.academic_year,division=None),context):
        text = '\n'.join(p.content for p in document.passages)
        answer = f"For {document.programme}, Semester {document.semester}, AY {document.academic_year}:\n{text}\n"
        target = ', '.join(context.get('requested_subjects') or [context.get('subject') or 'each subject'])
        answer += f'The exact paper date/time for {target} is not specified in this calendar. It must come from a subject-wise timetable.'
        citations = [citation_for(document,text)]
    missing = [key for key in ['programme','semester','academic_year'] if not context.get(key)]
    if document and citations and not context.get('subject') and not re.search(r'\bmy\b',question.lower()):
        missing = []  # A general calendar question can receive an explicitly scoped window.
    if missing:
        return ChatResponse(**base,state='needs_context',answer=answer,citations=citations,
            clarification_question='Please tell me your '+', '.join(missing)+' (for example: B.Tech, semester 1, 2026-27).')
    return ChatResponse(**base,state='answered',answer=answer+' Your admin can add exact dates in Admin Login → Exam timetable.',citations=citations)
