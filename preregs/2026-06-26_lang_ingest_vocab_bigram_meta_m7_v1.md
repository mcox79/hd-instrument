# Prereg: lang_ingest_vocab_bigram_meta_m7_v1

**Filed:** 2026-06-26
**Anchor:** `lang_ingest_vocab_bigram_meta_m7_v1`
**Script:** `experiments/exp_lang_ingest_vocab_bigram_meta_m7_v1.py`
**Queue:** `overnight_queue` (GPU; matmul-bound at V_TOK=8192 + N_PARTITIONS=64 + N_DIM=8192)
**Research drill:** `notes/research_language_ingest_drill3_pipeline_composition_substrate_native_2026-06-26.md`
**Handoff:** `notes/exp_dev_handoff_research_language_ingest_drill3_pipeline_composition_substrate_native_2026-06-26.md`

---

## Scientific question

Does substrate-native Path C ingest reproduce the n1_v3 bigram-gap-closure
signal (top1 = 0.4455 vs unigram 0.2757; +61.6% relative lift) on text8 with
NO Pythia / MiniLM / word2vec encoder? Uses the new Path C infrastructure
shipped commit `df8511e8`:

- `hdlab/lm_eval_harness.py` -- META_M7 top-K from raw scores (rigged-harness
  trap permanently impossible).
- `hdlab/token_vocab.py` -- deterministic-hash bipolar codebook;
  ENCODER_PROVENANCE = SUBSTRATE_NATIVE.
- `hdlab/bigram_gap_measurement.py` -- standardized substrate_top1 - word_bigram_top1.

## Arms (4)

| Arm | Encoder | Sequence binding | Cleanup | Question |
|---|---|---|---|---|
| ARM_A_NULL_UNIGRAM | none | none | argmax unigram | discriminator floor |
| ARM_B_BIGRAM_HRR | token_vocab bipolar | S matrix bigram | cosine codebook | Path C bigram LM |
| ARM_C_TRIGRAM_HRR | token_vocab bipolar | HRR depth=2 cue + S | cosine codebook | depth lift |
| ARM_D_CHAR_TRIGRAM_BIGRAM | char_trigram bag-of-HD | S matrix bigram | cosine codebook | encoder choice |

## Config (LOCKED)

```
V_TOK         = 8192
N_DIM         = 8192
N_PARTITIONS  = 64
SEEDS         = [11, 13, 19]
CORPUS        = text8 (data/text8_cache/text8.txt; 100MB ASCII Wikipedia)
N_TRAIN_FULL  = 16_000_000 tokens
N_EVAL_FULL   = 32_768 held bigram pairs
N_TRAIN_SMOKE = 200_000 tokens
N_EVAL_SMOKE  = 4_096 held pairs
ENCODER_PROVENANCE = SUBSTRATE_NATIVE
CORPUS_PROVENANCE_REAL = True
PATH_C_COMPLIANT = True
GPU_BATCH = 4096 (full) / 1024 (smoke)
```

META_M7 capacity-sensitive dims (N_DIM, N_PARTITIONS, V_TOK) identical
smoke vs full; only N_TRAIN / N_EVAL shrink.

## Pre-registered bands (LOCKED at module init)

```
HARD_PASS_TOP1_FLOOR      = 0.40   # best non-NULL arm absolute floor
HARD_PASS_LIFT_OVER_NULL  = 0.10   # best non-NULL - NULL_UNIGRAM
HARD_PASS_CV_CEILING      = 0.05   # per-seed cv on best arm
NULL_DISCRIMINATOR_CEIL   = 0.30   # NULL must HARD_FAIL else regime broken
MIDDLE_BAND_LOWER         = 0.30
MIDDLE_BAND_UPPER         = 0.40
```

- **HARD_PASS_CHAIN_GRADE_CANDIDATE:**
  best(ARM_B_BIGRAM_HRR, ARM_C_TRIGRAM_HRR) top1 >= 0.40 AND
  best - ARM_A_NULL_UNIGRAM top1 >= 0.10 AND
  per-seed cv on best arm <= 0.05 AND
  ARM_A_NULL_UNIGRAM top1 < 0.30.
