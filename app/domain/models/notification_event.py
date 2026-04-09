from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.models.base import BaseEntity


class NotificationEvent(BaseEntity):
    __tablename__ = "notification_events"

    notification_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    event_type: Mapped[str] = mapped_column(String(32), index=True)
    receiver_id: Mapped[str] = mapped_column(String(64), index=True)
    channel: Mapped[str] = mapped_column(String(32), default="in_app")
    delivery_status: Mapped[str] = mapped_column(String(32), default="pending")
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    payload: Mapped[str] = mapped_column(String(4000), default="{}")
