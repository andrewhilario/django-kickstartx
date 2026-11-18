"""Project generator — renders Jinja2 templates into a Django project tree."""

import keyword
import os
import re
import secrets
from pathlib import Path

from jinja2 import Environment, FileSystemLoader


TEMPLATES_DIR = Path(__file__).parent / "templates"

# Characters safe for unquoted .env files (python-decouple) and Docker Compose env_file
SECRET_KEY_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@^&*(-_=+)"

RESERVED_NAMES = {
    "django",
    "test",
    "tests",
    "site",
    "sys",
    "os",
    "rest_framework",
    "corsheaders",
    "decouple",
    "django_filters",
}


def validate_identifier(name: str, label: str = "Project name") -> None:
    """Validate that a project or app name is a safe, non-reserved Python identifier."""
    if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", name):
        raise ValueError(
            f"Invalid {label.lower()} '{name}'. "
            "Use only letters, numbers, and underscores, and do not start with a number."
        )
    if keyword.iskeyword(name):
        raise ValueError(
            f"Invalid {label.lower()} '{name}'. "
            f"'{name}' is a reserved Python keyword."
        )
    if name.lower() in RESERVED_NAMES:
        raise ValueError(
            f"Invalid {label.lower()} '{name}'. "
            f"'{name}' conflicts with a standard library or Django package name."
        )


class ProjectGenerator:
    """Generates a Django project from Jinja2 templates."""

    def __init__(
        self,
        project_name: str,
        project_type: str = "mvp",
        view_style: str = "fbv",
        database: str = "sqlite",
        app_name: str = "core",
        with_docker: bool = False,
        base_dir: Path | None = None,
    ):
        validate_identifier(project_name, "Project name")
        validate_identifier(app_name, "App name")

        if project_name == app_name:
            raise ValueError(
                f"Project name and app name cannot both be '{project_name}'. "
                "Choose a different project name or pass a different --app name."
            )

        self.project_name = project_name
        self.project_type = project_type
        self.view_style = view_style
        self.database = database
        self.app_name = app_name
        self.with_docker = with_docker
        root_dir = Path(base_dir).resolve() if base_dir is not None else Path(os.getcwd()).resolve()
        self.output_dir = (root_dir / project_name).resolve()

        self.env = Environment(
            loader=FileSystemLoader(str(TEMPLATES_DIR)),
            keep_trailing_newline=True,
        )

        # Generate a cryptographically secure SECRET_KEY safe for .env and Docker Compose
        secret_key = "".join(secrets.choice(SECRET_KEY_CHARS) for _ in range(50))

        self.context = {
            "project_name": project_name,
            "app_name": app_name,
            "project_type": project_type,
            "view_style": view_style,
            "database": database,
            "secret_key": secret_key,
            "is_api": project_type == "api",
            "is_mvp": project_type == "mvp",
            "is_cbv": view_style == "cbv",
            "is_fbv": view_style == "fbv",
            "is_postgresql": database == "postgresql",
            "is_sqlite": database == "sqlite",
            "is_docker": with_docker,
        }

    def generate(self):
        """Generate the full project structure."""
        # Prevent accidentally overwriting an existing project
        if self.output_dir.exists():
            raise FileExistsError(
                f"Directory '{self.output_dir}' already exists. "
                "Remove it first or choose a different project name."
            )

        self._create_root_files()
        self._create_project_config()
        self._create_app()
        if self.with_docker:
            self._create_docker_files()

        if self.project_type == "mvp":
            self._create_templates()
            self._create_static_files()

    def _render(self, template_name: str) -> str:
        """Render a Jinja2 template with context."""
        template = self.env.get_template(template_name)
        return template.render(**self.context)

    def _write(self, relative_path: str, content: str, executable: bool = False):
        """Write content to a file using LF line endings, creating directories as needed."""
        full_path = (self.output_dir / relative_path).resolve()

        # Prevent path traversal — all files must reside inside output_dir
        try:
            full_path.relative_to(self.output_dir)
        except ValueError as exc:
            raise ValueError(
                f"Path traversal detected: '{relative_path}' escapes the project directory."
            ) from exc

        full_path.parent.mkdir(parents=True, exist_ok=True)
        with open(full_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(content)

        if executable:
            try:
                full_path.chmod(0o755)
            except OSError:
                pass

    def _create_root_files(self):
        """Create root-level project files."""
        self._write("manage.py", self._render("manage.py.j2"), executable=True)
        self._write("requirements.txt", self._render("requirements.txt.j2"))
        self._write(".env.example", self._render(".env.example.j2"))
        self._write(".gitignore", self._render(".gitignore.j2"))

    def _create_project_config(self):
        """Create the Django project config package."""
        config_dir = self.project_name

        self._write(f"{config_dir}/__init__.py", "")
        self._write(f"{config_dir}/settings.py", self._render("project/settings.py.j2"))
        self._write(f"{config_dir}/urls.py", self._render("project/urls.py.j2"))
        self._write(f"{config_dir}/wsgi.py", self._render("project/wsgi.py.j2"))
        self._write(f"{config_dir}/asgi.py", self._render("project/asgi.py.j2"))

    def _create_app(self):
        """Create the Django app including initial migrations."""
        app = self.app_name

        self._write(f"{app}/__init__.py", "")
        self._write(f"{app}/admin.py", self._render("app/admin.py.j2"))
        self._write(f"{app}/apps.py", self._render("app/apps.py.j2"))
        self._write(f"{app}/models.py", self._render("app/models.py.j2"))
        self._write(f"{app}/tests.py", self._render("app/tests.py.j2"))
        self._write(f"{app}/migrations/__init__.py", "")
        self._write(
            f"{app}/migrations/0001_initial.py",
            self._render("app/migrations/0001_initial.py.j2"),
        )

        # Views — branch by project type + view style
        if self.project_type == "api":
            if self.view_style == "cbv":
                self._write(f"{app}/views.py", self._render("app/views_api_cbv.py.j2"))
            else:
                self._write(f"{app}/views.py", self._render("app/views_api_fbv.py.j2"))
            self._write(f"{app}/serializers.py", self._render("app/serializers.py.j2"))
            self._write(f"{app}/urls.py", self._render("app/urls_api.py.j2"))
        else:
            if self.view_style == "cbv":
                self._write(f"{app}/views.py", self._render("app/views_cbv.py.j2"))
            else:
                self._write(f"{app}/views.py", self._render("app/views_fbv.py.j2"))
            self._write(f"{app}/urls.py", self._render("app/urls_mvp.py.j2"))
            self._write(f"{app}/forms.py", self._render("app/forms.py.j2"))

    def _create_templates(self):
        """Create Django HTML templates (MVP only)."""
        app = self.app_name
        tpl_dir = f"{app}/templates/{app}"

        self._write(f"{tpl_dir}/base.html", self._render("html/base.html.j2"))
        self._write(f"{tpl_dir}/home.html", self._render("html/home.html.j2"))
        self._write(f"{tpl_dir}/about.html", self._render("html/about.html.j2"))

    def _create_static_files(self):
        """Create static CSS and design token files (MVP only)."""
        self._write("static/css/tokens.css", self._render("static/tokens.css.j2"))
        self._write("static/css/style.css", self._render("static/style.css.j2"))

    def _create_docker_files(self):
        """Create Docker configuration files."""
        self._write("Dockerfile", self._render("Dockerfile.j2"))
        self._write("docker-compose.yml", self._render("docker-compose.yml.j2"))
        self._write(".dockerignore", self._render(".dockerignore.j2"))
        self._write("entrypoint.sh", self._render("entrypoint.sh.j2"), executable=True)


