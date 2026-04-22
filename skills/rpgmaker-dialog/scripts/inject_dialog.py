"""inject_dialog.py — Inject a dialog block into a CommonEvent or Map event.

Injects plain text as valid 101/401 event command sequences into a CommonEvent
or Map event list. All writes go through safe_write.py: .bak backup, dry-run
by default, ID-integrity validation.

Usage:
  # Dry-run (no file modification):
  python inject_dialog.py --project /path/to/project --target common-event:1 \
      --lines "Line one." "Line two."

  # Apply (creates .bak backup, writes file):
  python inject_dialog.py --project /path/to/project --target common-event:1 \
      --lines "Line one." "Line two." --apply

  # Map event target:
  python inject_dialog.py --project /path/to/project --target map:1:event:2 \
      --lines "Hello traveler!" --apply

Notes:
  - Injection always targets the first page of map events.
  - Dialog is injected at indent=0 (top-level). Nested injection inside choice
    branches is out of scope for Phase 2.
  - --face and --face-index set the face sprite for the 101 command header.
"""
from __future__ import annotations

import argparse
import copy
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[3]))  # repo root
from scripts.lib.safe_write import (
    add_argparse_write_args,
    load_json_preserving_format,
    safe_write,
)


# ---------------------------------------------------------------------------
# Target resolution
# ---------------------------------------------------------------------------


def resolve_target(project_path: str, target: str) -> tuple[str, int, bool]:
    """Parse the --target specifier and return (filepath, event_id, is_common_event).

    Supported formats:
      common-event:N   → CommonEvents.json, event id N
      map:M:event:E    → MapMMM.json, event id E (e.g. map:1:event:2 → Map001.json)

    Args:
        project_path: Path to RPG Maker project root.
        target:       Target specifier string.

    Returns:
        Tuple of (absolute filepath, event_id integer, is_common_event boolean).

    Raises:
        ValueError: If target format is unknown.
    """
    if target.startswith("common-event:"):
        parts = target.split(":")
        if len(parts) != 2:
            raise ValueError(
                f"Invalid common-event target '{target}'. "
                "Expected format: 'common-event:N'"
            )
        try:
            event_id = int(parts[1])
        except ValueError:
            raise ValueError(
                f"Invalid event id '{parts[1]}' in target '{target}'. Must be an integer."
            )
        filepath = os.path.join(project_path, "data", "CommonEvents.json")
        return filepath, event_id, True

    if target.startswith("map:"):
        parts = target.split(":")
        # Expected: map:M:event:E  (4 parts)
        if len(parts) != 4 or parts[2] != "event":
            raise ValueError(
                f"Invalid map target '{target}'. "
                "Expected format: 'map:M:event:E' (e.g. 'map:1:event:2')"
            )
        try:
            map_id = int(parts[1])
            event_id = int(parts[3])
        except ValueError:
            raise ValueError(
                f"Invalid numeric values in map target '{target}'. "
                "Map id and event id must be integers."
            )
        map_filename = f"Map{map_id:03d}.json"
        filepath = os.path.join(project_path, "data", map_filename)
        return filepath, event_id, False

    raise ValueError(
        f"Unknown target format '{target}'. "
        "Use 'common-event:N' or 'map:M:event:E'."
    )


# ---------------------------------------------------------------------------
# Event lookup
# ---------------------------------------------------------------------------


def get_common_event(data: list, event_id: int) -> dict:
    """Return the CommonEvent dict at the given id from the positional array.

    Args:
        data:     Parsed CommonEvents.json list (index 0 is null).
        event_id: The id / array index of the target event.

    Returns:
        The event dict.

    Raises:
        ValueError: If id is out of range or the slot is null.
    """
    if event_id < 1 or event_id >= len(data):
        raise ValueError(
            f"CommonEvent id {event_id} is out of range "
            f"(valid ids: 1–{len(data) - 1})."
        )
    event = data[event_id]
    if event is None:
        raise ValueError(f"CommonEvent id {event_id} is null (slot is empty).")
    return event


def get_map_event(events: list, event_id: int) -> dict:
    """Return the map event with the given id by scanning the events list.

    Map events are NEVER accessed by direct array index — the events list may
    have gaps and the id field is the authoritative identifier (Pitfall 4).

    Args:
        events:   The map's events list (may contain nulls).
        event_id: The id of the target event.

    Returns:
        The event dict.

    Raises:
        ValueError: If no event with the given id is found.
    """
    for ev in events:
        if ev is not None and ev.get("id") == event_id:
            return ev
    raise ValueError(f"No map event with id {event_id}.")


# ---------------------------------------------------------------------------
# Dialog block construction
# ---------------------------------------------------------------------------


