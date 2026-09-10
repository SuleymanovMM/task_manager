import uuid
from datetime import datetime, timezone
from pathlib import Path

import jwt
import pytest

from app.core.config import settings
from app.core.security import JWTService, PasswordService, TokenHasher


@pytest.fixture
def jwt_service() -> JWTService:
    return JWTService.from_files(
        settings.jwt_private_key_path,
        settings.jwt_public_key_path,
        settings.jwt_algorithm,
        settings.app_name,
    )


def test_password_hash_and_verify():
    svc = PasswordService()
    hashed = svc.hash("secret-password")
    assert hashed != "secret-password"
    assert svc.verify(hashed, "secret-password")
    assert not svc.verify(hashed, "wrong-password")


def test_token_hasher_is_deterministic():
    assert TokenHasher.hash("abc") == TokenHasher.hash("abc")
    assert TokenHasher.hash("abc") != TokenHasher.hash("xyz")


def test_dummy_hash_is_a_valid_but_unusable_hash():
    svc = PasswordService()
    assert svc.dummy_hash != svc.hash("secret-password")
    assert not svc.verify(svc.dummy_hash, "secret-password")


def test_decode_rejects_wrong_issuer():
    other_service = JWTService.from_files(
        settings.jwt_private_key_path, settings.jwt_public_key_path, settings.jwt_algorithm, "some-other-service"
    )
    token = other_service.create_access_token(uuid.uuid4(), "USER", 15)
    expected_issuer = JWTService.from_files(
        settings.jwt_private_key_path, settings.jwt_public_key_path, settings.jwt_algorithm, settings.app_name
    )
    with pytest.raises(jwt.InvalidIssuerError):
        expected_issuer.decode_access_token(token)


def test_access_token_contains_required_claims(jwt_service: JWTService):
    user_id = uuid.uuid4()
    token = jwt_service.create_access_token(user_id, "USER", 15)
    payload = jwt.decode(
        token,
        Path(settings.jwt_public_key_path).read_text(),
        algorithms=[settings.jwt_algorithm],
    )
    assert payload["sub"] == str(user_id)
    assert payload["role"] == "USER"
    assert payload["iss"] == settings.app_name
    assert "iat" in payload
    assert "exp" in payload
    assert "jti" in payload
    assert datetime.fromtimestamp(payload["exp"], tz=timezone.utc) > datetime.now(timezone.utc)
