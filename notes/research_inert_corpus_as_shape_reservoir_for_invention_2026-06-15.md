# Research drill: inert data corpus as SHAPE RESERVOIR for invention/discovery

Date: 2026-06-15
Topic: corpus-as-shape-reservoir; gap-closure utility certification; 19K Wikidata + 651 isolated ingested-fact atoms as candidate reservoir
Mode: 2x DEEP, 4 parallel Sonnet lit-scan sub-agents, Opus synthesis
Calibration: P_deflated 0.15-0.25; novel-synthesis P capped at 0.50

---

## HEADLINE

The published architectural skeleton across 5 distinct research traditions (OEIS-style integer-catalogue lookup; CBR/RAG retrieval; KG-augmented reasoning; library-learning/anti-unification; non-traditional invention reservoirs) is unanimous: **compute a query SHAPE on the active side, use the inert corpus as a fingerprint/index for exact or near-exact lookup, and let any HIT count only as a CONJECTURE that a downstream soundness layer must certify**. This is exactly the pattern the substrate's gap-driven loop needs. The 19K Wikidata + 651 isolated ingested atoms qualify as a shape reservoir under this pattern IF (a) the gap-shape is typed/signature-bearing (not bag-of-tokens), (b) the bind step is a structural match (not embedding similarity alone), and (c) the substrate's existing 4-gate + L6-PROOF + capability-preservation stack plays the role of the downstream certifier. P_deflated = 0.45 (novel-synthesis cap 0.50): no published system simultaneously delivers typed-shape match + provable soundness over a heterogeneous incidental reservoir, which IS the substrate's open wedge.

## Cheap decisive test

ONE CPU smoke (~1 hour): pick 5 recently-authored substrate operator signatures (Phase 4a self-model entries) and 5 historical capability gaps where a signature was AUTHORED to fill the gap. For each:
1. Compute the gap-shape as a typed (sort, arity, axiom-term) tuple from the substrate-internal description of what was missing.
2. Run two retrieval modes against the 19,651-atom inert reservoir: (R1) exact-prefix / signature-string match (OEIS-style), and (R2) structural match by atom-type + relation-degree + neighbor-axiom-class (SME MAC stage analogue).
3. Run the 4-gate pre-check + L6-PROOF on each retrieved candidate.
4. HARD-PASS if >= 2 of 10 gaps return at least one candidate that PASSES all four gates AND would have been an equivalent fill for the historical authoring. HARD-FAIL if 0 of 10 produce a gate-passing candidate (reservoir is irrelevant). MIDDLE_BAND 1 of 10 = directional only.

## Falsifiable predictions

| ID | Prediction | HARD-PASS | HARD-FAIL |
|---|---|---|---|
| F1 | Exact-prefix lookup (OEIS pattern M1) finds zero usable candidates because gap-shapes are signature-typed, not numeric-prefix-typed | 0 hits | >=1 hit (refutes typed-only premise) |
| F2 | Structural / SME-MAC match (typed-signature + relation-degree fingerprint) recovers >= 2 of 10 gap-aligned candidates | >= 2 of 10 | 0 of 10 |
| F3 | Substrate 4-gate + L6-PROOF rejects >= 60% of structural-match candidates (sound discrimination, not random pass) | >= 60% reject | <= 30% reject (no discrimination) |
| F4 | DreamCoder-style anti-unification over PAIRS of inert atoms produces at least 1 candidate compound type-atom that fills a gap (this is the 21st-rule type-graph terminating in atoms direction; M3 PLDI 2021 precedent) | >= 1 valid compound | 0 valid compounds |
| F5 | The reservoir is LOAD-BEARING -- removing it (using only the 26,285 substrate atoms) drops gap-closure hit rate by >= 1 absolute hit across the 10 trials | drop by >= 1 | no drop (reservoir was inert noise) |
| F6 | Cosine-similarity / dense-embedding retrieval (RAG / kNN-LM pattern) produces matches but FAILS the 4-gate at >= 80% (i.e. embedding similarity is not a sound shape-match for typed gaps; confirms NEGATIVE finding from Sub-Agent 3) | >= 80% gate-reject | <= 50% gate-reject (substrate gates are not tight enough OR embedding works) |

