"""Validate dialog text code references in an RPG Maker MV/MZ project.

Checks that all \\N[id] (actor) and \\I[id] (item) references in Show Text
commands (code 401) resolve to existing database entries. Prints structured
error lines and exits non-zero if any broken references are found.

Scope: only \\N[id] and \\I[id] — \\V[], \\C[], \\P[] are out of scope (Pitfall 6).

Usage:
    python validate_dialog_refs.py --project <path>

Exit codes:
    0 — no broken references found
    1 — one or more broken references found (errors printed to stdout)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[3]))  # repo root

import argparse
import glob
import json
import os
import re

# Regex patterns for actor and item text code references (Pitfall 6 / Pattern 5)
ACTOR_REF_RE = re.compile(r"\\N\[(\d+)\]")
ITEM_REF_RE = re.compile(r"\\I\[(\d+)\]")


def load_valid_ids(filepath: str) -> set:
    """Load valid IDs from a JSON database array (skipping null at index 0).

    Args:
        filepath: Absolute path to the JSON database file.

    Returns:
        Set of integer IDs present in the database.
    """
    with open(filepath, encoding="utf-8") as f:
        entries = json.load(f)

    ids: set = set()
    for entry in entries:
        if entry is None:
            continue
        ids.add(entry["id"])
    return ids


def check_refs_in_line(text: str, actor_ids: set, item_ids: set) -> list:
    """Check a single text string for broken \\N[] and \\I[] references.

    Args:
        text: The dialog text to scan.
        actor_ids: Set of valid actor IDs.
        item_ids: Set of valid item IDs.

    Returns:
        List of error description strings (empty if no errors).
    """
    errors: list = []

    for match in ACTOR_REF_RE.finditer(text):
        ref_id = int(match.group(1))
        if ref_id not in actor_ids:
            errors.append(f"\\N[{ref_id}] — no actor {ref_id}")

    for match in ITEM_REF_RE.finditer(text):
        ref_id = int(match.group(1))
        if ref_id not in item_ids:
            errors.append(f"\\I[{ref_id}] — no item {ref_id}")

    return errors


def walk_all_dialog(project_path: str):
    """Yield (source_label, command_list) pairs from all dialog sources.

    Covers CommonEvents.json and all Map[0-9]*.json files.

    Args:
        project_path: Path to RPG Maker project root.

    Yields:
        Tuples of (source_label: str, command_list: list).
    """
    # Walk CommonEvents.json
    ce_path = os.path.join(project_path, "data", "CommonEvents.json")
    if os.path.exists(ce_path):
        with open(ce_path, encoding="utf-8") as f:
            common_events = json.load(f)
        for entry in common_events:
            if entry is None:
                continue
            label = f"CommonEvent:{entry['id']}:{entry['name']}"
            yield label, entry.get("list", [])

    # Walk all map files — never hardcode filenames
    map_pattern = os.path.join(project_path, "data", "Map[0-9]*.json")
    map_files = sorted(glob.glob(map_pattern))

    for map_file in map_files:
        map_basename = os.path.basename(map_file)
        with open(map_file, encoding="utf-8") as f:
            map_data = json.load(f)

        events = map_data.get("events", [])
        # events is an array (MV) or object (MZ) — handle both
        if isinstance(events, list):
            event_iter = (e for e in events if e is not None)
        else:
            event_iter = (e for e in events.values() if e is not None)

        for event in event_iter:
            event_id = event.get("id", "?")
            event_name = event.get("name", "")
            pages = event.get("pages", [])
            for page_idx, page in enumerate(pages):
                label = (
                    f"{map_basename}:Event{event_id}:{event_name}:Page{page_idx}"
                )
                yield label, page.get("list", [])


def validate_project(project_path: str) -> int:
    """Validate all dialog text code references in the project.

    Args:
        project_path: Path to RPG Maker project root.

    Returns:
        0 if no errors, 1 if any broken references found.
    """
    actors_path = os.path.join(project_path, "data", "Actors.json")
    items_path = os.path.join(project_path, "data", "Items.json")

    if not os.path.exists(actors_path):
        print(f"Error: Actors.json not found at {actors_path}", file=sys.stderr)
        return 1

    if not os.path.exists(items_path):
        print(f"Error: Items.json not found at {items_path}", file=sys.stderr)
        return 1

    actor_ids = load_valid_ids(actors_path)
    item_ids = load_valid_ids(items_path)

    found_errors = False

    for source_label, command_list in walk_all_dialog(project_path):
        for cmd in command_list:
            if cmd.get("code") != 401:
                continue
            params = cmd.get("parameters", [])
            if not params:
                continue
            text = params[0]
            errors = check_refs_in_line(text, actor_ids, item_ids)
            for error in errors:
                print(f"{source_label}: {error}")
                found_errors = True

    return 1 if found_errors else 0


def main() -> None:
    """CLI entry point for dialog reference validation."""
    parser = argparse.ArgumentParser(
        description=(
            "Validate dialog text code references in an RPG Maker MV/MZ project. "
            "Checks \\N[id] (actor) and \\I[id] (item) references in all Show Text "
            "commands. Exits 0 if clean, 1 if broken references found."
        )
    )
    parser.add_argument(
        "--project",
        required=True,
        help="Path to RPG Maker project root directory",
    )
    args = parser.parse_args()

    if not os.path.isdir(args.project):
        print(f"Error: Project path does not exist: {args.project}", file=sys.stderr)
        sys.exit(1)

    sys.exit(validate_project(args.project))


if __name__ == "__main__":
    main()
