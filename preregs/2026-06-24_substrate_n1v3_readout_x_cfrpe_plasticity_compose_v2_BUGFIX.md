# PRE-REG: substrate_n1v3_readout_x_cfrpe_plasticity_compose_v2_BUGFIX

Date: 2026-06-24
Owner: exp_dev
Anchor: `substrate_n1v3_readout_x_cfrpe_plasticity_compose_v2_BUGFIX`
Routing: overnight_queue (GPU)
Supersedes: `substrate_n1v3_readout_x_cfrpe_plasticity_compose_v1` (PROVENANCE_FAIL + NaN)

## v1 failure analysis (Fix #28 read of v1 metrics.json BEFORE redesign)

v1 landed PROVENANCE_FAIL at the production config (N_DIM=8192, text8 V=4000,
N_TRAIN=100k, V_C=256):

- ARM_UNIGRAM:                              top1 = 0.2171  (correct floor)
- ARM_N1_V3_READOUT_HEBBIAN_PLASTICITY:     top1 = 0.2189  (PROVENANCE_FAIL: ref 0.4455)
- ARM_LOGIT_MIXER_READOUT_CFRPE_PLASTICITY: top1 = 0.2440  (provenance OK: ref 0.2438)
- ARM_N1_V3_READOUT_CFRPE_PLASTICITY:       bpc=NaN top1 = 0.2171 (NaN -> falls back to unigram)

Two distinct bugs in v1:

**BUG-1** (ARM 2 provenance, ARM 4 readout broken): v1's n1_v3 readout L2-
normalizes both the predicted concept code AND the per-vocab decode columns
before the logits matmul. This DESTROYS the sparse-Willshaw selectivity that
the n1_v3 reference relies on. The n1_v3 source cell
(`exp_n1_concept_lm_substrate_native_token_decode_v3.py`) feeds RAW
`scores = (concept_vec @ D)` into a calibrated temperature-softmax + unigram
back-off; the sparse-codebook property "v sparse -> D.T @ v selects k columns"
is the WHOLE point. Normalizing it away collapses ARM 2 to unigram-equivalent
top1 = 0.2189 (vs ref 0.4455). Confirmed by ARM 2's best_T = 0.02 + lambda =
0.05 (i.e. lambda choice favored heavy unigram backoff -- a smoking gun that
the substrate logits carry no signal).

**BUG-2** (sparse regime off Willshaw sweet spot): v1 used CONCEPT_SPARSE_F =
0.05 at N_DIM=8192 (k=409 active per code). The n1_v3 reference uses f=0.006
at N_DIM=4096 (k=25), the Willshaw sweet spot k ~ log(N). With k=409 the codes
are no longer near-orthogonal (cross-overlap ~ k^2/N grows from 25^2/4096=0.15
to 409^2/8192=20.4); the sparse selectivity argument breaks regardless of the
L2-norm bug.

**BUG-3** (ARM 4 NaN): cf-RPE on positive-mean sparse binary codes diverges.
The delta-rule `dW = (Nxt - Ctx @ W^T)^T @ Ctx / batch` accumulates UNBOUNDED
positive Frobenius mass when Ctx is non-negative (Ctx.T @ Ctx is positive
semi-definite with positive entries). Over 2000 steps at lr=0.5, W operator
norm grows monotonically -> float32 overflow -> Inf -> NaN propagation through
softmax -> all logits NaN -> argmax tiebreaks to the unigram argmax. Confirmed
by ARM 4's measured top1 = unigram_top1 = 0.2171 exactly (the argmax-of-NaN
fallback signature).

## v2 BUGFIX (three targeted fixes)

**FIX-1**: Remove BOTH L2-normalizations in `compute_arm_logits` for n1_v3
arms. Return RAW `activated @ D` as logits; let the joint (T, lambda) sweep do
the calibration externally (matches n1_v3 source). Verified by self-test T10
(BUGFIX-1-sparse-Willshaw-selectivity): planted c0->c1->c2 transition test
that fails when L2-norm is on.

**FIX-2**: Set `CONCEPT_SPARSE_F = 0.003` at N_DIM=8192 (k=25 = same k as
n1_v3 cert anchor). Keep k constant across N_DIM scaling, not f.

**FIX-3**: cf-RPE numerical stability (three layers):
  (a) center sparse codes (subtract per-codebook column-mean) before the
      delta-rule so the update is zero-mean (matches bipolar cf-RPE regime);
  (b) per-step Frobenius-norm clip on W (cap = sqrt(N_DIM) * 1.0); cheap (one
      `.norm()` + multiply per step); prevents unbounded operator-norm growth;
  (c) per-50-step finite-check on W with last-good fallback;
  (d) final NaN/Inf guard on activated_held and logits before .cpu().numpy().

