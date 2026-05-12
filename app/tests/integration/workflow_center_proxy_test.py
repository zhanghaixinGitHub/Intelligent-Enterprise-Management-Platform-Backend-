from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi.testclient import TestClient

from app.api.routes.workflow_routes import workflow_center_gateway_service
from app.main import app


client = TestClient(app)


def _login(username: str, password: str) -> str:
    response = client.post("/api/v1/auth/login", json={"username": username, "password": password})
    assert response.status_code == 200, response.text
    return response.json()["accessToken"]


def test_employee_can_start_process_via_python_gateway(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def fake_start_process_instance(*, current_user, payload):
        captured["employeeId"] = current_user.employeeId
        captured["processDefinitionKey"] = payload.processDefinitionKey
        captured["managerAssignee"] = payload.managerAssignee
        return {
            "processDefinitionKey": payload.processDefinitionKey,
            "processInstanceId": "pi-demo-001",
            "businessKey": payload.businessKey,
            "processStatus": "RUNNING",
            "currentTaskNames": ["直属主管审批"],
        }

    monkeypatch.setattr(workflow_center_gateway_service, "start_process_instance", fake_start_process_instance)
    token = _login("employee", "Employee@123")

    response = client.post(
        "/api/v1/workflows/process-instances/start",
        json={
            "processDefinitionKey": "leaveApproval",
            "managerAssignee": "employee-003",
            "hrAssignee": "employee-002",
            "businessKey": "LEAVE-PY-001",
            "title": "员工请假申请",
            "variables": {"leaveDays": 2},
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200, response.text
    assert captured == {
        "employeeId": "employee-004",
        "processDefinitionKey": "leaveApproval",
        "managerAssignee": "employee-003",
    }
    assert response.json()["processInstanceId"] == "pi-demo-001"
    assert response.json()["currentTaskNames"] == ["直属主管审批"]


def test_manager_can_query_my_tasks_via_python_gateway(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def fake_list_my_tasks(*, current_user):
        captured["employeeId"] = current_user.employeeId
        return [
            {
                "taskId": "task-demo-001",
                "taskName": "直属主管审批",
                "taskDefinitionKey": "managerApproveTask",
                "assignee": current_user.employeeId,
                "processInstanceId": "pi-demo-001",
                "processDefinitionId": "leaveApproval:1:test",
                "createTime": "2026-05-12 10:00:00",
            }
        ]

    monkeypatch.setattr(workflow_center_gateway_service, "list_my_tasks", fake_list_my_tasks)
    token = _login("manager", "Manager@123")

    response = client.get(
        "/api/v1/workflows/tasks/my",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200, response.text
    assert captured == {"employeeId": "employee-003"}
    assert response.json()["tasks"][0]["taskId"] == "task-demo-001"
    assert response.json()["tasks"][0]["assignee"] == "employee-003"


