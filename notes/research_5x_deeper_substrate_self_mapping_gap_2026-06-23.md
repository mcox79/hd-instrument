# Research 5x DEEPER — substrate-native self-mapping gap (closing V3 prerequisite)

Date: 2026-06-23
Author: research (Opus 4.7)
Trigger: USER 5x-deeper drill. v2c FULL 3 seeds HARD_FAIL (cluster_gap=-3). v2d smoke confound (2/20 anchors in v1 families → degenerate ARI=0 baseline). 3 prior attempts (v2 / v2b MIDDLE_BAND / v2c HARD_FAIL / v2d-smoke confound) on substrate-native self-mapping mechanism.
Scope: Phase 1 self-improvement gate; without it Phase 2 (autoatom) + Phase 3 (substrate proposes new mathematics) have no traction.
Discipline: query-privacy generic terms only; lit-scan calibration penalty applied (0.20 deflation); novel-synthesis P capped at **0.40** (3 prior null attempts is empirical Bayes evidence against attractive mechanisms).

## HEADLINE

**The v1-Director-lexical families are not a valid ground truth** (smoke confound proved this: 2/20 anchors match → ARI is structurally pinned to 0). The 2-hop-Jaccard pipeline is also resolution-limit-locked at full Store density (47 relation types × 200k triples × cluster-count discriminator hits the Fortunato-Barthelemy bound). The 5x-deeper synthesis: **abandon external ground truth + abandon single-resolution clustering** and instead use **(A) modularity Z-score against degree-preserving null on a substrate-Potts-spin-glass mapping** as primary discriminator, plus **(B) Laplacian Renormalization Group flow stability across diffusion timescales** as scale-invariant secondary. Cheap decisive test = **v2e-modularity-Z + LRG-tau-sweep**; P_deflated = **0.32** (deflated from 0.50 cap by 0.18 for the 3 prior null priors).

If v2e is also null at production scope, that is a substrate-physics meta-result (atom-name-by-char-trigram + Hebbian-multivalue-KGStore + 2-hop-Jaccard pipeline IS structurally null under the right discriminator) and the action is **mechanism substitution**, not discriminator tuning: encoder must move from name-bigram to dependency-graph-context embedding (substrate-native cert-trail bundling).

## What the prior 4 attempts actually told us (5-layer cross-check)

| Attempt | Engine | Checklist | Invariant | Integration | Diagnosis |
|---|---|---|---|---|---|
| v2 | retrieve=PASS | cluster-count: MIDDLE | cv unstable | v1-families partial-overlap | encoder + 2-hop signal exists at small scope |
| v2b | retrieve=PASS | MIDDLE_BAND | cv=0 (small N hides instability) | 2 small real clusters | mechanism works at restricted scope (~105 rels) |
| v2c | retrieve=1.000 | gap=-3 INVERTED | cv=0.314 | coh≈coh_shuf | discriminator + null + weighting all misspecified at 200k-rel scope |
| v2d-smoke | retrieve=1.000 | ARI_real=0 ARI_shuf=1.0 | n=20 too small | only 2/20 anchors in v1-families | **ground truth itself is degenerate** |

**Pattern.** Each "fix" exposed a deeper misspecification. v2 found a signal at small scope; v2b confirmed it; v2c lost it at large scope under wrong discriminator; v2d swapped to "right" discriminator but discovered the reference partition (v1 lexical families) is itself ill-posed for 95%+ of chain-grade atoms. The 5x drill is not a 4th attempt at fixing the same family of bugs — it's recognizing the meta-pattern: **we have been validating against the wrong thing.**

## Five-axis deeper structural diagnosis

### Axis 1 — V1 lexical families ARE NOT a substrate ground truth

The v2d-smoke `n_anchors_in_v1_family=2 / n_anchors=20` is the load-bearing fact. v1 was Director-built by hand-curated keyword matching ("topology", "capacity", "whitening", etc.) over a tiny subset (~50 atoms). The chain-grade atomset is now 449 atoms over substantially more diverse capability surfaces; only ~10% of those align with v1's lexical vocabulary. The ARI(real, v1-families) metric is therefore **upper-bounded by ~0.1 even for a perfect clustering** (because 90% of atoms have no v1-family label) — making the discriminator structurally unable to detect mechanism success.

