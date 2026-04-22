"""Safely append a new skill entry to an RPG Maker MV/MZ Skills.json file.

Creates a new skill with the specified name, damage formula, MP cost, and
optional note field. The new entry is appended at the next available array
index with the correct positional ID. Dry-run is the default.

Usage:
    python add_skill.py --project <path> --name <name> [options] [--apply]

Options:
    --name          Skill name (required)
    --description   Skill description (default: "")
    --formula       Damage formula string (default: "0")
    --mp-cost       MP cost (default: 0)
    --note          Note field content, written verbatim (default: "")

Exit codes:
    0 -- success (skill added or dry-run preview shown)
    1 -- error (file not found, validation failure)
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[3]))  # repo root

from scripts.lib.safe_write import (
    add_argparse_write_args,
    load_json_preserving_format,
    safe_write,
)


def build_skill_entry(new_id: int, args: argparse.Namespace) -> dict:
    """Build a complete RMMV skill entry dict from CLI arguments."""
    return {
        "id": new_id,
        "name": args.name,
        "iconIndex": 0,
        "description": args.description or "",
        "stypeId": 1,
        "scope": 1,
        "occasion": 1,
        "speed": 0,
        "successRate": 100,
        "repeats": 1,
        "tpGain": 0,
        "hitType": 1,
        "animationId": 0,
        "damage": {
            "type": 1,
            "elementId": 0,
            "formula": args.formula or "0",
            "variance": 20,
            "critical": False,
        },
        "effects": [],
        "mpCost": args.mp_cost or 0,
        "tpCost": 0,
        "message1": "",
        "message2": "",
        "note": args.note or "",
    }


def add_skill(project_path: str, args: argparse.Namespace) -> None:
    """Append a new skill to Skills.json using safe_write."""
    skills_path = os.path.join(project_path, "data", "Skills.json")
    if not os.path.exists(skills_path):
        raise FileNotFoundError(f"Skills.json not found at {skills_path}")

    data, indent = load_json_preserving_format(skills_path)
    original_data = data[:]
    new_id = len(data)
    new_entry = build_skill_entry(new_id, args)
    modified = data + [new_entry]

    safe_write(
        filepath=skills_path,
        original_data=original_data,
        modified_data=modified,
        apply=args.apply,
        indent=indent,
        label="Skills",
        changes_description=f"Add skill '{args.name}' as id={new_id}",
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Safely append a new skill to Skills.json"
    )
    parser.add_argument(
        "--project", required=True,
        help="Path to RPG Maker project root directory",
    )
    parser.add_argument("--name", required=True, help="Skill name")
    parser.add_argument("--description", default="", help="Skill description")
    parser.add_argument(
        "--formula", default="0",
        help="Damage formula string (default: '0')",
    )
    parser.add_argument(
        "--mp-cost", type=int, default=0,
        help="MP cost (default: 0)",
    )
    parser.add_argument(
        "--note", default="",
        help="Note field content, written verbatim",
    )
    add_argparse_write_args(parser)
    args = parser.parse_args()

    if not os.path.isdir(args.project):
        print(f"Error: Project path does not exist: {args.project}", file=sys.stderr)
        sys.exit(1)

    try:
        add_skill(args.project, args)
    except (ValueError, FileNotFoundError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
