from clinic_registry.core.dto.user import UserDTO
from clinic_registry.core.enums.user import UserRole
from clinic_registry.db.models.user import User


def user_to_dto(user: User) -> UserDTO:
    return UserDTO(
        id=user.id,
        username=user.username,
        email=user.email,
        password_hash=user.password_hash,
        first_name=user.first_name,
        last_name=user.last_name,
        role=UserRole(user.role),
    )
