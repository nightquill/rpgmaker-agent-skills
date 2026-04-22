"""Tests for Phase 5 consistency scripts: validate_project.py, check_orphaned_refs.py, check_switch_collisions.py.

All scripts are invoked via subprocess with PYTHONPATH set to the repo root so they
run in the same environment as normal CLI use. Tests use the example-mv-project fixture
for clean-state tests and broken fixture subdirectories for error-detection tests.
"""

import json
import os
import shutil
import subprocess
import sys

import pytest

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

FIXTURE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "fixtures", "example-mv-project")
)
SCRIPTS_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "scripts")
)
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ORPHANED_REFS_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "fixtures", "broken", "orphaned-refs")
)
SWITCH_COLLISIONS_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "fixtures", "broken", "switch-collisions")
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def run_script(script_name: str, args: list, cwd=None) -> subprocess.CompletedProcess:
    """Run a script from SCRIPTS_DIR via subprocess with PYTHONPATH set to repo root.

    Args:
        script_name: Filename of the script (e.g. 'check_orphaned_refs.py').
        args: List of CLI argument strings to pass to the script.
        cwd: Working directory for the subprocess (defaults to repo root).

    Returns:
        CompletedProcess instance with returncode, stdout, and stderr attributes.
    """
    env = os.environ.copy()
    env["PYTHONPATH"] = REPO_ROOT
    cmd = [sys.executable, os.path.join(SCRIPTS_DIR, script_name)] + args
    return subprocess.run(cmd, capture_output=True, text=True, env=env, cwd=cwd or REPO_ROOT)


# ---------------------------------------------------------------------------
# Tests: check_orphaned_refs.py
# ---------------------------------------------------------------------------


def test_check_orphaned_refs_clean_exits_0():
    """check_orphaned_refs.py must exit 0 on the clean example-mv-project fixture."""
    result = run_script("check_orphaned_refs.py", ["--project", FIXTURE_DIR])
    assert result.returncode == 0, (
        f"Expected exit 0 on clean fixture but got {result.returncode}.\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )


def test_check_orphaned_refs_broken_exits_1():
    """check_orphaned_refs.py must exit 1 and print ERROR lines on the orphaned-refs broken fixture."""
    result = run_script("check_orphaned_refs.py", ["--project", ORPHANED_REFS_DIR])
    assert result.returncode == 1, (
        f"Expected exit 1 on broken fixture but got {result.returncode}.\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    assert "ERROR:" in result.stdout, (
        f"Expected 'ERROR:' in stdout but got:\n{result.stdout}"
    )
    # Broken fixture has Corrupted Slime with skillId 99 and item ref 99
    assert "99" in result.stdout, (
        f"Expected orphaned ID '99' in stdout but got:\n{result.stdout}"
    )


def test_check_orphaned_refs_missing_project_exits_1():
    """check_orphaned_refs.py must exit 1 when the project path does not exist."""
    result = run_script("check_orphaned_refs.py", ["--project", "/nonexistent/path"])
    assert result.returncode == 1, (
        f"Expected exit 1 for nonexistent project but got {result.returncode}"
    )


# ---------------------------------------------------------------------------
# Tests: check_switch_collisions.py
# ---------------------------------------------------------------------------


def test_check_switch_collisions_clean_exits_0():
    """check_switch_collisions.py must exit 0 on the clean example-mv-project fixture."""
    result = run_script("check_switch_collisions.py", ["--project", FIXTURE_DIR])
    assert result.returncode == 0, (
        f"Expected exit 0 on clean fixture but got {result.returncode}.\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )


def test_check_switch_collisions_detects_collision():
    """check_switch_collisions.py must exit 0 and print WARNING lines on the switch-collisions broken fixture."""
    result = run_script("check_switch_collisions.py", ["--project", SWITCH_COLLISIONS_DIR])
    assert result.returncode == 0, (
        f"Expected exit 0 (warnings only) but got {result.returncode}.\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    assert "WARNING:" in result.stdout, (
        f"Expected 'WARNING:' in stdout for collision fixture but got:\n{result.stdout}"
    )
    # Both Map001 and Map002 set switch 5 — at least one should appear in output
    assert "Map001" in result.stdout or "Map002" in result.stdout, (
        f"Expected 'Map001' or 'Map002' in stdout but got:\n{result.stdout}"
    )


def test_check_switch_collisions_missing_project_exits_1():
    """check_switch_collisions.py must exit 1 when the project path does not exist."""
    result = run_script("check_switch_collisions.py", ["--project", "/nonexistent/path"])
    assert result.returncode == 1, (
        f"Expected exit 1 for nonexistent project but got {result.returncode}"
    )


# ---------------------------------------------------------------------------
# Tests: validate_project.py
# ---------------------------------------------------------------------------


def test_validate_project_clean_exits_0():
    """validate_project.py must exit 0 and include a report header on the clean fixture."""
    result = run_script("validate_project.py", ["--project", FIXTURE_DIR])
    assert result.returncode == 0, (
        f"Expected exit 0 on clean fixture but got {result.returncode}.\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    assert "Project Validation Report" in result.stdout, (
        f"Expected '# Project Validation Report' in stdout but got:\n{result.stdout}"
    )


def test_validate_project_errors_exits_1():
    """validate_project.py must exit 1 when run against the orphaned-refs broken fixture."""
    result = run_script("validate_project.py", ["--project", ORPHANED_REFS_DIR])
    assert result.returncode == 1, (
        f"Expected exit 1 on broken fixture but got {result.returncode}.\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    # Output must contain either ERROR lines or the Orphaned Reference Check section header
    has_signal = (
        "ERROR:" in result.stdout
        or "Orphaned Reference Check" in result.stdout
    )
    assert has_signal, (
        f"Expected 'ERROR:' or 'Orphaned Reference Check' in stdout but got:\n{result.stdout}"
    )


def test_validate_project_missing_project_exits_1():
    """validate_project.py must exit 1 when the project path does not exist."""
    result = run_script("validate_project.py", ["--project", "/nonexistent/path"])
    assert result.returncode == 1, (
        f"Expected exit 1 for nonexistent project but got {result.returncode}"
    )


# ---------------------------------------------------------------------------
# Parametrized: all three checkers on clean fixture must exit 0
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("script_name", [
    "validate_project.py",
    "check_orphaned_refs.py",
    "check_switch_collisions.py",
])
def test_all_checkers_clean_on_example_project(script_name):
    """All three checker scripts must exit 0 on the clean example-mv-project fixture."""
    result = run_script(script_name, ["--project", FIXTURE_DIR])
    assert result.returncode == 0, (
        f"{script_name} failed on clean fixture.\n"
        f"stderr: {result.stderr}\nstdout: {result.stdout}"
    )


# ---------------------------------------------------------------------------
# Parametrized: all three checkers respond to --help
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("script_name", [
    "validate_project.py",
    "check_orphaned_refs.py",
    "check_switch_collisions.py",
])
def test_all_checkers_have_help(script_name):
    """All three checker scripts must exit 0 and include '--project' in --help output."""
    result = run_script(script_name, ["--help"])
    assert result.returncode == 0, (
        f"{script_name} --help exited {result.returncode}.\n"
        f"stderr: {result.stderr}\nstdout: {result.stdout}"
    )
    assert "--project" in result.stdout, (
        f"Expected '--project' in {script_name} --help output but got:\n{result.stdout}"
    )
