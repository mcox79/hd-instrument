# Prereg: substrate_capacity_composition_full_b2xb4xhier_v1_n2048_gpu
## Anchor
substrate_capacity_composition_full_b2xb4xhier_v1_n2048_gpu
## Routing
research_to_exp_dev_SQ2_HP_metric_reframe_confirmed (Test A, re-framing CONFIRMED). Full capacity-axis
composition: B2 sparse x B4 ensemble x hierarchical D-domains, M_crit metric. GPU torch, $0. overnight_queue.
## Pre-registered bands
HARD-PASS total_capacity>=100K AND independence_recall>=0.90. MIDDLE 50-100K. HARD-FAIL <50K or interference.
## Formula self-tests (PROT-022)
sparse completion / dense recall / N=2048. [PASS]
## Smoke gate
Smoke (N=512): HARD_PASS total=125K (sparse 83x x K10 x D5), independence=1.00 (multiplicative composition confirmed).
## PROT-018/019
_n2048 -> N=2048. timeout floor 14400s.
## Queue
overnight_queue (GPU torch).
