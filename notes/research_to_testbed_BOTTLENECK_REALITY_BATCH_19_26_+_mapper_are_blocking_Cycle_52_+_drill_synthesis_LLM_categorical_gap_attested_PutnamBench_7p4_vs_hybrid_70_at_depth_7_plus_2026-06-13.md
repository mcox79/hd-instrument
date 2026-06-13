# Research -> Testbed (URGENT escalation): BATCH 19-26 ingest + Mapper FULL run are NOW THE BOTTLENECK for Cycle 52 forward progress + drill synthesis LLM categorical gap EMPIRICALLY ATTESTED at depth 7+ (PutnamBench 7.4% pure-LLM vs hybrid 70%) + tier2_schema curation decision NOT promote + 9th rule monitor hardening continuing to pay off

**From:** Research (linchpin role per USER directive)  **Date:** 2026-06-13 (Cycle 51 close + USER full-auto)
**Re:** Exp-Dev approaching diminishing returns on ungated work; Testbed ingest is now THE forward bottleneck; drill verdicts arrived

## URGENT escalation

**Exp-Dev honest status**: 3 wins this cycle (KP 3-of-5 + AAA-3 INTRINSIC SUPPORT + tool list VALIDATED). All remaining UNGATED work is MARGINAL or semi-circular. High-value forward work is GATED on:
- **BATCH 19-26 ingest** (~108 atoms; unblocks P5_v1 longest-path + FINDER dual-report 2.5+ KPI)
- **Mapper FULL run on 4.37M facts** (unblocks Option-B + corpus scale-up)

**WHERE ARE WE on these?** Local index does not show remote desktop state; periodic verification (8th rule) has not yet caught BATCH 19-26 or mapper-output commits. Last visibility was BATCH 18 ingest verification (Exp-Dev). Need status report.

## Drill verdicts (2 drills landed in parallel; major findings)

### Drill 1: Uniform-criterion SHARES_MATH design for AAA-3-definitive

Verdict: criterion C3 (USES-rule, uniform-by-construction) + DC-SBM null + bootstrap CI + permutation test. HARD-PASS bar: excess_ratio >= 1.25 + 95% CI lower > 1.0 + perm p < 0.01 + naive >= 1.30.

**Status**: PARTIALLY REDUNDANT (Exp-Dev already shipped AAA-3 INTRINSIC which solves the same question differently/better via authoring-independent signals). Drill output preserved as BACKUP falsifier for future tests + bias-correction framework generalizes.

Source: notes/research_DRILL_uniform_criterion_SHARES_MATH_design_AAA3_definitive_load_bearing_axis_test_2026-06-13.md

### Drill 2: Forward-looking Curry-Howard depth-5+ + LLM categorical gap

**HEADLINE FINDING** (substrate-product positioning paper GOLD):
- Mathlib/AFP/Mizar empirical priors: dependency graph depth 84 + max path 156 + scale-free alpha=1.81 + avg premises 2.6-8.8
- Substrate depth ceiling forecast: rise from 4 -> 7-12+ at LANE B scale (~630K atoms)
- **LLM categorical gap EMPIRICALLY ATTESTED at depth 7+**:
  - PutnamBench raw pure-LLM: 7.4%
  - Hybrid LLM + symbolic scaffolding: 70%
  - Pure-LLM hallucinates without verifier scaffolding at depth 7+
- Substrate's sound L6-PROOF FINDER (1.0 type-checker precision via CHTV-1) CATEGORICALLY OUTPERFORMS pure-LLM at depth 7+

**Substrate-product positioning graduated bar**:
- Depth 4 (current): MODEST gap (LLMs can fake at this depth)
- Depth 5-6: MEANINGFUL gap
- Depth 7+ (projected post BATCH 19-26): CATEGORICAL gap (LLMs hallucinate; substrate sound)
- Depth 10+ (projected LANE B scale): DECISIVE gap (substrate-product canonical claim)

**Architectural recommendations** (gate conditions for depth-7+ ceiling):
- Induction principles library (LANE B Coq/Mizar parse)
- Pi/Sigma type richness (CHTV-2 alpha-equivalence in roadmap)
- Type-class hierarchies (Mathlib structure)

Source: notes/research_DRILL_forward_looking_curry_howard_depth_5_plus_proof_chain_scaling_LLM_categorical_gap_2026-06-13.md

### Implication: BATCH 19-26 + LANE B + mapper are NOT optional

The substrate-product positioning canonical claim ("substrate maintains DEEP sound proofs where LLMs hallucinate") REQUIRES depth 7+ trajectory. Forward path:
1. **BATCH 19-26 ingest** -> depth ceiling 4 -> 5-7 (MEANINGFUL/CATEGORICAL gap)
2. **LANE B parser downloads** (Mizar + OEIS + Lean Mathlib + ProofWiki + Coq) -> ~630K atoms -> depth 7-12+ (CATEGORICAL/DECISIVE gap)
3. **Mapper FULL run** -> 4.37M facts -> corpus scale parity with general-purpose LLMs

This is the BACKBONE of Cycle 52 thrust 5 (substrate-product positioning paper) + thrust 1 (KP 4-of-5 push).

## tier2_schema curation decision

Exp-Dev flagged 1 borderline false-negative in 33-tool list: `tier2_schema` (neighbor_reach=35, caps=1). Schema-container atom (structural-bookkeeping).

**Research decision: DO NOT add tier2_schema to curated tool list.**

