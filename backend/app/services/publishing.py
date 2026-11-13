"""Document publication and knowledge-version management.

Implements the replacement workflow from the presentation. Crucially, the new
index is fully built *before* it becomes active, and the previous notice is only
retired once the switch has succeeded, so working information is never removed
prematurely.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Document, KnowledgeVersion


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def ensure_active_version(db: Session) -> KnowledgeVersion:
    version = db.scalar(
        select(KnowledgeVersion).where(KnowledgeVersion.is_active.is_(True))
    )
    if version:
        return version
    version = KnowledgeVersion(
        label="kv-0001", is_active=True, notes="Initial knowledge version"
    )
    db.add(version)
    db.flush()
    return version


def next_version_label(db: Session) -> str:
    count = len(list(db.scalars(select(KnowledgeVersion.id))))
    return f"kv-{count + 1:04d}"


def create_staging_version(db: Session, notes: str = "") -> KnowledgeVersion:
    """Create a *staging* version that is not yet active."""
    version = KnowledgeVersion(
        label=next_version_label(db), is_active=False, notes=notes
    )
    db.add(version)
    db.flush()
    return version


def activate_version(db: Session, version: KnowledgeVersion) -> None:
    """Switch the active knowledge version and invalidate cached answers.

    Cache invalidation is represented by deactivating every other version; any
    answer cached against an inactive version is considered stale.
    """
    for other in db.scalars(select(KnowledgeVersion)):
        other.is_active = other.id == version.id
    db.flush()


def publish_document(
    db: Session, document: Document, *, replace_document: Document | None = None
) -> KnowledgeVersion:
    """Publish ``document`` and, when it replaces another, retire the old one.

    A knowledge version is a *snapshot of the whole approved set*, not a single
    document. Publishing an additional notice therefore joins the active set,
    while publishing a *replacement* creates a new snapshot that carries every
    other published notice forward. Steps for a replacement:

    1. Confirm the new document's index is ready (it has passages).
    2. Create the new (staging) knowledge version.
    3. Carry all other published notices into the staging version and add the
       new document, then confirm the index is ready.
    4. Switch the active version.
    5. Retire the previous notice.
    6. Invalidate cached answers (the old version is deactivated).
    """
    if not document.passages:
        raise ValueError("Document has no indexed passages; index is not ready.")

    if replace_document is None:
        # A brand-new notice simply joins the current knowledge set.
        active = ensure_active_version(db)
        document.knowledge_version_id = active.id
        document.status = "published"
        document.published_at = _utcnow()
        db.commit()
        db.refresh(document)
        return active

    # 2. New knowledge version (staging).
    staging = create_staging_version(
        db, notes=f"Published {document.doc_uid} (v{document.version})"
    )

    # 3. Carry every other published notice forward, then add the new document.
    others = list(
        db.scalars(
            select(Document).where(
                Document.status == "published",
                Document.id.notin_([document.id, replace_document.id]),
            )
        )
    )
    for other in others:
        other.knowledge_version_id = staging.id
    document.knowledge_version_id = staging.id
    document.status = "published"
    document.published_at = _utcnow()
    db.flush()

    # 4. Activate the new version only now that its index is ready.
    activate_version(db, staging)

    # 5. Retire the replaced notice.
    replace_document.status = "replaced"
    replace_document.retired_at = _utcnow()
    db.flush()

    db.commit()
    db.refresh(document)
    return staging


def new_doc_uid(category: str) -> str:
    slug = "".join(c for c in category.lower() if c.isalnum())[:6] or "doc"
    return f"{slug}-{uuid.uuid4().hex[:8]}"
