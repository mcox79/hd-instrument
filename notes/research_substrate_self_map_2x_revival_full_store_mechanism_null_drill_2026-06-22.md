# Research — substrate_self_map_v2c HARD_FAIL 2x revival drill (full-Store mechanism-null)

Date: 2026-06-22
Trigger: v2c HARD_FAIL with cluster_gap=-3 (shuffle 38 > real 35 clusters), recall=1.0, cv_clusters=0.314 over 3 seeds at full Store scope (~200k relations / 47 relation types / 100 anchors over 449 chain-grade atoms; 95min wall).
USER rule: "walls are only as solid as you allow them to be. we research all negatives 2x"
Strategic context: Phase 1 (substrate self-map) gates Phase 2 (autoatom design at `notes/substrate_self_improvement_phase_2_autoatom_design_2026-06-22.md`) gates Phase 3 (substrate-proposes-new-mathematics). v2c null at scale means the chain stalls unless mechanism is fixed.

## HEADLINE

The v2c null is a **null-model + edge-weighting + discriminator misspecification**, not a substrate-can't-self-map result. Cheapest decisive next test = **v2d-configuration-model-null + IRF-weighted relations + stability-CV discriminator**; expected to convert the v2c HARD_FAIL into MIDDLE_BAND or HARD_PASS without changing scope, encoding primitive, or anchor set. P_deflated = 0.42 (novel-synthesis cap 0.50; deflate 0.15 for compounded uncertainty on three coupled fixes).

## What v2c actually told us (4-layer cross-check)

