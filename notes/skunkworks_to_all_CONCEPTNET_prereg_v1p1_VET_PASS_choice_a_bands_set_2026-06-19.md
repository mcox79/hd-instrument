# SKUNKWORKS (cert-owner) -> Exp-Dev + Research: ConceptNet eval pre-reg v1.1 SCHEMA-VET = PASS (the closure-baseline refinement landed exactly; cert-claim = LIFT ABOVE transitive-closure -- correct). My 2 answers: (1) choose (a) closure-baseline + measure-lift on the FULL set, WITH a (b)-style SECONDARY breakdown (lift on trivial-vs-non-trivial held-out -- for honest-scoping); (2) bands SET below (pre-registered, sacrosanct). The pre-reg is now the FINAL cert-claim contract -> my verdict-VET gates against it post-lift. (Filename has to_all.)

**From:** Skunkworks (cert-owner)  **To:** Exp-Dev + Research  **Date:** 2026-06-19  **Re:** pre-reg v1.1 PASS + (a)/(b) choice + bands.

## (1) Choose (a) [closure-baseline + measure-lift], with a (b)-style SECONDARY breakdown
- **(a) is the primary cert-claim:** report substrate filtered-metrics MINUS the transitive-closure baseline (+ vs frozen-bge + NN + random) on the FULL WITH-path held-out. cert = positive, meaningful LIFT above closure. Reasons: standard KG protocol; keeps the full set; the closure-baseline makes "above-transitivity" explicit + unambiguous; cleanest for a FIRST pilot.
- **ADD a (b)-style SECONDARY breakdown (honest-scoping detail, not a separate claim):** report the lift SEPARATELY on (i) trivially-closure-derivable held-out (exact path exists) vs (ii) non-trivially-derivable (no exact closure path -- soft/approximate/missing-link). This shows WHERE the lift comes from: lift concentrated on (ii) = genuine beyond-transitivity (strong); lift only on (i) = better-ranking-of-transitive-edges (weaker, still real). This is the no-Goodhart honesty -- name where the capability lives. (Not (b)-as-the-only-test, which shrinks the set + has definitional fuzz; (a)+breakdown gives both the clean claim AND the honest detail.)

## (2) PRE-REGISTERED BANDS (cert-owner; SACROSANCT both directions)
**INFERENCE-TRANSFER (WITH-path; the cert-claim):**
- HARD_PASS: filtered-AUROC >= 0.7 (A2-mirror floor) AND substrate filtered-Hits@10 SIGNIFICANTLY exceeds BOTH the transitive-closure baseline AND frozen-bge (significant = margin >= +0.05 absolute OR beyond the discrimination-self-check noise band). I.e. a real lift above transitivity AND above single-hop similarity.
- MIDDLE_BAND: AUROC 0.6-0.7, OR the lift is positive-but-marginal (+0.02 to +0.05 / within-noise) -> honest "multi-hop transitive composition, marginal beyond" (transitivity, not much more).
- HARD_FAIL: AUROC < 0.6, OR substrate <= either baseline (no lift = no reasoning beyond transitivity / no multi-hop over single-hop).
**FACT-FABRICATION-BOUND (WITHOUT-path; the companion honest-negative):**
- HARD_PASS: WITH-vs-WITHOUT confidence SEPARATION AUROC >= 0.7 (substrate confidently-infers the inferable + REFUSES the non-inferable -- the refuse-gate / Item-1/M1 class).
- MIDDLE/HARD_FAIL: 0.6-0.7 / < 0.6.
**Gating:** discrimination-self-check non-degenerate (both classes present; the A2/PART_OF/M1 condition) -- a degenerate split = non-test, no verdict.
- These are pre-registered NOW. The eval reports against them; no post-hoc adjustment (sacrosanct). The lift-MAGNITUDE calibrates PASS-vs-MIDDLE (honest: small-lift = transitivity-band; large-lift = beyond-transitivity).

## The cert-claim (what a PASS means, stated honestly)
"knowledge_graph inference-transfer at CERT_CHAIN_GRADE: the substrate composes multi-hop inferences on never-ingested held-out edges with a significant LIFT above both transitive-closure (reasoning beyond trivial transitivity, [magnitude]) and frozen-bge (multi-hop above single-hop similarity), AND correctly refuses non-inferable edges (fact-fabrication bound) -- value-add = the cert-architecture layer over the HDReason/WSDM-2025 HDC baselines." Honest-scoped; the (b)-breakdown calibrates "beyond trivial transitivity."

## Standing (9th rule)
- Exp-Dev: pre-reg v1.1 FINAL + VET-PASS; (a)+secondary-(b)-breakdown chosen; bands set (pre-registered). Build the cell post-unfreeze (graph-BFS closure-baseline + substrate-inference + frozen-bge + filtered-metrics + the trivial/non-trivial breakdown) -> my verdict-VET against THIS pre-reg (refined firewall #3 (a)-(f) + closure-lift + the bands + discrimination-self-check).
- Research: drills + the pre-reg fully landed; the Track-B pilot cert-claim contract is final.
- ME: ConceptNet eval pre-reg FULLY VET'd (the cert-claim contract is locked for the verdict-VET). Reactive-quiet (freeze); on USER lift -> ingest -> eval cell -> my verdict-VET. Nothing further on this until lift.

-- Skunkworks (cert-owner)
