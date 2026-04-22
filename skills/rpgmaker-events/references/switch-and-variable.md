# Switches, Variables, and Self-Switches

RPG Maker MV/MZ provides three types of persistent state flags for event logic:
project-wide switches (boolean), project-wide variables (integer), and per-event
self-switches (boolean, four per event). Understanding which type to use — and
how each appears across event command codes and page conditions — is essential for
correct event scripting.

---

## Comparison Table

| Type | Scope | Storage | Max Count | Set Command | Check Command | Page Condition Field |
|------|-------|---------|-----------|-------------|---------------|----------------------|
| Switch | Global — whole project | `System.json["switches"]` names; saved to savefile at runtime | Length of switches array | Code 121 | Code 111 (`params[0]=0`) | `switch1Id` / `switch2Id` |
| Variable | Global — whole project | `System.json["variables"]` names; saved to savefile at runtime | Length of variables array | Code 122 | Code 111 (`params[0]=1`) | `variableId` + `variableValue` |
| Self-Switch | Per-event (A, B, C, D only) | Stored per-event in savefile; not in JSON files | Always 4 per event | Code 123 | Code 111 (`params[0]=2`) | `selfSwitchCh` + `selfSwitchValid` |

---

## Switches

Switches are project-wide boolean flags (ON or OFF). They are named in
`System.json["switches"]` — a string array where index 0 is always `""` and
index 1+ are switch names. Switch ID 1 corresponds to `switches[1]`.

### Setting a Switch

```json
{"code": 121, "indent": 0, "parameters": [1, 1, 0]}
```

Code 121 — Control Switches. Parameters:

| Index | Field | Values |
|-------|-------|--------|
| 0 | `startSwitchId` | First switch to set (IDs are inclusive range) |
| 1 | `endSwitchId` | Last switch to set (same as start for a single switch) |
| 2 | `value` | 0 = ON, 1 = OFF |

To set a range of switches at once, set `startSwitchId` and `endSwitchId` to
the beginning and end of the range.

### Checking a Switch in a Conditional Branch

```json
{"code": 111, "indent": 0, "parameters": [0, 1, 0]}
```

Code 111 — Conditional Branch, switch type (`params[0]=0`):

| Index | Field | Values |
|-------|-------|--------|
| 0 | Condition type | `0` = Switch |
| 1 | `switchId` | The switch to check |
| 2 | `value` | 0 = check ON, 1 = check OFF |

### Switch Page Condition

On an event page's `conditions` object:

```json
{
  "switch1Valid": true,
  "switch1Id": 1,
  "switch2Valid": false,
  "switch2Id": 1
}
```

A page activates only when all enabled conditions are true. `switch1Valid` and
`switch2Valid` enable checking `switch1Id` and `switch2Id` respectively.

### Looking Up Switch Names

```python
# System.json switches array (VERIFIED from fixture)
import json
with open("data/System.json", encoding="utf-8") as f:
    system = json.load(f)
# Index 0 is "" (empty placeholder). Index 1+ are names.
switch_name = system["switches"][1]  # e.g. "Quest Active"
```

---

## Variables

Variables are project-wide integers. They are named in `System.json["variables"]`
using the same index-0-null convention as switches. Variable values are saved to
the save file at runtime; the names in `System.json` are for the editor only.

### Setting a Variable

```json
{"code": 122, "indent": 0, "parameters": [1, 1, 0, 0, 10]}
```

Code 122 — Control Variables. Parameters:

| Index | Field | Values |
|-------|-------|--------|
| 0 | `startVarId` | First variable to set |
| 1 | `endVarId` | Last variable to set (same as start for a single variable) |
| 2 | `operation` | 0=set, 1=add, 2=subtract, 3=multiply, 4=divide, 5=modulo |
| 3 | `operandType` | 0=constant, 1=variable, 2=random, 3=game data |
| 4+ | operand value(s) | For type 0 (constant): `params[4]` is the value. For type 1 (variable): `params[4]` is the source variable ID. For type 2 (random): `params[4]` min, `params[5]` max. |

### Checking a Variable in a Conditional Branch

```json
{"code": 111, "indent": 0, "parameters": [1, 1, 0, 10]}
```

Code 111 — Conditional Branch, variable type (`params[0]=1`):

| Index | Field | Values |
|-------|-------|--------|
| 0 | Condition type | `1` = Variable |
| 1 | `varId` | The variable to check |
| 2 | `comparisonOp` | 0=equal, 1=>=, 2=<=, 3=>, 4=<, 5=!= |
| 3 | `compareValue` | The value to compare against |

### Variable Page Condition

```json
{
  "variableValid": true,
  "variableId": 1,
  "variableValue": 5
}
```

Page activates when `variables[variableId] >= variableValue` (greater-than-or-equal).

---

## Self-Switches (A, B, C, D)

Self-switches are per-event boolean flags. Each event has exactly four: A, B, C,
and D. They are not stored in JSON project files — they are stored in the save
file as a per-event-instance state.

**Critical:** Self-switch parameters are always strings (`"A"`, `"B"`, `"C"`, `"D"`),
never integers. Using integers silently fails at runtime.

### Setting a Self-Switch

