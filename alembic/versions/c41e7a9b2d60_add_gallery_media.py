"""add standalone gallery media association

Revision ID: c41e7a9b2d60
Revises: b05059d773cd
Create Date: 2026-10-10
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c41e7a9b2d60"
down_revision: Union[str, Sequence[str], None] = "b05059d773cd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "gallery_media",
        sa.Column("media_id", sa.UUID(), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["media_id"],
            ["media.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("media_id"),
    )


def downgrade() -> None:
    op.drop_table("gallery_media")
