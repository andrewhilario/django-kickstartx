# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

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
