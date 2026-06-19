# Wave 14f — ICL-on-ultrametric-memory: synergy with branch membership

Research compiled 2026-05-20. External search only, generic math terms.
Scope: when a memory has confirmed ultrametric/tree structure, and we add N
new examples at query time for in-context-learning-style adaptation, does
the gain depend on whether the added examples sit ON the same branch as
the test query, or on a DISTANT branch?

---

## TL;DR

The literature points decisively to **non-monotonic, U-shaped gain**:

1. **Tree-CLOSE** added examples give the biggest single-shot likelihood
   boost when the test query is itself well-described by the existing
   branch posterior. This is the regime where kNN-LM / RETRO / RAG all win
   — large overlap, rare-but-on-manifold facts, "long tail within schema".
2. **Tree-DISTANT** added examples give the biggest *posterior reshaping*
   when the test query sits in a region the current memory under-covers.
   This is the schema-inconsistent / prediction-error regime: information
   gain per example is highest precisely because the prior is most wrong
   there.
3. **Tree-MID** (same broad cluster, different leaf) is the worst spot —
   examples are too redundant to reshape the prior and too off-axis to
   sharpen the existing leaf.

For our setup (HDC memory with confirmed ultrametric structure being
probed by ICL-style on-the-fly augmentation), the **dominant prediction
is regime-dependent**:

- If test queries are drawn from existing branches: **tree-close wins**
  at small N (16); tree-distant catches up by N=256 because it adds
  capacity rather than refining.
- If test queries are drawn uniformly across the tree (including held-out
  branches): **tree-distant wins** monotonically; tree-close is wasted
  effort on a branch the query never visits.

### Recommended experiment design

Run a **2 (query distribution) x 3 (add-set placement) x 3 (N) factorial**
on a pool whose ultrametric structure has already been confirmed (HCA
cophenetic correlation > 0.85; the wave14e prerequisite).

Factors:

- Query distribution: `on-branch` (test queries drawn from the same
  branch we will add to), `uniform-tree` (test queries drawn across all
  branches including held-out ones).
- Add-set placement: `same-branch` (tree-close), `sibling-branch`
  (tree-mid), `distant-branch` (tree-distant). Distance measured by
  ultrametric path length.
- N ∈ {16, 64, 256}.

Primary outcome: ICL gain = base-model NLL on test - augmented-model NLL
on test. Bayes-factor secondary outcome with 5 seeds.

Pre-registered prediction (ranked by literature support):

> P1 (strongest support): `on-branch × same-branch` peaks at small N and
> plateaus.
> P2 (strong): `uniform-tree × distant-branch` is monotone increasing in
> N and overtakes same-branch by N=256.
> P3 (medium): `sibling-branch` is dominated by either extreme at every N.

---

## 1. kNN-LM literature: what does neighbor placement do?

### Khandelwal 2020 (1911.00172), Borgeaud RETRO 2022 (2112.04426)

- kNN-LM helps most on **rare patterns** — factual knowledge, names,
  near-duplicate sentences. This is the **on-branch long-tail** regime.
- Perplexity decreases nearly linearly with datastore size; most
  marginal gain is from coverage rather than precision.
- RETRO retrieves chunked neighbors with cross-attention; with a 2T
  database, most queries have on-manifold (tree-close) neighbors.
- Hosseini-Tahmasebian 2025 (arxiv:2505.14309): input-neighbor overlap
  shows **threshold behavior** — minimal effect below threshold, then
  substantial perplexity reduction above it.

### Xu/Alon 2023 (2301.02828); Drozdov 2022 (2210.15859); Doostmohammadi 2023 (2305.16243)

Most direct evidence for branch effects:

- Biggest contributor to kNN-LM gain is the **softmax temperature** on
  the kNN distribution — peaked retrieval over a few tight neighbors
  beats flat retrieval over diverse ones.
- Not all retrieved neighbors are useful; quality > diversity at small k.
- Surface-level n-gram overlap (tree-close) is the dominant driver of
  perplexity reduction.

### Diversity-selection lineage (Mavi 2025 2505.01842, Sui 2025 2505.19426)

Complicates the pure tree-close story:

