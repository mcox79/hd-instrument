# PRE-REG: cleanup_floor_learned_encoder_v1

**Date:** 2026-06-23
**Author:** exp_dev (cell author; spawn-and-die)
**Cell:** `experiments/exp_cleanup_floor_learned_encoder_v1.py`
**Anchor:** `cleanup_floor_learned_encoder_v1`
**Queue routing:** local_cpu_queue (numpy CPU; <5min wall full expected)

## Role

META-INFORMER for cert ledger row 675:
`T3/META_cleanup_ceiling_shannon_floor_substrate_operating_envelope_sigma_leq_1p0`

Skunkworks tiered this META at MEASURED_MECHANISM (NOT chain-grade) 2026-06-23 because 3
branches remain untested. Branches #1 (N-DIM-scan, M=200, sigmas {1.0, 1.5, 2.0} across
N in {512, 1024, 2048, 4096, 8192, 16384}) and #2 (M-scan, M in {25, 50, 100, 200, 400})
already closed at SYNTHETIC RANDOM-BIPOLAR regime (M-INDEPENDENT; N_DIM-INDEPENDENT).

This cell closes BRANCH #3: LEARNED + STRUCTURED encoder keys. Does an anisotropic / structured
codebook escape the Shannon-floor at sigma=1.5 where random-bipolar fails (recall~0.027)?

NOT a chain-grade-candidate cell on own merits. Informer only -> status_log importance=HIGH
(META branch closure has chain-grade-tier implications for parent META).

## Motivation

Branches #1 and #2 closed at SYNTHETIC RANDOM BIPOLAR codebook. The actual substrate-product
use case uses LEARNED or STRUCTURED keys (encoder-derived, hub-spoke composition, etc).
Hypothesis: anisotropic / lower-dim-manifold codebooks may evade the noise floor if signal
geometry is partially orthogonal to isotropic noise -- noise direction at sigma=1.5 may not
fully corrupt structured signal.

Prior data:
- Random bipolar codebook at N=2048 M=200 sigma=1.5 -> recall~0.027 (Shannon-floor regime)
- ENC1 cell ARM_DENSE_N4096 was 0.027 (same floor at higher N)
- N-DIM-INDEPENDENT result from branch #1: floor persists at N=16384

This cell extends the META to LEARNED + STRUCTURED codebooks at the same N=2048 M=200
regime for direct comparison.

## Cell design

3 arms (load-bearing comparison), all at N=2048 M=200 N_EVAL=200 seeds={7, 17, 23}:

1. **ARM_RANDOM_BIPOLAR** -- random bipolar codebook (+/-1), L2-normalized. Reproduces parent
   Shannon-floor regime at N=2048 (expected recall ~0.027 at sigma=1.5 per prior N_DIM-scan
   data point).
2. **ARM_CHAR_TRIGRAM_LEARNED** -- codebook = `hdlab/char_trigram_encoder.CharTrigramEncoder`
   encoding of 200 English words from `data/datasets/conceptnet5_en_100k.jsonl` (deterministic
   subject/object token extraction, alphabetic+underscore, len 2-20, distinct). Substrate-native
   bag-of-char-trigrams sum-then-sign bipolar encoder. L2-normalized post-encode.
3. **ARM_HUB_SPOKE_STRUCTURED** -- 20 hubs x 10 spokes = 200 atoms. Each hub is a random
   bipolar vector at N=2048 with amplitude HUB_BIND_MAGNITUDE=1.0; each spoke = hub +
   gaussian perturbation of magnitude SPOKE_PERTURB_MAGNITUDE=0.5. L2-normalized post-compose.

All arms: same argmax-cleanup protocol (single-step cosine argmax over noised cue against the
codebook). Same noise injection (gaussian per N_DIM dim). Same query indices per seed.

Grid: 3 arms x 3 sigmas {1.0, 1.5, 2.0} x 3 seeds = 27 cells. Each cell is one (200,2048) @
(2048,200) matmul. Pure numpy. <5min wall full expected.

## Decision rules (NOT HARD_PASS / HARD_FAIL bands)

This cell informs META-scope; doesn't HARD_PASS/HARD_FAIL on its own. Discriminator sigma=1.5.
max_structured = max(ARM_CHAR_TRIGRAM_LEARNED, ARM_HUB_SPOKE_STRUCTURED) recall at sigma=1.5.

