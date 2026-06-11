# exp_dev hand-off -- research: dreaming substrate 2x refinement

Filed-by: research sub-agent
Date: 2026-06-10
Trigger: notes/research_drill_dreaming_refinement_2x_2026-06-10.md
Urgency: HIGH -- PP-328 HARD_PASS was n=1 synthetic-only; six mechanism upgrades identified from 2025-2026 literature; polysemy stress test is minimum gate before customer-facing schema discovery claims.

---

## Pause state

Experiments below are PROPOSED, not queued. Pause gate applies per normal exp_dev protocol.
Check data/orchestrator_paused.flag before dispatching.

---

Per [[feedback-no-experiment-design-in-prompts]]:
This file provides ROUTING POINTERS and ANCHOR CANDIDATES only.
Experiment design details (cell grids, hyperparameter values, script paths) are authored by exp_dev from the research note + cap_map context. Do NOT treat the descriptions below as implementation specs.

---

## Anchor candidates (rank-ordered)

### Anchor 1: dreaming_temporal_order_control_v1 (TEMPORAL-ORDER-CONTROL)

Anchor pointer: Research note Section CHEAP DECISIVE TEST + Test 1. Ablation of temporal replay order on existing PP-328 setup.
Substrate-product reading: Phasor Agents (arXiv:2601.04362) validated that compression-progress signal requires temporal ordering to be genuine -- their timestamp-shuffle control showed signal disappears under random order. If the substrate's PP-328 compression_progress=0.618 is also order-dependent, temporal structure is load-bearing and all scale-up must preserve it. If order-independent, PP-328 result may be partially spurious and needs re-audit before scale-up investment.
Tier hint: local CPU, ~30 minutes. Add shuffle ablation to existing dreaming substrate code. Queue: local_cpu_queue. Read-only extension of PP-328 setup; no new model training.
Why-now: gates all downstream dreaming anchors. Cheapest decisive test available. n=1 synthetic result requires this control before scale-up.

Pre-reg bands:
  HARD-PASS: ordered replay compression_progress > shuffled + 0.10 (temporal structure load-bearing; scale-up justified)
  MIDDLE-BAND: ordered > shuffled by 0.03-0.10 (partial effect; scale-up with caution)
  HARD-FAIL: shuffled >= ordered (temporal order has no effect; PP-328 compression signal validity questioned; triggers 2x re-audit of PP-328 before further investment)

### Anchor 2: dreaming_polysemy_stress_v1 (POLYSEMY-STRESS-TEST)

Anchor pointer: Research note Section LEVEL 5, Test 2. 500-item Wikipedia subset with 5 polysemous term domains.
Substrate-product reading: PP-328 used controlled synthetic data with no polysemy. Real-world text has pervasive polysemy (Python, Mercury, Java, etc.). Purity=0.875 on synthetic gives NO information about purity on real vocabulary. This test is the minimum gate for any customer-facing claim about schema discovery on real text. Without it, schema discovery is only demonstrated on synthetic corpora.
Tier hint: local CPU, ~2 hours. Requires Wikipedia article loader (existing testbed infrastructure) + polysemy domain selection (5 domains, ~100 articles each). Queue: local_cpu_queue or overnight_queue.
Why-now: directly gates the "substrate discovers schemas from real knowledge bases" product claim. Cost is low; discriminating power is high.

Pre-reg bands:
  HARD-PASS: purity at N=500 Wikipedia with disambiguation check (MU-2 spatial binding with sense consistency) >= 0.75
  MIDDLE-BAND: purity 0.60-0.75 (polysemy degrades but does not destroy; disambiguation upgrade required before production)
  HARD-FAIL: purity < 0.60 (schema discovery fails on real polysemous vocabulary; mechanism redesign required before scale-up)

### Anchor 3: dreaming_scaleup_5k_v1 (SCALE-UP-5K)

Anchor pointer: Research note Section LEVEL 5, Test 3 + MU-1 + MU-3 + MU-6.
Substrate-product reading: Validates that the dreaming substrate with serial-position replay (MU-1), Y-conditioned compression (MU-3), and adaptive schema threshold (MU-6) produces a stable, compute-bounded schema store at N=5K items. This is the first checkpoint at which the "substrate autonomously discovers KB organization" product claim becomes testable at meaningful scale. Key output: schema count, purity, compute per dreaming cycle.
Tier hint: remote CPU, ~1 day. 5K Wikipedia articles, full dreaming pipeline with MU-1+MU-3+MU-6. Queue: overnight_queue (remote_cpu_queue). Requires Anchors 1 + 2 HARD-PASS before dispatch.
Why-now: N=5K is the smallest scale at which sqrt(N) schema scaling becomes distinguishable from linear scaling; also the smallest scale at which per-cycle compute feasibility for production can be assessed.

