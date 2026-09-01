from fastapi import APIRouter

from app.api.v1.routes.score import router as score_router

api_router = APIRouter()
api_router.include_router(score_router)
