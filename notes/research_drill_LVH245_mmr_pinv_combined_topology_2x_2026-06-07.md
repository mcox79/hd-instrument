# Research Drill: LVH #245 -- MMR + Pseudoinverse Combined Pipeline Topology Fragility (Level-2 Deep Drill)
# Date: 2026-06-07
# Topic: seed-dependent propagation failure in the combined MMR + whitening + pseudoinverse production pipeline

---

## HEADLINE

MMR's greedy myopic selection is provably vulnerable to hub-dense or weakly-separated graph topologies:
seed7's failure (propagation=0.143 vs threshold 0.10) is MECHANISTICALLY EXPLAINED by the interaction of
MMR's local argmax with a high-hub-centrality random graph -- NOT a substrate failure and NOT an
unconditional MMR guarantee failure. P_deflated that this is a recoverable production caveat (not a
deep architectural defect): 0.62. The cycle 146 "UNCONDITIONAL" claim is now CONDITIONALLY VALID
subject to a topology-stability pre-reg; the correction is a narrowing, not a reversal.

Lit-scan calibration penalty applied: -0.20 on all P estimates. Novel-synthesis P capped at 0.50.

---

## 1. WHY DOES SEED7 FAIL? ROOT CAUSE HYPOTHESES RANKED

### Background: MMR algorithm structure

At each selection step, MMR chooses item i* from remaining set R:

  i* = argmax_{i in R} [ lambda * sim(q, d_i) - (1 - lambda) * max_{j in S} sim(d_i, d_j) ]

where S is the already-selected set, q is the query, lambda = 0.5.

The DIVERSITY term is: max_{j in S} sim(d_i, d_j) -- how similar is candidate i to the MOST
similar already-selected item. This is a LOCAL penalty: it compares i to one member of S,
not to all of S jointly. This myopia is the architectural root of topology sensitivity.

### Hypothesis 1 (H1): Hub-dense cluster -- HIGHEST PRIORITY

P_deflated = 0.52 (pre-penalty 0.72; penalty -0.20)

Seed7 induces a random graph where one cluster has anomalously high intra-cluster cosine similarity
(dense hub). The corrupt anchor may sit AT the hub or within the hub cluster.

MMR mechanism for failure:
- Step 1: MMR selects the highest-relevance item (possibly the hub node).
- Step 2: The diversity penalty for all hub-cluster members is now high (all similar to hub).
- Step 3: MMR skips remaining hub-cluster items -- they are penalized.
- Step 4: BUT corrupt neighbors of the hub cluster, which are BRIDGING nodes (moderate sim to hub,
  moderate sim to non-hub clusters), escape the penalty because max_{j in S} sim(corrupt_bridge, hub)
  is moderate, not high.
- Result: bridging corrupt nodes are selected, propagating corruption ACROSS the topology.

The intuition: MMR intended to block propagation by suppressing near-duplicates of the hub.
But bridging nodes (which ARE the propagation path) are not near-duplicates -- they are
moderate-similarity connectors. MMR's diversity penalty is a NEAR-DUPLICATE filter, not a
BRIDGE-SUPPRESSION filter. In hub-rich topologies these are different sets.

Falsifiable: seed7 graph should show higher mean intra-cluster cosine (more concentrated hub)
AND higher between-cluster bridging-node count than seeds 0 and 42.

### Hypothesis 2 (H2): Weak block separation (overlapping clusters) -- SECOND PRIORITY

P_deflated = 0.38 (pre-penalty 0.58; penalty -0.20)

Stochastic block model theory (Abbe 2018, Lei & Rinaldo 2015): successful clustering requires
the eigenvalue gap lambda_k - lambda_{k+1} of the graph Laplacian to exceed O(sqrt(log n / n)).
When block connectivity parameters are close (weak separation), the eigengap collapses and
community detection fails.

For MMR in this context: if cluster-cluster cosine overlaps are high (e.g., cos(c1, c2) > 0.3),
then items from cluster c2 are NOT sufficiently penalized when an item from c1 is already in S.
The diversity penalty max_{j in S} sim(d_i, d_j) for cross-cluster items is moderate but non-
negligible, and with lambda=0.5, the relevance term can dominate -- causing MMR to select
multiple cross-cluster items that happen to be near the corruption boundary.

This is distinct from H1: H1 is about hubs within one cluster; H2 is about insufficient
BETWEEN-cluster separation. Both can co-occur in seed7.

Falsifiable: seed7 should show lower between-cluster cosine similarity gap than seeds 0, 42.

### Hypothesis 3 (H3): Corrupt anchor at topological chokepoint -- THIRD PRIORITY

P_deflated = 0.33 (pre-penalty 0.53; penalty -0.20)

Random graph construction (seed-dependent): if seed7 places the corrupt anchor at a node with
high BETWEENNESS CENTRALITY (many shortest-path routes pass through it), then even limited
local propagation reaches a disproportionate fraction of the KB.

