# Character Voice Consistency Workflow

When writing new dialog for an existing character, always establish their
voice before drafting a single new line. Agents that skip this step produce
tonally inconsistent dialog that developers must rewrite entirely.

The four-step workflow below guarantees that new lines match the character's
established voice, vocabulary, and speech patterns.

---

## Step 1: Extract Existing Lines

Run `extract_npc_lines.py` to pull all dialog attributed to the character
across the entire project (CommonEvents and all Map*.json files):

```bash
PYTHONPATH=. python skills/rpgmaker-dialog/scripts/extract_npc_lines.py \
  --project /path/to/your-project \
  --npc "CharacterName"
```

The script outputs one dialog line per line, prefixed with its source:

```
[CommonEvent:1] Welcome to the village inn!
[CommonEvent:1] Would you like to rest? It's 50 gold.
[Map001:Event1] Hello traveler! Welcome to our village.
[Map001:Event1] Be careful if you head to the cave.
```

**If the script is not yet available**, search manually:
1. Open `data/CommonEvents.json` — scan each event `list` for code 101
   entries where `parameters[0]` (faceName) and `parameters[1]` (faceIndex)
   match the character's face portrait. Collect all following code 401 lines.
2. Open each `data/Map*.json` — scan every event's page lists for the same
   code 101 pattern, or match events by their `name` field.

---

## Step 2: Analyze Voice Patterns

Review every extracted line and note the following:

| Dimension | Questions to Answer |
|-----------|---------------------|
| **Formality** | Casual ("Hey!") vs formal ("Greetings, traveler.") |
| **Vocabulary** | Simple everyday words vs elevated/technical language |
| **Sentence length** | Short punchy fragments vs long flowing sentences |
| **Verbal tics** | Recurring phrases ("I reckon…", "By the gods!", "Aye,") |
| **Emotional register** | Stoic and flat vs cheerful and expressive vs anxious |
| **Player address** | Uses `\N[1]` (player's name) vs a title vs no address |
| **Text codes used** | Which `\C[n]`, `\I[n]`, `\N[n]` codes the character already uses |

Write a two-sentence summary of the character's voice before drafting. For
example: *"The innkeeper speaks in short, direct sentences with a warm but
businesslike tone. He rarely uses the player's name, keeps word choices simple,
and occasionally uses folksy phrasing like 'rest your bones'."*

---

## Step 3: Draft New Lines

Write new dialog lines that match the patterns identified in Step 2:

- Mirror the formality level exactly
- Use words already in the character's vocabulary range
- Keep sentence length consistent with their established cadence
- Include any recurring verbal tics
- Use `\N[1]` or `\C[n]` only if the character's existing lines already do

**Mark all drafted lines as drafts.** Prefix your output with:
`# DRAFT — developer review required`

---

## Step 4: Validate References

After drafting, check that all text code references are valid:

```bash
PYTHONPATH=. python skills/rpgmaker-dialog/scripts/validate_dialog_refs.py \
  --project /path/to/your-project
```

The validator checks:
- `\N[id]` — actor ID must exist in `data/Actors.json`
- `\I[id]` — item ID must exist in `data/Items.json`

Fix any reported errors before presenting the draft to the developer.

---

## Examples

### Example 1: Gruff Innkeeper (short, direct, businesslike)

**Existing lines extracted from the fixture:**

```
[CommonEvent:1] Welcome to the village inn!
[CommonEvent:1] Would you like to rest? It's 50 gold.
[CommonEvent:1] Sweet dreams!
[CommonEvent:1] Come back anytime.
[Map001:Event1] Hello traveler! Welcome to our village.
[Map001:Event1] Be careful if you head to the cave.
```

**Voice analysis:** Short sentences. Warm but functional. No verbal tics.
No player name address. Exclamation on greetings, period on practical info.

**New line — bad (wrong voice):**
```
"Ah, \N[1], it warms my heart greatly to see you return to our humble
establishment this fine evening. Might I interest you in our finest room?"
```
Too long, too flowery, too formal — breaks the established voice.

**New line — good (matches voice):**
```
"Back again? Usual room's free. 50 gold."
```
Short. Direct. Business first. Matches the innkeeper's established cadence.

---

### Example 2: Scholarly Mage (formal, technical, philosophical)

**Hypothetical existing lines:**

```
"The arcane fluctuations in this region defy conventional explanation."
"I have dedicated thirty years to this research, \N[1]. Do not interrupt."
"Fascinating. The energy signature is unlike anything in the literature."
```

**Voice analysis:** Long sentences. Formal vocabulary (arcane, fluctuations,
conventional, literature). Uses player's name exactly once (dismissively).
Academic emotional register. No contractions.

**New line — bad (wrong voice):**
```
"Whoa, this magic stuff is really weird, huh?"
```

**New line — good (matches voice):**
```
"The convergence is accelerating beyond my initial projections. I require
your assistance, \N[1], though I confess the request is… distasteful."
```
Long sentence. Formal vocabulary. Uses `\N[1]` with the same slight
condescension. No contractions. Matches the scholarly register.

---

## Common Mistakes

- **Skipping Step 1 because the character "seems simple"** — even one-line
  NPCs have a voice. A terse guard with three existing lines still has a
  discernible register. Extract first.

- **Using `\N[1]` in a new line when the character never used it before** —
  If the existing lines don't address the player by name, don't start now
  without asking the developer first.

- **Forgetting that JSON stores `\\N[1]`** — In the JSON file, the backslash
  is escaped. `json.load()` gives you `\N[1]` in Python. Use that verbatim
  in any new dialog lines passed to `inject_dialog.py`.

- **Drafting in a vacuum** — Always show the existing lines alongside the
  draft so the developer can judge voice consistency directly.

---

*All drafted dialog is a suggestion for developer review, not a final decision.*
