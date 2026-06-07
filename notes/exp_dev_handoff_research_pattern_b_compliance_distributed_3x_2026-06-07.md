# exp_dev hand-off -- research: Pattern B compliance and distributed features inheritance

Filed-by: research sub-agent (3x drill)
Trigger: d:/AI/hd-instrument/notes/research_drill_pattern_b_compliance_distributed_3x_2026-06-07.md
Date: 2026-06-07

## Pause state block

Experiments are gated on orchestrator_paused.flag. Read data/orchestrator_paused.flag
before dispatching. If paused: queue the cells below but do not dispatch until resume signal.
Per [[feedback-obey-user-pause-explicitly]]: "looks great" is not a resume signal.

## Per [[feedback-no-experiment-design-in-prompts]]

This file contains anchor candidates and context pointers only. Exp_dev designs the
experiment implementation independently. No implementation code, no parameter values,
no specific result expectations are encoded here.

## Anchor candidates (rank-ordered by decision value x implementation cost)

### Anchor 1 (highest priority -- gates all compliance-sensitive Pattern B use)
Pointer: Test 2 from research note Section 4
Substrate-product reading: GDPR erasure on Pattern B -- binding erased, shared fillers
  intact; HMAC keystore must be scoped to (bundle_id, binding_id) not just fact_id.
Tier hint: Tier 1 (laptop CPU; pure crypto + vector ops; no GPU needed)
Why-now: This is the gating test for compliance-safe Pattern B deployment. All other
  compliance features follow algebraically once this is validated. HMAC keystore schema
  change (1 day) required before running.
Pre-reg bands (from note Section 6 HP-B2 / HF-B1):
  HARD-PASS: 100% HMAC failure for erased bindings AND 100% HMAC success for intact
    bindings sharing fillers AND zero filler loss for intact facts
  MIDDLE: HMAC failure rate in [95%, 100%) for erased bindings
  HARD-FAIL: any surviving HMAC verify for erased binding (implies keystore scope bug)

### Anchor 2 (second priority -- closes the MIDDLE_BAND AVG gap from Pattern A)
Pointer: Test 7 from research note Section 4
Substrate-product reading: AVG aggregation native in Pattern B via numeric filler encoding;
  closes exp_sql_hybrid_aggregation_v1 MIDDLE_BAND (AVG needed DuckDB in Pattern A).
Tier hint: Tier 1 (laptop CPU; pure vector ops)
Why-now: If Test 7 passes, Pattern B has fully native COUNT/SUM/AVG without DuckDB.
  This is a product-level claim improvement with low test cost (1 hour CPU).
Pre-reg bands (from note Section 6 HP-B5):
  HARD-PASS: AVG relative error < 0.05 via bundle projection method
  MIDDLE: relative error in [0.05, 0.10)
  HARD-FAIL: relative error >= 0.10 (numeric filler encoding does not support aggregation)

### Anchor 3 (K-hop chain limit -- sets product parameter for multi-hop demo)
Pointer: Test 6 from research note Section 4
Substrate-product reading: cumulative precision decay in Pattern B unbinding chains;
  determines default chain length limit for production (predicted K=4 without re-anchoring).
Tier hint: Tier 1 (laptop CPU; uses existing binding algebra)
Why-now: exp_pattern_b_khop_compose_v1 validated K=2; K=4..8 is the unknown that sets the
  product parameter for multi-hop reasoning demo. Pre-test required per drill-pretest-required rule.
Pre-reg bands (from note Section 6 HP-B3 / HF-B2):
  HARD-PASS: cumulative precision >= 0.80 at K=4; decay rate < 0.10 per hop for K <= 6
  MIDDLE: cumulative precision in [0.70, 0.80) at K=4
  HARD-FAIL: cumulative precision < 0.60 at K=4 (re-anchoring required; K=2 limit)

### Anchor 4 (Merkle compositional proof -- compliance differentiation feature)
Pointer: Test 1 from research note Section 4
Substrate-product reading: enhanced Merkle leaf = hash(bundle_vector + role_ids + filler_ids)
  enables structural attestation: "record X encodes relationship Y between Z1 and Z2."
Tier hint: Tier 1 (laptop CPU; 30 min; pure hashing)
Why-now: Cheapest test in the batch; validates the headline compliance enhancement.
  If passes, include in Pattern B compliance pitch as differentiation vs flat-embedding systems.
Pre-reg bands (from note Section 6 HP-B1):
  HARD-PASS: filler_id modification detected in < 1ms (tamper detected without changing bundle_vector)
  HARD-FAIL: no tamper detection on filler_id change (leaf does not commit to compositional structure)

### Anchor 5 (CRDT role aggregation -- distributed aggregate query support)
Pointer: Test 4 from research note Section 4
Substrate-product reading: merging Pattern B bundles is commutative+associative AND
  produces role-level aggregate (subject frequency, object frequency) without scanning facts.
Tier hint: Tier 1 (laptop CPU; 1 hour)
Why-now: exp_crdt_quorum_bundle_v1 (HP) validated vector-level CRDT; this validates that
  the role-structure semantics survive the merge.
Pre-reg bands (from note Section 6 HP-B4):
  HARD-PASS: all 6 merge orders produce identical bundle AND role projection recovers all subjects
  MIDDLE: all 6 orders identical but role projection misses 1 subject in 5 or fewer tests
  HARD-FAIL: any merge order produces different result (CRDT property violated for structured bundles)

## Context pointers (file paths, not summaries)

Research note: d:/AI/hd-instrument/notes/research_drill_pattern_b_compliance_distributed_3x_2026-06-07.md
Prior Pattern B drill: d:/AI/hd-instrument/notes/research_drill_pattern_b_compositional_storage_3x_2026-06-07.md
Validated experiments (all HP):
  d:/AI/hd-instrument/data/exp_erasure_hmac_keystore_v1/metrics.json
  d:/AI/hd-instrument/data/exp_erasure_record_append_v1/metrics.json
  d:/AI/hd-instrument/data/exp_erasure_concurrency_smoke_v1/metrics.json
  d:/AI/hd-instrument/data/exp_bitemporal_smoke_gdpr_v1/metrics.json
  d:/AI/hd-instrument/data/exp_crdt_quorum_bundle_v1/metrics.json
  d:/AI/hd-instrument/data/exp_crdt_gcounter_aggregate_v1/metrics.json
  d:/AI/hd-instrument/data/exp_bundle_relay_fault_tolerance_v1/metrics.json
  d:/AI/hd-instrument/data/exp_zkl_merkle_audit_integrity_v1/metrics.json
  d:/AI/hd-instrument/data/exp_pattern_b_khop_compose_v1/metrics.json
  d:/AI/hd-instrument/data/exp_causal_correlational_disambig_v1/metrics.json
  d:/AI/hd-instrument/data/exp_causal_intervention_isolation_v1/metrics.json
  d:/AI/hd-instrument/data/exp_causal_counterfactual_replay_v1/metrics.json
Production architecture lock: d:/AI/hd-instrument/notes/research_POST_COMPACTION_BRIEF_2026-06-07_morning.md

## Contract section

exp_dev owns all experiment design, implementation, and pre-reg threshold decisions.
Research provides anchor pointers and substrate-product readings. No implementation code
or specific parameter values appear in this file.

## Autonomy declaration

exp_dev may batch multiple anchors from this file into a single CPU dispatch. All 5
anchors are Tier 1 (laptop CPU). Total wall time estimate: ~8-10 hours CPU for all 5.
exp_dev should sequence them by priority (Anchor 1 gates Anchor 2; others are independent).