## Cross-thread synthesis (5 patterns mapped to substrate)

### Pattern 1 -- OEIS / SuperSeeker (Sloane 2003; Colton-Bundy-Walsh AAAI 2000; Billey-Tenner 2013)

**What it is.** OEIS is a 370K-entry catalogue of integer sequences. The intended use is exact-prefix lookup, but the published mechanism for SHAPE-MATCH is SuperSeeker: apply ~130 transforms (binomial, Euler, Mobius, INVERT, WEIGH, differences/ratios, ...) to the query sequence, then look up each transformed result via the same exact-prefix index. The work is done ON THE QUERY SIDE, not the catalogue.

**Precondition.** Corpus stores fingerprints (initial terms); query side carries enough transforms to canonicalize before lookup.

**Shape-match mechanism.** Heavy query-side transformation -> cheap O(1)-ish exact lookup. Complexity ~ 130 x hash_lookup per query.

**Soundness on hit.** ZERO. A hit is a CONJECTURE; Colton's HR then dispatched to Otter/Mace for proof. Billey-Tenner 2013 frames the catalogue explicitly as a "fingerprint file for theorems."

**Substrate applicability.** Map to substrate: the "transforms" are the 4-gate canonicalizations (forward-walk operation-class-invariant + corpus-scoped monotone + axiom-term + dangling). Apply these to the GAP-SHAPE; index the 19,651 inert reservoir by the canonical signature tuple; hit = conjectured fill; substrate L6-PROOF + capability-preservation = the Otter/Mace soundness gate.

### Pattern 2 -- CBR + RAG + SME / MAC-FAC (Aamodt-Plaza 1994; Lewis NeurIPS 2020; Falkenhainer-Forbus-Gentner 1989; Gentner-Loewenstein-Thompson-Forbus 2009 "Reviving Inert Knowledge")

**What it is.** CBR retrieves stored <problem, solution> cases by feature-similarity, REUSES with adaptation, REVISES via external validator. RAG retrieves passages by dense MIPS over a corpus encoded by DPR. SME / MAC-FAC retrieves cases by structural alignment (systematicity preference for relation-preserving mappings). The Gentner et al. 2009 paper title -- "Reviving Inert Knowledge" -- is the exact phrase for the question's premise.

**Precondition.** CBR: indexed cases with similarity metadata. RAG: dense vector index, dual-encoder, generator. SME: cases as structured predicate-calculus expressions with explicit relational predicates.

**Shape-match mechanism.** CBR k-NN O(N) flat or O(log N) indexed. RAG sublinear FAISS MIPS. SME MAC = content-vector sparse prefilter, FAC = polynomial structural alignment. Critically, the "lexical surfaces differ" case is handled because SME-MAC matches on RELATION-PREDICATE TYPES, not surface tokens (this is the substrate-relevant variant).

**Soundness on hit.** CBR: NONE (Smyth-Keane critique on "most-similar = easiest-to-adapt" assumption). RAG: NONE (hallucination, grounding mismatch). SME: candidate inferences are HYPOTHESES, not theorems. Soundness lives in the REVISE step (CBR), in the generator/user (RAG, none), or in downstream verifier (SME for inferences).

**Substrate applicability.** STRONG mapping for SME, NEGATIVE finding for RAG/kNN-LM. The substrate's atom representation (sort + axiom-term + relation-edges) IS the SME structured-relational case format. The 4-gate stack plays the role of REVISE. Direct map: substrate atoms with relation-degree + axiom-class are the relational fingerprint; gap-shape is the new problem's relational template; MAC content-vector match over relation-predicate types ranks top-K; FAC structural alignment selects best; 4-gate verifies.

