# 2026-06-23 sparse_bipolar_substrate_lm_param_sweep_v1 -- envelope characterization

## Anchor
`sparse_bipolar_substrate_lm_param_sweep_v1`

## Status
- Prereg authored 2026-06-23 (exp_dev)
- Queue: `overnight_queue` (GPU, marsh@home)
- Timeout: 7200s (2h)
- Estimated wall: ~85 min GPU full (20 configs * 3 seeds)

## Cell
`experiments/exp_sparse_bipolar_substrate_lm_param_sweep_v1.py`

## Referent verified (per verify-the-referent discipline)
`data/exp_fair_harness_substrate_as_lm_v1/metrics.json`:
- ARM_SUBSTRATE_SPARSE_BIPOLAR bpc_best_mean = 7.3065 vs unigram 7.7378 = +0.4313 bits lift
- bpc_best_cv = 0.0018 (chain-grade-tight)
- best_T_for_bpc = 0.05, best_lambda_for_bpc = 0.3
- top1_ok = false (top-1 not above unigram; win is BPC-shape, not top-1)
- ARM_SUBSTRATE_SPARSE_BIPOLAR listed in degen_arms (raw_bpc_at_T1_L1 = 11.6085 within DEGEN_TOL of vocab_entropy=11.97) -- the joint sweep recovers the win at T=0.05

This cell extends that ONE validated point into an envelope over (f, N_DIM, N_TRAIN).

## Why now
USER 2026-06-23 (exp_dev cycle): "characterize the operating envelope of the
chain-grade substrate-as-LM win... need to know what configuration is OPTIMAL."

## Sweep grid (BUDGET-PRUNED factorial)
- f_sparse: [0.01, 0.02, 0.05 (validated), 0.10, 0.20] -- 5 points
- N_DIM in {4096, 8192 (validated), 16384}
- N_TRAIN: 1M only at N_DIM=4096 (cheap); 100k at all 3 N_DIM
- V vocab: 4000 (fixed; matches validated config)
- seeds: [7, 17, 23]

**Pruning rationale:** Hebbian rank-1 W build is O(N_TRAIN * D^2); held-set
logits is O(N_HELD * D^2). At observed 42s/seed for fair_harness (N=8192,
NT=100k), the full factorial (3 N_DIM x 2 N_TRAIN) would imply ~25200s for
(N=16384, NT=1M) alone -- 3.5x over the 7200s budget. Pruning drops the two
worst corners (8192/1M, 16384/1M) so the full f-axis is preserved at all 3
N_DIM points (f-optimum visible at every dimension) AND N_TRAIN-scaling is
visible at the cheapest dimension. If sweep finds a clear optimum, follow-up
cell can re-validate the top-2 configs at NT=1M.

Configs (20 total):
- N_DIM=4096 x NT=100k    x 5 f = 5 configs
- N_DIM=4096 x NT=1M      x 5 f = 5 configs
- N_DIM=8192 x NT=100k    x 5 f = 5 configs (one is the validated point)
- N_DIM=16384 x NT=100k   x 5 f = 5 configs

3 seeds each => 60 (config, seed) cells.

## Reused infrastructure
Single-arm extraction of fair_harness_substrate_as_lm_v1 harness:
- word2vec-google-news-300 encoder (defensive gensim_load_helper, char-trigram OOV)
- sparsify_bipolar_gpu (validated f-quantile top-k bipolar)
- build_rank1_W_gpu (chunked Hebbian outer-products on GPU)
- joint (T,lambda) sweep on dev half; eval on test half
- 3 metrics per cell: bpc / top-1 / MRR@10
- TEMP_GRID=[0.01..1.0]; LAMBDA_GRID=[0.0..1.0]
- READOUT_DEGENERATE diagnostic (raw_bpc_at_T1_L1 reported per cell)
- per-(config,seed) checkpoint via _seed_checkpoint (PROT-021-compatible)

## Pre-reg HARD bands

