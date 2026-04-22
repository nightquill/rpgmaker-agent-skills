# Event Pattern Templates

Six standard event patterns cover most RPG Maker map interactions. Each
pattern is a complete `list` array — paste it into an event page's `list`
field, or generate it with `scaffold_event.py`.

All patterns end with the mandatory code-0 terminator (D-09). All patterns
are drafts for developer review; adjust IDs, text, and logic to fit your
project.

---

## Chest

A one-time item pickup. Page 1 gives the item and sets self-switch A ON.
Page 2 (with condition `selfSwitchCh: "A"`) shows "already opened" dialog.

**Required params:** `itemId` (int), `quantity` (int, default 1)

```json
[
  {"code": 126, "indent": 0, "parameters": [3, 0, 0, 1]},
  // code 126: Change Items — params: [itemId, 0=add/1=remove, 0=constant, quantity]
  // Replace 3 with your item ID; replace 1 with your quantity
  {"code": 123, "indent": 0, "parameters": ["A", 0]},
  // code 123: Control Self Switch — "A" ON (always string, never integer)
  {"code": 0, "indent": 0, "parameters": []}
  // list terminator — always last
]
```

CLI: `PYTHONPATH=. python scripts/scaffold_event.py --project <path> --pattern chest --item-id 3 --quantity 1`

| Parameter | Flag | Default | Notes |
|-----------|------|---------|-------|
| Item ID | `--item-id` | required | ID from Items.json |
| Quantity | `--quantity` | `1` | Number of items to add |

**Notes:**
- Page 2 of the chest event must have `conditions.selfSwitchValid: true` and `conditions.selfSwitchCh: "A"` to activate after the chest is opened.
- Page 2 typically contains only a dialog line ("The chest is empty.") and the code-0 terminator.

---

## Shop

Opens the shop menu. Each item for sale is a code 605 continuation entry
after the opening code 302.

**Required params:** At least one shop item entry `(itemType, itemId)`

```json
[
  {"code": 302, "indent": 0, "parameters": [0, 3, false, false]},
  // code 302: Shop Processing — params[0]=first goods itemType (0=item,1=weapon,2=armor)
  // params[1]=first goods itemId, params[2]=purchaseOnly flag, params[3]=reserved
  // The first item is embedded in code 302; subsequent items use code 605
  {"code": 605, "indent": 0, "parameters": [0, 5, 0, 0]},
  // code 605: Shop Goods continuation — params: [itemType, itemId, priceType(0=normal), price]
  // priceType 0 = use the item's default price from the database
  {"code": 605, "indent": 0, "parameters": [1, 2, 0, 0]},
  // Another item: weapon ID 2 at normal price
  {"code": 0, "indent": 0, "parameters": []}
]
```

CLI: `PYTHONPATH=. python scripts/scaffold_event.py --project <path> --pattern shop --shop-items "0,3" --shop-items "0,5" --shop-items "1,2"`

| Parameter | Flag | Default | Notes |
|-----------|------|---------|-------|
| Shop items | `--shop-items` | required (at least 1) | Comma-separated `itemType,itemId` pairs. Type: 0=item, 1=weapon, 2=armor |
| Purchase only | `--purchase-only` | false | When true, player cannot sell items |

**Parameter detail — code 302:**

| Index | Field | Values |
|-------|-------|--------|
| 0 | First goods `itemType` | 0=item, 1=weapon, 2=armor |
| 1 | First goods `itemId` | ID from corresponding database file |
| 2 | `purchaseOnly` | false = allow selling; true = buy only |
| 3 | reserved | always false |

**Parameter detail — code 605:**

| Index | Field | Values |
|-------|-------|--------|
| 0 | `itemType` | 0=item, 1=weapon, 2=armor |
| 1 | `itemId` | ID from corresponding database file |
| 2 | `priceType` | 0=use item's default price |
| 3 | `price` | Only used when priceType=1 (custom price) |

