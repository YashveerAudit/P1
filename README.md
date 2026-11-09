# Blog Post Manager

A full-stack blog post manager: a **FastAPI + MongoDB** REST API and a **React** single-page app for creating, reading, updating and deleting blog posts.

> Status: core requirements complete. Frontend containerisation and authentication are in progress (see [Roadmap](#roadmap)).

## Tech stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11, FastAPI, Pydantic v2, PyMongo (async) |
| Database | MongoDB Atlas |
| Frontend | React 19, React Router 7, Vite |
| Testing | pytest, FastAPI TestClient |
| DevOps | Docker, Docker Compose |

**Why Python/FastAPI?** FastAPI gives request validation, typed models and interactive OpenAPI docs out of the box, which keeps the code small and lets the focus stay on structure, error handling and tests.

## Features

- Full CRUD for blog posts with server-side pagination
- Input validation on both client and server, with field-level error messages
- Consistent JSON error format across the whole API
- Structured request logging with a per-request ID (`X-Request-ID` header)
- Responsive UI: post grid, detail view, create/edit form, delete confirmation, loading/empty/error states, dark mode
- Containerised backend with a health check

## Project structure

```
.
├── blog-backend/
│   ├── app/
│   │   ├── main.py                 # App factory: CORS, logging, error handlers, routers
│   │   ├── core/                   # Settings (.env), logging, exceptions + handlers
│   │   ├── api/routes/posts.py     # HTTP layer – thin endpoints
│   │   ├── api/dependencies.py     # Dependency injection wiring
│   │   ├── services/               # Business logic (timestamps, not-found rules)
│   │   ├── repositories/           # Data access: PostRepository interface + MongoDB impl
│   │   ├── schemas/                # Request/response models (validation)
│   │   └── models/                 # Domain model
│   ├── tests/                      # API + service tests using an in-memory repository
│   └── Dockerfile
├── blog-frontend/
│   └── src/
│       ├── api/                    # fetch wrapper + typed API calls
│       ├── components/             # Layout, PostCard, PostEditor, ConfirmDialog, status UI
│       ├── hooks/useApi.js         # Data loading with loading/error/retry + request cancelling
│       ├── pages/                  # Home, PostDetail, PostForm (create/edit), NotFound
│       └── utils/                  # Validation rules, formatting
└── docker-compose.yml
```

### Design decisions

- **Layered architecture** – routes → service → repository. Each layer has one responsibility (SRP), and the HTTP layer never touches the database directly.
- **Dependency inversion** – the service depends on the abstract `PostRepository`, not on MongoDB. FastAPI's `Depends()` injects the MongoDB implementation at runtime; tests inject an in-memory one, so the test suite runs in under a second with no database.
- **Separate input and output schemas** – clients cannot set server-controlled fields such as `id` or timestamps (unknown fields are rejected).
- **One error shape** – every error is returned as `{"error": {"code", "message", "details?"}}`, so the frontend handles errors in one place.

## Getting started

### Prerequisites

- Python 3.9+ and Node.js 20+
- A MongoDB connection string (e.g. a free MongoDB Atlas cluster)
- Docker (optional)

### 1. Configure environment variables

```bash
cp blog-backend/.env.example blog-backend/.env
# then edit blog-backend/.env and set MONGO_URI
```

| Variable | Required | Default | Description |
|---|---|---|---|
| `MONGO_URI` | yes | – | MongoDB connection string |
| `MONGO_DB_NAME` | no | `blog_database` | Database name |
| `CORS_ORIGINS` | no | `["http://localhost:5173","http://127.0.0.1:5173"]` | Allowed browser origins (JSON list) |
| `LOG_LEVEL` | no | `INFO` | Logging level |

The frontend reads `VITE_API_URL` (default `http://127.0.0.1:8000`); see `blog-frontend/.env.example`.

### 2a. Run the backend locally

```bash
cd blog-backend
python -m venv .venv
.venv\Scripts\activate          # Windows  (macOS/Linux: source .venv/bin/activate)
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

API: http://127.0.0.1:8000 · Interactive docs: http://127.0.0.1:8000/docs

### 2b. …or run the backend with Docker

```bash
docker compose up --build
```

### 3. Run the frontend

```bash
cd blog-frontend
npm install
npm run dev
```

Open http://localhost:5173

## API reference

Base URL: `http://127.0.0.1:8000`

| Method | Endpoint | Description | Success |
|---|---|---|---|
| `GET` | `/api/posts?skip=0&limit=20` | List posts, newest first (`limit` 1–100) | `200` |
| `GET` | `/api/posts/{id}` | Get one post | `200` |
| `POST` | `/api/posts` | Create a post | `201` |
| `PUT` | `/api/posts/{id}` | Replace a post | `200` |
| `DELETE` | `/api/posts/{id}` | Delete a post | `204` |
| `GET` | `/api/health` | Health check | `200` |

**Request body** (`POST` / `PUT`):

```json
{ "title": "My first post", "content": "At least ten characters…", "author": "Jane" }
```

| Field | Rules |
|---|---|
| `title` | 3–150 characters (surrounding whitespace trimmed) |
| `content` | 10–20,000 characters |
| `author` | 2–80 characters |

**List response:**

```json
{ "items": [ { "id": "…", "title": "…", "content": "…", "author": "…",
               "created_at": "2026-11-10T09:00:00Z", "updated_at": "2026-11-10T09:00:00Z" } ],
  "total": 1, "skip": 0, "limit": 20 }
```

**Error response:**

```json
{ "error": { "code": "validation_error", "message": "The request data is invalid.",
             "details": [ { "field": "title", "message": "String should have at least 3 characters" } ] } }
```

| Status | Code | When |
|---|---|---|
| 404 | `post_not_found` | No post with that id |
| 422 | `validation_error` | Invalid body or query parameters |
| 503 | `database_unavailable` | MongoDB unreachable |
| 500 | `internal_error` | Unexpected error (details logged, never returned) |

## Testing

```bash
cd blog-backend
python -m pytest
```

25 tests cover every endpoint (success and failure paths), validation rules, pagination, timestamp behaviour, the standard error format and database-outage handling. Tests use an in-memory repository, so no database is required.

Frontend: `npm run lint` and `npm run build`.

## Security measures

- **No secrets in source control** – configuration comes from environment variables / a git-ignored `.env`.
- **Strict input validation** – length limits, whitespace trimming, unknown fields rejected (prevents clients injecting `_id` or timestamps).
- **CORS restricted** to the configured frontend origins.
- **XSS-safe rendering** – post content is rendered as text by React, never as raw HTML.
- **No internal details leaked** – unexpected and database errors return generic messages; full details go to server logs.
- **Container runs as a non-root user**; secrets are passed at runtime, not baked into the image.

## Roadmap

- [ ] Frontend Dockerfile + full-stack `docker compose up`
- [ ] Authentication (JWT) – only signed-in users can create, edit or delete posts
- [ ] Frontend component tests