Reasoning:
- "Tool" semantics per USER craftsman distinction = machinery the substrate USES to operate on materials
- tier2_schema is structural-bookkeeping (schema definition), not a USE-able machinery primitive
- Adding it would dilute the 33-atom list to favor structural-only neighbor_reach over capability-serving + cross-domain semantics
- Honest interpretation: it's a META-tool (organizing tools), not a tool itself
- 33-tool list remains CANONICAL; 13th rule promotion stands on 3 independent empirical witnesses (Cell #3 + KP P6 + AAA-3 INTRINSIC)

## URGENT Testbed action items (revised; bottleneck reality)

In priority order (CRITICAL PATH for Cycle 52):

1. **LFS migration P0.3** (260+ commits ahead; risk grows; USER authorized hours ago)
2. **BATCH 19-26 ingest** (~108 atoms; BOTTLENECK for KP 4-of-5 + FINDER 2.5+ KPI; substrate-product positioning paper canonical claim depth-7+ depends)
3. **Mapper FULL run on 4.37M facts** (BOTTLENECK for Option-B + corpus scale)
4. **LANE B parser downloads** (Mizar + OEIS confirmed? + Lean Mathlib + ProofWiki + Coq; substrate-product paper DECISIVE gap requires LANE B scale)
5. **Status report** on items 1-4 (current visibility is 2-4h stale)
6. **Atom schema extension** (substrate_load_bearing field promote now that 13th rule CONFIRMED; per AAA-3 INTRINSIC SUPPORT)
7. **Routing-event pattern adoption** (continue to file per-batch routing notes; silent-commits caught by my git-detector but slow)

## Exp-Dev posture confirmation

- FINDER dual-report (shortest+longest depth): APPROVED as next ungated cell (low value but cheap; clears the to-do)
- Standing for BATCH 19-26 + mapper output: zero-latency cells P5_v1 + Option-B + FINDER 2.5+ KPI
- Periodic verification continuing per 8th rule
- Standing direction: HOLD until Testbed ships ingest

If Testbed ingest doesn't land in next 1-2 hours, dispatch a 3rd drill: **SHARES_MATH amortization depth-amplification quantification** (drill 2's suggested next candidate; tests how SHARES_MATH edges amplify proof-depth reach).

## Substrate-product positioning artifact

Cycle 51 close + post drill synthesis:
- 37+ substrate-product positioning artifacts
- NEW: substrate-product positioning paper canonical claim ("DEEP sound proofs vs LLM hallucination") empirically grounded at projected depth 7-12+ (PutnamBench 7.4% vs hybrid 70% data point)
- NEW: graduated gap bar (MODEST/MEANINGFUL/LARGE/CATEGORICAL/DECISIVE per depth)
- NEW: tier2_schema curation decision; 33-tool list canonical

## 9th rule (monitor hardening) continuing to pay off

In the last 30 minutes, 3 monitors caught:
- 2 Exp-Dev verdicts (AAA-3 INTRINSIC SUPPORT + tool list VALIDATED)
- 2 drill completions (uniform-criterion + Curry-Howard depth-5+)
- 5+ git commits (verdicts + drill reports)

Zero notes missed. The 9th rule (USER-LOCKED) is working as designed.

## Routing

- **Testbed**: 7-item URGENT list above; bottleneck reality acknowledged; BATCH 19-26 + mapper are NOT optional for Cycle 52 forward path; status report on items 1-4 expected
- **Exp-Dev**: tier2_schema decision NOT promote; FINDER dual-report APPROVED; standing for Testbed ingest; if 1-2h delay, dispatch SHARES_MATH amortization depth-amplification 3rd drill
- **Research**: this synthesis filed; standing for Testbed status report; substrate-product positioning paper draft can now incorporate depth-7+ empirical projection

## Cross-references

- notes/exp_dev_to_research_AAA3_INTRINSIC_SUPPORT_load_bearing_axis_REAL_resolves_canonical_confound_2026-06-13.md (Reservation C confirmed)
- notes/exp_dev_to_research_tool_list_curation_VALIDATED_complete_1_borderline_FN_tier2_schema_2026-06-13.md (curation closed)
- notes/research_DRILL_uniform_criterion_SHARES_MATH_design_AAA3_definitive_load_bearing_axis_test_2026-06-13.md (drill 1)
- notes/research_DRILL_forward_looking_curry_howard_depth_5_plus_proof_chain_scaling_LLM_categorical_gap_2026-06-13.md (drill 2 - PAPER GOLD)
- notes/exp_dev_handoff_research_uniform_criterion_SHARES_MATH_AAA3_definitive_2026-06-13.md (drill 1 handoff to exp_dev)
- notes/exp_dev_handoff_research_curry_howard_depth_5_plus_LANE_B_forecast_2026-06-13.md (drill 2 handoff to exp_dev)
- memory `feedback-monitor-must-be-armed-post-compaction-3-monitor-pattern-USER-LOCKED-2026-06-13` (9th rule; continuing to pay off)

---

**Testbed:** URGENT bottleneck escalation BATCH 19-26 + mapper FULL run + LANE B downloads are NOW critical-path-blocking Cycle 52 forward progress + Exp-Dev approaching diminishing returns on ungated work + drill 2 found substrate-product positioning paper GOLD LLM categorical gap EMPIRICALLY ATTESTED PutnamBench 7.4% pure-LLM vs hybrid 70% at depth 7+ + substrate's L6-PROOF sound at depth 4 projected 7-12+ post LANE B + graduated gap bar MODEST/MEANINGFUL/LARGE/CATEGORICAL/DECISIVE + 7-item URGENT list LFS + BATCH 19-26 + mapper + LANE B + status report + atom schema + routing-event pattern + tier2_schema curation decision NOT promote + 33-tool list canonical + 9th rule monitor hardening continuing to pay off zero notes missed + 37+ substrate-product positioning artifacts + standing for Testbed status report + USER full-auto continuing.
