# 审计中间件
# 功能：拦截所有HTTP请求，自动记录请求路径、方法、状态码和操作员信息到数据库
# 应用场景：系统审计追踪、操作日志记录、问题排查
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request

from app.domain.models.audit_log import AuditLog
from app.infra.db.session import SessionLocal
from app.infra.logging.logger import AppLogger


class AuditMiddleware(BaseHTTPMiddleware):
    """
    审计日志中间件
    
    工作原理：
    1. 拦截所有经过的HTTP请求
    2. 先让请求正常处理（call_next）
    3. 获取响应后，将请求信息写入审计日志表
    4. 记录内容包括：请求路径、方法、响应状态码、操作员ID
    """
    
    def __init__(self, app):
        super().__init__(app)
        self._logger = AppLogger(self.__class__.__name__)

    async def dispatch(self, request: Request, call_next):
        """
        中间件核心处理逻辑
        
        参数：
        - request: 当前HTTP请求对象
        - call_next: 调用下一个中间件或最终路由处理函数
        
        流程：
        1. 先执行请求处理，获取响应
        2. 从请求头提取操作员ID（X-Operator-Id），默认为anonymous
        3. 创建数据库会话，写入审计日志记录
        4. 异常情况下记录错误日志，但不影响正常响应
        """
        # 先让请求正常处理，获取响应结果
        response = await call_next(request)
        
        # 从请求头提取操作员ID，如果未提供则默认为anonymous
        operator_id = request.headers.get("X-Operator-Id", "anonymous")
        
        # 创建数据库会话用于写入审计日志
        db = SessionLocal()
        try:
            # 创建审计日志记录对象
            log = AuditLog(
                path=request.url.path,           # 请求路径，如 /api/v1/audit/logs
                method=request.method,           # 请求方法，如 GET/POST
                status_code=response.status_code,  # 响应状态码，如 200/401/403
                operator_id=operator_id,         # 操作员ID
                message="request handled",       # 日志描述信息
            )
            # 将日志记录添加到数据库并提交
            db.add(log)
            db.commit()
            # 记录成功日志到应用日志
            self._logger.info("dispatch", "写入审计日志", path=request.url.path, status=response.status_code)
        except Exception as exc:
            # 审计日志写入失败不应影响正常请求，只记录错误
            self._logger.error("dispatch", "审计日志写入失败", error=str(exc))
        finally:
            # 确保数据库连接被正确关闭
            db.close()
        
        # 返回原始响应给客户端
        return response
