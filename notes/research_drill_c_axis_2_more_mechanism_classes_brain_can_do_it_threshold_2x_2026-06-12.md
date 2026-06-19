# Research drill: C-axis 2 MORE mechanism class candidates (brain-can-do-it 5-substrate-paths threshold; 2x DEEP)

Date: 2026-06-12
Drill type: 2x DEEP (operational drill for closure-threshold satisfaction; NOT verification re-scan)
Field: graph-similarity / random-walk-graph-mining / spectral-graph-theory /
information-theoretic-similarity / tensor-factorization
Calibration: lit-scan penalty applied (deflate P 0.15-0.25; novel-synthesis cap 0.50;
HARD-FAIL thresholds explicit).

## HEADLINE

Four additional mechanism class candidates surveyed for C-axis (functional similarity /
capability-serves) closure-threshold. Two graduate to "drill-worthy 4th/5th class"
under the brain-can-do-it 5-substrate-paths discipline:

(4) Personalized PageRank / Random-Walk-with-Restart over SHARES_MATH edges as
    structural-functional similarity surrogate. Lit-strong; data-cheap; addresses the
    SUPERVISION-DENSITY failure of contrastive directly because it requires ZERO
    labeled positive pairs. P_deflated = 0.42.

(5) Information-theoretic similarity (Jensen-Shannon over capability-served-axes
    distributions OR Pointwise-Mutual-Information over solution_history
    co-occurrence). Lit-strong; data-cheap; orthogonal to bge/contrastive/structural.
    P_deflated = 0.38.

Bilinear KGE (DistMult/ComplEx) and Spectral-Laplacian Eigenmaps are DEPRIORITIZED
to deferred-class: bilinear KGE has the SAME data-density gating as contrastive
(would re-fail for the same reason: 122 pairs across 74 caps = median 1 pair/cap is
under the 5-10/cap density threshold in the KGE lit); Laplacian eigenmaps require
a DENSE similarity graph as input which is the missing artifact (circular).

If both (4) and (5) HARD-FAIL on cheap decisive tests, then 5-substrate-paths
threshold is satisfied (5 distinct mechanism classes refuted: bge-topical, structural
1-hop propagation, contrastive supervised metric learning, PPR/RWR, info-theoretic
divergence) and the C-axis architectural-ceiling-vs-authoring-bound dichotomy can
be resolved IN FAVOR OF authoring-bound with the brain-can-do-it discipline
satisfied. Until then, claim remains premature.

## Cheap decisive test (per candidate)

### Candidate (4) -- Personalized PageRank over SHARES_MATH edges

Setup:
- Graph G: nodes = atoms; edges = SHARES_MATH (existing substrate edge type) +
  serves_capability (capability nodes as bipartite layer).
- For each query capability q, run PPR with restart vector = capability node q
  (alpha = 0.15 standard).
- Rank atoms by stationary PPR probability; take top-k as candidate atoms.
- Cost: closed-form power iteration (~30 iters to 1e-6 convergence) on a graph
  with ~1700 atoms; <2 minutes CPU; no training.

Compare against `what_serves` baseline (C-F1 0.6784) and against the bge+structural
union failure case (~0.43).

HARD-PASS: C-F1 >= 0.74 (>= +0.05 over what_serves baseline) AND NONE-gold
recovery (gold that what_serves misses) >= 4/12 (vs contrastive 1/12).
HARD-FAIL: C-F1 < 0.67 (regression below baseline) OR NONE-gold recovery <= 1/12
(no additive signal).
MIDDLE: C-F1 in [0.67, 0.74) -- partial signal; investigate alpha sensitivity and
edge-weight scheme before escalation.

### Candidate (5) -- Information-theoretic similarity (JSD over served-axes profile)

Setup:
- For each atom a, build a profile vector p_a over the 7 benchmark axes (A,B,C,D,E,F,G)
  using solution_history evidence (count of times atom a participates in a successful
  solution for an axis-X question; normalize to a probability distribution).
