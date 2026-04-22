"""Detect RPG Maker project version (MV or MZ) from manifest files."""

import argparse
import os
import sys


def detect_version(project_path: str) -> str:
    """Detect RPG Maker version from project manifest.

    Checks for Game.rmmzproject (MZ) first, then Game.rpgproject (MV).
    If both exist, returns "MZ" (per spec section 2.4: "If both, prefer MZ").

    Args:
        project_path: Path to RPG Maker project root directory.

    Returns:
        "MV" or "MZ"

    Raises:
        SystemExit: If neither manifest file is found.
    """
    if os.path.exists(os.path.join(project_path, "Game.rmmzproject")):
        return "MZ"
    if os.path.exists(os.path.join(project_path, "Game.rpgproject")):
        return "MV"
    print(
        f"Error: No RPG Maker project found at {project_path}",
        file=sys.stderr,
    )
    sys.exit(1)


def main() -> None:
    """Entry point for CLI usage."""
    parser = argparse.ArgumentParser(
        description=(
            "Detect RPG Maker project version. "
            "Prints 'MV' or 'MZ' to stdout based on the project manifest file."
        )
    )
    parser.add_argument(
        "--project-path",
        required=True,
        help="Path to RPG Maker project root directory",
    )
    args = parser.parse_args()
    version = detect_version(args.project_path)
    print(version)


if __name__ == "__main__":
    main()
