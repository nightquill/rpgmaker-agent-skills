# RPG Maker MV/MZ — Event Command Codes

This reference covers the full event command code range used in
`CommonEvents.json` and `MapXXX.json` event command lists.

**Scope:** Full event command code range (100s-600s). Dialog codes documented in Phase 2; remaining codes added in Phase 4.

---

## Dialog Command Code Table

| Code | Name | Parameters | Description |
|------|------|------------|-------------|
| `101` | Show Text (header) | `[faceName: string, faceIndex: int, background: int, position: int]` | Opens a dialog window. Sets the face portrait and window style. Required before code 401 lines. |
| `401` | Show Text (line) | `[text: string]` | One line of dialog text. Must follow a code 101 or another code 401. Multiple 401s form a multi-line message (RPG Maker shows up to 4 lines per window). |
| `102` | Show Choices | `[choices: string[], cancelType: int, defaultType: int, positionType: int, background: int]` | Presents the player with a branching choice menu. |
| `402` | When [Choice] | `[choiceIndex: int, choiceName: string]` | Branch block for a specific choice option. `indent` increases by 1 from the enclosing 102. |
| `403` | When Cancel | `[]` | Branch executed when the player presses cancel (only present when `cancelType` ≠ -1 in the 102). |
| `404` | End Choice | `[]` | Closes the choice block. `indent` returns to the level of the 102. |
| `0` | List Terminator | `[]` | Marks the end of an event command list. Every list must end with exactly one code-0 entry. |

---

## Parameter Details — Dialog Codes

### Code 101 — Show Text (header)

```json
{ "code": 101, "indent": 0, "parameters": ["Actor1", 0, 0, 2] }
```

| Index | Field | Values |
|-------|-------|--------|
| 0 | `faceName` | Sprite sheet filename without extension (e.g., `"Actor1"`) |
| 1 | `faceIndex` | 0–7: which of the 8 portraits in the 4×2 sprite sheet |
| 2 | `background` | 0 = window, 1 = dim, 2 = transparent |
| 3 | `position` | 0 = top, 1 = middle, 2 = bottom |

Pass an empty string for `faceName` and `0` for `faceIndex` to show a dialog
window with no face portrait.

### Code 401 — Show Text (line)

```json
{ "code": 401, "indent": 0, "parameters": ["Welcome to the village inn!"] }
```

Single element array containing the text string for that line. Text may
contain escape codes (see `text-codes.md`).

### Code 102 — Show Choices

```json
{ "code": 102, "indent": 0, "parameters": [["Yes", "No"], 1, 0, 2, 0] }
```

| Index | Field | Values |
|-------|-------|--------|
| 0 | `choices` | Array of choice label strings |
| 1 | `cancelType` | -1 = disallow cancel; 0–N = cancel maps to choice at that index; 5 = branch at code 403 |
| 2 | `defaultType` | Index of the initially-highlighted choice (0-based) |
| 3 | `positionType` | 0 = left, 1 = center, 2 = right |
| 4 | `background` | 0 = window, 1 = dim, 2 = transparent |

---

## Input Codes

| Code | Name | Parameters | Description |
|------|------|------------|-------------|
| `103` | Input Number | `[variableId: int, digitCount: int]` | Shows a number input field. Stores the result in the specified variable. [ASSUMED] |
| `104` | Select Item | `[variableId: int, itemType: int]` | Shows an item selection menu. Stores selected item ID in the variable. [ASSUMED] |
| `105` | Show Scrolling Text | `[speed: int, noFast: bool]` | Begins a scrolling text display. Lines follow as code 405 entries. [ASSUMED] |
| `405` | Scrolling Text Line | `[text: string]` | One line of scrolling text content. Follows a code 105. [ASSUMED] |

---

## Comment Codes

| Code | Name | Parameters | Description |
|------|------|------------|-------------|
| `108` | Comment | `[text: string]` | Adds a comment line to the event list. No runtime effect. [ASSUMED] |
| `408` | Comment (continuation) | `[text: string]` | Continuation line for a multi-line comment started by code 108. [ASSUMED] |

