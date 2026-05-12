from fastapi import APIRouter, Depends

from app.api.dependencies.security import CurrentUserContext, get_current_user
from app.api.schemas.common import ApprovalActionRequest
from app.api.schemas.workflow import (
    WorkflowCompleteTaskRequest,
    WorkflowCompleteTaskResponse,
    WorkflowMyTasksResponse,
    WorkflowProcessDefinitionListResponse,
    WorkflowStartProcessRequest,
    WorkflowStartProcessResponse,
)
from app.domain.services.approval_service import ApprovalService
from app.domain.services.notification_service import NotificationService
from app.domain.services.workflow_center_gateway_service import workflow_center_gateway_service


router = APIRouter(prefix="/api/v1/workflows", tags=["workflow"])
approval_service = ApprovalService()
notification_service = NotificationService()


@router.get("/process-definitions", response_model=WorkflowProcessDefinitionListResponse)
def list_process_definitions(current_user: CurrentUserContext = Depends(get_current_user)):
    # 这里由 Python 平台对前端暴露统一契约，后续即使 Java 侧升级 Flowable 版本，
    # 前端和其他 Python 业务模块也不需要感知下游接口的细节变化。
    process_definitions = workflow_center_gateway_service.list_process_definitions()
    return {"processDefinitions": process_definitions}


@router.post("/process-instances/start", response_model=WorkflowStartProcessResponse)
def start_process_instance(
    payload: WorkflowStartProcessRequest,
    current_user: CurrentUserContext = Depends(get_current_user),
):
    result = workflow_center_gateway_service.start_process_instance(current_user=current_user, payload=payload)
    notification_service.send(
        current_user.employeeId,
        "workflow-start",
        {
            "processDefinitionKey": payload.processDefinitionKey,
            "processInstanceId": result["processInstanceId"],
            "processStatus": result["processStatus"],
        },
    )
    return result


@router.get("/tasks/my", response_model=WorkflowMyTasksResponse)
def list_my_tasks(current_user: CurrentUserContext = Depends(get_current_user)):
    tasks = workflow_center_gateway_service.list_my_tasks(current_user=current_user)
    return {"tasks": tasks}


@router.post("/tasks/{task_id}/complete", response_model=WorkflowCompleteTaskResponse)
def complete_task(
    task_id: str,
    payload: WorkflowCompleteTaskRequest,
    current_user: CurrentUserContext = Depends(get_current_user),
):
    result = workflow_center_gateway_service.complete_task(current_user=current_user, task_id=task_id, payload=payload)
    notification_service.send(
        current_user.employeeId,
        "workflow-task-complete",
        {
            "taskId": task_id,
            "processInstanceId": result["processInstanceId"],
            "processEnded": result["processEnded"],
        },
    )
    return result


@router.post("/{workflow_id}/approve", deprecated=True)
def approve_workflow(
    workflow_id: str,
    payload: ApprovalActionRequest,
    current_user: CurrentUserContext = Depends(get_current_user),
):
    # 兼容旧前端调用：当前该接口仍走本地模板服务。
    # 新的 Java Flowable 审批链路统一使用 /process-instances/start、/tasks/my、/tasks/{task_id}/complete。
    result = approval_service.approve(
        workflow_id=workflow_id,
        action=payload.action,
        expected_version=1,
        current_version=1,
        comment=payload.comment,
    )
    notification_service.send(current_user.employeeId, "approval", {"workflowId": workflow_id, "status": result["status"]})
    return result
