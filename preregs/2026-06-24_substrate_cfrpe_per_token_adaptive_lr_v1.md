# Pre-registration: substrate_cfrpe_per_token_adaptive_lr_v1

**Date:** 2026-06-24
**Anchor:** substrate_cfrpe_per_token_adaptive_lr_v1
**Routing:** remote_cpu_queue (USER 2026-06-24 directive: "remote CPU is idle, refill")
**Motivation:** A6 audit identified that only ONE cf-RPE formula (fixed global LR=0.5 applied uniformly to all batch samples) has been tested in the substrate-LM stack. Per-token adaptive learning-rate schedules are UN-TESTED. Single-arm cf-RPE coarse @5000 steps showed +0.30 lift over fair_harness Hebbian (chain-grade border per Skunkworks). Per-token adaptive may close the remaining gap to clean chain-grade lift.

## Reference Cells (heritage)

- `experiments/exp_substrate_heterogeneous_plasticity_cfrpe_stdp_fair_harness_v1.py` -- the ARM_CFRPE_ONLY delta-rule implementation (lines 322-326) is the EXACT coarse rule.
- `experiments/exp_substrate_cfrpe_n_steps_curve_extension_v2.py` -- `build_W_cfrpe_gpu` lines 303-327; v2 testing N_STEPS asymptote at {5000, 7000, 10000, 15000}. v1's N=5000 produced best BPC 7.0386.
- `data/exp_fair_harness_substrate_as_lm_v1/metrics.json` -- ARM_SUBSTRATE_SPARSE_BIPOLAR baseline BPC=7.3065 (chain-grade cert row 473).

## Design

### Four arms

1. **ARM_HEBBIAN_BASELINE** -- one-pass rank-1 Hebbian; sanity rail at fair_harness 7.3065. Identical to ARM_HEBBIAN_ONLY in heritage cells.
2. **ARM_CFRPE_COARSE_5000** -- standard cf-RPE @ 5000 steps with GLOBAL LR=0.5 applied uniformly to all batch samples. The reference / coarse-rule arm. EXACT rule:
   ```
   error[i] = Nxt[i] - Ctx[i] @ W^T            # [batch, dim]
   dW       = (error^T @ Ctx) / batch
   W        = W + 0.5 * dW
   ```
3. **ARM_CFRPE_PER_TOKEN_ADAPTIVE** -- per-sample LR scales with prediction-error magnitude:
   ```
   error[i]    = Nxt[i] - Ctx[i] @ W^T
   e_norm[i]   = ||error[i]|| / sqrt(dim)       # per-sample RMS error (scalar)
   med         = median(e_norm)
   lr_per[i]   = 0.5 * clamp(e_norm[i] / med, 0.25, 4.0)
   weighted_err= error * lr_per[:, None]
   dW          = (weighted_err^T @ Ctx) / batch
   W           = W + dW
   ```
   Median-normalized so the BATCH-MEAN update magnitude stays comparable to the coarse rule. Clamped to [ADAPT_LR_FLOOR=0.25, ADAPT_LR_CEIL=4.0] to prevent runaway on outliers.
4. **ARM_CFRPE_PER_TOKEN_PLATEAU** -- per-token adaptive + global plateau-detection damping:
   - Same per-sample LR weighting as ARM_CFRPE_PER_TOKEN_ADAPTIVE.
   - Additionally tracks exponential-moving-average of batch_mean_err.
   - After every PLATEAU_WINDOW=200 steps, if EMA-error has improved by less than PLATEAU_TOL=0.001 relative to PLATEAU_WINDOW steps ago, multiply global_lr by PLATEAU_DECAY=0.5.
   - Decay-only invariant: global_lr can never increase (asserted in self-test ST5).

### Encoder + corpus

- word2vec-google-news-300 projected to N_DIM=8192, sparse-bipolar f=0.05 (production config; matches fair_harness baseline encoder).
- text8 corpus; N_TRAIN=100k tokens; N_HELD=20k tokens; VOCAB_CAP=4000.
- LAMBDA_GRID = [0.05, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0] (C7: excludes 0.0).
- TEMP_GRID = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0].
- SEEDS = [7, 17, 23] (3 seeds).
- N_STEPS_PLASTIC = 5000 for all cf-RPE arms (anchored to the v1 N=5000 best).
- INGEST_BATCH = 64; CFRPE_LR = 0.5 (same as heritage).

## Pre-registered HARD Bands (locked before dispatch)

