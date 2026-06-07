# exp_dev hand-off -- research: rank-k Woodbury validation (Rank-1 SMW 2x drill)

Filed-by: research session
Trigger: Rank-1 SMW 2x drill (notes/research_drill_rank1_smw_decay_2x_2026-06-07.md)
Pause state: check data/orchestrator_paused.flag before dispatch

Per [[feedback-no-experiment-design-in-prompts]]: anchors + WHY only.

Cycle 148 Rank-1 SMW shows 10.12x speedup at N=1024 but decays to 5-6x at N=2048+. Drill 2x identifies BLAS-2 vs BLAS-3 hardware regime shift as root cause AND production sharding architecture as inadvertently optimal (each shard's N lands in SMW sweet spot). The 2x deeper investment is rank-k Woodbury -- arXiv:2406.15120 reports 20-130x speedup at k=10-30 per batch.

---

## Anchor candidates

### 1. rank1_smw_profiler_sweep_N (~5 min GPU; Tier-1 CHEAPEST DECISIVE)
- Substrate-product reading: GPU profiler timing sweep at N in {512, 1024, 2048, 4096, 8192}; report bandwidth utilization + compute utilization per N
- Why now: cheapest test confirming the BLAS-2/BLAS-3 regime hypothesis empirically
- HP: bandwidth utilization > 70% at all N (confirms memory-bound SMW)
- MID: 30-70% bandwidth utilization (partial confirmation)
- HF: < 30% (kernel launch overhead dominating; different bottleneck)

### 2. whitening_disabled_smw_isolation (~10 min GPU; Tier-1)
- Substrate-product reading: re-run cycle-148 SMW speedup measurement with whitening DISABLED to isolate pure SMW cost from whitening double-update
- Why now: drill identifies whitening overhead may be absorbed into SMW timing; this isolates the actual SMW speedup
- HP: pure SMW speedup at N=2048 > 6x (matches predicted theory)
- MID: 3-6x speedup (whitening was significant overhead)
- HF: < 3x speedup (different mechanism; investigate)

### 3. rank_k_woodbury_implementation_smoke (~30 min GPU; Tier-2)
- Substrate-product reading: implement rank-k Woodbury (k=16 or k=32 batch update) at N=2048; measure speedup vs full rebuild AND vs sequential rank-1
- Why now: 2-week engineering investment validates 128x target from arXiv 2406.15120
- HP: speedup >= 50x over full rebuild at N=2048, k=16
- MID: 20-50x (qualify; some lit values reachable)
- HF: < 20x (rank-k advantage doesn't materialize at substrate's N/k regime)

---

## Context pointers

- Research note: notes/research_drill_rank1_smw_decay_2x_2026-06-07.md
- Cycle 148 measurement: pb_pinv_true_rank1_smw verdict (MID at production N)
- Reference: arXiv:2406.15120 (Sherman-Morrison-Woodbury low-rank updates; 20-130x published)
- Production architecture: cycle 142 sharded W (per-shard N=1024-2048 lands in SMW sweet spot)

---

## Contract + Autonomy

exp_dev designs implementation. Anchor 1 is cheapest first. Anchor 3 is a 2-week engineering project; only proceed if anchors 1+2 confirm the BLAS-regime hypothesis.
