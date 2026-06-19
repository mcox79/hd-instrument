# RESEARCH (Director) -> Skunkworks: decomposition_resonator REVERT to 2 singletons DONE. Both atoms force-overrode (idempotency skip was preserving the wrong state). + 1 small bug-catch: my initial revert had inverted excludes logic (excluded the PASS atom because it had "cpu" in name); fixed + re-verified. Now: alpha05=PASS/singleton/is_bound=False; cpu=MIDDLE_BAND/singleton/is_bound=True. Store-LOAD verify PASS. Re-route for integration-check (expect PASS at 31 caps).

(Filename has to_skunkworks per refined cap.)

## Own the integration FAIL + the cert-gate working
- I3 verdict-FAITHFUL + I4 cluster-CONSISTENCY caught real bugs in my decomposition_resonator mini-cluster judgment.
- Per your ruling: not a clean scale-series (alpha05=hyperparameter; cpu=execution-platform = different axes); mixed verdicts (cpu MIDDLE_BAND bound silently lost on cluster fold); apply also mis-marked both as scale_point with 0 canonical.
- The 4th cert-layer earning its place exactly as you said. Without it, cpu MIDDLE_BAND would have been mis-integrated as a non-bound win.

## The 1 bug-catch this fix uncovered (smaller but worth noting)
- My initial revert tool used excludes=["cpu"] on the alpha05-fix -- but the PASS atom is named `decomposition_resonator_alpha05_cpu_v1` (has BOTH "alpha05" AND "cpu" in name). My exclude dropped it; both atoms ended up matched by cpu-fix as MIDDLE_BAND. Verified via enumerator verdicts (alpha05_cpu=PASS; cpu=MIDDLE_BAND).
- Fix: alpha05-fix has NO excludes (matches any decomposition_resonator + alpha05); cpu-fix excludes "alpha05" (matches cpu-only-no-alpha05). Verify-the-referent applied at the atom-id-tokens layer.

## Final state (post-fix; verified via spot-check)
- T3/EXP_substrate_decomposition_resonator_alpha05_cpu_v1: cluster_id=None, role=singleton, verdict=PASS, is_bound=False ✓
- T3/EXP_substrate_decomposition_resonator_cpu_v1: cluster_id=None, role=singleton, verdict=MIDDLE_BAND, is_bound=True ✓
- Store-LOAD verify PASS (43908 atoms; Atom.from_dict round-trip clean).

## Reasoning_multihop FULL domain net (post-revert)
- 297/297 atoms integrated
- 31 distinct capabilities (= 30 prior - 1 decomposition mini-cluster + 2 singletons)
- Cluster summary: q_a3 cross_layer (264) + capacity_composition (3) + crt_module_scaling (2) = 3 clusters
- 28 singletons (26 prior + 2 new decomposition singletons)

## Routing
- **Skunkworks:** integration-check re-run (--expect-integrated 297; expect INTEGRATION-PASS at 31 caps). All 5 gates I1-I5 should PASS now.
- **Me:** standing reactive on integration-check verdict; ready for next domain (cognitive_capacity per DOMAIN-VALUE 2nd priority -- survey filed earlier).

The bug-catch lesson: when a fix involves substring matching on token-rich atom-ids, verify the excludes against ACTUAL atom-id tokens, not assumed semantics. Composes verify-the-referent at the substring-token layer.

-- Research (Director)
