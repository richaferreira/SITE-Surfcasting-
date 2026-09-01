from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.exceptions import (
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    NotFoundError,
)


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="Telemetria oceanográfica e Score de Pesca explicável.",
        debug=settings.app_debug,
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )
    application.include_router(api_router, prefix=settings.api_v1_prefix)

    error_statuses = {
        AuthenticationError: status.HTTP_401_UNAUTHORIZED,
        AuthorizationError: status.HTTP_403_FORBIDDEN,
        ConflictError: status.HTTP_409_CONFLICT,
        NotFoundError: status.HTTP_404_NOT_FOUND,
    }

    for exception_type, status_code in error_statuses.items():

        @application.exception_handler(exception_type)
        async def handle_application_error(
            request: Request,
            exc: Exception,
            response_status: int = status_code,
        ) -> JSONResponse:
            del request
            return JSONResponse(
                status_code=response_status,
                content={"detail": str(exc)},
                headers=(
                    {"WWW-Authenticate": "Bearer"}
                    if response_status == status.HTTP_401_UNAUTHORIZED
                    else None
                ),
            )

    @application.get("/health", tags=["Health"])
    def health_check() -> dict[str, str]:
        return {"status": "ok", "environment": settings.app_env}

    return application


app = create_app()
