"""add guide notifier events

Revision ID: a4c9d2e7f1b3
Revises: ed9f015280d3
Create Date: 2026-08-29 10:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "a4c9d2e7f1b3"
down_revision: str | None = "ed9f015280d3"
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def upgrade() -> None:
    with op.batch_alter_table("group_events_notifier_options", schema=None) as batch_op:
        for column_name in ("guide_created", "guide_updated", "guide_deleted"):
            batch_op.add_column(
                sa.Column(
                    column_name,
                    sa.Boolean(),
                    nullable=False,
                    default=False,
                    server_default=sa.sql.expression.false(),
                )
            )


def downgrade() -> None:
    with op.batch_alter_table("group_events_notifier_options", schema=None) as batch_op:
        for column_name in ("guide_deleted", "guide_updated", "guide_created"):
            batch_op.drop_column(column_name)
