# A HARD_PASS ON THE GOAL-BEARING LINE IS INVISIBLE, WELL-EVIDENCED, AND ONE CONTROL SHORT

**2026-08-23, strategy session.** Found by auditing whether findings actually reach the plan --
`exp_stated_entity_fate_reading_extractor_v2_highprecision`.

---

## 1. THE VISIBILITY DEFECT, IN ONE LINE

| field, same `metrics.json` | value |
|---|---|
| `verdict` -- **what every tool and every scan reads** | `STRICT_READY_PENDING_HANDCHECK` |
| `final_verdict` -- **what the adjudicator wrote after doing the work** | **`HARD_PASS_CLEAN_GROW_BY_READING_VIABLE`** |

**The hand-check was done, scored against a pre-registered band, and passed. The top-level field was
never updated.** So the archive presents a passing result on the goal-bearing line as unfinished, and
anything counting `verdict` misses it.

*Seven cells carry both fields and all seven disagree. **In six the stale field is the pessimistic
one** -- four refine a `HARD_FAIL` into a more specific `HARD_FAIL`, two resolve `PENDING` to
`HARD_FAIL`. **This is the only one where the stale field HIDES a pass.***

---

## 2. AND THE WORK BEHIND IT IS UNUSUALLY CAREFUL FOR THIS ARCHIVE

I expected to find the label unearned. **I did not.**

- ✅ **A PRE-REGISTERED BAND, SET BEFORE:** `HARD_PASS_FILTERED_PRECISION: 0.85`. Result `0.90`.
  *A stated threshold beaten, not a threshold fitted to a result.*
- ✅ **`100` items hand-adjudicated, `90` correct**, with a full error taxonomy: ten distinct
  categories, **one instance each** -- no dominant failure mode hiding inside the 10%.
- ✅ **THE SAMPLE WAS DRAWN FRESH, WITH A SEED OFFSET, AFTER the filters were fixed** -- so it is not
  the sample the filters were tuned on.
- ✅ **THE RECALL COST IS REPORTED HONESTLY AND PROMINENTLY:** raw `4,015` -> strict `1,414`
  survivors, **survival `0.3522`**. *It buys precision by discarding two thirds of its own output and
  says so.*
- ✅ **A REAL v1 -> v2 COMPARISON:** raw real-prose precision `0.394` -> filtered `0.90`, via six
  named glass-box filters.
- ✅ Curated design `P=1.0/R=1.0`; held-out `P=1.0/R=0.8`; negation clean; ProPara dev-entity
  coverage by reading `129/175 = 0.7371`.

**By this archive's standards -- where 99.5% of HARD_PASS cells carry neither a CI nor a null -- this
is in the top fraction of a percent for care.**

---

## 3. WHAT IT IS STILL MISSING, AND IT IS EXACTLY ONE THING

🔻 **NO FLOOR ON THE PRECISION NUMBER. No null, no trivial baseline, on the population it scored.**

**That matters specifically because of how the survivors were produced.** Six filters removed two
thirds of the raw output. Filters that raise precision by discarding hard cases are doing something
real; filters that discard *everything except the easy cases* raise precision without adding
capability, and **`0.90` cannot distinguish those two without knowing what a trivial extractor scores
on the SAME 1,414 survivors.**

**THE MISSING ARM IS CHEAP AND OBVIOUS:** run the dumbest available extractor -- first noun after the
verb, or the most frequent patient type -- over the surviving population and report its precision
beside `0.90`. *If the trivial arm also reads `0.85`, the filters selected easy sentences. If it
reads `0.4`, the `0.90` is earned.*

⚠️ **AND THE COMPARISON THAT WOULD SETTLE IT IS PARTLY LOST.** `v1` saved all `4,015` of its outputs
(1.2 MB); `v2` saved only `37 KB` and **did not persist its `1,414` survivors**. So the
precision-versus-recall trade between the two versions cannot be re-analysed without a re-run --
*this project's "save the population you scored" rule, and the stronger result is the one that broke
it.*

---

## 4. WHAT I AM AND AM NOT SAYING

- ✅ **IS:** a carefully-run, pre-registered, hand-adjudicated result on the goal-bearing line that
  the archive presents as unfinished.
- ✅ **IS:** one specific, cheap control away from clearing the standing bar.
- 🚫 **IS NOT** a claim that reading-to-grow works. `0.90` precision on a set that survived six
  filters, with no floor, does not establish that.
- 🚫 **IS NOT** a criticism of the cell's authors. **They pre-registered, hand-checked, drew a fresh
  sample and reported their recall cost** -- the missing floor is a gap against a bar this project
  tightened later, not sloppiness.
- 🚫 **DO NOT QUOTE `0.90` as an extraction accuracy.** It is FILTERED precision on survivors, at a
  survival rate of `0.3522`.

---

## TLDR

Chasing a hunch about findings that never reach the main plan, I found an experiment that **passed and
is recorded as unfinished**. Someone did the review, wrote the passing verdict into the file, and
never changed the headline field — so every tool that scans results reads "awaiting review."

It matters because of what it is: evidence that the system can learn facts by reading real prose,
which is the central thing we are trying to build.

I expected, on opening it, to find the pass unearned. The opposite. They set the target *before*
running, checked a hundred results by hand, drew that sample fresh so it wasn't the one they tuned
on, and reported plainly that their precision came at the cost of throwing away two thirds of their
own output. That is more careful than almost anything else in the archive.

It is short exactly one thing: nobody checked what a stupid method would score on the same surviving
sentences. Since those sentences survived six filters, they might simply be the easy ones. One cheap
comparison would settle it, and until then the number can't be banked.

## QUESTIONS

None. `Q115` and `Q116` remain open.

## NEXT STEPS

1. **Run the trivial-extractor arm on the surviving population** -- it is the one control between
   this and a bankable result on the goal-bearing line.
2. **The survivors were not persisted**, so that arm needs a re-run rather than a re-score. Price it
   before starting.
3. The six other verdict/final_verdict disagreements are all conservative and need no action beyond
   tools reading the adjudicated field, which `tools/reproduce.py` now does.
