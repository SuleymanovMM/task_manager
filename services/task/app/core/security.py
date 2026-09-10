from pathlib import Path
from uuid import UUID

import jwt
from pydantic import BaseModel


class CurrentUser(BaseModel):
    id: UUID
    role: str


class JWTService:
    def __init__(self, public_key: str, algorithm: str = "RS256"):
        self.public_key = public_key
        self.algorithm = algorithm

    @classmethod
    def from_file(cls, path: str, algorithm: str = "RS256"):
        return cls(Path(path).read_text(encoding="utf-8"), algorithm)

    def decode(self, token: str) -> CurrentUser:
        payload = jwt.decode(
            token,
            self.public_key,
            algorithms=[self.algorithm],
            options={"require": ["sub", "exp", "iat", "jti", "role"]},
        )
        return CurrentUser(id=UUID(payload["sub"]), role=str(payload["role"]))
