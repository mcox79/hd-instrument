# Strategy -> Research: burn-down of 3 orphaned 2026-05-23 Research deliveries (D1/D2/D3 per audit)

**Date**: 2026-05-23 ~12:28 EDT
**From**: Strategy session (cycle 178 / v158)
**To**: Research session (status acknowledgement + concrete next steps)
**Trigger**: Audit Rec 3 per `notes/audit_dropped_and_review_2026-05-23.md`. Three Research deliveries filed on 2026-05-23 morning went directly to disk without an integration cycle in cap_map or strategy_decisions. Strategy v158 acknowledges the orphan and files concrete next-step actions for each.

---

## Context

Per audit:

> Three Research deliveries on 2026-05-23 morning (`research_strategy_open_questions_2026-05-23.md` 09:41, `research_semiconductor_physics_substrate_analogies_2026-05-23.md` 07:08, `research_order_param_2x_drill_2026-05-23.md` 09:40) appear in no cap_map narrative and no `strategy_decisions_2026-05-23.md` entry. These are 6/22 today's Research deliveries (the count Strategy v156 cycle 176 cited as "saturation"). Strategy treated them as inbox-overflow rather than integrating them. Three deliveries went directly to disk and never got an integration cycle.

This burn-down note is the structural acknowledgement + integration pointer per [[feedback-design-space-and-audit-cadence]] (burn down inventory before adding more Research work).

Per [[feedback-no-smoke]] brutal honesty: this is a Strategy discipline gap. The orphans accumulated because v156 / v157 / v158 cycle pressure prioritized verdict-integration over Research-delivery-integration. The right move is to acknowledge each orphan explicitly with a concrete next-step + a Strategy commitment to either (a) integrate findings into a future cap_map narrative or (b) close the route as superseded.

---

## D1 -- `notes/research_strategy_open_questions_2026-05-23.md` (09:41)

**Trigger origin**: `strategy_request_to_research_strategy_open_questions_2026-05-23.md` filed 09:34. User directive: "and ask research your questions". Three open substrate-physics questions at v149: (Q1) ~25% partial idempotence fraction mechanism; (Q2) 15-peak P(q) -> 28-endpoint hierarchy; (Q3) broad K-band + near-degenerate eigenspectrum at K=1000.

**Delivery snapshot**: Top candidate for Q1: Kerdock 4-coset codebook geometry -- RM(1,16) is exactly 1 of 4 cosets = 25% by construction (P=0.40 per Agent FF). Strategy notes v152 already REFUTED this -- substrate AVOIDS RM(1,16) (frac=0.000). So D1's Q1 top candidate is empirically falsified; remaining D1 candidates for Q1 + Q2 + Q3 are unintegrated.

**Concrete next step (Strategy v158)**:

- D1 Q1 (~25% mechanism): the Kerdock 4-coset explanation is REFUTED at v152. Remaining mechanism candidates in D1 (entropic + energetic separation between linear and nonlinear cosets per audit Rank-5 cheap-CPU experiment) deserve a 30-min CPU re-analysis pass; route to Exp Dev as Pick 4 in the next-pipeline routing (alongside the v158 Online W noise envelope sweep). One cycle.
- D1 Q2 (15-peak P(q) cardinality): integrate into next P(q)-related Research drill when one fires (currently no scheduled work; defer until v158-plus pipeline output suggests one).
- D1 Q3 (broad K-band + near-degenerate eigenspectrum at K=1000): cross-reference with audit Rank-2 cheap-CPU "P(q) sub-K-region analyzer pass on existing data" -- both touch K-binning at K-resonance boundaries. Route the Rank-2 analyzer pass to Exp Dev as bandwidth-permitting CPU re-analysis; informs Q3 mechanism.

**Decision**: NOT a kill / NOT a fresh Research drill. Folded into the v158 next-pipeline routing as 1-cycle CPU re-analysis tasks (low-leverage but cheap).

---

## D2 -- `notes/research_order_param_2x_drill_2026-05-23.md` (09:40)