Pre-reg bands:
  HARD-PASS: schema count in [15, 60] AND purity > 0.70 AND per-cycle compute < 120 seconds
  MIDDLE-BAND: schema count in [10, 100] AND purity 0.60-0.70 OR compute 120-600 seconds (needs tuning)
  HARD-FAIL: schema count > 100 (adaptive threshold not working) OR purity < 0.60 OR per-cycle compute > 600 seconds (not production-feasible)

### Anchor 4: dreaming_streaming_100k_v1 (STREAMING-100K)

Anchor pointer: Research note Section LEVEL 5, Test 4 + Section 4.2 + MU-4 + MU-5.
Substrate-product reading: 100K Wikipedia articles is the scale at which a fintech or healthcare customer KB would operate. Validates schema stability under streaming (no catastrophic forgetting), sub-linear schema growth (saturation by batch 7/10), and compute sustainability of performance-gated dreaming (MU-4) + multi-tau consolidation (MU-5). If this passes, the "substrate maintains an organized, stable, growing understanding of your knowledge domain" product claim is empirically grounded.
Tier hint: remote CPU, 2-3 days. Requires Anchor 3 HARD-PASS and MU-4+MU-5 implementation. Queue: overnight_queue.
Why-now: only after Anchors 1-3 pass. This is the production-validation gate, not the discovery gate.

Pre-reg bands:
  HARD-PASS: schema count growth curve shows clear plateau by batch 7 AND purity > 0.65 AND > 60% of batch-1 schemas survive to batch 10 AND performance-gated dreaming reduces cycles by > 30%
  MIDDLE-BAND: plateau delayed to batch 9-10 OR purity 0.55-0.65 OR batch-1 schema survival 40-60%
  HARD-FAIL: no saturation through batch 10 (super-linear growth) OR batch-1 schemas fully pruned by batch 5 (catastrophic forgetting) OR purity < 0.55

---

## Context pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_dreaming_refinement_2x_2026-06-10.md
- PP-328 cap_map entry: d:/AI/hd-instrument/notes/substrate_capability_map.md (row PP-328, dreaming_substrate_cpu_v1)
- Prior 5x autonomous discovery note: d:/AI/hd-instrument/notes/research_drill_autonomous_discovery_5x_2026-06-10.md (F2.3 DREAMING-SUBSTRATE mechanism design v1)
- Prior 5x handoff: d:/AI/hd-instrument/notes/exp_dev_handoff_research_autonomous_discovery_5x_2026-06-10.md (existing DREAMING-SUBSTRATE-SMOKE anchor)
- Sleep defrag generalization note: d:/AI/hd-instrument/notes/research_drill_sleep_defrag_implicit_generalization_3x_2026-06-07.md
- Cross-shard sharding note: d:/AI/hd-instrument/notes/research_drill_sharding_losses_biology_sleep_2x_2026-06-08.md

---

## Contract section

exp_dev owns ALL numerical parameters, cell grid, seed count, queue routing, and smoke profile design.
Research has provided: mechanism upgrade specs (MU-1 through MU-6), pre-reg band definitions, priority ordering of anchors, and literature pointers.
Research has NOT specified: N values per cell, exact threshold values, code paths, queue names, or batch sizes.

## Autonomy declaration

Per [[feedback-no-experiment-design-in-prompts]]: exp_dev designs experiments from anchor pointers + research context. This handoff is a routing document, not a spec. exp_dev should read the research note sections cited in each anchor pointer before designing cells.

Key decision for exp_dev: the existing DREAMING-SUBSTRATE-SMOKE anchor in exp_dev_handoff_research_autonomous_discovery_5x_2026-06-10.md is a v1 design (no MU-1 through MU-6). The anchors in this handoff (Anchor 1: TEMPORAL-ORDER-CONTROL) should run BEFORE the existing v1 smoke, because if Anchor 1 HARD-FAILs, the v1 smoke design is based on a spurious signal. exp_dev should decide whether to hold the v1 smoke pending Anchor 1 result, or run them in parallel (faster but potentially wasted compute if Anchor 1 fails).
