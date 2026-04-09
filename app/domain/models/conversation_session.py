from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.models.base import BaseEntity


class ConversationSession(BaseEntity):
    __tablename__ = "conversation_sessions"

    session_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    employee_id: Mapped[str] = mapped_column(String(64), index=True)
    current_intent: Mapped[str] = mapped_column(String(64), default="")
    state: Mapped[str] = mapped_column(String(32), default="collecting")
    context_snapshot: Mapped[str] = mapped_column(String(4000), default="{}")
