from app.infra.logging.logger import AppLogger


class QueryExecutor:
    """受控 NL2Query 执行器：仅允许白名单查询类型。"""

    def __init__(self) -> None:
        self._logger = AppLogger(self.__class__.__name__)
        self._whitelist = {"overtime_rank", "monthly_attendance"}

    def run(self, question: str) -> dict:
        query_type = "overtime_rank" if "加班" in question else "monthly_attendance"
        if query_type not in self._whitelist:
            return {"status": "forbidden", "summary": "query type forbidden", "data": {}}
        self._logger.info("run", "执行受控查询", query_type=query_type, question=question)
        return {"status": "success", "summary": "查询执行成功", "data": {"queryType": query_type, "rows": []}}
