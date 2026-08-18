from __future__ import annotations

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from platform_core.modules.auth.application.use_cases.validate_access_token import (
    ValidateAccessToken,
)
from platform_core.modules.auth.domain.exceptions import InsufficientRoleError
from platform_core.modules.auth.domain.value_objects.authenticated_user import (
    AuthenticatedUser,
)

_bearer_scheme = HTTPBearer(auto_error=True)


def _get_validate_access_token_use_case(request: Request) -> ValidateAccessToken:
    """Resolvido pelo Composition Root (bootstrap/container.py) em
    app.state — RA-005, Capítulo 67."""
    use_case: ValidateAccessToken = request.app.state.validate_access_token_use_case
    return use_case


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
    use_case: ValidateAccessToken = Depends(_get_validate_access_token_use_case),
) -> AuthenticatedUser:
    return await use_case.execute(credentials.credentials)


def require_roles(*roles: str):
    """RBAC (SEC-001, Seção 5). Autorização em nível de objeto específico
    (RN-SEC-003) não é coberta aqui — cada endpoint que acessa um recurso
    específico deverá validar, além da role, se o usuário tem direito sobre
    aquele recurso (ex.: dono do pedido)."""

    async def _dependency(
        user: AuthenticatedUser = Depends(get_current_user),
    ) -> AuthenticatedUser:
        if not user.has_any_role(*roles):
            raise InsufficientRoleError(required_roles=list(roles))
        return user

    return _dependency
