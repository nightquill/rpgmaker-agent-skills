"""Run all RPG Maker MV/MZ project consistency checks and produce a structured report.

Imports and runs: check_orphaned_refs, check_switch_collisions, validate_dialog_refs,
and validate_database. Collects findings into a markdown report with sections per checker.

Usage:
    python validate_project.py --project <path>

Exit codes:
    0 -- all checks pass (no ERRORs; warnings are informational)
    1 -- one or more ERROR-level findings
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))  # repo root


def run_checker(script_path: str, project_path: str, extra_args: list | None = None) -> tuple[int, str]:
    """Run a checker script via subprocess and capture its output.

    Only known script paths within the repo are called. The project_path argument
    is the only user-supplied value, and it is passed as a positional CLI argument
    (not interpolated into a shell command), preventing injection.

    Args:
        script_path: Absolute path to the checker script within the repo.
        project_path: Path to the RPG Maker project root (user-supplied, passed as arg).
        extra_args: Optional additional CLI arguments to append.

    Returns:
        Tuple of (returncode, stdout_text).
    """
    cmd = [sys.executable, script_path, "--project", project_path]
    if extra_args:
        cmd.extend(extra_args)
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).parents[1])
    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    return result.returncode, result.stdout.strip()


def validate_project(project_path: str) -> int:
    """Run all consistency checkers and print a structured markdown report.

    Runs four sub-validators in sequence:
    1. check_orphaned_refs.py (ERROR-level, contributes to exit code)
    2. check_switch_collisions.py (WARNING-level only, never causes exit 1)
    3. validate_dialog_refs.py (ERROR-level, contributes to exit code)
    4. validate_database.py (ERROR-level, contributes to exit code)

    Checkers 3 and 4 are skipped gracefully if their scripts do not exist.

    Args:
        project_path: Path to RPG Maker project root directory.

    Returns:
        0 if no ERROR-level findings across all checkers, 1 otherwise.
    """
    repo_root = str(Path(__file__).parents[1])
    has_errors = False
    report_lines = []

    report_lines.append("# Project Validation Report")
    report_lines.append("")
    report_lines.append(f"Project: {os.path.abspath(project_path)}")
    report_lines.append("")

    # 1. Orphaned Reference Check (ERROR-level — contributes to exit code)
    report_lines.append("## Orphaned Reference Check")
    script = os.path.join(repo_root, "scripts", "check_orphaned_refs.py")
    if os.path.exists(script):
        rc, output = run_checker(script, project_path)
        if rc != 0:
            has_errors = True
            report_lines.append(output if output else "  (errors found)")
        else:
            report_lines.append(output if output else "  (clean)")
    else:
        report_lines.append("  SKIP  check_orphaned_refs.py (not found)")
    report_lines.append("")

    # 2. Switch Collision Check (WARNING-level — never causes exit 1 per D-02)
    report_lines.append("## Switch Collision Check")
    script = os.path.join(repo_root, "scripts", "check_switch_collisions.py")
    if os.path.exists(script):
        _rc, output = run_checker(script, project_path)
        if output:
            report_lines.append(output)
        else:
            report_lines.append("  (clean)")
    else:
        report_lines.append("  SKIP  check_switch_collisions.py (not found)")
    report_lines.append("")

    # 3. Dialog Reference Check (ERROR-level — contributes to exit code)
    report_lines.append("## Dialog Reference Check")
    script = os.path.join(repo_root, "skills", "rpgmaker-dialog", "scripts", "validate_dialog_refs.py")
    if os.path.exists(script):
        rc, output = run_checker(script, project_path)
        if rc != 0:
            has_errors = True
            report_lines.append(output if output else "  (errors found)")
        else:
            report_lines.append(output if output else "  (clean)")
    else:
        report_lines.append("  SKIP  validate_dialog_refs.py (not found)")
    report_lines.append("")

    # 4. Database Schema Validation (ERROR-level — contributes to exit code)
    report_lines.append("## Database Schema Validation")
    script = os.path.join(repo_root, "skills", "rpgmaker-database", "scripts", "validate_database.py")
    if os.path.exists(script):
        schema_dir = os.path.join(repo_root, "schemas")
        rc, output = run_checker(script, project_path, ["--schema-dir", schema_dir])
        if rc != 0:
            has_errors = True
            report_lines.append(output if output else "  (errors found)")
        else:
            report_lines.append(output if output else "  (clean)")
    else:
        report_lines.append("  SKIP  validate_database.py (not found)")
    report_lines.append("")

    # Print full report
    report = "\n".join(report_lines)
    print(report)

    return 1 if has_errors else 0


def main() -> None:
    """CLI entry point for the umbrella project validator."""
    parser = argparse.ArgumentParser(
        description="Run all RPG Maker MV/MZ project consistency checks."
    )
    parser.add_argument(
        "--project",
        required=True,
        help="Path to RPG Maker project root directory",
    )
    args = parser.parse_args()

    if not os.path.isdir(args.project):
        print(f"Error: Project path does not exist: {args.project}", file=sys.stderr)
        sys.exit(1)

    try:
        sys.exit(validate_project(args.project))
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
