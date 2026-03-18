from fastapi import APIRouter

from app.api.health import router as health_router
from app.api.auth import router as auth_router
from app.api.sections import router as sections_router
from app.api.factors import router as factors_router
from app.api.score_ranges import router as score_ranges_router
from app.api.governance import router as governance_router
from app.api.risk_flags import router as risk_flags_router
from app.api.sizing import router as sizing_router

api_router = APIRouter(prefix="/api")

api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(sections_router)
api_router.include_router(factors_router)
api_router.include_router(score_ranges_router)
api_router.include_router(governance_router)
api_router.include_router(risk_flags_router)
api_router.include_router(sizing_router)
