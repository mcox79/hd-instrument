# Pre-registration: substrate_cortex_hippo_handoff_chain_grade_M_8192_GPU_v1

**Date:** 2026-06-28
**Anchor base:** substrate_cortex_hippo_handoff_chain_grade_M_8192_GPU_v1
**Chunks:** 3 single-seed cells (seeds {7, 13, 19})
**Scripts:**
  - experiments/exp_substrate_cortex_hippo_handoff_chain_grade_M_8192_GPU_v1_seed_7.py
  - experiments/exp_substrate_cortex_hippo_handoff_chain_grade_M_8192_GPU_v1_seed_13.py
  - experiments/exp_substrate_cortex_hippo_handoff_chain_grade_M_8192_GPU_v1_seed_19.py
**Queue:** overnight_queue (RTX 4060 Ti remote; torch+cuda; ~6h/seed est)
**Drill source:** Skunkworks landed-VET of seed_17 (commit f60880f7); MM re-tier
  due to n_seeds=1 + CAPACITY_WARN alpha=0.024 + PRE-REG DRIFT (N_h ran 512
  instead of declared 4096).

## Hypothesis

Items written one-shot into a sparse-DG hippocampus store (W_h, 10% bipolar
density, N_h=4096) can be CONSOLIDATED into a dense cortex store (W_c,
N_c=8192) during a "sleep" phase via random-uniform replay + slow Hebbian
covariance writes, such that the consolidated cortex memory:
  (a) Cortical recall on transferred items >= 0.50 absolute after hippo zeroed
  (b) Gap vs no-replay >= 0.40 (proves transfer is doing the work)
  (c) Cortical recall reaches >= 0.70 of direct-cortex ceiling
  (d) Operates at chain-grade capacity alpha >= 0.05 (M=8192 yields alpha=1.0
      simple OR 0.120 strict-Hopfield -- both >= 0.05)

