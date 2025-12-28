"""Convert status to uppercase.

Revision ID: c64b54e792b2
Revises: c64b54e792b1
Create Date: 2025-12-28 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c64b54e792b2'
down_revision: Union[str, Sequence[str], None] = 'c64b54e792b1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Convert status values from lowercase to uppercase.

    Updates existing member status values:
    - 'unverified' -> 'UNVERIFIED'
    - 'pending' -> 'PENDING'
    - 'approved' -> 'APPROVED'
    """
    bind = op.get_bind()
    dialect = bind.dialect.name

    if dialect == "sqlite":
        # SQLite: use batch_alter_table which properly handles foreign keys
        # by recreating the table outside of the transaction
        with op.batch_alter_table('member', recreate='always') as batch_op:
            # Update data before table recreation
            batch_op.execute("""
                UPDATE member
                SET status = CASE
                    WHEN LOWER(status) = 'unverified' THEN 'UNVERIFIED'
                    WHEN LOWER(status) = 'pending' THEN 'PENDING'
                    WHEN LOWER(status) = 'approved' THEN 'APPROVED'
                    ELSE UPPER(status)
                END
            """)

            # Update the default value
            batch_op.alter_column(
                'status',
                server_default='UNVERIFIED'
            )
    else:
        # PostgreSQL/MySQL: update in place
        op.execute("""
            UPDATE member
            SET status = CASE
                WHEN LOWER(status) = 'unverified' THEN 'UNVERIFIED'
                WHEN LOWER(status) = 'pending' THEN 'PENDING'
                WHEN LOWER(status) = 'approved' THEN 'APPROVED'
                ELSE UPPER(status)
            END
        """)

        # Update default constraint using Alembic's cross-dialect method
        op.alter_column('member', 'status', server_default='UNVERIFIED')


def downgrade() -> None:
    """Revert status values from uppercase to lowercase.

    Reverts member status values back to lowercase:
    - 'UNVERIFIED' -> 'unverified'
    - 'PENDING' -> 'pending'
    - 'APPROVED' -> 'approved'
    """
    bind = op.get_bind()
    dialect = bind.dialect.name

    if dialect == "sqlite":
        # SQLite: use batch_alter_table which properly handles foreign keys
        with op.batch_alter_table('member', recreate='always') as batch_op:
            # Update data before table recreation
            batch_op.execute("""
                UPDATE member
                SET status = CASE
                    WHEN UPPER(status) = 'UNVERIFIED' THEN 'unverified'
                    WHEN UPPER(status) = 'PENDING' THEN 'pending'
                    WHEN UPPER(status) = 'APPROVED' THEN 'approved'
                    ELSE LOWER(status)
                END
            """)

            # Revert the default value
            batch_op.alter_column(
                'status',
                server_default='unverified'
            )
    else:
        # PostgreSQL/MySQL: update in place
        op.execute("""
            UPDATE member
            SET status = CASE
                WHEN UPPER(status) = 'UNVERIFIED' THEN 'unverified'
                WHEN UPPER(status) = 'PENDING' THEN 'pending'
                WHEN UPPER(status) = 'APPROVED' THEN 'approved'
                ELSE LOWER(status)
            END
        """)

        # Revert the default constraint using Alembic's cross-dialect method
        op.alter_column('member', 'status', server_default='unverified')