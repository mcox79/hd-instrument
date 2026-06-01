# exp_dev -> queue: percolation depth-sweep diagnostic

Date: 2026-06-01
Anchor: path_d_percolation_depth_sweep_v1_n4096
Smoke: PASS (COMPOSITION_CLIFF signal at smoke scale)
Self-test: PASS (module-scope assertions + live forward pass)
PROT-018: N=4096 verified in script
PROT-019: timeout=14400s (at floor)
PROT-022: device=cpu forced

## Queue entry (Schema A)

queue=remote_cpu_queue name=path_d_percolation_depth_sweep_v1_n4096 script=experiments/exp_path_d_percolation_depth_sweep_v1_n4096.py prereg=prereqs/2026-06-01_path_d_percolation_depth_sweep_v1_n4096.md timeout=14400

## Ship status

SHIPPED. queue_add.sh exit=0. Remote VERIFY: PASS (1/1).
Entry confirmed present in remote remote_cpu_queue/queue.json.

## Source routing

notes/routed_completed/strategy_request_to_strategy_negative_results_followon_experiments_2026-06-01.md
(Test 1A; Test 2A routed to testbed separately)


---

Acted-on 2026-06-01: percolation depth-sweep HARD_PASS verdict processed in v316 batch; depth>=3 N-INDEPENDENT gap LOCATED


Acted-on 2026-06-01: percolation depth-sweep HARD_PASS verdict processed in v316; depth>=3 N-INDEPENDENT gap LOCATED
