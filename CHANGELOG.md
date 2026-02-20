# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [1.0.5] — 2026-02-20

### 🐳 Docker Support

- **New `--docker` flag**: Adds a ready-to-use Docker setup to any generated project
- **`Dockerfile`**: Multi-stage-friendly, based on `python:3.12-slim-bookworm` (Debian Buster EOL replaced); uses `--no-cache-dir` and a single chained `RUN` to minimise image layers and size
- **`docker-compose.yml`**: PostgreSQL projects get a full `web` + `db` service setup; SQLite projects get a minimal single-service config; deprecated `version:` field removed
- **`entrypoint.sh`**: Generated for PostgreSQL projects only — waits for the database to be ready via `nc` before running migrations; `set -e` ensures the container exits on any failure
- **`.dockerignore`**: Excludes `venv`, `__pycache__`, `.env`, `*.sqlite3`, `staticfiles/`, `media/`, and other build-irrelevant paths
- **Health-checked `depends_on`**: Compose uses `condition: service_healthy` with a `pg_isready` healthcheck on the `db` service — container startup order is now truly safe
- **Correct Docker DB host**: `DB_HOST` is injected as `db` (the Compose service name) via the `environment` block, overriding any `.env` value that would incorrectly point to `localhost`
- **Context-aware next steps**: When `--docker` is used, the post-generation output shows `docker-compose up --build` and `docker-compose exec web python manage.py createsuperuser` instead of local-dev instructions

## [1.0.2] — 2026-02-18

### 🚀 Features

- **Auto virtual environment**: `django-kickstart create` now automatically creates a venv and installs dependencies
- **Cross-platform support**: Improved Windows/Unix compatibility for venv creation

## [1.0.0] — 2026-02-18

### 🚀 Features
- **Project type choice**: Generate MVP (traditional Django with templates) or API (Django REST Framework) projects
- **View style choice**: Function-Based Views (FBV) or Class-Based Views (CBV)
- **Database choice**: SQLite (development) or PostgreSQL (production)
- Interactive CLI with colorful prompts and one-liner flag mode
- Production-ready `settings.py` with environment variable support via `python-decouple`
- Admin panel enabled and configured out of the box
- URL routing fully wired (admin + app)
- Example `Item` model with admin registration, tests, and views
- DRF browsable API with pagination and permissions (API projects)
- CORS support via `django-cors-headers` (API projects)
- Modern starter HTML templates and CSS (MVP projects)
- `ModelForm` with widget customization (MVP projects)
- `.env.example` and `.gitignore` auto-generated

### 🔒 Security
- **Auto-generated SECRET_KEY**: Each project gets a unique 50-character cryptographically random key — no shared insecure defaults
- **Mandatory SECRET_KEY**: App fails immediately if `SECRET_KEY` is not set in environment, preventing silent insecure operation
- **Path traversal protection**: All generated file paths are validated to stay within the project directory
- **Overwrite protection**: CLI refuses to overwrite existing project directories, preventing accidental data loss
- **Input validation**: Project names are validated against a strict `[a-zA-Z_][a-zA-Z0-9_]*` pattern in both CLI and generator
- **API permissions**: All FBV API views include `@permission_classes([IsAuthenticatedOrReadOnly])` — matching CBV security
- **`.env` in `.gitignore`**: Secrets are excluded from version control by default, while `.env.example` is preserved
- Production security settings (HSTS, secure cookies, XSS protection) included as ready-to-uncomment block
- All 4 Django password validators enabled by default