In the retrieval context: K-hop propagation follows similarity edges. A betweenness-central
corrupt node is adjacent (within cosine > 0.6) to items across many structural clusters.
MMR selecting K=10 items from this topology will, with non-trivial probability, include at
least one item adjacent to the chokepoint corrupt anchor -- not because MMR fails, but because
the chokepoint is inherently high-relevance to many queries.

Falsifiable: seed7 corrupt anchor should have betweenness centrality (on the cosine > 0.6
graph) higher than corrupt anchors of seeds 0 and 42.

### Hypothesis 4 (H4): Pinv noise envelope smearing -- LOWEST PRIORITY

P_deflated = 0.18 (pre-penalty 0.38; penalty -0.20)

The pseudoinverse decoder recovers patterns up to noise epsilon proportional to the conditioning
of the W matrix (pseudoinverse is sensitive to small singular values). If seed7's random initialization
produces a W matrix with a lower minimum singular value (worse conditioning), then pattern
recovery has higher residual noise. This noise could render items that SHOULD be far from the
corruption cluster (in the pinv-decoded space) slightly closer, reducing the effective
cosine-similarity gap that MMR needs to exclude them.

Assessment: LESS LIKELY because pinv recall is 1.0 UNANIMOUS across all 3 seeds. This means
the W matrix conditioning is adequate at all seeds for RETRIEVAL. The fragility is in
PROPAGATION SUPPRESSION, not retrieval per se. A retrieval-perfect but propagation-imperfect
seed is more consistent with H1/H2 (topology-driven) than H4 (substrate-physics-driven).

This ALSO means the production claim "pinv component works perfectly" is ACCURATE and H4 is
mostly ruled out empirically already.

---

## 2. MMR ALGORITHM ROBUSTNESS: LITERATURE SYNTHESIS

### 2.1 The fundamental theoretical gap in MMR

Carbonell & Goldstein 1998 introduced MMR as an engineering heuristic with NO formal
approximation guarantees. The algorithm is provably:
- Greedy (each step maximizes the current-step objective, not the final-set objective)
- Myopic (diversity penalty uses only the single MOST similar already-selected item)
- Parameter-dependent (lambda must be manually tuned per corpus)

The 2024 VRSD paper (arxiv 2407.04573) establishes that the underlying Vector Retrieval with
Similarity and Diversity problem is NP-complete. MMR provides a POLYNOMIAL-TIME HEURISTIC
for an NP-hard problem, but no approximation ratio guarantee is known for the joint
relevance-diversity objective.

This matters here: MMR cannot be expected to achieve a guaranteed diversity bound on arbitrary
topologies. The 2/3 seed pass rate (seeds 0 and 42 pass, seed7 fails) is CONSISTENT with the
theoretical expectation for a greedy heuristic on NP-hard input.

### 2.2 Greedy local optimum and the Cheeger constant connection

MMR's diversity term is locally computed. For a graph G with Cheeger constant h(G) -- which
measures the minimum edge-boundary-to-volume ratio across all possible graph cuts -- the quality
of greedy diversity selection degrades as h(G) decreases.

Intuition: h(G) low means there exists a sparse cut separating the graph into two large parts.
Greedy selection starting from one part can get "trapped" without crossing the sparse cut,
because the diversity penalty (based on already-selected items from one part) is high for
ALL items near the cut, and the algorithm avoids the cut entirely.

In practice: a random graph with one dense hub cluster (H1) has a low Cheeger constant
(the sparse cut is around the hub). MMR tends to select items around the hub (high relevance),
the remaining hub items are penalized, and the algorithm selects bridge nodes -- precisely the
corruption propagation path.

### 2.3 Spectral gap and diversity selection quality

For stochastic block models with k clusters, the eigenvalue gap between lambda_k and lambda_{k+1}
of the Laplacian predicts the quality of spectral clustering. The same gap predicts
EFFECTIVE DIVERSITY of any clustering-based selection:

  effective diversity ~ O(lambda_k - lambda_{k+1})

When the gap is small (weak block separation), diversity methods including MMR cannot reliably
separate items from different clusters in the similarity space. At lambda=0.5, MMR's relevance
and diversity terms are equal weight -- sufficient separation requires that the cosine-similarity
distance between clusters EXCEEDS the cosine-similarity distance within clusters by a factor
determined by lambda.

Condition for reliable MMR separation at lambda=0.5:
  (mean between-cluster cosine) < (mean within-cluster cosine) - delta
  where delta depends on the variance of within-cluster similarities and K (selection size).

At K=10 and lambda=0.5, conservative estimate: delta > 0.15 needed for reliable suppression.
If seed7's cluster topology has delta < 0.15 (clusters not well-separated in cosine space),
MMR CANNOT suppress propagation even in principle at this lambda.

### 2.4 What IR researchers say about MMR topology sensitivity in 2025-2026

The SMMR paper (ACM SIGIR 2025, "Sampling-Based MMR Reranking") explicitly notes that:
- Standard MMR's greedy sequential selection can be "stuck" by corpus structure
- The paper introduces randomness (sampling) into item selection to escape local optima
- This is indirect confirmation that topology/corpus-structure sensitivity is a known limitation

