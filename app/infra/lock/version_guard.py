from dataclasses import dataclass


@dataclass
class VersionCheckResult:
    ok: bool
    message: str


def check_version(expected: int, current: int) -> VersionCheckResult:
    if expected != current:
        return VersionCheckResult(False, f"version conflict: expected={expected}, current={current}")
    return VersionCheckResult(True, "ok")
