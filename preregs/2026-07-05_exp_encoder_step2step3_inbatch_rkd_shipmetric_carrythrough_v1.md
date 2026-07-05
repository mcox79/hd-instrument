# Prereg: exp_encoder_step2step3_inbatch_rkd_shipmetric_carrythrough_v1

**Date:** 2026-07-05
**Author:** exp_dev (cell author / prover)
**Cell:** `experiments/exp_encoder_step2step3_inbatch_rkd_shipmetric_carrythrough_v1_core.py`
**Hand-off:** `notes/exp_dev_handoff_research_encoder_perception_shipmetric_carrythrough_2026-07-05.md`
**Research scope:** `notes/research_encoder_perception_state_buried_win_shipmetric_carrythrough_2026-07-05.md`

## What / why

Carry the BURIED in-batch-RKD-only WIN of `step1b_v3c` through Step2 (sparse-
encode) and Step3 (ship-metric gold-verify), dropping the algebra-breaking
GLOBAL co-arm. The winning arm is verified off-disk (5 seeds):

- INBATCH_BLOCK spearman-to-teacher mean 0.886 [0.852, 0.897]
  MEASURED@data/exp_encoder_migration_step1b_v3c_paired_rkd_only_seed_{7,13,23,29,31}/metrics.json:per_unit[INBATCH_BLOCK].spearman_all
- INBATCH_BLOCK keyed_roundtrip@J5 = 1.000 all 5 seeds (algebra INTACT)
  MEASURED@ same :per_unit[keyed::INBATCH_BLOCK::J5].acc_at1
- INBATCH_BLOCK hi80_cos (cosine on teacher-highly-similar pairs) mean 0.827 [0.786, 0.861]
  MEASURED@ same :per_unit[INBATCH_BLOCK].hi80_cos
- INBATCH_BLOCK ret_agree10 mean 0.221 [0.184, 0.266]
  MEASURED@ same :per_unit[INBATCH_BLOCK].ret_agree10

No surviving checkpoint (v3c FULL ran on remote cuda; artifacts not local),
so this cell RETRAINS the cheapest arm (in-batch RKD, no landmark, no InfoNCE)
via the proven v3c training loop verbatim (`v3c._train_student_full`,
objective="in_batch", nce_weight=0.0) -- SAME code path that produced the win.

## Ship-metric definition (exp_dev decision -- FLAGGED)

The existing Step2/Step3 chain is wired to the ORTHOGRAPHIC char-positional
encoder (Step3 ARM_CONCEPT = CharPositionalEncoder + top-K WTA, encodes raw
query STRINGS). The in-batch-RKD winner is a BGE-embedding(1024d) -> MLP ->
block-STE student; its input space is a BGE embedding, incompatible with
Step3's string-query pipeline without live BGE inference. This cell therefore
measures a self-contained, teacher-anchored ship metric on the held concept
set (which has cached BGE embeddings):

