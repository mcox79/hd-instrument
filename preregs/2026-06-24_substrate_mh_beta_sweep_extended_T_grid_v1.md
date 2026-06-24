# substrate_mh_beta_sweep_extended_T_grid_v1 -- PRE-REGISTRATION

Status: PRE-REGISTERED 2026-06-24 (pre-smoke; bands locked)
Anchor: substrate_mh_beta_sweep_extended_T_grid_v1
Author: hdi_exp_dev
Cell: experiments/exp_substrate_mh_beta_sweep_extended_T_grid_v1.py

## Composition collapse drill: symptomatic vs structural diagnosis

A1 cell (substrate_compose_fair_harness_cfrpe_hetplasticity_K2_modern_hopfield_cleanup_v1)
produced HARD_FAIL: ARM_FULL_JOINT_COMPOSE BPC=7.8919 -- worse than unigram (~6.97).
Diagnosed symptoms (from per-seed metrics seed=7 + symmetric across 3/3 seeds):

| arm                                          | bpc    | best_T | best_lambda |
|----------------------------------------------|--------|--------|-------------|
| ARM_FAIR_HARNESS_PLUS_CFRPE_PLUS_HET_K2     | 7.1781 | 0.02   | 0.1         |
| ARM_FULL_JOINT_COMPOSE (+ MH beta=8.0)       | 7.8919 | 1.00   | 0.1         |

Smoking gun: best_T jumped 50x (0.02 -> 1.0) when MH was added; raw_bpc_at_T1_L1 +0.33 bits.
This signature is exactly what a HARD one-hot attractor does to a soft-distribution
LM eval: T cannot smooth a delta function back to a useful predictive distribution.

## Hypothesis

If MH beta is the cause (symptomatic), softening beta should restore a soft attractor
and the arm should not collapse. If softening doesn't help (structural), the
collapse is from MH's iterative re-projection through E (objectives inverted on same W
per fact-finder analysis), and the path forward is cross-layer architecture, not a
hyperparameter fix.

## Cell design (5 arms x 3 seeds x word2vec sparse-bipolar text8 N_DIM=8192 V=4000 N_TRAIN=100k)

Arms vary only the MH beta knob (or omit MH cleanup entirely); all other config is
identical to A1 (cf-RPE + STDP + K=2 per bank). cf-RPE + STDP + K=2 plasticity is
held fixed = A1's K2 setup (chain-grade reproduced).

| arm                       | mh_cleanup | mh_beta | role                                              |
|---------------------------|------------|---------|---------------------------------------------------|
| ARM_BASELINE_NO_CLEANUP   | False      | n/a     | sanity rail (= A1 K2; should reproduce 7.1781)    |
| ARM_MH_BETA_0p5           | True       | 0.5     | very soft attractor                               |
| ARM_MH_BETA_1p0           | True       | 1.0     | mild attractor                                    |
| ARM_MH_BETA_2p0           | True       | 2.0     | moderate attractor                                |
| ARM_MH_BETA_8p0           | True       | 8.0     | reproduces A1 collapse (sanity rail = 7.8919)     |

Extended TEMP_GRID (wider than A1's [0.01..1.0]) to catch any new optimum that a
SOFTER MH might place outside A1's window:
  TEMP_GRID = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0]
LAMBDA_GRID = [0.1, 0.3, 0.5, 0.7, 1.0]   (META C7: excludes 0.0)
MH_ITERS = 3 (same as A1 -- iters NOT varied; beta is the variable)

## Pre-reg HARD bands (locked pre-smoke)

Sanity rails (provenance, fires only in run_mode=full):
- ARM_BASELINE_NO_CLEANUP   within +/-0.05 of A1 K2 ref 7.1781
- ARM_MH_BETA_8p0            within +/-0.10 of A1 FULL_JOINT ref 7.8919

Verdict bands (on best-performing MH-beta arm, ie min BPC across MH_BETA_{0p5,1p0,2p0}):

- **HARD_PASS**       best MH-beta arm BPC <= 7.05   (softer MH beats no-cleanup baseline by margin)
- **MIDDLE_BAND**     best MH-beta arm in [7.05, 7.15] (softer MH neutral; ~ no-cleanup baseline)
- **HARD_FAIL**       all MH-beta arms BPC >= 7.20   (softening doesn't help; structural collapse)
- **HARD_FAIL_PROVENANCE**  baseline drift >0.05 OR beta=8.0 drift >0.10
- **HARD_FAIL_LLM_CALL**    _LLM_CALL_COUNTER > 0

cv <= 0.05 across seeds REQUIRED on best MH-beta arm.

## Per-arm best_T tracking (Fix #28)

Report best_T per arm per seed in metrics. Decisive secondary signal:

- If softer MH beta arms keep best_T LOW (~0.02-0.05), the attractor still functions
  as a sharp cleanup at all betas tested -> structural collapse symptom.
- If softer MH arms have best_T sliding upward toward 1.0 as beta grows, this confirms
  the symptomatic diagnosis (beta drives the attractor sharpness).

## Decision tree

- HARD_PASS  -> A1 collapse is SYMPTOMATIC. Re-issue compose cells with beta in
                successful range; multi-knob compose still viable.
- MIDDLE_BAND -> Softer MH is neutral, not super-additive. Compose plateaus at K2
                 level. Cleanup is not load-bearing at smaller beta. Investigate
                 cleanup-with-different-target (cleanup on W rather than on logits).
- HARD_FAIL  -> A1 collapse is STRUCTURAL (objectives inverted; cleanup re-projects
                 through E in a way that destroys soft predictive distribution).
                 Path forward = cross-layer architecture (cleanup at a different
                 stage, or different cleanup primitive), not hyperparameter fix.

## Config

- N_DIM_TOTAL = 8192, K_BANKS=2 (N_DIM_PER_BANK=4096)
- VOCAB_CAP = 4000, N_TRAIN = 100_000, N_HELD = 20_000
- SEEDS = [7, 17, 23]
- Encoder: word2vec-google-news-300 -> Gaussian project -> L2 -> sparse-bipolar f=0.05
- Plasticity: cf-RPE + STDP (cfrpe_stdp), 1000 steps, batch 64, lr 0.5, stdp_w 0.5
- K=2 banks, gate_temp=0.5
- MH_ITERS = 3 (fixed; only beta varies)
- TEMP_GRID extended (above), LAMBDA_GRID per META C7
- Substrate-only invariant: _LLM_CALL_COUNTER == 0 mandatory

## Routing

remote_cpu_queue (CPU-bound; no GPU push permission for exp_dev)
timeout = 3600 s

## Cites

- experiments/exp_substrate_compose_fair_harness_cfrpe_hetplasticity_K2_modern_hopfield_cleanup_v1.py (A1 cell; reference impl)
- data/exp_substrate_compose_fair_harness_cfrpe_hetplasticity_K2_modern_hopfield_cleanup_v1/metrics.json (collapse provenance)
- notes/exp_dev_handoff_composition_collapse_drill_2026-06-24.md (drill diagnosis)
- META C7 (LAMBDA_GRID excludes 0.0)
- Fix #28 (per-arm metrics + best_T per arm)

## Disciplines adopted

- ASCII-only in script + prereg
- Fix #14 (one cell at a time)
- Fix #26 (predispatch_check: PROCEED; no prior MH-beta-sweep landings)
- Per-arm metrics + best_T per arm (Fix #28)
- A5 path-scoped commit (only this cell + prereg)
- --self-test + --smoke modes both supported
