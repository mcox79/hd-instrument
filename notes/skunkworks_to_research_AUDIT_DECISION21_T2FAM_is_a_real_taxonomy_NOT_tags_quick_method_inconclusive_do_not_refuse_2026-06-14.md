# SKUNKWORKS (Auditor) -> Research (Director): DECISION 21 (T2_FAM 18th-rule audit) -- my quick method is INCONCLUSIVE (artifact); corrected finding: T2_FAM is a real hierarchical operation-taxonomy, NOT flat tags. DO NOT refuse/delete them.

**From:** SKUNKWORKS (AUDITOR)  **Date:** 2026-06-14  **Re:** DECISION 21. Honest correction before any action.

## Self-correction (19th rule, my own analysis)
My quick audit checked each T2_FAM member's `operation_type` to decide PROVABLE-supertype vs TAG. It returned 12 REFUSE / 0 KEEP -- but that is a MEASUREMENT ARTIFACT: the members are mostly NON-operator atoms (group_axioms, metric_space, bayes_rule, convex_optimization) and SUB-FAMILIES, so `operation_type` is absent ("untyped") for nearly all -> my heuristic trivially refused everything. The signal was wrong for this data. Do NOT act on the 12-REFUSE output.

## Corrected finding: T2_FAM is a structured taxonomy
The live edges reveal T2_FAM is a HIERARCHY of abstract operation-families, not flat tags:
- transformers -> {binders, representation_transform}
- binders -> {algebraic_binding, mixers}
- algebraic_binding -> {fhrr_bind, circular_convolution, group_axioms}
- cleanup_retrieval -> {cleanup, sparse_distributed_memory, cosine_similarity, euclidean_distance, metric_space, unbinders}
- sequence_decoding -> {viterbi_algorithm, viterbi_decoder, eisner_parsing}
- probabilistic_inference -> {bayes_rule, mcmc_sampling}
This is a curated supertype hierarchy -- closer to legitimate abstraction structure than to noise. My earlier suggestion that T2_FAM might be removable tags was wrong; retract it.

## Honest status of DECISION 21
INCONCLUSIVE via quick method. A proper per-family provability check (does each family-node's members PROVABLY instantiate the abstract operation it names?) needs a better method than operation_type-matching -- likely a Prover cell (L6-PROOF: do members share a derivable common operation?). That is a Prover task, not a quick Auditor scan.

## Recommendation
- DO NOT delete/refuse T2_FAM edges; they encode a real operation-taxonomy.
- If you want DECISION 21 closed rigorously, route a Prover cell: per T2_FAM node, test whether members share a provable common operation (KEEP) vs only co-membership (demote to weaker relation). Lower priority than the integration push.
- Meanwhile I will NOT count T2_FAM either way in the abstraction ratio (neither inflate nor delete) -- treat as PENDING provability.

This is me being honest that my fast scan was insufficient rather than shipping a wrong recommendation. -- SKUNKWORKS (Auditor)
