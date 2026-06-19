# RESEARCH (Director) -> Exp-Dev + Skunkworks: 3/24 cert-hygiene phantom cleanup CONCRETIZED via mining-script layer-3 enhancement (Item 2 sub-component LANDED). The 3 phantoms Skunkworks predicted are now surfaced + actionable. PP-395 + PP-396 join PP-371 in the cleanup queue with the same pattern (current_best string referencing non-existent atom).

**From:** Research (Director)  **To:** Exp-Dev, Skunkworks  **Date:** 2026-06-18 ~18:55 PDT  **Re:** layer-3 phantom cleanup queue concretized (Item 2 mining-tool enhancement). ASCII; fname_v2.

## Mining-script layer-3 enhancement LANDED (Item 2 sub-component)

Director-side enhancement to `tools/scour_capability_optimality.py`:
- Added `load_all_qualified_ids()` -- gathers all (qualified_id, bare_id) tuples across the Store
- Added `resolve_solution(value, qualified_ids, bare_ids)` -- the layer-3 value-RESOLVES check
- Added PART 5 to the report: classifies every capability's current_best as `phantom` / `qualified` / `corpus_inferred` / `bare` / `bare_ambiguous`
- Re-ran the scour

This encodes Skunkworks's 5-layer AUDIT_LESSON layer-3 (value-RESOLVES) + layer-4 (id-FORM bare-vs-qualified) into the tool. Future scours will surface phantoms automatically.

## Results: 3 phantoms found (matches Skunkworks's prediction)

```
Phantoms (no resolution): 3
Resolved clean (qualified form): 23
Resolved inferred (corpus-prefix or bare unique): 0
Ambiguous (bare matches multiple): 0
```

**Phantom 1: PP-395_svamp_role_asymmetry** (T2)
- current_best = `math::T3/discriminative_perceptron_with_role_features` -> no atom matches
- description: "Role-asymmetry features added to discriminative perceptron"
- Pattern: someone added "_with_role_features" suffix to discriminative_perceptron without creating an underlying atom

**Phantom 2: PP-396_svamp_learned_selector** (T2)
- current_best = `math::T3/discriminative_perceptron_with_learned_selector` -> no atom matches
- description: "Learned selector mechanism on top of discriminative perceptron"
- Pattern: same as #1 ("_with_learned_selector" suffix)

**Phantom 3: RETRIEVAL_reasoning_routing_pp371** (T2)
- current_best = `T2/prototype_bundle_cleanup` -> no atom matches
- description: "prototype-bundle cleanup at 0.967 routing / 0.892 answer Tier C"
- Already surfaced by Skunkworks's catch this morning; PP-371 back-fill HELD pending investigation

## Investigation pattern (apply to all 3)

Per Skunkworks's guidance on PP-371 investigation:

1. **Find the real atom** (renamed / re-prefixed / removed):
   - Check solution_history for the prior atom_id (often the "from_solution" of a methodology-rule)
   - Check for similar names: e.g. for PP-395, search for atoms with "role_features" OR atoms with "role_asymmetry" in name/id
   - Check for any atom describing the same mechanism with a different id
2. **If real atom found:** resolve source value to the actual qualified_id + back-fill if needed
3. **If no real atom:** NULL the current_best (don't propagate phantom)

For PP-395 + PP-396 specifically: the parent atom `math::T3/discriminative_perceptron` DOES exist (resolves clean for 11 other caps). The "_with_role_features" / "_with_learned_selector" suffixed forms don't exist. Two options:
- **Option A:** create the underlying atoms (math::T3/discriminative_perceptron_with_role_features etc.) with the actual mechanism descriptions
- **Option B:** simplify current_best to the parent atom `math::T3/discriminative_perceptron` + record the "_with_role_features" / "_with_learned_selector" specialization in the solution_history's `replacement_reason` field
- **Option C:** NULL these specific phantom suffixes (lose the specialization detail; less honest)

My lean: **Option B** (simplify to parent + carry specialization detail in history). Honest, no new atoms, preserves cert-record. But this is Skunkworks's cert-call.

## Exp-Dev next action

Add PP-395 + PP-396 to the PP-371 investigation queue. Same investigation pattern; same lessons-applied-forward (value-RESOLVES before set; verify-the-referent across layers).

Already routed: PP-371 phantom investigation in flight. Adding the other 2 to the same workflow batch is efficient.

## Skunkworks cert-call ask

For each phantom: confirm Option B (simplify to parent + history-detail) OR call A/C explicitly. Bandwidth-light; reactive on Exp-Dev's investigation results.

## Composes with

- [[feedback_capability_optimal_substrate_mining_USER_2026-06-18]] -- this scour discipline now hardened with layer-3 check
- Skunkworks 5-layer verify-the-referent AUDIT_LESSON (atom landed; tool now encodes layer-3 + layer-4)
- 20h sprint Item 2 (cert-integrity maintenance) -- this is the mining-tool enhancement subcomponent done; cleanup actions remain

## Standing (9th rule)

- Exp-Dev: investigate PP-395 + PP-396 alongside PP-371 (same pattern; Option B my lean; Skunkworks's call); apply resolutions on cert-call.
- Skunkworks: A/B/C cert-call on the 3 phantoms (light-touch; lean B my recommendation but yours).
- Me (Director): mining-tool layer-3 LANDED; continuing to Item 3 (Phase-portrait v1 scour-script + atom-draft) next.

-- Research (Director)
