from clinic_registry.core.dto.base import PageDTO
from clinic_registry.core.dto.procedure_category import (
    ProcedureCategoryCreateDTO,
)
from clinic_registry.core.dto.procedure_category import ProcedureCategoryDTO
from clinic_registry.core.dto.procedure_category import (
    ProcedureCategoryUpdateDTO,
)
from clinic_registry.core.errors.common import AlreadyExistsError
from clinic_registry.core.errors.common import NotFoundError
from clinic_registry.core.repos.procedure_category import (
    ProcedureCategoryRepository,
)


class ProcedureCategoryService:
    def __init__(
        self,
        category_repo: ProcedureCategoryRepository,
    ) -> None:
        self._category_repo = category_repo

    async def create_category(
        self,
        dto: ProcedureCategoryCreateDTO,
    ) -> ProcedureCategoryDTO:
        await self._validate_code_is_unique(dto.code)

        return await self._category_repo.create_category(
            code=dto.code,
            name=dto.name,
            description=dto.description,
            is_active=dto.is_active,
        )

    async def get_category(self, category_id: str) -> ProcedureCategoryDTO:
        category = await self._category_repo.get_category_by_id_or_none(
            category_id,
        )

        if category is None:
            raise NotFoundError("Procedure category not found")

        return category

    async def get_categories(
        self,
        page: int,
        page_size: int,
        search_query: str | None = None,
        is_active: bool | None = None,
    ) -> PageDTO[ProcedureCategoryDTO]:
        return await self._category_repo.fetch_all_categories(
            page=page,
            page_size=page_size,
            search_query=search_query,
            is_active=is_active,
        )

    async def update_category(
        self,
        dto: ProcedureCategoryUpdateDTO,
    ) -> ProcedureCategoryDTO:
        if dto.code is not None:
            await self._validate_code_is_unique(
                dto.code,
                exclude_category_id=dto.category_for_update.id,
            )

        await self._category_repo.update_category(
            category=dto.category_for_update,
            code=dto.code,
            name=dto.name,
            description=dto.description,
            is_active=dto.is_active,
        )

        return await self.get_category(dto.category_for_update.id)

    async def _validate_code_is_unique(
        self,
        code: str,
        exclude_category_id: str | None = None,
    ) -> None:
        code_exists = await self._category_repo.code_exists(
            code,
            exclude_category_id=exclude_category_id,
        )
        if code_exists:
            raise AlreadyExistsError(
                "Procedure category with this code already exists",
            )
