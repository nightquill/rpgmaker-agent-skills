"""Detect switch collision candidates in an RPG Maker MV/MZ project.

A switch collision occurs when the same global switch is SET (code 121) in
more than one map file without being a recognized global switch. This often
indicates a copy-paste bug where a developer reused a switch ID unintentionally.

Checking (reading) a switch across maps is normal and is never flagged.

Usage:
    python check_switch_collisions.py --project <path>

Exit codes:
    0 -- always (collisions are warnings, not errors per D-02)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))  # repo root

import argparse
import json
import os
from collections import defaultdict

from scripts.lib.event_traverse import iter_event_lists


def load_system_data(project_path: str) -> dict:
    """Read and return parsed data/System.json.

    Args:
        project_path: Path to RPG Maker project root directory.

    Returns:
        Parsed System.json as a dict.

    Raises:
        FileNotFoundError: If System.json does not exist.
        json.JSONDecodeError: If System.json is malformed.
    """
    system_path = os.path.join(project_path, "data", "System.json")
    if not os.path.exists(system_path):
        raise FileNotFoundError(f"System.json not found: {system_path}")
    with open(system_path, encoding="utf-8") as f:
        return json.load(f)


def get_switch_name(system_data: dict, switch_id: int) -> str:
    """Look up switch name from System.json switches array.

    Args:
        system_data: Parsed System.json dict.
        switch_id: The switch ID to look up (1-based index into switches array).

    Returns:
        The switch name if found and non-empty, else '(unnamed switch {switch_id})'.
    """
    switches = system_data.get("switches", [])
    if 0 < switch_id < len(switches) and switches[switch_id]:
        return switches[switch_id]
    return f"(unnamed switch {switch_id})"


def is_global_switch(name: str) -> bool:
    """Determine whether a switch name indicates it is intentionally global.

    A switch is considered global (and thus not a collision candidate) if:
    - It contains "GLOBAL" (case-insensitive)
    - Its name contains an underscore (naming convention for global switches)
    - Its name starts with an uppercase letter (convention for global flags)

    Unnamed switches are never considered global.

    Args:
        name: The switch name from System.json (may be a '(unnamed switch N)' fallback).

    Returns:
        True if the switch appears to be intentionally global, False otherwise.
    """
    if name.startswith("(unnamed"):
        return False
    if "GLOBAL" in name.upper():
        return True
    if "_" in name:
        return True
    if name and name[0].isupper():
        return True
    return False


def collect_switch_sets(project_path: str) -> defaultdict:
    """Collect all switch SET operations, grouped by switch ID and source location.

    Only tracks SET operations (code 121). Conditional branch checks (code 111)
    are reads and are never tracked. Page conditions are also reads and not tracked.

    Labels from iter_event_lists look like:
    - "Map001.json:Event2:Guard:Page0" (map events)
    - "CommonEvent:1:Name" (common events)

    CommonEvent SET operations are tracked separately — a switch SET in a
    CommonEvent AND a map is not flagged (CommonEvents are called from maps,
    so this is expected behavior).

    Args:
        project_path: Path to RPG Maker project root directory.

    Returns:
        defaultdict(set) mapping switch_id -> set of map filenames where SET.
    """
    switch_sets: defaultdict = defaultdict(set)

    for label, event_list in iter_event_lists(project_path):
        for cmd in event_list:
            code = cmd.get("code")
            if code != 121:
                continue

            params = cmd.get("parameters", [])
            if len(params) < 2:
                continue

            start_id = params[0]
            end_id = params[1]

            # Extract source identifier from label
            # CommonEvent labels: "CommonEvent:1:Name"
            # Map labels: "Map001.json:Event2:Guard:Page0"
            parts = label.split(":")
            if parts[0].startswith("CommonEvent"):
                source = "CommonEvent"
            else:
                source = parts[0]  # e.g. "Map001.json"

            for sw_id in range(start_id, end_id + 1):
                switch_sets[sw_id].add(source)

    return switch_sets


def check_project(project_path: str) -> int:
    """Detect switch collision candidates in the project.

    A collision candidate is a switch that is SET in more than one distinct map
    file and does not appear to be an intentional global switch (per is_global_switch).

    Args:
        project_path: Path to RPG Maker project root directory.

    Returns:
        Always 0 (warnings are informational only, per D-02).
    """
    system_data = load_system_data(project_path)
    switch_sets = collect_switch_sets(project_path)

    for switch_id in sorted(switch_sets.keys()):
        sources = switch_sets[switch_id]

        # Only flag switches SET in more than one distinct source
        if len(sources) <= 1:
            continue

        # CommonEvent is called from maps -- mixed CommonEvent+map is normal
        map_sources = {s for s in sources if s != "CommonEvent"}
        if len(map_sources) <= 1:
            continue

        name = get_switch_name(system_data, switch_id)

        # Skip recognized global switches
        if is_global_switch(name):
            continue

        print(
            f"WARNING: Switch {switch_id} ({name}) set in multiple maps:"
            f" {', '.join(sorted(map_sources))}"
        )

    return 0


def main() -> None:
    """CLI entry point for switch collision detection."""
    parser = argparse.ArgumentParser(
        description="Detect switch collision candidates in an RPG Maker MV/MZ project."
    )
    parser.add_argument(
        "--project",
        required=True,
        help="Path to RPG Maker project root directory",
    )
    args = parser.parse_args()

    if not os.path.isdir(args.project):
        print(
            f"Error: Project path does not exist: {args.project}",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        sys.exit(check_project(args.project))
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
