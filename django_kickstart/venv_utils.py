"""Utilities for creating virtual environments and installing dependencies."""

import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

import click
from colorama import Fore, Style


def _get_venv_pip(venv_dir: Path) -> Path:
    """Return the path to pip inside the virtual environment (cross-platform)."""
    if os.name == "nt":
        return venv_dir / "Scripts" / "pip.exe"
    return venv_dir / "bin" / "pip"


def _get_venv_python(venv_dir: Path) -> Path:
    """Return the path to python inside the virtual environment (cross-platform)."""
    if os.name == "nt":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def _get_activate_hint(venv_dir_name: str = "venv") -> str:
    """Return an OS-appropriate activation command hint."""
    if os.name == "nt":
        return f"{venv_dir_name}\\Scripts\\activate"
    return f"source {venv_dir_name}/bin/activate"


def create_virtualenv(
    project_dir: Path,
    python_executable: Optional[str] = None,
) -> bool:
    """Create a virtual environment and install requirements.txt.

    Args:
        project_dir: Absolute path to the generated project directory.
        python_executable: Python interpreter to use. Defaults to the
            currently running interpreter (``sys.executable``).

    Returns:
        ``True`` if the venv was created **and** dependencies installed
        successfully, ``False`` otherwise.
    """
    python_exe = python_executable or sys.executable
    venv_dir = project_dir / "venv"
    requirements_file = project_dir / "requirements.txt"

    # --- Step 1: Create the virtual environment -------------------------
    click.echo(
        f"\n{Fore.CYAN}🐍 Creating virtual environment...{Style.RESET_ALL}"
    )

    try:
        subprocess.run(
            [python_exe, "-m", "venv", str(venv_dir)],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        click.echo(
            f"{Fore.RED}✖ Failed to create virtual environment:{Style.RESET_ALL}"
        )
        if exc.stderr:
            click.echo(f"  {exc.stderr.strip()}")
        click.echo(
            f"{Fore.YELLOW}  ⤷ Your project files are fine — "
            f"create a venv manually with: python -m venv venv{Style.RESET_ALL}"
        )
        return False
    except FileNotFoundError:
        click.echo(
            f"{Fore.RED}✖ Python executable not found: {python_exe}{Style.RESET_ALL}"
        )
        return False

    click.echo(f"  {Fore.GREEN}✔ Virtual environment created{Style.RESET_ALL}")

    # --- Step 2: Install requirements -----------------------------------
    pip_path = _get_venv_pip(venv_dir)
    if not pip_path.exists():
        click.echo(
            f"{Fore.RED}✖ pip not found in venv at {pip_path}{Style.RESET_ALL}"
        )
        return False

    if not requirements_file.exists():
        click.echo(
            f"{Fore.YELLOW}⚠ requirements.txt not found — "
            f"skipping dependency install.{Style.RESET_ALL}"
        )
        return True  # venv itself was created successfully

    click.echo(
        f"{Fore.CYAN}📦 Installing dependencies (this may take a moment)...{Style.RESET_ALL}"
    )

    try:
        subprocess.run(
            [str(pip_path), "install", "-r", str(requirements_file)],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        click.echo(
            f"{Fore.RED}✖ Failed to install dependencies:{Style.RESET_ALL}"
        )
        if exc.stderr:
            for line in exc.stderr.strip().splitlines()[-5:]:
                click.echo(f"  {line}")
        click.echo(
            f"{Fore.YELLOW}  ⤷ You can retry manually:\n"
            f"     {_get_activate_hint()}\n"
            f"     pip install -r requirements.txt{Style.RESET_ALL}"
        )
        return False

    click.echo(
        f"  {Fore.GREEN}✔ Dependencies installed successfully{Style.RESET_ALL}"
    )
    return True
