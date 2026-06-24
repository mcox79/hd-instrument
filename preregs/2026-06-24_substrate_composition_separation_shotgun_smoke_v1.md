# Pre-registration: substrate_composition_separation_shotgun_smoke_v1

**Date:** 2026-06-24
**Anchor:** substrate_composition_separation_shotgun_smoke_v1
**Queue:** local_cpu_queue
**N_DIM:** 2048 (smoke), **Seeds:** [7, 17, 23], **V:** 300, **N_TRAIN:** 20k
**Arms:** 9 (BASELINE_CFRPE_ALONE / NAIVE_CFRPE_PLUS_STDP / TIME_SEP / BANK_SEP /
SUBSPACE_SEP / FREQ_SEP / SEQUENTIAL_CONSOLIDATION / REPLAY_BASED /
ORTHOGONAL_PROJECTION)

## Scientific question

USER directive: "can't we shotgun smoke the composition question?" Tests 8
candidate separation strategies for cf-RPE x STDP same-W composition collapse
at smoke scale (V=300, N_DIM=2048, N_TRAIN=20k synthetic Zipf bigram) plus the
NAIVE reproduction control to confirm the collapse, plus the BASELINE cf-RPE-
alone reference. Goal: identify ANY arm with signal worth promoting to
production scale.

The intuitive frame is "5 chefs reaching into the same pot": the brain solves
this via separate pots per chef (bank separation), separate cooking times
(temporal separation), or replay-based consolidation. So far the substrate
program has tested ~3 separation strategies (NAIVE / SUBSPACE-ish via K=2 /
PCGRAD ANCHOR 2 in flight). This shotgun lights up 6 more in one cell.

If ANY arm shows signal at smoke, that arm gets promoted to production scale
+ becomes the next chain-grade-eligible architecture. If ALL fail at smoke
including PCGRAD-style ARM 9, the composition collapse is genuinely
fundamental and the program pivots to corpus-transfer or single-arm + Path C
encoder.

## Arms (9 total)

1. **ARM_BASELINE_CFRPE_ALONE** -- single W, cf-RPE updates only (reference;
   expected ~+0.22 BPC gap over Hebbian; smoke-scale calibration).
2. **ARM_NAIVE_CFRPE_PLUS_STDP** -- single W, simultaneous cf-RPE + 0.5*STDP
   updates (CONTROL: reproduces A1 sub-additive collapse at smoke).
3. **ARM_TIME_SEPARATION** -- single W, cf-RPE updates on EVEN training steps,
   STDP updates on ODD steps (no within-step overlap; sequential interleaving).
4. **ARM_BANK_SEPARATION** -- two W matrices (W_A: cf-RPE only; W_B: STDP only);
   both trained on full encoder; readout averages logits from both banks.
5. **ARM_SUBSPACE_SEPARATION** -- single W of shape (N_DIM, N_DIM); cf-RPE
   updates only the W[:N/2, :N/2] sub-block; STDP updates only W[N/2:, N/2:].
   Encoder uses full N_DIM; readout via full W.
6. **ARM_FREQ_SEPARATION** -- single W; per step, high-frequency context tokens
   (top-50% unigram freq) get cf-RPE update; low-frequency tokens get STDP.
7. **ARM_SEQUENTIAL_CONSOLIDATION** -- single W; phase 1 (N_STEPS/2): cf-RPE
   only -> freeze W; phase 2 (N_STEPS/2): STDP updates added on top of frozen
   W (no further cf-RPE).
8. **ARM_REPLAY_BASED** -- single W; cf-RPE LIVE updates each step. A replay
   buffer of recent (Ctx, Nxt) pairs accumulates; STDP updates ONLY on
   replayed buffer pairs (one-way; STDP never sees live data).
9. **ARM_ORTHOGONAL_PROJECTION** -- single W; per step compute g_cf and
   g_stdp gradients; project g_stdp_proj = g_stdp - (g_stdp dot g_cf /
   ||g_cf||^2) * g_cf; W += LR * (g_cf + 0.5 * g_stdp_proj).

## Pre-registered bands (smoke-scale)

**Sanity rails (must hold):**
- ARM_BASELINE_CFRPE_ALONE BPC within +/-0.20 of expected smoke cf-RPE baseline.
  Smoke V=300, N_TRAIN=20k -> cf-RPE-alone expected BPC ~5.5-7.0 (uniform =
  log2(300) = 8.23 bpc; cf-RPE typically lifts 1-3 bpc at smoke). Wide
  tolerance because smoke scale is not the cert config; rail validates that
  cf-RPE primitive is operational, not absolute numerical comparison to A1.
