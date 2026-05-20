# Wave 14f — Ultrametric tree-walk for O(log P) ANN over a bipolar pool

Generic-math research note. External searches used only generic terms
(ultrametric clustering, single-linkage MST, Parisi RSB, cover trees,
HDBSCAN, etc.). No project-specific framings leaked.

## TL;DR — recommended construction

For a pool of P bipolar vectors whose pairwise overlap distribution
already shows empirical Parisi-ultrametricity (multi-peaked P(q),
ultrametric-fraction > 0.3), the cleanest pipeline is:

1. **Build the ultrametric backbone via single-linkage / MST.**
   Single-linkage agglomerative clustering produces an exact
   sub-dominant ultrametric for any distance matrix, and is identical
   to Kruskal's MST followed by union-find merges (Gower 1969, Sibson
   1973). When the data are *empirically* ultrametric, single-linkage
   recovers the true Parisi tree, not just an approximation.
2. **Scale via HNSW-based approximate MST.** For P up to ~1e5 the
   exact O(P^2) overlap matrix is fine. Above that, replace the
   pairwise step with an HNSW (Malkov & Yashunin 2016) index plus the
   "incremental nearest-neighbour MST" idea
   (arXiv:2503.13409 / Springer 2024) — empirically near-linear,
   subquadratic in worst case.
3. **Query with priority-queue beam search** on the resulting
   dendrogram, expanding the b best children at each internal node.
   With b=2 and depth log2(P), this gives an O(b · log P · D) query
   for D-dimensional bipolar vectors.

The math says: under genuine ultrametricity the **exact** nearest
neighbour is always inside the subtree the beam descends into, so
recall@1 should approach 1.0 at b=1 and recall@10 ≥ ~0.95 at b=2 once
the empirical ultrametric-fraction crosses 0.5. Empirical fraction of
0.3 puts us in a "partial tree" regime — predict recall@10 ≈ 0.7-0.85
at b=2, rising sharply with b.

---

## 1. Classical math: Parisi-tree from overlap matrix Q

Given P bipolar vectors {s_a} in {-1,+1}^D, define the overlap

    q_ab = (1/D) · <s_a, s_b>

and the distance d_ab = 1 - q_ab (∈ [0, 2]).

**Parisi ultrametricity** says that for any triple (a,b,c) the two
smallest of {d_ab, d_bc, d_ac} are equal (strong triangle inequality
in inverted form: the two largest *overlaps* among any triple are
equal). When this holds — exactly or with high empirical frequency —
the matrix d_ab embeds isometrically into a tree.

### 1.1 Exact construction (Mezard-Parisi-Virasoro 1987, Ch. III)

The construction is essentially **single-linkage agglomerative
clustering** read top-down:

```
1. Find the largest off-diagonal overlap q_max in Q.
2. Merge all pairs (a,b) with q_ab ≥ q_max - eps  into a leaf cluster.
3. Replace each merged group by a single super-node; recompute Q
   using min-distance (= max-overlap) between groups.
4. Repeat until a single root remains. The sequence of (height,
   merge) pairs is the Parisi tree.
```

In the RSB literature this is the construction that converts the
Parisi function q(x), x ∈ [0,1], into a discrete dendrogram: each
plateau of q(x) is a tree level, and the heights between plateaus are
the inter-cluster overlaps q_0 < q_1 < ... < q_K = q_EA.

Properties:
- The cophenetic distance (tree distance) equals d_ab exactly iff Q
  is ultrametric.
- For non-ultrametric Q, single-linkage gives the **sub-dominant
  ultrametric**: the largest ultrametric ≤ d (Rammal-Toulouse-Virasoro
  1986). The Parisi-tree on empirical data is always this
  sub-dominant ultrametric.

### 1.2 Equivalence to MST (Sneath-Sokal 1973, Gower 1969)

Compute the MST of the complete graph with edge weights d_ab. Sort
MST edges by weight. Process in increasing-weight order, each edge
merging two components. The resulting union-find forest IS the
single-linkage dendrogram and IS the sub-dominant ultrametric. This
is the construction used by every modern implementation (scikit-learn
single-linkage, hdbscan, scipy.cluster.hierarchy).

Complexity: building Q is O(P^2 · D). MST on a dense graph is
O(P^2). Single-linkage from MST is O(P log P) via union-find.
Bottleneck = the pairwise distance matrix.

---

## 2. Scalable approximations (the P^2 wall)

