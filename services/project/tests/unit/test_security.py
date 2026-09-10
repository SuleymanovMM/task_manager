from uuid import uuid4
import jwt
from datetime import datetime, timedelta, timezone
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from app.core.security import JWTService
from app.domain.entities.project import Project
from app.domain.enums.project_role import ProjectRole
from app.domain.enums.visibility import Visibility


def make_keys():
    private = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    priv = private.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
                                 serialization.NoEncryption()).decode()
    pub = private.public_key().public_bytes(serialization.Encoding.PEM,
                                            serialization.PublicFormat.SubjectPublicKeyInfo).decode()
    return priv, pub


def test_project_validates_rs256_jwt_with_public_key_only():
    private, public = make_keys()
    user_id = uuid4()
    token = jwt.encode({"sub": str(user_id), "role": "USER", "iat": datetime.now(timezone.utc),
                        "exp": datetime.now(timezone.utc) + timedelta(minutes=15), "jti": str(uuid4())}, private,
                       algorithm="RS256")
    current = JWTService(public).decode(token)
    assert current.id == user_id
    assert current.role == "USER"


def test_project_role_rules():
    user_id = uuid4()
    project = Project.create(user_id, "demo", None, Visibility.PRIVATE, None, None)
    assert project.can_assign_role(ProjectRole.OWNER, ProjectRole.MANAGER)
    assert project.can_assign_role(ProjectRole.MANAGER, ProjectRole.MEMBER)
    assert not project.can_assign_role(ProjectRole.MANAGER, ProjectRole.MANAGER)
