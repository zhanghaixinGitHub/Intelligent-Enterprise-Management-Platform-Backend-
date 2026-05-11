from fastapi import APIRouter, Depends

from app.api.dependencies.security import CurrentUserContext, get_current_user
from app.api.schemas.common import ApprovalActionRequest
from app.domain.services.approval_service import ApprovalService
from app.domain.services.notification_service import NotificationService


router = APIRouter(prefix="/api/v1/workflows", tags=["workflow"])
approval_service = ApprovalService()
notification_service = NotificationService()


@router.post("/{workflow_id}/approve")
def approve_workflow(
    workflow_id: str,
    payload: ApprovalActionRequest,
    current_user: CurrentUserContext = Depends(get_current_user),
):
    result = approval_service.approve(
        workflow_id=workflow_id,
        action=payload.action,
        expected_version=1,
        current_version=1,
        comment=payload.comment,
    )
    notification_service.send(current_user.employeeId, "approval", {"workflowId": workflow_id, "status": result["status"]})
    return result
