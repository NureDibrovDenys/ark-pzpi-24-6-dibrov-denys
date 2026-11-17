"""retry add user roles and drone ownership

Revision ID: ec0870f94c3a
Revises: 931b03733176
Create Date: 2026-11-17 17:37:41.750745

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ec0870f94c3a'
down_revision: Union[str, Sequence[str], None] = '931b03733176'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Додати ролі користувачів і власників дронів."""
    user_role = sa.Enum(
        "ADMIN",
        "USER",
        name="user_role",
    )
    user_role.create(op.get_bind(), checkfirst=True)

    op.add_column(
        "users",
        sa.Column(
            "role",
            user_role,
            server_default="USER",
            nullable=False,
        ),
    )

    op.add_column(
        "drones",
        sa.Column(
            "owner_id",
            sa.Integer(),
            nullable=False,
        ),
    )

    op.create_index(
        "ix_drones_owner_id",
        "drones",
        ["owner_id"],
        unique=False,
    )

    op.create_foreign_key(
        "fk_drones_owner_id_users",
        "drones",
        "users",
        ["owner_id"],
        ["id"],
    )


def downgrade() -> None:
    """Прибрати ролі користувачів і власників дронів."""
    op.drop_constraint(
        "fk_drones_owner_id_users",
        "drones",
        type_="foreignkey",
    )

    op.drop_index(
        "ix_drones_owner_id",
        table_name="drones",
    )

    op.drop_column("drones", "owner_id")
    op.drop_column("users", "role")

    sa.Enum(
        name="user_role",
    ).drop(op.get_bind(), checkfirst=True)