---

## Flow Control Codes

| Code | Name | Parameters | Description |
|------|------|------------|-------------|
| `111` | Conditional Branch | `[condType: int, ...condParams]` | Opens an if/else block. See condition type table below. [VERIFIED] |
| `411` | Else | `[]` | Opens the else branch of a code 111 block. `indent` matches the 111. [VERIFIED] |
| `412` | End of Conditional Branch | `[]` | Closes a conditional branch (code 111). NOT the same as 413. [VERIFIED] |
| `112` | Loop | `[]` | Begins a loop block. Everything until code 413 repeats. [VERIFIED] |
| `413` | Repeat Above (Loop End) | `[]` | Closes a Loop (code 112). NOT the same as 412 — never use this to close a conditional branch. [VERIFIED] |
| `113` | Break Loop | `[]` | Exits the current loop immediately. [VERIFIED] |
| `115` | Exit Event Processing | `[]` | Stops executing the current event command list immediately. [VERIFIED] |
| `117` | Common Event | `[commonEventId: int]` | Calls a common event by ID. [VERIFIED] |
| `118` | Label | `[labelName: string]` | Marks a jump target. [VERIFIED] |
| `119` | Jump to Label | `[labelName: string]` | Jumps to the named label. [VERIFIED] |

### Code 111 — Conditional Branch: Condition Types

`params[0]` selects the condition category. Subsequent params vary by type.

| params[0] | Type | params[1] | params[2] | params[3] |
|-----------|------|-----------|-----------|-----------|
| `0` | Switch | `switchId` | `0=ON, 1=OFF` | — |
| `1` | Variable | `varId` | `comparisonOp (0=eq,1=>=,2=<=,3=>,4=<,5=!=)` | `compareValue` |
| `2` | Self Switch | `"A"|"B"|"C"|"D"` (string) | `0=ON, 1=OFF` | — |
| `3` | Timer | `comparisonOp` | `seconds` | — |
| `4` | Actor | `actorId` | `condType` | varies by condType |
| `5` | Enemy | `enemyIndex` | `condType` | — |
| `6` | Character | `characterId` | `directionFacing` | — |
| `7` | Gold | `comparisonOp` | `amount` | — |
| `8` | Item | `itemId` | — | — |
| `9` | Weapon | `weaponId` | `includeEquipped` | — |
| `10` | Armor | `armorId` | `includeEquipped` | — |
| `11` | Button | `buttonCode` | — | — |
| `12` | Script | `jsExpressionString` | — | — |

[VERIFIED: swquinn/rmmv-docs + Game_Interpreter class documentation]

#### Example — Conditional Branch on Switch

```json
{"code": 111, "indent": 0, "parameters": [0, 1, 0]},
// params[0]=0: Switch type; params[1]=1: switch ID 1; params[2]=0: check ON
{"code": 401, "indent": 1, "parameters": ["Quest is active!"]},
{"code": 411, "indent": 0, "parameters": []},
// Else branch
{"code": 401, "indent": 1, "parameters": ["Quest not started."]},
{"code": 412, "indent": 0, "parameters": []}
// End of Conditional Branch — use 412, not 413
```

---

## Switch/Variable Control Codes

| Code | Name | Parameters | Description |
|------|------|------------|-------------|
| `121` | Control Switches | `[startSwitchId: int, endSwitchId: int, value: int]` | Sets one or more project switches. value: 0=ON, 1=OFF. [VERIFIED] |
| `122` | Control Variables | `[startVarId: int, endVarId: int, operation: int, operandType: int, ...operand]` | Sets one or more project variables. [VERIFIED] |
| `123` | Control Self Switch | `[selfSwitchCh: string, value: int]` | Sets a self-switch on the current event. **params[0] MUST be a string: "A", "B", "C", or "D".** [VERIFIED] |
| `124` | Control Timer | `[operation: int, minutes: int, seconds: int]` | Starts or stops the countdown timer. [VERIFIED] |

