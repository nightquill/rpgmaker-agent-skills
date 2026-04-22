"""Tests for dialog helper scripts: extract_npc_lines.py, inject_dialog.py, validate_dialog_refs.py.

All scripts are invoked via subprocess with PYTHONPATH set to the repo root so they
run in the same environment as normal CLI use. Tests use the example-mv-project fixture
for clean-state tests and the broken/bad-dialog-refs fixture for error-detection tests.
"""

import json
import os
import shutil
import subprocess
import sys

import jsonschema
import pytest

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

FIXTURE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "fixtures", "example-mv-project")
)
BROKEN_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "fixtures", "broken", "bad-dialog-refs")
)
GOLDEN_DIR = os.path.join(os.path.dirname(__file__), "golden")
DIALOG_SCRIPTS = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "skills", "rpgmaker-dialog", "scripts")
)
SCHEMA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "schemas"))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def run_script(script_name: str, args: list, cwd=None) -> subprocess.CompletedProcess:
    """Run a dialog script via subprocess with PYTHONPATH set to the repo root.

    Args:
        script_name: Filename of the script (e.g. 'extract_npc_lines.py').
        args: List of CLI argument strings to pass to the script.
        cwd: Working directory for the subprocess (defaults to repo root).

    Returns:
        CompletedProcess instance with returncode, stdout, and stderr attributes.
    """
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    env = os.environ.copy()
    env["PYTHONPATH"] = repo_root
    cmd = [sys.executable, os.path.join(DIALOG_SCRIPTS, script_name)] + args
    return subprocess.run(cmd, capture_output=True, text=True, env=env, cwd=cwd or repo_root)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def tmp_project(tmp_path):
    """Copy the example fixture to a temp directory for write-test isolation.

    Ensures that tests that call --apply do not modify the committed fixture files.
    """
    dest = tmp_path / "project"
    shutil.copytree(FIXTURE_DIR, dest)
    return str(dest)


# ---------------------------------------------------------------------------
# Tests: extract_npc_lines.py (DLOG-06)
# ---------------------------------------------------------------------------


def test_extract_hero_golden_match():
    """Stdout from extracting Hero must exactly match the committed golden file."""
    result = run_script(
        "extract_npc_lines.py", ["--project", FIXTURE_DIR, "--npc", "Hero"]
    )
    assert result.returncode == 0, f"Script failed: {result.stderr}"

    golden_path = os.path.join(GOLDEN_DIR, "extract_hero.txt")
    with open(golden_path, encoding="utf-8") as fh:
        expected = fh.read()

    assert result.stdout == expected, (
        f"Hero output does not match golden file.\n"
        f"Expected:\n{expected}\n"
        f"Got:\n{result.stdout}"
    )


def test_extract_innkeeper_golden_match():
    """Stdout from extracting Innkeeper must exactly match the committed golden file."""
    result = run_script(
        "extract_npc_lines.py", ["--project", FIXTURE_DIR, "--npc", "Innkeeper"]
    )
    assert result.returncode == 0, f"Script failed: {result.stderr}"

    golden_path = os.path.join(GOLDEN_DIR, "extract_innkeeper.txt")
    with open(golden_path, encoding="utf-8") as fh:
        expected = fh.read()

    assert result.stdout == expected, (
        f"Innkeeper output does not match golden file.\n"
        f"Expected:\n{expected}\n"
        f"Got:\n{result.stdout}"
    )


def test_extract_nonexistent_npc_exits_1():
    """Requesting a NPC name that has no dialog lines must exit with return code 1."""
    result = run_script(
        "extract_npc_lines.py", ["--project", FIXTURE_DIR, "--npc", "ZzzNobody"]
    )
    assert result.returncode == 1, (
        f"Expected exit 1 for unknown NPC but got {result.returncode}. "
        f"stdout={result.stdout!r}"
    )


def test_extract_preserves_text_codes():
    r"""Dialog text codes (e.g. \N[1]) must be preserved verbatim in the output."""
    result = run_script(
        "extract_npc_lines.py", ["--project", FIXTURE_DIR, "--npc", "Hero"]
    )
    assert result.returncode == 0, f"Script failed: {result.stderr}"
    assert r"\N[1]" in result.stdout, (
        r"Expected \N[1] text code in Hero output (from Quest Start dialog) "
        f"but got:\n{result.stdout}"
    )


# ---------------------------------------------------------------------------
# Tests: inject_dialog.py (DLOG-05)
# ---------------------------------------------------------------------------


def test_inject_dry_run_does_not_modify(tmp_project):
    """Without --apply the script must not modify any files."""
    ce_path = os.path.join(tmp_project, "data", "CommonEvents.json")
    with open(ce_path, encoding="utf-8") as fh:
        before = fh.read()

    result = run_script(
        "inject_dialog.py",
        ["--project", tmp_project, "--target", "common-event:1", "--lines", "Test dry run."],
    )
    assert result.returncode == 0, f"Script failed: {result.stderr}"

    with open(ce_path, encoding="utf-8") as fh:
        after = fh.read()

    assert before == after, (
        "Dry-run mode must not modify CommonEvents.json but the file changed."
    )


