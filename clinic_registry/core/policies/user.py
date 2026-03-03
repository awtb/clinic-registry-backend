from clinic_registry.core.dto.user import CurrentUserDTO
from clinic_registry.core.dto.user import UserDTO
from clinic_registry.core.enums.user import UserRole
from clinic_registry.core.errors.common import NotAllowedError


class UserPolicy:
    def authorize_create_user(self, actor: CurrentUserDTO) -> None:
        if actor.role != UserRole.admin:
            raise NotAllowedError("Only admins can create users")

    def authorize_update_user(
        self,
        actor: CurrentUserDTO,
        user_for_update: UserDTO,
    ) -> None:
        if actor.role != UserRole.admin and actor.id != user_for_update.id:
            raise NotAllowedError("Only admins can update other users")

    def authorize_change_user_role(self, actor: CurrentUserDTO) -> None:
        if actor.role != UserRole.admin:
            raise NotAllowedError("Only admins can change roles")
