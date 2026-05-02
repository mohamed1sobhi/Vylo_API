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
    "app.modules.users.models.models",
    "app.modules.auth.models.models",
    "app.modules.social_graph.models.models",
    "app.modules.communities.models.models",
    "app.modules.content.models.models",
    "app.modules.notifications.models.models",
]
