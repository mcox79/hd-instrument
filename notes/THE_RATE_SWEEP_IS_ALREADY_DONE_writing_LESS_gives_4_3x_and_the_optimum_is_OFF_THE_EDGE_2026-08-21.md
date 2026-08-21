# **THE WRITE-RATE SWEEP IS ALREADY DONE. WRITING *LESS* GIVES 4.3x -- AND THE SWEEP NEVER FOUND ITS PEAK.**

**One turn ago I proposed: "if write-rate is the real lever, sweep the rate with a random gate and
find where it peaks." That sweep is already inside
`exp_predictive_coding_write_gate_dissociation_v1`, as its threshold sweep. Here is what it says.**

---

## 1. THE FULL SWEEP -- FOUR THRESHOLDS, BOTH ARMS

| threshold | **P1** (prediction-gated) | **N1** (random, **same rate**) | P1 - N1 | band | P1 - A0 |
|---|---|---|---|---|---|
| 0.4039 | 0.0961 | 0.0971 | **-0.0010** | `NOT_SEPARATED` | +0.0251 |
| 0.4497 | 0.1526 | 0.1368 | +0.0157 | `NOT_SEPARATED` | +0.0816 |
| 0.4862 | 0.2268 | 0.2165 | +0.0103 | `NOT_SEPARATED` | +0.1558 |
| **0.5151** | **0.3079** | **0.3007** | +0.0071 | `NOT_SEPARATED` | **+0.2369** |

*(`A0_INCUMBENT` = 0.0710 throughout. The thresholds are percentiles of the surprise distribution:
0.4039 = p25, 0.4497 = p50, 0.4862 = p75, 0.5151 = **p90**.)*

## 2. 🎯 **THREE THINGS, AND ALL THREE ARE CLEAN**

**(a) PERFORMANCE RISES MONOTONICALLY AS YOU WRITE LESS.**
`0.0961 -> 0.1526 -> 0.2268 -> 0.3079`. **From 0.0710 to 0.3079 is a 4.3x gain over the incumbent,
and it requires no new mechanism at all -- only writing less.**

**(b) THE RANDOM GATE TRACKS IT IN LOCKSTEP.**
`0.0971 -> 0.1368 -> 0.2165 -> 0.3007`. **`NOT_SEPARATED` at every single threshold**, with the gap
*shrinking* as the rate tightens (+0.016 -> +0.010 -> +0.007). **Prediction error contributes nothing
distinguishable at any rate tested.**

**(c) `BEST_P1_THRESHOLD` = 0.5151 -- THE HIGHEST VALUE TESTED. THE SWEEP HIT THE EDGE OF ITS OWN
RANGE AND WAS STILL CLIMBING.** *The optimum is not in the data. Writing only the top 10% most
surprising items was the best point available, and there is no evidence it is the best point.*

## 3. ⚠️ **THE CEILING THAT MUST TRAVEL WITH THE 4.3x**

**EVERY ARM AT EVERY THRESHOLD REMAINS IN BAND `BELOW_0.5_COOCCURRENCE`.** *0.3079 is 4.3x the
incumbent and **still below the co-occurrence reference**. **The gain is real and the destination is
not yet parity.*** *Quoting "4.3x" without this would be the single most misleading number available
from tonight's work.*

## 4. WHAT IS ACTUALLY ACTIONABLE HERE

1. **THE LEVER IS RATE, AND IT IS UNTUNED.** The best tested point is the edge of the tested range.
   **Extending the sweep past p90 costs one parameter and no new mechanism.**
2. **THE SELECTION RULE IS FREE.** Since random matches prediction-error at every rate, **any cheap
   rule will do** -- which also means *no selection rule should be credited* until one separates from
   random at matched rate.
3. **THIS IS THE LARGEST SINGLE EFFECT I FOUND TONIGHT** and it belongs to the variable nobody was
   arguing about.

## TLDR

One turn ago I suggested testing whether the real benefit is simply **storing less**. **That test had
already been run inside the same experiment**, and the answer is unusually clear.

**As the system stores less and less, it gets steadily better** — from about 7% up to about 31%, a
**four-fold improvement**, achieved with no new machinery whatsoever. Just being more selective.

**But being *cleverly* selective adds nothing.** At every level of strictness tested, throwing away
the same proportion **at random** works just as well — and the gap between clever and random gets
*smaller* as you tighten, not larger.

**And the sweep never found its best point.** The strictest setting tested — keep only the 10% most
surprising — was the best one, and it was still improving when the experiment stopped looking.
**Extending that costs one number and no new ideas.**

**The essential caveat:** even at its best, this is **still below what plain word-counting achieves.**
A fourfold gain that doesn't reach parity is a real gain and not a solution — and quoting "four times
better" without that would be the most misleading thing I could take from tonight.

## QUESTIONS

None.

## NEXT STEPS

1. **Extend the threshold sweep past p90** -- the best point tested is the edge of the range and it
   was still climbing. *One parameter, no new mechanism.*
2. **Credit no selection rule** until one separates from a rate-matched random gate.
3. Report the `BELOW_0.5_COOCCURRENCE` band beside any rate result.
