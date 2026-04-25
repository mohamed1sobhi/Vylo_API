# Engineering Guidelines — Vylo Social Media API

This document is the authoritative reference for architecture rules, coding constraints, and design contracts for this project. Every coding session must follow these rules without exception.

---

## 1. Module Internal Layer Rules

Every module under `app/modules/<module>/` must follow this strict internal layering:

| Layer | Responsibility | May Import From |
|---|---|---|
| `models/` | SQLAlchemy ORM entities | `shared/database/session.py` (Base), SQLAlchemy only |
| `repositories/` | All SQL operations | own `models/` only, SQLAlchemy types |
| `services/` | Pure business logic | `shared/auth/jwt.py`, `shared/events/bus.py`, `shared/events/events.py` (event class imports only) |
| `clients/` | Outbound adapters to other modules | own `schemas/public_schemas/responses.py` (boundary validation only) |
| `public/` | Inbound facade for other modules | own `schemas/public_schemas/requests.py` (boundary validation only) |
| `api/` | FastAPI routes, HTTP entry point | own `schemas/api_schemas.py`, `shared/auth/dependencies.py`, `shared/dependencies/<module>_deps.py` |

**No layer imports another layer of the same module** (e.g. `services/` must not import `repositories/`). All cross-layer coupling is delivered through `__init__` constructor injection, wired exclusively in `shared/dependencies/<module>_deps.py`.

---

## 2. Schema Layer Rules

| Schema File | Purpose | Used By |
|---|---|---|
| `schemas/api_schemas.py` | HTTP request/response Pydantic models | `api/` only |
| `schemas/public_schemas/requests.py` | Public-facade ingress validation models owned by the receiving domain | same domain `public/` only |
| `schemas/public_schemas/responses.py` | Client egress validation models owned by the consuming domain | same domain `clients/` only |

- `api_schemas` must **never** be used outside the `api/` layer.
- `public_schemas/requests.py` must **never** be imported outside its own module's `public/` layer.
- `public_schemas/responses.py` must **never** be imported outside its own module's `clients/` layer.
- No module may import another module's `schemas/public_schemas/*` files.
- `public_schemas.py`, `dto.py`, and `dtos.py` are forbidden for inter-module contracts.

---

## 3. Service Purity Contract

Services work exclusively with **pure Python types** (primitives, dataclasses, plain dicts). Neither Pydantic models nor SQLAlchemy ORM models may cross the service boundary in either direction.

- `api/` maps `api_schemas` → pure types → calls service → maps result back to `api_schemas`
- `public/` validates inbound inter-module payloads with own `schemas/public_schemas/requests.py` → converts to pure types → calls service → returns pure Python payloads
- `clients/` receives pure Python payloads from the foreign facade → validates them with own `schemas/public_schemas/responses.py` → converts to pure types → returns to own service
- All Pydantic validation for cross-module communication happens only at `public/` ingress and `clients/` egress.

---

## 4. Constructor-Based Dependency Injection Contract

All repositories, services, public facades, and clients use `__init__` constructor injection. No layer self-instantiates its own dependencies.

| Component | Injected With |
|---|---|
| `Repository` | `AsyncSession` |
| `Service` | own `Repository` instances + own `Client` instances |
| `Public facade` | own `Service` instance |
| `Outbound Client` | other module's `Public facade` instance |

All wiring is performed by FastAPI `Depends()` chains defined **exclusively** in `shared/dependencies/<module>_deps.py`. The `_deps.py` file is always the **last artifact** built in each phase.

---

## 5. Centralized Composition Root

`shared/dependencies/` is the **only** place where cross-module wiring occurs.

- Each module has exactly one corresponding `<module>_deps.py`.
- These files import concrete classes from modules and chain `Depends()` providers.
- A `_deps.py` may import another `_deps.py` to reuse an already-wired facade instance.
- Only `api/router.py` files and `main.py` (lifespan startup only) may import from `shared/dependencies/`.
- `services/`, `clients/`, and `public/` must **never** import from `shared/dependencies/`.

| File | Imports from |
|---|---|
| `users_deps.py` | `modules/users/*` only |
| `rbac_deps.py` | `modules/rbac/*` + `users_deps` |
| `social_graph_deps.py` | `modules/social_graph/*` + `users_deps` |
| `communities_deps.py` | `modules/communities/*` + `users_deps` |
| `content_deps.py` | `modules/content/*` + `communities_deps` |
| `notifications_deps.py` | `modules/notifications/*` + `communities_deps` + `users_deps` |

