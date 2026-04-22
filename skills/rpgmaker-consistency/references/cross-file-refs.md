# Cross-File Reference Map

Every field in an RPG Maker MV/MZ data file that stores a database ID is a
cross-file reference. If the target entry does not exist at that array index
(the array is shorter than the ID, or the entry is null), RPG Maker silently
uses a fallback value or crashes at runtime. This document maps every known
reference type so validators know what to check.

---

## Event Command References

Event commands reference database entries via their `parameters` array. The
field path notation below refers to the command object:
`{"code": N, "indent": I, "parameters": [...]}`.

| Code | Name | Parameter Field | References | Notes |
|------|------|-----------------|------------|-------|
| `121` | Control Switches | `params[0]` to `params[1]` | System.json `switches` array | Range SET/CLEAR -- both endpoints must be within array length |
| `122` | Control Variables | `params[0]` to `params[1]` | System.json `variables` array | Range operation -- both endpoints must be within array length |
| `126` | Change Items | `params[0]` | Items.json by ID | ID must exist and not be null |
| `127` | Change Weapons | `params[0]` | Weapons.json by ID | ID must exist and not be null |
| `128` | Change Armors | `params[0]` | Armors.json by ID | ID must exist and not be null |
| `129` | Change Party Member | `params[0]` | Actors.json by ID | ID must exist and not be null |
| `301` | Battle Processing | `params[0]` | Troops.json by ID | ID must exist and not be null |
| `302` | Shop Processing | `goods[n][1]` | Items/Weapons/Armors.json by ID | `goods[n][0]` selects type: 0=item, 1=weapon, 2=armor |
| `111` | Conditional Branch | varies by `params[0]` | Switches (params[0]=0), Variables (params[0]=1), Self-Switches (params[0]=2), Items (params[0]=4), Actors (params[0]=5) | Only ID-bearing subtypes are checked; numeric/script subtypes are skipped |

### Conditional Branch Subtypes (Code 111)

| `params[0]` | Subtype | ID Field | Target File |
|-------------|---------|----------|-------------|
| `0` | Switch | `params[1]` | System.json `switches` |
| `1` | Variable | `params[1]` | System.json `variables` |
| `2` | Self-Switch | string (`"A"`--`"D"`) | (no file reference -- per-event state) |
| `4` | Item | `params[1]` | Items.json |
| `5` | Actor | `params[1]` | Actors.json |

---

## Dialog Text Code References

Text codes embedded in dialog strings (code 401 parameters) are cross-file
references. They appear in the format `\N[id]` or `\I[id]`.

| Text Code | Pattern | References | Notes |
|-----------|---------|------------|-------|
| `\N[id]` | Actor name display | Actors.json by ID | If actor ID does not exist, the game displays an empty string or crashes |
| `\I[id]` | Icon display | Items.json by ID | Used for item icons in message windows |

Text codes also appear in CommonEvents and Map event dialog lines. Checkers
must scan all `list` arrays containing code 401 entries.

---

## Database Cross-References

These are ID fields stored directly in database JSON files (not in event
command lists). They do not depend on event traversal -- a JSON load and field
inspection is sufficient.

| Source File | Source Field Path | Target File | Notes |
|-------------|-------------------|-------------|-------|
| `Enemies.json` | `actions[n].skillId` | `Skills.json` | Enemy uses this skill during battle; ID 1 (Attack) is the default |
| `Troops.json` | `members[n].enemyId` | `Enemies.json` | Troop formation lists these enemies |
| `Classes.json` | `learnings[n].skillId` | `Skills.json` | Character class learns this skill when reaching `learnings[n].level` |
| `Actors.json` | `classId` | `Classes.json` | Actor belongs to this class |
| `Actors.json` | `equips[n]` | `Weapons.json` (n=0) / `Armors.json` (n=1..4) | Initial equipment; ID 0 means no equipment (valid) |
| `Skills.json` | `stypeId` | `System.json skillTypes` | Skill type category index |
| `Items.json` | `itypeId` | `System.json itemTypes` (MZ only) | Item type index; MV uses a fixed set |
| `Weapons.json` | `wtypeId` | `System.json weaponTypes` | Weapon type index |
| `Armors.json` | `atypeId` | `System.json armorTypes` | Armor type index |

### Notes on equips[n] in Actors.json

The `equips` array has 5 slots by default:
- `equips[0]` -- weapon (Weapons.json)
- `equips[1]` -- shield (Armors.json)
- `equips[2]` -- head armor (Armors.json)
- `equips[3]` -- body armor (Armors.json)
- `equips[4]` -- accessory (Armors.json)

ID `0` in any slot means no initial equipment and is always valid. Only
non-zero IDs are checked against the target file.

---

## Switch and Variable Bounds

`System.json` defines the full list of named switches and variables. The
array length minus 1 (accounting for the empty string at index 0) is the
maximum valid ID.

```
System.json["switches"] = ["", "Quest Active", "DayNight", ...]
                           ^0   ^1              ^2
Maximum valid switch ID  = len(switches) - 1
```

Any event command using a switch ID greater than `len(switches) - 1` is an
out-of-bounds reference. RPG Maker treats it as an unnamed switch in the
out-of-range slot, which may silently work or may cause save data bloat.

The same rule applies to `System.json["variables"]`.

### Self-Switches

Self-switches (`"A"`, `"B"`, `"C"`, `"D"`) are stored in the game's save data
per event instance, not in any JSON file. They are always valid and require no
cross-file check.

---

## MZ-Specific Additions

RPG Maker MZ adds `pluginCommands` as a new event command structure (code
`357`), replacing the single-string code `356` from MV. The `357` command does
not reference database IDs in its parameters -- it calls named plugin functions
by string. No cross-file validation is needed for code 357.

MZ map files store `events` as an object keyed by string ID instead of an
array. Traversal must use `events.values()` (or iterate over object keys) when
the project is detected as MZ format.
