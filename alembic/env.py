import logging
import sys
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import engine_from_config, pool, text

from alembic import context as alembic_context

# ---------------------------------------------------------------------------
# Make the project root importable so "app.*" imports resolve correctly.
# ---------------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.shared.config.settings import settings  # noqa: E402
from app.shared.database.session import Base  # noqa: E402
from app.modules.model_registry import MODEL_MODULES  # noqa: E402

# ---------------------------------------------------------------------------
# Load every domain's models so SQLAlchemy metadata is fully populated before
# Alembic inspects it for autogenerate.  Each import is guarded so env.py
# stays functional even before a domain's models have been written.
# ---------------------------------------------------------------------------
_log = logging.getLogger(__name__)

for _mod in MODEL_MODULES:
    try:
        __import__(_mod)
    except Exception as _exc:  # pragma: no cover
        _log.warning("[model_registry] Could not import '%s': %s", _mod, _exc)

# ---------------------------------------------------------------------------
# Standard Alembic config.
# ---------------------------------------------------------------------------
config = alembic_context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Use MIGRATION_DATABASE_URL directly — a dedicated sync (psycopg2) URL stored
# in .env.  No driver string replacement needed.
config.set_main_option("sqlalchemy.url", settings.MIGRATION_DATABASE_URL)

target_metadata = Base.metadata

# All known PostgreSQL schemas.  Any schema that is not listed here cannot be
# selected and will be rejected at runtime.
_SCHEMAS: list[str] = [
    "users",
    "auth",
    "social_graph",
    "communities",
    "content",
    "notifications",
]

# Absolute path to the per-schema version directories.
_VERSIONS_ROOT: Path = Path(__file__).resolve().parent / "versions"


# ---------------------------------------------------------------------------
# Schema selection
#
# For revision commands, -x schema=<domain> is required:
#   alembic -x schema=users revision --autogenerate -m "users_init"
#   alembic -x schema=users revision -m "users_init"
#
# For upgrade/downgrade, no -x schema is needed:
#   alembic upgrade head
#   alembic downgrade -1
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# include_object — filter autogenerate diff to the selected schema only.
# Reads -x schema lazily so upgrade/downgrade are unaffected (no schema = include all).
# ---------------------------------------------------------------------------
def include_object(obj, name: str, type_: str, reflected: bool, compare_to) -> bool:
    if type_ == "table":
        schema = alembic_context.get_x_argument(as_dictionary=True).get("schema", "")
        if schema:
            return getattr(obj, "schema", None) == schema
    return True


# ---------------------------------------------------------------------------
# process_revision_directives — validate schema and auto-route migration files.
#
# Runs only during `alembic revision`.  This is the single place where
# -x schema=<domain> is enforced.  The final file path is always:
#   alembic/versions/<schema>/<rev>_<slug>.py
# ---------------------------------------------------------------------------
def process_revision_directives(context, revision, directives) -> None:  # type: ignore[override]
    if not directives:
        return
    x_args = alembic_context.get_x_argument(as_dictionary=True)
    schema = x_args.get("schema")
    if not schema:
        raise RuntimeError(
            "\n[Alembic] ERROR: No schema specified.\n"
            "  Every revision command requires: alembic -x schema=<domain> revision ...\n"
            f"  Valid schemas: {', '.join(_SCHEMAS)}\n"
        )
    if schema not in _SCHEMAS:
        raise RuntimeError(
            f"\n[Alembic] ERROR: Unknown schema '{schema}'.\n"
            f"  Valid schemas: {', '.join(_SCHEMAS)}\n"
        )
    target_dir: Path = _VERSIONS_ROOT / schema
    target_dir.mkdir(parents=True, exist_ok=True)
    for script in directives:
        script.version_path = str(target_dir)


# ---------------------------------------------------------------------------
# Offline mode
# ---------------------------------------------------------------------------
def run_migrations_offline() -> None:
    """Emit migration SQL to stdout without a live DB connection."""
    url = config.get_main_option("sqlalchemy.url")
    alembic_context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_schemas=True,
        include_object=include_object,
        process_revision_directives=process_revision_directives,
        compare_type=True,
        compare_server_default=True,
        version_table="alembic_version",
        version_table_schema="public",
    )

    with alembic_context.begin_transaction():
        alembic_context.run_migrations()


# ---------------------------------------------------------------------------
# Online mode (sync psycopg2 connection — Alembic requirement, never asyncpg)
# ---------------------------------------------------------------------------
def run_migrations_online() -> None:
    """Run migrations against a live database using a synchronous connection."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        # Ensure all domain schemas exist before running any migration.
        for schema in _SCHEMAS:
            connection.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema}"))
        connection.commit()

        alembic_context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_schemas=True,
            include_object=include_object,
            process_revision_directives=process_revision_directives,
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
