# Getting Started with RPG Maker Agent Skills

This walkthrough demonstrates the full loop: install the skill pack, extract existing dialog,
draft new lines, inject them, and validate the project.

## Prerequisites

- An RPG Maker MV or MZ project on your local filesystem
- An AI agent (Claude Code, Codex, or Cursor) configured with API access
- Python 3.10+ installed (for helper scripts)

## Step 1: Install the Skills

**macOS / Linux:**

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/nightquill/rpgmaker-agent-skills/main/install.sh)
```

**Windows (PowerShell):**

```powershell
irm https://raw.githubusercontent.com/nightquill/rpgmaker-agent-skills/main/install.ps1 | iex
```

The installer will ask whether to install globally (`~/.claude/skills/`) or locally
(`./.claude/skills/`). Choose global to use the skills across all your projects.

## Step 2: Open Your Project

Open your RPG Maker project directory in your agent. The `rpgmaker-core` skill automatically
detects MV projects via `Game.rpgproject` or MZ projects via `Game.rmmzproject` and adjusts the
file format rules accordingly.

## Step 3: Extract NPC Dialog

Find all dialog for a specific NPC using the extraction script:

```bash
PYTHONPATH=. python skills/rpgmaker-dialog/scripts/extract_npc_lines.py \
  --project /path/to/your/project \
  --npc "Innkeeper"
```

This outputs all dialog lines spoken by the Innkeeper across every map and common event, including
the map name, event ID, and page number for each line. Use this output to understand the NPC's
established voice before drafting new content.

## Step 4: Draft New Dialog

Give your agent the extracted lines and ask for new content:

> "Based on the Innkeeper's existing lines above, draft three new greeting lines for when the
> player returns after completing the dungeon quest. Match her friendly-but-businesslike tone."

The agent uses the extracted context to match voice and format. All agent output is a **draft for
your review** — read it carefully before proceeding to injection.

## Step 5: Inject the Dialog

Preview the injection with a dry run (no `--apply` flag):

```bash
PYTHONPATH=. python skills/rpgmaker-dialog/scripts/inject_dialog.py \
  --project /path/to/your/project \
  --map Map002 \
  --event 5 \
  --page 0 \
  --text "Welcome back, traveler. Heard you cleared the dungeon!"
```

The dry run shows exactly what will change. When the diff looks correct, add `--apply`:

```bash
PYTHONPATH=. python skills/rpgmaker-dialog/scripts/inject_dialog.py \
  --project /path/to/your/project \
  --map Map002 \
  --event 5 \
  --page 0 \
  --text "Welcome back, traveler. Heard you cleared the dungeon!" \
  --apply
```

A `.bak` backup is written beside the original file before any modification.

## Step 6: Validate the Project

Run the full consistency check:

```bash
PYTHONPATH=. python scripts/validate_project.py \
  --project /path/to/your/project
```

This runs four sub-validators in sequence:

1. **check_orphaned_refs.py** — finds broken database ID references in events and dialogs
2. **check_switch_collisions.py** — detects the same switch set in multiple maps (copy-paste bug)
3. **validate_dialog_refs.py** — checks `\N[id]` and `\I[id]` text codes in show-text events
4. **validate_database.py** — validates database JSON structure against schemas

The output is a structured markdown report. If any `ERROR:` lines appear, exit code is 1. Fix
the flagged issues, then re-run until the report is clean.

## Next Steps

- **Scaffold events:** Use `scaffold_event.py` to generate door, chest, NPC, and shop event patterns
- **Audit balance:** Run `skills/rpgmaker-database/scripts/balance_check.py` to flag stat outliers
- **Track switches:** Use `scripts/list_switches.py` to audit all switches used in your project
- **Check event references:** Use `scripts/find_event_refs.py` to trace where a specific switch or
  variable is used

### Agent-specific guides

- [Claude Code](for-claude-code.md) — auto-load configuration, skill triggers, example prompts
- [Codex](for-codex.md) — sandbox tips, task description patterns, example prompts
- [Cursor](for-cursor.md) — rules configuration, inline edit tips, example prompts