- **MIDDLE_BAND_MEASURED_MECHANISM:** best non-NULL arm top1 in [0.30, 0.40).
- **HARD_FAIL:** best non-NULL arm top1 < 0.30 OR null_discriminator broken.

## Disciplines (load-bearing)

- **META_M7** (drill 3 Section 3.1): top-K from raw scores; BPC at every T in
  default grid `[0.05, 0.1, 0.2, 0.5, 1.0, 2.0]`; T_optimal auto-picked.
  saturation_flag + regime_check_passed per arm.
- **Path C** (substrate-native; zero LLM forward calls at inference): encoder
  hoisted to setup-only (codebook precompute once per seed).
- **BIAS-S band calibration** (master checklist): top1 + top5 reported per arm;
  per-seed cv computed; coverage of bigram baseline reported.
- **Fix #24 GPU dispatch must actually use GPU:** torch.cuda used for S matmul +
  scoring; gpu_max_mem_alloc_mb logged; batched ops; raises if full mode and
  cuda unavailable.
- **Fix #28 verify-per-arm metrics:** per_arm dict at metrics root with per-arm
  top1 / top5 / BPC / cv / regime_check_passed / saturation_flag.
- **PROT-021 checkpoint hygiene:** run_config = {"N": 8192, "run_mode": "full"}
  prevents smoke partials contaminating full.
- **PROT-022 formula self-tests:** T1-T7 at module init AND under `--self-test`.
  T7 (added 2026-06-25 OOM-fix): closed-form GPU peak projection at FULL
  N_DIM x V_TOK x N_PARTITIONS x GPU_BATCH x N_EVAL; hard-asserts projected
  peak <= 6144 MB safety margin under 8 GB total. Pre-fix would have been
  16384 MB (the OOM root cause); post-fix peak 2688 MB. Runtime gate in
  `_device_for_run` also queries torch.cuda.mem_get_info and refuses to
  start a seed if projected peak > free GPU memory.
- **OOM-fix architecture (2026-06-25; commit 1ea55da9):** S_parts kept
  CPU-resident; only ONE partition transferred to GPU at a time for matmul;
  Hebbian outer-product accumulation on GPU then back to CPU. Eval-time
  scoring partition-major (each S_part transferred once across batches that
  need it). predicted_full + cues_full GPU buffers ~1 GB each. S_parts +
  cb_t freed between ARM_C and S_parts_d build to bound CPU RAM peak at
  one S_parts set (16.4 GB).
- **ASCII-only:** no emojis; no em-dashes.

## Failure-class revival paths (pre-registered)

- ARM_B HARD_FAIL + ARM_D HARD_PASS -> char-trigram encoder is load-bearing;
  route Path C atomization to CharTrigramEncoder.
- ARM_B / C / D all HARD_FAIL -> cleanup failing at LM scale; compose with
  Modern Hopfield attractor (gap3 anchor) as basin-sharpening layer.
- NULL_UNIGRAM top1 >= NULL_DISCRIMINATOR_CEIL -> V_TOK too small;
  regime-not-discriminating; redispatch at higher V_TOK before any claim.

## Substrate-product implications

If HARD_PASS: substrate IS a glass-box LM at vocabulary scale 8192 with
substrate-native encoding (zero LLM at inference, zero LLM at ingest, full
audit trail per token); the bigram-gap-closure signal that n1_v3 demonstrated
on Wikipedia / Pythia is reproduced on text8 / Path C substrate-native.

## Cost estimate

- Smoke: ~3-5 min on GPU (200k train + 4k eval).
- Full: ~2-4 hr on GPU (16M train + 32k eval; matmul-bound across 3 seeds).

## Source authority

- Cell design: cell-author (exp_dev) per drill 3 handoff autonomy declaration.
- Pre-reg bands: cell-author per envelope-fail-band ownership.
- Infrastructure: testbed (commit df8511e8; 37 verification tests pass).
- Routing decision: USER directive (overnight_queue GPU per drill 3 prompt).
