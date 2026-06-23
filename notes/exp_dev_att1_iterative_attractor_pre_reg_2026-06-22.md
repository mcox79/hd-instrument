# PRE-REG: att1_iterative_attractor_cleanup_v1 (META primitive cell; brain-mech 5)

**Date:** 2026-06-22
**Author:** exp_dev (cell author)
**Cell:** `experiments/exp_att1_iterative_attractor_cleanup_v1.py`
**Primitive:** `hdlab/iterative_attractor.py` (NEW; committed same cycle)
**Anchor:** `att1_iterative_attractor_cleanup_v1`
**Queue:** `remote_cpu_queue` (numpy-only; CPU bound; no GPU benefit)

## Motivation

USER directive 2026-06-22: "intrigued by systems that mimic the brain in conjunction with HD"
+ "empowered to experiment where lit says dismissed".

Per `notes/research_brain_mechanism_x_HD_broad_exploration_drill_2026-06-22.md` (broad-exploration
drill ranking 12 brain mechanisms across HD-fit, applicability, novelty):
- Top P_deflated = 0.42 (TEST A — `att1_iterative_cleanup_v1`).
- KEY INSIGHT from drill: "iterative-attractor-style cleanup is the convergent answer across
  4+ brain mechanisms (CAN bumps + DG-CA3 completion + ring attractors + dense associative
  memory) and is the highest-leverage missing-primitive for the substrate's repeated argmax-
  cleanup failures (n4 / n9 / n10 / p1 partials)".
- Modern-Hopfield theory (Ramsauer 2021 ICLR; Saxena & Bartlett 2024 arXiv:2212.01196)
  proves: iterative softmax-attractor over codebook gives exponential effective capacity
  vs single-step argmax.

The substrate currently uses single-step argmax for cleanup. This cell tests whether
substituting iterative soft-attractor dynamics (the brain's mechanism + the published-theory
analog) unblocks the repeated argmax-cleanup failure mode WITHOUT changing encoders, codebook,
or storage — just the cleanup operator.

## NEW PRIMITIVE: `hdlab/iterative_attractor.py`

Substrate-native iterative attractor cleanup:
- `iterative_cleanup(query, codebook, *, temp, max_steps, tol, return_trace)`
  - state_{t+1} = renormalize(softmax(temp * (state_t @ codebook.T)) @ codebook)
  - Convergence: ||state_{t+1} - state_t|| < tol * sqrt(D)
- `argmax_cleanup(query, codebook)` — single-step reference (the substrate baseline)
- `attractor_basin_robustness(codebook, target_indices, noise_sigmas, ...)` — noise sweep
- Forward-only; no backprop; numpy-native; substrate composable.
- High-temp 1-step recovers argmax exactly (CAN-FAIL anchor; T3 selftest asserts).

Composes back into:
- n4 within-concept floor cleanup (replace argmax over k-WTA-VQ codebook)
- n9 sparsemax decode (iterate the sparsemax-attractor; current is 1-step)
- n10 whitening rescue (iterative cleanup over whitened-projected codebook)
- p1 phase-action (iterative cleanup at any phase position)
- KGStore retrieval pipeline (score_all + argmax → iterative_cleanup)
- SubstrateGenerator (`_cleanup` step)

## Cell design

Substrate-native HD codebook (no encoder; substrate-only at inference by construction):
- N_DIM = 4096 (matches n4 / p1 line)
- M = 1000 codebook items (Gaussian, L2-normalized; "free" HD codebook per seed)
- N_EVAL = 200 query items sampled from codebook
- 3 seeds {7, 17, 23}

Four arms (CAN-FAIL discriminator):
| Arm | Mode | Temp | Max steps | Role |
|---|---|---|---|---|
| `ARGMAX_BASELINE` | argmax | n/a | 1 | substrate baseline; the CAN-FAIL anchor |
| `ATT1_SOFTATTRACTOR` | iterative | 4.0 | 8 | broad basin (default) |
| `ATT1_LOW_TEMP` | iterative | 2.0 | 8 | softer basin (more explore) |
| `ATT1_HIGH_TEMP` | iterative | 16.0 | 8 | sharper basin (closer to argmax but iterative) |

