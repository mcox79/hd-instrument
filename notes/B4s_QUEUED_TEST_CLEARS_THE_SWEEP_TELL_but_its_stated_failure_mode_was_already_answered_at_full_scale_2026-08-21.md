# **B4's QUEUED TEST CLEARS THE NEW SWEEP TELL -- THE SCORE REALLY DOES MOVE. BUT ITS STATED FAILURE MODE WAS ALREADY ANSWERED, AND NOT AT "PROBE SCALE".**

**Third and last of tonight's queued-test checks. B1's was impossible; D3's swept a variable that
does not move. B4's is SOUND -- which matters, because a tell that flags everything is worthless.**

*All numbers read from `data/exp_capacity_ceiling_near_far_v1/metrics.json`, not from the map that
quotes them -- which is tonight's whole lesson.*

---

## 1. ✅ THE TELL IS CLEARED: THE SWEPT VARIABLE MOVES THE SCORE

| d | **256** | **1024** | **4096** | movement |
|---|---|---|---|---|
| **QUANT NEAR** | 0.6395 | 0.7030 | **0.7380** | **+0.0985** |
| **GRAD NEAR** | 0.6980 | 0.7495 | **0.78225** | **+0.0843** |
| floors (6 measured) | \multicolumn{3}{c}{0.4845 – 0.5095} | chance 0.50 |

**Monotone across the sweep, ~0.20-0.28 above floor, and the movement is ~9-21x the reported
between-draw sd.** *Unlike D3, this test would produce a readable answer.*

**AND THE MAP'S THREE QUOTED NUMBERS VERIFY EXACTLY** -- `0.6395` live-d256 baseline, `0.7030`
sign@1024, `0.78225` graded@4096 all appear in `curve_by_dimension`. **Good citation hygiene here,
unlike the B1 bullet.**

## 2. 🔴 **BUT ITS "HOW IT CAN FAIL" CLAUSE IS ALREADY ANSWERED**

**`ORGAN_MAP` STEP 2 states the failure mode as:** *"if the gain does not survive the full anchor
population (**2,377+ concepts vs the probe's 400**)"*, **and its honest caveat calls the existing
result *"at PROBE scale"*.**

> **THE CELL REPORTS `n_anchors = 2377`, `n_items = 4000`.**

***That is the map's own "full anchor population" number, exactly.*** **So the measurement it calls
probe-scale was run at the scale its failure clause asks about, and the gain DID survive.** *Either
the caveat is mislabelled or a separate 400-item probe exists -- but the three numbers the map
quotes all come from THIS cell, so the numbers being quoted are not probe-scale ones.*

## 3. ✅ **THE TEST IS STILL WARRANTED -- FOR A DIFFERENT REASON, AND THE CELL SAYS SO ITSELF**

> **`HP_SCOPE`: `{'d4096_GRAD': ['NEAR level', 'FAR-NEAR gap'], 'all_other_cells': 'reported, no
> verdict weight'}`**

**Only d=4096 GRAD was pre-registered for verdict. The d=1024 numbers -- the ones the queued test is
actually about -- are REPORTED WITHOUT VERDICT WEIGHT.** *So the honest restatement is:*

| the test's stated job | status |
|---|---|
| *"does the gain survive the full anchor population?"* | **ALREADY ANSWERED at n_anchors = 2,377** |
| *"is d=1024 verdict-weighted ON THE LIVE PATH?"* | **GENUINELY OPEN -- this is the real job** |

**`ORGAN_MAP` already says the right thing in its caveat -- *"This is a WIRE-IT test, not a
discovery. Do not report a re-measurement of a known effect as a new finding."* THAT INSTRUCTION IS
CORRECT AND SHOULD BE FOLLOWED LITERALLY.**

## 4. ⚠️ ONE FRAGILITY TO CARRY, FROM THE CELL'S OWN CONTROL

`projection_draw_control`: `gap_per_draw_d256` **GRAD = [0.047, 0.025, 0.03725]**, between-draw sd
**0.009001**. *The cell's own note: "the item bootstrap is blind to projection-draw variance; no
claim in this cell may rest on a difference [smaller than that]."*

> **THE *GAP* NUMBERS ARE FRAGILE -- one draw reads 0.025 against another's 0.047. THE *NEAR LEVEL*
> MOVEMENT (+0.084) IS NOT: it is an order of magnitude larger than the draw spread.** *Quote the
> level; treat the gap as draw-sensitive.*

## 5. 📊 SCORECARD FOR TONIGHT'S THREE CHECKS

| test | check | outcome |
|---|---|---|
| **B1** | does the population its can-fail condition needs EXIST? | 🚫 **NO -- OUT stratum empty. Withdrawn.** |
| **D3** | does the score MOVE across the swept range? | 🚫 **NO -- 1.0000 at every N; projection solves it.** |
| **B4** | both | ✅ **YES to both. Sound.** |

***The tell discriminates. That is the point of checking a third one.***

## TLDR

I checked the last of the three queued experiments, and this one is **fine** — which matters, because
a warning sign that fires on everything is useless.

Its plan is to raise a size setting and see if the system gets better at telling similar words apart.
**It does: roughly 0.64 → 0.74, well clear of the ~0.49 "no information" level.** So unlike the last
one I checked, this experiment would produce a real answer. And the three numbers our summary
document quotes for it **all check out exactly against the raw results** — good practice, and the
opposite of the case I retracted earlier tonight.

**One thing does need fixing.** The experiment says its risk is *"the improvement might vanish on the
full vocabulary rather than the small sample"* — and it names 2,377 words as the full set. **The
results file says it already ran on 2,377.** So that particular worry has been settled, and the
description calling it a small-sample result is wrong.

**The experiment is still worth running, for a different reason the results file states plainly:**
only the largest setting was formally registered as counting toward a verdict. The middle setting —
the one actually being proposed — was recorded but never counted. **So it's a confirm-and-commit
job, not a discovery**, which is exactly what our own notes already instruct.

**Score for the night: of three queued experiments, one couldn't run, one measured the wrong thing,
and one is sound.**

## QUESTIONS

None.

## NEXT STEPS

1. **B4's test needs re-scoping before authoring:** its job is *verdict weight for d=1024 on the live
   path*, **not** establishing that the gain survives scale -- that is done at n=2,377.
2. **Quote the NEAR LEVEL, not the FAR−NEAR gap** -- the gap moves 0.025→0.047 between projection
   draws, and the cell forbids resting a claim on a smaller difference.
3. **The sweep tell discriminates** (2 caught, 1 cleared), so it is worth keeping as a pre-authoring
   check rather than a one-off.
