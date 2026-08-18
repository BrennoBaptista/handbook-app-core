from __future__ import annotations

from platform_core.shared.errors import AppError


class InvalidTokenError(AppError):
    """Access token ausente, expirado, malformado ou com assinatura inválida."""

    def __init__(self, reason: str) -> None:
        super().__init__(
            code="INVALID_TOKEN",
            message="The provided access token is invalid or expired.",
            status_code=401,
            details={"reason": reason},
        )


class InsufficientRoleError(AppError):
    """Usuário autenticado, mas sem nenhuma das roles exigidas pelo endpoint
    (SEC-001, Seção 5 — RBAC). Autorização em nível de objeto específico
    (RN-SEC-003) continua sendo responsabilidade de cada endpoint, não desta
    dependência genérica de role."""

    def __init__(self, required_roles: list[str]) -> None:
        super().__init__(
            code="INSUFFICIENT_ROLE",
            message="You do not have permission to perform this action.",
            status_code=403,
            details={"required_roles": required_roles},
        )
