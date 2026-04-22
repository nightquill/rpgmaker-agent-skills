# rpgmaker-agent-skills

> Stop clicking through RPG Maker menus. Tell your AI agent what you want and it edits the game files directly.

[![CI](https://github.com/nightquill/rpgmaker-agent-skills/actions/workflows/ci.yml/badge.svg)](https://github.com/nightquill/rpgmaker-agent-skills/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

## The Problem

RPG Maker MV and MZ store everything in JSON files, but the editor forces you through
click-heavy menus to change them. Adding one skill means filling out 15+ fields across
multiple tabs. Writing NPC dialog means clicking into each event, each page, each text
command. Wiring a shop event means memorizing command codes.

## The Solution

Install these skills into your AI coding agent. Then just say what you want:

### Write dialog by describing it

> "The blacksmith should greet the player, complain about the heat, and offer to forge
> something if they bring 3 Iron Ore."

The agent writes the dialog directly into your CommonEvents or Map event JSON — proper
Show Text commands, text codes preserved, character voice maintained. No editor needed.

### Add game content by describing it

> "Add a fire spell called Inferno that costs 24 MP, targets all enemies, uses the
> formula `a.mat * 8 - b.mdf * 2`, and has a 30% chance to inflict Burn state."

The agent appends the skill entry to `Skills.json` with every field filled correctly —
damage type, scope, effects array, cost, formula. One sentence replaces 15 menu clicks.

### Build events by describing what happens

> "Create a treasure chest on Map 3 that gives the player a Silver Key, shows a message,
> then disables itself so it can't be opened twice."

The agent scaffolds the full event command sequence — Control Self Switch, Conditional
Branch, Change Items, Show Text — as valid JSON ready to place in your map file.

### Catch bugs the editor never shows you

> "Check if anything in my project references items or skills that don't exist."

The agent scans every map, every common event, and every database file for orphaned
references, switch collisions, and broken text codes. RPG Maker won't warn you about
these — you'd find them as crashes during playtesting.

## How It Works

These are [Agent Skills](https://agentskills.io) — structured knowledge files that teach
AI coding agents how RPG Maker's JSON data files work. When installed, your agent
understands event command codes, database schemas, text escape sequences, and the safety
rules that prevent silent data corruption.

Helper scripts handle the actual file operations: extracting dialog, injecting text
commands, appending database entries, scaffolding events, and validating cross-file
references. Every write operation is **dry-run by default** with automatic `.bak` backups.

## Install

### macOS / Linux

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/nightquill/rpgmaker-agent-skills/main/install.sh)
```

### Windows (PowerShell)

```powershell
irm https://raw.githubusercontent.com/nightquill/rpgmaker-agent-skills/main/install.ps1 | iex
```

The installer prompts for global (`~/.claude/skills/`) or local (`./.claude/skills/`) installation.

## Skills

| Skill | What the agent can do with it |
|-------|-------------------------------|
| `rpgmaker-core` | Detect MV vs MZ, enforce data safety rules, understand file structure |
| `rpgmaker-dialog` | Extract NPC lines, write new dialog, inject text commands into events |
| `rpgmaker-database` | Add skills/enemies/items, check stat balance, validate against schemas |
| `rpgmaker-events` | Scaffold chest/shop/inn/door/cutscene events, track switches and variables |
| `rpgmaker-consistency` | Find orphaned references, detect switch collisions, validate the full project |

## Safety

RPG Maker projects break silently when IDs shift or arrays get reordered. Every tool in
this pack enforces:

- **Dry-run by default** — see what would change before it changes
- **Automatic backups** — `.bak` file created before every write
- **Append-only writes** — new entries go at the end, existing IDs never move
- **Index 0 is null** — the MV/MZ convention is preserved automatically

The agent drafts. You review and apply. Nothing writes to your project without `--apply`.

## Supported Agents

| Agent | Docs | Auto-loads skills? |
|-------|------|--------------------|
| [Claude Code](https://claude.com/claude-code) | [`docs/for-claude-code.md`](docs/for-claude-code.md) | Yes |
| [OpenAI Codex](https://openai.com/codex) | [`docs/for-codex.md`](docs/for-codex.md) | Via configuration |
| [Cursor](https://cursor.com) | [`docs/for-cursor.md`](docs/for-cursor.md) | Via rules |

## FAQ

**MV or MZ?** Both. The skills auto-detect from `Game.rpgproject` (MV) or `Game.rmmzproject` (MZ). The formats share ~90% of their schemas.

**Do I need an API key?** For your agent (Claude, OpenAI, etc.), yes. The skill pack itself is just Markdown and Python — no API keys, no external services.

**Will this break my project?** Every write is dry-run by default with backups. IDs are never renumbered. But you should still use version control.

**Can I use this commercially?** Yes. MIT license.

## Getting Started

See [docs/getting-started.md](docs/getting-started.md) for a full walkthrough.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

[MIT](LICENSE)
