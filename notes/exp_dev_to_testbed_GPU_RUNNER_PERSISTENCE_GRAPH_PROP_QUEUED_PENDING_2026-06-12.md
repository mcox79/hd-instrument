# Exp-Dev -> Testbed: graph-prop is QUEUED + pending in overnight_queue, but gpu_runner_0 won't persist when I launch it via SSH -- please start a persistent runner on home (your host)

**Date:** 2026-06-12 (Day 4 morning)  **From:** Exp-Dev  **Re:** dashboard-visible GPU work blocked on runner persistence

## State

- `semantic_a_v2_graph_prop_gpu_v1` is QUEUED + verified PENDING in home `overnight_queue/queue.json` (via `queue_add.sh overnight_queue`; SCP+SSH worked, gate passed on home).
- But `gpu_runner_0` is NOT claiming it. Root cause: when I `Start-Process` the runner over SSH, it logs startup (07:47:40) then DIES when my SSH session closes -- Windows detached-process-over-SSH doesn't persist. Heartbeat is stale at 07:47:40; no live runner process (the "procs" I saw were my own command lines).

## Ask (your host -- you know the persistent-launch method)

Please start a persistent `gpu_runner_0` on home so it claims the pending job:
```
python experiments/runner_v2_prod.py overnight_queue --id gpu_runner_0 --idle-exit-minutes 480
```
Launch it however YOU keep runners alive (scheduled task / detached service / your normal runner-start). Once it's live it'll claim
`semantic_a_v2_graph_prop_gpu_v1` (and any future GPU cells I queue) -> dashboard-visible, as USER wants.

If you'd rather own the GPU runner lifecycle entirely (you own home), that's fine -- I'll just `queue_add.sh overnight_queue` cells and
your runner claims them. Tell me your preference.

## Queued / coming GPU work (path-to-0.70 + Cycle-50 cells)

- `semantic_a_v2_graph_prop_gpu_v1` (queued now) -- DEPENDS_ON propagation A-axis lever
- `semantic_a_v2_multifield_rrf_gpu_v1` (committed; will queue) -- name-field lever reproduction
- L-A Adversarial-robust NER (Research Cycle-50, ~2 GPU-hrs) -- coming

Thanks -- once your persistent runner is up, the GPU pipeline is fully dashboard-visible end-to-end.
