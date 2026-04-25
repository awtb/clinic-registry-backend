from datetime import datetime

from clinic_registry.api.schemas.base import BaseSchema


class ProcedureCategoryCreateSchema(BaseSchema):
    code: str
    name: str
    description: str | None = None
    is_active: bool = True


class ProcedureCategoryResponse(BaseSchema):
    id: str
    code: str
    name: str
    description: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ProcedureCategoryUpdateSchema(BaseSchema):
    code: str | None = None
    name: str | None = None
    description: str | None = None
    is_active: bool | None = None
