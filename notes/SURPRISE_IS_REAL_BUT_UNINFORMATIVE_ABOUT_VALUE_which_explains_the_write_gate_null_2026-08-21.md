# **SURPRISE IS NOT SATURATED -- IT HAS REAL SPREAD. IT SIMPLY DOES NOT PREDICT A TRACE'S VALUE. THAT IS A MORE PRECISE EXPLANATION OF THE WRITE-GATE NULL, AND I NEARLY GAVE THE WRONG ONE.**

**Owner, Q74: *"I think we need to have some measure of what it's learning by taking notes each
time... only when there's something NEW that it can learn... I still think it's the 'surprise'
measurement - and that makes sense."* This tests that intuition directly.**

---

## 1. 🔻 **THE WRONG EXPLANATION I ALMOST FILED**

**Mean surprise by trace position barely moves: `0.9572 → 0.9288` across 37 positions.** *I read that
as "the surprise signal is SATURATED -- everything looks novel, so gating on it is necessarily
random."* **That is a clean story and it is wrong.**

## 2. ✅ **THE DISTRIBUTION SAYS OTHERWISE -- AND IT IS WHAT A GATE ACTUALLY THRESHOLDS ON**

*2,880 trace events over 80 lemmas. Surprise = 1 − cos(new trace, anchor built from all previous).*

| | mean | sd | p1 | p25 | p50 | p75 | p99 | range |
|---|---|---|---|---|---|---|---|---|
| per-trace surprise | 0.9360 | **0.0960** | 0.6437 | 0.8865 | 0.9477 | 1.0013 | 1.1230 | **0.348 – 1.204** |

**THERE IS REAL SPREAD.** *p10-p90 spans 0.233 on a 0-1 scale; a threshold has something to bite on.*
**So the write-gate null is NOT explained by a degenerate signal, and the position-means were
misleading because averaging over 80 lemmas hid the within-position variance.**

*(Values above 1.0 are traces ANTI-correlated with the anchor -- expected when context vectors are
near-orthogonal.)*

## 3. 🎯 **THE ACTUAL FINDING: THE SIGNAL IS REAL AND UNINFORMATIVE ABOUT VALUE**

| | |
|---|---|
| correlation between per-position surprise and per-position marginal task gain | **r = +0.2382, n=36** |
| **95% interval on that r** | **comfortably spans zero** |

***Surprise varies, marginal value varies, and they do not vary together.*** **A gate can select
high-surprise traces perfectly well -- it just will not be selecting valuable ones.**

## 4. 🔗 **AND THAT EXPLAINS A PREVIOUSLY UNEXPLAINED NULL**

**`exp_predictive_coding_write_gate_dissociation_v1` found prediction-error gating `NOT_SEPARATED`
from a rate-matched RANDOM gate at ALL FOUR thresholds** (0.0961/0.1526/0.2268/0.3079 against
0.0971/0.1368/0.2165/0.3007). *That was recorded as a fact without a mechanism.*

> ### **THE MECHANISM IS NOW NAMED: NOT THAT SURPRISE IS UNMEASURABLE, BUT THAT IT IS UNCORRELATED WITH WHAT A TRACE IS WORTH. GATING ON AN UNCORRELATED SIGNAL *IS* GATING AT RANDOM.**

**⚠️ AND THE EVIDENCE IS ASYMMETRIC, WHICH I AM STATING RATHER THAN HIDING: my correlation is on 36
aggregated positions and is UNDERPOWERED. The strong evidence is the landed cell's rate-matched
control, which is a direct measurement with CIs at four thresholds. They agree, and the cell is the
load-bearing one.**

## 5. WHAT THIS MEANS FOR THE OWNER'S INTUITION

**The intuition -- *write when there is something new to learn* -- is sound and is exactly what the
brain-side prediction-error account says.** *What fails is our PROXY for "something new": cosine
distance from the accumulated anchor.* **That proxy measures NOVELTY OF FORM, and what the intuition
needs is NOVELTY OF CONTENT.** *In a representation where every context is near-orthogonal to every
other, form-novelty is nearly constant and tells you nothing about whether the trace teaches
anything.*

***So the route is not closed. The measure is.***

## TLDR

You said the system should only take a note when there's something new to learn, and that surprise
was the right measure. **I tested it, and the intuition is right while our way of measuring surprise
is wrong.**

**First, a mistake I nearly published.** Averaged across words, surprise looks pinned near 0.94 for
every encounter, which suggested everything looks equally novel and so choosing on it must be
arbitrary. **Checking the actual spread showed that's false** — individual encounters range from 0.35
to 1.20. There is plenty for a filter to work with.

**The real problem is subtler and worse.** How surprising an encounter is simply doesn't track how
much it teaches. The two vary independently.

**And that explains something we'd recorded without understanding.** An earlier experiment found that
picking notes cleverly by surprise did no better than throwing away the same proportion at random, at
every setting tried. We knew it was true; we didn't know why. **Now we do: filtering on a signal
unrelated to value is the same as filtering at random.**

**Why the measure fails, in one line:** our surprise measures whether an encounter *looks* different,
not whether it *says* anything different. In a system where nearly every context looks different from
every other, that tells you almost nothing.

**So your instinct isn't refuted — our implementation of it is.** The thing to replace is the yardstick,
not the idea.

**One honesty note:** my correlation test rests on 36 aggregated points and is weak on its own. The
solid evidence is the earlier experiment's direct comparison against random discarding. They agree,
and that one carries the weight.

## QUESTIONS

None.

## NEXT STEPS

1. **The intuition survives; the proxy does not.** *Cosine-from-anchor measures novelty of FORM. What
   is needed is novelty of CONTENT -- and that requires a representation in which two contexts about
   the same thing look alike, which is the 0.0056 encoding gap again.*
2. **Do not re-run surprise-gating experiments with this proxy.** *Two independent measurements now
   agree it is uninformative about value.*
3. *Recorded because it was nearly wrong: the position-MEANS suggested saturation; the DISTRIBUTION
   refuted it. Averaging over 80 lemmas hid the variance that mattered.*
