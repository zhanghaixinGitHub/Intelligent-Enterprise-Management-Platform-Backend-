from app.infra.logging.logger import AppLogger


class WorkflowTemplateService:
    """Template Method: 统一审批流程执行骨架。"""

    def __init__(self) -> None:
        self._logger = AppLogger(self.__class__.__name__)

    def execute(self, workflow_id: str, action: str, comment: str | None = None) -> dict:
        self._before_validate(workflow_id, action)
        result = self._do_action(workflow_id, action, comment)
        self._after_audit(workflow_id, action, result)
        return result

    def _before_validate(self, workflow_id: str, action: str) -> None:
        self._logger.info("_before_validate", "执行审批前校验", workflow_id=workflow_id, action=action)

    def _do_action(self, workflow_id: str, action: str, comment: str | None) -> dict:
        return {"workflowId": workflow_id, "status": "approved" if action == "approve" else "running", "comment": comment}

    def _after_audit(self, workflow_id: str, action: str, result: dict) -> None:
        self._logger.info("_after_audit", "记录审批审计日志", workflow_id=workflow_id, action=action, result=result)
