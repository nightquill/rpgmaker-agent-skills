# Armor Schema Reference

Armors are equippable items providing stat bonuses and traits. They occupy
equipment slots defined by `etypeId`. Referenced by actor `equips[1..4]` and
shop commands.

## Fields

| Field | Type | Default | Notes |
|-------|------|---------|-------|
| `id` | integer | — | Array index. **Never change.** |
| `name` | string | `""` | Display name shown in equipment menus. |
| `iconIndex` | integer | `0` | Icon sheet index for display. |
| `description` | string | `""` | Tooltip shown in menus. |
| `atypeId` | integer | `0` | Armor type — references `System.json` `armorTypes` array. |
| `etypeId` | integer | `2` | Equipment slot (see slot table below). |
| `params` | integer[8] | `[0,0,0,0,0,0,0,0]` | Stat **bonuses** (see params table below). |
| `price` | integer | `0` | Shop buy price. Sell price is `price / 2`. |
| `traits` | array | `[]` | Trait objects (element resistance, state resistance, etc.). |
| `note` | string | `""` | Plugin notetag field. **Never overwrite.** |

> **id field**: This is the array index. Changing it breaks actor `equips`
> references and enemy drop tables (`dropItems.dataId` where `kind == 3`).

> **note field**: Opaque string used by plugin ecosystems (Yanfly, VisuStella).
> Never parse, strip, or validate.

## Equipment Slot Codes (etypeId)

| Code | Slot | Actor equips Index |
|------|------|--------------------|
| 1 | Shield | `equips[1]` |
| 2 | Head | `equips[2]` |
| 3 | Body | `equips[3]` |
| 4 | Accessory | `equips[4]` |

> **etypeId determines the slot.** An armor with `etypeId: 4` is an accessory,
> regardless of its `atypeId` (armor type). Getting this wrong means the item
> appears in the wrong equipment slot.

## Params Array (Bonuses)

Armor `params` are **additive bonuses** — same semantics as weapons.

| Index | Stat | Typical Range | Example |
|-------|------|---------------|---------|
| 0 | Max HP bonus | 0–500 | `100` (heavy armor) |
| 1 | Max MP bonus | 0–100 | `20` (magic robe) |
| 2 | ATK bonus | 0 | Armors rarely add ATK |
| 3 | DEF bonus | 5–30 | `10` (leather shield) |
| 4 | MAT bonus | 0–20 | `5` (magic hat) |
| 5 | MDF bonus | 5–20 | `8` (blessed robe) |
| 6 | AGI bonus | 0–10 | `3` (light boots) |
| 7 | LUK bonus | 0–10 | `2` (lucky charm) |