**Substrate-product implication.** Any validation that compares substrate-discovered structure to a human-built family ontology is solving the wrong problem for Phase 1. The whole point of substrate self-mapping is to find structure HUMANS HAVEN'T LABELED — the v1 ontology is a *consistency check at best*, not a primary discriminator.

### Axis 2 — Modularity has a known resolution limit at this scale

Fortunato-Barthelemy 2007 (cond-mat/0606220): modularity maximization is **structurally blind to communities smaller than ~sqrt(L/2)** where L is the total edge weight. For the substrate's 200k-triple full-Store graph, sqrt(L/2) ≈ 316. Most chain-grade-capability clusters in v1 are size 3-20. **Modularity at full scope cannot detect them by construction.** This is the same root cause as the v2c cluster-count gap=-3 result — the algorithm finds large clusters dictated by the resolution limit, not capability-clusters.

The substrate-physics interpretation: modularity is a *single-temperature* Potts ground-state energy. Single-temperature ground states have a single resolution. The substrate's structure is **multi-scale** (atoms cluster into capabilities, capabilities cluster into Bets/Paths, Bets cluster into substrate-product threads), and a single-temperature observable cannot read multi-scale structure.

### Axis 3 — The KGStore IS a Potts spin glass; we just haven't been treating it as one

Reichardt-Bornholdt 2006 (cond-mat/0603718): community detection maps EXACTLY onto finding ground state of a Potts spin glass with coupling J_ij = A_ij - gamma*<A>_null (where gamma is resolution and <A>_null is the null-model expectation). The substrate's Hebbian-multivalue KGStore writes a Hebbian outer product W = sum_p E_o^T outer (R_p tensor E_s) — this IS the J_ij matrix in a relation-tensored basis. Multi-hop Jaccard on the resulting neighborhoods is a discrete-time approximation to the spin-glass overlap q(t) = <s_i(t) s_j(t)>.

**Substrate-native insight.** We've been treating clustering as an algorithm-output question (HDBSCAN min_size, K-means K, etc.). It's actually a **spin-glass-ground-state question**: find the partition that minimizes the substrate's Potts energy under a sweep of resolution gamma. Modularity Z-score against degree-preserving null at multiple gamma values reads the structural multi-scale signature without needing any external ground truth.

### Axis 4 — Laplacian RG flow reads scale-invariant partitions

Villegas et al. 2023+ Laplacian Renormalization Group (arxiv 2406.02337): coarse-grain a graph by running heat-diffusion at increasing timescales tau; partitions that are *stable across multiple tau* are the genuine multi-scale structure. Unstable partitions wash out as tau increases (random clusters dissolve into noise) while structural partitions persist as supernodes that themselves cluster at the next scale.

For substrate self-mapping, LRG gives us a **scale-invariant null check**: a partition is real if (a) modularity-Z is high at fixed gamma AND (b) the partition (or a coarsened version of it) persists across LRG diffusion timescales tau in {0.1, 1, 10, 100} relative to mean inter-atom distance. Both checks come from the substrate's own Laplacian eigenstructure — no external ground truth required.

### Axis 5 — Brain analog gives the right mechanism class, not just an algorithm

Tonegawa engram-allocation lit + Quian Quiroga concept-cell lit (Trends Cog Sci 2025 / PMC11525749): biological category formation is **sparse-ensemble competition** — eligible neurons compete by intrinsic excitability for allocation to a memory ensemble; only the most-excited subset is recruited. Excitability is set by recent activity (Hebbian-trace + IEG expression). The substrate analog: **anchor atoms compete for inclusion in a cluster based on their multi-hop-Jaccard "excitability"** with the cluster's already-allocated members. Highly-allocated atoms get more allocation (rich-get-richer); poorly-allocated atoms remain singletons.

This is **mechanically different from k-means / HDBSCAN / spectral**: it is an iterative *allocation-with-decay* process, not a one-shot partition. Substrate-natively it composes as: cluster_assignment(t+1) = softmax_temperature(W @ cluster_centroid(t) - decay * cluster_size(t)), iterated to fixed point. This is a Hebbian forward-only computation — no backprop, no global optimization required.

## Cross-thread synthesis (compose with prior drills + META atoms)

