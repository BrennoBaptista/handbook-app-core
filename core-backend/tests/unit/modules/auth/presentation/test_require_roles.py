import pytest

from platform_core.modules.auth.domain.exceptions import InsufficientRoleError
from platform_core.modules.auth.domain.value_objects.authenticated_user import (
    AuthenticatedUser,
)
from platform_core.modules.auth.presentation.dependencies.auth_dependencies import (
    require_roles,
)


def _make_user(roles: frozenset[str]) -> AuthenticatedUser:
    return AuthenticatedUser(
        subject="user-123",
        username="jane.doe",
        email="jane@example.test",
        roles=roles,
    )


async def test_require_roles_when_user_has_required_role_should_return_user():
    dependency = require_roles("ADMIN", "MANAGER")
    user = _make_user(frozenset({"MANAGER"}))

    result = await dependency(user=user)

    assert result is user


async def test_require_roles_when_user_lacks_required_role_should_raise_insufficient_role_error():
    dependency = require_roles("ADMIN")
    user = _make_user(frozenset({"CUSTOMER"}))

    with pytest.raises(InsufficientRoleError):
        await dependency(user=user)
