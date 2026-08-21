# **I GUESSED THE COSINE SATURATION WAS ONE DOMINANT SHARED AXIS. IT IS NOT: PC1 IS `27.5%`, ITS LOADINGS ARE SPREAD, AND REMOVING IT MOVES THE UNRELATED 95th PERCENTILE FROM `0.912` TO `0.890`. THE MODULE'S OWN EXPLANATION STANDS AND MINE DOES NOT.**

**Human-rated-unrelated word pairs score `0.912` cosine on our 12 grounded dimensions. I proposed a
mechanism for that. The measurement refuses it.**

---

## 1. THE HYPOTHESIS, AND WHERE I GOT IT

*`grounded_similarity.py` mentions "a dominant shared concreteness axis".* **I read that as the
mechanical cause -- one axis eating the variance, so every vector points roughly the same way and
cosine compresses into a narrow high band.** *If true, removing it is a standard, cheap fix.*

## 2. 🔻 THE MEASUREMENT, ON 1,028 WORDS

| | |
|---|---|
| explained variance, components 1-5 | **0.275**, 0.218, 0.159, 0.088, 0.055 |
| **PC1 alone** | **27.5%** -- *not a dominating axis; the variance is spread* |
| PC1 loadings across the 12 dims | `0.19 0.50 0.40 0.08 0.51 0.23 0.10 0.25 0.15 0.12 0.15 0.32` |

***PC1 PEAKS AT `0.51` ON A SENSORIMOTOR DIMENSION. CONCRETENESS (dim 12) LOADS `0.32`. SO PC1 IS NOT
"THE CONCRETENESS AXIS".***

## 3. AND REMOVING IT BARELY HELPS

| representation | SYN | REL | UNREL | **UNREL p95** | no-false-merge bar admits |
|---|---|---|---|---|---|
| **RAW (what ships)** | 0.627 | 0.551 | 0.360 | **0.912** | **0 of 120** |
| mean-centred | 0.627 | 0.501 | 0.314 | 0.902 | 0 of 120 |
| **mean-centred, PC1 removed** | 0.600 | 0.457 | 0.282 | **0.890** | **4 of 120** |

> ### **`0.912 -> 0.890`. The strata separate a little better, and the guarantee test goes from admitting NOTHING to admitting 4 of 120. NEITHER IS A FIX, AND THE SATURATION IS NOT ONE AXIS.**

## 4. ✅ **WHAT THE NUMBERS LEAVE STANDING IS THE MODULE'S OWN EXPLANATION**

*Its words: the metric measures **"how do I perceive/interact with X, not what X specifically IS"**.*

***With 12 dimensions describing perception and action, two unrelated words can genuinely have similar
profiles -- both mid-sized things you look at and handle. That is not an artifact to be projected
away; it is what the representation MEANS.*** **A 12-dimension perceptual code is not a
1,028-word identity code, and no rotation of it becomes one.**

## TLDR

Word pairs that people rate as completely unrelated still score 0.91 out of 1 on our grounded
similarity. **I had a tidy explanation: one dominant direction that all the vectors share, which is a
standard and easily removed problem.**

**I measured it, and my explanation is wrong.** The biggest single direction accounts for about a
quarter of the variation, not most of it, and it is not the "how concrete is this" direction I
assumed — it loads most heavily on a sensory dimension instead. **Removing it entirely moves the
number from 0.91 to 0.89.**

**What survives is the explanation the component already gave**, which I had treated as a phrase
rather than a finding: these twelve numbers describe *how you perceive and handle a thing*, not *what
the thing is*. **Two unrelated objects can genuinely be perceived and handled alike.** That is not a
flaw to be scrubbed out — it is what the measurement is *about*.

**The general point: twelve dimensions of perception cannot be a thousand-word identity system**, and
no clever rotation makes them one.

## QUESTIONS

None.

## NEXT STEPS

1. **Do not propose removing a principal component from the grounded dims.** *PC1 is 27.5%, its
   loadings are spread, and removing it buys `0.022` on the unrelated 95th percentile.*
2. **Stop treating the module's "dominant shared concreteness axis" phrase as a mechanism** -- *the
   variance is not concentrated and not on concreteness.*
3. *Method note: **I had a cheap fix for a cause I had not verified.** Checking the cause took one
   command and removed the fix.*