- Pure similarity-based selection introduces topical bias.
- MMR-style reranking balancing similarity with diversity consistently
  improves downstream performance, especially on **complex / OOD**
  tasks — exactly when the test query may not sit cleanly on the
  most-similar branch.

**Synthesis for our setup**: kNN-LM lineage says tree-CLOSE dominates at
small N when the test query is well-described by the existing branch.
Diversity-selection lineage says the optimum shifts toward tree-distant
when the test distribution is heterogeneous / OOD.

---

## 2. Bayesian view: ICL as inference under a structured prior

### Xie et al. 2021 (arxiv:2111.02080)

ICL = locating a latent concept c in the prior p(c). The likelihood of a
prompt under concept c contributes evidence; the posterior over c sharpens
as examples accumulate.

Now suppose the prior p(c) is hierarchical: c lives on an ultrametric
tree, with mass concentrated near existing leaves. Two cases:

- **Test query latent concept c* sits ON an existing branch**: prior
  p(c*) is already large. Each on-branch example multiplies the
  likelihood by a sharp factor (because the data really were generated
  from a nearby concept). Posterior collapses fast → small N suffices.
  This is the **same-branch wins at small N** prediction.
- **Test query c* sits on a held-out / sparsely-populated branch**:
  prior p(c*) is small. On-branch examples (relative to memory, not c*)
  do nothing for c* because they live elsewhere on the tree. Distant
  examples that happen to be on the c* branch supply the evidence that
  shifts mass there. This is the **distant-branch wins under tree-OOD**
  prediction.

The likelihood ratio between branches is, under an ultrametric tree
prior, dominated by the **path distance** in the tree. Adding K examples
at tree-distance d from c* contributes log-evidence roughly proportional
to K · exp(-α·d) for some α > 0. So:

- Adding K examples at d=0 (same leaf): full evidence per example.
- Adding K examples at d=mid (sibling): exponentially attenuated.
- Adding K examples at d=large (distant branch): negligible for the
  on-branch case, but the dominant signal when c* itself is far.

### Akyürek et al. 2022 (arxiv:2211.15661)

ICL as implicit gradient descent / ridge regression. Under a structured
(hierarchical) prior this becomes hierarchical Bayesian regression. The
**effective learning rate per added example** is highest where the prior
is most uncertain — that is, in tree regions with little existing mass.

This argues for tree-DISTANT additions to give higher per-example info
gain when measured by KL-to-true-posterior, even though they give lower
per-example NLL reduction on existing-branch queries.

### Hierarchical Dirichlet Process intuition (Teh et al. 2006)

HDP posterior over a new observation borrows strength from same-cluster
observations (concentration toward existing tables) but admits a
new-table probability proportional to α. Adding examples to a populated
table (same-branch) reduces posterior variance there; adding examples
that open a new table (distant-branch) increases the number of clusters
the model is willing to entertain. The **two interventions are
qualitatively different**: refinement vs. structure-extension.

---

## 3. Hippocampal-cortical schema effects: biological grounding

### Tse et al. 2007 (Science) — schema enables one-trial consolidation

In rats with a pre-trained flavor-place schema, a single new
flavor-place association becomes hippocampus-independent within 48
hours. Without the schema, weeks. This is the canonical **same-branch
(schema-consistent) wins** result: existing structure allows immediate
absorption.

For ICL: if the added examples are schema-consistent (tree-close), the
model needs almost no examples to integrate them. Translates to a
prediction that **gain saturates quickly with N** for on-branch additions.

### Tse 2011 follow-up; van Kesteren et al. 2012, 2020

Schema-inconsistent material is initially harder to encode but updates
the schema more dramatically once consolidated. Prediction errors index
the *amount of schema updating* (Greve et al. 2017, 2019,
biorxiv:805887). Schema-inconsistent (tree-distant in our framing)
events produce larger prediction errors, which:

- Recruit more hippocampal-vmPFC binding,
- Lead to more durable schema-level changes,
- BUT have lower immediate behavioral recall than consistent items.

This maps onto the ICL distinction:

- Immediate-task NLL gain (= behavioral recall analogue) → **tree-close
  wins**.
- Posterior-reshaping / generalization gain (= schema update analogue)
  → **tree-distant wins**.

### Schapiro 2017 (Phil Trans Roy Soc B) — CLS within hippocampus

