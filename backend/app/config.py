"""Application settings.

All configuration is read from environment variables so that no secrets are
ever committed to the repository. See ``.env.example`` for the full list.
"""

import os
import tempfile
from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Vercel Functions run on a read-only filesystem with a writable /tmp scratch
# space, and their working directory is not writable. When we detect a Vercel
# deployment (or a non-writable working directory) the writable defaults below
# move to the system temp directory so the app boots. Override DATABASE_URL /
# UPLOAD_DIR for persistent storage (see docs/SETUP.md).
_ON_VERCEL = bool(os.getenv("VERCEL") or os.getenv("VERCEL_ENV"))
_SCRATCH_DIR = tempfile.gettempdir()
_USE_SCRATCH = _ON_VERCEL or not os.access(os.getcwd(), os.W_OK)


def _default_database_url() -> str:
    if _USE_SCRATCH:
        return f"sqlite:///{_SCRATCH_DIR}/campusmate.db"
    return "sqlite:///./campusmate.db"


def _default_upload_dir() -> str:
    if _USE_SCRATCH:
        return os.path.join(_SCRATCH_DIR, "campusmate-documents")
    return "./storage/documents"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "CampusMate API"
    environment: str = "development"
    campusmate_dataset: str = "jscoe"  # jscoe | demo | empty

    # --- Public path prefix -------------------------------------------------
    # Set to the public mount path when the API is served behind a gateway that
    # forwards the prefix (e.g. the Vercel services rewrite "/api/(.*)" ->
    # backend). Starlette strips ``root_path`` before matching routes, so the
    # OpenAPI docs and citation ``open_url`` links stay correct. Defaults to
    # /api on Vercel; empty elsewhere, where nginx strips /api itself.
    root_path: str = "/api" if _ON_VERCEL else ""

    # --- Database -----------------------------------------------------------
    # Defaults to a local SQLite file so the project runs with zero setup.
    # docker-compose overrides this with a PostgreSQL + pgvector URL.
    database_url: str = _default_database_url()

    @field_validator("database_url")
    @classmethod
    def _normalize_database_url(cls, value: str) -> str:
        # Some providers hand out "postgres://" URLs, which SQLAlchemy 2.x no
        # longer recognises (it expects "postgresql://").
        if value.startswith("postgres://"):
            return "postgresql://" + value[len("postgres://") :]
        return value

    # --- Auth ---------------------------------------------------------------
    # CHANGE THIS IN PRODUCTION. Kept here only so the demo runs out of the box.
    secret_key: str = "change-me-in-production"
    access_token_expire_minutes: int = 60 * 8

    # --- Seeded administrator (private) -------------------------------------
    # The admin account is created from these values on first start. The
    # password defaults to empty, so a deployment starts with NO built-in admin
    # until you set SEED_ADMIN_PASSWORD in the environment (e.g. Vercel project
    # settings). No credential is committed to the repository, and these values
    # are never exposed through the public API or UI.
    seed_admin_email: str = "admin@campusmate.demo"
    seed_admin_password: str = ""
    seed_admin_name: str = "CampusMate Administrator"

    # --- Model adapters -----------------------------------------------------
    # When no API key is configured the app falls back to deterministic,
    # offline implementations so the demo never depends on a paid service.
    llm_provider: str = "stub"  # "stub" | "openai"
    llm_base_url: str = "https://api.openai.com/v1"
    llm_model: str = "gpt-4o-mini"
    llm_api_key: str = ""

    embedding_provider: str = "hashing"  # "hashing" | "openai"
    embedding_base_url: str = "https://api.openai.com/v1"
    embedding_model: str = "text-embedding-3-small"
    embedding_api_key: str = ""
    embedding_dim: int = 384

    # --- Retrieval ----------------------------------------------------------
    retrieval_top_k: int = 5
    # Minimum hybrid score for a passage to be considered "supporting evidence".
    retrieval_min_score: float = 0.08
    # Minimum fraction of the question's content words a passage must contain to
    # be treated as evidence. Prevents answers built on one incidental word.
    retrieval_min_coverage: float = 0.5

    # --- Uploads ------------------------------------------------------------
    upload_dir: str = _default_upload_dir()
    max_upload_mb: int = 20

    # --- CORS ---------------------------------------------------------------
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
