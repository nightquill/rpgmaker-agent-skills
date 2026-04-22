# Enemy Schema Reference

Enemies are battle opponents. Referenced by troop member lists and encountered
during random or evented battles.

## Fields

| Field | Type | Default | Notes |
|-------|------|---------|-------|
| `id` | integer | — | Array index. **Never change.** |
| `name` | string | `""` | Display name shown in battle. |
| `battlerName` | string | `""` | Battler sprite filename in `img/enemies/` (no extension). |
| `battlerHue` | integer | `0` | Hue rotation for battler sprite (0–360). |
| `params` | integer[8] | `[0,0,0,0,0,0,0,0]` | **Base stats** (see params table below). |
| `exp` | integer | `0` | Experience points awarded on defeat. |
| `gold` | integer | `0` | Gold awarded on defeat. |
| `dropItems` | array | `[]` | Items dropped on defeat (see structure below). |
| `actions` | array | `[]` | AI action patterns (see structure below). |
| `traits` | array | `[]` | Trait objects (element rates, attack element, etc.). |
| `note` | string | `""` | Plugin notetag field. **Never overwrite.** |

> **id field**: This is the array index. Changing it breaks troop member
> references and any event that checks enemy state by ID.

> **note field**: Opaque string used by plugin ecosystems (Yanfly, VisuStella).
> Never parse, strip, or validate.

## Params Array (Base Stats)

Unlike weapons and armors, enemy `params` are **absolute base stats**, not
bonuses.

| Index | Stat | Typical Early-Game | Typical Mid-Game |
|-------|------|--------------------|--------------------|
| 0 | Max HP | 30–100 | 500–2000 |
| 1 | Max MP | 0–50 | 100–500 |
| 2 | ATK | 5–15 | 30–80 |
| 3 | DEF | 5–15 | 20–60 |
| 4 | MAT | 5–15 | 30–80 |
| 5 | MDF | 5–15 | 20–60 |
| 6 | AGI | 5–15 | 20–50 |
| 7 | LUK | 5–10 | 10–30 |

## Drop Items Structure

Each element in `dropItems`:

```json
{ "dataId": 1, "denominator": 8, "kind": 1 }
```

| Field | Meaning |
|-------|---------|
| `kind` | 1 = Item (Items.json), 2 = Weapon (Weapons.json), 3 = Armor (Armors.json) |
| `dataId` | The ID in the corresponding database file. |
| `denominator` | Drop chance is `1 / denominator`. E.g., `8` = 12.5% chance. |

> **kind maps to different files.** `kind: 1` references Items.json, `kind: 2`
> references Weapons.json, `kind: 3` references Armors.json. Getting the kind
> wrong means the drop references the wrong database entirely.

## Actions Structure

Each element in `actions`:

```json
{
  "conditionParam1": 0,
  "conditionParam2": 0,
  "conditionType": 0,
  "rating": 5,
  "skillId": 1
}
```

| Field | Meaning |
|-------|---------|
| `skillId` | References `Skills.json` by ID. `1` = basic attack. |
| `rating` | Priority weight (1–10). Higher = more likely to use. |
| `conditionType` | 0=always, 1=turn-based, 2=HP-based, 3=MP-based, 4=state-based, 5=party level, 6=switch |
| `conditionParam1/2` | Condition parameters (meaning depends on `conditionType`). |