---

## 6. Communication Flow — The Single-Hop Rule

```
External request
      │
      ▼
Module A / api/              ← maps api_schema → pure type; calls injected Service
      │
      ▼
Module A / services/         ← pure logic; calls injected Client for cross-module needs
      │
      ▼
Module A / clients/          ← calls injected B/public/ facade; validates returned pure payload with own responses.py; returns pure type
      │
      ▼
Module B / public/           ← validates inbound payload with own requests.py; calls injected Service; returns pure Python payload
      │
      ▼
Module B / services/         ← pure logic
```

Cross-module calls are always exactly **one hop**: `clients/` → `public/`. Chaining public facades is forbidden.

---

## 7. Strict Prohibitions

```
❌ Any layer           →  imports another layer of the same module (outside the allowed list in §1)
❌ Any layer           →  imports anything from another module directly
❌ Any layer           →  imports another module's `schemas/public_schemas/*`
❌ api/                →  imports other module's public/ or api/
❌ public/             →  imports other module's public/ (no chaining)
❌ services/           →  imports repositories/, models/, api_schemas, public_schemas, or any other module
❌ services/           →  imports shared/dependencies/
❌ clients/            →  imports other module's services/, repositories/, models/, or schemas/
❌ handlers/           →  imports other module's public/, services/, repositories/, or models/
❌ shared/auth/dependencies.py → imports any module
❌ Any layer           →  uses `public_schemas.py`, `dto.py`, or `dtos.py` for inter-module boundaries

✅ services/           →  shared/auth/jwt.py              (token issuance + password hashing)
✅ services/           →  shared/events/bus.py             (event publishing only)
✅ services/           →  shared/events/events.py          (event class imports for publishing)
✅ models/             →  shared/database/session.py       (Base)
✅ repositories/       →  own models/                      (only this layer)
✅ clients/            →  own `schemas/public_schemas/responses.py` (boundary validation only)
✅ public/             →  own `schemas/public_schemas/requests.py`  (boundary validation only)
✅ api/                →  shared/auth/dependencies.py      (get_current_user, require_permission)
✅ api/                →  shared/dependencies/<module>_deps.py
✅ main.py (lifespan)  →  shared/dependencies/<module>_deps.py  (startup wiring only)
✅ _deps.py            →  own module's concrete classes + other _deps.py files
```

---

## 8. Authentication Contract

### Token Issuance — owned by `users/services/`

- `UserService` imports `hash_password`, `verify_password`, `create_access_token`, `create_refresh_token`, `decode_token` directly from `shared/auth/jwt.py`.
- Tokens are issued on `register`, `login`, and `refresh` — all inside `UserService`.
- The JWT payload **must** embed everything needed for authorization at request time:
  - `user_id`
  - `system_permissions: list[str]`

### Token Verification — stateless and shared

- `shared/auth/jwt.py` — pure functions only; zero DB calls, zero module imports.
- `shared/auth/dependencies.py` — stateless FastAPI helpers; **zero imports from any module or `shared/dependencies/`**.
  - Uses `OAuth2PasswordBearer` for Bearer token extraction.
  - `get_current_user` — extracts the Bearer token, calls `decode_token`, returns the raw claims **dict** (not a Pydantic model).
  - `require_permission(codename)` — closure that checks `current_user["system_permissions"]`; raises `ForbiddenError` if absent.

### OAuth2 Login Input Contract

- Login endpoints must use FastAPI `OAuth2PasswordRequestForm` as the input form contract.

### No DB Calls at Request Time

**No route or service ever calls a DB query to resolve permissions at request time.** All permission data is already embedded in the token. `shared/auth/dependencies.py` checks only the token claims.

---

## 9. Layer Build Order

Within every module phase, always build in this order:

```
models → repositories → services → clients → public → schemas → api
→ shared/dependencies/<module>_deps.py
```

The `_deps.py` file is always the **last artifact** in each phase. It is the composition step that wires everything together.

---

## 10. Cross-Module Dependency Graph

```
users           ← no outbound module dependencies
rbac            → users
social_graph    → users
communities     → users
content         → communities
notifications   → communities, users
```

No module may introduce a dependency not listed in this graph.

---

## 11. Database Schema Rules

- Foreign keys that cross PostgreSQL schemas (e.g. `rbac.user_roles.user_id` → `users.users.id`) are **soft references** (plain UUID columns, no FK constraint). Hard FK constraints are only used within the same PostgreSQL schema.
- Alembic is configured for multi-schema migrations covering all 6 schemas: `users`, `rbac`, `social_graph`, `communities`, `content`, `notifications`.
- Alembic migrations must use a separate synchronous database URL (`MIGRATION_DATABASE_URL`) loaded from `.env`.
- `get_db()` must use the following session atomicity guard:

```python
async with AsyncSessionLocal() as session:
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()
```

---

## 12. Event Bus Rules

- `shared/events/base.py` defines `DomainEvent` (dataclass: `event_id: UUID`, `occurred_at: datetime` UTC).
- `shared/events/bus.py` implements the singleton `EventBus` using an `@subscribe` async decorator pattern; `bus.publish(event)` fans out to all registered handlers via `asyncio.gather`.
- **Event contracts** (e.g. `UserRegisteredEvent`, `FriendRequestSentEvent`) are defined in `shared/events/events.py`. These are the only shared objects that cross the publisher/subscriber boundary — they must never carry ORM models or Pydantic schemas.
- Module services that publish events import their event class from `shared/events/events.py` and call `await bus.publish(event)`.
- **Handler registration** is performed inside `NotificationService._setup_event_listeners()` using the `@event_bus.subscribe(EventClass)` decorator. This method is called once during `NotificationService.__init__`. The `NotificationService` is instantiated as a startup singleton via `notifications_deps.py` — not re-created per request.
- Handler methods live inside `NotificationService` and receive all required infrastructure and outbound clients via the service's `__init__` constructor — no self-instantiation, no module imports.
- Handlers must convert `DomainEvent` data into pure Python types before calling repository methods or passing data to delivery infrastructure.
- The event bus is used **only for notification triggers** — it must not replace the `clients/` → `public/` communication pattern for data flow.
- Services import the bus as `from app.shared.events.bus import bus`; event types are imported as `from app.shared.events.events import <EventClass>`.

---

## 13. Shared Infrastructure Rules

| Component | File | Rule |
|---|---|---|
| Settings | `shared/config/settings.py` | Single `BaseSettings` instance; all config from environment variables |
| Database | `shared/database/session.py` | Async engine only (`create_async_engine`); `get_db` yields `AsyncSession` with atomicity guard |
| JWT + hashing | `shared/auth/jwt.py` | Pure functions only — zero DB access, zero module imports |
| Auth dependencies | `shared/auth/dependencies.py` | Zero module imports; only decodes token; uses `OAuth2PasswordBearer` |
| WebSocket manager | `shared/websockets/manager.py` | Module-level singleton; injected into `NotificationService` via constructor DI |
| Exception handlers | `shared/exceptions/handlers.py` | Covers `HTTPException`, `RequestValidationError`, unhandled 500 |
| Composition roots | `shared/dependencies/<module>_deps.py` | One file per module; the only place cross-module wiring happens |

---

## 14. Notification Service Zero-Import Rule

`NotificationService` must have **zero cross-module imports**. Its constructor receives all required dependencies via injection:

**Infrastructure dependencies:**
- `NotificationRepository`
- `InMemoryConnectionManager` (WebSocket delivery)
- `EmailClient` (email delivery)
- `TwilioSMSClient` (SMS delivery)

**Outbound clients (for cross-module reads inside handlers):**
- `UsersClient` (e.g. resolve a user's email address or phone number)
- `CommunitiesClient` (e.g. resolve community owner/member list for fan-out)

All cross-module lookups are performed by calling methods on these injected client instances. Clients receive their foreign facade via `__init__` injection, validate returned payloads with their own `schemas/public_schemas/responses.py`, and never import another module's schemas at any level.

Handler methods live inside `NotificationService` and are registered via `@event_bus.subscribe` inside `_setup_event_listeners()`. Each handler: persists a DB notification row, broadcasts via `InMemoryConnectionManager`, and triggers `EmailClient`/`TwilioSMSClient` as required by the event type. Handlers must convert `DomainEvent` data to pure Python types before calling repository methods or delivery infrastructure.
