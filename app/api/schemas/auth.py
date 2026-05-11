from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, description="登录用户名")
    password: str = Field(..., min_length=1, description="登录密码")


class AuthUser(BaseModel):
    employeeId: str
    username: str
    displayName: str
    departmentId: str
    roleCodes: list[str] = Field(default_factory=list)
    roleNames: list[str] = Field(default_factory=list)
    status: str = "active"


class MenuPermission(BaseModel):
    key: str
    title: str
    desc: str
    path: str
    icon: str
    order: int


class LoginResponse(BaseModel):
    accessToken: str
    tokenType: str = "Bearer"
    expiresIn: int
    expiresAt: str
    user: AuthUser
    menus: list[MenuPermission] = Field(default_factory=list)
    homePath: str = "/403"


class CurrentUserResponse(BaseModel):
    user: AuthUser
    menus: list[MenuPermission] = Field(default_factory=list)
    homePath: str = "/403"
    actionScopes: list[str] = Field(default_factory=list)


class LogoutResponse(BaseModel):
    success: bool = True

