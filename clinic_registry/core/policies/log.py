from clinic_registry.core.dto.user import CurrentUserDTO
from clinic_registry.core.errors.common import NotAllowedError


class LogPolicy:
    def authorize_view_logs(self, actor: CurrentUserDTO) -> None:
        if actor.role != "admin":
            raise NotAllowedError("Only admins can view logs")
