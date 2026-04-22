"""Tests for Phase 4 event scripts: scaffold_event.py, list_switches.py, find_event_refs.py.

All scripts are invoked via subprocess with PYTHONPATH set to the repo root so they
run in the same environment as normal CLI use. Tests use the example-mv-project fixture
for clean-state tests and temp directories for MZ/write-isolation tests.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile

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


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def run_script(script_name: str, args: list, cwd=None) -> subprocess.CompletedProcess:
    """Run a script from SCRIPTS_DIR via subprocess with PYTHONPATH set to repo root.

    Args:
        script_name: Filename of the script (e.g. 'scaffold_event.py').
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
# Tests: scaffold_event.py — basic patterns
# ---------------------------------------------------------------------------


def test_scaffold_chest_ends_with_code0():
    """Chest pattern must end with code-0 terminator and start with code 126."""
    result = run_script(
        "scaffold_event.py",
        ["--project", FIXTURE_DIR, "--pattern", "chest", "--item-id", "1"],
    )
    assert result.returncode == 0, f"Script failed: {result.stderr}"
    cmd_list = json.loads(result.stdout)
    assert len(cmd_list) >= 1, "Output must be non-empty"
    last = cmd_list[-1]
    assert last["code"] == 0, f"Last entry must have code 0, got {last['code']}"
    assert last["indent"] == 0, f"Last entry must have indent 0, got {last['indent']}"
    assert last["parameters"] == [], f"Last entry must have empty parameters, got {last['parameters']}"
    first = cmd_list[0]
    assert first["code"] == 126, f"First entry must have code 126 (Change Items), got {first['code']}"


def test_scaffold_chest_has_self_switch_string():
    """Chest pattern must include code 123 with parameters[0] == 'A' (string, not integer)."""
    result = run_script(
        "scaffold_event.py",
        ["--project", FIXTURE_DIR, "--pattern", "chest", "--item-id", "1"],
    )
    assert result.returncode == 0, f"Script failed: {result.stderr}"
    cmd_list = json.loads(result.stdout)
    self_switch_entries = [c for c in cmd_list if c.get("code") == 123]
    assert len(self_switch_entries) >= 1, "Chest pattern must include a code 123 (Control Self Switch) entry"
    entry = self_switch_entries[0]
    params = entry.get("parameters", [])
    assert len(params) >= 1, "code 123 must have at least one parameter"
    assert params[0] == "A", (
        f"Self-switch parameter must be string 'A', got {params[0]!r} (type: {type(params[0]).__name__})"
    )


def test_scaffold_shop_produces_302_and_605():
    """Shop pattern must produce code 302 header and code 605 continuation entries."""
    result = run_script(
        "scaffold_event.py",
        ["--project", FIXTURE_DIR, "--pattern", "shop", "--shop-items", "0:1,0:2"],
    )
    assert result.returncode == 0, f"Script failed: {result.stderr}"
    cmd_list = json.loads(result.stdout)
    codes = [c["code"] for c in cmd_list]
    assert 302 in codes, f"Shop pattern must include code 302 (Shop Processing), got codes: {codes}"
    assert 605 in codes, f"Shop pattern must include code 605 (Shop Goods continuation), got codes: {codes}"
    assert codes[-1] == 0, f"Last entry must be code 0, got {codes[-1]}"


def test_scaffold_inn_has_choice_branches():
    """Inn pattern must include codes 102, 402, 404 (choice), 125 (Change Gold), and code 0."""
    result = run_script(
        "scaffold_event.py",
        ["--project", FIXTURE_DIR, "--pattern", "inn"],
    )
    assert result.returncode == 0, f"Script failed: {result.stderr}"
    cmd_list = json.loads(result.stdout)
    codes = [c["code"] for c in cmd_list]
    assert 102 in codes, f"Inn pattern must include code 102 (Show Choices), got codes: {codes}"
    assert 402 in codes, f"Inn pattern must include code 402 (When [choice]), got codes: {codes}"
    assert 404 in codes, f"Inn pattern must include code 404 (End Choice), got codes: {codes}"
    assert 125 in codes, f"Inn pattern must include code 125 (Change Gold), got codes: {codes}"
    assert codes[-1] == 0, f"Last entry must be code 0, got {codes[-1]}"


