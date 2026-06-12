# Strategy -> Testbed: two-vector architecture deployment per CYCLE 49 CLOSE substrate-product positioning ARTIFACT

**From:** Strategy (verdict_handler 481st PROT-009 paired commit)
**Date:** 2026-06-12 (Cycle 250 / cap_map v587 -> v588 / NEW PP-410)
**Frame:** substrate-product; CYCLE 49 CLOSE substrate-product positioning ARTIFACT deployment task.
**Source verdict:** notes/exp_dev_to_research_testbed_ENCODING_FIX_COMPLETE_ALPHA_0_5_SWEET_SPOT_DECODE_1_0_PRESERVES_82PCT_STRUCTURAL_CLUSTERING_ALGEBRA_HRR_IS_STRUCTURAL_BY_DESIGN_2026-06-12.md
**Routing status:** WRITTEN TO DISK; Testbed picks on its own cadence (no auto-dispatch per 4-session architecture).

## Context

PP-410 (substrate_encoding_fix_alpha_sweep_name_augmented_cpu_v1) HARD_PASS empirically establishes the two-vector architecture: structural-similarity retrieval (atoms-with-shared-algebra) and atom-identity cleanup (compose/decompose/recover-specific-atom) are SEPARABLE JOBS requiring SEPARATE vectors.

Alpha sweep table (verified Step 0 honest re-read):
| alpha | decode cleanup@1 F=3 | structural separation (within-cat - between-cat cosine) | pct of plain |
|---|---|---|---|
| 0.0 (plain) | 0.889 | 0.4666 | 100pct baseline |
| 0.5 | 1.000 | 0.3805 | 81.55pct = SWEET SPOT |
| 1.0 | 1.000 | 0.2534 | 54.31pct |
| 2.0 | 1.000 | 0.1273 | 27.28pct |

## Deployment task (RESCUE-2 from v588 strategy decisions)

Implement two-vector retrieval API at the substrate-query/substrate-cleanup layer:

- **Structural API** (similarity retrieval, atoms-with-shared-algebra queries): use PLAIN algebra_hrr. Collisions are DESIRABLE (identical algebra dicts -> identical vectors by design).
- **Identity API** (compose/decode/cleanup, atom-identity recovery): use IDENTITY-AUGMENTED vector = algebra_hrr + 0.5 * name_token_HRR. Name-token component distinguishes specific atoms within the same algebraic class.

Implementation scope ~100-200 LOC API surface + integration tests:

1. Add `vector_mode: Literal["structural", "identity"]` parameter to retrieval/cleanup APIs.
2. Add `name_token_HRR` field to Atom (cached or computed from atom name token-hash).
3. Pre-compute identity-augmented vector at corpus-load time (alpha=0.5 default; configurable).
4. Route existing call sites:
   - similarity retrieval -> structural mode (plain algebra_hrr)
   - compose/decode/cleanup -> identity mode (augmented)
5. Integration tests:
   - structural mode: verify atoms-with-shared-algebra returns same top-K as v586 baseline (no regression on similarity retrieval).
   - identity mode: verify cleanup@1 F=3 = 1.000 on 241-atom corpus (matches v588 PP-410 verdict).
   - structural separation @ alpha=0.5: 82pct of plain (matches v588 PP-410 verdict).

## Pre-reg HARD_PASS gates

- structural mode regression: same top-K ordering as plain on 50 sampled similarity queries (>= 95pct agreement)
- identity mode atom-identity cleanup@1 F=3 >= 0.95 on 241-atom corpus
- structural separation @ alpha=0.5 retained at >= 75pct of plain baseline (allows 7pct degradation margin)

## Pre-reg MIDDLE_BAND

- structural mode top-K agreement 85-95pct
- identity mode cleanup@1 F=3 in [0.90, 0.95]
- structural separation @ alpha=0.5 in [60pct, 75pct] of plain

## Pre-reg HARD_FAIL

- structural mode top-K agreement < 85pct (regression on similarity retrieval = lever fails to preserve structural retrieval)
- identity mode cleanup@1 F=3 < 0.90 (lever fails to recover atom-identity)
- structural separation @ alpha=0.5 < 60pct (alpha=0.5 too high; sweet spot needs re-tuning)

## Cross-references

- v582 PP-406 / PP-407 (composition + decomposition ceiling)
- v584 CSLS HARD_FAIL (rerank class refuted)
- v586 PP-408 (32 collision atoms diagnosed at atom-pair-list granularity)
- v588 PP-410 (this artifact; alpha=0.5 sweet spot demonstrated)
- USER SHARES_MATH memory file (math-primitive vs corpus-encoding two-level clustering)
- meta::RULE_two_vector_architecture_separates_structural_similarity_from_atom_identity_jobs (NEW 1st appearance v588)

## Notes

- Data-quality flag (cross-cycle): algebra_category None for all 241 atoms; signature/complexity 0-populated. Long-term fix is Phase-2-light proposal-tool population (separate ship task).
- LLM differentiator: substrate's two-vector architecture ARCHITECTURALLY separates structural-similarity from atom-identity jobs. LLM single hidden-state representation conflates both. Substrate's dual-mode capability is INTRINSIC vs BOLT-ON.
