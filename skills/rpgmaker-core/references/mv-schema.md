# RPG Maker MV — Data File Quick Reference

All database files are JSON arrays where **index 0 is always `null`**. Each
entry's `id` field equals its array index. Never renumber. New entries must be
appended; never insert in the middle.

---

## Actors.json

Playable characters. Referenced by event conditions (`actorId`), dialog face
images, and equipment.

| Field | Type | Notes |
|-------|------|-------|
| `id` | integer | Array index. Never change. |
| `name` | string | Display name. Used by `\N[id]` text code. |
| `nickname` | string | Short alias shown in status screen. |
| `classId` | integer | References Classes.json by ID. |
| `initialLevel` | integer | Starting level (1–99). |
| `maxLevel` | integer | Level cap (1–99). |
| `profile` | string | Long bio shown in status screen. |
| `characterName` | string | Walk sprite sheet filename (no extension). |
| `characterIndex` | integer | Position in sprite sheet (0–7, left→right top→bottom). |
| `faceName` | string | Face portrait sheet filename (no extension). |
| `faceIndex` | integer | Position in face sheet (0–7). |
| `equips` | integer[5] | Starting equipment IDs: [weapon, shield, head, body, accessory]. 0 = none. |
| `traits` | array | Trait objects (element rates, attack element, etc.). |
| `note` | string | Plugin notetag field. **Never overwrite.** |

> **note field:** Plugins use `<tag>value</tag>` syntax in this string. If you
> add plugin notetags, append to the existing value — never replace it.

---

## Skills.json

Abilities usable in battle or from the menu.

| Field | Type | Notes |
|-------|------|-------|
| `id` | integer | Array index. Never change. |
| `name` | string | Display name. |
| `iconIndex` | integer | Icon sheet index. |
| `description` | string | Tooltip shown in menus. |
| `stypeId` | integer | Skill type (references System.json skillTypes). |
| `scope` | integer | Target (0=none, 1=enemy, 2=all enemies, 7=ally, 11=all). |
| `occasion` | integer | Usability (0=always, 1=battle, 2=menu, 3=never). |
| `mpCost` | integer | MP consumed on use. |
| `tpCost` | integer | TP consumed on use. |
| `animationId` | integer | References Animations.json by ID. |
| `damage.type` | integer | 0=none, 1=HP damage, 3=HP recover, 5=MP damage. |
| `damage.elementId` | integer | References System.json elements list. |
| `damage.formula` | string | JS expression. `a`=attacker, `b`=target. E.g. `a.atk * 4 - b.def * 2`. |
| `damage.variance` | integer | Damage variance percentage (0–100). |
| `effects` | array | State adds/removes, stat changes, etc. |
| `note` | string | Plugin notetag field. **Never overwrite.** |

---

## Items.json

Key items, consumables, and tools.

| Field | Type | Notes |
|-------|------|-------|
| `id` | integer | Array index. Never change. |
| `name` | string | Display name. Referenced by `\I[id]` icon code. |
| `iconIndex` | integer | Icon sheet index. |
| `description` | string | Tooltip shown in menus. |
| `price` | integer | Shop buy price (sell = price / 2). |
| `consumable` | boolean | True = removed from inventory after use. |
| `itypeId` | integer | 1=regular, 2=key item. Key items can't be sold. |
| `scope` | integer | Target (same values as Skills.json scope). |
| `occasion` | integer | Usability (same values as Skills.json). |
| `effects` | array | HP recover, MP recover, state add/remove, etc. |
| `note` | string | Plugin notetag field. **Never overwrite.** |

---

## Enemies.json

Enemy battlers for combat.

| Field | Type | Notes |
|-------|------|-------|
| `id` | integer | Array index. Never change. |
| `name` | string | Display name. |
| `battlerName` | string | Battle sprite filename in `img/enemies/` (no extension). |
| `battlerHue` | integer | Hue rotation 0–360 applied to battler sprite. |
| `params` | integer[8] | Stats array: [mhp, mmp, atk, def, mat, mdf, agi, luk] |
| `exp` | integer | Experience awarded on defeat. |
| `gold` | integer | Gold awarded on defeat. |
| `dropItems` | array | Drop item definitions with kind, dataId, denominator. |
| `actions` | array | Battle action patterns with skill IDs and conditions. |
| `traits` | array | Trait objects (element rates, immunities, etc.). |
| `note` | string | Plugin notetag field. **Never overwrite.** |

> **params array indexes:** 0=mhp, 1=mmp, 2=atk, 3=def, 4=mat, 5=mdf, 6=agi, 7=luk