**Notes:**
- The first shop item's type and ID are encoded in code 302 params[0] and params[1]. All additional items use code 605.
- [ASSUMED] code 302 exact parameter layout — verify by exporting a shop event from RPG Maker editor if results look wrong.

---

## Inn

Choice-gated rest for gold. Shows cost, prompts Yes/No, charges gold and
fully heals the party on "Yes", shows a polite refusal on "No".

**Required params:** `cost` (int, gold amount)

```json
[
  {"code": 101, "indent": 0, "parameters": ["", 0, 0, 2]},
  // code 101: Show Text — no face portrait (""), window style, bottom position
  {"code": 401, "indent": 0, "parameters": ["Rest here? (50 gold)"]},
  // Replace 50 with your inn cost
  {"code": 102, "indent": 0, "parameters": [["Yes", "No"], 1, 0, 2, 0]},
  // code 102: Show Choices — cancelType=1 maps cancel to "No" choice
  {"code": 402, "indent": 1, "parameters": [0, "Yes"]},
  // code 402: When [Yes] — indent 1 (one more than the 102)
  {"code": 125, "indent": 2, "parameters": [1, 0, 50]},
  // code 125: Change Gold — params: [1=remove, 0=constant, amount]
  // params[0]=1 means REMOVE gold (player pays) [VERIFIED from fixture]
  {"code": 311, "indent": 2, "parameters": [0, 0]},
  // code 311: Change HP — full recover
  {"code": 312, "indent": 2, "parameters": [0, 0]},
  // code 312: Change MP — full recover
  {"code": 250, "indent": 2, "parameters": [{"name": "Recovery", "volume": 90, "pitch": 100, "pan": 0}]},
  // code 250: Play SE — recovery sound effect
  {"code": 101, "indent": 2, "parameters": ["", 0, 0, 2]},
  {"code": 401, "indent": 2, "parameters": ["Sweet dreams!"]},
  {"code": 402, "indent": 1, "parameters": [1, "No"]},
  // code 402: When [No]
  {"code": 101, "indent": 2, "parameters": ["", 0, 0, 2]},
  {"code": 401, "indent": 2, "parameters": ["Come back anytime."]},
  {"code": 404, "indent": 1, "parameters": []},
  // code 404: End Choice — same indent as the 402 entries
  {"code": 0, "indent": 0, "parameters": []}
]
```

CLI: `PYTHONPATH=. python scripts/scaffold_event.py --project <path> --pattern inn --cost 50`

| Parameter | Flag | Default | Notes |
|-----------|------|---------|-------|
| Cost | `--cost` | required | Gold amount charged for rest |

**Notes:**
- Code 311/312 with operation 0 performs a full HP/MP recover for all party members.
- The SE name "Recovery" is a placeholder — replace with your project's actual sound effect filename.
- [ASSUMED] code 125 `params[0]=1` means REMOVE gold — strongly implied by fixture but cross-verify against `Game_Interpreter.prototype.command125` if results look wrong.

---

## Door

A conditional door event. If self-switch A is OFF (locked), show a "locked"
message. If self-switch A is ON (unlocked), transfer the player to the
destination map. The door opens via a different event that sets self-switch A.

**Required params:** `mapId` (int), `x` (int), `y` (int), `direction` (int, 0=retain/2=down/4=left/6=right/8=up)

```json
[
  {"code": 111, "indent": 0, "parameters": [2, "A", 0]},
  // code 111: Conditional Branch — params[0]=2 means Self-Switch type
  // params[1]="A" (string), params[2]=0=ON
  // This branch fires when self-switch A is ON (door is unlocked)
  {"code": 201, "indent": 1, "parameters": [0, 2, 5, 10, 0, 0]},
  // code 201: Transfer Player — params: [0=direct, mapId, x, y, direction, fadeType]
  // Replace 2, 5, 10 with your destination mapId, x, y
  {"code": 411, "indent": 0, "parameters": []},
  // code 411: Else — fires when self-switch A is OFF (door is locked)
  {"code": 101, "indent": 1, "parameters": ["", 0, 0, 2]},
  {"code": 401, "indent": 1, "parameters": ["The door is locked."]},
  {"code": 412, "indent": 0, "parameters": []},
  // code 412: End of Conditional Branch (NOT 413 — see Anti-Patterns)
  {"code": 0, "indent": 0, "parameters": []}
]
```

