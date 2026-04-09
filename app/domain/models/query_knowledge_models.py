from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.models.base import BaseEntity


class QueryTask(BaseEntity):
    __tablename__ = "query_tasks"

    query_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    employee_id: Mapped[str] = mapped_column(String(64), index=True)
    question: Mapped[str] = mapped_column(String(2000))
    query_dsl: Mapped[str] = mapped_column(String(4000), default="{}")
    result_summary: Mapped[str] = mapped_column(String(2000), default="")
    result_payload: Mapped[str] = mapped_column(String(4000), default="{}")
    status: Mapped[str] = mapped_column(String(20), default="pending")


class KnowledgeEntry(BaseEntity):
    __tablename__ = "knowledge_entries"

    knowledge_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    source_path: Mapped[str] = mapped_column(String(500))
    content_chunk: Mapped[str] = mapped_column(String(4000))
    tags: Mapped[str] = mapped_column(String(500), default="")
    version: Mapped[str] = mapped_column(String(50), default="v1")
