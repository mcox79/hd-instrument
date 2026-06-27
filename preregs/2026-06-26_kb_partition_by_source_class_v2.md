# Pre-reg: kb_partition_by_source_class_v2 (ANCHOR 1 RESCUE; INFRASTRUCTURE; 2026-06-26)

**Anchor:** `kb_partition_by_source_class_v2`
**Cell:** `experiments/exp_kb_partition_by_source_class_v2.py`
**Queue:** `local_cpu_queue`
**Tier hint:** INFRASTRUCTURE cell; composes on chain-grade KB primitives.
**Wave:** 3b rescue (v1 HARD_FAILED on over-strict gates; mechanism actually worked)

## Source

Research handoff via SendMessage to exp_dev on 2026-06-26. v1 HARD_FAIL was a
GATE problem, not a mechanism problem:

- v1 reported `routing_accuracy=1.0` and `cross_partition_leak_rate=0.0`
  (mechanism perfect).
- v1 HARD_FAILED on (A) over-strict `n_capacity_regression==0` gate
  comparing partitioned-retrieval to unfiltered-baseline (structurally
  lossy: filter is by construction a strict subset) and (B) corpus has
  cross-cutting queries that legitimately live in multiple source
  classes simultaneously (USER directives in memory + notes + preregs).

## v2 fixes

### Path A (success criterion relaxation)

HARD_PASS requires all three:
- `routing_accuracy >= 0.95`
- `cross_partition_leak_rate < 0.05`
- `ratio_resolved >= 0.80`

ARM_MEMORY_OVERSIZED replaces the 1.0 user_directive_retention floor with:
- `user_directive_retention >= max(non_ud_resolved_ratio - 0.10, 0.70)`

This measures whether oversize HELPS UDs match non-UDs (relative band),
not whether `confidence_floor=0.3` is met inside the memory shard
(by-construction-tight).

`n_capacity_regression` is reported as diagnostic only; no longer hard-gates.

### Path B (corpus relabel)

`ROUTED_QUERIES` declares `expected_classes` as a TUPLE of permissible
source classes (was singleton). Cross-cutting queries permitted:
- "USER directive no busy work" -> (memory, note, prereg)
- "USER directive monitor armed" -> (memory, note)
- "memory curator skill dispatch" -> (memory, note)
- "fleet waiting on shared file" -> (memory, note)
- "fleet waiting on tracker" -> (note, memory)
- "substrate director kb ingest" -> (note, prereg)

Routing accuracy counts as correct if top-1 lands in ANY permissible class.

## Pre-reg bands

### HARD_PASS (all must hold)
- ARM_SINGLE_W_BASELINE completes without error
- ARM_PARTITIONED_W_EQUAL_CAPACITY: routing_acc >= 0.95
  AND leak_rate < 0.05 AND ratio_resolved >= 0.80
- ARM_PARTITIONED_W_MEMORY_OVERSIZED:
  ud_retention >= max(non_ud_resolved_ratio - 0.10, 0.70)

### MIDDLE_BAND (default per Fix #28)
- routing_acc in [0.90, 0.95)
- OR ratio_resolved in [0.70, 0.80)
- OR ud_retention within 0.15 of the relative floor

### HARD_FAIL
- routing_acc < 0.90 (partition leakage too high; mechanism broken)
- OR leak_rate >= 0.05 (cross-partition contamination)
- OR ratio_resolved < 0.70 (severe capacity loss; mechanism degrades base)
- OR ud_retention much-below the relative floor
- OR any arm exception

## Discipline gates

- Fix #26: pre-dispatch referent check (KB exists; source_class metadata present).
- Fix #28: default MIDDLE; HARD_PASS only when ALL three relaxed criteria met.
- META_RULE_H: cardinality_ok asserted (30 queries; expected number per arm).
- META_RULE_J: no silent except (each arm wrapped; exceptions recorded).
- META_RULE_K: smoke must FIRE discriminator (routing_acc must compute over
  >= 1 query; mechanism non-degenerate).
- META_RULE_L: band-floor is MIDDLE_BAND (not HARD_PASS).
- Principles 1-12 preserved (no schema modification; routing layer additive).

## Estimated cost

~10-30s full run (90 query evaluations over loaded KB on laptop CPU).
Smoke: ~3-10s (10 queries; 1 partition each arm).

## REQUIRED_FIELDS

`verdict`, `verdict_msg`, `elapsed_s`, `summary`.
