import pytest

from platform_core.modules.auth.application.ports.token_validator_port import (
    TokenValidatorPort,
)
from platform_core.modules.auth.application.use_cases.validate_access_token import (
    ValidateAccessToken,
)
from platform_core.modules.auth.domain.exceptions import InvalidTokenError
from platform_core.modules.auth.domain.value_objects.authenticated_user import (
    AuthenticatedUser,
)


class FakeTokenValidator(TokenValidatorPort):
    def __init__(self, result: AuthenticatedUser | Exception) -> None:
        self._result = result

    async def validate(self, token: str) -> AuthenticatedUser:
        if isinstance(self._result, Exception):
            raise self._result
        return self._result


async def test_execute_when_token_valid_should_return_authenticated_user():
    expected_user = AuthenticatedUser(
        subject="user-123",
        username="jane.doe",
        email="jane@example.test",
        roles=frozenset({"CUSTOMER"}),
    )
    use_case = ValidateAccessToken(FakeTokenValidator(expected_user))

    result = await use_case.execute("a-valid-token")

    assert result == expected_user


async def test_execute_when_token_invalid_should_propagate_invalid_token_error():
    use_case = ValidateAccessToken(
        FakeTokenValidator(InvalidTokenError(reason="expired"))
    )

    with pytest.raises(InvalidTokenError):
        await use_case.execute("an-expired-token")
