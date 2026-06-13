# Research -> Testbed + Exp-Dev: MATH + SCIENCE CORPUS PARALLEL-INGEST COORDINATION -- 3 LANES (A mapper breadth + B Mizar/Lean Mathlib/OEIS bedrock + C BATCH 19-25 structural depth) -- per USER directive "are we continuing to get all math data downloaded and ingested"

**From:** Research (guiding session)  **Date:** 2026-06-13 (Cycle 51 close + USER full-auto overnight)
**Re:** USER directive "Are we continuing to get all the math data downloaded and ingested? This seems very important to the depth mapping and bedrock work that testbed and expdev are working on, while it may be parallel ultimately having access to all mathematical and scientific knowledge to fill in gaps will be super important"

## TL;DR

USER is right + I strongly agree. Math/science corpus ingest is KEY for USER vision substrate-on-all-knowledge. Current state: mapper build IN PROGRESS (4.37M facts breadth queue); BUT bedrock-specific corpora (Mizar + Lean Mathlib + OEIS + ProofWiki + Coq) are NOT in parallel queue with mapper -- they were queued AFTER mapper completes.

**Recommendation**: 3-lane parallel-ingest restructure. Restructure Testbed throughput across lanes A + B + C running concurrently rather than serially.

## Honest assessment (agree with USER + nuance on sequencing)

### Why USER is right (KEY):

1. **L6-PROOF depth ceiling = 3** is corpus-limited per Exp-Dev empirical
2. **Manual authoring (BATCH 17-25) is one lever** -- meaningful but slow (10 atoms per batch + 30 DEPENDS_ON edges)
3. **Mizar 50K formalized theorems WITH AXIOM DEPENDENCIES** would give substrate INSTANT depth 5-10+ chains, no manual authoring needed
4. **Lean Mathlib 80K formalized statements** = similar instant-depth payoff
5. **USER goal "substrate understands its own mathematics" at FULL strength** = scale + structure both required
6. **Recursive self-improvement loop Stage 2** (find-relevant-knowledge) needs deep + broad knowledge base
7. **Substrate-product positioning at scale**: LLMs trained on ~13T tokens; substrate at ~1.7M atoms is 0.01-0.1% of comparable corpus -- need orders-of-magnitude scale-up to match language mastery

### Nuance (not all corpora equal):

- **High USER-goal alignment** (axiom-dependency structure + L6-PROOF compatible):
  - Mizar Mathematical Library (50K theorems w/ axiom deps; PROVEN format)
  - Lean Mathlib (80K formalized math)
  - Coq library (thousands of theorems)
  - ProofWiki (~30K proofs)
  - OEIS (370K math sequences w/ structured definitions)
  - DLMF (Digital Library of Math Functions)
- **Medium USER-goal alignment** (rich content but flat structure):
  - arXiv math.* + math.SE + MathOverflow + Stack Exchange math
  - Wolfram MathWorld (math reference encyclopedia)
- **Lower USER-goal alignment** (breadth + retrieval but not bedrock):
  - Wikidata truthy 3.4M facts (already in queue)
  - ConceptNet 458K facts (already ingested)
  - arxiv ML 234K (already ingested)
  - Wikipedia 100K + 1M (already ingested)
  - Semantic Scholar 200M (HUGE; mostly flat citations + abstracts)
  - PubMed 35M (HUGE; biomedical breadth)

**Key insight**: high-USER-goal-alignment corpora (Mizar + Lean Mathlib + OEIS + ProofWiki) are MUCH SMALLER than the flat-triple corpora (50K + 80K + 370K + 30K = ~530K atoms total) BUT have MUCH higher per-atom USER-goal leverage. Should NOT be deferred behind huge low-USER-goal corpora.

## 3-lane parallel-ingest coordination

### LANE A: Mapper build + breadth ingest (Testbed primary)

| Item | Status | Est cost |
|---|---|---|
| LFS migration P0.3 | IN PROGRESS (USER auth + handoff filed) | 1-2h |
| extract-from-facts COMMON MAPPER build | IN PROGRESS | 1-2 days |
| First mapper run: wikidata_truthy_50m --filter math/science | gated on mapper | 6-12h |
| Second mapper run: conceptnet_8m --filter all | gated | 1-2h |
| Third mapper run: arxiv_2m | gated | 2-4h |
| Fourth mapper run: pubmed_5m | gated | 1h |
| Fifth mapper run: wikipedia_100k --filter math/science | gated | 2-4h |

**Cumulative LANE A**: ~3-5 days build + ingest. Substrate +2-5M atoms.

### LANE B: BEDROCK math + science PARALLEL with LANE A (Testbed secondary or split)

| Item | Why parallel | Est cost | Per-atom USER-goal leverage |
|---|---|---|---|
| **CELL 1 Mizar Mathematical Library** (~50K formalized theorems) | axiom-dependency structure direct L6-PROOF lift | 3-5 days build + 2 days ingest | VERY HIGH (axiom deps + proof chains explicit) |
| **CELL 6 Lean Mathlib** (~80K formalized math) | similar to Mizar | 2-3 days build + 2 days ingest | VERY HIGH |
| **CELL 5 OEIS** (~370K math sequences) | structured definitions + cross-reference + smallest size | 1 day build + 6h ingest (FAST) | HIGH (math primitive cross-reference) |
| **NEW CELL 7 ProofWiki** (~30K proofs) | proof corpus extension | 2 days build + 1 day ingest | VERY HIGH (proof chains explicit) |
| **NEW CELL 8 Coq Library** (theorems w/ dependent types) | dependent type theory + Curry-Howard direct | 3 days build + 2 days ingest | VERY HIGH (Curry-Howard pillar) |
| **NEW CELL 9 DLMF + MathWorld** (~50K math reference entries) | math primitive reference | 2 days build + 1 day ingest | MEDIUM-HIGH |

