from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.models.base import BaseEntity


class AttendanceRecord(BaseEntity):
    __tablename__ = "attendance_records"

    record_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    employee_id: Mapped[str] = mapped_column(String(64), index=True)
    work_date: Mapped[str] = mapped_column(String(32), index=True)
    clock_in: Mapped[str] = mapped_column(String(32), default="")
    clock_out: Mapped[str] = mapped_column(String(32), default="")
    overtime_minutes: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(32), default="normal")
