# Nginx Log Processor

A small, production-minded Django service that streams structured Nginx access
logs into a database and exposes a read-only API with filtering, search, and
pagination.

This project started as a take-home assignment in August 2024. I completed the
assignment, but did not receive an offer. In 2026 I revisited the code, kept the
original idea, and updated its dependencies, tests, security defaults, and
deployment setup.

## Features

- streaming JSON parsing without loading the complete log into memory;
- batched database inserts;
- HTTP(S) downloads with status checks and timeouts;
- authenticated, paginated REST API;
- exact filters and full-text-style search across common log fields;
- OpenAPI schema with optional Swagger UI and ReDoc;
- themed Django Unfold admin, health endpoint, PostgreSQL Compose stack, and Gunicorn;
- uv dependency locking, Ruff checks, pytest coverage, and GitHub Actions CI.

## Stack

- Python 3.13
- Django 6.1 and Django REST Framework 3.18
- PostgreSQL 17 in Docker; SQLite for zero-config local development
- ijson, django-filter, django-unfold, drf-spectacular, Gunicorn, and WhiteNoise
- uv, Ruff, pytest, and pytest-django

## Input format

The importer accepts consecutive JSON objects or one JSON object per line. Each
object is expected to follow this shape:

```json
{
  "time": "17/May/2015:08:05:32 +0000",
  "remote_ip": "192.0.2.1",
  "remote_user": "alice",
  "request": "GET /downloads/product_1 HTTP/1.1",
  "response": 200,
  "bytes": 1024
}
```

## Local development

Install [uv](https://docs.astral.sh/uv/), then run:

```bash
cp .env.example .env
uv sync --dev
uv run python manage.py migrate
uv run python manage.py createsuperuser
uv run python manage.py runserver
```

SQLite is used when database variables are not configured. The API requires an
authenticated Django user. Session authentication works through `/admin/`, and
Basic authentication is convenient for API clients over HTTPS.

Import a remote log file:

```bash
uv run python manage.py processlog https://example.com/access.log
uv run python manage.py processlog https://example.com/access.log --batch-size 500
```

The importer is an operator-only management command; its URL must use HTTP or
HTTPS. Do not expose arbitrary command execution to untrusted users.

## Admin interface

Visit `/admin/` after creating a superuser. Django Unfold provides the themed
dashboard and consistent user, group, and log-entry pages. Log entries can be
searched by IP address, user, or URI and filtered by HTTP method, response code,
and date. Imported fields are read-only and entries cannot be created manually;
use the `processlog` command as the ingestion path.

## API

| Endpoint | Purpose |
| --- | --- |
| `GET /api/logs/` | List imported entries; authentication required |
| `GET /api/schema/` | Download the OpenAPI schema |
| `GET /api/schema/swagger/` | Swagger UI when `ENABLE_API_DOCS=true` |
| `GET /api/schema/redoc/` | ReDoc when `ENABLE_API_DOCS=true` |
| `GET /health/` | Lightweight unauthenticated liveness check |

Exact filters are available for `ip_address`, `user`, `http_method`,
`request_uri`, `response_code`, and `response_size`. The `search` parameter
searches IP address, user, HTTP method, and URI.

```bash
curl -u reader:password \
  "http://127.0.0.1:8000/api/logs/?response_code=404&search=downloads"
```

## Docker

Copy the environment template and replace both placeholder secrets before
starting the stack:

```bash
cp .env.example .env
docker compose up --build
```

Compose waits for PostgreSQL, applies committed migrations, and starts Gunicorn.
Database data is stored in the named `postgres_data` volume. Create an admin
user inside the running container with:

```bash
docker compose exec web python manage.py createsuperuser
```

For an internet-facing deployment, terminate TLS at a trusted reverse proxy,
set the real hosts and CSRF origins, enable the secure-cookie settings from
`.env.example`, and keep API documentation disabled unless it is intentionally
public.

## Checks

```bash
uv run ruff check .
uv run ruff format --check .
uv run python manage.py makemigrations --check --dry-run
uv run pytest
```

The test suite covers environment parsing, streaming imports, error handling,
the management command, the rendered Unfold admin, authentication, API filtering
and search, the schema, health checks, and model behavior. Coverage is enforced
at 90%.

## Structure

- `config/` — Django settings, environment parsing, URLs, ASGI, and WSGI
- `logs/` — log model, API, admin integration, migrations, and importer command
- `tests/` — pytest suite
- `.github/workflows/ci.yml` — lint, formatting, migration, and test checks
- `Dockerfile` and `docker-compose.yml` — container image and PostgreSQL stack