| Band | Condition | Verdict |
|------|-----------|---------|
| Sanity rail | ARM_HEBBIAN_BASELINE BPC within +/- 0.05 of 7.3065 (full only) | gate; encoder-correctness |
| HARD_PASS | best adaptive arm lift >= 0.40 bits over ARM_HEBBIAN_BASELINE AND cv <= 0.10 | HARD_PASS |
| MIDDLE_BAND | best adaptive arm lift in [0.20, 0.40) | MIDDLE_BAND |
| HARD_FAIL | best adaptive arm lift <= 0.20 bits | HARD_FAIL (per-token doesn't add over coarse) |
| CHAIN_GRADE_BONUS | best adaptive arm BPC <= 6.85 | bonus flag (beats best known cf-RPE single-arm 7.0386 by >0.18) |

Best-adaptive-arm is defined as `argmax(lift_vs_hebbian)` between ARM_CFRPE_PER_TOKEN_ADAPTIVE and ARM_CFRPE_PER_TOKEN_PLATEAU.

cv = std(BPC) / mean(BPC) across the 3 seeds for the best-adaptive arm. cv > 0.10 downgrades to MIDDLE_BAND_HIGH_CV regardless of lift band.

## Smoke Results (2026-06-24)

- N_DIM=512, N_TRAIN=2000, VOCAB_CAP=300, N_STEPS_PLASTIC=200, seeds=[0], device=cpu.
- All 10 instrumentation self-tests PASS, including:
  - ST3 per-token LR ordering: high-error sample gets ratio=4.0, low-error gets 0.25 (ordered as expected).
  - ST5 plateau detection fires: after 200-step plateau window, plateau_hits=1 + final_global_lr=0.25 (= 0.5 * 0.5 = decay applied once).
  - ST6 adaptive W differs from coarse W with non-trivial magnitude.
- Smoke verdict: MIDDLE_BAND (best_adapt=ARM_CFRPE_PER_TOKEN_PLATEAU lift=0.362 at smoke scale).
- Smoke wall: 41.8s (encoder dominant).
- ARM_HEBBIAN_BASELINE bpc=5.1196; ARM_CFRPE_COARSE_5000 bpc=4.7211 (lift +0.40); ARM_CFRPE_PER_TOKEN_ADAPTIVE bpc=4.7769 (lift +0.34); ARM_CFRPE_PER_TOKEN_PLATEAU bpc=4.7576 (lift +0.36).
- hebbian_sanity_ok=False at smoke (expected: smaller N_DIM/V so the 7.3065 ref does not apply; gate is suppressed in smoke mode).

## Routing Decision

- **Routing: remote_cpu_queue** per USER 2026-06-24 directive ("remote CPU is idle, refill the queue").
- This is N_DIM=8192 matmul-dominant which would normally route to overnight_queue (Fix #22) but USER directive overrides for queue-refill purpose.
- Timeout: 3600s per Anchor 3 task spec. Per-seed checkpoint via `experiments/_seed_checkpoint.py` means restart-on-timeout safely resumes; total full run estimated at 2-3h CPU. If individual run hits the 3600s wall it resumes; worst-case 3 restarts to complete 3 seeds.
- PROT-018/019 not triggered (no `_n<NUM>` suffix in anchor name).

## C7 META Compliance

LAMBDA_GRID excludes 0.0. Post-hoc LAMBDA_ZERO_COLLAPSE flag detects if any arm selects the grid minimum (0.05) as best (diagnostic, not FAIL).

## Discriminator Honesty

- Three NON-ADAPTIVE arms vs two ADAPTIVE arms makes this a 3-way discriminator (Hebbian / coarse-cfrpe / per-token-adaptive-family). HARD_PASS requires per-token to lift by >= 0.40 BPC over baseline, and the coarse arm provides a within-cell reference (lift_vs_baseline for coarse can be compared to lift_vs_baseline for the per-token arms to isolate the per-token contribution).
- If best_adapt_lift >= 0.40 AND coarse_lift < 0.40, per-token mechanism is the dominant lever.
- If best_adapt_lift >= 0.40 AND coarse_lift >= 0.40 (similar magnitude), per-token does NOT add over coarse cf-RPE (HARD_FAIL band on the mechanism-claim; possible MIDDLE_BAND on the substrate-as-LM claim if both arms beat baseline).
- discriminator interpretation pathway also notes if all 3 cfrpe arms cluster within +/- 0.05 BPC of each other (per-token weighting is null).

## What This Does NOT Show

- Does not test cf-RPE x STDP heterogeneous compose (heterogeneous_plasticity covers that).
- Does not test N_STEPS scaling effects (n_steps_curve_v2 covers that).
- Does not test generalization beyond text8 / word2vec encoder.
- Does not test alternative per-token formulations (e.g. softmax-weighted error rather than median-clamped ratio).
- Does not test interaction with cleanup / autoregressive generation.

## Cites

- `experiments/exp_substrate_heterogeneous_plasticity_cfrpe_stdp_fair_harness_v1.py` (heritage cf-RPE rule)
- `experiments/exp_substrate_cfrpe_n_steps_curve_extension_v2.py` (N_STEPS asymptote context)
- `data/exp_fair_harness_substrate_as_lm_v1/metrics.json` (baseline 7.3065)
- `data/exp_substrate_cfrpe_per_token_adaptive_lr_v1_smoke/metrics.json` (this cell's smoke result)
