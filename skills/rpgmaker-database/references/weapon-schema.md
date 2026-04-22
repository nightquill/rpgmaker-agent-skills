# Weapon Schema Reference

Weapons are equippable items that provide stat bonuses and may modify attack
animation and element. Referenced by actor `equips[0]` and shop commands.

## Fields

| Field | Type | Default | Notes |
|-------|------|---------|-------|
| `id` | integer | — | Array index. **Never change.** |
| `name` | string | `""` | Display name shown in equipment menus. |
| `iconIndex` | integer | `0` | Icon sheet index for display. |
| `description` | string | `""` | Tooltip shown in menus. |
| `wtypeId` | integer | `0` | Weapon type — references `System.json` `weaponTypes` array. |
| `params` | integer[8] | `[0,0,0,0,0,0,0,0]` | Stat **bonuses** (see params table below). |
| `price` | integer | `0` | Shop buy price. Sell price is `price / 2`. |
| `animationId` | integer | `0` | Attack animation — references `Animations.json`. |
| `traits` | array | `[]` | Trait objects (attack element, attack state, etc.). |
| `note` | string | `""` | Plugin notetag field. **Never overwrite.** |

> **id field**: This is the array index. Changing it breaks actor `equips`
> references and enemy drop tables (`dropItems.dataId` where `kind == 2`).

> **note field**: Opaque string used by plugin ecosystems (Yanfly, VisuStella).
> Never parse, strip, or validate.

## Params Array (Bonuses)

Weapon `params` are **additive bonuses** applied on top of the actor's class
base stats — not absolute values.

| Index | Stat | Typical Range | Example |
|-------|------|---------------|---------|
| 0 | Max HP bonus | 0–500 | `0` (weapons rarely add HP) |
| 1 | Max MP bonus | 0–100 | `0` |
| 2 | ATK bonus | 5–50 | `10` (Short Sword) |
| 3 | DEF bonus | 0–10 | `0` |
| 4 | MAT bonus | 0–50 | `10` (Staff) |
| 5 | MDF bonus | 0–10 | `5` (Staff) |
| 6 | AGI bonus | 0–10 | `0` |
| 7 | LUK bonus | 0–10 | `0` |

> **params are bonuses, not base stats.** A weapon with `params[2] = 10` adds
> 10 ATK to the wielder's class curve value. Do not confuse with enemy `params`
> which are absolute base stats.
