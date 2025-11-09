"""add post.status

Revision ID: d52f7f946dca
Revises: 8795c7145133
Create Date: 2025-11-09 21:10:02.041335

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd52f7f946dca'
down_revision: Union[str, Sequence[str], None] = '8795c7145133'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

enum_name = "post_status"
enum_values = ("draft", "published", "archived")

def upgrade() -> None:
    """Upgrade schema."""
    sa_enum = sa.Enum(*enum_values, name=enum_name)
    sa_enum.create(op.get_bind(), checkfirst=True)

    op.add_column(
        "posts",
        sa.Column(
            "status",
            sa.Enum(*enum_values, name=enum_name),
            server_default=sa.text("'draft'"),
            nullable=False,
        ),
    )
    op.alter_column("posts", "status", server_default=None)

def downgrade() -> None:
    op.drop_column("posts", "status")
    op.execute(f"DROP TYPE IF EXISTS {enum_name}")