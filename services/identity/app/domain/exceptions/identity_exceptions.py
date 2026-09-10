class IdentityDomainError(Exception):
    """Базовое исключение домена identity."""


class UserAlreadyExistsError(IdentityDomainError):
    def __init__(self, message: str = "User already exists"):
        super().__init__(message)


class InvalidCredentialsError(IdentityDomainError):
    def __init__(self, message: str = "Invalid credentials"):
        super().__init__(message)


class TokenExpiredError(IdentityDomainError):
    def __init__(self, message: str = "Access token expired"):
        super().__init__(message)


class TokenRevokedError(IdentityDomainError):
    def __init__(self, message: str = "Access token revoked"):
        super().__init__(message)


class RefreshTokenExpiredError(IdentityDomainError):
    def __init__(self, message: str = "Refresh token expired"):
        super().__init__(message)


class RefreshTokenRevokedError(IdentityDomainError):
    def __init__(self, message: str = "Refresh token revoked"):
        super().__init__(message)


class UserNotFoundError(IdentityDomainError):
    def __init__(self, message: str = "User not found"):
        super().__init__(message)
