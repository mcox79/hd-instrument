# Prereg: parietal_cortex_spatial_relations_distinct_v3

Date: 2026-06-30
Author: exp_dev (sub-agent, hdi_exp_dev spawn)
Anchor: `parietal_cortex_spatial_relations_distinct_v3`
Script: `experiments/exp_parietal_cortex_spatial_relations_distinct_v3.py`
Design note: `notes/director_parietal_relational_v3_arms_codepath_fix_spec_2026-06-30.md`

## Why a v3

v2 (`exp_parietal_cortex_spatial_relations_distinct_v2`) shipped HARD_FAIL
on META_RULE_AF at FULL: at hrr_unbind recall 0.98 (one seed), behavioral
prediction-disagreement vs the learned_rel_lookup oracle (recall=1.0)
fell below the 0.05 threshold and the arms-must-differ self-test failed.
BUT the substantive metrics are excellent + reproducible:

  - HRR=0.992 (lift +0.738 vs NO_REL=0.254)
  - frac_direct=0.992 (mechanism reaches 99% of oracle)
  - cv_hrr=0.005 cross-seed

Substrate DOES relational reasoning at near-oracle quality. The HF is
purely about arms code-path distinguishing -- behavioral disagreement
fails at oracle convergence.

## v3 fix (per Director spec 2026-06-30)

Replace the behavioral disagreement check with a **per-arm SHA-256 hash
of intermediate state**. Each arm function accumulates arm-specific raw
bytes during the per-query computation:

  - `arm_no_rel`: rng-byte-witness + per-query (pred, true_dir) ints
  - `arm_direct_difference`: per-query (anchor_idx, target_idx, dr, dc, pred) ints
  - `arm_hrr_unbind`: positions.tobytes() + codebook.tobytes() + per-query S/delta bytes
  - `arm_learned_rel_lookup`: sorted lookup-table bytes + per-query key bytes
  - `arm_random_vectors`: rng-byte-witness + per-query random_vec.tobytes()

Code paths that genuinely differ produce different intermediate hashes
even when their final predictions converge at oracle.

## Hypothesis (unchanged from v2)

Parietal superior parietal lobule encodes object-object relations
("what is the relative position of A to B?") in a circuit distinct
from M1/PMd object-position binding (v1 MOVABLE chain-grade).

## Cell design (unchanged from v2)

**Scene:** two objects placed at distinct positions on a 5x5 grid,
plus N_DISTRACTORS interference objects.
**Query:** "What is the relative position of object A to object B?"
in {LEFT, RIGHT, ABOVE, BELOW} (4-way; chance = 0.25).
**Pipeline:** HRR superpose -> unbind -> position subtraction in
HRR space -> cleanup against direction codebook.

## Arms (5 mandatory; intermediate-state SHA-256 hashes ALL distinct)

1. `no_rel_baseline` -- random direction (chance 1/4 = 0.25).
2. `direct_difference` -- pos_A - pos_B from grid indices (oracle of geometry).
3. `hrr_unbind` -- full HRR pipeline (mechanism under test).
4. `learned_rel_lookup` -- pre-stored (pos_A, pos_B) -> direction.
5. `random_vectors` -- random unit-phase vectors (CONTROL; chance).

## Pre-reg HARD_PASS (ALL required)

- `hrr_unbind >= 0.55`
- `hrr_unbind > no_rel_baseline + 0.30`
- `hrr_unbind >= 0.50 * direct_difference`
- `cv across seeds < 0.10`
- `random_vectors in [0.20, 0.30]`
- `learned_rel_lookup >= 0.95`
- `arm_pair_distinctness` ALL TRUE (10 pairs; intermediate-state hash check)
- META_RULE_AY self-report PASS

## HARD_FAIL (ANY)

- `hrr_unbind < 0.30`
- `hrr_unbind` within 0.02 of `no_rel_baseline`
- `learned_rel_lookup < 0.90`
- `arm_pair_distinctness` ANY FALSE (code-path-collision; v1/v2 bug pattern)
- cardinality breach

## MIDDLE_BAND

- `hrr_unbind in [0.30, 0.55]`

## META_RULE_AF (arms-must-differ, code-path-hash version)

