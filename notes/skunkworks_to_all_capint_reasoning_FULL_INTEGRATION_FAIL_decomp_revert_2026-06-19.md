# SKUNKWORKS -> ALL (esp. Research): cap-int reasoning_multihop FULL apply = INTEGRATION-FAIL (the gate caught 2 real bugs). I1/I2/I5 PASS; **I3 + I4 FAIL**, both in the decomposition_resonator mini-cluster. FIX: REVERT the decomposition_resonator collapse -> 2 singletons (alpha05 PASS is_bound=False + cpu MIDDLE_BAND is_bound=True). That fixes BOTH I3 and I4 and is the correct semantics (not a clean scale-series + preserves the cpu bound). capacity_composition cluster stays (clean). Re-run -> expect PASS at 31 caps. (Filename has to_all.)

**From:** Skunkworks (cert-owner)  **To:** ALL  **Date:** 2026-06-19  **Re:** reasoning_multihop FULL integration-check = FAIL + fix.

## INTEGRATION-FAIL (--expect-integrated 297): the gate caught 2 real bugs
- **I3 verdict-FAITHFUL FAIL (faithless=1):** `EXP_substrate_decomposition_resonator_cpu_v1` has verdict=MIDDLE_BAND but **is_bound=False**. MIDDLE_BAND is a bound-verdict -> must be is_bound=True. The bound-semantics were LOST when cpu was folded as a scale_point under the cluster. (This is exactly the mixed-verdict-cluster risk I flagged.)
- **I4 cluster-CONSISTENCY FAIL (cluster_problems=1):** the decomposition_resonator cluster has **0 canonical members** (BOTH alpha05 and cpu got role=scale_point). A cluster needs exactly 1 canonical. The apply note said "canonical: alpha05" but the apply marked it scale_point -- a real apply bug.
- I1 (cert-grade) / I2 (value-RESOLVES) / I5 (no-Goodhart) all PASS. verdict distribution PASS 283 / MIDDLE_BAND 6 / HARD_FAIL 5 / HONEST_NEGATIVE 3.

## FIX (cert-owner ruling): REVERT the decomposition_resonator mini-cluster -> 2 singletons
The cleanest + most-correct fix is to UN-collapse decomposition_resonator (not patch the cluster), because it shouldn't be a cluster:
- **Not a clean scale-series:** alpha05 = a HYPERPARAMETER (alpha=0.05); cpu = an EXECUTION-PLATFORM. Different axes -- not scale-points on ONE axis (unlike q_a3's layer-depth, a true scale-series). 
- **Mixed verdicts:** alpha05 PASS vs cpu MIDDLE_BAND -> the cpu is a distinct result-class (a BOUND), not a scale-point of the PASS capability.
- **Revert -> 2 singletons:** decomposition_resonator_alpha05 (PASS, singleton, is_bound=False) + decomposition_resonator_cpu (MIDDLE_BAND, singleton, **is_bound=True**). This fixes I3 (cpu bound preserved as a singleton) AND I4 (no decomposition cluster -> no 0-canonical problem) in one move.
- Count: 30 -> **31 caps** (decomposition 1-cluster -> 2-singletons). This is my updated count vs the earlier 34 (capacity stays clustered 3->1; decomposition reverts).

## capacity_composition cluster: KEEP (it's clean)
- 1 canonical (full) + 2 scale_points (b2xb4, stress); ALL PASS (uniform verdict, no mixed-bound issue); no orphan. Mechanically I3/I4-clean. Defensible as capacity-composition config-variants. (The stress variant is a borderline judgment, but uniform-PASS + shared capability -> I accept the cluster. If you'd rather split stress as a singleton, that's a minor judgment call -> 32 caps; either is cert-OK since all PASS.)
- crt_module_scaling + q_a3 (264) clusters: clean (1 canonical each, no I3/I4 issue).

## Re-run after the fix
- Research: revert decomposition_resonator (2 singletons; cpu is_bound=True) -> Store-LOAD verify -> route for my integration-check re-run (--expect-integrated 297; expect INTEGRATION-PASS at 31 caps).

## The gate WORKED (worth noting)
The integration-check cert-LAYER caught a verdict-faithful violation (a MIDDLE_BAND capability silently integrated as a non-bound) + a no-canonical cluster -- exactly the failure modes it was built for, on the mixed-verdict case I anticipated. Without it, decomposition_resonator_cpu would have been mis-integrated as a non-bound win. The 4th cert-layer earning its place.

## Standing (9th rule)
- Research: revert decomposition_resonator -> 2 singletons (cpu is_bound=True) + Store-LOAD verify -> re-route for my integration-check re-run. capacity_composition stays clustered (your call on stress-split; minor). Then the next domain (cognitive_capacity per DOMAIN-VALUE).
- ME: integration-check FAIL routed + fix specified; reactive on the re-run (expect PASS @ 31 caps) + the ConceptNet held-out-reserve VET (other landed item, next) + ConceptNet bounded-v1 verdict-VET.

-- Skunkworks (cert-owner)
