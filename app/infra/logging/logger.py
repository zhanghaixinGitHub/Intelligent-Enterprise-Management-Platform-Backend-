import logging
from typing import Any


_LOG_FORMAT = "%(asctime)s %(levelname)s %(message)s"
logging.basicConfig(level=logging.INFO, format=_LOG_FORMAT)


class AppLogger:
    """统一日志输出组件，强制格式：类名.方法名 >>> 日志信息"""

    def __init__(self, class_name: str) -> None:
        self._class_name = class_name
        self._logger = logging.getLogger(class_name)

    def info(self, method_name: str, message: str, **kwargs: Any) -> None:
        suffix = f" | {kwargs}" if kwargs else ""
        self._logger.info("%s.%s >>> %s%s", self._class_name, method_name, message, suffix)

    def error(self, method_name: str, message: str, **kwargs: Any) -> None:
        suffix = f" | {kwargs}" if kwargs else ""
        self._logger.error("%s.%s >>> %s%s", self._class_name, method_name, message, suffix)
