# 🚀 Django Kickstart

**Scaffold production-ready Django projects in seconds.**

Skip the boilerplate. Start building.

[![PyPI version](https://badge.fury.io/py/django-kickstartx.svg)](https://pypi.org/project/django-kickstartx/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

---

## ✨ Features

- **Two project types**: MVP (traditional Django with templates) or API (Django REST Framework)
- **View style choice**: Function-Based Views (FBV) or Class-Based Views (CBV)
- **Database options**: SQLite (dev) or PostgreSQL (production)
- **Docker support**: Optional `--docker` flag generates a production-ready `Dockerfile`, `docker-compose.yml`, and `entrypoint.sh`
- **Auto virtual environment**: Creates a venv and installs dependencies automatically
- **Production-ready settings**: Security hardened, environment variables via `python-decouple`
- **Admin panel**: Enabled and configured out of the box
- **URL routing**: Fully wired with app URLs included
- **Example model**: `Item` model with admin registration, tests, and views
- **Beautiful starter templates**: Modern CSS with responsive layout (MVP only)
- **DRF browsable API**: Auto-configured with pagination and permissions (API only)

---

## 📦 Installation

```bash
pip install django-kickstartx
```

---

## 🚀 Quick Start

### Interactive mode (guided prompts)

```bash
django-kickstart create myproject
```

### Flag mode (one-liner)

```bash
# MVP with function-based views + SQLite
django-kickstart create myproject --type mvp --views fbv --db sqlite

# REST API with class-based views + PostgreSQL
django-kickstart create myproject --type api --views cbv --db postgresql

# Any project with Docker support
django-kickstart create myproject --type api --views fbv --db postgresql --docker
```

### After creating your project

A virtual environment is created automatically with all dependencies installed.

```bash
cd myproject
# Activate the virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

> **Tip:** Use `--no-venv` to skip automatic virtual environment creation.

### With Docker

If you used `--docker`, skip the venv entirely and use Compose:

```bash
cd myproject
cp .env.example .env
docker compose up --build
```

Once the containers are running:

```bash
docker compose exec web python manage.py createsuperuser
```

> **Note:** For PostgreSQL projects, the `web` container waits for the database to pass its health check before running migrations automatically.

---

## 🔧 Options

| Flag | Choices | Default | Description |
|---|---|---|---|
| `--type` | `mvp`, `api` | interactive | MVP (templates) or API (DRF) |
| `--views` | `fbv`, `cbv` | interactive | Function or class-based views |
| `--db` | `sqlite`, `postgresql` | interactive | Database backend |
| `--app` | identifier | `core` | Name of the starter Django app |
| `--no-venv` | — | `false` | Skip automatic virtual environment creation |
| `--docker` | — | `false` | Add Docker configuration (`Dockerfile`, `docker-compose.yml`, `.dockerignore`, and `entrypoint.sh`) |

---

## 📁 Generated Structure

### MVP Project

```
myproject/
├── venv/                       # Auto-created virtual environment
├── manage.py
├── requirements.txt
├── .env.example
├── .gitignore
├── myproject/
│   ├── settings.py         # Security, DB, static/media config
│   ├── urls.py             # Admin + core app wired
│   ├── wsgi.py
│   └── asgi.py
├── core/
│   ├── migrations/
│   │   └── 0001_initial.py # Ready-to-run initial migration
│   ├── admin.py            # Item model registered
│   ├── models.py           # Example Item model
│   ├── views.py            # FBV or CBV
│   ├── urls.py
│   ├── forms.py            # ModelForm
│   ├── tests.py
│   └── templates/core/
│       ├── base.html
│       ├── home.html
│       └── about.html
└── static/css/
    ├── tokens.css          # OKLCH design tokens (Cobalt theme)
    └── style.css           # Hallmark anti-slop starter stylesheet
```

### API (DRF) Project

```
myproject/
├── venv/                       # Auto-created virtual environment
├── manage.py
├── requirements.txt
├── .env.example
├── .gitignore
├── myproject/
│   ├── settings.py         # DRF + CORS config included
│   ├── urls.py             # Admin + /api/ router
│   ├── wsgi.py
│   └── asgi.py
└── core/
    ├── migrations/
    │   └── 0001_initial.py  # Ready-to-run initial migration
    ├── admin.py
    ├── models.py
    ├── serializers.py       # DRF ModelSerializer
    ├── views.py             # @api_view or ModelViewSet
    ├── urls.py              # DRF Router or explicit paths
    └── tests.py
```

### With `--docker` (additional files)

```
myproject/
├── Dockerfile              # python:3.12-slim-bookworm, no-cache pip install
├── docker-compose.yml      # web service (+ db service for PostgreSQL)
├── .dockerignore
└── entrypoint.sh           # Waits for DB (PostgreSQL) and runs migrations automatically
```

---

## 🤔 What's Included?

### Settings Highlights

- `SECRET_KEY` loaded from `.env`
- `DEBUG` and `ALLOWED_HOSTS` from environment
- Pre-configured password validators
- Static & media file configuration
- Production security settings (commented, ready to uncomment)
- Login/logout redirect URLs

### MVP Extras

- Django HTML templates with `{% block %}` structure
- Clean starter CSS with responsive grid
- ModelForm with widget customization

### API Extras

- Django REST Framework with pagination
- `django-cors-headers` configured
- `django-filter` included in requirements
- DRF browsable API at `/api/`

---

## 📄 License

MIT © 2026

---

## 🤝 Contributing

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit: `git commit -m 'Add my feature'`
4. Push: `git push origin feature/my-feature`
5. Open a Pull Request

---

## 🌟 Star this project

If Django Kickstart saved you time, give it a ⭐ on GitHub!
