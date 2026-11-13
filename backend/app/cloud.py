"""Production entry point for the combined website and API."""
from .config import settings
from .local import create_local_app


def create_cloud_app():
    if not settings.database_url.startswith(("postgresql://", "postgresql+psycopg2://")):
        raise RuntimeError("Cloud deployment requires DATABASE_URL for a persistent PostgreSQL database.")
    if len(settings.secret_key) < 32 or settings.secret_key == "change-me-in-production":
        raise RuntimeError("Set a private SECRET_KEY with at least 32 characters in your hosting settings.")
    if not settings.seed_admin_email or len(settings.seed_admin_password) < 12:
        raise RuntimeError("Set SEED_ADMIN_EMAIL and SEED_ADMIN_PASSWORD (at least 12 characters) in your hosting settings.")
    return create_local_app()
