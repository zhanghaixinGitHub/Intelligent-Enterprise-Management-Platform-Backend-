from __future__ import annotations

import re
from typing import Final


# 菜单目录由后端统一定义，前端只负责按 key 渲染对应页面。
# 这样做可以把“谁能看到什么菜单”的规则收敛到服务端，避免前端写死菜单后再做二次过滤。
MENU_CATALOG: Final[list[dict[str, object]]] = [
    {
        "key": "dashboard",
        "title": "经营看板",
        "desc": "经营、人事与审批总览",
        "path": "/dashboard",
        "icon": "DataBoard",
        "order": 10,
    },
    {
        "key": "attendance",
        "title": "考勤管理",
        "desc": "个人打卡与月度汇总",
        "path": "/attendance",
        "icon": "Calendar",
        "order": 20,
    },
    {
        "key": "workflow",
        "title": "审批待办",
        "desc": "审批流转与处理",
        "path": "/workflow",
        "icon": "List",
        "order": 30,
    },
    {
        "key": "dialog",
        "title": "AI 对话中心",
        "desc": "自然语言办理业务",
        "path": "/dialog",
        "icon": "ChatDotRound",
        "order": 40,
    },
    {
        "key": "insight",
        "title": "智能洞察",
        "desc": "知识问答与数据分析",
        "path": "/insight",
        "icon": "MagicStick",
        "order": 50,
    },
]

MENU_MAP: Final[dict[str, dict[str, object]]] = {item["key"]: item for item in MENU_CATALOG}
MENU_KEYS: Final[set[str]] = {item["key"] for item in MENU_CATALOG}

ROLE_POLICY_SEEDS: Final[list[dict[str, str]]] = [
    {
        "policy_id": "policy-admin",
        "role_code": "admin",
        "menu_scopes": "*",
        "action_scopes": "*",
        "data_scopes": "all",
    },
    {
        "policy_id": "policy-hr",
        "role_code": "hr",
        "menu_scopes": "dashboard,attendance,insight",
        "action_scopes": "dashboard:view,attendance:view,attendance:clock-in,insight:data,insight:knowledge",
        "data_scopes": "self,department",
    },
    {
        "policy_id": "policy-manager",
        "role_code": "manager",
        "menu_scopes": "dashboard,workflow,dialog,insight",
        "action_scopes": "dashboard:view,workflow:approve,dialog:use,insight:data,insight:knowledge",
        "data_scopes": "self,team",
    },
    {
        "policy_id": "policy-employee",
        "role_code": "employee",
        "menu_scopes": "attendance,dialog,insight",
        "action_scopes": "attendance:view,attendance:clock-in,dialog:use,insight:data,insight:knowledge",
        "data_scopes": "self",
    },
]

DEFAULT_USER_SEEDS: Final[list[dict[str, str]]] = [
    {
        "account_id": "account-admin",
        "username": "admin",
        "password": "Admin@123",
        "employee_id": "employee-001",
        "name": "平台管理员",
        "department_id": "dept-platform",
        "role_codes": "admin",
    },
    {
        "account_id": "account-hr",
        "username": "hr",
        "password": "Hr@123456",
        "employee_id": "employee-002",
        "name": "人事专员",
        "department_id": "dept-hr",
        "role_codes": "hr",
    },
    {
        "account_id": "account-manager",
        "username": "manager",
        "password": "Manager@123",
        "employee_id": "employee-003",
        "name": "审批经理",
        "department_id": "dept-finance",
        "role_codes": "manager",
    },
    {
        "account_id": "account-employee",
        "username": "employee",
        "password": "Employee@123",
        "employee_id": "employee-004",
        "name": "普通员工",
        "department_id": "dept-rd",
        "role_codes": "employee",
    },
]

ROLE_LABELS: Final[dict[str, str]] = {
    "admin": "平台管理员",
    "hr": "人事角色",
    "manager": "审批经理",
    "employee": "普通员工",
}

PUBLIC_PATHS: Final[set[str]] = {
    "/health",
    "/openapi.json",
    "/docs",
    "/docs/oauth2-redirect",
    "/redoc",
    "/api/v1/auth/login",
}

ACTION_RULES: Final[list[dict[str, object]]] = [
    {"method": "GET", "pattern": re.compile(r"^/api/v1/dashboard/overview$"), "action": "dashboard:view"},
    {"method": "POST", "pattern": re.compile(r"^/api/v1/attendance/clock-in$"), "action": "attendance:clock-in"},
    {"method": "GET", "pattern": re.compile(r"^/api/v1/attendance/monthly-summary$"), "action": "attendance:view"},
    {"method": "POST", "pattern": re.compile(r"^/api/v1/workflows/[^/]+/approve$"), "action": "workflow:approve"},
    {"method": "POST", "pattern": re.compile(r"^/api/v1/chat/operate$"), "action": "dialog:use"},
    {"method": "POST", "pattern": re.compile(r"^/api/v1/query/ask$"), "action": "insight:data"},
    {"method": "POST", "pattern": re.compile(r"^/api/v1/knowledge/ask$"), "action": "insight:knowledge"},
]


def is_public_path(path: str) -> bool:
    return path in PUBLIC_PATHS


def resolve_action_scope(method: str, path: str) -> str | None:
    for rule in ACTION_RULES:
        if method.upper() != rule["method"]:
            continue
        if rule["pattern"].match(path):
            return str(rule["action"])
    return None

