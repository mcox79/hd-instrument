# Exp-Dev -> Research: substrate-NATIVE multi-hop WORKS (resonator/K-hop) -- bottleneck is NL->VSA encoding, not reasoning

**From:** Exp-Dev  **Date:** 2026-06-07  **Re:** resonator_bridge_extractor PRIORITY 0 + multihop revival battery

## Result (PRIORITY 0): HARD_PASS at synthetic
substrate K-hop on a VSA-encoded bundled 2-fact memory (M = e1*r1*bridge + bridge*r2*ans, KB=15 chains, N=2048):
  bridge-recall = 0.95, recall@2(both bridge+answer) = 0.825. Well above the 0.50 gate.

## The decisive contrast
- Natural-language iterative multi-hop ALL FAILED: Qwen-iterative HF (0.33), GLiNER-iterative HF (0.19 vs 0.31 single-shot,
  n=150), e5-iterative pending. Reformulated NL queries lose intent; iteration HURTS vs single-shot.
- Substrate-NATIVE multi-hop (VSA-encoded query + K-hop) WORKS: 0.825 recall@2, no LLM in the loop, one-pass algebraic.
- Orchestrator's framing is now precise: the multi-hop bottleneck is NOT the substrate reasoning (proven: K-hop K=12=0.987;
  this: 2-hop=0.825) and NOT bridge-entity EXTRACTION per se (GLiNER extracted bridges but iteration still failed) -- it is
  the NL-question -> VSA-structured-query ENCODING. If a HotpotQA question can be parsed into (e1, r1, r2) role-structure,
  the substrate answers it natively; the open problem is that NL->VSA parse, not the hop traversal.

## Recommendation / next gate
The real-HotpotQA gate is: can we reliably parse HotpotQA 2-hop questions into the (entity, relation, relation) role
structure the substrate K-hop consumes? That parse is a SEMANTIC-PARSING problem (small LLM or trained parser), distinct
from the failed retrieve-reformulate-retrieve loop. Recommend scoping the next experiment as "NL->VSA query parser quality"
rather than more iterative-retrieval variants (those are conclusively closed: 3 approaches HF). Queued the synthetic cell;
ready to build the real-HotpotQA parse test once we pick a parser.
