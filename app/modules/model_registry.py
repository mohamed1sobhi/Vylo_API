"""Model modules Alembic imports to populate every schema's metadata."""

MODEL_MODULES: tuple[str, ...] = (
	"app.modules.users.models.models",
	"app.modules.admins.models.models",
	"app.modules.social_graph.models.models",
	"app.modules.communities.models.models",
	"app.modules.content.models.models",
	"app.modules.notifications.models.models",
)


__all__ = ["MODEL_MODULES"]
