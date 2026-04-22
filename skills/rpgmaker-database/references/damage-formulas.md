# Damage Formula DSL Reference

The `damage.formula` field in Skills.json and Items.json is a **JavaScript
expression string** evaluated by the RPG Maker engine at runtime. The engine
provides two objects: `a` (the acting battler) and `b` (the target battler).

---

## Formula Variables

| Variable | Meaning | Type |
|----------|---------|------|
| `a.atk` | Attacker's ATK (physical attack power) | integer |
| `a.def` | Attacker's DEF (physical defense) | integer |
| `a.mat` | Attacker's MAT (magic attack power) | integer |
| `a.mdf` | Attacker's MDF (magic defense) | integer |
| `a.agi` | Attacker's AGI (agility) | integer |
| `a.luk` | Attacker's LUK (luck) | integer |
| `a.hp` | Attacker's current HP | integer |
| `a.mp` | Attacker's current MP | integer |
| `a.tp` | Attacker's current TP | integer |
| `a.mhp` | Attacker's max HP | integer |
| `a.mmp` | Attacker's max MP | integer |
| `a.level` | Attacker's level (actors only; enemies always 1) | integer |
| `b.atk` | Target's ATK | integer |
| `b.def` | Target's DEF | integer |
| `b.mat` | Target's MAT | integer |
| `b.mdf` | Target's MDF | integer |
| `b.agi` | Target's AGI | integer |
| `b.luk` | Target's LUK | integer |
| `b.hp` | Target's current HP | integer |
| `b.mp` | Target's current MP | integer |
| `b.tp` | Target's current TP | integer |
| `b.mhp` | Target's max HP | integer |
| `b.mmp` | Target's max MP | integer |
| `b.level` | Target's level | integer |
| `v[n]` | Game Variable #n | integer |

---

## damage.type Codes

| Code | Meaning | Formula Effect |
|------|---------|----------------|
| 0 | None | Formula is ignored. |
| 1 | HP Damage | Positive result = HP loss on target. |
| 2 | MP Damage | Positive result = MP loss on target. |
| 3 | HP Recover | Positive result = HP gain on target. |
| 4 | MP Recover | Positive result = MP gain on target. |
| 5 | HP Drain | HP damage to target; same amount heals attacker. |
| 6 | MP Drain | MP damage to target; same amount restores attacker. |

---

## Common Patterns

### Physical Damage

Standard melee formula scaling with ATK vs DEF:

```
a.atk * 4 - b.def * 2
```

Typical multipliers: `* 2` (weak), `* 4` (normal), `* 6` (strong).

### Magical Damage

Standard spell formula scaling with MAT vs MDF:

```
a.mat * 4 - b.mdf * 2
```

### Healing

Flat heal with MAT scaling:

```
a.mat * 2 + 20
```

Note: For healing skills, `damage.type` must be `3` (HP Recover).

### HP-Percentage Attack

Deals damage based on the target's current HP:

```
b.hp * 0.1
```

### Mixed Physical + Magical

```
(a.atk + a.mat) * 3 - (b.def + b.mdf)
```

### Level-Scaled

```
a.atk * 4 * (1 + a.level / 100) - b.def * 2
```

### Guaranteed Minimum

```
Math.max(a.atk * 4 - b.def * 2, 1)
```

Uses JavaScript `Math.max` to guarantee at least 1 damage.

### Conditional

```
a.hp < a.mhp / 2 ? a.atk * 8 - b.def * 2 : a.atk * 4 - b.def * 2
```

Double damage when attacker is below 50% HP.

---

## Pitfall: These Are JavaScript

Damage formulas are JavaScript, **not Python**. Key differences that affect
tools and scripts:

1. **`b.def`** — `def` is a Python keyword. You cannot directly evaluate this
   in Python. Replace variables with numeric values via string substitution
   before any evaluation.

2. **`Math.max()`, `Math.min()`** — JavaScript builtins that don't exist in
   Python. Replace with Python equivalents if evaluating.

3. **Integer division** — JavaScript `/` always returns float. Python `//` is
   integer division. Use Python `/` for consistency.

4. **Ternary syntax** — JavaScript uses `? :`, Python uses `if/else`. Do not
   attempt to evaluate ternary formulas in Python.

### Safe Evaluation Pattern

For `balance_check.py` and similar analysis tools, use string substitution
with known reference stats, then evaluate the resulting numeric expression:

```python
def formula_to_damage(formula: str) -> float:
    """Evaluate a damage formula with reference stats."""
    expr = formula
    expr = expr.replace("a.atk", "20").replace("a.mat", "20")
    expr = expr.replace("b.def", "10").replace("b.mdf", "10")
    expr = expr.replace("a.luk", "10").replace("b.hp", "500")
    # After substitution, expr is a pure numeric expression
    try:
        return max(0.0, float(eval(expr)))
    except Exception:
        return 0.0
```

This is safe because all variables are replaced with numeric literals before
`eval()` runs — no user-controlled code reaches the interpreter.
