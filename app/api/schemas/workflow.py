from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class WorkflowProcessDefinitionItem(BaseModel):
    """流程定义摘要。

    这里显式定义 Python 网关层的输出模型，目的是把 Java Flowable 的返回结构稳定下来，
    避免前端或其他调用方直接依赖下游服务的原始 JSON 细节。
    """

    id: str
    key: str
    name: str
    version: int
    suspended: bool
    deploymentId: str


class WorkflowProcessDefinitionListResponse(BaseModel):
    processDefinitions: list[WorkflowProcessDefinitionItem] = Field(default_factory=list)


class WorkflowStartProcessRequest(BaseModel):
    """发起流程请求。

    当前阶段仍然要求前端显式传主管审批人与 HR 办理人，这是为了在组织架构中心尚未打通前，
    先保证 Python 平台到 Java Flowable 的跨服务审批链路可运行、可验证、可演进。
    """

    processDefinitionKey: str
    managerAssignee: str
    hrAssignee: str
    businessKey: str | None = None
    title: str | None = None
    variables: dict[str, Any] = Field(default_factory=dict)


class WorkflowStartProcessResponse(BaseModel):
    processDefinitionKey: str
    processInstanceId: str
    businessKey: str | None = None
    processStatus: str
    currentTaskNames: list[str] = Field(default_factory=list)


class WorkflowTaskItem(BaseModel):
    taskId: str
    taskName: str
    taskDefinitionKey: str
    assignee: str
    processInstanceId: str
    processDefinitionId: str
    createTime: str | None = None


class WorkflowMyTasksResponse(BaseModel):
    tasks: list[WorkflowTaskItem] = Field(default_factory=list)


class WorkflowCompleteTaskRequest(BaseModel):
    """完成待办任务请求。

    操作人不允许由前端自传，而是统一取当前登录人，防止客户端伪造他人身份直接办理审批。
    """

    approved: bool | None = None
    comment: str | None = None
    variables: dict[str, Any] = Field(default_factory=dict)


class WorkflowCompleteTaskResponse(BaseModel):
    taskId: str
    processInstanceId: str
    processEnded: bool
    currentTaskNames: list[str] = Field(default_factory=list)

