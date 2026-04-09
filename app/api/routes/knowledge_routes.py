from fastapi import APIRouter

from app.ai.rag.knowledge_service import KnowledgeService
from app.api.schemas.common import KnowledgeAskRequest


router = APIRouter(prefix="/api/v1/knowledge", tags=["knowledge"])
knowledge_service = KnowledgeService()


@router.post("/ask")
def ask_knowledge(payload: KnowledgeAskRequest):
    result = knowledge_service.ask(payload.question)
    return result