### Code 121 — Control Switches

```json
{"code": 121, "indent": 0, "parameters": [1, 1, 0]}
```

| Index | Field | Values |
|-------|-------|--------|
| 0 | `startSwitchId` | First switch ID to set |
| 1 | `endSwitchId` | Last switch ID to set (same as start for a single switch) |
| 2 | `value` | 0 = ON, 1 = OFF |

### Code 122 — Control Variables

```json
{"code": 122, "indent": 0, "parameters": [1, 1, 0, 0, 10]}
```

| Index | Field | Values |
|-------|-------|--------|
| 0 | `startVarId` | First variable ID to set |
| 1 | `endVarId` | Last variable ID to set |
| 2 | `operation` | 0=set, 1=add, 2=subtract, 3=multiply, 4=divide, 5=modulo |
| 3 | `operandType` | 0=constant, 1=variable, 2=random, 3=game data |
| 4+ | operand | For type 0: `params[4]` is the constant value. For type 1: `params[4]` is source variable ID. For type 2: `params[4]` min, `params[5]` max. |

### Code 123 — Control Self Switch

```json
{"code": 123, "indent": 0, "parameters": ["A", 0]}
```

| Index | Field | Values |
|-------|-------|--------|
| 0 | `selfSwitchCh` | **String** — `"A"`, `"B"`, `"C"`, or `"D"`. Never an integer. |
| 1 | `value` | 0 = ON, 1 = OFF |

---

## Inventory Codes

| Code | Name | Parameters | Description |
|------|------|------------|-------------|
| `125` | Change Gold | `[operation: int, operandType: int, amount: int]` | Adds or removes gold. params[0]: 0=add, 1=remove. [VERIFIED] |
| `126` | Change Items | `[itemId: int, operation: int, operandType: int, quantity: int]` | Adds or removes items. params[1]: 0=add, 1=remove. [VERIFIED] |
| `127` | Change Weapons | `[weaponId: int, operation: int, operandType: int, quantity: int, includeEquipped: bool]` | Adds or removes weapons. [VERIFIED] |
| `128` | Change Armors | `[armorId: int, operation: int, operandType: int, quantity: int, includeEquipped: bool]` | Adds or removes armors. [VERIFIED] |
| `129` | Change Party Member | `[actorId: int, operation: int, initialize: bool]` | Adds or removes an actor from the party. params[1]: 0=add, 1=remove. [VERIFIED] |

### Code 125 — Change Gold

```json
{"code": 125, "indent": 0, "parameters": [1, 0, 50]}
```

| Index | Field | Values |
|-------|-------|--------|
| 0 | `operation` | 0 = add gold, 1 = remove gold (player pays) |
| 1 | `operandType` | 0 = constant, 1 = variable |
| 2 | `amount` | Amount (or variable ID when operandType=1) |

[VERIFIED: fixture CommonEvents.json shows `[1, 0, 50]` in the inn payment branch — params[0]=1 removes gold]

### Code 126 — Change Items

```json
{"code": 126, "indent": 0, "parameters": [3, 0, 0, 1]}
```

| Index | Field | Values |
|-------|-------|--------|
| 0 | `itemId` | ID from Items.json |
| 1 | `operation` | 0 = add, 1 = remove |
| 2 | `operandType` | 0 = constant, 1 = variable |
| 3 | `quantity` | Number to add/remove (or variable ID when operandType=1) |

---

## Map/Movement Codes

