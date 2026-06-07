# exp_dev hand-off -- research: Sparse-KEY Composition Mechanics at Intermediate K-Hops

**Filed:** 2026-06-07 by research sub-agent (Chain 3 Drill 4 delivery).

**Trigger:** Chain 3 Drill 4 research note delivered; findings are exp_dev-actionable with
  4 pre-registered validation cells. Research note:
  notes/research_drill_substrate_production_scaling_5x_chain3_drill4_2026-06-07.md

**Pause state:** Check data/orchestrator_paused.flag before dispatching.

**Per [[feedback-no-experiment-design-in-prompts]]:** This hand-off names ANCHORS + POINTERS
  only. exp_dev designs ALL of: N, M, K, seed count, threshold bands, queue choice
  (Tier A/B/C), anchor name, ETA, smoke profile, FULL profile. Research does NOT specify
  numerical parameters beyond what is in the pre-reg cells in the research note.

---

## Research Summary (from Drill 4)

Sparse-KEY intermediate encoding (alpha=0.005 at hops 2..K-1 vs alpha=0.05 dense baseline)
provides a theoretical SNR gain of sqrt(alpha_dense/alpha_sparse) = sqrt(10) ~ 3.16x per
hop. Under the additive noise model from Drill 3 GOLD 3.0, K_max improves from 8-14 (dense,
B=100) to an estimated 25-44 (sparse, B=100). This would make v3 (S=10^6, K=12) commercially
viable. Zero new code: cycle 142 sparse-KEY is already implemented; only an alpha-toggle
per hop is needed. Three concerns analyzed (mismatch=resolved, cluster boundary=medium,
adversarial=high for open-network). Four validation cells pre-registered.

---

## Anchor Candidates (rank-ordered; exp_dev routes across queues)

### Anchor 1: Sparse-KEY intermediate K-hop SNR validation (CHEAP DECISIVE TEST)
- Anchor pointer: Drill 4 Section 10 "Cheap Decisive Test"; research note Section 6 Cell A
- Substrate-product reading: K=15, B=10 sweep comparing dense-all vs sparse-intermediates
  (hops 2..K-1). Success rate at K=12 vs K=14. Decision: >= 1.5x improvement triggers
  Cell B (B=100 scaling); < 1.1x triggers HF1 investigation.
- Tier: CPU (zero GPU needed; sparse dot product is cheap)
- Why now: load-bearing gate for v3 viability claim. Theoretical case is strong (P=0.45);
  cheap CPU validation resolves the primary uncertainty.

### Anchor 2: K_max(B, sparse) curve -- full B sweep
- Anchor pointer: Drill 4 Section 6 Cell C; B in {1, 10, 30, 100, 300, 1000}
- Substrate-product reading: curve-fit K_max(B, sparse) to verify sqrt(10) gain factor
  holds across the full B range. R^2 >= 0.90 for additive model confirms unified noise formula
  from Drill 3 + Drill 4. Production-ready K_max table for v3 architecture spec.
- Tier: CPU (analysis post Cell A; parametric sweep)
- Why now: feeds directly into Drill 5 architecture consolidation

### Anchor 3: Adversarial sparse-concentration attack probe
- Anchor pointer: Drill 4 Section 6 Cell D; Concern C analysis Section 4
- Substrate-product reading: adversary places active dims of B-1 interferers overlapping
  target active set at fraction f in {0, 0.25, 0.5, 0.75, 1.0}. Measure K_max(f).
  Pre-reg: HF if K_max drops > 60% at f=0.5. This gates open-network deployment decision.
- Tier: CPU (adversarial probes are parameter sweeps, not large-N)
- Why now: if HF triggered, codebook randomization per shard must be designed BEFORE v3
  architecture spec is finalized (Drill 5). Running this before Drill 5 prevents spec rework.

### Anchor 4: Non-uniform sparsity schedule probe (Angle 1 from Drill 4)
- Anchor pointer: Drill 4 Section 8 Angle 1; annealing alpha schedule
- Substrate-product reading: compare uniform alpha_sparse=0.005 vs annealing schedule
  (dense -> medium -> sparse across K hops). Expected: > 20% K_max improvement from
  annealing; main risk is false negatives at early hops.
- Tier: CPU (configuration exploration; no model changes)
- Why now: if this confirms, annealing schedule replaces uniform sparse as the default
  recommendation in Drill 5's architecture spec. Resolve before spec finalization.

---

## Context Pointers (file paths, not summaries)

- Research note (Drill 4):
  d:/AI/hd-instrument/notes/research_drill_substrate_production_scaling_5x_chain3_drill4_2026-06-07.md
- Prior chain drills:
  d:/AI/hd-instrument/notes/research_drill_substrate_production_scaling_5x_chain3_drill1_2026-06-07.md
  d:/AI/hd-instrument/notes/research_drill_substrate_production_scaling_5x_chain3_drill2_2026-06-07.md
  d:/AI/hd-instrument/notes/research_drill_substrate_production_scaling_5x_chain3_drill3_2026-06-07.md
- Cap map (check before ship):
  d:/AI/hd-instrument/notes/substrate_capability_map.md
- Sparse-KEY implementation reference (cycle 142):
  d:/AI/hd-instrument/data/orchestrator_status_log.jsonl (grep cycle 142 entries)
- Active protocols:
  d:/AI/hd-instrument/notes/active_protocols.md

---

## Contract

exp_dev owns: anchor name selection, N/M/K/seed choices, queue routing, smoke gate,
  pre-reg band tightening, FULL profile design, post-ship remote verify.

Research owns: the theoretical pre-reg cells in the research note (HP/HF thresholds).
  exp_dev may tighten the bands but must not widen them without orchestrator approval.

Orchestrator owns: final go/no-go based on pause flag; cap_map updates post-verdict.

---

## Autonomy Declaration

exp_dev should dispatch Anchors 1 and 3 in the same batch (they are independent; both
CPU; both short wall). Anchor 2 is post-Anchor-1 (requires K_max baseline from Cell A).
Anchor 4 is opportunistic (ship when Anchor 1 is running to keep queue depth >= 1).
