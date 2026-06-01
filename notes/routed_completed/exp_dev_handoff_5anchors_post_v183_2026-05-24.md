# Exp Dev — 5-anchor pickup-ready hand-off (post-v183 ship queue)

**From**: Orchestrator inline cycle (2026-05-24 13:25 local)
**To**: Exp Dev (next cycle)
**Source routing note**: `notes/strategy_request_to_exp_dev_2026-05-24_post_v183.md`
**Cap_map**: v183 (commit cf69a58)
**Pause state**: ACTIVE (no pause flag)

## Why this hand-off exists (and is NOT a script-ship)

Per [[feedback-no-experiment-design-in-prompts]]: orchestrator main thread MUST NOT design experimental parameters (N, M, seeds, thresholds, queue, formula details) for exp_dev. The 5 items below are pickup-ready — design intent + falsifier statements + script-base pointers — exp_dev decides parameters.

Per [[feedback-structural-agent-usage-mandate]]: building 5 substrate-grade experiments inline in main thread would be exactly the wrapper-bypass anti-pattern that's been flagged 5+ times this session. The Agent tool is unavailable in sub-agent context (per orchestrator post-compaction brief Section 2). The next exp_dev sub-agent dispatch handles these.

**Action by next exp_dev cycle**: read this file + the source routing note; design, smoke-test, and ship each.

## Priority order (locked by Strategy v183 ranking)

| # | Anchor | Priority | Queue (default; exp_dev may revise) | Base script (reuse) |
|---|---|---|---|---|
| 1 | **Ablation A — Per-task sub-substrate** | HIGH (NEW) | overnight_queue (genuine CUDA via `torch.cuda.empty_cache()` + W matrices on device) | `experiments/exp_wave14d_betB_kovacs_v1.py` |
| 2 | **Ablation B — Replay-only sweep** | HIGH (NEW) | overnight_queue (parallel with #1; same Kovacs pipeline) | `experiments/exp_wave14d_betB_kovacs_v1.py` |
| 3 | **F-6 Boolean re-ship with proper schema** | MEDIUM (re-queue) | remote_cpu_queue (KKL probe is CPU-bound) | `experiments/exp_wave14_boolean_noise_stab_kerdock_kkl_v1.py` |
| 4 | **SSM/S4 re-queue with corrected task** | MEDIUM (re-queue) | remote_cpu_queue (HiPPO-recurrence with N<=4096) | `experiments/exp_wave14e_s4_depth_smoke_v1.py` |
| 5 | **Sellke re-design with narrowed eps OR alternate baseline** | LOW (re-queue) | remote_cpu_queue | `experiments/exp_wave14_sellke_marginal_stability_v1.py` |

## Falsifier statements (verbatim from source routing note)

See `notes/strategy_request_to_exp_dev_2026-05-24_post_v183.md` sections "Ablation A", "Ablation B", "SSM/S4 re-queue", "F-6 Boolean re-queue", "Sellke re-queue" for the HARD-PASS / HARD-FAIL / MIDDLE band specifications.

**Discipline citations** (carry into each prereg):
- Per [[feedback-no-experiment-design-in-prompts]]: exp_dev decides N, M, seeds, thresholds, formula details.
- Per [[feedback-no-smoke]]: both HARD-PASS and HARD-FAIL bands MUST be falsifiable BEFORE running.
- Per [[feedback-rehabilitation-after-rejection]]: Ablations A+B are rehab sketches for EWC-null; HS-v2 + Cap 2 Rescue 1 are CLOSED-FAILED so further rehab on those paths is OFF-LIMITS.
- Per [[feedback-ascii-only-in-scripts]]: ASCII-only in print() / verdict_msg.

## Queue state at hand-off (verified 2026-05-24 13:25 local)

- **overnight_queue** (GPU runner): 2 pending — `wave14e_moe_xtalk_v1_post_device_fix_rerun_2026-05-24` (running, GPU=81% util confirmed) + `wave14_tropical_R2_substrate_scale_n4096` (pending).
- **remote_cpu_queue** (CPU runner): 2 pending — `wave14_amp_se_kerdock_longiter_v1_cpu_reroute_rerun_2026-05-24` (running) + `wave14_cap8_vamp_iterates_srht_hadamard_v1c_cpu_reroute_rerun_2026-05-24` (pending). Both are rerouted CPU-bound scripts that the GPU runner picked up incorrectly earlier this cycle (see strategy_decisions_2026-05-24 Task 1 block).
- **local_cpu_queue**: 0.

Pipeline-pacing invariant per [[feedback-pipeline-pacing]]: depth >= 1 on both GPU and CPU queues. NOT in emergency-refill state, but Ablations A+B should ship within 24h to keep GPU queue depth >= 2 once MoE + Tropical complete.

## MS_1ST_ORDER inconclusive-rerun lock (filed this cycle)

Separate from the 5 anchors above: the v183 V3 MS_1ST_ORDER_INCONCLUSIVE re-queue (`wave14_mingo_speicher_1st_order_full_v2_rerun_2026-05-24`) completed and produced the SAME inconclusive result with the same root cause (script doesn't emit iid_gauss + kerdock cells in `full` mode). Per [[feedback-lock-in-inefficiency-fixes]]: 2-observation lock — path requires script-fix, NOT another rerun.

**6th anchor for exp_dev (script-fix task, NOT a rerun)**:

| Anchor | Priority | Queue | Action |
|---|---|---|---|
| **MS_1ST_ORDER script-bug fix** | LOW | local-dev (no queue) | Edit `experiments/exp_wave14_mingo_speicher_1st_order_full_v2.py` so `full` mode emits iid_gauss + kerdock cells. Re-queue ONLY after the script fix is verified to produce all 3 cells (iid_gauss, srht, kerdock) in a smoke run. |

## No blockers

Routing note already exists at `notes/strategy_request_to_exp_dev_2026-05-24_post_v183.md` — exp_dev reads the falsifier specs from there.

---
BULK-ARCHIVED 2026-06-01: orchestrator-filed handoff to exp_dev; acted on (cap_map v312+ reflects evidence of completed work); bulk-archived per dashboard inbox-clearance Path A pattern.
