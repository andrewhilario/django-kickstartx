"""Project generator — renders Jinja2 templates into a Django project tree."""

import os
import re
import secrets
import string
from pathlib import Path

from jinja2 import Environment, FileSystemLoader


TEMPLATES_DIR = Path(__file__).parent / "templates"


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
    ):
        # Validate project name against path traversal
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', project_name):
            raise ValueError(
                f"Invalid project name '{project_name}'. "
                "Use only letters, numbers, and underscores."
            )

        self.project_name = project_name
        self.project_type = project_type
        self.view_style = view_style
        self.database = database
        self.app_name = app_name
        self.with_docker = with_docker
        self.output_dir = Path(os.getcwd()).resolve() / project_name

        self.env = Environment(
            loader=FileSystemLoader(str(TEMPLATES_DIR)),
            keep_trailing_newline=True,
        )

        # Generate a cryptographically secure SECRET_KEY
        alphabet = string.ascii_letters + string.digits + string.punctuation
        secret_key = ''.join(secrets.choice(alphabet) for _ in range(50))

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

    def _write(self, relative_path: str, content: str):
        """Write content to a file, creating directories as needed."""
        full_path = (self.output_dir / relative_path).resolve()

        # Prevent path traversal — all files must be within output_dir
        if not str(full_path).startswith(str(self.output_dir)):
            raise ValueError(
                f"Path traversal detected: '{relative_path}' escapes the project directory."
            )

        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content, encoding="utf-8")

    def _create_root_files(self):
        """Create root-level project files."""
        self._write("manage.py", self._render("manage.py.j2"))
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
        """Create the Django app."""
        app = self.app_name

        self._write(f"{app}/__init__.py", "")
        self._write(f"{app}/admin.py", self._render("app/admin.py.j2"))
        self._write(f"{app}/apps.py", self._render("app/apps.py.j2"))
        self._write(f"{app}/models.py", self._render("app/models.py.j2"))
        self._write(f"{app}/tests.py", self._render("app/tests.py.j2"))

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
        """Create static CSS file (MVP only)."""
        self._write("static/css/style.css", self._render("static/style.css.j2"))

    def _create_docker_files(self):
        """Create Docker configuration files."""
        self._write("Dockerfile", self._render("Dockerfile.j2"))
        self._write("docker-compose.yml", self._render("docker-compose.yml.j2"))
        self._write(".dockerignore", self._render(".dockerignore.j2"))
        if self.database == "postgresql":
            self._write("entrypoint.sh", self._render("entrypoint.sh.j2"))
            # entrypoint.sh needs to be executable on Linux/Mac,
            # but on Windows we can just write the file.
            # Users on Linux/Mac will need to `chmod +x entrypoint.sh`
            # or the Dockerfile handles it (which we added).