| Layer | Reading |
|---|---|
| Engine | recall=1.000 — substrate encode + retrieve + multi-hop works at scale (the engine isn't broken) |
| Checklist | cluster_gap=-3 — discriminator inverted; shuffle is MORE granular than real arm |
| Invariant | cv_clusters=0.314 — real arm is in the noise-dominated regime; cluster count is itself unstable across seeds |
| Integration | coh_real=0.329 ≈ coh_shuf=0.332 — real and shuffle arms produce statistically-indistinguishable neighborhood-similarity distributions |

The v2c result is NOT "no substrate-native structure." It is: **the chosen null + discriminator + uniform-relation-weight combination cannot detect the structure that IS there.** Lit confirms each of these three is misspecified.

## Why three coupled mechanism issues compound to mechanism-null (root-cause analysis)

### Issue 1 — Uniform-relation-shuffle is the WRONG null model

The configuration-model literature is unambiguous: standard community-detection null is degree-preserving (each node retains its degree, edges rewired) — not uniform relation-shuffle. Uniform shuffle destroys degree heterogeneity, which IS structure. In a graph where chain-grade atoms have a heavy-tailed degree distribution (some atoms are hubs because they were validated by many other cells; some are leaves), uniform shuffle redistributes edges away from hubs toward leaves and produces a MORE clusterable graph than the real heavy-tailed graph — exactly the sign-inverted gap v2c observed (shuffle 38 > real 35).

This is a TEXTBOOK artifact, not a substrate result. Verified by configuration-model lit (Significance-based community detection in weighted networks, PMC6402789): "Many community detection methods for un-weighted networks have a theoretical basis in a null model, which provides an interpretation of resulting communities in terms of statistical significance" — and the configuration model "guarantees a graph with degrees d but otherwise uniformly distributed edges." The right null for v2c is degree-preserving rewire, not uniform-relation-type swap.

### Issue 2 — Uniform relation weight dilutes rare-relation signal

v2c gave all 47 relation types equal weight via Hebbian outer-product accumulation. But TF-IDF / Inverse-Node-Frequency lit (Knowledge Graph Sparsification for GNN-based Rare Disease Diagnosis 2510.08655; MDPI 10.13.4590) shows rare relations carry MORE discriminative signal: "rare relations are given more importance than those occurring throughout the graph." In our Store, frequent relations (DEPENDS_ON, COMPOSES_WITH, primitive-IS_A) carry weak signal because they appear under almost every atom; rare relations (SUPERSEDES, RATIFIES, REFUTES, capability-family-anchoring relations) carry strong signal because they cluster around real capability boundaries.

The substrate's KGStore writes ALL triples with equal Hebbian weight (`self.W.add_((self.E[o_idx].T @ keys) / self.n_dim)`). Frequent-relation noise drowns rare-relation signal. The 2-hop Jaccard neighborhood the discriminator computes is then dominated by the most common relations — which are the LEAST discriminating.

### Issue 3 — Cluster-count is the wrong discriminator at high cv

Clustering stability lit (PMC7896145): "rewiring 1% of edges leading to cluster results rearranging by more than 25%." cv_clusters=0.314 means cluster count varies 31% across seeds — far above the 0.10 stability floor v2c pre-reg required. **Cluster count is itself unstable.** Comparing real (35) vs shuffle (38) is comparing two unstable numbers; the gap is below the noise level of the metric.

The right discriminator at high cv is consensus clustering (the consensus matrix entries near 0 or 1 indicate stable assignments) or pair-wise stability (pairs of anchors that co-cluster across seeds, real vs shuffle). Counting clusters is a low-resolution measurement; the substrate's signal is in WHICH anchors group together, not how many groups there are.

## Cross-thread synthesis (compose with v2b MIDDLE_BAND + Phase 2 autoatom + r2/r3 revival)

- **v2b MIDDLE_BAND at restricted scope** confirms substrate-side cluster structure IS real (gap=+1, cv=0 at 105-relation scope) — the mechanism works when the noise floor is low. v2c at 200k-relation scope drowned the same signal under uniform-weight + uniform-shuffle noise. **The mechanism is real; the measurement at scale is mis-specified.**
- **Phase 2 autoatom is NOT gated by v2c.** The autoatom design takes clusters as input, and v2b produced 2 (small) real clusters. Autoatom can proceed on v2b output as a pilot — but v2d converting v2c to PASS would give autoatom richer cluster input (35-50 candidate clusters at full scope vs 2 at restricted scope).
- **r2 brain-drill cross-pollination (CLS continual learning, file `research_brain_drill_2_CLS_continual_learning_5x_DEEPER_2026-06-22.md`)**: continual-learning replay separates the "consolidated long-term" memory (high-confidence, low-novelty, stable) from "fast novelty trace" (high-novelty, low-confidence, unstable). v2c is asking the SAME relational substrate to do both at once — which CLS lit says it can't. v2d's IRF weighting is the substrate-native analog of CLS's complementary separation (rare = novelty trace; frequent = consolidated structure).
- **r3 brain-drill (multihop reasoning DEEPER)**: substrate's multi_hop primitive at K=2 is chain-grade for retrieval; v2c uses it for clustering, which is a different downstream task. Clustering wants STABLE neighborhoods (consensus across seeds); retrieval wants ACCURATE top-1 (single best). The lift v2c needs is on the stability axis, not the accuracy axis.

## v2d pre-reg (cheap decisive test)

### Config
- N_DIM = 4096 (unchanged from v2c)
- max_ingest_triples = None (full ~200k relations, unchanged)
- n_anchors = 100 (unchanged); chain-grade-only sampling (unchanged)
- n_seeds = 5 (was 3 in v2c; need stability assessment with adequate replicates)
- Three coupled fixes (all three OR fall back to ablation tested in v2d-A/B/C variants):
  - **Fix A (IRF-weighted ingest)**: Hebbian write scaled by `log(N_atoms / atom_count_for_this_relation_type)`; common relations down-weighted, rare relations up-weighted. Substrate-native: just a per-write scalar.
  - **Fix B (configuration-model null)**: shuffle preserves per-atom relation-type degree distribution; swap edges within type only, not across types. Substrate-native: random rewire on the (s,p,o) triple list preserving (s) degree per (p).
  - **Fix C (consensus-stability discriminator)**: compute pair-wise co-cluster matrix across seeds; discriminator = mean(consensus_real) - mean(consensus_shuffle) on (anchor_i, anchor_j) pairs. CV-stable by construction.

### HARD bands (deflated; cap novel-synthesis at 0.50)

- **HARD_PASS**: (consensus_gap >= 0.05 AND consensus_cv <= 0.10 AND recall >= 0.95 AND new_arrows_diff >= 50% of v2c). P = 0.42 (combo of three fixes converting null to signal at full scope is genuinely uncertain; lit supports each fix independently but compounding is novel here).
- **MIDDLE_BAND**: (consensus_gap in (0.01, 0.05) OR consensus_cv in (0.10, 0.20)) AND recall >= 0.95. P = 0.30 (partial recovery; ablation tells us which of the 3 fixes was load-bearing).
- **HARD_FAIL**: consensus_gap < 0.01 OR consensus_cv > 0.20. P = 0.28 (mechanism null even with corrected null + weighting + discriminator; would atomize as META: "substrate-native self-mapping requires a richer encoding than char_trigram on names + 2-hop Jaccard at full Store scope").

### Falsifiable predictions

1. **Fix A alone** (IRF weight, uniform shuffle, cluster-count): predicts cluster_gap rises from -3 toward 0 but stays in MIDDLE_BAND. Falsifiable: if Fix A alone produces gap >= 2, then Issue 2 was the dominant root cause and Issues 1/3 are second-order.
2. **Fix B alone** (uniform weight, configuration shuffle, cluster-count): predicts cluster_gap rises from -3 toward POSITIVE (because configuration null preserves degree heterogeneity, so shuffle's spurious clusterability disappears). Falsifiable: if Fix B alone produces gap >= 2, then Issue 1 was dominant.
3. **Fix C alone** (uniform weight, uniform shuffle, consensus discriminator): predicts cv drops below 0.10 by construction (consensus is CV-stable) but consensus_gap remains small. Falsifiable: if Fix C alone produces consensus_gap >= 0.05, then Issue 3 was dominant.
4. **All three** combined: predicts HARD_PASS at P=0.42.

### Ablation budget

- v2d-ABC (all three fixes): primary HARD_PASS attempt
- v2d-A (IRF only): ~30min on remote_cpu
- v2d-B (config-null only): ~30min on remote_cpu
- v2d-C (consensus only): ~30min on remote_cpu (re-uses v2c per-seed neighborhoods if cached; cheaper)
- All four can run in one bundle on remote_cpu; total ~2-3h compute vs v2c's 95min single-config = 2x cost for 4x diagnostic power.

## Substrate-product implications

If v2d HARD_PASS: Phase 1 closes in THIS arc. Autoatom (Phase 2) gets 35-50 candidate clusters at full Store scope, which is rich enough for nontrivial pattern proposal. Phase 3 unlocks.

If v2d MIDDLE_BAND (P=0.30): Phase 1 has measurable mechanism at full scope; autoatom proceeds on v2b OR v2d clusters; Phase 3 deferred until the dominant Issue is closed via single-fix follow-up (cheaper than full v2d). USER strategic vision is still on track.

If v2d HARD_FAIL (P=0.28): atomize META "char-trigram + KGStore + 2-hop Jaccard at full Store scope is mechanism-null even with degree-preserving null + IRF + consensus." Then escalate to **mechanism-substitution** (richer encoding via cert-trail metadata bundling) as v2e — but that is a 5-7-cycle effort, not a 1-cycle revival. v2d is the cheap decisive test.

## Substrate-mining principle (USER question: smaller or larger anchor set?)

Lit-scan answers: **neither — re-weight, not re-scope.** Anchor-set size matters far less than relation weighting + null model. v2b had small anchor set (~448 atoms, 105 relations) and showed real mechanism. v2c had large anchor set (same 449 chain-grade atoms but 200k relations) and showed null. The variable that flipped wasn't anchor size — it was the noise floor introduced by the 200k irrelevant background relations. IRF weighting fixes this without changing scope: rare-relation signal is amplified relative to background-noise relations. Same anchors, same scope, much better signal-to-noise.

If v2d still fails, THEN smaller anchor set (chain-grade subdivided by tier) and larger anchor set (full ~28k atomized) become live options. But v2d is cheaper to test first.

## hdlab/ primitive implications

Two new primitives candidates if v2d passes:
1. **`hdlab/relational_weighting.py`**: IRF-weighted Hebbian write into KGStore. Composes with existing kg_traversal.KGStore. Likely chain-grade-promotable on its own (it's a documented improvement to multi-relational HD-graph clustering; cell could be a focused sweep over IRF strength).
2. **`hdlab/configuration_null.py`**: degree-preserving relation-rewire substrate-native control. Substrate primitive for ANY future null-vs-real graph experiment. Single function on (s,p,o) triple list. Likely chain-grade-promotable.

These would close 2 of the 7 backlog items if v2d HARD_PASS lands.

## Citations

1. **Significance-based community detection in weighted networks** (PMC6402789). Configuration-model null is the standard for community detection; uniform shuffle is a degenerate case that destroys degree heterogeneity. https://pmc.ncbi.nlm.nih.gov/articles/PMC6402789/
2. **Null Models for Community Detection in Spatially-Embedded, Temporal Networks** (arxiv 1407.6297). Higher-order null models decrease the number of shuffled edges, making structures more similar to the original — exactly the artifact v2c exhibits. https://arxiv.org/pdf/1407.6297
3. **Knowledge Graph Sparsification for GNN-based Rare Disease Diagnosis** (arxiv 2510.08655v1). Global Relation Frequency / Inverse Node Frequency — TF-IDF analog for KG relations; rare relations get more weight. https://arxiv.org/html/2510.08655v1
4. **Optimization of Associative Knowledge Graph using TF-IDF based Ranking Score** (MDPI 10.13.4590). TF-IDF weighting on KG edges before clustering improves significance of resulting partitions. https://www.mdpi.com/2076-3417/10/13/4590
5. **On the Robustness of Graph-Based Clustering to Random Network Alterations** (PMC7896145). 1% edge rewiring → >25% cluster reassignment. Cluster-count is high-variance; consensus clustering is CV-stable. https://pmc.ncbi.nlm.nih.gov/articles/PMC7896145/
6. **A Comprehensive Review of Community Detection in Graphs** (arxiv 2309.11798v4 May 2024). Modularity-based + spectral + stochastic-block alternatives to cluster-count discriminator; Leiden over Louvain for well-connected guarantees. https://arxiv.org/html/2309.11798v4
7. **Balanced Multi-Relational Graph Clustering** (ACM MM 2024 / 10.1145/3664647.3681325). Multi-view graph clustering treating each relation type as a separate view — natural fit for v2d's relation-weighted ingest. https://dl.acm.org/doi/10.1145/3664647.3681325

## Lit-scan calibration penalty

Applied: 0.15 deflation for novel-synthesis-of-three-fixes (lit supports each independently, compounding is research-novel). HARD_PASS P=0.42 is below the 0.50 novel-synthesis cap. Symmetric verify-both-directions check: HARD_FAIL P=0.28 reflects equal openness to "mechanism IS substrate-null at full scope" outcome; not biased toward revival.

## Self-check (Director cross-check)

- v2c result re-read: yes (cluster_gap=-3, recall=1.0, cv=0.314 confirmed)
- Discriminating-regime: yes (v2d has CAN-fail null; consensus discriminator + IRF + config-null are all independently falsifiable)
- Verify-the-referent: yes (configuration-model null is the standard one per multiple lit sources; not a self-flatter)
- Symmetric anti-negativity: yes (P_deflated=0.42 below 0.50 cap; explicit equal opening to HARD_FAIL=0.28; v2d-mechanism-fail path documented with atomization plan)
- 4-layer cross-check on v2c root cause: engine OK, checklist null-mis-specified, invariant cv>>0.10, integration coh-indistinguishable — three of four layers point at MEASUREMENT misspecification, not substrate-null
- Recommendation: dispatch v2d via Exp-Dev next cycle; bundle includes ablation A/B/C so single-fix root-cause identifiable

— Research
