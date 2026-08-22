# THE REPRODUCIBILITY HOLE IS GROWING, AND THE CHEAP FIX FOR IT IS REFUTED

**2026-08-22, strategy session.** Follow-up to landing SH-7 (`HDI_FRESH_RUN`) and
`tools/reproduce.py`. Three measurements, in the order that makes the last one matter.

---

## 1. THE HEADLINE

**The share of new experiment cells that route output through the harness function has fallen from
`90.8%` in June to `27.2%` in August.** SH-7 can only redirect cells that use that function, so
**its coverage does not improve on its own -- it SHRINKS.** Migrating the 275 legacy cells while new
ones keep arriving bare is bailing water.

**AND THE ONE-HOOK SHORTCUT THAT WOULD AVOID THAT MIGRATION IS REFUTED BY MEASUREMENT**, not by
argument: only `5%` of bare cells write `metrics.json` through a shared helper.

---

## 2. ADOPTION IS FALLING, AND IT IS NOT A FILE-GENERATION ARTIFACT

Every file in `experiments/`, first-add commit from one `git log` pass, bucketed by month:

| month | cells added | routed through `get_output_dir` |
|---|---|---|
| 2026-05 | 937 | **78.1%** |
| 2026-06 | 2,869 | **90.8%** |
| 2026-07 | 1,132 | **47.3%** |
| 2026-08 | 707 | **27.2%** |

*(PRIMARY cells only -- `exp_*` without a `_smoke` / `_REDUCED` / `_selftest` suffix.)*

**THE OBVIOUS CONFOUND IS RULED OUT.** With 5,897 sources for ~7,875 landed cells, a burst of
generated siblings in August would produce this shape without any change in practice. It is not
that: **variant-suffix files are `n<=2` per month**, and non-cell scripts are a small, flat
population (`4.5%`-`13.9%` routed throughout). **The decline is in primary cells, at n=707-2,869 per
month.**

⚠️ **STATED LIMIT: this is a source grep for the literal `get_output_dir`.** An aliased import or an
unusual construction would be miscounted. It is not a claim that any specific cell is broken -- it
is a claim about a rate, and the rate moved by `63` points.

🔻 **AND A SECOND MEASUREMENT ON THIS DID NOT SURVIVE ITS OWN MAPPING, SO IT IS NOT QUOTED HERE:**
restricting the trend to the 421 cells that actually checkpoint mapped only `231` of them to a dated
source (`45%` unmapped) and produced a two-month table pointing the OTHER way. **A table built on
55% coverage is not evidence** and I am not reporting a trend from it.

---

## 3. THE PRIOR NIGHT'S SAMPLE WAS RIGHT, AND WEAKER THAN THE TRUTH

A 25-per-class sample the same evening read bare cells as NEWER -- median first-commit `2026-07-02`
against `2026-06-01` -- and was recorded as **a direction, not a verdict**, on the grounds of small
n, wide ranges, and rename-unreliable dates.

**The powered version confirms it and is much stronger than two medians suggested.** *Worth noting
which way this went: the underpowered read was directionally correct. That is not a reason to trust
underpowered reads -- it is a reason to run the powered one, which cost about four minutes.*

---

## 4. THE ONE-HOOK SHORTCUT: REFUTED, RECORDED SO IT IS NOT RE-PROPOSED

The `harness_cannot_recompute` submission rejected an alternative, verbatim:

> *"an env-var in `tools/exp_checkpoint.py` that makes `completed_units()` return empty and redirects
> `record_unit()` would force a recompute for all 400 without per-cell edits -- BUT it does not
> redirect `metrics.json` (each cell writes that to its own `OUTPUT_DIR`), so a bare cell would
> overwrite its landed `metrics.json`. That breaks the byte-identity guarantee."*

**That objection is right ONLY IF cells write `metrics.json` themselves.** If most wrote it through
a shared helper taking the output dir as an argument, redirecting inside that helper would carry
`metrics.json` too, the objection would dissolve, and 275 file edits would collapse into one hook.
**Nobody had measured which it was, so I did rather than accepting the reasoning.**

| how a bare primary cell emits `metrics.json` | n |
|---|---|
| via `write_metrics()` only | 4 |
| `write_metrics()` **and** raw `json.dump` | 81 |
| 🔻 **raw `json.dump` only** | **849** |
| no `metrics.json` at all | 650 |

**A redirect inside `write_metrics` would carry `85` of `1,584` bare cells -- `5%`. THE OBJECTION
HOLDS.** *For contrast, the units side is genuinely shared: `208` bare cells call `record_unit` and
`239` call `completed_units` -- which is exactly why a units-only redirect is the tempting and wrong
fix. It would force a recompute and let the landed `metrics.json` be overwritten.*

🚫 **DO NOT RE-PROPOSE "just hook `exp_checkpoint` and skip the migration."** It is measured at 5%.

---

## 5. WHAT THIS CHANGES

**THE LEVERAGE IS NOT IN THE 275 LEGACY CELLS. IT IS AT AUTHORING TIME.** The legacy migration is a
fixed, priced, one-line-each chore. The trend is the part that compounds: at `27.2%` and falling,
most cells written from here will be un-reproducible by construction, and each one adds to the pile
faster than the pile can be cleared.

**NOT DONE, AND NOT MINE TO DECIDE ALONE:** whether new cells should be *required* to route through
the harness function. That is a convention change affecting every author, and this note is the
evidence for it rather than the decision.

**WHAT EXISTS TODAY:** `python tools/reproduce.py <cell> --check` answers the question per cell and
prints the one-line migration. Nothing yet catches a NEW cell being written bare -- **that is the
gap this measurement identifies, and it is where a guard would earn the most.**

---

## TLDR

We can now force a finished experiment to genuinely redo itself, but only for experiments that use
a particular shared helper. **The share of new experiments using that helper has dropped from about
nine in ten to under three in ten since June** -- so the fix reaches fewer experiments over time, not
more, and fixing the old ones while new ones keep arriving broken does not close the gap.

There was an appealing shortcut: patch one shared function and cover everything at once, no
per-file edits. **I checked instead of assuming, and it does not work** -- fewer than one in twenty
experiments saves its results through a shared function; the rest write the file themselves. Patching
the shared one would reach 5% while creating a real risk of overwriting original results in the rest.

So the useful move is not cleaning up the backlog. It is stopping new experiments from joining it.

## QUESTIONS

None. *(The one decision worth an owner's time -- whether to require the shared helper in new cells
-- is a convention change; this note is the evidence, and I would rather file it as a board question
with a working guard beside it than as an abstract ask.)*

## NEXT STEPS

1. **A guard that catches a new cell written bare** is where the leverage is, and nothing does it today.
2. The 275-cell migration is a priced chore, not an emergency: `--check` names them one at a time.
3. Do not re-propose the `exp_checkpoint` one-hook shortcut; it is measured at 5% and recorded above.
