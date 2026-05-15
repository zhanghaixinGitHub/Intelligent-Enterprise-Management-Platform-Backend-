from __future__ import annotations

from typing import Any

from fastapi import HTTPException

from app.api.dependencies.security import CurrentUserContext
from app.api.schemas.workflow import WorkflowCompleteTaskRequest, WorkflowStartProcessRequest
from app.integration.workflow_center.client import (
    WorkflowCenterClient,
    WorkflowCenterIntegrationError,
    WorkflowCenterUnavailableError,
)
from app.infra.logging.logger import AppLogger


class WorkflowCenterGatewayService:
    """Python 平台到 Java 审批中心的业务网关服务。

    这里采用“门面模式（Facade Pattern）+ 适配器模式（Adapter Pattern）”的组合：
    - WorkflowCenterClient 负责屏蔽下游 HTTP 协议差异；
    - 当前服务负责注入登录人上下文、统一错误映射、稳定对上输出。
    """

    def __init__(self, client: WorkflowCenterClient | None = None) -> None:
        self._logger = AppLogger(self.__class__.__name__)
        self._client = client or WorkflowCenterClient()

    def list_process_definitions(self) -> list[dict[str, Any]]:
        try:
            definitions = self._client.list_process_definitions()
        except WorkflowCenterUnavailableError as exc:
            self._logger.error("list_process_definitions", "Java 审批中心不可用", error=str(exc))
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        except WorkflowCenterIntegrationError as exc:
            self._logger.error("list_process_definitions", "查询流程定义失败", error=str(exc))
            raise HTTPException(status_code=502, detail=str(exc)) from exc

        self._logger.info("list_process_definitions", "查询流程定义成功", count=len(definitions))
        return definitions

    def start_process_instance(
        self,
        current_user: CurrentUserContext,
        payload: WorkflowStartProcessRequest,
    ) -> dict[str, Any]:
        request_body = {
            "processDefinitionKey": payload.processDefinitionKey,
            "initiator": current_user.employeeId,
            "managerAssignee": payload.managerAssignee,
            "hrAssignee": payload.hrAssignee,
            "businessKey": payload.businessKey,
            "leaveReason": payload.leaveReason,
            "leaveTime": payload.leaveTime,
            "variables": payload.variables,
        }
        try:
            result = self._client.start_process_instance(request_body)
        except WorkflowCenterUnavailableError as exc:
            self._logger.error(
                "start_process_instance",
                "Java 审批中心不可用",
                employee_id=current_user.employeeId,
                process_definition_key=payload.processDefinitionKey,
                error=str(exc),
            )
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        except WorkflowCenterIntegrationError as exc:
            self._logger.error(
                "start_process_instance",
                "发起流程失败",
                employee_id=current_user.employeeId,
                process_definition_key=payload.processDefinitionKey,
                error=str(exc),
            )
            raise HTTPException(status_code=502, detail=str(exc)) from exc

        self._logger.info(
            "start_process_instance",
            "发起流程成功",
            employee_id=current_user.employeeId,
            process_definition_key=payload.processDefinitionKey,
            process_instance_id=result.get("processInstanceId"),
        )
        return result

    def list_my_tasks(self, current_user: CurrentUserContext) -> list[dict[str, Any]]:
        try:
            tasks = self._client.list_user_tasks(current_user.employeeId)
        except WorkflowCenterUnavailableError as exc:
            self._logger.error("list_my_tasks", "Java 审批中心不可用", employee_id=current_user.employeeId, error=str(exc))
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        except WorkflowCenterIntegrationError as exc:
            self._logger.error("list_my_tasks", "查询我的待办失败", employee_id=current_user.employeeId, error=str(exc))
            raise HTTPException(status_code=502, detail=str(exc)) from exc

        self._logger.info("list_my_tasks", "查询我的待办成功", employee_id=current_user.employeeId, count=len(tasks))
        return tasks

    def complete_task(
        self,
        current_user: CurrentUserContext,
        task_id: str,
        payload: WorkflowCompleteTaskRequest,
    ) -> dict[str, Any]:
        request_body = {
            "operatorId": current_user.employeeId,
            "approved": payload.approved,
            "comment": payload.comment,
            "variables": payload.variables,
        }
        try:
            result = self._client.complete_task(task_id=task_id, payload=request_body)
        except WorkflowCenterUnavailableError as exc:
            self._logger.error(
                "complete_task",
                "Java 审批中心不可用",
                employee_id=current_user.employeeId,
                task_id=task_id,
                error=str(exc),
            )
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        except WorkflowCenterIntegrationError as exc:
            self._logger.error(
                "complete_task",
                "完成待办失败",
                employee_id=current_user.employeeId,
                task_id=task_id,
                error=str(exc),
            )
            raise HTTPException(status_code=502, detail=str(exc)) from exc

        self._logger.info(
            "complete_task",
            "完成待办成功",
            employee_id=current_user.employeeId,
            task_id=task_id,
            process_instance_id=result.get("processInstanceId"),
        )
        return result

    def list_my_requests(self, current_user: CurrentUserContext) -> list[dict[str, Any]]:
        """查询当前用户发起的流程请求列表。

        设计模式：门面模式（Facade Pattern）
        统一错误映射、日志记录和上下文注入，为路由层提供稳定的接口。
        """
        try:
            requests = self._client.list_user_requests(current_user.employeeId)
        except WorkflowCenterUnavailableError as exc:
            self._logger.error(
                "list_my_requests",
                "Java 审批中心不可用",
                employee_id=current_user.employeeId,
                error=str(exc),
            )
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        except WorkflowCenterIntegrationError as exc:
            self._logger.error(
                "list_my_requests",
                "查询我的请求失败",
                employee_id=current_user.employeeId,
                error=str(exc),
            )
            raise HTTPException(status_code=502, detail=str(exc)) from exc

        self._logger.info(
            "list_my_requests",
            "查询我的请求成功",
            employee_id=current_user.employeeId,
            count=len(requests),
        )
        return requests


workflow_center_gateway_service = WorkflowCenterGatewayService()

