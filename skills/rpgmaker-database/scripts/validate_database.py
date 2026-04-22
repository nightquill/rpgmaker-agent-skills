"""Validate all RPG Maker MV/MZ database JSON files against JSON schemas.

Checks each database file in the project's data/ directory against the
corresponding JSON Schema in the schemas/ directory. Reports PASS/FAIL
per file and exits non-zero if any validation errors are found.

Usage:
    python validate_database.py --project <path> [--schema-dir <path>]

Exit codes:
    0 -- all files pass validation
    1 -- one or more validation errors found
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[3]))  # repo root

import argparse
import glob
import json
import os

import jsonschema


FILE_SCHEMA_MAP = {
    "Actors.json": "actors.schema.json",
    "Classes.json": "classes.schema.json",
    "Skills.json": "skills.schema.json",
    "Items.json": "items.schema.json",
    "Weapons.json": "weapons.schema.json",
    "Armors.json": "armors.schema.json",
    "Enemies.json": "enemies.schema.json",
    "Troops.json": "troops.schema.json",
    "States.json": "states.schema.json",
    "Animations.json": "animations.schema.json",
    "Tilesets.json": "tilesets.schema.json",
    "CommonEvents.json": "common-events.schema.json",
    "System.json": "system.schema.json",
    "MapInfos.json": "map-infos.schema.json",
}


def validate_file(data_path: str, schema_path: str, label: str) -> str | None:
    """Validate a data file against a JSON schema.

    Returns None on success, error message string on failure.
    """
    with open(data_path, encoding="utf-8") as fh:
        data = json.load(fh)
    with open(schema_path, encoding="utf-8") as fh:
        schema = json.load(fh)

    try:
        jsonschema.validate(instance=data, schema=schema)
        print(f"  PASS  {label}")
        return None
    except jsonschema.ValidationError as exc:
        msg = str(exc.message)[:200]
        print(f"  FAIL  {label}: {msg}")
        return msg


def validate_project(project_path: str, schema_dir: str) -> int:
    """Validate all database files in a project. Returns exit code."""
    data_dir = os.path.join(project_path, "data")
    errors = []

    print(f"Validating: {project_path}\n")

    # Database files
    for data_file, schema_file in FILE_SCHEMA_MAP.items():
        data_path = os.path.join(data_dir, data_file)
        schema_path = os.path.join(schema_dir, schema_file)

        if not os.path.exists(data_path):
            print(f"  SKIP  {data_file} (not found)")
            continue

        if not os.path.exists(schema_path):
            print(f"  SKIP  {data_file} (schema {schema_file} not found)")
            continue

        err = validate_file(data_path, schema_path, data_file)
        if err:
            errors.append((data_file, err))

    # Map files (Map001.json, Map002.json, etc.)
    map_schema_path = os.path.join(schema_dir, "map.schema.json")
    if os.path.exists(map_schema_path):
        map_pattern = os.path.join(data_dir, "Map[0-9]*.json")
        for map_path in sorted(glob.glob(map_pattern)):
            map_name = os.path.basename(map_path)
            err = validate_file(map_path, map_schema_path, map_name)
            if err:
                errors.append((map_name, err))

    # Summary
    print()
    if errors:
        print(f"Validation failed: {len(errors)} file(s) with errors")
        for name, err in errors:
            print(f"  - {name}: {err[:100]}")
        return 1
    else:
        print("All files passed validation")
        return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate RPG Maker database files against JSON schemas"
    )
    parser.add_argument(
        "--project", required=True,
        help="Path to RPG Maker project root directory",
    )
    parser.add_argument(
        "--schema-dir", default=None,
        help="Path to schemas/ directory (default: auto-detect from script location)",
    )
    args = parser.parse_args()

    if not os.path.isdir(args.project):
        print(f"Error: Project path does not exist: {args.project}", file=sys.stderr)
        sys.exit(1)

    schema_dir = args.schema_dir or str(Path(__file__).parents[3] / "schemas")
    if not os.path.isdir(schema_dir):
        print(f"Error: Schema directory not found: {schema_dir}", file=sys.stderr)
        sys.exit(1)

    sys.exit(validate_project(args.project, schema_dir))


if __name__ == "__main__":
    main()
