from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.models.base import BaseEntity


class MeetingMinutes(BaseEntity):
    __tablename__ = "meeting_minutes"

    minutes_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    meeting_topic: Mapped[str] = mapped_column(String(300))
    participants: Mapped[str] = mapped_column(String(1000), default="")
    summary: Mapped[str] = mapped_column(String(4000), default="")
    action_items: Mapped[str] = mapped_column(String(4000), default="[]")
    decision_items: Mapped[str] = mapped_column(String(4000), default="[]")
    owner_employee_id: Mapped[str] = mapped_column(String(64), index=True)
