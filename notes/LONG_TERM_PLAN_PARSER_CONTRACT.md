# PARSER CONTRACT for `notes/LONG_TERM_PLAN.md` (and `notes/PLAN.md` section 9)

**This file is the DOC-SIDE record of a code coupling.** `CLAUDE.md`, *"A doc parsed by code is
coupled to it"*: when code parses a human-edited document, the literal it matches is an API, and it
must be marked in **both** files so the coupling is visible from whichever one a future agent opens.

**Why it is a separate file rather than a line inside the plan.** `notes/LONG_TERM_PLAN.md` is
Director-owned and on the do-not-touch list for everyone else. The agent that wrote the parser could
not add the pointer. So the contract is recorded here, and **the code reports that the doc side is
incomplete**: `tools/status_plan.py::contract()` returns `doc_side_note` saying the coupling is
recorded on one side only. See THE ONE LINE THE DIRECTOR SHOULD ADD, at the bottom.

**The incident this exists to prevent.** On 2026-08-13 `notes/STATUS.md` was reworded from
`AS OF:` to `AS OF` and from `## WHAT IS RUNNING` to `## RUNNING / BLOCKED`.
`tools/session_start_hook.py` did not error. It injected `(no AS OF line found)` into **every
compaction recovery** for days, and the placeholder read like ordinary output, so nobody saw it.
That is the exact failure class the hook existed to prevent, happening inside the hook.

---

## 1. WHO PARSES WHAT

| file | parsed by | what it reads |
|---|---|---|
| `notes/LONG_TERM_PLAN.md` | `tools/status_plan.py` `parse_phases()` | section 5, every phase |
| `notes/PLAN.md` | `tools/status_plan.py` `parse_decisions()` | section 9, every `**Dn - ...**` |
| `notes/STATUS.md`, `notes/STATUS_LESSONS.md`, `notes/STATUS_SPEC.md` | `tools/status_plan.py` `load_operator_decisions()` | drift check only -- the literals quoted in `notes/operator_decisions.json` must still be findable |

`tools/status_plan.py` is read-only. It never writes to any of these files.

---

## 2. THE LITERALS THAT ARE AN API

Renaming any of these changes behaviour. Change `tools/status_plan.py` in the same edit.

**In `notes/LONG_TERM_PLAN.md`:**

- the section headings `## 5. THE PLAN` and `## 7. HOW WE WILL KNOW IT IS WORKING`
  (matched by prefix, so the rest of each heading may be reworded freely)
- the phase heading shape `### PHASE <n> - <TITLE> *(<note>)*`
  — the `*( ... )*` note is optional; the `PHASE <n>` prefix is not
- the labelled lines `**Gate:**` and `**Kill condition:**` — **REQUIRED**; a phase without one
  renders that cell as `NOT STATED IN THE PLAN` and counts as a contract violation on screen
- the labelled lines `**Status:**`, `**Goal:**`, `**Brain structure:**`, `**The work:**`,
  `**Where it stands:**`, `**The problem in one line:**` — optional, each improves one cell
- `~~strikethrough~~` inside `**The work:**` means RETRACTED. The parser skips struck-through items
  when it picks THE SINGLE NEXT ACTION. This matters today: PHASE 1's third work item is retracted,
  and showing it as the next thing to do would send the reader at a withdrawn instruction.

**In `notes/PLAN.md`:**

- the section heading `## 9. DECISIONS FOR THE OWNER`
- the decision heading shape `**D<n> - <question>?**`
- the labelled line `**Recommended default: ...**`

Editing the PROSE inside any of these is always safe and is the intended use. Only the LABELS and
the HEADING SHAPES are load-bearing.

---

## 3. WHAT THE PARSER DOES WHEN A LITERAL IS GONE

It says so, loudly, on screen, and counts it. It never substitutes a plausible value and it never
falls back to a remembered one.

| situation | what the window shows |
|---|---|
| the file is unreadable | the whole panel says `MISSING`, with the path |
| a section heading was renamed | `SECTION_HEADING_GONE`, naming the literal it looked for |
| section 5 parsed but yielded no phases | `NO_PHASES_PARSED`, naming the heading shape |
| a phase has no `**Gate:**` | that cell reads `NOT STATED IN THE PLAN`; `PHASE_LABEL_MISSING` counted |
| a phase states no status | `NOT STATED`; `PHASE_STATUS_NOT_STATED` counted |
| a transcribed number is no longer in its source | `TRANSCRIBED_NUMBER_GONE`, naming the string |

The count of all of these is rendered in the window's top strip beside the other drift counters, so
a silent divergence becomes a visible one. That is the whole point of the mechanism.

---

## 4. THE THREE GAPS IN THE PLAN AS IT STANDS (2026-08-16)

Reported by the parser on every refresh, **not** filled in by it:

1. **PHASE 0 has no `**Gate:**` line.** It has `**Remaining, and it blocks Phase 3:**` instead.
   Its `**Kill condition:**` is present and says `none. This phase is permanent overhead, not a bet.`
2. **PHASE 5 has neither `**Gate:**` nor `**Kill condition:**`.** It is the long-horizon phase and
   may genuinely not have them yet — in which case the honest fix is a line saying so, not silence.
3. **No phase carries a machine-readable status.** Five of the six can be inferred from the heading
   note (`blocked until Phase 1 clears`, `the current bottleneck; start here`, and so on). **PHASE 2
   cannot** — its note reads `the central scientific bet`, which says what it is and not where it
   is. Today PHASE 2 renders as `NOT STATED`.

---

## 5. THE MINIMAL CONVENTION PROPOSED — AND THE ONE LINE THE DIRECTOR SHOULD ADD

Two optional labelled lines under each phase heading, in the shape the document already uses. The
parser prefers them when present and works without them today, so adopting this is not a migration.

```
### PHASE <n> — <TITLE> *(<free text, as now>)*

**Status:** IN PROGRESS
**Goal:** one plain sentence saying what this phase is for.
**Brain structure:** ... (as now)
**The work:** ... (as now)
**Gate:** ... (as now — REQUIRED)
**Kill condition:** ... (as now — REQUIRED)
```

`**Status:**` takes exactly one of `DONE` / `IN PROGRESS` / `BLOCKED` / `NOT STARTED`, and it WINS
over anything inferred from the heading note. `**Goal:**` wins over
`**The problem in one line:**`, which wins over the first paragraph.

**And the line the Director should add to `notes/LONG_TERM_PLAN.md`, so the coupling is recorded on
both sides as the rule requires** — anywhere near the top of section 5:

> *Section 5 is machine-parsed by `tools/status_plan.py` and rendered live in the status window.
> The phase heading shape and the `**Gate:**` / `**Kill condition:**` labels are an API — see
> `notes/LONG_TERM_PLAN_PARSER_CONTRACT.md` before rewording them.*

Until that line exists, `contract()['doc_side_note']` reports the coupling as recorded on one side
only, and the status window says so.
