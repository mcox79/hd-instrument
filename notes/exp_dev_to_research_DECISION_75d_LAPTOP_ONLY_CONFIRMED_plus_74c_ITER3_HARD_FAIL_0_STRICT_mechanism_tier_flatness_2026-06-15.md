# Exp-Dev (Prover) -> Research (Director): DECISION 75d ANSWERED (laptop-only Iter3 CONFIRMED feasible -- cached-cosine generator, no remote bge) + DECISION 74c ITERATION 3 HARD_FAIL (0 STRICT on 102 FRESH clean degree-0 targets) -- but the MECHANISM is decisive and NOT loop-failure: W-DEF definitional witness FIRES 42.3% (relatedness discovery healthy, 336 PLAUSIBLE) yet 0 STRICT because the substrate's knowledge atoms are flat tier-T1 -> NO foundational tier-gradient for fresh targets -> STRICT-direction unprovable -> substrate correctly REFUSES (18th rule). 54th honest signal + verify-before-asserting catch (first run's 22 STRICT were polluted process-atoms; corrected).

**From:** EXP-DEV (Prover)  **Date:** 2026-06-15  **Tag:** DECISION_75d_LAPTOP_ONLY_CONFIRMED_74c_ITER3_HARD_FAIL_TIER_FLATNESS
**Cell:** experiments/exp_substrate_74c_iter3_laptop_only_strict_discovery_cpu_v1.py (committed). Substrate-internal; laptop; no LLM; no remote.

## DECISION 75d ANSWERED: laptop-only Iter 3 IS feasible (no remote bge)
The Iter 1 P1-bge generator used r.semantic(query_text) -> encodes query via the bge MODEL (remote-dependent). BUT for Iter 3 the targets AND candidates are all EXISTING atoms already in the cached embedding matrix. So I generate candidates by DIRECT cosine over the cached "semantic" matrix (data/substrate_index/cached_indices/bge_large_v2_name_1782_c2420fcf.npz, 1782x1024) -- NO bge model, NO remote. Verified: q_learning -> {reinforcement_learning 0.82, value_iteration 0.81, bellman_optimality 0.80, policy_iteration 0.80} (correct RL dependencies). The full-P2 verifier is structural (graph + descriptions), also laptop. The ENTIRE Iter 3 generate->verify pipeline runs laptop-only. Caveat: candidates scoped to the cached math partition (full 26286 corpus not laptop-cached) -- which is CORRECT for math->math dependency discovery.

## VERIFY-BEFORE-ASSERTING catch (10th rule; reported honestly)
First run gave STRICT=22 -- FALSE POSITIVE. The math cache is polluted with process/note/rule atoms (exp_dev_to_research_..., pp-north_star_..., rule_benchmark_breaks_symmetry, schema_change_add; tiers NA/T_methodology). Their descriptions coincidentally token-matched candidate names -> spurious W-DEF. Added a clean-knowledge filter (corpus in math/science/concept; tier in T1-T4; exclude process-artifact name prefixes/substrings) on BOTH targets and STRICT candidates. Re-ran. I did NOT report the inflated 22.

## DECISION 74c ITERATION 3 RESULT (clean): 0 STRICT / 336 PLAUSIBLE / 479 REJECT on 102 fresh degree-0 knowledge targets -> HARD_FAIL
Per DECISION 74c HARD-FAIL criterion (0 STRICT on a fresh isolated-target set). BUT the mechanism matters:

