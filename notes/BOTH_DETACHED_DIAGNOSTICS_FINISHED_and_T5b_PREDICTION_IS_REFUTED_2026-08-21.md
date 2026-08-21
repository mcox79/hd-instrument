# BOTH DETACHED DIAGNOSTICS FINISHED AND NEITHER HAD BEEN READ -- **AND THE ONE WITH A PREDICTION REFUTES IT**

**`STATUS.md` listed two detached diagnostics as `🟢 LIVE`. Both had completed. One landed a
`metrics.json` at 03:48Z that nobody opened.** *Tonight's recurring lesson, now applied to work this
same session launched.*

---

## 1. ⭐ **`exp_graded_vs_signed_query_v1` -- WHAT THE HARDCODED `np.sign` ACTUALLY COSTS**

**One variable: the QUERY. The anchor field is graded in BOTH arms.** `n_items = 4000`, all scored.

| arm | hit@1 (opt = pess) | median rank |
|---|---|---|
| **`Q_GRADED`** (magnitude restored) | **0.0480** | **37.0** |
| `Q_SIGNED` (`reading_grounding_loop.py:776`) | 0.0455 | 41.0 |

**PAIRED: `GRADED - SIGNED = +0.0025`, CI95 `[-0.0030, +0.0080]` -- NOT SEPARATED.**

### 🔴 **THE PREDICTION UNDER TEST IS REFUTED, AND THE CELL NAMES IT IN A FIELD**

> `prediction_under_test`: *"restoring magnitude moves hit@1 **specifically** and leaves median rank
> **roughly alone** (T5b)"*

**IT DID THE OPPOSITE.** *hit@1 did **not** separate (+0.0025, CI crosses zero). **Median rank moved 4
places** (41.0 -> 37.0).* **The effect landed exactly where the prediction said it would not.**

### ✅ AND IT IS A REAL NULL, NOT A REACHABILITY FAILURE

| check | value |
|---|---|
| **positive control** | `Q_GRADED` hit@1 **0.0480 = the landed C3 headline 0.0480** -> `positive_control_reproduces_c3_headline: True` |
| **picks changed** | **1,774 of 4,000** |
| **ranks changed** | **3,708 of 4,000** |

*The cell refused to report unless the positive control reproduced, and it did, exactly. **The
intervention demonstrably reached the scorer on 93% of items.** So `+0.0025` is a measured null.*

### ➡️ **PRACTICAL CONSEQUENCE**

**THE HARDCODED `np.sign` IN THE QUERY COSTS ALMOST NOTHING** -- a non-significant `+0.0025` hit@1 and
4 median ranks. **`:663`'s comment that the graded-field/signed-query pairing is *"worse than either"*
is not supported at the scale this measures.** *Fixing `:776` is **not** the lever, and that question
can be closed.*

## 2. `tools/diagnose_read_with_loaded_foundation.py` -- COMPLETED, AND THE GUARD DID ITS JOB

| arm | sentences read | anchors | `n_grounded` | refusals THIS read | foundation already carried |
|---|---|---|---|---|---|
| `v1` | **1,060** (requested 1,200) | 4,322 -> 4,390 | **0** | 279 | **0** |
| `v2_qualityfix` | **1,060** | 1,415 -> 1,461 | **0** | 380 | **11,122** |

**The corpus exhausted mid-read on BOTH arms -- the guard printed it rather than silently reporting a
zero.** *That is the whole reason this re-run existed.*

**⚠️ AND `n_grounded` IS STILL 0 ON A READ THAT PROCESSED 1,060 SENTENCES WHILE ANCHORS GREW BY 68.**
*Anchors growing while `n_grounded` stays exactly zero means **the field is not being populated on
this path**, not that nothing was learned. **It remains a reachability failure and must not be quoted
as a null.*** *The clean number from this run is the refusal delta -- **279 vs 380** -- which is 1.36x,
not the 22x headline that was 93% pre-existing.*

## TLDR

Two background diagnostics this session started had **both finished, and neither had been looked at.**
One had written its results to disk at 3:48 in the morning.

**The useful one tested whether a shortcut in the code is costing us anything.** There's a line that
throws away the strength of a signal and keeps only its direction. The prediction was that fixing it
would improve the system's top answer specifically.

**It did the opposite.** The top-answer accuracy barely moved and the change isn't distinguishable
from nothing. What *did* improve was the overall ranking quality — the exact thing the prediction said
would stay put.

**And it's a trustworthy result**, because the experiment refused to report at all unless it could
first reproduce a previously published number exactly — which it did — and it confirmed the change
actually affected 93% of the items it scored. So this is a real "no difference", not a broken test.

**Practical upshot: that shortcut is not worth fixing.** It costs almost nothing. A comment in the
code calling the combination "worse than either" isn't supported at this scale.

**The second diagnostic** confirmed a probe bug I'd found earlier — the text ran out mid-run, and this
version says so out loud instead of quietly reporting a zero. **But one number in it is still broken:**
it claims nothing was learned while simultaneously showing the vocabulary grew by 68 entries. **That
field isn't being filled in, so it can't be read as a result.**

## QUESTIONS

None.

## NEXT STEPS

1. **Close the `np.sign` question** -- measured, null, positive-controlled. *Remove it from the
   open-items list rather than leaving it as "under test".*
2. **`n_grounded` not populating on the loaded-foundation path is a real instrumentation bug** and is
   worth one look, since it silently produces a zero that reads like a null.
3. `STATUS.md`'s `WHAT IS RUNNING` should stop calling these live.
