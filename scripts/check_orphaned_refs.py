"""Check for orphaned cross-file references in an RPG Maker MV/MZ project.

Validates that all database ID references in event commands and database
cross-references point to existing entries. Reports ERROR-level findings
for references that would crash or silently fail at runtime.

Implements D-03: full cross-file reference coverage.

Usage:
    python check_orphaned_refs.py --project <path>

Exit codes:
    0 -- no orphaned references found
    1 -- one or more orphaned references found (errors printed to stdout)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))  # repo root

import argparse
import json
import os
import re

from scripts.lib.event_traverse import iter_event_lists

# Regex patterns for actor and item text code references
ACTOR_REF_RE = re.compile(r"\\N\[(\d+)\]")
ITEM_REF_RE = re.compile(r"\\I\[(\d+)\]")


def load_valid_ids(filepath: str) -> set:
    """Load valid IDs from a JSON database array (skipping null at index 0).

    Args:
        filepath: Absolute path to the JSON database file.

    Returns:
        Set of integer IDs present in the database. Empty set if file not found.
    """
    with open(filepath, encoding="utf-8") as f:
        entries = json.load(f)
    ids: set = set()
    for entry in entries:
        if entry is None:
            continue
        ids.add(entry["id"])
    return ids


def load_system_switch_count(system_path: str) -> int:
    """Return the number of usable switch slots from System.json.

    Args:
        system_path: Absolute path to System.json.

    Returns:
        Maximum valid switch ID (length of switches array minus 1 for index 0).
    """
    with open(system_path, encoding="utf-8") as f:
        system = json.load(f)
    return len(system.get("switches", [])) - 1  # index 0 is unused


def load_system_variable_count(system_path: str) -> int:
    """Return the number of usable variable slots from System.json.

    Args:
        system_path: Absolute path to System.json.

    Returns:
        Maximum valid variable ID (length of variables array minus 1 for index 0).
    """
    with open(system_path, encoding="utf-8") as f:
        system = json.load(f)
    return len(system.get("variables", [])) - 1  # index 0 is unused


def check_event_commands(project_path: str, db_ids: dict) -> list:
    """Check event commands for orphaned database ID references.

    Implements D-03: event command reference checks for items, weapons, armors,
    actors, troops, skills, states, switches, and variables.

    Args:
        project_path: Path to RPG Maker project root directory.
        db_ids: Dict with keys: items, weapons, armors, actors, troops, skills,
                states (all sets of valid IDs), switches_max, variables_max (ints).

    Returns:
        List of error description strings (empty if no errors).
    """
    errors = []

    for label, event_list in iter_event_lists(project_path):
        for cmd in event_list:
            code = cmd.get("code")
            params = cmd.get("parameters", [])

            if code == 126:
                # Change Items: params[0] is item ID
                if params and isinstance(params[0], int):
                    item_id = params[0]
                    if item_id not in db_ids["items"]:
                        errors.append(
                            f"ERROR: {label}: code 126 (Change Items) references"
                            f" non-existent item ID {item_id}"
                        )

            elif code == 127:
                # Change Weapons: params[0] is weapon ID
                if params and isinstance(params[0], int):
                    weapon_id = params[0]
                    if weapon_id not in db_ids["weapons"]:
                        errors.append(
                            f"ERROR: {label}: code 127 (Change Weapons) references"
                            f" non-existent weapon ID {weapon_id}"
                        )

            elif code == 128:
                # Change Armors: params[0] is armor ID
                if params and isinstance(params[0], int):
                    armor_id = params[0]
                    if armor_id not in db_ids["armors"]:
                        errors.append(
                            f"ERROR: {label}: code 128 (Change Armors) references"
                            f" non-existent armor ID {armor_id}"
                        )

            elif code == 129:
                # Change Party Member: params[0] is actor ID
                if params and isinstance(params[0], int):
                    actor_id = params[0]
                    if actor_id not in db_ids["actors"]:
                        errors.append(
                            f"ERROR: {label}: code 129 (Change Party Member) references"
                            f" non-existent actor ID {actor_id}"
                        )

            elif code == 301:
                # Battle Processing: params[0] is troop designation type (0=direct, 1=variable)
                # Only validate when params[0] == 0 (direct troop ID), not variable reference
                if len(params) >= 2 and params[0] == 0 and isinstance(params[1], int):
                    troop_id = params[1]
                    if troop_id not in db_ids["troops"]:
                        errors.append(
                            f"ERROR: {label}: code 301 (Battle Processing) references"
                            f" non-existent troop ID {troop_id}"
                        )

            elif code == 302:
                # Shop Processing: params contains list of goods as [type, id, ...] pairs
                # In RMMV, shop goods are embedded in code 302 params directly as
                # a list of sub-arrays: params is a list of [type, id, price_type, price]
                # Each sub-array: params[n][0] = type (0=item,1=weapon,2=armor), params[n][1] = ID
                for good in params:
                    if not isinstance(good, list) or len(good) < 2:
                        continue
                    good_type = good[0]
                    good_id = good[1]
                    if not isinstance(good_id, int):
                        continue
                    if good_type == 0:
                        if good_id not in db_ids["items"]:
                            errors.append(
                                f"ERROR: {label}: code 302 (Shop Processing) references"
                                f" non-existent item ID {good_id}"
                            )
                    elif good_type == 1:
                        if good_id not in db_ids["weapons"]:
                            errors.append(
                                f"ERROR: {label}: code 302 (Shop Processing) references"
                                f" non-existent weapon ID {good_id}"
                            )
                    elif good_type == 2:
                        if good_id not in db_ids["armors"]:
                            errors.append(
                                f"ERROR: {label}: code 302 (Shop Processing) references"
                                f" non-existent armor ID {good_id}"
                            )

            elif code == 121:
                # Control Switches: params[0]=startSwitchId, params[1]=endSwitchId
                if len(params) >= 2:
                    start_id = params[0]
                    end_id = params[1]
                    for sw_id in range(start_id, end_id + 1):
                        if sw_id > db_ids["switches_max"]:
                            errors.append(
                                f"ERROR: {label}: code 121 (Control Switches) references"
                                f" switch ID {sw_id} beyond defined range"
                                f" (max={db_ids['switches_max']})"
                            )

            elif code == 122:
                # Control Variables: params[0]=startVarId, params[1]=endVarId
                if len(params) >= 2:
                    start_id = params[0]
                    end_id = params[1]
                    for var_id in range(start_id, end_id + 1):
                        if var_id > db_ids["variables_max"]:
                            errors.append(
                                f"ERROR: {label}: code 122 (Control Variables) references"
                                f" variable ID {var_id} beyond defined range"
                                f" (max={db_ids['variables_max']})"
                            )

            elif code == 313:
                # Change State: params[1] is state ID
                if len(params) >= 2 and isinstance(params[1], int):
                    state_id = params[1]
                    if state_id not in db_ids["states"]:
                        errors.append(
                            f"ERROR: {label}: code 313 (Change State) references"
                            f" non-existent state ID {state_id}"
                        )

            elif code == 318:
                # Change Skill: params[1] is skill ID
                if len(params) >= 2 and isinstance(params[1], int):
                    skill_id = params[1]
                    if skill_id not in db_ids["skills"]:
                        errors.append(
                            f"ERROR: {label}: code 318 (Change Skill) references"
                            f" non-existent skill ID {skill_id}"
                        )

            elif code == 401:
                # Show Text line: check \N[id] and \I[id] patterns
                if params:
                    text = params[0]
                    if not isinstance(text, str):
                        continue
                    for match in ACTOR_REF_RE.finditer(text):
                        ref_id = int(match.group(1))
                        if ref_id not in db_ids["actors"]:
                            errors.append(
                                f"ERROR: {label}: Show Text \\N[{ref_id}]"
                                f" references non-existent actor ID {ref_id}"
                            )
                    for match in ITEM_REF_RE.finditer(text):
                        ref_id = int(match.group(1))
                        if ref_id not in db_ids["items"]:
                            errors.append(
                                f"ERROR: {label}: Show Text \\I[{ref_id}]"
                                f" references non-existent item ID {ref_id}"
                            )

    return errors


def check_database_crossrefs(project_path: str, db_ids: dict) -> list:
    """Check database-to-database cross-references for orphaned entries.

    Implements D-03: database cross-reference checks including states coverage.

    Checks:
    - Enemies.json: enemy action skill IDs
    - Troops.json: troop member enemy IDs
    - Classes.json: class skill learning IDs
    - Actors.json: actor class IDs
    - Skills.json: skill effect state IDs (codes 21 and 22)

    Args:
        project_path: Path to RPG Maker project root directory.
        db_ids: Dict of valid ID sets for each database type.

    Returns:
        List of error description strings (empty if no errors).
    """
    errors = []
    data_dir = os.path.join(project_path, "data")

    # Enemies.json: each enemy's actions[n].skillId
    enemies_path = os.path.join(data_dir, "Enemies.json")
    if os.path.exists(enemies_path):
        with open(enemies_path, encoding="utf-8") as f:
            enemies = json.load(f)
        for enemy in enemies:
            if enemy is None:
                continue
            for action in enemy.get("actions", []):
                skill_id = action.get("skillId")
                if skill_id is not None and skill_id not in db_ids["skills"]:
                    errors.append(
                        f"ERROR: Enemies.json:{enemy['name']}(id={enemy['id']}):"
                        f" action references non-existent skill ID {skill_id}"
                    )

    # Troops.json: each troop's members[n].enemyId
    troops_path = os.path.join(data_dir, "Troops.json")
    if os.path.exists(troops_path):
        with open(troops_path, encoding="utf-8") as f:
            troops = json.load(f)
        for troop in troops:
            if troop is None:
                continue
            for member in troop.get("members", []):
                enemy_id = member.get("enemyId")
                if enemy_id is not None and enemy_id not in db_ids["enemies"]:
                    errors.append(
                        f"ERROR: Troops.json:{troop['name']}(id={troop['id']}):"
                        f" member references non-existent enemy ID {enemy_id}"
                    )

    # Classes.json: each class's learnings[n].skillId
    classes_path = os.path.join(data_dir, "Classes.json")
    if os.path.exists(classes_path):
        with open(classes_path, encoding="utf-8") as f:
            classes = json.load(f)
        for cls in classes:
            if cls is None:
                continue
            for learning in cls.get("learnings", []):
                skill_id = learning.get("skillId")
                if skill_id is not None and skill_id not in db_ids["skills"]:
                    errors.append(
                        f"ERROR: Classes.json:{cls['name']}(id={cls['id']}):"
                        f" learning references non-existent skill ID {skill_id}"
                    )

    # Actors.json: each actor's classId
    actors_path = os.path.join(data_dir, "Actors.json")
    if os.path.exists(actors_path):
        with open(actors_path, encoding="utf-8") as f:
            actors = json.load(f)
        for actor in actors:
            if actor is None:
                continue
            class_id = actor.get("classId")
            if class_id is not None and class_id not in db_ids["classes"]:
                errors.append(
                    f"ERROR: Actors.json:{actor['name']}(id={actor['id']}):"
                    f" classId {class_id} references non-existent class"
                )

    # Skills.json: skill effects where code==21 (Add State) or code==22 (Remove State)
    # dataId 0 means "normal attack state" -- skip it
    skills_path = os.path.join(data_dir, "Skills.json")
    if os.path.exists(skills_path):
        with open(skills_path, encoding="utf-8") as f:
            skills = json.load(f)
        for skill in skills:
            if skill is None:
                continue
            for effect in skill.get("effects", []):
                effect_code = effect.get("code")
                if effect_code in (21, 22):
                    data_id = effect.get("dataId", 0)
                    if data_id == 0:
                        continue  # dataId 0 = normal attack state, skip
                    if data_id not in db_ids["states"]:
                        action_label = "Add State" if effect_code == 21 else "Remove State"
                        errors.append(
                            f"ERROR: Skills.json:{skill['name']}(id={skill['id']}):"
                            f" effect {action_label} references non-existent"
                            f" state ID {data_id}"
                        )

    return errors


def validate_project(project_path: str) -> int:
    """Validate all cross-file references in the RPG Maker project.

    Checks event commands and database entries for orphaned ID references.

    Args:
        project_path: Path to RPG Maker project root directory.

    Returns:
        0 if no errors, 1 if any orphaned references found.
    """
    data_dir = os.path.join(project_path, "data")

    # Build db_ids dict by loading valid IDs from each database file
    db_file_map = {
        "actors": "Actors.json",
        "items": "Items.json",
        "skills": "Skills.json",
        "weapons": "Weapons.json",
        "armors": "Armors.json",
        "enemies": "Enemies.json",
        "troops": "Troops.json",
        "classes": "Classes.json",
        "states": "States.json",
    }

    db_ids: dict = {}
    for key, filename in db_file_map.items():
        filepath = os.path.join(data_dir, filename)
        if os.path.exists(filepath):
            db_ids[key] = load_valid_ids(filepath)
        else:
            db_ids[key] = set()

    # Load system switch/variable counts
    system_path = os.path.join(data_dir, "System.json")
    if os.path.exists(system_path):
        db_ids["switches_max"] = load_system_switch_count(system_path)
        db_ids["variables_max"] = load_system_variable_count(system_path)
    else:
        db_ids["switches_max"] = 0
        db_ids["variables_max"] = 0

    # Collect all errors
    all_errors = []
    all_errors.extend(check_event_commands(project_path, db_ids))
    all_errors.extend(check_database_crossrefs(project_path, db_ids))

    # Print all errors to stdout
    for error in all_errors:
        print(error)

    return 1 if all_errors else 0


def main() -> None:
    """CLI entry point for orphaned reference validation."""
    parser = argparse.ArgumentParser(
        description=(
            "Check for orphaned cross-file references in an RPG Maker MV/MZ project. "
            "Validates that all database ID references in event commands and database "
            "entries point to existing records. Exits 0 if clean, 1 if errors found."
        )
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
        sys.exit(validate_project(args.project))
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as exc:
        print(f"Error: Malformed JSON — {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
