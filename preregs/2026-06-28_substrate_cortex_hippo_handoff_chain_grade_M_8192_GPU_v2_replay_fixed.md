# Pre-registration: substrate_cortex_hippo_handoff_chain_grade_M_8192_GPU_v2_replay_fixed

**Date:** 2026-06-28
**Anchor base:** substrate_cortex_hippo_handoff_chain_grade_M_8192_GPU_v2_replay_fixed
**Supersedes:** preregs/2026-06-28_substrate_cortex_hippo_handoff_chain_grade_M_8192_GPU_v1.md
**Chunks:** 3 single-seed cells (seeds {7, 13, 19})
**Scripts:**
  - experiments/exp_substrate_cortex_hippo_handoff_chain_grade_M_8192_GPU_v2_replay_fixed_seed_7.py
  - experiments/exp_substrate_cortex_hippo_handoff_chain_grade_M_8192_GPU_v2_replay_fixed_seed_13.py
  - experiments/exp_substrate_cortex_hippo_handoff_chain_grade_M_8192_GPU_v2_replay_fixed_seed_19.py
**Queue:** overnight_queue / remote_gpu_queue (RTX 4060 Ti remote; torch+cuda; ~3-6h/seed est)
**Drill source:** Skunkworks audit of v1 ARM_FULL_HANDOFF vs ARM_DIRECT_CORTEX bit-exact equivalence
  across all 3 v1 seeds. Root cause: v1 cell's FULL_HANDOFF arm bypassed W_hippo entirely
  and wrote cortex directly from stored vals_c, keys_c (lines 462-477 = same code path as
  DIRECT_CORTEX at 511-512). The "permutation-invariant sum" rationalization is
  mathematically wrong for the CLS theory under test.

## The v1 bug (root cause)

v1 ARM_FULL_HANDOFF (after encoding):

    W_hippo.addmm_(vals_h.T, keys_h)                          # writes hippo
    for cycle in range(N_REPLAY_CYCLES):
        perm = torch.randperm(...)                            # unused
        W_cortex.addmm_(vals_c.T, keys_c, alpha=ETA_CORTEX)   # bypasses W_hippo!

v1 ARM_DIRECT_CORTEX:

    for cycle in range(N_REPLAY_CYCLES):
        W_cortex.addmm_(vals_c.T, keys_c, alpha=ETA_CORTEX)   # same write

The two arms produce bit-identical W_cortex because the only difference (W_hippo write +
zero) doesn't touch W_cortex. The unused `perm` was a comment-rationalization for a
write that doesn't depend on `perm` at all.

CLS-theory-required behavior MISSING in v1:
  - replay should REACTIVATE items via hippo READOUT (W_hippo @ cue);
  - cortex Hebbian writes should use those REACTIVATED signals, NOT the
    pre-stored vals_c, keys_c.

## v2 corrected replay (CLS-faithful)

v2 ARM_FULL_HANDOFF replay loop:

    W_hippo.addmm_(vals_h.T, keys_h)            # one-shot hippo encode (kept)
    gen = torch.Generator(device=dev); gen.manual_seed(seed + 31)
    for cycle in range(N_REPLAY_CYCLES * M_ITEMS):   # M_ITEMS sample-events per cycle
        # 1. Sample a cue from the hippo bank (random-uniform replay sampling;
        #    NOT replay-count-as-importance per META_RULE_AF).
        idx = torch.randint(0, M_ITEMS, (1,), generator=gen, device=dev).item()
        cue_h = keys_h[idx]                      # sparse N_h bipolar
        # 2. Hippo readout: reactivate via existing W_hippo.
        val_reactivated_h = torch.sign(W_hippo @ cue_h)   # dense N_h bipolar
        # 3. Project hippo state -> cortex spaces using P_hc.
        cue_c = (P_hc @ cue_h);   cue_c = cue_c / cue_c.norm().clamp_min(1e-12)
        val_c_reactivated = (P_hc @ val_reactivated_h)
        val_c_reactivated = val_c_reactivated / val_c_reactivated.norm().clamp_min(1e-12)
        # 4. Cortex Hebbian write from REACTIVATED signals (NOT stored vals_c).
        W_cortex.addr_(val_c_reactivated, cue_c, alpha=ETA_CORTEX)
    W_hippo.zero_()
    # ... readout via cortex_readout(W_c, keys_c) -> cosine_match against vals_c

