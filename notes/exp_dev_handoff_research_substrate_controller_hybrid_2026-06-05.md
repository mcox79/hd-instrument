# exp_dev hand-off -- research: substrate_controller_hybrid_architecture

Filed-by: research sub-agent (2026-06-05)
Trigger: notes/research_drill_substrate_controller_hybrid_architecture_2x_2026-06-05.md

Per [[feedback-no-experiment-design-in-prompts]]: this file hands off TASK + WHY + CONTRACT + AUTONOMY only. exp_dev decides anchor names, sweep grids, threshold formulas, queue choice, and cap_map decisions.

---

## Pause state

Check data/orchestrator_paused.flag before dispatching. Do not queue if paused.

---

## Anchor candidates (rank-ordered)

### 1. Isolated dual-substrate vs shared-W comparison (PRIORITY -- pre-reg ready, CPU-feasible)

Why now: empirical finding already confirmed shared-W failure; isolation is the predicted fix; this is the smallest decisive test of the architectural principle.

Substrate-product reading: if isolated W achieves >=1.5x accuracy on 2-hop associative+decomposition task, the product architecture is confirmed -- two separate weight matrices with controller routing is the correct design.

Tier hint: Tier 2 (mechanism validation; not yet a full capability row but directly informs cap_map Architecture row).

Task: 2-hop chain task requiring episodic retrieval (W_s) followed by factor decomposition (W_r); compare Architecture A (isolated W_s + W_r + controller routing) vs baseline (shared W, single matrix for both storage and decomposition).

Key parameters (do NOT hard-code in exp_dev prompt -- exp_dev decides): N, M sweep, K factors, D codebook size, seed count, I_max, controller state count.

Pre-reg bands (from research note):
  HARD-PASS: accuracy_isolated / accuracy_shared >= 1.5 at M=100, N=1024
  MIDDLE-BAND: ratio in [1.1, 1.5)
  HARD-FAIL: ratio < 1.1

Resource: CPU-feasible (< 60s wall on laptop). Queue: overnight_cpu_queue or remote_cpu_queue.

### 2. Controller iteration depth extension (SECONDARY)

Why now: depth extension K_max = K_sub * I_max is the algebraic prediction; needs empirical anchor at I_max=2,4,8,16 to measure actual depth scaling.

Substrate-product reading: if depth scales linearly with I_max, the K>=100 production target is achievable with trivial controller overhead.

Tier hint: Tier 3 (depth mechanism, needs isolation anchor to pass first).

Pre-reg bands: HARD-PASS = K_effective doubles when I_max doubles (linear scaling); HARD-FAIL = K_effective < 1.2x when I_max quadruples (no depth extension).

### 3. VSA-FSM controller capacity at substrate-class N

Why now: Cotteret et al. 2024 predicts O(N) FSM capacity for bipolar dense vectors; substrate-class N=1024 should support ~1000 FSM states; this is the Turing-completeness empirical anchor.

Tier hint: Tier 3 (theoretical completeness, lower priority than mechanism anchors 1-2).

---

## Context pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_substrate_controller_hybrid_architecture_2x_2026-06-05.md
- Cap map: d:/AI/hd-instrument/data/cap_map.md (check Architecture row)
- Status log: d:/AI/hd-instrument/data/orchestrator_status_log.jsonl (last research_delivery entry)
- Existing shared-W empirical failure: check recent metrics.json for any shared-substrate resonator runs

---

## Contract

exp_dev takes anchor candidates above as input, decides which to queue based on current pipeline state, designs the experiments (sweep grids, anchor names, timeouts, pre-reg formulas), and ships via queue_add.sh. exp_dev does NOT interpret verdicts or update cap_map.

---

## Autonomy declaration

exp_dev has full autonomy over: anchor names and _n<N> suffixes, parameter sweep grids, timeout formula, queue assignment (CPU vs GPU), seed count, and order of dispatch. The only hard constraints are: (a) check pause flag before dispatch; (b) pre-register HARD-PASS / HARD-FAIL bands before coding; (c) ASCII-only in print()/verdict_msg; (d) write_metrics() with required fields.
