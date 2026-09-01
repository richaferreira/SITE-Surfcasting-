from fastapi import APIRouter

from app.api.v1.routes.admin_beaches import router as admin_beaches_router
from app.api.v1.routes.admin_fishing_points import router as admin_fishing_points_router
from app.api.v1.routes.admin_media import router as admin_media_router
from app.api.v1.routes.admin_monitoring import router as admin_monitoring_router
from app.api.v1.routes.admin_posts import router as admin_posts_router
from app.api.v1.routes.auth import router as auth_router
from app.api.v1.routes.beaches import router as beaches_router
from app.api.v1.routes.fishing_points import router as fishing_points_router
from app.api.v1.routes.posts import router as posts_router
from app.api.v1.routes.recommendations import router as recommendations_router
from app.api.v1.routes.score import router as score_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(beaches_router)
api_router.include_router(admin_beaches_router)
api_router.include_router(fishing_points_router)
api_router.include_router(admin_fishing_points_router)
api_router.include_router(admin_media_router)
api_router.include_router(admin_monitoring_router)
api_router.include_router(posts_router)
api_router.include_router(recommendations_router)
api_router.include_router(admin_posts_router)
api_router.include_router(score_router)
