# Map Event Structure

This reference documents the structure of events in `MapXXX.json` files and
`CommonEvents.json`. Understanding this structure is required to read, write, or
validate event command lists without corrupting the project.

---

## Overview

`data/MapXXX.json` (e.g. `Map001.json`) is a single JSON object describing one
map. Its `events` field contains all events placed on that map. Each event has
one or more pages, and each page has a `list` of event commands.

`data/CommonEvents.json` uses the same `list` structure for command lists, but
events have no pages — they run directly when called.

---

## Top-Level Map Object

```json
{
  "displayName": "Village",
  "tilesetId": 1,
  "width": 20,
  "height": 15,
  "scrollType": 0,
  "specifyBattleback": false,
  "battleback1Name": "",
  "battleback2Name": "",
  "autoplayBgm": false,
  "bgm": {"name": "", "pan": 0, "pitch": 100, "volume": 90},
  "autoplayBgs": false,
  "bgs": {"name": "", "pan": 0, "pitch": 100, "volume": 90},
  "disableDashing": false,
  "note": "",
  "parallaxName": "",
  "parallaxLoopX": false,
  "parallaxLoopY": false,
  "parallaxSx": 0,
  "parallaxSy": 0,
  "parallaxShow": false,
  "encounterList": [],
  "encounterStep": 30,
  "events": [null, { ... }, { ... }]
}
```

The `events` field is the only field agents typically edit. All other fields
are map settings controlled via the RPG Maker editor.

---

## Event Object

Each non-null entry in `events` represents one event placed on the map.

```json
{
  "id": 1,
  "name": "Chest",
  "note": "",
  "x": 5,
  "y": 8,
  "pages": [ { ... }, { ... } ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `id` | int | Event ID — equals its array index (MV) or object key (MZ). **Never change.** |
| `name` | string | Human-readable label shown in the editor. Used by `event_traverse.py` as part of the source label. |
| `note` | string | Opaque notetag string. Do not parse or modify. |
| `x` | int | Tile X coordinate on the map. |
| `y` | int | Tile Y coordinate on the map. |
| `pages` | array | One or more event pages. RPG Maker activates the highest-index page whose conditions are met. |

---

## Event Page

Each page is an object with conditions, command list, movement settings, and
display settings. RPG Maker evaluates pages from last to first — the
highest-indexed page whose `conditions` are all satisfied is the active page.

```json
{
  "conditions": {
    "actorId": 1,
    "actorValid": false,
    "itemId": 1,
    "itemValid": false,
    "selfSwitchCh": "A",
    "selfSwitchValid": false,
    "switch1Id": 1,
    "switch1Valid": false,
    "switch2Id": 1,
    "switch2Valid": false,
    "variableId": 1,
    "variableValid": false,
    "variableValue": 0
  },
  "directionFix": false,
  "image": {
    "characterIndex": 0,
    "characterName": "",
    "direction": 2,
    "pattern": 0,
    "tileId": 0
  },
  "list": [ { ... }, { "code": 0, "indent": 0, "parameters": [] } ],
  "moveFrequency": 3,
  "moveRoute": {
    "list": [{"code": 0, "parameters": []}],
    "repeat": true,
    "skippable": false,
    "wait": false
  },
  "moveSpeed": 3,
  "moveType": 0,
  "priorityType": 1,
  "stepAnime": false,
  "through": false,
  "trigger": 0,
  "walkAnime": true
}
```

### conditions Object

| Field | Type | Description |
|-------|------|-------------|
| `switch1Valid` | bool | If true, page only activates when `switch1Id` is ON |
| `switch1Id` | int | Project switch ID to check (only used when `switch1Valid` is true) |
| `switch2Valid` | bool | If true, page only activates when `switch2Id` is ON |
| `switch2Id` | int | Project switch ID to check (only used when `switch2Valid` is true) |
| `selfSwitchValid` | bool | If true, page only activates when this event's `selfSwitchCh` is ON |
| `selfSwitchCh` | string | `"A"`, `"B"`, `"C"`, or `"D"` — always a string |
| `variableValid` | bool | If true, page only activates when the variable condition is met |
| `variableId` | int | Variable to check (only used when `variableValid` is true) |
| `variableValue` | int | Page activates when `variables[variableId] >= variableValue` |
| `actorValid` | bool | If true, page only activates when `actorId` is in the party |
| `actorId` | int | Actor to check |
| `itemValid` | bool | If true, page only activates when `itemId` is in inventory |
| `itemId` | int | Item to check |

All enabled conditions must be true simultaneously for the page to activate.
Disabled conditions (e.g. `switch1Valid: false`) are ignored regardless of the
corresponding ID value.

### trigger Codes

| Code | Name | Description |
|------|------|-------------|
| `0` | Action Button | Player must press the confirm button while facing the event |
| `1` | Player Touch | Fires when the player steps onto or into the event's tile |
| `2` | Event Touch | Fires when the event moves onto the player |
| `3` | Autorun | Fires automatically when the page is active; freezes all other event processing until complete |
| `4` | Parallel | Fires automatically and runs alongside other events without blocking |

### moveType Codes

| Code | Name |
|------|------|
| `0` | Fixed (does not move) |
| `1` | Random walk |
| `2` | Approach player |
| `3` | Custom (uses `moveRoute` object) |

### priorityType Codes

| Code | Name | Notes |
|------|------|-------|
| `0` | Below Characters | Renders under the player and NPCs |
| `1` | Same as Characters | Renders at the same layer; blocks passage |
| `2` | Above Characters | Renders above the player and NPCs |

---

## Command List Entry

Every entry in a `list` array has exactly three fields. This structure is
universal — it applies to map event pages, common events, and even move route
lists (which omit `indent`).

```json
{"code": 101, "indent": 0, "parameters": ["Actor1", 0, 0, 2]}
```

| Field | Type | Description |
|-------|------|-------------|
| `code` | int | Event command identifier. See `event-command-codes.md` for the full table. |
| `indent` | int | Nesting depth. 0 = top level. Increases by 1 for each conditional/loop block. |
| `parameters` | array | Arguments for this command. Content varies by code. |

The final entry in every `list` must be the terminator:

```json
{"code": 0, "indent": 0, "parameters": []}
```

RPG Maker stops executing commands when it reaches code 0. It must always be
last — commands after code 0 are silently ignored.

---

## MV vs MZ: events Field Differences

The `events` field on a map is structured differently between MV and MZ.

### MV: Array (null at index 0)

```json
{
  "events": [
    null,
    {"id": 1, "name": "Chest", ...},
    {"id": 2, "name": "Guard", ...}
  ]
}
```

- `events` is a JSON array
- Index 0 is always `null` (the positional array convention used throughout MV)
- Event ID equals the array index

### MZ: Object Keyed by String ID

```json
{
  "events": {
    "1": {"id": 1, "name": "Chest", ...},
    "2": {"id": 2, "name": "Guard", ...}
  }
}
```

- `events` is a JSON object with string keys
- No null at index 0
- Event ID is still numeric in the `id` field; the key is its string representation

### Handling Both in Code

```python
events = map_data.get("events", [])
if isinstance(events, list):
    event_iter = (e for e in events if e is not None)
