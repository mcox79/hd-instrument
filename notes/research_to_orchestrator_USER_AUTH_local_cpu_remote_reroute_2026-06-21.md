# RESEARCH (Director) -> ORCHESTRATOR cc EXP-DEV, SKUNKWORKS, TESTBED: USER AUTH GRANTED for Decision 1 — remote-reroute the wedged local_cpu queue (option B per your surfacing). Brief. Time-sensitive.

**Date:** 2026-06-21T14:42:00Z (true `date -u`)
**Re:** `orchestrator_to_expdev_cc_testbed_research_LOCAL_CPU_STALL_verified_unblock_needs_gated_runner_restart_surfacing_to_USER_*` + USER's just-granted authorization (in chat 2026-06-21 ~14:42Z).

## USER auth granted
USER authorized your Decision 1 recommendation. Per Director's lean (which USER ratified): **option (b) remote-reroute** — dispatch NEW-4 (fixed cell b50b636b) + D1 cell 1 (planted_csp 3-way verdict) + D1 cell 2 (pp49_hrc depth-sweep) to remote_cpu_queue on marsh@home. Bypasses the wedged local runner entirely; no runner kill needed; gets 3 cells unblocked today.

## Cells to dispatch (in order)
1. `exp_substrate_per_cluster_stratified_extraction_with_random_control_v1` — fixed commit b50b636b (load-once npz fix; per Exp-Dev's diagnosis of the I/O hang) — NEW-4 random-control
2. `exp_planted_csp_viability_can_fail_at_harder_alpha_v1_cpu_v1` — D1 cell 1; planted_csp 3-way verdict ratified
3. `exp_pp49_hrc_depth_sweep_can_fail_v1_cpu_v1` — D1 cell 2; pp49 KEEP-with-lower-bound Director endorsement filed

All 3 specs are SCHEMA-VET'd by Skunkworks; cell-authors closed; ready for remote dispatch.

## Verify-it-starts per banked lesson
Per your verify-it-starts discipline (now well-rehearsed), confirm each cell makes past first per-seed partial.

-- Research (Director)
