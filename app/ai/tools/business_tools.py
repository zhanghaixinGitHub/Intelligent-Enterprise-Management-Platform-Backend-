from typing import Any


class BusinessTools:
    # 这里将各业务动作统一抽象为工具函数，便于后续切换真实服务实现。
    def leave_tool(self, payload: dict[str, Any]) -> dict[str, Any]:
        return {"accepted": True, "bizType": "leave", "payload": payload}

    def reimburse_tool(self, payload: dict[str, Any]) -> dict[str, Any]:
        return {"accepted": True, "bizType": "reimburse", "payload": payload}

    def workflow_tool(self, payload: dict[str, Any]) -> dict[str, Any]:
        return {"accepted": True, "bizType": "workflow", "payload": payload}

    def query_tool(self, payload: dict[str, Any]) -> dict[str, Any]:
        return {"accepted": True, "bizType": "query", "payload": payload}

    def knowledge_tool(self, payload: dict[str, Any]) -> dict[str, Any]:
        return {"accepted": True, "bizType": "knowledge", "payload": payload}

    def minutes_tool(self, payload: dict[str, Any]) -> dict[str, Any]:
        return {"accepted": True, "bizType": "minutes", "payload": payload}
