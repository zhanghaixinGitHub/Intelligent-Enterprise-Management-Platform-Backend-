from __future__ import annotations

from copy import deepcopy
import hashlib
import secrets
from typing import Any, cast
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.domain.constants.auth_catalog import (
    DEFAULT_USER_SEEDS,
    MENU_CATALOG,
    MENU_KEYS,
    ROLE_LABELS,
    ROLE_POLICY_SEEDS,
)
from app.domain.models.auth_models import UserAccount
from app.domain.models.employee_access import AccessPolicy, Employee
from app.infra.logging.logger import AppLogger
from app.security.token_service import token_service


class AuthService:
    """认证与菜单权限服务。

    这里使用了“策略模式”的轻量变体：
    - 角色 -> 权限策略 存在 `access_policies` 表中；
    - 菜单元数据在目录常量中集中维护；
    - 登录后由本服务把“用户 + 角色策略 + 菜单目录”组装成前端可直接消费的结果。
    """

    def __init__(self) -> None:
        self._logger = AppLogger(self.__class__.__name__)

    @staticmethod
    def _split_csv(raw_value: str | None) -> list[str]:
        if not raw_value:
            return []
        return [item.strip() for item in raw_value.split(",") if item.strip()]

    @staticmethod
    def _hash_password(password: str, salt: str | None = None) -> str:
        actual_salt = salt or secrets.token_hex(16)
        digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), actual_salt.encode("utf-8"), 120000).hex()
        return f"{actual_salt}${digest}"

    @classmethod
    def _verify_password(cls, plain_password: str, stored_hash: str) -> bool:
        try:
            salt, _ = stored_hash.split("$", 1)
        except ValueError:
            return False
        return cls._hash_password(plain_password, salt=salt) == stored_hash

    def ensure_seed_data(self, db: Session) -> None:
        changed = False

        for seed in DEFAULT_USER_SEEDS:
            employee = db.get(Employee, seed["employee_id"])
            if employee is None:
                employee = Employee(
                    employee_id=seed["employee_id"],
                    name=seed["name"],
                    department_id=seed["department_id"],
                    role_codes=seed["role_codes"],
                    status="active",
                )
                db.add(employee)
                changed = True

            account = db.get(UserAccount, seed["account_id"])
            if account is None:
                account = UserAccount(
                    account_id=seed["account_id"],
                    username=seed["username"],
                    password_hash=self._hash_password(seed["password"]),
                    employee_id=seed["employee_id"],
                    status="active",
                )
                db.add(account)
                changed = True

        for policy_seed in ROLE_POLICY_SEEDS:
            policy = db.get(AccessPolicy, policy_seed["policy_id"])
            if policy is None:
                policy = AccessPolicy(
                    policy_id=policy_seed["policy_id"],
                    role_code=policy_seed["role_code"],
                    menu_scopes=policy_seed["menu_scopes"],
                    action_scopes=policy_seed["action_scopes"],
                    data_scopes=policy_seed["data_scopes"],
                    enabled="true",
                )
                db.add(policy)
                changed = True
                continue

            # 这里对角色策略采用“幂等同步”的方式而不是仅首次插入：
            # 当企业项目的菜单范围、动作范围、数据范围随着架构演进发生变化时，
            # 如果只在空表时插入，旧数据库里的策略会永久停留在历史版本，导致新接口无权限或菜单不显示。
            updated = False
            if policy.role_code != policy_seed["role_code"]:
                policy.role_code = policy_seed["role_code"]
                updated = True
            if policy.menu_scopes != policy_seed["menu_scopes"]:
                policy.menu_scopes = policy_seed["menu_scopes"]
                updated = True
            if policy.action_scopes != policy_seed["action_scopes"]:
                policy.action_scopes = policy_seed["action_scopes"]
                updated = True
            if policy.data_scopes != policy_seed["data_scopes"]:
                policy.data_scopes = policy_seed["data_scopes"]
                updated = True
            if policy.enabled != "true":
                policy.enabled = "true"
                updated = True

            if updated:
                changed = True

        if changed:
            db.commit()
            self._logger.info("ensure_seed_data", "初始化或同步默认账号与权限策略完成")

    def _build_menu_list(self, menu_keys: list[str]) -> list[dict[str, Any]]:
        if "*" in menu_keys:
            return self._clone_menu_items(MENU_CATALOG)

        allowed_key_set = set(menu_keys)
        return self._filter_menu_items(MENU_CATALOG, allowed_key_set)

    def _clone_menu_items(self, items: list[dict[str, object]]) -> list[dict[str, Any]]:
        cloned_items = [cast(dict[str, Any], deepcopy(item)) for item in items]
        for item in cloned_items:
            children = item.get("children")
            if isinstance(children, list):
                item["children"] = sorted(children, key=lambda child: int(cast(dict[str, Any], child)["order"]))
        return sorted(cloned_items, key=lambda item: int(item["order"]))

    def _filter_menu_items(self, items: list[dict[str, object]], allowed_key_set: set[str]) -> list[dict[str, Any]]:
        filtered_items: list[dict[str, Any]] = []
        for item in sorted(items, key=lambda current: int(current["order"])):
            item_key = str(item["key"])
            raw_children = item.get("children")
            child_items = [cast(dict[str, object], child) for child in raw_children] if isinstance(raw_children, list) else []
            filtered_children = self._filter_menu_items(child_items, allowed_key_set) if child_items else []

            if item_key not in allowed_key_set and not filtered_children:
                continue

            cloned_item = cast(dict[str, Any], deepcopy(item))
            cloned_item["children"] = filtered_children
            filtered_items.append(cloned_item)
        return filtered_items

    def _flatten_menu_keys(self, items: list[dict[str, Any]]) -> list[str]:
        collected_keys: list[str] = []
        for item in items:
            collected_keys.append(str(item["key"]))
            children = item.get("children")
            if isinstance(children, list) and children:
                collected_keys.extend(self._flatten_menu_keys([cast(dict[str, Any], child) for child in children]))
        return collected_keys

    def _resolve_home_path(self, items: list[dict[str, Any]]) -> str:
        for item in items:
            children = item.get("children")
            if isinstance(children, list) and children:
                child_home_path = self._resolve_home_path([cast(dict[str, Any], child) for child in children])
                if child_home_path:
                    return child_home_path

            path = str(item.get("path", "")).strip()
            if path:
                return path

        return "/403"

    def resolve_permissions(self, db: Session, role_codes: list[str]) -> dict[str, Any]:
        policies = (
            db.query(AccessPolicy)
            .filter(AccessPolicy.role_code.in_(role_codes), AccessPolicy.enabled == "true")
            .all()
            if role_codes
            else []
        )

        menu_scope_set: set[str] = set()
        action_scope_set: set[str] = set()
        for policy in policies:
            menu_scope_set.update(self._split_csv(cast(str | None, cast(object, policy.menu_scopes))))
            action_scope_set.update(self._split_csv(cast(str | None, cast(object, policy.action_scopes))))

        if "*" in menu_scope_set:
            menu_keys = ["*"]
        else:
            menu_keys = sorted(scope for scope in menu_scope_set if scope in MENU_KEYS)

        if "*" in action_scope_set:
            action_scopes = ["*"]
        else:
            action_scopes = sorted(action_scope_set)

        menus = self._build_menu_list(menu_keys)
        home_path = self._resolve_home_path(menus)
        flattened_menu_keys = self._flatten_menu_keys(menus)

        return {
            "menus": menus,
            "menuKeys": flattened_menu_keys,
            "actionScopes": action_scopes,
            "homePath": home_path,
        }

    def build_user_context(self, db: Session, employee_id: str, username: str) -> dict[str, Any]:
        employee = db.get(Employee, employee_id)
        if employee is None or employee.status != "active":
            raise HTTPException(status_code=401, detail="当前账号关联的员工已停用")

        role_codes = self._split_csv(cast(str | None, cast(object, employee.role_codes)))
        permissions = self.resolve_permissions(db, role_codes)
        user = {
            "employeeId": employee.employee_id,
            "username": username,
            "displayName": employee.name,
            "departmentId": employee.department_id,
            "roleCodes": role_codes,
            "roleNames": [ROLE_LABELS.get(code, code) for code in role_codes],
            "status": employee.status,
        }
        return {
            "user": user,
            "menus": permissions["menus"],
            "menuKeys": permissions["menuKeys"],
            "actionScopes": permissions["actionScopes"],
            "homePath": permissions["homePath"],
        }

    def build_session_context(self, db: Session, token_payload: dict[str, Any]) -> dict[str, Any]:
        employee_id = str(token_payload.get("employeeId", "")).strip()
        username = str(token_payload.get("username", "")).strip()
        if not employee_id or not username:
            raise HTTPException(status_code=401, detail="token 缺少必要身份信息")
        return self.build_user_context(db, employee_id=employee_id, username=username)

    def login(self, db: Session, username: str, password: str) -> dict[str, Any]:
        self.ensure_seed_data(db)
        account = db.query(UserAccount).filter(UserAccount.username == username).first()
        if account is None or account.status != "active":
            self._logger.error("login", "登录失败，账号不存在或已停用", username=username)
            raise HTTPException(status_code=401, detail="用户名或密码错误")

        if not self._verify_password(password, cast(str, cast(object, account.password_hash))):
            self._logger.error("login", "登录失败，密码校验不通过", username=username)
            raise HTTPException(status_code=401, detail="用户名或密码错误")

        session_context = self.build_user_context(
            db,
            employee_id=cast(str, cast(object, account.employee_id)),
            username=cast(str, cast(object, account.username)),
        )
        token_result = token_service.create_token(
            {
                "tokenId": str(uuid4()),
                "employeeId": session_context["user"]["employeeId"],
                "username": session_context["user"]["username"],
            }
        )
        self._logger.info("login", "用户登录成功", username=username, employee_id=account.employee_id)
        return {
            **token_result,
            "user": session_context["user"],
            "menus": session_context["menus"],
            "homePath": session_context["homePath"],
            "actionScopes": session_context["actionScopes"],
        }

    def get_current_user_info(self, db: Session, token_payload: dict[str, Any]) -> dict[str, Any]:
        session_context = self.build_session_context(db, token_payload)
        return {
            "user": session_context["user"],
            "menus": session_context["menus"],
            "homePath": session_context["homePath"],
            "actionScopes": session_context["actionScopes"],
        }

    def has_action_scope(self, action_scopes: list[str], required_action: str | None) -> bool:
        if not required_action:
            return True
        if "*" in action_scopes:
            return True
        return required_action in action_scopes


# 复用单例，避免路由和中间件重复创建。
auth_service = AuthService()

