from __future__ import annotations

from abc import ABC, abstractmethod

from platform_core.modules.auth.domain.value_objects.authenticated_user import (
    AuthenticatedUser,
)


class TokenValidatorPort(ABC):
    """Port (RA-005, Seção 104) — toda dependência externa de validação de
    identidade deverá passar por esta interface, nunca por uma implementação
    concreta importada diretamente na camada de aplicação."""

    @abstractmethod
    async def validate(self, token: str) -> AuthenticatedUser:
        """Deverá levantar platform_core.modules.auth.domain.exceptions.
        InvalidTokenError quando o token não puder ser validado, por
        qualquer motivo."""
