# Research Drill: Semantic A-axis Beyond bge Cosine (2x DEEP)
Date: 2026-06-12
Scope: Lit-scan + cross-domain probe for retrieval mechanisms that could push
A-axis (content retrieval) from bge-large top_k=8 ceiling 0.369 toward 0.50+.
Constraints: substrate-implementable on FHRR + cleanup + Tier-A NL primitives;
no LLM-as-judge; ASCII only; generic literature queries only.

Lit-scan calibration: deflate raw lit P estimates 0.15-0.25; cap novel-synthesis
P at 0.50. Substrate-extracted rules are PRIOR not ORACLE (memory rule).

================================================================================
CANDIDATE 1: Multi-field multi-vector atom embeddings + RRF fusion
================================================================================
1. MECHANISM: Encode each substrate atom as N field-specific vectors
   (description, aliases, serves_capability, partition_path, id_token_decomp).
   Run query against each field index; fuse via Reciprocal Rank Fusion (k=60).
2. DISTINCTION: bge cosine uses ONE vector per atom (description only).
   Multi-field exposes structured atom metadata as parallel retrieval signal.
   RRF combines RANK orderings (score-invariant); orthogonal to single-vector
   cosine since different fields surface different relevant atoms (Q35 Lyapunov
   missed because "stability/convergence/fixed-point" live in serves_capability
   not description). Signal source = ATOM STRUCTURE, not text similarity alone.
3. LIT ANCHORS:
   - Cormack, Clarke, Buttcher SIGIR 2009 "Reciprocal Rank Fusion outperforms
     Condorcet and Individual Rank Learning Methods" (k=60 default).
   - Findings-ACL 2025 "Rank Fusion Framework for Enhanced Sparse Retrieval"
     (multi-signal RRF beats single dense on BEIR-class benchmarks).
4. SUBSTRATE SKETCH: For each atom A, build {v_desc, v_alias, v_caps, v_path}
   via existing bge encoder calls on each field string. At query time:
   rank_i = bge_topk(query, field_i, k=20) for i in 4 fields. Final score:
   sum_i 1/(60 + rank_i(atom)). Pure numpy fusion, no new model. ~80 lines.
5. BRAIN ANALOGUE: Hub-and-spoke (Patterson/Lambon Ralph ATL semantic hub) -
   modality-specific spokes (description=visual/verbal, capability=functional,
   path=spatial-categorical) converge at hub for cued recall. RRF is the
   convergence-zone integrator across spoke channels.
6. COST: CHEAP. 4x bge encode cost (one-time, atoms only); query cost 4x bge
   forward + numpy fusion. No new training. Reuses existing bge model.
7. ESTIMATED LIFT: +0.06 to +0.10 over 0.369 -> 0.43-0.47. Field expansion
   directly addresses Q35-class diagnostics where signal lives in non-desc field.
8. P_deflated = 0.55. Lit support strong (RRF is SOTA hybrid default since 2009);
   substrate fit excellent; risk = field redundancy with description.

================================================================================
CANDIDATE 2: Cleanup-driven HRR semantic retrieval (substrate-native)
================================================================================
1. MECHANISM: Encode query as superposition of unbound atom hypervectors via
   bge_to_hrr projector (Tier-A primitive). Apply cleanup against atom codebook
   in HRR space; return top-k cleanup-similarity neighbors. Cleanup uses
   FHRR phase-preserving similarity, not raw cosine.
