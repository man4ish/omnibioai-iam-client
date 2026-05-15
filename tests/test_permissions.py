import pytest
from iam_client.permissions import has_role, has_any_role, has_permission, require_role
from iam_client.exceptions import IAMError, AuthenticationError, AuthorizationError


# ---------------------------------------------------------------------------
# has_role
# ---------------------------------------------------------------------------

def test_has_role_true():
    assert has_role(["admin", "researcher"], "admin") is True


def test_has_role_false():
    assert has_role(["researcher"], "admin") is False


def test_has_role_empty_list():
    assert has_role([], "admin") is False


# ---------------------------------------------------------------------------
# has_any_role
# ---------------------------------------------------------------------------

def test_has_any_role_first_match():
    assert has_any_role(["admin", "researcher"], ["admin", "superuser"]) is True


def test_has_any_role_second_match():
    assert has_any_role(["researcher"], ["admin", "researcher"]) is True


def test_has_any_role_no_match():
    assert has_any_role(["viewer"], ["admin", "researcher"]) is False


def test_has_any_role_empty_user_roles():
    assert has_any_role([], ["admin"]) is False


def test_has_any_role_empty_required():
    assert has_any_role(["admin"], []) is False


# ---------------------------------------------------------------------------
# has_permission
# ---------------------------------------------------------------------------

def test_has_permission_true():
    assert has_permission(["read", "write"], "read") is True


def test_has_permission_false():
    assert has_permission(["read"], "delete") is False


def test_has_permission_empty():
    assert has_permission([], "read") is False


# ---------------------------------------------------------------------------
# require_role
# ---------------------------------------------------------------------------

def test_require_role_success():
    # Should not raise
    require_role(["admin", "researcher"], "admin")


def test_require_role_raises_permission_error():
    with pytest.raises(PermissionError) as exc_info:
        require_role(["researcher"], "admin")
    assert "Missing role: admin" in str(exc_info.value)


def test_require_role_empty_roles_raises():
    with pytest.raises(PermissionError):
        require_role([], "admin")


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

def test_iam_error_is_exception():
    err = IAMError("base error")
    assert isinstance(err, Exception)
    assert str(err) == "base error"


def test_authentication_error_inherits_iam_error():
    err = AuthenticationError("auth failed")
    assert isinstance(err, IAMError)
    assert isinstance(err, Exception)


def test_authorization_error_inherits_iam_error():
    err = AuthorizationError("not authorized")
    assert isinstance(err, IAMError)
    assert isinstance(err, Exception)


def test_raise_authentication_error():
    with pytest.raises(AuthenticationError):
        raise AuthenticationError("bad token")


def test_raise_authorization_error():
    with pytest.raises(AuthorizationError):
        raise AuthorizationError("forbidden")


def test_catch_as_iam_error():
    with pytest.raises(IAMError):
        raise AuthenticationError("bad")


def test_catch_authorization_as_iam_error():
    with pytest.raises(IAMError):
        raise AuthorizationError("denied")
