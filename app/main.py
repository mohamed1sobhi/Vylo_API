from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.modules.users.api.router import router as users_router
from app.modules.auth.api.router import router as auth_router
from app.modules.social_graph.api.router import router as social_graph_router
from app.modules.communities.api.router import router as communities_router
from app.modules.content.api.router import router as content_router
from app.modules.notifications.api.router import router as notifications_router
from app.shared.exceptions.handlers import register_exception_handlers

API_V1_PREFIX = "/api/v1"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Phase 10: register startup singletons such as notification listeners here.
    yield
    # Phase 10: teardown (e.g. close DB connections) here


app = FastAPI(
    title="Social Media API",
    version="1.0.0",
    lifespan=lifespan,
)

register_exception_handlers(app)


# ---------------------------------------------------------------------------
# Domain routers
# ---------------------------------------------------------------------------

app.include_router(users_router, prefix=API_V1_PREFIX)
app.include_router(auth_router, prefix=API_V1_PREFIX)
app.include_router(social_graph_router, prefix=API_V1_PREFIX)
app.include_router(communities_router, prefix=API_V1_PREFIX)
app.include_router(content_router, prefix=API_V1_PREFIX)
app.include_router(notifications_router, prefix=API_V1_PREFIX)
