from __future__ import annotations

import time
from typing import Any

import httpx
from jose import JWTError, jwt

from platform_core.modules.auth.application.ports.token_validator_port import (
    TokenValidatorPort,
)
from platform_core.modules.auth.domain.exceptions import InvalidTokenError
from platform_core.modules.auth.domain.value_objects.authenticated_user import (
    AuthenticatedUser,
)


class KeycloakTokenValidator(TokenValidatorPort):
    """Valida access tokens JWT (RS256) emitidos pelo Keycloak, buscando as
    chaves públicas do realm via JWKS (RFC 7517) — nunca confiando em nenhum
    claim antes da assinatura ser verificada.

    O JWKS é cacheado em memória por processo — aceitável para um único
    realm/deployment (RA-006, Seção 17 — Single-Tenant Replicável); um cache
    compartilhado via Valkey só se justificaria com múltiplas instâncias e
    evidência de custo real de rede.
    """

    def __init__(
        self,
        issuer_url: str,
        audience: str | None,
        http_client: httpx.AsyncClient,
        jwks_cache_ttl_seconds: float = 3600.0,
    ) -> None:
        self._issuer_url = issuer_url.rstrip("/")
        self._audience = audience
        self._http_client = http_client
        self._jwks_cache_ttl_seconds = jwks_cache_ttl_seconds
        self._jwks_cache: dict[str, Any] | None = None
        self._jwks_cached_at = 0.0

    async def _get_jwks(self) -> dict[str, Any]:
        now = time.monotonic()
        is_stale = (
            self._jwks_cache is None
            or (now - self._jwks_cached_at) > self._jwks_cache_ttl_seconds
        )
        if is_stale:
            response = await self._http_client.get(
                f"{self._issuer_url}/protocol/openid-connect/certs"
            )
            response.raise_for_status()
            self._jwks_cache = response.json()
            self._jwks_cached_at = now
        assert self._jwks_cache is not None
        return self._jwks_cache

    async def validate(self, token: str) -> AuthenticatedUser:
        try:
            jwks = await self._get_jwks()
            unverified_header = jwt.get_unverified_header(token)
            signing_key = next(
                (
                    key
                    for key in jwks["keys"]
                    if key.get("kid") == unverified_header.get("kid")
                ),
                None,
            )
            if signing_key is None:
                raise InvalidTokenError(reason="signing_key_not_found")

            claims = jwt.decode(
                token,
                signing_key,
                algorithms=["RS256"],
                audience=self._audience,
                issuer=self._issuer_url,
                options={"verify_aud": self._audience is not None},
            )
        except JWTError as exc:
            raise InvalidTokenError(reason=str(exc)) from exc

        realm_access = claims.get("realm_access", {})
        roles = realm_access.get("roles", [])

        return AuthenticatedUser(
            subject=claims["sub"],
            username=claims.get("preferred_username", claims["sub"]),
            email=claims.get("email"),
            roles=frozenset(roles),
            raw_claims=claims,
        )