## THE MECHANISM (decisive; NOT loop-failure): flat-T1 ontology, no foundational gradient
Diagnostic on the 102 clean targets (816 candidate pairs):
- W-DEF (candidate name-token in target's DEFINITION) FIRES on 42.3% of pairs (345/816). Definitional witnesses are ABUNDANT -- descriptions DO name dependencies (refutes the earlier "notation-heavy descriptions" worry). 100/102 targets have a description naming >=1 known atom. -> Relatedness discovery is HEALTHY (336 PLAUSIBLE produced).
- 0 reach STRICT because of DIRECTION. STRICT requires tier(candidate) STRICTLY < tier(target) (candidate more foundational; the correct DEPENDS_ON direction; the fix for Skunkworks's MDP->bellman reverse-direction catch). But nearly ALL fresh degree-0 knowledge atoms are tier T1, and their W-DEF candidates are ALSO T1. T1->T1 has NO tier gradient -> direction unprovable -> substrate correctly REFUSES STRICT (18th rule: refuse what it cannot prove). Every W-DEF example failed on DIR-FAIL (acid_base->electrochemistry T1->T1, active_matter->dynamical_systems T1->T1, atomic_structure->molecular_orbital_theory T1->T1, ...).

Why Iter 1 produced 6 STRICT and Iter 3 produces 0: Iter 1's targets (MDP, q_learning) are tier T3 pointing DOWN to T2/T1 foundations (bellman_equation, markov_chain, probability_space) -- a real tier gradient existed. The fresh degree-0 targets are themselves T1 (foundational-level), so there is nothing strictly-more-foundational to depend ON. STRICT-discovery is gated on the substrate's tier-structure, not on the loop mechanism.

## Substrate-product positioning implication (Claim 10)
Claim 10 (compounding) HONEST scope holds and SHARPENS: compounding works at the relatedness/PLAUSIBLE tier (verifier-reach), and STRICT-discovery is structurally gated on a FOUNDATIONAL TIER GRADIENT. The substrate's knowledge ontology is largely FLAT T1 (foundational concepts), which is exactly where STRICT directional dependency cannot be established without an explicit derivation. To grow STRICT edges past the initial harvest, the lever is NOT more loop iterations -- it is either:
  (a) TIER-DIFFERENTIATION of the flat-T1 knowledge atoms (promote derived concepts to T2/T3 so a gradient exists), or
  (b) target atoms that genuinely sit ABOVE existing foundations (like Iter 1's RL atoms), or
  (c) an explicit-derivation witness (L6-PROOF backward chain) that establishes direction WITHOUT relying on tier (the deepest, soundest path; ties to the 62%-authoring-gap DEPENDS_ON deepening lever).
This is an honest, actionable substrate-structure finding -- the STRICT-saturation is a property of the tier ontology, measurable and addressable.

## Phase 4b instrumentation (Iter 3 axes; per DECISION 74e)
- strict_yield_count = 0 ; plausible_yield_count = 336 ; reject_yield_count = 479 (816 pairs over 102 targets)
- W-DEF fire-rate = 0.423 (NEW diagnostic axis: definitional-witness availability -- HIGH; rules out generator/description starvation)
- STRICT-blocker = tier-direction (NEW diagnostic: 100% of W-DEF hits failed dir_strict due to flat T1)

## Status / requests
- DECISION 75d: laptop-only path CONFIRMED -> bge-blocker does NOT block Phase 3 STRICT-discovery experiments (only the M4d F1 metric / 73g remains remote-blocked).
- DECISION 74c: HARD_FAIL with mechanism (tier-flatness). RECOMMEND Director consider lever (a)/(c) (tier-differentiation or L6-PROOF directional witness) as the Iter 4 design rather than more same-tier iterations.
- 336 PLAUSIBLE edges are available if Director wants them ratified (PLAUSIBLE-tier; per DECISION 74a do NOT add to M4d STRICT-walk). I have NOT emitted them pending your call (avoid PLAUSIBLE-tier flood without targeting).
- Skunkworks: no STRICT to vet this iteration (0 produced). The finding itself (tier-flatness gate) may warrant Skunkworks adversarial check of my direction=tier operationalization.

## ADDENDUM (19th rule -- adversarial self-correction of my OWN recommendation above)
Re-examining lever (c): L6-PROOF backward-chains over EXISTING DEPENDS_ON edges. But the Iter 3 targets are degree-0 (zero edges -- that is WHY they are targets). A backward chain from a degree-0 atom is EMPTY. So lever (c) is CIRCULAR for isolated atoms: establishing STRICT direction by proof needs pre-existing edges, but the isolated atoms have none. Likewise lever (a)'s tier-gradient does not pre-exist for them.

SHARPENED CLAIM: autonomous STRICT-DEPENDENCY discovery for ISOLATED (degree-0) atoms is structurally BOOTSTRAP-LIMITED -- it requires externally-authored scaffolding (a tier assignment that creates a gradient, OR a first foundational edge to chain from). The autonomous loop CAN discover RELATEDNESS (PLAUSIBLE, 336 this iteration) for isolated atoms on its own, but STRICT direction cannot be self-bootstrapped from zero structure without an unsound directional guess (which the substrate correctly refuses, 18th rule). Iter 1's 6 STRICT were NOT a counterexample: its targets (MDP/q_learning) were already T3 with the foundational tier-gradient PRE-AUTHORED. So the only sound lever for NEW STRICT on isolated atoms is an AUTHORING act (tier-differentiation or seed-edge), not a loop iteration. This is a clean substrate-product scope boundary: relatedness is autonomous; strict dependency needs a foundation to build from.

-- EXP-DEV (Prover)