| Code | Name | Parameters | Description |
|------|------|------------|-------------|
| `201` | Transfer Player | `[designationType: int, mapId: int, x: int, y: int, direction: int, fadeType: int]` | Moves the player to a new map position. [VERIFIED] |
| `202` | Set Vehicle Location | `[vehicleType: int, designationType: int, mapId: int, x: int, y: int]` | Sets a vehicle's position. [VERIFIED] |
| `203` | Set Event Location | `[eventId: int, designationType: int, x: int, y: int, direction: int]` | Teleports an event to a new position. [VERIFIED] |
| `204` | Scroll Map | `[direction: int, distance: int, speed: int]` | Scrolls the map in a direction. [VERIFIED] |
| `205` | Set Movement Route | `[characterId: int, route: object]` | Assigns a custom movement route to a character. [VERIFIED] |
| `206` | Getting On/Off Vehicles | `[]` | Toggles the player onto or off a vehicle. [VERIFIED] |
| `211` | Change Transparency | `[flag: int]` | Makes the player transparent (0) or visible (1). [ASSUMED] |
| `214` | Erase Event | `[]` | Removes this event from the map until the player re-enters the map. [VERIFIED] |
| `216` | Change Player Followers | `[flag: int]` | Shows or hides follower characters. [VERIFIED] |
| `217` | Gather Followers | `[]` | Teleports all followers to the player's position. [VERIFIED] |

### Code 201 — Transfer Player

```json
{"code": 201, "indent": 0, "parameters": [0, 2, 5, 10, 0, 0]}
```

| Index | Field | Values |
|-------|-------|--------|
| 0 | `designationType` | 0 = direct (constant coords), 1 = variable (variable IDs for coords) |
| 1 | `mapId` | Destination map ID |
| 2 | `x` | Destination X tile coordinate |
| 3 | `y` | Destination Y tile coordinate |
| 4 | `direction` | 0 = retain current, 2 = down, 4 = left, 6 = right, 8 = up |
| 5 | `fadeType` | 0 = black, 1 = white, 2 = none |

[VERIFIED: fixture Map001.json]

### Code 205 — Set Movement Route

```json
{"code": 205, "indent": 0, "parameters": [0, {
  "list": [
    {"code": 9, "parameters": []},
    {"code": 0, "parameters": []}
  ],
  "repeat": true,
  "skippable": true,
  "wait": false
}]}
```

| Index | Field | Values |
|-------|-------|--------|
| 0 | `characterId` | -1 = player, 0 = this event, 1+ = event by map ID |
| 1 | `route` | Route object with `list`, `repeat`, `skippable`, `wait` fields |

Route object fields:
- `list`: array of move route sub-commands (see Move Route Sub-Commands section)
- `repeat`: true = loop the route indefinitely
- `skippable`: true = skip blocked sub-commands instead of freezing
- `wait`: true = wait for the route to complete before proceeding

[VERIFIED: swquinn/rmmv-docs]

---

## Screen/Wait Codes

| Code | Name | Parameters | Description |
|------|------|------------|-------------|
| `221` | Fadeout Screen | `[]` | Fades the screen to black. [VERIFIED] |
| `222` | Fadein Screen | `[]` | Fades the screen from black to normal. [VERIFIED] |
| `223` | Tint Screen | `[[r,g,b,gray]: int[], duration: int, wait: bool]` | Applies a color tint to the screen. [ASSUMED] |
| `224` | Flash Screen | `[[r,g,b,intensity]: int[], duration: int, wait: bool]` | Flashes the screen with a color. [ASSUMED] |
| `225` | Shake Screen | `[power: int, speed: int, duration: int, wait: bool]` | Shakes the screen. [ASSUMED] |
| `230` | Wait | `[frames: int]` | Pauses event processing for N frames (60 fps). [VERIFIED] |
| `231` | Show Picture | `[pictureId: int, name: string, origin: int, x: int, y: int, scaleX: int, scaleY: int, opacity: int, blendMode: int]` | Displays a picture on screen. [ASSUMED] |
| `232` | Move Picture | `[pictureId: int, ...]` | Animates a picture to new position/properties. [ASSUMED] |
| `235` | Erase Picture | `[pictureId: int]` | Removes a displayed picture. [ASSUMED] |

---

## Audio Codes

