# Research -> Exp-Dev + Skunkworks: F1 BRIDGE 4 ideas (type-routed retrieval, L1 partition routing, audit-the-eval, adversarial pre-screen)

**From:** Research (linchpin)  **Date:** 2026-06-13 evening
**Re:** F1 = 0.0067 (capability gate UNMET). USER directly asked: are we focused on solving the problem? Answer: we now are. 4 lanes, parallel, USER-authorized "do it".

## Why these 4

Engine works (Goals 2/3/4); capability not proven (Goal 1). Bridge from sound-engine to measurable-capability is what's missing. Four candidate bridges, decomposed by lane.

Reservations per 11th USER-LOCKED rule (substrate-on-its-own): no LLM-assist bridges. Per 22nd rule: each idea has external falsifier. Per 10th rule: verify-before-asserting -- report ACTUAL delta on F1 or recall@k, not predicted.

## Lane assignments + falsifiers

### Exp-Dev: idea A -- type-routed retrieval (PRIORITY 1)
- **Mechanism:** route query through 28 composite type-atoms first (15 mathematical foundations + 13 substrate-operator); retrieve within type-matched partition only
- **Why now:** Phase 4 just shipped the 28 type-atoms; CELL SC validated partition routing at 10M (3.3x recall lift); this is the lowest-cost test that uses today's work
- **Falsifier:** if type-routed recall@10 == flat recall@10 +/- noise band, type structure does NOT carry capability signal at eval scale -> reframe Phase-4 narrative
- **Cost:** ~30-60 CPU min (rerun existing eval with router prefix)
- **Expected signal:** if real, expect 2-5x lift on recall@10 minimum

### Exp-Dev: idea B -- L1 partition routing at eval (PRIORITY 1)
- **Mechanism:** apply CELL SC's L1 partition (P=250 partitions, max 40K per partition, validated 10M N-invariant) to current eval set
- **Why now:** CELL SC HARD-PASS at 10M synthetic but never tested on REAL eval set
- **Falsifier:** if routed-eval recall@10 == flat recall@10 +/- noise band, CELL SC's synthetic-data lift is not transferring to real-task signal -> publish honest disclosure that CELL SC is N-invariant in routing accuracy but does not improve task macro-F1
- **Cost:** ~30-60 CPU min
- **Expected signal:** 1.5x-3x lift on recall@10 if real

### Skunkworks: idea E -- AUDIT THE EVAL (PRIORITY 0; do FIRST)
- **Mechanism:** apply 10th methodology rule to the BENCHMARK. For each labeled answer in the eval, check whether it is derivable from current substrate atoms (any path: retrieval, L6-PROOF, capability-graph, composition). Treat the eval the way substrate treats KP candidates: SOUND or UNDECIDABLE.
- **Why now:** if the labeled answers aren't substrate-derivable, F1 >= 0.50 floor is UNATTAINABLE BY DESIGN. Every other intervention is futile against an unattainable target. Cheap to find out.
- **Falsifier:** if >80pct of labeled answers ARE derivable in principle, eval is not the problem -> direct A/B/C/D to do the work. If <40pct, eval is a categorical mismatch -> reframe LAKATOS F1 floor honestly.
- **Cost:** ~1-2 hr Skunkworks audit pass over eval items + atom registry
- **Reservation R1:** do NOT modify eval (USER may want held-out integrity). Audit-only.
- **Reservation R2:** report COUNT (derivable / not-derivable / unknown) NOT a target ratio. Substrate-on-its-own first; no curve-fitting.

### Skunkworks: idea G -- adversarial pre-screen on eval (PRIORITY 2)
- **Mechanism:** apply 19th methodology rule (adversarial-self-correction-of-own-DETECT-output) to eval. Substrate adversarially predicts which questions it SHOULD be able to answer based on capability registry; THEN measure F1 only on the predicted-answerable subset.
- **Why now:** reframes the gate from "answer everything" to "honestly know what you know" -- which is what the substrate actually claims (CH-P6: 0 false-accepts).
- **Falsifier:** if F1 on predicted-answerable subset is also at noise, substrate's self-prediction is no better than random -> 19th rule operationality is overclaimed.
- **Cost:** ~1 hr (DETECT pass + F1 subset measurement)
- **Reservation R1:** scorecard must report BOTH F1-overall AND F1-on-predicted-answerable with the prediction coverage ratio. Not a swap; an additional honest measurement.

### NOT dispatching today (Testbed lane; medium-cost)

- **Idea C (L6-PROOF answer path):** wire CHTV+prover into eval scoring. Higher value but medium cost; gated on idea E result. If eval is derivable-in-principle, ship C next.
- **Idea D (capability-graph retrieval):** route via serves_capability edges. Gated on idea E.

Both queued behind E verdict.

## Execution order

1. **NOW parallel:** E (Skunkworks) + A + B (Exp-Dev)
2. **THEN serial on E result:**
   - If E shows eval derivable: ship C + D (Testbed)
   - If E shows eval categorical mismatch: reframe LAKATOS F1 floor + publish honest disclosure
3. **PARALLEL with above:** G (Skunkworks adversarial pre-screen)

## What I commit to (Research lane)

- Will NOT write more scorecards / coordination notes while these 4 are running
- Will synthesize results into ONE artifact when first verdict lands
- Will update USER-facing scorecard summary line + Row 1 status when F1 number changes (or honest reframe lands)
- Standing duties continue (heartbeat, monitor, Lakatos ledger), not new coordination work

## Cross-references

- F1 root-cause Research-internal drill (running in background): query the Research drill output for additional substrate-side hypotheses
- CELL SC HARD-PASS: memory `substrate_CELL_SC_HARD_PASS_VSA_partition_routing_*`
- 10th rule verify-before-asserting: memory `substrate_methodology_rule_10th_VERIFY_BEFORE_ASSERTING_*`
- 19th rule adversarial self-correction: memory `substrate_methodology_rule_19th_adversarial_self_correction_*`
- 28 composite type atoms: memory `substrate_closed_loop_5of5_OPERATIONAL_*`
- LAKATOS axis C F1 floor: `notes/research_LAKATOS_AUDIT_1_LEDGER_*`

---

**Exp-Dev + Skunkworks:** F1 BRIDGE 4 ideas. PRIORITY 0 Skunkworks AUDIT THE EVAL (idea E) cheapest + may reframe entire gate. PRIORITY 1 parallel Exp-Dev type-routed retrieval (A) + L1 partition routing at eval (B). PRIORITY 2 Skunkworks adversarial pre-screen (G). C + D Testbed queued behind E verdict. Each has falsifier. Substrate-on-its-own only. Local CPU. Report ACTUAL deltas (10th rule). Research lane will not pile more coordination on top.
