from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.models.base import BaseEntity


class AuditLog(BaseEntity):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    path: Mapped[str] = mapped_column(String(300), index=True)
    method: Mapped[str] = mapped_column(String(16))
    status_code: Mapped[int] = mapped_column(Integer)
    operator_id: Mapped[str] = mapped_column(String(64), default="anonymous", index=True)
    message: Mapped[str] = mapped_column(String(500), default="")
