from app.domain.enums.role import UserRole
from app.domain.exceptions.identity_exceptions import UserAlreadyExistsError


def test_user_role_values():
    assert UserRole.USER == "USER"
    assert UserRole.ADMIN == "ADMIN"


def test_user_already_exists_error_message():
    exc = UserAlreadyExistsError()
    assert str(exc) == "User already exists"
