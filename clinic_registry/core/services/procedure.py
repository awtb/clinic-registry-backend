from clinic_registry.core.dto.base import PageDTO
from clinic_registry.core.dto.procedure import ProcedureCreateDTO
from clinic_registry.core.dto.procedure import ProcedureDTO
from clinic_registry.core.dto.procedure import ProcedureUpdateDTO
from clinic_registry.core.errors.common import AlreadyExistsError
from clinic_registry.core.errors.common import NotFoundError
from clinic_registry.core.repos.procedure import ProcedureRepository
from clinic_registry.core.repos.procedure_category import (
    ProcedureCategoryRepository,
)


class ProcedureService:
    def __init__(
        self,
        procedure_repo: ProcedureRepository,
        category_repo: ProcedureCategoryRepository,
    ) -> None:
        self._procedure_repo = procedure_repo
        self._category_repo = category_repo

    async def create_procedure(
        self,
        dto: ProcedureCreateDTO,
    ) -> ProcedureDTO:
        await self._validate_code_is_unique(dto.code)
        await self._validate_category_exists(dto.category_id)

        return await self._procedure_repo.create_procedure(
            code=dto.code,
            name=dto.name,
            category_id=dto.category_id,
            description=dto.description,
            default_price=dto.default_price,
            is_active=dto.is_active,
        )

    async def get_procedure(self, procedure_id: str) -> ProcedureDTO:
        procedure = await self._procedure_repo.get_procedure_by_id_or_none(
            procedure_id,
        )

        if procedure is None:
            raise NotFoundError("Procedure not found")

        return procedure

    async def get_procedures(
        self,
        page: int,
        page_size: int,
        search_query: str | None = None,
        category_id: str | None = None,
        is_active: bool | None = None,
    ) -> PageDTO[ProcedureDTO]:
        return await self._procedure_repo.fetch_all_procedures(
            page=page,
            page_size=page_size,
            search_query=search_query,
            category_id=category_id,
            is_active=is_active,
        )

    async def update_procedure(
        self,
        dto: ProcedureUpdateDTO,
    ) -> ProcedureDTO:
        if dto.code is not None:
            await self._validate_code_is_unique(
                dto.code,
                exclude_procedure_id=dto.procedure_for_update.id,
            )
        if dto.category_id is not None:
            await self._validate_category_exists(dto.category_id)

        await self._procedure_repo.update_procedure(
            procedure=dto.procedure_for_update,
            code=dto.code,
            name=dto.name,
            category_id=dto.category_id,
            description=dto.description,
            default_price=dto.default_price,
            is_active=dto.is_active,
        )

        return await self.get_procedure(dto.procedure_for_update.id)

    async def _validate_code_is_unique(
        self,
        code: str,
        exclude_procedure_id: str | None = None,
    ) -> None:
        code_exists = await self._procedure_repo.code_exists(
            code,
            exclude_procedure_id=exclude_procedure_id,
        )
        if code_exists:
            raise AlreadyExistsError(
                "Procedure with this code already exists",
            )

    async def _validate_category_exists(self, category_id: str) -> None:
        category_exists = await self._category_repo.category_exists(
            category_id,
            active_only=True,
        )
        if not category_exists:
            raise NotFoundError("Procedure category not found")
