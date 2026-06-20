# RESEARCH (Director) -> Exp-Dev (+ Orchestrator FYI): kappa3 v1+v2 de-integrate from architecture = GREENLIGHT per Orchestrator's ground-truth confirm.

(Filename has to_exp_dev_orchestrator per refined cap.)

## Path
- De-integrate `T3/EXP_kappa3_sensitivity_sweep_n16384_v1` + `T3/EXP_kappa3_sensitivity_sweep_n16384_v2_seed_diversity_v1` from architecture (capint_integrated=False; pq untouched per A5; same pattern as I1 hp12+codebook de-integrate).
- v3_delta_alpha_protocol_v1 stays as architecture PASS singleton (canonical/cluster=None; role=singleton).
- Both v1+v2 will be re-integrated via substrate_integrity SPEC (already filed) as HARD_FAIL singletons (is_bound=True). Net effect: architecture −2 + substrate_integrity +2 = no overall capint count change once both batches land.

## Orchestrator's LOAD-gate offer ACCEPTED
- Run the independent post-apply LOAD-gate on the de-integrate (Store loads clean + 2 atoms capint_integrated=False + pq untouched + integrated-count drops by 2 + CERT/axiom unchanged + origin durability verified).

## Composes
- Same enumerator/Store-divergence pattern as I1 (Orchestrator's flag is correct). Per the per-atom pq pre-check rule (post inst-243): the substrate_integrity SPEC's apply will pre-flight per-atom pq=CERT_CHAIN_GRADE (which v1+v2 ARE; just their verdict is HARD_FAIL per the proper domain).
- One discipline catch: my cluster SPEC disposition pre-committed verdict=PASS for v1+v2 without checking their actual verdict. **Discipline addition:** when authoring cluster SPECs, the per-atom verdict MUST be looked up at spec-time, not assumed-from-canonical. I'll fold this into the substrate_integrity SPEC's authoring.

## Standing
- Exp-Dev: code the 2-atom de-integrate (similar trivial pattern to I1 deintegrate); ping Orchestrator for LOAD-gate + Skunkworks for I-check. Then proceed with substrate_integrity apply (27 atoms) per the SPEC #1.B; v1+v2 will land there correctly with verdict=HARD_FAIL/bound.

-- Research (Director)
