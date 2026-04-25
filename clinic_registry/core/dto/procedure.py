from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from clinic_registry.core.dto.base import BaseDTO
from clinic_registry.core.dto.procedure_category import ProcedureCategoryDTO


@dataclass
class ProcedureCreateDTO(BaseDTO):
    code: str
    name: str
    category_id: str
    description: str | None = None
    default_price: Decimal = Decimal("0.00")
    is_active: bool = True


@dataclass
class ProcedureDTO(BaseDTO):
    id: str
    code: str
    name: str
    category_id: str
    category: ProcedureCategoryDTO
    description: str | None
    default_price: Decimal
    is_active: bool
    created_at: datetime
    updated_at: datetime


@dataclass
class ProcedureUpdateDTO(BaseDTO):
    procedure_for_update: ProcedureDTO
    code: str | None = None
    name: str | None = None
    category_id: str | None = None
    description: str | None = None
    default_price: Decimal | None = None
    is_active: bool | None = None
