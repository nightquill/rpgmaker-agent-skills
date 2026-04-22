# Skill Schema Reference

Skills are abilities usable in battle or from the menu. Referenced by class
learnings, enemy actions, and item/equipment effects.

## Fields

| Field | Type | Default | Notes |
|-------|------|---------|-------|
| `id` | integer | — | Array index. **Never change.** |
| `name` | string | `""` | Display name shown in menus. |
| `iconIndex` | integer | `0` | Icon sheet index for display. |
| `description` | string | `""` | Tooltip shown in skill menus. |
| `stypeId` | integer | `1` | Skill type — references `System.json` `skillTypes` array. |
| `scope` | integer | `0` | Target selection (see table below). |
| `occasion` | integer | `0` | When usable: 0=always, 1=battle only, 2=menu only, 3=never. |
| `speed` | integer | `0` | Speed modifier added to AGI for turn order. |
| `successRate` | integer | `100` | Hit chance percentage (0–100). |
| `repeats` | integer | `1` | Number of times the skill hits. |
| `tpGain` | integer | `0` | TP gained on use. |
| `hitType` | integer | `0` | 0=certain hit, 1=physical (uses ATK), 2=magical (uses MAT). |
| `animationId` | integer | `0` | References `Animations.json` by ID. |
| `damage` | object | — | Damage sub-object (see below). |
| `effects` | array | `[]` | State adds/removes, stat buffs, special effects. |
| `mpCost` | integer | `0` | MP consumed on use. |
| `tpCost` | integer | `0` | TP consumed on use. |
| `message1` | string | `""` | Battle message line 1 (e.g., "casts Fire!"). |
| `message2` | string | `""` | Battle message line 2. |
| `note` | string | `""` | Plugin notetag field. **Never overwrite.** |

> **id field**: This is the array index. Changing it breaks class learnings,
> enemy action references, and any event that references this skill by ID.

> **note field**: Opaque string used by plugin ecosystems (Yanfly, VisuStella).
> Never parse, strip, or validate.

## Scope Codes

| Code | Target |
|------|--------|
| 0 | None |
| 1 | One enemy |
| 2 | All enemies |
| 3 | One random enemy |
| 4 | Two random enemies |
| 5 | Three random enemies |
| 6 | Four random enemies |
| 7 | One ally |
| 8 | All allies |
| 9 | One ally (dead) |
| 10 | All allies (dead) |
| 11 | The user |

## Damage Sub-Object

| Field | Type | Notes |
|-------|------|-------|
| `damage.type` | integer | 0=none, 1=HP damage, 2=MP damage, 3=HP recover, 4=MP recover, 5=HP drain, 6=MP drain |
| `damage.elementId` | integer | References `System.json` `elements` array. 0 = normal attack element. |
| `damage.formula` | string | **JavaScript expression** — `a` = attacker, `b` = target. E.g., `a.atk * 4 - b.def * 2`. |
| `damage.variance` | integer | Damage variance percentage (0–100). |
| `damage.critical` | boolean | Whether this skill can critical hit. |

> **damage.formula pitfall**: This is JavaScript, not Python. `b.def` uses
> `def` which is a Python keyword. Never `eval()` formula strings directly in
> Python without variable substitution first.