| Code | Name | Parameters | Description |
|------|------|------------|-------------|
| `241` | Play BGM | `[{name, volume, pitch, pan}: object]` | Plays background music. [ASSUMED] |
| `245` | Play BGS | `[{name, volume, pitch, pan}: object]` | Plays background sound (environmental). [ASSUMED] |
| `249` | Play ME | `[{name, volume, pitch, pan}: object]` | Plays a music effect (fanfare, jingle). [ASSUMED] |
| `250` | Play SE | `[{name, volume, pitch, pan}: object]` | Plays a sound effect. [VERIFIED: fixture] |
| `261` | Play Movie | `[filename: string]` | Plays a video file. [VERIFIED] |

### Audio Object Structure

```json
{"name": "Battle1", "volume": 90, "pitch": 100, "pan": 0}
```

| Field | Values |
|-------|--------|
| `name` | Audio filename without extension |
| `volume` | 0–100 |
| `pitch` | 50–150 (100 = normal speed) |
| `pan` | -100 to 100 (0 = center) |

[VERIFIED: fixture CommonEvents.json code 250 entry]

---

## Battle/Actor Codes

| Code | Name | Parameters | Description |
|------|------|------------|-------------|
| `301` | Battle Processing | `[troopType: int, troopId: int, canEscape: bool, canLose: bool]` | Starts a battle encounter. [VERIFIED: fixture Map003.json] |
| `302` | Shop Processing | `[firstGoodsType: int, firstGoodsId: int, purchaseOnly: bool, reserved: bool]` | Opens the shop menu. Followed by code 605 for additional items. [VERIFIED] |
| `303` | Name Input Processing | `[actorId: int, maxCharacters: int]` | Shows the name input screen for an actor. [ASSUMED] |
| `311` | Change HP | `[actorType: int, actorId: int, operation: int, operandType: int, value: int, allowDeath: bool]` | Changes an actor's HP. [VERIFIED: fixture] |
| `312` | Change MP | `[actorType: int, actorId: int, operation: int, operandType: int, value: int]` | Changes an actor's MP. [VERIFIED: fixture] |
| `313` | Change State | `[actorType: int, actorId: int, operation: int, stateId: int]` | Adds or removes a state from an actor. [ASSUMED] |
| `314` | Recover All | `[actorType: int, actorId: int]` | Fully restores an actor's HP, MP, and removes states. [ASSUMED] |
| `315` | Change EXP | `[actorType: int, actorId: int, operation: int, operandType: int, value: int, showLevelUp: bool]` | Grants or removes experience points. [ASSUMED] |
| `316` | Change Level | `[actorType: int, actorId: int, operation: int, operandType: int, value: int, showLevelUp: bool]` | Changes an actor's level. [ASSUMED] |
| `317` | Change Parameter | `[actorType: int, actorId: int, paramType: int, operation: int, operandType: int, value: int]` | Modifies a specific stat (param index 0–7). [ASSUMED] |
| `318` | Change Skill | `[actorType: int, actorId: int, operation: int, skillId: int]` | Teaches or removes a skill. params[2]: 0=learn, 1=forget. [ASSUMED] |
| `319` | Change Equipment | `[actorId: int, equipSlot: int, itemId: int]` | Equips or removes an item. [ASSUMED] |
| `320` | Change Actor Name | `[actorId: int, name: string]` | Changes an actor's display name. [ASSUMED] |

### Code 301 — Battle Processing

```json
{"code": 301, "indent": 0, "parameters": [0, 1, true, false]}
```

| Index | Field | Values |
|-------|-------|--------|
| 0 | `troopType` | 0 = fixed troop by ID, 1 = random encounter |
| 1 | `troopId` | Troop ID from Troops.json (used when type=0) |
| 2 | `canEscape` | true = player can flee the battle |
| 3 | `canLose` | true = game does not end on party defeat |

Battle branch codes (601-604) follow the 301 to handle outcomes.

[VERIFIED: fixture Map003.json]

### Code 302 — Shop Processing

