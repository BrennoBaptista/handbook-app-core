from __future__ import annotations

from platform_core.modules.auth.application.ports.token_validator_port import (
    TokenValidatorPort,
)
from platform_core.modules.auth.domain.value_objects.authenticated_user import (
    AuthenticatedUser,
)


class ValidateAccessToken:
    """Depende apenas do Port (RA-005, Seção 104) — nunca de uma implementação
    concreta de infrastructure."""

    def __init__(self, token_validator: TokenValidatorPort) -> None:
        self._token_validator = token_validator

    async def execute(self, token: str) -> AuthenticatedUser:
        return await self._token_validator.validate(token)
