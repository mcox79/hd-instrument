# Research -> Testbed: scientific corpus ingest strategic priorities + new sources

**From:** Research  **Date:** 2026-06-11 late evening
**Re:** User strategic question: percent of scientific knowledge we're downloading; what to add; substrate-on-corpus capability

## Honest current state

| Source | Status | Coverage estimate |
|---|---|---|
| Wikidata | Stage A1 ~23.4 facts/sec | ~20% of subset; ~0.1% of full |
| Wikipedia 100K | DONE | ~1.4% of 7M articles |
| ConceptNet 8M | DONE 458K facts | ~5% (full) |
| arxiv ML 234K | DONE | ~10% of ML; ~1% of all-arxiv |
| Penn Treebank + UD-English-EWT | Bundled | NLP-foundational |
| MBPP | Bundled | ~1K code problems |
| WordNet + MetaMath + DLMF + arxiv math.* | Planned/scheduled | Tier-1 NLP+math |
| Semantic Scholar Open Corpus (~200M) | NOT INGESTED | **0%** -- huge gap |
| PubMed (~35M) | NOT INGESTED | **0%** -- huge gap |

**Honest total: ~0.01-0.1% of all scientific/encyclopedic/linguistic corpus.** Massive runway.

## High-leverage sources to add (ranked)

### Tier 1 (most-leverage; commercial+research differentiating)

1. **Semantic Scholar Open Corpus** (~200M papers metadata + abstracts; canonical citation graph)
2. **PubMed abstracts** (~35M biomedical; trivial download)
3. **arxiv math.\*** (drill 13's 42 cross-domain equivalences auto-extend from this; scheduled)
4. **MathOverflow + math.StackExchange** (high-quality structured math Q&A)
5. **Stack Overflow + cs.SE** (code + algorithm + concept dialogue)
6. **OEIS** (Online Encyclopedia of Integer Sequences; pure structural math)

### Tier 2 (domain depth)

7. PropBank / FrameNet / VerbNet (semantic role labeling)
8. The Stack (~3TB GitHub code)
9. DBLP (CS bibliography; citation graph CS-specific)
10. INSPIRE-HEP (high-energy physics)
11. bioRxiv / medRxiv / ChemRxiv (open preprints)
12. Wolfram MathWorld + ProofWiki + nLab (encyclopedic + formal math)

### Tier 3 (knowledge graphs)

13. DBpedia + YAGO + BabelNet (structured Wikipedia + lexical)
14. Open Research Knowledge Graph (ORKG)
15. Connected Papers (citation graph)

## Strategic UNLOCK: substrate-on-scientific-corpus

At corpus scale, substrate becomes:

| Capability | What it does |
|---|---|
| Universal scientific search | Substrate-novel relational + algebraic queries LLMs cannot match |
| Cross-domain equivalences auto-extend | Drill 13's 42 manual -> 1000s substrate-discovered |
| Schools-of-thought at scale | Drill 12's 30-school taxonomy -> 500+ traced via citation + topic + concept graphs |
| Mathematical-discovery engine | Substrate proposes structural unifications across arxiv math.* + DLMF + ProofWiki + MathOverflow |
| Gap detection at corpus scale | Substrate identifies 1000s of under-explored adjacencies |
| Lineage tracing of any idea | "What schools contributed to X? What un-explored adjacent fields?" |
| Recursive substrate-on-corpus self-evaluation | 8-layer program against entire scientific corpus |

## Infrastructure requirements

| Scale | Substrate capacity | Validated |
|---|---|---|
| kb100K | PP-225 Tier A | YES |
| kb1M streaming | Test A authorized (drill 17) | PENDING |
| kb10M | Multi-substrate wrapper (memory: substrate-v32-engineered-wrapper) | THEORETICAL |
| kb100M+ | Dense-Hopfield + sharded substrate (drill 7 frontier-scale) | TO RESEARCH |

## Strategic recommendation

### Short-term (next 2 weeks)
- Complete current ingest pipeline (Wikidata + WordNet + arxiv math.*)
- Test A 1M streaming continual learning (drill 17 routed; ~1 day CPU)
- Validate substrate spectral observability at M >= 100 (Day 2)

### Medium-term (next 1-3 months)
- Ingest Tier 1 sources (Semantic Scholar Open Corpus + PubMed + Stack Exchange + OEIS)
- Scale substrate to kb10M with multi-substrate wrapper
- Substrate-self-index validated against Tier 1 corpora
- Cross-domain equivalences auto-extend from arxiv math.* + DLMF

### Long-term (3-12 months)
- Ingest Tier 2 + Tier 3 sources
- Substrate-as-mathematical-discovery-engine (Tier 5 of 5-tier progression)
- Commercial: substrate-as-scientific-corpus-search + LLM applications
- Substrate proposes novel research questions empirically

## What I'm dispatching

2x DEEP drill on substrate-as-universal-scientific-corpus architecture + scale + capabilities + risks (background; ~5 min). Will return concrete pilot experiments to test feasibility.

## Strategic significance

User's strategic vision: substrate-on-substrate (today) + substrate-on-scientific-corpus (proposed) = recursive scientific instrument. The current ingest (~0.01-0.1% of all corpus) is the foundation; scaling to Tier 1 (Semantic Scholar Open Corpus + PubMed + arxiv math.* + Stack Exchange) is the massive runway.

Combined with today's substrate-self-evaluation closed loop empirically operational + universal compositional generation engine + NORTH STAR head-to-head won + substrate v4.0 lineage triangle complete: the substrate-on-scientific-corpus direction is the natural extension of today's work.

## Cross-references
- Drill 17 RAG-backend: notes/research_drill_substrate_continual_learning_rag_backend_2x_2026-06-11.md
- Drill 13 cross-domain equivalences: notes/research_drill_cross_domain_equivalences_catalog_2x_2026-06-11.md
- Drill 12 schools-of-thought: notes/research_drill_schools_of_thought_lineage_2x_2026-06-11.md
- 5-tier progression: substrate_on_substrate_5_tier_progression_2026-06-11
- Universal compositional engine: substrate_unified_compositional_generation_engine_2026-06-11

---

**Testbed:** scientific corpus ingest strategic priorities ranked Tier 1-3; Semantic Scholar Open Corpus + PubMed + Stack Exchange + OEIS as top adds; substrate-on-scientific-corpus drill dispatched; user vision of substrate-as-recursive-scientific-instrument captured.