CLI: `PYTHONPATH=. python scripts/scaffold_event.py --project <path> --pattern door --map-id 2 --x 5 --y 10`

| Parameter | Flag | Default | Notes |
|-----------|------|---------|-------|
| Destination map ID | `--map-id` | required | ID from MapInfos.json |
| Destination X | `--x` | required | Tile X coordinate |
| Destination Y | `--y` | required | Tile Y coordinate |
| Direction after transfer | `--direction` | `0` | 0=retain, 2=down, 4=left, 6=right, 8=up |

**Notes:**
- Self-switch A starts OFF by default. A separate event (a key pickup, a switch, etc.) must set self-switch A ON to open this door.
- The transfer fade type 0 is "black". Options: 0=black, 1=white, 2=none.

---

## Switch-Gated Cutscene

A one-time dialog sequence gated on a project switch. Fires when the switch
is ON, clears the switch when done so the cutscene won't repeat.

**Required params:** `switchId` (int)

```json
[
  {"code": 111, "indent": 0, "parameters": [0, 1, 0]},
  // code 111: Conditional Branch — params[0]=0 means Switch type
  // params[1]=1 (switch ID), params[2]=0=ON
  // Replace 1 with your switch ID
  {"code": 101, "indent": 1, "parameters": ["", 0, 0, 2]},
  {"code": 401, "indent": 1, "parameters": ["Something important happens here."]},
  // Add more 401 lines or dialog blocks as needed
  {"code": 121, "indent": 1, "parameters": [1, 1, 1]},
  // code 121: Control Switches — params: [startId, endId, 1=OFF]
  // Clears switch 1 after cutscene plays so it won't fire again
  // Replace 1, 1 with your switch ID (start and end are the same for a single switch)
  {"code": 411, "indent": 0, "parameters": []},
  // code 411: Else — fires when switch is OFF (cutscene already played or not triggered)
  {"code": 101, "indent": 1, "parameters": ["", 0, 0, 2]},
  {"code": 401, "indent": 1, "parameters": ["Nothing to see here."]},
  {"code": 412, "indent": 0, "parameters": []},
  // code 412: End of Conditional Branch
  {"code": 0, "indent": 0, "parameters": []}
]
```

CLI: `PYTHONPATH=. python scripts/scaffold_event.py --project <path> --pattern cutscene --switch-id 1`

| Parameter | Flag | Default | Notes |
|-----------|------|---------|-------|
| Switch ID | `--switch-id` | required | ID from System.json switches array |

**Notes:**
- The switch is cleared (set OFF) inside the if-branch so the cutscene plays exactly once per trigger.
- Swap the else branch content for an empty branch or remove the 411 block entirely if no fallback dialog is needed.
- Check `System.json["switches"]` for the correct ID — index 0 is always an empty placeholder.

---

## Wanderer

An NPC that moves randomly in a loop. Uses code 205 (Set Movement Route)
with a route object configured for random movement.

**No required params** — produces a generic random-walk NPC.

```json
[
  {"code": 205, "indent": 0, "parameters": [
    0,
    {
      "list": [
        {"code": 9, "parameters": []},
        {"code": 9, "parameters": []},
        {"code": 9, "parameters": []},
        {"code": 9, "parameters": []},
        {"code": 0, "parameters": []}
      ],
      "repeat": true,
      "skippable": true,
      "wait": false
    }
  ]},
  // code 205: Set Movement Route
  // params[0]: character ID — 0=this event, -1=player, 1+=event by ID
  // params[1]: route object — list is the movement sub-command array
  // repeat: true — loops the route indefinitely
  // skippable: true — if blocked, skip to next sub-command rather than freezing
  // Move sub-command code 9 = Move at Random [ASSUMED]
  // code 0 in the route list = end of route (required)
  {"code": 0, "indent": 0, "parameters": []}
]
```

