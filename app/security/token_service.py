from __future__ import annotations

import base64
import hashlib
import hmac
import json
from datetime import UTC, datetime, timedelta
from typing import Any

from app.infra.config.settings import settings


class TokenService:
    """轻量级令牌服务。

    说明：
    1. 当前项目还未引入 JWT 依赖，因此使用标准库实现一个可验证签名的 Bearer Token。
    2. 这里采用“适配器模式”，把令牌的生成与校验收口到单独服务，后续若切换为 JWT / OAuth2，
       只需要替换本类实现，业务路由与中间件不需要大改。
    """

    def __init__(self, secret: str, expire_minutes: int) -> None:
        self._secret = secret.encode("utf-8")
        self._expire_minutes = expire_minutes

    @staticmethod
    def _b64_encode(raw: bytes) -> str:
        return base64.urlsafe_b64encode(raw).decode("utf-8").rstrip("=")

    @staticmethod
    def _b64_decode(raw: str) -> bytes:
        padding = "=" * (-len(raw) % 4)
        return base64.urlsafe_b64decode(f"{raw}{padding}".encode("utf-8"))

    def _sign(self, payload_segment: str) -> str:
        digest = hmac.new(self._secret, payload_segment.encode("utf-8"), hashlib.sha256).digest()
        return self._b64_encode(digest)

    def create_token(self, payload: dict[str, Any]) -> dict[str, Any]:
        expires_at = datetime.now(UTC) + timedelta(minutes=self._expire_minutes)
        enriched_payload = {
            **payload,
            "exp": int(expires_at.timestamp()),
            "iat": int(datetime.now(UTC).timestamp()),
        }
        payload_segment = self._b64_encode(json.dumps(enriched_payload, separators=(",", ":")).encode("utf-8"))
        signature_segment = self._sign(payload_segment)
        return {
            "accessToken": f"{payload_segment}.{signature_segment}",
            "tokenType": "Bearer",
            "expiresIn": self._expire_minutes * 60,
            "expiresAt": expires_at.isoformat(),
        }

    def verify_token(self, token: str) -> dict[str, Any]:
        try:
            payload_segment, signature_segment = token.split(".", 1)
        except ValueError as exc:
            raise ValueError("token 格式非法") from exc

        expected_signature = self._sign(payload_segment)
        if not hmac.compare_digest(signature_segment, expected_signature):
            raise ValueError("token 签名校验失败")

        payload = json.loads(self._b64_decode(payload_segment).decode("utf-8"))
        expires_at = int(payload.get("exp", 0))
        if expires_at <= int(datetime.now(UTC).timestamp()):
            raise ValueError("token 已过期")
        return payload


# 单例即可满足当前场景，避免每次请求重复构建实例。
token_service = TokenService(
    secret=settings.auth_token_secret,
    expire_minutes=settings.auth_token_expire_minutes,
)