Two regimes (per pre-reg; absolute Gaussian std on pre-normalized cue):
- `NOISE_GENTLE = 0.5` — cue cosine to target ~0.89; sanity-anchor (argmax should still win)
- `NOISE_HARDER = 2.0` — cue cosine to target ~0.45; discriminator regime where argmax fails

Plus basin_robustness sweep `{0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0}` per arm × seed.

NOTE on noise scaling: noise added in absolute std (cue = cb[i] + sigma * eps then L2-normalized).
At D=4096 cosine-gap between random L2-normalized vectors is ~1/sqrt(D) ~ 0.016; argmax breaks
when cue-to-target cosine drops below ~2x the nearest-non-target cosine. At M=1000 this happens
around sigma >= 1.5-2.0 for isotropic Gaussian codebooks (calibrated via smoke).

NOTE on primitive scaling: `hdlab.iterative_attractor.iterative_cleanup` uses
`scale_by_sqrt_d=True` (default) so the effective softmax inverse-temperature is `temp * sqrt(D)`
(Ramsauer 2021 / Vaswani 2017 attention scaling). This makes the temp choices {2, 4, 16}
D-portable: at D=4096, effective beta = {128, 256, 1024}.

Per-arm metrics:
- `recall_at_1` (cleaned argmax == target codebook entry)
- `mean_iterations` (att1 cost; argmax = 1 by definition)
- `frac_converged` (att1 stability check)
- `basin_robustness` map: sigma → recall_at_1

## Pre-registered HARD bands (USER task spec 2026-06-22)

Discriminator = best ATT1 arm at NOISE_HARDER (sigma=0.30):

**HARD_PASS (chain-grade, ALL of):**
- best ATT1 arm `recall_at_1` >= ARGMAX_BASELINE + 0.10 absolute at sigma=0.30
- best ATT1 arm `basin_robustness@0.30` >= 2x ARGMAX_BASELINE @ sigma=0.30
- best ATT1 arm `frac_converged` >= 0.80 (stable convergence)
- best ATT1 arm `cv` across seeds <= 0.10
- substrate-only gate: `zero_llm_calls_at_inference = True` (enforced; HD codebook = no encoder)

**MIDDLE_BAND (MEASURED_MECHANISM):**
- best ATT1 arm lift in [0.03, 0.10) at sigma=0.30
  OR basin_ratio < 2x
  OR cv > 0.10 (seed-unstable)

