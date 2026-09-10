from pathlib import Path
from typing import Any

import jwt


class JWTService:
    def __init__(self, public_key_path: str, algorithm: str = "RS256") -> None:
        self.public_key = Path(public_key_path).read_text(encoding="utf-8")
        self.algorithm = algorithm

    def decode(self, token: str) -> dict[str, Any]:
        return jwt.decode(
            token,
            self.public_key,
            algorithms=[self.algorithm],
            options={"require": ["sub", "role", "iat", "exp", "jti"]},
        )
