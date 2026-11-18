"""Unit tests for ProjectGenerator and template rendering."""

import itertools
import tempfile
import unittest
from pathlib import Path

from django_kickstart.generator import ProjectGenerator, SECRET_KEY_CHARS, validate_identifier


class TestValidateIdentifier(unittest.TestCase):
    """Tests for identifier and reserved name validation."""

    def test_valid_identifiers(self):
        for name in ("myproject", "my_project_2", "app1", "custom_core"):
            validate_identifier(name)

    def test_invalid_syntax_rejected(self):
        for bad in ("123project", "my-project", "my project", "../escape", ""):
            with self.assertRaises(ValueError):
                validate_identifier(bad)

    def test_python_keywords_rejected(self):
        for kw in ("class", "def", "import", "async", "await", "return"):
            with self.assertRaises(ValueError):
                validate_identifier(kw)

    def test_reserved_module_names_rejected(self):
        for reserved in ("django", "test", "tests", "site", "rest_framework"):
            with self.assertRaises(ValueError):
                validate_identifier(reserved)

    def test_project_and_app_name_collision_rejected(self):
        with self.assertRaises(ValueError):
            ProjectGenerator(project_name="core", app_name="core")


class TestProjectGenerator(unittest.TestCase):
    """Tests for project generation across all option combinations."""

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.base_path = Path(self.tmp_dir.name)

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_all_permutations_generate_valid_python(self):
        project_types = ["mvp", "api"]
        view_styles = ["fbv", "cbv"]
        databases = ["sqlite", "postgresql"]
        docker_flags = [False, True]

        for idx, (p_type, v_style, db, docker) in enumerate(
            itertools.product(project_types, view_styles, databases, docker_flags)
        ):
            project_name = f"proj_{idx}_{p_type}_{v_style}_{db}"
            gen = ProjectGenerator(
                project_name=project_name,
                project_type=p_type,
                view_style=v_style,
                database=db,
                with_docker=docker,
                base_dir=self.base_path,
            )
            gen.generate()
            project_dir = self.base_path / project_name

            self.assertTrue((project_dir / "manage.py").is_file())
            self.assertTrue((project_dir / "requirements.txt").is_file())
            self.assertTrue((project_dir / ".env.example").is_file())
            self.assertTrue((project_dir / ".gitignore").is_file())
            self.assertTrue((project_dir / "core" / "migrations" / "__init__.py").is_file())
            self.assertTrue((project_dir / "core" / "migrations" / "0001_initial.py").is_file())

            # Every generated Python file must compile without syntax errors
            py_files = list(project_dir.rglob("*.py"))
            self.assertGreaterEqual(len(py_files), 10)
            for py_file in py_files:
                source = py_file.read_text(encoding="utf-8")
                compile(source, str(py_file), "exec")

            # Verify MVP static and template files
            if p_type == "mvp":
                tokens_css = project_dir / "static" / "css" / "tokens.css"
                style_css = project_dir / "static" / "css" / "style.css"
                self.assertTrue(tokens_css.is_file())
                self.assertTrue(style_css.is_file())
                style_text = style_css.read_text(encoding="utf-8")
                self.assertIn("/* Hallmark ·", style_text)
                self.assertNotIn("#", style_text)

            # Verify Docker files when enabled
            if docker:
                self.assertTrue((project_dir / "Dockerfile").is_file())
                self.assertTrue((project_dir / "docker-compose.yml").is_file())
                self.assertTrue((project_dir / ".dockerignore").is_file())
                entrypoint = project_dir / "entrypoint.sh"
                self.assertTrue(entrypoint.is_file())
                # Ensure LF line endings on entrypoint.sh even on Windows
                raw_bytes = entrypoint.read_bytes()
                self.assertNotIn(b"\r\n", raw_bytes)

    def test_secret_key_is_env_and_docker_safe(self):
        gen = ProjectGenerator(project_name="safe_secret_proj", base_dir=self.base_path)
        secret_key = gen.context["secret_key"]
        self.assertEqual(len(secret_key), 50)
        for ch in secret_key:
            self.assertIn(ch, SECRET_KEY_CHARS)
            self.assertNotIn(ch, {"#", "$", "'", '"', "\\", " "})

    def test_api_includes_django_filters_and_patch(self):
        gen = ProjectGenerator(
            project_name="api_proj",
            project_type="api",
            view_style="fbv",
            database="postgresql",
            with_docker=True,
            base_dir=self.base_path,
        )
        gen.generate()
        project_dir = self.base_path / "api_proj"

        settings_content = (project_dir / "api_proj" / "settings.py").read_text(encoding="utf-8")
        self.assertIn('"django_filters"', settings_content)
        self.assertIn("DjangoFilterBackend", settings_content)
        self.assertNotIn("SECURE_BROWSER_XSS_FILTER", settings_content)

        views_content = (project_dir / "core" / "views.py").read_text(encoding="utf-8")
        self.assertIn('"PATCH"', views_content)
        self.assertIn("partial=", views_content)

        compose_content = (project_dir / "docker-compose.yml").read_text(encoding="utf-8")
        self.assertIn("POSTGRES_USER=${DB_USER:-postgres}", compose_content)
        self.assertIn("POSTGRES_PASSWORD=${DB_PASSWORD:-postgres}", compose_content)

        dockerfile_content = (project_dir / "Dockerfile").read_text(encoding="utf-8")
        self.assertIn("/usr/local/bin/entrypoint.sh", dockerfile_content)

    def test_custom_app_name_pascal_case_config(self):
        gen = ProjectGenerator(
            project_name="my_saas",
            app_name="billing_engine",
            base_dir=self.base_path,
        )
        gen.generate()
        apps_py = (self.base_path / "my_saas" / "billing_engine" / "apps.py").read_text(
            encoding="utf-8"
        )
        self.assertIn("class BillingEngineConfig(AppConfig):", apps_py)

    def test_existing_directory_raises_file_exists_error(self):
        gen = ProjectGenerator(project_name="dup_proj", base_dir=self.base_path)
        gen.generate()
        with self.assertRaises(FileExistsError):
            gen.generate()


if __name__ == "__main__":
    unittest.main()
