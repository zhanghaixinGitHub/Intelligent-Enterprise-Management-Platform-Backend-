from __future__ import annotations

from typing import Any

from fastapi import HTTPException, Request
from pydantic import BaseModel, Field


class CurrentUserContext(BaseModel):
    employeeId: str
    username: str
    displayName: str
    departmentId: str
    roleCodes: list[str] = Field(default_factory=list)
    roleNames: list[str] = Field(default_factory=list)
    status: str = "active"
    menuKeys: list[str] = Field(default_factory=list)
    actionScopes: list[str] = Field(default_factory=list)
    homePath: str = "/403"


# 采用依赖注入模式，把“从 request.state 提取当前登录人”的动作统一封装，
# 避免每个路由重复写同样的鉴权样板代码，也便于后续扩展租户、组织等上下文信息。
def get_current_user(request: Request) -> CurrentUserContext:
    context: dict[str, Any] | None = getattr(request.state, "current_user", None)
    if not context:
        raise HTTPException(status_code=401, detail="未登录或登录已失效")
    return CurrentUserContext(**context)

