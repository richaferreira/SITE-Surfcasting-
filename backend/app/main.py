from pathlib import Path

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.http_security import CSRFMiddleware, SecurityHeadersMiddleware
from app.services.health import check_dependencies
from app.services.observability import RequestObservabilityMiddleware


def create_app() -> FastAPI:
    settings = get_settings()
    settings.validate_runtime()

    application = FastAPI(
        title=settings.app_name,
        version="0.4.0",
        description="Telemetria oceanográfica, Score de Pesca explicável e comunidade Surfcasting.",
        debug=settings.app_debug,
    )

    application.add_middleware(SecurityHeadersMiddleware)
    application.add_middleware(CSRFMiddleware)
    application.add_middleware(RequestObservabilityMiddleware)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    media_root = Path(settings.media_root).resolve()
    media_root.mkdir(parents=True, exist_ok=True)
    application.mount(
        settings.media_public_url,
        StaticFiles(directory=str(media_root), check_dir=False),
        name="media",
    )

    application.include_router(api_router, prefix=settings.api_v1_prefix)

    @application.get("/health", tags=["Health"])
    @application.get("/health/live", tags=["Health"])
    def health_check() -> dict[str, str]:
        return {"status": "ok", "environment": settings.app_env}

    @application.get("/health/ready", tags=["Health"])
    def readiness_check() -> JSONResponse:
        dependencies = check_dependencies()
        return JSONResponse(
            status_code=status.HTTP_200_OK if dependencies.ready else status.HTTP_503_SERVICE_UNAVAILABLE,
            content=dependencies.as_dict(),
        )

    return application


app = create_app()
