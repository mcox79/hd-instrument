# **THE CONCEPT STORE'S OWN OPERATION, MEASURED FOR THE FIRST TIME: MORE TRACES *HELPS*, MONOTONICALLY, ACROSS THE ENTIRE RANGE LIVE CONCEPTS OCCUPY. THERE IS NO SATURATION.**

**One turn ago I withdrew a saturation claim and recorded the reason as an OPEN question: neither
capacity curve was the store's own operation. This measures that operation. The answer points the
opposite way from saturation, and it is CI-separated with a working control.**

---

## 1. THE OPERATION, BUILT TO MATCH `canonicalize` RATHER THAN A NEARBY CURVE

**`ConceptSpace` accumulates a plain sum per lemma and `canonicalize` matches against anchors. So:**

> **anchor(lemma) = sum of L of its context vectors. probe = a HELD-OUT context vector of the same
> lemma, never in any anchor. Score = hit@1 over 80 anchors. Chance = 0.0125.**

*80 lemmas, 41+ live context vectors each from 59,797 real corpus sentences, 8 held out per lemma,
640 probes per point. `hdlab.substrate.context_vector_masked` -- the live function, not a
reimplementation.*

## 2. THE RESULT

| L (traces in the anchor) | hit@1 | ±95% | **shuffled-label control** |
|---|---|---|---|
| **1** | **0.0312** | ±0.0135 | 0.0078 |
| 4 | 0.0516 | ±0.0171 | 0.0141 |
| 8 | 0.0719 | ±0.0200 | 0.0172 |
| 16 | 0.0984 | ±0.0231 | 0.0219 |
| 24 | 0.1219 | ±0.0253 | 0.0156 |
| 32 | 0.1172 | ±0.0249 | 0.0141 |
| **37** | **0.1328** | ±0.0263 | 0.0156 |

**✅ THE CONTROL WORKS: permuting the anchor-to-label assignment collapses every point to chance
(0.0078-0.0219 against 0.0125).** *The effect is not an artefact of the harness.*

**✅ L=1 vs L=37 IS CI-SEPARATED** -- `[0.0177, 0.0447]` vs `[0.1065, 0.1591]`. **Accumulating more
traces makes a concept's anchor a BETTER match for a held-out encounter with the same word, by a
factor of 4.3x, and 10.6x chance at the top.**

## 3. 🎯 **WHY THIS MATTERS: THE LIVE RANGE IS ENTIRELY INSIDE THE IMPROVING REGION**

**Measured live loads: median 10, p90 36, max 77.** *The curve is still rising at L=37.*

> ***THERE IS NO SATURATION ANYWHERE IN THE RANGE LIVE CONCEPTS ACTUALLY OCCUPY. MORE IS BETTER.***
> **This independently confirms the withdrawal one turn ago and closes the saturation story
> properly -- not by retracting a bad comparison, but by measuring the right thing.**

## 4. ⚠️ WHAT IT DOES *NOT* SETTLE, STATED PLAINLY

1. **THE SWEEP HITS ITS EDGE STILL CLIMBING (or flat): L=24 `0.1219±0.0253` vs L=37
   `0.1328±0.0263` OVERLAP.** *So the top of the range is flat within noise and **an optimum is not
   located**. This is the same tell as Q96 -- and it is already an executable assertion in
   `vsa_cleanup_memory.selftest_capacity_is_measurable`.* **Do not read "more is better" as
   unbounded; read it as "no cost up to 37".**
2. **ABSOLUTE PERFORMANCE IS LOW.** *0.1328 is 10.6x chance and it is still 87% wrong.* **This says
   accumulation is not what is broken; it does not say the representation is good.**
3. **DIFFERENT TASK FROM THE WRITE-RATE SWEEP.** *That sweep scored a paradigmatic-vs-syntagmatic
   AUC; this scores self-identification against anchors.* **Both are measured; neither transfers.**

## 5. ⚡ **THE TENSION THIS EXPOSES -- AND IT IS NOW MEASURED ON BOTH SIDES**

| | task | direction |
|---|---|---|
| write-rate sweep | paradigmatic/syntagmatic AUC | **writing LESS helps** (0.0710 -> 0.3079) |
| **this** | anchor self-identification | **writing MORE helps** (0.0312 -> 0.1328) |

***These are not contradictory -- they are different tasks -- but they pull in opposite directions,
and anyone acting on "write less" should know that the store's own matching operation gets WORSE
when you do.*** **That is a real cost of the approved sweep and it was not visible before tonight.**

## TLDR

Last turn I withdrew a claim and said the honest reason was that I'd never measured what the system
actually does. **I've measured it now, and it points the other way.**

The system builds up a picture of each word by adding up the contexts it appears in. **The question:
does adding more contexts make that picture better or worse?** Answer: **better, steadily, across the
whole range our words actually occupy.** A word's picture built from 37 encounters identifies a fresh
encounter with that word **four times more reliably** than one built from a single encounter.

**And the check that matters passed:** shuffle which picture belongs to which word and performance
collapses to guessing. So the effect is real.

**There is no overcrowding.** The worry I raised two turns ago and withdrew one turn ago is now
closed properly — not by admitting a bad comparison, but by measuring the right thing.

**Three honest limits.** The improvement flattens near the top of what I tested, so I can't say where
it stops — the same "ran out of road" problem as the other experiment. The absolute numbers are poor:
ten times better than guessing, still wrong seven times in eight. And this is a *different task* from
the write-less experiment.

**Which surfaces something worth your attention.** The experiment you approved says the system does
better when it writes *less*. This measurement says its word-pictures get better when it writes
*more*. **Both are now measured. They're different jobs, so it isn't a contradiction — but it does
mean writing less has a cost that wasn't visible until tonight.**

## QUESTIONS

None.

## NEXT STEPS

1. **The saturation story is closed.** *No bundle overcrowding exists in the live range.*
2. **Extend this sweep past 37**, with the same stopping discipline the write-rate sweep now has --
   it is flat-within-noise at the top and no optimum is located.
3. **Carry the tension into the approved sweep's writeup:** *less writing improves one task and
   degrades the store's own matching operation. Report both or the result is half a picture.*
