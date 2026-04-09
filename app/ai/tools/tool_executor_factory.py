from app.ai.tools.business_tools import BusinessTools


class ToolExecutorFactory:
    def __init__(self) -> None:
        self._tools = BusinessTools()

    def get(self, intent: str):
        # 工厂模式：根据意图名称分发对应执行器，避免上层编排器感知具体实现。
        mapping = {
            "leave": self._tools.leave_tool,
            "reimburse": self._tools.reimburse_tool,
            "workflow": self._tools.workflow_tool,
            "query": self._tools.query_tool,
            "knowledge": self._tools.knowledge_tool,
            "minutes": self._tools.minutes_tool,
        }
        return mapping.get(intent)
