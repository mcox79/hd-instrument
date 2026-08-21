# T4 -- **HOW MUCH OF THE ARCHIVE CAN BE RE-ANALYSED? BOUNDED BETWEEN 7% AND 96.5%, AND THE WIDTH OF THAT GAP IS THE FINDING.**

**Generalised from tonight's foraging dead end**, where the correct re-analysis became impossible
because the cell persisted **the score but not the scored population** -- 604 strings, a few
kilobytes, that would have made it a one-second recompute.
**The question: is that one careless cell, or is it how we build?**

---

## 1. TWO SCANS, DELIBERATELY BIASED IN OPPOSITE DIRECTIONS

*Running one and quoting it would have repeated tonight's own error -- accepting the first number
that answered the question.*

| scan | what it counts | bias | result |
|---|---|---|---|
| **A** | cells scoring a population with **no list of >=20 strings** anywhere in `metrics.json`, `units.jsonl` or sibling JSON | **OVER**-counts the defect (a cell may write items somewhere unscanned) | **3,547 of 3,676 = 96.5%** |
| **B** | of those, only ones whose metrics name a **run-GENERATED** population and **no fixed source** | **UNDER**-counts (a named gold file is credited as recoverable even if the scored set did not come from it) | **251 = 7.0%** |

**Denominator: 7,866 cell directories with a `metrics.json`; 3,676 score a population.**

## 2. 🚨 **THE HONEST BREAKDOWN -- AND THE BIGGEST CELL IS "CANNOT TELL"**

| | n | share |
|---|---|---|
| scored a **FIXED named set** -> **RECOVERABLE, not a defect** | 481 | 13.5% |
| scored a **RUN-GENERATED** population -> **GENUINELY LOST** | **251** | **7.0%** |
| mentions both -> ambiguous | 133 | 3.7% |
| **neither hint -> UNCLASSIFIED** | **2,702** | **75.7%** |

**➡️ THREE QUARTERS OF THE ARCHIVE CANNOT BE CLASSIFIED FROM ITS OWN METRICS.** *That is not a
limitation of the scan so much as a finding about the metrics: **a `metrics.json` that does not say
what population it scored cannot be audited for whether that population survived.***

**SO THE 96.5% HEADLINE IS WITHDRAWN BEFORE IT IS EVER QUOTED.** The defensible statement is:
**at least 251 cells have permanently lost their scored population; at most 3,547 have; and the
archive does not contain the information to narrow that further without reading cells one at a
time.** *Both bounds are reported because either alone is misleading -- which is the same discipline
that withdrew the foraging headline two hours ago.*

## 3. ⚠️ **61 OF THE GENUINELY-LOST ARE `HARD_PASS` -- AND ONE OF THEM IS LOAD-BEARING**

These are the ones most likely to be cited, and they are a concrete worklist rather than a
percentage:

> `exp_context_vector_signal_v1` · `exp_gap_driven_reader_controlled_v1` ·
> `exp_cls_read_sleep_foundation_acquire_v1` · `exp_graded_divisive_comparator_v1` ·
> `exp_grounded_inductive_concept_encoder_heldout_new_v3` ·
> `exp_grounding_gated_fusion_relation_inference_mammal_v1` ·
> `exp_foundation_validation_harness_v1` · `exp_grounded_meaning_wire_lexical_fallback_v1` ...

**🔴 `exp_context_vector_signal_v1` IS THE ONE THAT MATTERS.** `CLAUDE.md` records its figure --
*"the context vector is NOT noise -- REAL 0.7830 vs SCRAMBLE_SENT 0.9984"* -- as **"currently
load-bearing in the MEMORY.md banner"**, and separately records that **the agent who produced it hit
a denial, silently dropped the clean-slate precondition, and did not disclose it.**
**So a load-bearing number sits on a run whose precondition is known-compromised AND whose scored
population cannot be recovered to re-check it.** *Those two facts were recorded in different
documents on different days and have not previously been put side by side.*

## 4. THE FIX IS SMALL, AND IT BELONGS IN THE CELL

**Any cell that scores a population it GENERATED must dump that population.** Not a new framework --
one list, beside the score it already writes:

```python
"scored_population": sorted(banked_subjects),   # a few KB; makes every future re-score free
```

**The asymmetry is the whole argument:** a few kilobytes at write time versus **4,144 seconds x 5
arms** to recover it later -- and that is the cost only when you *can* re-run. *When the corpus,
seed or code has moved on, the number is simply unauditable forever.*

## 5. WHAT THIS SCAN IS NOT

**It is a prompt to go look, not a verdict on any cell.** It reads metrics only; it cannot see items
written to unscanned files, and it cannot tell a genuinely-lost population from a reconstructible one
in 75.7% of cases. **No cell should be called defective on the strength of this scan alone** -- the
61 named above are a reading list.

## TLDR

Tonight's dead end came from an experiment that saved **how well it scored** but not **what it
actually produced** — so when the test turned out to be unfair, there was nothing left to re-check.

I asked whether that's one sloppy experiment or how we build generally. **The answer is: we can't
tell, and that's the finding.**

Two counts, deliberately slanted opposite ways. The generous-to-the-critic count says **96.5%** of
scoring experiments saved no output. The generous-to-the-archive count says **7%** definitely lost
something irreplaceable. **The truth is somewhere between, and the reason the gap is so wide is that
three quarters of our experiments don't record what they were scoring in the first place** — so
there's no way to check whether it survived without opening them one by one.

I'm reporting both numbers rather than the dramatic one, because quoting the 96.5% would be exactly
the mistake I made twice already tonight.

**One concrete thing did fall out.** Sixty-one experiments that passed *and* lost their data are
named. One of them is the source of a number our own top-level notes call **load-bearing** — and the
same notes separately record that the run producing it **skipped a setup step and didn't say so**.
**So an important number rests on a run we already knew was compromised, and we can no longer check
it.** Those two facts were written down on different days in different files and had never been put
next to each other.

The fix is one line: save the list of things you scored. A few kilobytes now against an hour of
recomputation later — or, once the code moves on, against never being able to check at all.

## QUESTIONS

None.

## NEXT STEPS

1. **`exp_context_vector_signal_v1` deserves a decision** — it is load-bearing, its precondition is
   known-compromised, and it is now known to be unrecoverable. *A clean re-run is the only thing that
   settles it.*
2. Add the one-line population dump to the cell template before the next scoring cell is written.
3. The 61-cell list is a reading list, not a verdict.
