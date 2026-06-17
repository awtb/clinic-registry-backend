"""add medical record pricing

Revision ID: 371ae7f5adf0
Revises: 5d085590d409
Create Date: 2026-06-17 09:30:25.950765

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '371ae7f5adf0'
down_revision: Union[str, Sequence[str], None] = '5d085590d409'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add price columns as nullable first so existing rows can be backfilled
    # before the NOT NULL constraint is enforced.
    op.add_column(
        "medical_record_procedures",
        sa.Column("unit_price", sa.Numeric(precision=12, scale=2), nullable=True),
    )
    op.add_column(
        "medical_records",
        sa.Column("total_price", sa.Numeric(precision=12, scale=2), nullable=True),
    )

    # Snapshot each existing line item's price from the current catalog price
    # of its procedure. The procedure FK is RESTRICT, so a matching procedure
    # always exists; COALESCE guards against any unexpected gap.
    op.execute("""
        UPDATE medical_record_procedures AS line
        SET unit_price = COALESCE(procedures.default_price, 0)
        FROM procedures
        WHERE procedures.id = line.procedure_id
        """)
    op.execute(
        "UPDATE medical_record_procedures SET unit_price = 0 "
        "WHERE unit_price IS NULL"
    )

    # Set each record's total to the sum of its line items. Records without any
    # procedures fall back to 0.
    op.execute("""
        UPDATE medical_records AS record
        SET total_price = COALESCE(line_totals.total, 0)
        FROM (
            SELECT
                medical_record_id,
                SUM(unit_price) AS total
            FROM medical_record_procedures
            GROUP BY medical_record_id
        ) AS line_totals
        WHERE record.id = line_totals.medical_record_id
        """)
    op.execute(
        "UPDATE medical_records SET total_price = 0 WHERE total_price IS NULL"
    )

    op.alter_column("medical_record_procedures", "unit_price", nullable=False)
    op.alter_column("medical_records", "total_price", nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("medical_records", "total_price")
    op.drop_column("medical_record_procedures", "unit_price")
