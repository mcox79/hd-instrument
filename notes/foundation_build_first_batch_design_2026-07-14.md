# Foundation build — first batch design (2026-07-14; greenlit by conjunction-mechanism HARD-PASS)

**Status:** design ready; DISPATCH gated on conjunction FULL confirming the mechanism at multi-seed scale (measure-as-you-go). Route to exp_dev on confirmation.

## Why this batch (the closed chain)
1. Prize = CONJUNCTIONS (single-relation refuted: homophily wins, v3 REFUTED).
2. Current CSKG has ~ZERO conjunction structure (76% lexical; semantic buckets +0% narrowing) -> must GENERATE.
3. Mechanism CONFIRMED: native-bind + CONSTRUCTABLE (FPE/known-group) codes BEAT frequency on conjunctions at real scale (MEMSMOKE HARD-PASS: CLEAN 1.0 vs FREQ_NULL 0.013; must-fails fire).
4. => Build the DATA. The mechanism is proven for CONSTRUCTABLE structure (weak-link-#2 SOLVED case); the foundation SUPPLIES constructable structure, so structure-DISCOVERY (open sub-problem) is OFF the critical path.

## What the first batch must prove (the de-risk)
The mechanism cell used PLANTED conjunctions. This batch tests whether **externally-GENERATED conjunction structure** (real-world knowledge, not planted) is (a) PRESENT/generable, (b) CONSTRUCTABLE-encodable, (c) beats frequency under native-bind. If yes -> the full foundation build is de-risked. If generated conjunctions DON'T beat frequency (e.g., real-world "conjunctions" are actually single-relation-determined / homophily-solvable), that REFUTES the generate-conjunctions premise and is the most valuable outcome.

## Design (compute-proportionate FIRST batch -- one concept cluster, not the whole foundation)
1. **Concept cluster:** ONE coherent domain where multi-attribute conjunction is NATURAL and vettable (exp_dev picks; candidates: organisms [taxon x habitat x morphology x diet -> ecological/physiological properties], or a physical-object domain [material x size x structure -> function/behavior]). Aim ~200-500 entities. Prefer a domain that also addresses a real coverage gap (science/biology 0.6%).
2. **Generate conjunction-bearing structure** via the VALIDATED external generation pipeline (the 93.75%-truth pilot method): for each entity, generate K>=3 interacting relations AND a held-out attribute whose value is CONJUNCTION-determined (depends on a COMBINATION, not any single relation). CRITICAL: verify the conjunction property empirically on the generated data -- single-relation mutual-info(held-out | one relation) LOW, joint mutual-info(held-out | conjunction) HIGH (the same measure as cskg_conjunction_by_bucket.py). If generated relations are single-relation-determined, the generation FAILED to create conjunctions -> report + fix the generation prompt.
3. **Vet the generated structure** (raw-then-VET, the pilot's method): adversarial-judge truth, schema-coherence, sense-disambiguation, cross-model agreement. Report truth rate; hold out a clean test slice (don't trivialize generalization).
4. **Encode with CONSTRUCTABLE codes:** FPE/fractional-power for ordinal/magnitude attributes; group-structured (known-group) codes for categorical relations matched to their structure. NO SGD-learned-from-scratch codes (weak-link-#2: 0.11). Use the substrate's real hdlab.binding.bind.
5. **Measure (same discriminator as the mechanism cell):** NATIVE_BIND composition vs FREQ_NULL = max(HOMOPHILY_cond, HOMOPHILY_jaccard, POP) on the NOVEL constraint-combination stratum. Must-fails: ARBITRARY-structure (bind must NOT beat frequency) + SHUFFLE (collapse). Info-ceiling = oracle knowing the generated rule.

## Pre-registered outcome
- HARD-PASS: on GENERATED conjunctions, NATIVE_BIND novel-combination acc >> FREQ_NULL (dissociation >= 0.30) with must-fails firing AND generation truth-rate >= ~0.85 -> the full foundation build is GO (scale to more clusters + domains, measure-as-you-go).
- REFUTE: generated "conjunctions" are single-relation/homophily-solvable (NATIVE_BIND ~= FREQ_NULL) OR generation truth too low -> the generate-conjunctions premise fails; rethink what structure to generate (or whether real-world knowledge is conjunction-poor).

## Guardrails
- Compute-proportionate: ONE cluster, mechanism-test scale (NOT a multi-hour generation of the whole foundation). Incremental measure-as-you-go = safety valve.
- Runtime stays glass-box (external tools ONLY for foundation-building/generation; NO external LLM at inference).
- Hold out a clean test slice up front (don't let generation trivialize the generalization prize).
- raw-then-VET the generated structure + the mechanism result independently.

## Coupling to the other half
Once the foundation supplies constructable conjunction structure, the CONSOLIDATION loop (P1, Claim B CONFIRMED) is the mechanism that would MAINTAIN/refine it (manufacture + consolidate structured codes). Foundation (this batch) + consolidation (P1) = the two brain halves, both now with positive evidence.
