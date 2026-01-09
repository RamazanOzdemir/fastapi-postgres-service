from collections.abc import Collection, Mapping
from typing import Any, Literal
from uuid import uuid4

from alembic.operations import ops
from alembic.runtime.migration import MigrationContext, MigrationInfo
from sqlalchemy import CheckConstraint, Column, Connection, MetaData, Table, types
from sqlalchemy.sql import func

from alembic import op


class AlembicAuditor:
    """
    This is a simplified implementation of the long deprecated Audit-Alembic project.
    https://github.com/jpassaro/Audit-Alembic/tree/master
    """

    def __init__(
        self,
        table_name: str = "alembic_audit",
        id_column_name: str = "id",
        alembic_version_column_name: str = "alembic_version",
        previous_alembic_version_column_name: str = "previous_alembic_version",
        operation_type_column_name: str = "operation_type",
        operation_direction_column_name: str = "operation_direction",
        created_at_column_name: str = "created_at",
    ) -> None:
        self.table_name = table_name

        self.column_names = {
            "id": id_column_name,
            "alembic_version": alembic_version_column_name,
            "previous_alembic_version": previous_alembic_version_column_name,
            "operation_type": operation_type_column_name,
            "operation_direction": operation_direction_column_name,
            "created_at": created_at_column_name,
        }

        self.table_columns: list[Any] = [
            Column(
                id_column_name,
                types.UUID,
                primary_key=True,
                default=uuid4,
                nullable=False,
                unique=True,
            ),
            Column(alembic_version_column_name, types.String(255)),
            Column(previous_alembic_version_column_name, types.String(255)),
            CheckConstraint(
                f"coalesce({alembic_version_column_name}, {previous_alembic_version_column_name}) IS NOT NULL",
                name="alembic_versions_nonnull",
            ),
            Column(operation_type_column_name, types.String(32), nullable=False),
            Column(operation_direction_column_name, types.String(32), nullable=False),
            Column(
                created_at_column_name,
                types.DateTime(timezone=True),
                nullable=False,
                default=func.now(),
            ),
        ]

        self.metadata = MetaData()

        self.table = Table(self.table_name, self.metadata, *self.table_columns)

        self.created_table: bool = False

    def ensure_audit_table_exists(self, context: MigrationContext) -> None:
        if not self.created_table:
            if context.as_sql:
                op.invoke(ops.CreateTableOp.from_table(self.table))
            else:
                if not isinstance(context.connection, Connection):
                    raise ValueError("Connection not available")
                self.table.create(context.connection, checkfirst=True)

            self.created_table = True

    @staticmethod
    def get_operation_type(step: MigrationInfo) -> Literal["stamp", "migration"]:
        if step.is_stamp:
            return "stamp"
        if step.is_migration:
            return "migration"
        raise ValueError("Invalid migration step")

    @staticmethod
    def get_operation_direction(step: MigrationInfo) -> Literal["up", "down"]:
        if step.is_upgrade:
            return "up"
        return "down"

    def on_version_apply(
        self,
        ctx: MigrationContext,  # The MigrationContext running the migration
        step: MigrationInfo,  # Represents the migration step currently being applied
        heads: Collection[
            Any
        ],  # Collection of version strings representing the current heads
        run_args: Mapping[str, Any],  # The kwargs passed to run_migrations
    ) -> None:
        """
        https://alembic.sqlalchemy.org/en/latest/api/runtime.html#alembic.runtime.environment.EnvironmentContext.configure.params.on_version_apply
        """

        self.ensure_audit_table_exists(ctx)

        separator = "##"

        stmt = self.table.insert().values(
            {
                self.column_names["alembic_version"]: separator.join(
                    step.destination_revision_ids
                ),
                self.column_names["previous_alembic_version"]: separator.join(
                    step.source_revision_ids
                ),
                self.column_names["operation_type"]: self.get_operation_type(step),
                self.column_names["operation_direction"]: self.get_operation_direction(
                    step
                ),
            }
        )
        op.execute(stmt)
