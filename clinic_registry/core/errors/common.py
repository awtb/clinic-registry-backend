from fastapi import HTTPException
from fastapi import status


class Error(HTTPException):
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    message: str = "Something went wrong"

    def __init__(self, message: str | None = None, **kwargs) -> None:
        if message:
            self.message = message
        self.detail = {"message": self.message, **kwargs}


class NotFoundError(Error):
    status_code = status.HTTP_404_NOT_FOUND
    message = "Entity not found"


class AlreadyExistsError(Error):
    status_code = status.HTTP_400_BAD_REQUEST
    message = "Entity already exists"


class NotAllowedError(Error):
    status_code = status.HTTP_403_FORBIDDEN
    message = "Not allowed"


class InvalidData(Error):
    status_code = status.HTTP_400_BAD_REQUEST
    message = "One or more invalid fields"


class RemoteServerError(Error):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    message = "Remote server error"


class TooManyRequests(Error):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    message = "Too many requests"
