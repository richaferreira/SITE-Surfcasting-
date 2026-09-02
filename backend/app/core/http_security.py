from hmac import compare_digest

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core.config import get_settings


settings = get_settings()
SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}
PUBLIC_AUTH_SUFFIXES = {
    "/auth/login",
    "/auth/register",
    "/auth/forgot-password",
    "/auth/reset-password",
    "/auth/verify-email",
    "/auth/resend-verification",
}


class CSRFMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        if request.method in SAFE_METHODS:
            return await call_next(request)

        if any(request.url.path.endswith(suffix) for suffix in PUBLIC_AUTH_SUFFIXES):
            return await call_next(request)

        has_auth_cookie = bool(
            request.cookies.get(settings.access_cookie_name)
            or request.cookies.get(settings.refresh_cookie_name)
        )
        if not has_auth_cookie:
            return await call_next(request)

        cookie_token = request.cookies.get(settings.csrf_cookie_name, "")
        header_token = request.headers.get(settings.csrf_header_name, "")
        if not cookie_token or not header_token or not compare_digest(cookie_token, header_token):
            return JSONResponse(status_code=403, content={"detail": "Token CSRF ausente ou inválido."})
        return await call_next(request)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=(self)")
        response.headers.setdefault("Cross-Origin-Opener-Policy", "same-origin")
        response.headers.setdefault("Content-Security-Policy", "default-src 'none'; frame-ancestors 'none'")
        if settings.auth_cookie_secure:
            response.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
        return response
