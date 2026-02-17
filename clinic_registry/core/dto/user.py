from dataclasses import dataclass

from clinic_registry.core.dto.base import BaseDTO
from clinic_registry.core.enums.user import UserRole


@dataclass
class UserDTO(BaseDTO):
    id: str
    username: str
    first_name: str
    last_name: str
    role: UserRole
    email: str
    password_hash: str


@dataclass
class UserCreateDTO(BaseDTO):
    username: str
    first_name: str
    last_name: str
    email: str
    password: str
    role: UserRole


@dataclass
class UserUpdateDTO(BaseDTO):
    username: str | None = None
    password: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    role: UserRole | None = None


@dataclass
class CurrentUserDTO(BaseDTO):
    id: str
    email: str
    role: UserRole
