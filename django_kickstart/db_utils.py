"""Utilities for PostgreSQL database provisioning during project creation."""

from __future__ import annotations

import os
import shutil
import subprocess
from typing import Optional


def _find_psql() -> Optional[str]:
    """Return the path to the psql executable, or None if not found."""
    return shutil.which("psql")


def _get_os_env() -> dict:
    """Return a copy of the current OS environment."""
    return dict(os.environ)


def create_postgres_database(
    db_name: str,
    db_user: str = "postgres",
    db_password: str = "postgres",
    db_host: str = "localhost",
    db_port: str = "5432",
) -> tuple[bool, str]:
    """Attempt to create a PostgreSQL database if psql is available.

    Returns a (success, message) tuple.
    """
    psql = _find_psql()
    if psql is None:
        return False, "psql not found on PATH"

    env = {**_get_os_env(), "PGPASSWORD": db_password}

    check_cmd = [
        psql,
        "-h",
        db_host,
        "-p",
        db_port,
        "-U",
        db_user,
        "-tAc",
        f"SELECT 1 FROM pg_database WHERE datname='{db_name}'",
        "postgres",
    ]

    try:
        result = subprocess.run(
            check_cmd,
            capture_output=True,
            text=True,
            timeout=10,
            env=env,
        )
        if result.returncode != 0:
            return False, f"Could not connect to PostgreSQL: {result.stderr.strip()}"

        if result.stdout.strip() == "1":
            return True, f"Database '{db_name}' already exists"

        create_cmd = [
            psql,
            "-h",
            db_host,
            "-p",
            db_port,
            "-U",
            db_user,
            "-c",
            f'CREATE DATABASE "{db_name}";',
            "postgres",
        ]
        create_result = subprocess.run(
            create_cmd,
            capture_output=True,
            text=True,
            timeout=10,
            env=env,
        )
        if create_result.returncode == 0:
            return True, f"Database '{db_name}' created successfully"
        return False, create_result.stderr.strip()

    except subprocess.TimeoutExpired:
        return False, "Connection timed out"
    except Exception as exc:
        return False, str(exc)
