# 2026-06-24 substrate_pc_hierarchy_fair_harness_v1 -- META-SKEPTICISM Anchor 1

## Anchor
`substrate_pc_hierarchy_fair_harness_v1`

## Status
- Prereg authored 2026-06-24 (exp_dev)
- Queue: `overnight_queue` (GPU, marsh@home)
- Timeout: 14400s (4h safety margin on ~3-4h GPU wall estimate)
- Estimated wall: 3-4 h GPU full (4 arms x 3 seeds x text8 N_TRAIN=100k N_DIM=8192,
  with 7x5=35 (T,L) sweep points per arm; PC layers + cf-RPE compose adds modest overhead)

## Cell
`experiments/exp_substrate_pc_hierarchy_fair_harness_v1.py`

## Why now (meta-skepticism drill Anchor 1 + USER directive 2026-06-24)

Resolves A12 contradiction:
- PC hierarchy chain-grade for 5-corpus aggregation BUT degraded capacity 0.25x.
- Prior cells (`exp_substrate_pc_hierarchy_text8_lm_v1+v2`) HARD_FAILed under
  META_HARNESS_RIGGED methodology (cosine logits + T=1 = uniform; BPC-only bar).
- Skunkworks methodology audit 2026-06-23 reclassified those to SUSPENDED METHCONF
  (cert ledger row 588).
- USER directive 2026-06-24: hierarchy may have COMPUTATIONAL reasons beyond
  biology -- TEST IT under the fair_harness rail.

This cell re-tests PC hierarchy under the methodology-corrected fair_harness rail
that established `fair_harness_substrate_as_lm_v1` as the production reference.

## Arms (4)

1. **ARM_RANK_1_BASELINE** -- fair-harness reference; sparse-bipolar f=0.05 + rank-1
   Hebbian W. Sanity rail at ~7.3065 BPC ref (from ARM_SUBSTRATE_SPARSE_BIPOLAR in
   `fair_harness_substrate_as_lm_v1`).
2. **ARM_PC_HIERARCHY_2LEVEL** -- Rao-Ballard 2-level PC with top-down feedback
   (n_layers=2 + W_pred predictor; variance-scaled Gaussian init per v2 bugfix;
   alpha=0.05 PC update rate).
3. **ARM_PC_HIERARCHY_3LEVEL** -- 3-level PC (n_layers=3 + W_pred predictor).
4. **ARM_PC_HIERARCHY_2LEVEL_PLUS_CFRPE** -- 2-level PC + cf-RPE plasticity on the
   predictor layer (heterogeneity test); cf-RPE refines W_pred from zero-init on
   L2-normalized top-layer output (50 stochastic steps in smoke, 200 in full;
   lr=0.5, batch=256).

All 4 arms apply sparse-bipolar f=0.05 transform to the word2vec base E (validated
20-300x bundle-capacity lift). FRESH W per arm; no cross-contamination.

