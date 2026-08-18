"""Formato de log estruturado (OBS-001, Seção 4)."""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime

from platform_core.shared.logging.context import trace_id_var

# Campos correlacionais que, quando presentes no LogRecord (via `extra=`),
# entram no payload — nenhum é obrigatório individualmente (OBS-001, Seção 4:
# "os demais deverão ser incluídos sempre que aplicáveis ao contexto").
_OPTIONAL_FIELDS = ("correlation_id", "request_id", "user_id", "tenant_id")


class JsonFormatter(logging.Formatter):
    """Nunca inclua senhas, tokens ou dados sensíveis via `extra=` em nenhum
    log — RN-OBS-002, sem exceção (OBS-001, Seção 6)."""

    def __init__(self, service_name: str, environment: str) -> None:
        super().__init__()
        self._service_name = service_name
        self._environment = environment

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, object] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "level": record.levelname,
            "service": self._service_name,
            "environment": self._environment,
            "event": getattr(record, "event", record.name),
            "message": record.getMessage(),
        }

        trace_id = trace_id_var.get()
        if trace_id is not None:
            payload["trace_id"] = trace_id

        for field in _OPTIONAL_FIELDS:
            value = getattr(record, field, None)
            if value is not None:
                payload[field] = value

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload)
