# Next Arc: DENSITY + GENERATE-AND-TEST (unified design) — 2026-07-10 (Director)

**The reframe (evidence-backed, off-disk verified):** the whole "make relational real" arc's negatives have a SINGLE mechanism-free root cause we never controlled for -- GRAPH DENSITY. KG relational inference works at avg degree ~37 (FB15k-237) and fails at ~4 (WN18RR). **Our tested graphs, off-disk: ConceptNet 2.68, science 2.91, bio-trio arms ~3.3 -- ALL ~10-14x below the inference floor, sparser even than the benchmark where inference is KNOWN to fail.** So every relational-inference negative this arc (codes/encoder/richness/grounding/loop-closer) was measured on a graph where held-out edges are NOT LATENTLY INFERABLE BY ANY METHOD. We were testing inference where the information wasn't there.

**Both drills converge (USER "both" vindicated -- A and B are COMPLEMENTARY necessary conditions, not a fork):**
- CANDIDATE A (density/knowledge): a quantified DENSITY FLOOR must be cleared or no method can infer (mechanism-free ceiling). But knowledge-ALONE never suffices (brain lit unanimous: schema/chunking/structure-mapping/Cyc all require a mechanism). P: 0.45 density-is-a-bottleneck / 0.25 density-alone-sufficient. [notes/research_knowledge_density_information_ceiling_relational_inference_2026-07-10.md]
- CANDIDATE B (mechanism): the missing piece = a DISCRETE GENERATE-AND-TEST loop (propose a candidate relation by COMPOSING known ones, then VERIFY with a hard/cheap exogenous support-confidence check). Hippocampal memory-integration + KG rule-induction (AMIE/RNNLogic/RulE/IterE) independently converge on it. The VERIFIER is the load-bearing piece every passive/smoothing method lacked. Needs dense knowledge (A) as fuel. P_deflated 0.35. [notes/research_generate_and_test_relational_inference_candidate_b_2026-07-10.md]

**UNIFIED THESIS:** relational inference needs BOTH (1) a graph above the density floor (so held-out edges are latently determined) AND (2) a generate-and-test mechanism with an exogenous verifier (to exploit the latent structure). We had NEITHER. This decomposes the wall cleanly.

## The build (density-CONTROLLED generate-and-test -- the fair test of both at once)

MECHANISM (B): a rule-induction / generate-and-test loop on our EXISTING CG primitives -- PROPOSE candidate edges by composing known relations via the chain-grade bind/unbind operator (e.g. AMIE-style: r1(A,B) and r2(B,C) frequent -> propose r3(A,C)); VERIFY each candidate with a hard support-confidence check against the graph (exogenous verifier); accept above threshold; measure held-out edge inference.

DENSITY CONTROL (A) -- the decisive contrast: run the SAME mechanism on graphs at MULTIPLE densities spanning the floor:
- SPARSE arm: our ConceptNet subgraph (deg ~2.7) -- mechanism should FAIL (below floor, nothing to infer).
- DENSE arm: a standard dense KG (FB15k-237, deg ~37, inference known-possible) OR a dense subgraph -- mechanism should WORK if it's real.
- (ladder of intermediate densities to locate the crossover.)

DECISION (pre-register): HARD_PASS = generate-and-test infers held-out edges materially above a degree/popularity baseline ON THE DENSE arm, degree-invariantly, AND fails/degrades on the SPARSE arm (proving the density floor is real and the mechanism exploits density). HARD_FAIL = mechanism fails even on the dense arm (generate-and-test is not the lever) OR works on sparse (density wasn't the wall).

MUST-FAIL CONTROLS (the fairness lens): (1) BROKEN VERIFIER -- a generator with a random/shuffled verifier must NOT infer (proves the verifier is load-bearing, not the generator alone); (2) degree/popularity baseline (must beat it -- not popularity); (3) MEMORIZATION control -- held-out edges must be genuinely held out (no leakage/inverse-relation duplication, the WN18 leakage trap); (4) info-ceiling: compute whether held-out edges are latently determined at each density (the achieved/ceiling discipline).

## Why this is different from everything we ruled out
Every prior lever was a PASSIVE representation change (code/encoder/richness/grounding) tested on a SINGLE sparse graph. This is (a) a DIFFERENT MECHANISM CLASS (discrete generate-and-test with a verifier, not a smooth read-off) tested (b) with DENSITY as a controlled variable (never varied cleanly before -- density-payoff was a k-core SUBSET confound). It directly tests the two necessary conditions the drills identified.

## Sequencing / honesty
- HOLD until the loop-closer FULL+VET confirm the grounding-doesnt-chain negative (don't stack a new arc on an unconfirmed prior).
- CHEAP FIRST STEP already done (off-disk density check -> all our graphs are sub-floor). Next cheap step: confirm a dense benchmark (FB15k-237) is acquirable as a controlled testbed (public, standard) -- ingest as testbed data, NOT canonical store.
- Deflated P (mechanism works on dense graph) ~0.35-0.45. Honest: this could still HARD_FAIL (maybe our CG compose + cheap verifier isn't enough even dense) -- but it is the first evidence-motivated, density-controlled, mechanism-class-novel bet, and a clean negative would itself be decisive (density isn't the wall / generate-and-test isn't the mechanism).
- Deepest connection: the exogenous verifier IS the active/verifiable-grounding target (predict-check-be-wrong). This arc operationalizes it.
