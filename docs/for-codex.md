# Using RPG Maker Agent Skills with OpenAI Codex

## Installation

Run the installer on macOS or Linux:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/nightquill/rpgmaker-agent-skills/main/install.sh)
```

On Windows (PowerShell):

```powershell
irm https://raw.githubusercontent.com/nightquill/rpgmaker-agent-skills/main/install.ps1 | iex
```

For Codex, copy the skills to `.codex/skills/` or configure them via your Codex settings file.
The installer places skills in `.claude/skills/` by default; for Codex, copy or symlink the skill
directories:

```bash
mkdir -p .codex/skills
cp -r ~/.claude/skills/rpgmaker-* .codex/skills/
```

Or reference the install path in your Codex configuration if it supports custom skill directories.

## How Skills Load

Codex skill loading varies by configuration. Reference the skills in your task description or
Codex configuration file. When you mention "RPG Maker", "MV", "MZ", or describe dialog, database,
or event work, Codex will use the relevant skill context.

If your Codex setup supports auto-loading from a skills directory, point it at the directory
containing the five `rpgmaker-*` skill folders. Each folder contains a `SKILL.md` with the
triggers and rules the agent needs.

## Tips

- **Sandbox filesystem access:** Codex's sandbox may limit filesystem access. Run helper scripts
  (`extract_npc_lines.py`, `validate_project.py`, etc.) in a separate terminal and paste the output
  into your Codex prompt for the agent to interpret.
- **Dry-run first:** All write scripts default to dry-run mode. Review the diff before adding
  `--apply` to commit changes.
- **PYTHONPATH:** Set `PYTHONPATH=.` from the skill pack root when running scripts manually:
  `PYTHONPATH=. python skills/rpgmaker-dialog/scripts/extract_npc_lines.py --project /path/to/project`
- **Backups:** Every write script creates a `.bak` beside the original file before modifying it.

## Example Prompts

Copy-paste these as Codex task descriptions:

**Dialog drafting:**

> "The Innkeeper NPC in Map002 has three existing greeting lines. Draft two new lines for after
> the player completes the dungeon quest, matching her friendly-but-businesslike tone. Output as
> RPG Maker show-text event commands."

Codex uses the `rpgmaker-dialog` skill context to format the output correctly. All output is a
**draft for your review** — inject it using `inject_dialog.py --apply` only when satisfied.

**Database entry addition:**

> "Add a 'Silver Key' item to Items.json. It should be a key item (itypeId 2), price 0, not
> consumable. Use the safe-append pattern that never renumbers existing IDs."

Codex drafts the JSON entry and the `add_skill.py`-style insertion command. The modification is
a **draft for your review** before you apply it.

**Balance audit:**

> "Run a balance check on the weapons in Weapons.json. Flag any weapon whose attack stat is more
> than 2 standard deviations above the average for its level range."

Codex interprets the output of `balance_check.py` and summarizes outliers. The analysis is a
**draft for your review** — Codex does not modify database files without explicit approval.