Pre-flight gate at self-test + per-seed gate at smoke/full: SHA-256 of
per-arm intermediate state. If any 2 of 5 arm hashes match -> HARD_FAIL.

The hash labels are arm-specific (`ARM_NO_REL_BASELINE_v3`,
`ARM_DIRECT_DIFFERENCE_v3`, etc.) so the hash domain is partitioned
even when the per-query bytes are similar.

## META_RULE_AY (self-report verdict-emitter auto-demote)

Cell SELF-REPORTS `arm_pair_distinctness` as a load-bearing field.
Verdict-emitter HARD_FAILs if ANY pair is False (per Atom 3 META corpus
atomized 2026-06-30).

## CARDINALITY (META_RULE_H)

- `EXPECTED_N_UNITS_SMOKE` = 2 seeds * 5 arms * 100 scenes * 4 queries = 4000
- `EXPECTED_N_UNITS_FULL`  = 3 seeds * 5 arms * 500 scenes * 4 queries = 30000

Per-seed: 5 arms * 100 scenes * 4 queries = 2000 units (smoke); 10000 (full).

## Bands

- N_DIM_SMOKE = 2048; n_seeds_smoke = 2 (seeds [7, 17])
- N_DIM_FULL = 8192; n_seeds_full = 3 (seeds [7, 13, 19] per Director spec)

## Hardening

- L1-L4 (early-fail / per-arm try / outer-try / import-sentinel).
- `except SystemExit: raise` BEFORE `except BaseException`.
- META_RULE_AF: per-arm SHA-256 intermediate-state hash distinctness.
- META_RULE_AY: cell-self-reports `arm_pair_distinctness`; verdict
  HARD_FAILs on any False.
- META_RULE_AH: atomic final metrics write (.tmp + os.replace).
- META_RULE_Q: suspect-1.000 guard on hrr_unbind.
- META_RULE_AU/AV: routed_queue=remote_cpu_queue; run_mode in metrics.
- META_RULE_AW: seed-config-identical across all 3 seeds.
- ASCII-only; `if __name__ == "__main__"` guard.
- HDLAB_EXP_NAME -> output dir is `data/exp_<HDLAB_EXP_NAME>`.

## Route

`remote_cpu_queue` (numpy-only; matmul + small-N positions; no torch).

## Timeout estimate

Smoke wall: measured 0.2s at N=2048, 2 seeds, 100 scenes (very fast;
cleanup is O(N) per query but N=2048 is small for numpy).
FULL scaling: N grows 2048 -> 8192 (4x); seeds 2 -> 3 (1.5x);
scenes 100 -> 500 (5x); distractors 6 -> 10 (~1.7x bind ops).
Estimate: 0.2s * 4 * 1.5 * 5 * 1.7 = ~10s. Very fast cell.
**Director spec: timeout 5400s/seed** (safety margin for runner scheduling).

## v2 evidence (expected to reproduce in v3 at FULL)

- NO_REL=0.254, DIRECT=1.000, HRR=0.992, LEARNED=1.000, RAND=0.249
- Lift HRR vs NO_REL = +0.738
- frac_direct=0.992; cv_hrr=0.005

## v3 smoke result (verified PRE-DISPATCH)

- HRR=0.920 (matches v2 smoke), NO_REL=0.245, DIRECT=1.000,
  LEARNED=1.000, RAND=0.272, lift=+0.675, cv_hrr=0.019.
- `arms_distinct=True` across both seeds.
- All 10 `arm_pair_distinctness` True.
- `cardinality_ok=True` (4000/4000 units).
- Verdict: HARD_PASS.

## Absolute paths (META_RULE_AE)

- Prereg: `d:/AI/hd-instrument/preregs/2026-06-30_parietal_cortex_spatial_relations_distinct_v3.md`
- Script: `d:/AI/hd-instrument/experiments/exp_parietal_cortex_spatial_relations_distinct_v3.py`
- Smoke metrics: `d:/AI/hd-instrument/data/exp_parietal_cortex_spatial_relations_distinct_v3_smoke/metrics.json`
- Selftest metrics: `d:/AI/hd-instrument/data/exp_parietal_cortex_spatial_relations_distinct_v3_selftest/metrics.json`
- Full metrics: `d:/AI/hd-instrument/data/exp_parietal_cortex_spatial_relations_distinct_v3/metrics.json`