The trisynaptic pathway memorizes individual episodes (tree-leaf-like);
the monosynaptic pathway extracts statistical regularities (tree-internal
nodes). The hippocampus runs **both modes in parallel**. The
neuroscience-honest answer is: the question "is tree-close or tree-distant
better" is itself underspecified — biology runs them simultaneously
because they answer different problems.

### McClelland, McNaughton, O'Reilly 1995 (CLS); McClelland 2013 schema
extensions

The fast hippocampal system handles same-branch (within-schema)
particulars rapidly. The slow cortical system integrates across branches
to build the tree itself. When a schema already exists (tree is mature),
new on-schema material consolidates fast (Tse 2007); when no schema
exists, the cortex needs many examples to build one — i.e., tree-distant
items in our setup, used early, primarily *grow the tree* rather than
fill leaves.

---

## 4. The two predictions, ranked

### Prediction A: tree-CLOSE ICL is more effective (refining a known schema)

Evidence FOR:

- kNN-LM gain driven by surface overlap and concentrated retrieval
  (Khandelwal 2020, Xu/Alon 2023, Doostmohammadi 2023).
- Tse 2007 schema-consistent one-trial consolidation.
- Bayesian posterior under hierarchical prior: same-branch evidence has
  exponentially larger likelihood factor (path distance kernel).
- Input-neighbor overlap threshold (Hosseini-Tahmasebian 2025): below
  threshold, retrieval adds nothing.

Evidence AGAINST:

- Diversity-selection literature shows pure similarity introduces bias
  and underperforms diversity-aware selection on complex tasks (Mavi
  2025, Sui 2025).
- At large N, same-branch returns diminish (datastore saturation).

### Prediction B: tree-DISTANT ICL is more effective (filling gaps)

Evidence FOR:

- Schema-inconsistent items index larger schema updates (Greve 2019,
  biorxiv:805887).
- vmPFC compression and schema-extension literature (Mack 2020).
- HDP intuition: distant examples open new tables.
- Diversity-aware example selection wins on OOD / complex tasks.
- ICL OOD generalization requires diverse pretraining (Garg et al. 2025,
  arxiv:2506.05574).

Evidence AGAINST:

- Without an on-branch hook, distant examples can confuse the retriever
  (Drozdov 2022 — bad neighbors hurt).
- Immediate NLL on on-branch test queries: distant additions are nearly
  useless.

### Ranking for our setup

**Most likely**: U-shape / regime-dependent. Tree-close dominates when
test queries are drawn from already-populated branches. Tree-distant
dominates when test queries are uniform-over-tree (i.e., include
held-out branches). Tree-mid (sibling branch) is dominated everywhere.

**Second most likely**: tree-close dominates at small N (16–64),
tree-distant catches up at large N (256+) by adding capacity rather
than refining.

**Least likely (but possible if our memory is very dense)**: tree-close
always wins because the test distribution we care about is, in practice,
always on-branch.

---

## 5. Design pseudocode

```python
def wave14f_design():
    # Prerequisites
    assert pool.ultrametric_cophenetic_corr() > 0.85  # confirmed structure
    branches = pool.tree_branches(level=3)  # K=8 branches, depth 3

    # Split branches into populated vs held-out
    populated = random.sample(branches, k=6)
    held_out  = [b for b in branches if b not in populated]

    # Build memory from populated branches only
    memory = build_memory(branches=populated)

    # Two test-query distributions
    test_sets = {
        "on_branch":    sample_from(populated),
        "uniform_tree": sample_from(populated + held_out),
    }

    # Three add-set placements
    add_sets = {
        "same_branch":    pick_branch_matching_test(),
        "sibling_branch": pick_sibling_branch(),
        "distant_branch": pick_branch_at_max_tree_distance(),
    }

    Ns = [16, 64, 256]
    seeds = [0, 1, 2, 3, 4]

    results = []
    for test_dist in test_sets:
        for add_pos in add_sets:
            for N in Ns:
                for seed in seeds:
                    base_nll = eval_nll(memory, test_sets[test_dist],
                                        seed=seed)
                    aug_nll  = eval_nll(memory + add_sets[add_pos](N),
                                        test_sets[test_dist], seed=seed)
                    gain = base_nll - aug_nll
                    results.append((test_dist, add_pos, N, seed, gain))

    # Analysis: 2x3x3 ANOVA with seed as random effect.
    # Bayes factor: H_close (same-branch best) vs H_distant (distant best)
    # vs H_regime (interaction with test_dist).
    return results

def pick_branch_at_max_tree_distance():
    # Use ultrametric path distance, not embedding cosine.
    # Ultrametric distance = depth at which branches diverge.
    pass
```

