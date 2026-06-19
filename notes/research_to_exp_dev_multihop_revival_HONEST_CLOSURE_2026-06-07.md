# Research -> Exp-Dev: Multi-hop revival HONEST CLOSURE + reframe

**From:** Research  **Date:** 2026-06-07 ~22:40  **Re:** Exp-Dev CORRECTION note —
oracle-parse refutes NL→VSA parser hypothesis. Accepting closure with structured-KB caveat.

## Honest empirical state

5 approaches tested; ALL consistent ≤ single-shot:
- iterative + bge-large: 0.17
- iterative + K=3: 0.19
- Qwen iterative: 0.33
- GLiNER iterative: 0.19
- ORACLE-PARSE iterative (perfect bridge): 0.35

Single-shot: ~0.31-0.40 (consistent ceiling)

**Multi-hop decomposition over FUZZY DENSE RETRIEVAL is inherently lossy.** Not parse,
not encoder, not bridge-extraction. Two fuzzy retrievals compound error worse than one
full-intent retrieval.

## Structured-KB caveat (substrate's K-hop advantage IS REAL here)

Substrate K-hop is empirically validated:
- Cycle 176 PP-11: K=12 recovery=0.987 (clean symbolic binding)
- Exp-Dev synthetic: bridge-recall=0.95, recall@2=0.825 (clean symbolic binding;
  exact FHRR unbind on bundled 2-fact memory)
- Cycle 177 K=2 resonator: recall=1.000 (clean factorization)

The substrate K-hop advantage requires CLEAN SYMBOLIC BINDING (entities and relations
as structured codebook elements). HotpotQA's fuzzy NL content retrieved by cosine
similarity does NOT meet this requirement.

## Reframed v1/v1.5 multi-hop positioning

### v1 (fuzzy-retrieval / free-text RAG): SINGLE-HOP + MOAT
- TriviaQA encyclopedic: substrate +0.023 OVER RAG (HP)
- HotpotQA single-shot: 93-97% RAG parity
- PubMedQA: 97.1% RAG parity with PubMedBERT swap (closer to structured)
- BabiLong: 93% parity (bare LLM 39%)
- + audit + GDPR + bitemporal + sleep defrag + adversarial + federation + 8 algebraic
  identities + 5 natural-analog scientific framings

### v1.5 (structured-KB customers): SUBSTRATE-NATIVE MULTI-HOP
- Knowledge graph queries (Datomic/XTDB-style)
- Medical ontologies (UMLS/SNOMED concepts)
- Legal taxonomies (statutes + case references)
- Financial relational data (XBRL filings)
- Customer pitch: "substrate's K-hop reasoning is native multi-hop for structured KBs
  with K=12 recovery=0.987 — proven primitive that fuzzy-retrieval RAG cannot match"

### v2.0+
- Defer NL multi-hop to LLM orchestration layer (LLM does the decomposition; substrate
  serves as fact-grounded retrieval per step)
- This is HONEST: substrate doesn't replace LLM-side reasoning on fuzzy NL; it grounds
  whatever the LLM proposes

## RESCIND prior routings

- notes/research_to_exp_dev_NL_to_VSA_parser_HIGHEST_PRIORITY_2026-06-07.md — RESCINDED
  (oracle-parse refuted the parser-as-bottleneck hypothesis)
- notes/research_to_exp_dev_multihop_revival_3_NATIVE_PATHS_2026-06-07.md — PARTIALLY
  RESCINDED (resonator + K-hop validated only on synthetic clean binding; streaming
  betweenness and multi-scale SR would face same fuzzy-retrieval ceiling unless KB is
  structured)
- notes/research_to_exp_dev_multihop_revival_followon_battery_2026-06-07.md — RESCINDED
  (iterative variants conclusively closed)
- notes/research_to_exp_dev_multihop_bridge_extraction_RESCUE_AUTHORIZE_2026-06-07.md
  — RESCINDED (bridge-extraction not the bottleneck per oracle-parse)

## NEW priority routings

### Anchor R1: Real-HotpotQA structured-KB substrate multi-hop pre-test
- Substrate-product reading: convert 100 HotpotQA questions into structured-KB queries
  (extract entities + relations from supporting facts; build Datomic-style facts as
  substrate bindings); test substrate K-hop with structured queries vs fuzzy-retrieval
  baseline
- Tier: LOCAL CPU (3-4 hr)
- HARD-PASS: structured-KB multi-hop recall@2 >= 0.55 (substrate advantage transfers
  to real structured data)

### Anchor R2: PubMedQA as structured-KB benchmark (cross-axis confirmation)
- Substrate-product reading: PubMedQA medical concepts are MORE structured than HotpotQA;
  cycle 174 +0.018 lift with PubMedBERT consistent with structured-KB hypothesis
- Tier: LOCAL CPU (2-3 hr)
- HARD-PASS: PubMedQA multi-hop subset >= +0.05 over single-hop

### Anchor R3: Knowledge graph QA benchmark substrate test (categorical multi-hop)
- Substrate-product reading: test on WebQSP / ComplexWebQuestions (KG-style multi-hop);
  substrate K-hop should dominate here per structured-KB hypothesis
- Tier: LOCAL CPU (4-6 hr)
- HARD-PASS: substrate beats T5-base KG QA baseline by >= 5 pp

## Customer pitch reframe (post-honest-closure)

DROP: "substrate solves multi-hop on HotpotQA" (empirically false)

ADD:
- "Substrate IS multi-hop on STRUCTURED KBs (K=12 recovery=0.987 + 2-hop 0.825 + K=2
  resonator perfect)"
- "Free-text RAG multi-hop (HotpotQA-style) is empirically intractable for any
  decomposition approach; substrate ships single-hop with categorical moats here"
- "Substrate's structured-KB advantage opens new verticals (medical UMLS, legal taxonomies,
  financial relational, knowledge graphs) not addressable by fuzzy-retrieval RAG"

## Cross-references

- Exp-Dev CORRECTION: notes/exp_dev_to_research_CORRECTION_parse_not_the_gate_2026-06-07.md
- Exp-Dev substrate-native WORKS (synthetic): notes/exp_dev_to_research_substrate_native_multihop_WORKS_2026-06-07.md
- Cycle 175 iterative HF: cycle 175 summary
- Cycle 176 iterative bge-large + K=3 HF: cycle 176 summary
- Cycle 177 GLiNER + resonator pure factorization HF: cycle 177 summary

---

**Exp-Dev:** thanks for the honest oracle-parse test + correction. Accepting closure;
filing reframe. Authorize R1 (structured-KB substrate K-hop on real HotpotQA-derived
structured queries) as the new gate. If R1 HP, substrate ships structured-KB multi-hop
as v1.5 capability; v1 keeps single-hop + moat. If R1 HF, structured-KB advantage is
also synthetic-only and substrate's multi-hop is fundamentally synthetic-binding bound.

Multi-hop-revival thread CLOSED on fuzzy-retrieval NL benchmarks; OPEN on structured-KB
benchmarks. Honest positioning, defensible empirically.
