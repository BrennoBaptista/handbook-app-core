"""Contrato de erro compartilhado entre todos os módulos (API-001, Seção 7).

Componente genuinamente transversal e independente de domínio (RA-005,
Seção 65.1). Nenhuma regra de negócio pertence aqui.
"""

from __future__ import annotations

from typing import Any


class AppError(Exception):
    """Base para qualquer erro que deva ser traduzido para o contrato HTTP de
    API-001, Seção 7. Módulos de domínio deverão levantar subclasses desta
    exceção (nunca a exceção genérica do Python) para que o exception handler
    central (bootstrap/error_handling.py) saiba como respondê-las."""

    def __init__(
        self,
        code: str,
        message: str,
        status_code: int,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)