def test_inject_common_event_apply(tmp_project):
    """Applying inject_dialog.py to a CommonEvent must insert valid 401 entries."""
    result = run_script(
        "inject_dialog.py",
        [
            "--project", tmp_project,
            "--target", "common-event:1",
            "--lines", "Injected line one.", "Injected line two.",
            "--apply",
        ],
    )
    assert result.returncode == 0, f"Script failed: {result.stderr}"

    ce_path = os.path.join(tmp_project, "data", "CommonEvents.json")
    with open(ce_path, encoding="utf-8") as fh:
        data = json.load(fh)

    event_list = data[1]["list"]

    # Check both injected lines appear as code 401 entries
    texts = [
        cmd["parameters"][0]
        for cmd in event_list
        if cmd.get("code") == 401
    ]
    assert "Injected line one." in texts, (
        f"'Injected line one.' not found in 401 entries. Got: {texts}"
    )
    assert "Injected line two." in texts, (
        f"'Injected line two.' not found in 401 entries. Got: {texts}"
    )

    # Terminator (code 0) must be the last command
    assert event_list[-1]["code"] == 0, (
        f"Last command must be code 0 (terminator) but got code {event_list[-1]['code']}"
    )

    # Backup must have been created
    bak_path = ce_path + ".bak"
    assert os.path.exists(bak_path), f"Expected .bak file at {bak_path} but it was not created"


def test_inject_validates_schema(tmp_project):
    """CommonEvents.json after injection must still validate against its JSON Schema."""
    result = run_script(
        "inject_dialog.py",
        [
            "--project", tmp_project,
            "--target", "common-event:1",
            "--lines", "Schema test.",
            "--apply",
        ],
    )
    assert result.returncode == 0, f"Script failed: {result.stderr}"

    ce_path = os.path.join(tmp_project, "data", "CommonEvents.json")
    schema_path = os.path.join(SCHEMA_DIR, "common-events.schema.json")

    with open(ce_path, encoding="utf-8") as fh:
        data = json.load(fh)
    with open(schema_path, encoding="utf-8") as fh:
        schema = json.load(fh)

    # Must not raise jsonschema.ValidationError
    jsonschema.validate(instance=data, schema=schema)


def test_inject_map_event_apply(tmp_project):
    """Applying inject_dialog.py to a map event must insert a valid dialog entry."""
    result = run_script(
        "inject_dialog.py",
        [
            "--project", tmp_project,
            "--target", "map:1:event:1",
            "--lines", "Map inject test.",
            "--apply",
        ],
    )
    assert result.returncode == 0, f"Script failed: {result.stderr}"

    map_path = os.path.join(tmp_project, "data", "Map001.json")
    with open(map_path, encoding="utf-8") as fh:
        map_data = json.load(fh)

    # Find event with id == 1
    events = map_data.get("events", [])
    target_event = next(
        (e for e in events if e is not None and e.get("id") == 1), None
    )
    assert target_event is not None, "Event id=1 not found in Map001.json"

    page_list = target_event["pages"][0]["list"]

    # Injected line must appear as a code 401 entry
    texts = [
        cmd["parameters"][0]
        for cmd in page_list
        if cmd.get("code") == 401
    ]
    assert "Map inject test." in texts, (
        f"'Map inject test.' not found in 401 entries. Got: {texts}"
    )

    # Terminator (code 0) must be the last command
    assert page_list[-1]["code"] == 0, (
        f"Last command must be code 0 (terminator) but got code {page_list[-1]['code']}"
    )


# ---------------------------------------------------------------------------
# Tests: validate_dialog_refs.py (DLOG-07)
# ---------------------------------------------------------------------------


def test_validate_clean_project_exits_0():
    """validate_dialog_refs.py must exit 0 when the project has no broken references."""
    result = run_script(
        "validate_dialog_refs.py", ["--project", FIXTURE_DIR]
    )
    assert result.returncode == 0, (
        f"Expected exit 0 on clean project but got {result.returncode}. "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )


def test_validate_broken_fixture_exits_1():
    r"""validate_dialog_refs.py must exit 1 and report \N[99] and \I[999] errors."""
    result = run_script(
        "validate_dialog_refs.py", ["--project", BROKEN_DIR]
    )
    assert result.returncode == 1, (
        f"Expected exit 1 on broken fixture but got {result.returncode}. "
        f"stdout={result.stdout!r}"
    )
    assert r"\N[99]" in result.stdout, (
        r"Expected \N[99] in error output but got: " + result.stdout
    )
    assert r"\I[999]" in result.stdout, (
        r"Expected \I[999] in error output but got: " + result.stdout
    )


def test_validate_after_inject_still_clean(tmp_project):
    r"""After injecting valid dialog containing \N[1], validate must still exit 0."""
    inject_result = run_script(
        "inject_dialog.py",
        [
            "--project", tmp_project,
            "--target", "common-event:2",
            "--lines", r"Valid dialog \N[1].",
            "--apply",
        ],
    )
    assert inject_result.returncode == 0, (
        f"inject_dialog.py failed: {inject_result.stderr}"
    )

    validate_result = run_script(
        "validate_dialog_refs.py", ["--project", tmp_project]
    )
    assert validate_result.returncode == 0, (
        "validate_dialog_refs.py should exit 0 after injecting valid dialog. "
        f"stdout={validate_result.stdout!r} stderr={validate_result.stderr!r}"
    )