NEGATIVE: dense-embedding RAG (Lewis 2020) and kNN-LM (Khandelwal 2020) will NOT meet substrate's CHTV-1 / capability-preservation bar. Sub-Agent 2 P=0.70 they fail. F6 above tests this directly.

### Pattern 3 -- DreamCoder / Stitch / babble (Ellis PLDI 2021; Cao 2023 babble arXiv:2212.04596)

**What it is.** Library learning. Wake phase: neural policy searches the current library for programs matching I/O shape. Sleep-abstraction phase: anti-unification (or E-graph match in babble) over PAIRS of solved programs extracts shared sub-expressions; promotes to library entry if MDL improves. Sleep-dream: train policy.

**Precondition.** Typed lambda-calculus DSL; I/O example tasks; corpus of already-solved programs.

**Shape-match mechanism.** Anti-unification = the corpus-to-new-primitive mechanism. Take 2+ inert programs, compute their most-specific generalization; if it improves MDL, promote.

**Soundness on hit.** Sound by construction up to I/O example coverage (program executes correctly on the examples). No generalization guarantee beyond examples. Library entry promotion is MDL-justified, not semantically guaranteed.

**Substrate applicability.** Direct precedent for the 19K + 651 reservoir's role: the inert atoms become CANDIDATE PAIRS for anti-unification; pairs whose anti-unification produces a substrate-typed compound atom that fills a gap AND passes the 4-gate become library promotions. This IS the substrate's atom-MERGE Phase 2 trajectory (per MEMORY.md DECISION 100 checkpoint) but staged as gap-driven retrieval rather than batch sweep. F4 tests this directly.

### Pattern 4 -- KG-augmented QA + premise selection (Yih ACL 2015; Sun EMNLP 2018/2019; Urban-Vyskocil 2013; Kaliszyk-Urban 2014; Bansal ICML 2019 HOList; Irving NeurIPS 2016 DeepMath)

**What it is.** SP-QA: question -> staged query graph -> entity link + beam search over predicate sequences. PullNet: iterative learned subgraph expansion. Premise selection: conjecture features -> kNN over axiom library -> top-k axioms fed to ATP kernel.

**Precondition.** Typed KG (Freebase, Wikidata, Mizar, HOL Light). For premise selection: homogeneous formal library, not heterogeneous encyclopedic reservoir.

**Shape-match mechanism.** Query-graph beam search O(beam * neighbors_per_hop). Premise selection: kNN over feature space, O(|library|) with indexing, then ATP kernel re-verifies.

**Soundness on hit.** QA branch: NONE (soft matching, no logical guarantee). Premise selection: SOUND, because ATP kernel re-verifies the proof using retrieved axioms; retrieval is heuristic but final answer is kernel-certified. HOList/Holophrasm specifically uses HOL Light kernel.

**Substrate applicability.** Premise selection (M5-M6 from Sub-Agent 3) is the CLEANEST published precedent for substrate's pattern -- retrieval heuristic + downstream sound check. But: premise selection operates over HOMOGENEOUS formal library, not heterogeneous Wikidata-style reservoir. The substrate's premise is more ambitious: heterogeneous incidental reservoir + substrate-internal sound check. NEGATIVE finding from Sub-Agent 3 (verbatim): "No published system computes a TYPED MISSING-PREMISE SHAPE (a hole with signature/sort/role constraints) and retrieves a Wikidata/Wikipedia fact whose schema is checked to fill exactly that shape."

This is the substrate's open wedge. The 4-gate + L6-PROOF is the substrate-specific kernel that plays the ATP-soundness role over a heterogeneous reservoir.

### Pattern 5 -- non-traditional invention reservoirs (Chef Watson; DeepBach; KEGG/CMap drug repurposing; AlphaCode; Syzygy tablebases)

**What it is.** Catalogues authored for an unrelated purpose (cookbooks, Bach corpus, biological pathways, GitHub, exhaustive chess positions) used as gap-fill reservoirs via (gap-shape) -> (index) -> (candidate + filter).