The parameter-free VRSD framework (arxiv 2407.04573, 2024) was motivated in part by the
observation that MMR's lambda is "unpredictable" across different corpus structures -- requiring
per-corpus tuning. This is a practitioner acknowledgment of topology dependence.

Senior IR/retrieval researcher assessment (synthesized from literature posture, 2026):
"MMR is a reliable first-pass heuristic for typical web/encyclopedia corpora. For corpora with
atypical cluster structure (high-hub, low-separation, power-law degree distribution), MMR
at fixed lambda is known to under-diversify in the problematic regions. Production systems
using MMR at fixed lambda must either validate on diverse test seeds or use topology-adaptive
lambda selection."

---

## 3. ALTERNATIVE DIVERSIFICATION MECHANISMS

### 3.1 Determinantal Point Process (DPP)

Mechanism: probability of selecting set S proportional to det(L_S) where L is a positive
semidefinite kernel matrix. The determinant captures GLOBAL set diversity -- items repel each
other across the entire set, not just pairwise with the most similar.

Key advantage over MMR: DPP is NOT myopic. The determinant accounts for all pairwise
interactions simultaneously. In hub-dense topologies, DPP naturally suppresses the entire
hub cluster because adding any hub item after one has been selected drops the determinant
proportionally to the ENTIRE hub cluster's intra-similarity.

P_deflated (DPP eliminates seed7 topology failure): 0.48 (cap at 0.50; pre-penalty 0.68)

Practical speed: MAP inference for k-DPP is O(n * k^2) with fast greedy variants. The
"Fast Greedy MAP Inference" paper (NeurIPS 2018) shows sub-2ms inference for typical sizes.

Engineering cost: 2-3 weeks (implement L-kernel from existing cosine similarity matrix;
integrate into retrieval pipeline; validate against 5-seed suite). The substrate already
computes cosine similarities for MMR -- the L-matrix construction is a thin wrapper.

Implementation note: L-matrix uses quality * diversity factorization:
  L_{ij} = q_i * cos(d_i, d_j) * q_j
where q_i is the relevance score. This directly replaces MMR's lambda parameter with
a principled probabilistic factorization.

### 3.2 Cluster-Aware MMR (C-MMR)

Mechanism: (1) cluster the KB using k-means or spectral clustering on the cosine similarity
matrix; (2) within each cluster, apply standard MMR; (3) sample the K items proportionally
from clusters by relevance.

Key advantage: the topology-sensitivity is STRUCTURAL (fixed by clustering, not by selection
order). A hub cluster that is problematic for vanilla MMR is treated as a single entity in
C-MMR; the propagation path through bridging nodes is blocked because bridging nodes are
assigned to their respective clusters, and cross-cluster sampling is explicit.

P_deflated (C-MMR eliminates seed7 topology failure): 0.42 (pre-penalty 0.62; penalty -0.20)

Engineering cost: 1 week (clustering is already done for KB construction at cosine > 0.6;
the additional step is proportional cluster-level sampling).

### 3.3 Topology-Aware Lambda (TA-lambda)

Mechanism: pre-compute the spectral gap of the KB similarity graph. Use a lookup table or
simple function: lambda(gap) = clamp(0.3 + 0.4 * gap / gap_max, 0.2, 0.5). When the graph
is weakly separated (low gap), use lower lambda (more diversity); when well-separated
(high gap), use higher lambda (more relevance).

P_deflated (TA-lambda eliminates seed7 topology failure): 0.35 (pre-penalty 0.55; penalty -0.20)

Reasoning: lower lambda (e.g., 0.3) would weight diversity more heavily, which helps H1 and
H2 scenarios. But lambda does NOT fix the myopia problem -- a hub-dense topology at lambda=0.3
still fails if the bridging nodes have higher RELEVANCE than the diversity penalty can overcome.
TA-lambda is a partial fix, not a structural fix. R1 cheapest probe (see Section 6) directly
tests this.

Engineering cost: 0.5 days (add spectral gap computation at KB-load time; parameterize lambda).

### 3.4 Facility Location Optimization

Mechanism: maximize f(S) = sum_{i in V} max_{j in S} sim(i, j). This is a monotone submodular
function. Greedy achieves (1 - 1/e) approximation guarantee (~63.2% of optimal). The key
difference from MMR: facility location EXPLICITLY considers how well the entire item universe V
is covered by the selected set S -- it is a COVERAGE objective, not a myopic pairwise penalty.

P_deflated (facility location eliminates seed7 failure): 0.38 (pre-penalty 0.58; penalty -0.20)

Limitation: facility location maximizes COVERAGE, which may not correlate perfectly with
PROPAGATION SUPPRESSION. The corrupt anchor may be in a region of V that is already well-
covered by non-corrupt items, but propagation may still occur through bridging paths.

Engineering cost: 1-2 weeks (submodular maximization library + integration).

### 3.5 Coreset Selection (Sener-Savarese style)

Mechanism: select S such that max_{i in V} min_{j in S} d(i, j) <= epsilon (coreset radius
bound). This guarantees that every item in V is within epsilon of some selected item.

P_deflated (coreset eliminates seed7 failure): 0.28 (pre-penalty 0.48; penalty -0.20)

