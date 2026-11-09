# Blog Post Manager

A full-stack blog post manager: a **FastAPI + MongoDB** REST API and a **React** single-page app for creating, reading, updating and deleting blog posts, with JWT authentication so only a post's author can edit or delete it.

## Tech stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11, FastAPI, Pydantic v2, PyMongo (async) |
| Auth | JWT access tokens (PyJWT), Argon2 password hashing (pwdlib) |
| Database | MongoDB Atlas |
| Frontend | React 19, React Router 7, Vite |
| Testing | pytest, FastAPI TestClient |
| DevOps | Docker, Docker Compose |

**Why Python/FastAPI?** FastAPI gives request validation, typed models and interactive OpenAPI docs out of the box, which keeps the code small and lets the focus stay on structure, error handling and tests.

## Features

- Full CRUD for blog posts with server-side pagination
- Sign up / log in; posts are owned by their author, and only the author can edit or delete them
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
│   │   ├── core/                   # Settings (.env), logging, security (JWT/hashing), exceptions
│   │   ├── api/routes/             # HTTP layer – thin endpoints (posts.py, auth.py)
│   │   ├── api/dependencies.py     # Dependency injection + current-user resolution
│   │   ├── services/               # Business logic (ownership rules, timestamps, login)
│   │   ├── repositories/           # Data access: abstract interfaces + MongoDB implementations
│   │   ├── schemas/                # Request/response models (validation)
│   │   └── models/                 # Domain models (Post, User)
│   ├── tests/                      # 43 API + service tests using in-memory repositories
│   └── Dockerfile
├── blog-frontend/
│   └── src/
│       ├── api/                    # fetch wrapper (adds the token), typed API calls, token storage
│       ├── context/                # AuthProvider + useAuth hook
│       ├── components/             # Layout, PostCard, PostEditor, AuthForm, RequireAuth, ConfirmDialog…
│       ├── hooks/useApi.js         # Data loading with loading/error/retry + request cancelling
│       ├── pages/                  # Home, PostDetail, PostForm (create/edit), Login, Register, NotFound
│       └── utils/                  # Validation rules, formatting
└── docker-compose.yml
```

### Design decisions

- **Layered architecture** – routes → service → repository. Each layer has one responsibility (SRP), and the HTTP layer never touches the database directly.
- **Dependency inversion** – services depend on the abstract `PostRepository` / `UserRepository`, not on MongoDB. FastAPI's `Depends()` injects the MongoDB implementations at runtime; tests inject in-memory ones, so the whole suite runs in a few seconds with no database.
- **Separate input and output schemas** – clients cannot set server-controlled fields such as `id`, `author`, `owner_id` or timestamps (unknown fields are rejected). The author is always the signed-in user.
- **Authorisation lives in the service layer** – `PostService` checks ownership before any update/delete, so the rule holds no matter which route calls it. The UI hides the buttons too, but the server is the source of truth.
- **One error shape** – every error is returned as `{"error": {"code", "message", "details?"}}`, so the frontend handles errors in one place (including signing the user out automatically when a token expires).

## Getting started

### Prerequisites

- Python 3.9+ and Node.js 20+
- A MongoDB connection string (e.g. a free MongoDB Atlas cluster)
- Docker (optional)

### 1. Configure environment variables

```bash
cp blog-backend/.env.example blog-backend/.env
# then edit blog-backend/.env: set MONGO_URI and a random JWT_SECRET
```

| Variable | Required | Default | Description |
|---|---|---|---|
| `MONGO_URI` | yes | – | MongoDB connection string |
| `JWT_SECRET` | yes | – | Random string (32+ chars) used to sign login tokens |
| `MONGO_DB_NAME` | no | `blog_database` | Database name |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | no | `720` | How long a login lasts |
| `CORS_ORIGINS` | no | `["http://localhost:5173","http://127.0.0.1:5173"]` | Allowed browser origins (JSON list) |
| `LOG_LEVEL` | no | `INFO` | Logging level |

Generate a secret with `python -c "import secrets; print(secrets.token_urlsafe(48))"`.

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

Open http://localhost:5173, create an account via **Sign up**, and start posting.

## API reference

Base URL: `http://127.0.0.1:8000`. Endpoints marked 🔒 need an `Authorization: Bearer <token>` header.

### Auth

