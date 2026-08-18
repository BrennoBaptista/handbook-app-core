from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class AuthenticatedUser:
    """Identidade validada a partir de um access token do Identity Provider.
    Não é uma entidade persistida — este módulo não possui tabela própria de
    usuários, pois a autenticação é delegada (ADR-021)."""

    subject: str
    username: str
    email: str | None
    roles: frozenset[str]
    raw_claims: dict[str, Any] = field(default_factory=dict, repr=False)

    def has_role(self, role: str) -> bool:
        return role in self.roles

    def has_any_role(self, *roles: str) -> bool:
        return any(role in self.roles for role in roles)
