import pytest
from iam_client.models import TokenPayload, UserContext


# ---------------------------------------------------------------------------
# TokenPayload
# ---------------------------------------------------------------------------

def test_token_payload_required_fields():
    tp = TokenPayload(sub="user1", email="u@t.com")
    assert tp.sub == "user1"
    assert tp.email == "u@t.com"


def test_token_payload_defaults():
    tp = TokenPayload(sub="user1", email="u@t.com")
    assert tp.roles == []
    assert tp.permissions == []
    assert tp.exp is None


def test_token_payload_with_roles_and_permissions():
    tp = TokenPayload(
        sub="user1",
        email="u@t.com",
        roles=["admin", "researcher"],
        permissions=["read", "write"],
        exp=9999999999,
    )
    assert tp.roles == ["admin", "researcher"]
    assert tp.permissions == ["read", "write"]
    assert tp.exp == 9999999999


def test_token_payload_is_pydantic_model():
    # Validation: missing required field raises
    with pytest.raises(Exception):
        TokenPayload()


# ---------------------------------------------------------------------------
# UserContext
# ---------------------------------------------------------------------------

def test_user_context_creation():
    uc = UserContext(
        user_id="u1",
        email="u1@test.com",
        roles=["admin"],
        permissions=["read"],
        valid=True,
    )
    assert uc.user_id == "u1"
    assert uc.email == "u1@test.com"
    assert uc.valid is True


def test_user_context_invalid_flag():
    uc = UserContext(
        user_id="u2",
        email="u2@test.com",
        roles=[],
        permissions=[],
        valid=False,
    )
    assert uc.valid is False


def test_user_context_empty_roles_and_permissions():
    uc = UserContext(
        user_id="u3",
        email="u3@test.com",
        roles=[],
        permissions=[],
        valid=True,
    )
    assert uc.roles == []
    assert uc.permissions == []


def test_user_context_serialization():
    uc = UserContext(
        user_id="u4",
        email="u4@test.com",
        roles=["researcher"],
        permissions=["submit"],
        valid=True,
    )
    data = uc.dict()
    assert data["user_id"] == "u4"
    assert data["roles"] == ["researcher"]
