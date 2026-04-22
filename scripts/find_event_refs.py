"""Find references to a specific switch, variable, or self-switch across an RPG Maker MV/MZ project.

Scans all event command lists and page conditions, printing matching references
to stdout. Exits 0 if any references found, 1 if none found.

Usage:
    python scripts/find_event_refs.py --project /path/to/project --switch-id 1
    python scripts/find_event_refs.py --project /path/to/project --var-id 2
    python scripts/find_event_refs.py --project /path/to/project --self-switch A
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

import argparse
import json
import os

from scripts.lib.event_traverse import iter_event_lists, iter_event_pages


def find_refs(
    project_path: str,
    switch_id: int | None = None,
    var_id: int | None = None,
    self_switch: str | None = None,
) -> bool:
    """Search all events for references to the specified switch, variable, or self-switch.

    Prints each reference as a line to stdout.

    Args:
        project_path: Path to RPG Maker project root directory.
        switch_id: Switch ID to search for (mutually exclusive with var_id/self_switch).
        var_id: Variable ID to search for (mutually exclusive with switch_id/self_switch).
        self_switch: Self-switch letter ("A"/"B"/"C"/"D") (mutually exclusive with switch_id/var_id).

    Returns:
        True if any references were found, False otherwise.
    """
    found = False

    # Source 1: Event command lists
    for label, event_list in iter_event_lists(project_path):
        for cmd in event_list:
            code = cmd.get("code")
            params = cmd.get("parameters", [])

            if switch_id is not None:
                if code == 121 and len(params) >= 2:
                    # Control Switches: params[0]=startSwitchId, params[1]=endSwitchId, params[2]=value
                    if params[0] <= switch_id <= params[1]:
                        value = params[2] if len(params) > 2 else 0
                        state = "ON" if value == 0 else "OFF"
                        print(
                            f"{label}: Control Switches — set switch {switch_id} to {state}"
                        )
                        found = True

                elif code == 111 and len(params) >= 2 and params[0] == 0:
                    # Conditional Branch on Switch: params[0]=0, params[1]=switchId, params[2]=value
                    if params[1] == switch_id:
                        value = params[2] if len(params) > 2 else 0
                        state = "ON" if value == 0 else "OFF"
                        print(
                            f"{label}: Conditional Branch — check switch {switch_id} == {state}"
                        )
                        found = True

            elif var_id is not None:
                if code == 122 and len(params) >= 2:
                    # Control Variables: params[0]=startVarId, params[1]=endVarId
                    if params[0] <= var_id <= params[1]:
                        print(
                            f"{label}: Control Variables — set variable {var_id}"
                        )
                        found = True

                elif code == 111 and len(params) >= 2 and params[0] == 1:
                    # Conditional Branch on Variable: params[0]=1, params[1]=varId
                    if params[1] == var_id:
                        print(
                            f"{label}: Conditional Branch — check variable {var_id}"
                        )
                        found = True

            elif self_switch is not None:
                if code == 123 and len(params) >= 1:
                    # Control Self Switch: params[0]="A"|"B"|"C"|"D", params[1]=value
                    if params[0] == self_switch:
                        value = params[1] if len(params) > 1 else 0
                        state = "ON" if value == 0 else "OFF"
                        print(
                            f"{label}: Control Self Switch — set {self_switch} to {state}"
                        )
                        found = True

                elif code == 111 and len(params) >= 2 and params[0] == 2:
                    # Conditional Branch on Self Switch: params[0]=2, params[1]="A"|"B"|"C"|"D"
                    if params[1] == self_switch:
                        value = params[2] if len(params) > 2 else 0
                        state = "ON" if value == 0 else "OFF"
                        print(
                            f"{label}: Conditional Branch — check self-switch {self_switch} == {state}"
                        )
                        found = True

    # Source 2: Page conditions
    for label, event, page_idx, page in iter_event_pages(project_path):
        conditions = page.get("conditions", {})

        if switch_id is not None:
            if conditions.get("switch1Valid") and conditions.get("switch1Id") == switch_id:
                print(f"{label}: Page condition — switch1Id = {switch_id}")
                found = True
            if conditions.get("switch2Valid") and conditions.get("switch2Id") == switch_id:
                print(f"{label}: Page condition — switch2Id = {switch_id}")
                found = True

        elif var_id is not None:
            if conditions.get("variableValid") and conditions.get("variableId") == var_id:
                threshold = conditions.get("variableValue", 0)
                print(
                    f"{label}: Page condition — variable {var_id} >= {threshold}"
                )
                found = True

        elif self_switch is not None:
            if (
                conditions.get("selfSwitchValid")
                and conditions.get("selfSwitchCh") == self_switch
            ):
                print(f"{label}: Page condition — selfSwitch {self_switch}")
                found = True

    return found


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Find references to a specific switch, variable, or self-switch "
            "across an RPG Maker MV/MZ project."
        )
    )
    parser.add_argument(
        "--project",
        required=True,
        help="Path to RPG Maker project root directory",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--switch-id", type=int, help="Switch ID to search for")
    group.add_argument("--var-id", type=int, help="Variable ID to search for")
    group.add_argument(
        "--self-switch",
        choices=["A", "B", "C", "D"],
        help="Self-switch letter to search for",
    )
    args = parser.parse_args()

    if not os.path.isdir(args.project):
        print(
            f"Error: Project path does not exist: {args.project}",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        found = find_refs(args.project, args.switch_id, args.var_id, args.self_switch)
        sys.exit(0 if found else 1)
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