```json
{"code": 302, "indent": 0, "parameters": [0, 3, false, false]},
{"code": 605, "indent": 0, "parameters": [0, 5, 0, 0]},
{"code": 605, "indent": 0, "parameters": [1, 2, 0, 0]}
```

The first shop item is encoded in code 302 parameters. Additional items are
code 605 continuation entries (see Battle Branch / Shop Goods Codes section).

| Index | Field | Values |
|-------|-------|--------|
| 0 | First goods `itemType` | 0=item, 1=weapon, 2=armor |
| 1 | First goods `itemId` | ID from the corresponding database file |
| 2 | `purchaseOnly` | false = allow selling; true = buy only |
| 3 | reserved | always false |

[ASSUMED — verify by exporting a shop event from RPG Maker editor; HIGH priority]

### Code 311 — Change HP

```json
{"code": 311, "indent": 0, "parameters": [0, 0, 0, 0, 0, false]}
```

| Index | Field | Values |
|-------|-------|--------|
| 0 | `actorType` | 0 = fixed actor, 1 = whole party |
| 1 | `actorId` | Actor ID (used when actorType=0) |
| 2 | `operation` | 0=add, 1=subtract |
| 3 | `operandType` | 0=constant, 1=variable |
| 4 | `value` | Amount (or variable ID when operandType=1) |
| 5 | `allowDeath` | true = HP can drop to 0 (KO) |

[VERIFIED: fixture CommonEvents.json]

---

## Advanced Codes

| Code | Name | Parameters | Description |
|------|------|------------|-------------|
| `339` | Show Animation | `[characterId: int, animationId: int, wait: bool]` | Plays a battle animation on a character. [VERIFIED] |
| `340` | Balloon Icon | `[characterId: int, balloonType: int, wait: bool]` | Shows an emotion balloon above a character. [ASSUMED] |
| `346` | Show Battle Animation | `[animationId: int, wait: bool]` | Plays an animation on all battle targets. [ASSUMED] |
| `355` | Script | `[script: string]` | Evaluates a JavaScript expression. [VERIFIED] |
| `356` | Plugin Command (MV) | `[command: string]` | Calls a plugin command. Single string: `"PluginName command arg1 arg2"`. MV only. [VERIFIED] |
| `357` | Plugin Command (MZ) | `[pluginName: string, commandName: string, guid: string, args: object]` | Calls a plugin command. Object-format params. MZ only. [VERIFIED] |

### Code 355 — Script

```json
{"code": 355, "indent": 0, "parameters": ["$gameVariables.setValue(1, 100);"]}
```

Single-element array containing the JavaScript expression string.

### Code 356 — Plugin Command (MV)

```json
{"code": 356, "indent": 0, "parameters": ["PluginName CommandName arg1 arg2"]}
```

Space-delimited string. First token is the plugin name, second is the command,
remaining tokens are arguments. **MV projects only — do not use in MZ.**

### Code 357 — Plugin Command (MZ)

```json
{"code": 357, "indent": 0, "parameters": ["PluginName", "CommandName", "", {"arg1": "value1"}]}
```

| Index | Field | Values |
|-------|-------|--------|
| 0 | `pluginName` | Plugin name as registered |
| 1 | `commandName` | Command name as registered |
| 2 | `guid` | Internal GUID string (usually empty string `""` when hand-authoring) |
| 3 | `args` | Object containing named arguments |

**MZ projects only — do not use in MV.**

[VERIFIED: multiple sources; MV vs MZ distinction is critical — using the wrong code causes the plugin command to silently fail]

---

## Move Route Sub-Commands

Move route sub-commands appear inside the `route.list` array of code 205
(Set Movement Route). They have a simpler two-field structure — no `indent`.

```json
{"code": 9, "parameters": []}
```

These sub-commands are [ASSUMED] from training knowledge. Verify against
`rpg_objects.js` Game_Character.processMoveCommand for your engine version.