**Precondition.** Domain catalogue of completed examples; gap definable in the catalogue's domain.

**Shape-match mechanism.** Varies: bipartite ingredient graph (Chef Watson); SPEAC signature recombinance (EMI); signature-reversal cosine (CMap); behavioral-cluster sampling (AlphaCode); canonical-position hash (Syzygy).

**Soundness on hit.** Chef Watson: hedonic regression. DeepBach: Turing discrimination. CMap: hypergeometric enrichment + in-vitro validation. AlphaCode: hidden test pass. Syzygy: PROVABLY OPTIMAL via retrograde BFS from terminal. **Syzygy is the strongest precedent: provably-sound inert oracle, billion-scale, O(1) match.**

**Substrate applicability.** STRONGEST in spirit (M5 Syzygy from Sub-Agent 4, P=0.65): a brute-force inert artifact built as a curiosity became a sound terminal oracle inside neural search. Substrate analog: the 19,651 inert atoms, properly indexed by typed signature, become a sound look-up resource for gap-closure IF the L6-PROOF + 4-gate plays the retrograde-soundness role. Wikidata is closer in shape to AlphaCode's GitHub (heterogeneous, schema-loose, soundness via downstream filter) than to Syzygy (closed-world, provably exhaustive). So the realistic substrate target is AlphaCode-class (filtered candidates, sample-and-verify) not Syzygy-class (oracle).

## Substrate-product implications

1. **Mechanism is published-precedented at the architectural level**, even though no published system delivers the specific combination (typed-shape match + heterogeneous reservoir + substrate-internal sound check). The substrate's existing 4-gate + L6-PROOF + capability-preservation stack IS the kernel that turns the inert reservoir into a sound gap-fill source. This is the same pattern as premise-selection + ATP kernel, lifted from homogeneous formal libraries to heterogeneous incidental reservoirs.

2. **The 19K + 651 atom reservoir size is in the right regime.** Premise-selection literature operates on Mizar (~50K theorems) and HOL Light (~25K). OEIS is 370K. Reactome is ~2,500 pathways but is dense-typed. The substrate's reservoir is in the premise-selection regime by size, not the OEIS or Syzygy regime.

3. **The carrier-novelty-via-gap-closure-utility argument is structurally sound.** Across all 5 patterns, the corpus item gets its function VIA the gap it fills, not via any intrinsic novelty signal computed on the corpus item alone. Chef Watson's pleasantness/novelty score is computed AT COMBINATION TIME, not at ingredient-cataloguing time. DreamCoder's library-promotion happens AT ANTI-UNIFICATION TIME, not at program-storage time. SME's "reviving inert knowledge" framing (Gentner 2009) is direct precedent for the substrate's claim.

4. **The retrieval mechanism MUST be structural, not embedding-similarity.** Sub-Agent 3's NEGATIVE finding is direct: no published embedding-retrieval system delivers schema-checked shape match. SME-MAC + DreamCoder anti-unification + premise-selection ATP-kernel are the precedents that DO. F6 tests embedding-similarity directly and predicts failure.

5. **Two anchor candidates surface naturally:**
   - **PRIMARY: CELL-RESERVOIR-RETRIEVAL-1.** 10-gap retro-validation (the cheap decisive test). Tests F1-F6 in one cell. Substrate-product implication: validates or refutes the inert-corpus-as-shape-reservoir thesis, gating any large-scale ingest expansion.
   - **SECONDARY: CELL-ANTI-UNIFICATION-PAIRWISE-1.** DreamCoder-style pairwise anti-unification over the 19K reservoir, filtered by 4-gate + L6-PROOF. Tests F4 specifically. Complements the gap-driven retrieval path with a corpus-driven library-promotion path. Approximately the same as substrate's atom-MERGE Phase 2 but staged narrowly.

6. **No need to ingest more before testing.** The 19K + 651 is enough to falsify F2/F4/F5 cheaply. If the retro-validation HARD-FAILs, ingest expansion is gated; if HARD-PASSes, ingest expansion is empirically justified (not faith-based).

