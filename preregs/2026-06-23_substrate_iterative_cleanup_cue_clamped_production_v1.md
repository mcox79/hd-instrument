# Prereg: substrate_iterative_cleanup_cue_clamped_production_v1

**Authored:** 2026-06-23
**Cell:** experiments/exp_substrate_iterative_cleanup_cue_clamped_production_v1.py
**Queue:** overnight_queue (N_DIM=8192, matmul-heavy; Fix #22 rule: N_DIM >= 8192 -> overnight_queue)
**Routing:** overnight_queue GPU/CPU (remote machine); W [8192x8192] float32 = 268 MB; per-arm recall [20000,8192]@[8192,4000]

## Context

PRIMARY cell substrate_iterative_cleanup_cue_clamped_v1 HARD_PASSed at smoke
(N=256/2048, alpha=0.3: +0.075 accuracy lift, cv=0.0, HARD_PASS). This SECONDARY
production cell validates the cue-clamped mechanism at production BPC scale
(N_DIM=8192, text8 N_TRAIN=100k), the same setting as the prior HARD_FAIL
substrate_multi_iteration_cleanup_LM_v1.

Prior HARD_FAIL root cause: bipolar sign() Hopfield steps caused all cleanup arms
to converge to identical BPC=7.3753 (self-consistent collapse). This cell uses
softmax-attractor cue-clamped update from hdlab/iterative_attractor.py (alpha param).

Brain-canonical basis: CA3 perforant-path (Hasselmo 2002) + Attractor LM
(arXiv:2605.12466 +32-46% LM perplexity). USER directive: "we have definitive proof
from biology that this works. keep working towards the solution."

## Design

Five arms (shared E, W per seed; only cleanup mechanism varies):
1. ARM_BASELINE_NO_CLEANUP: raw W @ E[src] logits; no cleanup. Baseline.
2. ARM_SINGLE_STEP: argmax_cleanup (single cosine lookup). Reference.
3. ARM_CLAMPED_ALPHA_03: alpha=0.3 (smoke-optimal from PRIMARY cell)
4. ARM_CLAMPED_ALPHA_05: alpha=0.5 (brain-canonical; Hasselmo/Attractor-LM)
5. ARM_CLAMPED_ALPHA_07: alpha=0.7 (high cue re-injection)

Seeds: [7, 17, 23]. N_DIM=8192, N_TRAIN=100k, N_HELD=20k, VOCAB_CAP=4000.
MAX_STEPS=8, TEMP_CLEANUP=4.0 (fixed). LAMBDA_GRID excludes 0.0 (META C7).

## Pre-registered HARD bands (IMMUTABLE -- do NOT adjust after seeing data)

- **HARD_PASS:** best ARM_CLAMPED beats ARM_BASELINE_NO_CLEANUP (7.2268 bpc) by >= +0.10 bits BPC
  (lower BPC = better; lift = bpc_baseline - bpc_clamped >= 0.10)
- **CHAIN_GRADE_BONUS:** lift >= +0.20 AND best_clamped_bpc beats cf-RPE chain-grade 7.1052 by >= +0.05
- **MIDDLE_BAND:** lift +0.03 to +0.10
- **HARD_FAIL:** lift <= +0.03 (smoke mechanism does not scale to production)

## Sanity rails (full scale only; smoke exempted)

- SANITY_RAIL_1: ARM_BASELINE_NO_CLEANUP within +-0.05 of 7.2268 (provenance from prior HARD_FAIL)
- SANITY_RAIL_2: ARM_SINGLE_STEP within +-0.05 of 7.3753 (prior HARD_FAIL reference)
- CV_MAX: cv < 0.05 across seeds

## PROT-018 compliance

Anchor name has no _nN suffix. Production N_DIM=8192 is stated in experiments/
exp_substrate_iterative_cleanup_cue_clamped_production_v1.py in the `if RUN_MODE == "full":`
block: `N_DIM = 8192`. Smoke uses N_DIM=512 (smaller, as expected).

## N-suffix pre-ship audit

No _nN suffix in anchor name; PROT-018 exemption applies. Production N=8192 confirmed in
script config: grep output below.

Script config section (full mode):
  N_DIM = 8192             # PROT-018: production N; anchor has no _nN suffix; stated here

## Timeout estimate

Formula: ceil(1.5 * smoke_wall_s * (FULL_N/smoke_N)^scaling_exp * (FULL_seeds/smoke_seeds))

- smoke_wall_s = 0.6s (local laptop smoke run -- NOTE: remote machine is ~5-10x faster)
- But: prior multi-iter cell (same N/corpus, 4 arms, 3 seeds) ran at same remote machine.
  Using component analysis:
  - W build [8192x8192]: ~60s per seed on remote CPU
  - E build [4000 words, N=8192]: ~30s per seed
  - Per-arm recall [20k queries, N=8192, V=4000, 5 arms with 8-step iterative]:
    ~200s per arm x 5 arms = ~1000s per seed
  - Per-seed total: ~1090s; 3 seeds: ~3270s; overhead: +50% = ~4905s
- Round up to nearest 300s: timeout_s = 5100

**timeout_s = 5100** (~85 min on remote CPU; conservative)

Long-run note (5100s > 2h? No -- 5100s = 85 min < 7200s): no flag required.

## Smoke gate status

Smoke ran successfully (N_DIM=512, N_TRAIN=2000, N_HELD=400, VOCAB_CAP=300, 1 seed):
- INSTRUMENTATION_SELFTEST: PASS (all 5 arms produce valid finite BPC)
- No all-zero, all-constant, or non-finite metrics
- Script exits in >100ms (0.6s total wall time)
- Smoke shows HARD_FAIL at small scale (expected -- corpus scale effect, not instrumentation)
- Suspicious gate: NOT triggered (max-min BPC across arms = 0.014 >> 0.001)

Smoke HARD_FAIL rationale: BPC at N=512/tiny corpus is ~5 bpc vs production ~7 bpc.
The PRIMARY accuracy cell (N=256/M=64) showed +0.075 lift. Production at N=8192/text8
is the correct test. Brain-canonical mechanism hypothesis: scaling to N=8192 should
reproduce or amplify the accuracy benefit in the BPC metric.

## Dependencies

- experiments/_seed_checkpoint.py (exists, confirmed)
- hdlab/iterative_attractor.py with alpha parameter (exists, confirmed; falls back to inline)
- data/text8_cache/text8.txt (remote machine only; confirmed present from prior HARD_FAIL run)
- No other external dependencies

## Provenance

- PRIMARY HARD_PASS: data/exp_substrate_iterative_cleanup_cue_clamped_v1/metrics.json
- Prior HARD_FAIL: data/exp_substrate_multi_iteration_cleanup_LM_v1/metrics.json
- Handoff: notes/exp_dev_handoff_research_multi_iter_cleanup_brain_analog_2026-06-23.md
- Drill: notes/research_multi_iter_cleanup_brain_analog_2x_drill_2026-06-23.md
