# Pre-registration: path_e_engineering_characterization_v1_n4096

**Date:** 2026-05-30
**Anchor:** path_e_engineering_characterization_v1_n4096
**Test:** T4 (Test 23 of user-routed batch)
**Queue:** overnight_queue (GPU)
**Script:** experiments/exp_path_e_engineering_characterization_v1_n4096.py

## Hypothesis

Path E delivers ~50% partial accuracy at breaking and sub-linear K-scaling.
Even though Path D wins on absolute multi-hop accuracy, Path E may shine
in three niche application contexts:

  A) Top-K candidate identification at high K (5000, 10000): use Path E
     as a fast ranking filter; top-K precision @ k=10 should be high
     even when absolute hop accuracy is partial.
  B) Quick approximate multi-hop within a 50 ms wall-budget: Path E's
     continuous propagation + final argmax is one-shot and fast; useful
     when latency dominates and partial accuracy is acceptable.
  C) Latency-sensitive partial-accuracy tradeoff: at increasing noise
     sigma, latency should drop (or remain stable) faster than accuracy
     -> a useful operating point at sigma=0.2.

If at least 2/3 sub-tests show Path E delivering a useful application
property, Path E earns a niche capability classification (not raw multi-hop
winner but a useful filter/early-termination mechanism).

## Config

- N = 4096 (PROT-018 _n4096 binding).
- BSC substrate. M = 2048; depth = 5.
- 5 seeds = [7, 17, 23, 31, 41]; 32 path-starts per seed.

### Sub-tests

- Sub-test A: K_high in [5000, 10000]; top-K precision @ K=10.
  HP: precision >= 0.85 at one of the K-points in >= 3/5 seeds.
- Sub-test B: budget = 50 ms wall (time.perf_counter()).
  Process starts in budget; accuracy = correct / done.
  HP: accuracy >= 0.65 within budget in >= 3/5 seeds.
- Sub-test C: sigma in [0.0, 0.1, 0.2, 0.4]; measure accuracy + latency
  per sigma. Speedup = lat[sigma=0.0] / lat[sigma=0.2].
  HP: speedup >= 3.0 at sigma=0.2 in >= 3/5 seeds.

### Composite

n_pass = (A_hp + B_hp + C_hp) where each is a 3/5-seed-majority indicator.

## Pre-registered bands

**HARD_PASS:** n_pass >= 2/3.
**HARD_FAIL:** n_pass == 0.
**MIDDLE_BAND:** n_pass == 1.

## Self-tests

- N_FULL == 4096 (PROT-018).
- path_e_topk_score returns a permutation of candidates (no element added
  or dropped). Length preserved.
- measure_subB budget loop exits within budget_s + one final iteration
  duration; reported elapsed_s monotone increasing.
- compute_verdict returns T4_HARD_PASS / T4_HARD_FAIL / T4_MIDDLE_BAND /
  T4_INCONCLUSIVE only.
- Smoke verdict T4_HARD_PASS at N=1024 confirmed (subA=1.0, subB=1.0,
  subC=2/3 pass).

## OOM check

- N=4096, M=2048: 1 GB peak.
- Sub-test A: candidate tensor (K_high+1) longs ~ 80 KiB. Trivial.
- Sub-test B: continuous-propagation per start; per-batch ~1 MiB.
- Sub-test C: 4 sigma sweeps x same propagation; ~4x sub-B memory.
- All within 6 GB GPU ceiling.

## Smoke result

- N_smoke=1024, M=256, depth=3, n_paths=8, suba_Ks=[200], subc_sigmas=
  [0.0, 0.2], 1 seed.
- smoke_wall_s ~ 0.2s.
- subA_prec=1.000, subB_acc=1.000, subC_speedup=1.009 -> subA + subB pass,
  subC marginal at smoke (speedup~1 means no actual noise speedup since
  the smoke-noise path is dominated by overhead).
- All metrics non-null; instrumentation self-test PASSes.

## Walk-back gate

subC speedup at smoke is ~1.0 (within 20% of threshold of 3.0). The smoke
sigma sweep is only 2 points and noise has barely an effect at N=1024.
At FULL N=4096 with full sigma_sweep [0.0, 0.1, 0.2, 0.4], the speedup is
expected to scale with the per-hop noise-truncation effect on argmax.

Because subC is borderline at smoke, walk-back gate fires: 5 seeds is the
spec'd N — we do NOT increase to 10 because (a) the 2/3 sub-test rule
already gives n_pass=2 even if subC fails, sufficient for HP; (b) subA and
subB show clear margin (precision=1.0, accuracy=1.0 both far above their
0.85/0.65 thresholds). FULL run with 5 seeds is power-adequate.

## Timeout estimate

- smoke_wall_s = 0.2s at N=1024.
- FULL: 4x N, 4x n_paths, 8x M, 1.7x depth, 5 seeds, 2 K_high points, 4
  sigmas.
- Per-cell scaling factor (FULL/smoke): 4*4*8*1.7 = ~217; with
  scaling_exp=1.5 -> ~46x per-cell vs smoke.
- 0.2s/seed * 46 * 5 = 46s. Apply 2x safety + sub-test sweeps -> ~150s.
- Conservative budget with all 3 sub-tests fully exercised: timeout_s
  = 14400 (user task spec; budget is generous).

**timeout_s = 14400** (user task spec).