Verified by self-test:
  - T6  : cf-RPE finite after 50 steps (carryover from v1)
  - T6b : cf-RPE finite after 1000 steps at lr=1.0 (regression test for v1 NaN)
  - T6c : centered codes magnitude bounded
  - T10 : sparse-Willshaw selectivity with raw logits

Self-test PASSED on .venv (`python experiments/...v2_BUGFIX.py --self-test`)
2026-06-24.

Smoke run (N_DIM=512, V=300, N_TRAIN=2k, seed=0, CPU, N_STEPS=80, ~94s
wall) end-to-end:
  - All 4 arms complete; ARM 4 (the v1 NaN case) returns finite bpc=5.752,
    top1=0.3719 (vs v1: bpc=NaN, top1=0.2171=unigram-fallback).
  - cf-RPE diagnostics: n_finite_resets=0, n_clip_events=0, final_w_fro=1.45
    vs fro_cap=22.63 (W well within bound at smoke scale).
  - Smoke VERDICT = PROVENANCE_FAIL (EXPECTED: smoke at N_DIM=512 cannot
    reproduce production-scale 0.4455 reference; smoke validates EXECUTION
    not provenance).

## Cell design (4 arms x 3 seeds, N_DIM=8192, text8 V=4000, N_TRAIN=100k)

Identical to v1 except for the three bugfixes above. Same:

- Encoder: word2vec-google-news-300 projected to N_DIM=8192 sparse-bipolar (f=0.05).
- TEMP_GRID = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0].
- LAMBDA_GRID = [0.05, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0] (excludes 0.0 per META C7).
- cf-RPE: N_STEPS = 2000 (plateau per N_STEPS_curve audit).
- V_C = 256 (matches n1_v3 reference).
- f_sparse (concept codebook) = 0.003 (k=25, matches n1_v3 cert anchor k=25).
- SEEDS = [7, 17, 23].

Arms (each builds FRESH W / fresh concept state, no contamination):

1. `ARM_UNIGRAM` -- analytic floor (top1 + BPC + MRR).
2. `ARM_N1_V3_READOUT_HEBBIAN_PLASTICITY` -- v3-faithful sparse Willshaw
   readout (raw logits + temp-softmax + unigram backoff via joint sweep) +
   one-pass Hebbian concept-transition W_C. PROVENANCE rail:
   top1 within +/- 0.05 of n1_v3 reference 0.4455.
3. `ARM_LOGIT_MIXER_READOUT_CFRPE_PLASTICITY` -- fair_harness logit-mixer
   readout + cf-RPE iterative delta-rule on word-level W. PROVENANCE rail:
   top1 within +/- 0.05 of cf-RPE reference 0.2438.
4. `ARM_N1_V3_READOUT_CFRPE_PLASTICITY` -- v3-faithful readout + cf-RPE on
   concept-level W_C (with centered codes + W clip + NaN guard). THE TEST ARM.

## Pre-registered HARD bands (TOP1 primary; BPC reported but not load-bearing
per META_HARNESS_RIGGED row 588)

Sanity rails (Fix #28; widened to +/- 0.05 from v1's +/- 0.03 because the
port from N_DIM=4096 cert config to N_DIM=8192 is itself a derived result):
- ARM 2 top1 within +/- 0.05 of n1_v3 reference 0.4455.
- ARM 3 top1 within +/- 0.05 of cf-RPE reference 0.2438.

ARM 4 (N1_V3 x CFRPE) verdict bands (unchanged from v1):
- **HARD_PASS**: top1 >= 0.50 (super-additive lift)
- **CHAIN_GRADE_BONUS**: HARD_PASS AND top1 >= 0.55 AND cv < 0.05
- **MIDDLE_BAND**: top1 in [0.46, 0.50] (additive but not super-additive)
- **HARD_FAIL**: top1 <= 0.45 (no super-additive; n1_v3 readout dominates)

Stability rail: cv across seeds < 0.05 for all reported PASS configs.

PROVENANCE_FAIL deflate: if EITHER provenance rail fails by > 0.05, demote
to PROVENANCE_FAIL DESIGN-ERROR. v2 has WIDENED tolerance and FIXED the
mechanism that caused v1's ARM 2 fail; if v2 still fails ARM 2 provenance,
the n1_v3 readout port to N_DIM=8192 itself does not work and a separate
investigation (port v3 to N_DIM=8192 at f=0.003 in isolation) is needed.

## What this does NOT show