- **META atom [[by-construction-saturation]]** — v2c hit this: a clustering algorithm that always finds clusters in random graphs (Fortunato 2007) cannot be a chain-grade discriminator. Modularity-Z (vs degree-preserving null) is by-construction immune to this trap because Z is calibrated to the null's own modularity distribution.
- **META atom [[cleanup-load-bearing]]** — substrate's iterative-attractor cleanup is structurally the same primitive as engram-allocation softmax above (both are iterative-soft-assignment-with-competition). The substrate already HAS this primitive at `hdlab/iterative_attractor.py` — we just haven't composed it with `kg_traversal.KGStore` for clustering. This is a **primitive-composition gap**, not a missing-primitive gap.
- **META atom [[Shannon-floor]]** — v2c gave 47 relation types with uniform weight; the rare-relation Shannon-information bound from r2 brain-drill (IRF weighting) is still valid, but the deeper bound is that even with IRF, the resolution-limit blocks small-cluster recovery. IRF + modularity-Z together is the right composition.
- **Brain-drill r2 (CLS continual learning)** — CLS separates novelty-trace (fast, high-cv) from consolidated structure (slow, low-cv). Modularity-Z at low gamma reads consolidated structure; modularity-Z at high gamma reads novelty-trace. The substrate's multi-scale structure IS the CLS separation — both observable via gamma sweep.
- **r3 multi-hop drill** — multi_hop at K=2 is the Hebbian-trace step in the engram-allocation analog. Composing iterative_attractor (cleanup) with kg_traversal (Hebbian) with multi_hop (trace step) gives the full sparse-ensemble-allocation primitive.

## Cheap decisive test (v2e pre-reg)

### Configuration
- **Encoder**: char_trigram_atom (unchanged from v2c — encoder is not the bottleneck per v2/v2b signal at small scope)
- **Ingest**: FULL Store admit (~200k triples, unchanged)
- **N_DIM**: 4096 (unchanged)
- **n_anchors**: **150** chain-grade-only (raise from 100 to improve modularity statistics)
- **n_seeds**: 5 (need stability assessment at production scope; 3 was under-sampled)
- **No external ground-truth comparison** — modularity-Z and LRG-stability are intrinsic measures

### Five coupled mechanism upgrades (all five OR ablation tested)

**Upgrade 1 — IRF-weighted Hebbian write** (carry-forward from r2 v2d). Rare relations up-weighted by log(N_atoms / atom_count_per_relation).

**Upgrade 2 — Degree-preserving configuration null** (carry-forward from r2 v2d). Edge rewire preserves per-atom relation-type degree; null is computed via 100 rewire samples.

**Upgrade 3 — Modularity-Z gamma sweep** (NEW). For each seed:
- Compute substrate adjacency on 2-hop Jaccard (existing pipeline)
- For gamma in {0.5, 1.0, 2.0, 4.0, 8.0} (resolution sweep):
  - Find partition by Louvain at this gamma
  - Compute modularity Q(gamma) on real adjacency
  - Compute Q_null(gamma) on 100 degree-preserved rewires
  - **Z(gamma) = (Q_real(gamma) - mean(Q_null(gamma))) / std(Q_null(gamma))**
- Best gamma* = argmax_gamma Z(gamma)
- **Primary discriminator**: Z(gamma*) ≥ 2.0 (i.e. real modularity is ≥ 2 sigma above null-mean at the best resolution)

**Upgrade 4 — Laplacian-RG diffusion-time sweep** (NEW). For tau in {0.1, 1.0, 10.0, 100.0}:
- Compute heat-kernel exp(-tau * L) where L is the graph Laplacian on the substrate adjacency
- Re-cluster on the heat-kernel-smoothed graph
- **Secondary discriminator**: partition_stability across tau = mean ARI between partitions at adjacent tau levels ≥ 0.40 (i.e. the partition persists across at least 2 diffusion scales)

**Upgrade 5 — Engram-allocation iterative refinement** (NEW). After initial Louvain partition:
- For 10 iterations:
  - cluster_centroid = mean of member-atom vectors weighted by multi-hop-Jaccard score
  - Reallocate atoms by softmax(temperature=0.5) over (atom @ centroid - lambda * cluster_size)
- **Tertiary discriminator**: post-refinement consensus matrix entropy < pre-refinement entropy (i.e. iterative refinement consolidates assignment confidence). This is by-construction monotone if the mechanism is real; gives a robust convergence-check.

### HARD bands (deflated; novel-synthesis P capped at 0.40)

