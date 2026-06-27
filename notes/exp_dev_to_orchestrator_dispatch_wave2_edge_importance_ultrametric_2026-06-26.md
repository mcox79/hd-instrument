# exp_dev -> orchestrator: DISPATCH WAVE 2 cortex E_tensor alternatives (2 cells SMOKE-PASS)

**Filed-by:** exp_dev (Opus 4.7 1M)
**Date:** 2026-06-26
**Type:** Dispatch request (remote_cpu_queue)
**Pause flag:** NOT_PAUSED (checked)

## Summary

USER green-lit 2026-06-26 top-2 cortex alternative mechanisms. Both cells authored,
both primitives self-test PASS, both cells SMOKE-CLEAR gates. Committed to local
main as `1851cc51`. Requesting Orchestrator dispatch to remote_cpu_queue (cells
require origin/main on marsh@home; harness denies push to exp_dev; needs
hd_metrics_sync push + Orchestrator dispatch via `tools/orchestrator/queue_add.sh`).

## Cells (both ready to ship)

### Cell 1: edge_importance_bound_pair_consolidation_v1

- **Script:** `experiments/exp_edge_importance_bound_pair_consolidation_v1.py`
- **Prereg:** `preregs/2026-06-26_edge_importance_bound_pair_consolidation_v1.md`
- **NEW primitive:** `hdlab/edge_importance.py`
- **Queue:** remote_cpu_queue
- **Timeout:** 7200s (2hr; conservative buffer over ~25min estimated wall per seed)
- **Smoke result:** MIDDLE_BAND at smoke (alpha=1.367 above critical; FULL alpha=0.977)
  - cor(E_derived, |W|) = **-0.043** (USER fairness gate PASS; was 0.984 on per-atom-scalar)
  - EDGE_GATED rec_RETR = 1.000 vs RANDOM 0.700 (+0.30 selectivity)
  - H_n_edges = 1916 from 1000 composite queries (mechanism FIRES)
- **What it tests:** importance lives on per-EDGE space (bound-pair graph H[i,j]),
  derived per-atom E via row-sum/PageRank, structurally orthogonal to |W|.
  Composite-query workload (3-atom HRR bundles) populates H during J=3000 cycles.

### Cell 2: cortex_ultrametric_clustering_coarse_grain_v1

- **Script:** `experiments/exp_cortex_ultrametric_clustering_coarse_grain_v1.py`
- **Prereg:** `preregs/2026-06-26_cortex_ultrametric_clustering_coarse_grain_v1.md`
- **NEW primitive:** `hdlab/ultrametric_clustering.py`
- **Queue:** remote_cpu_queue
- **Timeout:** 3600s (1hr; very conservative over ~7min estimated wall total)
- **Smoke result:** MIDDLE_BAND at smoke (cap_drop=0.192 just below 0.20; FULL has 8x8 -> ~0.24)
  - n_qualifying_clusters = 4/4 planted (PERFECT detection)
  - min_within_cosine = 0.919, max_between_cosine = 0.066 (clean ultrametricity)
  - ULTRA rec_cl = 1.000 (cluster-level recall via centroid) vs RANDOM 0.792 (+0.21)
  - 200 random atoms NOT clustered (0 false positives)
- **What it tests:** compositional abstraction via single-linkage agglomerative
  clustering (cosine>=0.85, size>=5); collapse clusters to centroid; recall is
  CLUSTER-LEVEL (any cluster member retrieval = hit; matches schema-fast-track semantics).

## Dispatch commands (for Orchestrator to execute after push)

```bash
# After hd_metrics_sync pushes commit 1851cc51 to origin/main:

cd /d/AI/hd-instrument

bash tools/orchestrator/queue_add.sh \
  remote_cpu_queue \
  edge_importance_bound_pair_consolidation_v1 \
  experiments/exp_edge_importance_bound_pair_consolidation_v1.py \
  preregs/2026-06-26_edge_importance_bound_pair_consolidation_v1.md \
  7200

bash tools/orchestrator/queue_add.sh \
  remote_cpu_queue \
  cortex_ultrametric_clustering_coarse_grain_v1 \
  experiments/exp_cortex_ultrametric_clustering_coarse_grain_v1.py \
  preregs/2026-06-26_cortex_ultrametric_clustering_coarse_grain_v1.md \
  3600
```

Both cells will re-run their --self-test + --smoke gates on the remote machine
via queue_add.py before being added to remote_cpu_queue. No `--skip-smoke` flag
because the smoke must execute on remote (.venv parity check).

## Pre-flight discipline (DONE)

- [x] Fix #26 predispatch_check.py PASS for both anchor names (0 prior matches)
- [x] Pause flag check (NOT_PAUSED at 2026-06-26 dispatch time)
- [x] Both --self-test PASS locally
- [x] Both --smoke PASS locally (mechanism-fires + fairness/selectivity gates clear)
- [x] ASCII-only verified (no emojis / em-dashes / unicode in scripts)
- [x] Substrate-only decode gate (n_llm_calls=0) by structural guarantee
- [x] 3 mandatory arms in each cell (BASELINE rail + MECHANISM + RANDOM control)
- [x] Multi-seed FULL >= 3 (seeds [7, 17, 23])
- [x] Per-arm metrics in verdict (Fix #28 compliance; verdict reads per-arm not verdict_msg)
- [x] Commit pushed to local main as 1851cc51 (awaiting hd_metrics_sync push to origin)

## On verdict (handoff back to research / skunkworks)

- Cell 1 HARD_PASS -> chain-grade candidate (cortex content-extraction breakthrough);
  notify Skunkworks for landed-VET; Research can plan compositional-network probes.
- Cell 1 HARD_FAIL on fairness gate (cor>=0.30) -> ANCHOR 5 falsified; ANCHOR 6
  distribution-homeostasis becomes next-line per Research handoff.
- Cell 2 HARD_PASS -> compositional abstraction primitive operational;
  composes with edge_importance for hybrid mechanism.
- Cell 2 HARD_FAIL on selectivity gate (ULTRA = RANDOM) -> structure-detection
  works but doesn't beat capacity-reduction alone; Research re-design needed.

-- exp_dev (Opus 4.7 1M), 2026-06-26
