# Exp Dev -> Queue: wave14_pq_high_resolution_v1

**Filed**: 2026-05-23
**Routing trigger**: strategy_request_to_exp_dev_post_v158_pipeline_2026-05-23.md (Pick 2)

name=wave14_pq_high_resolution_v1 script=experiments/exp_wave14_pq_high_resolution_v1.py prereg=preregs/2026-05-23_wave14_pq_high_resolution_v1.md timeout=2400

## Smoke gate

PASSED (pre-existing smoke from cycle 172; re-verified 2026-05-23 after utf-8 reconfigure patch):
- N=2048, K=100, depth=25, n_seeds=50, n_starts=30
- n_outer=12, n_total_peaks=31
- VERDICT: PQ_HIERARCHICAL_28 (n_total_peaks=31 in [24,32]; outer=12)
- metrics.json: data/exp_wave14_pq_high_resolution_v1_smoke/metrics.json
- Self-test: 4/4 cases PASS

## FULL config

N=16384, K=100, depth=50, num_entities=200, num_relations=20, n_starts=100, n_seeds=200
Runner: GPU (cheap GPU run ~20 min)

## Memory budget (FULL)

- M (factbase): N x N float32 = 16384 x 16384 x 4 = 1,073 MB (~1.05 GB)
- ea codebook: 200 x 16384 x 4 = 12.8 MB
- ra codebook: 20 x 16384 x 4 = 1.3 MB
- Total peak VRAM: ~1.1 GB (dominated by M matrix)
- Well under 4 GB budget target and 8 GB hardware cap.

## Substrate-product axis

P(q) substructure probe for Cap 3/multihop axis. Tests whether 15 outer P(q) peaks
have hierarchical 28-element sub-structure (matching endpoint partition cardinality).
5 cycles overdue (queued cycle 172, pending through v153-v158 per audit D9).
