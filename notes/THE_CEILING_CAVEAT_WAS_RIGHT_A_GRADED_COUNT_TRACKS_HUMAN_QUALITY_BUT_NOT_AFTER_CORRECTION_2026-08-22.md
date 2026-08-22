# **THE CEILING CAVEAT I RAISED AGAINST MYSELF WAS CORRECT: A *GRADED* CO-OCCURRENCE COUNT TRACKS HUMAN QUALITY (`rho +0.2279`, `p 0.0349`) WHERE THE BOOLEAN CANNOT. AND IT DOES NOT SURVIVE CORRECTION FOR THE FIVE TESTS I RAN TO FIND IT (`p 0.1745`).**

**Both halves matter. The boolean criterion really is useless; the graded one is the most promising
quality proxy we have; and I am not entitled to call it established.**

---

## 1. THE CAVEAT THAT MADE THIS WORTH DOING

*Yesterday I concluded the co-occurrence criterion "does not measure meaning" -- it passed `86%` of
human-NOISE and `86%` of human-GOOD, Fisher `p = 1.0000`. **And I flagged, in the same note, that a
criterion saying yes to 86% of everything may simply be at CEILING rather than blind.*** **That caveat
turned out to be the whole story.**

## 2. ✅ THE GRADED VERSION SHOWS A CLEAN MONOTONE ORDERING

| human label | n | **median co-occurrence count** | median PMI |
|---|---|---|---|
| **MEANINGFUL** | 3 | **8.0** | 4.785 |
| **RELATED** | 19 | **4.0** | 4.719 |
| **NOISE** | 78 | **2.0** | 4.411 |

**Monotone on both measures. A graded count of human-MEANINGFUL facts is 4x that of human-NOISE.**

| test | rho | p |
|---|---|---|
| **graded count vs human quality rank** | **`+0.2279`** | ✅ **`0.0349`** *(null p95 `0.2143`)* |
| boolean vs human quality rank | `+0.4825` | 🔻 `0.2509` |

*The boolean's rho is LARGER and its p far WORSE -- because at 86 ones and 14 zeros it is nearly
constant, so its permutation null is enormous. **A near-constant predictor produces big-looking rank
correlations by chance**, which is the same family as the tie-density defect this repo already
documents.*

## 3. 🔻 **AND HERE IS WHY I CANNOT BANK IT**

**I ran FIVE tests on these same 100 rows today:**

| test | p |
|---|---|
| boolean GOOD vs NOISE (Fisher) | 1.0000 |
| graded count GOOD vs NOISE (perm) | 0.2407 |
| PMI GOOD vs NOISE (perm) | 0.5314 |
| **graded count TREND (Spearman perm)** | **0.0349** |
| boolean TREND (Spearman perm) | 0.2509 |

> # **SMALLEST `p = 0.0349`. BONFERRONI-CORRECTED FOR FIVE TESTS: `p = 0.1745`. THE ONE RESULT THAT CLEARED DOES NOT SURVIVE CORRECTION FOR THE SEARCH THAT FOUND IT.**

**I did not pre-register which measure or which test.** *I tried a boolean, a graded count and a PMI,
each two ways, and am reporting the one that worked. **That is exactly the shape this project's own
rules exist to stop**, and the fact that it is MY search rather than someone else's changes nothing.*

## 4. WHERE THIS LEAVES THE QUALITY PROXY

| claim | status |
|---|---|
| the BOOLEAN criterion tracks meaning | 🔻 **REFUTED** -- `p = 1.0000` on the direct test, and at ceiling |
| *"foundation validated"* as a QUALITY claim | 🔻 **still must be re-worded** -- it rests on the boolean |
| **a GRADED count tracks meaning** | ⚠️ **PROMISING, NOT ESTABLISHED** -- monotone across three levels, `p 0.0349` raw, `0.1745` corrected |
| we have a validated cheap quality proxy | 🔻 **NO** |

## 5. WHAT WOULD SETTLE IT, AND IT IS SMALL

**Pre-register the graded count as THE measure, then score a FRESH blind sample.** *One measure, one
test, stated before looking. The effect size to power against is what was seen here: median 4 vs 2, or
`rho ~ 0.23`.* **At `rho 0.23` a fresh sample of ~150 items would decide it at 80% power** -- and that
is the same eval-bank enlargement already named three times this week, which now has a fourth reason.

## LIMITS

1. **n = 3 MEANINGFUL.** *The three-level ordering leans on a group of three. The trend test uses all
   100 and is the honest version, but the top level is nearly empty.*
2. **One scorer, once, no second annotator, no kappa.**
3. **Prefix matching over 30,889 sentences** -- crude, and the corpus is the harness's own reference set.
4. **The trend test is more powerful than the two-group tests BECAUSE it uses the ordering** -- which is
   legitimate, but it is also the test most likely to reward a monotone pattern that arose by chance.

## TLDR

Yesterday I showed our automatic quality check can't tell a good learned fact from a junk one — it
waves through 86% of everything. **I also warned, in the same note, that a check which says yes to
almost everything might just be set too loose rather than genuinely blind. Today I tested my own
caveat, and it was right.**

**If you count how often the two words appear together, instead of just asking whether they ever do,
the numbers line up with human judgement.** Facts a person called meaningful appear together about 8
times; vaguely related ones 4; junk ones 2. That ordering is exactly what you'd hope for, and the
statistical test on it comes out just past the usual threshold.

**But I can't bank it, and the reason is worth being blunt about.** I tried five different versions of
this test today and am reporting the one that worked. Correcting properly for having gone looking, the
result lands at 0.17 — comfortably short. **Trying things until one passes and then quoting that one is
the exact mistake our own rules exist to prevent, and it doesn't stop being that mistake because I'm
the one doing it.**

**So: the yes/no check is dead — that stands. The counting version is the most promising quality
measure we have and is not yet proven.** Settling it needs one pre-declared measure on a fresh batch of
facts, roughly 150 of them. **That is the fourth separate reason this week to enlarge the test set.**

## QUESTIONS

None — Q105 still open, and this adds a fourth argument to the "enlarge the test set" side of it.

## NEXT STEPS

1. 🎯 **Pre-register the graded count and score a fresh blind sample of ~150.** *One measure, one test,
   declared first.*
2. ⚠️ **Until then, do not use co-occurrence -- boolean or graded -- as evidence of quality.**
3. *Method note: **testing my own caveat took twenty minutes and changed the conclusion in both
   directions** -- it rescued the graded criterion and then disqualified my own evidence for it.*
