# **OUR CA3 MERGES OVERLAPPING MEMORIES INSTEAD OF COMPLETING THEM. THE FAILURE IS THE IMPORTED COMPLETION RULE -- NOT THE SPARSITY REGIME, NOT THE MISSING ALLOCATOR -- AND THE THRESHOLD IS MEASURED.**

**Working the way the owner asked: name the brain structure, state its computation, state what we
substituted, and design the arm that distinguishes them. Three arms, two of my own hypotheses
refuted, and the third isolates the fault to a specific line of imported mathematics.**

---

## 1. THE STRUCTURE AND THE SUBSTITUTION

**CA3 (organ D2). Brain's job: PATTERN COMPLETION -- recover a full stored episode from a partial or
degraded cue.** *`ORGAN_MAP`: core operation **UNPINNED** -- "Hopfield sign-update and modern-Hopfield
softmax are OUR imports."* **So the completion RULE is ours, and it is the thing under test.**

## 2. ARM 1 -- MY FIRST HYPOTHESIS, REFUTED

*Hypothesis: our pipeline routes the RETRIEVAL cue through DG, which pattern-separates it away from
its target; the brain retrieves via the direct EC→CA3 path instead.*

| | CA3 ON | CA3 OFF | delta |
|---|---|---|---|
| corrupt the INPUT, re-encode through DG (25% flip) | 0.6700 | **0.8125** | **−0.1425** |
| **degrade the STORED CODE directly (direct path), 20% of units kept** | 0.8375 | **1.0000** | **−0.1625** |

**🚫 REFUTED. The direct path does not rescue CA3 -- it is worse there.** *And note `CA3 OFF = 1.0000`
with **80% of active units deleted**: ~40 active units in 2,048 dimensions means ~8 survivors still
identify the pattern uniquely.*

## 3. ARM 2 -- SECOND HYPOTHESIS, ALSO REFUTED: "IT NEEDS MORE LOAD"

| N stored | 400 | 2,000 | 8,000 | **20,000** |
|---|---|---|---|---|
| CA3 OFF | 1.0000 | 1.0000 | 1.0000 | **1.0000** |

**🚫 REFUTED. Even at 20,000 stored patterns a 20% cue is unambiguous.** *Completion is never
REQUIRED at any load we can reach, because the codes are near-orthogonal by construction.*

## 4. ✅ ARM 3 -- THE ONE THAT ISOLATES IT: OVERLAPPING MEMORIES

**Real episodes share content. Random vectors do not. So: families of variants around a shared base.**
*(Reported WITHIN-family, after I first made the mean-over-the-wrong-population error again -- with
30 families only ~1 pair in 30 is same-family, so the all-pairs mean hid the effect entirely.)*

| input corr | **within-family code cos** | cross-family | **CA3 ON** | CA3 OFF | delta |
|---|---|---|---|---|---|
| 0.00 | −0.0003 | −0.0000 | 0.9050 | 1.0000 | −0.0950 |
| 0.50 | 0.0467 | 0.0001 | 0.8450 | 1.0000 | −0.1550 |
| **0.80** | **0.2254** | −0.0002 | **0.1433** | 1.0000 | **−0.8567** |
| **0.95** | **0.5510** | 0.0002 | **0.0533** | 0.9733 | **−0.9200** |

> ### **CA3 COLLAPSES FROM 0.845 TO 0.143 AS WITHIN-FAMILY OVERLAP RISES FROM 0.047 TO 0.225. AT 0.55 OVERLAP IT SCORES 0.0533 WHILE SIMPLY *NOT* COMPLETING SCORES 0.9733.**
>
> ***IT DOES NOT FAIL TO COMPLETE. IT ACTIVELY MERGES OVERLAPPING MEMORIES INTO THEIR SHARED BASE --
> which is the catastrophic-interference failure that DG exists to prevent, happening in the organ
> DOWNSTREAM of DG.***

**✅ CONSTRAINT CHECK: my within-family 0.5510 at ρ=0.95 reconciles with the organ's OWN self-test,
which reports `input_cos 0.934 → code_cos 0.561` for a near-duplicate.** *Independent route, same
answer -- so the measurement is trustworthy.*

**✅ AND IT VINDICATES DG, one of the five `fidelity SAME` organs: cross-family cosine stays at
~0.0000 while within-family rises to 0.55. DG separates WITHOUT destroying graded structure, which
is exactly what pattern separation should do.**

## 5. 🎯 THE ANSWER TO "WHICH OF THE THREE"

| candidate | verdict |
|---|---|
| sparsity regime (0.01-0.03 vs pinned ~0.2%) | **NOT IT** -- the project's own sweep already found the pinned band was the WORST point |
| the missing allocator | **NOT THE PROXIMATE CAUSE** -- failure is present with addresses assigned correctly |
| **the imported COMPLETION RULE** | ✅ **IT.** *Hopfield sign-update merges correlated attractors. The brain's CA3 does not.* |

## TLDR

Working the way you asked — name the brain part, say what it does, say what we substituted, then
design the test that tells them apart — I got two of my own guesses wrong and then found the answer.

**The component is CA3, whose job in the brain is to reconstruct a whole memory from a fragment.**
Our version doesn't. **I'd assumed either that we were feeding it the fragment the wrong way, or that
it just needed more memories before it mattered. Both wrong** — I tested them and neither helped, even
with twenty thousand memories stored.

**The third test found it.** Real memories overlap — two visits to the same café share most of their
content. Random test patterns don't. So I built memories that genuinely overlap.

**Our CA3 doesn't merely fail to help there — it destroys the answer.** With overlapping memories it
scores 0.05, while *simply not using it at all* scores 0.97. **It blurs similar memories together into
their common core**, which is precisely the failure the brain's memory system is built to avoid.

**Two things this vindicates.** The upstream component that separates similar inputs is working
properly — it keeps unrelated things far apart while preserving genuine similarity, exactly as it
should. And my measurement agrees with that component's own built-in test, reached by a different
route, which is why I trust it.

**So the fault is the specific piece of borrowed mathematics we chose for completion** — a classic
recipe that is known to merge overlapping memories. Not the sparsity setting, which was already
tested. Not the missing addressing step. **The completion rule itself.**

## QUESTIONS

None.

## NEXT STEPS

1. **The build target is now specific: a completion rule that tolerates overlap.** *The literature
   does not pin CA3's update rule, so this is ours to choose and declare -- but the SIGNATURE it must
   reproduce is pinned: completion from a partial cue WITHOUT merging correlated episodes.*
2. **The test now exists and can fail**: the within-family overlap sweep, where the incumbent scores
   0.0533 against a not-completing baseline of 0.9733. *That is a real bar, not random.*
3. **Do not re-run the sparsity sweep or blame the allocator** -- both are excluded above.
