"""Pydantic request/response schemas (API contract)."""

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

# ---------------------------------------------------------------------------
# Shared enums
# ---------------------------------------------------------------------------
Category = Literal[
    "Admissions", "Fees", "Examinations", "Timetables", "College activities"
]
AnswerState = Literal["answered", "needs_context", "escalated"]
DocumentStatus = Literal["draft", "published", "replaced", "retired"]
TicketStatus = Literal["open", "pending", "in_progress", "resolved", "closed"]


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------
class AdminLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AdminOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    full_name: str
    role: str


class StudentSignup(BaseModel):
    full_name: str = Field(min_length=2, max_length=255)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    programme: str | None = Field(default=None, max_length=64)
    semester: str | None = Field(default=None, max_length=16)


class StudentLogin(BaseModel):
    email: EmailStr
    password: str


class StudentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    full_name: str
    programme: str | None = None
    semester: str | None = None


class AuthToken(BaseModel):
    """Access token plus the signed-in account, so the UI can greet the user."""

    access_token: str
    token_type: str = "bearer"
    account: StudentOut


# ---------------------------------------------------------------------------
# Chat
# ---------------------------------------------------------------------------
class ChatContext(BaseModel):
    programme: str | None = None
    semester: str | None = None
    subject: str | None = None
    academic_year: str | None = None
    division: str | None = None
    exam_data_mode: Literal['college', 'demo'] = 'college'
    # Prior turns, e.g. [{"role": "student", "content": "When is my exam?"}]
    history: list[dict] = Field(default_factory=list)


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=1000)
    context: ChatContext = Field(default_factory=ChatContext)


class Citation(BaseModel):
    document_id: str
    document_title: str
    page: int
    publication_date: str | None = None
    effective_date: str | None = None
    expiry_date: str | None = None
    version: int
    status: DocumentStatus
    source_status: Literal["current", "replaced", "expired", "conflicting", "historical", "snapshot", "custom", "demo"]
    category: str
    # Short quoted excerpt that supports the answer (never fabricated).
    excerpt: str
    open_url: str
    source_format: str = "pdf"
    checked_on: str | None = None
    is_sample_data: bool = False


class ChatResponse(BaseModel):
    state: AnswerState
    answer: str
    clarification_question: str | None = None
    citations: list[Citation] = Field(default_factory=list)
    knowledge_version: str | None = None
    category: str | None = None
    # True when the answer is based on synthetic demo data.
    is_sample_data: bool = True
    ticket_suggested: bool = False
    data_origin: Literal['college', 'admin', 'demo'] | None = None


class ExamRow(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    subject: str = Field(min_length=1, max_length=128)
    exam_date: date
    start_time: str | None = Field(default=None, pattern=r'^([01]\d|2[0-3]):[0-5]\d$')
    venue: str | None = Field(default=None, max_length=128)
    aliases: list[str] = Field(default_factory=list, max_length=10)

    @field_validator('aliases')
    @classmethod
    def limit_aliases(cls, aliases):
        if any(not alias.strip() or len(alias) > 64 for alias in aliases):
            raise ValueError('Each subject alias must contain 1 to 64 characters.')
        return aliases


class ExamTimetableIn(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    programme: str = Field(min_length=1, max_length=64)
    semester: str = Field(pattern=r'^[1-8]$')
    academic_year: str = Field(pattern=r'^20\d{2}-\d{2}$')
    division: str | None = Field(default=None, max_length=32)
    exam_kind: Literal['end_sem', 'in_sem', 'practical', 'retest'] = 'end_sem'
    rows: list[ExamRow] = Field(min_length=1, max_length=100)

    @field_validator('academic_year')
    @classmethod
    def consecutive_years(cls, value):
        if (int(value[:4]) + 1) % 100 != int(value[-2:]):
            raise ValueError('Use a consecutive academic year, such as 2026-27.')
        return value


# ---------------------------------------------------------------------------
# Documents
# ---------------------------------------------------------------------------
class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    doc_uid: str
    title: str
    category: str
    doc_type: str
    programme: str | None = None
    academic_year: str | None = None
    semester: str | None = None
    subject: str | None = None
    publication_date: str | None = None
    effective_date: str | None = None
    expiry_date: str | None = None
    version: int
    source_page: int | None = None
    status: str
    replaces_document_id: int | None = None
    knowledge_version_id: int | None = None
    created_at: datetime
    published_at: datetime | None = None
    source_url: str | None = None
    source_status: str = "current"
    source_format: str = "pdf"
    checked_on: str | None = None
    is_sample_data: bool = False


class DocumentMetadata(BaseModel):
    """Metadata accepted alongside a document upload."""

    title: str = Field(min_length=3, max_length=255)
    category: Category
    doc_type: Literal["pdf", "faq"] = "pdf"
    programme: str | None = None
    academic_year: str | None = None
    semester: str | None = None
    subject: str | None = None
    publication_date: str | None = None
    effective_date: str | None = None
    expiry_date: str | None = None
    source_page: int | None = None
    replaces_document_id: int | None = None
    body: str | None = Field(
        default=None, description="Raw text for FAQ documents (no file upload)."
    )


class PassageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    page_number: int
    ordinal: int
    content: str


class DocumentDetail(DocumentOut):
    passages: list[PassageOut] = Field(default_factory=list)
    source_status: str = "current"


class ReindexResult(BaseModel):
    document_id: str
    passages_indexed: int
    knowledge_version: str
    message: str


# ---------------------------------------------------------------------------
# Tickets
# ---------------------------------------------------------------------------
class TicketCreate(BaseModel):
    student_name: str | None = Field(default=None, max_length=255)
    contact: str | None = Field(default=None, max_length=255)
    category: Category | str = "College activities"
    programme: str | None = None
    semester: str | None = None
    subject: str | None = None
    description: str = Field(min_length=5, max_length=4000)
    related_document_id: int | None = None


class TicketMessageCreate(BaseModel):
    body: str = Field(min_length=1, max_length=4000)
    is_internal: bool = False


class TicketMessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    author: str
    body: str
    is_internal: bool
    created_at: datetime


class TicketOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    reference: str
    student_name: str | None = None
    contact: str | None = None
    category: str
    programme: str | None = None
    semester: str | None = None
    subject: str | None = None
    description: str
    related_document_id: int | None = None
    status: str
    created_at: datetime
    updated_at: datetime


class TicketDetail(TicketOut):
    messages: list[TicketMessageOut] = Field(default_factory=list)


class TicketStatusUpdate(BaseModel):
    status: TicketStatus


# ---------------------------------------------------------------------------
# Admin overview
# ---------------------------------------------------------------------------
class OverviewStats(BaseModel):
    total_notices: int
    published_notices: int
    replaced_notices: int
    pending_tickets: int
    resolved_tickets: int
    unanswered_categories: dict[str, int]
    active_knowledge_version: str | None = None
    # Always true in the demo build: metrics come from the local sample store.
    is_sample_data: bool = True
