# 2026-06-23 fair_harness_substrate_as_lm_v1 -- METHODOLOGY-CORRECTED LM HARNESS

## Anchor
`fair_harness_substrate_as_lm_v1`

## Status
- Prereg authored 2026-06-23 (exp_dev)
- Queue: `overnight_queue` (GPU, marsh@home)
- Timeout: 7200s (2h safety margin)
- Estimated wall: 45-90 min GPU full

## Cell
`experiments/exp_fair_harness_substrate_as_lm_v1.py`

## Why now (Skunkworks methodology audit 2026-06-23)
Previous 7+ substrate-as-LM HARD_FAIL landings were METHODOLOGY-CONFOUND, not
mechanism failures. The harness used cosine-similarity logits with T=1.0 softmax
which produced near-uniform distributions (BPC mis-measured); separately, top-1
accuracy showed substrate WAS learning (0.2248 vs unigram 0.2171), but the bar
was BPC. The TEMP_GRID was too coarse ([0.5, 1.0, 2.0, 5.0]) and lambda was
swept sequentially rather than jointly with T.

This cell:
1. Extends TEMP_GRID to [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0] (down to peaked)
2. Sweeps (T, lambda) JOINTLY on dev; picks best joint config; evals on test
3. Reports THREE metrics per arm: BPC, top-1, MRR@10 (so substrate's strengths
   are visible even if BPC ranks unchanged)
4. Multi-metric HARD_PASS: ANY of BPC, top-1, MRR clears its bar
5. READOUT_DEGENERATE sanity gate: if raw_bpc_at_T1_L1 ~= -log2(1/V), flag the
   failure as readout-degeneracy not substrate-failure

## Arms (4)
1. **ARM_UNIGRAM** -- analytic floor (BPC=-Sum p log2 p; top-1=p_max; MRR=?)
2. **ARM_SUBSTRATE_WORD2VEC_DENSE** -- word2vec encoder + rank-1 Hebbian W (Path A current)
3. **ARM_SUBSTRATE_SPARSE_BIPOLAR** -- word2vec encoder + sparse-bipolar f=0.05 (validated)
4. **ARM_SUBSTRATE_BRAIN_COMPOSE** -- PC 3-layer + sparse + lock-in + WM HRR-slots (full compose)

## Config (PRODUCTION SCALE GPU)
- V=4000 vocab, N_TRAIN=100_000 text8 tokens, N_HELD=20_000
- N_DIM=8192, seeds=[7,17,23]
- Encoder: word2vec-google-news-300 (Path A reference; defensive gensim loader)
- GENSIM_CACHE_DIR=`data/gensim_cache_v2`
- All ops via torch.cuda (Fix #24)
- INGEST_CHUNK=4096, RECALL_BATCH=256
- TEMP_GRID=[0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
- LAMBDA_GRID=[0.0, 0.1, 0.3, 0.5, 0.7, 1.0]
- Joint (T, lambda) sweep on dev half; pick best joint (T*, lambda*); report on test

## Reported metrics per arm
- `bpc_best` (at best joint (T*, lambda*))
- `top1_acc` (at best joint (T*, lambda*))
- `mrr_at_10` (at best joint (T*, lambda*))
- `best_T`, `best_lambda`
- `raw_bpc_at_T1_L1` (sanity check; should be near -log2(1/V) if degenerate)

## Pre-reg HARD bands

### HARD_PASS (substrate-as-LM works under fair harness; chain-grade-eligible V2)
Any of:
- **HARD_PASS_BPC**: any substrate arm clears `bpc_best < unigram_bpc - 0.3` bits
- **HARD_PASS_TOP1**: any substrate arm clears `top1_acc > unigram_top1 + 2 * sigma_seeds`
- **HARD_PASS_MRR**: any substrate arm clears `mrr_at_10 >= unigram_mrr + 0.02` (~ meaningful)

### HARD_FAIL (substrate-as-LM genuinely fails even under fair harness)
ALL of:
- ALL 3 substrate arms fail HARD_PASS_BPC AND HARD_PASS_TOP1 AND HARD_PASS_MRR
- AND `raw_bpc_at_T1_L1` is NOT near `-log2(1/V) +/- 0.5` (so failure isn't readout-degeneracy)

### MIDDLE_BAND
Substrate beats unigram on at least one metric but doesn't cross HP bar.

### READOUT_DEGENERATE
If `raw_bpc_at_T1_L1` near `-log2(1/V) +/- 0.5` AND no substrate arm HP, classify as
`READOUT_DEGENERATE_NOT_SUBSTRATE_FAILURE` (NOT HARD_FAIL; requires harness re-calibration).

### Bonus
BRAIN_COMPOSE beats SUBSTRATE_WORD2VEC_DENSE on at least 2 of 3 metrics.

## Mandatory sanity self-tests (in cell --self-test)
- T1: char-trigram bipolar (defensive; not actually used at full but in selftest)
- T2: gensim mock-KV pipeline (load + project)
- T3: At T=0.01, substrate logits softmaxed on a single peaked input have max_prob > 0.5
- T4: At T=10.0, substrate logits softmaxed are near-uniform (max_prob < 0.01)
- T5: Joint sweep at (T=0.0001, lambda=0.0) reproduces unigram BPC (endpoint)
- T6: Joint sweep at (T=*, lambda=1.0) reports raw substrate (no fallback)
- T7: MRR@10 on planted 5-pair set (known values; reproducible)
- T8: Sparse-bipolar primitive (exact non-zero count + uniq={-1,0,1})
- T9: Verdict band classification (HP_BPC / HP_TOP1 / HP_MRR / HARD_FAIL / DEGEN / MIDDLE)
- T10: LLM call counter zero

## Routing rationale
- GPU REQUIRED per Fix #24 (torch.cuda for matmul / PC training / sparse-bipolar projection).
- Estimated 45-90 min GPU wall at 100k tokens x 4 arms x 3 seeds + 7x6=42 joint (T,L) points.
- Timeout 7200s = 2h buffer.
- PROT-021: timeout < 14400 so no checkpoint-import required, BUT cell uses
  `_seed_checkpoint` for per-seed resume on partial timeout (defensive).
- ANCHOR has no `_n<N>` suffix => PROT-018/019 not applicable.

## Cites
- experiments/exp_fresh_W_bpc_per_encoder_v2.py -- parent pattern (fresh W; word2vec)
- experiments/exp_substrate_brain_full_compose_LM_v2.py -- BRAIN_COMPOSE primitive stack
- experiments/exp_substrate_as_lm_composed_primitives_GPU_v1.py -- composition pattern
- Skunkworks 2026-06-23 methodology audit (cosine logits + T=1 = uniform; coarse TEMP_GRID)
- USER 2026-06-23 audit ratification (V2 LM gap; load-bearing for closure decision)
- USER 2026-06-22 Fix #24 (GPU dispatch must use GPU)
- USER 2026-06-22 Fix #26 (predispatch_check; PROCEED: 0 prior matching landings)

## Pre-dispatch
- predispatch_check: PROCEED (0 matching landings; 0 matching atoms; fresh anchor)
- Smoke target: < 180s laptop CPU under N_TRAIN=2000 N_DIM=512 V=300; exercises all
  4 arms + joint sweep + verdict assembly + 3 metric computations.
