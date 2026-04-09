from threading import Lock


class IdempotencyGuard:
    """进程内幂等键保护器，用于本地轻量场景快速防重。"""

    def __init__(self) -> None:
        self._lock = Lock()
        self._seen: set[str] = set()

    def acquire(self, key: str) -> bool:
        with self._lock:
            if key in self._seen:
                return False
            self._seen.add(key)
            return True


idempotency_guard = IdempotencyGuard()