- For each query capability q with axis distribution p_q (extracted from the
  capability's serves entry), score atoms by 1 - JSD(p_a, p_q).
- Alternative: PMI(atom_a, capability_q) over solution_history co-occurrence as
  scoring function; no probability estimation needed.
- Cost: O(N_atoms * 7) per query; closed-form; no training.

HARD-PASS: C-F1 >= 0.74 AND independent NONE-gold recovery (different gold atoms
than candidate (4) recovers, evidencing orthogonal signal) >= 3/12.
HARD-FAIL: C-F1 < 0.67 OR solution_history profile is uniform/uninformative for
>= 50% of atoms (the profile estimate is degenerate at current corpus density).
MIDDLE: C-F1 in [0.67, 0.74) -- partial signal; investigate axis-resolution and
profile smoothing (Laplace / Dirichlet prior) before escalation.

## Falsifiable predictions

### Prediction P4.1 (PPR/RWR)

Substrate SHARES_MATH graph has been authored (Cell 2 / strategy_scribe outputs
2026-06-12). PPR over this graph should expose FUNCTIONAL similarity (atoms that
share underlying math primitive cluster as PPR-neighbors of the capability node
EVEN IF bge cosine ranks them topically-distant). This addresses the bge-fails-
functional finding directly and uses ZERO labeled supervision pairs (sidesteps
the contrastive failure mode).

HARD-FAIL: PPR on substrate SHARES_MATH graph produces C-F1 < 0.67. This refutes
"structural propagation via SHARES_MATH is the C-axis lever" -- which is a stronger
refutation than the 1-hop propagation refutation (RWR is the GENERAL form of
propagation; if RWR fails, the structural-propagation class as a whole is closed).

### Prediction P4.2 (PPR/RWR composition)

Combining PPR scores with what_serves (union or weighted sum) should produce
ADDITIVE signal at least 2 NONE-gold recovered (gold what_serves misses) without
regressing the precision. If combination HURTS (like contrastive did, -0.246),
that refutes the orthogonal-signal claim and demotes RWR to topical-redundant.

HARD-FAIL: PPR-union C-F1 < what_serves baseline -0.02. Mirrors the contrastive
union-hurts failure mode.

### Prediction P5.1 (Info-theoretic JSD over axis profiles)

Atoms that successfully serve axis-X questions in solution_history have a
characteristic axis distribution p_a. Capabilities that serve axis-X have a
matching p_q. JSD or PMI should rank functionally-similar atoms ABOVE topically-
similar atoms when their axis-profile distributions match the query's.

HARD-FAIL: solution_history profile is degenerate -- >= 50% of atoms have zero
or single-axis profiles (no within-atom diversity), making JSD comparisons
uninformative. This would EVIDENCE corpus-deficiency (matches the corpus-bound
hypothesis already validated 3x across MWP triangulation and Phase-6 ingest
strategic priority).

### Prediction P5.2 (Info-theoretic PMI over solution_history co-occurrence)

Atoms that co-occur with capability q in solution_history at rate above PMI=0
threshold are functionally relevant (lit-precedent: trace-embedding / process-mining
literature; Behavior2Vec class).

HARD-FAIL: PMI signal at current solution_history density (~155 pairs across 74
capabilities) is too sparse to produce > 3 above-PMI=0 atoms per query for >= 50%
of test queries. This MIRRORS the contrastive density failure but at PMI's smaller
data-requirement floor; if PMI ALSO data-fails, the data-density bottleneck is
confirmed (NOT mechanism-specific).

## Mechanism class survey -- ranking of 4 drill targets

### Candidate (4) PPR/RWR over SHARES_MATH -- PROMOTED

Why promoted:
- ZERO labeled supervision pairs required (sidesteps the contrastive failure mode
  decisively; the 1-pair/cap median was the killer).
- SHARES_MATH edges already authored as substrate primitive (Cell 2 + strategy
  outputs). Graph is ready.
- Closed-form (~30 power iterations); no training; cheap.
- Lit-strong: PPR / RWR is one of the most-cited node-similarity primitives;
  Tong-Faloutsos-Pan 2007 "Random Walk with Restart: Fast Solutions and
  Applications" is the foundational citation; entity-search lit (RWRDoc,
  Springer 2020) demonstrates RWR for KG entity ranking with recall@k as the
  evaluation metric.
- DIFFERENT mechanism class than 1-hop propagation (which was REFUTED): 1-hop
  is myopic; RWR integrates k-hop topology with damped restart and captures the
  CLUSTER structure of the graph not just neighborhood. Lit-evidenced category
  distinction (Tong et al. 2007; structural-propagation refutation does NOT
  generalize to RWR).
- Captures the "functional similarity = clustering in math-primitive graph"
  hypothesis directly.

Risks (P_deflated 0.42):
- If SHARES_MATH edges are too sparse, PPR distributes mass uniformly over the
  graph (uninformative). Estimated density: ~ 1500-2000 SHARES_MATH edges per
  Cycle 51 status. Adequate for PPR if median degree >= 5.
