# **THE `0.45` CAP IS NOT A DEFECT -- IT IS A MEASURED SAFETY PROPERTY. BUT ITS OWN JUSTIFICATION SAYS "THIS SAME METRIC", AND THREE SEPARATE MEASUREMENTS NOW SHOW THE OTHER METRIC DOES BETTER ON EXACTLY THE CONTRAST IT NAMES.**

**I went to verify a claim I had been repeating -- that `GROUNDED_CAP=0.45` cripples the live grounded
scalar. It is true that it flattens the top of the range, and it is NOT a bug.**

---

## 1. ✅ FIRST, THE CORRECTION TO MY OWN FRAMING: THE CAP IS DELIBERATE AND EARNED

*`hdlab/grounded_similarity.py`, verified on disk (`GROUNDED_CAP = 0.45` at :96,
`min(GROUNDED_CAP, max(0.0, raw))` at :190):*

**Raw cosine over the 12 z-scored dims CANNOT separate a true synonym from a perceptually similar
sibling** -- `sofa/couch 0.968`, `happy/joyful 0.962`, `apple/orange 0.952`, `dog/cat 0.932`. *Against
a 2,000-pair random background, both classes sit in the p95-p99.9 tail and fully overlap.*

**So the module caps at `0.45`, STRUCTURALLY BELOW the `0.50` same-idea/merge threshold, guaranteeing
BY CONSTRUCTION that the grounded fallback can never trigger a false identity merge.** *Its words:
**"not a calibration bug and not something a different threshold on this SAME metric can fix"**, and
**"only the TOP of the range is deliberately flattened"** -- below the cap the ordering is genuine.*

> ### **QUOTING THAT CAP AS A CRIPPLING IS WRONG, AND I HAD BEEN DOING IT. It is a safety property with a measured reason.**

## 2. 🎯 **BUT READ THE ESCAPE CLAUSE IT WROTE FOR ITSELF: *"THIS SAME METRIC"***

***The documented ceiling is a property of COSINE.*** **Three independent measurements now say the
other metric does better on precisely the synonym-versus-sibling contrast the cap exists to survive:**

| evidence | cosine | euclid |
|---|---|---|
| `sensorimotor_spoke`'s own probe (10 synonym + 10 sibling pairs) | 0.511 SD | **1.348 SD** |
| my SimLex run tonight (829 pairs, 200-shuffle null) | rho 0.2176 | **rho 0.2876** |
| **the capped module's OWN six named pairs** (2 synonym, 4 sibling) | **+1.26 SD**, margin **0.010** | **+2.68 SD**, margin **0.272** |

**On the module's own documented failure cases, euclid separates at 2.1x the effect size and with a
27x larger absolute margin.**

## 3. ⚠️ **WHAT I HAVE *NOT* SHOWN, AND IT MATTERS**

1. ***I HAVE NOT REFUTED THE MODULE.*** **Its claim is about STATISTICAL separability against a
   2,000-pair background. Six pairs cannot test that.** *Cosine actually orders those six correctly
   -- by `0.010`.*
2. **n = 2 synonyms.** *A pooled SD from two points is fragile; treat `+1.26` and `+2.68` as
   directional, not as measurements.*
3. **NOT a proposal to remove or raise the cap.** *The cap's job is to make a false merge structurally
   impossible. Any metric change has to re-establish that guarantee on its own scale before the cap
   could move, and that is a live-path safety change needing its own can-fail test.*
4. **The 60.4% token coverage caveat is untouched.**

> ### **THE HONEST CLAIM: THE CAP'S JUSTIFICATION IS METRIC-SPECIFIC AND SAYS SO. THREE MEASUREMENTS AGREE THAT EUCLID IS BETTER ON THAT CONTRAST. THAT IS A REASON TO TEST A METRIC CHANGE, NOT TO MAKE ONE.**

## TLDR

I have been repeating that a safety limit in our code cripples one of our better signals. **I went to
check, and I was being unfair.**

The limit exists because the way that component measures similarity genuinely cannot tell a true
synonym from a merely similar thing — *sofa/couch* scores 0.968 and *apple/orange* 0.952, which is
indistinguishable. **So it deliberately refuses to report anything above a level that could be
mistaken for "these are the same idea".** That is a sensible piece of engineering, and it says so
clearly.

**But it also states exactly why it cannot do better: because of the particular way it measures
distance.** And we have a second component whose notes record that a *different* way of measuring
does far better on that exact problem.

**I checked, and three separate pieces of evidence agree** — including running the better measure on
the six examples the original component itself lists as its failures. **It separates them about twice
as cleanly, with a gap roughly twenty-seven times wider.**

**What I am not saying:** that the safety limit should be removed. Its job is to make a certain kind
of mistake impossible, and any change of measure would have to earn that guarantee again. **This is a
reason to test a change, not to make one at midnight.**

## QUESTIONS

None. *A test proposal, not a decision.*

## NEXT STEPS

1. **Stop describing the `0.45` cap as a crippling.** *It is a measured safety property; I was wrong
   to frame it otherwise, in the plan and in chat.*
2. **The testable proposal is a METRIC change with the cap re-derived on the new scale** -- *not
   raising the cap on cosine.*
3. *Method note: **the module's own docstring contained both the justification and its escape clause,
   two sentences apart.** I had quoted neither and was repeating a summary of it.*
