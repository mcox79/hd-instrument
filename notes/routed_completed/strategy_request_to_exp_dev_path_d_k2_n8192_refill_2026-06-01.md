# strategy -> exp_dev: Path D K=2 production-stack stress N=8192 refill

Filed-by: strategy_scribe
Trigger: cap_map v315 path_d_k2_production_stack_stress_n16384 INFRA_FAILURE (CUDA OOM local 4060 Ti 8GB VRAM); re-ship at N=8192 which fits in local 8GB
Pause state: ABSENT (all operations normal)

Per [[feedback-no-experiment-design-in-prompts]]: this file names ANCHOR + POINTERS only. exp_dev determines sweep grids, exact thresholds, queue command, and timeout.

## Anchor: Path D K=2 production-stack stress at N=8192

- Row: Path D production-default sub-row (within multi-hop combined row) + K=2 saturation characterization (PP-8 row OOM caveat v315)
- What to test: cross-N K=2 envelope at N=8192 (up from N=4096 HARD_PASS at v309 V1); full 3-way production stack (compression c_quant/bits8 + Path D K_paths=2 + a_query_sim defense + collision pressure); 5 seeds
- Why now: N=16384 INFRA_FAILURE on path_d_k2_production_stack_stress_n16384 (CUDA OOM local GPU); N=8192 fits in 8GB VRAM; extends K=2 cross-N envelope from N=4096 to N=8192 without hitting N=16384 OOM ceiling; closes most-immediate cross-N caveat at production K=2
- Queue: overnight_queue (local GPU; N=8192 fits in 4060 Ti 8GB VRAM)
- Expected wall: estimate based on N=4096 wall_s=22.5s; N=8192 ~2x = ~45s wall; 5 seeds; total ~3-5min GPU

## Pre-reg shape (same family as N=16384 anchor)
- HARD_PASS: unanimous 5/5 acc_gated >= 0.95 AND def_act >= 1.0 AND fp = 0.000
- HARD_FAIL: acc_gated < 0.85 OR def_act < 0.75 (any cell)
- MIDDLE_BAND: between HARD_PASS and HARD_FAIL
- Cap_map implication if HARD_PASS: Path D K=2 cross-N envelope extends to N=8192; OOM ceiling for local GPU located between N=8192 (passes) and N=16384 (OOM); N=16384 production-deployment requires cloud H100

## M_grid suggestion
M_grid=[1024, 2048] -- avoid M=4096 which combined with N=16384 contributed to the OOM episode (M=4096 at N=8192 is 2N same relative ratio as M=8192 at N=16384 which hit OOM)

## Context pointers
- N=4096 HARD_PASS reference: d:/AI/hd-instrument/notes/substrate_capability_map.md (v309 V1 section)
- OOM failure details: v315 PP-8 row caveat, path_d_k2_production_stack_stress_n16384 INFRA_FAILURE
- Related: d:/AI/hd-instrument/notes/active_protocols.md (PROT-018 _n<N> anchor naming required)

## Contract
- Anchor must include _n8192 suffix per PROT-018
- --timeout required per [[feedback-per-experiment-timeout-required]]
- ASCII-only in print()/verdict_msg per [[feedback-ascii-only-in-scripts]]
- set -ex + python -u + stdbuf -oL + tee remote log per [[feedback-always-verbose-remote-dispatch]]
- Post-ship REMOTE VERIFY via queue.json state; confirm NOT a re-use of any existing N=4096 name

## Autonomy declaration
exp_dev has full autonomy on: anchor name (must include _n8192), exact sweep grid refinement, timeout calculation, pre-reg threshold formula, queue command construction. If M=2048 at N=8192 also approaches OOM, exp_dev may narrow to M_grid=[1024] only.

---

**ROUTING STATUS**: Acted-on 2026-06-01: N=8192 blocked by Kerdock odd-log2; closure annotation added v317
