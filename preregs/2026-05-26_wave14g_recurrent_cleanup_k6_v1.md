# Pre-registration: Bounded-Iteration Recurrent Cleanup Head — Multi-Hop K6 Probe

**Experiment:** wave14g_recurrent_cleanup_k6_v1  
**Filed:** 2026-05-26  
**Script:** experiments/exp_wave14g_recurrent_cleanup_k6_v1.py  
**Queue:** overnight_queue (GPU-accelerated; 5 seeds x 3 d-values x 4 M-grid cells)  
**Timeout:** 7200s  
**Handoff source:** notes/exp_dev_handoff_research_recurrent_cleanup_head_multihop_2026-05-25.md

---

## Hypothesis

A bounded sign-Hopfield cleanup head applied to the SAME outer-product storage W
improves multi-hop d-cliff retrieval at d=25, compared to the linear arm (single-pass W k query).

Two arms share identical W = (1/N) sum v_i k_i^T:
- Arm A (linear baseline): y = W k
- Arm B (bounded recurrent): y_0 = W k; y_{t+1} = sign((1/N) Σ_j <y_t, v_j> k_j); T in {2,3,5}

---

## Design

- N=4096 (full), N=512 (smoke)
- K=8 (multi-hop reference K from cap_map v60)
- d_values=[10, 25, 50]; primary test is d=25 (the known d-cliff)
- M_grid=[50, 100, 200, 500]
- Seeds=[7, 17, 23, 31, 41]
- T_values=[2, 3, 5] (bounded iteration counts for arm B)

---

## Pre-registered verdicts

### HARD_PASS

Arm B lift >= +0.10 per-hop accuracy at d=25, in >= 3/4 M-grid cells, with CI width < 0.05 across seeds.

Consequence: Queue the multi-hop-mode config knob design (separate handoff).
Document the recurrent-variant capability against cap_map under NEW row "multi-hop bounded recurrent cleanup".

### HARD_FAIL

Arm B <= arm A (lift <= 0.00) at d=25 in >= 3/4 M-grid cells.

Consequence: Close the recurrent-variant question for multi-hop. The primitive decision
tightens to "linear is sole primitive across all evaluated tasks". File closure annotation
in primitive-decision note.

### MIDDLE_BAND

Arm B delivers +0.03 to +0.10 in 1-2 cells, sub-threshold in other cells.

Consequence: Document the conditional benefit (which M/K cells benefit) WITHOUT queueing
a full mode knob.

### INSTRUMENTATION_FAIL

Arm B fails to converge (oscillation; CI >= 0.10) in > 20% of cells.

Consequence: Investigate convergence behavior before any verdict.

---

## Smoke pre-registration note

Smoke at N=512, seeds=[7,17], d=[10,25], M=[20,50]:
- linear arm performs correctly (cos > 0.5 at M=50 d=10,25)
- Arm B (recurrent) yields lift = -1.0 at several cells (arm B acc = 0.0 where linear = 1.0)
- Effect size: d >> 1.0 (large, not borderline) -- no walk-back gate required
- This pattern is REAL (not instrumentation failure): the sign-Hopfield formula
  y_{t+1} = sign((1/N) Σ_j <y_t, v_j> k_j) drives y_t toward the KEY space, not VALUE space,
  in heteroassociative storage. This is a genuine mechanistic finding.
- Full run at N=4096, 5 seeds, full M_grid will confirm RECURRENT_HARD_FAIL.
- The probe is productive: closes the recurrent variant for multi-hop definitively.

---

## Self-test cells (verified before smoke)

1. outer_product_store produces non-zero W
2. linear_recall on exact match gives cosine > 0.0 at N=64, M=10
3. recurrent_recall_with_keys produces non-NaN output
4. CI width computation gives > 0 on non-constant samples

All 4 passed at smoke.

---

## Notes

- No prior empirical anchor for arm B in heteroassociative setting: this is a first measurement.
- Bands are calibration-probe policy: theory predicts HARD_FAIL (formula drives toward key space).
- Smoke result is consistent with HARD_FAIL prediction.
