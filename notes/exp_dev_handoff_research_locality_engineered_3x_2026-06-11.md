# exp_dev hand-off -- research: locality_engineered_3x

Filed-by: research sub-agent
Date: 2026-06-11
Trigger: research note d:/AI/hd-instrument/notes/research_drill_locality_engineered_3x_2026-06-11.md

Per [[feedback-no-experiment-design-in-prompts]]: this file names anchor candidates and
context pointers only. exp_dev designs the actual experiment cells autonomously from the
substrate codebase, cap_map, and research note. No inline experiment code or parameter
prescriptions below.

---

## Pause state block

Experiments are permitted if the orchestrator is not paused. Check
d:/AI/hd-instrument/data/orchestrator_paused.flag before dispatching.
Pause-gated: any queue_add.sh call. Annotation bumps to cap_map: allowed while paused.

---

## Anchor candidates (rank-ordered)

### Anchor 1 (TIER-1, HIGHEST PRIORITY)
Pointer: F9 -- Tier-1 frozen + Tier-3 mutable (copy-on-write hierarchical containment)
Substrate-product reading: Tier-1 W_1 is locked read-only after construction. Tier-3 W_3
  accumulates entity-level edits. Retrieval reads W_3 first (entity override), then falls
  through to W_1. Zero risk to universal relational structure from any entity edit.
Why now: purest engineering test; no new math required; integrates directly with existing
  tier architecture; expected HARD PASS (formal guarantee if implemented correctly);
  P_deflated=0.70 (highest of all mechanisms reviewed).
Queue: local CPU (numpy, no GPU needed, N=1024, M=100).

### Anchor 2 (TIER-1)
Pointer: F1 -- Per-shard W_i isolation smoke
Substrate-product reading: split W into S=4 shards by key-hash. Edit 10 facts in SHARD-1.
  Measure delta_acc in SHARD-2/3/4 (expect 0.000). Confirm cross-shard contamination < 0.005.
  If cross-shard = 0 confirmed, this provides structural edit isolation for correlated-key
  byte-LM regime -- closing the gap left open by KF-2 (which only confirmed Kerdock-atom
  isolation). P_deflated=0.52.
Why now: cheapest decisive test for the entire locality framework; 30-second CPU run;
  closes KF-2 open thread for correlated keys.
Queue: local CPU.

### Anchor 3 (TIER-1)
Pointer: D3 -- ROME-style pseudoinverse edit (covariance-deflected rank-1 update)
Substrate-product reading: implement delta_W = (v_new - W*k) * k^T * C^{-1} where
  C = empirical key covariance. Compare collateral damage (E[delta_acc on non-target facts])
  vs naive rank-1 delta_W = (v_new - W*k) * k^T. Expect 2x+ reduction in collateral.
  MEMIT is the validated LLM precedent; substrate W has identical mathematical structure.
  P_deflated=0.57.
Why now: closes the "within-shard correlated-key" gap that F1 does not address (F1 isolates
  shards but does not reduce within-shard bleed; D3 reduces within-shard bleed).
Queue: local CPU (O(N^2) covariance, N=1024 => 4MB, cheap).

### Anchor 4 (TIER-2)
Pointer: F5 -- Bounded-norm edit (epsilon-cap on |delta_W|_F per edit operation)
Substrate-product reading: add 2-line epsilon cap to existing edit path. Verify that
  max delta across all queries never exceeds epsilon after 500 sequential edits. Confirm
  cumulative drift stays bounded (|W_t - W_0|_F < 500 * epsilon).
Why now: retroactive addition to ANY existing substrate version; zero architectural change;
  immediate safety floor even before F1/D3 are implemented.
Queue: local CPU, can piggyback on Anchor 2 cell.

### Anchor 5 (TIER-2)
Pointer: F7 -- Routed-by-role MVCC merge (read-write separation + periodic merge)
Substrate-product reading: maintain W_read (immutable snapshot) and W_write (edit buffer).
  Retrieval reads from W_read. Edits accumulate in W_write. At refresh-cycle boundary,
  atomic merge W_write into W_read. Confirm: (a) retrieval accuracy stable between merges,
  (b) post-merge accuracy reflects all pending edits, (c) rollback (discard W_write) restores
  W_read exactly.
Why now: F7 + F9 together enable the full audit/rollback product capability (F10); integrates
  with substrate v3.1 refresh cycle design already in progress.
Queue: local CPU.

---

## Context pointers (file paths, not summaries)

Research note:
  d:/AI/hd-instrument/notes/research_drill_locality_engineered_3x_2026-06-11.md

KF-2 prior baseline (Kerdock isolation confirmed, correlated-key gap open):
  d:/AI/hd-instrument/notes/exp_dev_to_strategy_instrumentation_suspect_kf2_edit_impact_2026-05-27.md

Type-partitioning cross-thread (per-domain W_d as capacity multiplier + isolation):
  d:/AI/hd-instrument/notes/research_drill_type_partitioning_lit_scan_2x_2026-06-10.md

Substrate v3.0 compositional cliff crossed (current substrate version baseline):
  d:/AI/hd-instrument/memory/substrate_v3_compositional_cliff_crossed.md

Active priorities:
  d:/AI/hd-instrument/notes/active_priorities.md

---

## Contract section

Research has identified 10 locality mechanisms with P_deflated estimates and HARD PASS /
HARD FAIL thresholds. exp_dev's job is to select from the anchor candidates above, build
and smoke-test the implementation, and ship to the appropriate queue. Research does NOT
prescribe experiment parameters, cell structure, or code. exp_dev chooses those from the
substrate codebase and the research note context.

The cheap decisive test (F1 per-shard isolation smoke) is the correct starting point:
it is the fastest path to a binary locality confirmation that grounds the higher-complexity
mechanisms (D3, F7) as follow-ons.

## Autonomy declaration

exp_dev is autonomous on: which queue, cell structure, hyperparameters, smoke vs full,
test sequence order, whether to combine anchors in one cell. exp_dev consults Research if
a mechanism requires new math not in the research note (e.g., if D3 covariance estimation
is unstable at small M and needs regularization choice).
