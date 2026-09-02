from fastapi import APIRouter

from app.api.v1.routes.admin import router as admin_router
from app.api.v1.routes.auth import router as auth_router
from app.api.v1.routes.beaches import router as beaches_router
from app.api.v1.routes.community import router as community_router
from app.api.v1.routes.forecast import router as forecast_router
from app.api.v1.routes.recommendations import router as recommendations_router
from app.api.v1.routes.score import router as score_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(beaches_router)
api_router.include_router(community_router)
api_router.include_router(forecast_router)
api_router.include_router(recommendations_router)
api_router.include_router(admin_router)
api_router.include_router(score_router)
