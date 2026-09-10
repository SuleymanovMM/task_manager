import hashlib
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHash, VerificationError, VerifyMismatchError


class PasswordService:
    def __init__(self) -> None:
        self._hasher = PasswordHasher()
        # Фиктивный хэш: сверяемся с ним, если пользователь не найден — время ответа
        # не выдаёт существование аккаунта.
        self.dummy_hash = self._hasher.hash(secrets.token_urlsafe(32))

    def hash(self, password: str) -> str:
        return self._hasher.hash(password)

    def verify(self, password_hash: str, password: str) -> bool:
        try:
            return self._hasher.verify(password_hash, password)
        except (VerifyMismatchError, VerificationError, InvalidHash):
            return False


class TokenHasher:
    @staticmethod
    def hash(token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()


class JWTService:
    def __init__(self, private_key: str, public_key: str, algorithm: str = "RS256", issuer: str = "taskflow-identity") -> None:
        self.private_key = private_key
        self.public_key = public_key
        self.algorithm = algorithm
        self.issuer = issuer

    @classmethod
    def from_files(
            cls, private_key_path: Path, public_key_path: Path, algorithm: str = "RS256",
            issuer: str = "taskflow-identity"
    ) -> "JWTService":
        return cls(private_key_path.read_text(), public_key_path.read_text(), algorithm, issuer)

    def create_access_token(self, user_id: uuid.UUID, role: str, expires_minutes: int) -> str:
        now = datetime.now(timezone.utc)
        payload: dict[str, Any] = {
            "sub": str(user_id),
            "role": role,
            "iss": self.issuer,
            "iat": now,
            "exp": now + timedelta(minutes=expires_minutes),
            "jti": str(uuid.uuid4()),
        }
        return jwt.encode(payload, self.private_key, algorithm=self.algorithm)

    def decode_access_token(self, token: str) -> dict[str, Any]:
        return jwt.decode(token, self.public_key, algorithms=[self.algorithm], issuer=self.issuer,
                          options={"require": ["sub", "role", "iss", "iat", "exp", "jti"]})


def generate_refresh_token() -> str:
    return secrets.token_urlsafe(48)
