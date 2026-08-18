"""Testes unitários do adapter, com JWKS/assinatura gerados localmente
(nenhuma rede real envolvida via httpx.MockTransport)."""

from __future__ import annotations

import time
from typing import Any

import httpx
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from jose import jwk, jwt

from platform_core.modules.auth.domain.exceptions import InvalidTokenError
from platform_core.modules.auth.infrastructure.adapters.keycloak_token_validator import (
    KeycloakTokenValidator,
)

_ISSUER = "http://keycloak.test/realms/app"
_KID = "test-key-1"


def _generate_rsa_keypair() -> tuple[str, str]:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode()
    public_pem = (
        private_key.public_key()
        .public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        .decode()
    )
    return private_pem, public_pem


def _build_jwks(public_pem: str) -> dict[str, Any]:
    public_jwk = jwk.construct(public_pem, algorithm="RS256").to_dict()
    public_jwk["kid"] = _KID
    public_jwk["use"] = "sig"
    return {"keys": [public_jwk]}


def _http_client_returning(jwks: dict[str, Any]) -> httpx.AsyncClient:
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=jwks)

    return httpx.AsyncClient(transport=httpx.MockTransport(handler))


def _sign_token(private_pem: str, claims: dict[str, Any]) -> str:
    return jwt.encode(claims, private_pem, algorithm="RS256", headers={"kid": _KID})


@pytest.fixture
def keypair() -> tuple[str, str]:
    return _generate_rsa_keypair()


async def test_validate_when_token_valid_should_return_authenticated_user(keypair):
    private_pem, public_pem = keypair
    validator = KeycloakTokenValidator(
        issuer_url=_ISSUER,
        audience=None,
        http_client=_http_client_returning(_build_jwks(public_pem)),
    )
    token = _sign_token(
        private_pem,
        {
            "sub": "user-123",
            "preferred_username": "jane.doe",
            "email": "jane@example.test",
            "iss": _ISSUER,
            "exp": int(time.time()) + 300,
            "realm_access": {"roles": ["CUSTOMER"]},
        },
    )

    user = await validator.validate(token)

    assert user.subject == "user-123"
    assert user.username == "jane.doe"
    assert user.has_role("CUSTOMER")


async def test_validate_when_token_expired_should_raise_invalid_token_error(keypair):
    private_pem, public_pem = keypair
    validator = KeycloakTokenValidator(
        issuer_url=_ISSUER,
        audience=None,
        http_client=_http_client_returning(_build_jwks(public_pem)),
    )
    token = _sign_token(
        private_pem,
        {
            "sub": "user-123",
            "iss": _ISSUER,
            "exp": int(time.time()) - 10,
            "realm_access": {"roles": []},
        },
    )

    with pytest.raises(InvalidTokenError):
        await validator.validate(token)


async def test_validate_when_signature_invalid_should_raise_invalid_token_error(
    keypair,
):
    _, public_pem = keypair
    other_private_pem, _ = _generate_rsa_keypair()
    validator = KeycloakTokenValidator(
        issuer_url=_ISSUER,
        audience=None,
        http_client=_http_client_returning(_build_jwks(public_pem)),
    )
    token = _sign_token(
        other_private_pem,
        {
            "sub": "user-123",
            "iss": _ISSUER,
            "exp": int(time.time()) + 300,
            "realm_access": {"roles": []},
        },
    )

    with pytest.raises(InvalidTokenError):
        await validator.validate(token)


async def test_validate_when_issuer_mismatched_should_raise_invalid_token_error(
    keypair,
):
    private_pem, public_pem = keypair
    validator = KeycloakTokenValidator(
        issuer_url=_ISSUER,
        audience=None,
        http_client=_http_client_returning(_build_jwks(public_pem)),
    )
    token = _sign_token(
        private_pem,
        {
            "sub": "user-123",
            "iss": "http://attacker.test/realms/fake",
            "exp": int(time.time()) + 300,
            "realm_access": {"roles": []},
        },
    )

    with pytest.raises(InvalidTokenError):
        await validator.validate(token)
