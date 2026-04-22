"""
safe_write.py — Write-safety library for RPG Maker JSON data files.

All write operations on RPG Maker project files MUST go through this module.
It enforces five invariants:

  FNDN-02: Always create a .bak backup before modifying any file.
  FNDN-03: Dry-run is the default (apply=False). Explicit --apply required to write.
  FNDN-04: No ID renumbering. No entry's id field may change; index 0 must stay null.
  FNDN-05: Source file indentation is detected and replicated on write.
  FNDN-06: Dry-run output uses draft framing language ("Draft preview", "Would modify").

Usage:
  from scripts.lib.safe_write import (
      load_json_preserving_format,
      validate_positional_array,
      validate_no_id_changes,
      safe_write,
      add_argparse_write_args,
  )
"""

from __future__ import annotations

import argparse
import json
import shutil
from typing import Any


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def load_json_preserving_format(filepath: str) -> tuple[Any, int]:
    """Load a JSON file and detect its indentation style.

    Args:
        filepath: Path to the JSON file to load.

    Returns:
        A tuple of (parsed_data, detected_indent) where detected_indent is the
        number of spaces used for indentation (defaults to 2 when undetectable).
    """
    with open(filepath, encoding="utf-8") as fh:
        raw = fh.read()

    data = json.loads(raw)
    detected_indent = _detect_indent(raw)
    return data, detected_indent


def validate_positional_array(data: list, label: str) -> None:
    """Validate that a positional RMMV/MZ array has the correct structure.

    RPG Maker database arrays are positional: index 0 is always null, and each
    entry's `id` field must equal its array index.  Renumbering breaks all
    cross-file references silently.

    Args:
        data:  The list to validate.
        label: Human-readable name used in error messages (e.g. "Actors").

    Raises:
        ValueError: If data[0] is not None, or if any entry's id != its index.
    """
    if not data or data[0] is not None:
        raise ValueError(f"{label}: index 0 must be null (found {data[0]!r})")

    for i in range(1, len(data)):
        entry = data[i]
        if entry is None:
            continue
        entry_id = entry.get("id") if isinstance(entry, dict) else None
        if entry_id != i:
            raise ValueError(
                f"{label}: entry at index {i} has id={entry_id!r}, expected {i}"
            )


def validate_no_id_changes(
    original: list, modified: list, label: str
) -> None:
    """Ensure that no existing entry's `id` field was altered.

    New entries may be appended (modified is longer than original) but the list
    must not shrink and existing IDs must not change.

    Args:
        original: The list before modification.
        modified: The list after modification.
        label:    Human-readable name used in error messages.

    Raises:
        ValueError: If modified is shorter than original, or if any id changed.
    """
    if len(modified) < len(original):
        raise ValueError(
            f"{label}: modified array is shorter than original "
            f"({len(modified)} < {len(original)}). Deletion of entries is not allowed."
        )

    for i in range(len(original)):
        orig_entry = original[i]
        mod_entry = modified[i]

        if orig_entry is None or mod_entry is None:
            continue

        if not isinstance(orig_entry, dict) or not isinstance(mod_entry, dict):
            continue

        orig_id = orig_entry.get("id")
        mod_id = mod_entry.get("id")

        if orig_id != mod_id:
            raise ValueError(
                f"{label}: entry at index {i} had id={orig_id!r}, "
                f"but modified entry has id={mod_id!r}. "
                "Changing existing IDs is not allowed."
            )


def safe_write(
    filepath: str,
    original_data: Any,
    modified_data: Any,
    apply: bool = False,
    indent: int = 2,
    label: str = "",
    changes_description: str = "",
) -> bool:
    """Write modified JSON data to a file with full safety enforcement.

    Validates data integrity, creates a .bak backup before writing, and defaults
    to dry-run mode (apply=False) per FNDN-03.

    Args:
        filepath:            Path to the JSON file to write.
        original_data:       The data before modification (used for ID checks).
        modified_data:       The new data to write.
        apply:               If False (default), print a dry-run summary only.
                             If True, create .bak and write the file.
        indent:              Indentation width to use when serialising JSON.
        label:               Human-readable file label used in validation messages.
        changes_description: Short description of what changed (shown in dry-run).

    Returns:
        True if the file was written, False if dry-run only.

    Raises:
        ValueError: If any write-safety invariant is violated.
    """
    # --- Validate before doing anything ---
    if isinstance(modified_data, list) and label:
        validate_positional_array(modified_data, label)

    if isinstance(original_data, list) and isinstance(modified_data, list):
        validate_no_id_changes(original_data, modified_data, label or filepath)

    # --- Dry-run (default) ---
    if not apply:
        desc = changes_description or "changes pending"
        print(f"[Draft preview] {desc}")
        print(f"Would modify: {filepath}")
        print("No changes written. Use --apply to write.")
        return False

    # --- Apply: backup then write ---
    bak_path = filepath + ".bak"
    shutil.copy2(filepath, bak_path)
    print(f"Backup created: {bak_path}")

    with open(filepath, "w", encoding="utf-8") as fh:
        json.dump(modified_data, fh, indent=indent, ensure_ascii=False)
        fh.write("\n")  # trailing newline per FNDN-05

    print(f"Written: {filepath}")
    return True


def add_argparse_write_args(parser: argparse.ArgumentParser) -> None:
    """Add the standard --apply flag to an ArgumentParser.

    Every domain script must call this so users get consistent dry-run /
    apply behaviour across the entire toolset.

    Args:
        parser: The ArgumentParser to augment.
    """
    parser.add_argument(
        "--apply",
        action="store_true",
        default=False,
        help=(
            "Write changes to disk. "
            "Without this flag, changes are previewed only (dry-run)."
        ),
    )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _detect_indent(raw_json: str) -> int:
    """Scan the first 20 lines of a JSON string and detect leading-space indent.

    Returns the detected number of spaces (2 or 4 typically), or 2 as the
    default when the file is too flat to measure.
    """
    lines = raw_json.splitlines()[:20]
    for line in lines:
        if not line:
            continue
        stripped = line.lstrip(" ")
        leading = len(line) - len(stripped)
        if leading > 0:
            return leading
    return 2  # default fallback when indentation is undetectable
