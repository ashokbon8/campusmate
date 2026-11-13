"""Vercel deployment configuration.

Locks in the services/routing contract: the backend is served under the public
``/api`` prefix (which the platform forwards without stripping) and the
frontend receives everything else.
"""

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
VERCEL_JSON = json.loads((REPO_ROOT / "vercel.json").read_text())


def test_both_services_are_declared():
    services = VERCEL_JSON["services"]
    assert set(services) == {"backend", "frontend"}
    assert services["backend"]["root"] == "backend"
    assert services["backend"]["framework"] == "fastapi"
    assert services["frontend"]["root"] == "frontend"
    assert services["frontend"]["framework"] == "vite"


def test_rewrites_route_api_to_backend_and_everything_else_to_frontend():
    rewrites = VERCEL_JSON["rewrites"]
    assert rewrites[0] == {
        "source": "/api/(.*)",
        "destination": {"service": "backend"},
    }
    # The catch-all must come last so it never shadows the /api rule.
    assert rewrites[-1] == {
        "source": "/(.*)",
        "destination": {"service": "frontend"},
    }


def test_backend_serves_under_the_public_api_prefix():
    from fastapi.testclient import TestClient

    from app.main import create_app

    # On Vercel the platform forwards the original path ("/api/health") and does
    # not set an ASGI root_path, so the app must strip the prefix itself.
    with TestClient(create_app(root_path="/api")) as client:
        assert client.get("/api/health").status_code == 200
        assert client.get("/api/meta/categories").status_code == 200
        assert client.post(
            "/api/chat", json={"question": "When is my exam?", "context": {}}
        ).status_code == 200


def test_vercel_env_defaults_to_writable_paths_and_api_prefix():
    """Vercel has a read-only filesystem; the app must default to /tmp."""
    import json
    import os
    import subprocess
    import sys
    import tempfile

    code = (
        "import json; from app.config import settings; "
        "print(json.dumps({'root_path': settings.root_path, "
        "'database_url': settings.database_url, 'upload_dir': settings.upload_dir}))"
    )
    env = {k: v for k, v in os.environ.items() if k not in {"DATABASE_URL", "UPLOAD_DIR", "ROOT_PATH"}}
    env["VERCEL"] = "1"
    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=str(REPO_ROOT / "backend"),
        env=env,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout.strip().splitlines()[-1])
    scratch = tempfile.gettempdir()
    assert data["root_path"] == "/api"
    assert data["database_url"] == f"sqlite:///{scratch}/campusmate.db"
    assert data["upload_dir"] == os.path.join(scratch, "campusmate-documents")
