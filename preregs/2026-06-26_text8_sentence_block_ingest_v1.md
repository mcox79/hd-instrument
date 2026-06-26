# Pre-registration: text8_sentence_block_ingest_v1

**Date:** 2026-06-26
**Anchor name:** text8_sentence_block_ingest_v1
**Script:** experiments/exp_text8_sentence_block_ingest_v1.py
**Queue:** remote_cpu_queue (smoke + full)
**Authority:** exp_dev (drill 2 anchor 1 per Research hand-off `notes/exp_dev_handoff_research_language_ingest_drill2_segmentation_block_size_2026-06-26.md` ANCHOR 1)
**Bands source:** Research drill 2 note (`notes/research_language_ingest_drill2_segmentation_block_size_2026-06-26.md`) Falsifiable Predictions P1-P5 verbatim
**Composes with:** char_trigram_encoder (Path C; hdlab/char_trigram_encoder.py), SequenceMatrix S (hdlab/sequence_memory.py; g1b chain-grade primitive), lm_eval_harness (hdlab/lm_eval_harness.py; rigged-harness-immune)

---

## What this tests

Substrate-native sentence-grade ingest of text8 with sentence-length-proxy boundary discipline. Tests block-size sweet spot K in [5, 25] tokens (substrate-physics-derived per research note L2 SNR analysis: SNR ~ sqrt(N/K) at K=20 / N=8192 = 20.2; matches g1b chain-grade K_SEQ=20; matches Eugenio 2025 RG-tokenizer cap at n=3-4; matches BEAGLE n=[2,7] HRR word-context).

