import httpx

from platform_core.bootstrap.container import build_validate_access_token_use_case
from platform_core.modules.auth.application.use_cases.validate_access_token import (
    ValidateAccessToken,
)
from platform_core.modules.auth.infrastructure.adapters.keycloak_token_validator import (
    KeycloakTokenValidator,
)


def test_build_validate_access_token_use_case_should_wire_keycloak_adapter():
    http_client = httpx.AsyncClient()

    use_case = build_validate_access_token_use_case(http_client)

    assert isinstance(use_case, ValidateAccessToken)
    # Acessa o atributo "privado" propositalmente — o objetivo deste teste é
    # verificar a fiação do Composition Root (RA-005, Capítulo 67), não o
    # comportamento do Use Case (já coberto em tests/unit/modules/auth).
    assert isinstance(use_case._token_validator, KeycloakTokenValidator)