| Method | Endpoint | Description | Success |
|---|---|---|---|
| `POST` | `/api/auth/register` | Create an account, returns a token | `201` |
| `POST` | `/api/auth/login` | Log in, returns a token | `200` |
| `GET` | `/api/auth/me` 🔒 | The signed-in user | `200` |

```json
// POST /api/auth/register
{ "email": "jane@example.com", "name": "Jane", "password": "at-least-8-chars" }

// response (register and login)
{ "access_token": "eyJ…", "token_type": "bearer",
  "user": { "id": "…", "email": "jane@example.com", "name": "Jane" } }
```

### Posts

| Method | Endpoint | Description | Success |
|---|---|---|---|
| `GET` | `/api/posts?skip=0&limit=20` | List posts, newest first (`limit` 1–100) | `200` |
| `GET` | `/api/posts/{id}` | Get one post | `200` |
| `POST` | `/api/posts` 🔒 | Create a post (author = signed-in user) | `201` |
| `PUT` | `/api/posts/{id}` 🔒 | Replace a post – owner only | `200` |
| `DELETE` | `/api/posts/{id}` 🔒 | Delete a post – owner only | `204` |
| `GET` | `/api/health` | Health check | `200` |

**Request body** (`POST` / `PUT`):

```json
{ "title": "My first post", "content": "At least ten characters…" }
```

| Field | Rules |
|---|---|
| `title` | 3–150 characters (surrounding whitespace trimmed) |
| `content` | 10–20,000 characters |

**List response:**

```json
{ "items": [ { "id": "…", "title": "…", "content": "…", "author": "Jane", "owner_id": "…",
               "created_at": "2026-11-10T09:00:00Z", "updated_at": "2026-11-10T09:00:00Z" } ],
  "total": 1, "skip": 0, "limit": 20 }
```

### Errors

```json
{ "error": { "code": "validation_error", "message": "The request data is invalid.",
             "details": [ { "field": "title", "message": "String should have at least 3 characters" } ] } }
```

| Status | Code | When |
|---|---|---|
| 401 | `not_authenticated` | Missing, invalid or expired token |
| 401 | `invalid_credentials` | Wrong email or password (same response for both) |
| 403 | `forbidden` | Editing or deleting someone else's post |
| 404 | `post_not_found` | No post with that id |
| 409 | `email_already_registered` | Sign-up with an existing email |
| 422 | `validation_error` | Invalid body or query parameters |
| 503 | `database_unavailable` | MongoDB unreachable |
| 500 | `internal_error` | Unexpected error (details logged, never returned) |

## Testing

```bash
cd blog-backend
python -m pytest
```

43 tests cover every endpoint (success and failure paths), validation rules, pagination, timestamps, ownership rules (403 for another user's post), registration/login, expired and forged tokens, the standard error format and database-outage handling. Tests use in-memory repositories, so no database is required.

Frontend: `npm run lint` and `npm run build`.

## Security measures

- **No secrets in source control** – configuration comes from environment variables / a git-ignored `.env`.
- **Passwords are hashed with Argon2** and never stored, returned or logged in plain text.
- **JWT access tokens** are signed with a server-side secret and expire; forged or expired tokens are rejected.
- **Ownership enforced server-side** – only the author can modify a post, regardless of what the UI shows.
- **Identical login errors** for unknown email and wrong password, so attackers cannot enumerate accounts.
- **Strict input validation** – length limits, whitespace trimming, unknown fields rejected (prevents clients setting `_id`, `author` or `owner_id`).
- **Unique email index** in MongoDB, so duplicates are impossible even under concurrent sign-ups.
- **CORS restricted** to the configured frontend origins.
- **XSS-safe rendering** – post content is rendered as text by React, never as raw HTML.
- **No internal details leaked** – unexpected and database errors return generic messages; full details go to server logs.
- **Container runs as a non-root user**; secrets are passed at runtime, not baked into the image.

**Known trade-off:** the frontend stores the token in `localStorage` so a refresh keeps you signed in. This is safe only because the app never renders untrusted HTML; a production system would move to an `httpOnly` cookie with CSRF protection and add refresh tokens plus login rate-limiting.

## Roadmap

- [ ] Frontend Dockerfile + full-stack `docker compose up`
- [ ] Login rate-limiting and refresh tokens
- [ ] Frontend component tests
