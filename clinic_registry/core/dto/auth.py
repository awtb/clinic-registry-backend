from dataclasses import dataclass

from clinic_registry.core.dto.base import BaseDTO


@dataclass
class RegistrationResponseDTO(BaseDTO):
    email: str


@dataclass
class RegistrationRequestDTO(BaseDTO):
    email: str
    password: str


@dataclass
class TokenPairDTO(BaseDTO):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


@dataclass
class LoginRequestDTO(BaseDTO):
    email: str
    password: str
