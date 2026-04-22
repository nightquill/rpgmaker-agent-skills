# Item Schema Reference

Items are consumable or key items usable from the menu or in battle. Referenced
by enemy drop tables and shop event commands.

## Fields

| Field | Type | Default | Notes |
|-------|------|---------|-------|
| `id` | integer | — | Array index. **Never change.** |
| `name` | string | `""` | Display name shown in inventory. |
| `iconIndex` | integer | `0` | Icon sheet index for display. |
| `description` | string | `""` | Tooltip shown in item menus. |
| `itypeId` | integer | `1` | Item type: 1=regular item, 2=key item. |
| `scope` | integer | `0` | Target selection (same codes as Skills). |
| `occasion` | integer | `0` | When usable: 0=always, 1=battle only, 2=menu only, 3=never. |
| `consumable` | boolean | `true` | Whether the item is consumed on use. |
| `price` | integer | `0` | Shop buy price. Sell price is `price / 2` by default. |
| `animationId` | integer | `0` | References `Animations.json` by ID. |
| `damage` | object | — | Damage sub-object (same structure as Skills). |
| `effects` | array | `[]` | State adds/removes, stat recovery, etc. |
| `note` | string | `""` | Plugin notetag field. **Never overwrite.** |

> **id field**: This is the array index. Changing it breaks enemy drop tables
> (`dropItems.dataId` where `kind == 1`), shop commands, and event item checks.

> **note field**: Opaque string used by plugin ecosystems (Yanfly, VisuStella).
> Never parse, strip, or validate.

## itypeId Codes

| Code | Meaning | Behavior |
|------|---------|----------|
| 1 | Regular item | Appears in "Items" tab. Can be sold. Consumed based on `consumable` flag. |
| 2 | Key item | Appears in "Key Items" tab. Cannot be sold. Not consumed on use. |

## Effects Array

Each element in `effects` has this structure:

```json
{ "code": 11, "dataId": 0, "value1": 0.5, "value2": 0 }
```

Common effect codes:
- `11`: Recover HP (`value1` = rate, `value2` = flat amount)
- `12`: Recover MP
- `21`: Add state (`dataId` = state ID from States.json)
- `22`: Remove state
