"""Run the built website and API together for the complete local download."""
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .main import create_app


def create_local_app(frontend_dir: Path | None = None) -> FastAPI:
    folder = frontend_dir or Path(__file__).resolve().parents[2] / 'frontend/dist'
    if not (folder / 'index.html').is_file():
        raise RuntimeError('The built website is missing. Extract the full final ZIP, or build frontend with npm run build.')
    api = create_app(root_path='')

    @asynccontextmanager
    async def lifespan(app):
        async with api.router.lifespan_context(api):
            yield

    app = FastAPI(title='CampusMate local website',docs_url=None,redoc_url=None,openapi_url=None,lifespan=lifespan)
    app.mount('/api',api)
    app.mount('/',StaticFiles(directory=str(folder),html=True),name='website')
    return app
