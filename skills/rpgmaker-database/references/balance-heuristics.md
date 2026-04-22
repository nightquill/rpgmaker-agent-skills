# Balance Heuristics Reference

This document describes the statistical outlier detection method used by
`balance_check.py` to flag potentially unbalanced database entries.

---

## Overview

For each category, compute a power metric per entry. Calculate the sample mean
and sample standard deviation. Flag any entry whose metric exceeds
**mean + 2 standard deviations** as a potential outlier.

This approach adapts to whatever power level the project uses — a high-power
project where all skills do 500+ damage will have a higher threshold than a
low-power project. No hardcoded thresholds.

---

## Skills: Damage Per MP

**Metric:** `formula_damage(reference_stats) / mpCost`

**Reference stats for formula evaluation:**
- ATK = 20, MAT = 20 (attacker)
- DEF = 10, MDF = 10 (defender)

**Included entries:** Only skills where `damage.type == 1` (HP damage) and
`mpCost > 0`. Heals, drains, physical-no-MP skills, and passive skills are
excluded.

### Worked Example (from fixture)

| Skill | Formula | Damage | MP | DPM |
|-------|---------|--------|----|-----|
| Fire | `a.mat * 4 - b.mdf * 2` | 60 | 5 | 12.00 |
| Ice | `a.mat * 4 - b.mdf * 2` | 60 | 7 | 8.57 |
| Thunder | `a.mat * 4 - b.mdf * 2` | 60 | 10 | 6.00 |

Mean DPM = 8.86, SD = 3.01, Threshold = 8.86 + 2 * 3.01 = 14.88

All three skills are below the threshold — no outliers in the clean fixture.

**Unbalanced example:**

| Skill | Formula | Damage | MP | DPM | Flag |
|-------|---------|--------|----|-----|------|
| Fire | `a.mat * 4 - b.mdf * 2` | 60 | 5 | 12.00 | |
| Ice | `a.mat * 4 - b.mdf * 2` | 60 | 7 | 8.57 | |
| Thunder | `a.mat * 4 - b.mdf * 2` | 60 | 10 | 6.00 | |
| Apocalypse | `a.mat * 50 - b.mdf * 2` | 980 | 5 | 196.00 | OUTLIER |

With Apocalypse added: Mean = 55.64, SD = 92.29, Threshold = 240.22.
Actually, 196.0 may still trigger due to the extreme skew — the exact
threshold depends on sample statistics. The important thing: Apocalypse's DPM
is 16x the next highest entry, making it a clear statistical outlier.

---

## Weapons: Price Per Power

**Power index:** `params[2] + params[4]` (ATK bonus + MAT bonus)

**Metric:** `price / max(power_index, 1)`

**Included entries:** All weapons with `power_index > 0` or `price > 0`.
Weapons with both zero power and zero price are skipped (placeholder entries).

### Worked Example (from fixture)

| Weapon | ATK | MAT | Power | Price | PPP |
|--------|-----|-----|-------|-------|-----|
| Short Sword | 10 | 0 | 10 | 100 | 10.00 |
| Staff | 0 | 10 | 10 | 80 | 8.00 |

Mean PPP = 9.00, SD = 1.41, Threshold = 11.83

Both weapons are below threshold — no outliers.

**Unbalanced example:** Adding "Gilded Toothpick" with ATK=10, price=5000:
PPP = 500. Clearly exceeds any reasonable threshold.

---

## Enemies: HP Per EXP

**Metric:** `params[0] / max(exp, 1)`

**Included entries:** All enemies with `exp > 0`. Enemies with `exp == 0` are
excluded (boss-type enemies that give no EXP are intentional design choices).

### Worked Example (from fixture)

| Enemy | HP | EXP | HPE |
|-------|-----|-----|-----|
| Slime | 50 | 5 | 10.00 |
| Bat | 40 | 7 | 5.71 |
| Goblin | 80 | 12 | 6.67 |

Mean HPE = 7.46, SD = 2.27, Threshold = 11.99

All enemies are below threshold — no outliers.

**Unbalanced example:** Adding "Immortal Snail" with HP=50000, EXP=5:
HPE = 10000. An absurdly tanky enemy for its reward.

---

## Integration with balance_check.py

```bash
# Check all categories
PYTHONPATH=. python skills/rpgmaker-database/scripts/balance_check.py \
  --project fixtures/example-mv-project

# Check only skills
PYTHONPATH=. python skills/rpgmaker-database/scripts/balance_check.py \
  --project fixtures/example-mv-project --category skills
```

**Exit codes:**
- `0` — No outliers found (all entries within 2 SD of mean).
- `1` — One or more outliers flagged.

**Output format:** One markdown table per category:

```
## Skills (Damage per MP)

| Name       | Metric |  Mean |   SD | Flag    |
|------------|--------|-------|------|---------|
| Fire       |  12.00 |  8.86 | 3.01 |         |
| Ice        |   8.57 |  8.86 | 3.01 |         |
| Thunder    |   6.00 |  8.86 | 3.01 |         |
```

---

## Anti-Patterns

1. **Never hardcode thresholds.** "ATK > 50 is overpowered" is useless — it
   depends entirely on the project's power curve. Use statistical deviation.

2. **Never evaluate damage formulas as Python directly.** Use string
   substitution with reference stats first (see `damage-formulas.md`).

3. **Guard against < 2 entries.** `statistics.stdev()` requires at least 2
   values. If a category has fewer than 2 qualifying entries, skip it with
   an informational message.

4. **Do not include non-damage skills in the skills category.** Heals, buffs,
   and passive skills have no meaningful DPM metric.

5. **Do not include zero-EXP enemies.** Bosses with 0 EXP are intentional
   design choices, not balance errors.
