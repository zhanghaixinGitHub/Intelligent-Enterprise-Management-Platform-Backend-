from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.infra.db.session import get_db
from app.domain.services.attendance_service import AttendanceService


router = APIRouter(prefix="/api/v1/attendance", tags=["attendance"])
attendance_service = AttendanceService()


@router.post("/clock-in")
def clock_in(employeeId: str, workDate: str, clockIn: str, db: Session = Depends(get_db)):
    return attendance_service.clock_in(db, employeeId, workDate, clockIn)


@router.get("/monthly-summary")
def monthly_summary(
    employeeId: str = Query(...),
    month: str = Query(..., description="YYYY-MM"),
    db: Session = Depends(get_db),
):
    return attendance_service.monthly_summary(db, employeeId, month)