2. DISTINCTION: bge cosine = Euclidean/cosine in 1024-dim continuous bge space.
   Cleanup-driven HRR retrieval = phase-coherent similarity in FHRR space with
   inherent regularization (codebook is the substrate's OWN organized memory).
   Signal source = SUBSTRATE-LEARNED structure, not pretrained encoder geometry.
   Per memory "substrate-classical NLP outperforms phasor" caveat - but here
   HRR is downstream of bge not replacing it.
3. LIT ANCHORS:
   - Plate 2003 Holographic Reduced Representations (foundational cleanup).
   - Frady-Sommer 2018 Neural Computation "Robust computation with rhythmic
     spike patterns" (FHRR cleanup capacity bounds).
4. SUBSTRATE SKETCH: query_bge -> projector W -> q_hrr; cleanup(q_hrr, codebook)
   returns ranked atoms. Reuse existing fhrr_cleanup primitive (already Tier-A).
   ~40 lines wiring. Optional: bundle query into multi-atom superposition before
   cleanup to surface CONJUNCTIVE matches.
5. BRAIN ANALOGUE: Hippocampal pattern completion (CA3 attractor cleanup) on
   cortically-presented query cue. Cued recall via attractor convergence.
6. COST: MEDIUM. Requires bge->HRR projector training (one-time, ~1hr CPU on
   remote desktop). Query cost: 1 bge forward + 1 cleanup pass (~10ms).
7. ESTIMATED LIFT: +0.02 to +0.06. Risk = projector loses bge fidelity; codebook
   may not exceed bge cosine on description-text-dominated gold-set. Strongest
   on Q with cross-partition gold where HRR composition helps.
8. P_deflated = 0.32. Substrate-novel but high uncertainty on lift magnitude;
   lit gives capacity bounds not retrieval-quality predictions for this regime.

================================================================================
CANDIDATE 3: SPLADE-style learned sparse expansion on atom descriptions
================================================================================
1. MECHANISM: Generate expanded sparse term vector per atom via MLM-head
   expansion (SPLADE). Each atom -> sparse vocab-vector with weighted expansion
   terms. Query similarly expanded. Dot-product over sparse vectors via
   inverted index.
2. DISTINCTION: bge cosine = dense semantic; keyword AND-match = lexical surface.
   SPLADE = LEARNED LEXICAL EXPANSION - bridges vocabulary gap (Q35
   stability/convergence/fixed-point) WITHIN lexical space, interpretable per
   term. Signal source = MLM expansion vocabulary.
3. LIT ANCHORS:
   - Formal, Lassance, Piwowarski, Clinchant SIGIR 2021 "SPLADE: Sparse Lexical
     and Expansion Model for First Stage Ranking".
   - SPLADE v2 (arXiv 2109.10086) - improved expansion + sparse regularization.
4. SUBSTRATE SKETCH: Use existing distil-bert-class MLM (cheap CPU) to expand
   each atom description into top-200 weighted tokens with log-saturation. Build
   inverted index (substrate already has lexical infrastructure). Query expand
   similarly; dot-product. ~200 lines + ~6hr CPU offline expansion.
5. BRAIN ANALOGUE: Spreading activation (Collins-Loftus 1975) in lexical
   semantic network; ATL hub feeds back to lexical spokes for expansion.
6. COST: MEDIUM-HEAVY. Requires MLM model + offline expansion of 1731 atoms.
   Query latency comparable to bge but new infra.
7. ESTIMATED LIFT: +0.03 to +0.08. Strong on vocabulary-gap queries; weaker
   where gold-set requires cross-partition composition.
8. P_deflated = 0.40. Lit strong, substrate fit medium (parallel infra to bge).

================================================================================
CANDIDATE 4: Graph-propagation retrieval over substrate DEPENDS_ON edges
================================================================================
1. MECHANISM: Initial bge top-k seed atoms; expand via k-hop graph traversal on
   substrate's 1793 DEPENDS_ON / serves_capability / partition edges; rerank by
   propagated relevance (Personalized PageRank or spreading activation).
2. DISTINCTION: bge cosine = TEXT similarity; graph propagation = STRUCTURAL
   neighborhood. Signal source = substrate's own relational graph (substrate-
   self-extending engine memory). Recovers gold atoms that share NO text with
   query but are 1-2 hops from seed (Q05 quantum entanglement gold likely
   includes binding mechanisms 2 hops downstream).
3. LIT ANCHORS:
   - arXiv 2512.15922 "Spreading Activation for Document Retrieval in KG-RAG".
   - arXiv 2410.13765 "Knowledge-Aware Query Expansion with LLMs for Textual
     and Relational Retrieval" (graph-neighbor query expansion).
4. SUBSTRATE SKETCH: bge top-15 seed; run 2-hop BFS over substrate edge index;
   score by sum_{seed s} alpha^{hop(s,a)} * cosine(query, s). Rerank union.
   Uses existing substrate graph; ~120 lines pure numpy.
5. BRAIN ANALOGUE: Hippocampal-cortical replay propagation; sharp-wave ripple
   coordinated semantic network activation (biorxiv 2024.04.10.588795).
6. COST: CHEAP-MEDIUM. Graph already exists. BFS over 1731 nodes / 1793 edges
   is sub-ms. Edge weight tuning is the main effort.
7. ESTIMATED LIFT: +0.05 to +0.09. Directly exploits substrate-self-extending
   structural advantage; matches "structural cognition" positioning. Risk =
   over-propagation pulling in low-precision neighbors.
8. P_deflated = 0.50. Lit anchor strong (KG-RAG spreading activation 2025);
   substrate-product alignment EXCELLENT (uses Gap-1 serves_capability + Phase-1
   DEPENDS_ON edges as discriminating signal).

================================================================================
CANDIDATE 5: Cross-encoder rerank with substrate structural features
================================================================================
1. MECHANISM: bge top_k=30 candidates; rerank via lightweight cross-encoder
   that consumes (query, atom_description, atom_partition, atom_serves_caps,
   atom_alias_list) as concatenated input.
