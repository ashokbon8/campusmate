"""Host the complete app on the port supplied by the cloud platform."""
from pathlib import Path
import os
import sys


def main():
    root = Path(__file__).resolve().parents[1]
    os.chdir(root / "backend")
    sys.path.insert(0, str(root / "backend"))
    import uvicorn

    uvicorn.run(
        "app.cloud:create_cloud_app", factory=True, host="0.0.0.0",
        port=int(os.environ.get("PORT", "10000")), workers=1,
    )


if __name__ == "__main__":
    main()
