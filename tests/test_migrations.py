import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine


@pytest.mark.asyncio
async def test_migrations_applied(db_engine: AsyncEngine) -> None:
    async with db_engine.connect() as connection:
        result = await connection.execute(
            text("SELECT version_num FROM alembic_version LIMIT 1")
        )
        assert result.scalar_one_or_none() is not None