The strict, performance-batched alternative we adopt:

    for cycle in range(N_REPLAY_CYCLES):
        perm = torch.randperm(M_ITEMS, generator=gen, device=dev)
        cues_h = keys_h[perm]                              # (M, N_h) sampled cues
        vals_reactivated_h = torch.sign(cues_h @ W_hippo.T)   # (M, N_h) via hippo
        # zero-handling: sign(0) -> +1 to keep bipolar
        cues_c = (cues_h @ P_hc.T)                         # (M, N_c) projected cues
        cues_c = cues_c / cues_c.norm(dim=1, keepdim=True).clamp_min(1e-12)
        vals_c_reactivated = (vals_reactivated_h @ P_hc.T) # (M, N_c) projected reacts
        vals_c_reactivated = vals_c_reactivated / vals_c_reactivated.norm(dim=1, keepdim=True).clamp_min(1e-12)
        # Hebbian batched write -- KEY: uses reactivated values, not stored vals_c.
        W_cortex.addmm_(vals_c_reactivated.T, cues_c, alpha=ETA_CORTEX)

Critical mathematical distinction:
  - DIRECT_CORTEX writes `eta * vals_c.T @ keys_c` (deterministic; uses stored values).
  - FULL_HANDOFF v2 writes `eta * vals_c_reactivated.T @ cues_c` where
    vals_c_reactivated depends on W_hippo readout. When W_hippo is one-shot encoded
    from M=8192 outer products, readout is interference-laden and bipolar-thresholded.
    These two write streams are guaranteed mathematically distinct.

## Hypothesis

Items written one-shot into a sparse-DG hippocampus store (W_h, 10% bipolar
density, N_h=4096) can be CONSOLIDATED into a dense cortex store (W_c,
N_c=8192) during a "sleep" phase by reading them OUT of W_hippo via cue-based
reactivation and writing the REACTIVATED signals (not stored signals) into
W_cortex via slow Hebbian covariance writes, such that:
  (a) Cortical recall on transferred items >= 0.50 absolute after hippo zeroed
  (b) Gap vs no-replay >= 0.40 (proves transfer is doing the work)
  (c) FULL and DIRECT arms produce demonstrably DIFFERENT cortex weights
      (abs(recall_FULL - recall_DIRECT) > 0.05; bit-exact equality forbidden)
  (d) Operates at chain-grade capacity alpha >= 0.05 (M=8192 yields alpha=1.0
      simple OR 0.120 strict-Hopfield -- both >= 0.05)