- ARM_NAIVE_CFRPE_PLUS_STDP BPC > ARM_BASELINE_CFRPE_ALONE BPC by >= 0.05
  (i.e. NAIVE compose REGRESSES vs cf-RPE alone, confirming sub-additive
  collapse reproduces at smoke scale). If NAIVE doesn't collapse at smoke,
  smoke is too small to discriminate -- flag as MIDDLE_BAND_SMOKE_TOO_SMALL.

**HARD_PASS_SIGNAL_FOUND (smoke success; promote to production):**
- ANY of ARM 3-9 BPC <= ARM_NAIVE_CFRPE_PLUS_STDP BPC - 0.10
  (separation strategy beats naive collapse by >= 0.10 BPC at smoke) AND
- That arm's BPC <= ARM_BASELINE_CFRPE_ALONE BPC - 0.03
  (separation also beats cf-RPE-alone by >= 0.03 BPC -- the separation
  isn't just "as good as cf-RPE alone" but actually super-additive at smoke)
- INTERPRETATION: that separation strategy works at smoke; promote to
  production (N_DIM=8192, V=4000, text8 N_TRAIN=100k, 3 seeds) for cert-grade
  test.

**MIDDLE_BAND_WEAK_SIGNAL:**
- Any arm beats ARM_NAIVE_CFRPE_PLUS_STDP by [0.05, 0.10) BPC
  (weak signal; worth investigating but not promotable as-is)

**MIDDLE_BAND_SMOKE_TOO_SMALL:**
- If ARM_NAIVE_CFRPE_PLUS_STDP does NOT exceed ARM_BASELINE_CFRPE_ALONE by
  >= 0.05 BPC, smoke scale is insufficient to reproduce the collapse, and
  no arm's "rescue" claim is interpretable. Re-author at larger smoke (or
  promote to production NAIVE-only to confirm collapse first).

**HARD_FAIL_DECISIVE (composition collapse is fundamental):**
- ALL of ARM 3-9 fail to beat ARM_NAIVE_CFRPE_PLUS_STDP by >= 0.05 BPC AND
  ARM_NAIVE_CFRPE_PLUS_STDP DOES collapse (i.e. is decisively > BASELINE).
- INTERPRETATION: composition collapse is fundamental at smoke scale;
  none of 7 distinct separation strategies (time / bank / subspace / freq /
  sequential / replay / orthogonal-projection) rescue it. Pivot to
  corpus-transfer (substrate-only without same-W composition) or to
  single-arm + Path C encoder.

**HARD_FAIL_PROVENANCE trip-wires (sanity gates):**
- ARM_BASELINE_CFRPE_ALONE BPC > log2(V) - 0.5 = 7.73 (cf-RPE not learning)
  -> HARD_FAIL_PROVENANCE (cf-RPE primitive broken at smoke; debug encoder)

**Discriminator reporting:**
- Per-arm BPC mean +/- std across 3 seeds (target cv <= 0.10 at smoke;
  smoke is signal detection not cert).
- Per-arm top1 acc (cross-check vs BPC; top1 can show signal where BPC
  is dominated by tail mass).
- Rank-order: which arms are top-3 by BPC? Which by top1? If discordant,
  flag for production cell to use both as discriminators.

## Calibration rationale

- The +/-0.20 rail tolerance for ARM_BASELINE_CFRPE_ALONE is wide because
  smoke V=300 N_DIM=2048 N_TRAIN=20k is FAR from the A1 production
  V=4000 N_DIM=8192 N_TRAIN=100k regime. The rail validates that cf-RPE
  PRIMITIVE is operational at smoke (not at-chance), not that it matches
  any specific number.
- The 0.05 collapse threshold for NAIVE > BASELINE is the smoke equivalent
  of A1's 0.116 production collapse (cf-RPE 7.0888 -> NAIVE 7.2044). At
  smaller smoke configs we expect weaker collapse signal but still
  measurable.
- The 0.10 HARD_PASS_SIGNAL_FOUND lift threshold (rescue beats naive by
  >= 0.10 BPC) is the smoke proxy for "production-promotable signal." A
  smoke arm beating naive by 0.10 BPC has a strong prior to also beat
  naive at production scale; an arm beating naive by < 0.10 at smoke
  has weak prior to translate.
