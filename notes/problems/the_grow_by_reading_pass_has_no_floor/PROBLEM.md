---
priority: 3
review:
review_text:
---

# PROBLEM: OUR BEST EVIDENCE THAT THE SYSTEM CAN LEARN BY READING HAS NO FLOOR UNDER IT

**slug:** `the_grow_by_reading_pass_has_no_floor` - **opened:** 2026-08-23 by the strategy session
**status:** OPEN - **one missing control stands between a careful result and a bankable one**

> **RANKED 3.** It decides whether a claimed pass on the central capability is real. Cheaper than
> most of the list and more consequential than anything below it - but it needs a re-run rather than
> a re-score (§6), which is why it is not 2. *Everything from the old 3 down moved one step.*

> **If a tool call is denied, STOP and report the exact denial text verbatim. Do not retry a variant,
> and do not silently proceed without the denied step.**

---

## 1. THE PROBLEM IN PLAIN LANGUAGE

We have an experiment that reads ordinary prose and pulls out what happened to things - which
substance got dissolved, which object got moved. **It reports getting 90 out of 100 right**, and it
is one of the most carefully run things in the archive.

**Nobody checked what a stupid method scores on the same sentences.**

That matters more than usual here, because the 90% is measured only on sentences that survived **six
filters that threw away two thirds of the original output**. Filters that discard the *hard*
sentences and keep the easy ones raise the score without the system getting any better at anything.

**So the number could mean "this reads well" or it could mean "we kept only the easy sentences", and
as it stands there is no way to tell.**

## 2. WHY THIS ONE

- 🔑 **IT IS ONE CONTROL, NOT A BUILD.** Everything else about this result is already done and done
  well (§4). This is the single missing arm.
- **It is on the goal-bearing line.** *Can the system grow its knowledge by reading real prose* is the
  central question, and this is our best current evidence for a yes. **Leaving it unfalsifiable is
  worse than a clean negative.**
- **A null here is as useful as a pass.** If a trivial extractor also scores ~0.85 on the survivors,
  we learn that the filters -- not the reading -- produced the number, which redirects real effort.

## 3. MEASURED vs INFERRED

**MEASURED**, all from `data/exp_stated_entity_fate_reading_extractor_v2_highprecision/metrics.json`,
read on disk 2026-08-23:

| | |
|---|---|
| hand-adjudicated | `100` items, `90` correct, **filtered precision `0.90`** |
| pre-registered band | `HARD_PASS_FILTERED_PRECISION: 0.85` -- set BEFORE the run |
| survival | raw `4,015` -> strict `1,414`, **`0.3522`** |
| v1 -> v2 real-prose precision | `0.394` -> `0.90` (six glass-box filters) |
| curated / held-out | `P=1.0/R=1.0` and `P=1.0/R=0.8`; negation clean |
| ProPara dev-entity coverage by reading | `129/175 = 0.7371` |
| 🔻 **floor / trivial / baseline arm** | **ABSENT** -- none of the four `stated_entity_fate` cells contains the string `floor`, `trivial`, `naive` or `baseline` |

**INFERRED, NOT MEASURED:**

- 🔻 **That the filters are selecting EASY sentences rather than discarding hard ones.** Plausible
  given a `0.3522` survival rate, and **completely untested** -- that is the whole point of this
  brief, not a finding it asserts.
- 🔻 **That a trivial extractor would score lower.** Nobody has run one. **It might score `0.85`.**

## 4. ALREADY TRIED - DO NOT REDO ANY OF IT

*Read this before assuming the cell was sloppy. It was not.*

*Read this section before assuming the cell was sloppy. It was not.*

- ✅ **PRE-REGISTERED BAND, SET BEFORE THE RUN:** `HARD_PASS_FILTERED_PRECISION: 0.85`. Result `0.90`.
- ✅ **`100` items HAND-ADJUDICATED, `90` correct**, with a full error taxonomy: **ten categories, one
  instance each** -- no dominant failure hiding in the 10%.
- ✅ **THE SAMPLE WAS DRAWN FRESH (seed offset) AFTER the filters were fixed** -- not the sample they
  were tuned on.
- ✅ **RECALL COST DISCLOSED PROMINENTLY:** raw `4,015` -> strict `1,414` survivors, survival
  `0.3522`.
- ✅ **REAL v1 -> v2 COMPARISON:** raw real-prose precision `0.394` -> filtered `0.90`, six named
  glass-box filters.
- ✅ Curated design `P=1.0/R=1.0`; held-out `P=1.0/R=0.8`; negation clean; ProPara dev-entity coverage
  by reading `129/175 = 0.7371`.