```json
{"code": 123, "indent": 0, "parameters": ["A", 0]}
```

Code 123 — Control Self Switch. Parameters:

| Index | Field | Values |
|-------|-------|--------|
| 0 | `selfSwitchCh` | `"A"`, `"B"`, `"C"`, or `"D"` — always a string |
| 1 | `value` | 0 = ON, 1 = OFF |

### Checking a Self-Switch in a Conditional Branch

```json
{"code": 111, "indent": 0, "parameters": [2, "A", 0]}
```

Code 111 — Conditional Branch, self-switch type (`params[0]=2`):

| Index | Field | Values |
|-------|-------|--------|
| 0 | Condition type | `2` = Self-Switch |
| 1 | `selfSwitchCh` | `"A"`, `"B"`, `"C"`, or `"D"` — always a string |
| 2 | `value` | 0 = check ON, 1 = check OFF |

### Self-Switch Page Condition

```json
{
  "selfSwitchValid": true,
  "selfSwitchCh": "A"
}
```

Page activates when self-switch A is ON for this event instance. Used by the
chest pattern to show the "already opened" page once self-switch A has been set.

### Typical Self-Switch Usage Pattern

Self-switches A, B, C, D are conventionally used in this order:
- **A**: Primary opened/triggered state (chest opened, dialog seen)
- **B**: Secondary state (event progressed to second phase)
- **C/D**: Additional phases or conditions as needed

---

## Where Each Type Appears in Event Commands

| Type | Set Command | Code | Params | Check Command | Code | Params | Page Condition Field |
|------|-------------|------|--------|---------------|------|--------|----------------------|
| Switch | Control Switches | 121 | `[startId, endId, 0=ON/1=OFF]` | Conditional Branch type 0 | 111 | `[0, switchId, 0=ON/1=OFF]` | `switch1Id`, `switch2Id` |
| Variable | Control Variables | 122 | `[startId, endId, operation, operandType, ...]` | Conditional Branch type 1 | 111 | `[1, varId, compOp, compareValue]` | `variableId`, `variableValue` |
| Self-Switch | Control Self Switch | 123 | `["A"/"B"/"C"/"D", 0=ON/1=OFF]` | Conditional Branch type 2 | 111 | `[2, "A"/"B"/"C"/"D", 0=ON/1=OFF]` | `selfSwitchCh`, `selfSwitchValid` |

**Page conditions vs. command list conditions:**
Page conditions (in the `conditions` object on the page) determine whether the
page is *active at all*. Command list conditions (code 111 inside the `list`)
determine branching *within* an active page. Both are common; switches and
self-switches appear in both locations.

---

## Using list_switches.py and find_event_refs.py

### list_switches.py — Project-Wide Switch Audit

Scans all event lists and page conditions across CommonEvents.json and all
Map*.json files. Outputs a markdown table of every switch reference found.

```bash
PYTHONPATH=. python scripts/list_switches.py --project fixtures/example-mv-project
```

Output format:

| Switch ID | Name | Used In | Operation |
|-----------|------|---------|-----------|
| 1 | Quest Active | CommonEvent:1:Quest Start | set |
| 1 | Quest Active | Map003.json:Event2:Boss:Page0 | page condition (switch1) |
| 1 | Quest Active | Map003.json:Event3:Guard:Page1 | check |

- **set**: code 121 in the event list sets this switch
- **check**: code 111 in the event list checks this switch
- **page condition (switch1/switch2)**: switch used as a page activation condition

Switch names come from `System.json["switches"]`. If a switch has no name
(empty string), the output shows `(unnamed switch N)`.

### find_event_refs.py — Find All Uses of One ID

Searches for every reference to a specific switch ID, variable ID, or
self-switch letter across the entire project.

```bash
# Find all references to switch ID 1
PYTHONPATH=. python scripts/find_event_refs.py --project fixtures/example-mv-project --switch-id 1

# Find all references to variable ID 3
PYTHONPATH=. python scripts/find_event_refs.py --project fixtures/example-mv-project --var-id 3

# Find all references to self-switch A
PYTHONPATH=. python scripts/find_event_refs.py --project fixtures/example-mv-project --self-switch A
```

Only one of `--switch-id`, `--var-id`, or `--self-switch` may be specified per run.

The script exits 0 if references are found, 1 if none are found (useful for
scripted checks: "is this switch actually used anywhere?").

---

## Common Mistakes

**Using integers for self-switch letter:**

```json
// WRONG — silently fails
{"code": 123, "indent": 0, "parameters": [0, 0]}

// CORRECT
{"code": 123, "indent": 0, "parameters": ["A", 0]}
```

**Forgetting that System.json index 0 is always empty:**

```python
# WRONG — switches[0] is always ""
switch_name = system["switches"][0]  # "" — not the first switch

# CORRECT — switch ID 1 is at index 1
switch_name = system["switches"][1]  # "Quest Active"
```

**Checking page conditions only in the list array:**

Switch references appear in two locations: inside `list` arrays (as command
parameters) and in `conditions` objects (as page activation conditions). Code
that only scans `list` arrays misses the page condition references. Always
check both `conditions.switch1Id`, `conditions.switch2Id`, and
`conditions.selfSwitchCh` when auditing switch usage.
