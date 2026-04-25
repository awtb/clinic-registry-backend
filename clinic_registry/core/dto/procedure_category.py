from dataclasses import dataclass
from datetime import datetime

from clinic_registry.core.dto.base import BaseDTO


@dataclass
class ProcedureCategoryCreateDTO(BaseDTO):
    code: str
    name: str
    description: str | None = None
    is_active: bool = True


@dataclass
class ProcedureCategoryDTO(BaseDTO):
    id: str
    code: str
    name: str
    description: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


@dataclass
class ProcedureCategoryUpdateDTO(BaseDTO):
    category_for_update: ProcedureCategoryDTO
    code: str | None = None
    name: str | None = None
    description: str | None = None
    is_active: bool | None = None
