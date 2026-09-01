from time import perf_counter

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.exceptions import (
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    DependencyUnavailableError,
    NotFoundError,
    PayloadTooLargeError,
    RateLimitExceededError,
    UnprocessableError,
)
from app.monitoring import monitoring_registry


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
    settings.media_root.mkdir(parents=True, exist_ok=True)
    application.mount(
        settings.media_url_prefix,
        StaticFiles(directory=settings.media_root, check_dir=False),
        name="media",
    )

    @application.middleware("http")
    async def collect_request_metrics(request: Request, call_next):
        started_at = perf_counter()
        response_status = status.HTTP_500_INTERNAL_SERVER_ERROR
        try:
            response = await call_next(request)
            response_status = response.status_code
            return response
        finally:
            monitoring_registry.record_http(
                response_status,
                (perf_counter() - started_at) * 1000,
            )

    error_statuses = {
        AuthenticationError: status.HTTP_401_UNAUTHORIZED,
        AuthorizationError: status.HTTP_403_FORBIDDEN,
        ConflictError: status.HTTP_409_CONFLICT,
        NotFoundError: status.HTTP_404_NOT_FOUND,
        UnprocessableError: status.HTTP_422_UNPROCESSABLE_ENTITY,
        PayloadTooLargeError: status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
        DependencyUnavailableError: status.HTTP_503_SERVICE_UNAVAILABLE,
        RateLimitExceededError: status.HTTP_429_TOO_MANY_REQUESTS,
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
                    else {"Retry-After": "60"}
                    if response_status == status.HTTP_429_TOO_MANY_REQUESTS
                    else None
                ),
            )

    @application.get("/health", tags=["Health"])
    def health_check() -> dict[str, str]:
        return {"status": "ok", "environment": settings.app_env}

    return application


app = create_app()
