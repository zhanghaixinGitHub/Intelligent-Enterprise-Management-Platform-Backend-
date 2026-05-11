from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.api.dependencies.security import CurrentUserContext, get_current_user
from app.api.schemas.auth import CurrentUserResponse, LoginRequest, LoginResponse, LogoutResponse
from app.domain.services.auth_service import auth_service
from app.infra.db.session import get_db
from app.security.token_service import token_service


router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    return auth_service.login(db, username=payload.username.strip(), password=payload.password)


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