| Decision | Trigger | META implication |
|---|---|---|
| META_BRANCH3_SCOPE_NARROW | max_structured >= 0.20 | DOWNGRADE META scope_clause: "applies to random-bipolar codebook only"; substrate-product at sigma=1.5 VIABLE with right encoder |
| META_BRANCH3_CHAIN_GRADE_ELIGIBLE | ALL 3 arms recall(sigma=1.5) < 0.10 | STRENGTHEN META; floor robust across RANDOM+LEARNED+STRUCTURED codebook types; RECOMMEND Skunkworks tier-up to chain-grade |
| META_BRANCH3_MIDDLE | Neither rule fires (one arm in [0.10, 0.20)) | Encoder-quality-vs-noise-tolerance map; nuanced scope-clause needed |
| HARD_FAIL | sigma=0 sanity recall < 0.99 for any (seed, arm) | Implementation bug (codebook L2-norm or argmax broken) |

## Sanity self-test (mandatory pre-dispatch; T1-T9)

- T1: each arm builder produces (M=200, N=2048) L2-normalized codebook
- T2: clean cue (sigma=0.0) recovers >=0.99 for ALL 3 arms
- T3: very-high noise (sigma=20) << 0.5 for all 3 arms
- T4: hub-spoke same-hub cosine > cross-hub cosine (structural integrity)
- T5: char_trigram distinct-word rows have off-diagonal sim < 0.99 (codebook discriminates)
- T6: compute_verdict returns SCOPE_NARROW on synthetic (char_trigram=0.30, random=0.03, hub_spoke=0.05)
- T7: compute_verdict returns CHAIN_GRADE_ELIGIBLE on synthetic (all arms 0.05)
- T8: compute_verdict returns MIDDLE on synthetic (one arm 0.15, others <0.10)
- T9: sanity-violation triggers HARD_FAIL
- _LLM_CALL_COUNTER == 0 after selftest (substrate-only-decode gate)

## Pre-flight discipline checklist

1. `tools/predispatch_check.py cleanup_floor_learned_encoder_v1` PROCEED (verified -- 0 prior landings, 0 prior atoms)
2. ASCII-only print + verdict_msg (cell-author verified)
3. Pre-reg note (this file) committed BEFORE dispatch (will commit before queue_add)
4. ship_name uniqueness: `cleanup_floor_learned_encoder_v1` is new (predispatch_check landings=0)
5. Per-seed checkpoint via `_seed_checkpoint` (write_partial_key per seed)
6. atexit + SIGTERM synthesizer to metrics.json (covers any kill mid-run)
7. REQUIRED_FIELDS verified in smoke metrics.json: verdict, verdict_msg, elapsed_s, summary
8. MANDATORY post-landing: `tools/peek_arm_metrics.py <metrics.json>` BEFORE writing verdict_msg
   framing (Fix #28 remediation: read per-arm metrics, never propagate verdict_msg framing
   without checking per-arm numbers)

## Honest scope

- Closes branch #3 of 3. SCOPE_NARROW outcome means parent META gains scope_clause (still atomic);
  CHAIN_GRADE_ELIGIBLE means cell RECOMMENDS Skunkworks tier-up (the cert-owner makes the call,
  not this cell).
- N_DIM=2048 only; structured-arm behavior at higher/lower N untested in this cell. (Branch #1
  N-DIM-INDEPENDENT result on random-bipolar suggests robust extrapolation, but encoder-derived
  codebooks may have different N-scaling).
- ARM_CHAR_TRIGRAM_LEARNED uses conceptnet5_en_100k -> 200 English-word tokens (deterministic order).
  Not all "learned encoders"; just substrate-native trigram bag.
- ARM_HUB_SPOKE_STRUCTURED uses 20x10 specific composition; other structured types (tree, manifold-
  learned, gradient-trained) untested.
- Pre-reg interpretation matches USER specification verbatim.

## Cites

- cert_ledger row 675 (META atom under measured_mechanism tier)
- `preregs/2026-06-23_cleanup_floor_M_scan_v1.md` (branch #2 prereg)
- `preregs/2026-06-23_cleanup_floor_N_DIM_scan_v1.md` (branch #1 prereg)
- cleanup_floor_M_scan_v1 result: META_DECISION_M_INDEPENDENT
- cleanup_floor_N_DIM_scan_v1 result: META_DECISION_N_INDEPENDENT (or whichever fires)
- `hdlab/char_trigram_encoder.py` (substrate-native text-to-HD encoder)
- USER 2026-06-22 directive: empowered to experiment where lit-scan says dismissed; substrate's
  bet is on doing what's considered dead-end.
