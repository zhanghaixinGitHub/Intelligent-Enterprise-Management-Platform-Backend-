from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies.security import CurrentUserContext, get_current_user
from app.infra.db.session import get_db
from app.domain.services.attendance_service import AttendanceService


router = APIRouter(prefix="/api/v1/attendance", tags=["attendance"])
attendance_service = AttendanceService()


@router.post("/clock-in")
def clock_in(
    workDate: str,
    clockIn: str,
    db: Session = Depends(get_db),
    current_user: CurrentUserContext = Depends(get_current_user),
):
    return attendance_service.clock_in(db, current_user.employeeId, workDate, clockIn)


@router.get("/monthly-summary")
def monthly_summary(
    month: str = Query(..., description="YYYY-MM"),
    db: Session = Depends(get_db),
    current_user: CurrentUserContext = Depends(get_current_user),
):
    return attendance_service.monthly_summary(db, current_user.employeeId, month)
