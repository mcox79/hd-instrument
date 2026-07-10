# CSKG commonsense-core k-core density gate — off-disk measurement

**Date:** 2026-07-10
**Task:** Pre-registered CSKG foundation gate. Is CSKG's cross-cutting COMMONSENSE core dense enough
to support relational inference (FB15k-237-like), before we commit to building on it?
**Gate (pre-registered):** PASS = a k-core with **>=5000 nodes at internal avg-degree >=37** (FB15k-237-like).
**Same discipline that showed:** ConceptNet slice (avg-deg 2.68) is 14x too sparse; FB15k-237 clears
(raw deg ~37, 10-core 9,549 @ 39); CoDEx-L / WN18RR (~4) FAIL.

## VERDICT: PASS (both full graph AND cross-cutting commonsense core clear the floor)

The commonsense spine survives stripping ALL lexical/taxonomic dilution. After dropping ~79% of edges
(Roget/WN synonymy, RelatedTo, Antonym, FormOf, IsA, HasContext, dbpedia facts, ...), the remaining
ATOMIC+ConceptNet-causal/functional subgraph (501k nodes / 1.18M simple edges) STILL contains a dense
inference core clearing the FB15k-237 floor with a **substantial (>=5000-node) core**:

- **CROSS-CUTTING 12-core = 23,632 nodes @ avg-deg 38.4  → PASS** (2.5x the size of FB15k-237's usable 10-core, at comparable density)
- CROSS-CUTTING 13-core = 17,793 @ 43.3  (PASS); 14-core = 10,731 @ 55.0 (PASS)
- Cliffs at k=15 to 3,617 nodes @ 112.9 (node-count fails, but an ultra-dense kernel remains)

Stripping lexical dilution **matters for honesty** (raw avg-deg 4.8-5.5 is misleading; the full-graph
core is partly a Roget-synonymy/RelatedTo-hub artifact) but does **NOT** overturn the verdict — the
commonsense core is genuinely dense. **CSKG is a valid dense-commonsense foundation.** The usable spine
is specifically the cross-cutting subgraph, and the dense inference core is the ~10-24k-node k=12-14 band.

---

## 1. Acquisition (traceable)

- Source: Zenodo record 4331372 (Ilievski/Szekely/Zhang, USC-ISI, CSKG v1.0, ESWC'21), file `cskg.tsv.gz`
  (the MERGED graph — identical nodes merged). URL: `https://zenodo.org/api/records/4331372/files/cskg.tsv.gz/content`
- Downloaded FULL: **112,312,195 bytes** gzipped. Columns: `id node1 relation node2 node1;label node2;label relation;label relation;dimension source sentence`.
- **6,001,531 data rows** (edges). Dropped 47,970 self-loops -> **5,953,561 non-self-loop directed edges**; **2,159,195 distinct nodes**.
- Analysis: manual Batagelj-Zaversnik core decomposition on the SIMPLE UNDIRECTED graph (parallel/antiparallel
  edges deduped), numpy CSR. k-core avg-deg = internal avg degree of the induced core (matches how
  FB15k-237's "10-core @ 39" is defined). Script: scratchpad/kcore.py.

## 2. Raw density (confirms ~5.4)

- Directed edges 5,953,561 / nodes 2,159,195 -> **raw undirected avg-deg = 5.51** (5.56 incl self-loops) — **~5.4 CONFIRMED, sparse on average.**
- Simple-undirected (deduped) edges = 5,167,463 -> avg-deg 4.79. Max degree 11,037 (hub-heavy, long tail).

## 3. Relation-type split (LEXICAL/taxonomic vs CROSS-CUTTING commonsense)

58 distinct relations. Edge totals:

| Bucket | Edges | % | Content |
|---|---|---|---|
| **LEXICAL / taxonomic / encyclopedic (DILUTION)** | ~4,708,873 | **79.1%** | RelatedTo 1.70M, Synonym 1.25M, Antonym 401k, FormOf 379k, DerivedFrom 326k, IsA 316k, HasContext 238k, fn:HasLexicalUnit 59k, EtymologicallyRelatedTo 32k, SimilarTo 31k, DistinctFrom 8k, DefinedAs 2k, InstanceOf 1.5k, dbpedia/* ~16k |
| **CROSS-CUTTING commonsense (SPINE)** | 1,244,688 | **20.9%** | ATOMIC at:* 711k (xAttr/xWant/xEffect/xNeed/xReact/xIntent/oWant/oEffect/oReact), LocatedNear 152k, MayHaveProperty 94k, UsedFor 43k, CapableOf 42k, PartOf 32k, AtLocation 28k, HasSubevent 25k, HasPrerequisite 25k, Causes 17k, HasA 17k, MannerOf 13k, MotivatedByGoal 9k, HasProperty 9k, ReceivesAction 6k, CausesDesire 5k, + smaller (Desires, MadeOf, CreatedBy, Entails, ...) |

Source provenance: ConceptNet 3.34M, **Roget thesaurus 1.40M** (this is where most Synonym/Antonym dilution
comes from), ATOMIC 711k, VisualGenome 266k, Wikidata 102k, WordNet-related ~135k, FrameNet ~73k.

## 4. THE GATE — k-core decomposition (nodes + internal avg-deg)

### (a) FULL graph  (2,159,195 nodes; 5,167,463 simple edges; avg-deg 4.79; degeneracy 371)

| k | nodes | avg-deg | k | nodes | avg-deg |
|---|---|---|---|---|---|
| 5 | 214,260 | 23.6 | 18 | 29,561 | 72.6 |
| 8 | 107,529 | 36.0 | 20 | 26,436 | 76.9 |
| 10 | **81,844** | **42.2** | 30 | 15,818 | 97.7 |
| 12 | 64,383 | 48.0 | 37 | 10,781 | 113.8 |
| 14 | 48,879 | 55.5 | 40 | 8,937 | 122.8 |
| 16 | 36,110 | 65.2 | 50 | 4,951 | 157.8 |

FULL PASSES massively (10-core 81,844 @ 42.2 = 8.6x FB15k-237's 9,549-node core) — but this is inflated by
lexical hub structure (Roget synonym cliques, RelatedTo). Largest connected component = 1,702,680 (78.9%).

### (b) CROSS-CUTTING subgraph  (501,391 nodes; 1,184,796 simple edges; avg-deg 4.73; degeneracy 147)

| k | nodes | avg-deg | verdict |
|---|---|---|---|
| 5 | 50,352 | 26.6 | |
| 8 | 39,567 | 30.6 | |
| 10 | 32,773 | 33.5 | (just under deg floor) |
| 11 | 28,606 | 35.5 | |
| **12** | **23,632** | **38.4** | **PASS (>=5000 @ >=37)** |
| 13 | 17,793 | 43.3 | PASS |
| 14 | 10,731 | 55.0 | PASS |
| 15 | 3,617 | 112.9 | cliff — node count fails |
| 20 | 3,037 | 128.0 | ultra-dense kernel |
| 37 | 2,016 | 165.5 | |
| 50 | 1,634 | 184.3 | |

Largest connected component = 424,080 (84.6%) — the commonsense spine is well-connected, not fragmented.
Structure: a broad dense floor-clearing band (k=12-14, ~10-24k nodes @ deg 38-55) sitting on top of an
ultra-dense small kernel (k>=20, ~1.6-3k nodes @ deg 128-184, i.e. the high-frequency ATOMIC event /
prototypical-concept hubs).

## 5. Comparison vs the calibration set

| Graph | avg-deg | usable dense core | Gate |
|---|---|---|---|
| FB15k-237 (works) | ~37 | 10-core 9,549 @ 39 | PASS (reference) |
| **CSKG FULL** | 4.8 (raw 5.5) | 10-core 81,844 @ 42; 37-core 10,781 @ 114 | **PASS** (lexically inflated) |
| **CSKG CROSS-CUTTING** | 4.7 | **12-core 23,632 @ 38; 14-core 10,731 @ 55** | **PASS** (commonsense spine survives stripping) |
| ConceptNet slice (ours) | 2.68 | — | FAIL (14x too sparse) |
| CoDEx-L | — | — | FAIL |
| WN18RR | ~4 | — | FAIL |

## 6. Implications for the foundation decision

1. **BUILD ON CSKG — its commonsense core clears the inference density floor.** No custom dense-commonsense
   build is required; the graph already contains a FB15k-237-caliber (in fact ~2.5x larger) dense core.
2. **Strip the lexical dilution when using it.** Raw avg-deg (4.8/5.5) badly understates the core, and the
   full-graph core is partly a Roget-synonymy artifact — do NOT feed raw CSKG. Restrict to the cross-cutting
   subgraph (ATOMIC + ConceptNet causal/functional/lateral + LocatedNear/MayHaveProperty): 501k nodes /
   1.18M edges, of which the dense inference spine is the ~10-24k-node k=12-14 band.
3. **Design note / caveat:** the cross-cutting core cliffs at k=15 (23.6k -> 3.6k). The robust >=5000-node
   floor-clearing core lives at k=12-14; below that you gain nodes but drop under deg 37; above k=14 you
   drop under 5000 nodes. So the "substantial dense core" is ~10-24k nodes, not the whole 501k spine — the
   periphery of the commonsense subgraph is still sparse and would need the same treatment as our ConceptNet slice.

---
**Traceability:** all numbers from `cskg.tsv.gz` (112,312,195 bytes, Zenodo 4331372); script kcore.py;
6,001,531 rows -> 5,953,561 non-self-loop edges -> 2,159,195 nodes. No hallucinated stats.
