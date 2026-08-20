# THE FLAGGER KEPT FLAGGING THE REPO'S **VIRTUES** -- WORKLIST **708 -> 279 -> 13 -> 1**, AND THE ONE SURVIVOR IS NOW EXAMINED AND CLEAR

`tools/read_what_the_cell_told_you.py` exists because **five times in one day the answer was already
in an artifact nobody read.** It has now needed **four** tightenings, and the pattern across them is
worth more than the tool.

---

## 1. THE WORKLIST IS NOW ONE ROW, AND IT IS EXAMINED

| tightening | flagged | what was firing |
|---|---|---|
| run 1 | **708** | *"has an `honest_scope` field"* -- fires everywhere **because this repo writes honest scope** |
| run 2 | **279** | a CONFIG threshold read as a measurement |
| run 3 (before today) | **13** | -- |
| **run 4 (today)** | **1** | see below |

**Today's three suppressions, and every one of them was the checker penalising something the repo
did RIGHT:**

1. **A tie self-test is fully tied ON PURPOSE.** `exp_sensorimotor_channel_discrimination_v1` carries
   `selftest_evidence.tie_conventions_both_ways.tie_mass_frac = 1.000` -- a deliberately
   fully-tied case proving the scorer handles ties both ways, and it does (`auc_ties_to_P` 1.0,
   `_to_S` 0.0, `half` 0.5). **Every real arm in that cell reads 0.000-0.005.** The flag punished
   the cell for HAVING the tie self-test this repo's own rules demand.
2. **A verdict that DISCLOSES its underpowered stratum is being honest.**
   `exp_organ_f_deep_reading_partialcue_ladder_v1` states `..._UNDERPOWERED_POP_768_...` **in its
   verdict string**; `exp_organ_f_accumulate_interference_diagnosis_v1` cites only the POWERED
   populations (`GROWS_FASTER_POP_128_POP_256_POP_512`). **Each has four powered populations and one
   underpowered one, and neither leans on the underpowered one.** *The coverage rule already had this
   suppression; the underpowered rule was missing it.*
3. **The tool was printing rows it ITSELF calls non-findings.** A tie-mass flag on a named
   floor/rival prints *"NOT proof the verdict is wrong"* -- and **22 of 27 Tier-1 rows were those**,
   four of them the same finding repeated across `_reduced` variants of one cell.

**And a fourth fix that was a plain defect: the arm-name list was hardcoded to five names**, so
`F1_TRIGRAM_ONLY_orthographic`, `F3_FREQUENCY_ONLY_constant`, `X3_QUERY_LENGTH` and `X4_CONSTANT`
all printed as *"an unnamed arm -- CHECK WHETHER IT IS THE TREATMENT"* **with their names sitting in
the path.** Now read from this repo's convention: `F<n>_`/`X<n>_` are floors and controls, `C<n>_` is
a candidate signal under test.

## 2. THE SURVIVING ROW, EXAMINED -- **NO ACTION**

`exp_confidence_calibration_replicate_v1`, `TIE MASS 0.979 on C1_TOP1_ABS`.

| | |
|---|---|
| all 8 candidate signals C1-C8 | **median tie mass 0.000** across 15 blocks each |
| maxima | C1 **0.979**, C2 0.003, C3 0.003, C7 0.006, rest **0.000** |
| C1's 0.979 | **1 of 15 blocks -- and it is the EXACT-KEY block.** All 14 others read 0.000 |
| controls X2/X3/X4 | 0.868 / 0.994 / **1.000** -- degenerate **as expected, they are the controls** |

**Top-1 absolute similarity saturates BY CONSTRUCTION when the query IS the key.** The standing rule
already holds that *an exact-key number does not transfer to the partial-cue regime, which is the
real one* -- and **every partial-cue block reads 0.000.** *Checked in both directions: the cell's
verdict is a NEGATIVE, and degeneracy INFLATES optimistic scores, so a degenerate arm scoring badly
anyway would be a STRONGER negative rather than a compromised one.* Persisted as
`_tie_mass_examination_2026-08-21.json` beside the evidence; `metrics.json` untouched.

## 3. 🎯 **THE GENERALISABLE PART**

**THREE OF THE FOUR TIGHTENINGS SUPPRESSED THE CHECKER PENALISING GOOD PRACTICE** -- writing honest
scope, self-testing tie conventions, disclosing an underpowered stratum. *A detector built from a
list of past failures will fire on the HABITS THOSE FAILURES CREATED, because the habit and the
failure leave the same trace in the artifact.*

**➡️ SO THE DISCRIMINATOR IS NEVER "IS THE CAVEAT PRESENT" BUT "DOES THE VERDICT DEPEND ON THE THING
THE CAVEAT IS ABOUT".** Every suppression today is that one question, and it is answerable from the
artifact alone.

## TLDR

I have a script that scans finished experiments for warning signs everyone missed at the time. It has
now been wrong in the same way four times, and the pattern is the interesting bit: **it kept flagging
things this project does WELL.**

It flagged experiments for writing down their own caveats. It flagged one for testing that its own
scoring handles ties properly. It flagged two for openly stating which part of their data was too
small to conclude from — the exact honesty you want. And it was printing warnings it had itself
labelled "this is not evidence of a problem" at the top of a list headed "things to investigate".

Fixing those took the list from **708 items down to 1**, and that last one I checked by hand: it is
fine, for a reason the project already knew.

**The lesson worth keeping: a warning system built from a list of past mistakes will fire on the good
habits those mistakes taught us**, because caution and carelessness leave the same fingerprint. The
right question is never "did they mention a limitation" but "does the conclusion actually rest on
it".

## QUESTIONS

None.

## NEXT STEPS

1. **NEXT ANGLE:** `notes/STATUS.md` is far over its size cap and is the compaction-recovery entry
   point every future session depends on -- trimming it protects all of them.
2. F5 remains cell-authoring work and is not started; its bar is measured and replicated.