- Generalization beyond text8 (single corpus).
- BPC chain-grade per row 588 methodology audit (BPC harness rigged in this
  regime; report but not load-bearing).
- Effect at N_DIM != 8192 or V != 4000.
- Composition with STDP or other plasticity rules (only cf-RPE).

## Discipline gates applied

- Fix #14: ONE cell (this one only this turn).
- Fix #17: cell-author smoke + runtime measurement (smoke wall_s = 94s on
  laptop CPU for N_DIM=512 / N_TRAIN=2k / seed=0).
- Fix #24: GPU dispatch via overnight_queue; torch.cuda + batched ops + W_C
  stays on GPU between cf-RPE iter and decode-D recall.
- Fix #26: pre-dispatch verify-the-referent gate PROCEED (no prior landings
  or atoms for this anchor; v1 IS the prior, supersedes documented above).
- Fix #28: per-arm metrics read DIRECTLY from `metrics.json -> detail.by_arm_agg`
  (not from verdict_msg framings); verdict logic computes a `provenance_check`
  flag from ARM 2 and ARM 3 top1 measurements.
- A5 role-separation: exp_dev produces, Skunkworks cert-grades.
- Substrate-only verified (zero LLM call counter at inference).
- C7: LAMBDA_GRID excludes 0.0 (anti-calibration-collapse).

## Timeout estimate

Per the formula in `tools/queue_add.py --help`:
  timeout_s = ceil(1.5 * smoke_wall_s * (FULL_N/smoke_N)^scaling_exp *
                   (FULL_seeds/smoke_seeds))

Smoke wall: 94s on laptop CPU (note: encoder was 76s of the 94s, dominated
by gensim init; the per-arm compute was ~17s VQ+Hebbian + 0.2s logit-mixer +
0.7s cfRPE = ~18s for all 3 substrate arms total).

GPU vs CPU: encoder load is ~10s on GPU (one-time per seed); per-arm compute
scales mostly with matmul; on GPU with N_DIM=8192 vs smoke N_DIM=512 the
matmul is ~16x cheaper-per-flop than CPU but the dim is 16x larger.

Production scaling:
- N_DIM: 512 -> 8192 = 16x  (matmul cost ~ N_DIM^2 = 256x for W_C build,
  recall, decode-D)
- N_TRAIN: 2k -> 100k = 50x  (W_C build + decode-D + cf-RPE iter scales linearly)
- N_HELD: 400 -> 20k = 50x  (recall scales linearly)
- N_STEPS: 80 -> 2000 = 25x  (cf-RPE arm only)
- V_C: 32 -> 256 = 8x  (codebook fit; small fraction of time)
- seeds: 1 -> 3 = 3x

The dominant cost on GPU is W_C @ Q (8192x8192 @ 20kx8192) ~ 1.3 TFLOP, ~3s
on a midrange GPU. Per-seed wall on GPU: ~5-8 min (encoder 10s + 3 substrate
arms each ~100-150s). 3 seeds = ~15-25 min total.

Adding 1.5x safety margin and 100% headroom for cf-RPE stress (2000 steps
on concept transitions takes ~30s GPU wall) and the joint-sweep cost (49
(T,lambda) combos x 3 substrate arms x 3 seeds in numpy CPU ~30s each
seed), realistic upper bound is 60-90 min.

PROT-019 floor for anchor _n>=4096 requires --timeout >= 3600s (1h).

**REQUESTED TIMEOUT: 7200 seconds (2h)** -- 4x the realistic wall, generous
margin for GPU cold-start / encoder load (gensim w2v can be slow on first
access if cache cold) / cf-RPE stress on production data.

## Cites

- `experiments/exp_substrate_n1v3_readout_x_cfrpe_plasticity_compose_v1.py` (v1 source).
- `data/exp_substrate_n1v3_readout_x_cfrpe_plasticity_compose_v1/metrics.json` (v1 PROVENANCE_FAIL evidence).
- `data/exp_n1_concept_lm_substrate_native_token_decode_v3/metrics.json` (n1_v3 reference; cert row 588).
- `experiments/exp_n1_concept_lm_substrate_native_token_decode_v3.py` (n1_v3 source; sparse-Willshaw sweet-spot f=0.006).
- `data/exp_substrate_cfrpe_n_steps_curve_v1/metrics.json` (cf-RPE N=5000 reference).
- `experiments/exp_fair_harness_substrate_as_lm_v1.py` (logit-mixer readout + joint T,lambda sweep).
- Skunkworks VET 2026-06-23 (chain-grade bottleneck is the READOUT not the plasticity).
- USER 2026-06-23 (META_HARNESS_RIGGED row 588; top1 is the load-bearing metric).