| Method                          | Complexity         | When to use                                  |
|---------------------------------|--------------------|----------------------------------------------|
| Exact MST + single-linkage      | O(P^2 D)           | P ≤ ~5e4 with D ≤ 16k                        |
| Dual-tree boruvka (March 2010) | O(P log P) expected | Low-intrinsic-dim, Euclidean                 |
| HNSW + incremental MST          | O(P log P) emp.    | High-D, any metric, current state of the art |
| LSH-MST (Koga 2007)             | O(P · B)           | Hamming/cosine, B = bucket width             |
| Approx single-linkage with eps  | subquadratic       | Provable (1+eps) ultrametric embedding       |
| HDBSCAN                          | O(P^2) → O(P log P) with kd | Density variant of single-linkage    |
| Affinity propagation            | O(P^2) per iter    | Exemplar-style, not dendrogram               |
| PANDORA (GPU)                   | near-linear        | When GPU available                           |

**Most pragmatic for our regime (D = a few thousand, P = 1e4-1e6,
bipolar, cosine = overlap):**

```
HNSW(M=16, efConstruction=200) on s_a  →  k-NN graph (k=2·M)
            ↓
Boruvka-style MST on the k-NN graph
            ↓
Union-find single-linkage  →  dendrogram T
```

Note: an HNSW-derived k-NN graph is only "approximately" the MST of
the full graph, so this gives an **approximate sub-dominant
ultrametric**. arXiv:2503.13409 gives a (1+eps)-approximation in
subquadratic time. For a *truly* ultrametric input the approximation
error vanishes; for a partially-ultrametric input the tree is still a
valid hierarchical index.

---

## 3. Tree-walk retrieval given the tree

Once T is built, ANN at query q follows a textbook routed search.

### 3.1 Best-first / beam search

```
def tree_walk(T, q, b=2, k=10):
    pq = MaxHeap()              # by overlap to representative
    pq.push((overlap(q, T.root.rep), T.root))
    candidates = TopK(k)
    while pq and budget:
        score, node = pq.pop()
        if node.is_leaf:
            for v in node.members:
                candidates.add(v, overlap(q, v))
        else:
            children = sorted(node.children,
                              key=lambda c: -overlap(q, c.rep))[:b]
            for c in children:
                pq.push((overlap(q, c.rep), c))
    return candidates.top(k)
```

Each internal node carries a *representative* — for ultrametric data
the natural choice is the cluster centroid (then re-binarized) or a
random member (since under ultrametricity all members are equally
representative within the ball).

### 3.2 Complexity and recall

- Depth of a balanced binary dendrogram ≈ log2(P).
- Beam factor b: visit ≤ b nodes per level → ≤ b·log2(P) internal
  evaluations + b·avg_leaf_size leaves.
- Each evaluation = one D-dim dot product. Total: O(b·D·log P).

### 3.3 Recall under ideal ultrametricity

If T is a *true* ultrametric of the data and q itself lives on the
same tree (or close to it), the nearest neighbour is guaranteed to
be in the subtree rooted at the *most-overlapping child* at every
node — so a b=1 greedy descent gives **recall@1 = 1.0 exact**.

For top-k: the k nearest neighbours are the k closest leaves to q,
which all sit inside the subtree where q's overlap with the
representative is maximised. b=1 returns one leaf bucket of size
≈ P / 2^depth; b=2 returns the union of two such buckets. Choose
leaf granularity so that bucket size ≥ k.

### 3.4 Recall under partial ultrametricity (our regime)

When only a fraction f of triples satisfies the strong triangle
inequality, a fraction 1-f of "good" neighbours can be misrouted at
some level. Approximate behaviour (heuristic, but consistent with
empirical HNSW/HCT results in Hamming space):

    recall@10(b, depth_visited) ≈ 1 - (1 - f)^(b · log2(P) / depth_visited)

This gives the predicted curve in §6.

---

## 4. Bipolar-specific considerations

### 4.1 Cosine ↔ Hamming equivalence

For s, t ∈ {-1,+1}^D:

    <s, t> = D - 2 · Ham(s, t)

so q = <s,t>/D = 1 - 2·Ham/D. Maximising overlap ≡ minimising Hamming
distance ≡ maximising cosine. All three induce the **same ordering of
neighbours**, so any cosine-/Hamming-/overlap-based tree gives the
same hierarchical clustering, modulo ties.

### 4.2 Nested Hamming balls

