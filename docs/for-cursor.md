# Using RPG Maker Agent Skills with Cursor

## Installation

Run the installer on macOS or Linux:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/nightquill/rpgmaker-agent-skills/main/install.sh)
```

On Windows (PowerShell):

```powershell
irm https://raw.githubusercontent.com/nightquill/rpgmaker-agent-skills/main/install.ps1 | iex
```

For Cursor, copy the skill directories to `.cursor/skills/`:

```bash
mkdir -p .cursor/skills
cp -r ~/.claude/skills/rpgmaker-* .cursor/skills/
```

Or reference the skill files directly from your Cursor rules configuration.

## Configuring Cursor Rules

Cursor's rules system can reference `SKILL.md` files to add context to every session. Add entries
to `.cursor/rules/` that include the relevant skill:

```
# .cursor/rules/rpgmaker.mdc

---
description: RPG Maker MV/MZ project rules
globs: ["data/*.json", "*.rpgproject", "*.rmmzproject"]
---

@.cursor/skills/rpgmaker-core/SKILL.md
@.cursor/skills/rpgmaker-dialog/SKILL.md
```

Adjust which skill files you include based on the work in each session. Including all five skills
at once will consume more context — load only what you need.

## Tips

- **Rules vs. skills:** Cursor's `.cursor/rules/` is the most reliable way to attach skill context.
  Drop a rule file per domain (dialog, database, events, consistency) so you can enable them
  selectively.
- **Inline editing:** When using Cursor's inline editing (Cmd+K), add "following RPG Maker data
  safety rules" to your prompt to trigger the skill constraints.
- **Dry-run:** All write scripts default to dry-run mode. Always review the diff in the terminal
  before adding `--apply`.
- **Backups:** Every write script creates a `.bak` beside the original file before modifying it.
- **PYTHONPATH:** Run scripts with `PYTHONPATH=.` from your project root or the skill pack root.

## Example Prompts

Use these in Cursor Chat or inline edit with your RPG Maker project open:

**NPC voice matching:**

> "Look at the Merchant NPC's existing dialog in Map003.json and draft three new lines for a
> haggling sequence. Match his gruff, reluctant tone. Format as RPG Maker show-text event commands."

Cursor uses the `rpgmaker-dialog` skill context to format dialog correctly, preserving text escape
codes. The output is a **draft for your review** — apply it with `inject_dialog.py --apply` only
when satisfied.

**Event pattern generation:**

> "Generate a locked-door event for Map002 position (15, 8). The door should require self-switch A
> to be ON (key collected), and show a 'The door is locked' message otherwise."

Cursor uses the door pattern from `rpgmaker-events` to produce the correct event JSON structure.
Output is a **draft for your review** — paste into the target map JSON after verifying the
dry-run diff.

**Project-wide consistency check:**

> "Run validate_project.py on the current project and summarize any errors or warnings."

Cursor runs the script in its terminal panel and interprets the markdown report. Findings are
presented as a **draft for your review** — no automatic repairs are made without your approval.