2. DISTINCTION: bge bi-encoder = independent query/atom encoding; cross-encoder
   = JOINT attention over query-atom pair with structural fields injected.
   Signal source = full attention interaction + substrate structural priors.
3. LIT ANCHORS:
   - Nogueira, Cho 2019 "Passage Re-ranking with BERT" (foundational).
   - Thakur et al BEIR 2021 (cross-encoder gains persist out-of-domain).
4. SUBSTRATE SKETCH: ms-marco-MiniLM-L-6-v2 (22M params, CPU-friendly) as
   reranker; feature concat at input. ~150 lines + ~2hr offline calibration.
5. BRAIN ANALOGUE: Prefrontal top-down attention re-weighting hippocampal
   recall candidates (discriminative-weighting universal lever per memory).
6. COST: MEDIUM. Pretrained reranker available; no training needed for v1.
   Query latency +50-100ms for top-30 rerank.
7. ESTIMATED LIFT: +0.04 to +0.08. Typical BEIR reranking lifts are large but
   domain-shift to substrate atom format may reduce gain; per memory
   "aux-features shrink with data" - substrate corpus is SMALL, favors rerank.
8. P_deflated = 0.38. Lit strong; substrate fit medium (cross-encoder is
   external pretrained, not substrate-native - violates spirit of source #5
   methodology rule somewhat).

================================================================================
RANKING (P_deflated)
================================================================================
1. C1 Multi-field RRF             P=0.55  CHEAP   lift +0.06-0.10
2. C4 Graph propagation           P=0.50  CHEAP-MED lift +0.05-0.09
3. C3 SPLADE expansion            P=0.40  MED-HVY lift +0.03-0.08
4. C5 Cross-encoder rerank        P=0.38  MEDIUM  lift +0.04-0.08
5. C2 Cleanup-driven HRR          P=0.32  MEDIUM  lift +0.02-0.06

================================================================================
RECOMMENDATION (cheapest x highest lift)
================================================================================
TOP-2 for Research authoring + Exp-Dev cell design:

(A) CANDIDATE 1 (Multi-field RRF) - PRIMARY. Cheapest path; reuses bge; directly
    exposes substrate's structured atom metadata (aliases, serves_capability,
    partition_path) that bge currently IGNORES. Implementable in ~80 lines
    numpy + 4x bge re-encode (one-time). Highest P_deflated. Brain analogue
    matches substrate's hub-and-spoke positioning. Pre-register: expect
    bge 0.369 -> RRF 0.43+/-0.04 on Gap 7 v1.1.

(B) CANDIDATE 4 (Graph propagation) - SECONDARY. Substrate-product native;
    exploits Phase-1 4.3x edge growth (1793 DEPENDS_ON) as retrieval signal
    LLMs cannot match. Composable with C1 (graph-expand the RRF union).
    Pre-register: C1+C4 stack 0.369 -> 0.47+/-0.05.

Combine (A)+(B): expected stacked lift +0.08 to +0.13 -> A-axis ~0.45-0.50,
which puts HP_v1 0.70 macro within 2 more axis lifts (B normalizer + intent
router per memory Gap 7 baseline note).

Methodology guards applied:
- Lit P deflated 0.15-0.25 (raw C1 RRF lit P ~0.75 -> deflated 0.55).
- Novel-synthesis cap 0.50 honored (C2/C4 substrate-native held at <=0.50).
- Per substrate-extracted-rules-are-PRIOR-not-ORACLE: lift estimates are
  directional, not magnitude oracle; A2+A3 composite calibration applies.
- Per brain-can-do-it: all 5 candidates have brain analogues (no
  drill-defeatism on substrate-implementability).
- No project numerics or cycle numbers in web queries (verified).

Source URLs (lit anchors):
- SIGIR 2009 RRF: dl.acm.org via researchgate Reciprocal Rank Fusion
- Findings-ACL 2025: aclanthology.org/2025.findings-acl.9.pdf
- SPLADE SIGIR 2021: arxiv.org/abs/2107.05720
- SPLADE v2: arxiv.org/abs/2109.10086
- ColBERTv2: arxiv.org/abs/2112.01488
- HyDE / PRF for dense: arxiv.org/abs/2305.07477
- KG spreading activation RAG: arxiv.org/abs/2512.15922
- KG-aware query expansion: arxiv.org/abs/2410.13765
- ATL semantic hub: pmc.ncbi.nlm.nih.gov/articles/PMC6838667/
- Hippocampal ripples semantic: biorxiv.org/content/10.1101/2024.04.10.588795
