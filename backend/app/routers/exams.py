"""A class timetable editor; writes require an authenticated publisher."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Admin
from ..schemas import ExamTimetableIn
from ..security import get_current_admin, require_publisher
from ..services.exams import current_timetables, save_timetable, timetable_details

router = APIRouter(tags=['exam timetables'])


@router.get('/admin/exam-timetables')
def list_timetables(db: Session = Depends(get_db), _: Admin = Depends(get_current_admin)):
    return [timetable_details(document,data) for document,data in current_timetables(db)]


@router.post('/admin/exam-timetables',status_code=201)
def publish_timetable(payload: ExamTimetableIn,db: Session = Depends(get_db),admin: Admin = Depends(require_publisher)):
    try:
        return save_timetable(db,payload,admin)
    except ValueError as error:
        db.rollback()
        raise HTTPException(status_code=400,detail=str(error)) from error
