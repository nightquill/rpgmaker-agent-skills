# Actor Schema Reference

Actors represent playable characters. Referenced by event conditions, dialog
face images (`\N[id]` text code), and party management commands.

## Fields

| Field | Type | Default | Notes |
|-------|------|---------|-------|
| `id` | integer | — | Array index. **Never change.** |
| `name` | string | `""` | Display name. Used by `\N[id]` text escape code. |
| `nickname` | string | `""` | Short alias shown in status screen. |
| `classId` | integer | `1` | References `Classes.json` by ID. Determines stat curves and learnable skills. |
| `initialLevel` | integer | `1` | Starting level (1–99). |
| `maxLevel` | integer | `99` | Level cap (1–99). |
| `profile` | string | `""` | Long bio shown in status screen. |
| `characterName` | string | `""` | Walk sprite sheet filename (no extension). |
| `characterIndex` | integer | `0` | Position in sprite sheet (0–7, left-to-right then top-to-bottom). |
| `faceName` | string | `""` | Face portrait sheet filename (no extension). |
| `faceIndex` | integer | `0` | Position in face sheet (0–7). |
| `equips` | integer[] | `[0,0,0,0,0]` | Starting equipment IDs: [weapon, shield, head, body, accessory]. `0` = none. |
| `traits` | array | `[]` | Trait objects (element rates, attack elements, etc.). |
| `note` | string | `""` | Plugin notetag field. **Never overwrite.** |

> **id field**: This is the array index. Changing it breaks all cross-file
> references silently — event conditions, party member checks, and `\N[id]`
> text codes will all point to the wrong character.

> **note field**: Opaque string used by plugin ecosystems (Yanfly, VisuStella).
> Never parse, strip, or validate. Append new tags — never replace existing
> content.

## Cross-References

- `classId` points to `Classes.json` — determines stat growth curves and which
  skills the actor learns at each level.
- `equips[0]` points to `Weapons.json` by ID (weapon slot).
- `equips[1..4]` point to `Armors.json` by ID (shield, head, body, accessory).
  A value of `0` means the slot is empty.
- `characterName` / `faceName` reference image files in `img/characters/` and
  `img/faces/` respectively. The index selects which character on the sheet.
