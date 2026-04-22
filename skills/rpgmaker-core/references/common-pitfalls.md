# Common Agent Pitfalls with RPG Maker Data Files

A reference guide to mistakes agents make when reading and writing RPG Maker
MV/MZ data files, what goes wrong, and how to avoid each one.

---

## Core Data Structure Pitfalls

### 1. Renumbering array IDs

**What goes wrong:** Every cross-file reference uses integer IDs. If you
reassign, sort, or reorder entries, every ID-based reference in the project
silently points to the wrong thing. Dialog shows the wrong actor name. Skills
trigger wrong animations. Actors equip wrong items. There is no runtime error
— the game just behaves incorrectly.

**Example of what NOT to do:**

```python
# WRONG: sorting by name compacts and renumbers IDs
data.sort(key=lambda x: x['name'] if x else '')
```

**How to avoid:** Never reassign `id` values. Never sort or reorder database
arrays. Append only. Run `validate_positional_array()` from `safe_write.py`
before any write operation.

---

### 2. Deleting entries instead of nulling them

**What goes wrong:** When you splice an entry out of the array, every entry
with a higher index shifts down by one. An actor previously at index 5 is now
at index 4. All events, skills, and dialog that referenced actor 5 now
reference actor 4 silently.

**Example of what NOT to do:**

```python
# WRONG: removes index 3, shifts all higher IDs down by one
del data[3]
```

**How to avoid:** Set deleted entries to `null` (Python `None`), never remove
them. The RPG Maker editor shows blank slots for null entries. Run
`validate_no_id_changes()` before any write to confirm no IDs changed.

```python
# CORRECT: tombstone, preserves all higher IDs
data[3] = None
```

---

### 3. Overwriting the `note` field

**What goes wrong:** The `note` field in every database entry (Actors, Skills,
Items, Enemies, Weapons, Armors, States, etc.) is a freeform string used
exclusively by plugins for notetag configuration. A notetag looks like:
`<PluginName:value>` or `<ElementRate: Fire, 150>`. If you replace the
`note` value entirely, you destroy all plugin configuration on that entry.
The plugin silently stops working for that entry.

**How to avoid:** Always read the existing `note` value before writing. If you
need to add a notetag, append it on a new line:

```python
# CORRECT: append, never replace
existing_note = actor.get('note', '')
actor['note'] = existing_note + '\n<MyTag: value>' if existing_note else '<MyTag: value>'
```

Never pass `note` through a string sanitizer, trimmer, or HTML escaper.

---

### 4. Forgetting null at index 0

**What goes wrong:** RPG Maker databases always have `null` at index 0.
Scripts that initialize a new array without this sentinel produce IDs that
are off by one — the entry at index 1 gets `id: 1` but should be at index 1
from a null-padded start, which is correct, but if you start at 0 the actor
with `id: 1` ends up at index 0 and the null invariant is broken.

**How to avoid:** Always initialize new positional arrays with null at index 0:

```python
# CORRECT
new_array = [None, {"id": 1, "name": "Hero", ...}]
```

Verify with `validate_positional_array()` before writing.

---

### 5. Treating map events as a plain array

**What goes wrong:** `MapXXX.json` has an `events` field that is an array
with `null` at index 0, identical to database arrays. Iterating from index 0
or using `enumerate` without offset produces off-by-one event ID errors.

**How to avoid:** Skip index 0. Use event IDs for lookups, not loop indices:

```python
# CORRECT: filter nulls, use .id for identification
for event in map_data['events']:
    if event is None:
        continue
    process_event(event)  # event['id'] is authoritative
```

---

### 6. Hardcoding map filenames

**What goes wrong:** `Map001.json`, `Map002.json`, etc. are determined by the
map's position in `MapInfos.json`. If the developer adds or deletes maps,
filenames may shift. A script hardcoding `Map003.json` may silently operate
on the wrong map after the project changes.

**How to avoid:** Look up maps by name via `MapInfos.json`, then derive the
filename from the ID:

