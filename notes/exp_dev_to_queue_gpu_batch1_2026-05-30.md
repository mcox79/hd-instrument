# exp_dev_to_queue: GPU Batch 1 (G1-G4) -- 2026-05-30

Shipped 4 anchors per user "let's get these experiments running" Batch 1
directive (items 1-4; item 5 skipped per supersession by V2
sustained_workload_24h_baseline already shipped).

All 4 are N=4096 BSC, Path D characterization + composition + KF-1
refinement to complete the prerequisites for Pattern B LLM-integration
design.

```
queue=overnight_queue name=path_d_latency_profiling_v1_n4096 script=experiments/exp_path_d_latency_profiling_v1_n4096.py prereg=preregs/2026-05-30_path_d_latency_profiling_v1_n4096.md timeout=21600
queue=overnight_queue name=path_d_high_k_scaling_v1_n4096 script=experiments/exp_path_d_high_k_scaling_v1_n4096.py prereg=preregs/2026-05-30_path_d_high_k_scaling_v1_n4096.md timeout=14400
queue=overnight_queue name=handoff_composition_probe_v1_n4096 script=experiments/exp_handoff_composition_probe_v1_n4096.py prereg=preregs/2026-05-30_handoff_composition_probe_v1_n4096.md timeout=21600
queue=overnight_queue name=multi_signal_kf1_refinement_v1_n4096 script=experiments/exp_multi_signal_kf1_refinement_v1_n4096.py prereg=preregs/2026-05-30_multi_signal_kf1_refinement_v1_n4096.md timeout=14400
```

## Status

- 4/4 scripts written with `_instrumentation_selftest()` (PROT-018, PROT-021)
- 4/4 preregs filed with HP/HF/MB bands pre-registered
- 4/4 self-tests PASS
- 4/4 smoke runs: G1=HP, G2=MB (1-seed only), G3=HF (expected — smoke
  regime too easy), G4=MB (expected — N=1024 small)
- 4/4 queue_add.sh REMOTE VERIFY OK on overnight_queue
- queue depth = 4 (up from 0)

## Anchor summaries

### G1 path_d_latency_profiling_v1_n4096 (TIMEOUT 21600s)
3 M x 4 depth x 3 K x 5 seeds = 180 cell-seeds. Per-op time decomposition
with TimingTrace. Identifies dominant op per cell + checks
within-family/across-seed consistency. Unblocks Path D optimization.
Smoke: dominant_op = time_likelihood_query_per_hop in 8/8 cells (~75-82%
of wall) -> HP at smoke.

### G2 path_d_high_k_scaling_v1_n4096 (TIMEOUT 14400s)
K_paths sweep [1500, 2000, 3000, 5000] at M=8192 depth=5. log-log scaling
slope <= 1.1 + accuracy >= 0.95 at K=5000 in >=3/5 seeds = HP. Smoke
slope 0.58 (sub-linear); 1-seed insufficient -> MB at smoke as designed.

### G3 handoff_composition_probe_v1_n4096 (TIMEOUT 21600s)
3 strategies (A_heuristic, B_parallel_verify, C_targeted_verifier) x 3
regimes (sub_cap M=2048, at_cap M=4096, past_cap M=16384) x 5 seeds = 45
cell-seeds. HP if any strategy delivers verifier_catch_rate >= 0.10 OR
accuracy_delta >= 0.05 in >= 3/5 seeds at any regime. Smoke
HF expected (smoke regime saturated at 1.0 below capacity); FULL past_cap
at N=4096 is the actual test.

### G4 multi_signal_kf1_refinement_v1_n4096 (TIMEOUT 14400s)
5 signals x 4 M values [128, 4096, 8192, 16384] x 5 seeds = 20 cell-seeds.
Adds BORDERLINE queries (stored_key + 10% BSC noise) to v2 in-store/OOS
mix. HP requires composite AUC >= 0.90 at ALL 4 M + resolution_accuracy
>= 0.75 + 3/5 seeds. Smoke MB (N=1024 too small).

## ETA

Estimated total compute: ~8-12h sequential on GPU runner
(G1 dominates at ~6h cap; G2/G4 ~1-2h each; G3 ~3-5h).
Verdicts arriving overnight.

## Blockers

- None at ship time.
- WATCH: G3 smoke HARD_FAIL is by-design (regime ceiling); if FULL also
  returns HARD_FAIL with all-strategies-zero across past_cap, NOT
  trivialization but a genuine "composition has no value" verdict for
  this regime mix -> route to Strategy for next-cycle pivot.
- WATCH: G4 smoke resolution_accuracy = 0.33; if FULL stays below 0.50,
  signal-redesign rescue needed (not a config bug).