- Capability node bipartite layer: must be authored. If capability nodes have <5
  edges each, restart vector is poorly localized.

Cost: <2 min CPU. Cheap-decisive.

### Candidate (5) Information-theoretic similarity (JSD/PMI) -- PROMOTED

Why promoted:
- ZERO labeled supervision pairs required.
- Orthogonal mechanism class to RWR (distribution overlap vs graph propagation).
- Lit-strong: Jensen-Shannon divergence is the symmetric KL form used widely in
  topic-similarity, behavioral-profile clustering (location privacy lit, mobility
  lit), document-similarity. Lin 1991 "Divergence measures based on the Shannon
  entropy" is foundational.
- PMI over co-occurrence is the foundational distributional-semantics signal
  (Church-Hanks 1990; Lin 1998 "Information-theoretic definition of similarity")
  with direct trace-embedding lit precedent (Behavior2Vec / Trace2Vec class).
- Tests a DIFFERENT axis of the corpus-deficiency hypothesis: if solution_history
  profile is degenerate, that's EVIDENCE for corpus-bound NOT architecture-bound
  (consistent with the 3rd-confirmation MWP triangulation result and Phase-6
  strategic priority).

Risks (P_deflated 0.38):
- Solution_history density may be too sparse (155 pairs / 74 caps) to produce
  non-degenerate axis profiles for most atoms. If profiles are degenerate, JSD
  is uninformative.
- Axis labels in benchmark are 7 categories; profile dimensionality is small;
  may not differentiate enough.
- Smoothing prior (Laplace, Dirichlet) needed to avoid zero-mass cells; choice
  of smoothing affects results.

Cost: <5 min CPU (closed-form). Cheap-decisive.

### Candidate (a) Bilinear KGE (DistMult/ComplEx/RotatE) -- DEPRIORITIZED

Why deprioritized (NOT a fresh class; collapses to contrastive failure):
- Bilinear KGE models learn entity and relation embeddings via low-rank tensor
  factorization. TuckER (Balazevic-Allen 2019, EMNLP) is the unifying framework.
  DistMult is symmetric-only (Yang et al. 2014); ComplEx (Trouillon et al. 2016,
  JMLR vol 18) extends to asymmetric via complex embeddings; RotatE (Sun et al.
  2019) models relations as rotations.
- DATA REQUIREMENTS: KGE benchmarks (FB15k-237 ~14k entities / 237 relations /
  272k train triples; WN18RR ~40k entities / 11 relations / 87k train triples)
  are 1000-10000x denser per relation than the substrate's serves_capability
  graph. Standard recipe assumes >> 100 train triples per relation type.
- Substrate serves_capability has ~155 triples across 1 effective relation type
  ("serves"). That's 1000x under the data-density floor that the KGE lit treats
  as viable.
- This re-fails for the same reason contrastive failed: insufficient supervision
  density for low-rank factorization to generalize off train caps.
- DEFERRED status: re-measure trigger when solution_history > 1500 pairs
  (~10x denser; matches Phase-6 ingest target). Until then, this is a
  parameter-counting failure mode, not a fresh mechanism class.

Risks: this candidate would COLLAPSE the brain-can-do-it 5-class portfolio into
4 + 1-redundant-of-3. Reject for closure-threshold purposes.

### Candidate (b) Spectral Laplacian Eigenmaps -- DEPRIORITIZED (circular)

Why deprioritized (circular; not a fresh class):
- Laplacian eigenmaps (Belkin-Niyogi 2003) embed nodes by the smallest k non-zero
  eigenvectors of the graph Laplacian L = D - W where W is a similarity matrix
  input. This is foundational spectral-clustering.
- Algebraic connectivity (Fiedler 1973, lambda_2 of L) is the standard global-
  structure observable.