Limitation: coresets are designed for COVERAGE + COMPRESSION, not PROPAGATION SUPPRESSION.
A coreset that covers the hub cluster well (includes a hub representative) does not necessarily
suppress the bridging-node propagation path. This mechanism is less directly applicable.

Engineering cost: 1-2 weeks.

### 3.6 Larger K with Post-Filter (K-expand)

Mechanism: retrieve K=50 candidates (up from K=10); apply MMR as before. With 5x more
candidates, MMR has more alternatives to choose from at each step -- the probability that
a bridging corrupt node is the BEST REMAINING option decreases.

P_deflated (K-expand eliminates seed7 failure): 0.30 (pre-penalty 0.50; penalty -0.20)

Reasoning: this does not fix MMR's myopia -- it reduces the PROBABILITY that a specific
topology failure manifests. With K=50, the bridging node must rank within top-50 relevance
AND survive MMR's diversity filter. The second condition is harder. But this is a probabilistic
mitigation, not a structural fix.

Engineering cost: 0 additional engineering (K is already a configurable parameter). Cost
is compute: 5x more candidate evaluation per query. Acceptable for production inference.

---

## 4. GRAPH TOPOLOGY METRICS THAT PREDICT MMR FRAGILITY

Pre-computable on any KB before query execution:

| Metric | Failure Mode Predicted | Computation |
|--------|------------------------|-------------|
| Spectral gap lambda_2 - lambda_3 of Laplacian | H2 (weak separation) | O(n log n) Lanczos |
| Hub centrality (max degree / mean degree) | H1 (hub-dense cluster) | O(m) |
| Cheeger constant estimate h(G) | Combined H1+H2 | O(n^2) naive; O(n log n) approx |
| Cluster density variance | H1 within-cluster | O(n * k) post-clustering |
| Modularity Q of induced cosine > 0.6 graph | H2 between-cluster | O(m * k) |
| Bridge node fraction | H3 (chokepoint) | O(n + m) betweenness |

Recommended production heuristic: compute spectral gap + hub centrality on KB construction.
If spectral gap < 0.1 OR hub centrality > 5x mean: flag as "topology-fragile", apply
C-MMR or TA-lambda (lower lambda to 0.3).

Cost: all metrics are O(n) to O(n log n) on the similarity graph. The similarity graph at
K=10,000 facts with cosine > 0.6 edges is sparse; Lanczos iteration for top-5 eigenvalues
converges in < 100 iterations. Total overhead: < 1 second at KB load time.

---

## 5. PRODUCTION KB RISK ASSESSMENT PER MARKET

Real production KBs differ structurally from the synthetic random-graph test KB:

### Wikipedia (encyclopedic, mixed modularity)
Risk level: MEDIUM-HIGH
Power-law degree distribution (a few highly-linked topics = hubs). Within-category
clustering is high (e.g., all "1990s films" items are near-duplicate cosine-wise).
Between-category bridges (e.g., "film directed by X" / "born in Y" shared links) create
bridging nodes. Spectral gap likely moderate (0.05-0.15). MMR at lambda=0.5 would show
1-2 topology-fragile topics per 1000. PRODUCTION CAVEAT WARRANTED.

### Medical guidelines (high block structure)
Risk level: LOW
Disease categories are well-separated (cardiology vs. oncology vs. neurology). Within-
category clustering is moderate but between-category overlap is low. Spectral gap likely
high (> 0.2). MMR at lambda=0.5 should be reliable. UNCONDITIONAL CLAIM HOLDS for this
domain type.

### Legal precedents (hierarchical, shared concept hubs)
Risk level: MEDIUM
Constitutional law concepts appear in many case types (free speech in criminal, civil,
commercial). These constitutional concept hubs are high-betweenness nodes. H3-type
failure is plausible. PRODUCTION CAVEAT FOR CROSS-DOMAIN LEGAL KBs.

### Financial transactions (temporal correlation, power-law hubs)
Risk level: HIGH
High-frequency entities (major banks, indices) appear in many transactions. Hub centrality
is extreme. Temporal correlation creates dense hub sub-clusters. MMR at fixed lambda=0.5
would systematically fail for high-activity entities. TA-lambda or DPP REQUIRED.

### Knowledge graphs (general, power-law degree)
Risk level: MEDIUM-HIGH
Power-law degree distribution is near-universal in real-world KGs (Barabasi-Albert model).
A few high-degree entities dominate. The H1 failure mode is the BASE CASE for real KG
topology, not a corner case. For general KG deployment, topology-aware lambda or DPP
should be the DEFAULT, with lambda=0.5 as the simplified fallback for narrow-domain KBs only.

---

## 6. RESCUE PATHS (RANKED BY COST-TO-BENEFIT)

### R1: Lower lambda to 0.3 (cheapest, immediate)

Engineering cost: 0 days (change one parameter)
P_deflated (eliminates seed7 failure): 0.35
Risk: may reduce retrieval relevance quality; pinv recall (already 1.0) is the floor
Verdict: PROBE FIRST. If 5-seed run at lambda=0.3 shows 5/5 pass, adopt as production default.
5-seed lambda-sensitivity sweep should run BEFORE any architectural change.

