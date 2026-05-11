from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def main() -> None:
    admin_login = client.post("/api/v1/auth/login", json={"username": "admin", "password": "Admin@123"})
    assert admin_login.status_code == 200, admin_login.text
    admin_token = admin_login.json()["accessToken"]

    admin_me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {admin_token}"})
    assert admin_me.status_code == 200, admin_me.text
    admin_menu_keys = [item["key"] for item in admin_me.json()["menus"]]
    assert "dashboard" in admin_menu_keys and "workflow" in admin_menu_keys

    hr_login = client.post("/api/v1/auth/login", json={"username": "hr", "password": "Hr@123456"})
    assert hr_login.status_code == 200, hr_login.text
    hr_token = hr_login.json()["accessToken"]

    hr_forbidden = client.post(
        "/api/v1/workflows/wf-demo-001/approve",
        json={"action": "approve"},
        headers={"Authorization": f"Bearer {hr_token}"},
    )
    assert hr_forbidden.status_code == 403, hr_forbidden.text

    attendance_ok = client.get(
        "/api/v1/attendance/monthly-summary",
        params={"month": "2026-05"},
        headers={"Authorization": f"Bearer {hr_token}"},
    )
    assert attendance_ok.status_code == 200, attendance_ok.text

    print("AuthPermissionsSmoke.main >>> 登录与权限烟雾测试通过")


if __name__ == "__main__":
    main()


