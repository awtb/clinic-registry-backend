from pydantic import EmailStr
from pydantic import Field
from pydantic import field_validator

from clinic_registry.api.schemas.base import BaseSchema
from clinic_registry.core.enums.user import UserRole


class UserCreateSchema(BaseSchema):
    username: str
    first_name: str
    last_name: str
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    role: UserRole = Field(default=UserRole.user)

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.lower()


class UserUpdateRequest(BaseSchema):
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None
    password: str | None = Field(default=None, min_length=8, max_length=128)
    role: UserRole | None = None

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value: str | None) -> str | None:
        return value.lower() if value else value


class ProfileResponse(BaseSchema):
    id: str
    first_name: str
    last_name: str
    email: str
    role: UserRole


class UserResponse(BaseSchema):
    id: str
    first_name: str
    last_name: str
    username: str
    email: str
    role: UserRole
