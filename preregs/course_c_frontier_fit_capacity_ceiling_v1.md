# Pre-reg: course_c_frontier_fit_capacity_ceiling_v1

Date: 2026-07-11. Author: exp_dev. Cell: `experiments/exp_course_c_frontier_fit_capacity_ceiling_v1.py`.
Routing: **overnight_queue (GPU)**. Seed: 7 (single-seed capacity-ceiling diagnostic).

## Question / escalate-to-strategy fork

The oracle-capacity-ladder (`course_c_oracle_capacity_ladder_v1`) landed **LADDER_FIT_LIMITED**: the transductive
DIRECT-readout ORACLE climbs monotonically with capacity
(L0 h@10=0.140 -> L5 anchor1 k32/d8192 h@10=0.424 MEASURED@data/exp_course_c_oracle_capacity_ladder_v1/metrics.json:ladder)
and was **still climbing at the top rung**, while the FPE readout was flat ~0.000 (a bandwidth-underflow bug).
This cell resolves the fork the ladder left open:

> Does the transductive DIRECT-readout ORACLE EVER fire (hits@10 -> 0.90) with enough FIT capacity, or does it
> PLATEAU = a genuine representation wall (additive/translational TransE functional form insufficient for the
> SYNONYM/IS_A CSKG relation mix at N=25752)?

COMPLEMENTARY to the in-flight `course_c_strengthened_fit_recipe_extended_ladder_v1` (isolates WHICH lever at
MODERATE capacity, tops k48/ep450/dim8192). THIS cell pushes the CEILING far higher: a 16x coordinate-capacity
sweep (k 32 -> 512), RotatE-comparable epochs, LR-fix, n_neg -> 256.

## Compute architecture

class: (c) MIXED. Symbolic CSKG assembly + degree map = sequential-CPU (one assembly reused across all rungs ->
memory FLAT). Coord fit = vectorized minibatch SGD (torch, device-parameterized -- GPU-batching mandate
satisfied, NOT a numpy Python loop). Readout = batched/query-chunked matmul. Storage strategy: **no_storage**
(KGE coordinate fit, not an associative-memory store). Single seed by design (capacity-CEILING diagnostic; the
PLATEAU verdict is a trajectory across many k, robust to a single seed -- the decisive 3-seed re-run is the
Branch-1 follow-on, not this cell).

**GPU feasibility (honest routing call):** `fit_kge_anchor1` (`experiments/_kge_anchor1_fit.py`) is fully
vectorized torch and threads `device` end-to-end (X/D/Adam/negatives/scoring all on `device`) -- it is NOT
numpy-bound and has a working GPU path. The frontier rungs (k up to 512, epochs up to 400) are a large number of
vectorized gradient steps; on CPU each rung would take many hours (the CPU ladder ran only to k32/ep2400 in
5414s). GPU is the honest routing to reach a HIGHER ceiling than CPU feasibly can, and it feeds the idle card.

## STRICT OOM DISCIPLINE (this family OOM'd 3x)

- **Peak drivers bounded + stated:**
  - Fit negative tensor `(batch, n_neg, k)` fp32 -> **adaptive batch** (`_adaptive_batch`) keeps the forward
    footprint <= `NEG_TENSOR_BUDGET_BYTES=1.0e9` (~2GB with autograd) at EVERY rung. At k512/n_neg256 batch
    falls to ~1907; at k256/n_neg256 ~3814; at k64/n_neg128 clamped to MAX_BATCH=8192.
  - FPE candidate encoding `S_all=(N, dim)` complex64 -> `dim` **CAPPED at 8192** (1.69GB; freed between the two
    FPE readouts). This is the reason FPE dim is NOT pushed higher: it is DIAGNOSTIC-only (the fire gate is the
    DIRECT readout, which uses only the k coordinates), so pushing dim buys the ceiling question nothing and only
    risks OOM (3.4GB at 16384).
- **NEVER materializes [N x N]** (25.7k x 25.7k = 2.6GB fp32 avoided): all scoring is (nq=500, N) query-chunked at
  chunk=256 -> 26MB tiles moved to CPU and freed.
- **Peak estimate at the biggest rung (k512, dim8192):** ~1.69GB (FPE) + fit tensors (~160MB) < 2GB, well under
  the 6GB ship ceiling on the 8GB card.
- **PER-RUNG ATOMIC CHECKPOINT:** `metrics.json` is atomically re-written (tmp + os.replace) after EVERY rung, so
  a queue-timeout hard-kill preserves all completed rungs (verdict degrades gracefully over whatever landed).
- **INTERNAL wall-budget guard** (`INTERNAL_TOTAL_BUDGET_S=13000`): skips remaining rungs (recorded as
  `SKIPPED_INTERNAL_BUDGET`, never silent) if elapsed would risk a hard-kill before the atomic finalize.
