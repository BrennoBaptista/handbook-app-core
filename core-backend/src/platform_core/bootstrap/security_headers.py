"""Headers de segurança (SEC-001, Seção 7) aplicados a toda resposta."""

from __future__ import annotations

from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

_STATIC_HEADERS = {
    "Content-Security-Policy": "default-src 'self'",
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "geolocation=(), camera=(), microphone=()",
}

# HSTS só faz sentido sob HTTPS real — aplicado apenas quando a requisição já
# chegou via TLS (ex.: atrás do Load Balancer/CDN de RA-006, Seção 10).
# Emiti-lo sobre HTTP simples (desenvolvimento local) não tem efeito.
_HSTS_HEADER = "Strict-Transport-Security"
_HSTS_VALUE = "max-age=31536000; includeSubDomains"


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        response = await call_next(request)
        for header, value in _STATIC_HEADERS.items():
            response.headers.setdefault(header, value)
        if request.url.scheme == "https":
            response.headers.setdefault(_HSTS_HEADER, _HSTS_VALUE)
        return response
