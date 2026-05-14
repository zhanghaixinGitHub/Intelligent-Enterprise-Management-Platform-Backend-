# 授权中间件（Authorization Middleware）
# 功能：实现API访问的认证与授权控制
# 应用场景：保护API接口，验证用户身份和权限，防止未授权访问
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.domain.constants.auth_catalog import is_public_path, resolve_action_scope
from app.domain.services.auth_service import auth_service
from app.infra.db.session import SessionLocal
from app.security.token_service import token_service


class AuthzMiddleware(BaseHTTPMiddleware):
    """
    授权中间件 - 负责API访问的认证（Authentication）和授权（Authorization）
    
    工作流程：
    1. 判断是否为公开路径（无需认证）
    2. 提取并验证Authorization请求头中的Bearer Token
    3. 解析Token获取用户信息和权限范围
    4. 检查用户是否有所需的操作权限
    5. 将用户上下文注入到请求状态中，供后续路由使用
    
    错误处理：
    - 401: 未提供Token或Token无效
    - 403: Token有效但权限不足
    """
    
    async def dispatch(self, request: Request, call_next):
        """
        中间件核心处理逻辑 - 认证与授权流程
        
        参数：
        - request: 当前HTTP请求对象
        - call_next: 调用下一个中间件或最终路由处理函数
        
        返回：
        - 如果认证/授权失败：返回401或403错误响应
        - 如果认证成功：继续处理请求
        """
        
        # 步骤1：检查是否为公开路径（如登录接口、文档等）
        # 公开路径无需认证，直接放行
        if is_public_path(request.url.path):
            return await call_next(request)

        # 步骤2：提取Authorization请求头
        auth_header = request.headers.get("Authorization", "")
        
        # 如果未提供Authorization头，返回401未授权错误
        if not auth_header:
            return JSONResponse(
                {"code": 401, "message": "missing authorization header", "data": None}, 
                status_code=401
            )

        # 验证Authorization头格式必须为 "Bearer <token>"
        if not auth_header.startswith("Bearer "):
            return JSONResponse(
                {"code": 401, "message": "invalid authorization header", "data": None}, 
                status_code=401
            )

        # 步骤3：提取Token字符串（去除"Bearer "前缀）
        token = auth_header.replace("Bearer ", "", 1).strip()
        
        # 步骤4：验证Token有效性并解析payload
        # 如果Token无效或过期，token_service.verify_token会抛出ValueError异常
        try:
            token_payload = token_service.verify_token(token)
        except ValueError as exc:
            # Token验证失败，返回401错误
            return JSONResponse(
                {"code": 401, "message": str(exc), "data": None}, 
                status_code=401
            )

        # 步骤5：构建用户会话上下文并检查权限
        db = SessionLocal()
        try:
            # 根据Token payload从数据库构建完整的用户会话上下文
            # 包含：用户信息、菜单权限、操作权限范围、首页路径等
            session_context = auth_service.build_session_context(db, token_payload)
            
            # 根据请求方法和路径解析所需的操作权限范围
            # 例如：GET /api/v1/users -> "user:read"
            required_action = resolve_action_scope(request.method, request.url.path)
            
            # 检查用户的权限范围是否包含所需的操作权限
            if not auth_service.has_action_scope(session_context["actionScopes"], required_action):
                # 权限不足，返回403禁止访问错误
                return JSONResponse(
                    {"code": 403, "message": f"forbidden: missing scope {required_action}", "data": None},
                    status_code=403,
                )
            
            # 步骤6：将用户上下文信息注入到请求状态中
            # 后续的路由处理函数可以通过 request.state.current_user 访问用户信息
            request.state.current_user = {
                **session_context["user"],              # 用户基本信息
                "menuKeys": session_context["menuKeys"],      # 用户可访问的菜单列表
                "actionScopes": session_context["actionScopes"],  # 用户操作权限范围
                "homePath": session_context["homePath"],       # 用户默认首页路径
            }
        finally:
            # 确保数据库连接被正确关闭
            db.close()

        # 步骤7：认证授权通过，继续处理请求
        return await call_next(request)