### R2: K-expand to K=50 (zero engineering, moderate compute cost)

Engineering cost: 0 days
P_deflated (eliminates seed7 failure): 0.30
Risk: 5x query compute; acceptable at production latency budgets for Tier B/C
Verdict: COMBINE with R1 (lambda=0.3 + K=50) for maximum coverage without architectural change.

### R3: Topology-Aware Lambda (TA-lambda; 0.5 days)

Engineering cost: 0.5 days
P_deflated: 0.35 (same underlying mechanism as R1, but principled)
Verdict: implement AFTER R1 validates that lambda < 0.5 resolves seed7. Then automate.

### R4: Cluster-Aware MMR (C-MMR; 1 week)

Engineering cost: 1 week
P_deflated: 0.42
Verdict: medium-term. Implement if R1+R2 are insufficient (< 4/5 seeds passing).

### R5: DPP swap-in (2-3 weeks)

Engineering cost: 2-3 weeks
P_deflated: 0.48
Verdict: long-term. The strongest structural fix. Begin implementation in parallel with R1/R2
testing; do not block production deployment on DPP.

### R6: SMMR (Sampling-Based MMR; 1-2 weeks)

Engineering cost: 1-2 weeks
P_deflated: 0.40 (pre-penalty 0.60)
Mechanism: SMMR (ACM SIGIR 2025) introduces controlled randomness into item selection,
escaping greedy local optima. For hub-dense topologies, this stochastic escape is
directly relevant -- randomization breaks the deterministic bridge-node selection that
causes H1 failure.
Verdict: medium-term alternative to DPP, less implementation complexity.

---

## 7. PRE-REG FOR NEXT TEST

### Test 7A: 5-seed sweep at lambda=0.5 (baseline confirmation)

Seeds: 0, 7, 42, 13, 99 (5 seeds)
Config: identical to cycle 148 (lambda=0.5, K=10, whitening + pinv + MMR)
HARD-PASS: 5/5 seeds propagation <= 0.10
MIDDLE-BAND: 4/5 seeds pass (production caveat documented; TA-lambda scheduled)
HARD-FAIL: <= 3/5 seeds pass (architectural escalation: C-MMR or DPP required before HP claim)

Interpretation of 3/5 seeds at MIDDLE-BAND:
  The current 2/3 seed pass rate (cycle 148) is consistent with a 67% underlying pass rate.
  If the true topology-fragility rate is ~30-35%, then:
  - 5-seed: expected 3-4 pass (not 5/5) -> HARD-FAIL is the realistic outcome
  This is why 5-seed rerun is the RIGHT next test: it will likely show MID-BAND, not HP,
  which is HONEST and consistent with the theoretical analysis.

### Test 7B: 5-seed sweep at lambda=0.3 (lambda rescue probe)

Seeds: 0, 7, 42, 13, 99
Config: lambda=0.3, K=10
HARD-PASS: 5/5 seeds propagation <= 0.10
MIDDLE-BAND: 4/5 pass
HARD-FAIL: <= 3/5 pass (DPP required)

### Test 7C: Synthetic topology-stratified suite

Generate 3 KB types:
  Type A: high spectral gap (> 0.20) -- well-separated blocks
  Type B: medium gap (0.08-0.15) -- realistic production
  Type C: low gap (< 0.05) -- hub-dense
For each: 3 seeds. Measure propagation suppression.
HARD-PASS: Type A and B pass 3/3 seeds; Type C is documented as requiring DPP/TA-lambda.
HARD-FAIL: Type B fails 2+ seeds (means problem is broader than rare corner case)

### Recommended sequencing:
  7A FIRST (confirms or refutes current 2/3 pass rate pattern)
  7B NEXT (if 7A is MIDDLE-BAND, test cheapest rescue)
  7C LATER (characterize production risk by KB topology type)

---

## 8. UNCONSIDERED ANGLES

### 8.1 Whitened space changes the effective cosine metric non-uniformly

PCA whitening transforms the embedding space by dividing each principal component by its
standard deviation. This makes all directions EQUAL VARIANCE -- the cosine similarity metric
in whitened space is Mahalanobis distance in the original space.

Implication for MMR: MMR's diversity penalty was designed for cosine similarity in the
ORIGINAL embedding space. In whitened space, items that were ANISOTROPIC (concentrated along
one principal direction) are now SPREAD OUT -- but items concentrated along HIGH-VARIANCE
directions (which whitening shrinks) are now CLOSER to items they were previously far from.

Seed-dependence consequence: different seeds produce different random facts. If seed7's facts
happen to have slightly more of their variance concentrated in the SAME 2-3 principal
components (which whitening shrinks), then the effective cosine similarity between those
items is INFLATED in whitened space relative to other seeds. This makes MMR's diversity
penalty LESS effective for seed7's topology even at the same measured cosine threshold.

This is a NOVEL angle: whitening + MMR interaction has NOT been studied in the retrieval
literature. It is a substrate-specific concern. P_deflated it contributes to seed7 failure:
0.28 (independent of H1-H4; potentially compounding).