## Config (PRODUCTION SCALE GPU)
- V=4000 vocab, N_TRAIN=100_000 text8 tokens, N_HELD=20_000
- N_DIM=8192, seeds=[7, 17, 23]
- Encoder: word2vec-google-news-300 (Path A; defensive gensim loader)
- GENSIM_CACHE_DIR=`data/gensim_cache_v2`
- All ops via torch.cuda (Fix #24)
- INGEST_CHUNK=4096, RECALL_BATCH=256
- TEMP_GRID=[0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
- LAMBDA_GRID=[0.1, 0.3, 0.5, 0.7, 1.0]   (META C7: 0.0 excluded; full-unigram degenerate selector)
- PC_INIT_SCALE=0.01 / sqrt(dim)   (variance-scaled Gaussian; v2 bugfix preserved)
- PC_ALPHA=0.05   (mid of v2 ALPHA_GRID=[0.01, 0.05, 0.1])
- CFRPE_LR=0.5, CFRPE_N_STEPS=200, CFRPE_BATCH=256

## Reported metrics per arm
- `bpc_best`, `top1_acc`, `mrr_at_10` (at best joint (T*, lambda*) on dev)
- `raw_bpc_at_T1_L1` (DEGEN sanity check)
- `pc_recon_err_quarter`, `pc_recon_err_end` (PC arm only; monotonicity diagnostic)

## Pre-reg HARD bands (per USER Anchor 1)

### Sanity rail (load-bearing; FAIL aborts interpretation)
- `ARM_RANK_1_BASELINE` BPC within +/- 0.05 of 7.3065 (the production
  fair_harness_substrate_as_lm_v1 reference).
- If sanity rail FAILS, verdict = HARD_FAIL with `SANITY_RAIL_FAIL` reason
  (harness drift detected; PC lifts not interpretable).

### HARD_PASS (PC hierarchy has COMPUTATIONAL reasons beyond biology)
Any PC arm clears EITHER:
- `top1_acc - rank1_top1 >= 0.05` (top-1 lift of 5 percentage points), OR
- `rank1_bpc - bpc_best >= 0.05` (BPC lift of 0.05 bits)
under the selection-mixer harness.

### MIDDLE_BAND
Any PC arm achieves top1 lift in `[0.02, 0.05)` (partial signal; not chain-grade).

### HARD_FAIL (PC hierarchy is the capacity-degradation regime, NOT LM-lift regime)
ALL PC arms fail both HARD_PASS conditions AND no MIDDLE_BAND PC arm exists.
(All PC arm top-1 lift < 0.02 AND all PC arm BPC lift < 0.05.)

### READOUT_DEGENERATE (NOT HARD_FAIL; harness re-calibration needed)
If `raw_bpc_at_T1_L1` within +/- 0.5 of -log2(1/V)=11.97 for any PC arm AND no PC
arm achieves HARD_PASS, classify as DEGEN (NOT HARD_FAIL).

### CHAIN_GRADE_BONUS (substantial new chain-grade)
Any PC arm achieves `top1_acc >= 0.55` (well above the 0.4 ARM_RANK_1 baseline at
production scale).

## Mandatory sanity self-tests (in cell --self-test)
- T1: char-trigram bipolar primitive
- T2: sparse-bipolar primitive (nnz exact + uniq subset {-1, 0, 1})
- T3: rank-1 W builder shape + nonzero
- T4: build_pc_layers_gpu returns n_layers + W_pred matrices + finite recon_err
- T5: forward_pc_layers_gpu shape + non-degenerate output
- T6: build_pc_layers_plus_cfrpe_gpu runs end-to-end
- T7: softmax with T peaked vs near-uniform
- T8: MRR@10 on planted 5-pair set (known ranks 1..5)
- T9: verdict band classification (HARD_PASS / MIDDLE_BAND / SANITY_RAIL_FAIL /
       HARD_FAIL / CHAIN_GRADE_BONUS)
- T10: LLM call counter zero

## Routing rationale
- GPU REQUIRED per Fix #24 (torch.cuda for matmul / PC training / sparse-bipolar).
- 4 arms x 3 seeds x text8 N_TRAIN=100k N_DIM=8192 with 7x5=35 joint (T,L) points.
- Estimated 3-4h GPU wall (PC layers are O(N_TRAIN * N_DIM^2) per layer per seed;
  3-level adds ~50% over 2-level; CFRPE adds ~10-15% on top of 2-level).
- Timeout 14400s = 4h safety margin (PROT-021: >=14400 requires per-seed checkpoint;
  cell uses `_seed_checkpoint` for resume on partial timeout, satisfying PROT-021).
- ANCHOR has no `_n<N>` suffix => PROT-018/019 not applicable.

## What this DOES show
- Whether PC hierarchy adds LM lift under the fair harness that exposed
  substrate-as-LM as methodology-confound.
- Whether 2-vs-3 level hierarchy is the right depth.
- Whether heterogeneous plasticity (cf-RPE on PC features) compounds with hierarchy.

## What this does NOT show (honest scope)
- f=0.05 only (doesn't test phase-shift modes or other f values; separate cell for
  f=0.02 if direct N1 comparison needed).
- text8 only (doesn't test 5-corpus aggregation).
- LM lift only (no M-sweep; doesn't test capacity).

## Smoke result (laptop CPU 2026-06-24)
- Smoke wall: ~84s end-to-end (well under 180s budget).
- All 4 arms produced finite, sensible metrics at smoke scale (V=300, N_DIM=512,
  N_TRAIN=2000).
- Smoke per-arm: RANK_1 bpc=5.178 top1=0.331 mrr=0.405; PC_2LEVEL bpc=5.284
  top1=0.331 mrr=0.401; PC_3LEVEL bpc=5.542 top1=0.306 mrr=0.393;
  PC_2LEVEL_PLUS_CFRPE bpc=5.163 top1=0.331 mrr=0.406.
- Smoke SANITY_RAIL_FAIL (expected): 7.3065 ref is full-scale; smoke RANK_1=5.178
  reflects smaller V=300. Full-scale will calibrate to 7.3065 +/- 0.05.
- Verdict logic fires correctly across HP / MB / HARD_FAIL / SANITY / DEGEN / CG.

## Cell-author bugfixes during authoring (atomized as discipline)
- **cf-RPE refinement requires zero-init W_pred + L2-normalized top_out.**
  Initial design re-used the Hebbian-init W_pred for cf-RPE refinement; the cf-RPE
  update `error = tgt - top_b @ W_pred.T` exploded because Hebbian-init has
  spectral norm proportional to n_pairs. Fix: discard Hebbian W_pred for cf-RPE
  arm; start cf-RPE from W_pred=0; L2-normalize top_out per row (otherwise
  bipolar top_out norm = sqrt(dim) ~ 22.6 and cf-RPE updates grow geometrically).
  Inference forward in CFRPE arm uses `l2_top=True` to match training scale.

## Cites
- `preregs/2026-06-23_fair_harness_substrate_as_lm_v1.md`  (parent harness)
- `experiments/exp_fair_harness_substrate_as_lm_v1.py`  (template + production 7.3065 ref)
- `experiments/exp_substrate_pc_hierarchy_text8_lm_v2.py`  (build_pc_layers_gpu source)
- `experiments/exp_substrate_heterogeneous_plasticity_cfrpe_stdp_fair_harness_v1.py`  (cf-RPE pattern)
- `data/exp_substrate_pc_hierarchy_text8_lm_v2/metrics.json`  (prior HARD_FAIL; SUSPENDED METHCONF)
- cert_ledger.jsonl row 588 META_HARNESS_RIGGED reclassification
- USER_2026-06-24_anchor1_test_PC_hierarchy_computational_reasons_beyond_biology
- USER_2026-06-23_audit_ratification (V2 LM gap load-bearing)
- USER_2026-06-22_Fix24 (GPU dispatch must use GPU)

## Pre-dispatch
- predispatch_check: PROCEED (0 matching landings; 0 matching atoms; fresh anchor)
- selftest: PASS (T1-T10)
- smoke: PASS (all 4 arms produce finite metrics; verdict logic fires correctly;
  wall ~84s on laptop CPU; SANITY_RAIL_FAIL expected at smoke scale)
- REQUIRED_FIELDS verified in smoke metrics.json: verdict, verdict_msg, elapsed_s, summary