**MEASURED 2026-08-23:** none of the four `stated_entity_fate` cells contains the string `floor`,
`trivial`, `naive` or `baseline`. **The arm has never been run.**

## 5. VERIFY BEFORE YOU START

1. **Read `data/exp_stated_entity_fate_reading_extractor_v2_highprecision/metrics.json` yourself** --
   `bands`, `hand_check`, `final_verdict_msg`. *Notes here go stale within hours.*
2. `python tools/before_you_start.py "trivial extractor floor for entity fate precision"` and read
   **every** row. *`"floor"` alone returns 214 cells.*
3. ⚠️ **A NOTE ON THIS CELL'S VERDICT FIELD, so it does not derail you:** the top-level `verdict`
   reads `STRICT_READY_PENDING_HANDCHECK` while `final_verdict` in the same file reads
   `HARD_PASS_CLEAN_GROW_BY_READING_VIABLE`. **`final_verdict` is the adjudicated one.**
   `experiment_index.py` already resolves this correctly and shows `HARD_PASS`; the raw field is what
   is stale.

## 6. THE COMPLICATION - PRICE IT BEFORE YOU START

🔻 **THE SURVIVORS WERE NOT PERSISTED.** `v2` saved `37 KB`; `v1` saved all `4,015` outputs in
`1.2 MB`. **So the `1,414` survivors this needs to score are gone, and the arm needs a RE-RUN of the
extractor rather than a re-score of a saved file.**

*This is the project's own "save the population you scored" rule, broken by the stronger of the two
versions -- and it is why this is ranked 3 and not 2.* **Price the re-run before starting; if it is
expensive, say so and stop rather than half-running it.**

## 7. THE BAR

**THE TRIVIAL ARM AND THE REAL ARM SCORED ON THE SAME SURVIVING SENTENCES, PRECISION REPORTED SIDE
BY SIDE, WITH A CI ON THE DIFFERENCE.**

- **THE TRIVIAL ARM MUST BE GENUINELY TRIVIAL** and named in advance: first noun after the verb, or
  the most frequent patient type, or the syntactic object with no filtering. **Not a weakened version
  of the real extractor** -- that measures the filters twice.
- 🚨 **SCORE IT ON THE SURVIVORS, NOT ON THE RAW SET.** Scoring the trivial arm on all `4,015` while
  the real arm scores on `1,414` is two populations and answers nothing. *That error was made
  elsewhere in this project this week.*
- **HAND-ADJUDICATE THE TRIVIAL ARM THE SAME WAY**, same `n`, same adjudication protocol, ideally the
  same items. A precision comparison where one side was hand-checked and the other was auto-scored is
  not a comparison.
- **REPORT BOTH, WHATEVER HAPPENS.** If the trivial arm reads `~0.85`, say so plainly -- that is the
  informative outcome and it redirects effort away from filter engineering.
- **DO NOT ADJUST THE `0.85` BAND.** It was pre-registered and beaten; the question is what it should
  be measured *against*, not where it sits.

## 8. FILES AND ENTRY POINTS

| what | where |
|---|---|
| the result | `data/exp_stated_entity_fate_reading_extractor_v2_highprecision/metrics.json` |
| the cell | `experiments/exp_stated_entity_fate_reading_extractor_v2_highprecision.py` |
| the predecessor, which DID save its population | `data/exp_stated_entity_fate_reading_extractor_v1/` (1.2 MB, 4,015 rows) |
| the adjudicated hand-check | `hand_check.adjudication_path` inside the metrics |
| the write-up | `notes/A_HARD_PASS_ON_GROW_BY_READING_IS_INVISIBLE_AND_ONE_CONTROL_SHORT_2026-08-23.md` |

## 9. DO NOT QUOTE

- 🚫 **`0.90` as an extraction accuracy.** It is FILTERED precision on survivors at a survival rate of
  `0.3522`.
- 🚫 **`0.394 -> 0.90` as a sixfold improvement in reading.** Those are different populations - raw
  versus filtered - and the whole question is whether the filtering explains the gap.
- 🚫 **"grow by reading is viable"** on the strength of this cell alone. That is the verdict string,
  not an established finding, and this brief exists because the control that would establish it is
  missing.

## 10. WHAT THE BRAIN SAYS, AND WHERE WE ARE INVENTING

**Learning what happened to a thing from a sentence describing it is close to what the brain does
when it reads** - building a situation model rather than storing the sentence. That framing is
PINNED by the project's plan, not invented here.

**OURS-UNDER-TEST:** that six hand-written syntactic filters are a reasonable way to get there.
**Nothing pins that**, and a trivial arm scoring near `0.85` would say the filters are doing
selection rather than comprehension - **which is exactly the distinction this project keeps having to
make** (a similarity proxy where reasoning was claimed).
