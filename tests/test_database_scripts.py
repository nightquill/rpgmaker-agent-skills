"""Tests for database helper scripts: balance_check.py, add_skill.py, add_enemy.py, validate_database.py.

All scripts are invoked via subprocess with PYTHONPATH set to the repo root.
Tests use the example-mv-project fixture for clean-state tests, the
broken/unbalanced fixture for outlier detection tests, and the
broken/malformed-db fixture for schema validation failure tests.
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
UNBALANCED_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "fixtures", "broken", "unbalanced")
)
MALFORMED_DB_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "fixtures", "broken", "malformed-db")
)
DATABASE_SCRIPTS = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "skills", "rpgmaker-database", "scripts")
)
SCHEMA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "schemas"))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def run_script(script_name: str, args: list, cwd=None) -> subprocess.CompletedProcess:
    """Run a database script via subprocess with PYTHONPATH set to the repo root."""
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    env = os.environ.copy()
    env["PYTHONPATH"] = repo_root
    cmd = [sys.executable, os.path.join(DATABASE_SCRIPTS, script_name)] + args
    return subprocess.run(cmd, capture_output=True, text=True, env=env, cwd=cwd or repo_root)


@pytest.fixture
def tmp_project(tmp_path):
    """Copy the example fixture to a temporary directory for write tests."""
    dest = tmp_path / "project"
    shutil.copytree(FIXTURE_DIR, dest)
    return str(dest)


# ---------------------------------------------------------------------------
# balance_check.py tests
# ---------------------------------------------------------------------------


def test_balance_check_clean_exits_0():
    result = run_script("balance_check.py", ["--project", FIXTURE_DIR, "--category", "all"])
    assert result.returncode == 0, (
        f"Expected exit 0 but got {result.returncode}. "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )


def test_balance_check_unbalanced_skills_exits_1():
    result = run_script("balance_check.py", ["--project", UNBALANCED_DIR, "--category", "skills"])
    assert result.returncode == 1, (
        f"Expected exit 1 but got {result.returncode}. stdout={result.stdout!r}"
    )
    assert "OUTLIER" in result.stdout, "Expected OUTLIER flag in output"


def test_balance_check_unbalanced_weapons_exits_1():
    result = run_script("balance_check.py", ["--project", UNBALANCED_DIR, "--category", "weapons"])
    assert result.returncode == 1, (
        f"Expected exit 1 but got {result.returncode}. stdout={result.stdout!r}"
    )
    assert "OUTLIER" in result.stdout, "Expected OUTLIER flag in output"


def test_balance_check_unbalanced_enemies_exits_1():
    result = run_script("balance_check.py", ["--project", UNBALANCED_DIR, "--category", "enemies"])
    assert result.returncode == 1, (
        f"Expected exit 1 but got {result.returncode}. stdout={result.stdout!r}"
    )
    assert "OUTLIER" in result.stdout, "Expected OUTLIER flag in output"


def test_balance_check_output_has_table():
    result = run_script("balance_check.py", ["--project", FIXTURE_DIR])
    assert result.returncode == 0
    assert "|" in result.stdout, "Expected markdown table in output"


# ---------------------------------------------------------------------------
# add_skill.py tests
# ---------------------------------------------------------------------------


def test_add_skill_dry_run_does_not_modify(tmp_project):
    skills_path = os.path.join(tmp_project, "data", "Skills.json")
    with open(skills_path) as f:
        before = f.read()

    result = run_script("add_skill.py", [
        "--project", tmp_project, "--name", "TestSkill",
        "--formula", "a.atk * 3", "--mp-cost", "5",
    ])
    assert result.returncode == 0, f"stderr={result.stderr!r}"

    with open(skills_path) as f:
        after = f.read()
    assert before == after, "Dry-run should not modify the file"


def test_add_skill_apply_appends_entry(tmp_project):
    result = run_script("add_skill.py", [
        "--project", tmp_project, "--name", "NewSpell",
        "--formula", "a.mat * 6", "--mp-cost", "12", "--apply",
    ])
    assert result.returncode == 0, f"stderr={result.stderr!r}"

    skills_path = os.path.join(tmp_project, "data", "Skills.json")
    with open(skills_path) as f:
        data = json.load(f)

    assert data[0] is None, "Index 0 must be null"
    last = data[-1]
    assert last["name"] == "NewSpell"
    assert last["id"] == len(data) - 1, f"Expected id={len(data)-1}, got {last['id']}"

    bak_path = skills_path + ".bak"
    assert os.path.exists(bak_path), "Backup file should exist after --apply"


def test_add_skill_note_preserved_verbatim(tmp_project):
    note_content = "<SType:Magic>\\n<Cost:MP 10>"
    result = run_script("add_skill.py", [
        "--project", tmp_project, "--name", "NoteSkill",
        "--note", note_content, "--apply",
    ])
    assert result.returncode == 0, f"stderr={result.stderr!r}"

    skills_path = os.path.join(tmp_project, "data", "Skills.json")
    with open(skills_path) as f:
        data = json.load(f)

    last = data[-1]
    assert last["note"] == note_content, (
        f"Note field not preserved verbatim. Expected {note_content!r}, got {last['note']!r}"
    )


def test_add_skill_existing_ids_unchanged(tmp_project):
    skills_path = os.path.join(tmp_project, "data", "Skills.json")
    with open(skills_path) as f:
        original = json.load(f)
    original_ids = [e["id"] if e else None for e in original]

    result = run_script("add_skill.py", [
        "--project", tmp_project, "--name", "ExtraSkill", "--apply",
    ])
    assert result.returncode == 0

    with open(skills_path) as f:
        modified = json.load(f)

    for i, orig_id in enumerate(original_ids):
        if orig_id is not None:
            assert modified[i]["id"] == orig_id, (
                f"Entry at index {i} had id changed from {orig_id} to {modified[i]['id']}"
            )


# ---------------------------------------------------------------------------
# add_enemy.py tests
# ---------------------------------------------------------------------------


def test_add_enemy_dry_run_does_not_modify(tmp_project):
    enemies_path = os.path.join(tmp_project, "data", "Enemies.json")
    with open(enemies_path) as f:
        before = f.read()

    result = run_script("add_enemy.py", [
        "--project", tmp_project, "--name", "TestEnemy", "--hp", "200",
    ])
    assert result.returncode == 0, f"stderr={result.stderr!r}"

    with open(enemies_path) as f:
        after = f.read()
    assert before == after, "Dry-run should not modify the file"


def test_add_enemy_apply_appends_entry(tmp_project):
    result = run_script("add_enemy.py", [
        "--project", tmp_project, "--name", "Dragon",
        "--hp", "500", "--atk", "30", "--exp", "50", "--apply",
    ])
    assert result.returncode == 0, f"stderr={result.stderr!r}"

    enemies_path = os.path.join(tmp_project, "data", "Enemies.json")
    with open(enemies_path) as f:
        data = json.load(f)

    assert data[0] is None, "Index 0 must be null"
    last = data[-1]
    assert last["name"] == "Dragon"
    assert last["id"] == len(data) - 1
    assert last["params"][0] == 500, "HP should be 500"
    assert last["params"][2] == 30, "ATK should be 30"

    bak_path = enemies_path + ".bak"
    assert os.path.exists(bak_path), "Backup file should exist after --apply"


def test_add_enemy_note_preserved_verbatim(tmp_project):
    note_content = "<Drop:Potion 1/4>\\n<Level:5>"
    result = run_script("add_enemy.py", [
        "--project", tmp_project, "--name", "NoteEnemy",
        "--note", note_content, "--apply",
    ])
    assert result.returncode == 0, f"stderr={result.stderr!r}"

    enemies_path = os.path.join(tmp_project, "data", "Enemies.json")
    with open(enemies_path) as f:
        data = json.load(f)

    last = data[-1]
    assert last["note"] == note_content, (
        f"Note field not preserved verbatim. Expected {note_content!r}, got {last['note']!r}"
    )


# ---------------------------------------------------------------------------
# validate_database.py tests
# ---------------------------------------------------------------------------


def test_validate_database_clean_exits_0():
    result = run_script("validate_database.py", [
        "--project", FIXTURE_DIR, "--schema-dir", SCHEMA_DIR,
    ])
    assert result.returncode == 0, (
        f"Expected exit 0 but got {result.returncode}. "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    assert "PASS" in result.stdout


def test_validate_database_output_lists_files():
    result = run_script("validate_database.py", [
        "--project", FIXTURE_DIR, "--schema-dir", SCHEMA_DIR,
    ])
    assert result.returncode == 0
    for name in ["Actors.json", "Skills.json", "Enemies.json"]:
        assert name in result.stdout, f"Expected {name} in output"


def test_validate_database_malformed_exits_1():
    result = run_script("validate_database.py", [
        "--project", MALFORMED_DB_DIR, "--schema-dir", SCHEMA_DIR,
    ])
    assert result.returncode == 1, (
        f"Expected exit 1 but got {result.returncode}. stdout={result.stdout!r}"
    )
    assert "FAIL" in result.stdout, "Expected FAIL in output"
    assert "Skills.json" in result.stdout, "Expected Skills.json identified as broken"
