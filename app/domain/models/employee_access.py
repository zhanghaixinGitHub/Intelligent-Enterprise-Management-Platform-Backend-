from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.models.base import BaseEntity


class Employee(BaseEntity):
    __tablename__ = "employees"

    employee_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    department_id: Mapped[str] = mapped_column(String(64), default="")
    role_codes: Mapped[str] = mapped_column(String(500), default="")
    status: Mapped[str] = mapped_column(String(20), default="active")


class AccessPolicy(BaseEntity):
    __tablename__ = "access_policies"

    policy_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    role_code: Mapped[str] = mapped_column(String(64), index=True)
    menu_scopes: Mapped[str] = mapped_column(String(1000), default="")
    action_scopes: Mapped[str] = mapped_column(String(1000), default="")
    data_scopes: Mapped[str] = mapped_column(String(1000), default="")
    enabled: Mapped[str] = mapped_column(String(10), default="true")