def build_dialog_block(
    lines: list[str],
    face: str = "",
    face_index: int = 0,
    indent: int = 0,
) -> list[dict]:
    """Build a dialog command block: one code 101 header + one code 401 per line.

    Args:
        lines:      The dialog lines to inject (list of strings).
        face:       Face sprite filename for the 101 command (default: empty = no face).
        face_index: Face index within the sprite sheet (default: 0).
        indent:     Command indent level (default: 0 for top-level injection).

    Returns:
        List of command dicts ready to insert into an event list.
    """
    # Code 101 parameters: [faceName, faceIndex, background, windowPosition]
    # background=0 (window), windowPosition=2 (bottom) — sensible defaults
    block: list[dict] = [
        {"code": 101, "indent": indent, "parameters": [face, face_index, 0, 2]}
    ]
    for line in lines:
        block.append({"code": 401, "indent": indent, "parameters": [line]})
    return block


# ---------------------------------------------------------------------------
# Injection
# ---------------------------------------------------------------------------


def inject_into_event_list(event_list: list, new_block: list) -> None:
    """Insert new_block before the code-0 terminator in event_list.

    Mutates event_list in place. The code-0 terminator is always the last
    command — inserting after it would corrupt the event structure (Pitfall 2).

    Args:
        event_list: The command list from an event or page dict.
        new_block:  The commands to insert (built by build_dialog_block).
    """
    terminator_idx = next(
        (i for i, cmd in enumerate(event_list) if cmd["code"] == 0),
        len(event_list),
    )
    for offset, cmd in enumerate(new_block):
        event_list.insert(terminator_idx + offset, cmd)


def inject(
    project_path: str,
    target: str,
    lines: list[str],
    face: str = "",
    face_index: int = 0,
    apply: bool = False,
) -> None:
    """Load the target file, inject the dialog block, and write via safe_write.

    Args:
        project_path: Path to RPG Maker project root.
        target:       Target specifier ('common-event:N' or 'map:M:event:E').
        lines:        Dialog lines to inject.
        face:         Face sprite filename for the 101 command header.
        face_index:   Face sprite index for the 101 command header.
        apply:        If True, create .bak and write the file. Default is dry-run.

    Raises:
        ValueError: On any target format error, out-of-range id, or safe_write
                    integrity violation.
        FileNotFoundError: If the target data file does not exist.
    """
    filepath, event_id, is_common_event = resolve_target(project_path, target)

    if not os.path.exists(filepath):
        raise ValueError(f"Data file not found: {filepath}")

    data, detected_indent = load_json_preserving_format(filepath)
    original_data = copy.deepcopy(data)

    if is_common_event:
        event = get_common_event(data, event_id)
        dialog_block = build_dialog_block(lines, face=face, face_index=face_index, indent=0)
        inject_into_event_list(event["list"], dialog_block)
        label = "CommonEvents"
    else:
        # Map files: events is a list, not a positional database array
        events = data.get("events", [])
        event = get_map_event(events, event_id)
        page = event["pages"][0]
        dialog_block = build_dialog_block(lines, face=face, face_index=face_index, indent=0)
        inject_into_event_list(page["list"], dialog_block)
        # Map files are NOT positional arrays at the top level — pass empty label
        # so safe_write skips validate_positional_array for the map root object
        label = ""

    safe_write(
        filepath=filepath,
        original_data=original_data,
        modified_data=data,
        apply=apply,
        indent=detected_indent,
        label=label,
        changes_description=f"Injected {len(lines)} dialog line(s) into {target}",
    )


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def main() -> None:
    """CLI entry point for inject_dialog.py."""
    parser = argparse.ArgumentParser(
        description=(
            "Inject a dialog block into a CommonEvent or Map event. "
            "Dry-run by default — use --apply to write changes to disk."
        )
    )
    parser.add_argument(
        "--project",
        required=True,
        help="Path to RPG Maker project root directory.",
    )
    parser.add_argument(
        "--target",
        required=True,
        help=(
            "Target specifier. Formats: "
            "'common-event:N' (e.g. 'common-event:1') or "
            "'map:M:event:E' (e.g. 'map:1:event:2'). "
            "Map targets inject into the first page of the event."
        ),
    )
    parser.add_argument(
        "--lines",
        nargs="+",
        required=True,
        metavar="LINE",
        help=(
            "Dialog lines to inject. Each argument becomes one code 401 entry. "
            "RPG Maker text codes (e.g. \\\\N[1], \\\\I[3]) are embedded verbatim."
        ),
    )
    parser.add_argument(
        "--face",
        default="",
        help="Face sprite filename for the dialog header (code 101). Default: no face.",
    )
    parser.add_argument(
        "--face-index",
        type=int,
        default=0,
        dest="face_index",
        help="Face sprite index within the sheet (0–7). Default: 0.",
    )
    add_argparse_write_args(parser)  # adds --apply flag; dry-run is the default

    args = parser.parse_args()

    try:
        inject(
            project_path=args.project,
            target=args.target,
            lines=args.lines,
            face=args.face,
            face_index=args.face_index,
            apply=args.apply,
        )
    except (ValueError, FileNotFoundError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
