"""Extract all dialog lines spoken by a named NPC across RPG Maker MV/MZ project files.

Searches CommonEvents.json and all Map*.json files. Uses actor face lookup as the
primary strategy (D-07) and event name match as fallback (D-08). Preserves text
codes verbatim (\\N[], \\V[], \\C[], \\I[]).

Usage:
    python extract_npc_lines.py --project <path> --npc <name>
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[3]))  # repo root

import argparse
import glob
import json
import os


def build_actor_face_lookup(project_path: str) -> dict:
    """Build a face-key to actor-name lookup from Actors.json.

    Args:
        project_path: Path to RPG Maker project root.

    Returns:
        dict mapping (faceName, faceIndex) tuples to actor name strings.
    """
    actors_path = os.path.join(project_path, "data", "Actors.json")
    if not os.path.exists(actors_path):
        print(f"Error: Actors.json not found at {actors_path}", file=sys.stderr)
        sys.exit(1)

    with open(actors_path, encoding="utf-8") as f:
        actors = json.load(f)

    lookup: dict = {}
    for entry in actors:
        if entry is None:
            continue
        face_name = entry.get("faceName", "")
        face_index = entry.get("faceIndex", 0)
        actor_name = entry.get("name", "")
        if actor_name:
            lookup[(face_name, face_index)] = actor_name
    return lookup


def find_npc_face_keys(lookup: dict, npc_name: str) -> set:
    """Return all (faceName, faceIndex) tuples that match the given NPC name.

    Matching is case-insensitive.

    Args:
        lookup: dict from build_actor_face_lookup.
        npc_name: Name to search for (e.g. "Hero", "Mage").

    Returns:
        Set of (faceName, faceIndex) tuples for actors whose name matches npc_name.
    """
    npc_lower = npc_name.lower()
    return {key for key, name in lookup.items() if name.lower() == npc_lower}


def walk_common_events(project_path: str):
    """Yield (source_label, command_list) pairs from CommonEvents.json.

    Args:
        project_path: Path to RPG Maker project root.

    Yields:
        Tuples of (source_label: str, command_list: list).
    """
    ce_path = os.path.join(project_path, "data", "CommonEvents.json")
    if not os.path.exists(ce_path):
        return

    with open(ce_path, encoding="utf-8") as f:
        common_events = json.load(f)

    for entry in common_events:
        if entry is None:
            continue
        label = f"CommonEvent:{entry['id']}:{entry['name']}"
        yield label, entry.get("list", [])


def walk_map_events(project_path: str):
    """Yield (source_label, command_list) pairs from all Map*.json files.

    Never hardcodes map filenames — uses glob for discovery.

    Args:
        project_path: Path to RPG Maker project root.

    Yields:
        Tuples of (source_label: str, command_list: list).
    """
    # MapInfos.json is NOT a map data file — only process Map[0-9]+.json
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


def extract_lines_for_npc(
    command_list: list,
    npc_face_keys: set,
    source_label: str,
    npc_search: str,
) -> list:
    """Extract dialog lines attributed to the NPC from a command list.

    Primary strategy: match code-101 face parameters against npc_face_keys.
    Fallback strategy (D-08): match NPC name against source_label (event name).

    Text codes (\\N[], \\V[], etc.) are preserved verbatim — never stripped.

    Args:
        command_list: List of RPG Maker event commands.
        npc_face_keys: Set of (faceName, faceIndex) tuples for the target NPC.
        source_label: Source identifier string (used for fallback name matching).
        npc_search: Lowercase NPC name for fallback event-name matching.

    Returns:
        List of extracted dialog text strings.
    """
    lines: list = []
    in_npc_block = False

    for cmd in command_list:
        code = cmd.get("code")
        params = cmd.get("parameters", [])

        if code == 101:
            # Start of a Show Text block — check if it's our NPC
            face_name = params[0] if len(params) > 0 else ""
            face_index = params[1] if len(params) > 1 else 0
            face_key = (face_name, face_index)

            # Primary: face lookup match
            if face_key in npc_face_keys and npc_face_keys:
                in_npc_block = True
            # Fallback (D-08): event name contains NPC name
            elif npc_search in source_label.lower():
                in_npc_block = True
            else:
                in_npc_block = False

        elif code == 401 and in_npc_block:
            # Show Text continuation — collect the line verbatim
            if params:
                lines.append(params[0])

        elif code != 401:
            # Any non-continuation command ends the current dialog block
            in_npc_block = False

    return lines


def main() -> None:
    """CLI entry point for NPC dialog extraction."""
    parser = argparse.ArgumentParser(
        description=(
            "Extract all dialog lines spoken by a named NPC across "
            "an RPG Maker MV/MZ project. Searches CommonEvents and all maps."
        )
    )
    parser.add_argument(
        "--project",
        required=True,
        help="Path to RPG Maker project root directory",
    )
    parser.add_argument(
        "--npc",
        required=True,
        help="NPC name to search for (e.g. 'Hero', 'Innkeeper')",
    )
    args = parser.parse_args()

    project_path = args.project
    npc_name = args.npc

    if not os.path.isdir(project_path):
        print(f"Error: Project path does not exist: {project_path}", file=sys.stderr)
        sys.exit(1)

    # Build face lookup and find keys for this NPC
    lookup = build_actor_face_lookup(project_path)
    npc_face_keys = find_npc_face_keys(lookup, npc_name)
    npc_lower = npc_name.lower()

    # Collect all dialog lines from common events and map events
    results: list = []

    for source_label, command_list in walk_common_events(project_path):
        lines = extract_lines_for_npc(command_list, npc_face_keys, source_label, npc_lower)
        for line in lines:
            results.append((source_label, line))

    for source_label, command_list in walk_map_events(project_path):
        lines = extract_lines_for_npc(command_list, npc_face_keys, source_label, npc_lower)
        for line in lines:
            results.append((source_label, line))

    if not results:
        print(f"No dialog found for NPC: {npc_name}", file=sys.stderr)
        sys.exit(1)

    for source_label, line in results:
        print(f"[{source_label}] {line}")


if __name__ == "__main__":
    main()