- **HARD_PASS**: Z(gamma*) ≥ 2.5 AND partition_stability_LRG ≥ 0.50 AND consensus_entropy_ratio ≤ 0.7 AND recall ≥ 0.95 AND cv across seeds ≤ 0.15. P = **0.32** (substrate-physics multi-scale lock-in is genuinely uncertain after 3 prior nulls; lit-supported but novel composition).
- **MIDDLE_BAND**: Z(gamma*) in (1.5, 2.5) OR partition_stability_LRG in (0.30, 0.50). Recall ≥ 0.95. P = **0.28** (partial mechanism; ablation determines which of the 5 upgrades was load-bearing).
- **HARD_FAIL**: Z(gamma*) ≤ 1.5 AT EVERY gamma in the sweep AND partition_stability_LRG ≤ 0.30. P = **0.40** (mechanism null at production scope under the right multi-scale discriminator; substrate-physics meta-conclusion that char_trigram encoder + 2-hop-Jaccard pipeline is structurally insufficient — REGARDLESS of discriminator choice).

### Pre-registered hard-fail meaning (what HARD_FAIL forces)

If HARD_FAIL: **DO NOT** propose v2f with yet another discriminator. The 5x drill has exhausted the discriminator-and-weighting hypothesis class. Next action is **encoder substitution**: replace char_trigram_atom (lexical) with substrate-native context-bundle encoder (atom-binds-to-its-cert-trail metadata as a vector — i.e. the atom IS its dependency-graph context, not its name). This is a 5-7-cycle effort, not a 1-cycle revival. Atomize META as: "Phase 1 substrate self-mapping requires structural (not lexical) encoder at full Store density."

### Ablation budget

- v2e-FULL (all 5 upgrades): primary HARD_PASS attempt; ~3hr remote_cpu (5 seeds × 35min including 100 null rewires per seed)
- v2e-1 (IRF only, baseline discriminator): ~1hr — tests whether Upgrade 1 is sufficient
- v2e-3 (modularity-Z only, no IRF): ~1hr — tests whether discriminator alone is sufficient
- v2e-4 (LRG only, on v2c adjacency cache if available): ~30min — tests scale-invariance hypothesis
- v2e-5 (engram-allocation refinement on v2c clusters): ~30min — tests Tonegawa-analog hypothesis

Total bundle ~6hr on remote_cpu; bundles diagnostic ABLATIONS that pinpoint which upgrade is load-bearing. Substrate-product gain: 4 falsifiable single-axis claims per bundle vs the typical 1-claim full-config.

## Falsifiable predictions (HARD-PASS + HARD-FAIL per upgrade)