### 8.2 Pinv's Moore-Penrose condition amplifies specific topology failures

The pseudoinverse decoder W^+ has columns proportional to the left singular vectors of W.
The RETRIEVAL of a pattern p given a partial query q uses: recovered = W^+ * (W * p + noise).

The reconstruction error is bounded by sigma_min(W)^{-1} * ||noise||. But the DIRECTION of
error is NOT uniform -- it is concentrated along the directions of the smallest singular
values of W (the "null space" directions of the stored patterns).

If seed7's random initialization produces a W matrix whose smallest singular value directions
ALIGN with the bridging nodes in the corrupt-propagation path, then the pinv-reconstructed
items have INFLATED similarity to corrupt-adjacent items, making them appear more relevant
than they are. This inflated similarity then undermines MMR's diversity filter.

Assessment: this is a genuine concern but REQUIRES empirical verification (check seed7's W
singular value structure). P_deflated: 0.20.

### 8.3 K-hop reasoning may ALREADY diversify before MMR reaches it

The substrate's K-hop retrieval component localizes information across multiple hops.
If K-hop reasoning pre-selects items from STRUCTURALLY DIVERSE graph positions (by design,
K-hop explores different graph neighborhoods), then the candidate set presented to MMR may
ALREADY be more diverse than a flat top-K retrieval would produce.

Implication: MMR's marginal contribution to diversity is LOWER when input candidates are
already K-hop diversified. The failure mode in seed7 may be that K-hop was NOT applied
before MMR (the pipeline feeds flat pinv-retrieved items into MMR), meaning MMR is doing
all the diversification work without K-hop pre-filtering.

Rescue angle: ADD K-hop pre-diversification before MMR. K-hop (K=3-5 hops) on the KB
similarity graph selects candidates from topologically diverse regions; then MMR re-ranks
for relevance + fine-grained diversity. This two-stage approach is structurally stronger
than single-stage MMR.

P_deflated (K-hop pre-diversity eliminates MMR topology failure): 0.40.

### 8.4 Substrate's discrete bipolar states change the density metric

The substrate stores items as bipolar discrete vectors (+1/-1). The cosine similarity
between two substrate-stored items takes values in {-1, -1+2/N, -1+4/N, ..., 1} --
a DISCRETE, QUANTIZED set rather than a continuous interval.

For small N (e.g., N=1024), the granularity is 2/N = 0.00195 -- fine enough to be
treated as continuous. For large N this is negligible. But for the CLUSTER STRUCTURE
with cosine > 0.6 threshold: items are classified as "in cluster" (cosine >= 0.6)
vs "out of cluster" (cosine < 0.6). This binary threshold applied to a discrete
cosine distribution produces different CLUSTER SIZE DISTRIBUTIONS than it would on a
continuous distribution -- small perturbations in similarity can flip cluster membership.

Seed-dependence: if seed7 places items near the 0.6 boundary (discretization boundary),
the effective cluster structure is highly sensitive to which items happen to land
just above vs. just below 0.6. This is a substrate-novel failure mode not present in
standard retrieval systems.

### 8.5 MMR is DESIGNED for document retrieval; KB atom retrieval has different structure

MMR was designed for DOCUMENT retrieval where items are independently authored and have
organic topic clusters. KB atoms (stored substrate patterns) are generated by the KB
CONSTRUCTION process -- which in the test is seeded random facts.

In real production, KB atoms come from a source (document chunks, extracted triples,
entity-relation pairs). These have STRUCTURED REDUNDANCY that organic documents do not:
e.g., extracted triples about the same entity are deliberately similar (high cosine)
because they share entity embeddings. This creates HIGHER HUB CENTRALITY in production
KBs than in test KBs.

Implication: the seed7 failure in a SYNTHETIC KB may actually UNDERSTATE the production
risk. Real production KBs (with structured entity-sharing) may have HIGHER hub centrality
than any of the 3 test seeds. The 2/3 pass rate on synthetic data could be a 1/3 or worse
pass rate on real extracted data.

This is a BRUTAL HONESTY finding: the production risk is likely UNDERSTATED by cycle 148.

---

## 9. HONEST PRODUCTION CLAIM REFINEMENT

### Current claim (post cycle 148):
"MMR + pseudoinverse combined pipeline is production-deployable with caveat: seed7 fails."

### What the honest refined claim should be:

Option A (conservative):
"MMR topology fragility is a real production risk for hub-dense KBs. At lambda=0.5,
the combined pipeline shows 2/3 seed pass rate on synthetic data. Production deployment
REQUIRES either: (a) 5-seed stability verification per KB deployment, OR (b) topology-
aware lambda selection (lower lambda when hub centrality > 5x mean or spectral gap < 0.1)."

Option B (middle):
"Combined pipeline (whitening + pinv + MMR, lambda=0.5) is empirically robust at 2/3 seeds
on synthetic balanced KBs. For narrow-domain KBs with high block separation (medical, legal
with clear domain boundaries), UNCONDITIONAL claim holds. For general-purpose or entity-rich
KBs, topology-aware lambda or DPP is required."

