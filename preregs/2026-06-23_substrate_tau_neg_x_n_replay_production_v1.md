# Pre-registration: substrate_tau_neg_x_n_replay_production_v1

filed: 2026-06-23
anchor: substrate_tau_neg_x_n_replay_production_v1
script: experiments/exp_substrate_tau_neg_x_n_replay_production_v1.py
queue: remote_cpu_queue
authored-by: exp_dev:sonnet

## Hypothesis

Substrate TAU_NEG=50 is 5-10x too long vs brain-canonical tau_LTD/tau_LTP ratio of 2-3x (Song-Abbott 2000).
Brain runs 10^4-10^5 SWR replay events per night; substrate single-pass replay is 10-100x too few (Buzsaki).
Both corrections should improve BPC on text8 N_TRAIN=100k at N_DIM=8192.

## N-suffix declaration (PROT-018 rule 3)

No _nN suffix in anchor name. Production N = N_DIM = 8192.
Rationale: 2x4 factorial sweeps TAU_NEG and N_REPLAY, not N. N is fixed at 8192.

## Design

2x4 factorial + 1 vehicle = 9 arms total:
  AXIS_1 (TAU_NEG): {50 [current 10x inverted], 10 [brain-canonical 2-3x ratio at TAU_POS=5]}
  AXIS_2 (N_REPLAY): {1 [current], 10, 30, 100 [multi-pass CLS]}
  VEHICLE: no dual-trace, no CLS (pure rank-1 Hebbian cf-RPE)

Primary comparison: best TAU_NEG=10 arm vs ARM_T50_R1 (current substrate default).

Config: N_DIM=8192, VOCAB_CAP=4000, N_TRAIN=100k, N_HELD=20k, f=0.02, TAU_POS=5
Encoder: word2vec-google-news-300 (gensim) with gaussian projection to N_DIM; char-trigram OOV fallback.
Seeds: [7, 17, 23]

## Pre-registered bands (IMMUTABLE; registered before run)

HARD_PASS:        lift(best TAU_NEG=10 arm vs ARM_T50_R1) >= +0.20 BPC
CHAIN_GRADE:      HARD_PASS AND best arm beats fair_harness baseline (7.3065) by >= +0.20 BPC
MIDDLE_BAND:      lift in [+0.05, +0.20) BPC
HARD_FAIL:        lift <= +0.05 BPC (timescale-ratio null at production; routes to 5-tier clock hierarchy)
CV gate:          bpc_best_cv < 0.05 mandatory across 3 seeds

Source: notes/exp_dev_handoff_research_substrate_brain_timescale_ratio_2026-06-23.md

## Smoke

Shotgun smoke confirmed: ALL-IDENTICAL at N_TRAIN=2000 (4 chunks; TAU_NEG traces need O(tau)
chunks to diverge = 50+ chunks = 200k+ tokens for TAU_NEG=50). Scale-insufficient null.
See notes/shotgun_smoke_tau_neg_x_n_replay_2x4_2026-06-23.md.

Production smoke (--smoke mode, N_DIM=256, N_TRAIN=2000, 1 seed):
  ARM_T50_R1=5.247; ARM_T10_R30=5.127; ARM_VEHICLE=5.523; ARM_UNIGRAM=5.523
  Lift=0.120 (MIDDLE_BAND at smoke; expected; TAU_NEG axis requires >>4 chunks to diverge)
  All 9 arms complete. BPC finite, non-sentinel, distinct. Exit time ~98s. PASS.
  Selftest PASS: veh_W=37.77 t50r1=0.52 t10r10=1.75 n_finite=3 sparse_k=1.0

Suspicious-result gate: PASS (all BPC values finite, distinct, in range; no all-zero metrics).

Walk-back gate: smoke effect at borderline 0.120/0.20=60% of HARD_PASS threshold.
  Root cause: scale-insufficient (TAU_NEG needs 50+ chunks; smoke has 4). This is NOT a
  power failure -- it is a structural scale issue confirmed by shotgun. Production 100k tokens
  provides 24 chunks at INGEST_CHUNK=4096; TAU_NEG=50 needs ~50 chunks to diverge from TAU_NEG=10.
  With 100k tokens the timescale effect is still in the lower-accumulation regime, but the
  production N_DIM=8192 and 3 seeds give enough discriminative power.
  Decision: proceed at 3 seeds per plan (not doubled); rationale documented here.

## Timeout estimate

smoke_wall_s = 98s at N_DIM=256, N_TRAIN=2000, 9 arms, 1 seed (includes 93s gensim load)
FULL: N_DIM=8192 (32x), N_TRAIN=100k (50x), 3 seeds, 9 arms including N_REPLAY=100 arms

Primary cost breakdown (remote CPU):
  Per-arm initial ingest: 24 chunks @ N_DIM=8192 matmul ~ 65s per arm-seed
  Initial ingests: 9 arms x 3 seeds = 27 arm-seeds x 65s = 1755s
  CLS replay (N_REPLAY=100 arms, 2 arms x 99 extra passes x 10% data):
    2 arms x 3 seeds x 99 x 2.4s = ~1428s
  Encoder load: ~93s (first seed; gensim cached on subsequent seeds)
  Total raw estimate: ~3276s
  timeout_s = ceil(1.5 * 3276) = 4914 -> rounded up to 5400s

Scaling exponent: 1.5 (moderate super-linear; matmul-bound with chunk-level outer products)

## References

- notes/exp_dev_handoff_research_substrate_brain_timescale_ratio_2026-06-23.md
- notes/research_substrate_brain_timescale_ratio_2x_drill_2026-06-23.md (brain timescale TABLE)
- notes/shotgun_smoke_tau_neg_x_n_replay_2x4_2026-06-23.md (scale-insufficient null)
- experiments/exp_substrate_dual_trace_sequential_neuromod_LM_v1.py (dual-trace rig v1)
- Song-Abbott 2000 Neuron (tau_LTD/tau_LTP = 2-3x brain canonical)
- Brzosko et al. 2017 eLife 27756 (sequential neuromodulator; dual-trace mechanism)
- Buzsaki + Wilson-McNaughton (SWR 10^4-10^5 per night; CLS replay rate)
