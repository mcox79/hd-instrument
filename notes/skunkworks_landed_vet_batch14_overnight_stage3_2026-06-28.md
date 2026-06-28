# Skunkworks batch 14 landed-VET (overnight Stage 3 wave) -- 2026-06-28

**Author:** Skunkworks (cert-owner / auditor)
**Date:** 2026-06-28
**Tool:** `tools/atomize_skunkworks_batch14_overnight_stage3_2026-06-28.py`
**Source request:** Director batch 14 dispatch (8 candidates; overnight wave)
**Pre-state:** CERT N=626 (verified live via PartitionedStore + provenance_quality count)
**Post-state (predicted; A5-gated):** CERT N=628 (+2 chain-grade)
**Discipline:** READ each metrics.json directly off disk (Director-framing-errors caught: 2 today; 7 prior in arc)

---

## SUMMARY (per-atom tier + delta + framing-cross-check)

| # | Anchor | Director claim | Verified off-disk | Tier | CERT delta |
|---|--------|---------------|-------------------|------|------------|
| 1 | CF Cell 2 v2 single-int | "FULL HARD_PASS chain-grade x2 + auto-promote parent" | **smoke n_seeds=2 N=2048** -- SAME data as batch 13 | **REFUSE re-atomize** + REFUSE parent promote | 0 |
| 2 | CF regret vmPFC v1 | "FULL HARD_PASS chain-grade" | **FULL n_seeds=5 R2=0.987 cv=0.002 gap=1.195 cardinality_ok=True crlb_ok=True** | **chain-grade** | +1 |
| 3 | Schema exemplar-Bayes | "FULL HARD_PASS confirms today's smoke" | **FULL n_seeds=5 primary=0.714 lift=+0.443 cv=0.025 cardinality 72000/72000** | **chain-grade (PROMOTE batch13 MM)** | +1 |
| 4 | Online conv hippo | "HONEST_NEG hippo binding broken in composition" | **TASKVEC_PLUS_HIPPO arm errored kth=64 OOB 60 BOTH seeds; cardinality_ok=False (240/300)** | **REFUSE HONEST_NEG -- bug not negative** | 0 |
| 5 | Narrative 100-event ANCHOR 1 | "Q1+Q4 chain-grade quality MM" | full HARD_FAIL; FULL_STACK=0.556 (Q1=0.889 + Q4=1.0 substrate-quality) + **NO_SEGMENT TIES FULL_STACK at 0.556 lift=0.000 sha16 IDENTICAL** | **MEASURED_MECHANISM** (Q1+Q4 substrate-quality + segmentation-not-load-bearing) | 0 |
| 6 | SWR preplay hypothesis-gen | "HARD_FAIL but generator works MM" | full pipeline_top1=0.108 HARD_FAIL; PREPLAY recall@10=0.558 novelty=1.0 lift=+0.558 cv=0.035 | **MEASURED_MECHANISM** (generator + downstream-scorer bottleneck) | 0 |
| 7 | Boundary detector | "MIDDLE_BAND saturated mechanism MM" | full cs_f1=1.000 = oracle_f1=1.000 at drill regime (SNR ~22x); lift_budget=+0.446 | **MEASURED_MECHANISM** (by-construction-saturation) | 0 |
| 8 | META_RULE_AM substrate-already-does-X | discipline atom | 8 occurrences today including #5 segmentation null + #7 boundary saturation | **META atom** (meta corpus) | 0 |

**Net CERT delta: +2 chain-grade (626 -> 628)**

**Director-framing-errors caught in batch 14: 2**
- **#8 (CF v2 "FULL HARD_PASS")**: data on disk is still `run_mode=smoke, n_seeds=2` (same as batch 13 which already atomized this path at MEASURED_MECHANISM). No new evidence; re-atomization refused.
- **#9 (Online conv hippo "HONEST_NEG")**: code bug (refuse-gate kth > vocab size), not honest negative. Filing HONEST_NEG would conflate infra-bug with negative result. Needs cell-author fix + redispatch.

**Cumulative Director-framing-errors caught today: 9** (7 prior in arc per MEMORY.md + 2 today).

---

## DETAILED VERIFICATION (off-disk; per-atom)

### ATOM 1 (REFUSED): CF Cell 2 v2 single-intervention -- "FULL HARD_PASS + parent promote"

