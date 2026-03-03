from pydantic import EmailStr
from pydantic import Field
from pydantic import field_validator

from clinic_registry.api.schemas.base import BaseSchema


class TokenSchema(BaseSchema):
    access_token: str
    refresh_token: str
    token_type: str = Field(default="bearer")


class RegistrationRequestSchema(BaseSchema):
    username: str
    first_name: str
    last_name: str
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.lower()


class RegistrationResponseSchema(BaseSchema):
    email: str
