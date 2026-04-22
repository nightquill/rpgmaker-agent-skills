# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2026-04-21

### Added

- Core skill (`rpgmaker-core`): MV/MZ project detection, safety rules, and project structure documentation
- Dialog skill (`rpgmaker-dialog`): NPC dialog extraction, injection, and reference validation with text code preservation
- Database skill (`rpgmaker-database`): Balance checking, safe entry addition, schema validation for all database file types
- Events skill (`rpgmaker-events`): Event scaffolding (6 patterns), switch/variable tracking, full event command code reference
- Consistency skill (`rpgmaker-consistency`): Cross-file reference checking, switch collision detection, umbrella project validator
- Helper scripts:
  - `validate_project.py` — Umbrella validator running all checkers in one pass
  - `check_orphaned_refs.py` — Cross-file reference checker for items, skills, actors, switches, variables
  - `check_switch_collisions.py` — Switch collision detector for copy-paste bugs
  - `scaffold_event.py` — Event scaffolding with 6 parameterized patterns
  - `list_switches.py` — Switch and variable inventory across all maps
  - `find_event_refs.py` — Event reference search
  - `extract_npc_lines.py` — NPC dialog extraction to text format
  - `inject_dialog.py` — Dialog injection back into map events
  - `balance_check.py` — Database balance heuristics
  - `add_skill.py` — Safe skill addition with ID preservation
  - `add_enemy.py` — Safe enemy addition with ID preservation
  - `validate_database.py` — Database file schema validation
  - `validate_dialog_refs.py` — Dialog reference validator for `\N[]`, `\I[]` codes
- Install scripts for macOS/Linux (`install.sh`) and Windows (`install.ps1`)
- JSON schemas (Draft 2020-12) for all MV data file types
- Example MV project fixture for testing (3 maps, 2 actors, 5 skills, 3 items, 3 enemies)
- Broken fixture sets for orphaned-refs and switch-collision defect testing
- Shared reference docs: text codes, event command codes (full 100s-600s range), plugin format, common pitfalls
- Agent-specific documentation for Claude Code, Codex, and Cursor
- CI pipeline (GitHub Actions) with Python 3.10/3.11/3.12 matrix and coverage reporting
