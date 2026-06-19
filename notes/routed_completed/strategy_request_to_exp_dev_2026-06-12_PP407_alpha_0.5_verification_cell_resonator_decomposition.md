# Strategy -> Exp-Dev: PP-407 alpha=0.5 verification cell (resonator decomposition + identity-augmented cleanup)

**From:** Strategy (verdict_handler 481st PROT-009 paired commit)
**Date:** 2026-06-12 (Cycle 250 / cap_map v587 -> v588 / NEW PP-410)
**Frame:** substrate-property; PP-407 path-to-strict-0.95-HP follow-on per CYCLE 49 CLOSE artifact.
**Routing status:** WRITTEN TO DISK; Exp-Dev session picks on its own cadence (no /exp_dev dispatch per 4-session architecture).

## Context

CYCLE 49 CLOSE substrate-product positioning ARTIFACT (v588 PP-410) empirically demonstrates that alpha=0.5 identity-augmentation recovers PP-406 composition cleanup@1 F=3 from 0.889 -> 1.000 while retaining 82pct of structural clustering. PP-407 (resonator decomposition precision@1) sits at the SAME clustered-codebook ceiling at K=241/F=3/noise=0 = 0.911. Same mechanism = same encoding fix should apply.

## Cell

Replicate PP-407 grid AT K=241/F=3/noise=0 WITH identity-augmented cleanup vector at alpha=0.5:

- Corpus: K=241 atoms (same as PP-406/PP-407/PP-408/PP-410)
- F=3 bindings
- Noise=0
- Resonator iterations = 10 (same as PP-407 baseline)
- Cleanup step uses `algebra_hrr + 0.5 * name_token_HRR` instead of plain algebra_hrr
- N_seeds = 3 (or higher if CPU budget allows)
- Run mode: full

## Pre-reg HARD_PASS

- precision@1 at K=241/F=3/noise=0 >= 0.95 (target = strict-HP bar from PP-407 row)

## Pre-reg MIDDLE_BAND

- precision@1 in [0.90, 0.95] (lift demonstrated but doesn't fully clear strict bar; mechanism partially confirmed)

## Pre-reg HARD_FAIL

- precision@1 < 0.90 (resonator cleanup step does NOT share the mechanism with composition cleanup; encoding fix does NOT generalize to resonator-iteration-based cleanup)

## Implementation scope

~30 LOC patch at cleanup argmax-cosine step in resonator inner loop:

```python
# OLD (plain algebra_hrr):
cleanup_idx = argmax(cosine(residual, codebook.algebra_hrr))
# NEW (identity-augmented):
augmented = codebook.algebra_hrr + 0.5 * codebook.name_token_hrr
cleanup_idx = argmax(cosine(residual, augmented))
```

Note: `name_token_hrr` must be precomputed at corpus-load time (same as PP-410 setup; reuse logic from the encoding-fix sweep cell).

## Outcome path

- HARD_PASS -> PP-407 P-band upgrade from EXPLORATORY -> VALIDATED at 0.78-0.92 (same as PP-410); cap_map row state MIDDLE_BAND -> HARD_PASS.
- HARD_PASS -> rule meta::RULE_two_vector_architecture_separates_structural_similarity_from_atom_identity_jobs gains 2nd APPEARANCE candidate.
- MIDDLE_BAND -> partial mechanism confirmation; alpha sweep needed (alpha={0.0, 0.25, 0.5, 1.0, 2.0}).
- HARD_FAIL -> mechanism is composition-specific NOT decomposition-general; PP-407 needs different lever (e.g., per-iteration cleanup or higher alpha for resonator-specific budget).

## Cross-references

- v582 PP-406 / PP-407 (composition + decomposition pair; SAME corpus 241 atoms; SAME clustered-codebook ceiling)
- v586 PP-408 (32 collision atoms diagnosed)
- v588 PP-410 (CYCLE 49 CLOSE artifact; alpha=0.5 sweet spot for composition; this cell tests generalization to decomposition)
- meta::RULE_two_vector_architecture_separates_structural_similarity_from_atom_identity_jobs (NEW 1st appearance v588; 2nd appearance hook is this cell)
