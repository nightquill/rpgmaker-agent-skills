# RPG Maker MZ — Differences from MV

This document covers **only what changes between MV and MZ**. For the full field
reference, see `mv-schema.md`. When working with an MZ project, apply these
differences on top of the MV schema.

Detect the version first:

```bash
python -m scripts.lib.project_detect --project-path /path/to/project
```

---

## Manifest File

| MV | MZ |
|----|-----|
| `Game.rpgproject` | `Game.rmmzproject` |

If both manifest files exist, treat the project as MZ.

---

## Plugin Commands — Major Structural Change

The biggest MV→MZ difference affecting agents is plugin command syntax.

### MV: Event Command Code 356

MV plugin commands use a single freeform string parameter. The plugin parses
it however it likes.

```json
{ "code": 356, "indent": 0, "parameters": ["PluginName command arg1 arg2"] }
```

### MZ: Event Command Code 357

MZ plugin commands use a structured object with named arguments. Plugins
register commands via `@command`/`@arg` annotations in the plugin header.

```json
{
  "code": 357,
  "indent": 0,
  "parameters": [
    "PluginName",
    "commandName",
    { "argName1": "value1", "argName2": "value2" }
  ]
}
```

**When building events:** Check the detected version before emitting plugin
command event entries. Code 356 in an MZ project (or 357 in an MV project)
will not invoke any plugin.

---

## New Database Fields in MZ

### Actors.json

| New field | Type | Notes |
|-----------|------|-------|
| `face2Name` | string | Secondary face portrait filename (damage portrait). |
| `face2Index` | integer | Secondary face portrait index. |

### System.json

| New field | Type | Notes |
|-----------|------|-------|
| `advanced` | object | Advanced settings block (frame rate, screen size, etc.). |
| `advanced.screenWidth` | integer | Default: 816. |
| `advanced.screenHeight` | integer | Default: 624. |
| `advanced.uiAreaWidth` | integer | UI layer width. |
| `advanced.uiAreaHeight` | integer | UI layer height. |

### Skills.json / Items.json

No structural changes. MZ adds optional fields for some plugin-provided
features but the base schema is identical to MV.

---

## Tileset Format

MZ adds additional auto-tile passability flags to tileset data. The
`Tilesets.json` structure is ~90% identical but includes additional bitflag
fields in MZ:

| Field | MV | MZ |
|-------|----|----|
| `flags` | integer array | integer array (same format, more values) |
| `tilesetNames` | string[9] | string[9] (same) |

For most agent tasks (event scripting, dialog, database), tileset differences
are irrelevant.

---

## Event Command Code Additions in MZ

MZ adds a small number of new event command codes. The codes most relevant to
dialog and scripting:

| Code | Name | Notes |
|------|------|-------|
| `357` | Plugin Command (MZ) | Replaces code 356 for MZ plugins. |

All dialog-related codes (101, 401, 102, 402, 403, 404) are **identical** in
MV and MZ.

---

## Plugin Registration Format

MZ plugins use inline JSDoc-style annotations in the plugin file header to
register commands and parameters. These are consumed by RPG Maker's Plugin
Manager and affect how code 357 events are structured.

**MZ plugin command registration (in .js file):**

```javascript
/*:
 * @command MyCommand
 * @text My Command Name
 * @desc What this command does.
 *
 * @arg targetId
 * @type number
 * @text Target ID
 */
```

MV plugins use a `pluginCommand` property on the plugin object instead:

```javascript
(function() {
  var _Game_Interpreter_pluginCommand = Game_Interpreter.prototype.pluginCommand;
  Game_Interpreter.prototype.pluginCommand = function(command, args) {
    if (command === 'MyCommand') { /* ... */ }
    _Game_Interpreter_pluginCommand.call(this, command, args);
  };
})();
```

---

## Summary Checklist: MV vs MZ

| Concern | MV | MZ |
|---------|----|----|
| Manifest | `Game.rpgproject` | `Game.rmmzproject` |
| Plugin command code | 356 | 357 |
| Plugin command format | Space-separated string | Structured object with named args |
| Plugin registration | `pluginCommand` override | `@command`/`@arg` annotations |
| Actor face fields | `faceName`, `faceIndex` | + `face2Name`, `face2Index` |
| System advanced block | Absent | `advanced` object |
| Dialog codes (101/401/102/402/403/404) | Identical | Identical |
| Database array structure | Positional, index-0 null | Identical |
| Map file format | `MapXXX.json` | `MapXXX.json` (identical) |
