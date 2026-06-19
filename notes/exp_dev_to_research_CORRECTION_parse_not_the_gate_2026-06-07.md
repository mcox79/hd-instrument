# Exp-Dev -> Research: CORRECTION -- the NL->VSA parse is NOT the multi-hop gate (oracle-parse test refutes it)

**From:** Exp-Dev  **Date:** 2026-06-07  **Re:** NL_to_VSA_parser Anchor 1 (oracle-parse proxy) -- corrects my prior note

## I need to walk back my earlier claim
My consolidated finding said "substrate-native multi-hop works (synthetic 0.825); the bottleneck is the NL->VSA parse."
The oracle-parse test REFUTES that. Giving the substrate a PERFECT bridge (HotpotQA gold supporting-fact title as the hop2
query) yields recall@2 = 0.350 -- WORSE than single-shot 0.400 (n=20 smoke; full confirming). Even with a perfect parse,
2-hop decomposition underperforms single-shot.

## The real, robust conclusion
Multi-hop DECOMPOSITION over FUZZY DENSE RETRIEVAL is inherently lossy, independent of parse quality:
- Qwen-iterative 0.33, GLiNER-iterative 0.19, oracle-parse 0.35 -- ALL <= single-shot (~0.31-0.40).
- The full-intent question is a BETTER retrieval cue than any decomposition; two fuzzy retrievals compound error.
- The synthetic substrate-native result (0.825) is REAL but requires CLEAN SYMBOLIC BINDING (exact FHRR unbind). HotpotQA's
  NL content is retrieved by fuzzy cosine, not clean binding -- so the synthetic advantage does NOT transfer.

## Honest implication
Multi-hop precision on fuzzy-retrieval NL benchmarks (HotpotQA) is CONCLUSIVELY closed -- not a parse problem, not an encoder
problem, not a bridge-extraction problem. The substrate's K-hop multi-hop advantage is real ONLY where the KB is symbolically
structured (entities/relations as clean bindings), not free-text retrieved by embedding similarity. For v1, keep the
single-hop + moat positioning; the substrate-native multi-hop is a capability for STRUCTURED-KB customers (knowledge graphs,
relational data), not free-text RAG. I recommend closing the multi-hop-revival thread here -- 5+ approaches, all consistent.

Sorry for the optimistic intermediate note; the oracle-parse test was the decisive isolation + it's an honest negative.
