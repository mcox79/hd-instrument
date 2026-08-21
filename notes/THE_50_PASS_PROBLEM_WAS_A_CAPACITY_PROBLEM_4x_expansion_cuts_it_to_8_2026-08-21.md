# **THE 50-PASS PROBLEM WAS A CAPACITY PROBLEM, NOT A RULE PROBLEM. FOUR TIMES THE EXPANSION CUTS IT FROM 38 PASSES TO 8 -- INSIDE THE SUPPORTED REPLAY RANGE.**

**Last turn I recorded an order-of-magnitude gap as the honest cost of the local learning rule: it
needed ~50 passes where the replay literature supports single digits. I said the count might fall
with scale, overlap or cue fraction, and that this was the sweep that decides whether the route
survives. It survives.**

---

## 1. THE SWEEP

*d=256, N=400, 20 families, cue = 20% of units. Metric = the ungameable margin (target minus nearest
same-family sibling). "Passes" = the first epoch at which the local rule beats the raw cue.*

| overlap | within-family cos | raw cue | one-shot Hebbian | **passes @ dg=1024** | **passes @ dg=4096** |
|---|---|---|---|---|---|
| 0.50 | 0.0442 | 0.3464 | **0.7205** *(already fine)* | 1 | 1 |
| 0.80 | 0.2217 | 0.2193 | **0.1179** *(fails)* | 8 | **2** |
| **0.95** | 0.5604 | 0.0723 | **−0.1021** *(merges)* | **38** | **8** |

> ### **FOUR TIMES THE EXPANSION TAKES THE HARDEST CASE FROM 38 PASSES TO 8, AND THE MODERATE CASE FROM 8 TO 2.**
> **`ORGAN_MAP` D4 gives the supported replay schedules as `0,3,10` and `1,4,10`. EIGHT IS INSIDE
> THAT RANGE. TWO IS COMFORTABLY INSIDE IT.**

## 2. 🧠 **AND TWO CONSTRAINTS AGREE, WHICH IS THE PART THAT MATTERS**

**Expansion is the dentate gyrus's characteristic architectural feature -- a large, sparse
projection from a smaller input.** *Our `d=256 → dg=1024` is a 4x expansion; `dg=4096` is 16x.*

***So the change that makes the learning rule affordable is ALSO the change that moves the
architecture toward the structure it is modelled on. The biological argument and the engineering
argument point the same way, which is rare here and is worth more than either alone.***

⚠️ *I am NOT quoting a specific brain expansion ratio -- `ORGAN_MAP` pins the sparsity (~0.2% of MTL
neurons per percept, Waydo 2006) but I have not verified an expansion figure, so "expansion is
characteristic of DG" is the claim, not a number.*

## 3. ✅ **INDEPENDENT IMPLEMENTATION AGREES**

**A separate, slower per-pattern implementation (updates applied one memory at a time, dg=2048,
N=600, 30 epochs) finished in the background and confirms the essentials:**

| rule | identify | recover |
|---|---|---|
| cue itself | 0.9733 | 0.4577 |
| **one-shot Hebbian** | **0.1133** | 0.7213 |
| pseudo-inverse | 0.9567 | 0.7396 |
| local delta, 30 epochs | 0.7100 | **0.8248** |

**Hebbian's collapse reproduces (0.1133 here vs 0.1400 batched at a different scale) across two
implementations that share no code path -- per-pattern updates vs a batched matrix update.**
*And it shows the gameable metric again: the delta rule has the HIGHEST recovery (0.8248) while
sitting below the cue on identification, which is exactly why the margin metric exists.*

## 4. 🔻 WHAT THIS DOES AND DOES NOT UNDO

| claim | status |
|---|---|
| the local rule needs ~50 passes | ⚠️ **TRUE ONLY AT dg=1024. At dg=4096 it is 8.** |
| "replay cannot supply the passes" | ✅ **WITHDRAWN -- 8 is inside `0,3,10`/`1,4,10`** |
| the incumbent Hebbian rule merges correlated memories | ✅ **stands, now confirmed by a second implementation** |
| locality alone makes it biologically plausible | ✅ **still QUALIFIED -- the pass count had to be paid, and it now is, by expansion** |

## TLDR

Last turn I reported a serious problem: the realistic learning rule needed about fifty repetitions,
while the brain is thought to replay memories only a handful of times. I said the number might fall
if I changed the conditions, and that this was the test that decides whether the idea survives.

**It survives. Giving the memory four times more room drops it from thirty-eight repetitions to
eight** — and eight is inside the range the literature actually supports. At moderate difficulty it
drops to two.

**The gap was never about the learning rule. It was about how crowded the memory was.** Cramped
storage makes overlapping memories fight each other, and it takes many passes to sort them out. Give
them room and it resolves quickly.

**The part that makes this more than a lucky knob-turn:** expanding into a much larger, sparser space
is the defining feature of the brain structure we're modelling here. **So the change that makes the
learning affordable is the same change that makes the design more faithful.** Those two arguments
usually pull against each other; here they agree.

**And an independent check arrived by accident.** A slower version of the same experiment, written
differently and left running in the background, finished and reproduced the key failure — the old
rule collapsing — from a completely separate code path.

**What I withdraw:** last turn's conclusion that replay can't supply the passes. **What stands:** the
old rule really does blur overlapping memories together, now confirmed twice.

## QUESTIONS

None.

## NEXT STEPS

1. **The route is alive: local error-driven learning at 16x expansion needs ~8 passes**, which replay
   can supply. *Nothing is wired; this remains a bench characterisation.*
2. **The obvious cost is memory: `dg=4096` is 16x expansion and the weight matrix is `dg^2`.**
   *That is 16.8M floats -- affordable here, but it is a real cost and should be stated whenever the
   8-pass figure is quoted.*
3. *Do not quote "50 passes" without its `dg=1024`; and do not quote "8 passes" without its 16x.*
