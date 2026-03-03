from clinic_registry.core.dto.user import CurrentUserDTO
from clinic_registry.core.enums.user import UserRole
from clinic_registry.core.errors.common import NotAllowedError


class PatientPolicy:
    def authorize_update_patient(self, actor: CurrentUserDTO) -> None:
        if actor.role != UserRole.admin:
            raise NotAllowedError("Only admins can update patients")
