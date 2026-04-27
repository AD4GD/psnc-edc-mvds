"""add credential_type to issued_credentials

Revision ID: e3f1a2b4c5d6
Revises: b59521dc1cb9
Create Date: 2026-04-13 19:30:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e3f1a2b4c5d6"
down_revision: Union[str, Sequence[str], None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "issued_credentials",
        sa.Column("credential_type", sa.String(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("issued_credentials", "credential_type")