```python
import json, pathlib

map_infos = json.loads(pathlib.Path('data/MapInfos.json').read_text())
# find map by name
target = next((m for m in map_infos if m and m['name'] == 'Dungeon'), None)
if target:
    filename = f"data/Map{target['id']:03d}.json"
```

---

### 7. Inserting commands after the code-0 terminator

**What goes wrong:** Every RPG Maker event command list ends with a mandatory
terminator entry: `{"code": 0, "indent": 0, "parameters": []}`. The
interpreter stops processing when it hits code 0. Any commands inserted after
this terminator are silently ignored — the dialog or logic never runs.

**How to avoid:** Always find the terminator index and insert **before** it:

```python
# CORRECT: find terminator, insert before it
term_idx = next(i for i, cmd in enumerate(event_list) if cmd['code'] == 0)
event_list.insert(term_idx, new_command)
```

---

### 8. Stripping text escape codes from dialog

**What goes wrong:** RPG Maker's dialog text supports escape codes that are
evaluated at runtime: `\N[1]` inserts actor 1's name, `\V[3]` inserts variable
3's value, `\C[2]` changes text color, `\I[42]` shows an icon. If you run
dialog strings through a sanitizer or escaper that removes backslashes, the
codes become literal text displayed on screen (`\N[1]` shows as the string
`\N[1]` instead of "Hero").

**How to avoid:** Treat dialog text fields as opaque strings. Never run them
through HTML escapers, JSON string escapers, or regex replacements that touch
backslashes unless you specifically intend to modify escape codes.

---

### 9. Using unquoted `3.10` in YAML

**What goes wrong:** YAML treats unquoted `3.10` as the float `3.1` by
dropping the trailing zero. A GitHub Actions CI matrix with
`python-version: 3.10` will attempt to install Python 3.1, which either
fails with an error or installs an unexpected version.

**How to avoid:** Always quote Python version strings in YAML:

```yaml
# CORRECT
matrix:
  python-version: ["3.10", "3.11", "3.12"]
```

---

### 10. Changing indentation style when rewriting JSON

**What goes wrong:** RPG Maker project files use a specific indentation style
(typically 2 or 4 spaces). If you rewrite a file with a different indent,
`git diff` shows the entire file as modified rather than just the changed
lines. This makes reviewing changes difficult and may suggest a full-file
rewrite when only one entry changed.

**How to avoid:** Use `load_json_preserving_format()` from `safe_write.py` to
detect the existing indent level, then replicate it on write:

```python
data, indent = load_json_preserving_format('data/Actors.json')
# ... modify data ...
safe_write('data/Actors.json', original, data, apply=args.apply, indent=indent)
```

---

## Pitfalls at Write Time

| Pitfall | Symptom | Fix |
|---------|---------|-----|
| Not creating `.bak` before writing | No recovery if write produces bad data | Use `safe_write()` — it always runs `shutil.copy2` before writing |
| Writing without `--apply` guard | Script modifies files on first run (no dry-run) | Use `add_argparse_write_args()`; default `apply=False` |
| `json.dumps` without `ensure_ascii=False` | Japanese/accented text becomes `\uXXXX` sequences | Always pass `ensure_ascii=False` |
| Missing trailing newline | Some editors flag files without final newline | Add `fh.write("\n")` after `json.dump` |

---

## Quick Safety Checklist

Before any write operation on an RPG Maker data file:

- [ ] Detected correct engine version (MV or MZ) via `project_detect.py`?
- [ ] Loaded with `load_json_preserving_format()` to capture indent level?
- [ ] Ran `validate_positional_array()` on the modified data?
- [ ] Ran `validate_no_id_changes()` against the original data?
- [ ] Previewed with dry-run (no `--apply`) first?
- [ ] `.bak` backup created before writing?
- [ ] Schema validation run after writing?
- [ ] Reminded developer to close and reopen project in RPG Maker editor?
