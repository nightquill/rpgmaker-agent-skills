# Validation Rules

This document defines the exact rules applied by each consistency checker
script. All checkers follow a two-severity model: **ERROR** for issues that
would cause a runtime crash or silent data loss, and **WARNING** for issues
that may be intentional and require developer review.

---

## Severity Levels

| Severity | Definition | Exit Code | When to Use |
|----------|-----------|-----------|-------------|
| **ERROR** | An orphaned reference where the target ID does not exist in the referenced file. The game will crash, produce garbage output, or silently use wrong data at runtime. | `exit 1` | Missing skill IDs, item IDs, actor IDs, out-of-bounds switch IDs in events |
| **WARNING** | A suspicious pattern that may be intentional. The developer must confirm whether it is a bug. | `exit 0` | Switch SET in multiple maps, unnamed switch used as global, unusually large ID values |

`validate_project.py` exits with code `1` if any checker reports at least one ERROR.
It exits `0` only when all checkers report zero errors (warnings are allowed).

---

## check_orphaned_refs.py Rules

This checker scans all event command lists (CommonEvents and Map events via
`event_traverse.iter_event_lists()`) and all database JSON files for references
to IDs that do not exist in their target file.

### Event Command Reference Checks

| Rule ID | Event Code | Check | Severity |
|---------|-----------|-------|---------|
| ORP-01 | `126` Change Items | `params[0]` must be a valid index in Items.json (not null, within array bounds) | ERROR |
| ORP-02 | `127` Change Weapons | `params[0]` must be a valid index in Weapons.json | ERROR |
| ORP-03 | `128` Change Armors | `params[0]` must be a valid index in Armors.json | ERROR |
| ORP-04 | `129` Change Party Member | `params[0]` must be a valid index in Actors.json | ERROR |
| ORP-05 | `301` Battle Processing | `params[0]` must be a valid index in Troops.json | ERROR |
| ORP-06 | `302` Shop Processing | `goods[n][1]` must be valid in Items/Weapons/Armors.json based on `goods[n][0]` type | ERROR |
| ORP-07 | `121` Control Switches | `params[0]` and `params[1]` must be within `len(System.json["switches"]) - 1` | ERROR |
| ORP-08 | `122` Control Variables | `params[0]` and `params[1]` must be within `len(System.json["variables"]) - 1` | ERROR |
| ORP-09 | `111` Conditional Branch (switch) | `params[1]` must be within switch array bounds when `params[0] == 0` | ERROR |
| ORP-10 | `111` Conditional Branch (variable) | `params[1]` must be within variable array bounds when `params[0] == 1` | ERROR |
| ORP-11 | `111` Conditional Branch (item) | `params[1]` must be valid in Items.json when `params[0] == 4` | ERROR |
| ORP-12 | `111` Conditional Branch (actor) | `params[1]` must be valid in Actors.json when `params[0] == 5` | ERROR |

### Dialog Text Code Checks

| Rule ID | Pattern | Check | Severity |
|---------|---------|-------|---------|
| ORP-13 | `\N[id]` in code 401 text | `id` must be a valid index in Actors.json | ERROR |
| ORP-14 | `\I[id]` in code 401 text | `id` must be a valid index in Items.json | ERROR |

### Database Cross-Reference Checks

| Rule ID | Source | Field | Target | Severity |
|---------|--------|-------|--------|---------|
| ORP-15 | Enemies.json | `actions[n].skillId` | Skills.json | ERROR |
| ORP-16 | Troops.json | `members[n].enemyId` | Enemies.json | ERROR |
| ORP-17 | Classes.json | `learnings[n].skillId` | Skills.json | ERROR |
| ORP-18 | Actors.json | `classId` | Classes.json | ERROR |
| ORP-19 | Actors.json | `equips[0]` | Weapons.json (if non-zero) | ERROR |
| ORP-20 | Actors.json | `equips[1..4]` | Armors.json (if non-zero) | ERROR |

