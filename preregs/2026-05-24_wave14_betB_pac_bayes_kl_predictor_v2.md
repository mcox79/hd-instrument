# Prereg: wave14_betB_pac_bayes_kl_predictor_v2

**Filed**: 2026-05-24 exp_dev (re-ship after 0-valid-cells crash fix)
**Anchor**: Alt3 PAC-Bayes Laplace-Fisher KL as retention predictor [v2]
**Trigger**: wave14_betB_pac_bayes_kl_predictor_v1 ALT3_INSTRUMENTATION_FAIL (0 valid cells,
             22ms exit -- all 25 cells threw silently-swallowed exceptions).
**Design unchanged**: same hypothesis, KL formula, thresholds, seeds/pairs as v1.

## Root cause of v1 failure (diagnosed)

All 25 cells (5 seeds x 5 pairs) crashed silently inside the try/except wrapper,
producing 0 valid cells. Two candidate root causes, both fixed in v2:

(1) torch.Generator(device=device) with device="cuda" -- pa.make_bsc_atoms uses
    torch.rand(..., generator=gen) which requires gen.device == output tensor device.
    On some CUDA builds, cross-device generator usage raises RuntimeError.
    v2 fix: use torch.Generator() (CPU) + .to(device) for atom tensors.

(2) Silent exception swallowing -- the bare `except Exception as ex:` block in v1
    only printed ex without traceback, so the runner log captured no useful detail.
    v2 fix: traceback.print_exc() called before appending NaN cell.

(3) Corpus empty check: added preflight to fail fast if corpus_a < 100 bytes,
    before entering seed/pair loops.

## Hypothesis (unchanged from v1)

Does the Laplace-Fisher posterior KL between W_A and W_B predict retention_A?

Formula (eq (**) from handoff):
  KL_diag(q_B || q_A) = 0.5 * sum_i [
      (f_{A,i}/f_{B,i}) - 1 - log(f_{B,i}/f_{A,i}) + f_{A,i}*(W_B - W_A)_i^2
  ]
  Ridge = 1/N to handle rank degeneracy.

## Design (unchanged from v1)

- N = 4096 (FULL), 512 (smoke)
- batch = 64 (FULL), 32 (smoke)
- epochs = 5 (FULL), 1 (smoke); phase_a_epochs = 8 (FULL), 2 (smoke)
- n_bytes = 200k (FULL), 3k (smoke)
- Seeds FULL: [7, 17, 23, 31, 41]; Seeds smoke: [17]
- Pairs FULL: [0,1,2,3,4]; Pairs smoke: [0,2,4]
- Queue: overnight_queue (GPU)

## Pre-registered bands (unchanged from v1)

HARD-PASS:
  r^2(KL_fisher, retention_A) >= 0.50 across >= 15 valid cells
  AND r^2_fisher > r^2_euclidean + 0.10
  -> Laplace-Fisher KL is binding mechanism for Bet B retention.

HARD-FAIL:
  r^2_fisher < 0.20 AND r^2_euclidean < 0.20
  -> No weight-space geometry predicts Bet B retention.
  Rehab: (a) function-space KL, (b) empirical Bernstein, (c) task-arithmetic.

MIDDLE:
  r^2 in [0.20, 0.50) OR Fisher improvement < 0.10
  -> Partial signal; run with larger n_cells or upgrade to KFAC Fisher.

LAPLACE-ASSUMPTION-VIOLATED:
  ||Delta_W||_F / ||W_A||_F > 0.5 majority
  -> Flag; KL estimate unreliable in this regime.
  Rehab: switch to Bernstein-McAllister instead of Laplace-Fisher bound.

## Self-tests (unchanged; 5 cells passed in v1 gate)

All 5 self-tests from v1 still apply:
1. KL(q_A || q_A) = 0 exactly
2. 1-D scalar case: W_A=0, W_B=1, f_A=4, f_B=1, ridge=0 -> 2.8069
3. High-curvature direction: f_A=100 at [0,0] -> KL=50.0
4. Euclidean proxy for same case = 1.0 (confirms Fisher 50x larger)
5. pac_bayes_floor(kl=50, m=200) = 0.646

v2 ADDITIONAL self-test: verify run_one_cell does not raise with N=128 smoke params.
