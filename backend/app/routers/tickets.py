"""Helpdesk ticket endpoints.

Students may create a ticket and read their own tickets (looked up by the
returned reference). Staff may list, filter, annotate, respond to and update
tickets. Internal notes are never exposed through the student-facing lookup.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Admin, Ticket, TicketMessage
from ..schemas import (
    TicketCreate,
    TicketDetail,
    TicketMessageCreate,
    TicketMessageOut,
    TicketOut,
    TicketStatusUpdate,
)
from ..security import get_current_admin

router = APIRouter(tags=["tickets"])


def _reference() -> str:
    return f"CM-{uuid.uuid4().hex[:6].upper()}"


@router.post("/tickets", response_model=TicketOut, status_code=201)
def create_ticket(payload: TicketCreate, db: Session = Depends(get_db)) -> Ticket:
    ticket = Ticket(
        reference=_reference(),
        student_name=payload.student_name,
        contact=payload.contact,
        category=str(payload.category),
        programme=payload.programme,
        semester=payload.semester,
        subject=payload.subject,
        description=payload.description,
        related_document_id=payload.related_document_id,
        status="open",
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


@router.get("/tickets/{reference}", response_model=TicketDetail)
def get_ticket(reference: str, db: Session = Depends(get_db)) -> TicketDetail:
    """Student lookup by reference. Internal notes are filtered out."""
    ticket = db.scalar(select(Ticket).where(Ticket.reference == reference))
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    detail = TicketDetail.model_validate(ticket)
    detail.messages = [
        TicketMessageOut.model_validate(m)
        for m in ticket.messages
        if not m.is_internal
    ]
    return detail


# ---------------------------------------------------------------------------
# Admin
# ---------------------------------------------------------------------------
@router.get("/admin/tickets", response_model=list[TicketOut])
def list_tickets(
    status: str | None = Query(None),
    category: str | None = Query(None),
    db: Session = Depends(get_db),
    _: Admin = Depends(get_current_admin),
) -> list[Ticket]:
    stmt = select(Ticket)
    if status:
        stmt = stmt.where(Ticket.status == status)
    if category:
        stmt = stmt.where(Ticket.category == category)
    return list(db.scalars(stmt.order_by(Ticket.created_at.desc())))


@router.get("/admin/tickets/{ticket_id}", response_model=TicketDetail)
def admin_ticket_detail(
    ticket_id: int, db: Session = Depends(get_db), _: Admin = Depends(get_current_admin)
) -> TicketDetail:
    ticket = db.get(Ticket, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    detail = TicketDetail.model_validate(ticket)
    detail.messages = [TicketMessageOut.model_validate(m) for m in ticket.messages]
    return detail


@router.post(
    "/admin/tickets/{ticket_id}/messages", response_model=TicketMessageOut, status_code=201
)
def add_message(
    ticket_id: int,
    payload: TicketMessageCreate,
    db: Session = Depends(get_db),
    _: Admin = Depends(get_current_admin),
) -> TicketMessage:
    ticket = db.get(Ticket, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    message = TicketMessage(
        ticket_id=ticket.id,
        author="staff",
        body=payload.body,
        is_internal=payload.is_internal,
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


@router.patch("/admin/tickets/{ticket_id}", response_model=TicketOut)
def update_status(
    ticket_id: int,
    payload: TicketStatusUpdate,
    db: Session = Depends(get_db),
    _: Admin = Depends(get_current_admin),
) -> Ticket:
    ticket = db.get(Ticket, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    ticket.status = payload.status
    db.commit()
    db.refresh(ticket)
    return ticket
