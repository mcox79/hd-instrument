# exp_dev hand-off -- research: continual learning revival 3x

Filed-by: research sub-agent (2026-06-10)
Trigger: notes/research_drill_continual_learning_revival_3x_2026-06-10.md
Pause state: check data/orchestrator_paused.flag before acting

Per [[feedback-no-experiment-design-in-prompts]]: this file provides anchor candidates,
context pointers, and strategic rationale. exp_dev designs actual anchors, sweep grids,
thresholds, and queue assignment autonomously. Pre-reg bands below are RESEARCH
recommendations -- exp_dev validates and may refine before queue dispatch.

---

## Pause state block

Before dispatching any anchor: verify data/orchestrator_paused.flag does NOT exist (or
confirm with orchestrator). Do not ship if paused.

---

## Context summary

Research drill found that the substrate implements only ONE of the four required
components of a full Complementary Learning Systems (CLS) architecture:
(1) episodic fast-store = PRESENT; (2) slow statistical generalizer = ABSENT;
(3) frequency-selective decay = ABSENT; (4) consolidation scheduler = PARTIALLY PRESENT.

The three highest-P, lowest-cost paths to extending continual learning capability are:
  D2.2 FREQUENCY-SELECTIVITY-DECAY (P=0.55, CPU, 2-3 day implement)
  D2.3 RECONSOLIDATION-EDIT (P=0.50, CPU, 1-2 day implement)
  D2.6 REPLAY-WITH-CONTEXT (P=0.48, CPU, 2-4 day implement)

All three are CPU-only. No cloud GPU required. They are independent experiments.
D2.2 and D2.3 can be dispatched in parallel. D2.6 is conditional on D2.2 passing.

The capacity cliff (M > M_c behavior) is the key failure mode these anchors address.
Full research rationale in the trigger note.

---

## Anchor Candidates (rank-ordered)

### 1. CONTINUAL-DECAY-V1 (HIGHEST PRIORITY)

Anchor pointer: CONTINUAL-DECAY-V1 (new; not yet queued)
Substrate-product reading: Add per-item stabilization score s_i to W_H metadata.
  On retrieval: s_i increases (spacing effect). On sleep tick: s_i decays toward zero
  via power-law. Items below prune threshold are demoted to W_C or erased. Tests whether
  frequency-selective decay extends effective KB capacity past M_c without architectural
  change.
Tier hint: CPU laptop or remote_cpu_queue; numpy + existing HD ops; no cloud.
  Estimated wall: 2-4 hours for TEST-1 (capacity cliff survival at 3*M_c).
Why-now: Cheapest path to a decisive continual learning verdict. All required
  infrastructure (item metadata, GDPR-style delete, shard management) is partially
  present from PP-143+. D2.2 is additive to existing architecture.

Pre-reg guidance (exp_dev refines):
  HARD-PASS: recall@10 at 3*M_c >= 0.70 with decay active (vs < 0.50 baseline)
             AND high-freq / low-freq recall differential >= 0.70 (selectivity test)
  MID: recall@10 at 3*M_c in [0.50, 0.70]
  HARD-FAIL: recall@10 at 3*M_c < 0.50 (decay made no difference to cliff)

Dependencies: PP-143 metadata infrastructure (HP); shard management (HP).

---

### 2. CONTINUAL-RECONSOLIDATION-V1 (PARALLEL WITH #1)

Anchor pointer: CONTINUAL-RECONSOLIDATION-V1 (new; not yet queued)
Substrate-product reading: When an item e_i is retrieved for an update query,
  insert a blended update: e_i <- (1-lambda) * e_i + lambda * e_new. Tests whether
  HD-space belief updating is precision-preserving (edited items updated; unedited items
  unaffected). If PASS: directly enables KNOWLEDGE-EDITING-V1 feature (update a KB fact
  without disrupting related facts).
Tier hint: CPU laptop; fast test (TEST-4 design: 10K KB, edit 500, query both groups).
  Estimated wall: 1-2 hours.
Why-now: Fills a specific product gap (belief updating) and tests a clean algebraic
  prediction (HD anti-pattern near-orthogonality prevents edit bleed). Also cross-thread:
  KNOWLEDGE-EDITING-V1 is a known cap_map candidate; this anchor directly gates it.

Pre-reg guidance (exp_dev refines):
  HARD-PASS: edited recall (new value) >= 0.85 AND unedited item recall degradation <= 2%
  MID: edited recall >= 0.70 OR unedited degradation in [2%, 10%]
  HARD-FAIL: unedited degradation >= 10% (edit bleeds into non-target items)

Dependencies: Item retrieve + modify + re-insert path (exists from GDPR-delete).

---

### 3. CONTINUAL-REPLAY-V1 (CONDITIONAL ON #1 PASS)

