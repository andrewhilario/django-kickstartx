"""CLI entry point for Django Kickstart."""

import click
from colorama import init, Fore, Style

from django_kickstart import __version__
from django_kickstart.generator import ProjectGenerator
from django_kickstart.venv_utils import create_virtualenv, _get_activate_hint

init(autoreset=True)


BANNER = f"""
{Fore.CYAN}{'━' * 50}
  🚀  Django Kickstart v{__version__}
  Scaffold production-ready Django projects in seconds
{'━' * 50}{Style.RESET_ALL}
"""

PROJECT_TYPES = {
    "mvp": "MVP — Traditional Django with HTML templates",
    "api": "API — Django REST Framework",
}

VIEW_STYLES = {
    "fbv": "Function-Based Views (FBV)",
    "cbv": "Class-Based Views (CBV)",
}

DATABASES = {
    "sqlite": "SQLite (great for development)",
    "postgresql": "PostgreSQL (recommended for production)",
}


def prompt_choice(label: str, choices: dict, default: str) -> str:
    """Display a numbered menu and return the selected key."""
    click.echo(f"\n{Fore.YELLOW}? {label}{Style.RESET_ALL}")
    keys = list(choices.keys())
    for i, (key, desc) in enumerate(choices.items(), 1):
        marker = f"{Fore.GREEN}❯{Style.RESET_ALL}" if key == default else " "
        click.echo(f"  {marker} {i}. {desc}")

    while True:
        raw = click.prompt(
            f"  Enter choice (1-{len(keys)})",
            default=str(keys.index(default) + 1),
            show_default=False,
        )
        try:
            idx = int(raw) - 1
            if 0 <= idx < len(keys):
                selected = keys[idx]
                click.echo(
                    f"  {Fore.GREEN}✔ {choices[selected]}{Style.RESET_ALL}")
                return selected
        except ValueError:
            pass
        click.echo(f"  {Fore.RED}Invalid choice. Try again.{Style.RESET_ALL}")


@click.group()
@click.version_option(version=__version__, prog_name="django-kickstart")
def main():
    """🚀 Django Kickstart — Scaffold production-ready Django projects."""
    pass


@main.command()
@click.argument("project_name")
@click.option(
    "--type",
    "project_type",
    type=click.Choice(["mvp", "api"], case_sensitive=False),
    default=None,
    help="Project type: mvp (templates) or api (DRF).",
)
@click.option(
    "--views",
    "view_style",
    type=click.Choice(["fbv", "cbv"], case_sensitive=False),
    default=None,
    help="View style: fbv (function-based) or cbv (class-based).",
)
@click.option(
    "--db",
    "database",
    type=click.Choice(["sqlite", "postgresql"], case_sensitive=False),
    default=None,
    help="Database: sqlite or postgresql.",
)
@click.option(
    "--no-venv",
    "no_venv",
    is_flag=True,
    default=False,
    help="Skip virtual environment creation.",
)
@click.option(
    "--docker",
    "with_docker",
    is_flag=True,
    default=False,
    help="Add Docker configuration.",
)
def create(project_name: str, project_type: str, view_style: str, database: str, no_venv: bool, with_docker: bool):
    """Create a new Django project scaffold.

    PROJECT_NAME is the name of the project to create.
    """
    click.echo(BANNER)

    # Validate project name
    if not project_name.isidentifier():
        click.echo(
            f"{Fore.RED}✖ '{project_name}' is not a valid Python identifier. "
            f"Use only letters, numbers, and underscores.{Style.RESET_ALL}"
        )
        raise SystemExit(1)

    # Interactive prompts for missing options
    if project_type is None:
        project_type = prompt_choice(
            "Select project type:", PROJECT_TYPES, "mvp")

    if view_style is None:
        view_style = prompt_choice("Select view style:", VIEW_STYLES, "fbv")

    if database is None:
        database = prompt_choice("Select database:", DATABASES, "sqlite")

    click.echo(
        f"\n{Fore.CYAN}📦 Creating project '{project_name}'...{Style.RESET_ALL}")
    click.echo(f"   Type:     {PROJECT_TYPES[project_type]}")
    click.echo(f"   Views:    {VIEW_STYLES[view_style]}")
    click.echo(f"   Database: {DATABASES[database]}")
    if with_docker:
        click.echo(f"   Docker:   {Fore.GREEN}Yes{Style.RESET_ALL}")
    click.echo()

    # Generate project
    generator = ProjectGenerator(
        project_name=project_name,
        project_type=project_type,
        view_style=view_style,
        database=database,
        with_docker=with_docker,
    )

    try:
        generator.generate()
    except FileExistsError as e:
        click.echo(f"{Fore.RED}✖ {e}{Style.RESET_ALL}")
        raise SystemExit(1)
    except ValueError as e:
        click.echo(f"{Fore.RED}✖ {e}{Style.RESET_ALL}")
        raise SystemExit(1)

    # Create virtual environment (unless opted out)
    venv_created = False
    if not no_venv:
        project_dir = generator.output_dir
        venv_created = create_virtualenv(project_dir)

    # Success message
    click.echo(f"\n{Fore.GREEN}{'━' * 50}")
    click.echo(f"  ✅ Project '{project_name}' created successfully!")
    click.echo(f"{'━' * 50}{Style.RESET_ALL}")
    click.echo(f"\n{Fore.YELLOW}Next steps:{Style.RESET_ALL}")
    click.echo(f"  cd {project_name}")

    if with_docker:
        click.echo("  cp .env.example .env")
        click.echo(f"  {Fore.CYAN}docker-compose up --build{Style.RESET_ALL}")
        click.echo(f"\n{Fore.YELLOW}Once running:{Style.RESET_ALL}")
        click.echo("  docker-compose exec web python manage.py createsuperuser")
    else:
        if venv_created:
            click.echo(f"  {_get_activate_hint()}")
        else:
            click.echo("  python -m venv venv")
            click.echo(f"  {_get_activate_hint()}")
            click.echo("  pip install -r requirements.txt")

        click.echo("  cp .env.example .env")
        click.echo("  python manage.py migrate")
        click.echo("  python manage.py createsuperuser")
        click.echo("  python manage.py runserver")

    if project_type == "api":
        click.echo(f"\n{Fore.CYAN}API endpoints:{Style.RESET_ALL}")
        click.echo("  http://127.0.0.1:8000/api/")
        click.echo("  http://127.0.0.1:8000/admin/")
    else:
        click.echo(f"\n{Fore.CYAN}Visit:{Style.RESET_ALL}")
        click.echo("  http://127.0.0.1:8000/")
        click.echo("  http://127.0.0.1:8000/admin/")

    click.echo()


if __name__ == "__main__":
    main()
