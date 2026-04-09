from app.infra.logging.logger import AppLogger


class NotificationService:
    def __init__(self) -> None:
        self._logger = AppLogger(self.__class__.__name__)

    def send(self, receiver_id: str, event_type: str, payload: dict) -> dict:
        self._logger.info("send", "发送通知", receiver_id=receiver_id, event_type=event_type)
        return {"receiverId": receiver_id, "eventType": event_type, "deliveryStatus": "sent", "payload": payload}
