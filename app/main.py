from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.middleware.authz_middleware import AuthzMiddleware
from app.api.middleware.audit_middleware import AuditMiddleware
from app.api.router import api_router
from app.infra.config.settings import settings
from app.infra.db.session import Base, engine

# 导入模型用于建表
from app.domain.models.conversation_session import ConversationSession  # noqa: F401
from app.domain.models.operation_request import OperationRequest  # noqa: F401
from app.domain.models.employee_access import Employee, AccessPolicy  # noqa: F401
from app.domain.models.workflow_models import WorkflowInstance, ApprovalRecord  # noqa: F401
from app.domain.models.notification_event import NotificationEvent  # noqa: F401
from app.domain.models.query_knowledge_models import QueryTask, KnowledgeEntry  # noqa: F401
from app.domain.models.meeting_minutes import MeetingMinutes  # noqa: F401
from app.domain.models.attendance_record import AttendanceRecord  # noqa: F401
from app.domain.models.audit_log import AuditLog  # noqa: F401


Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name)
# 使用全局 CORS 中间件统一处理跨域，后续新增接口会自动继承这套策略。
# 采用“中间件模式（Middleware Pattern）”集中治理跨域，避免路由级重复配置。
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
    expose_headers=settings.cors_expose_headers,
)
app.add_middleware(AuthzMiddleware)
app.add_middleware(AuditMiddleware)
app.include_router(api_router)


@app.get("/health")
def health():
    return {"status": "ok"}
