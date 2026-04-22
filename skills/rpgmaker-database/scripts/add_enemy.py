"""Safely append a new enemy entry to an RPG Maker MV/MZ Enemies.json file.

Creates a new enemy with the specified name, stats, and optional note field.
The new entry is appended at the next available array index with the correct
positional ID. Dry-run is the default.

Usage:
    python add_enemy.py --project <path> --name <name> [options] [--apply]

Options:
    --name          Enemy name (required)
    --battler-name  Battler sprite name (default: "")
    --hp            Max HP (default: 100)
    --atk           Attack stat (default: 10)
    --def           Defense stat (default: 10)
    --mat           Magic attack (default: 10)
    --mdf           Magic defense (default: 10)
    --agi           Agility (default: 10)
    --luk           Luck (default: 10)
    --exp           Experience points (default: 10)
    --gold          Gold drop (default: 0)
    --note          Note field content, written verbatim (default: "")

Exit codes:
    0 -- success
    1 -- error
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


def build_enemy_entry(new_id: int, args: argparse.Namespace) -> dict:
    """Build a complete RMMV enemy entry dict from CLI arguments."""
    return {
        "id": new_id,
        "name": args.name,
        "battlerName": args.battler_name or "",
        "battlerHue": 0,
        "params": [
            args.hp,      # 0: Max HP
            0,            # 1: Max MP (not exposed as CLI arg, default 0)
            args.atk,     # 2: ATK
            args.def_stat,  # 3: DEF
            args.mat,     # 4: MAT
            args.mdf,     # 5: MDF
            args.agi,     # 6: AGI
            args.luk,     # 7: LUK
        ],
        "exp": args.exp,
        "gold": args.gold,
        "dropItems": [],
        "actions": [
            {
                "conditionParam1": 0,
                "conditionParam2": 0,
                "conditionType": 0,
                "rating": 5,
                "skillId": 1,
            }
        ],
        "traits": [],
        "note": args.note or "",
    }


def add_enemy(project_path: str, args: argparse.Namespace) -> None:
    """Append a new enemy to Enemies.json using safe_write."""
    enemies_path = os.path.join(project_path, "data", "Enemies.json")
    if not os.path.exists(enemies_path):
        raise FileNotFoundError(f"Enemies.json not found at {enemies_path}")

    data, indent = load_json_preserving_format(enemies_path)
    original_data = data[:]
    new_id = len(data)
    new_entry = build_enemy_entry(new_id, args)
    modified = data + [new_entry]

    safe_write(
        filepath=enemies_path,
        original_data=original_data,
        modified_data=modified,
        apply=args.apply,
        indent=indent,
        label="Enemies",
        changes_description=f"Add enemy '{args.name}' as id={new_id}",
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Safely append a new enemy to Enemies.json"
    )
    parser.add_argument(
        "--project", required=True,
        help="Path to RPG Maker project root directory",
    )
    parser.add_argument("--name", required=True, help="Enemy name")
    parser.add_argument(
        "--battler-name", default="",
        help="Battler sprite name (default: '')",
    )
    parser.add_argument("--hp", type=int, default=100, help="Max HP (default: 100)")
    parser.add_argument("--atk", type=int, default=10, help="Attack stat (default: 10)")
    parser.add_argument(
        "--def", type=int, default=10, dest="def_stat",
        help="Defense stat (default: 10)",
    )
    parser.add_argument("--mat", type=int, default=10, help="Magic attack (default: 10)")
    parser.add_argument("--mdf", type=int, default=10, help="Magic defense (default: 10)")
    parser.add_argument("--agi", type=int, default=10, help="Agility (default: 10)")
    parser.add_argument("--luk", type=int, default=10, help="Luck (default: 10)")
    parser.add_argument("--exp", type=int, default=10, help="Experience points (default: 10)")
    parser.add_argument("--gold", type=int, default=0, help="Gold drop (default: 0)")
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
        add_enemy(args.project, args)
    except (ValueError, FileNotFoundError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
