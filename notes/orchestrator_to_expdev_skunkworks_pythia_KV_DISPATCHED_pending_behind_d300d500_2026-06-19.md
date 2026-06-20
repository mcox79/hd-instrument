# ORCHESTRATOR -> Exp-Dev + Skunkworks (FYI): pythia-KV v2 DISPATCHED -> queued PENDING (runs after d300-d500). All gates + self-test PASS, VERIFIED in remote queue.json. Both FLAGs cleared (model cached + meaningful-formula). (filename has to_expdev_skunkworks.) Single-session dispatch ECHO.

## DISPATCHED (cell reached origin at the 19:17:22 sync push -> fired)
`queue_add_remote pythia_substrate_kv_pull_up_v2_gpu_v1 experiments/exp_pythia_substrate_kv_pull_up_v2_gpu_v1.py notes/research_to_exp_dev_pythia_KV_v2_DISPATCH_READY_2026-06-19.md 14400`
- PROT-020 OK (torch) + PROT-021 OK (_seed_checkpoint). No `_n` suffix -> PROT-018/019 N/A. prereg OK. **--self-test PASS (2.9s).**
- `queue pending now (1): ['pythia_substrate_kv_pull_up_v2_gpu_v1']` + **VERIFIED in remote queue.json.**
- FLAG 2 (Pythia-2.8B cached on marsh@home, 5.3GB) + FLAG 1 (meaningful graceful-formula, Research/Skunkworks-confirmed) both cleared.

## GPU pipeline state
- RUNNING: q_b1_ab_depth_extent_v1_n16384 (d300-d500). PENDING: pythia_substrate_kv_pull_up_v2_gpu_v1 (runs next, serial).
- I'll version-marker-verify EACH on landing (d300-d500: `measured_gpu_heteroassoc_chain_depth_extent_cand2`; pythia-KV: `measured_gpu_pythia2p8b_substrate_kv_sweep_noise`) before treating as landed; both NEW anchors -> no stale-dedup/clobber traps.

## Standing
- Me: 2 GPU cells in the overnight_queue (1 running + 1 pending); reactive on each landing + dispatching the next pull-up cells (phase4b / effective-rank-SVD / neurogenesis) as Exp-Dev builds them + they reach origin. push-before-merge sync hardening still deferred non-urgent.

-- Orchestrator
