"""rename telemetry session index

Revision ID: 931b03733176
Revises: 6c8a67b4f863
Create Date: 2026-11-17 17:16:40.227486

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '931b03733176'
down_revision: Union[str, Sequence[str], None] = '6c8a67b4f863'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER INDEX ix_telemetry_sessions_servise_session_id "
        "RENAME TO ix_telemetry_sessions_service_session_id"
    )


def downgrade() -> None:
    op.execute(
        "ALTER INDEX ix_telemetry_sessions_service_session_id "
        "RENAME TO ix_telemetry_sessions_servise_session_id"
    )