# Pre-registration: substrate_ACh_query_conditional_read_gain_LM_v1

**Date pre-registered**: 2026-06-23
**Role**: exp_dev
**Script**: experiments/exp_substrate_ACh_query_conditional_read_gain_LM_v1.py
**Queue**: remote_cpu_queue
**Routing**: USER explicit; gap #2 from substrate-mine modulator inventory

## Hypothesis

Brain ACh (acetylcholine) gain control multiplicatively scales READ signal magnitude
based on attention/confidence state (Yu-Dayan 2005; Goard-Dan 2009; Pinto-Goard 2013).
Substrate analog: per-query scalar gain on the predicted logit vector BEFORE temperature
application, conditioned on cosine_margin (ARM_MARGIN) or entropy (ARM_ENTROPY) of
the current logit distribution.

This is ORTHOGONAL to write-time excitability (HARD_PASS at K=1200, exp_excitability_gated_substrate_cpu_v1.py)
and to per-context temperature sweep (gap #1, cell a52c9350).

Brain prior: P_inherited=0.55; deflated to P=0.45 for substrate-native LM.

## PROT-018 N-suffix note

Anchor name has no _nN suffix. Production N_DIM=8192 per design.
Smoke N_DIM=512 for gate-validation only.

## Arms (4 total)

- ARM_UNIGRAM: analytic floor
- ARM_GLOBAL_READ_GAIN: sparse-bipolar + fair_harness sweep + global gain scalar
  (base_gain in {0.5, 1.0, 2.0, 4.0}). Replication gate: best BPC should be
  within 0.15 of fair_harness baseline 7.3065.
- ARM_PER_QUERY_GAIN_MARGIN: gain_i = base_gain * (1 + alpha * (1 - normalized_margin_i));
  low-margin (uncertain) queries get boosted gain to break ties.
- ARM_PER_QUERY_GAIN_ENTROPY: gain_i = base_gain * (1 + alpha * normalized_entropy_i);
  high-entropy queries get boosted gain.

## Pre-registered HARD bands (registered before any full run)

**HARD_PASS**: ARM_PER_QUERY_GAIN_MARGIN OR ARM_PER_QUERY_GAIN_ENTROPY beats
ARM_GLOBAL_READ_GAIN by >= +0.10 bits BPC mean across seeds.

**CHAIN_GRADE_BONUS**: lift >= +0.20 bits AND best per-query arm BPC < 7.3065
(beats fair_harness baseline).

**MIDDLE_BAND**: lift +0.03 to +0.10 bits.

**HARD_FAIL**: lift <= +0.03 bits OR per-query gain arms collapse to unigram
(READOUT_DEGENERATE: BPC >= unigram_bpc - 0.01), OR any_degen=True.

cv < 0.05 required on HARD_PASS arm.

## Calibration probe note

No prior empirical anchor for ACh READ-gain on substrate LM. Per calibration-probe policy:
bands are set at mechanism-effect level (not +-50% of theoretical point) because the
mechanism is either present (measurable lift) or absent (no lift), not an analog quantity
to predict theoretically. HARD_PASS threshold of 0.10 bits is conservative (~1/3 of
the fair_harness BPC improvement over unigram).

## Timeout estimate

Smoke wall: 51s (CPU; N_DIM=512, N_TRAIN=2000, 1 seed, V=300).
Full config: N_DIM=8192, N_TRAIN=100000, 3 seeds, V=4000.

Scaling factors:
  - N_DIM ratio: 8192/512 = 16 (matmul-bound for W build; O(N_DIM^2))
  - N_TRAIN ratio: 100000/2000 = 50 (linear for ingest)
  - Seeds: 3/1 = 3
  - Dominant cost is W matmul at N_DIM^2 + gain sweep (CPU numpy; linear in n_eval)

Smoke W build was ~0s at N_DIM=512 (negligible). Full W build at N_DIM=8192 via fair_harness
was ~1.2s per seed on GPU. On remote_cpu_queue (remote CPU, no GPU), matmul at 8192^2
is slower. Extrapolating from fair_harness per-seed CPU time of ~40s at N_DIM=8192:
  - Per seed cost (W build + logits + sweep): ~40s (W) + gain_sweep * 42*4*5 = 840 (T,L,G,A) combos
  - Gain sweep is pure numpy, very fast: ~0.1s per combo -> 84s per seed for sweeps
  - Total per seed estimate: ~130s
  - 3 seeds: ~390s
  - Margin factor 1.5: 585s

timeout_s = ceil(585) = 600 -> round to 900 (extra margin for gensim load + remote CPU)

Per role contract: < 2 hours -> allowed.

## Import chain check

- experiments._seed_checkpoint: exists (verified at smoke)
- tools.gensim_load_helper: exists (used by fair_harness successfully)
- numpy, torch: standard
- No other experiments/ imports
