import importlib
import sys
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import MetaData, engine_from_config, pool
from sqlalchemy.schema import CreateSchema

from alembic import context as alembic_context


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.modules import model_registry  # noqa: E402


for model_module in model_registry.MODEL_MODULES:
	importlib.import_module(model_module)


from app.shared.config.settings import settings  # noqa: E402
from app.shared.database.base import ALL_METADATA, SCHEMA_NAMES  # noqa: E402


config = alembic_context.config

if config.config_file_name is not None:
	fileConfig(config.config_file_name)

config.set_main_option("sqlalchemy.url", settings.MIGRATION_DATABASE_URL)


def _foreign_key_target_schema(source_schema: str | None, target_fullname: str) -> str | None:
	target_table, separator, _target_column = target_fullname.rpartition(".")
	if not separator:
		return source_schema
	target_schema, separator, _target_table_name = target_table.rpartition(".")
	return target_schema if separator else source_schema


def validate_no_cross_schema_foreign_keys(metadata_collection: tuple[MetaData, ...]) -> None:
	violations: list[str] = []

	for metadata in metadata_collection:
		for table in metadata.tables.values():
			source_schema = table.schema
			for foreign_key in table.foreign_keys:
				target_schema = _foreign_key_target_schema(source_schema, foreign_key.target_fullname)
				if source_schema != target_schema:
					violations.append(
						f"{table.fullname}.{foreign_key.parent.name} -> {foreign_key.target_fullname}"
					)

	if violations:
		details = "\n  - ".join(violations)
		raise RuntimeError(
			"Cross-schema foreign keys are forbidden; use soft-reference columns instead:\n"
			f"  - {details}"
		)


validate_no_cross_schema_foreign_keys(ALL_METADATA)
target_metadata = ALL_METADATA


def include_name(name: str | None, type_: str, _parent_names: dict[str, str | None]) -> bool:
	if type_ == "schema":
		return name in SCHEMA_NAMES
	return True


def run_migrations_offline() -> None:
	"""Emit migration SQL without opening a database connection."""
	alembic_context.configure(
		url=config.get_main_option("sqlalchemy.url"),
		target_metadata=target_metadata,
		literal_binds=True,
		dialect_opts={"paramstyle": "named"},
		include_schemas=True,
		include_name=include_name,
		compare_type=True,
		compare_server_default=True,
		version_table="alembic_version",
		version_table_schema="public",
	)

	with alembic_context.begin_transaction():
		alembic_context.run_migrations()


def run_migrations_online() -> None:
	"""Run migrations through the synchronous migration database URL."""
	connectable = engine_from_config(
		config.get_section(config.config_ini_section, {}),
		prefix="sqlalchemy.",
		poolclass=pool.NullPool,
	)

	with connectable.connect() as connection:
		for schema_name in SCHEMA_NAMES:
			connection.execute(CreateSchema(schema_name, if_not_exists=True))
		connection.commit()

		alembic_context.configure(
			connection=connection,
			target_metadata=target_metadata,
			include_schemas=True,
			include_name=include_name,
			compare_type=True,
			compare_server_default=True,
			version_table="alembic_version",
			version_table_schema="public",
		)

		with alembic_context.begin_transaction():
			alembic_context.run_migrations()


if alembic_context.is_offline_mode():
	run_migrations_offline()
else:
	run_migrations_online()