Brain-grounded: CLS theory (McClelland-McNaughton-O'Reilly 1995);
Frankland & Bontempi 2005 systems consolidation; Klinzing-Niethard-Born 2019
SWR-replay.

## Chain-grade promotion path

This pre-reg supersedes the earlier
`preregs/2026-06-27_cortex_hippo_handoff_sparse_DG_dense_cortex_v1.md`
for the chain-grade tier. Seed_17 satisfied HARD_PASS on mechanism (FULL=1.000,
gap=+0.995, ratio=1.000) but was re-tiered to MEASURED_MECHANISM by Skunkworks
(commit f60880f7) on three audit findings:

  1. **n_seeds=1.** Chain-grade requires >=3 seeds with shared HARD_PASS.
  2. **PRE-REG DRIFT.** Prior prereg declared N_h=4096; seed_17 ran N_h=512
     (8x smaller). This rerun honors the original N_h=4096 spec.
  3. **CAPACITY_WARN.** Seed_17 ran M=200, N_c=8192 -> alpha=0.024 < 0.05.
     The Hopfield-textbook formulation gives an even stricter threshold;
     M=8192 lifts both alpha-simple (M/N_c=1.0) and alpha-Hopfield
     (M/(2*N*log N)=0.120) above 0.05 chain-grade floor.

## Pre-registered fairness disciplines (load-bearing)

1. W_h and W_c MUST be different tensors, different shapes, different sparsity.
2. Object-identity assertion `W_h is not W_c` at runtime.
3. Random-uniform replay sampling (NOT replay-count-as-importance; avoids the
   v4 NREM trap).
4. NO_REPLAY baseline must show cortex recall < 0.10 (cortex genuinely empty).
5. DIRECT_CORTEX ceiling matches total Hebbian-write count of the replay arm
   (no eta confound).
6. Same fixed projection P_hc for all arms (no learned-projection overfit).
7. GPU compute via torch.cuda; smoke verifies cuda available + reports
   peak GPU util heuristically (memory delta as proxy where util sampler
   unavailable).
8. Per Fix #24: full-run script imports torch; the overnight_queue routing
   gate would REJECT a numpy-only script -- this cell ships torch+cuda
   matmul ops as the FULL-N compute path.

## Pre-registered thresholds (single-seed; aggregated across 3 chunks for cert)

- **HARD_PASS** (per chunk):
    acc(FULL_HANDOFF) >= 0.50 AND
    acc(FULL) - acc(NO_REPLAY) >= 0.40 AND
    acc(FULL) >= 0.70 * acc(DIRECT_CORTEX) AND
    alpha_simple (M/N_c) >= 0.05 (auto-satisfied at M=8192, N_c=8192)
- **HARD_FAIL** (per chunk):
    acc(FULL) - acc(NO_REPLAY) < 0.10 (transfer does nothing)
    OR NO_REPLAY > 0.20 (cortex leaks signal)
    OR cardinality breach (n_arms != 3)
- **MIDDLE_BAND** (per chunk): everything else.

**Chain-grade promotion gate (Skunkworks aggregation):**
  3-of-3 seeds HARD_PASS AND alpha >= 0.05 in all three AND no CAPACITY_WARN.
  Then atomize cortex_hippo_handoff as CLS-architecture chain-grade primitive.

## Pre-registered §15 envelope-fail-bands

1. **Sweep alignment:** N/A. This is a capacity-anchored chain-grade
   verification cell -- a single config (N_h=4096, N_c=8192, M=8192) replicated
   across 3 seeds. The "sweep" was the parent prereg's prior smoke at
   N_h=512 + seed_17 FULL chunk; the present cell is the chain-grade rerun
   at the prereg-declared full spec. NO sweep axis required.

2. **Discriminating bracket:** acc(FULL_HANDOFF) - acc(NO_REPLAY) >= 0.40.
   Seed_17 measured +0.995 at M=200; M=8192 increases task difficulty
   (40x more items in 8192-dim cortex) so the discriminator gap may narrow.
   Floor (HARD_FAIL): gap < 0.10. PASS band: gap >= 0.40.

3. **Signal-shape audit:** hippo input keys/values are bipolar +-1 in N_raw=64;
   pattern_separate_sparse projects them to N_h=4096 sparse-bipolar (10%
   active = 410 nonzero units, +-1). project_hippo_to_cortex projects via
   random Gaussian P_hc and L2-normalizes to N_c=8192 dense unit vectors.
   Cortex readout: W_c @ key_c -> sign() -> bipolar prediction. cosine_match
   against vals_c bank. All shapes verified by _selftest_projection_dim_match.

4. **Positive control:** seed_17 (FULL=1.000, NO_REPLAY=0.005, DIRECT=1.000)
   serves as positive control at smaller params (N_h=512, M=200). Expected at
   N_h=4096, M=8192:
     - DIRECT_CORTEX should still saturate near 1.0 (M=8192 in N_c=8192 dense
       Hebbian is at-capacity for outer-product memory but with N_replay=50
       passes the effective writes (M * N_replay = 410k Hebbian outer-product
       contributions) gives strong overlap-canceling -- predict 0.80-1.00).
     - ARM_FULL_HANDOFF should track DIRECT within ratio >= 0.70 (predict
       0.55-1.00); the load-bearing question is whether replay-via-hippo
       loses info vs direct write. The mechanism remains identical at M=8192.
     - NO_REPLAY should be at deterministic floor ~1/M = 1.2e-4 (predict
       0.00-0.02).
   Smoke will use intermediate params (N_h=512, N_c=2048, M=512, N_replay=10);
   discriminator must FIRE: smoke gap >= 0.40 required before FULL dispatch.

5. **Functional-requirement decomposition:**
   - (a) hippo encode = pattern_separate_sparse (k-WTA bipolar) -- exists.
   - (b) replay reactivation = uniform sample from hippo bank
     (random.choice) -- exists.
   - (c) cortex consolidation = hebbian_write_cortex (outer product, eta) --
     exists.
   - (d) cortex readout = W_c @ key -> sign() -> cosine match argmax -- exists.
   All four primitives are implemented + selftested; no new substrate
   capabilities required to land this cell.

## Pre-reg fields (required)

- `expected_n_units = 3` (ARM_FULL_HANDOFF, ARM_NO_REPLAY, ARM_DIRECT_CORTEX)
- `cardinality_ok` mandatory in metrics.json
- `HARD_FAIL_CARDINALITY_BREACH` when observed != 3
- `HARD_FAIL_BY_CONSTRUCTION_SAT_OR_FLOOR` if all 3 arms saturate at 1.0
  (no discriminator)
- `HARD_FAIL_CAPACITY_WARN` deferred -- alpha auto-satisfies at M=8192
- `discriminator_survives_scale` -- smoke at intermediate params demonstrates
  gap >= 0.40 BEFORE FULL dispatch (per USER-LOCKED 2026-06-26 rule)
- §13 patterns: start_marker + crash_diagnostic + per-seed checkpoint +
  heartbeat (CellHeartbeat ctx manager from experiments/_cell_heartbeat.py)

## Smoke result (to be filled in by exp_dev pre-dispatch)

Smoke config: N_h=512, N_c=2048, M=512, N_replay=10, eta_c=0.005, seed=7.
Smoke runs locally on CPU (numpy fallback active under torch.cuda.is_available=False).
Smoke wall ~3-5min target. Gate: HARD_PASS at smoke; gap >= 0.40 to discharge
discriminator_survives_scale gate.

## Cap-map rows (proposed; on 3-of-3 HARD_PASS)

- Hippocampus->cortex consolidation (sparse-DG handoff at chain-grade scale)
- CLS-theory substrate primitive at chain-grade capacity
- NREM-replay-via-random-uniform-sampling (proves it's NOT replay-count-as-
  importance signal that's doing the work; matches Klinzing-Niethard-Born 2019)

## GPU rationale (per Fix #24)

- W_c shape (N_c x N_c) = 8192x8192 float32 = 268 MB -- fits on 8/16 GB GPU.
- W_h shape (N_h x N_h) = 4096x4096 float32 = 67 MB.
- keys_c bank shape (M, N_c) = 8192x8192 float32 = 268 MB.
- vals_c bank shape (M, N_c) = 8192x8192 float32 = 268 MB.
- Hebbian write: vectorized as `W_c += eta * vals_c.T @ keys_c` (batched
  matmul) instead of M individual outer products; this is ~M-fold GPU
  speedup over the parent's per-item Python loop.
- Readout: `preds = sign(W_c @ keys_c.T)` (batched) -> cosine match against
  vals_c bank via `vals_c @ preds_normalized.T`. All matmul.

GPU util target: >= 0.5 mean over per-arm compute window. Smoke runs on CPU
(numpy fallback); GPU util check applies only to FULL runs and is recorded
as a metrics-side proxy (peak GPU memory delta during arm compute).

## Coordination

- Cell-author: exp_dev (this dispatch).
- Landed-VET: skunkworks (aggregates 3 seeds for chain-grade promotion).
- Orchestrator: ship 3 single-seed cells to overnight_queue (GPU; remote@home).
- Push gate: harness-DENIED to exp_dev; orchestrator/hd_metrics_sync push to
  origin/main; remote runner reads from C:/dev/hd-instrument.

## Risk + mitigations

- **Capacity saturation at M=8192 N_c=8192**: outer-product Hebbian memory
  has well-known M < N_c capacity in the dense-bipolar regime. At alpha=1.0
  (simple) we are AT capacity. If DIRECT_CORTEX collapses to ~0.20-0.40
  this is the EXPECTED Hopfield-limit signature, not a cell failure --
  the discriminator (FULL vs NO_REPLAY gap) is what matters. Skunkworks
  should NOT auto-fail on DIRECT < 0.70 alone; the gap is the load-bearing
  signal.
- **GPU-util gate**: if smoke can't measure (CPU fallback), FULL run records
  memory-delta as proxy; Skunkworks reviews proxy >= 100 MB peak during
  ARM_FULL_HANDOFF.
- **Per-seed runtime**: timeout 28800s (8h); seed_17 took 8112s at M=200
  on CPU. With M=8192 (40x items) but vectorized GPU matmul (~30-100x
  speedup vs CPU-loop), expect 1-4h/seed. 8h cap is conservative.
