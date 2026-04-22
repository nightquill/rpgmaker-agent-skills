from __future__ import annotations

"""Balance outlier detection for RPG Maker MV/MZ database files.

Computes per-category power metrics and flags entries that exceed
mean + 2 standard deviations as potential balance outliers.

Usage:
    python balance_check.py --project <path> [--category skills|weapons|enemies|all]

Exit codes:
    0 -- no outliers found
    1 -- one or more outliers flagged
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[3]))  # repo root

import argparse
import json
import os
import statistics

# Reference stats for formula evaluation
REF_ATK = 20
REF_MAT = 20
REF_DEF = 10
REF_MDF = 10


def formula_to_damage(formula: str) -> float:
    """Evaluate a damage formula with reference stat values.

    Substitutes known variables with numeric literals, then evaluates
    the resulting arithmetic expression. Safe because all variables are
    replaced before eval() runs.
    """
    expr = formula
    expr = expr.replace("a.atk", str(REF_ATK))
    expr = expr.replace("a.mat", str(REF_MAT))
    expr = expr.replace("a.luk", "10")
    expr = expr.replace("b.def", str(REF_DEF))
    expr = expr.replace("b.mdf", str(REF_MDF))
    expr = expr.replace("b.hp", "500")
    try:
        return max(0.0, float(eval(expr)))
    except Exception:
        return 0.0


def skill_dpm(skill: dict) -> float | None:
    """Compute damage-per-MP for a skill. Returns None if not applicable."""
    damage = skill.get("damage", {})
    if damage.get("type") != 1:
        return None
    mp_cost = skill.get("mpCost", 0)
    if mp_cost <= 0:
        return None
    formula = damage.get("formula", "0")
    dmg = formula_to_damage(formula)
    return dmg / mp_cost


def weapon_price_per_power(weapon: dict) -> float | None:
    """Compute price-per-power for a weapon. Returns None if trivial."""
    params = weapon.get("params", [0] * 8)
    power_index = params[2] + params[4] if len(params) > 4 else 0
    price = weapon.get("price", 0)
    if power_index == 0 and price == 0:
        return None
    return price / max(power_index, 1)


def enemy_hp_per_exp(enemy: dict) -> float | None:
    """Compute HP-per-EXP for an enemy. Returns None if exp is 0."""
    exp = enemy.get("exp", 0)
    if exp <= 0:
        return None
    params = enemy.get("params", [0] * 8)
    hp = params[0] if len(params) > 0 else 0
    return hp / max(exp, 1)


def flag_outliers(entries, metric_fn, threshold_sd=2.0):
    """Compute metrics and flag outliers using leave-one-out statistics.

    For each entry, computes mean and SD of all OTHER entries, then checks
    if this entry exceeds that leave-one-out mean + threshold_sd * SD.
    This prevents a single extreme outlier from inflating the SD so much
    that it masks itself — a known problem with small sample sizes.

    Returns (rows, mean, sd, outlier_entries) where rows is a list of
    (name, metric_value, is_outlier) tuples, and mean/sd are the overall
    statistics for display purposes.
    """
    scored = []
    for entry in entries:
        metric = metric_fn(entry)
        if metric is not None:
            scored.append((entry.get("name", "???"), metric))

    if len(scored) < 2:
        return ([], 0.0, 0.0, [])

    values = [v for _, v in scored]
    overall_mean = statistics.mean(values)
    overall_sd = statistics.stdev(values)

    rows = []
    outliers = []
    for i, (name, value) in enumerate(scored):
        # Leave-one-out: compute stats without this entry
        others = values[:i] + values[i + 1:]
        if len(others) < 2:
            is_outlier = False
        else:
            loo_mean = statistics.mean(others)
            loo_sd = statistics.stdev(others)
            threshold = loo_mean + threshold_sd * loo_sd
            # Require both: exceeds statistical threshold AND is at least
            # 3x the leave-one-out mean. This prevents false positives in
            # small samples where minor natural variation exceeds 2 SD.
            is_outlier = value > threshold and value > loo_mean * 3
        rows.append((name, value, is_outlier))
        if is_outlier:
            outliers.append((name, value))

    return (rows, overall_mean, overall_sd, outliers)


def print_category_table(category_name: str, metric_label: str, rows, mean: float, sd: float) -> None:
    """Print a markdown-style results table for one category."""
    print(f"\n## {category_name} ({metric_label})\n")
    print(f"| {'Name':<20} | {'Metric':>8} | {'Mean':>8} | {'SD':>8} | {'Flag':<7} |")
    print(f"|{'-' * 22}|{'-' * 10}|{'-' * 10}|{'-' * 10}|{'-' * 9}|")
    for name, value, is_outlier in rows:
        flag = "OUTLIER" if is_outlier else ""
        print(f"| {name:<20} | {value:>8.2f} | {mean:>8.2f} | {sd:>8.2f} | {flag:<7} |")


def check_balance(project_path: str, categories: list) -> int:
    """Run balance check across requested categories.

    Returns 0 if no outliers found, 1 if any outliers flagged.
    """
    data_dir = os.path.join(project_path, "data")
    found_outliers = False

    category_config = {
        "skills": {
            "file": "Skills.json",
            "metric_fn": skill_dpm,
            "label": "Damage per MP",
        },
        "weapons": {
            "file": "Weapons.json",
            "metric_fn": weapon_price_per_power,
            "label": "Price per Power",
        },
        "enemies": {
            "file": "Enemies.json",
            "metric_fn": enemy_hp_per_exp,
            "label": "HP per EXP",
        },
    }

    for category in categories:
        cfg = category_config[category]
        filepath = os.path.join(data_dir, cfg["file"])

        if not os.path.exists(filepath):
            print(f"Warning: {cfg['file']} not found at {filepath}, skipping {category}")
            continue

        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)

        # Skip null entries (index 0 and any tombstones)
        entries = [entry for entry in data if entry is not None]

        rows, mean, sd, outliers = flag_outliers(entries, cfg["metric_fn"])

        if not rows:
            print(f"\n## {category.title()} — fewer than 2 qualifying entries, skipped")
            continue

        print_category_table(category.title(), cfg["label"], rows, mean, sd)

        if outliers:
            found_outliers = True

    return 1 if found_outliers else 0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Check RPG Maker database balance via statistical outlier detection"
    )
    parser.add_argument(
        "--project", required=True,
        help="Path to RPG Maker project root directory"
    )
    parser.add_argument(
        "--category",
        choices=["skills", "weapons", "enemies", "all"],
        default="all",
        help="Category to check (default: all)",
    )
    args = parser.parse_args()

    if not os.path.isdir(args.project):
        print(f"Error: Project path does not exist: {args.project}", file=sys.stderr)
        sys.exit(1)

    categories = ["skills", "weapons", "enemies"] if args.category == "all" else [args.category]
    sys.exit(check_balance(args.project, categories))


if __name__ == "__main__":
    main()