| Sub-Code | Name | Notes |
|----------|------|-------|
| `1` | Move Down | [ASSUMED] |
| `2` | Move Left | [ASSUMED] |
| `3` | Move Right | [ASSUMED] |
| `4` | Move Up | [ASSUMED] |
| `9` | Move at Random | [ASSUMED] — standard wanderer sub-command |
| `10` | Move Toward Player | [ASSUMED] |
| `11` | Move Away from Player | [ASSUMED] |
| `15` | 1 Step Forward | [ASSUMED] |
| `16` | 1 Step Backward | [ASSUMED] |
| `21` | Jump | [ASSUMED] — `parameters: [dx, dy]` |
| `27` | Wait | [ASSUMED] — `parameters: [frames]` |
| `0` | End of Route | Required — must be the last entry in `route.list` |

---

## Battle Branch / Shop Goods Codes

These codes appear after code 301 (Battle Processing) or code 302 (Shop
Processing) to handle outcomes.

| Code | Name | Parameters | Description |
|------|------|------------|-------------|
| `601` | If Win | `[]` | Branch block executed when the party wins the battle. [VERIFIED: fixture Map003.json] |
| `602` | If Escape | `[]` | Branch block executed when the party escapes. [VERIFIED: fixture Map003.json] |
| `603` | If Lose | `[]` | Branch block executed when the party is defeated (only when canLose=true in 301). [VERIFIED: fixture Map003.json] |
| `604` | End Battle Processing | `[]` | Closes the battle branch block. [VERIFIED: fixture Map003.json] |
| `605` | Shop Goods | `[itemType: int, itemId: int, priceType: int, price: int]` | Adds one item to the shop started by code 302. [VERIFIED] |

### Code 605 — Shop Goods

```json
{"code": 605, "indent": 0, "parameters": [0, 5, 0, 0]}
```

| Index | Field | Values |
|-------|-------|--------|
| 0 | `itemType` | 0 = item, 1 = weapon, 2 = armor |
| 1 | `itemId` | ID from the corresponding database file |
| 2 | `priceType` | 0 = use item's default price from database |
| 3 | `price` | Custom price (only used when priceType = 1) |

### Battle Branch Example

```json
{"code": 301, "indent": 0, "parameters": [0, 1, true, false]},
{"code": 601, "indent": 0, "parameters": []},
// If Win branch
{"code": 401, "indent": 1, "parameters": ["Victory!"]},
{"code": 602, "indent": 0, "parameters": []},
// If Escape branch
{"code": 401, "indent": 1, "parameters": ["You fled!"]},
{"code": 603, "indent": 0, "parameters": []},
// If Lose branch (only present when canLose=true)
{"code": 401, "indent": 1, "parameters": ["Defeated..."]},
{"code": 604, "indent": 0, "parameters": []},
// End Battle Processing
{"code": 0, "indent": 0, "parameters": []}
```

---

## Indent Rules

The `indent` field tracks nesting depth. Getting indent wrong corrupts the
event's logical structure and may crash the game when the event runs.

| Context | Indent Value |
|---------|-------------|
| Top-level commands in an event list | `0` |
| Commands inside a choice branch (after 402 or 403) | `1` (one more than the 102) |
| Dialog block (101+401) inside a choice branch | Same indent as the 402 that opened the branch |
| Commands inside a conditional branch (after 111 or 411) | One more than the 111 |
| Code 411 (Else) | Same indent as the 111 it pairs with |
| Code 412 (End Conditional) | Same indent as the 111 it closes |
| Commands inside a loop (after 112) | One more than the 112 |
| Code 413 (Repeat Above) | Same indent as the 112 it closes |
| Code 404 (End Choice) | Same indent as the 402/403 it closes |
| Nested choice inside a choice | Each level adds 1 |

---

## Complete Walkthrough — Innkeeper Dialog

This is the actual fixture at `fixtures/example-mv-project/data/CommonEvents.json`,
event 1 ("Innkeeper Dialog"):

```json
{ "code": 101, "indent": 0, "parameters": ["Actor1", 0, 0, 2] }
```
*Open dialog window. Face: Actor1, portrait 0. Window style. Position: bottom.*

