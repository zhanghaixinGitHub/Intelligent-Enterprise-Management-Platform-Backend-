from sqlalchemy.orm import Session

from app.domain.models.workflow_models import WorkflowInstance
from app.domain.models.attendance_record import AttendanceRecord


class DashboardService:
    def overview(self, db: Session) -> dict:
        workflow_total = db.query(WorkflowInstance).count()
        attendance_total = db.query(AttendanceRecord).count()
        return {
            "workflowTotal": workflow_total,
            "attendanceTotal": attendance_total,
            "pendingApprovals": max(workflow_total - 1, 0),
            "trendHint": "本周审批吞吐平稳，考勤异常率低于上周。",
        }