def test_scaffold_door_has_conditional_branch():
    """Door pattern must include codes 111, 411, 412 (conditional branch) and code 0."""
    result = run_script(
        "scaffold_event.py",
        ["--project", FIXTURE_DIR, "--pattern", "door", "--switch-id", "1"],
    )
    assert result.returncode == 0, f"Script failed: {result.stderr}"
    cmd_list = json.loads(result.stdout)
    codes = [c["code"] for c in cmd_list]
    assert 111 in codes, f"Door pattern must include code 111 (Conditional Branch), got codes: {codes}"
    assert 411 in codes, f"Door pattern must include code 411 (Else branch), got codes: {codes}"
    assert 412 in codes, f"Door pattern must include code 412 (End Conditional), got codes: {codes}"
    assert codes[-1] == 0, f"Last entry must be code 0, got {codes[-1]}"


def test_scaffold_cutscene_has_switch_gate():
    """Cutscene pattern must include codes 111, 121, 412 and code 0."""
    result = run_script(
        "scaffold_event.py",
        ["--project", FIXTURE_DIR, "--pattern", "cutscene", "--switch-id", "1"],
    )
    assert result.returncode == 0, f"Script failed: {result.stderr}"
    cmd_list = json.loads(result.stdout)
    codes = [c["code"] for c in cmd_list]
    assert 111 in codes, f"Cutscene pattern must include code 111 (Conditional Branch), got codes: {codes}"
    assert 121 in codes, f"Cutscene pattern must include code 121 (Control Switches), got codes: {codes}"
    assert 412 in codes, f"Cutscene pattern must include code 412 (End Conditional), got codes: {codes}"
    assert codes[-1] == 0, f"Last entry must be code 0, got {codes[-1]}"


def test_scaffold_wanderer_has_move_route():
    """Wanderer pattern must include code 205 (Set Movement Route) targeting this event (params[0]=0)."""
    result = run_script(
        "scaffold_event.py",
        ["--project", FIXTURE_DIR, "--pattern", "wanderer"],
    )
    assert result.returncode == 0, f"Script failed: {result.stderr}"
    cmd_list = json.loads(result.stdout)
    move_entries = [c for c in cmd_list if c.get("code") == 205]
    assert len(move_entries) >= 1, "Wanderer pattern must include code 205 (Set Movement Route)"
    entry = move_entries[0]
    params = entry.get("parameters", [])
    assert len(params) >= 2, "code 205 must have at least 2 parameters"
    assert params[0] == 0, (
        f"params[0] must be 0 (this event), got {params[0]!r}. "
        "Note: -1 would target the player, not this event."
    )
    route = params[1]
    assert isinstance(route, dict), f"params[1] must be a route dict, got {type(route)}"
    assert route.get("repeat") is True, (
        f"Movement route must have repeat=True, got repeat={route.get('repeat')!r}"
    )
    codes = [c["code"] for c in cmd_list]
    assert codes[-1] == 0, f"Last entry must be code 0, got {codes[-1]}"


@pytest.mark.parametrize(
    "pattern,extra_args",
    [
        ("chest", ["--item-id", "1"]),
        ("shop", ["--shop-items", "0:1"]),
        ("inn", []),
        ("door", ["--switch-id", "1"]),
        ("cutscene", ["--switch-id", "1"]),
        ("wanderer", []),
        ("plugin-command", ["--plugin-name", "TestPlugin", "--plugin-command", "DoThing"]),
    ],
)
def test_scaffold_all_patterns_end_with_code0(pattern, extra_args):
    """All 7 patterns (6 standard + plugin-command) must produce valid JSON ending with code 0."""
    result = run_script(
        "scaffold_event.py",
        ["--project", FIXTURE_DIR, "--pattern", pattern] + extra_args,
    )
    assert result.returncode == 0, (
        f"Pattern '{pattern}' failed with exit {result.returncode}.\n"
        f"stderr: {result.stderr}\nstdout: {result.stdout}"
    )
    cmd_list = json.loads(result.stdout)
    assert isinstance(cmd_list, list), f"Output must be a JSON array, got {type(cmd_list)}"
    assert len(cmd_list) >= 1, f"Pattern '{pattern}' must produce at least one entry"
    last = cmd_list[-1]
    assert last["code"] == 0, (
        f"Pattern '{pattern}' last entry must have code 0 (terminator), got {last['code']}"
    )


