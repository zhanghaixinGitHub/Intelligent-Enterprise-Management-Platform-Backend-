from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.api.dependencies.security import CurrentUserContext, get_current_user
from app.api.schemas.auth import CurrentUserResponse, LoginRequest, LoginResponse, LogoutResponse
from app.domain.services.auth_service import auth_service
from app.infra.db.session import get_db
from app.infra.logging.logger import AppLogger
from app.security.token_service import token_service


router = APIRouter(prefix="/api/v1/auth", tags=["auth"])
logger = AppLogger("AuthRoutes")


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    # 先对用户名做去空白处理，避免前端无意携带首尾空格导致账号匹配异常。
    # 这里在路由层仅做轻量参数整理，不承载实际认证逻辑，保持分层职责清晰。
    username = payload.username.strip()

    # 使用局部变量承接 service 返回值，避免重复调用登录逻辑。
    # 原实现会执行两次登录：不仅造成重复的鉴权与 token 生成，还可能带来审计噪音与潜在状态不一致。
    login_result = auth_service.login(db, username=username, password=payload.password)

    # 按项目统一日志格式输出到控制台。
    # 日志仅记录业务定位所需的非敏感信息，严禁输出密码、token 等敏感字段。
    logger.info(
        "login",
        "登录接口处理完成",
        username=username,
        login_result=login_result,
    )
    return login_result


@router.get("/me", response_model=CurrentUserResponse)
def get_current_user_info(request: Request, db: Session = Depends(get_db), current_user: CurrentUserContext = Depends(get_current_user)):
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "", 1).strip()
    token_payload = token_service.verify_token(token)
    return auth_service.get_current_user_info(db, token_payload)


@router.get("/menus")
def get_user_menus(request: Request, db: Session = Depends(get_db), current_user: CurrentUserContext = Depends(get_current_user)):
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "", 1).strip()
    token_payload = token_service.verify_token(token)
    result = auth_service.get_current_user_info(db, token_payload)
    return {"menus": result["menus"], "homePath": result["homePath"]}


@router.post("/logout", response_model=LogoutResponse)
def logout(current_user: CurrentUserContext = Depends(get_current_user)):
    # 当前采用无状态 token，服务端无需维护会话表，因此登出只由前端清理本地 token 即可。
    # 保留该接口是为了给未来接入黑名单、单点登录、审计扩展预留稳定契约。
    return {"success": True}

