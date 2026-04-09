from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request

from app.domain.models.audit_log import AuditLog
from app.infra.db.session import SessionLocal
from app.infra.logging.logger import AppLogger


class AuditMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self._logger = AppLogger(self.__class__.__name__)

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        operator_id = request.headers.get("X-Operator-Id", "anonymous")
        db = SessionLocal()
        try:
            log = AuditLog(
                path=request.url.path,
                method=request.method,
                status_code=response.status_code,
                operator_id=operator_id,
                message="request handled",
            )
            db.add(log)
            db.commit()
            self._logger.info("dispatch", "写入审计日志", path=request.url.path, status=response.status_code)
        except Exception as exc:
            self._logger.error("dispatch", "审计日志写入失败", error=str(exc))
        finally:
            db.close()
        return response
