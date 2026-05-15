from __future__ import annotations

from typing import Any

import requests
from requests import Response, Session

from app.infra.config.settings import settings
from app.infra.logging.logger import AppLogger


class WorkflowCenterIntegrationError(RuntimeError):
    """Java 审批中心返回业务错误时抛出的异常。"""


class WorkflowCenterUnavailableError(RuntimeError):
    """Java 审批中心不可用或超时时抛出的异常。"""


class WorkflowCenterClient:
    """Java 审批中心 HTTP 适配客户端。

    这里采用“适配器模式（Adapter Pattern）”封装 Flowable Java 服务调用，解决的问题是：
    - Python 平台不直接依赖下游服务的裸 HTTP 细节，后续切换网关、鉴权头、返回结构时改动面更小；
    - 把超时、错误码处理、日志、统一 headers 收敛到一个地方，避免路由层重复拼接；
    - 为未来增加重试、熔断、TraceId 透传保留稳定扩展点。
    """

    def __init__(self, session: Session | None = None) -> None:
        self._logger = AppLogger(self.__class__.__name__)
        self._base_url = settings.workflow_center_base_url.rstrip("/")
        self._timeout = (
            settings.workflow_center_connect_timeout_seconds,
            settings.workflow_center_read_timeout_seconds,
        )
        self._session = session or requests.Session()
        self._session.headers.update(
            {
                "Accept": "application/json",
                "Content-Type": "application/json; charset=UTF-8",
                "X-Internal-Token": settings.workflow_center_internal_token,
            }
        )

    def list_process_definitions(self) -> list[dict[str, Any]]:
        return self._request("GET", "/api/v1/workflows/process-definitions")

    def start_process_instance(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._request("POST", "/api/v1/workflows/process-instances/start", json=payload)

    def list_user_tasks(self, assignee: str) -> list[dict[str, Any]]:
        return self._request("GET", "/api/v1/workflows/tasks", params={"assignee": assignee})

    def complete_task(self, task_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        return self._request("POST", f"/api/v1/workflows/tasks/{task_id}/complete", json=payload)

    def list_user_requests(self, initiator: str) -> list[dict[str, Any]]:
        """查询用户发起的流程请求列表。

        设计模式：适配器模式（Adapter Pattern）
        封装对Java Flowable后端的HTTP调用，屏蔽底层协议细节。
        """
        return self._request("GET", "/api/v1/workflows/requests", params={"initiator": initiator})

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> Any:
        url = f"{self._base_url}{path}"
        self._logger.info("_request", "开始调用 Java 审批中心", method=method, url=url)
        try:
            response = self._session.request(
                method=method,
                url=url,
                params=params,
                json=json,
                timeout=self._timeout,
            )
        except requests.RequestException as exc:
            self._logger.error("_request", "调用 Java 审批中心失败", method=method, url=url, error=str(exc))
            raise WorkflowCenterUnavailableError("Java 审批中心暂时不可用，请稍后重试") from exc

        return self._parse_response(response=response, method=method, url=url)

    def _parse_response(self, response: Response, *, method: str, url: str) -> Any:
        try:
            payload = response.json()
        except ValueError as exc:
            self._logger.error(
                "_parse_response",
                "Java 审批中心返回了不可解析的响应",
                method=method,
                url=url,
                status_code=response.status_code,
                body=response.text[:500],
            )
            raise WorkflowCenterUnavailableError("Java 审批中心响应格式异常，请联系管理员处理") from exc

        if response.status_code >= 500:
            self._logger.error(
                "_parse_response",
                "Java 审批中心返回服务端异常",
                method=method,
                url=url,
                status_code=response.status_code,
                payload=payload,
            )
            raise WorkflowCenterUnavailableError("Java 审批中心处理失败，请稍后重试")

        if response.status_code >= 400 or not payload.get("success", False):
            message = str(payload.get("message") or "Java 审批中心业务处理失败")
            self._logger.error(
                "_parse_response",
                "Java 审批中心返回业务错误",
                method=method,
                url=url,
                status_code=response.status_code,
                payload=payload,
            )
            raise WorkflowCenterIntegrationError(message)

        self._logger.info(
            "_parse_response",
            "Java 审批中心调用成功",
            method=method,
            url=url,
            status_code=response.status_code,
        )
        return payload.get("data")