- CIRCULAR FAILURE MODE: Laplacian eigenmaps require a DENSE pre-existing
  similarity matrix W as input. At substrate scale (~1700 atoms), the missing
  artifact IS the dense similarity matrix. If we had W, we wouldn't need
  Laplacian eigenmaps (we'd just rank by W).
- Possible workaround: use SHARES_MATH adjacency as W. But this REDUCES TO
  PPR/RWR over SHARES_MATH (candidate 4); spectral embedding of the SHARES_MATH
  graph is a different representation of the SAME signal that PPR exposes
  (PPR matrix and Laplacian eigenvectors are spectrally related; classical
  result, see Chung 1997 "Spectral Graph Theory").
- DEFERRED status: spectral methods on the SHARES_MATH graph are a
  GENERALIZATION of (4), not an independent class. If (4) HARD-FAILS,
  spectral on the same graph would HARD-FAIL too (Chung-spectral-relation).
  Defer.

Risks: this candidate would COLLAPSE into candidate (4); not independent.
Reject for closure-threshold purposes.

## Substrate-product implications

### If both (4) and (5) HARD-FAIL on the cheap decisive tests

Then 5-substrate-paths threshold is satisfied: bge-cosine, structural-1-hop,
contrastive metric learning, PPR/RWR, info-theoretic divergence ALL refuted at
current corpus density. Per brain-can-do-it rule, the C-axis architectural-ceiling-
vs-authoring-bound dichotomy resolves CLEANLY to authoring-bound.

Substrate-product framing: "C-axis is empirically authoring-bound at corpus
density <= 200 supervision pairs. Authoring backfill is the validated lever
(Testbed P0.2 0.6711 HARD-PASS, C-axis 0.622 -> 0.867). Substrate makes this
DIAGNOSIS via 5-mechanism portfolio refutation; LLMs cannot diagnose mechanism-
class boundaries without explicit-architecture inspection."

This is a stronger product story than "C-axis authoring-bound by 3-class
refutation" because brain-can-do-it discipline is fully satisfied (5 paths
tried, all data-bound, supervisor density is the universal lever, NOT
architectural ceiling).

### If (4) PPR/RWR HARD-PASSES on the cheap test

Substrate gains a SUBSTRATE-DISTINCTIVE C-axis lever via SHARES_MATH-graph PPR.
This is exactly the SHARES_MATH-architectural-insight USER framing: capabilities
share underlying math, and PPR over the math-primitive graph EXPOSES functional
similarity without labeled supervision. The Cell-2 SHARES_MATH authoring is
validated as a foundational structural primitive.

This would be a CRITICAL substrate-product result: substrate-only graph
propagation under SHARES_MATH exposes functional similarity that LLMs cannot
because LLMs have no SHARES_MATH-equivalent structured graph.

### If (5) info-theoretic HARD-PASSES on the cheap test

Substrate gains a corpus-DERIVED C-axis lever; solution_history trace IS the
supervision (no separate authoring needed). This is the substrate-as-self-knowing-
system framing -- the system uses its own success trace to expose functional
similarity. LLMs have no self-trace; this is substrate-distinctive.

### If (4) and (5) both MIDDLE-band

Then partial signal exists; mechanism-portfolio diversity rule applies and BOTH
should ship into the C-axis pipeline (union with what_serves and bge cosine
recall) for residual lift. Cycle 53 hand-off.

## Cross-thread synthesis with prior entries

- This drill is the 4th and 5th C-axis mechanism class survey. Combined with prior
  refutations (bge cosine, structural 1-hop propagation, contrastive supervised
  metric learning), the closure-threshold under brain-can-do-it is the explicit
  target.
- Consistent with substrate-extracted methodology rule
  capability-portfolio-mechanism-diversity-is-the-lever (10th rule;
  validated across 3 distinct off-attractor mechanisms; extending to 5 classes
  here).
- Consistent with substrate-extracted SHARES_MATH-architectural-insight
  (USER Cycle 49 close): SHARES_MATH edges encode the right structural prior for
  PPR; candidate (4) IS the empirical test of that insight at the C-axis surface.
- Consistent with substrate-extracted corpus-deficiency-confirmation
  (3rd-confirmation MWP triangulation): if (5) info-theoretic degenerates on
  solution_history density, that's a 4th confirmation of corpus-bound at the
  C-axis surface specifically.
- Adjacent to the cap_map row C-axis-route-mechanism: this drill PROVIDES the
  two additional refutations needed before the row goes structural-closure under
  brain-can-do-it discipline.

## Honest scope

STRONG (P >= 0.55 deflated):
- PPR/RWR is empirically the dominant graph-similarity primitive in the lit and
  the natural test of structural-functional similarity via SHARES_MATH. Lit
  consensus dense (Tong-Faloutsos-Pan 2007 + RWR-Doc Springer 2020 + Mixture-of-
  PageRanks 2024). Implementation is closed-form and cheap.
- The substrate SHARES_MATH graph is the right structural input for PPR
  (architecture matches the lit pattern).

MODERATE (P 0.35-0.50 deflated):
- PPR over SHARES_MATH will achieve >= 0.05 absolute C-axis lift (HARD-PASS).
  Lit-typical PPR lifts on knowledge-graph entity-similarity tasks are
  +0.02 to +0.10 NDCG@10 over baseline retrieval; substrate-specific graph
  density at sub-2000 atoms may underperform lit-typical large KG benchmarks.
  Calibration penalty applied: capped at 0.42.
