# Research CORRECTION: external corpus inventory -- substrate has MUCH MORE ingested than my prior coordination note claimed -- cycle-187 roadmap already active

**From:** Research  **Date:** 2026-06-13 (Cycle 51 close + USER full-auto overnight)
**Re:** USER catch on my incomplete inventory in research_to_testbed_PRODUCTION_SCALE_EXTERNAL_CORPUS_INGEST_5_CELL_DESIGN_*; verify-before-asserting failure on my part

## Honest correction

My prior coordination note (research_to_testbed_PRODUCTION_SCALE_EXTERNAL_CORPUS_INGEST_5_CELL_DESIGN_*) claimed substrate had "small-to-medium scale ingest with Wikidata + Mizar + nLab NOT BUILT". **This was incomplete and wrong.** USER correctly flagged that substrate has been downloading + ingesting external corpora.

I missed evidence because:
1. Looked only at LOCAL file system (`C:/Users/marsh/.claude/projects/d--AI/`) but ingest data is on REMOTE desktop (`C:/dev/hd-instrument/data/datasets/`)
2. Did not check git log for ingest commits
3. Did not search notes/ for ingest-related routing
4. Assumed current Cycle 51 numbering = absolute substrate lifetime; actually substrate has been at cycle 187+ in prior campaigns

## Corrected actual state (per git + notes evidence)

### OPERATIONAL (ingested or in progress)

| Corpus | Status | Scale | Performance |
|---|---|---|---|
| Wikipedia 100K | DONE | 100K articles | banked |
| Wikipedia 1M | DONE | 1M articles (1.45GB) | cycle 187 wikipedia_ingest **0.97 r@5 HARD-PASS** |
| ConceptNet | DONE | 458K facts | banked (per `8484fc7c` note "ConceptNet 458K 5pct full") |
| arXiv ML | DONE | 234K papers | banked (10% of ML / 1% of all-arXiv) |
| arXiv math.* re-ingest | APPROVED in flight | ~2M math facts at ~25 facts/sec | 22h re-ingest started Day 3-4 slot |
| Wikidata Stage A | IN FLIGHT | ~20% subset at ~23.4 facts/sec | running on home GPU |
| Wikidata5M | DONE | KB-shard for FB15K | banked (PP-313 0.965 FB15K) |
| Penn Treebank | BUNDLED | sample WSJ sec 24 20K tokens | substrate POS 0.906 (PP-362) |
| UD-English-EWT | BUNDLED | dependency parse corpus | dep-parse UAS gate authorized |
| MBPP | BUNDLED | code generation | CODEGEN-LIGHT-1 path |
| `tools/wikidata_dump_ingest.py` | OPERATIONAL | with --resume + incremental keys_partial | commit `7518c120` |
| Phase 1 evolve auto-ingest (research_drill_*.md) | OPERATIONAL | research_history partition | Cycle 13 4.3x atom growth proven |

### NOT YET INGESTED (per cycle-187 note `8484fc7c` strategic inventory)

| Corpus | Scale | USER-goal alignment |
|---|---|---|
| Semantic Scholar Open Corpus | 200M papers | huge gap; cross-discipline |
| PubMed | 35M abstracts | huge gap; biomedical |
| MathOverflow + math.SE | ~1M Q-A | math reasoning corpus |
| Stack Overflow + cs.SE | ~20M Q-A | code + algorithm reasoning |
| OEIS | sequences DB | math primitive cross-reference |
| Mizar Mathematical Library | 50K theorems | direct L6-PROOF + USER-goal alignment |
| ProofWiki | ~30K proofs | proof-corpus extension |
| nLab | ~10K-30K articles | category theory depth |
| Lean Mathlib | ~80K formalized statements | formal verification |
| Coq library | thousands of theorems | dependent type theory |
| DBpedia + YAGO + BabelNet | structured KG | knowledge graph integration |
| ORKG | structured research KG | research-graph integration |
| Connected Papers | citation graph | research-graph integration |
| bioRxiv + medRxiv + ChemRxiv | preprint corpora | biomedical + chemistry |
| PropBank + FrameNet + VerbNet | semantic role labeling | NLU depth |
| The Stack | code corpus | code-generation depth |
| DBLP | author-paper graph | bibliometrics |
| INSPIRE-HEP | physics literature graph | physics depth |
| Wolfram MathWorld | math reference encyclopedia | math primitive depth |

## Honest total estimate

Per cycle-187 strategic note: substrate has ingested **~0.01-0.1% of all scientific corpus**. The runway is **massive**. The existing roadmap (Tier 1 + 2 + 3 corpus expansion) was already in flight at cycle 187 + continuing.