**Cumulative LANE B**: ~13-18 days build + ingest. Substrate +600K atoms with VERY HIGH per-atom USER-goal leverage.

**Why parallel-not-serial**: if LANE B is serialized behind LANE A (8-10 days mapper build + 20+ days ingest streams), substrate sits at depth-3 ceiling for weeks while waiting. Testbed bandwidth allows LANE A + LANE B concurrent via different runners / queues.

### LANE C: Research structural depth authoring CONTINUING

| Item | Status |
|---|---|
| BATCH 17 (depth-2 + new T1; filed) | filed; awaiting T1.5 ingest |
| BATCH 18 (deep chains 5-7 hops; filed) | filed; awaiting T1.7 ingest |
| **BATCH 19** foundational ML primitives (per drill #2 recipe) | NEXT Research artifact |
| **BATCH 20** NLU foundational atoms | queued |
| **BATCH 21** RL foundational atoms | queued |
| **BATCH 22** info-theory + statistics extensions | queued |
| **BATCH 23-25** deep chains 7-10 hops | queued |

**Cumulative LANE C**: ~80 atoms structural depth across BATCH 18-25. Substrate +80 atoms with EXTREME per-atom USER-goal leverage (curated authoring).

## Three-lane resource allocation

| Resource | LANE A | LANE B | LANE C |
|---|---|---|---|
| Testbed throughput | 60% (mapper + breadth ingest) | 35% (Mizar + Lean Mathlib + OEIS) | 5% (BATCH ingest review) |
| Exp-Dev throughput | standing (KP P5_v1 + SC scaling + Cell C re-run + L6-PROOF FINDER) | 0% (not Exp-Dev work) | 0% |
| Research throughput | 0% | 0% (CELL 1 Mizar skeleton already shipped; standing) | 100% (BATCH 19+ authoring) |

This allocation:
- Preserves mapper progress (LANE A continues at 60% Testbed)
- Adds bedrock high-USER-goal corpora in PARALLEL (LANE B at 35% Testbed)
- Continues Research structural depth (LANE C at 100% Research; non-Testbed-blocking)

## Substrate trajectory projection

| Phase end | Substrate atoms | L6-PROOF depth ceiling | KP scorecard | Substrate-product position |
|---|---|---|---|---|
| Cycle 51 close (now) | 1844 | 3 | 2-of-5 | 25+ artifacts |
| Phase 2 exit (72h; mapper + BATCH 17+18 ingest) | ~50K-100K | 5-7 | 4-of-5 | 30+ artifacts |
| Phase 3 exit (168h; LANE A all 5 corpora + LANE B Mizar/Lean/OEIS) | ~1-5M | 7-10 | 5-of-5 | 35+ artifacts |
| Phase 4 (Cycle 52; LANE B ProofWiki/Coq/DLMF + LANE C BATCH 19-25 + recursive loop operational) | ~5-15M | 10+ | 5-of-5 OPERATIONAL | 40+ artifacts |
| Long-term (Cycle 100; ~3-5 years) | ~10-100B atoms-equivalent | depth >= 15 | KP + recursive loop autonomous | substrate-LLM parity |

## Routing

- **Testbed**: confirm 60/35/5 LANE allocation OR propose alternative; LANE B parallel ingest cells: CELL 1 Mizar + CELL 5 OEIS + CELL 6 Lean Mathlib (smaller corpora first; CELL 7 ProofWiki + CELL 8 Coq + CELL 9 DLMF after); start with OEIS (FASTEST 1 day end-to-end) as risk-free first
- **Exp-Dev**: continue standing direction (KP P5_v1 + SC scaling + L6-PROOF FINDER re-run); no impact from this routing
- **Research**: filing this coordination; BATCH 19 as immediate next artifact (foundational ML primitives per drill #2 recipe + USER goal alignment); standing for Testbed LANE confirmation

## Cross-references

- notes/research_to_testbed_PRODUCTION_SCALE_EXTERNAL_CORPUS_INGEST_*.md (original 5-cell strategy)
- notes/research_CORRECTION_external_corpus_inventory_substrate_has_much_more_than_initially_claimed_cycle_187_roadmap_active_2026-06-13.md (existing corpus inventory + roadmap)
- notes/research_to_testbed_CELL_1_MIZAR_INGEST_PARSER_SKELETON_*.md (CELL 1 skeleton already shipped)
- notes/research_to_testbed_exp_dev_USER_VISION_all_knowledge_on_substrate_*.md (USER vision context)
- notes/testbed_to_research_FULL_ACCOUNTING_EXTERNAL_CORPORA_DOWNLOADED_REMOTE_DESKTOP_*.md (Testbed inventory)
- notes/exp_dev_to_research_DERIVATION_DEPTH_CEILING_*.md (depth ceiling 3 source = corpus-limited)

---

**Testbed + Exp-Dev:** MATH + SCIENCE CORPUS PARALLEL-INGEST COORDINATION + 3 LANES + LANE A 60pct Testbed mapper + breadth ingest 4.37M facts wikidata + conceptnet + arxiv ML + pubmed + wikipedia + LANE B 35pct Testbed BEDROCK Mizar 50K + Lean Mathlib 80K + OEIS 370K + ProofWiki 30K + Coq + DLMF = +600K atoms VERY HIGH per-atom USER-goal leverage + LANE C 100pct Research BATCH 19-25 80 atoms structural depth + start LANE B with OEIS FASTEST 1 day end-to-end + parallel-not-serial preserves mapper progress AND adds bedrock + USER full-auto overnight continuing.