Diagnostic plots:

- 2x3 panel: rows = test_dist; cols = N. y = gain, x = add_pos.
- Expect rows to differ qualitatively (interaction). If they don't,
  fall back to single-prediction model.

Pre-registration checklist (per project_research_playbook):

- [ ] Lock seeds, branches, N before any runs.
- [ ] 5 seeds per cell minimum.
- [ ] Bayes factor threshold: BF > 10 for declaring an effect.
- [ ] Bandit allocation across cells if compute-constrained — but the
      factorial is small enough (2x3x3x5 = 90 runs) to enumerate.
- [ ] Verify ultrametric structure on the actual pool before starting.

---

## 6. Risks and confounds

- **Tree-distance vs embedding-distance confound**: kNN-LM uses
  embedding cosine; our ultrametric distance may not correlate. Confirm
  correlation on the pool before running, or report both.
- **Capacity confound**: at large N, memory is just bigger. Add a
  `random_placement` control drawing N items uniformly from the tree.
- **Distillation confound**: if the model already internalized the
  held-out branches from pretraining, "tree-distant" isn't actually OOD.
  Probe zero-shot NLL on held-out branches before augmentation.
- **Branch-balance confound**: ensure all branches have comparable
  density in memory — otherwise we measure density, not placement.

---

## Sources

- Khandelwal et al. 2020. Generalization through Memorization: Nearest
  Neighbor Language Models. arXiv:1911.00172.
- Borgeaud et al. 2022. Improving language models by retrieving from
  trillions of tokens (RETRO). arXiv:2112.04426.
- Xu, Alon et al. 2023. Why do Nearest Neighbor Language Models Work?
  arXiv:2301.02828.
- Drozdov et al. 2022. You can't pick your neighbors, or can you? When
  and how to rely on retrieval in the kNN-LM. arXiv:2210.15859.
- Doostmohammadi et al. 2023. Surface-Based Retrieval Reduces Perplexity
  of Retrieval-Augmented Language Models. arXiv:2305.16243.
- Hosseini-Tahmasebian et al. 2025. Studying the Role of Input-Neighbor
  Overlap in Retrieval-Augmented Language Models Training Efficiency.
  arXiv:2505.14309.
- Mavi et al. 2025. Exploring the Role of Diversity in Example Selection
  for In-Context Learning. arXiv:2505.01842.
- Sui et al. 2025. The Role of Diversity in In-Context Learning for
  Large Language Models. arXiv:2505.19426.
- Xie, Raghunathan, Liang, Ma 2021. An Explanation of In-context
  Learning as Implicit Bayesian Inference. arXiv:2111.02080.
- Akyürek, Schuurmans, Andreas, Ma, Zhou 2022. What learning algorithm
  is in-context learning? Investigations with linear models.
  arXiv:2211.15661.
- Garg et al. 2025. When can in-context learning generalize out of task
  distribution? arXiv:2506.05574.
- Tse et al. 2007. Schemas and Memory Consolidation. Science 316:76–82.
- Tse et al. 2011. Schema-dependent gene activation and memory encoding
  in neocortex. Science 333:891–895.
- van Kesteren et al. 2012. How schema and novelty augment memory
  formation. Trends in Neurosciences.
- Greve et al. 2017, 2019. Prediction errors and schema updating.
  bioRxiv:805887.
- Schapiro et al. 2017. Complementary learning systems within the
  hippocampus. Phil. Trans. R. Soc. B 372:20160049.
- McClelland, McNaughton, O'Reilly 1995. Why there are complementary
  learning systems. Psychological Review.
- Mack et al. 2020. Ventromedial prefrontal cortex compression during
  concept learning. Nature Communications 11:46.
- Teh, Jordan, Beal, Blei 2006. Hierarchical Dirichlet Processes. JASA.
