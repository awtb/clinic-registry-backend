from clinic_registry.core.errors.common import InvalidData
from clinic_registry.core.errors.common import NotAllowedError


class UserAlreadyExistsError(InvalidData):
    message = "User already exists"


class IncorrectEmailOrPasswordError(NotAllowedError):
    message = "Incorrect email or password"


class MissingAuthorizationHeader(NotAllowedError):
    message = "Missing token or header"


class InvalidAuthorizationScheme(InvalidData):
    message = "Invalid authorization scheme"


class ExpiredTokenError(NotAllowedError):
    message = "Expired token"


class InvalidTokenScopeError(NotAllowedError):
    message = "Invalid token scope"