- `cosine_to_gold` := INBATCH_BLOCK `hi80_cos` (mean code cosine on concept-
  pairs the BGE teacher rates teacher_cos>=0.80; "for the right answers, how
  high is the code cosine").
- `ret_agree10` := INBATCH_BLOCK top-10 retrieval overlap vs the BGE teacher.
- `composed_roundtrip` := INBATCH_BLOCK SBC keyed bind/unbind roundtrip at a
  harder composed load J_COMPOSED (>J=5, the load the buried win reported).

A live-BGE real-query variant (BGE-encode the 100 gold queries -> MLP -> code
-> retrieve against BGE-cached KB codes) is the strictly-more-faithful FUTURE
test; out of scope for this cheap carry-through.

## Bands (JOINT gate; HARD-PASS requires ALL THREE)

| Metric | HARD-PASS | MIDDLE_BAND | HARD-FAIL |
|---|---|---|---|
| cosine_to_gold (INBATCH_BLOCK hi80_cos) | >= 0.80 | [0.60, 0.80) | < 0.60 |
| composed_roundtrip (INBATCH_BLOCK keyed@J_COMPOSED) | >= 0.95 | [0.85, 0.95) | < 0.85 |
| ret_agree10 (INBATCH_BLOCK vs teacher) | >= 0.30 | -- | -- (joint) |

HARD-PASS iff (cosine_to_gold >= 0.80 AND composed_roundtrip >= 0.95 AND
ret_agree10 >= 0.30 AND baseline_in_band). HARD-FAIL iff (cosine_to_gold < 0.60
OR composed_roundtrip < 0.85). Else MIDDLE_BAND. All thresholds
HYPOTHESIZED@hand-off contract.

## Honest forecast (MEASURED off the buried win's own held-pair numbers)

cosine_to_gold 0.827 STRADDLES 0.80 (3/5 seeds clear); algebra 1.000 (clears);
ret_agree10 0.221 MISSES 0.30 on all 5 seeds. **Forecast: MIDDLE_BAND** at
FULL, localizing the proxy-to-real gap to top-10 retrieval agreement (strong
rank-spearman does not imply strong top-10 retrieval). Genuine actionable
outcome, not a reason to abort. `P_deflated = 0.42` for the headline HARD-PASS
band (CITED@research note; lit-scan-calibrated).

## Integrity gates (both modes)

- RANDOM_BLOCK keyed@J5 >= 0.98 (SBC-lossless prior; algebra machinery, training-independent).
- shuffled-key INBATCH_BLOCK@J5 <= 0.05 (no leak; discriminator valid).
- baseline_in_band: CHARPOS ret_agree10 in (0.05, 0.95).
- arms_differ: INBATCH_BLOCK / CHARPOS / RANDOM_BLOCK sha256 distinct.

## SCHEMA-VET fields

- `arms_differ_verified: true` (sha256 over the 3 code matrices).
- `final_metrics_atomicity: tmp_replace` (write_metrics + E_concept.pt os.replace).
- `crlb_floor_computed: 0.901` at K=128 (THEORETICAL@v2/v3 prereg; unchanged channel). `discriminator_reachability: true` (0.80 < 0.901).
- `baseline_in_band: true` (checked at smoke).
- `cardinality_ok`: EXPECTED_N_UNITS = 8 (semantic x4 + keyed x4); verdict counts per_unit.
- `calibration_check: default_ok_for_this_regime` (identical hyperparams to v3c INBATCH arm).
- `cell_chunked: false` (single-seed; FULL multi-seed via re-dispatch of --seed 7/13/23/29/31).
- `start_marker_written / crash_diagnostic_present / heartbeat_present: true`.
- `progress_logging: print_flush_true` (line-buffered stdout + flush=True; FULL timeout >= 1800s).
- `discriminator-survives-scale`: option (B) analytical. Ship discriminator is a FULL-only question (smoke V too small to reproduce the retrieval-agreement regime); the discriminator is in a MEASURABLE non-saturated band by construction (held-pair 0.827/0.221). Smoke fires the ALGEBRA discriminator via by-construction SBC-lossless pos-ctrl + shuffled-key leak control.

### Section 15 composition/sweep gates
- `sweep_alignment_verdict: N/A` (no parameter sweep axis).
- `discriminating_fraction: N/A` (no sweep; single-config carry-through).
- `composition_edges`: BGE-teacher-embedding(1024d) -> MLP student -> block-STE code (SHAPE_MATCH, the v3c-proven edge); block-code -> sparse-CSR (SHAPE_MATCH, lossless int8); block-code -> SBC keyed bind/unbind (SHAPE_MATCH, native SBC algebra). No SHAPE_MISMATCH.
- `positive_control_arms`: RANDOM_BLOCK keyed@J5 reproduces the SBC-lossless prior (>=0.98) AT the test regime; INBATCH training reproduces the v3c INBATCH objective verbatim (same loop, cited prior spearman 0.886). tolerance 0.10 on the reproduced spearman at FULL.
- `functional_requirements`: (1) preserve teacher similarity geometry -> in-batch RKD distillation (chain-grade in v3c INBATCH arm); (2) sparse composable code -> block-STE + SBC keyed bind/unbind (chain-grade); (3) valid retrievable artifact -> sparse-CSR (Step2 lossless converter).

## Compute architecture

Class **(c) mixed with justification**. Training is sequential-by-step (Adam
over 1800 steps; genuine sequential dependency) on GPU tensors (batched matmul
per step); encode + semantic-eval + keyed cleanup are batched-GPU (matmul-heavy,
chunked). Storage strategy: **sharded** (each concept its own block code;
retrieval + keyed algebra are per-item, never a global bundle) -- correct per
the composition-depth physics law. FULL is GPU (heavy: retrain + 400K-pair eval
+ keyed cleanup over ~17790 held codes).

## Dispatch

- SMOKE: `local_cpu_queue` (SMOKE-ONLY on local per USER lock). LANDED HARD_PASS.
- FULL: GPU (`overnight_queue`), staged for Orchestrator (exp_dev cannot push).
  Recommend seeds {7,13,23,29,31} (match v3c) as separate re-dispatches of
  `--seed`. Recommended timeout 3600s/seed (v3b 10-arm battery = 663s at this
  regime; this cell is 1 arm + eval, ample margin). `--run-mode full`.

## Smoke result (LANDED)

`data/exp_encoder_step2step3_inbatch_rkd_shipmetric_carrythrough_v1_smoke/metrics.json`
verdict=HARD_PASS (SMOKE_MACHINERY_OK), run_mode=smoke, 8/8 units, 62.2s CPU.
Machinery + all discriminators fire: RANDOM_BLOCK keyed@J5=1.0, shuffled leak
0.0, CHARPOS baseline ret_agree10=0.191 in band, INBATCH beats baseline by
+0.143, sparse-CSR roundtrip 0/100 mismatch. (Smoke ship numbers 0.855/0.333
are at tiny V=400 held and are NOT a FULL forecast -- retrieval is easier at
small V; FULL forecast remains ~0.827/0.221 per the buried win's larger held
set.)
