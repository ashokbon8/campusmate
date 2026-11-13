"""Retain original uploaded PDFs in the database for cloud hosting."""
from alembic import op
import sqlalchemy as sa

revision = "b3c4d5e6f7a8"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "document_files",
        sa.Column("document_id", sa.Integer(), sa.ForeignKey("documents.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("content", sa.LargeBinary(), nullable=False),
    )


def downgrade():
    op.drop_table("document_files")
