from uuid import uuid4
from sqlalchemy.orm import Session

from app.domain.models.attendance_record import AttendanceRecord
from app.infra.logging.logger import AppLogger


class AttendanceService:
    def __init__(self) -> None:
        self._logger = AppLogger(self.__class__.__name__)

    def clock_in(self, db: Session, employee_id: str, work_date: str, clock_in: str) -> dict:
        record = AttendanceRecord(
            record_id=str(uuid4()),
            employee_id=employee_id,
            work_date=work_date,
            clock_in=clock_in,
            status="normal",
        )
        db.add(record)
        db.commit()
        self._logger.info("clock_in", "考勤打卡成功", employee_id=employee_id, work_date=work_date)
        return {"recordId": record.record_id, "employeeId": employee_id, "workDate": work_date, "status": "normal"}

    def monthly_summary(self, db: Session, employee_id: str, month: str) -> dict:
        records = db.query(AttendanceRecord).filter(
            AttendanceRecord.employee_id == employee_id,
            AttendanceRecord.work_date.like(f"{month}%"),
        ).all()
        overtime = sum(r.overtime_minutes for r in records)
        return {"employeeId": employee_id, "month": month, "days": len(records), "overtimeMinutes": overtime}
