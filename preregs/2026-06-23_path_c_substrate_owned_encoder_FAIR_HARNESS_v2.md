# 2026-06-23 path_c_substrate_owned_encoder_FAIR_HARNESS_v2 -- PATH C UNDER FAIR HARNESS

## Anchor
`path_c_substrate_owned_encoder_FAIR_HARNESS_v2`

## Status
- Prereg authored 2026-06-23 (exp_dev)
- Queue: `overnight_queue` (GPU, marsh@home)
- Timeout: 10800s (3h; PC training is the dominant cost; 73min observed in Path C v1)
- Estimated wall: 90-150 min GPU full (3 seeds * (PC train + 4-arm fair harness))

## Cell
`experiments/exp_path_c_substrate_owned_encoder_FAIR_HARNESS_v2.py`

## Why now (USER strategic principle 2026-06-23)
Path C substrate-owned PC encoder is THE substrate-product answer. Previous
Path C v1 (substrate_owned_predictive_coding_encoder_v1, 73min GPU) HARD_FAILed
under the OLD RIGGED HARNESS where ALL arms collapsed to lambda=0 (a log-linear
mixer mathematical artifact, NOT a substrate mechanism failure). Skunkworks
methodology audit 2026-06-23 ratified the diagnosis as METHODOLOGY-CONFOUND
(`META_HARNESS_RIGGED` atom, T3 cert tier).

This cell re-tests Path C under the FAIR HARNESS that already proved
ARM_SUBSTRATE_SPARSE_BIPOLAR (word2vec encoder + sparse-bipolar) crosses the
chain-grade bar (bpc_best=7.31 vs unigram 7.738, lift 0.43; per
`fair_harness_substrate_as_lm_v1` HARD_PASS landing 2026-06-23).

## Arms (4; each builds FRESH W; no cross-contamination)
1. **ARM_UNIGRAM** -- analytic floor (BPC + top-1 + MRR reference)
2. **ARM_WORD2VEC_DENSE** -- word2vec encoder + dense rank-1 Hebbian W; Path A reference;
   expected bpc_best ~ 7.72 (lift ~ 0.02 over unigram); reproduces fair_harness v1.
3. **ARM_WORD2VEC_SPARSE_BIPOLAR** -- word2vec encoder + sparse-bipolar f=0.05 + rank-1
   Hebbian W; chain-grade winner from fair_harness v1; expected bpc_best ~ 7.31 (lift ~ 0.43).
4. **ARM_SUBSTRATE_OWNED_PC_ENCODER_SPARSE_BIPOLAR** -- substrate-owned PC encoder
   (3-layer Hebbian-PC; Rao-Ballard local update; NO backprop; variance-scaled init;
   Tonegawa write-time competitive allocation at L3) -> sparse-bipolar f=0.05 -> rank-1
   Hebbian W. THE substrate-product arm.