### Validity Definition

An ID is **valid** if ALL of the following are true:
1. The target JSON file exists and is a parseable array
2. The ID is a positive integer greater than 0
3. `id < len(target_array)` (within bounds)
4. `target_array[id] is not None` (not a null slot)

ID `0` is always treated as "none" and is never checked (equips, weapon slots,
etc. use 0 to indicate empty).

---

## check_switch_collisions.py Rules

This checker identifies switches that are SET (not just read) in more than one
distinct map. Setting the same switch from two different maps is often a
copy-paste error, but may be intentional for global flags.

### Detection Rules

| Rule ID | Check | Severity |
|---------|-------|---------|
| COL-01 | Collect all code `121` (Control Switches) commands across all Map files, grouped by switch ID and source map filename | — |
| COL-02 | A switch is a **collision candidate** if it appears in code `121` in 2 or more distinct map files | WARNING |
| COL-03 | Apply global-switch heuristic (see below) to filter intentional globals | — |
| COL-04 | Report remaining candidates as WARNING with the list of maps that SET the switch | WARNING |

CommonEvents are **excluded** from collision detection -- a common event that
sets a switch is called explicitly and does not represent a map-level collision.

### Global-Switch Heuristic

A switch is treated as **intentionally global** (and NOT flagged) when the
switch name in `System.json["switches"][id]` meets any of the following:

- Name starts with an uppercase letter (`"Quest Active"`, `"DayNight"`)
- Name contains an underscore (`"BOSS_DEFEATED"`, `"shop_open"`)
- Name starts with `GLOBAL` (case-insensitive)
- Name is `"Quest Active"` or otherwise indicates a project-wide state

A switch is treated as a **local collision candidate** (and IS flagged) when:

- Name is an empty string `""` (unnamed switch)
- Name is all lowercase with no underscores (e.g., `"trigger"`, `"door"`)

When the heuristic is ambiguous, the switch is flagged as a WARNING so the
developer can review it.

### Reading vs Setting

- Code `121` (Control Switches) with `params[2] == 0` = SET ON -- flagged
- Code `121` (Control Switches) with `params[2] == 1` = SET OFF -- also flagged (still a collision if done from multiple maps)
- Code `111` (Conditional Branch checking a switch) = READ ONLY -- never flagged

---

## validate_project.py Behavior

The umbrella runner imports and executes sub-checkers in sequence, collecting
all findings into a single structured markdown report.

### Execution Order

1. `check_orphaned_refs` -- cross-file reference check (can produce ERRORs)
2. `check_switch_collisions` -- switch SET collision check (warnings only)
3. (Optional) `validate_dialog_refs` -- dialog text code check (if present)
4. (Optional) `validate_database` -- database schema check (if present)

### Report Format

```markdown
# Project Validation Report

**Project:** path/to/project
**Date:** YYYY-MM-DD HH:MM:SS

## Summary

| Checker | Errors | Warnings |
|---------|--------|---------|
| check_orphaned_refs | N | N |
| check_switch_collisions | 0 | N |
| **Total** | **N** | **N** |

## Orphaned Reference Errors

| Location | Code | ID | Target File | Message |
|----------|------|----|-------------|---------|
| CommonEvent:1:Setup:cmd3 | 126 | 99 | Items.json | Item ID 99 not found |
| Map001:Event2:Chest:Page0:cmd1 | 121 | 999 | System.json switches | Switch ID 999 out of bounds |

## Switch Collision Warnings

| Switch ID | Name | Maps |
|-----------|------|------|
| 5 | (unnamed) | Map001.json, Map002.json |
```

### Exit Codes

- `exit 0` -- zero ERRORs (warnings may be present)
- `exit 1` -- one or more ERRORs found

The exit code is determined by the total ERROR count across all sub-checkers.
Warnings never contribute to a non-zero exit.