**HARD_FAIL (ANY of):**
- ALL ATT1 arms `recall_at_1` <= ARGMAX_BASELINE in BOTH regimes (no benefit at gentle AND harder)
- NO ATT1 arm `frac_converged` >= 0.80 (mechanism unstable; doesn't converge)
- substrate-only gate violated (`zero_llm_calls_at_inference != True`)

## Pre-flight discipline (Section 7a + Director Fix 3 + Skunkworks disciplines)

1. **--self-test PASSES on .venv:** T1 zero-noise identity per arm + T2 low-noise per arm
   + T3 ATT1 iters >= 1 + T4 basin_robustness + T5 compute_verdict on synthetic + T6 hdlab
   primitive selftest. Smoke gate runs both `--self-test` and `--smoke` on local CPU first.
2. **REQUIRED_FIELDS metrics:** anchor_name, verdict, verdict_msg, run_mode, n_seeds, detail,
   per_unit, elapsed_s, summary, zero_llm_calls_at_inference, substrate_only_decode_gate.
3. **Per-seed runtime measurement:** measured via local-CPU smoke at N_DIM=512, M=200 before
   full dispatch; full N_DIM=4096, M=1000 wall extrapolated.
4. **CAN-FAIL discriminator:** ARGMAX_BASELINE is the anchor; if att1 doesn't beat it at
   sigma=0.30, mechanism is rejected (per pre-reg-direction-must-match-intent discipline; the
   directional claim is "iterative > one-shot"; if iterative <= one-shot, that's HARD_FAIL not
   MIDDLE_BAND).
5. **Substrate-only-decode gate:** HD codebook generated per-seed; no encoder/forward/generate.
   `_LLM_CALL_COUNTER = [0]` at module top; asserted in metrics.
6. **CONFIG_VERSION:** captures N_DIM, M, N_EVAL, SIGMA_SWEEP, arms, noise_gentle, noise_harder,
   tol, seeds, run_mode. Invalidates checkpoints if changed.
7. **Per-seed checkpoint:** imports `_seed_checkpoint`; partial write + resume per seed.
8. **Fix #11 TODO #6 in-cell smoke detection:** parses `HDLAB_EXP_NAME` for `_smoke` suffix as
   a fallback signal (the queue runner doesn't reliably honor `HDLAB_RUN_MODE` env passthrough).
9. **Fix #11 TODO #9 atexit/SIGTERM synthesizer:** writes metrics.json from partials on
   SIGTERM/timeout (n9 lesson).

## Discriminating controls

- High-temp 1-step att1 == argmax exactly (hdlab primitive T3 selftest). This is the
  "iterative-is-the-trick" verification: if HIGH_TEMP att1 (which has 8 max_steps but a sharp
  basin) lifts over argmax, iteration itself matters (not just softmax). If only LOW_TEMP
  helps, the lift is from soft averaging not iterative dynamics.
- frac_converged >= 0.80 control: catches the "doesn't converge" failure mode separately
  from the "converges but to wrong attractor" mode.
- Basin sweep across 5 sigmas: catches the case where att1 is ALL-OR-NOTHING vs ARGMAX (e.g.,
  helps at moderate noise but fails catastrophically at high noise).

## Honest scope

- Substrate-native HD codebook (Gaussian, L2-normalized); does NOT yet test on real encoder-
  derived codebook (n4/n9/n10 keys). If att1 HARD_PASSes on substrate-native, NEXT cycle
  swaps att1 in for argmax in n4/n9/n10/p1 (per task spec: "those revival cells become
  next-next-cycle priority with att1 swapped in for argmax").
- Tests cleanup-only; does NOT test downstream task accuracy (e.g., BPC, multi-hop QA). A
  substrate-mine swap into n4/n9/n10/p1 would close that loop.
- 4 temps tested; sweep is coarse. If MIDDLE_BAND, a finer temp sweep is the immediate revival.
- Random Gaussian codebook is the "easy" regime; real encoder-derived codebooks may be more
  anisotropic (the n10-whitening case) — att1 may help MORE on real data (broader basins
  from collapsed-direction artifact) or LESS (more attractor crosstalk).

## Estimated wall

- Single seed: ~10-20 min at N_DIM=4096 M=1000 (4 arms × 2 regimes × N_EVAL=200 = 1600 cleanup
  evaluations + 4 arms × 5 sigmas × 50 = 1000 basin trials). All numpy matmul; CPU-bound;
  remote_cpu_queue appropriate (numpy-only; no GPU benefit).
- 3 seeds: ~30-60 min total. Conservative timeout 7200s (2h; per Fix #11 TODO #8 wall budget).

## 2x-revival angle (if HARD_FAIL or MIDDLE_BAND)

Route to Research per USER STANDING (negatives → 2x-revival drill):
- Angle 1: finer temp sweep (1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 6.0, 10.0, 16.0)
- Angle 2: higher max_steps (16, 32) — convergence rate per max_steps
- Angle 3: warm-start att1 from argmax output (hybrid: argmax → 2-3 att1 refinement steps)
- Angle 4: anisotropic codebook (post-whitening n10 keys) — does att1 help MORE on collapsed
  spectra?
- Angle 5: per-cue adaptive temp (high-confidence cue → high temp; low-confidence → low temp)

## Cites

- `notes/research_brain_mechanism_x_HD_broad_exploration_drill_2026-06-22.md` (drill;
  P_deflated=0.42; top of broad-exploration)
- Saxena & Bartlett 2024 arXiv:2212.01196 "VSA Finite State Machines in Attractor Neural Networks"
- Ramsauer et al. 2021 ICLR "Hopfield Networks Is All You Need"
- Krotov & Hopfield 2016 NeurIPS "Dense Associative Memory for Pattern Recognition"
- Amari 1977 (CAN bumps); Treves-Rolls (DG-CA3 pattern completion); Skaggs-Knierim (ring attractors)
