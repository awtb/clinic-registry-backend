import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from sqlalchemy import URL

from alembic import context

sys.path.append("src")


config = context.config


from clinic_registry.settings import Settings
from clinic_registry.db.models import BaseModel


if config.config_file_name is not None:
    fileConfig(config.config_file_name)


target_metadata = BaseModel.metadata

app_settings = Settings()

url = URL.create(
    drivername=app_settings.db_sync_driver,
    username=app_settings.db_user,
    password=app_settings.db_password,
    host=app_settings.db_host,
    port=app_settings.db_port,
    database=app_settings.db_name,
)

config.set_main_option(
    "sqlalchemy.url",
    url.render_as_string(
        hide_password=False,
    ),
)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
