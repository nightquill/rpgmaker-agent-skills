"""
Tests for JSON Schema validation of RPG Maker MV fixture data files.

Validates that every data file in fixtures/example-mv-project/data/
validates successfully against its corresponding JSON Schema in schemas/.
"""

import json
import os

import jsonschema
import pytest

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

MAP_FILES = ["Map001.json", "Map002.json", "Map003.json"]


@pytest.mark.parametrize("data_file,schema_file", list(FILE_SCHEMA_MAP.items()))
def test_data_file_validates(fixture_dir, schema_dir, data_file, schema_file):
    """Each fixture data file should validate against its corresponding schema."""
    data_path = os.path.join(fixture_dir, "data", data_file)
    schema_path = os.path.join(schema_dir, schema_file)

    with open(data_path, encoding="utf-8") as fh:
        data = json.load(fh)
    with open(schema_path, encoding="utf-8") as fh:
        schema = json.load(fh)

    # Should not raise ValidationError
    jsonschema.validate(instance=data, schema=schema)


@pytest.mark.parametrize("map_file", MAP_FILES)
def test_map_file_validates(fixture_dir, schema_dir, map_file):
    """Each map file should validate against map.schema.json."""
    data_path = os.path.join(fixture_dir, "data", map_file)
    schema_path = os.path.join(schema_dir, "map.schema.json")

    with open(data_path, encoding="utf-8") as fh:
        data = json.load(fh)
    with open(schema_path, encoding="utf-8") as fh:
        schema = json.load(fh)

    # Should not raise ValidationError
    jsonschema.validate(instance=data, schema=schema)


def test_positional_arrays_have_null_index_0(fixture_dir):
    """All positional-array data files must have null at index 0."""
    for data_file in FILE_SCHEMA_MAP:
        if data_file == "System.json":
            # System.json is an object, not a positional array
            continue
        data_path = os.path.join(fixture_dir, "data", data_file)
        with open(data_path, encoding="utf-8") as fh:
            data = json.load(fh)
        assert data[0] is None, (
            f"{data_file}: expected null at index 0, got {type(data[0]).__name__!r}"
        )


def test_all_fixture_files_exist(fixture_dir):
    """Every expected fixture file must exist on disk."""
    all_files = list(FILE_SCHEMA_MAP.keys()) + MAP_FILES
    for filename in all_files:
        path = os.path.join(fixture_dir, "data", filename)
        assert os.path.exists(path), f"Fixture file missing: {path}"


def test_schema_files_use_draft_2020_12(schema_dir):
    """Every schema file must declare JSON Schema Draft 2020-12."""
    schema_files = [f for f in os.listdir(schema_dir) if f.endswith(".schema.json")]
    assert len(schema_files) > 0, "No schema files found in schemas/"
    for filename in schema_files:
        path = os.path.join(schema_dir, filename)
        with open(path, encoding="utf-8") as fh:
            schema = json.load(fh)
        assert "$schema" in schema, f"{filename}: missing '$schema' key"
        assert "2020-12" in schema["$schema"], (
            f"{filename}: '$schema' does not reference Draft 2020-12, got {schema['$schema']!r}"
        )
