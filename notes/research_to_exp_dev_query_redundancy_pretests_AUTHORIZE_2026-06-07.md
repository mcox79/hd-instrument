# Research -> Exp-Dev: query redundancy methodology 3 pre-tests AUTHORIZED

**From:** Research  **Date:** 2026-06-07  **Re:** Query redundancy methodology 2x drill.

Per blanket Exp-Dev authorization. Customer onboarding gating capability per drill.

## Drill key takeaways

- USE BOTH semantic similarity AND substrate-native (Jaccard on top-K retrieval
  candidates) measures; report as range = confidence interval proxy
- N=100 onboarding gives ±8-12 pp 95% CI — honest profiling requires flagging this
- Helpdesk typical: 30-50% redundancy attributable to top-20 intent clusters
- Equilibrium estimate vs cold-start estimate distinction matters for tier recommendation

## Authorize all 3 pre-tests from drill handoff

Per `exp_dev_handoff_research_query_redundancy_methodology_2026-06-07.md`.

### Pre-test 1 (PRIMARY): Methodology validation on synthetic stream with known redundancy
~30 min - 1 hr CPU. Generate synthetic query streams with KNOWN redundancy ground truth
(e.g., 10%, 20%, 30%, 50%); measure methodology's estimate vs ground truth.

HARD-PASS: methodology estimates ground truth within ±5 pp at N=500 queries.

### Pre-test 2: Real benchmark redundancy profiles
~1-2 hr CPU. Compute redundancy for HotpotQA + TriviaQA + NQ + PubMedQA query sets;
establish per-domain baseline.

HARD-PASS: per-domain profiles consistent with literature expectations (helpdesk
high; scientific low).

### Pre-test 3: Cold-start vs equilibrium estimation
~1-2 hr CPU. Estimate R_inf (equilibrium redundancy) from first 100 queries vs
ground truth measured at 5000 queries.

HARD-PASS: R_inf estimate from 100 queries within ±10 pp of measured equilibrium.

## Customer onboarding decision tree (per drill)

| Redundancy R | Customer Tier | Self-improving lift promised |
|---|---|---|
| >= 30% | Premium (full self-improving) | 2-4x latency improvement at equilibrium |
| 15-30% | Standard | Moderate latency improvement; partial benefits |
| < 15% | Basic | NO self-improving claims; moat features only |

This is HONEST customer-facing methodology; aligns with self-improving drill's "must
measure, not assume" warning.

## Cross-references

- Query redundancy 2x: notes/research_drill_query_redundancy_methodology_2x_2026-06-07.md
- Drill handoff: notes/exp_dev_handoff_research_query_redundancy_methodology_2026-06-07.md
- Self-improving routing 3x (motivating drill): notes/research_drill_self_improving_substrate_routing_3x_2026-06-07.md

---

**Exp-Dev:** authorize 3 pre-tests at convenience. Methodology becomes part of v1
customer onboarding workflow once validated.
