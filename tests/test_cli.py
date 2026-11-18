"""Unit tests for the CLI interface."""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

from django_kickstart.cli import main


class TestCLI(unittest.TestCase):
    """Tests for the django-kickstart CLI commands."""

    def setUp(self):
        self.runner = CliRunner()

    def test_cli_flag_mode_no_venv(self):
        with tempfile.TemporaryDirectory() as tmp:
            old_cwd = os.getcwd()
            try:
                os.chdir(tmp)
                result = self.runner.invoke(
                    main,
                    [
                        "create",
                        "demo_project",
                        "--type",
                        "api",
                        "--views",
                        "cbv",
                        "--db",
                        "sqlite",
                        "--no-venv",
                    ],
                )
                self.assertEqual(result.exit_code, 0, msg=result.output)
                self.assertTrue((Path(tmp) / "demo_project" / "manage.py").is_file())
            finally:
                os.chdir(old_cwd)

    def test_cli_interactive_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            old_cwd = os.getcwd()
            try:
                os.chdir(tmp)
                result = self.runner.invoke(
                    main,
                    ["create", "interactive_proj", "--no-venv"],
                    input="1\n2\n1\n",
                )
                self.assertEqual(result.exit_code, 0, msg=result.output)
                self.assertTrue((Path(tmp) / "interactive_proj" / "manage.py").is_file())
            finally:
                os.chdir(old_cwd)

    @patch("django_kickstart.cli.create_virtualenv")
    def test_docker_flag_skips_local_venv_creation(self, mock_venv):
        with tempfile.TemporaryDirectory() as tmp:
            old_cwd = os.getcwd()
            try:
                os.chdir(tmp)
                result = self.runner.invoke(
                    main,
                    [
                        "create",
                        "docker_proj",
                        "--type",
                        "mvp",
                        "--views",
                        "fbv",
                        "--db",
                        "postgresql",
                        "--docker",
                    ],
                )
                self.assertEqual(result.exit_code, 0, msg=result.output)
                mock_venv.assert_not_called()
                self.assertIn("docker compose up --build", result.output)
            finally:
                os.chdir(old_cwd)

    def test_cli_rejects_keyword_and_collision_names(self):
        for bad_args in (
            ["create", "class", "--no-venv"],
            ["create", "django", "--no-venv"],
            ["create", "core", "--no-venv"],
            ["create", "myapp", "--app", "myapp", "--no-venv"],
        ):
            result = self.runner.invoke(main, bad_args)
            self.assertNotEqual(result.exit_code, 0)


if __name__ == "__main__":
    unittest.main()
