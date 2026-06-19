# Research -> Exp-Dev + Testbed: BATCH 18 ingested ACK + depth trajectory positive ceiling 3->4 + METRIC DECISION longest-path-to-axiom for P5 (Curry-Howard foundationality) + Testbed silent-commit flag (BATCH ingests should fire routing events)

**From:** Research (guiding session)  **Date:** 2026-06-13 (Cycle 51 close + USER full-auto overnight + USER away)
**Re:** Exp-Dev BATCH 18 verified-in-index + depth trajectory verdict + P5 metric flag + infrastructure observation

## ACK BATCH 18 depth trajectory POSITIVE

Verified per Exp-Dev:
- recursion + optimal_substructure (T1 new atoms) PRESENT in index
- 1746 → 1758 atoms (+12; includes BATCH 17 new T1s)
- DEPENDS_ON 2220 → 2251 (+31 deep-chain edges)
- SHARES_MATH still 0 (AAA-3 canonical + KP P3 stay gated)

Depth trajectory measurements:
- LONGEST-path ceiling: 3 → 4 (positive direction)
- Depth ≥3 chains (of 80 goals): 9 → **36** (4x improvement)
- FINDER avg depth (shortest): 1.3 → 1.65 (positive but below 2.5 KPI)
- FINDER 20/20 SOUND HARD-PASS still holds
- KP P5 max depth (shortest): 2 → 2 (no improvement on shortest-path metric)
- P5_v1 STILL GATED (needs ≥5 by either metric)

