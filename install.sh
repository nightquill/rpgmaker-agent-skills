#!/usr/bin/env bash
set -euo pipefail

# RPG Maker Agent Skills Installer
# Installs skills/ and scripts/ into your agent's skills directory.
# Usage: bash install.sh [--version <tag>]

VERSION="latest"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --version)
            VERSION="${2:?--version requires an argument}"
            shift 2
            ;;
        -v)
            VERSION="${2:?-v requires an argument}"
            shift 2
            ;;
        --help|-h)
            echo "Usage: bash install.sh [--version <tag>]"
            echo ""
            echo "Options:"
            echo "  --version <tag>   Install a specific release tag (default: latest main branch)"
            echo "  --help            Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1" >&2
            echo "Run 'bash install.sh --help' for usage." >&2
            exit 1
            ;;
    esac
done

REPO="nightquill/rpgmaker-agent-skills"

echo "RPG Maker Agent Skills Installer"
echo ""
echo "Install location:"
echo "  1) Global: ~/.claude/skills/ (default)"
echo "  2) Local:  ./.claude/skills/ (current project)"
echo ""
read -r -p "Choose [1/2]: " choice

case "$choice" in
    2)
        BASE_DIR="$(pwd)/.claude"
        ;;
    *)
        BASE_DIR="$HOME/.claude"
        ;;
esac

SKILLS_TARGET="$BASE_DIR/skills"
SCRIPTS_TARGET="$BASE_DIR/rpgmaker-scripts"

# Create temp directory and clean up on exit
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

# Build download URL
if [ "$VERSION" = "latest" ]; then
    URL="https://github.com/$REPO/archive/refs/heads/main.tar.gz"
else
    URL="https://github.com/$REPO/archive/refs/tags/$VERSION.tar.gz"
fi

echo ""
echo "Downloading from $URL..."

# Download using curl or wget
if command -v curl &>/dev/null; then
    curl -fsSL "$URL" -o "$TMP/pack.tar.gz"
elif command -v wget &>/dev/null; then
    wget -q "$URL" -O "$TMP/pack.tar.gz"
else
    echo "Error: curl or wget is required to download the skill pack." >&2
    exit 1
fi

echo "Extracting..."
tar -xzf "$TMP/pack.tar.gz" -C "$TMP" --strip-components=1

# Install skills
mkdir -p "$SKILLS_TARGET"
cp -r "$TMP/skills/"* "$SKILLS_TARGET/"
echo "Installed skills to: $SKILLS_TARGET"

# Install scripts and schemas alongside skills
mkdir -p "$SCRIPTS_TARGET"
cp -r "$TMP/scripts" "$SCRIPTS_TARGET/"
cp -r "$TMP/schemas" "$SCRIPTS_TARGET/"
echo "Installed scripts to: $SCRIPTS_TARGET/scripts/"
echo "Installed schemas to: $SCRIPTS_TARGET/schemas/"

echo ""
echo "Done! Restart your agent to pick up the new skills."
echo ""
echo "To use helper scripts:"
echo "  cd $SCRIPTS_TARGET && PYTHONPATH=. python scripts/validate_project.py --project /path/to/your/project"
echo ""
echo "Available skills:"
for skill_dir in "$SKILLS_TARGET"/rpgmaker-*; do
    [ -d "$skill_dir" ] && echo "  - $(basename "$skill_dir")"
done
