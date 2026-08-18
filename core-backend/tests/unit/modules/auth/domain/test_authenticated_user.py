from platform_core.modules.auth.domain.value_objects.authenticated_user import (
    AuthenticatedUser,
)


def _make_user(roles: frozenset[str]) -> AuthenticatedUser:
    return AuthenticatedUser(
        subject="user-123",
        username="jane.doe",
        email="jane@example.test",
        roles=roles,
    )


def test_has_role_when_role_present_should_return_true():
    user = _make_user(frozenset({"CUSTOMER"}))

    assert user.has_role("CUSTOMER") is True


def test_has_role_when_role_absent_should_return_false():
    user = _make_user(frozenset({"CUSTOMER"}))

    assert user.has_role("ADMIN") is False


def test_has_any_role_when_one_of_the_roles_present_should_return_true():
    user = _make_user(frozenset({"OPERATOR"}))

    assert user.has_any_role("ADMIN", "OPERATOR") is True


def test_has_any_role_when_none_of_the_roles_present_should_return_false():
    user = _make_user(frozenset({"CUSTOMER"}))

    assert user.has_any_role("ADMIN", "MANAGER") is False
