"""add test data

Revision ID: ab67cbad7118
Revises: 0d9f0e3234c9
Create Date: 2026-01-09 11:15:47.154653

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "ab67cbad7118"
down_revision: str | Sequence[str] | None = "0d9f0e3234c9"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')

    op.execute(
        sa.text(
            """
            INSERT INTO users (id, name, role, is_active, created_at, last_login_at)
            VALUES
                (uuid_generate_v4(), 'Alice', 'admin', true, NOW() - INTERVAL '10 days', NOW() - INTERVAL '1 day'),
                (uuid_generate_v4(), 'Bob', 'user', true, NOW() - INTERVAL '20 days', NOW() - INTERVAL '2 days'),
                (uuid_generate_v4(), 'Charlie', 'user', false, NOW() - INTERVAL '30 days', NOW() - INTERVAL '5 days');
            """
        )
    )


def downgrade() -> None:
    raise NotImplementedError
