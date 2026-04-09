from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.models.base import BaseEntity


class OperationRequest(BaseEntity):
    __tablename__ = "operation_requests"

    request_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    session_id: Mapped[str] = mapped_column(String(64), index=True)
    employee_id: Mapped[str] = mapped_column(String(64), index=True)
    operation_type: Mapped[str] = mapped_column(String(32), index=True)
    payload: Mapped[str] = mapped_column(String(4000), default="{}")
    idempotency_key: Mapped[str] = mapped_column(String(128), index=True)
    status: Mapped[str] = mapped_column(String(32), default="pending")
    error_message: Mapped[str] = mapped_column(String(500), default="")
