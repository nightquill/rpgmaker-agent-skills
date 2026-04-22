"""List all switch references across an RPG Maker MV/MZ project.

Scans CommonEvents.json, all Map*.json files, and CommonEvents trigger
conditions to produce a markdown table of every switch reference with
its source location, name (from System.json), and operation type.

Usage:
    python scripts/list_switches.py --project /path/to/project
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

import argparse
import json
import os

from scripts.lib.event_traverse import iter_event_lists, iter_event_pages


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


def collect_switch_refs(project_path: str) -> list:
    """Collect all switch references from event command lists and page conditions.

    Covers three sources:
    1. Event command lists (code 121 = Control Switches, code 111 type 0 = Conditional Branch on Switch)
    2. Map event page conditions (switch1Valid/switch1Id, switch2Valid/switch2Id)
    3. CommonEvents trigger conditions (trigger 1/2 with switchId)

    Args:
        project_path: Path to RPG Maker project root directory.

    Returns:
        List of dicts with keys: switch_id, location, operation.
    """
    refs = []

    # Source 1: Event command lists
    for label, event_list in iter_event_lists(project_path):
        for cmd in event_list:
            code = cmd.get("code")
            params = cmd.get("parameters", [])

            if code == 121:
                # Control Switches: params[0]=startSwitchId, params[1]=endSwitchId, params[2]=value
                if len(params) >= 2:
                    start_id = params[0]
                    end_id = params[1]
                    for sw_id in range(start_id, end_id + 1):
                        refs.append({
                            "switch_id": sw_id,
                            "location": label,
                            "operation": "set",
                        })

            elif code == 111 and len(params) >= 2 and params[0] == 0:
                # Conditional Branch on Switch: params[0]=0, params[1]=switchId
                refs.append({
                    "switch_id": params[1],
                    "location": label,
                    "operation": "check",
                })

    # Source 2: Map event page conditions
    for label, event, page_idx, page in iter_event_pages(project_path):
        conditions = page.get("conditions", {})

        if conditions.get("switch1Valid"):
            refs.append({
                "switch_id": conditions["switch1Id"],
                "location": label,
                "operation": "page condition",
            })

        if conditions.get("switch2Valid"):
            refs.append({
                "switch_id": conditions["switch2Id"],
                "location": label,
                "operation": "page condition",
            })

    # Source 3: CommonEvent trigger conditions
    ce_path = os.path.join(project_path, "data", "CommonEvents.json")
    if os.path.exists(ce_path):
        with open(ce_path, encoding="utf-8") as f:
            common_events = json.load(f)
        for entry in common_events:
            if entry is None:
                continue
            # trigger 1 = Autorun (condition), trigger 2 = Parallel (condition)
            if entry.get("trigger") in (1, 2) and entry.get("switchId"):
                refs.append({
                    "switch_id": entry["switchId"],
                    "location": f"CommonEvent:{entry['id']}:{entry.get('name', '')}",
                    "operation": "trigger condition",
                })

    return refs


def main():
    parser = argparse.ArgumentParser(
        description="List all switch references across an RPG Maker MV/MZ project."
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
        system_data = load_system_data(args.project)
        refs = collect_switch_refs(args.project)
        # Sort by switch_id, then by location
        refs.sort(key=lambda r: (r["switch_id"], r["location"]))
        print("| Switch ID | Name | Used In | Operation |")
        print("|-----------|------|---------|-----------|")
        for ref in refs:
            name = get_switch_name(system_data, ref["switch_id"])
            print(
                f"| {ref['switch_id']} | {name} | {ref['location']} | {ref['operation']} |"
            )
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