# ---------------------------------------------------------------------------
# Tests: scaffold_event.py — missing required args (non-zero exit)
# ---------------------------------------------------------------------------


def test_scaffold_chest_missing_item_id_exits_nonzero():
    """Running chest pattern without --item-id must exit non-zero."""
    result = run_script(
        "scaffold_event.py",
        ["--project", FIXTURE_DIR, "--pattern", "chest"],
    )
    assert result.returncode != 0, (
        f"Expected non-zero exit for chest without --item-id but got {result.returncode}"
    )


def test_scaffold_shop_missing_items_exits_nonzero():
    """Running shop pattern without --shop-items must exit non-zero."""
    result = run_script(
        "scaffold_event.py",
        ["--project", FIXTURE_DIR, "--pattern", "shop"],
    )
    assert result.returncode != 0, (
        f"Expected non-zero exit for shop without --shop-items but got {result.returncode}"
    )


def test_scaffold_plugin_command_missing_args_exits_nonzero():
    """Running plugin-command pattern without --plugin-name and --plugin-command must exit non-zero."""
    result = run_script(
        "scaffold_event.py",
        ["--project", FIXTURE_DIR, "--pattern", "plugin-command"],
    )
    assert result.returncode != 0, (
        f"Expected non-zero exit for plugin-command without required args but got {result.returncode}"
    )


# ---------------------------------------------------------------------------
# Tests: scaffold_event.py — MV/MZ plugin command discrimination (SC-3)
# ---------------------------------------------------------------------------


def test_scaffold_plugin_cmd_mv_uses_356():
    """On the MV fixture (Game.rpgproject), plugin-command pattern must produce code 356."""
    result = run_script(
        "scaffold_event.py",
        [
            "--project", FIXTURE_DIR,
            "--pattern", "plugin-command",
            "--plugin-name", "TestPlugin",
            "--plugin-command", "DoThing",
        ],
    )
    assert result.returncode == 0, f"Script failed: {result.stderr}"
    cmd_list = json.loads(result.stdout)
    # Find the non-terminator entry (the plugin command itself)
    plugin_entries = [c for c in cmd_list if c["code"] != 0]
    assert len(plugin_entries) >= 1, "Expected at least one non-terminator entry"
    plugin_entry = plugin_entries[0]
    assert plugin_entry["code"] == 356, (
        f"MV fixture must produce code 356 for plugin-command, got {plugin_entry['code']}"
    )
    params = plugin_entry.get("parameters", [])
    assert len(params) >= 1, "code 356 must have at least one parameter"
    assert "TestPlugin" in params[0], (
        f"code 356 parameters[0] must contain plugin name 'TestPlugin', got {params[0]!r}"
    )


def test_scaffold_plugin_cmd_mz_uses_357():
    """On an MZ project (Game.rmmzproject), plugin-command pattern must produce code 357."""
    with tempfile.TemporaryDirectory() as tmp:
        # Create MZ project marker file
        open(os.path.join(tmp, "Game.rmmzproject"), "w").close()
        result = run_script(
            "scaffold_event.py",
            [
                "--project", tmp,
                "--pattern", "plugin-command",
                "--plugin-name", "TestPlugin",
                "--plugin-command", "DoThing",
            ],
        )
        assert result.returncode == 0, f"Script failed: {result.stderr}"
        cmd_list = json.loads(result.stdout)
        plugin_entries = [c for c in cmd_list if c["code"] != 0]
        assert len(plugin_entries) >= 1, "Expected at least one non-terminator entry"
        plugin_entry = plugin_entries[0]
        assert plugin_entry["code"] == 357, (
            f"MZ project must produce code 357 for plugin-command, got {plugin_entry['code']}"
        )
        params = plugin_entry.get("parameters", [])
        assert len(params) >= 2, f"code 357 must have at least 2 parameters, got {params}"
        assert params[0] == "TestPlugin", (
            f"code 357 parameters[0] must be plugin name 'TestPlugin', got {params[0]!r}"
        )
        assert params[1] == "DoThing", (
            f"code 357 parameters[1] must be command 'DoThing', got {params[1]!r}"
        )