## Citations (verified count: 24)

Pattern 1 -- OEIS / SuperSeeker / fingerprint-DB:
- Sloane, "The On-Line Encyclopedia of Integer Sequences," Notices of the AMS 50(8), 2003.
- Sloane, "The OEIS," arXiv:1805.10343, 2018.
- Colton, Bundy, Walsh, "Automatic Invention of Integer Sequences," AAAI 2000.
- Colton, "Automated Theory Formation in Pure Mathematics," Springer 2002.
- Colton, "Computational Discovery in Pure Mathematics," LNAI 4660, 2007.
- Billey & Tenner, "Fingerprint Databases for Theorems," Notices of the AMS 60(8), 2013.

Pattern 2 -- CBR / RAG / SME:
- Aamodt & Plaza, "Case-Based Reasoning: Foundational Issues, Methodological Variations, and System Approaches," AI Communications 7(1), 1994.
- Lewis et al., "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks," NeurIPS 2020 (arXiv:2005.11401).
- Karpukhin et al., "Dense Passage Retrieval for Open-Domain Question Answering," EMNLP 2020.
- Khandelwal et al., "Generalization through Memorization: Nearest Neighbor Language Models," ICLR 2020 (arXiv:1911.00172).
- Falkenhainer, Forbus, Gentner, "The Structure-Mapping Engine: Algorithm and Examples," AI 41, 1989.
- Forbus, Gentner, Law, "MAC/FAC: A Model of Similarity-Based Retrieval," Cognitive Science 19(2), 1995.
- Gentner, Loewenstein, Thompson, Forbus, "Reviving Inert Knowledge: Analogical Abstraction Supports Relational Retrieval of Past Events," Cognitive Science 33(8), 2009.

Pattern 3 -- DreamCoder / babble:
- Ellis et al., "DreamCoder: Bootstrapping Inductive Program Synthesis with Wake-Sleep Library Learning," PLDI 2021 (DOI 10.1145/3453483.3454080).
- Cao et al., "babble: Learning Better Abstractions with E-Graphs and Anti-Unification," arXiv:2212.04596, 2023.

Pattern 4 -- KG-QA / premise selection:
- Yih, Chang, He, Gao, "Semantic Parsing via Staged Query Graph Generation," ACL 2015.
- Sun et al., "Open Domain QA Using Early Fusion of Knowledge Bases and Text (GraftNet)," EMNLP 2018.
- Sun, Bedrax-Weiss, Cohen, "PullNet," EMNLP 2019.
- Urban & Vyskocil, "Theorem Proving in Large Formal Mathematics as an Emerging AI Field," LNAI 7788, 2013.
- Kaliszyk & Urban, "Learning-Assisted Automated Reasoning with Flyspeck," J. Automated Reasoning 53, 2014.
- Irving, Szegedy, Alemi, Een, Chollet, Urban, "DeepMath -- Deep Sequence Models for Premise Selection," NeurIPS 2016.
- Bansal, Loos, Rabe, Szegedy, Wilcox, "HOList: An Environment for Machine Learning of Higher-Order Theorem Proving," ICML 2019.

Pattern 5 -- non-traditional reservoirs:
- Varshney, Pinel, Varshney, Schorgendorfer, Chee, "A Big Data Approach to Computational Creativity (Chef Watson)," IBM J R&D, 2019.
- Ahn, Ahnert, Bagrow, Barabasi, "Flavor Network and the Principles of Food Pairing," Sci Reports 1, 2011.
- Hadjeres, Pachet, Nielsen, "DeepBach: A Steerable Model for Bach Chorales Generation," ICML 2017.
- Hodos et al., "In Silico Methods for Drug Repurposing and Pharmacology," WIREs Sys Biol Med 8, 2016.
- Li et al., "Competition-Level Code Generation with AlphaCode," Science 378, 2022.
- de Man / Syzygy 7-piece tablebases, Lomonosov 2018 (no formal venue; archive notes).
