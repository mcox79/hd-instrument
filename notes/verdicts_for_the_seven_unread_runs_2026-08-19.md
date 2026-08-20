# VERDICTS FOR THE SEVEN RUNS THAT FINISHED WITHOUT ONE (2026-08-19), READ 2026-08-20

**Why this file exists.** The owner asked: *"there are a lot of 'no verdict' runs in the latest
results tab - is that correct or old?"* Measured: the seven NEWEST runs had no `verdict` field and
everything 1.7 days older had one -- a sharp cutoff. **They were neither old nor broken.** Their
files are 9-26 KB carrying `units`, `spec`, `what_is_tested` and `run_mode: full`. They finished.
They simply never wrote the one-line `verdict` the dashboard displays, so each rendered as
"(no verdict recorded)" and read like a failure.

**⛔ THE LANDED `metrics.json` FILES ARE NOT MODIFIED.** Writing a verdict into a finished result
after reading it is the same hazard class as adjusting a gate after seeing the data, and this project
refuses that elsewhere. These verdicts live here, beside the evidence, dated, and attributed to a
reader rather than to the run.

**Every number below is quoted from the run's own `metrics.json`.** Five of the seven carry
substantive findings. Four of those change what the project believes.

---

## 1. `exp_grounding_precision_gold_v1` -- **HARD_FAIL_LOSES_TO_TRIVIAL_BASELINE**
*The most consequential of the seven.* Grounding precision against an INDEPENDENT gold
(`conceptnet_gold_v1`, 422,082 edges, provenance-filtered, **NO WordNet source**),
`items_predate_mechanism: True`, ~40,000 sentences/seed across 28 corpora, paired permutation tests.

| seed | SUBSTRATE | RANDOM_ANCHOR | MOST_FREQUENT | TOP_COOCCURRENT |
|---|---|---|---|---|
| 20260819 (n=441) | 0.0159 | 0.0023 *(p=.069)* | 0.0023 *(p=.065)* | **0.0476 (p=.0045)** |
| 7 (n=398) | 0.0302 | 0.0025 *(p=.005)* | 0.0025 *(p=.002)* | **0.0653 (p=.019)** |
| 101 (n=441) | 0.0272 | 0.0045 *(p=.011)* | 0.0023 *(p=.005)* | **0.0590 (p=.015)** |

**A trivial top-co-occurrent baseline is 2-3x more accurate than the substrate on all three seeds.**
On seed 20260819 the substrate is not distinguishable from a RANDOM anchor (p=.069).
`top_anchor` is **`way`** on all three seeds -- a contentless word is the single most-assigned
meaning. ~10,000 refused per seed against ~550 grounded, so the gate is not the leak.
**SCOPE:** ConceptNet absence is not proof a grounding is wrong, so 1.6-3.0% is a LOWER bound. The
COMPARISON survives that: same gold for every arm.

## 2. `exp_substrate_end_to_end_readout_v1` -- **CONSOLIDATION_IS_INERT_ON_THE_READ_OUT**
Its own prereg question: *"With consolidation actually firing, does the read-out change at all?"*

| ablate | n_episodes | n_provenance | n_refused | OUTPUT |
|---|---|---|---|---|
| (control) | 8394 | 68 | 487 | -- |
| `episodic` | **0** | 68 | 487 | **CHANGED** |
| `definitions` | 8394 | **46** | **523** | IDENTICAL |
| **`consolidation`** | 8394 | **0** | **0** | **IDENTICAL** |
| `foraging` | 8394 | 68 | 487 | IDENTICAL |
| `gap_detector` | 8394 | 68 | 487 | IDENTICAL |

**The ablations demonstrably fired** -- the middle columns prove it -- so IDENTICAL means INERT, not
"the switch failed". Ablating consolidation zeroes provenance and refusals and changes no arm's
hit@1 to four decimals on any seed. **Three components do real work that never reaches the read-out.**
`gap_detector` does not even change internal state, independently reproducing the
correct-but-redundant finding.
**This cell also retired its own headline** (*"the hit@1 is NOT a capability claim"*) and warned that
cloze-like tasks favour co-occurrence BY DESIGN -- a caveat that applies to the synonym-rank work
done on 2026-08-20 and is recorded there.

## 3. `exp_discrimination_ceiling_v1` -- **HARD_FAIL_LOSES_TO_BAG_OF_WORDS**
Same independent gold. The DISCRIMINATION arms re-rank the SAME top-50 set, so any difference is the
RANKER, not retrieval.

| corpus | RAW (ours) | BAG_COSINE | SECOND_ORDER | RANDOM |
|---|---|---|---|---|
| simplewiki | 0.1356 | **0.1557** | 0.1557 | 0.0392 |
| onestop | 0.0913 | **0.1010** | 0.1010 | 0.0291 |
| mcguffey_graded | 0.0781 | **0.0985** | 0.0985 | 0.0170 |

