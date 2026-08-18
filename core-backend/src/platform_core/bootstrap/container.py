"""Composition Root (RA-005, Capítulo 67) — único lugar onde uma Port é
conectada à sua implementação concreta. Nenhum outro ponto do código deverá
instanciar um Adapter de infraestrutura diretamente."""

from __future__ import annotations

import httpx

from platform_core.bootstrap.settings import get_settings
from platform_core.modules.auth.application.use_cases.validate_access_token import (
    ValidateAccessToken,
)
from platform_core.modules.auth.infrastructure.adapters.keycloak_token_validator import (
    KeycloakTokenValidator,
)


def build_validate_access_token_use_case(
    http_client: httpx.AsyncClient,
) -> ValidateAccessToken:
    settings = get_settings()
    token_validator = KeycloakTokenValidator(
        issuer_url=settings.keycloak_issuer_url,
        audience=settings.keycloak_audience,
        http_client=http_client,
    )
    return ValidateAccessToken(token_validator)
