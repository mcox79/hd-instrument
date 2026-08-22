# **`156` SMOKE RUNS ARE LABELLED HARD_PASS WHILE THEIR OWN FULL RUN IS NOT -- `5.8%` OF EVERY HARD_PASS ROW IN THE ARCHIVE, AND `65` OF THEM ARE FLAT CONTRADICTIONS (`HARD_PASS` vs `HARD_FAIL`).**

**A single-file evidence gate cannot see this class, because the defect exists BETWEEN two files.**
*Found by accident yesterday, in one cell, while doing something else.*

---

## 1. THE SWEEP

| | |
|---|---|
| matched smoke/full pairs | **1,897** |
| agree | 1,519 |
| FULL passes where smoke did not *(got BETTER with scale -- fine)* | 222 |
| 🔻 **SMOKE PASSES, FULL DOES NOT** | **156** |

**Of those 156:** *full says* **`HARD_FAIL` 65** · *full says* **`MIDDLE` 62** · *other* 29.

> # **`156` OF THE ARCHIVE'S `2,680` HARD_PASS ROWS -- `5.8%` -- ARE REDUCED-SCALE RUNS WHOSE OWN FULL-SCALE RUN DID NOT PASS. SIXTY-FIVE ARE DIRECT CONTRADICTIONS.**

## 2. 🔑 **THIS IS THE PIPELINE WORKING. THE HAZARD IS CITATION, NOT SCIENCE.**

**A smoke that passes and a full run that fails is exactly what the full run is FOR.** *Nothing here
says those 156 experiments were done badly -- it says the small trial was optimistic and the real run
caught it, which is the system behaving correctly.*

**The danger is downstream, and it is real in this repo:**

- `experiment_index.py` lists smoke rows as **their own landed cells with their own verdicts** -- I saw
  exactly this earlier in the session (`exp_graded_path_vs_orthographic_floor_v1_smoke`, listed
  separately).
- **Any count of "how many HARD_PASS do we have" includes all 156.**
- **A prior-work check that reads row 1 and stops** -- the documented 2026-08-21 failure, where row 4
  reversed row 1 -- **will sometimes read the smoke.**

## 3. ⚠️ **AND THE EVIDENCE GATE IS BLIND TO IT BY CONSTRUCTION -- CONFIRMED, NOT ASSUMED**

**`verdict_evidence_gate` passes BOTH files in the motivating pair.** *Both carry a CI, a null AND a
floor.* **It audits one file at a time; a disagreement between two files is invisible to it no matter
how careful it is.**

*One detail that cuts the other way and is worth stating: **only 1 of the 156 passing smokes carries
both a CI and a null.** So the evidence gate would independently flag 155 of them as
`EVIDENCE_INSUFFICIENT` anyway -- **the two checks overlap far more than I expected, and this sweep's
unique contribution is the ONE cell they disagree about**, which happens to be the one I found by
hand.*

## 4. WHAT I AM AND AM NOT CLAIMING

| | |
|---|---|
| ✅ 156 smoke rows carry a pass their full run does not | **measured, reproducible** |
| ✅ they are 5.8% of all HARD_PASS rows | **measured** |
| ✅ the single-file gate cannot see the class | **confirmed on the motivating pair** |
| 🔻 that any specific claim in the archive was actually mis-cited from a smoke | **NOT shown -- I have not traced a single downstream citation** |
| 🔻 that the 156 experiments are wrong | **NO -- their full runs already say so; that is the point** |

## 5. LIMITS

1. **Pair-matching is by NAME** (`_smoke`, `_selftest`, `_SMOKE_n600`, ...). *A smoke whose name does
   not follow the convention is invisible to this sweep; the true count is a LOWER BOUND.*
2. **`_selftest` is treated as a reduced-scale companion.** *Sometimes it is a genuine self-test rather
   than a small run of the same experiment; those cases are miscounted here.*
3. **Verdict strings are compared, not methods.** *`MIDDLE` vs `HARD_PASS` is a real disagreement;
   `other` (29 cells) is a bucket I have not read.*

## TLDR

Experiments here get run twice: a quick small trial first, then the real full-size run.

**I checked all 1,897 pairs. In 156 of them the small trial says "success" and the real run does not.
Sixty-five of those are flat contradictions — the trial says pass, the real run says fail.**

**This is not a scandal. It is the full run doing its job** — small trials are easier and sometimes
flatter, which is exactly why we run the big one.

**The problem is bookkeeping.** Both runs are recorded as separate results with separate verdicts, so
**anyone counting successes counts the small trial too — 156 of our 2,680 recorded successes, about one
in seventeen, are small trials whose own real run failed.** And our tool for checking whether a result
is trustworthy examines one file at a time, so it cannot possibly notice that the file next to it
disagrees.

**One thing that makes this less alarming than it looks:** only one of those 156 small trials carries
the statistical checks we require anyway, so 155 of them would already be flagged as unproven for a
different reason. **The two checks catch almost the same things** — which is itself worth knowing, and
was not obvious before measuring it.

## QUESTIONS

None — Q105 remains open; this work is independent of it.

## NEXT STEPS

1. **The honest fix is a bookkeeping one:** any count of results should exclude a smoke row whose full
   run exists and disagrees. `tools/smoke_full_disagreement.py` gives the exclusion list.
2. 🎯 **Trace ONE real citation before claiming harm.** *I have shown the hazard exists and NOT that it
   has bitten. Those are different claims and I am not merging them.*
3. *Method note: **this whole class came from a smoke row appearing in a list I nearly filtered as
   noise.** The instinct to drop "_smoke" rows before printing would have hidden it.*
