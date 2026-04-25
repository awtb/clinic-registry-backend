from datetime import datetime
from decimal import Decimal

from clinic_registry.api.schemas.base import BaseSchema
from clinic_registry.api.schemas.procedure_category import (
    ProcedureCategoryResponse,
)


class ProcedureCreateSchema(BaseSchema):
    code: str
    name: str
    category_id: str
    description: str | None = None
    default_price: Decimal = Decimal("0.00")
    is_active: bool = True


class ProcedureResponse(BaseSchema):
    id: str
    code: str
    name: str
    category_id: str
    category: ProcedureCategoryResponse
    description: str | None
    default_price: Decimal
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ProcedureUpdateSchema(BaseSchema):
    code: str | None = None
    name: str | None = None
    category_id: str | None = None
    description: str | None = None
    default_price: Decimal | None = None
    is_active: bool | None = None