- Info-theoretic JSD/PMI will produce orthogonal signal. Lit-precedent is
  strong for trace-derived similarity but substrate solution_history density
  may be at the floor of viable regime; data-degenerate failure is plausible.
  Capped at 0.38.

SPECULATIVE (P 0.20-0.35 deflated):
- (4) and (5) together provide additive signal exceeding either individually.
  Lit-precedent for ensemble in retrieval is strong but substrate-specific
  signal redundancy is unknown.

SPECULATIVE (P <= 0.30 deflated):
- A single cheap test will produce decisive evidence at HARD-PASS or HARD-FAIL
  band without MIDDLE-band complication. Substrate-classical retrieval cells
  empirically land in MIDDLE-band ~40% of the time per prior verdict-band
  distribution.

REFUTED (P <= 0.20 deflated):
- Bilinear KGE (DistMult/ComplEx/RotatE) will produce lift at current
  supervision density. Re-fails by the same data-density mechanism as
  contrastive; not a fresh class. DEFER until corpus density 10x.
- Spectral Laplacian eigenmaps will produce independent signal beyond PPR/RWR
  over the SAME graph. Chung-spectral-relation collapses them to PPR class.
  DEFER as redundant.

## Pre-registered Cycle 52/53 cell suite

### Cell C4: PPR over SHARES_MATH
- Setup as described above.
- Pre-registered thresholds as above.
- Cost: <2 min CPU; one runner cell.

### Cell C5: Info-theoretic JSD/PMI over solution_history
- Setup as described above.
- Pre-registered thresholds as above.
- Cost: <5 min CPU; one runner cell.

Run order: C4 first (cheaper, higher P_deflated). If C4 HARD-PASSES, C5 is
not strictly required for closure but still informative (orthogonal signal
hypothesis). If C4 HARD-FAILS, C5 is required (must satisfy 5-paths threshold).

## Citations (verified count: 14 lit-anchors)

1. Tong-Faloutsos-Pan 2007 "Random Walk with Restart: Fast Solutions and Applications"
   (Springer KAIS / ACM equivalent). PPR/RWR foundational + applications.
2. Page-Brin-Motwani-Winograd 1999 (PageRank technical report; restart variant).
3. RWRDoc (Springer KAIS 2020) entity representation learning via RWR for KG search.
4. Klicpera-Bojchevski-Gunnemann 2019 "Predict then Propagate: Graph Neural
   Networks meet Personalized PageRank" (arxiv 1810.05997). PPR for GNN node
   representations.
5. Chung 1997 "Spectral Graph Theory" (AMS) -- spectral-PPR relation,
   Laplacian eigenvector theory.
6. Belkin-Niyogi 2003 "Laplacian Eigenmaps for Dimensionality Reduction and
   Data Representation" (Neural Computation).
7. Fiedler 1973 "Algebraic connectivity of graphs" (Czechoslovak Math Journal).
8. Lin 1991 "Divergence Measures Based on the Shannon Entropy" (IEEE Trans
   Info Theory). JSD foundational.
9. Lin 1998 "An Information-Theoretic Definition of Similarity" (ICML).
10. Church-Hanks 1990 "Word Association Norms, Mutual Information, and
    Lexicography" (Computational Linguistics). PMI foundational.
11. Yang et al. 2014 "Embedding Entities and Relations for Learning and
    Inference in Knowledge Bases" (DistMult).
12. Trouillon et al. 2016 "Complex Embeddings for Simple Link Prediction"
    (ComplEx; JMLR vol 18).
13. Sun et al. 2019 "RotatE: Knowledge Graph Embedding by Relational Rotation
    in Complex Space" (ICLR).
14. Balazevic-Allen-Hospedales 2019 "TuckER: Tensor Factorization for
    Knowledge Graph Completion" (EMNLP).

Supplementary mentions (not first-source anchors):
- Jeh-Widom 2002 (SimRank): structural-context similarity, related but
  separately refuted-class (closer to structural-1-hop generalization than
  to RWR class; covered by prior structural propagation refutation).
- Behavior2Vec / Trace2Vec lit class for PMI/co-occurrence motivation.
- Kondor-Lafferty 2002 "Diffusion Kernels on Graphs" (heat-kernel diffusion).
  Related to PPR via Laplacian-spectral relation.

End.