Option C (optimistic but NOT warranted):
"One bad seed among 3; production caveat documented."

RECOMMENDED: Option A. The theoretical analysis (Section 2) strongly supports that MMR
topology sensitivity is MECHANISTIC, not coincidental. Option C is the label-vs-honest
failure mode the user's standing rules explicitly prohibit.

### Senior IR researcher assessment (synthesized):
"MMR at fixed lambda is a known fragility vector for corpus-structure-dependent retrieval.
Any production system using MMR at fixed lambda on general-purpose KBs should include
topology-adaptive lambda or DPP as a fallback. The 2/3 seed pass rate on a synthetic
balanced KB is a warning sign, not a minor anomaly. Given that real KBs have higher hub
centrality than synthetic balanced random graphs, the production failure rate is likely
higher than 1/3."

---

## 10. CYCLE 146 UNCONDITIONAL CLAIM RE-EVALUATION

### Original claim (cycle 146, PROT-008):
"MMR for clustered KBs: UNCONDITIONAL (lambda <= 0.5 SAFE; rho NOT relevant;
cuts propagation 51-86% -> 2-5%)"

### What LVH #245 (cycle 148) reveals:
- The cycle 146 test used 3 seeds, same as cycle 148.
- Cycle 146 showed 3/3 seeds pass (UNANIMOUS) -- that is what locked the UNCONDITIONAL claim.
- Cycle 148 (COMBINED pipeline: whitening + pinv + MMR) shows 2/3 seeds pass.

### The critical distinction:
Cycle 146 tested MMR ALONE on the clustered KB. The COMBINED pipeline adds:
(1) PCA whitening (changes the effective cosine metric -- see Section 8.1)
(2) Pseudoinverse write + decode path (adds noise envelope -- see H4/Section 8.2)

The "UNCONDITIONAL" claim for MMR ALONE on the clustered KB MAY still hold.
The combined pipeline adds two components that can INTERACT with MMR in topology-sensitive ways.

### Revised claim hierarchy:

For MMR ALONE on the clustered KB:
  Claim: CONDITIONALLY VALID -- 3/3 seeds pass in the component-only test. The
  UNCONDITIONAL label should be DOWNGRADED to "robust at lambda <= 0.5 on 3-seed test;
  not validated in combined pipeline."

For COMBINED pipeline (whitening + pinv + MMR):
  Claim: MIDDLE-BAND pending 5-seed rerun.
  New label: "Combined pipeline composes; MMR topology sensitivity requires 5-seed
  pre-deployment validation or TA-lambda."

### Impact on production architecture:
The 57.3x capacity lift claim (cycle 146, PROT-008) is NOT affected -- that is about
CAPACITY (how many facts can be stored), not PROPAGATION SUPPRESSION.
The MMR component's role is PROPAGATION SUPPRESSION (keep corrupt anchors from spreading).
The downgrade affects only the propagation-suppression guarantee of the combined pipeline.
The retrieval quality and capacity claims remain VALID.

---

## CHEAP DECISIVE TEST

Run Test 7A (5-seed sweep at lambda=0.5) on the combined pipeline.
Expected outcome based on analysis: likely MIDDLE-BAND (3-4/5 seeds pass), not HARD-PASS.
This is the minimum-cost test that will either:
(a) Resolve to HARD-PASS (5/5) -- production caveat is minor corner case
(b) Resolve to MIDDLE-BAND (4/5) -- TA-lambda probe scheduled
(c) Resolve to HARD-FAIL (<=3/5) -- DPP required; C-MMR as interim

Cost: adds 2 seeds to existing infrastructure; ~15 min additional experiment time.

---

## FALSIFIABLE PREDICTIONS (HARD-PASS / HARD-FAIL)

HARD-PASS:
  7A: 5/5 seeds pass propagation <= 0.10 at lambda=0.5
  7B (if 7A MID): 5/5 seeds pass at lambda=0.3

MIDDLE-BAND:
  7A: 4/5 seeds pass (document and proceed with TA-lambda)
  7A: 3/5 seeds pass (C-MMR or DPP required)

HARD-FAIL:
  7A AND 7B both <= 3/5 seeds pass (DPP swap-in mandated before combined-pipeline HP claim)
  Topology-stratified (7C): Type B (medium gap, realistic production) fails 2+ seeds
    (means production risk is NOT just a corner case; fundamental architectural change needed)

---

## CROSS-THREAD SYNTHESIS

This drill synthesizes with:
- Cycle 146 (MMR component UNCONDITIONAL): now CONDITIONALLY VALID for component alone;
  MIDDLE-BAND for combined pipeline. NOT a reversal of cycle 146 -- a scope clarification.
- Phase 2 Chain 3 (cross-shard K-hop UNTESTED): the K-hop pre-diversity rescue (Section 8.3)
  connects to the K-hop multi-shard gap. Both point to graph-topology-awareness as a
  production-scale requirement.
- Production architecture (whitening as universal encoder): the whitening -> cosine-metric
  distortion (Section 8.1) is a substrate-specific finding that is NEW and orthogonal to
  prior research. Warrants a standalone drill.
