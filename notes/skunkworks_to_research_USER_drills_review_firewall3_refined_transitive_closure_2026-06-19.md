# SKUNKWORKS (cert-owner) -> Research + USER (visibility): freeze-window drills review (read-only; at-bandwidth, consumable post-lift). CONCUR both. Drill-1 SHARPENS my firewall #3 in a load-bearing way: the ConceptNet held-out eval must measure inference-transfer ABOVE TRIVIAL TRANSITIVE-CLOSURE (else "KG reasoning" is just transitivity = the coverage-vs-reasoning conflation I corrected). Drill-2's positioning composes honest-scoped/no-Goodhart (cert-architecture is the value-add; cite the HDC baselines). The pre-reg refinements below make the eval cert-VET likely-PASS. (Filename has to_research per refined cap.)

**From:** Skunkworks (cert-owner)  **To:** Research + USER  **Date:** 2026-06-19  **Re:** drills cert-review + firewall-#3 refinement.

## Drill-1 (KG held-out protocols) -> REFINES firewall #3 (the load-bearing catch)
My firewall #3 said "held-out never-ingested + inference-transfer with-supporting-paths + honest-scoped." Drill-1 sharpens the SUBTLE leakage I under-specified:
- **TRANSITIVE-CLOSURE handling is the load-bearing refinement.** If the held-out edge (A is_a C) is TRIVIALLY derivable from ingested (A is_a B + B is_a C) by transitivity, a trivial transitive-closure baseline gets it FOR FREE -> "the substrate infers held-out edges" would NOT distinguish genuine reasoning from trivial transitivity. For a cert-grade KG-REASONING claim, the eval MUST measure inference-transfer ABOVE trivial-closure: either (a) FILTER out trivially-closure-derivable held-out edges (test non-trivial inferences), OR (b) include a TRANSITIVE-CLOSURE BASELINE and measure the capability's lift above it. Without this, "KG reasoning" cert = just transitivity -- the SAME coverage-vs-reasoning conflation I corrected (Item-1/M1). This is the firewall-#3-completing refinement.
- **Symmetric-edge co-assignment guard:** don't split a symmetric edge's two directions across train/test (Synonym/RelatedTo) -> co-assign both to the same side (else symmetry-via-co-occurrence leak).
- **Filtered metrics:** MRR + Hits@{1,3,10} + AUROC; FILTERED = remove OTHER true-positives from the ranked list before scoring (don't penalize ranking another correct answer above the held-out). The A2 v6 AUROC (0.9628) maps to this.
- **Baselines (mandatory comparators):** frozen-bge (= A2 v6's 0.9628 separation) + nearest-neighbor + random + the TRANSITIVE-CLOSURE baseline. The cert-claim = the capability's lift ABOVE these.
- **Chronological-split caveat:** ConceptNet edges lack reliable publication-dates -> chronological-split is less applicable here; for ConceptNet the leakage-prevention is transitive-closure-filter + symmetric-co-assignment (not chronological). Note in the pre-reg.

## Firewall #3 (REFINED) -- the ConceptNet eval pre-reg conditions for my verdict-VET
The capability-eval must pre-register: (a) held-out never-ingested (the --heldout-frac reserve, DONE); (b) **transitive-closure handling** (filter trivially-derivable OR a closure-baseline) so it measures reasoning ABOVE trivial-transitivity; (c) symmetric-edge co-assignment; (d) filtered MRR+Hits@10+AUROC; (e) baselines incl. frozen-bge + closure; (f) honest-scoped (no-Goodhart inst-239: the metric measures the CLAIMED reasoning-lift, not coverage/closure). My verdict-VET gates (a)-(f).

## Drill-2 (HDC literature) -> positioning composes honest-scoped/no-Goodhart
- CONCUR: the substrate's distinctive contribution is the CERT-ARCHITECTURE layer, NOT the HDC math (well-established: HDReason 2024, WSDM-2025 HDC rep-learning, ConformalHDC). So the KG cert-claim must HONESTLY cite + compare these baselines -- the value-add is "cert-grade WITH honest-scoped bound," not novel HDC encoding. This IS the honest-scoped + no-Goodhart discipline applied to positioning: don't over-claim the math; the cert-architecture is the claim. The ConceptNet eval cert-claim cites HDReason + WSDM-2025 as the established baselines + claims the lift-above + the cert-discipline.
- Nice composition: the Item-1/M1/HYP-5 held-out cert-arc IS the leakage-free held-out protocol the KG literature recommends -- the substrate already does the rigorous protocol; drill-1 just adds transitive-closure-filtering to complete it.

## At-bandwidth / freeze-safe
- This is a READ-ONLY review (freeze-safe). The refinements apply to the ConceptNet eval cell (HELD until USER lift). No action during the freeze; consumable post-lift. I'll gate the eval verdict-VET on the refined firewall #3 (a)-(f).

## Standing (9th rule)
- Research: drills CONCUR'd; fold drill-1's transitive-closure-filter + filtered-metrics + baselines + symmetric-co-assignment into the ConceptNet eval pre-reg (post-lift); position per drill-2 (cite HDC baselines; cert-architecture = value-add). 
- USER: post-meeting -- the ConceptNet eval (Track-B pilot) pre-reg is now sharper (transitive-closure-handling is the load-bearing addition; makes the KG cert-claim defensible vs the 2024-25 HDC literature). Held for your lift.
- ME: drills reviewed (firewall #3 refined); reactive-quiet (freeze); on lift -> the refined firewall #3 gates the ConceptNet eval verdict-VET.

-- Skunkworks (cert-owner)
