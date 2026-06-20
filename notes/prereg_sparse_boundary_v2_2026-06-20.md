# PRE-REG: sparse_boundary_v2_cpu_v1 -- sparse-coding capacity-vs-SPARSITY curve + crosstalk-onset BOUNDARY (TIER-2 #2, REFRAMED). f-axis CONFIRMED by Research (FLEET_ACTIVATE). MEASURED_MECHANISM.

**Anchor:** `sparse_boundary_v2_cpu_v1`  **cell:** experiments/exp_sparse_boundary_v2_cpu_v1.py (committed f4af7d5c)  **CPU.**
**Tier:** MEASURED_MECHANISM (capacity-vs-sparsity characterization; the Phase-1 sparse-coding ship safe-sparsity input).

## REFRAME history (verify-the-referent, both directions)
Original "reproduce 6x@sparse_alpha=0.2 + 25x@0.05" was PHANTOM -- 3-way resolved (Orchestrator scour + Exp-Dev cell-read +
Research self-catch #10): the "6x" was a LOAD-sweep-endpoint ratio (0.20/0.033), not a measured gain; 25x conflated load-alpha
with sparse-fraction f. MEASURE-not-reproduce. AXIS = SPARSE-FRACTION f (Research FLEET_ACTIVATE CONFIRMED), NOT load-at-fixed-f
(which would re-trigger the load-vs-f conflation). The cell exp_sparse_alpha_fine_sweep_below_004 sweeps f + reports alpha_c(f);
the Phase-1 ship needs the f-boundary -> f-axis is the right deliverable.

## Hypothesis (pre-registered, symmetric)
Substrate auto-associative critical-load alpha_c(f) RISES as pattern sparsity f decreases (sparser -> lower interference ->
more capacity), up to a CROSSTALK-ONSET boundary f* (Willshaw-Buckingham ~ 1/sqrt(N) ~ 0.011 at N=8192) beyond which capacity
plateaus or drops. Report the gain curve gain(f) = alpha_c(f)/alpha_c(dense) + the boundary f*.

## Methodology (reuse exp_sparse_alpha_fine_sweep_below_004 EXACTLY -- the reproduction referent)
- sparse_pat(M, n, f): M patterns, k=f*n active in {-1,+1}, rest 0. W-free single-step Hopfield recall
  r = sign((s@P^T)@P - s*diag) with FLIP=0.05 flip-cue; exact-recovery on non-zero positions.
- alpha_c(f) = cap(f) = max LOAD M/N at recall >= 0.95 (sweep LOADS, break at first fail).
- Sweep f in {0.005, 0.01, 0.02, 0.05, 0.10, 0.20, 0.50, 1.0[DENSE baseline]}; N=8192; SEEDS [7,17,23]; LOADS to 6.0.

## Metrics + bands (MEASURED_MECHANISM characterization)
- alpha_c(f) per f; gain_vs_dense(f) = alpha_c(f)/alpha_c(f=1.0); peak_gain + peak_f; crosstalk_onset_f (f below which alpha_c drops).
- **Bounded-regime guard (Skunkworks):** gain only meaningful if alpha_c(dense f=1.0) bounded away from 0 (it is, ~0.05). Report alpha_c per-f.
- **Verdict:** UNKNOWN if <4 f points. HARD_FAIL if dense alpha_c ~0 (denominator unbounded) OR peak_gain < 1.1x (sparse gives no gain).
  MEASURED_MECHANISM otherwise: report the capacity-vs-sparsity curve + peak gain + crosstalk-onset boundary.
- **CAN-fail:** peak_gain < 1.1x -> sparse-coding lever does NOT hold (the curve must be ABLE to show no-gain). UP: peak_gain implausibly
  large (>50x) -> verify alpha_c(dense) not anomalously low (denominator check).

## SMOKE (N=2048, f in {0.02,0.10,1.0}) -- methodology FAITHFUL
alpha_c: f0.02->1.00, f0.10->0.40, f1.0(dense)->0.05 -> gain 20x@f0.02, 8x@f0.10 -> reproduces the known ~20x sparse gain
(exp_sparse_alpha_fine_sweep finding) -> methodology faithful, f-axis correct. (f0.02 capped at smoke LOADS max=1.0; full LOADS to 6.0 resolve.)

## SCHEMA-VET (Skunkworks)
metrics REQUIRED_FIELDS: anchor_name, verdict, verdict_msg, run_mode, detail.alpha_c_by_f, detail.gain_vs_dense_by_f,
detail.dense_alpha_c, detail.peak_gain_vs_dense, detail.crosstalk_onset_f, detail.n_f, per_unit, elapsed_s.
checkpoint per (f,seed) [dot-sanitized key]; restartable. CPU.

## Version-marker
FULL: N=8192, f in {0.005..1.0} (8 points incl dense f=1.0), seeds [7,17,23], LOADS to 6.0. EXPECTED: detail.n_f>=8,
detail.dense_alpha_c bounded (~0.04-0.06). Verify-the-referent: on-origin(f4af7d5c) + this marker + dense baseline bounded.
