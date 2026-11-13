"""SQLAlchemy models.

The embedding column uses a portable fallback: pgvector's ``Vector`` type on
PostgreSQL and a JSON-encoded ``TEXT`` column on SQLite. This keeps the demo
runnable without a database server while still using real pgvector in
production (see ``database/schema.sql``).
"""

from datetime import datetime, timezone

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    LargeBinary,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base, is_postgres

# ---------------------------------------------------------------------------
# Portable embedding column type
# ---------------------------------------------------------------------------
if is_postgres():  # pragma: no cover - exercised only against PostgreSQL
    from pgvector.sqlalchemy import Vector

    from .config import settings

    EmbeddingType = Vector(settings.embedding_dim)
else:
    EmbeddingType = JSON


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Admin(Base):
    """College staff account. Admin credentials are never shown in the UI."""

    __tablename__ = "admins"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255))
    hashed_password: Mapped[str] = mapped_column(String(255))
    # Role-based access: "admin" may upload/publish, "viewer" may only read.
    role: Mapped[str] = mapped_column(String(32), default="admin")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)


class Student(Base):
    """Student account created through the public sign-up page."""

    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255))
    hashed_password: Mapped[str] = mapped_column(String(255))
    programme: Mapped[str | None] = mapped_column(String(64))
    semester: Mapped[str | None] = mapped_column(String(16))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)


class KnowledgeVersion(Base):
    """A snapshot of the approved knowledge base.

    Publishing a document creates/updates a version and re-indexes it. Only one
    version is ``is_active`` at a time; the previous one is retired so that the
    working information is never removed before its replacement is ready.
    """

    __tablename__ = "knowledge_versions"

    id: Mapped[int] = mapped_column(primary_key=True)
    label: Mapped[str] = mapped_column(String(64), unique=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)

    documents: Mapped[list["Document"]] = relationship(back_populates="knowledge_version")


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    # Document ID exposed in metadata (stable, human-readable).
    doc_uid: Mapped[str] = mapped_column(String(64), unique=True, index=True)

    title: Mapped[str] = mapped_column(String(255), index=True)
    category: Mapped[str] = mapped_column(String(64), index=True)  # Admissions/Fees/...
    doc_type: Mapped[str] = mapped_column(String(32), default="pdf")  # pdf | faq

    # Retrieval metadata
    programme: Mapped[str | None] = mapped_column(String(64), index=True)
    academic_year: Mapped[str | None] = mapped_column(String(32))
    semester: Mapped[str | None] = mapped_column(String(16), index=True)
    subject: Mapped[str | None] = mapped_column(String(128), index=True)
    publication_date: Mapped[str | None] = mapped_column(String(32))
    effective_date: Mapped[str | None] = mapped_column(String(32))
    expiry_date: Mapped[str | None] = mapped_column(String(32))
    version: Mapped[int] = mapped_column(Integer, default=1)
    source_page: Mapped[int | None] = mapped_column(Integer)

    # Lifecycle: draft | published | replaced | retired
    status: Mapped[str] = mapped_column(String(32), default="draft", index=True)
    replaces_document_id: Mapped[int | None] = mapped_column(ForeignKey("documents.id"))
    retired_at: Mapped[datetime | None] = mapped_column(DateTime)

    stored_path: Mapped[str | None] = mapped_column(String(512))
    content_hash: Mapped[str | None] = mapped_column(String(64))

    knowledge_version_id: Mapped[int | None] = mapped_column(
        ForeignKey("knowledge_versions.id"), index=True
    )
    knowledge_version: Mapped[KnowledgeVersion | None] = relationship(
        back_populates="documents"
    )

    uploaded_by_id: Mapped[int | None] = mapped_column(ForeignKey("admins.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)
    published_at: Mapped[datetime | None] = mapped_column(DateTime)

    passages: Mapped[list["Passage"]] = relationship(
        back_populates="document", cascade="all, delete-orphan"
    )

    @property
    def source_url(self) -> str | None:
        from .services.college_data import entry_for
        entry = entry_for(self.doc_uid)
        return entry['source']['url'] if entry else None

    @property
    def source_format(self) -> str:
        from .services.college_data import entry_for
        entry = entry_for(self.doc_uid)
        return entry['source']['format'] if entry else 'pdf'

    @property
    def checked_on(self) -> str | None:
        from .services.college_data import entry_for
        entry = entry_for(self.doc_uid)
        return entry['source']['checked_on'] if entry else None

    @property
    def source_status(self) -> str:
        from .services.retrieval import source_status
        return source_status(self)

    @property
    def is_sample_data(self) -> bool:
        return any('[SAMPLE DEMO DATA]' in p.content for p in self.passages)


class DocumentFile(Base):
    """Original uploaded PDF, retained when a cloud instance loses its files."""

    __tablename__ = "document_files"

    document_id: Mapped[int] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"), primary_key=True
    )
    filename: Mapped[str] = mapped_column(String(255))
    content: Mapped[bytes] = mapped_column(LargeBinary)


class Passage(Base):
    """An extracted, indexed chunk of a document."""

    __tablename__ = "passages"

    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"), index=True)
    page_number: Mapped[int] = mapped_column(Integer, default=1)
    ordinal: Mapped[int] = mapped_column(Integer, default=0)
    content: Mapped[str] = mapped_column(Text)
    # Embedding vector (pgvector on Postgres, JSON list on SQLite).
    embedding: Mapped[list | None] = mapped_column(EmbeddingType, nullable=True)

    document: Mapped[Document] = relationship(back_populates="passages")


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(primary_key=True)
    reference: Mapped[str] = mapped_column(String(32), unique=True, index=True)

    # Minimal personal information only.
    student_name: Mapped[str | None] = mapped_column(String(255))
    contact: Mapped[str | None] = mapped_column(String(255))

    category: Mapped[str] = mapped_column(String(64), index=True)
    programme: Mapped[str | None] = mapped_column(String(64))
    semester: Mapped[str | None] = mapped_column(String(16))
    subject: Mapped[str | None] = mapped_column(String(128))
    description: Mapped[str] = mapped_column(Text)
    related_document_id: Mapped[int | None] = mapped_column(ForeignKey("documents.id"))

    # open | pending | in_progress | resolved | closed
    status: Mapped[str] = mapped_column(String(32), default="open", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow, onupdate=_utcnow)

    messages: Mapped[list["TicketMessage"]] = relationship(
        back_populates="ticket", cascade="all, delete-orphan"
    )


class TicketMessage(Base):
    __tablename__ = "ticket_messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id"), index=True)
    author: Mapped[str] = mapped_column(String(32))  # student | staff
    body: Mapped[str] = mapped_column(Text)
    # Internal notes are never shown to the student.
    is_internal: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)

    ticket: Mapped[Ticket] = relationship(back_populates="messages")


class ChatLog(Base):
    """Stores questions and answer states for the "unanswered categories" metric."""

    __tablename__ = "chat_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    question: Mapped[str] = mapped_column(Text)
    category: Mapped[str | None] = mapped_column(String(64), index=True)
    answer_state: Mapped[str] = mapped_column(String(32), index=True)
    knowledge_version: Mapped[str | None] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)
