from dataclasses import dataclass, field
from pathlib import Path
import os
from dotenv import load_dotenv


load_dotenv()

# 项目根目录（settings.py 所在目录的上两级）
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent


def _parse_csv_env(value: str | None, default: list[str]) -> list[str]:
    """
    解析逗号分隔的环境变量，统一裁剪空白并过滤空值。
    允许使用英文逗号或分号，便于不同习惯的配置方式。
    """
    if not value:
        return default
    normalized = value.replace(";", ",")
    return [item.strip() for item in normalized.split(",") if item.strip()]


def _parse_bool_env(value: str | None, default: bool) -> bool:
    """
    将环境变量转换为布尔值，兼容常见写法。
    """
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "AI Enterprise Platform")
    app_env: str = os.getenv("APP_ENV", "dev")
    app_host: str = os.getenv("APP_HOST", "0.0.0.0")
    app_port: int = int(os.getenv("APP_PORT", "8000"))
    auth_token_secret: str = os.getenv("AUTH_TOKEN_SECRET", "ai-enterprise-demo-secret")
    auth_token_expire_minutes: int = int(os.getenv("AUTH_TOKEN_EXPIRE_MINUTES", "480"))
    sqlite_db_path: str = os.getenv(
        "SQLITE_DB_PATH",
        str(PROJECT_ROOT / "data" / "ai_enterprise.db"),
    )
    workflow_center_base_url: str = os.getenv("WORKFLOW_CENTER_BASE_URL", "http://127.0.0.1:8081")
    workflow_center_internal_token: str = os.getenv("WORKFLOW_CENTER_INTERNAL_TOKEN", "change-me-in-prod")
    workflow_center_connect_timeout_seconds: float = float(os.getenv("WORKFLOW_CENTER_CONNECT_TIMEOUT_SECONDS", "3"))
    workflow_center_read_timeout_seconds: float = float(os.getenv("WORKFLOW_CENTER_READ_TIMEOUT_SECONDS", "10"))
    openai_base_url: str = os.getenv("OPENAI_BASE_URL", "https://api.openai-proxy.org/v1")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    embedding_model: str = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    rag_store_dir: str = os.getenv("RAG_STORE_DIR", str(PROJECT_ROOT / "data" / "rag"))
    cors_allow_origins: list[str] = field(
        default_factory=lambda: _parse_csv_env(
            os.getenv("CORS_ALLOW_ORIGINS"),
            [
                "http://localhost:5173",
                "http://127.0.0.1:5173",
                "http://localhost:5175",
                "http://127.0.0.1:5175",
                "http://localhost:8080",
                "http://127.0.0.1:8080",
                "http://localhost:3000",
                "http://127.0.0.1:3000",
            ],
        )
    )
    cors_allow_methods: list[str] = field(
        default_factory=lambda: _parse_csv_env(
            os.getenv("CORS_ALLOW_METHODS"),
            ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        )
    )
    cors_allow_headers: list[str] = field(
        default_factory=lambda: _parse_csv_env(
            os.getenv("CORS_ALLOW_HEADERS"),
            ["Authorization", "Content-Type", "X-Requested-With"],
        )
    )
    cors_expose_headers: list[str] = field(
        default_factory=lambda: _parse_csv_env(
            os.getenv("CORS_EXPOSE_HEADERS"),
            ["X-Request-Id"],
        )
    )
    cors_allow_credentials: bool = _parse_bool_env(os.getenv("CORS_ALLOW_CREDENTIALS"), True)


settings = Settings()
