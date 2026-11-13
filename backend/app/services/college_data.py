"""Reviewed JSCOE FAQs and provenance; no network request on the chat path."""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Document
from . import documents as ingestion, publishing

DATA_PATH = Path(__file__).resolve().parents[1] / 'data' / 'jscoe_knowledge.json'


@lru_cache
def knowledge_pack() -> dict:
    return json.loads(DATA_PATH.read_text(encoding='utf-8'))


@lru_cache
def entries_by_id() -> dict[str, dict]:
    return {entry['id']: entry for entry in knowledge_pack()['entries']}


def entry_for(doc_uid: str) -> dict | None:
    return entries_by_id().get(doc_uid)


def canonical_programme(value: str | None) -> str | None:
    if not value or not value.strip():
        return None
    clean = re.sub(r'[^a-z0-9]', '', value.lower())
    if clean in {'be', 'btech', 'fe', 'fybtech', 'firstyear', 'firstyearengineering',
                 'computerengineering', 'informationtechnology', 'electricalengineering',
                 'mechanicalengineering', 'entc', 'electronicsandtelecommunication',
                 'artificialintelligenceanddatascience'}:
        return 'B.Tech'
    if clean in {'me', 'mtech', 'masterofengineering'}:
        return 'M.E'
    if clean in {'mba', 'mca'}:
        return clean.upper()
    return value.strip()


def inferred_context(question: str, context: dict) -> dict:
    """Read explicit programme/year/semester words; never assume a student profile."""
    result = {**context, 'programme': canonical_programme(context.get('programme'))}
    q = question.lower()
    programmes = [
        ('MBA', r'\bmba\b'), ('MCA', r'\bmca\b'),
        ('M.E', r'\bm\s*\.?\s*(?:e|tech)\b'),
        ('B.Tech', r'\bb\s*\.?\s*(?:e|tech)\b|\bf\.?\s*y\.?\s*b\.?\s*tech\b|'
                   r'\bfirst[ -]year\b|\bfe\b|\b(?:computer|electrical|mechanical) engineering\b|'
                   r'\binformation technology\b|\bentc\b'),
    ]
    for programme, pattern in programmes:
        if re.search(pattern, q):
            result['programme'] = programme
            break
    year = re.search(r'\b(20\d{2})\s*[-/–]\s*(20\d{2}|\d{2})\b', q)
    if year:
        result['academic_year'] = f'{year[1]}-{year[2][-2:]}'
    elif re.search(r'\b20\d{2}\b', q) and 'fee' in q:
        # A fee query explicitly naming another year must not get the bundled year.
        start = re.search(r'\b(20\d{2})\b', q)[1]
        result['academic_year'] = f'{start}-{(int(start) + 1) % 100:02d}'
    sem = re.search(r'\bsem(?:ester)?\s*[-:]?\s*([1-8])\b', q)
    if sem:
        result['semester'] = sem[1]
    from .exam_rules import enrich_exam_context
    return enrich_exam_context(question,result)


def missing_college_context(question: str, category: str | None, context: dict) -> list[str]:
    q = question.lower()
    if category == 'Fees' and not context.get('programme'):
        if not re.search(r'\b(structure|all programmes|all programs|overview)\b', q):
            return ['programme']
    if category == 'Examinations' and re.search(r'\bmy (?:exam|paper)\b', q):
        return [key for key in ['programme', 'semester'] if not context.get(key)]
    return []


def faq_covers_request(entry: dict, question: str) -> bool:
    """Do not match an unsupported detail just because a caveat mentions it."""
    q = question.lower()
    if entry['category'] == 'Fees' and re.search(
        r'\b(hostel|bus|transport|mess|laundry|refund|instalment|installment|deadline|balance|outstanding)\b', q
    ):
        return False
    if entry['source']['format'] == 'image' and re.search(
        r'\b(room|hall|venue|time|timing|clock|mathematics|physics|chemistry|weekly)\b|\bwhere\b.*\bclass\b|\bnext class\b', q
    ):
        return False
    return True


def seed_jscoe_data(db: Session, *, refresh: bool = False) -> dict:
    """Import once on startup. Retain tickets, accounts and staff-authored notices.

    Staff retirements/edits are preserved on subsequent startups. ``refresh`` is
    an explicit CLI operation for a newly reviewed pack, not an automatic fetch.
    """
    from .seed import SAMPLE_NOTICES, SAMPLE_TAG, seed_admin

    admin = seed_admin(db)
    version = publishing.ensure_active_version(db)
    db.commit()
    created = []
    for entry in knowledge_pack()['entries']:
        document = db.scalar(select(Document).where(Document.doc_uid == entry['id']))
        if document is not None and not refresh:
            continue
        if document is None:
            document = Document(doc_uid=entry['id'], title=entry['title'],
                category=entry['category'], doc_type='faq', version=1, status='draft',
                uploaded_by_id=admin.id if admin else None)
            db.add(document)
        else:
            document.version += 1
        document.title = entry['title']
        document.programme = entry['programme']
        document.semester = entry['semester']
        document.academic_year = entry['academic_year']
        document.source_page = entry['source']['page']
        document.knowledge_version_id = version.id
        db.flush()
        ingestion.index_document(db, document, [(1, entry['answer'])])
        publishing.publish_document(db, document)
        created.append(document.doc_uid)

    # Only recognise the exact, tagged demo fixtures. No user document is deleted.
    sample_titles = {entry['meta']['title'] for entry in SAMPLE_NOTICES}
    for document in db.scalars(select(Document).where(Document.title.in_(sample_titles))):
        if any(SAMPLE_TAG in p.content for p in document.passages):
            document.status = 'retired'
    db.commit()
    return {'dataset': 'jscoe', 'created_documents': created,
            'checked_on': knowledge_pack()['checked_on']}
