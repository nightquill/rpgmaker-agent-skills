# Using RPG Maker Agent Skills with Claude Code

## Installation

Run the installer and choose global or local:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/nightquill/rpgmaker-agent-skills/main/install.sh)
```

Choose **Global** to install to `~/.claude/skills/` (available in all projects) or **Local** to
install to `./.claude/skills/` in the current project directory only.

The installer copies five skill directories and the helper scripts:

```
~/.claude/skills/
  rpgmaker-core/
  rpgmaker-dialog/
  rpgmaker-database/
  rpgmaker-events/
  rpgmaker-consistency/

~/rpgmaker-scripts/   (or ./.rpgmaker-scripts/ for local install)
  check_orphaned_refs.py
  check_switch_collisions.py
  validate_project.py
  scaffold_event.py
  list_switches.py
  find_event_refs.py
  skills/rpgmaker-dialog/scripts/extract_npc_lines.py
  skills/rpgmaker-dialog/scripts/inject_dialog.py
  skills/rpgmaker-database/scripts/balance_check.py
  skills/rpgmaker-database/scripts/add_skill.py
  skills/rpgmaker-database/scripts/add_enemy.py
```

## How Skills Load

Claude Code automatically loads `SKILL.md` files from `.claude/skills/` based on the `description`
field triggers. When your project contains:

- `Game.rpgproject` or `Game.rmmzproject` — loads `rpgmaker-core`
- Dialog-related prompts — loads `rpgmaker-dialog`
- Database or balance prompts — loads `rpgmaker-database`
- Event or switch prompts — loads `rpgmaker-events`
- Validation or consistency prompts — loads `rpgmaker-consistency`

No manual skill invocation is needed. Just describe your task.

## Tips

- **Dry-run:** All write scripts default to dry-run mode. Add `--apply` to commit changes.
- **PYTHONPATH:** When running helper scripts manually, set `PYTHONPATH=.` from the skill pack or
  installed scripts root directory.
- **disable-model-invocation:** Skills with write operations use `disable-model-invocation: true`
  to prevent autonomous writes. You must approve each modification.
- **allowed-tools:** Read-only analysis skills use `allowed-tools: Read Grep Bash(python *)` to
  scope tool access to safe operations.
- **Backups:** All write scripts call `shutil.copy2` to create a `.bak` before any modification.
  Find backups beside the original file (e.g., `Items.json.bak`).

## Example Prompts

Copy-paste these into Claude Code with your RPG Maker project open:

**Dialog extraction and drafting:**

> "Extract all dialog for the Guard NPC on Map001 and draft two new lines where he mentions the
> locked dungeon door."

Claude Code uses `extract_npc_lines.py` to gather existing Guard dialog, matches the established
voice, and drafts new lines as a **draft for your review** before calling `inject_dialog.py`.

**Event scaffolding and validation:**

> "Scaffold a chest event that gives the player item ID 3 (Silver Key) and then validate the
> project for broken references."

Claude Code generates the event JSON using the chest pattern from `rpgmaker-events`, adds it to
the target map in dry-run mode, then runs `validate_project.py` to confirm no orphaned references.
All output is a **draft for your review**.

**Full consistency check:**

> "Run a full project consistency check and summarize any orphaned references or switch conflicts."

Claude Code runs `validate_project.py --project .` which calls all four sub-validators in sequence
and produces a structured markdown report. Findings are presented as a **draft report for your
review** — no automatic repairs are made without your approval.
