"""Synthetic demo seed data.

Everything created here is clearly-labelled SAMPLE data for the CampusMate
demonstration. It is never presented as real college information. Each notice is
generated as a real PDF (so the source viewer has a file to open), indexed, and
published into the active knowledge version.

The examination notice mirrors the example conversation from the presentation:
BSc CS, Semester 1, Mathematics -> 10 December 2026, 10:00 AM, Room 204, with
version 2 replacing version 1.
"""

from __future__ import annotations

import os

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import settings
from ..models import Admin, Document
from ..security import hash_password, verify_password
from . import documents as doc_service
from . import publishing
from .pdf_writer import build_pdf

SAMPLE_TAG = "[SAMPLE DEMO DATA]"


def _write_pdf(filename: str, lines: list[str]) -> str:
    os.makedirs(settings.upload_dir, exist_ok=True)
    path = os.path.join(settings.upload_dir, filename)
    with open(path, "wb") as fh:
        fh.write(build_pdf(lines, title=filename))
    return path


# (metadata, page text lines)
SAMPLE_NOTICES: list[dict] = [
    {
        "meta": {
            "title": "Admissions document checklist (sample)",
            "category": "Admissions",
            "programme": "BSc CS",
            "academic_year": "2026-27",
            "publication_date": "2026-10-28",
            "effective_date": "2026-10-28",
            "version": 1,
            "source_page": 1,
        },
        "lines": [
            SAMPLE_TAG + " This is not an official college document.",
            "Admissions document checklist",
            "Programme: BSc Computer Science | Academic year: 2026-27",
            "Documents required for admission:",
            "1. Class 12 marksheet and passing certificate",
            "2. Transfer certificate from the previous institute",
            "3. Migration certificate, if applicable",
            "4. Category or reservation certificate, if applicable",
            "5. Four recent passport-size photographs",
            "6. Government photo identity proof",
            "Submit the originals for verification and two photocopies of each.",
            "For queries contact the admissions office.",
        ],
    },
    {
        "meta": {
            "title": "Fee payment information (sample)",
            "category": "Fees",
            "programme": "BSc CS",
            "academic_year": "2026-27",
            "publication_date": "2026-10-22",
            "effective_date": "2026-10-22",
            "version": 1,
            "source_page": 1,
        },
        "lines": [
            SAMPLE_TAG + " This is not an official college document.",
            "Fee payment information",
            "Programme: BSc Computer Science | Academic year: 2026-27",
            "The semester fee can be paid in two instalments.",
            "The first instalment is due on 15 August 2026.",
            "The second instalment is due on 20 January 2027.",
            "Pay online through the college fee portal and keep the receipt.",
            "Late payment may attract a late fee as per college rules.",
            "Private individual fee balances are never shown in the public chatbot.",
            "For account-specific questions contact the accounts office.",
        ],
    },
    {
        "meta": {
            "title": "Sample Mathematics examination notice (superseded)",
            "category": "Examinations",
            "programme": "BSc CS",
            "semester": "1",
            "subject": "Mathematics",
            "publication_date": "2026-09-15",
            "effective_date": "2026-12-08",
            "version": 1,
            "source_page": 1,
        },
        "lines": [
            SAMPLE_TAG + " This is not an official college document.",
            "Mathematics examination notice (version 1)",
            "Programme: BSc Computer Science | Semester: 1 | Subject: Mathematics",
            "The Mathematics examination was scheduled for 08 December 2026 at 10:00 AM in Room 204. This version has been replaced by version 2.",
        ],
    },
    {
        "meta": {
            "title": "Sample Mathematics examination notice (current)",
            "category": "Examinations",
            "programme": "BSc CS",
            "semester": "1",
            "subject": "Mathematics",
            "publication_date": "2026-11-03",
            "effective_date": "2026-12-10",
            "version": 2,
            "source_page": 1,
        },
        "lines": [
            SAMPLE_TAG + " This is not an official college document.",
            "Mathematics examination notice (version 2 - current)",
            "Programme: BSc Computer Science | Semester: 1 | Subject: Mathematics",
            "The Mathematics examination will be held on 10 December 2026 at 10:00 AM in Room 204.",
            "This notice replaces version 1. Bring your hall ticket and student ID.",
        ],
    },
    {
        "meta": {
            "title": "Weekly timetable sample",
            "category": "Timetables",
            "programme": "BSc CS",
            "semester": "1",
            "publication_date": "2026-10-18",
            "effective_date": "2026-10-20",
            "version": 1,
            "source_page": 1,
        },
        "lines": [
            SAMPLE_TAG + " This is not an official college document.",
            "Weekly class timetable (sample)",
            "Programme: BSc Computer Science | Semester: 1",
            "Monday: Mathematics 09:00 AM Room 204",
            "Monday: Programming Lab 11:00 AM Lab 3",
            "Tuesday: Physics 09:00 AM Room 201",
            "Wednesday: Mathematics 10:00 AM Room 204",
            "Thursday: English 09:00 AM Room 105",
            "Friday: Programming Lab 02:00 PM Lab 3",
            "Always confirm room changes on the official noticeboard.",
        ],
    },
    {
        "meta": {
            "title": "Campus activity registration (sample)",
            "category": "College activities",
            "programme": None,
            "publication_date": "2026-10-12",
            "effective_date": "2026-10-12",
            "version": 1,
            "source_page": 1,
        },
        "lines": [
            SAMPLE_TAG + " This is not an official college document.",
            "Campus activity registration",
            "How to register for an event:",
            "1. Open the student activities portal and sign in.",
            "2. Choose the event you want to attend.",
            "3. Fill the registration form and confirm your details.",
            "4. Collect your participation pass from the activity desk.",
            "Eligibility varies by event. Check each event notice for who can join.",
        ],
    },
]