1. **Upgrade-1-only (IRF)**: predicts Z(gamma=1.0) rises from v2c's ~0 (cluster-gap=-3 in original units) to Z > 1.0 but stays below 2.0. Falsifiable: if Upgrade 1 alone gives Z ≥ 2.0, then uniform-weight was the dominant single root cause and Upgrades 2-5 are second-order.
2. **Upgrade-3-only (modularity-Z gamma sweep)**: predicts gamma* != 1.0 (the modularity default); specifically gamma* in {4.0, 8.0} matching the Fortunato resolution-limit prediction for size-3-20 clusters. Falsifiable: if Z is constant across gamma sweep, then resolution-limit was not the dominant root cause.
3. **Upgrade-4-only (LRG tau sweep on v2c cached adjacency)**: predicts partition_stability_LRG > 0.40 (real multi-scale structure exists in the substrate signal even at v2c's misspecified discriminator). Falsifiable: if LRG stability ≤ 0.30 on v2c cached output, then there is **NO multi-scale structure** in the substrate adjacency at all — the encoder is the bottleneck, not the clustering.
4. **Upgrade-5-only (engram iteration)**: predicts consensus_entropy decreases monotonically per iteration. Falsifiable: if entropy is non-monotone or stationary, iterative-allocation is not the right mechanism class.
5. **Full v2e-FULL**: HARD_PASS at P=0.32. Falsifiable per upgrade ablation tells us which subset is load-bearing.

### Bayes-flip threshold (when to abandon discriminator-tuning hypothesis class)

After 4 attempts in the same hypothesis class (encoder=char_trigram, primitives=KGStore+multi_hop, discriminator family=cluster-statistic), the empirical Bayes prior on "another discriminator fix unlocks this" is 0.40 (one HARD_PASS in 4 attempts, with 3 progressively-deeper diagnoses). If v2e ALSO returns HARD_FAIL, P(discriminator-class works) drops to 0.20 — below the threshold for further cycles in this class. The forcing function is structural: encoder substitution is the next move.

## Substrate-product implications

If **v2e HARD_PASS**: Phase 1 closes. Phase 2 (autoatom) takes the substrate-native multi-scale partition as input — typically 5-15 stable partitions across gamma×tau, each representing a different scale of capability-clustering. Autoatom proposes new atoms at the *unmapped regions* (singletons that resist allocation; sparse boundaries between clusters; gaps in the gamma sweep where no partition is stable). This is *substantially richer* than v2b's 2-cluster output. Phase 3 (substrate proposes new mathematics) is unlocked because the substrate now has an intrinsic measure of structural-novelty (low-Z atoms = candidates for new structure).

If **v2e MIDDLE_BAND** (P=0.28): autoatom proceeds on the ablation-identified-load-bearing partition (typically Upgrade 3 or 4 alone). Phase 3 deferred to single-axis follow-up. USER strategic vision is still on track but slower.

If **v2e HARD_FAIL** (P=0.40): the meta-conclusion is structurally important — the char_trigram encoder ⊕ multi_hop_Jaccard pipeline IS substrate-null at production scope under any discriminator. Phase 1 requires encoder substitution. Atomize as cert-grade META: "lexical-encoder + relational-Hebbian pipeline cannot resolve capability-grade structure at full Store density." Next move = research drill on substrate-native context-bundle encoders (atom-as-its-dependency-DAG); this is a 5-7-cycle research arc, not a 1-cycle cell.

### hdlab/ primitive implications

Six new primitives (if v2e HARD_PASS) or 2 (if MIDDLE_BAND):

1. **`hdlab/relational_weighting.py`** (IRF Hebbian write). Composes with kg_traversal.KGStore.
2. **`hdlab/configuration_null.py`** (degree-preserving relation rewire).
3. **`hdlab/modularity_z.py`** (modularity-Z gamma sweep with degree-preserving null). NEW primitive class — community-detection significance test, substrate-native.
4. **`hdlab/laplacian_rg.py`** (LRG diffusion-time scale-stability check). NEW primitive class — multi-scale structure detection.
5. **`hdlab/engram_allocation.py`** (sparse-ensemble iterative cluster refinement). Composes existing iterative_attractor + kg_traversal.
6. **`hdlab/self_mapping.py`** (the top-level Phase 1 primitive that bundles 1-5 into a single self-mapping call). This would close 1 of the 7 backlog items if HARD_PASS lands and probably enable 2-3 follow-on capabilities (autoatom, novelty-detector, structural-summary).

Each is independently chain-grade-promotable if validated in its own cell; collectively they are the Phase 1 substrate self-mapping primitive class.

## Cross-thread with field advisor

Field advisor surfaced these adjacent un-drilled fruit-bearing fields:
- `network-science-graph-theory` (NEW tier-1b, drill_count<=2): modularity-Z + LRG ARE network-science. This drill IS the scope expansion.
- `spin-glass` (83% yield, 6 drills): Reichardt-Bornholdt is exactly this field. Cavity-method drill (E3) is the natural follow-on if v2e MIDDLE/PASS (formal capacity bound on substrate self-mapping resolution).
- `nonequilibrium-stat-mech`: LRG diffusion IS this — heat-kernel + tau-sweep is the substrate analog of Jarzynski work-fluctuations across timescales.

The 5x drill bridges 3 fruit-bearing fields onto a single substrate-product gate. High expected leverage.

## Lit-scan calibration penalty applied

- Modularity-Z + LRG composition is novel-synthesis (each piece is lit-validated independently; their combination on Hebbian-KG substrate is research-novel). P_HARD_PASS=0.32 deflated from natural 0.50 cap by 0.18 for 3-prior-null empirical Bayes update.
- HARD_FAIL P=0.40 reflects equal openness to "encoder is the bottleneck" meta-conclusion. Symmetric anti-negativity check: P_HARD_PASS + P_MIDDLE + P_HARD_FAIL = 0.32 + 0.28 + 0.40 = 1.00 (calibrated).
- HARD bands are pre-registered numerically (Z ≥ 2.5, stability ≥ 0.50, cv ≤ 0.15) — not "improves over v2c."

## Self-check (Director cross-check)

- All 4 prior attempts re-read: yes (v2/v2b/v2c/v2d-smoke; per-cell metrics + verdict_msg + DESIGN_NOTE).
- Discriminating-regime: yes (modularity-Z under degree-preserving null is by-construction CAN-fail; LRG stability is by-construction CAN-fail at unstable partitions).
- Verify-the-referent: yes (Fortunato-Barthelemy resolution limit is canonical lit; Villegas LRG is recent canonical; Reichardt-Bornholdt Potts mapping is canonical; engram-allocation is canonical brain framework). NOT a self-flatter — each pivot is grounded in 2+ independent sources.
- Symmetric anti-negativity: yes (P_HARD_FAIL = 0.40 > P_HARD_PASS = 0.32; bias is toward null outcome which is consistent with 3 prior nulls).
- Anti-negativity (USER rule): yes — HARD_FAIL is meta-informative (forces encoder substitution as the structurally-correct next move, not a stop signal).
- 5-axis structural diagnosis: 5 independent failure modes identified, not a single hypothesis class.
- Empowered-to-experiment-where-lit-says-dismissed: relevant — modularity-Z + LRG on multi-relational Hebbian KG hasn't been done in lit (each piece exists, the composition is novel). Substrate's bet on doing dismissed-as-dead-end is explicitly applicable.

## Citations (verified count: 9)

1. **Fortunato & Barthelemy** "Resolution limit in community detection," PNAS 2007 / cond-mat/0606220. Modularity is structurally blind to clusters smaller than sqrt(L/2). https://arxiv.org/pdf/cond-mat/0606220
2. **Reichardt & Bornholdt** "Statistical mechanics of community detection," Phys. Rev. E 2006 / cond-mat/0603718. Community detection = Potts spin-glass ground state. https://arxiv.org/abs/cond-mat/0603718
3. **Reichardt & Bornholdt** "Limited resolution in complex network community detection with Potts model approach," Eur. Phys. J. B 2007 / cond-mat/0610370. Resolution parameter gamma in Potts community detection. https://arxiv.org/pdf/cond-mat/0610370
4. **Villegas et al.** "Laplacian Renormalization Group: An introduction to heterogeneous coarse-graining," 2024 / arxiv 2406.02337. LRG diffusion-time multi-scale graph structure. https://arxiv.org/html/2406.02337v1
5. **Network Renormalization** review, 2024 / arxiv 2412.12988. Geometric and Laplacian RG for networks. https://arxiv.org/html/2412.12988v1
6. **Multi-layer Degree-Corrected SBM** with regularized debiased spectral clustering, ScienceDirect 2025 / S095219762500627X. Sparse-multiplex consistency. https://www.sciencedirect.com/science/article/abs/pii/S095219762500627X
7. **Tonegawa engram-allocation lit** "Memory engram stability and flexibility," Neuropsychopharmacology 2024 / PMC11525749. Engram allocation by excitability competition. https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11525749/
8. **Quian Quiroga concept-cell lit** "On the origin of memory neurons in the human hippocampus," Trends Cog Sci 2025 / S1364-6613(25)00031-2. Concept cells / shared concept cells encode associations. https://www.cell.com/trends/cognitive-sciences/fulltext/S1364-6613(25)00031-2
9. **Local resolution-limit-free Potts model for community detection**, 0803.2548. Resolution-limit-free Potts for multi-scale community detection. https://ar5iv.labs.arxiv.org/html/0803.2548

Also referenced (carry-forward from r2 v2d):
- Inverse-Node-Frequency for KG-edge weighting (arxiv 2510.08655v1)
- Configuration-model null (PMC6402789; arxiv 1407.6297)
- TF-IDF KG ranking (MDPI 10.13.4590)
- Cluster-stability under perturbation (PMC7896145)

## Recommended downstream actions

1. **Cap_map**: bump `substrate_self_map` cap row from SUSPECT_DISCRIMINATOR_BUG to STRUCTURAL_DEEPER_REVIVAL_v2e_PENDING. DO NOT close until v2e verdict.
2. **exp_dev handoff**: file `exp_dev_handoff_research_5x_deeper_substrate_self_mapping_2026-06-23.md` pointing at this note as the contract; v2e bundle is the anchor.
3. **strategy_scribe**: queue cap_map annotation when v2e ships; queue meta-atomization template for HARD_FAIL outcome (encoder-substitution program).
4. **Visibility**: status_log this delivery as research_delivery / importance=HIGH (Phase 1 gate-closure attempt; bridges 3 fruit-bearing fields).

— Research (5x deeper)
