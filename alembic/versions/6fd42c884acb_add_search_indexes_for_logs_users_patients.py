"""add search indexes for logs, users and patients.

Revision ID: 6fd42c884acb
Revises: a4f54e85dca3
Create Date: 2026-02-23 18:20:00.000000

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "6fd42c884acb"
down_revision: Union[str, Sequence[str], None] = "a4f54e85dca3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_index(
        "idx_users_created_at",
        "users",
        ["created_at"],
        unique=False,
    )
    op.create_index(
        "idx_users_first_name",
        "users",
        ["first_name"],
        unique=False,
    )
    op.create_index(
        "idx_users_last_name",
        "users",
        ["last_name"],
        unique=False,
    )

    op.create_index(
        "idx_patients_created_at",
        "patients",
        ["created_at"],
        unique=False,
    )
    op.create_index(
        "idx_patients_first_name",
        "patients",
        ["first_name"],
        unique=False,
    )
    op.create_index(
        "idx_patients_last_name",
        "patients",
        ["last_name"],
        unique=False,
    )
    op.create_index(
        "idx_patients_phone_number",
        "patients",
        ["phone_number"],
        unique=False,
    )

    op.create_index(
        "idx_logs_created_at",
        "logs",
        ["created_at"],
        unique=False,
    )
    op.create_index(
        "idx_logs_actor_id_created_at",
        "logs",
        ["actor_id", "created_at"],
        unique=False,
    )
    op.create_index(
        "idx_logs_entity_type_entity_id_created_at",
        "logs",
        ["entity_type", "entity_id", "created_at"],
        unique=False,
    )
    op.create_index(
        "idx_logs_action_created_at",
        "logs",
        ["action", "created_at"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("idx_logs_action_created_at", table_name="logs")
    op.drop_index(
        "idx_logs_entity_type_entity_id_created_at",
        table_name="logs",
    )
    op.drop_index("idx_logs_actor_id_created_at", table_name="logs")
    op.drop_index("idx_logs_created_at", table_name="logs")

    op.drop_index("idx_patients_phone_number", table_name="patients")
    op.drop_index("idx_patients_last_name", table_name="patients")
    op.drop_index("idx_patients_first_name", table_name="patients")
    op.drop_index("idx_patients_created_at", table_name="patients")

    op.drop_index("idx_users_last_name", table_name="users")
    op.drop_index("idx_users_first_name", table_name="users")
    op.drop_index("idx_users_created_at", table_name="users")