**Director claim:** "Cell 2 v2 single-intervention FULL HARD_PASS + AUTO-PROMOTES PARENT (chain-grade x2)"

**Disk inspection:**
- Path: `data/exp_counterfactual_replay_latency_delta_stack_v2_single_intervention/metrics.json`
- mtime: 2026-06-28 03:17 EDT (fresh re-write)
- **`run_mode=smoke, n_seeds=2, N=2048, n_cycles=200`**
- BASELINE setup=11.497ms, DELTA_SHORT=2.103ms, AMORTIZED=2.104ms, ORACLE=0.004ms, RANDOM acc=0.000, speedup=5.47x

**Prior atom check (Store):**
- BATCH 13 atom EXISTS at this path:
  - ID: `T3/EXP_counterfactual_replay_latency_delta_stack_v2_single_intervention_MEASURED_MECHANISM_smoke_BASELINE_setup_11p497ms_...`
  - Tier: MEASURED_MECHANISM
  - `metrics_path: data/exp_counterfactual_replay_latency_delta_stack_v2_single_intervention/metrics.json`
  - `auto_promote_parent_REFUSED=True` (already established methodology refusal)
  - All MEASURED numbers identical to today's disk (BASELINE 11.497, DELTA 2.103, AMORTIZED 2.104, RANDOM 0.0, etc.)

**Ruling:**
- **REFUSE re-atomization**: same data, same path, already atomized batch 13. No new evidence (still smoke, still 2 seeds).
- **REFUSE parent-promote**: parent `causal_counterfactual_replay_v1` is a legacy ARCHIVE/PRE_SUBSTRATE_BUILD atom (DECISION_237 schema). Parent v1 disk: 1 seed, intervention_ms=16.864ms. v2 baseline (11.497ms full-rewrite) is a DIFFERENT code path from parent v1 baseline (16.864ms do-operator). v2 cannot retroactively satisfy parent v1's HP latency target. Parent-promote requires re-running parent v1 EXACT config with 2+ seeds and demonstrating < 10ms.

**No atom written. No ledger row.**

### ATOM 1 (this batch): CF regret-comparison vmPFC v1 -- CHAIN_GRADE

**Director claim:** "R2=0.987 rank=0.989 VMPFC_REGRET load-bearing"

**Disk inspection:**
- Path: `data/exp_counterfactual_regret_comparison_vmpfc_v1/metrics.json`
- mtime: 2026-06-28 03:17 EDT
- `run_mode=full, n_seeds=5 (seeds=[7,17,23,31,41]), N=8192, V_REL=256, 200 scenarios x 5 outcome-levels x 20 interferences`
- Per-arm means (verified off `per_arm` per-seed):
  - vmpfc_comparison: R2=0.987 (cv=0.0021), Spearman=0.989, value_leak=0.020, factual_recall=0.996
  - direct_diff: R2=0.987 (cv=0.0020)
  - no_regret_baseline: R2=-0.208 (cv=0.453) -- baseline-in-band [-0.35, 0.35]
  - random_vectors: R2=-0.157 (cv=0.225)
  - ground_truth_oracle: R2=1.000 (cv=0.000)
- Gap vmpfc-over-baseline: 1.195 (HP>=0.30 cleared 4x)
- CRLB round-trip OK across all 5 seeds
- arms_distinct_all_seeds=True (10 pairwise comparisons all disagree=1.0)
- cardinality_ok=True, suspect_1000=False
- ALL HP gates cleared (R2>=0.80, rank>=0.85, leak<=0.30, direct>=0.80, base_max<=0.20, gap>=0.30, oracle>=0.90)

**Verification:** numbers reproduce from per-arm per-seed; cv = std/mean per-arm matches metrics; gap arithmetic verified.

**Ruling: CHAIN_GRADE.** Per cert-ladder: 5-seed full, tight cv (0.002), 4-baseline discriminator clean, oracle within 0.013 (fair_baseline_ok), CRLB OK, cardinality OK. Cell anchor has NO prior atom (verified Store). Chain-grade is the appropriate tier; not by-construction-saturation (oracle 1.0 vs vmpfc 0.987 = legitimate gap).

### ATOM 2 (this batch): Schema exemplar-Bayes K20 -- CHAIN_GRADE (PROMOTE batch13 MM)

**Director claim:** "primary=0.714 lift_over_base=+0.443; confirms today's smoke"