# ---------------------------------------------------------------------------
# Tests: list_switches.py
# ---------------------------------------------------------------------------


def test_list_switches_produces_markdown_table():
    """list_switches.py must output a markdown table with the expected header row."""
    result = run_script("list_switches.py", ["--project", FIXTURE_DIR])
    assert result.returncode == 0, f"Script failed: {result.stderr}"
    assert "| Switch ID | Name | Used In | Operation |" in result.stdout, (
        f"Expected markdown table header in output, got:\n{result.stdout}"
    )


def test_list_switches_finds_quest_active():
    """list_switches.py must surface the 'Quest Active' switch name from System.json."""
    result = run_script("list_switches.py", ["--project", FIXTURE_DIR])
    assert result.returncode == 0, f"Script failed: {result.stderr}"
    assert "Quest Active" in result.stdout, (
        f"Expected 'Quest Active' in output (from System.json switches array), got:\n{result.stdout}"
    )


def test_list_switches_finds_set_in_common_event():
    """list_switches.py must detect the code 121 switch-set in CommonEvents.json event 2."""
    result = run_script("list_switches.py", ["--project", FIXTURE_DIR])
    assert result.returncode == 0, f"Script failed: {result.stderr}"
    output_lower = result.stdout.lower()
    assert "commonevent" in output_lower, (
        f"Expected 'CommonEvent' label in output (code 121 in CommonEvents.json event 2), "
        f"got:\n{result.stdout}"
    )
    assert "set" in output_lower, (
        f"Expected 'set' operation in output (code 121 sets a switch), got:\n{result.stdout}"
    )


def test_list_switches_finds_page_condition():
    """list_switches.py must detect the switch page condition in Map003.json (switch1Valid=true, switch1Id=1)."""
    result = run_script("list_switches.py", ["--project", FIXTURE_DIR])
    assert result.returncode == 0, f"Script failed: {result.stderr}"
    assert "page condition" in result.stdout.lower(), (
        f"Expected 'page condition' operation in output (Map003.json switch1Valid=true), "
        f"got:\n{result.stdout}"
    )


def test_list_switches_nonexistent_project_exits_nonzero():
    """list_switches.py must exit non-zero when project path does not exist."""
    result = run_script("list_switches.py", ["--project", "/nonexistent/path/to/project"])
    assert result.returncode != 0, (
        f"Expected non-zero exit for nonexistent project but got {result.returncode}"
    )


# ---------------------------------------------------------------------------
# Tests: find_event_refs.py
# ---------------------------------------------------------------------------