`ORACLE_ceiling_diagnostic = 1.0`, so the task is not capped. **`BAG_COSINE` and `SECOND_ORDER`
score identically but are NOT the same arm** -- they differ on `ci_half_width`, `ci_hi`, `ci_lo` and
`paired_perm_p_vs_RAW` on every corpus, which depend on WHICH items were hit. **"Same accuracy by
different routes", not "the same ranker".**

## 4. `exp_sr_scale_ladder_v1` -- **SR_DOES_NOT_SCALE_WHILE_THE_COUNTER_DOES**
Population FROZEN to the smallest rung's vocabulary, rung corpora NESTED, so only the amount of text
varies. No population confound available.

| rung | COOC_floor (3 seeds) | SR_g0.1 | SR_g0.9 |
|---|---|---|---|
| 750 | 0.020 / 0.018 / 0.020 | 0.008 / 0.013 / 0.023 | 0.013 / 0.008 / 0.015 |
| 40,000 | **0.070 / 0.055 / 0.050** | 0.013 / 0.013 / 0.013 | **0.000 / 0.000** / 0.005 |

**The counter scales ~3.5x over a 53x text increase; SR is flat or declining and
`clears_credible_bar` is False on every rung, seed and discount.** `SR_g0.9` reaches exactly 0.0 at
40,000 sentences on two seeds -- a mechanism that degrades as evidence accumulates is mis-specified,
not under-trained. `transitions_per_state` goes 2.5 -> 80.2, so the matrix densifies and a
heavily-discounted multi-step occupancy washes out.
*This supersedes the weaker single-sample SR closure done on 2026-08-20.*

## 5. `exp_cortical_read_consolidated_v1` -- **CHANNELS_COMBINE_BUT_STILL_LOSE_TO_THE_FLOOR**
Median rank, lower is better:

| seed | CONTEXT | SPOKE | **BOTH** | SCRAMBLE | COOC_floor |
|---|---|---|---|---|---|
| 20260819 | 126.0 | 82.0 | **69.0** | 173.0 | 15.0 |
| 7 | 115.5 | 88.0 | **79.0** | 176.0 | 20.5 |
| 101 | 121.0 | 88.0 | **75.5** | 196.0 | 17.0 |

**`BOTH` beats both single channels on every seed** -- the best evidence in the project for the
owner's *"the brain uses many channels and combines them"*. Scramble control clean.
**But `CONTEXT_clears=False, BOTH_clears=False` at every k**, and the floor is 4x better.
**Honest tension: at hit@1, `BOTH` (0.030) is WORSE than `CONTEXT` (0.057)** -- combining helps the
tail and hurts first place. v2 of this cell passed against weak floors; v3 added the co-occurrence
floor and the same arms failed.

## 6. `exp_sensorimotor_spoke_grounding_v1` -- **BAR_NOT_CLEARED, BUT SUPPLIED NORMS BEAT US**
Bar pre-registered: *"TOP_COOCCURRENT. Beating RANDOM_CANDIDATE is not the bar."*
Spoke arms vs that bar: **paired p = 1.0, 1.0, 0.3353 -- NOT separated.** *Point estimates suggested
otherwise; the paired statistic decides.*
**What IS separated:** supplied norms beat the SUBSTRATE on all three seeds (p = .029/.017/.0155),
and the `SHUFFLED_NORMS` can-fail control collapses (p = .008/.0145/.0025). Our substrate sits at
RANDOM on seed 20260819 (7 hits vs 7). The cell scopes itself: *"the norms are SUPPLIED human
ratings... no result here is the substrate having LEARNED perceptual structure."*

## 7. `exp_predictive_write_gate_v1` -- **ALREADY READ AND RECORDED**
Its results were read on 2026-08-19 and are quoted in full in `notes/STATUS.md` (54 cells, the
monotone-degradation table, GATED == RANDOM_SKIP at high skip rates). **The only one of the seven
whose findings were already in the record.** *Which is why its blank verdict line went unnoticed --
the finding existed, the display did not.*

---

## THE PROCESS FINDING, WHICH IS WORTH AS MUCH AS ANY OF THE SEVEN

**Six runs with complete results, four of them changing what the project believes, were invisible
for a day because of a missing one-line field.** The dashboard rendered them as
"(no verdict recorded)" -- indistinguishable from a crash.

Two fixes landed 2026-08-20:
- `tools/status_state.py` now renders a verdictless run as
  `NO VERDICT LINE -- RESULTS PRESENT (full, N units recorded)`, and `_grade` treats it as
  NO-VERDICT rather than letting the tokeniser read the word "NO" as a negative result.
- **The deeper fix is not code**: a cell that writes 26 KB of units and no verdict has done the
  expensive part and skipped the cheap one. *A run without an adjudication is not a finished run.*
