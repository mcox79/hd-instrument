# Research -> Exp-Dev: concept drift alerting + query redundancy methodology (cheap pre-tests; not drills)

**From:** Research session
**To:** Exp-Dev
**Date:** 2026-06-07
**Re:** Self-improving routing drill flagged 2 items as "actionable as cheap pre-tests; not
drill candidates." Routing directly.

## Pre-test A: Concept drift alerting (Misra-Gries time-window comparison)

Per self-improving routing drill option (k); 8/10 creativity; immediately actionable.

Method:
- Substrate's Misra-Gries counters (from sleep defrag) record top-K binding frequencies
  per time window
- Compare counters across windows (e.g., week-over-week)
- Sharp shifts in counter distribution = concept drift in customer KB
- Surface as customer-facing alert: "Your KB has shifted significantly in topic
  distribution; consider reviewing"

HARD-PASS: synthetic test with planted drift (e.g., 30% topic shift) is detected with
>= 90% recall, <= 10% false positive rate.

Wall: 30 min - 1 hr CPU.

This becomes a customer-visible capability ("substrate alerts you when your KB drifts")
that frontier LLMs cannot offer (their parametric memory has no concept-drift detection).

## Pre-test B: Query redundancy measurement methodology

Per self-improving routing drill CRITICAL RISK: if query redundancy < 15%, self-improving
architecture is equivalent to standard LLM-fallback. Must measure on customer onboarding.

Method:
- For first 100 queries from a customer (or synthetic stream), compute query-to-query
  similarity matrix
- Define "redundant" as similarity > threshold (e.g., 0.7)
- Compute redundancy rate
- Report distribution

This is the gating measurement for the self-improving customer pitch — if a customer's
queries are highly diverse, we should NOT promise self-improving benefits to them.

HARD-PASS: methodology produces reliable redundancy estimates on synthetic streams with
known redundancy ground truth.

Wall: 30 min - 1 hr CPU.

## Customer onboarding decision tree

After Pre-test B methodology validated, customer onboarding includes:
- Measure first 100 queries' redundancy
- If >= 30%: full self-improving routing benefits; pitch accordingly
- If 15-30%: moderate benefits; pitch with caveats
- If < 15%: self-improving doesn't help materially; pitch standard substrate + LLM

This is HONEST customer-facing methodology; aligns with drill's "must be measured, not
assumed" warning.

## Cross-references

- Self-improving routing 3x drill: notes/research_drill_self_improving_substrate_routing_3x_2026-06-07.md
- Sleep defrag scaling 2x: notes/research_drill_sleep_defrag_scaling_adversarial_2x_2026-06-07.md

---

**END.**

**Exp-Dev:** authorize both pre-tests (30 min - 1 hr each CPU). Apply HARD-PASS
autonomously. File results.
