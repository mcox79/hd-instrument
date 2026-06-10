# Research -> Exp-Dev: lift-validation gap tests (3 anchors)

**From:** Research  **Date:** 2026-06-10
**Re:** Audit found 0 new silent overclaims but 3 documentation gaps need empirical verification

## 3 gap tests

### GAP-1 PP-292 retrieval-only baseline (HIGHEST PRIORITY)
- Pre-empts meta-learning K-sweep escalation
- Run plain substrate retrieval (no episode format) on same 1500 queries
- Pre-reg: plain_acc > 0.700 = HARD-FAIL for method (episode adds nothing)
- Pre-reg: plain_acc < 0.650 = HARD-PASS (method genuinely adds value)
- Pre-reg: 0.650 ≤ plain_acc ≤ 0.700 = MIDDLE (inconclusive lift)
- **Cost:** minutes CPU; reuses existing data

### GAP-2 PP-310..PP-312 flat-bundle comparison
- Document N per shard for each of story/program/argument
- Run flat-bundle (no compositional structure) at equivalent total atom counts: 50K + 5K + 1K
- Pre-reg HARD-PASS: flat-bundle recall < 0.85 AT 50K (story); composition adds genuine lift
- Pre-reg HARD-FAIL: flat-bundle recall = 1.000 at 50K (composition is artifact at chosen N)
- **Cost:** moderate; same data, different bundle structure

### GAP-3 PP-274 chance-rate documentation
- Compute 1/N_classes for the task
- Add to PP-274 row annotation
- No new experiment; documentation fix
- **Cost:** zero CPU

## Discipline rule (memory)

Method-comparison anchors must pre-register lift thresholds:
- baseline_estimate (what method-WITHOUT-rescue would score)
- lift_threshold_2se (above-noise gate)
- lift_threshold_5se (decisive gate)

Capability anchors with paired baselines (cleanup-vs-no-cleanup) already satisfy this.

## Strategic significance

- GAP-1 resolves: meta-learning rescue claim REAL or artifact
- GAP-2 resolves: production-scale shard claim REAL or trivial
- GAP-3 resolves: PP-274 saturation claim CONTEXT-grounded

All 3 are cheap CPU verifications. Run before extending production claims.

## Cross-references
- Audit drill: notes/research_drill_lift_validation_audit_2x_2026-06-10.md
- LVH-274 (caught at cycle 220): cycle 220 strategy_decisions
- LVH-272 (caught at cycle 215)
- feedback_method_overclaim_lift_validation memory rule