- The +0.03 over BASELINE additional condition for HARD_PASS prevents
  "naive collapse fixed back to cf-RPE-alone level" from being claimed
  as a rescue. True rescue must SUPER-ADDITIVELY beat single best, not
  just recover.
- cv tolerance loosened to 0.10 from the standard 0.05 because smoke has
  fewer effective samples; signal detection is the goal, not chain-grade
  certainty.

## Critical disciplines

- **Fix #28 per-arm metrics**: each arm's BPC + top1 + n_steps + wall_s
  written to per_seed metrics; verdict NEVER trusts summary string, only
  per-arm numbers.
- **Fix #26 predispatch_check**: ran clean (0 matching landings; 0 matching
  atoms; RECOMMENDATION: PROCEED).
- **Fix #14 ONE cell**: 9 arms in one cell is acceptable for a shotgun
  signal-detection sweep; not 9 separate cells (would saturate spawn budget).
- **A5 path-scoped commit**: cell + prereg only; never git add -A.
- **ASCII-only**: all code, comments, output.
- **Pure numpy CPU**: no torch / no CUDA; smoke is local CPU dispatch.
- **Smoke uses clean synthetic data**: V=300 vocab from synthetic Zipf
  bigram (NOT substrate's existing atoms/labels). Encoder = bipolar
  random projection (no word2vec, no pretrained).
- **LAMBDA_GRID excludes 0.0** (per Skunkworks META C7).
- **Self-test BEFORE smoke**: assert cf-RPE shrinks error, STDP antisym
  invariant holds, Zipf cond-ent < log(V).

## Timeout estimate

Smoke target: under 40 min CPU wall total (9 arms x 3 seeds = 27 arm-seeds).

Per arm-seed wall:
- Encoder build (per seed): ~1s (synthetic Gaussian -> L2 norm for V=300, N_DIM=2048)
- Training: N_STEPS=300 * batch=32 * matmul (32 x 2048) @ (2048 x 2048) per step
  = 32 * 2048 * 2048 = 1.34e8 ops per step
  * 300 steps = 4e10 ops per arm-seed
  / ~3 GFLOPS CPU (conservative numpy single-thread) = ~14s per arm-seed
- Recall: N_HELD=2000, batch=128, ~2000 * 2048 * 300 = 1.2e9 ops = ~0.4s
- Total per arm-seed: ~15s
- Total: 9 arms x 3 seeds x 15s = ~405s = ~7 min
- Plus overhead (selftest, joint sweep T x lambda grid eval) = ~2 min
- Total wall estimate: ~9-12 min on CPU

Formula: ceil(1.5 * 12 min * 60) = 1080 seconds, round to 2700 (45 min) per
USER directive (gives 3x margin for slow CPU or zombie process contention).

timeout_s = 2700

## Why this is load-bearing

USER directly asked for shotgun on composition. The composition collapse
(A1: cf-RPE 7.0888 -> NAIVE 7.2044, +0.116 regress) is the load-bearing
blocker for substrate-as-LM at the bigram-floor regime. If any of these 7
new separation strategies show signal, the substrate program has a new
chain-grade-eligible architecture to develop. If none do, the program's
composition-stacking thesis is decisively refuted at smoke scale and the
pivot to corpus-transfer / single-arm becomes the rational next step.

## References

- `notes/director_composition_store_mine_inventory_2026-06-24.md` (60+ cells; 11 rules; 6 hypotheses)
- `data/exp_substrate_compose_fair_harness_cfrpe_hetplasticity_K2_modern_hopfield_cleanup_v1/metrics.json` (A1 collapse provenance)
- `data/exp_substrate_cfrpe_stdp_heterogeneous_superadditive_bigram_v1_n512/metrics.json` (heterogeneous superadditive at N=512)
- `preregs/2026-06-24_substrate_pcgrad_cfrpe_stdp_v1.md` (ANCHOR 2 PCGrad; related; ARM 9 is smoke equivalent)
- `experiments/exp_substrate_cfrpe_stdp_heterogeneous_superadditive_bigram_v1_n512.py` (cf-RPE + STDP primitive base; GPU torch)
- `experiments/exp_substrate_compose_fair_harness_cfrpe_hetplasticity_K2_modern_hopfield_cleanup_v1.py` (A1 reference; BPC harness)
- Yu et al. 2020 "Gradient Surgery for Multi-Task Learning" arxiv.org/abs/2001.06782 (PCGrad / ARM 9 source)
- McClelland et al. 1995 CLS (complementary learning systems / replay; ARM 8 source)