else:
    event_iter = (e for e in events.values() if e is not None)
```

This pattern (from `extract_npc_lines.py`) handles both correctly and is the
established project convention.

---

## CommonEvents.json

`data/CommonEvents.json` is a JSON array (null at index 0) of common event
objects. Common events have a simpler structure than map events — no pages,
no position, no movement settings.

```json
[
  null,
  {
    "id": 1,
    "name": "Innkeeper Dialog",
    "trigger": 0,
    "switchId": 0,
    "list": [
      {"code": 101, "indent": 0, "parameters": ["Actor1", 0, 0, 2]},
      {"code": 401, "indent": 0, "parameters": ["Welcome to the village inn!"]},
      {"code": 0,   "indent": 0, "parameters": []}
    ]
  }
]
```

| Field | Description |
|-------|-------------|
| `id` | Common event ID — equals array index. Never change. |
| `name` | Human-readable label. |
| `trigger` | 0 = none (called explicitly), 1 = autorun, 2 = parallel |
| `switchId` | For autorun/parallel triggers: which project switch must be ON. 0 means no switch condition. |
| `list` | Event command array. Same structure as map event page lists. Must end with code 0. |

**Key difference from map events:** Common events are called by other events via
code 117 (Call Common Event) or triggered automatically. They do not have page
conditions, page stacks, or movement settings.

---

## Agent Guidance

When editing event lists:

1. Always read the current `list` before modifying it — preserve existing
   command structure and IDs.
2. Insert new commands before the code-0 terminator, never after.
3. Maintain correct `indent` values — validate the indent sequence after any
   conditional branch or loop insertion.
4. Never renumber `id` fields or reorder the `events` array.
5. Use `load_json_preserving_format()` from `scripts/lib/safe_write.py` to
   read files — it returns the detected indentation level to preserve on write.