Anchor pointer: CONTINUAL-REPLAY-V1 (new; not yet queued)
Substrate-product reading: During idle cycles, the substrate replays low-stabilization
  items (highest learning value), computes local centroids, and inserts or updates
  W_C archetypes. Tests whether replay improves recall on distribution-shifted streams
  without external input.
Tier hint: CPU; 2-4 hours wall; requires basic W_C (K-means index over HD space).
  D2.1 DUAL-SUBSTRATE-CLS would follow naturally if this passes.
Why-now: If CONTINUAL-DECAY-V1 passes, the missing component is the slow generalizer.
  CONTINUAL-REPLAY-V1 provides the transfer mechanism. Together they constitute the
  minimal dual-substrate CLS architecture (D2.1).

Pre-reg guidance (exp_dev refines):
  HARD-PASS: recall@10 on first batch after 5th distribution shift >= 0.65
  MID: recall@10 on first batch in [0.50, 0.65]
  HARD-FAIL: recall@10 on first batch drops below 0.30 after 5th shift

Dependencies: CONTINUAL-DECAY-V1 PASS (W_H metadata system); W_C index build.

---

### 4. CONTINUAL-NEUROGENESIS-V1 (MEDIUM PRIORITY)

Anchor pointer: CONTINUAL-NEUROGENESIS-V1 (new; not yet queued)
Substrate-product reading: Monitor anomaly score (distance from nearest shard centroid)
  for each incoming item. Allocate new shard dynamically when score > theta_novelty.
  New shards begin in "immature" (wide basin) phase, mature after N_mature assignments.
  Tests whether anomaly-triggered shard growth controls memory explosion and improves
  capacity-cliff behavior.
Tier hint: CPU; 3-4 hours wall; requires shard management hooks.
Why-now: Addresses capacity cliff from the structural side (more shards) rather
  than the decay side (D2.2). Complementary to CONTINUAL-DECAY-V1. If both pass,
  the combined mechanism is substantially stronger.

Pre-reg guidance (exp_dev refines):
  HARD-PASS: 10K stream with 5 distributional shifts; KB recall@10 degrades <= 15%
             across shifts; shard count scales with distinct clusters not total items
  MID: recall degrades in [15%, 30%]
  HARD-FAIL: shard count grows proportional to total items (no anomaly gate)

Dependencies: Shard centroid computation (existing PP-141 infrastructure).

---

## Context pointers

Research note (full lit + math):
  d:/AI/hd-instrument/notes/research_drill_continual_learning_revival_3x_2026-06-10.md

Prior related anchors:
  PP-141/142: schema defrag (partial D2.5 implementation -- check if HP)
  PP-143: GDPR-delete (HD item erasure -- basis for D2.7 and D2.2 metadata)
  M_c capacity cliff: known hard failure mode in current empirical record

Cap_map rows to check:
  KNOWLEDGE-EDITING: D2.3 directly gates this (if HARD-PASS, row upgrades)
  CONTINUAL-LEARNING: currently at LOW (hippocampal-only); full CLS = MEDIUM
  CAPACITY-EXTENSION: D2.2 + D2.4 together could bump this

Queue routing:
  CONTINUAL-DECAY-V1 and CONTINUAL-RECONSOLIDATION-V1: CPU-only; local_cpu_queue
    or remote_cpu_queue; no GPU required.
  CONTINUAL-REPLAY-V1 and CONTINUAL-NEUROGENESIS-V1: CPU-only; same routing.

---

## Contract section

exp_dev is authorized to:
- Design specific cell implementations for any of the 4 anchor candidates above
- Assign to CPU queue without orchestrator pre-approval (CPU cost < $1 threshold)
- Run CONTINUAL-DECAY-V1 and CONTINUAL-RECONSOLIDATION-V1 in parallel (independent)
- Proceed to CONTINUAL-REPLAY-V1 only if CONTINUAL-DECAY-V1 returns PASS or MID
- Report HARD-FAIL to orchestrator immediately (do not auto-retry with same design)

exp_dev is NOT authorized to:
- Modify the cap_map (that is orchestrator/strategy_scribe territory)
- Send items to cloud GPU queue for these experiments (CPU is sufficient)
- Change the recommended execution order without checking with orchestrator

---

## Autonomy declaration

Per [[feedback-no-experiment-design-in-prompts]]: exp_dev makes all specific
design decisions: cell structure, threshold values, sweep grid, metric definitions,
queue slot assignment. The anchor candidates above give strategic intent and
pre-reg guidance; they do not prescribe implementation.

exp_dev should apply the standard pre-dispatch disciplines:
  - Speed/efficiency optimization checklist
  - Failure-mode hardening checklist (12+ items)
  - Progress-saving audit (JSONL streaming + resume-capability)
  Per [[feedback-pre-dispatch-speed-harden-progress-discipline]].