## CELL 1-5 design status update

My prior CELL 1 Mizar parser skeleton + CELL 2 Wikidata SPARQL + CELL 4 nLab + CELL 5 Wikipedia math-targeted ARE STILL VALID work items for the NOT-YET-INGESTED bucket. CELL 1 Mizar in particular remains highest-priority USER-goal-aligned (Mizar's 50K formalized theorems with axiom dependencies map directly to L6-PROOF + CHTV-1 typed-derivation ground truth).

CELL 2 Wikidata SPARQL is PARTIALLY SUPERSEDED by existing `wikidata_dump_ingest.py` (Stage A in flight). What I proposed as new is actually existing pipeline scope-expansion. Coordinate with current Stage A; do NOT duplicate.

CELL 3 arXiv full-text is PARTIALLY DONE (arxiv ML 234K + arxiv math.* re-ingest 2M in progress). What I proposed as new is scope-expansion to live-update daily harvest.

CELL 5 Wikipedia math-targeted is PARTIALLY DONE (1M generic + 0.97 r@5). What I proposed as new is math/science category-tree filtering refinement.

CELL 4 nLab + Mizar + Semantic Scholar + PubMed + MathOverflow + math.SE + OEIS + Lean Mathlib + Coq remain GENUINELY NOT BUILT.

## Substrate-product positioning artifact correction

Cycle 51 close + post-CHTV-1 + corrected inventory:
- Substrate is FIRST cognitive architecture with cycle-187-validated 1M Wikipedia + 458K ConceptNet + 234K arXiv ML + Wikidata-in-flight ingest
- Substrate has CHECKABLE 0.97 r@5 retrieval over Wikipedia-scale corpus (PP-225 deterministic + Path A validated)
- Mizar + Semantic Scholar + PubMed + math.SE + Lean Mathlib remain genuine USER-goal-aligned gaps; CELL 1 Mizar still highest priority

## Methodology rule reinforcement

Per memory `feedback_full_auto_productivity_look_harder`: "VERIFY-BEFORE-BUILD (data-structure, env-availability bge-not-local, gate-state grep index atom count -- caught real issues + spawned ~6 substrate-extracted rules)". I violated this rule by claiming "NOT BUILT" without grepping git log + notes/ for ingest evidence.

Filing memory entry to PREVENT this class of mis-inventory in future Research sessions.

## Routing

- **Testbed**: coordinate with active Stage A Wikidata ingest (do NOT duplicate via new tool); CELL 1 Mizar still highest priority addition
- **Exp-Dev**: heat-aware queue still applies; remote_cpu_queue safe for new ingest cells
- **Research**: filing this correction + memory entry; future inventory questions require grep notes/ + git log first

## Cross-references

- notes/research_to_testbed_PRODUCTION_SCALE_EXTERNAL_CORPUS_INGEST_*.md (prior incomplete inventory; CORRECTED HERE)
- notes/research_to_testbed_CELL_1_MIZAR_INGEST_PARSER_SKELETON_*.md (Mizar skeleton; still valid)
- commit `b586e9ff` (1M Wikipedia downloaded)
- commit `8bcc38b5` (cycle 187 wikipedia_ingest 0.97 r@5 HP)
- commit `7518c120` (wikidata_dump_ingest.py operational with --resume)
- commit `8484fc7c` (cycle-187 SCIENTIFIC CORPUS INGEST STRATEGIC PRIORITIES note; ~0.01-0.1% total ingested with massive runway)
- commit `0580743d` (arxiv math.* re-ingest APPROVED Day 3-4 slot)

---

**Testbed + Exp-Dev:** RESEARCH CORRECTION external corpus inventory was incomplete substrate has MUCH MORE ingested than prior note claimed + Wikipedia 1M + ConceptNet 458K + arXiv ML 234K + arXiv math.* 2M re-ingest in progress + Wikidata Stage A 20pct in flight + Wikidata5M + Penn Treebank + UD-English-EWT + MBPP all OPERATIONAL + cycle 187 wikipedia_ingest 0.97 r@5 HARD-PASS + NOT YET INGESTED Semantic Scholar 200M + PubMed 35M + MathOverflow + Mizar + ProofWiki + nLab + Lean Mathlib + Coq + others + ~0.01-0.1pct total ingested massive runway + CELL 1 Mizar still highest priority USER-goal-aligned + CELL 2-5 partially superseded by existing pipelines coordinate not duplicate + verify-before-build rule reinforced + USER full-auto overnight continuing.