CLI: `PYTHONPATH=. python scripts/scaffold_event.py --project <path> --pattern wanderer`

| Parameter | Flag | Default | Notes |
|-----------|------|---------|-------|
| Character ID | `--char-id` | `0` | 0=this event, -1=player, 1+=event by ID |
| Move steps | `--steps` | `4` | Number of random move sub-commands per loop |

**Move route sub-commands (inside route.list):**

| Sub-Code | Name | Notes |
|----------|------|-------|
| `1` | Move Down | [ASSUMED] |
| `2` | Move Left | [ASSUMED] |
| `3` | Move Right | [ASSUMED] |
| `4` | Move Up | [ASSUMED] |
| `9` | Move at Random | [ASSUMED] — standard wanderer choice |
| `10` | Move Toward Player | [ASSUMED] |
| `11` | Move Away from Player | [ASSUMED] |
| `0` | End of Route | Required — must be last in route.list |

**Notes:**
- The event page's `moveType` field (on the page object itself, not inside `list`) can also be set to `1` (random walk) or `3` (custom). Setting `moveType: 1` makes the editor handle random movement without a command list entry, but using code 205 gives finer control (number of steps, specific pattern).
- Move sub-command codes 1–27 are [ASSUMED] from training knowledge. Verify against `rpg_objects.js` Game_Character.processMoveCommand for your engine version before deploying in production.

---

## Anti-Patterns

**Wrong end code for conditional branch (413 instead of 412)**

Code 413 ("Repeat Above") closes a Loop (code 112). It does NOT close a
Conditional Branch (code 111). Using 413 to close a 111 corrupts event flow
without producing an error — the interpreter misidentifies block boundaries.

```json
// WRONG — closes a Loop, not a conditional branch
{"code": 413, "indent": 0, "parameters": []}

// CORRECT — closes a conditional branch
{"code": 412, "indent": 0, "parameters": []}
```

**Missing code-0 terminator**

Every event list must end with `{"code": 0, "indent": 0, "parameters": []}`.
scaffold_event.py appends this automatically (D-09). If you hand-edit a list,
always verify it is present as the final entry.

**Integer self-switch parameter**

Code 123 (Control Self Switch) and code 111 with `params[0]=2` both use
string letters for the self-switch value. Integers silently fail.

```json
// WRONG
{"code": 123, "indent": 0, "parameters": [0, 0]}

// CORRECT
{"code": 123, "indent": 0, "parameters": ["A", 0]}
```

**Wrong indent inside choice branches**

Commands inside a choice branch (after code 402/403) must be at one indent
level higher than the 402/403. Commands at the wrong indent level are
misattributed to the wrong branch or skipped entirely.

```json
// WRONG — dialog is at indent 1, same as the 402 (should be 2)
{"code": 402, "indent": 1, "parameters": [0, "Yes"]},
{"code": 401, "indent": 1, "parameters": ["Wrong indent!"]},

// CORRECT — dialog is at indent 2 (one more than the 402)
{"code": 402, "indent": 1, "parameters": [0, "Yes"]},
{"code": 101, "indent": 2, "parameters": ["", 0, 0, 2]},
{"code": 401, "indent": 2, "parameters": ["Correct indent."]},
```

**MV/MZ plugin command code confusion**

Code 356 is for MV (single string parameter). Code 357 is for MZ (array
parameter). Using the wrong code in the wrong version causes the plugin
command to fail silently. scaffold_event.py handles this automatically via
project_detect.py, but hand-edited events must match the project version.
