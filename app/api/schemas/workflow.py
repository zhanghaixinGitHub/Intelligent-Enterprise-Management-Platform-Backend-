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

    修改说明：
    1. managerAssignee 和 hrAssignee 改为可选字段，由后端自动获取或提供默认值
    2. businessKey 改为可选字段，由后端自动生成
    3. 将 title 字段替换为 leaveReason（请假原因），语义更明确
    4. 新增 leaveTime（请假时间）字段

    设计模式：数据传输对象模式（DTO Pattern）
    用于在不同服务层之间传输数据，提供稳定的接口契约。
    """

    processDefinitionKey: str
    managerAssignee: str | None = None
    hrAssignee: str | None = None
    businessKey: str | None = None
    leaveReason: str | None = None
    leaveTime: str | None = None
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


class WorkflowRequestItem(BaseModel):
    """我发起的流程请求项。

    设计模式：数据传输对象模式（DTO Pattern）
    用于在不同服务层之间传输流程请求数据，提供稳定的接口契约。
    """

    processInstanceId: str
    processDefinitionKey: str
    processDefinitionName: str | None = None
    businessKey: str | None = None
    title: str | None = None
    processStatus: str
    currentTaskNames: list[str] = Field(default_factory=list)
    startTime: str | None = None
    canRevoke: bool = False


class WorkflowMyRequestsResponse(BaseModel):
    """我的流程请求列表响应。

    设计模式：聚合根模式（Aggregate Root Pattern）
    将相关的流程请求数据聚合为一个响应对象，便于前端统一处理。
    """

    requests: list[WorkflowRequestItem] = Field(default_factory=list)

