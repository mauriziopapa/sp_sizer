import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import async_session
from app.api.router import api_router
from app.seed import seed_database

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


def run_migrations():
    """Run Alembic migrations to head via subprocess to avoid event-loop conflicts."""
    import subprocess

    backend_dir = Path(__file__).resolve().parent.parent
    result = subprocess.run(
        ["python", "-m", "alembic", "upgrade", "head"],
        cwd=str(backend_dir),
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"alembic upgrade failed:\n{result.stderr}")
    if result.stdout:
        print(result.stdout)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Run migrations then seed
    try:
        run_migrations()
        print("Migrations applied successfully")
    except Exception as e:
        print(f"Migration failed: {e}")

    async with async_session() as db:
        try:
            await seed_database(db)
            print("Seed completed successfully")
        except Exception as e:
            print(f"Seed skipped or failed: {e}")
    yield


app = FastAPI(
    title="SOLID PROJECT Sizer",
    description="Strumento di classificazione dimensionale per progetti CRM/integrazione",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

# Serve frontend static files in production
if STATIC_DIR.is_dir():
    app.mount("/assets", StaticFiles(directory=STATIC_DIR / "assets"), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(request: Request, full_path: str):
        """Serve the SPA index.html for all non-API routes."""
        file_path = STATIC_DIR / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(STATIC_DIR / "index.html")
