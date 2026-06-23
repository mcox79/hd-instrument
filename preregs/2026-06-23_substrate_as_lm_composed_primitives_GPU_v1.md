# 2026-06-23 substrate_as_lm_composed_primitives_GPU_v1 -- COMPOSED PRIMITIVES

## Anchor
`substrate_as_lm_composed_primitives_GPU_v1`

## Status
- Prereg authored 2026-06-23 (exp_dev)
- Queue: `overnight_queue` (GPU, marsh@home)
- Timeout: 5400s (1.5h)
- Estimated wall: 30-60 min GPU

## Cell
`experiments/exp_substrate_as_lm_composed_primitives_GPU_v1.py`

## Why now (USER directive 2026-06-23)
This session validated multiple substrate primitives. Compose them in one
production-scale substrate-as-LM test and see if substrate-as-LM finally
beats unigram. Validated this session:
1. word2vec semantic encoder (Spearman 0.6 vs human; clean methodology)
2. Lock-in amplifier noise rejection (16x lift; chain-grade-eligible)
3. HRR contextual binding (mechanism real; depth-lossless involutive bind)
4. Working memory HRR-slots (recall=1.000 across K=2..16)
5. Sparse-bipolar bundle (20-300x capacity lift per just-landed drill)
6. Per-layer cleanup (substrate primitive)

## Hypothesis
Previous substrate-as-LM tests (BPC 7.864 = 0.126 above unigram) used
char-trigram encoder + DENSE bipolar + NO context + NO lock-in. With ALL
validated primitives composed properly, BPC should beat unigram and
approach bigram (~6.6).

## Arms (5; each builds FRESH W per arm; clean methodology)
1. **ARM_UNIGRAM** -- analytic baseline BPC=7.738 reference
2. **ARM_CHAR_TRIGRAM_DENSE_NO_CONTEXT** -- worst-case substrate;
   reproduces ~11.6 raw BPC
3. **ARM_WORD2VEC_DENSE_NO_CONTEXT** -- Path A baseline (~7.87 BPC ref)
4. **ARM_WORD2VEC_SPARSE_BIPOLAR_CONTEXT_5** -- word2vec encoder +
   sparse-bipolar f=0.05 + HRR context bind 5-word window
5. **ARM_WORD2VEC_SPARSE_LOCK_IN_CONTEXT** -- word2vec + sparse-bipolar +
   lock-in amp at freq=pos*31 for positional encoding + HRR bind (the
   FULL composition; DECISIVE arm)

## Config (PRODUCTION SCALE GPU)
- V=4000 vocab, N_TRAIN=100_000 text8 tokens, N_HELD=20_000
- N_DIM=8192, seeds=[7,17,23]
- All ops via torch.cuda (Fix #24)
- INGEST_CHUNK=4096, RECALL_BATCH=256
- LAMBDA_GRID=[0.0, 0.1, 0.3, 0.5, 0.7, 1.0]
- SPARSE_BIPOLAR_F=0.05, CONTEXT_WINDOW=5, LOCK_IN_FREQ_STEP=31

## Pre-reg HARD bands
- **HARD_PASS:** `ARM_WORD2VEC_SPARSE_LOCK_IN_CONTEXT` BPC < 7.5 AND cv <= 0.05.
  Substrate-as-LM finally works via composed primitives; chain-grade
  substrate-as-LM evidence; closes V2 LM gap.
- **HARD_FAIL:** `ARM_WORD2VEC_SPARSE_LOCK_IN_CONTEXT` BPC >= 7.738.
  Substrate-as-LM still can't beat unigram even with ALL primitives
  composed; substrate W matrix is the fundamental bottleneck; V2 LM gap
  CLOSED as scope-narrow. Pivot to architectural rewrite or descope.
- **MIDDLE_BAND:** BPC in (7.5, 7.738). Composed primitives lift over
  dense baselines but don't cross unigram floor; characterize
  encoder-vs-W bottleneck.

## Sanity self-tests (in cell --self-test)
- T1 char-trigram bipolar; T2 sparse-bipolar primitive (exact non-zero
  count + uniq={-1,0,1}); T3 HRR bind commutativity (circular convolution);
  T4 lock-in positional vector L2-norm and position-distinguishing;
  T5 random-role baseline; T6 context-keys shape/norm; T7 fresh W
  builder; T8 log-linear endpoints (lambda=1 -> raw substrate;
  lambda=0 -> unigram); T9 verdict bands HP/HF/MID; T10 unigram
  analytic; T11 LLM-call counter zero.

## Routing rationale
- GPU REQUIRED per Fix #24 (torch.cuda for matmul/roll/bind at N_DIM=8192).
- Estimated 30-60min GPU wall at 100k tokens x 5 arms x 3 seeds.
- Timeout 5400s = 1.5h buffer; under PROT-019 floor of 21600s only because
  this is _GPU_v1 not _n8192_ suffix (intentional -- N_DIM is config not
  anchor name); the script's N_DIM=8192 is enforced via this prereg, not
  PROT-018.
- PROT-021: timeout < 14400 so no checkpoint-import required, BUT cell
  uses `_seed_checkpoint` anyway for per-seed resume on partial timeout.

## Cites
- experiments/exp_fresh_W_bpc_per_encoder_v1.py -- parent pattern (fresh W per arm)
- experiments/exp_encoder_word2vec_substrate_bind_v1.py -- word2vec primitive
- experiments/exp_lock_in_amplifier_hd_frequency_v1_FULL.py -- lock-in primitive
- experiments/exp_substrate_bipolar_hadamard_expansion_k8_v2.py -- sparse-bipolar
- USER 2026-06-23 compose-validated-primitives directive
- USER 2026-06-22 GPU dispatch must use GPU (Fix #24)

## Pre-dispatch
- predispatch_check: PROCEED (0 prior landings/atoms; 2026-06-23T pre-flight)
