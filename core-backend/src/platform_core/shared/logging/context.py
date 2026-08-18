"""Contexto de correlação (RN-OBS-003) disponível para qualquer código —
inclusive Use Cases que não têm acesso ao objeto Request — sem precisar
passar trace_id manualmente por toda a cadeia de chamadas."""

from __future__ import annotations

from contextvars import ContextVar

trace_id_var: ContextVar[str | None] = ContextVar("trace_id", default=None)
