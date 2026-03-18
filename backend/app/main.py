from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import async_session
from app.api.router import api_router
from app.seed import seed_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Seed database on startup if empty
    async with async_session() as db:
        try:
            await seed_database(db)
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