def seed_admin(db: Session) -> Admin | None:
    """Create the seeded administrator from configuration (private, no UI hint).

    Returns ``None`` when ``SEED_ADMIN_PASSWORD`` is empty, so a deployment can
    start with no built-in admin at all. The stored password is refreshed to the
    configured value when it no longer matches, so rotating the secret in the
    hosting environment (e.g. Vercel) takes effect on the next start.
    """
    email = settings.seed_admin_email.strip()
    password = settings.seed_admin_password
    if not email or not password:
        return None

    existing = db.scalar(select(Admin).where(Admin.email == email))
    if existing:
        if not verify_password(password, existing.hashed_password):
            existing.hashed_password = hash_password(password)
        return existing

    admin = Admin(
        email=email,
        full_name=settings.seed_admin_name,
        hashed_password=hash_password(password),
        role="admin",
    )
    db.add(admin)
    db.flush()
    return admin


def seed_demo_data(db: Session) -> dict:
    """Create admin, knowledge version and sample notices. Idempotent."""
    admin = seed_admin(db)
    version = publishing.ensure_active_version(db)
    db.commit()

    created: list[str] = []

    for entry in SAMPLE_NOTICES:
        meta = entry["meta"]
        existing = db.scalar(
            select(Document).where(Document.title == meta["title"])
        )
        if existing:
            continue

        doc_type = meta.get("doc_type", "pdf")
        filename = meta["title"].replace(" ", "_").replace("(", "").replace(")", "")
        if doc_type == "pdf":
            filename = f"{filename}.pdf"
            path = _write_pdf(filename, entry["lines"])
            pages = doc_service.extract_pdf_pages(open(path, "rb").read())
        else:
            path = None
            pages = doc_service.extract_text_pages(meta.get("body", ""))

        replace_target = None
        if meta["category"] == "Examinations" and meta["version"] == 2:
            replace_target = db.scalar(
                select(Document).where(
                    Document.title == "Sample Mathematics examination notice (superseded)"
                )
            )

        document = Document(
            doc_uid=publishing.new_doc_uid(meta["category"]),
            title=meta["title"],
            category=meta["category"],
            doc_type=doc_type,
            programme=meta.get("programme"),
            academic_year=meta.get("academic_year"),
            semester=meta.get("semester"),
            subject=meta.get("subject"),
            publication_date=meta.get("publication_date"),
            effective_date=meta.get("effective_date"),
            expiry_date=meta.get("expiry_date"),
            version=meta["version"],
            source_page=meta.get("source_page"),
            status="draft",
            stored_path=path,
            knowledge_version_id=version.id,
            replaces_document_id=replace_target.id if replace_target else None,
            uploaded_by_id=admin.id if admin else None,
        )
        db.add(document)
        db.flush()
        doc_service.index_document(db, document, pages)
        db.flush()

        publishing.publish_document(db, document, replace_document=replace_target)
        created.append(document.doc_uid)

    return {
        "admin_email": admin.email if admin else None,
        "knowledge_version": version.label,
        "created_documents": created,
    }
