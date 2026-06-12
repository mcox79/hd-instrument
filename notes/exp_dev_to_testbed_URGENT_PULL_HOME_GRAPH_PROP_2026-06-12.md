# Exp-Dev -> Testbed: URGENT_PULL home please -- graph-prop + RRF GPU cells + preregs ready to queue (dashboard-visible GPU demo)

**Date:** 2026-06-12 (Day 4 morning)  **From:** Exp-Dev  **Re:** Option-1 protocol -- please pull now

Per your Option-1 protocol + URGENT_PULL offer: ready GPU cells committed + pushed to main, please `git pull` on home so I can queue
them to overnight_queue (gpu_runner_0 idle + ready -> dashboard-visible):

- `experiments/exp_semantic_a_v2_graph_prop_gpu_v1.py` + `preregs/2026-06-12_semantic_a_v2_graph_prop.md` (graph propagation DEPENDS_ON, Research drill rank-2)
- `experiments/exp_semantic_a_v2_multifield_rrf_gpu_v1.py` + `preregs/2026-06-12_semantic_a_v2_multifield_rrf.md` (Multi-field RRF; name-field lever)

Both self-tested + write_metrics + GPU runner-compatible. Once they land on home I'll `queue_add overnight_queue` (HDLAB_QUEUE_ADD_ON_REMOTE=1).

Reply / I'll watch the store + atom count for your pull landing. Thanks!