```json
{ "code": 401, "indent": 0, "parameters": ["Welcome to the village inn!"] }
{ "code": 401, "indent": 0, "parameters": ["Would you like to rest? It's 50 gold."] }
```
*Two lines of dialog. Same indent (0) as the opening 101.*

```json
{ "code": 102, "indent": 0, "parameters": [["Yes", "No"], 1, 0, 2, 0] }
```
*Show choices: "Yes" and "No". cancelType=1 maps cancel to the "No" choice.*

```json
{ "code": 402, "indent": 1, "parameters": [0, "Yes"] }
```
*Branch for choice index 0 ("Yes"). Indent increases to 1.*

```json
{ "code": 101, "indent": 2, "parameters": ["Actor1", 0, 0, 2] }
{ "code": 401, "indent": 2, "parameters": ["Sweet dreams!"] }
```
*Dialog inside the "Yes" branch. Indent is 2 (one more than the 402).*

```json
{ "code": 402, "indent": 1, "parameters": [1, "No"] }
```
*Branch for choice index 1 ("No"). Back to indent 1.*

```json
{ "code": 101, "indent": 2, "parameters": ["Actor1", 0, 0, 2] }
{ "code": 401, "indent": 2, "parameters": ["Come back anytime."] }
```
*Dialog inside the "No" branch. Indent is 2.*

```json
{ "code": 404, "indent": 1, "parameters": [] }
```
*End Choice. Same indent (1) as the 402 entries it pairs with.*

```json
{ "code": 0, "indent": 0, "parameters": [] }
```
*List terminator. Always last. Always indent 0.*

---

## Anti-Patterns

**Never insert commands after the code-0 terminator.**
Code 0 must be the final entry in every event command list. RPG Maker stops
processing at code 0. Any commands after it are silently ignored.

```python
# WRONG — appends after terminator
event["list"].append(new_dialog_command)

# CORRECT — insert before the code-0 entry
terminator_idx = next(i for i, cmd in enumerate(event["list"]) if cmd["code"] == 0)
for i, cmd in enumerate(new_block):
    event["list"].insert(terminator_idx + i, cmd)
```

**Never mix indent levels within a single dialog block.**
All code-401 entries that belong to the same visible text window share the
same `indent` as their opening code-101.

**Never renumber event IDs.**
Events in both CommonEvents and Map files have `id` fields that match their
array position. Renumbering silently breaks every cross-file reference.

**Do not use code 413 to close a conditional branch.**
Code 413 ("Repeat Above") closes a Loop block (code 112). It does NOT close a
Conditional Branch (code 111). The correct closing code for a conditional
branch is 412. Using 413 instead corrupts event flow silently — the
interpreter misidentifies block boundaries without producing any error.

```json
// WRONG — 413 closes a Loop, not a Conditional Branch
{"code": 111, "indent": 0, "parameters": [0, 1, 0]},
{"code": 401, "indent": 1, "parameters": ["If branch"]},
{"code": 413, "indent": 0, "parameters": []},  // BUG — wrong closing code

// CORRECT
{"code": 111, "indent": 0, "parameters": [0, 1, 0]},
{"code": 401, "indent": 1, "parameters": ["If branch"]},
{"code": 412, "indent": 0, "parameters": []}   // Correct — End of Conditional Branch
```

**Do not use integer params for self-switch code 123.**
Code 123 (Control Self Switch) requires string letters — `"A"`, `"B"`, `"C"`,
`"D"`. Passing integers (0, 1, 2, 3) silently fails at runtime.

**Do not use plugin command code 356 in MZ projects (or 357 in MV).**
MV uses code 356 with a single space-separated string parameter. MZ uses code
357 with an array of named parameters. Using the wrong code causes the plugin
command to silently fail without any error message.

---

*Reference for: `skills/rpgmaker-events/SKILL.md`, `skills/rpgmaker-dialog/SKILL.md`,
and any script that reads or writes event command lists.*