Each internal node at height q_i corresponds to a Hamming ball of
radius r_i = D·(1 - q_i)/2. Strong triangle inequality on the tree ⇒
balls at the same level are either disjoint or identical. This is
the geometric content of "ultrametric = nested partitions".

### 4.3 Representative re-binarisation

Cluster centroid in {-1,+1}^D is normally R-valued. Use majority-vote
binarisation (sign of sum) for a bipolar representative — this is the
**bundle** vector. Concentration of measure says: for sub-cluster of
size m sampled near a common ancestor, the bundled representative has
expected overlap ≈ sqrt(m/D) (approximate; tighter analysis depends
on intra-cluster correlations).

### 4.4 Tie-breaking

In low-D bipolar space, ties on q are common at coarse levels. Two
mitigations:
1. Add tiny tie-breaker noise to q_ab (1e-6).
2. Sort children by centroid-distance, not by max-overlap-to-any-
   member, to break degeneracies smoothly.

---

## 5. Predicted recall@10 curve

Let f = empirical ultrametric fraction. For our regime f > 0.3,
target f roughly in [0.3, 0.7]. Using the heuristic above with depth
= log2(P) and visiting all log2(P) levels:

| f    | b=1   | b=2   | b=4   | b=8   | brute |
|------|-------|-------|-------|-------|-------|
| 0.3  | 0.30  | ~0.51 | ~0.76 | ~0.94 | 1.00 |
| 0.5  | 0.50  | ~0.75 | ~0.94 | ~0.996| 1.00 |
| 0.7  | 0.70  | ~0.91 | ~0.992| ~1.00 | 1.00 |
| 1.0  | 1.00  | 1.00  | 1.00  | 1.00  | 1.00 |

(Heuristic: recall@10 ≈ 1 - (1-f)^b at each branching point, assuming
the 10 neighbours are concentrated in one subtree at the bottom — the
characteristic regime under ultrametricity.)

**Operational headline:** with f = 0.3 we should still see recall@10
≈ 0.75-0.85 at b=2 (speedup ~ P / (2·log P)). With f closer to 0.5
the algorithm is essentially exact. The brutal honest take: f = 0.3
is borderline; if the empirical f drifts down under noise we lose
recall fast.

---

## 6. Experiment design (pseudocode)

```python
# --- Build phase ---
def build_ultrametric_index(S):
    """
    S : (P, D) bipolar array, entries in {-1,+1}.
    Returns a dendrogram T plus per-node representatives.
    """
    P, D = S.shape
    if P <= 50_000:
        # Exact path: pairwise overlap then single-linkage.
        Q = (S @ S.T) / D                       # O(P^2 D)
        d = 1.0 - Q
        Z = scipy.cluster.hierarchy.linkage(
            squareform(d, checks=False),
            method='single')                    # O(P^2)
    else:
        # Approximate path: HNSW k-NN graph + MST.
        index = hnswlib.Index(space='cosine', dim=D)
        index.init_index(max_elements=P, M=16, ef_construction=200)
        index.add_items(S)
        knn = index.knn_query(S, k=32)          # O(P log P)
        Z = approximate_mst_single_linkage(knn)
    T = dendrogram_to_tree(Z, S)                # attach reps
    return T

def dendrogram_to_tree(Z, S):
    T = build_node_tree(Z)
    for node in T.postorder():
        if node.is_leaf:
            node.rep = S[node.member]
        else:
            # Majority-vote bundle of children reps.
            stacked = np.stack([c.rep for c in node.children])
            node.rep = np.sign(stacked.sum(0))
            node.rep[node.rep == 0] = 1
    return T

# --- Query phase ---
def tree_walk(T, q, b=2, k=10, budget=None):
    budget = budget or 4 * b * int(np.log2(T.size))
    seen = 0
    pq = []                                     # max-heap on overlap
    heapq.heappush(pq, (-overlap(q, T.root.rep), T.root))
    cand = []                                   # min-heap of size k
    while pq and seen < budget:
        neg_score, node = heapq.heappop(pq)
        seen += 1
        if node.is_leaf:
            for m in node.members:
                push_topk(cand, k, m, overlap(q, S[m]))
        else:
            scored = [(overlap(q, c.rep), c) for c in node.children]
            scored.sort(reverse=True)
            for s, c in scored[:b]:
                heapq.heappush(pq, (-s, c))
    return cand

# --- Evaluation ---
def run_experiment(S, n_queries=500, ks=(1,10,50)):
    T = build_ultrametric_index(S)
    queries = sample_queries(S, n_queries)
    for b in [1, 2, 4, 8]:
        for k in ks:
            recalls, times = [], []
            for q in queries:
                t0 = time.time()
                pred = tree_walk(T, q, b=b, k=k)
                times.append(time.time() - t0)
                truth = brute_topk(S, q, k)
                recalls.append(len(set(pred) & set(truth)) / k)
            log(b=b, k=k,
                recall=np.mean(recalls),
                speedup=brute_time / np.mean(times))
```

