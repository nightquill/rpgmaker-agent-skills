"""
Tests for scripts/lib/safe_write.py

Covers all write-safety invariants:
  FNDN-02: .bak backup created before any write
  FNDN-03: dry-run by default (apply=False)
  FNDN-04: no ID renumbering; no index-0 mutation
  FNDN-05: source file indentation preserved
  FNDN-06: draft framing language in dry-run output
"""
import json
import sys
import os
import argparse

import pytest

# Ensure scripts package is importable regardless of cwd
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from scripts.lib.safe_write import (
    load_json_preserving_format,
    validate_positional_array,
    validate_no_id_changes,
    safe_write,
    add_argparse_write_args,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def write_json_file(path, data, indent=2):
    """Write JSON to a file with a specific indentation."""
    path.write_text(json.dumps(data, indent=indent) + "\n", encoding="utf-8")
    return path


def make_positional_array(*entries):
    """Build a valid positional array: [None, {id:1,...}, {id:2,...}, ...]"""
    return [None] + list(entries)


# ---------------------------------------------------------------------------
# load_json_preserving_format
# ---------------------------------------------------------------------------

class TestLoadJsonPreservingFormat:
    def test_2space_indent_detected(self, tmp_path):
        data = {"key": "value", "nested": {"a": 1}}
        f = tmp_path / "test.json"
        write_json_file(f, data, indent=2)
        result_data, detected_indent = load_json_preserving_format(str(f))
        assert detected_indent == 2
        assert result_data == data

    def test_4space_indent_detected(self, tmp_path):
        data = {"key": "value", "nested": {"a": 1}}
        f = tmp_path / "test.json"
        write_json_file(f, data, indent=4)
        result_data, detected_indent = load_json_preserving_format(str(f))
        assert detected_indent == 4
        assert result_data == data

    def test_default_indent_2_when_undetectable(self, tmp_path):
        # A flat single-line JSON has no indentation to detect
        f = tmp_path / "flat.json"
        f.write_text('{"key": "value"}\n', encoding="utf-8")
        result_data, detected_indent = load_json_preserving_format(str(f))
        assert detected_indent == 2  # default fallback

    def test_returns_parsed_data(self, tmp_path):
        data = [None, {"id": 1, "name": "Hero"}]
        f = tmp_path / "actors.json"
        write_json_file(f, data, indent=2)
        result_data, _ = load_json_preserving_format(str(f))
        assert result_data == data


# ---------------------------------------------------------------------------
# validate_positional_array
# ---------------------------------------------------------------------------

class TestValidatePositionalArray:
    def test_raises_if_index0_not_null(self):
        data = [{"id": 0, "name": "Bad"}, {"id": 1, "name": "Good"}]
        with pytest.raises(ValueError, match="index 0 must be null"):
            validate_positional_array(data, "Actors")

    def test_raises_if_entry_id_does_not_match_index(self):
        data = [None, {"id": 1, "name": "Hero"}, {"id": 99, "name": "Wrong"}]
        with pytest.raises(ValueError, match="index 2"):
            validate_positional_array(data, "Actors")

    def test_passes_for_valid_array(self):
        data = [None, {"id": 1, "name": "Hero"}, {"id": 2, "name": "Mage"}]
        # Should not raise
        validate_positional_array(data, "Actors")

    def test_raises_with_label_in_message(self):
        data = [{"id": 0}]
        with pytest.raises(ValueError, match="MyLabel"):
            validate_positional_array(data, "MyLabel")

    def test_passes_for_single_entry_array(self):
        data = [None, {"id": 1, "name": "Solo"}]
        validate_positional_array(data, "Solo")


# ---------------------------------------------------------------------------
# validate_no_id_changes
# ---------------------------------------------------------------------------

class TestValidateNoIdChanges:
    def test_raises_if_existing_entry_id_changed(self):
        original = [None, {"id": 1, "name": "Hero"}, {"id": 2, "name": "Mage"}]
        modified = [None, {"id": 99, "name": "Hero"}, {"id": 2, "name": "Mage"}]
        with pytest.raises(ValueError, match="id"):
            validate_no_id_changes(original, modified, "Actors")

    def test_passes_if_ids_unchanged(self):
        original = [None, {"id": 1, "name": "Hero"}, {"id": 2, "name": "Mage"}]
        modified = [None, {"id": 1, "name": "Hero Updated"}, {"id": 2, "name": "Mage Updated"}]
        # Should not raise
        validate_no_id_changes(original, modified, "Actors")

    def test_passes_if_modified_is_longer(self):
        """New entries appended — allowed."""
        original = [None, {"id": 1, "name": "Hero"}]
        modified = [None, {"id": 1, "name": "Hero"}, {"id": 2, "name": "Mage"}]
        validate_no_id_changes(original, modified, "Actors")

    def test_raises_if_modified_is_shorter(self):
        """Deletion is not allowed."""
        original = [None, {"id": 1, "name": "Hero"}, {"id": 2, "name": "Mage"}]
        modified = [None, {"id": 1, "name": "Hero"}]
        with pytest.raises(ValueError):
            validate_no_id_changes(original, modified, "Actors")


# ---------------------------------------------------------------------------
# safe_write
# ---------------------------------------------------------------------------

class TestSafeWriteDryRun:
    def test_dry_run_does_not_modify_file(self, tmp_path, capsys):
        data = {"key": "original"}
        f = tmp_path / "test.json"
        write_json_file(f, data, indent=2)
        original_content = f.read_text()

        safe_write(
            str(f),
            original_data=data,
            modified_data={"key": "changed"},
            apply=False,
        )

        assert f.read_text() == original_content

    def test_dry_run_returns_false(self, tmp_path, capsys):
        data = {"key": "original"}
        f = tmp_path / "test.json"
        write_json_file(f, data, indent=2)

        result = safe_write(
            str(f),
            original_data=data,
            modified_data={"key": "changed"},
            apply=False,
        )
        assert result is False

    def test_dry_run_output_contains_draft_framing(self, tmp_path, capsys):
        """FNDN-06: output must use draft framing language."""
        data = {"key": "original"}
        f = tmp_path / "test.json"
        write_json_file(f, data, indent=2)

        safe_write(
            str(f),
            original_data=data,
            modified_data={"key": "changed"},
            apply=False,
            changes_description="Updated key value",
        )

        captured = capsys.readouterr()
        output = captured.out
        # Must contain "Draft" OR "Would" per FNDN-06 / D-06
        assert "Draft" in output or "Would" in output

    def test_dry_run_output_contains_filepath(self, tmp_path, capsys):
        data = {"key": "original"}
        f = tmp_path / "test.json"
        write_json_file(f, data, indent=2)

        safe_write(str(f), original_data=data, modified_data={"key": "changed"}, apply=False)

        captured = capsys.readouterr()
        assert str(f) in captured.out


class TestSafeWriteApply:
    def test_apply_creates_bak_file(self, tmp_path):
        """FNDN-02: backup must be created before write."""
        data = {"key": "original"}
        f = tmp_path / "test.json"
        write_json_file(f, data, indent=2)

        safe_write(
            str(f),
            original_data=data,
            modified_data={"key": "changed"},
            apply=True,
        )

        bak_path = tmp_path / "test.json.bak"
        assert bak_path.exists()

    def test_apply_bak_has_original_content(self, tmp_path):
        """Backup content must match original before modification."""
        data = {"key": "original"}
        f = tmp_path / "test.json"
        write_json_file(f, data, indent=2)
        original_content = f.read_text()

        safe_write(
            str(f),
            original_data=data,
            modified_data={"key": "changed"},
            apply=True,
        )

        bak_path = tmp_path / "test.json.bak"
        assert bak_path.read_text() == original_content

    def test_apply_writes_valid_json(self, tmp_path):
        """FNDN-05: written file must be valid JSON."""
        data = {"key": "original"}
        f = tmp_path / "test.json"
        write_json_file(f, data, indent=2)

        modified = {"key": "changed", "new_field": 42}
        safe_write(str(f), original_data=data, modified_data=modified, apply=True, indent=2)

        written_data = json.loads(f.read_text())
        assert written_data == modified

    def test_apply_preserves_indentation(self, tmp_path):
        """FNDN-05: indentation style must be preserved."""
        data = {"key": "original"}
        f = tmp_path / "test.json"
        write_json_file(f, data, indent=4)

        safe_write(
            str(f),
            original_data=data,
            modified_data={"key": "changed"},
            apply=True,
            indent=4,
        )

        written = f.read_text()
        # 4-space indent means the "key" line should have 4 spaces
        assert '    "key"' in written

    def test_apply_returns_true(self, tmp_path):
        data = {"key": "original"}
        f = tmp_path / "test.json"
        write_json_file(f, data, indent=2)

        result = safe_write(
            str(f),
            original_data=data,
            modified_data={"key": "changed"},
            apply=True,
        )
        assert result is True


class TestSafeWriteValidation:
    def test_refuses_write_if_positional_array_invalid(self, tmp_path):
        """If validate_positional_array would fail, safe_write must not write."""
        # Corrupt: index 0 is not null
        data = [{"id": 0, "name": "Bad"}, {"id": 1, "name": "Good"}]
        f = tmp_path / "actors.json"
        write_json_file(f, data, indent=2)
        original_content = f.read_text()

        with pytest.raises(ValueError):
            safe_write(
                str(f),
                original_data=data,
                modified_data=data,
                apply=True,
                label="Actors",
            )

        # File should not have been modified
        assert f.read_text() == original_content

    def test_refuses_write_if_id_changed(self, tmp_path):
        """validate_no_id_changes must block writes that alter existing IDs."""
        original = [None, {"id": 1, "name": "Hero"}]
        modified = [None, {"id": 99, "name": "Hero"}]  # ID changed!
        f = tmp_path / "actors.json"
        write_json_file(f, original, indent=2)

        with pytest.raises(ValueError):
            safe_write(
                str(f),
                original_data=original,
                modified_data=modified,
                apply=True,
                label="Actors",
            )


# ---------------------------------------------------------------------------
# add_argparse_write_args
# ---------------------------------------------------------------------------

class TestAddArgparseWriteArgs:
    def test_adds_apply_flag(self):
        parser = argparse.ArgumentParser()
        add_argparse_write_args(parser)
        args = parser.parse_args([])
        assert hasattr(args, "apply")
        assert args.apply is False

    def test_apply_true_when_flag_passed(self):
        parser = argparse.ArgumentParser()
        add_argparse_write_args(parser)
        args = parser.parse_args(["--apply"])
        assert args.apply is True
