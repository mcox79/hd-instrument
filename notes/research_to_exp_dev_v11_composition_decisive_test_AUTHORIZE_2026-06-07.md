# Research -> Exp-Dev: v1.1 composition decisive test + v1 demo CURATED QUERY mitigation

**From:** Research  **Date:** 2026-06-07  **Re:** v1.1 composition risks 2x drill output.

CRITICAL FINDING: composed pipeline at current individual values gives P(silent
failure) = 0.53 on random multi-hop queries. v1 demo design needs URGENT update.

## DECISIVE TEST: 100-query HotpotQA composition with per-component telemetry

~2 hours wall time. Gates the v1.1 integration question empirically.

Method:
- Build minimal composed pipeline: pre-trained Wikipedia substrate (CELL-2 v3) +
  DistilBERT-NER cascade + Pattern B Mech1 L2 norm + sleep defrag streaming +
  Qwen-1.5B base (Tier 4 LoRA pending; use base for now)
- Run 100 HotpotQA bridge questions
- Measure: end-to-end accuracy + per-component latency + per-component error
  contribution (ablate one at a time)

HARD-PASS: end-to-end accuracy >= 0.55 (composed pipeline holds individual benefits;
ready for engineering refinement).
BORDER: 0.45-0.55 (composition cascades partially; need component tuning before
v1 demo).
HARD-FAIL: < 0.45 (composition cascades materially; need integration redesign).

Wall: 2 hours; CPU + minimal GPU. NO TRAINING required.

## v1 DEMO DESIGN UPDATE: CURATED QUERIES

Per drill's mitigation. v1 demo MUST NOT use open user-typed queries on random
multi-hop. Composition silent-failure rate (0.53) means 4-6 wrong answers per 10
random multi-hop queries — unacceptable for customer-facing demo.

**Updated demo design:**
- 20 curated queries per vertical (medical / legal / financial)
- Each query individually validated: all components return correct on that query
- Demo shows: "Here's what substrate does on these representative queries; here's the
  per-component telemetry; here's where the limits are"
- Honest framing: "These queries showcase the capability; telemetry reveals failure
  modes we're addressing"
- Customer can submit their own queries via "Submit a query for evaluation" form
  (results delivered next session, not live; allows curated subset of customer queries
  to validate before showing)

Compromise:
- Live demo: curated queries (showcase capability)
- Customer-submitted: batched offline (validate then show)
- Transparency: per-component telemetry visible on every query
- Audit: every demo query's reasoning chain auditable

## Component-tuning agenda (post-decisive-test)

If decisive test BORDER/HF, the 4 dominant failure modes need targeted patches:

1. **Bridge entity encoding:** use SPECIALIZED entity encoder (different from bge-small
   sentence encoder) for NER bridge candidates; or use SapBERT (biomedical entity
   encoder) as universal entity layer
2. **Latency budget:** parallel component execution; component caching;
   pre-compute pre-trained base retrievals
3. **Misra-Gries threshold calibration:** per-customer threshold tuning; or two-tier
   thresholds (different for pre-trained vs customer layers)
4. **L2 norm + bridge matching:** apply L2 norm AFTER bridge entity verification;
   don't normalize on under-sampled bridge regions

## Qwen-7B promotion now has additional motivation

Drill flagged: at Qwen-7B, sleep defrag + NER noise-addition risk DROPS (stronger
context selection). Per Qwen-7B promotion drill + this drill combined, 7B is more
robust to composition cascades. Recommend: Experiment 1 (Qwen-7B benchmark battery)
ALSO measures composition accuracy at 7B vs 1.5B for direct comparison.

## Strategic implication for v1 demo timeline

- v1 demo design needs CURATED-QUERY architecture (not open-input random)
- Decisive 2-hour composition test BEFORE finalizing demo query set
- Component-tuning iteration may add 1-2 weeks to v1 demo build (3-4 → 4-6 weeks)
- Honest customer pitch: "Each component HP individually; composition demo on curated
  queries shows what's working; engineering iteration ongoing"

## Cross-references

- v1.1 composition risks 2x: notes/research_drill_v11_composition_risks_2x_2026-06-07.md
- Drill handoff: notes/exp_dev_handoff_research_v11_composition_risks_2026-06-07.md
- v1 demo design: notes/research_to_exp_dev_v1_demo_design_routing_2026-06-07.md
- Qwen-7B promotion drill: notes/research_drill_qwen7b_promotion_risks_2x_2026-06-07.md

---

**Exp-Dev:** authorize 100-query composition test (2 hours; CPU + minimal GPU). File
results with per-component telemetry breakdown. If HARD-PASS, v1.1 composition is on
track. If BORDER/HF, route the 4 component-tuning patches.

**Engineering:** v1 demo design update to curated-query architecture. Honest customer
framing required. Engineering scope estimate updated to 4-6 weeks (was 3-4).
