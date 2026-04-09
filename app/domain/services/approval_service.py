from app.domain.services.workflow_template_service import WorkflowTemplateService
from app.infra.lock.version_guard import check_version


class ApprovalService:
    def __init__(self) -> None:
        self._workflow_template = WorkflowTemplateService()

    def approve(self, workflow_id: str, action: str, expected_version: int = 1, current_version: int = 1, comment: str | None = None) -> dict:
        version_check = check_version(expected_version, current_version)
        if not version_check.ok:
            return {"workflowId": workflow_id, "status": "running", "version": current_version, "message": version_check.message}
        result = self._workflow_template.execute(workflow_id, action, comment)
        return {"workflowId": workflow_id, "status": result["status"], "version": current_version + 1}
