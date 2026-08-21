# **A `HARD_PASS` IS SITTING BEHIND A `PENDING` VERDICT: A HAND-CHECKED 90%-PRECISION READING EXTRACTOR NOBODY HAS SURFACED**

**Found by enumerating all 20 cells whose verdict says `PENDING` -- a small enough population to check
completely rather than sample. 13 of 20 have resolution evidence beside them. This is the best of
them.**

`exp_stated_entity_fate_reading_extractor_v2_highprecision`:

| field | value |
|---|---|
| `verdict` *(what the archive shows)* | **`STRICT_READY_PENDING_HANDCHECK`** |
| **`final_verdict`** *(inside the same file)* | **`HARD_PASS_CLEAN_GROW_BY_READING_VIABLE`** |

***The hand-check was done, adjudicated, scored against a pre-registered band, and passed -- and a
`final_verdict` was written INTO THE SAME `metrics.json`. The top-level `verdict` field was never
updated.***

---

## 1. WHAT IT ACHIEVED

| | |
|---|---|
| **hand-checked precision** | **90/100 = 0.90**, against a pre-registered band of **>= 0.85** ✅ |
| curated design | P = 1.0 / R = 1.0 (n=8) |
| curated held-out | **P = 1.0 / R = 0.8** (n=10) |
| **negation control** | **7 cases, 0 false-positive emissions -- `negation_clean: true`** |
| ProPara dev coverage | 0.7371 (**unseen** 0.1724) |

**AND THE PREDECESSOR, ALSO HAND-CHECKED, ALSO BEHIND A `PENDING` VERDICT:**
`exp_stated_entity_fate_reading_extractor_v1` -- **39/99 = 0.3939 precision.**

**➡️ 0.394 -> 0.90 HAND-CHECKED PRECISION, ~100 ADJUDICATED ITEMS EACH.**

## 2. ✅ THE ERROR TAXONOMY CONFIRMS THE MECHANISM, WHICH IS BETTER THAN THE HEADLINE

| v1 error families | n |
|---|---|
| `wrong_patient` | **17** |
| `intransitive_subject_is_theme` | **13** |
| `causative_light_verb` | **12** |
| `proper_noun_title` | 6 |

**v2's remaining errors are ALL SINGLETONS** -- `wrong_patient_reactant` 1,
`wrong_head_chemical_modifier` 1, `wrong_patient_agent_lightverb` 1, `adjectival_agent_oxidizing` 1...

***The named systematic families were eliminated and what remains is a scattered long tail. That is
what a real fix looks like, as opposed to a threshold move.***

## 3. ⚠️ **THE COST, STATED PLAINLY -- AND IT IS TONIGHT'S "WRITE LESS" PATTERN WITH A TWIST**

**`corpus: raw=4015 -> strict=1414, survival_rate 0.3522`.** *Only 35% of extractions survive the
strict filter.*

**APPROXIMATE EFFECTIVE YIELD** *(precision measured on each version's own hand-check sample, so this
is indicative, not exact)*:

| | extractions | precision | ~correct facts |
|---|---|---|---|
| v1 | 4,015 | 0.394 | **~1,582** |
| **v2 strict** | **1,414** | **0.90** | **~1,273** |

**➡️ V2 PRODUCES *FEWER* CORRECT FACTS IN ABSOLUTE TERMS (~1,273 vs ~1,582) AT MUCH HIGHER PURITY.**
*Tonight's write-less finding held that keeping less improved the score. **Here keeping less improves
purity and REDUCES total correct output.** Which is better depends entirely on whether downstream
cares more about volume or contamination -- and that has not been measured.*

## 4. WHY THIS WAS INVISIBLE

**`query` and any dashboard reads `verdict`. `verdict` says `PENDING`. The answer is in
`final_verdict`, four fields further down the same file.** *No tooling looks there. **The archive is
not missing this result -- it is displaying the wrong field.***

## TLDR

I checked every one of the twenty experiments whose status says "waiting for a human to grade this."
**Thirteen have the grading sitting right next to them. One of those is a clear success nobody has
mentioned.**

A reading extractor -- the thing that pulls facts like *"the stomach destroys food"* out of ordinary
sentences -- was hand-checked at **90% correct on a hundred examples**, against a target of 85% set in
advance. Its predecessor scored **39%**. The improvement is real rather than cosmetic: the earlier
version had three big recurring mistakes, and in the new version those are gone entirely, leaving
only scattered one-off errors.

**It also handles negation correctly** — given seven sentences like *"the wood is not consumed"*, it
produced zero false claims.

**The honest cost:** it only keeps about a third of what it finds. And doing the arithmetic, that
means it produces **fewer** correct facts overall than the sloppier version — roughly 1,270 against
1,580 — but with far less rubbish mixed in. **Whether that's the right trade depends on what happens
downstream, which nobody has measured.**

**Why nobody noticed:** the file contains both a "status" field and a "final verdict" field. The
status still says "awaiting grading." The final verdict, a few lines below in the same file, says it
passed. **Every tool reads the first one.**

## QUESTIONS

None.

## NEXT STEPS

1. **This result should be surfaced** -- a hand-checked 90%-precision extractor with verified negation
   handling is one of the better things in the archive and it is invisible.
2. **The `verdict` vs `final_verdict` split is a display bug with a real cost** -- *any tool reading
   `verdict` reports the wrong state for at least this cell.*
3. **The volume/purity trade needs a downstream measurement** before v2 is preferred to v1.