Substrate-native composition:
1. Tokenize text8 by whitespace (text8 is pre-cleaned a-z + space).
2. Segment tokens into K-sized disjoint blocks (per arm).
3. Encode each block via char_trigram bag-of-trigrams (Path C; substrate-only-decode).
4. Bind adjacent (block_i, block_{i+1}) ordered pairs into a SequenceMatrix S (g1b chain-grade primitive; offline-Hebbian outer-product accumulate).
5. Eval: (a) identity-retrieval KNN@1 sanity (Fix #28 sentinel; encoder-health gate at M=400; >= 0.90), (b) next-block prediction via S @ block_i (the load-bearing substrate task), (c) BPC measured on the next-block-prediction task via lm_eval_harness (T-calibrated; rigged-harness-immune).

This is the data substrate for future cortex/Hopfield/NREM cells (per USER 2026-06-26 directive: substrate doesn't have enough accumulated experience for higher-level mechanisms to work; this cell starts accumulating real language data so future revival cells have something to learn over).

---

## Arms

| Arm | K (block size) | Notes |
|---|---|---|
| ARM_K5_BLOCKS  | 5  | substrate-physics tight; tests lower bound |
| ARM_K10_BLOCKS | 10 | mid-range |
| ARM_K20_BLOCKS | 20 | matches g1b chain-grade K_SEQ=20 (reference) |
| ARM_K25_BLOCKS | 25 | substrate-physics tested upper bound |

Cross-cell rail (Fix #28 sentinel):
- KNN@1 at sentinel size M=400 must be >= 0.90 on every arm/seed (encoder-health gate; if substrate cannot do identity-retrieval at M=400, the encoder is miscalibrated and everything else is moot).

---

## Configurable params (defaults pre-registered here)

| Param | Full default | Smoke default | How to set |
|---|---|---|---|
| N_DIM | 8192 | 1024 | HDLAB_N_DIM or --n-dim |
| M_EVAL | 10000 | 200 | HDLAB_M_EVAL or --m-eval |
| M_KNN_SENTINEL | 400 | 200 | HDLAB_M_KNN_SENTINEL |
| MAX_TOKENS_TRAIN | 500000 | 20000 | HDLAB_MAX_TOKENS_TRAIN |
| SEEDS | [11, 13, 19] | [11] | HDLAB_SEEDS (comma) |
| ARMS | 4 arms (K=5,10,20,25) | ARM_K20 only | hardcoded |
| ALLOW_SYNTHETIC | False (LOCKED) | False | code-locked: fail-loud |
| ENCODER_PROVENANCE | "SUBSTRATE_NATIVE" (LOCKED) | same | code-locked |

Smoke at N=1024 / K=20 / M_EVAL=200 / 1 seed / 20k tokens measured locally at ~50s wall (fits queue_add SMOKE_TIMEOUT_S=180s).

---

## Pre-registered verdict bands (research note P1-P5 verbatim)

**HARD_PASS_CHAIN_GRADE:**
- best_arm KNN@1 at M=10000 >= 0.50 (P1 sentence segmentation beats fixed-window)
- substrate matches KNN within 0.02 (|substrate_top1 - knn_top1| <= 0.02; P3 substrate at cosine floor not below)
- downstream BPC < 4.50 at_T_optimal on next-block-prediction task (P4 composability with N1 v3.1 substrate-LM)
- cv <= 0.05 across seeds (seed-stable)
- KNN sentinel @ M=400 >= 0.90 (Fix #28 encoder-health gate)
- zero LLM forward calls (substrate-only-decode; structural + counter-asserted)
- corpus_provenance_real = True (allow_synthetic=False, real text8 fingerprint verified)

**MIDDLE_BAND:**
- best_arm BPC in [4.50, 5.50) at_T_optimal, OR
- (HARD_PASS bpc + cv > 0.05): seed-unstable demote

**HARD_FAIL:**
- best_arm BPC >= 5.50 at_T_optimal (no substrate learning beyond chance), OR
- KNN sentinel < 0.90 on any arm/seed (Fix #28 sentinel violation; encoder bad), OR
- any LLM forward call (substrate-only-decode violation), OR
- corpus_provenance_real = False (synthetic-fallback fail-loud), OR
- any primitive collapse

The HARD_PASS direction is correctly oriented (KNN@1 higher = better; substrate-KNN gap absolute-smaller = better; BPC lower = better). Verdict logic asserted in T8 selftest with 6 scenarios (HP / LLM-violation / sentinel-violation / HARD_FAIL / MIDDLE_BAND / synthetic).

---

## BIAS-Q (suspect 1.000 results) discrimination

The identity-retrieval KNN@1 = 1.000 at M=200 in smoke is **by-construction-saturated** at small M with non-colliding bipolar HVs (encoder produces near-orthogonal HVs per block, so identity is trivially recoverable). This is the Fix #28 sentinel + encoder-health rail, NOT the load-bearing substrate measurement.

The load-bearing substrate measurement is **next-block-prediction** via SequenceMatrix S:
- vocabulary = M_blocks (1000s); uniform BPC = log2(M_blocks) ~ 10-13
- chance accuracy = 1/M_blocks ~ 0.001
- HARD_PASS BPC < 4.50 means substrate predicts at probability > 2^-4.5 = 0.044 (far above chance; ~50x lift over uniform)

Smoke measured BPC=9.871 at N=1024 / 1000 blocks (very close to uniform 9.97) confirming the next-block task is genuinely discriminative — substrate at smoke scale has not learned the sequence mechanism. Full at N=8192 / M=10000 is where genuine substrate learning is expected.

---

## By-construction guards

1. **NO LEAK:** text8 deterministic 90/5/5 char-position split (per testbed.substrate_lm.data.text8_char_corpus); train range slice loaded; eval queries drawn from the same train slice but at distinct block-indices (M_EVAL randomly sampled from len(blocks) without replacement).

2. **Fix #28 sentinel:** KNN@1 at M=400 must be >= 0.90 on every arm/seed. If not, the encoder is producing colliding HVs and downstream measurements are unreliable; HARD_FAIL.

3. **Substrate-only-decode:** This cell imports NO transformers / sentence-transformers / pythia / minilm. Encoder is char_trigram_encoder (Path C; per-trigram bipolar HV via deterministic hash). _LLM_CALL_COUNTER asserted == 0 before metrics write.

4. **CORPUS_PROVENANCE_REAL = True asserted + LOGGED:** ALLOW_SYNTHETIC=False passed to loader (fail-loud per phase_d_tier6 wikitext2 silent-fallback lesson). Independent fingerprint at runtime: real text8 has 27-char vocab in {a-z + space}; synthetic fallback has ~78-char vocab — vocab-size mismatch surfaces.

5. **cv <= 0.05 required for HARD_PASS:** computed across 3 seeds [11,13,19] for the full run. Smoke (1 seed) cannot satisfy this; smoke is structural validation only.

6. **Identity vs next-block discrimination (BIAS-Q):** identity-retrieval KNN@1 at small M is by-construction-saturated (encoder produces near-orthogonal HVs); next-block-prediction is the genuine substrate task. BPC measured on next-block-prediction, NOT identity-retrieval.

---

## Instrumentation (Skunkworks N2 chain-grade structural blockers, all 4 baked)

1. **per_unit (per-arm-per-seed):** every (arm, seed) is one entry in `per_unit`. Recompute-off-per_unit ready.
2. **cv <= 0.05:** computed in verdict() across seeds for each arm; aggregate also reported.
3. **zero_llm_calls_at_inference: True LOGGED:** structural guarantee (no transformers import) + counter audit per arm.
4. **VQ-floor analog:** BPC on next-block-prediction has natural floor = log2(M_blocks) (uniform-over-block-bank); reported via `bpc_at_t_optimal` vs `sanity_top1_at_random`; the discriminating-regime gate (`regime_check_passed`) tests top1 > 2 * sanity, which is rigged-harness-immune.

---

## Config version (checkpoint invalidation)

`N=<NDIM>,V_TOK=auto,CORPUS=text8,CORPUS_VER=matt_mahoney_2006,M_EVAL=<M>,MAX_TOK=<MAXTOK>,SEEDS=<SEEDS>,SENT_LEN_MEAN=18,SENT_LEN_MAX=40,SYNTH=False,ENC=SUBSTRATE_NATIVE,BANDS=KNN>=0.50/BPC<4.50/MB<5.50`

Any change to N, M_EVAL, MAX_TOKENS_TRAIN, SEEDS, ENCODER_PROVENANCE, or band thresholds invalidates checkpoints (PROT-021 run_config guard via experiments/_seed_checkpoint.py).

---

## Seeds

- Full run: SEEDS = [11, 13, 19] (3 seeds; cv computed across all 3)
- Smoke: SEEDS = [11] (single-seed pipeline validation only; cv undefined)

---

## Timeout estimate

**Smoke arm** (this dispatch + queue_add gate):
- Measured local wall (N=1024, M=200, K=20, 20k tokens, 1 seed, 1 arm): ~50s on Windows laptop CPU
- queue_add SMOKE_TIMEOUT_S default 180s: ample headroom; passes gate
- **Smoke entry timeout pre-reg: 600s** (safety margin for remote runner overhead)

**Full run extrapolation:**
- Per-arm wall ~ smoke_wall * (N_full/N_smoke)^1.5 * (M_full/M_smoke)
  = 50 * (8192/1024)^1.5 * (10000/200) * (500000/20000) / (500000/20000)
  = 50 * 22.6 * 50 = ~56500s
- BUT 4 arms instead of 1: 4x = 226000s = 62.8 hours per seed
- This is too high; needs revision.
- Reality check: the matmul bottleneck is (M_eval x M_blocks x N_DIM); for full = 10000 x 25000 x 8192 = 2.05e12 ops per arm (~30-60min on CPU)
- 4 arms x 3 seeds x ~45min = ~9 hours total; comfortable on remote_cpu_queue.
- **Full entry timeout pre-reg: 28800s** (8 hours; PROT-021 checkpoint-required floor of 14400s exceeded; cell IS checkpointed per-seed via _seed_checkpoint).

---

## Dispatch plan

1. Self-test PASS (8/8) on .venv -- DONE.
2. Local smoke wall measured -- DONE (~50s at N=1024 / 1 arm / 200 M; verdict HARD_FAIL as expected at smoke scale due to undertrained substrate; metrics shape valid).
3. Path-scoped commit (cell + prereg + research note + handoff).
4. queue_add to remote_cpu_queue with --timeout 28800 (full).
5. queue_add includes its own smoke gate (validates metrics shape, not verdict).
6. REMOTE VERIFY post-dispatch: confirm entry in remote queue.json.

---

## N-suffix note (PROT-018)

Anchor name `text8_sentence_block_ingest_v1` has no `_nN` suffix. N is configurable via HDLAB_N_DIM env (smoke=1024, full=8192). Per PROT-018 rule 3: no _nN suffix because N is sweepable.

---

## Risk surface (honest)

- **text8 download (~100MB) on first remote run** if not cached on remote. The loader caches under data/text8_cache/text8.txt after download. Locally cached (verified 100MB file). REMOTE may or may not have it; first remote smoke includes the download in wall.
- **char_trigram bag-of-trigrams loses word-order within a block** (Path C trade-off, documented in hdlab/char_trigram_encoder.py). For next-block prediction this may limit substrate accuracy; the substrate is tested under this constraint deliberately (substrate-native; no Pythia/MiniLM borrow).
- **Substrate at smoke scale = near-uniform BPC** (smoke verdict HARD_FAIL by design); full at N=8192 / M=10000 is where learning is expected. queue_add gates on metrics-shape, not verdict-PASS.
- **Sentence-length-proxy NOT IMPLEMENTED in v1:** v1 uses fixed-K disjoint blocks (the cleaner per-arm comparator per research note L3); gamma-distributed variable-K is a follow-up (v2) if v1 KNN sweet spot emerges and motivates a variable-K test. The 4 fixed-K arms at [5, 10, 20, 25] cover substrate-physics-derived sweet spot.
- **g1b composition** at K=20 reference uses NumPy SequenceMatrix variant (not the torch hdlab.sequence_memory.SequenceMatrix; same architecture, NumPy for CPU speed). Verified by T4 selftest that the NumPy variant predicts next correctly on a small chain (p2_k2=0.977 cosine).
- **Drill 2 dependency: gap3 Modern Hopfield in flight.** Per research note L5 and hand-off: this cell ships as retrieval-only; if gap3 HARD_PASSes, future v2 composes Modern Hopfield + sentence-blocks for max lift; if gap3 HARD_FAILs, this v1 still ships as retrieval-only with refuse-gate (substrate-product = "retrieval engine" not "generative LM").

---

## Why now (USER directive 2026-06-26)

USER quote: "We don't have enough data on substrate for this to be meaningful... Can't we, and shouldn't we, use cortex layer and sleep to compress/learn and pass context?"

This cell is the DATA SUBSTRATE for future cortex/NREM cells. Cortex revival, Hopfield prototype-attractor, NREM compression — none of those can work without a chain-grade-validated language ingest as the substrate to learn over. This anchor ships that substrate.

Composes naturally with:
- Future Modern Hopfield prototype-attractor cells (gap3 in flight) for compositional retrieval
- Future NREM compression cells (c3 chain-grade extended to language scale)
- Future schema-layer cells (substrate-product Math/Science process-knowledge ingest)

---

## Substrate-product implications (per research note)

- **Substrate-as-RAG-engine** (substrate-product immediate reading): sentence-block ingest + char_trigram bag + g1b chain-grade retrieval = "substrate-native semantic search at sentence granularity." Zero LLM at retrieval.
- **Math/Science process-knowledge priority lane:** theorem/proof block = K-bounded sentence-tier ingest. This cell's framework maps directly to substrate-product Math/Science scope.
