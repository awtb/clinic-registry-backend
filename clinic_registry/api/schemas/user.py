from clinic_registry.api.schemas.base import BaseSchema
from clinic_registry.core.enums.user import UserRole


class ProfileResponse(BaseSchema):
    id: str
    first_name: str
    last_name: str
    email: str
    role: UserRole