Brain-grounded: CLS theory (McClelland-McNaughton-O'Reilly 1995);
Frankland & Bontempi 2005 systems consolidation; Klinzing-Niethard-Born 2019
SWR-replay; Wittkuhn & Schuck 2021 fast-replay reactivation.

## Pre-registered fairness disciplines (load-bearing)

1. W_h and W_c MUST be different tensors, different shapes, different sparsity.
2. Object-identity assertion `W_h is not W_c` at runtime.
3. FULL_HANDOFF replay sampling is random-uniform over indices (NOT
   replay-count-as-importance; avoids META_RULE_AF trap).
4. NO_REPLAY baseline must show cortex recall < 0.10 (cortex genuinely empty).
5. DIRECT_CORTEX ceiling matches total Hebbian-write count of the replay arm
   (no eta confound; both run N_REPLAY_CYCLES batched matmul writes).
6. Same fixed projection P_hc for all arms (no learned-projection overfit).
7. GPU compute via torch.cuda; smoke verifies cuda available + reports
   peak GPU util heuristically (memory delta as proxy where util sampler
   unavailable).
8. Per Fix #24: full-run script imports torch; the overnight_queue routing
   gate would REJECT a numpy-only script -- this cell ships torch+cuda
   matmul ops as the FULL-N compute path.
9. **NEW v2 discipline:** FULL_HANDOFF cortex writes MUST use signals derived
   from W_hippo @ cue (the reactivated readout), NOT the pre-stored vals_c,
   keys_c. Code review must verify the write expression references a tensor
   computed via W_hippo readout.
10. **NEW v2 guard:** verdict HARD_FAILs when abs(recall_FULL - recall_DIRECT)
    < 0.05 (catches v1 bug recurrence; bit-exact identity at 1e-6 catches
    raw recurrence; 0.05 catches subtler write-stream collapse).

## Pre-registered thresholds (single-seed; aggregated across 3 chunks for cert)

- **HARD_PASS** (per chunk):
    acc(FULL_HANDOFF) >= 0.50 AND
    acc(FULL) - acc(NO_REPLAY) >= 0.40 AND
    abs(acc(FULL) - acc(DIRECT_CORTEX)) > 0.05 AND       # NEW v2 guard
    alpha_simple (M/N_c) >= 0.05 (auto-satisfied at M=8192, N_c=8192)
- **HARD_FAIL** (per chunk):
    acc(FULL) - acc(NO_REPLAY) < 0.10 (transfer does nothing)
    OR NO_REPLAY > 0.20 (cortex leaks signal)
    OR cardinality breach (n_arms != 3)
    OR abs(acc(FULL) - acc(DIRECT_CORTEX)) <= 0.05 (META_RULE_AF write-collapse)  # NEW
    OR abs(acc(FULL) - acc(DIRECT_CORTEX)) < 1e-6 (bit-exact arm collapse)        # NEW
- **MIDDLE_BAND** (per chunk): everything else.

**Chain-grade promotion gate (Skunkworks aggregation):**
  3-of-3 seeds HARD_PASS AND alpha >= 0.05 in all three AND no CAPACITY_WARN
  AND no FULL=DIRECT collapse in any seed.
  Then atomize cortex_hippo_handoff as CLS-architecture chain-grade primitive.

## Pre-registered MANDATORY §15 envelope-fail-bands

1. **Sweep alignment:** N/A. Single-config chain-grade verification cell --
   one config (N_h=4096, N_c=8192, M=8192) replicated across 3 seeds. No sweep
   axis required. The "scaling" justification is in band #2 (discriminator
   survives scale) plus the positive control at small N (band #4).

2. **Discriminating bracket:**
   - Primary gap: acc(FULL_HANDOFF) - acc(NO_REPLAY) >= 0.40 (PASS),
     < 0.10 (FAIL).
   - Arm-distinctness gap (v2 NEW): abs(acc(FULL) - acc(DIRECT)) > 0.05.
     The two write streams MUST produce measurably different recall.
   - Bit-exact guard (v2 NEW): abs(recall_FULL - recall_DIRECT) < 1e-6
     forces HARD_FAIL META_RULE_AF VIOLATION.

3. **Signal-shape audit (META_RULE_AP_v3):**
   - hippo state ∈ sparse_N_h (bipolar +-1, 10% active = 410 of 4096 units).
   - hippo->cortex projection P_hc maps R^{N_h} -> R^{N_c} (dense Gaussian).
   - cortex query/value ∈ dense_N_c (L2-normalized unit vectors).
   - W_hippo readout `sign(cue @ W_hippo.T)` produces N_h bipolar reactivated
     value; projected via P_hc and L2-normalized to a N_c dense unit vector.
   - The READ-then-WRITE coupling forces W_hippo into the dataflow.

4. **Positive control at test regime:**
   - v1 seed_17 positive control INVALIDATED (had the bug; FULL=1.000 because
     it ran the DIRECT_CORTEX code path under a different label).
   - NEW positive control to run as part of smoke: M=100, N_h=512, N_c=2048
     with replay enabled vs no-replay. Expected:
       FULL_HANDOFF (with corrected replay) > NO_REPLAY by >0.40,
     because at M=100 W_hippo (one-shot Hebbian, 512x512) easily holds 100
     sparse-bipolar item-value bindings with high SNR, and reactivation
     fidelity should be near 1.0.
   - HARD_PASS smoke gates FULL dispatch.

5. **Functional-requirement decomposition:**
   - (a) hippo fast encode (sparse-DG one-shot): `W_h.addmm_(vals_h.T, keys_h)`
     -- exists.
   - (b) hippo readout reactivation (sparse cue -> sparse value):
     `sign(cue @ W_h.T)` -- exists as primitive (matmul + sign).
   - (c) hippo-to-cortex projection (sparse N_h -> dense N_c):
     `(x @ P_hc.T) / norm` -- exists.
   - (d) cortex Hebbian write from REACTIVATED signals (NOT stored):
     `W_c.addmm_(vals_c_reactivated.T, cues_c, alpha=eta)` -- exists; the
     load-bearing requirement is that `vals_c_reactivated` is derived from
     `cue @ W_h.T` not from `vals_c` directly.
   - (e) cortex readout: `sign(keys_c @ W_c.T)` + cosine match -- exists.
   Each maps to existing hdlab/numpy primitive; no new substrate capability.

## Pre-reg fields (required)

- `expected_n_units = 3` (ARM_FULL_HANDOFF, ARM_NO_REPLAY, ARM_DIRECT_CORTEX)
- `cardinality_ok` mandatory in metrics.json
- `HARD_FAIL_CARDINALITY_BREACH` when observed != 3
- `HARD_FAIL_BY_CONSTRUCTION_SAT_OR_FLOOR` if all 3 arms saturate at 1.0
  (no discriminator)
- `HARD_FAIL_FULL_EQUALS_DIRECT_BIT_EXACT` v2 NEW: catches v1 bug recurrence
- `HARD_FAIL_FULL_EQUALS_DIRECT_FUZZY` v2 NEW: abs gap <= 0.05 means
  write-streams collapsed to indistinguishable
- `HARD_FAIL_GPU_UTIL_BELOW_50_PCT` (Fix #24; proxied via mem-delta floor)
- `HARD_FAIL_CAPACITY_WARN` deferred -- alpha auto-satisfies at M=8192
- `discriminator_survives_scale` -- smoke at intermediate params demonstrates
  gap >= 0.40 AND arm-distinctness > 0.05 BEFORE FULL dispatch
- §13 patterns: start_marker + crash_diagnostic + per-seed checkpoint +
  heartbeat (CellHeartbeat ctx manager from experiments/_cell_heartbeat.py
  or inlined helper)

## Smoke result (to be filled in by exp_dev pre-dispatch)

Smoke config: N_h=512, N_c=2048, M=512, N_replay=10, eta_c=0.005, seed=7.
Smoke runs locally on CPU (numpy fallback active under torch.cuda.is_available=False).
Smoke wall ~3-5min target. Gates (BOTH must HARD_PASS at smoke):
  (i) gap FULL vs NO_REPLAY >= 0.40 (discharges discriminator_survives_scale),
  (ii) abs(FULL - DIRECT) > 0.05 (discharges v2 arm-distinctness).

## Cap-map rows (proposed; on 3-of-3 HARD_PASS)

- Hippocampus->cortex consolidation (sparse-DG handoff at chain-grade scale)
- CLS-theory substrate primitive at chain-grade capacity (corrected replay)
- NREM-replay-via-cue-reactivation (proves it's hippo READOUT mediating the
  transfer, not bypass; matches Wittkuhn & Schuck 2021)

## GPU rationale (per Fix #24)

- W_c shape (N_c x N_c) = 8192x8192 float32 = 268 MB -- fits on 8/16 GB GPU.
- W_h shape (N_h x N_h) = 4096x4096 float32 = 67 MB.
- keys_c bank shape (M, N_c) = 8192x8192 float32 = 268 MB.
- vals_c bank shape (M, N_c) = 8192x8192 float32 = 268 MB.
- per-cycle replay:
    sample (M,) idx
    cues_h = keys_h[idx]                     # gather
    vals_reactivated_h = sign(cues_h @ W_h.T)   # (M, N_h) <- hippo readout
    cues_c = ((cues_h @ P_hc.T)) / norm     # (M, N_c)
    vals_c_react = ((vals_reactivated_h @ P_hc.T)) / norm     # (M, N_c)
    W_c.addmm_(vals_c_react.T, cues_c, alpha=eta)
  All batched matmul on GPU. Compared to v1 the extra cost per cycle is
  one (M, N_h) @ (N_h, N_h) matmul = 8192 * 4096 * 4096 = 137 GFlop, plus
  two (M, N_h) @ (N_h, N_c) matmul = 274 GFlop each = 548 GFlop per cycle.
  N_REPLAY_CYCLES=50 -> ~34 TFlop wall; well within RTX 4060 Ti budget.
- DIRECT path: unchanged from v1 (eta * vals_c.T @ keys_c per cycle).

GPU util target: >= 0.5 mean over per-arm compute window. Smoke runs on CPU
(numpy fallback); GPU util check applies only to FULL runs and is recorded
as a metrics-side proxy (peak GPU memory delta during arm compute).

## Coordination

- Cell-author: exp_dev (this dispatch).
- Landed-VET: skunkworks (aggregates 3 seeds for chain-grade promotion;
  audits write expression in source per discipline #9 + verifies arm-
  distinctness > 0.05).
- Orchestrator: ship 3 single-seed cells to overnight_queue / remote_gpu_queue
  (GPU; remote@home). Push gate harness-DENIED to exp_dev; hd_metrics_sync /
  orchestrator pushes to origin/main; remote runner reads from
  C:/dev/hd-instrument.

## Risk + mitigations

- **Capacity saturation at M=8192 N_c=8192**: outer-product Hebbian memory
  has well-known M < N_c capacity in the dense-bipolar regime. At alpha=1.0
  (simple) we are AT capacity. If DIRECT_CORTEX collapses to ~0.20-0.40
  this is the EXPECTED Hopfield-limit signature, not a cell failure --
  the gap (FULL vs NO_REPLAY) is the load-bearing discriminator. v2 makes
  the FULL-vs-DIRECT-distinctness gap ALSO load-bearing.
- **Hippo readout fidelity at M=8192 N_h=4096**: W_h is 4096x4096; M=8192
  one-shot items in alpha_h = M/(2*N_h*log(N_h)) = 8192/(2*4096*8.32) =
  0.120 Hopfield-strict regime. Reactivation fidelity will be lossy; this
  is REALISTIC neural consolidation noise. FULL should land lower than
  DIRECT (which gets clean vals_c). This is the EXPECTED v2 signature:
  FULL < DIRECT by some nonzero margin > 0.05.
- **FULL might collapse to NO_REPLAY level** if hippo reactivation is too
  lossy. Mitigation: smoke at intermediate params verifies the mechanism
  fires; if smoke FAILs, do not dispatch FULL.
- **GPU-util gate**: if smoke can't measure (CPU fallback), FULL run records
  memory-delta as proxy; Skunkworks reviews proxy >= 100 MB peak during
  ARM_FULL_HANDOFF.
- **Per-seed runtime**: timeout 28800s (8h); v1 seed_7 wall expected 1-4h.
  v2 adds ~3x compute per replay cycle. Budget 4-6h/seed on RTX 4060 Ti.

## Difference from v1 (one-line summary)

v1 wrote `W_c.addmm_(vals_c.T, keys_c, alpha=eta)` in BOTH FULL and DIRECT.
v2 FULL writes `W_c.addmm_(vals_c_reactivated.T, cues_c, alpha=eta)` where
`vals_c_reactivated = sign(cue_h @ W_h.T) @ P_hc.T` (L2-normalized), and
DIRECT is unchanged. The arms now exercise DIFFERENT code paths through
W_hippo, satisfying CLS theory under test.
