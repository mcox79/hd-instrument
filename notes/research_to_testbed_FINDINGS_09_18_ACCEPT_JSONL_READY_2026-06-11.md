# Research -> Testbed: 18 ACCEPT concept atoms JSONL ready -- Type A closed-loop CYCLE #5 closes

**From:** Research  **Date:** 2026-06-11 late evening
**Re:** Hand-authored 18 ACCEPT atoms ready for ingestion

## File ready

`data/substrate_index/concept_corpus_findings_09_type_A_18_accept.jsonl` -- 18 atoms hand-authored, JSONL format matching existing concept corpus.

Each atom:
- corpus: concept
- kind: capability
- empirical_validation_status: Tier_C_candidate (substrate-proposed; Research validated + hand-authored; Tier-A promotion requires usage in 2+ PP rows)
- provenance: substrate_proposed_tier3_type_A_research_validated_accept
- drill_origin: findings_09_tier3_atom_candidates_2026-06-11
- decomposes_to: matching math atom (1:1)
- related_concepts: cross-links to PP rows where the capability is empirically observed

## 18 atoms listed

T2 substrate primitives (6): CAP_fhrr_bind / CAP_fhrr_unbind / CAP_superposition / CAP_bundling / CAP_circular_convolution / CAP_cleanup

T3 algorithms (9): CAP_viterbi_decoding / CAP_forward_algorithm / CAP_backward_algorithm / CAP_em_algorithm / CAP_bayesian_inference / CAP_hungarian_assignment / CAP_chu_liu_edmonds / CAP_dynamic_programming / CAP_discriminative_perceptron

T1 information-theoretic (3): CAP_shannon_entropy / CAP_kl_divergence / CAP_probability_distribution

## Type A closed-loop CYCLE #5 closes

The loop:
1. Testbed Tier 3 atom-candidate runner surfaces 39 candidates (Findings 09)
2. Research validates 18 ACCEPT / 16 REJECT / 5 DEFER (per-tier triage)
3. Research hand-authors 18 ACCEPT atoms (THIS FILE)
4. Testbed ingests into concept partition (NEXT)
5. Substrate atom count: 74 -> 92 (+18) post-ingestion
6. Layer 1 attribution may re-rank atom utility with new connections
7. Tier 3 -> Tier 4 sustained measurement: candidate-acceptance rate this cycle = 18/39 = 46%

## Ingestion request

Phase A (overnight or Day 2):
1. Validate JSONL parses correctly (atoms_module.py)
2. Compute algebra-vec per existing batch02_algebra_vec_remaining_53 pattern
3. Ingest via Testbed write boundary (enforces 7 invariants)
4. Update CLI stats counts
5. Re-run atom_candidates.py -- the 16 REJECT + 5 DEFER atoms should still surface OR new candidates appear if PP-row connections shift

Post-ingestion sanity check:
- Each new CAP_* atom should have >=1 referrer (the corresponding math atom via decomposes_to inverse)
- Re-run Layer 1 attribution: do any new CAP atoms add Net-Positive utility?

## Cross-references

- FINDINGS_09 validation: notes/research_to_testbed_FINDINGS_09_TIER3_ATOM_CANDIDATES_VALIDATION_2026-06-11.md
- 5-tier progression memory
- Substrate content sources rule 8 memory
- 5-signal-types operational memory

## Next: candidate source #5 implementation

Per Q2 validation, adding source #5 substrate-eval-references-unknown-math-term gives substrate another self-improvement channel: research notes citing math primitives substrate doesn't have. Day 2 implementation per drill spec in Findings 09 response.

---

**Testbed:** 18 ACCEPT atoms JSONL ready at data/substrate_index/concept_corpus_findings_09_type_A_18_accept.jsonl. Ingest at convenience to close Cycle #5 Type A first loop. 39-candidate acceptance rate this cycle = 46%.
