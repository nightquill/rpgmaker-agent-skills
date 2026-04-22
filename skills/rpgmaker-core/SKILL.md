---
name: rpgmaker-core
description: >-
  Use this skill when working with any RPG Maker MV or MZ project. Triggers:
  presence of a Game.rpgproject or Game.rmmzproject manifest, data/*.json
  files named Actors.json/Skills.json/Items.json/Enemies.json/MapInfos.json,
  or when the user mentions RPG Maker, RPGMaker, MV, MZ, JRPG development,
  or narrative RPG in a project containing these files. Provides: project
  structure overview, MV/MZ detection, safety rules (MapInfos.json append-only,
  ID non-renumbering, dry-run first, backup before write).
license: MIT
metadata:
  version: "1.0.0"
  author: "nightquill"
compatibility: "Designed for Claude Code and compatible agents supporting the Agent Skills open standard"
---

# RPG Maker Core Skill

This skill provides the safety foundation for all RPG Maker MV and MZ agent
interactions. Load it first whenever you are working with any RPG Maker project.
It teaches you how the project is structured, which rules you must never break,
and where to find detailed reference docs.

All modifications you suggest are **drafts** for the developer to review and
approve — never authoritative decisions. See the "All AI outputs are drafts"
section below.

---

## MV/MZ Detection

Before doing anything, determine the engine version.

| Manifest file present | Version |
|----------------------|---------|
| `Game.rmmzproject`   | MZ      |
| `Game.rpgproject`    | MV      |
| Both present         | MZ (prefer MZ per spec) |
| Neither              | Error — not an RPG Maker project |

**Use `scripts/lib/project_detect.py`:**

```bash
python -m scripts.lib.project_detect --project-path /path/to/project
# Outputs: MV   or   MZ
```

State the detected version at the top of every work session comment:
`# Working on RPG Maker MV project at /path/to/project`

---

## Project Structure

```
YourGame/
├── Game.rpgproject       # MV: project manifest
├── Game.rmmzproject      # MZ: project manifest (replaces Game.rpgproject)
├── data/                 # All JSON database files
│   ├── Actors.json
│   ├── Classes.json
│   ├── Skills.json
│   ├── Items.json
│   ├── Weapons.json
│   ├── Armors.json
│   ├── Enemies.json
│   ├── Troops.json
│   ├── States.json
│   ├── Animations.json
│   ├── Tilesets.json
│   ├── CommonEvents.json
│   ├── System.json
│   ├── MapInfos.json     # Map tree — append-only (see Critical Safety Rules)
│   ├── Map001.json       # Three-digit zero-padded map files
│   ├── Map002.json
│   └── ...
├── js/
│   ├── plugins/          # js/plugins/ — JavaScript plugin files (*.js)
│   └── plugins.js        # Plugin manifest (load order + config)
├── img/
│   ├── faces/            # NPC face portraits
│   ├── characters/       # Character walk sprites
│   ├── sv_actors/        # Side-view battler sprites
│   ├── pictures/         # In-game picture displays
│   └── ...
└── audio/
    ├── bgm/              # Background music
    ├── bgs/              # Background sounds
    ├── me/               # Music effects (fanfares, game over)
    └── se/               # Sound effects
```

---

## Critical Safety Rules

These rules exist because RPG Maker's JSON files use **positional IDs** — the
array index *is* the ID. Breaking these rules corrupts references silently, with
no error at load time.

### Rule 1: MapInfos.json is append-only

`data/MapInfos.json` is the map tree the RPG Maker editor uses to display and
navigate maps. **Never delete or reorder entries.**

- Entries are indexed by their position in the array.
- When a map is deleted in the editor, its slot becomes `null` — not removed.
- New maps are always appended at the end.
- **Deleting or reordering breaks the editor's map tree, often silently.**

### Rule 2: Never renumber IDs

All database arrays (`Actors.json`, `Skills.json`, `Items.json`, `Enemies.json`,
`Weapons.json`, `Armors.json`, `Classes.json`, `Troops.json`, `States.json`,
`Animations.json`, `Tilesets.json`, `CommonEvents.json`) use **positional
indexing**:

- **Index 0 is always `null`.** This is required by RPG Maker. Do not remove it.
- Each entry's `id` field equals its array index.
- **Changing any `id` or reordering entries breaks every cross-file reference
  silently.**

**Safe operations:** Only *append* new entries. Set deleted entries to `null`
(tombstone) rather than removing them. Never shift, sort, or compact the array.

### Rule 3: ID references are everywhere

Cross-file references are encoded as integer IDs throughout the project:

| Reference type | Example |
|---------------|---------|
| Dialog text code | `\N[1]` — actor name lookup by ID |
| Actor's class | `"classId": 2` in Actors.json |
| Skill animation | `"animationId": 5` in Skills.json |
| Event condition | `"actorId": 1` in event page condition |
| Item change command | item ID 3 in `Change Items` event command |

One wrong ID introduces silent data corruption that only surfaces at runtime.

---

## Safety Principles

### Dry-run first

**All write scripts default to preview mode.** Use `--apply` to actually write.

```bash
# Preview what would change (safe, no file writes):
python scripts/inject_dialog.py --project . --target common-event:1 ...

# Actually write the changes:
python scripts/inject_dialog.py --project . --target common-event:1 ... --apply
```

Never skip the preview. The dry-run output uses "Draft preview" and "Would
modify" language so you and the developer can review before committing.

### Backup before write

Every write operation creates a `.bak` copy of the original file before
modifying it. This is enforced by `scripts/lib/safe_write.py`:

```python
# safe_write.py creates filepath + ".bak" via shutil.copy2 before writing
```

If you detect `.bak` files after a write, offer to clean them up after the
developer confirms the changes are correct.

### Validate after write

Run schema validation on any modified JSON file immediately after writing. The
schemas in `schemas/*.schema.json` cover all MV data file types.

```bash
python -c "
import json, jsonschema, pathlib
schema = json.loads(pathlib.Path('schemas/actors.schema.json').read_text())
data   = json.loads(pathlib.Path('data/Actors.json').read_text())
jsonschema.validate(data, schema)
print('Valid')
"
```

### Preserve formatting

RPG Maker exports JSON with a specific indentation style. When editing,
detect and preserve the existing indentation — do not reformat files unless the
developer explicitly requests it. Use `load_json_preserving_format()` from
`scripts/lib/safe_write.py` to detect indent width automatically.

### Re-open project warning

Changes to `data/*.json` files **do not appear** in a running RPG Maker editor.
Always remind the developer: *close and reopen the project in RPG Maker to see
changes.*

---

## The `safe_write.py` Library

`scripts/lib/safe_write.py` is the enforcement mechanism for all safety rules.
Every write script in this skill pack uses it. Key functions:

| Function | Purpose |
|---------|---------|
| `load_json_preserving_format(filepath)` | Load JSON, detect indentation |
| `validate_positional_array(data, label)` | Assert index-0 null, IDs match indexes |
| `validate_no_id_changes(original, modified, label)` | Assert no IDs changed, array not shortened |
| `safe_write(filepath, original, modified, apply, ...)` | Validate + backup + write (dry-run by default) |
| `add_argparse_write_args(parser)` | Add standard `--apply` flag to argparse |

---

## Navigation

Detailed reference docs for this skill:

- [MV Data File Quick Reference](references/mv-schema.md) — field tables for
  every data file type in RPG Maker MV
- [MZ Differences from MV](references/mz-schema.md) — only what changes in MZ;
  manifest, plugin commands, new fields
- [Plugin Command Format](references/plugin-format.md) — MV code 356 vs MZ code
  357 with JSON examples
- [Common Pitfalls](references/common-pitfalls.md) — table of agent mistakes and
  how to avoid them

Shared references used by other skills in this pack:

- [Text Escape Codes](../shared/references/text-codes.md) — `\N[id]`, `\V[id]`,
  `\C[n]`, etc.
- [Event Command Codes](../shared/references/event-command-codes.md) — 101 Show
  Text, 401 Text Line, 102 Show Choices, etc.

---

## All AI Outputs Are Drafts

All modifications suggested or generated by this skill — and any skill in this
pack — are **drafts for the developer to review**. They are never authoritative
decisions about the developer's game.

The developer is the author. The agent is a tool that produces drafts.

- Never auto-apply changes without explicit `--apply` confirmation.
- Never mass-edit database entries without showing before/after for each change.
- Frame all generated content with language like "Here is a draft — edit as
  needed before accepting."
- If you notice a potential issue outside the stated task scope, surface it as
  an observation, not as an automatic fix.
