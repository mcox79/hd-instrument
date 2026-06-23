# PRE-REG: att1_iterative_attractor_v2_low_storage_ratio_krotov_v1

**Date:** 2026-06-23
**Author:** exp_dev (cell author; spawn-and-die)
**Cell:** `experiments/exp_att1_iterative_attractor_v2_krotov_v1.py`
**Anchor:** `att1_iterative_attractor_v2_low_storage_ratio_krotov_v1`
**Queue routing:** local_cpu_queue (smoke + full; numpy CPU; very small N_DIM=512 M=50)
**Parent:** `att1_iterative_attractor_cleanup_v1` HARD_FAIL 2026-06-22

## Motivation

Per `notes/research_2x_revival_overnight_negatives_2026-06-23.md` (revival drill):

Parent v1 finding at N_DIM=512 M=200 (M/N=0.39, ABOVE Hopfield alpha_c~0.138):
all Ramsauer-softmax att1 arms plateaued at recall_harder=0.04 == argmax (best_att1_lift=0.000).
Verdict was HARD_FAIL "mechanism rejected as substrate-mine swap-in".

Revival hypothesis (2 axes the parent did NOT explore):
1. Parent was OVER-CAPACITY at M/N=0.39 (past linear-Hopfield envelope). Revival = test at
   M/N=0.10 (M=50, N=512), well below alpha_c.
2. Parent ONLY tested Ramsauer softmax variants (T=2, 4, 16); NEVER tested Krotov dense
   polynomial f(x)=x^n or f(x)=exp(beta*x) which give exponential capacity AND larger basin
   radius at finite T (Krotov-Hopfield 2016; Hopfield-Fenchel-Young arxiv:2411.08590).

USER 2026-06-22: "empowered to experiment where lit says dismissed".

If Krotov dense interaction lifts at low M/N, the att1 META primitive becomes substrate-mine
usable across n4 / n9 / n10 / p1 argmax-cleanup failures (all cap at one-shot argmax).

## Cell design

Substrate-native HD codebook (no encoder; substrate-only at inference by construction):
- N_DIM = 512
- M = 50  (M/N = 0.10, well below linear alpha_c ~ 0.138 -- KEY revival lever)
- N_EVAL = 200 query items
- 3 seeds {7, 17, 23}

Four arms:
| Arm | Mode | Krotov kind | kparam | Max steps |
|---|---|---|---|---|
| ARGMAX_BASELINE       | argmax       | -    | -   | 1 |
| ITER_KROTOV_QUADRATIC | iter_krotov  | poly | 2.0 | 8 |
| ITER_KROTOV_POLY      | iter_krotov  | poly | 4.0 | 8 |
| ITER_KROTOV_EXP       | iter_krotov  | exp  | 4.0 | 8 |

Sigmas: {0.5, 1.0, 1.5}; discriminator regime = sigma=1.5.
Basin sweep: {0.0, 0.5, 1.0, 1.5, 2.0} per arm.

Per-arm metrics: recall_at_1, mean_iterations, frac_converged, basin_robustness map.

## Pre-registered HARD bands (from handoff verbatim)

**HARD_PASS (chain-grade, ALL of):**
- best_iter_arm recall_harder >= 0.10 AND best_iter_arm lift_over_argmax >= 0.05 absolute at sigma=1.5
- cv across seeds <= 0.20
- substrate-only-decode gate: zero_llm_calls_at_inference = True

**HARD_FAIL (ANY of):**
- best_iter_arm recall_harder < argmax_recall_harder + 0.01 at sigma=1.5 (no benefit; lift < 0.01)
- substrate-only gate violated

**MIDDLE_BAND:** lift in [0.01, 0.05) (partial mechanism).

## Pre-flight discipline

1. --self-test: zero-noise identity per arm + high-noise random per arm + Krotov iters >=1
   + basin endpoints + compute_verdict on synthetic.
2. REQUIRED_FIELDS: anchor_name, verdict, verdict_msg, summary, elapsed_s, run_mode, n_seeds,
   detail, per_unit, zero_llm_calls_at_inference.
3. Per-seed checkpoint via _seed_checkpoint.
4. atexit/SIGTERM synthesizer to metrics.json.
5. ASCII-only (no unicode).
6. Smoke first (local_cpu_queue), then full (local_cpu_queue or remote_cpu_queue at N=4096
   if smoke shows >0.05 lift signal).

## Honest scope

- Substrate-native HD codebook (Gaussian, L2-normalized); does NOT test on real encoder-derived
  codebook (n4/n9/n10 keys). If v2 HARD_PASSes on substrate-native at low M/N, NEXT cycle
  swaps Krotov-iter in for argmax in n4/n9/n10/p1.
- Wall: ~30min CPU at N=512 M=50 N_EVAL=200 4 arms 3 seeds 5 sigmas basin sweep.
- 4 arms total (1 argmax + 3 Krotov variants); revival deflated P=0.35 per research handoff.
- If HARD_FAIL even in low-M/N + Krotov regime, mechanism is TRULY rejected (revival exhausted)
  -- route to next research drill.

## 2x-revival angle (if HARD_FAIL or MIDDLE_BAND)

- Finer kparam sweep (poly: 6, 8; exp: 2, 6, 8)
- Larger N_DIM (1024, 2048, 4096) keeping M/N=0.10 fixed
- Higher max_steps (16, 32) to test convergence rate
- Anisotropic codebook (post-whitening n10 keys) -- does Krotov help MORE on collapsed spectra

## Cites

- `notes/research_2x_revival_overnight_negatives_2026-06-23.md` (revival drill)
- `notes/exp_dev_handoff_research_2x_revival_overnight_negatives_2026-06-23.md` (handoff)
- Krotov-Hopfield 2016 NeurIPS "Dense Associative Memory"
- Ramsauer 2021 ICLR "Hopfield Networks Is All You Need"
- Hopfield-Fenchel-Young arxiv:2411.08590
- Parent: `notes/exp_dev_att1_iterative_attractor_pre_reg_2026-06-22.md`
