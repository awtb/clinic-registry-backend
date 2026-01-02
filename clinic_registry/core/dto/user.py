from dataclasses import dataclass

from clinic_registry.core.dto.base import BaseDTO


@dataclass
class UserDTO(BaseDTO):
    id: str
    email: str
    password_hash: str


@dataclass
class CurrentUserDTO(BaseDTO):
    id: str
    email: str