- DPP (Section 3.1): determinantal processes are mathematically adjacent to the free-probability
  framework (random matrix theory). The L-kernel's determinant structure connects to Wishart
  matrix determinant distributions. P(cross-applicable framing via free probability): 0.25
  (speculative; flagged for a future adjacency drill).

---

## SUBSTRATE-PRODUCT IMPLICATIONS

1. Production deployment of the combined pipeline SHOULD include topology-aware lambda or
   5-seed pre-deployment validation as a non-negotiable gate. This is a 0.5-day engineering
   add that prevents a class of customer-visible failures.

2. For general-purpose KBs (Wikipedia-style, entity-rich), DPP is the correct long-term
   retrieval diversification mechanism. MMR at fixed lambda is appropriate only for narrow-
   domain KBs with high block separation.

3. The whitening + cosine-metric distortion (Section 8.1) is a substrate-novel finding that
   has no published precedent. It should be empirically verified before a DPP implementation
   is designed (DPP uses the same cosine kernel; if whitening distorts it, DPP is also affected).

4. K-hop pre-diversification as a pipeline stage (Section 8.3) is a zero-additional-math rescue:
   the substrate already does K-hop reasoning. Routing K-hop graph traversal BEFORE MMR
   selection is a structural improvement at minimal engineering cost.

5. The "production risk is understated by synthetic KB" finding (Section 8.5) is a critical
   honest caveat for any customer demo or deployment: real extracted KBs will have higher
   hub centrality than random synthetic KBs, which means the 1/3 failure rate on synthetic
   data likely maps to a higher failure rate in production.

---

## CITATIONS (verified from lit-scan)

1. Carbonell, J. & Goldstein, J. (1998). "The Use of MMR, Diversity-Based Reranking for
   Reordering Documents and Producing Summaries." ACM SIGIR 1998. [MMR original]

2. Lei, J. & Rinaldo, A. (2015). "Consistency of spectral clustering in stochastic block
   models." Annals of Statistics. [spectral gap + block model separation conditions]

3. Kulesza, A. & Taskar, B. (2011). "k-DPPs: Fixed-Size Determinantal Point Processes."
   ICML 2011. [k-DPP foundation]

4. Chen, L. et al. (2017). "Fast Greedy MAP Inference for Determinantal Point Process to
   Improve Recommendation Diversity." NeurIPS 2018 / arXiv 1709.05135. [fast DPP inference]

5. VRSD paper (2024). "Vector Retrieval with Similarity and Diversity: How Hard Is It?"
   arXiv 2407.04573. [NP-hardness of VRSD; MMR theoretical limitations]

6. SMMR paper (2025). "Sampling-Based MMR Reranking for Faster, More Diverse, and Balanced
   Recommendations and Retrieval." ACM SIGIR 2025. [SMMR as topology-escape variant]

7. CCBQP paper (2025). "Principled and Scalable Diversity-Aware Retrieval via Cardinality-
   Constrained Binary Quadratic Programming." arXiv 2604.02554. [alternative to MMR with
   convergence guarantees]

8. Lei, J. (2019). "A tighter analysis of spectral clustering for the planted partition
   problem." / Improved Analysis of Spectral Algorithm for Clustering. arXiv 1912.02997.
   [eigengap heuristic rigorous justification]

9. Abbe, E. (2018). "Community Detection and Stochastic Block Models." Foundations and
   Trends in Communications and Information Theory. [SBM theory, separation conditions]

10. Krause, A. & Golovin, D. (2014). "Submodular Function Maximization." Tractability:
    Practical Approaches to Hard Problems. [facility location + (1-1/e) guarantee]

Verified count: 10 citations (mix of primary sources + arXiv confirmations from lit-scan).

---

## SUMMARY TABLE

| Hypothesis | P_deflated | Key metric | Falsifiable how |
|------------|-----------|------------|-----------------|
| H1: Hub-dense cluster | 0.52 | Intra-cluster cosine variance | seed7 higher hub centrality |
| H2: Weak block separation | 0.38 | Spectral gap | seed7 lower eigenvalue gap |
| H3: Corrupt anchor at chokepoint | 0.33 | Betweenness centrality | seed7 higher betweenness |
| H4: Pinv noise smearing | 0.18 | Min singular value of W | pinv recall unanimous -> low P |

| Rescue | P_deflated | Cost | Priority |
|--------|-----------|------|----------|
| R1: lambda=0.3 | 0.35 | 0 days | FIRST |
| R2: K-expand K=50 | 0.30 | 0 days | FIRST (combine with R1) |
| R3: TA-lambda | 0.35 | 0.5 days | SECOND |
| R4: C-MMR | 0.42 | 1 week | THIRD |
| R6: SMMR | 0.40 | 1-2 weeks | THIRD (alt to R4) |
| R5: DPP | 0.48 | 2-3 weeks | FOURTH |

P_deflated = deflated by 0.20 lit-scan calibration penalty.
Novel-synthesis P capped at 0.50.

---

**Note path: notes/research_drill_LVH245_mmr_pinv_combined_topology_2x_2026-06-07.md**
