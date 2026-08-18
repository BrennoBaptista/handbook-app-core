"""RN-OBS-003 — Correlação Obrigatória: propagação de trace_id por
requisição, tanto em `request.state` (para o exception handler) quanto num
contextvar (para qualquer log estruturado emitido durante a requisição,
mesmo em código sem acesso ao objeto Request — shared/logging/context.py)."""

from __future__ import annotations

import uuid
from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from platform_core.shared.logging.context import trace_id_var

_TRACE_ID_HEADER = "x-trace-id"


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        trace_id = request.headers.get(_TRACE_ID_HEADER, str(uuid.uuid4()))
        request.state.trace_id = trace_id
        token = trace_id_var.set(trace_id)

        try:
            response = await call_next(request)
        finally:
            trace_id_var.reset(token)

        response.headers[_TRACE_ID_HEADER] = trace_id
        return response