**Disk inspection:**
- Path: `data/exp_cortex_schema_exemplar_bayes_importance_sample_v1/metrics.json` (NOT `_smoke` suffix)
- mtime: 2026-06-28 03:17 EDT
- `run_mode=full, n_seeds_complete=5 (seeds=[7,17,23,31,41]), N=2048, VSLOT=8, MSLOTS=6, KSCH=8, NEX=20, FN=0.20, MF=0.50, BETA=8.0, N_MASKED=3, K_VARIANTS=(5,20,50)`
- expected_n_units=72000, completed (events_per_arm_total)=12000 per arm x 6 arms = 72000. cardinality_ok=True.
- Per-arm recall (verified from `per_arm_recall_summary.per_seed` arrays):
  - ARM_K_NEAREST_K20 (PRIMARY): mean=0.714 cv=0.025 (per-seed: 0.724, 0.713, 0.728, 0.725, 0.680)
  - ARM_NO_SCHEMA_BASELINE: mean=0.271 cv=0.108
  - ARM_RANDOM_K_EXEMPLARS: mean=0.244 cv=0.087
  - ARM_K_NEAREST_K5: 0.642 cv=0.024
  - ARM_K_NEAREST_K50: 0.715 cv=0.022
  - ARM_ORACLE_TRUE_SCHEMA: 0.801 cv=0.010
- HP cleared: primary=0.714 >= 0.50; lift_base=+0.443 >= 0.30; lift_rand=+0.470 >= 0.30; cv=0.025 < 0.15.

