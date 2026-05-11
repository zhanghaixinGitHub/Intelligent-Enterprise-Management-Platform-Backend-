from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.domain.constants.auth_catalog import is_public_path, resolve_action_scope
from app.domain.services.auth_service import auth_service
from app.infra.db.session import SessionLocal
from app.security.token_service import token_service


class AuthzMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if is_public_path(request.url.path):
            return await call_next(request)

        auth_header = request.headers.get("Authorization", "")
        if not auth_header:
            return JSONResponse({"code": 401, "message": "missing authorization header", "data": None}, status_code=401)

        if not auth_header.startswith("Bearer "):
            return JSONResponse({"code": 401, "message": "invalid authorization header", "data": None}, status_code=401)

        token = auth_header.replace("Bearer ", "", 1).strip()
        try:
            token_payload = token_service.verify_token(token)
        except ValueError as exc:
            return JSONResponse({"code": 401, "message": str(exc), "data": None}, status_code=401)

        db = SessionLocal()
        try:
            session_context = auth_service.build_session_context(db, token_payload)
            required_action = resolve_action_scope(request.method, request.url.path)
            if not auth_service.has_action_scope(session_context["actionScopes"], required_action):
                return JSONResponse(
                    {"code": 403, "message": f"forbidden: missing scope {required_action}", "data": None},
                    status_code=403,
                )
            request.state.current_user = {
                **session_context["user"],
                "menuKeys": session_context["menuKeys"],
                "actionScopes": session_context["actionScopes"],
                "homePath": session_context["homePath"],
            }
        finally:
            db.close()

        return await call_next(request)
