# ---------------------------------------------------------------------------
# Model Registry
#
# Single source of truth for all domain model modules.
# Imported by alembic/env.py to populate SQLAlchemy metadata before any
# autogenerate or migration run.
#
# Add a new entry here whenever a new domain is introduced so that Alembic
# automatically sees its tables — no other file needs to change.
# ---------------------------------------------------------------------------

MODEL_MODULES: list[str] = [
    "app.domains.users.models.models",
    "app.domains.rbac.models.models",
    "app.domains.social_graph.models.models",
    "app.domains.communities.models.models",
    "app.domains.content.models.models",
    "app.domains.notifications.models.models",
]