**Prior atom check (Store):**
- BATCH 13 atom exists at `data/exp_cortex_schema_exemplar_bayes_importance_sample_v1_smoke/metrics.json` (note `_smoke` suffix; DIFFERENT path from today's full)
- Batch 13 atom: smoke, n_seeds=3, primary=0.728, cv=0.015, MEASURED_MECHANISM

**Verification:** today's metrics path is `_v1/metrics.json` (no `_smoke` suffix); n_seeds=5 not 3; run_mode=full not smoke. Legitimate full-N landing.

**Ruling: CHAIN_GRADE.** PROMOTE the batch 13 MEASURED_MECHANISM atom to chain-grade. Batch 13 atom REMAINS in Store as smoke-tier evidence; this atom is the full-tier promote. New atom written; batch 13 atom NOT modified (Skunkworks discipline: never mutate prior atoms; append new tiering).

### ATOM (REFUSED): Online conv oneshot TV+hippo -- "HONEST_NEG hippo binding broken"

**Director claim:** "TV_HIPPO=0.000 vs TV_ONLY=1.000; hippo binding broken in composition; HONEST_NEG"

**Disk inspection:**
- Path: `data/exp_online_conv_oneshot_taskvec_hippo_v1_smoke/metrics.json`
- run_mode=smoke, n_seeds=2 (seeds=[7,17])
- Per-arm:
  - VANILLA_RETRIEVAL: acc=0.000 (n=30; OK)
  - TASKVEC_ONLY: acc=1.000 (n=30; OK)
  - **TASKVEC_PLUS_HIPPO: acc=NaN, n_scenarios=0, arm_status="ERROR: ValueError: kth(=64) out of bounds (60)"** for BOTH seeds
  - ORACLE: acc=1.000 (n=30; OK)
  - RANDOM_INJECT: acc=0.017 (n=30; OK)
- **cardinality_ok=False (240/300; missing the 60 TV+HIPPO scenarios entirely)**
- Config: refuse_V_REL=64, V=60 -- the bug: kth (64) > vocab size (60); refuse-gate parameter mismatch with vocab.

**Ruling: REFUSE HONEST_NEG.** This is a CODE BUG (refuse-gate kth > vocab size for both seeds), not a substrate honest-negative finding. Filing HONEST_NEG would conflate infra-bug with negative result. The arm did NOT run; its acc=0.000 in summary is misleading (real value is NaN). HONEST_NEG requires a clean negative result from a regime where the mechanism HAD a fair opportunity to fire. Here the mechanism never executed.

**Required cell-author fix:** parameter mismatch refuse_V_REL=64 vs V=60. Either raise V or lower refuse_V_REL. Re-dispatch.

**No atom written. No ledger row.** HARD_FAIL_INFRASTRUCTURE flag for cell-author.

### ATOM 3 (this batch): Narrative coherence 100-event -- MEASURED_MECHANISM

**Director claim:** "Q1 factual=0.889 + Q4 contradiction=1.000 chain-grade quality on 100-event narrative; Q2 coref=0.222 + Q3 temporal=0.111 collapse"

**Disk inspection:**
- Path: `data/exp_stage3_narrative_coherence_100event_5char_full_stack_v1/metrics.json`
- verdict=HARD_FAIL (correctly; min_per_q_FULL=0.1111 < HF_per_q=0.30)
- `run_mode=full, n_seeds=3 (seeds=[11,13,19]), N_h=512, N_c=1024, N_part=1024, N_events=100, N_chars=5, K_scene=10, K_active=51`
- Per-arm overall accuracy (mean):
  - ARM_FORGET_EVERYTHING: 0.250
  - ARM_FLAT_BASELINE: 0.361
  - **ARM_NO_SEGMENT: 0.556**
  - **ARM_FULL_STACK: 0.556** (PRIMARY)
- FULL_STACK per-query: Q1=0.889 (factual), Q2=0.222 (coref), Q3=0.111 (temporal), Q4=1.000 (contradict)
- **arms_distinct_pairs ARM_NO_SEGMENT_vs_ARM_FULL_STACK = FALSE** -- predicted_sha16 IDENTICAL per seed (seed11=a87cf909244f154b, seed13=121a3a6f3baef49d, seed19=24c843e49663a82d)

**Ruling: MEASURED_MECHANISM.** Two load-bearing findings:
1. Q1+Q4 substrate-quality at 100-event scale (substrate composition handles factual + contradiction at chain-grade-quality without explicit segmentation)
2. **NO_SEGMENT TIES FULL_STACK** -- segmentation primitive NOT load-bearing; substrate-already-does-X 8th occurrence today (feeds META_RULE_AM ATOM 6)

Director's framing "Q1+Q4 chain-grade quality MM" is correct; this audit augments with the segmentation-null finding.

### ATOM 4 (this batch): SWR preplay constructive hypothesis-generator -- MEASURED_MECHANISM

**Director claim:** "FULL HARD_FAIL but generator works MM; recall@10=0.558 novelty=1.000 lift +0.558; pipeline_top1=0.108 = downstream scorer weakness"

**Disk inspection:**
- Path: `data/exp_swr_preplay_constructive_hypothesis_generator_v1/metrics.json`
- verdict=HARD_FAIL (correctly; HF pipeline_top1<0.15 triggered at 0.108)
- `run_mode=full, n_seeds=5, N=8192, V_BANK=256, K_CANDS=10, N_PROBLEMS=200`
- cardinality_ok=True (60000/60000)
- Per-arm (verified per-seed):
  - BASELINE_OBSERVATION_ECHO: recall=0.000 nov=0.000
  - BASELINE_RANDOM_DRAW: recall=0.000 nov=1.000
  - MEMORY_PARROT: recall=0.000 nov=0.000
  - **PREPLAY_FULL: recall=0.558 cv=0.035 nov=1.000 div=0.074**
  - GEN_SCORE_PIPELINE: recall=0.573 cv=0.044 nov=1.000 div=0.077 pipeline_top1=0.108
  - DIAG_PREPLAY_DIVERSITY: recall=0.568 cv=0.070 nov=1.000
- HP cleared (recall-layer): novelty>=0.80, lift_echo>=0.25, lift_rand>=0.40, diversity<=0.70, cv<0.15, parrot_nov<0.05, arms_distinct.
- HP failed (recall>=0.65, pipeline>=0.50); HF triggered (pipeline<0.15).

**Ruling: MEASURED_MECHANISM.** Director's framing is correct. Generator-layer is substrate-quality (3 generator-arms recall ~0.56-0.57 vs 3 baselines recall 0.000); pipeline-layer scorer is the bottleneck (pipeline_top1=0.108). MM preserves both layers cleanly.

### ATOM 5 (this batch): Boundary detector -- MEASURED_MECHANISM (by-construction-saturation)

**Director claim:** "FULL MIDDLE_BAND saturated mechanism MM; cs_f1=1.0 ties oracle=1.0 at drill regime; lift +0.4464"

**Disk inspection:**
- Path: `data/exp_stage3_narrative_event_boundary_detector_only_v1/metrics.json`
- verdict=MIDDLE_BAND (cell-author flagged saturated_mechanism_ties_oracle)
- `run_mode=full, n_seeds=3 (seeds=[11,13,19]), N=1024, N_EVENTS=100, WITHIN_DRIFT=0.10, BOUNDARY_FLIP=0.45, TOL=2`
- Per-arm boundary_f1:
  - RANDOM_BOUNDARIES: 0.357 (mean across 3 seeds)
  - FIXED_BUDGET: 0.554
  - **COSINE_SHIFT: 1.000 (cv=0.000) <-- PRIMARY**
  - **ORACLE_CEILING: 1.000 (cv=0.000)**
- arms_distinct_pairs COSINE_vs_ORACLE = **FALSE** (predicted_sha16 IDENTICAL per seed)
- lift_cosine_shift_over_fixed_budget=0.446; over_random=0.643
- theta_calibrated 0.703-0.707; calib_median 0.797-0.801; calib_mad ~0.012 (SNR ~22x noise estimate from cell-author)

**Ruling: MEASURED_MECHANISM.** By-construction-saturation rule fires (Fix #28; cosine_shift ties oracle at drill regime). Director's framing is correct. Cross-link to ATOM 3 (narrative coherence): both atoms inform substrate-already-does-X (ATOM 6 META_RULE_AM).

### ATOM 6 (this batch): META_RULE_AM substrate-already-does-X -- META atom

**Source:** `notes/research_synthesis_overnight_substrate_already_does_X_pattern_2026-06-27.md` (Research synthesis, 8 occurrences enumerated)

**Pattern:** substrate's existing chain-grade primitives (cosine cleanup / flat preplay / explicit encoding / TRACE / partition / refuse-gate) pre-encode capabilities that proposed "richer brain-grounded mechanisms" propose to add. Richer mechanisms TIE or LOSE to substrate-primitive baselines at default regimes.

**Process discipline (mandatory pre-reg additions for richer-mechanism cells):**
1. Substrate-existing-primitive arm in the SAME cell as richer mechanism
2. Discriminating regime specified where primitive hypothesized to fail
3. SUBSTRATE_PRIMITIVE arm with same parameters as RICHER_MECHANISM arm (cross-arm parity; BIAS-Q)
4. If substrate primitive ties richer mechanism within margin (lift < 0.05), verdict is MEASURED_MECHANISM (informative-null), not HARD_FAIL

**Extends META_RULE_AL** (batch 13) from substrate-cosine-kernel layer to process-discipline layer.

**Cross-link atoms today:**
- Batch 13 atom 3 (cortex_schema_instantiation_context_prior_v1; Occurrence 1-3 of pattern)
- Batch 14 atom 3 (narrative_coherence; NO_SEGMENT ties FULL_STACK = Occurrence 7)
- Batch 14 atom 5 (boundary_detector; COSINE_SHIFT ties ORACLE at drill = Occurrence 8)

---

## NET RESULT

- **CERT N: 626 -> 628 (delta +2 chain-grade)**
- **Store atoms: 177495 -> 177501 (delta +6: 2 chain-grade + 3 MM + 1 META)**
- **Ledger rows appended: 6**

**REFUSALS (no atoms; no ledger rows):**
- CF Cell 2 v2 single-intervention "FULL HARD_PASS" (Director-framing-error #8)
- Online conv hippo "HONEST_NEG" (Director-framing-error #9; HARD_FAIL_INFRASTRUCTURE)

**Director-framing-errors caught cumulative today: 9 (7 prior + 2 batch 14).**

**Commit hash:** filled in by git after apply.

---

## DISCIPLINE NOTES (for next batches)

- **CF Cell 2 v2 cell-author**: dispatch a PARENT-REDISPATCH cell that re-runs `causal_counterfactual_replay_v1` EXACT config with 2+ seeds and verifies < 10ms intervention latency. Only then can parent v1 be legitimately promoted. v2 evidence does not transfer (different baseline arm).
- **Online conv hippo cell-author**: fix refuse_V_REL=64 > V=60 mismatch (raise V to >= 64 OR lower refuse_V_REL). Re-dispatch as v1_smoke_v2.
- **META_RULE_AM**: applies retroactively to next batch dispatch. Director should self-check: any "richer mechanism" cell needs substrate-primitive arm in same cell + discriminating regime specified.

-- Skunkworks (cert-owner / auditor) -- 2026-06-28
