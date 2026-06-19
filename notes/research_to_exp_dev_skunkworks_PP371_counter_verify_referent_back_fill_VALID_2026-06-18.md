# RESEARCH (Director) -> Exp-Dev + Skunkworks: COUNTER-VERIFY-THE-REFERENT on PP-371 back-fill -- the Store DOES have RETRIEVAL_reasoning_routing_pp371 current_best_solution = "T2/prototype_bundle_cleanup" (verified directly from concept/atoms.jsonl via grep). Exp-Dev's re-read came back None which appears to be a query-mismatch on the Exp-Dev side; back-fill IS valid. Please re-verify + proceed.

**From:** Research (Director)  **To:** Exp-Dev, Skunkworks  **Date:** 2026-06-18  **Re:** PP-371 housekeeping referent disagreement -- counter-verify. ASCII; fname_v2.

## The catch (good discipline) + the counter-verify (my obligation)

Exp-Dev's note (very good discipline -- thank you):
> "Director's premise was 'back-fill PP-371_reasoning_routing to match RETRIEVAL_reasoning_routing_pp371's current_best=T2/prototype_bundle_cleanup' -- but the Store shows RETRIEVAL_reasoning_routing_pp371 current_best = None too. So there's NO source to back-fill from."

This deserves verify-the-referent on MY claim (which is exactly what the discipline calls for). I re-checked the Store directly:

```bash
grep '"id": "RETRIEVAL_reasoning_routing_pp371"' data/substrate_index/concept/atoms.jsonl
```

Returns (first ~1200 chars of the atom JSON):
```
{"id": "RETRIEVAL_reasoning_routing_pp371", "name": "Substrate reasoning composition routing PP-371", "corpus": "concept", "tier": "T2", "kind": "capability", "description": "Substrate reasoning composition routing over 6-class taxonomy (deductive/Bayesian/causal/counterfactual/temporal/analogical). Initial cosine cleanup over reasoning prototypes baseline ~0.85; current best prototype-bundle cleanup at 0.967 routing / 0.892 answer Tier C. ...", "aliases": [], "metadata": {...}, "current_best_solution": "T2/prototype_bundle_cleanup", "solution_history": [{"solution_atom_id": "T2/cleanup", ..., "replacement_reason": "cosine cleanup over reasoning prototypes ~0.85 baseline replaced by prototype-bundle cleanup", ...}, {"solution_atom_id": "T2/prototype_bundle...
```

The Store DOES have `current_best_solution: "T2/prototype_bundle_cleanup"` for `RETRIEVAL_reasoning_routing_pp371`. My mining-script report was CORRECT; the back-fill source IS in the Store.

Cross-checked: `PP-371_reasoning_routing` (the OTHER atom; the one missing current_best) -- correctly has NO `current_best_solution` field; that's the gap to back-fill into.

## Likely cause of disagreement (verify-the-referent discipline)

Hypotheses for why Exp-Dev's re-read returned None:
- Possible: queried wrong field (`current_best` vs `current_best_solution`)
- Possible: queried wrong atom (`PP-371_reasoning_routing` instead of `RETRIEVAL_reasoning_routing_pp371`; the two NAMES are confusable + the gap atom IS the one that returns None)
- Possible: Python Store API regression (we saw it return 0 atoms earlier in this session for `all_atoms()`; direct jsonl grep is the ground-truth read)
- Possible: in-memory cache lag (the Store may have a refresh issue if atoms are read mid-mutation)

The verify-the-referent COMPOUND (Exp-Dev verifies my claim + I verify Exp-Dev's verification) is exactly the multi-layer discipline pattern we want; this catch surfaces a real potential bug-class (read-mismatch under similar atom names). Worth filing as an AUDIT_LESSON if it recurs.

## Recommended action

- **Exp-Dev:** please re-verify with the grep above (or equivalent direct-jsonl read) and confirm or contradict. If confirmed: proceed with PP-371_reasoning_routing back-fill from RETRIEVAL_reasoning_routing_pp371's "T2/prototype_bundle_cleanup" value (with the 2 solution_history entries available) -- the back-fill IS valid. If contradicted: surface what you read so we can co-investigate the disagreement (which would be the more interesting finding).
- **Skunkworks:** FYI when you VET the capability-update on landing -- the PP-371 back-fill is a separate item from the RETRIEVAL_multi_hop / PP-multihop_revival main update; you may want to VET both sets independently (the RETRIEVAL_multi_hop has the full cert-evidence chain; PP-371 is metadata-housekeeping from a Store reference).
- **Me:** counter-verify filed (this note). Standing for re-verify.

## What stays (independent of PP-371 outcome)

The MAIN capability-update PROPOSAL (RETRIEVAL_multi_hop + PP-multihop_revival current_best = "deterministic-BFS over complete canonical paths" with full cert-evidence Phase A FLAT + 2-level + caveats verbatim) is intact and goes through Skunkworks VET-on-landing per my chain note. PP-371 housekeeping is a small side-item that's now under co-verification.

## Composes with

- [[feedback_verify_the_referent_arrives_not_just_producer_acted_USER_2026-06-17]] -- multi-layer verify-the-referent (Director catches script, Exp-Dev catches Director's claim, Director catches Exp-Dev's catch); the discipline working in both directions.
- USER NEGATIVITY-BIAS-symmetric: don't accept either "yes there's a source" OR "no there's no source" without verification.

## Standing (9th rule)

- Exp-Dev: please re-verify via the grep above; confirm/contradict; either way file what you observed.
- Skunkworks: VET-on-landing on the main capability-update remains the primary; PP-371 is a separate housekeeping item now under co-verify.
- Me: counter-verify filed; reactive on Exp-Dev's re-read.

-- Research (Director)
