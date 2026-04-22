# Contributing to RPG Maker Agent Skills

Thank you for your interest in contributing! This project is a skill pack for AI coding
agents — keeping it correct, safe, and easy to install is what matters most.

## Getting Started

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/nightquill/rpgmaker-agent-skills.git
   cd rpgmaker-agent-skills
   ```
3. Install dev dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```
4. Run tests to confirm everything passes:
   ```bash
   pytest tests/ -v
   ```

## Development Guidelines

### Code Style

- Python 3.10+ with type hints where practical
- Zero runtime dependencies beyond stdlib (except `jsonschema` for validation scripts)
- Use `argparse` for all script CLIs — no click, typer, or other third-party CLI libs
- All scripts default to `--dry-run` mode; require explicit `--apply` for write operations
- Follow existing code style in `scripts/lib/` (no external linter configured yet)

### Data Safety Rules

These are non-negotiable. The core value of this project is that agents can be trusted with
RPG Maker data files. Any change that weakens these rules will be rejected:

1. **Never renumber IDs** — RMMV/MZ positional arrays use array index as the ID; renumbering silently breaks every cross-file reference
2. **Never delete index 0** — index 0 is always `null` in database arrays; deleting it shifts all IDs
3. **Always create a `.bak` backup before modifying files** — use `shutil.copy2` before any write
4. **Dry-run by default** — all write scripts must default to preview mode; use `--apply` to commit changes
5. **Validate before and after mutations** — use `jsonschema.validate()` against the relevant schema

### SKILL.md Guidelines

- Keep SKILL.md body under 500 lines (spec requirement for context efficiency)
- Put detailed content in `references/*.md` (progressive disclosure pattern)
- Frame all AI outputs as "drafts for developer review" — not decisions, not final outputs
- Include YAML frontmatter with `name`, `description`, `license`, `metadata`, `compatibility`
- Cross-platform fields only in SKILL.md — Claude Code-only fields go in separate docs

### Testing

- All Python scripts must have pytest tests in `tests/`
- Test against `fixtures/example-mv-project/` for happy-path tests
- Test against `fixtures/broken/` subdirectories for error-detection tests
- Use subprocess-based testing for CLI scripts (test what the user actually runs)
- Golden file tests for output validation where deterministic output is important
- CI runs Python 3.10, 3.11, 3.12 — do not use language features from 3.11+

### Pull Request Process

1. Create a feature branch from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. Write tests for new functionality before writing the implementation
3. Ensure `pytest tests/ -v` passes locally on Python 3.10+
4. Update `CHANGELOG.md` under `[Unreleased]` with a brief description of your change
5. Submit a pull request with a clear description of what the change does and why
6. Ensure CI passes — PRs with failing tests will not be merged

## Reporting Issues

Use GitHub Issues. Include:

- Python version (`python --version`)
- Operating system (Windows / macOS / Linux + version)
- RPG Maker version (MV or MZ)
- Steps to reproduce, including the script invocation
- The exact error message or unexpected output
- For data corruption issues: the relevant JSON file (redact character/item names if needed)

## File Scope

| Directory | Purpose |
|-----------|---------|
| `skills/` | SKILL.md files and references — agent-facing documentation |
| `scripts/` | Python helper scripts — CLI tools invoked by developers |
| `scripts/lib/` | Shared Python library (`safe_write`, `event_traverse`, etc.) |
| `schemas/` | JSON Schema Draft 2020-12 files for MV data validation |
| `tests/` | pytest test suite |
| `fixtures/` | Example MV project and broken fixtures for testing |
| `docs/` | Agent-specific installation and usage guides |

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