- **MANDATORY >= 2-seed MEMORY smoke before FULL:** `--smoke` runs the frontier top-config (k512) at 2 seeds
  (7, 17) on the reduced CSKG slice so peak GPU allocation is exercised ACROSS seeds (catches the single-seed-
  masked OOM class) before the FULL is spent.

## Levers (highest-leverage first; per Branch-3 KGE-convergence lit-scan)

1. COORD capacity k (the DIRECT readout dim; demonstrated-strongest single lever, L4 k24 -> L5 k32 +0.052). Swept 32 -> 512.
2. EPOCHS / passes (RotatE ~376-472; ladder top only 150). Raised to 300-400.
3. LR fix (A1_LR=0.05 is ~1000x RotatE's ~5e-5). Fixed to 5e-3 on frontier rungs.
4. n_neg 64 -> 256 (RotatE FB15k-237 scale).

## Rungs (EXPECTED_N_UNITS = 5)

| label | k | fpe_dim | epochs | lr | n_neg | role |
|---|---|---|---|---|---|---|
| G0_repro_L5 | 32 | 8192 | 150 | 0.05 | 64 | Gate-D + positive control: reproduce ladder L5 direct=0.424 |
| G1_k64_ep300 | 64 | 8192 | 300 | 5e-3 | 128 | 2x coord capacity |
| G2_k128_ep300 | 128 | 8192 | 300 | 5e-3 | 256 | 4x coord capacity |
| G3_k256_ep400 | 256 | 8192 | 400 | 5e-3 | 256 | 8x coord capacity, RotatE-comparable epochs |
| G4_k512_ep400 | 512 | 8192 | 400 | 5e-3 | 256 | 16x coord capacity (ceiling rung; budget-guarded) |

`cardinality_ok`: verdict degrades gracefully over completed rungs (`n_rungs_completed` / `n_rungs_planned`
reported); a budget-skipped rung is recorded in `skipped_rungs` with `failure_class`, never silently dropped.
The FIRES-vs-PLATEAU read is defensible on k32->k256 alone (8x); k512 is the aspirational ceiling.

## Bands (verdict fork; gated on the WORKING DIRECT readout, un-confounded by the broken FPE)

**Integrity gates (take precedence):**
- `HARD_FAIL_CONTROL_METRIC_BROKEN` if RANDOM untrained control oracle_direct h@10 >= `RANDOM_CTRL_MAX=0.05`
  (metric leaking / structurally frozen-high).
- `HARD_FAIL_REGIME_OR_INVOCATION_MISMATCH` if `|G0_direct - L5_DIRECT_REF(0.424)| > GATE_D_TOL(0.10)` (Gate-D:
  the anchor1 invocation drifted from the ladder; frontier rungs suspect).

**Primary fork:**
- **FRONTIER_FIT_FIRES** (fit is REACHABLE with capacity): `oracle_direct h@10 >= 0.90` at SOME rung ->
  escalate-CAPACITY is the answer; license the Branch-1 decisive 3-seed re-run at the firing config (swap the
  decisive cell `fit_transe_coords -> fit_kge_anchor1` at the firing k/epochs).
- **FRONTIER_FIT_PLATEAU_REPRESENTATION_WALL** (representation wall): `oracle_direct` asymptotes below 0.90 (top
  frontier rung does NOT improve on the prior best by >= `PLATEAU_EPS=0.03`) despite the 16x coord-capacity jump,
  AND core dense (`core_avgdeg >= DENSE_AVGDEG=30`; the CSKG core is ~39.7, FB15k-237-comparable, so
  data-sparsity is ruled out) -> genuine FIT/REPRESENTATION wall; **escalate to STRATEGY: change the FUNCTIONAL
  FORM** (additive TransE poor fit for CSKG SYNONYM/IS_A mix, or genuine k-dim capacity ceiling). Do NOT keep
  cranking capacity.
- **FRONTIER_FIT_CLIMBING_UNDER_CAPACITY** (in-between): not fired, but the highest-capacity rung is still the
  best and improved >= PLATEAU_EPS on the prior -> capacity still buying accuracy at the tested ceiling; ONE more
  capacity rung MAY be warranted but that is a STRATEGY call (report trajectory; do NOT auto-escalate forever).

**Report:** the direct-hits-vs-capacity curve (`capacity_curve`: k, n_coord_params, oracle_direct_h10 per rung) +
per-rung degree-stratified DIRECT hits (LOW/MID/HIGH tail-degree tertile, weak-point localization) + the FPE
diagnostic (prereg ell=0.55 AND median-heuristic recalibration + health per rung).

## SCHEMA-VET fields

- `final_metrics_atomicity`: **tmp_replace** (write_metrics + os.replace; PLUS per-rung atomic checkpoint).
- `except SystemExit: raise` BEFORE `except Exception` (no BaseException / no bare except). Grep-verified clean.
- `start_marker_written`: true. `crash_diagnostic_present`: true (Exception -> CELL_CRASHED + traceback).
  `heartbeat_present`: true (`_heartbeat.jsonl` per rung). `defensive_error_checking`: passed_all_4_patterns.
- `cell_chunked`: false (single seed by design; the >=2-seed MEMORY smoke is the OOM gate, not a science multi-seed).
- `discriminator`: oracle_direct-fires (>=0.90) is the gate; RANDOM must-fail control fires (< 0.05); Gate-D G0
  reproduces ladder L5=0.424. No vacuous auto-pass (the RANDOM control REPRODUCES chance, proving calibration).
- `discriminator survives scale`: the discriminator IS a full-scale (N=25752) capacity sweep; there is no
  smaller-N smoke masking it. The FULL is run at production N; the ceiling question is only meaningful at scale.
- `baseline_in_band`: N/A as a saturating baseline; the RANDOM control (~0) and the ladder-anchored G0 (~0.42)
  bracket the measurable band, and the fire bar 0.90 sits above both -> the metric has full headroom to move.
- `crlb_n/a`: the fire threshold 0.90 is not a noise-floor CRLB; it is the pre-registered "reasoning question
  askable" bar from the ladder cell. Reachability is exactly the question this cell answers (FIRES vs PLATEAU) --
  not asserted a priori. RANDOM control proves the floor; G0 (=0.424 target) proves the metric reaches a
  non-trivial value, so 0.90 is not unreachable-by-construction (it is unreached-by-capacity iff PLATEAU fires).
- `calibration_check`: default_ok_for_this_regime -- FPE_ELL=0.55 is DELIBERATELY kept as the prereg diagnostic
  AND recalibrated via median-heuristic per rung (adaptive, logged, with health check); the fire gate does not
  depend on either FPE variant (it is the DIRECT readout).
- `arms_differ`: the rungs differ by construction (distinct k/epochs/lr/n_neg -> distinct fits + distinct scores);
  RANDOM control vs trained rungs are structurally different (untrained vs fit). No bit-identical-arm risk.
- `progress_logging`: **print_flush_true** (per-rung + per-fit flush; line-buffered stdout). timeout_s >= 1800.

## Validity preflight (DECLARED in self_test(); WARN-mode, ENFORCE-ready)

- **assert_positive_control_passes**: the transductive ORACLE (positive control) clears the self-test fire bar
  (direct h@10 >= 0.5 on the tiny clean functional graph). If the arm that SHOULD pass cannot, the bar is
  mis-directed.
- **assert_metric_moves**: DIRECT readout moves from RANDOM null (~0) to trained ORACLE; the median-heuristic FPE
  readout moves from 0 to a non-zero value (catches the exact-0.000 frozen-readout class).
- **assert_full_gates_exercised_at_selftest**: both FULL fail-closed gates (`random_control_mustfail`,
  `gate_d_regime_reproduce`) are exercised at tiny self-test scale.
- **assert_negative_control_fails_with_margin**: RANDOM control fails deterministically over 3 seeds (7,17,23)
  with margin 0.05 below the fire bar.

## Ship gate + dispatch plan

- Self-test: `--self-test` routes to `_run_selftest` (tiny synthetic, NO CSKG, seconds, exits 0/1). This is the
  ship gate (per no-local-smokes lock, executed on the remote runner, not locally).
- Memory smoke: `--smoke` (2-seed k512 top-config on reduced CSKG) on overnight_queue -> confirms GPU allocation
  across seeds before the FULL.
- FULL: overnight_queue (GPU), `--run-mode full`, seed 7. Timeout: 14400s (4h cap) -- justified by the 5-rung
  escalating-capacity ladder on GPU; the internal 13000s budget guard + per-rung atomic checkpoint guarantee a
  clean finalize under the hard timeout, and completed rungs survive even if G4 is budget-skipped.

## HYPOTHESIZED / MEASURED tags

- L5 direct h@10 = 0.424 MEASURED@data/exp_course_c_oracle_capacity_ladder_v1/metrics.json:ladder[5].oracle_direct_h10
- L5 elapsed = 1329.3s MEASURED@same:ladder[5].elapsed_s
- CSKG core avg-degree ~39.7 MEASURED@same:cskg_provenance.core_avgdeg
- FIRES vs PLATEAU outcome: not predicted here -- this cell MEASURES it (that is the fork). The prior trajectory
  (0.14 -> 0.42 still climbing) is MEASURED; whether it reaches 0.90 is the open question.
