# State Schema Reference

States are status effects like Poison, Stun, or custom buffs. Applied via skill
effects, item effects, or event commands. State 1 is always "Knockout" (death).

## Fields

| Field | Type | Default | Notes |
|-------|------|---------|-------|
| `id` | integer | — | Array index. **Never change.** |
| `name` | string | `""` | Display name (e.g., "Poison", "Sleep"). |
| `iconIndex` | integer | `0` | Icon shown in battle status. |
| `restriction` | integer | `0` | Behavior restriction (see table below). |
| `priority` | integer | `50` | Display priority in status icon list (higher = shown first). |
| `removeAtBattleEnd` | boolean | `false` | Whether state is removed when battle ends. |
| `removeByDamage` | boolean | `false` | Whether taking damage removes the state. |
| `autoRemovalTiming` | integer | `0` | 0=none, 1=at action end, 2=at turn end. |
| `minTurns` | integer | `1` | Minimum turns before auto-removal check. |
| `maxTurns` | integer | `1` | Maximum turns before auto-removal check. |
| `message1` | string | `""` | Message when state is added to actor (e.g., "was poisoned!"). |
| `message2` | string | `""` | Message when state is added to enemy. |
| `message3` | string | `""` | Message when state persists (e.g., "is hurt by poison!"). |
| `message4` | string | `""` | Message when state is removed. |
| `motion` | integer | `0` | SV battle motion index when affected (0=normal). |
| `overlay` | integer | `0` | SV battle overlay index when affected (0=none). |
| `traits` | array | `[]` | Trait objects (stat changes, element rates, etc.). |
| `note` | string | `""` | Plugin notetag field. **Never overwrite.** |

> **id field**: This is the array index. Changing it breaks skill/item effect
> references, trait conditions, and event state checks. State 1 is always
> "Knockout" — never reassign it.

> **note field**: Opaque string used by plugin ecosystems (Yanfly, VisuStella).
> Never parse, strip, or validate.

## Restriction Codes

| Code | Behavior |
|------|----------|
| 0 | None — battler acts normally. |
| 1 | Attack an enemy (forced basic attack). |
| 2 | Attack anyone (ally or enemy, random). |
| 3 | Attack an ally (confused). |
| 4 | Cannot act (stunned/paralyzed). |

## Auto-Removal Timing

| Code | When Checked |
|------|-------------|
| 0 | Never auto-removed (permanent until cured). |
| 1 | At end of each action (checked after the affected battler acts). |
| 2 | At end of each turn (checked at turn boundary). |

The state is removed when the turn counter reaches a random value between
`minTurns` and `maxTurns`. For example, `minTurns: 2, maxTurns: 4` means
the state lasts 2–4 turns before auto-removal.
