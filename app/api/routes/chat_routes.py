from fastapi import APIRouter

from app.ai.orchestrator.conversation_orchestrator import ConversationOrchestrator
from app.api.schemas.common import ChatOperateRequest, ChatOperateResponse
from app.infra.lock.idempotency_guard import idempotency_guard


router = APIRouter(prefix="/api/v1/chat", tags=["chat"])
orchestrator = ConversationOrchestrator()


@router.post("/operate", response_model=ChatOperateResponse)
def chat_operate(payload: ChatOperateRequest):
    key = payload.idempotencyKey or f"{payload.employeeId}:{payload.sessionId}:{payload.message}"
    if not idempotency_guard.acquire(key):
        return ChatOperateResponse(
            requestId="duplicate",
            status="failed",
            reply="检测到重复请求，请勿重复提交。",
            nextRequiredFields=[],
        )

    result = orchestrator.handle(
        session_id=payload.sessionId,
        employee_id=payload.employeeId,
        message=payload.message,
    )
    return ChatOperateResponse(**result)