---

## Weapons.json / Armors.json

Equipment items.

| Field | Type | Notes |
|-------|------|-------|
| `id` | integer | Array index. Never change. |
| `name` | string | Display name. |
| `iconIndex` | integer | Icon sheet index. |
| `description` | string | Tooltip shown in menus. |
| `price` | integer | Buy price. |
| `params` | integer[8] | Stat bonuses: [mhp, mmp, atk, def, mat, mdf, agi, luk] |
| `traits` | array | Trait objects. |
| `etypeId` | integer | Equipment slot (1=weapon, 2=shield, 3=head, 4=body, 5=accessory). |
| `wtypeId` | integer | **Weapons only.** Weapon type ID (references System.json weaponTypes). |
| `atypeId` | integer | **Armors only.** Armor type ID (references System.json armorTypes). |
| `animationId` | integer | **Weapons only.** Attack animation ID. |
| `note` | string | Plugin notetag field. **Never overwrite.** |

---

## CommonEvents.json

Reusable event scripts callable from anywhere.

| Field | Type | Notes |
|-------|------|-------|
| `id` | integer | Array index. Never change. |
| `name` | string | Display name (editor only). |
| `trigger` | integer | 0=none (call-only), 1=autorun, 2=parallel. |
| `switchId` | integer | Switch ID that enables autorun/parallel trigger. 0 = always active. |
| `list` | array | Ordered array of event command objects (see below). |

**Event command object:**

```json
{ "code": 101, "indent": 0, "parameters": ["Face", 0, 0, 2] }
```

Every event list **must end** with a code-0 terminator:

```json
{ "code": 0, "indent": 0, "parameters": [] }
```

**Never insert commands after the code-0 terminator.** Append before it.

---

## MapInfos.json

Map tree displayed in the RPG Maker editor.

| Field | Type | Notes |
|-------|------|-------|
| `id` | integer | Map ID. Equals array index. |
| `name` | string | Display name in the editor map tree. |
| `parentId` | integer | Parent map ID (0 = root). |
| `order` | integer | Display order within siblings. |
| `expanded` | boolean | Editor tree node expansion state. |

> **APPEND ONLY.** Deleted maps leave `null` at their index. Never reorder.
> Array index IS the map ID used in `Transfer Player` events.

---

## MapXXX.json

Individual map data files (e.g., `Map001.json`). Filename uses three-digit
zero-padded IDs matching MapInfos.json entries.

| Field | Type | Notes |
|-------|------|-------|
| `width` | integer | Map width in tiles. |
| `height` | integer | Map height in tiles. |
| `tilesetId` | integer | References Tilesets.json by ID. |
| `displayName` | string | Name shown on-screen when entering the map. |
| `scrollType` | integer | 0=no scroll, 1=vertical loop, 2=horizontal loop, 3=both. |
| `data` | integer[] | Flat tile layer data array (6 layers × width × height). |
| `events` | array | Event objects. Index 0 is null; each entry's `id` = its index. |

**Map event object** (abbreviated):

```json
{
  "id": 1,
  "name": "Innkeeper",
  "x": 5, "y": 3,
  "pages": [ { "conditions": {}, "list": [...], "moveType": 0, ... } ]
}
```

---

## System.json

Global game settings. A single object (not an array).

| Field | Type | Notes |
|-------|------|-------|
| `gameTitle` | string | Game title shown on title screen. |
| `switches` | string[] | Switch name list. Index = switch ID. Index 0 is empty string. |
| `variables` | string[] | Variable name list. Index = variable ID. Index 0 is empty string. |
| `weaponTypes` | string[] | Weapon type names. Index = wtypeId. Index 0 is empty string. |
| `armorTypes` | string[] | Armor type names. Index = atypeId. Index 0 is empty string. |
| `elements` | string[] | Element names (Fire, Ice, etc.). Index = elementId. Index 0 is empty. |
| `skillTypes` | string[] | Skill type names. Index = stypeId. Index 0 is empty string. |
| `equipTypes` | string[] | Equipment slot names. Index = etypeId. |
| `terms` | object | UI vocabulary (e.g., `terms.basic` for stat names). |
| `startMapId` | integer | Map ID where new game begins. |
| `startX` | integer | Starting X tile coordinate. |
| `startY` | integer | Starting Y tile coordinate. |

> Switches and variables use name arrays indexed by ID. When you add a switch,
> append its name to the `switches` array. The new ID = the new array length - 1.
