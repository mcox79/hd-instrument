# Prereg: n2_capacity_scaling_v1

**Date:** 2026-06-21
**Anchor name:** n2_capacity_scaling_v1
**Script:** experiments/exp_n2_capacity_scaling_v1.py
**Queue:** remote_cpu_queue
**Status:** PRE-REGISTERED (not yet dispatched)

## Hypothesis

The co-opt cell (n2_depth_x_codebook_coopt_v1) found that V_C=1024/N_DIM=4096 saturates the
transition store (alpha = unique_pairs/N_DIM = ~1.99 > 1.0), causing recall crosstalk and
substrate-BPC=5.27 (WORSE than V_C=256/N=4096 at 5.00). The hypothesis is: scaling N_DIM UP
un-saturates the store (alpha drops below 1.0), enabling the low-floor codebook (ceiling_bpc~1.96
at V_C=1024) and good concept recall (top1=0.554) to translate into lower token-BPC. The
breakthrough target: any (N_DIM, K) beats bigram BPC (~3.84) on Pythia-160M Pile tokens.

## Sweep grid

- N_DIM_GRID (production): {4096, 8192} -- V_C=1024 FIXED
- K_SET (depth): {1, 2}
- Seeds: {7, 17, 23}
- Total configs: 4 x 3 seeds = 12 runs
- V_C: 1024 (fixed; low-floor codebook from co-opt cell)
- f_sparse: 0.006 (matches co-opt verbatim)

Note: N_DIM=16384 is deferred (estimated 480 min/config at V_C=1024 on CPU; exceeds 4h budget
per-config). Production grid covers {4096, 8192} to stay within the 4h window per anchor.

## N-suffix binding (PROT-018)

No _nN suffix on anchor name. This anchor sweeps N_DIM as the independent variable axis.
Adding _n4096 or _n8192 would mis-label a multi-N sweep as a fixed-N run. Per role contract
PROT-018 rule 3: "No _nN suffix; production N = sweep {4096, 8192}; rationale: N_DIM is the
independent variable axis."

## Scientific questions (verdict must answer)

(a) Does scaling N_DIM up DROP alpha below 1.0 (un-saturate)?
    Expected: alpha ~1.99 at N=4096 -> ~1.0 at N=8192 (linear by construction).
(b) Does un-saturating LOWER substrate-BPC vs the saturated N=4096/V_C=1024 anchor (5.27)?
(c) Does any (N, K) BEAT BIGRAM (3.84)? -- the breakthrough.

## Anchor correctness check

N=4096/V_C=1024/K=1 must reproduce the co-opt saturated result ~5.27 (within 0.2 bits).
If the anchor check fails, the verdict must flag ANCHOR-MISMATCH and the result is inconclusive.

## Pre-registered verdict bands

### HARD_PASS (chain-grade, ALL conditions required)
- Some (N, K) substrate_bpc < bigram_bpc (expected ~3.84)
- CV across seeds for that config <= 0.05
- That config is NOT saturated (alpha <= 1.0)
- Substrate-only decode (no LLM at inference -- enforced by design)

This is the capacity-scaling breakthrough: V_C=1024 low-floor + un-saturated N_DIM beats bigram.

### MIDDLE_BAND (EITHER condition)
- N-scaling LOWERS substrate-BPC monotonically as alpha drops (N4096 > N8192 at K=1)
  AND best config gets within 0.5 bits of bigram (best_bpc <= bigram + 0.5)
- OR best_bpc < anchor_bpc (5.27) by >= 0.20 bits, even if not monotone

This confirms the capacity lever works (N_DIM expansion un-saturates and lowers BPC),
even if bigram beat is not achieved.

### HARD_FAIL
- N-scaling does NOT lower substrate-BPC across N_DIM grid (BPC does not decrease as N grows)
- AND best_bpc > bigram_bpc + 0.5 (architecture caps well above bigram regardless of N)

## Calibration notes

This is NOT a first-measurement calibration probe. The anchor (N=4096/V_C=1024/K=1) reproduces
the co-opt cell saturated result (~5.27). The N-scaling improvement is a theoretical prediction
(alpha drops ~linearly with N_DIM; recall crosstalk should decrease; BPC should improve).
Bands are tight because the mechanism is well-characterized from the co-opt cell.