def test_find_refs_switch_1_found():
    """find_event_refs.py must exit 0 and output results when switch 1 is referenced."""
    result = run_script(
        "find_event_refs.py",
        ["--project", FIXTURE_DIR, "--switch-id", "1"],
    )
    assert result.returncode == 0, (
        f"Expected exit 0 (found) for switch 1 but got {result.returncode}. "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    lines = [ln for ln in result.stdout.strip().splitlines() if ln]
    assert len(lines) >= 1, f"Expected at least one output line, got:\n{result.stdout}"


def test_find_refs_switch_999_not_found():
    """find_event_refs.py must exit 1 when switch 999 is not referenced anywhere."""
    result = run_script(
        "find_event_refs.py",
        ["--project", FIXTURE_DIR, "--switch-id", "999"],
    )
    assert result.returncode == 1, (
        f"Expected exit 1 (not found) for switch 999 but got {result.returncode}. "
        f"stdout={result.stdout!r}"
    )


def test_find_refs_self_switch_found():
    """find_event_refs.py must exit 0 when self-switch A is referenced.

    Fixture setup: Map002.json already contains a code 123 entry with parameters ["A", 0]
    (chest event that sets self-switch A). The test confirms the fixture data is present
    and that find_event_refs.py successfully locates it.
    """
    # Verify the fixture already has code 123 with self-switch "A"
    map002_path = os.path.join(FIXTURE_DIR, "data", "Map002.json")
    with open(map002_path, encoding="utf-8") as fh:
        map_data = json.load(fh)

    # Flatten all event page lists to check for code 123
    has_code_123 = False
    events = map_data.get("events", {})
    if isinstance(events, dict):
        event_iter = events.values()
    else:
        event_iter = (e for e in events if e is not None)

    for event in event_iter:
        if event is None:
            continue
        for page in event.get("pages", []):
            for cmd in page.get("list", []):
                if cmd.get("code") == 123 and cmd.get("parameters", [None])[0] == "A":
                    has_code_123 = True
                    break

    if has_code_123:
        # Fixture already has code 123 — run directly against FIXTURE_DIR
        project_path = FIXTURE_DIR
        cleanup = None
    else:
        # Fixture does not have code 123 — create a temp copy with the entry added
        tmp_dir = tempfile.mkdtemp()
        cleanup = tmp_dir
        shutil.copytree(FIXTURE_DIR, os.path.join(tmp_dir, "project"))
        project_path = os.path.join(tmp_dir, "project")
        map001_path = os.path.join(project_path, "data", "Map001.json")
        with open(map001_path, encoding="utf-8") as fh:
            map001_data = json.load(fh)
        # Add code 123 entry to event 1, page 0's command list (before the code-0 terminator)
        events_field = map001_data.get("events", {})
        if isinstance(events_field, dict):
            target_event = events_field.get("1")
        else:
            target_event = next(
                (e for e in events_field if e is not None and e.get("id") == 1), None
            )
        if target_event is not None:
            page_list = target_event["pages"][0]["list"]
            # Insert code 123 before the terminator
            insert_pos = next(
                (i for i, c in enumerate(page_list) if c["code"] == 0),
                len(page_list),
            )
            page_list.insert(insert_pos, {"code": 123, "indent": 0, "parameters": ["A", 0]})
        with open(map001_path, "w", encoding="utf-8") as fh:
            json.dump(map001_data, fh, ensure_ascii=False, indent=2)

    try:
        result = run_script(
            "find_event_refs.py",
            ["--project", project_path, "--self-switch", "A"],
        )
        assert result.returncode == 0, (
            f"Expected exit 0 (found) for self-switch A but got {result.returncode}. "
            f"stdout={result.stdout!r} stderr={result.stderr!r}"
        )
        output_lower = result.stdout.lower()
        assert any(
            keyword in output_lower
            for keyword in ["self switch", "self-switch", "control self switch"]
        ), (
            f"Expected 'Control Self Switch' or 'self-switch' in output, got:\n{result.stdout}"
        )
    finally:
        if cleanup is not None:
            shutil.rmtree(cleanup, ignore_errors=True)


def test_find_refs_requires_one_search_type():
    """find_event_refs.py must exit non-zero if none of --switch-id, --var-id, --self-switch are given."""
    result = run_script(
        "find_event_refs.py",
        ["--project", FIXTURE_DIR],
    )
    assert result.returncode != 0, (
        f"Expected non-zero exit when no search type given but got {result.returncode}"
    )


def test_find_refs_output_contains_location():
    """find_event_refs.py --switch-id 1 output must contain location labels (CommonEvent: or Map prefix)."""
    result = run_script(
        "find_event_refs.py",
        ["--project", FIXTURE_DIR, "--switch-id", "1"],
    )
    assert result.returncode == 0, f"Script failed: {result.stderr}"
    output = result.stdout
    has_location = any(
        label in output
        for label in ["CommonEvent:", "Map001:", "Map002:", "Map003:"]
    )
    assert has_location, (
        f"Expected output to contain a location label (CommonEvent: or MapXXX:), got:\n{output}"
    )
