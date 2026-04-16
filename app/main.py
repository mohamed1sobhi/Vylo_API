from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.domains.users.api.router import router as users_router
from app.domains.rbac.api.router import router as rbac_router
from app.domains.social_graph.api.router import router as social_graph_router
from app.domains.communities.api.router import router as communities_router
from app.domains.content.api.router import router as content_router
from app.domains.notifications.api.router import router as notifications_router

API_V1_PREFIX = "/api/v1"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Phase 10: seed RBAC defaults and register event handlers here
    yield
    # Phase 10: teardown (e.g. close DB connections) here


app = FastAPI(
    title="Social Media API",
    version="1.0.0",
    lifespan=lifespan,
)


# ---------------------------------------------------------------------------
# Global exception handlers
# ---------------------------------------------------------------------------

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


# ---------------------------------------------------------------------------
# Domain routers
# ---------------------------------------------------------------------------

app.include_router(users_router, prefix=API_V1_PREFIX)
app.include_router(rbac_router, prefix=API_V1_PREFIX)
app.include_router(social_graph_router, prefix=API_V1_PREFIX)
app.include_router(communities_router, prefix=API_V1_PREFIX)
app.include_router(content_router, prefix=API_V1_PREFIX)
app.include_router(notifications_router, prefix=API_V1_PREFIX)