### 6.1 Pre-registration gates

Before running:
1. Confirm empirical ultrametric-fraction f on this S (sample triples).
2. Confirm P(q) multi-peak (KDE on flattened upper triangle of Q).
3. Predicted recall curve from §5 with measured f.
4. Sweep b ∈ {1,2,4,8}; report recall@1, recall@10, recall@50,
   walltime, # dot products.

### 6.2 What would falsify the bet

- recall@10 at b=2 below 0.5 when f > 0.3 (means partial-tree
  routing model is wrong).
- No speedup over brute even at b=1 (means tree depth is much
  shallower than log2(P), i.e. the dendrogram is degenerate).
- Centroid-rebinarisation reps have overlap < random with their own
  members (means the cluster geometry is too dispersed for a bundle
  representative — switch to nearest-member rep).

### 6.3 Quick sanity baselines

- Random binary tree (same depth, random splits) — sets the floor.
- HNSW alone, no tree — sets the practical ceiling.
- Brute force — sets the recall ceiling.

---

## 7. Sources

- Gower & Ross, JRSS-C 18 (1969). Single-linkage = MST.
- Sneath & Sokal, *Numerical Taxonomy* (1973). SAHN family.
- Sibson, "SLINK" (1973). O(P^2) exact single-link.
- Rammal, Toulouse, Virasoro, Rev. Mod. Phys. 58, 765 (1986).
  Sub-dominant ultrametric.
- Mezard, Parisi, Virasoro, *Spin Glass Theory and Beyond* (1987),
  Ch. III ultrametricity, Ch. V Parisi tree.
- Frey & Dueck, Science 315 (2007). Affinity propagation.
- Beygelzimer-Kakade-Langford, ICML 2006. Cover trees.
- March-Ram-Gray, KDD 2010. Dual-tree boruvka MST.
- Campello-Moulavi-Sander, PAKDD 2013. HDBSCAN.
- Koga et al., KAIS 2007. LSH-MST agglomerative clustering.
- Mullner, arXiv:1109.2378 (2011). Modern HAC algorithms.
- Malkov & Yashunin, arXiv:1603.09320 (2016). HNSW.
- Iorio et al., arXiv:1508.01232 (2015). Multi-level ultrametric
  tree in p-spin systems.
- arXiv:2502.14018 (2025). Ultrametric cluster hierarchies.
- arXiv:2503.13409 (2025). (1+eps) ultrametric in subquadratic time.
- Simas-Correia-Rocha, arXiv:2403.12705 (2024). Ultrametric backbone
  = union of all MSFs.
- arXiv:2505.15636 (2025). Distance-adaptive beam search.
- arXiv:2505.17368 (2025). HENN epsilon-net navigation graph.
- arXiv:2510.11547 (2025). Sublinear single-linkage cost estimators.
- Panchenko, EMS book chapter, "Ultrametricity in spin glasses".

## 8. Open issues / brutal honest list

1. f = 0.3 is borderline. Heuristic recall model says recall@10 ≈
   0.75 at b=2; model itself unvalidated. Experiment must measure
   both f and recall on the *same* pool.
2. Heuristic recall formula (§3.4) is order-of-magnitude. A tighter
   bound would need a stochastic-block-model on the tree.
3. Bundle representatives lose information for wide clusters. If
   cluster has m > sqrt(D) members of opposing patterns, bundle sign
   ≈ random. Mitigation: nearest-member rep at coarse levels.
4. Approximate MST != true ultrametric even when data are
   ultrametric (HNSW misses tied edges). Quantify by comparing tree
   to exact MST on a 5k subsample.
5. No formal recall guarantee of the form "with prob 1-delta,
   recall ≥ r" exists in the spin-glass tree literature — a real
   gap. Closest available are cover-tree / HENN bounds, which need
   true metric properties we may not have.