**Trigger origin**: `strategy_request_to_research_order_param_2x_drill_2026-05-23.md` filed 09:33. Per [[feedback-2x-means-depth]]: level-2 operational drill on the cycle 170 ORDER_PARAM_SUB_REGION_STABLE finding (multi-component sub-K-region q_overlap).

**Delivery snapshot**: Drill output. Strategy v151-v152 integrated the multi-component sub-region OP finding via a different route (Sagawa-Ueda inspiration for Cap 1 metric-definition came from a different reading). D2's specific deep findings (per [[feedback-2x-means-depth]] this is operational depth on the existing finding) never got named in cap_map.

**Concrete next step (Strategy v158)**:

- Strategy commits to an integration pass at the NEXT cap_map cycle that touches the order-parameter row (v150's ORDER_PARAM_SUB_REGION_STABLE; v152's 15-peak P(q); or a future P(q)-related FULL verdict). D2 will be cited at that cycle.
- If no such cycle fires within 5 cap_map versions (v158 -> v163), Strategy will file a dedicated v163 acknowledgement entry summarizing what D2 added that the cap_map narrative did not absorb.

**Decision**: Hold for next OP-related cap_map cycle. Track for v163 deadline.

---

## D3 -- `notes/research_semiconductor_physics_substrate_analogies_2026-05-23.md` (07:08)

**Trigger origin**: no explicit Strategy request; inbound delivery from Research session (likely on cross-framework drill cadence per [[feedback-periodic-scope-expansion]]).

**Delivery snapshot**: cross-framework drill (semiconductor physics framings for substrate analogies). Per [[feedback-periodic-scope-expansion]] this is exactly the proactive scope-expansion work Research should do. Strategy v144 / v145 did absorb the "K-resonance K=1000 fixed-point" finding from a related fresh-angles-quirky-matsci delivery; D3 is a separate semiconductor-physics-specific drill that landed earlier (07:08) and was orphaned.

**Concrete next step (Strategy v158)**:

- This is the LOWEST-priority orphan to integrate because cross-framework drills feed substrate-physics characterization, not substrate-product verdicts. Strategy commits to a single one-cycle read pass at the next idle-research-cycle to extract any falsifiable predictions from D3 that haven't been tested. If D3 contains specific testable predictions, Strategy files a follow-up Exp Dev routing; if D3 is purely exploratory framing, Strategy notes it as background-context-only.
- This is a "read-and-decide" task; not blocking anything else.

**Decision**: Park as low-priority read-and-decide. No fresh Research work generated.

---

## Strategy commitment going forward

Per [[feedback-design-space-and-audit-cadence]]:

1. Going forward, Strategy will explicitly acknowledge inbound Research deliveries in the SAME strategy_decisions cycle (within 2 hours of delivery) -- either integrated into cap_map narrative or routed to a follow-up. No delivery should sit unintegrated for >5 cap_map versions.
2. Audit cadence: the audit doc that surfaced these 3 orphans (`notes/audit_dropped_and_review_2026-05-23.md`) is the standing audit surface. Strategy will consult the audit doc at each cap_map cycle to check for fresh orphans.

Per [[feedback-no-smoke]] brutal honesty: the orphan pattern reflects Strategy's verdict-driven processing cadence not absorbing inbound Research as fast as it lands. The structural fix is the audit cadence + explicit acknowledgement (this burn-down note + future ones if needed). The audit cadence catches it; the burn-down note acts on it.

---

## Net result of this burn-down note

- D1: folded into v158 Exp Dev next-pipeline routing as 1-cycle CPU re-analysis tasks (Rank-5 anti-linear-coset + Rank-2 P(q) sub-K-region).
- D2: held for next OP-related cap_map cycle; v163 deadline.
- D3: parked as low-priority read-and-decide.

Inventory burned. Three orphans acknowledged and routed (or held with deadlines). No new Research work generated until D1/D2/D3 are absorbed or v163 deadline hits.
