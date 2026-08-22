# **THE GROUNDING ANSWER, IN ONE PAIR OF NUMBERS: THE LOOP RELIABLY ACCUMULATES `3,359` NEW ENTRIES A CYCLE, AND A BLIND HAND-SCORE OF `100` OF THEM READS `3` MEANINGFUL / `19` RELATED / `78` NOISE.**

**Owner: "we did a fuckton of work on grounding. make sure you understand all of it." This is the
answer. Both halves are separately well-evidenced, and the archive kept them apart on purpose.**

---

## 1. ✅ WHAT IS SOLIDLY ESTABLISHED: THE MACHINERY RUNS

`exp_reading_grounding_loop_cycle2_v1`, HARD_PASS with CI + null + floor:

| gate | result |
|---|---|
| persistence round-trips | ✅ `persistence_ok=True` |
| foundation grows cumulatively | ✅ `185 -> 3,544`, **`3,359` new this cycle** |
| **responds to real text, not word soup** | ✅ **`scramble_ratio = 0.077`** -- *scrambled context grounds only 7.7% as much* |
| no leak / monotone / arms differ | ✅ all true |

**Its HARD_PASS gate is exactly `persistence_ok AND growth AND scramble_ratio < 0.5`.**

> ### 🔑 **AND THAT IS ALL IT CLAIMS. THERE IS NO CORRECTNESS MEASURE ANYWHERE IN THE CELL.** *Its verdict tag is literally `persistence_roundtrips_foundation_grows_cumulatively_scramble_discriminates` -- an honest name for exactly what was measured.*

## 2. ✅ AND THE QUALITY QUESTION WAS DELIBERATELY REFUSED, NOT FUDGED

`exp_grounding_quality_readout_v1` carries, in its own metrics:

> **`QUALITY_CLAIM: NONE -- this cell emits no quality tier.`** *"The primary discriminator is a BLIND
> HUMAN HAND-SCORE... the NULL outcome is pre-registered as LIVE and ACCEPTABLE."*

**A cell that refuses to score its own quality and routes it to a blind human is the archive at its
best.** *It is also why this cell is NOT a HARD_PASS -- it is `STRUCTURAL_PASS_PENDING_B3`, and I
briefly mis-listed it as a pass two days ago.*

## 3. 🔻 **THE BLIND HAND-SCORE, WHICH IS THE ACTUAL ANSWER**

*100 blind rows, scored and joined to their arms 10 minutes later (`B3_RESOLVED.md`):*

| | count | 95% CI |
|---|---|---|
| **MEANINGFUL** | 🔻 **3 / 100** | `[0.010, 0.085]` |
| RELATED | 19 / 100 | `[0.125, 0.278]` |
| 🔻 **NOISE** | **78 / 100** | `[0.689, 0.850]` |

**And the arm comparison: `BASE - F1F3 = -0.020`, CI `[-0.080, +0.040]`, NOT SEPARATED -- the read-out
fix did not move quality at all.**

> # **THE LOOP RELIABLY WRITES `3,359` THINGS PER CYCLE. ABOUT `3%` OF THEM MEAN ANYTHING, `78%` ARE NOISE, AND THE MECHANISM IMPROVEMENT THAT WAS SUPPOSED TO HELP DID NOT MOVE IT.**

## 4. ⚠️ TWO CITATION TRAPS IN THIS EXACT AREA, BOTH DOCUMENTED

1. **A `"32% vs 4% MEANINGFUL"` figure exists from an UNBLINDED re-score I did later** -- a duplicate of
   the blind one, whose **per-row labels were lost**. 🚫 **Use the BLIND `3/19/78`, not the unblinded
   32%.**
2. **`MEANINGFUL + RELATED` combined is `22/100`, CI `[0.150, 0.311]`.** *The archive warns specifically
   against quoting a combined MEANINGFUL-OR-RELATED figure as if it were MEANINGFUL.*

## 5. SO WHAT DOES THE GROUNDING WORK ACTUALLY ESTABLISH?

| claim | status |
|---|---|
| the loop persists, reloads and grows across processes | ✅ **solid** |
| it responds to real text structure rather than word soup | ✅ **solid** (`scramble_ratio 0.077`) |
| the comparator arithmetic can be improved | ✅ **solid** (`+0.0585`, and it is `sign()` removal, not divisive norm) |
| a plain capacity increase beats the mechanism change | ✅ **solid** (`+0.0985`) |
| 🔻 **what it grounds is MEANINGFUL** | 🔻 **`3%`, and the CI tops out at `8.5%`** |
| 🔻 **any mechanism change has improved quality** | 🔻 **not shown -- the one tested moved it `-0.020`, CI spanning zero** |

## TLDR

You asked me to understand all the grounding work. It comes down to two numbers that were measured
separately and honestly, and belong side by side.

**The machine works.** It reads, it writes down what it learns, it saves that to disk and picks it up
again next time, it grew from 185 entries to 3,544 in a single cycle, and — importantly — **if you
scramble the text into word soup it almost stops learning (down to 7.7%)**, which proves it is
responding to real structure rather than just hoovering up words.

**What it writes down is mostly wrong.** Someone scored 100 of its facts blind, without knowing which
was which: **3 were meaningful, 19 were vaguely related, 78 were noise.** And the one mechanism
improvement that was supposed to help quality **moved it by nothing** — the difference was slightly
negative with an error bar straddling zero.

**So: a reliable pipeline producing mostly noise.** That is a genuinely useful state to be in — it means
the plumbing is not the problem — but it should not be described as grounding working.

**The archive deserves credit here.** The experiment that could have quietly claimed quality explicitly
refused to: its own file says "this cell emits no quality tier", and it handed the question to a blind
human scorer with the null result pre-registered as an acceptable outcome. **That is why we know the 3%
rather than believing a 32%.**

## QUESTIONS

None — Q105 still open, independent of this.

## NEXT STEPS

1. **The grounding map is now answerable in one line** and I would put it in `STATUS.md`: *reliable
   accumulation, 3% meaningful, mechanism changes have not moved quality.*
2. **Two of four evidenced cells read** (`graded_divisive_comparator`, `reading_grounding_loop_cycle2`);
   the two `foundation_validation_harness` cells remain.
3. *Method note: **the most valuable thing in this area is a cell that refused to make a claim.**
   Without `QUALITY_CLAIM: NONE` and its blind sample, the growth number would be the only number, and
   "the foundation grew 19-fold" reads like success.*
