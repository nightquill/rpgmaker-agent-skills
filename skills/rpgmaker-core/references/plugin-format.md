# Plugin Command Format — MV vs MZ

This document explains how to read and write plugin command event entries in
RPG Maker MV and MZ project files. Relevant when scaffolding events that invoke
plugins (Phase 4 skills) or when validating existing event data.

---

## Overview

| Engine | Event command code | Parameter format |
|--------|--------------------|-----------------|
| MV     | `356`              | Single freeform string |
| MZ     | `357`              | Structured object with named args |

Always detect the engine version before emitting plugin command events:

```bash
python -m scripts.lib.project_detect --project-path /path/to/project
```

---

## MV: Code 356 — Freeform String

In MV, plugin commands are invoked via event command code `356`. The
`parameters` array contains exactly one string: the full command including
the plugin name, command keyword, and all arguments, space-separated. The
plugin parses this string itself.

**JSON structure:**

```json
{
  "code": 356,
  "indent": 0,
  "parameters": ["PluginName command arg1 arg2"]
}
```

**Example — calling a common hypothetical "ShowTitle" command on a plugin
named "TitleManager" with argument "ArcI":**

```json
{
  "code": 356,
  "indent": 0,
  "parameters": ["TitleManager ShowTitle ArcI"]
}
```

**Parsing conventions (MV):**

- First token: plugin name (must match the plugin file registered in
  `js/plugins.js`).
- Second token: command keyword (defined by the plugin).
- Remaining tokens: positional arguments (plugin-defined, usually space-split).
- Arguments with spaces must be handled by plugin conventions — most MV plugins
  use underscores or disallow spaces in arguments.

**When to use:**

Only when the target project is confirmed MV (via `project_detect.py`) and the
plugin uses the `pluginCommand` override pattern.

---

## MZ: Code 357 — Structured Object

In MZ, plugin commands use event command code `357`. The `parameters` array
contains three elements:

1. Plugin name (string) — must match the plugin file.
2. Command name (string) — must match a `@command` annotation in the plugin.
3. Arguments object (object) — key/value pairs matching `@arg` annotations.

**JSON structure:**

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

**Example — same "ShowTitle" command in MZ:**

```json
{
  "code": 357,
  "indent": 0,
  "parameters": [
    "TitleManager",
    "ShowTitle",
    { "arcName": "ArcI" }
  ]
}
```

**Argument values in MZ:**

- Arguments are always strings in the JSON, even for numeric types.
- The RPG Maker MZ runtime coerces them to the declared `@arg` type.
- Boolean args: `"true"` or `"false"` as strings.
- Number args: `"42"` as a string.

**@command registration (plugin file):**

```javascript
/*:
 * @command ShowTitle
 * @text Show Title Card
 * @desc Display a title card for a new story arc.
 *
 * @arg arcName
 * @text Arc Name
 * @type string
 * @desc Name of the arc to display.
 */
PluginManager.registerCommand('TitleManager', 'ShowTitle', function(args) {
    showTitleCard(args.arcName);
});
```

**When to use:**

Only when the target project is confirmed MZ (via `project_detect.py`) and the
plugin uses `PluginManager.registerCommand`.

---

## Side-by-Side Comparison

Same conceptual action — "open a shop using plugin ID 3" — in both formats:

**MV (code 356):**

```json
{
  "code": 356,
  "indent": 0,
  "parameters": ["ShopManager openShop 3"]
}
```

**MZ (code 357):**

```json
{
  "code": 357,
  "indent": 0,
  "parameters": [
    "ShopManager",
    "openShop",
    { "shopId": "3" }
  ]
}
```

---

## Common Mistakes

| Mistake | Result |
|---------|--------|
| Using code 356 in an MZ project | Silent no-op — MZ ignores code 356 for plugin commands |
| Using code 357 in an MV project | Silent no-op — MV doesn't process code 357 |
| Providing an integer for a code 357 arg value | Runtime error — args must be strings |
| Misspelling the plugin name in parameters[0] | Silent no-op — plugin not found |
| Misspelling the command name in parameters[1] | Runtime error or silent no-op depending on plugin |

---

## Checking Plugin Registration

To verify a plugin is registered and a command exists:

**MV:** Look for `pluginCommand` override in the `.js` file.

```bash
grep -n "pluginCommand" js/plugins/PluginName.js
```

**MZ:** Look for `@command` annotations in the plugin header.

```bash
grep -n "@command" js/plugins/PluginName.js
```

---

## When to Use This Doc

Load this reference only when:

- Scaffolding events that call plugin commands (Phase 4: events skill)
- Validating existing event lists for correct code 356/357 format
- Migrating an MV event file to MZ format

For standard dialog, flow control, and item commands, this reference is not
needed.
