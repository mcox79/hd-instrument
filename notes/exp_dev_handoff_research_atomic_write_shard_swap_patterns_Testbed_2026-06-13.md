# exp_dev hand-off -- research: atomic write + shard-swap patterns for PartitionedStore

Filed-by: research (Opus drill 2026-06-13)
Trigger: operational urgency from Testbed -- JSONDecodeError race on per-file write + transient near-empty whole-relations during bulk re-shard (atoms 1758->1847 growing while DEPENDS_ON 2251->12, SHARES_MATH 332->0 mid-rebuild). See research note:
  notes/research_DRILL_atomic_write_shard_swap_patterns_Testbed_operational_urgent_substrate_2026-06-13.md

Pause state: respect data/orchestrator_paused.flag. Patterns 1 and 3 are NON-experiment infrastructure changes (writer wrapper + reader wrapper); they do not consume GPU and do not need to be queued as anchors. They can ship through Testbed even when paused, since they reduce risk of silent-wrong-data rather than expanding it. Pattern 2 (CURRENT-pointer architecture) IS a substrate-architecture change and SHOULD be pre-reg'd as a scratch-shard experiment before going production.

Per [[feedback-no-experiment-design-in-prompts]]: I am NOT specifying experiment design here. exp_dev decides queue ordering, pre-reg envelope, smoke gate. I am providing anchor candidates ranked by urgency + tier hint.

## Anchor candidates (rank-ordered)

### Anchor 1 (urgent, low risk, drop-in): atomic_write wrapper for all JSONL writers

- Anchor pointer: `tools/atom_store_atomic.py` (new file) + grep for every existing JSONL writer in Testbed pipeline and wrap.
- Substrate-product reading: eliminates JSONDecodeError class entirely on POSIX, ~95% on Windows. Zero schema change. Direct fix for today's hazard #1.
- Tier hint: tier-1 infrastructure (LOW Goodhart risk; standard industry practice with 9 cited precedents).
- Why now: ongoing JSONDecodeError races corrupt cell reads RIGHT NOW. Cheap to ship. Reversible.
- Pre-reg sketch (exp_dev fills envelope): scratch-shard test per research note section (b) -- 2 readers + 1 ingest writer concurrent for 60s, target 0 JSONDecodeError.

### Anchor 2 (urgent, low risk, defensive): StoreReader wrapper with row-count sentinel

- Anchor pointer: `tools/store_reader.py` (new wrapper class) + route KP P1 + CH-P6 cells through it first.
- Substrate-product reading: cell refuses to return wrong data when shard count drops below 80% of last-known-good -- closes the "silently-wrong relation read" failure mode that corrupts downstream reasoning. FIRST concrete instantiation of "substrate refuses to return wrong data" as a runtime invariant.
- Tier hint: tier-1 substrate-product differentiator (this is the substrate-specific synthesis from the research drill, NOT borrowed verbatim from a DB).
- Why now: complements Anchor 1; together they cover both write-race (Anchor 1) and bulk-rebuild-transient (Anchor 2) hazards.
- Pre-reg sketch: false-positive rate target <= 5%; detection rate for mid-rebuild >= 99%. Validate on synthetic mid-rebuild snapshot.

### Anchor 3 (architectural, deferred, needs scratch-shard pre-reg): CURRENT pointer + snapshot directory layout

- Anchor pointer: `data/store/CURRENT` + `data/store/snapshots/<version>/` layout per research note section (d) Pattern 2.
- Substrate-product reading: gives substrate free rollback (verdict regression -> flip CURRENT back to previous snapshot in O(1)); MVCC-style snapshot isolation without a DB server; eliminates bulk-rebuild transient-empty window architecturally.
- Tier hint: tier-2 architecture refactor (HIGH leverage but non-trivial migration; defer until Anchors 1+2 are stable).
- Why now: NOT now. Queue after Anchors 1+2 ship and validate. Should be its own scratch-shard pre-reg before going production. Migration plan: one relation type at a time (start with SHARES_MATH).
- Pause-gate: this anchor IS gated by the orchestrator_paused.flag because it changes substrate architecture.

## Context pointers (file paths only -- no summaries)

- Research note: `d:/AI/hd-instrument/notes/research_DRILL_atomic_write_shard_swap_patterns_Testbed_operational_urgent_substrate_2026-06-13.md`
- Substrate filesystem layout: `d:/AI/hd-instrument/data/store/` (PartitionedStore root, find via `Glob` -- I am NOT pre-resolving exact paths to keep exp_dev autonomy)
- Memory rule index: `feedback_research_external_corpus_inventory_requires_grep_git_log_notes_before_asserting_not_built_2026-06-13.md` (GREP-FIRST applies before exp_dev asserts which JSONL writers exist)
- Verify-before-asserting cluster memory: `substrate_methodology_rule_verify_before_asserting_5_class_cluster_cycle_51_2026-06-13.md` (applies to the scratch-shard validation envelope)

## Contract

- I (research) did NOT design experiments. I named anchors + cited precedents + flagged HARD-PASS / HARD-FAIL thresholds. exp_dev owns pre-reg envelope, smoke gate, queue ordering.
- exp_dev MAY reorder anchors. Recommended order is 1 -> 2 -> validate -> 3.
- Anchors 1 + 2 SHOULD ship even under pause flag (risk-reducing infra, not capability expansion). Anchor 3 should NOT ship under pause flag.
- If exp_dev finds an existing writer already wraps with atomicwrites lib or filelock, respect prior art and only patch the gap.

## Autonomy declaration

exp_dev decides:
- Whether to use python-atomicwrites pypi package vs. inline implementation
- Whether to ship Pattern 1 as a context-manager wrapper or a function
- Which cells to route through StoreReader first (KP P1 + CH-P6 is a recommendation, not a mandate)
- Whether to validate on WSL/POSIX in addition to Windows (recommended, not required)
- Pre-reg envelope-fail-bands per [[feedback-envelope-fail-bands]]
- Smoke-gate criteria
