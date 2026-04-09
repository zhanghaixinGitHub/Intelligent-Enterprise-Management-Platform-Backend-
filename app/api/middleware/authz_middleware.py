from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


class AuthzMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 预留：后续可扩展成 JWT + RBAC + 数据权限校验。
        # 当前最小实现仅保证接口可跑通并统一拒绝非法 token。
        auth_header = request.headers.get("Authorization", "")
        if auth_header and not auth_header.startswith("Bearer "):
            return JSONResponse({"code": 401, "message": "invalid authorization header", "data": None}, status_code=401)
        return await call_next(request)
