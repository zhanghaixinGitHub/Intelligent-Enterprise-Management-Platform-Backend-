from app.infra.logging.logger import AppLogger


class MeetingMinutesService:
    def __init__(self) -> None:
        self._logger = AppLogger(self.__class__.__name__)

    def summarize(self, transcript: str) -> dict:
        self._logger.info("summarize", "生成会议纪要", transcript_length=len(transcript))
        return {
            "meetingTopic": "项目例会",
            "summary": transcript[:200],
            "actionItems": [{"task": "补充接口文档", "owner": "研发负责人", "dueDate": "2026-04-15"}],
            "decisionItems": ["按既定节奏推进 MVP 交付"],
        }