### HARD_PASS (clear optimal regime characterized)
ALL of:
- At least **3 distinct configs** clear `bpc_best_mean <= unigram_bpc - 0.30` AND `bpc_best_cv <= 0.05`
- Optimal config (lowest bpc_best_mean) beats fair_harness baseline (7.3065) by **>= 0.10 bits** (i.e. bpc_best_mean <= 7.21)

### HARD_FAIL (sparse-bipolar lift saturates at validated baseline)
- `max(lift_vs_unigram across all configs) <= baseline_lift (0.4313) + tol (0.05) = 0.4813`
- I.e. **no** config reaches bpc_best_mean below 7.2565
- Equivalently: envelope is one-point; no scaling lever exists in (f, N_DIM, N_TRAIN)

### MIDDLE_BAND (plateau without clear optimum)
- Substrate clears HP in >= 1 config but EITHER n_hp_configs < 3 OR optimal beats baseline by < 0.10 bits

## Metric semantics
- **PRIMARY**: BPC (the metric on which the validated win exists). Per fair_harness
  data: top-1 / MRR did NOT clear unigram bars for SPARSE_BIPOLAR (top1=0.2134
  vs uni=0.2171; mrr=0.2917 vs uni=0.2761 narrow). Reporting top-1 / MRR for
  transparency only; **NOT load-bearing** in this envelope verdict.
- bpc_best_mean = test-set BPC at the (T*, lambda*) chosen by dev-set joint sweep
- cv = std / |mean| across seeds (tight = within-config seed consistency)

## Self-tests (in cell --self-test)
- T1: char-trigram encoder bipolar (defensive fallback)
- T2: sparse_bipolar exact non-zero count + uniq={-1,0,1}
- T3: softmax_with_T peaked at T=0.01
- T4: lambda=0 endpoint reproduces unigram BPC (mixer correctness)
- T5: verdict band HARD_PASS path (>= 3 HP configs, optimal beats baseline)
- T6: verdict band HARD_FAIL path (max_lift <= baseline_lift + tol)
- T7: verdict band MIDDLE_BAND path (HP configs present but count < 3)
- T8: MRR@10 on planted 5-pair set (known ranks)

## Routing rationale
- **GPU REQUIRED** per Fix #24 (Hebbian D^2 matmul + V*D held-set logits).
- Estimated 85 min GPU wall at observed 42s/seed for N=8192/100k, scaling D^2 * N_TRAIN.
- Timeout 7200s = ~1.4x safety margin.
- PROT-019: anchor has no `_n<N>` suffix, BUT cells include N=16384 -- routing-sanity
  WARN may fire. Cell uses torch.cuda (PROT-020 satisfied).
- PROT-021: timeout 7200 < 14400, so checkpoint-import not REQUIRED, BUT cell uses
  per-(config,seed) checkpoint anyway for defensive partial-recovery on timeout.
- Anchor has no `_n<N>` suffix; sweep operates over N_DIM values; PROT-018 N/A.

## Predispatch + landing hooks
- predispatch_check: PROCEED (0 prior matching landings; 0 atoms)
- post-landing: peek_arm_metrics on metrics.json verdict; verify by-config
  bpc_best_mean per-cell (Fix #28: not verdict-msg framings only)

## Cites
- experiments/exp_fair_harness_substrate_as_lm_v1.py -- parent harness (cloned)
- preregs/2026-06-23_fair_harness_substrate_as_lm_v1.md -- validated baseline prereg
- data/exp_fair_harness_substrate_as_lm_v1/metrics.json -- referent (verified)
- notes/skunkworks_to_all_LANDED_VET_META_HARNESS_RIGGED_substrate_as_lm_reclassification_2026-06-23.md -- METHODOLOGY_AUDIT context
- USER_2026-06-23 (exp_dev cycle) -- envelope characterization request
- USER_2026-06-22 Fix #24 -- GPU dispatch must use GPU
- USER_2026-06-22 Fix #28 -- verify per-arm metrics not summary verdict text
