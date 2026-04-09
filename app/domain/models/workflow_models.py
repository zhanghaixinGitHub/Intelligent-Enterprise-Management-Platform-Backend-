from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.models.base import BaseEntity


class WorkflowInstance(BaseEntity):
    __tablename__ = "workflow_instances"

    workflow_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    request_id: Mapped[str] = mapped_column(String(64), index=True)
    workflow_type: Mapped[str] = mapped_column(String(32), default="leave")
    current_node: Mapped[str] = mapped_column(String(64), default="start")
    status: Mapped[str] = mapped_column(String(32), default="running")
    version: Mapped[int] = mapped_column(Integer, default=1)


class ApprovalRecord(BaseEntity):
    __tablename__ = "approval_records"

    approval_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    workflow_id: Mapped[str] = mapped_column(String(64), index=True)
    approver_id: Mapped[str] = mapped_column(String(64), index=True)
    action: Mapped[str] = mapped_column(String(32))
    comment: Mapped[str] = mapped_column(String(1000), default="")
