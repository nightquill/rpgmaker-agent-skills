# RPG Maker MV/MZ — Text Escape Codes

Text escape codes (also called text control codes) embed dynamic content
and formatting directly inside dialog strings. They appear in the `parameters`
field of code-401 event commands and in any text field within RPG Maker's
Show Text window.

In JSON files, backslashes are escaped: the source text `\N[1]` is stored
as the JSON string `"\\N[1]"`. When you read the file with `json.load()`,
Python gives you the unescaped string `\N[1]`. Always work with the
unescaped form in code; RPG Maker handles display.

---

## Full Code Reference

| Code | Effect | Example | Notes |
|------|--------|---------|-------|
| `\N[n]` | Actor name by ID | `\N[1]` → "Hero" | Reads name from `Actors.json`. ID must exist — missing ID displays blank. |
| `\V[n]` | Variable value (runtime) | `\V[1]` → current value of variable 1 | Value is resolved at runtime; no static validation possible. |
| `\C[n]` | Change text color | `\C[1]` = blue, `\C[0]` = white | Engine defines 32 colors (indices 0–31). `\C[0]` resets to default. |
| `\I[n]` | Display icon inline | `\I[64]` → icon sprite 64 | Icon IDs come from `IconSet.png` sprite sheet. ID must exist. |
| `\P[n]` | Party member name by slot | `\P[1]` → name of first party member | Slot-based, not actor ID. No static validation possible. |
| `\G` | Currency unit name | `\G` → "Gold" | Reads `currencyUnit` from `System.json`. |
| `\{` | Increase font size | | One step larger per use. |
| `\}` | Decrease font size | | One step smaller per use. |
| `\$` | Open gold window | | Shows current gold amount as an overlay. |
| `\.` | Wait 15 frames | | Approximately 0.25 seconds at 60 fps. |
| `\|` | Wait 60 frames | | Approximately 1 second at 60 fps. |
| `\!` | Wait for input | | Pauses text scrolling until the player presses a button. |
| `\>` | Display all text instantly | | Affects the current line; renders all characters at once until `\<`. |
| `\<` | Cancel instant display | | Resumes normal character-by-character display. |
| `\\` | Literal backslash | `\\` → `\` | Use to display a literal backslash in dialog. |

---

## Agent Rules

### NEVER strip text codes from extracted dialog

When extracting dialog lines (e.g., with `extract_npc_lines.py`), output
the text **verbatim**. Do not unescape, strip, or simplify text codes.
The voice consistency workflow depends on seeing the exact codes the character
already uses.

```
# CORRECT — preserve codes as-is
"Please, \N[1], you must help us!"

# WRONG — stripped code
"Please, [player name], you must help us!"
```

### NEVER fabricate `\N[id]` or `\I[id]` IDs

Before using `\N[id]` in a dialog draft, verify the actor ID exists in
`data/Actors.json`. Before using `\I[id]`, verify the item ID exists in
`data/Items.json`. A non-existent ID silently displays a blank in-game.

```
# WRONG — ID invented without checking
"The \I[999] has great power!"

# CORRECT — ID verified in Items.json first
"The \I[64] has great power!"
```

### Safe to use without database cross-check

- `\V[n]` — variable values are runtime state; no static file to check against
- `\C[n]` — colors 0–31 are engine constants; safe as long as n is 0–31
- `\P[n]` — party slot; slot-based, runtime state

### Python regex for text code extraction

Use these patterns in `validate_dialog_refs.py` and similar scripts:

```python
import re

# JSON-loaded strings contain single backslash: \N[1]
ACTOR_REF_RE = re.compile(r'\\N\[(\d+)\]')   # \N[id] -> Actors.json id
ITEM_REF_RE  = re.compile(r'\\I\[(\d+)\]')   # \I[id] -> Items.json id
COLOR_RE     = re.compile(r'\\C\[(\d+)\]')   # \C[n]  -> 0-31 valid range
VAR_RE       = re.compile(r'\\V\[(\d+)\]')   # \V[id] -> runtime variable

# Example usage
def find_actor_refs(text: str) -> list[int]:
    return [int(m.group(1)) for m in ACTOR_REF_RE.finditer(text)]
```

---

## MV vs MZ Compatibility

Text escape codes are identical between MV and MZ. No version-specific
behavior differences apply to the codes in the table above.

---

*Reference for: `skills/rpgmaker-dialog/SKILL.md` and any skill that reads
or writes RPG Maker text fields.*
