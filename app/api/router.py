from fastapi import APIRouter

from app.api.routes.auth_routes import router as auth_router
from app.api.routes.chat_routes import router as chat_router
from app.api.routes.workflow_routes import router as workflow_router
from app.api.routes.query_routes import router as query_router
from app.api.routes.knowledge_routes import router as knowledge_router
from app.api.routes.attendance_routes import router as attendance_router
from app.api.routes.dashboard_routes import router as dashboard_router
from app.api.routes.audit_routes import router as audit_router


api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(chat_router)
api_router.include_router(workflow_router)
api_router.include_router(query_router)
api_router.include_router(knowledge_router)
api_router.include_router(attendance_router)
api_router.include_router(dashboard_router)
api_router.include_router(audit_router)
