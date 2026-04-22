"""Generate a scaffolded event command list JSON for an RPG Maker MV/MZ pattern.

Outputs the 'list' JSON array to stdout. No file is modified (D-08/D-10).
Every pattern builder ends with a code-0 terminator (D-09).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))  # repo root

from scripts.lib.project_detect import detect_version


# ---------------------------------------------------------------------------
# Pattern builder functions
# ---------------------------------------------------------------------------


def build_chest_pattern(item_id: int, quantity: int = 1) -> list:
    """Build event command list for a chest pattern.

    Returns the 'list' array for an event page. Always ends with
    the code-0 terminator (D-09). Never modifies any file (D-08).

    Args:
        item_id: Database item ID to add.
        quantity: Number of items to add (default 1).
    """
    return [
        {"code": 126, "indent": 0, "parameters": [item_id, 0, 0, quantity]},
        # code 126: Change Items — params: [itemId, 0=add, 0=constant, quantity]
        {"code": 123, "indent": 0, "parameters": ["A", 0]},
        # code 123: Control Self Switch — "A" ON (string, NOT integer)
        {"code": 0, "indent": 0, "parameters": []},
        # List terminator — always last (D-09)
    ]


def build_shop_pattern(shop_items_str: str) -> list:
    """Build event command list for a shop pattern.

    Parses shop_items_str as "type:id,type:id,..." where type is
    0=item, 1=weapon, 2=armor. The first item becomes the code 302
    header entry; subsequent items become code 605 continuation entries.

    Args:
        shop_items_str: Comma-separated "type:id" pairs (e.g. "0:1,0:2,1:3").

    Returns:
        List of event command dicts ending with code-0 terminator.

    Raises:
        ValueError: If shop_items_str is empty or malformed.
    """
    # ASSUMED: 302 param layout [type, id, purchaseOnly, reserved] -- verify against RPG Maker editor export
    items = []
    for pair in shop_items_str.split(","):
        pair = pair.strip()
        if not pair:
            continue
        parts = pair.split(":")
        if len(parts) != 2:
            raise ValueError(
                f"Invalid shop item format '{pair}'. Expected 'type:id' (e.g. '0:1')."
            )
        item_type, item_id = int(parts[0]), int(parts[1])
        items.append((item_type, item_id))

    if not items:
        raise ValueError("--shop-items must contain at least one 'type:id' pair.")

    result = []
    # First item uses code 302 (Shop Processing header)
    # ASSUMED: 302 param layout [type, id, purchaseOnly, reserved] -- verify against RPG Maker editor export
    result.append(
        {
            "code": 302,
            "indent": 0,
            "parameters": [items[0][0], items[0][1], 0, 0],
        }
    )
    # Additional items use code 605 (Shop Goods continuation)
    for item_type, item_id in items[1:]:
        result.append(
            {
                "code": 605,
                "indent": 0,
                "parameters": [item_type, item_id, 0, 0],
            }
        )
    result.append({"code": 0, "indent": 0, "parameters": []})
    return result


def build_inn_pattern(inn_cost: int = 50) -> list:
    """Build event command list for an inn rest pattern.

    Includes dialog prompt, Yes/No choice, gold removal, HP/MP heal,
    SE play, and a polite refusal message. Uses verified fixture structures
    (RESEARCH.md Pattern 6).

    Args:
        inn_cost: Gold cost to rest (default 50).
    """
    return [
        # Opening dialog
        {"code": 101, "indent": 0, "parameters": ["", 0, 0, 2]},
        {"code": 401, "indent": 0, "parameters": [f"Rest here? ({inn_cost} gold)"]},
        # Yes/No choice
        {"code": 102, "indent": 0, "parameters": [["Yes", "No"], 1, 0, 2, 0]},
        # When [Yes] branch
        {"code": 402, "indent": 1, "parameters": [0, "Yes"]},
        # ASSUMED: params[0]=1 means REMOVE gold -- fixture evidence supports this
        # (CommonEvents.json event 1 shows [1, 0, 50] in the payment branch)
        {"code": 125, "indent": 2, "parameters": [1, 0, inn_cost]},
        # code 311: Change HP -- actorType=0 (entire party), operation=0 (heal all)
        {"code": 311, "indent": 2, "parameters": [0, 0]},
        # code 312: Change MP -- actorType=0 (entire party), operation=0 (heal all)
        {"code": 312, "indent": 2, "parameters": [0, 0]},
        # Play recovery SE
        {
            "code": 250,
            "indent": 2,
            "parameters": [{"name": "Recovery", "volume": 90, "pitch": 100, "pan": 0}],
        },
        # When [No] branch
        {"code": 402, "indent": 1, "parameters": [1, "No"]},
        {"code": 101, "indent": 2, "parameters": ["", 0, 0, 2]},
        {"code": 401, "indent": 2, "parameters": ["Come back anytime."]},
        # End Choice
        {"code": 404, "indent": 1, "parameters": []},
        # List terminator (D-09)
        {"code": 0, "indent": 0, "parameters": []},
    ]


def build_door_pattern(switch_id: int, item_id: int | None = None) -> list:
    """Build event command list for a door/lock pattern.

    Uses a self-switch A conditional: if self-switch A is ON, the door
    is already unlocked and transfers the player. Otherwise, shows a
    locked message (or uses an item if item_id is provided).

    Args:
        switch_id: Unused in the door pattern itself (kept for API consistency).
                   The door uses self-switch A, not a global switch.
        item_id: Optional item ID to consume when unlocking the door.
                 If None, shows a "locked" message only.
    """
    result = []
    # Conditional branch on self-switch A == ON
    # code 111, params[0]=2 = self-switch type, params[1]="A", params[2]=0=ON
    result.append({"code": 111, "indent": 0, "parameters": [2, "A", 0]})
    # If self-switch A is ON: door is unlocked, transfer player
    # code 201: Transfer Player -- params: [designationType=0(direct), mapId=1, x=0, y=0, direction=2, fadeType=0]
    result.append({"code": 201, "indent": 1, "parameters": [0, 1, 0, 0, 2, 0]})
    # Else branch (code 411)
    result.append({"code": 411, "indent": 0, "parameters": []})
    if item_id is not None:
        # Use item to unlock: show message, remove item, set self-switch A ON
        result.append({"code": 101, "indent": 1, "parameters": ["", 0, 0, 2]})
        result.append({"code": 401, "indent": 1, "parameters": ["Used the key!"]})
        result.append(
            {
                "code": 126,
                "indent": 1,
                "parameters": [item_id, 1, 0, 1],
            }
        )
        # code 123: Control Self Switch A = ON
        result.append({"code": 123, "indent": 1, "parameters": ["A", 0]})
    else:
        # No item: just show a locked message
        result.append({"code": 101, "indent": 1, "parameters": ["", 0, 0, 2]})
        result.append({"code": 401, "indent": 1, "parameters": ["This door is locked."]})
    # End of Conditional Branch (code 412 — NOT 413 which is Loop End)
    result.append({"code": 412, "indent": 0, "parameters": []})
    # List terminator (D-09)
    result.append({"code": 0, "indent": 0, "parameters": []})
    return result


def build_cutscene_pattern(switch_id: int, version: str) -> list:
    """Build event command list for a switch-gated cutscene pattern.

    If the switch is already ON, skips the cutscene with a short message
    and exits event processing (code 115). Otherwise, plays the cutscene,
    sets the switch ON, and shows a confirmation.

    Args:
        switch_id: Global switch ID that gates this cutscene (already-seen flag).
        version: "MV" or "MZ" (used for future plugin command needs; currently unused).
    """
    return [
        # Conditional branch: if switch_id == ON, cutscene already seen
        # code 111, params[0]=0 = switch type, params[1]=switch_id, params[2]=0=ON
        {"code": 111, "indent": 0, "parameters": [0, switch_id, 0]},
        # Already seen: show brief message then exit
        {"code": 101, "indent": 1, "parameters": ["", 0, 0, 2]},
        {"code": 401, "indent": 1, "parameters": ["(You've already seen this.)"]},
        # code 115: Exit Event Processing
        {"code": 115, "indent": 1, "parameters": []},
        # Else branch: play the cutscene
        {"code": 411, "indent": 0, "parameters": []},
        # Cutscene dialog sequence
        {"code": 101, "indent": 1, "parameters": ["", 0, 0, 2]},
        {"code": 401, "indent": 1, "parameters": ["[Cutscene dialog line 1]"]},
        {"code": 401, "indent": 1, "parameters": ["[Cutscene dialog line 2]"]},
        # code 121: Control Switches — set switch_id ON
        # params: [startSwitchId, endSwitchId, value(0=ON,1=OFF)]
        {"code": 121, "indent": 1, "parameters": [switch_id, switch_id, 0]},
        # Confirmation
        {"code": 101, "indent": 1, "parameters": ["", 0, 0, 2]},
        {"code": 401, "indent": 1, "parameters": ["[Cutscene complete.]"]},
        # End of Conditional Branch (code 412 — NOT 413 which is Loop End)
        {"code": 412, "indent": 0, "parameters": []},
        # List terminator (D-09)
        {"code": 0, "indent": 0, "parameters": []},
    ]


def build_wanderer_pattern(move_type: str = "random", move_steps: int = 4) -> list:
    """Build event command list for a wanderer NPC movement pattern.

    Uses code 205 (Set Movement Route) targeting this event (params[0]=0),
    with a repeating random movement route.

    Args:
        move_type: Movement behavior — "random", "toward", or "away".
        move_steps: Number of movement sub-commands to generate (default 4).

    Move sub-command codes:
        # ASSUMED: move sub-commands 9=random, 10=toward, 11=away -- from training data, verify against rpg_objects.js
    """
    # ASSUMED: move sub-commands 9=random, 10=toward, 11=away -- from training data, verify against rpg_objects.js
    move_code_map = {
        "random": 9,
        "toward": 10,
        "away": 11,
    }
    sub_code = move_code_map[move_type]

    # Build move route sub-command list: N sub-commands + code-0 terminator
    route_list = [{"code": sub_code, "parameters": []} for _ in range(move_steps)]
    route_list.append({"code": 0, "parameters": []})

    return [
        {
            "code": 205,
            "indent": 0,
            "parameters": [
                0,  # params[0]=0: this event (NOT -1 which targets the player)
                {
                    "list": route_list,
                    "repeat": True,
                    "skippable": True,
                    "wait": False,
                },
            ],
        },
        # List terminator (D-09)
        {"code": 0, "indent": 0, "parameters": []},
    ]


def build_plugin_command(version: str, plugin_name: str, command_str: str) -> list:
    """Build a plugin command event entry, version-aware.

    MV (code 356): single string parameter "PluginName command args"
    MZ (code 357): structured parameters [pluginName, commandName, "", {}]

    Per D-11: MV uses code 356, MZ uses code 357.

    Args:
        version: "MV" or "MZ" from detect_version().
        plugin_name: Name of the plugin (e.g. "YEP_BattleEngineCore").
        command_str: Command string for MV (e.g. "EnableBossMode") or
                     command name for MZ.

    Returns:
        List with one plugin command entry and a code-0 terminator.
    """
    if version == "MV":
        return [
            {
                "code": 356,
                "indent": 0,
                "parameters": [f"{plugin_name} {command_str}"],
            },
            {"code": 0, "indent": 0, "parameters": []},
        ]
    else:  # MZ
        return [
            {
                "code": 357,
                "indent": 0,
                "parameters": [plugin_name, command_str, "", {}],
            },
            {"code": 0, "indent": 0, "parameters": []},
        ]


# ---------------------------------------------------------------------------
# Argument validation helpers
# ---------------------------------------------------------------------------


def _require_arg(args: argparse.Namespace, flag: str, pattern: str) -> None:
    """Raise SystemExit if a required flag for the given pattern is missing."""
    value = getattr(args, flag.replace("-", "_"), None)
    if value is None:
        print(
            f"Error: --{flag} is required for --pattern {pattern}",
            file=sys.stderr,
        )
        sys.exit(1)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    """Entry point for the scaffold_event CLI."""
    parser = argparse.ArgumentParser(
        description=(
            "Generate a scaffolded event command list JSON for an RPG Maker "
            "MV/MZ pattern. Prints the 'list' JSON array to stdout. "
            "No file is modified (D-08/D-10)."
        )
    )
    parser.add_argument(
        "--project",
        required=True,
        help="Path to RPG Maker project root directory (used for MV/MZ detection).",
    )
    parser.add_argument(
        "--pattern",
        required=True,
        choices=["chest", "shop", "inn", "door", "cutscene", "wanderer", "plugin-command"],
        help="Event pattern to scaffold.",
    )
    # Pattern-specific flags
    parser.add_argument(
        "--item-id",
        type=int,
        dest="item_id",
        help="Item database ID. Required for: chest, door (optional for door).",
    )
    parser.add_argument(
        "--quantity",
        type=int,
        default=1,
        help="Item quantity for chest pattern (default: 1).",
    )
    parser.add_argument(
        "--switch-id",
        type=int,
        dest="switch_id",
        help="Global switch ID. Required for: cutscene, door.",
    )
    parser.add_argument(
        "--shop-items",
        dest="shop_items",
        help=(
            'Comma-separated "type:id" pairs for shop items '
            "(e.g. \"0:1,0:2,1:3\" where type 0=item, 1=weapon, 2=armor). "
            "Required for: shop."
        ),
    )
    parser.add_argument(
        "--inn-cost",
        type=int,
        dest="inn_cost",
        default=50,
        help="Gold cost to rest at the inn (default: 50).",
    )
    parser.add_argument(
        "--move-type",
        dest="move_type",
        default="random",
        choices=["random", "toward", "away"],
        help="Wanderer movement behavior (default: random).",
    )
    parser.add_argument(
        "--move-steps",
        type=int,
        dest="move_steps",
        default=4,
        help="Number of movement sub-commands for wanderer (default: 4).",
    )
    parser.add_argument(
        "--plugin-name",
        dest="plugin_name",
        help="Plugin name for plugin-command pattern. Required for: plugin-command.",
    )
    parser.add_argument(
        "--plugin-command",
        dest="plugin_command",
        help=(
            "Plugin command string (MV) or command name (MZ). "
            "Required for: plugin-command."
        ),
    )

    args = parser.parse_args()

    # Validate project path
    if not os.path.isdir(args.project):
        print(
            f"Error: Project path does not exist: {args.project}",
            file=sys.stderr,
        )
        sys.exit(1)

    # Validate pattern-specific required args
    if args.pattern == "chest":
        _require_arg(args, "item-id", "chest")
    elif args.pattern == "shop":
        _require_arg(args, "shop-items", "shop")
    elif args.pattern == "door":
        _require_arg(args, "switch-id", "door")
    elif args.pattern == "cutscene":
        _require_arg(args, "switch-id", "cutscene")
    elif args.pattern == "plugin-command":
        _require_arg(args, "plugin-name", "plugin-command")
        _require_arg(args, "plugin-command", "plugin-command")

    try:
        version = detect_version(args.project)

        if args.pattern == "chest":
            result = build_chest_pattern(args.item_id, args.quantity)
        elif args.pattern == "shop":
            result = build_shop_pattern(args.shop_items)
        elif args.pattern == "inn":
            result = build_inn_pattern(args.inn_cost)
        elif args.pattern == "door":
            result = build_door_pattern(args.switch_id, args.item_id)
        elif args.pattern == "cutscene":
            result = build_cutscene_pattern(args.switch_id, version)
        elif args.pattern == "wanderer":
            result = build_wanderer_pattern(args.move_type, args.move_steps)
        elif args.pattern == "plugin-command":
            result = build_plugin_command(version, args.plugin_name, args.plugin_command)
        else:
            # Should be unreachable due to argparse choices validation
            print(f"Error: Unknown pattern '{args.pattern}'", file=sys.stderr)
            sys.exit(1)

        print(json.dumps(result, ensure_ascii=False, indent=2))

    except (ValueError, FileNotFoundError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
