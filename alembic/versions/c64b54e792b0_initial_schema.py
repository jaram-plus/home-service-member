"""Initial schema

Revision ID: c64b54e792b0
Revises:
Create Date: 2025-12-26 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c64b54e792b0'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create initial member table.

    Creates the member table with status enum defaulting to 'pending'.
    This represents the baseline schema for existing databases.
    """
    bind = op.get_bind()
    dialect = bind.dialect.name

    if dialect == "sqlite":
        # SQLite approach: ENUMs are stored as VARCHAR
        op.execute("""
            CREATE TABLE member (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email VARCHAR(255) NOT NULL UNIQUE,
                name VARCHAR(100) NOT NULL,
                generation INTEGER NOT NULL,
                rank VARCHAR(50) NOT NULL,
                description TEXT,
                image_url VARCHAR(500),
                status VARCHAR(50) NOT NULL DEFAULT 'pending',
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL
            );
        """)
        op.execute("CREATE INDEX ix_member_email ON member (email);")
    else:
        # PostgreSQL approach: create ENUM types first
        op.execute("CREATE TYPE memberstatus AS ENUM ('unverified', 'pending', 'approved')")
        op.execute("CREATE TYPE memberrank AS ENUM ('정회원', 'OB', '준OB')")

        op.execute("""
            CREATE TABLE member (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) NOT NULL UNIQUE,
                name VARCHAR(100) NOT NULL,
                generation INTEGER NOT NULL,
                rank memberrank NOT NULL,
                description TEXT,
                image_url VARCHAR(500),
                status memberstatus NOT NULL DEFAULT 'pending',
                created_at TIMESTAMP NOT NULL,
                updated_at TIMESTAMP NOT NULL
            );
        """)
        op.execute("CREATE INDEX ix_member_email ON member (email);")


def downgrade() -> None:
    """Drop initial member table.

    Removes the member table and its associated enum types.
    """
    op.execute("DROP TABLE member;")

    bind = op.get_bind()
    dialect = bind.dialect.name

    if dialect != "sqlite":
        # Only PostgreSQL needs to drop ENUM types
        op.execute("DROP TYPE memberrank;")
        op.execute("DROP TYPE memberstatus;")