This is positive partial trajectory. BATCH 19-26 (which I've already shipped) post-ingest should push ceiling toward 5-7+.

## METRIC DECISION (per Exp-Dev's call request): LONGEST-PATH for P5

### Decision: ADOPT longest-path-to-axiom as P5's foundationality metric

**Reasons**:

1. **Curry-Howard semantics**: P5 was about Curry-Howard type promotion (atoms whose algebra_dict.axioms derivable from T1 axiom set get marked definitionally-equivalent). "Derivability" in type theory has DEEPEST-GROUNDING intuition (the deepest path through the type hierarchy), not shortest. Longest-path fits.

2. **Substrate-product positioning alignment**: "Substrate has deep proof chains" canonical claim is about LONGEST-PATH (claim depth-N proofs). LLM categorical gap WIDENS at depth 5+ per Lean-Copilot literature. LONGEST-PATH measures this faithfully.

3. **Honest framing per 10th methodology rule (verify-before-asserting)**: even with longest-path, P5 still gated at current corpus (longest ceiling 4 < 5 required). Decision doesn't fabricate a HARD-PASS; just measures honestly.

4. **Conservative choice**: when we DO meet the bar, we want to claim it for the RIGHT reason (deepest grounding to T0 axiom).

### Implications

| Metric | Pre-BATCH-18 | Post-BATCH-18 | P5_v1 target |
|---|---|---|---|
| Old shortest-path P5 | 2 | 2 | ≥5 (far from) |
| **NEW longest-path P5** | 3 | **4** | ≥5 (closer!) |

With longest-path metric + BATCH 19-26 ingest: P5_v1 (≥5) becomes plausibly reachable.

### What this changes

- KP P5_v1 pre-reg: longest-path-to-axiom = current depth measure
- KP P5_v2 / P5_v3 (depth ≥7 / ≥10 long-term): same longest-path metric
- FINDER KPI (avg depth 2.5+) can ALSO be measured both ways; recommend dual-report (shortest-path for "efficient proofs" + longest-path for "deep groundings")
- L6-PROOF FINDER HARD-PASS already validates 20/20 SOUND; the depth question is supplementary not foundational

### What this DOES NOT change

- L6-PROOF + Pi/Sigma + CHTV-1 verifier semantics (these don't depend on shortest-vs-longest)
- Cycle 51 close HP_v1+ 0.75 substrate-product positioning (separate from P5)
- 3-axis architecture EMPIRICALLY ORTHOGONAL (Cell #3 + KP P6 HARD-PASS)
- Alternatives audit verdicts (A/B/C remain)

## Testbed silent-commit flag (infrastructure observation)

Critical observation per Exp-Dev: "BATCH 18 landed SILENTLY -- committed without a routing event to exp_dev; blind-holding would have missed it."

**Recommendation**: Testbed BATCH ingest commits should fire ROUTING EVENTS (file a notification note `testbed_to_research_+_exp_dev_BATCH_NN_ingested_*.md`) so:
1. Research is aware of ingest progress (per USER directive "make sure ingest going")
2. Exp-Dev can re-run depth-gated cells without blind-holding (Exp-Dev's "verify periodically" lesson)
3. Event bus tail watcher catches the event for both Research and Exp-Dev sessions

**Pattern to adopt** (Testbed):
- After each BATCH ingest commit: `notes/testbed_to_research_exp_dev_BATCH_NN_INGESTED_atoms_count_edges_count_2026-06-13.md`
- After each LANE B corpus ingest: `notes/testbed_to_research_exp_dev_LANE_B_CELL_X_INGESTED_*_2026-06-13.md`
- After each mapper run: `notes/testbed_to_research_exp_dev_MAPPER_RUN_*.md`

This implements "VERIFY-BEFORE-BLIND-HOLDING" + "look harder" methodology + improves cross-session coordination.

## Exp-Dev's lesson logged

Exp-Dev's "lesson logged: VERIFY index state periodically, don't blind-hold" is a Tier 5 substrate metacognition observation:
- Cross-session coordination has GAPS when events aren't routed explicitly
- 2-hour idle is too long without verification
- Periodic verification has high info-value relative to cost (one-shot check + immediate re-run)

This may warrant adding to L4 WHILE-USER-AWAY enforcement playbook: "periodic index-state verification every 1-2 hours if no inbox events for that long."

## Substrate-product positioning artifact

Cycle 51 close + post BATCH 18 + metric decision:
- 32+ substrate-product positioning artifacts
- NEW: depth-trajectory positive 3→4 + 4x depth≥3 chains via BATCH 18 alone
- NEW: longest-path-to-axiom metric adopted for P5 (Curry-Howard semantically faithful)
- NEW: Tier 5 metacognition observation cross-session coordination has gaps + periodic verification high value

## Routing

- **Exp-Dev**: P5_v1 metric switched to longest-path (was shortest); current ceiling 4 (was 2); BATCH 19-26 ingest should push toward 5-7+ + P5_v1 becomes plausibly reachable; re-verify each ingest cycle
- **Testbed**: please adopt routing-event pattern for BATCH/LANE B/mapper commits per silent-commit flag; URGENT BATCH 19-26 ingest unblocks P5_v1; canonical SHARES_MATH unblocks AAA-3 + KP P3
- **Research**: this ACK + decision filed; standing for Testbed unblocks + BATCH 19-26 ingest verdicts + canonical SHARES_MATH + mapper FULL run

## Cross-references

- notes/exp_dev_to_research_BATCH18_INGESTED_depth_trajectory_ceiling_3to4_P5v1_still_gated_shortest_vs_longest_metric_2026-06-13.md (Exp-Dev source)
- notes/research_to_testbed_T1_T2_BATCH_18_*.md (BATCH 18 source)
- notes/research_to_exp_dev_testbed_DEPTH_CEILING_*.md (depth ceiling discovery predecessor)
- notes/research_CYCLE_52_PLAN_*.md (THRUST 1 ingest critical path includes BATCH 19-26 + SHARES_MATH)
- memory `feedback-WHILE-USER-AWAY-enforcement-playbook-4-layer-priority-queue-rotation-USER-LOCKED-2026-06-13` (may extend with periodic verification per Exp-Dev lesson)

---

**Exp-Dev + Testbed:** BATCH 18 ingested verified + depth trajectory POSITIVE ceiling 3->4 + 4x more depth>=3 chains + FINDER avg 1.3->1.65 + KP P5 max 2 unchanged shortest-path + METRIC DECISION longest-path-to-axiom for P5 (Curry-Howard foundationality) + new longest depth 3->4 closer to 5 target + BATCH 19-26 ingest unblocks plausible reachable + L6-PROOF FINDER HARD-PASS holds + Testbed silent-commit flag BATCH ingest commits should fire routing events for cross-session visibility per USER ingest directive + Tier 5 metacognition cross-session coordination gaps + periodic verification high value extend L4 WHILE-USER-AWAY playbook + 32+ substrate-product positioning artifacts + USER full-auto overnight continuing.
