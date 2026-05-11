from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.models.base import BaseEntity


class UserAccount(BaseEntity):
    """登录账号表。

    设计意图：
    1. 账号认证与员工主数据分表，避免为了登录功能强行污染现有业务实体。
    2. `employee_id` 继续作为业务系统内的统一身份标识，兼容现有考勤、审批、对话等接口。
    3. `password_hash` 存储加盐哈希结果，避免明文密码落库。
    """

    __tablename__ = "user_accounts"

    account_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(512))
    employee_id: Mapped[str] = mapped_column(String(64), index=True)
    status: Mapped[str] = mapped_column(String(20), default="active")

