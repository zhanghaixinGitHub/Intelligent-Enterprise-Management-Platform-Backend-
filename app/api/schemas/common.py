from typing import Any
from pydantic import BaseModel, Field


class ApiResponse(BaseModel):
    code: int = 0
    message: str = "ok"
    data: Any = None


class ChatOperateRequest(BaseModel):
    sessionId: str
    employeeId: str | None = None
    message: str
    idempotencyKey: str | None = None


class ChatOperateResponse(BaseModel):
    requestId: str
    status: str
    reply: str
    nextRequiredFields: list[str] = Field(default_factory=list)


class ApprovalActionRequest(BaseModel):
    approverId: str | None = None
    action: str
    comment: str | None = None
    idempotencyKey: str | None = None


class DataQueryRequest(BaseModel):
    employeeId: str | None = None
    question: str


class KnowledgeAskRequest(BaseModel):
    employeeId: str | None = None
    question: str