## Config (PRODUCTION SCALE GPU)
- V=4000 vocab, N_TRAIN=100_000 text8 tokens, N_HELD=20_000
- N_DIM=8192, seeds=[7,17,23]
- Encoder for word2vec arms: word2vec-google-news-300 (defensive gensim loader)
- GENSIM_CACHE_DIR=`data/gensim_cache_v2`
- All ops via torch.cuda (Fix #24)
- INGEST_CHUNK=4096, RECALL_BATCH=256
- TEMP_GRID=[0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
- LAMBDA_GRID=[0.0, 0.1, 0.3, 0.5, 0.7, 1.0]
- Joint (T, lambda) sweep on dev half; pick best joint (T*, lambda*); report on test
- PC encoder: 3 layers, alpha=0.05, beta=2.0, n_passes=1, training_tokens=100_000
  (best-from-Path-C-v1-sweep config; FULL grid sweep was already done in Path C v1)

## Reported metrics per arm
- `bpc_best` (at best joint (T*, lambda*))
- `top1_acc` (at best joint (T*, lambda*))
- `mrr_at_10` (at best joint (T*, lambda*))
- `best_T`, `best_lambda`
- `raw_bpc_at_T1_L1` (sanity for DEGEN gate)
- `wordsim_pre_sparsify` / `wordsim_post_sparsify` (PC arm: WordSim353-25 Spearman)
- `pc_meta` (per-pass mean recon err per layer; wall_train_s)
- `pc_sanity` (S1-S4 inline gates)

## Pre-reg HARD bands

### HARD_PASS (Path C substrate-OWNED encoder validated; chain-grade-eligible)
ALL of:
- **PC arm clears ANY of**: `bpc_best < unigram_bpc - 0.3` OR `top1_acc > unigram_top1 + 2 sigma_seeds`
  OR `mrr_at_10 >= unigram_mrr + 0.02`
- **AND PC beats `ARM_WORD2VEC_SPARSE_BIPOLAR` on at least 1 metric**

Rationale for the "beats w2v_sp on >=1 metric" clause: the substrate-OWNED
encoder must add something the borrowed encoder cannot, otherwise the PC training
is decorative. If PC matches w2v_sp exactly on everything, that's a MIDDLE result
(novel mechanism + same outcome) not a Path C win.

### HARD_FAIL (Path C substrate-OWNED encoder genuinely doesn't work as the answer)
PC arm underperforms `ARM_WORD2VEC_SPARSE_BIPOLAR` on ALL 3 metrics
(BPC >= w2v_sp.BPC AND top1 <= w2v_sp.top1 AND MRR <= w2v_sp.MRR).

Per brain-existence-proof: this might mean we haven't trained the PC encoder
long enough OR the PC primitive still has bugs. Route to drill.

### MIDDLE_BAND
PC encoder beats unigram on some metric but doesn't clear PC_HARD_PASS (no
metric clears the substrate bar OR doesn't beat w2v_sp on any metric).
Characterize the gap.

### READOUT_DEGENERATE
If `raw_bpc_at_T1_L1` near `-log2(1/V) +/- 0.5` AND no substrate arm HP, classify as
`READOUT_DEGENERATE_NOT_SUBSTRATE_FAILURE` (NOT HARD_FAIL; harness re-calibration).

## Mandatory runtime sanity gates (inline; informative, NOT verdict-blocking unless catastrophic)
- **S1**: PC mechanism mechanically valid: zero-noise input recon cos > 0.40 (32 random vocab)
- **S2**: Excitability trace evolves: std(E_excit)/mean(E_excit) > 0.05 after pass 1
- **S3**: Reconstruction error decreases or stays flat across passes
- **S4**: WordSim353-25 Spearman > 0.15 on PRE-sparsify PC encoder E (semantic-learning discriminator)
- **S5**: Sparse-bipolar fraction within target +/- 50% (implicit via sparsify primitive)

Also: **reproduce-w2v_sp**: ARM_WORD2VEC_SPARSE_BIPOLAR bpc_best within +/- 0.10 of
the fair_harness v1 reading (7.31). Sanity that the fair-harness implementation matches
the parent's HARD_PASS-validated path.

## Mandatory sanity self-tests (in cell --self-test; T1-T12)
- T1: char-trigram bipolar primitive
- T2: gensim mock-KV pipeline
- T3: At T=0.01, peaked input -> max_prob > 0.5
- T4: At T=10.0, peaked input -> near-uniform
- T5: Joint sweep at lambda=0 reproduces unigram BPC (endpoint)
- T6: lambda=1.0 reproduces raw substrate (no unigram blend)
- T7: MRR@10 on planted 5-pair set (known values)
- T8: Sparse-bipolar primitive (exact non-zero count + uniq={-1,0,1})
- T9: Verdict bands (HP_PC / HF_PC / MIDDLE)
- T10: LLM call counter zero
- T11: PC encoder forward shape + L2-norm output
- T12: PC encoder Tonegawa excitability trace evolves

## Routing rationale
- GPU REQUIRED per Fix #24 (torch.cuda for matmul / PC training / sparse-bipolar projection;
  PC training is the dominant cost ~ 30-60 min wall).
- Timeout 10800s (3h) -- under PROT-021 14400s threshold so no checkpoint-import
  required, BUT cell uses `_seed_checkpoint` for per-seed resume on partial timeout (defensive).
- ANCHOR has no `_n<N>` suffix => PROT-018/019 not applicable.
- atexit synthesizer writes partial metrics.json from completed seeds on SIGTERM/kill.

## Cites
- `experiments/exp_fair_harness_substrate_as_lm_v1.py` -- parent fair-harness pattern
- `experiments/exp_substrate_owned_predictive_coding_encoder_v1.py` -- PC primitive source
- `data/exp_fair_harness_substrate_as_lm_v1/metrics.json` -- target reproduce (7.31 bpc)
- `data/exp_substrate_owned_predictive_coding_encoder_v1/metrics.json` -- prior HARD_FAIL (METHODOLOGY-CONFOUND atom)
- Skunkworks 2026-06-23 META_HARNESS_RIGGED landed-VET (re-classification of 7+ HARD_FAILs)
- USER 2026-06-23 Path C substrate-owned encoder is THE answer
- USER 2026-06-23 audit ratification (V2 LM gap; load-bearing closure decision)
- USER 2026-06-22 Fix #24 (GPU dispatch must use GPU)
- USER 2026-06-22 Fix #26 (predispatch_check: PROCEED 0 prior matching landings)

## Pre-dispatch
- predispatch_check (`path_c_substrate_owned_encoder_FAIR_HARNESS_v2`): PROCEED (0 matching landings; 0 matching atoms)
- predispatch_check (`substrate_owned_predictive_coding`): PROCEED (1 atom = prior METHODOLOGY-CONFOUND; expected)
- Self-test (T1-T12): PASS on .venv laptop
- Smoke target: < 180s laptop CPU under N_TRAIN=2000 N_DIM=512 V=300 PC_TRAINING_TOKENS=1000