## Efficiency and RAM

W matrix peak RAM:
- N=4096:  4096x4096 float32 = 0.07 GB
- N=8192:  8192x8192 float32 = 0.27 GB
- N=16384: 16384x16384 float32 = 1.07 GB (deferred from production grid)

Peak RAM at N=8192 (largest in production grid):
  W(0.27) + D(8192 x 50257 x 4 = 1.65 GB) + C(1024 x 8192 x 4 = 0.03 GB) + misc ~ 2.0 GB
  Well within 14 GB budget.

P_src and P_dst are freed immediately after build_W via `del P_src, P_dst` (critical discipline).

## Timeout estimate

Smoke is NOT runnable locally (data lives on marsh@home). Using co-opt cell timing as anchor:
- n2_depth_x_codebook_coopt_v1 at N=4096/V_C=1024: estimated ~30 min/config
- N=8192: W is 4x larger (8192^2 vs 4096^2) + recall is 4x more expensive -> ~120 min/config
- K=2 adds ~10% overhead for context construction vs K=1
- Per-seed: 2 N_DIM x 2 K = 4 configs x ~30-120 min = 3-9 hr/seed (N_DIM-dominated)
- Full (3 seeds): 9-27 hr total

Applying timeout formula with smoke_wall_s from co-opt (est ~1800s/config):
  timeout_s = ceil(1.5 * 1800 * (2 configs N + 2 configs K) * 3 seeds) = ceil(1.5 * 1800 * 4 * 3)
  = ceil(32400) -> conservative: 36000 s = 10 hr per seed / 30 hr total

RECOMMENDED timeout_s: 108000 (30 hr) -- this is a long run but per-seed checkpoint protects it.
Flag for orchestrator: this run WILL tie up the remote CPU runner for 1-2 days. Acceptable only
if remote_cpu_queue runner is not needed for other high-priority cells during this window.

Alternative: queue N_DIM=4096 and N_DIM=8192 as separate anchors, each with a 2-seed quick run,
to get a preliminary result faster. Current design queues both together per the sweep spec.

## Dependency

Input file: data/exp_phase05_v1_pythia160m_residual_extract_pertoken_v1/residuals_per_token.npz
  - Must be present on marsh@home at C:/dev/hd-instrument/data/exp_phase05_v1_pythia160m_residual_extract_pertoken_v1/residuals_per_token.npz
  - Must contain token_ids key (verified by cell; hard error if absent)
  - Confirmed present on marsh@home per n2_depth_x_codebook_coopt_v1 run history

## Walk-back gate

No smoke wall_s available (data on remote). Effect size at smoke scale unknown. The N-scaling
lever is theoretically strong (alpha halves from N=4096 to N=8192), so no walk-back triggered.
If N=8192 shows borderline improvement (BPC reduction < 0.2 bits), recommend follow-on with
N=16384 before ruling on MIDDLE_BAND.

## Instrumentation self-test

Script runs _instrumentation_selftest() at module scope (11 tests). Self-test verified EXIT 0
on local .venv (d:/AI/hd-instrument/.venv/Scripts/python.exe). Tests cover:
  T1: permutation-binding invertibility (roll/unroll)
  T2: K=1 context == L2_norm(C[c_t]) for multiple N_DIM values
  T3: batched context == per-position for K in {1,2}
  T4: all per-(N_DIM,K) metrics non-null/non-sentinel on synthetic data
  T5: ceiling_bpc finite and positive
  T6: alpha = unique_pairs/N_DIM computes correctly
  T7: depth_token_gain finite for K=2
  T8: P_src/P_dst freed after build_W, W shape correct
  T9: RAM estimate at N=16384 < 14 GB ceiling (verified: 4.57 GB with 2000-chunk batching)
  T10: all module-level constants are real code, correct types
  T11: small end-to-end smoke path completes (bpc=3.385 on tiny synthetic)

AST verification: all 12 key constants confirmed module-level assignments (not docstring).
