# E-Library API

[![CI](https://github.com/agent-mino/e-library-server/actions/workflows/ci.yml/badge.svg)](https://github.com/agent-mino/e-library-server/actions/workflows/ci.yml)

Async REST API for an e-library, built with **FastAPI** and **MongoDB** (Motor). It manages books, categories,
videos, readers and admin accounts, and backs the [admin dashboard](https://github.com/agent-mino/e-library-admin).

> **Group project.** My part was the Next.js admin dashboard ([e-library-admin](https://github.com/agent-mino/e-library-admin));
> this API was written with teammates.

## Endpoints

Interactive docs are served at `/docs` (Swagger UI) once the server is running.

| Area | Public | Signed-in user | Admin only |
|---|---|---|---|
| **Books** `/books` | list (filter by `category_id`, search with `q`), get one | | create, update, delete |
| **Categories** `/categories` | list (with book counts), get one | | create, rename, delete (blocked while books use it) |
| **Videos** `/videos` | list by category | | create, update, delete |
| **Users** `/user` | sign up, log in | view/edit own profile, change own password | list users, view any, delete |
| **Admins** `/admin` | log in; sign up *only for the first admin* | | `/admin/me`, edit own profile/password, create more admins |
| **Health** `/health` | database ping | | |

## Security model

- **JWT bearer tokens** (`Authorization: Bearer …`), signed with `JWT_SECRET` and carrying the account's role.
  Every write route checks the token; admin routes also check `role == "admin"`.
- **No open admin signup.** The first admin can bootstrap the system; after that only an admin can create admins.
- **Passwords** are hashed with bcrypt. Login failures return the same message whether the email or the password
  was wrong.
- **Ownership checks:** users and admins can only change their own profile and password.
- **Configuration from the environment.** No credentials in code; see `.env.example`.
- **Input validation** with Pydantic: malformed IDs give `400`, not a server error, and search text is matched
  literally rather than as a regular expression.

## Run locally

Requires Python 3.12+ and MongoDB (local or Atlas).

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env          # set MONGO_URI and a long random JWT_SECRET
uvicorn main:app --reload     # http://127.0.0.1:8000/docs
```

## Tests

The tests drive the API end to end against a real MongoDB (database `elibrary_test`, dropped between tests):
auth, permissions, ownership, CRUD and validation.

```bash
pytest -q          # needs MongoDB on localhost:27017 (or set MONGO_URI)
ruff check . && ruff format --check .
```

CI runs lint and the test suite against a MongoDB service container on every push.

## Project layout

```
main.py            app, CORS, router registration, /health
settings.py        environment configuration
database.py        Motor client
security.py        password hashing, JWT, auth dependencies, id parsing
models/            Pydantic request/response schemas
services/          database logic (accounts shared by users and admins)
routes/            HTTP routes and their permission rules
tests/             end-to-end API tests
```
