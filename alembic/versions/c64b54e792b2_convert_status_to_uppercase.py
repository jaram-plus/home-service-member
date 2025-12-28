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
        # SQLite: recreate table with uppercase enum values
        # Disable foreign keys to avoid constraint errors during table recreation
        op.execute("PRAGMA foreign_keys = OFF;")

        op.execute("""
            CREATE TABLE member_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email VARCHAR(255) NOT NULL UNIQUE,
                name VARCHAR(100) NOT NULL,
                generation INTEGER NOT NULL,
                rank VARCHAR(50) NOT NULL,
                description TEXT,
                image_url VARCHAR(500),
                status VARCHAR(50) NOT NULL DEFAULT 'UNVERIFIED',
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL
            );
        """)

        # Convert status to uppercase during migration
        op.execute("""
            INSERT INTO member_new (id, email, name, generation, rank, description, image_url, status, created_at, updated_at)
            SELECT id, email, name, generation, rank, description, image_url,
                   CASE
                       WHEN LOWER(status) = 'unverified' THEN 'UNVERIFIED'
                       WHEN LOWER(status) = 'pending' THEN 'PENDING'
                       WHEN LOWER(status) = 'approved' THEN 'APPROVED'
                       ELSE UPPER(status)
                   END as status,
                   created_at, updated_at
            FROM member;
        """)

        op.execute("DROP TABLE member;")
        op.execute("ALTER TABLE member_new RENAME TO member;")

        # Recreate indexes
        op.execute("CREATE INDEX ix_member_email ON member (email);")

        # Recreate foreign key constraints on dependent tables
        op.execute("""
            CREATE TRIGGER fk_skill_member_id
            BEFORE INSERT ON skill
            FOR EACH ROW
            BEGIN
                SELECT RAISE(ABORT, 'foreign key constraint failed')
                WHERE (SELECT id FROM member WHERE id = NEW.member_id) IS NULL;
            END;
        """)
        op.execute("""
            CREATE TRIGGER fk_skill_member_id_update
            AFTER UPDATE OF id ON member
            FOR EACH ROW
            BEGIN
                UPDATE skill SET member_id = NEW.id WHERE member_id = OLD.id;
            END;
        """)
        op.execute("""
            CREATE TRIGGER fk_skill_member_id_delete
            AFTER DELETE ON member
            FOR EACH ROW
            BEGIN
                DELETE FROM skill WHERE member_id = OLD.id;
            END;
        """)

        op.execute("""
            CREATE TRIGGER fk_link_member_id
            BEFORE INSERT ON link
            FOR EACH ROW
            BEGIN
                SELECT RAISE(ABORT, 'foreign key constraint failed')
                WHERE (SELECT id FROM member WHERE id = NEW.member_id) IS NULL;
            END;
        """)
        op.execute("""
            CREATE TRIGGER fk_link_member_id_update
            AFTER UPDATE OF id ON member
            FOR EACH ROW
            BEGIN
                UPDATE link SET member_id = NEW.id WHERE member_id = OLD.id;
            END;
        """)
        op.execute("""
            CREATE TRIGGER fk_link_member_id_delete
            AFTER DELETE ON member
            FOR EACH ROW
            BEGIN
                DELETE FROM link WHERE member_id = OLD.id;
            END;
        """)

        # Re-enable foreign keys
        op.execute("PRAGMA foreign_keys = ON;")
    else:
        # PostgreSQL/MySQL: update in place
        op.execute("""
            UPDATE member
            SET status = CASE
                WHEN LOWER(status) = 'unverified' THEN 'UNVERIFIED'
                WHEN LOWER(status) = 'pending' THEN 'PENDING'
                WHEN LOWER(status) = 'approved' THEN 'APPROVED'
                ELSE status
            END
            WHERE LOWER(status) IN ('unverified', 'pending', 'approved');
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
        # SQLite: recreate table with lowercase values
        # Disable foreign keys to avoid constraint errors during table recreation
        op.execute("PRAGMA foreign_keys = OFF;")

        # Drop existing triggers first
        op.execute("DROP TRIGGER IF EXISTS fk_skill_member_id;")
        op.execute("DROP TRIGGER IF EXISTS fk_skill_member_id_update;")
        op.execute("DROP TRIGGER IF EXISTS fk_skill_member_id_delete;")
        op.execute("DROP TRIGGER IF EXISTS fk_link_member_id;")
        op.execute("DROP TRIGGER IF EXISTS fk_link_member_id_update;")
        op.execute("DROP TRIGGER IF EXISTS fk_link_member_id_delete;")

        op.execute("""
            CREATE TABLE member_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email VARCHAR(255) NOT NULL UNIQUE,
                name VARCHAR(100) NOT NULL,
                generation INTEGER NOT NULL,
                rank VARCHAR(50) NOT NULL,
                description TEXT,
                image_url VARCHAR(500),
                status VARCHAR(50) NOT NULL DEFAULT 'unverified',
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL
            );
        """)

        # Convert status to lowercase during downgrade
        op.execute("""
            INSERT INTO member_new (id, email, name, generation, rank, description, image_url, status, created_at, updated_at)
            SELECT id, email, name, generation, rank, description, image_url,
                   CASE
                       WHEN UPPER(status) = 'UNVERIFIED' THEN 'unverified'
                       WHEN UPPER(status) = 'PENDING' THEN 'pending'
                       WHEN UPPER(status) = 'APPROVED' THEN 'approved'
                       ELSE LOWER(status)
                   END as status,
                   created_at, updated_at
            FROM member;
        """)

        op.execute("DROP TABLE member;")
        op.execute("ALTER TABLE member_new RENAME TO member;")

        # Recreate indexes
        op.execute("CREATE INDEX ix_member_email ON member (email);")

        # Recreate foreign key constraints on dependent tables
        op.execute("""
            CREATE TRIGGER fk_skill_member_id
            BEFORE INSERT ON skill
            FOR EACH ROW
            BEGIN
                SELECT RAISE(ABORT, 'foreign key constraint failed')
                WHERE (SELECT id FROM member WHERE id = NEW.member_id) IS NULL;
            END;
        """)
        op.execute("""
            CREATE TRIGGER fk_skill_member_id_update
            AFTER UPDATE OF id ON member
            FOR EACH ROW
            BEGIN
                UPDATE skill SET member_id = NEW.id WHERE member_id = OLD.id;
            END;
        """)
        op.execute("""
            CREATE TRIGGER fk_skill_member_id_delete
            AFTER DELETE ON member
            FOR EACH ROW
            BEGIN
                DELETE FROM skill WHERE member_id = OLD.id;
            END;
        """)

        op.execute("""
            CREATE TRIGGER fk_link_member_id
            BEFORE INSERT ON link
            FOR EACH ROW
            BEGIN
                SELECT RAISE(ABORT, 'foreign key constraint failed')
                WHERE (SELECT id FROM member WHERE id = NEW.member_id) IS NULL;
            END;
        """)
        op.execute("""
            CREATE TRIGGER fk_link_member_id_update
            AFTER UPDATE OF id ON member
            FOR EACH ROW
            BEGIN
                UPDATE link SET member_id = NEW.id WHERE member_id = OLD.id;
            END;
        """)
        op.execute("""
            CREATE TRIGGER fk_link_member_id_delete
            AFTER DELETE ON member
            FOR EACH ROW
            BEGIN
                DELETE FROM link WHERE member_id = OLD.id;
            END;
        """)

        # Re-enable foreign keys
        op.execute("PRAGMA foreign_keys = ON;")
    else:
        # PostgreSQL/MySQL: update in place
        op.execute("""
            UPDATE member
            SET status = CASE
                WHEN UPPER(status) = 'UNVERIFIED' THEN 'unverified'
                WHEN UPPER(status) = 'PENDING' THEN 'pending'
                WHEN UPPER(status) = 'APPROVED' THEN 'approved'
                ELSE status
            END
            WHERE UPPER(status) IN ('UNVERIFIED', 'PENDING', 'APPROVED');
        """)

        # Revert the default constraint using Alembic's cross-dialect method
        op.alter_column('member', 'status', server_default='unverified')