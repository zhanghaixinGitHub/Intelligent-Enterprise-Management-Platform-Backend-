from fastapi import APIRouter, Depends

from app.ai.rag.knowledge_service import KnowledgeService
from app.api.dependencies.security import CurrentUserContext, get_current_user
from app.api.schemas.common import KnowledgeAskRequest


router = APIRouter(prefix="/api/v1/knowledge", tags=["knowledge"])
knowledge_service = KnowledgeService()


@router.post("/ask")
def ask_knowledge(payload: KnowledgeAskRequest, current_user: CurrentUserContext = Depends(get_current_user)):
    result = knowledge_service.ask(payload.question)
    return {**result, "employeeId": current_user.employeeId}
