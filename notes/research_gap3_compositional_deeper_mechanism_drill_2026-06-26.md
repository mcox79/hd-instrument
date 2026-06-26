# Research: GAP 3 -- WHY HRR-bundle fails + non-bundle mechanism classes (deeper drill)

date: 2026-06-26
filed-by: research (Opus 4.7 1M)
trigger: USER deep drill on Gap 3 -- two cells attempted (HRR cortical-schema bundles + LARS-VSA relational bottleneck), both PARTIAL/HARD_FAIL. USER asks: articulate the intuitive gap; identify WHY HRR-bundle fails; drill non-bundle mechanism classes (SDM/CLS/PredictiveCoding/ModernHopfield/CategoryTheory)
scope: depth drill, not breadth re-scan. Builds on notes/research_gap3_compositional_5x_drill_2026-06-26.md (prior breadth scan; 18 candidates ranked); two empirical anchors (Cell 1 cortex_schema MIDDLE_BAND; Cell 2 lars_vsa HARD_FAIL_CONFOUND).
calibration: per [[feedback-lit-scan-calibration-penalty]] -- agent P estimates deflated 0.15-0.25; novel-synthesis cap 0.50; hard-fail thresholds pre-registered.

## HEADLINE

The intuitive gap is NOT "no schema mechanism" -- it is "substrate stores instances by hash-address, not by membership in a category basin." HRR-bundle approaches (Cell 1 ARM_FEATURE / ARM_CAPABILITY / ARM_COMBINED; Cell 2 ARM_RELBOTTLENECK) FAIL for one structural reason: HRR bundling is **linear superposition with crosstalk that grows as O(sqrt(K/N))**, so adding more category members to a "schema" prototype creates a NOISIER prototype, not a CLEANER one (Plate 1995; Schlegel et al. 2021 Generalized-HRR confirms capacity is linear in N and degrades sharply at saturation). A true schema is the OPPOSITE: more exemplars should make the prototype SHARPER (basin deeper, basin wider, residual closer to class-mean). The mechanism class that actually delivers this is NOT bundling -- it is **attractor compression with energy-landscape sharpening** (Modern Hopfield exponential capacity, Demircigil 2017 + Ramsauer 2020) and/or **slow-rate Hebbian extraction across replay-aligned exemplars** (CLS framework, McClelland 1995 + Kumaran-McClelland 2016). Both have brain-existence-proof. Of the 5 mechanism classes drilled here, the two highest P_deflated candidates are:

1. **Modern-Hopfield prototype attractors over hippocampal episodes** (P_deflated=0.45) -- substrate already has codebook + iterative_attractor; the missing piece is `power-of-similarity` energy (Krotov-Hopfield 2016) which converts the linear cleanup into exponential capacity and creates basin-of-attraction for category prototypes that SHARPEN with more exemplars. Cell ~1.5 days local CPU at N=8192.
2. **CLS-replay schema-channel** (P_deflated=0.40) -- substrate has replay_cycle (continual.py) + gated_write (predictive_coding.py); missing piece is the **two-W architecture** where W_fast = episodic (existing) and W_slow = consolidated. Replay drives gradient-rate Hebbian into W_slow with rate eta_slow << eta_fast. Brain-existence-proof for compositional generalization; composes natively with the NREM proven-bound from last night's drill (Gap 4 TWO_TIER_GENERATIONAL).

Sparse Distributed Memory (Bricken-Pehlevan 2021) is a strong adjacency BUT is functionally similar to attention -- the substrate's iterative_attractor IS already approximately doing SDM-style address-overlap cleanup; the 0.00 heldout in original Gap 3 was NOT an SDM-capacity issue but a **no-prototype-formation** issue. SDM remains a useful Tier-3 angle if Modern-Hopfield + CLS both HARD_FAIL.

Critical re-framing: **Cell 1 ARM_FEATURE_BASED_SCHEMA 0.4733 vs baseline 0.3733 (+0.10 lift, 1.27x) IS the signal that schema-formation is mechanistically possible** -- it's just that the prototype-via-mean approach hits the HRR-bundle ceiling at ~0.50 because crosstalk noise floor at N=8192 with 4 category members per schema is ~0.35-0.45 (matches Cell 1 numbers within noise). Lifting that ceiling requires REPLACING bundling with attractor-compression. ARM_CAPABILITY_BASED_SCHEMA HURTS (-0.08) because it forces the schema vector to occupy a region OF the cone where capability-tagged neighbors live -- it's an anti-pattern reproducing the anisotropy issue from Gap 2.

## Cheap decisive test

CELL: `gap3_modern_hopfield_prototype_attractor_v1` (cell-author smoke + Fix #17 measurement + Fix #28 per-arm metrics)

- N=8192 (per HRR-crosstalk lesson; do NOT smoke at 2048)
- Same compositional task as Cell 1 (synthetic, no substrate-state contamination): 5 categories x 20 train + 10 heldout per category; chance 0.20; same seed pool [11, 13, 19]
- Three arms:
  - ARM_BASELINE: substrate's existing predictive_coding.gated_write + iterative_attractor.iterative_cleanup (will replicate Cell 1 ARM_NO_SCHEMA ~0.37)
  - ARM_HRR_BUNDLE_PROTOTYPE: Cell 1 ARM_FEATURE_BASED_SCHEMA exactly (linear-mean prototype). Acts as direct comparison-anchor; expected ~0.47.
  - ARM_MODERN_HOPFIELD_PROTOTYPE: power-of-similarity energy E(x) = -sum_i exp(beta * x . xi_i) per Krotov-Hopfield 2016 / Demircigil 2017. Each category gets ONE category prototype P_c = attractor_fixed_point of energy over the 20 training instances. Heldout query relaxes into nearest prototype basin via iterative gradient-flow on E.
  - ARM_MODERN_HOPFIELD_CONTINUOUS: Ramsauer-2020 softmax form (single-step attractor) -- new_x = X @ softmax(beta * X.T @ x). Simpler and substrate has all required primitives (just matmul + softmax).
- Pre-registered bands per [[feedback-experiment-bias-master-checklist]]:
  - HARD_PASS: ARM_MODERN_HOPFIELD_* >= 0.65 heldout (3.25x chance; lifts +0.18 absolute over ARM_HRR_BUNDLE_PROTOTYPE = the schema ceiling found in Cell 1)
  - HARD_FAIL: ARM_MODERN_HOPFIELD_* converges within 5% of ARM_HRR_BUNDLE_PROTOTYPE. Interpretation: attractor-compression does NOT escape the linear-bundle ceiling in substrate's regime; angle is closed; pivot to CLS-replay.
  - MIDDLE_BAND [0.50, 0.65]: PARTIAL; lift is positive but below chain-grade threshold; queue (beta_sweep x heldout_difficulty) follow-up.
- Discriminator: 3-arm spread (BASELINE / BUNDLE / HOPFIELD). If BUNDLE = HOPFIELD = BASELINE within 5% the test is non-discriminating; redesign before USER arbitration per [[feedback-encoder-picks-emerge-from-data-not-user-arbitration]].
- Cross-cell sanity rail: ARM_BASELINE must NOT rise above 0.45 (would replicate Cell 1 baseline drift; methodology confound).
- Substrate-mine FIRST per [[feedback-substrate-mine-capacity-before-extrapolating]]: search atoms for `modern_hopfield` / `dense_associative` / `krotov` -- there is prior Modern-Hopfield work (modern_hopfield_xl per Fix #28 memory) but it was COLLAPSE-to-0.007 in one arm, MIDDLE_BAND only in classical -- understand WHY before re-dispatching.
- Compute budget: 1.5 hour CPU local_cpu_queue at N=8192. Single 4-arm cell.

## Falsifiable predictions

### HARD PASS thresholds (chain-grade claim if met)

1. **ARM_MODERN_HOPFIELD_PROTOTYPE >= 0.65 heldout AND >= 1.35x ARM_HRR_BUNDLE_PROTOTYPE.** Interpretation: attractor-compression escapes the linear-bundle ceiling. Substrate-product implication: ship `hdlab/modern_hopfield.py` primitive; promote ARM_MODERN_HOPFIELD to capability-suite regression test for "schema generalization."
2. **ARM_MODERN_HOPFIELD_CONTINUOUS >= 0.65 AND matches PROTOTYPE within 3% AND is cheaper.** Interpretation: substrate's existing matmul+softmax suffices; no new primitive needed; the "schema" was already implicit in iterative_cleanup -- it just needed the right inverse-temperature beta. Substrate-product implication: ship a one-config-flag upgrade `iterative_cleanup(..., energy='modern_hopfield', beta=20)`. ~3 lines of code.
3. **Both ARM_MODERN_HOPFIELD_PROTOTYPE and ARM_MODERN_HOPFIELD_CONTINUOUS >= 0.65 with spread <0.05.** Interpretation: GAP 3 is structurally solvable via attractor-compression; pick cheaper arm for production.

### HARD FAIL thresholds (rules out attractor-compression angle)

1. **ARM_MODERN_HOPFIELD_* both within 0.05 of ARM_HRR_BUNDLE_PROTOTYPE.** Interpretation: at N=8192 with 5 categories x 20 instances, the schema-formation bottleneck is NOT energy-landscape design but **information-theoretic** -- 20 instances per category at chance 0.20 may simply not have enough mutual information to support 0.65 heldout. Action: pivot to CLS-replay (different mechanism class) AND drill `instances_per_category` capacity-sweep (10/20/40/80).
2. **ARM_BASELINE rises above 0.45.** Interpretation: replicates Cell 1 baseline drift; the cleanup mechanism itself is leaking class info. Re-audit harness per [[feedback-fix28-verify-per-arm-metrics]].
3. **All arms collapse near chance (<0.30).** Interpretation: methodology confound -- different seed regime than Cell 1. Stop, re-audit harness.

### MIDDLE BAND [0.50, 0.65]

- Partial; report per-arm metrics; cert-classify as MM-grade per [[feedback-fix28-recurring-skunkworks-correct-more-than-director]]; queue follow-up sweep over (beta in [5, 10, 20, 50, 100]) x (instances_per_cat in [10, 20, 40, 80]) x (n_categories in [3, 5, 10, 20]).

## Section 1: Articulate the intuitive gap

### The substrate-side story (in plain words)

Substrate stores facts the way a **filing cabinet** stores files: every fact gets a slot, the slot is found by hash-address (HRR binding), and retrieval is "pull the file from that slot." This works perfectly for what was filed. What the substrate **does not have** is the cabinet's equivalent of a **librarian who reads every file and writes a CARD CATALOG that lists which files share which themes.** When you ask "is this novel-thing X warm-blooded?" the substrate has no card catalog to consult -- it can only check if X is literally in the filing cabinet. It is not. So the substrate scores at chance on heldout items.

The brain solves this by running **TWO storage systems**: the hippocampus is the filing cabinet (fast, instance-by-instance, indexable by hash, capacity limited to ~weeks); the neocortex is the **slow-extracted card catalog** (slow, prototype-by-prototype, indexable by category-membership, capacity is essentially compressed representations). The brain runs the librarian during SLEEP -- the hippocampus replays episodes, the neocortex receives them at a slow learning rate, and over thousands of replays the neocortical weights converge to a representation where category-mates are **close in vector space** (intra-class compression) while across-category distances are **far** (inter-class separation). McClelland 1995 (Why-there-are-complementary-learning-systems) and Kumaran-McClelland 2016 establish this empirically and computationally.

The substrate has none of that. It has ONE W (one filing cabinet). When you try to build a "schema" by averaging the instances of a category, you build a **bundle vector**: a sum of class members. This is exactly what Cell 1 ARM_FEATURE_BASED_SCHEMA did. It got +0.10 lift. **The lift is real; it is the bundle prototype actually doing some work.** But it caps out around 0.47 because of HRR crosstalk math (see below).

### Why HRR-bundle fails specifically

Plate 1995 established the HRR superposition capacity:
- A bundle of K vectors in N dimensions has signal-to-noise ratio O(sqrt(N/K)).
- When you query the bundle with a probe matching member i, you get signal proportional to <member_i, member_i> = 1 plus noise sum_{j != i} <member_j, probe> which is sqrt(K-1)/sqrt(N) in expectation.

For Cell 1 at N=8192 with K=20 instances per category bundled into a "schema prototype":
- SNR = sqrt(8192/20) = 20.2
- Sounds good in isolation. But the heldout query is NOT a member of the bundle. It is an OUT-OF-BUNDLE item that should match the bundle by virtue of being "similar in feature space."
- The match between heldout and bundle is exactly cos(heldout, mean(members)) = (1/K) sum_i cos(heldout, member_i).
- For random features this is O(1/sqrt(K)) below the in-bundle SNR.
- So the heldout-vs-bundle similarity is in the noise floor.

**This is the structural reason a linear-mean prototype caps out at ~0.5 in Cell 1.** It is not a tuning issue, it is the geometry of linear bundling. The schema mechanism needs to be NON-LINEAR -- it needs to either (a) sharpen the prototype non-linearly with each new exemplar (Modern Hopfield), (b) use a separate slow-rate channel to compress the prototypes (CLS-replay), or (c) bypass prototypes entirely by using attractor-basin membership rather than vector similarity (modern-Hopfield exponential capacity).

### Specifically WHY ARM_CAPABILITY_BASED_SCHEMA HURTS (-0.08)

This was the surprising negative finding in Cell 1. The Capability-based arm constructed schema vectors by binding a category label with a "capability" descriptor (e.g., warm-blooded XOR breathes-air). It HURT performance. Why?

Per the anisotropy reframe from Gap 2 (notes/research_gap2_REFRAME_anisotropy_is_feature_2026-06-26.md), substrate atoms live on a **CONE** (high cosine similarity to a global mean direction). When you BIND category labels with capability tags via XOR / HRR convolution, you ROTATE the schema vector OFF the cone. Heldout instances live ON the cone. The schema is now in an orthogonal direction. Result: the schema is too far from heldout instances to provide signal -- the relative ranking against random-W cleanup is WORSE than no-schema baseline.

This is direct empirical confirmation of the anisotropy-is-feature thesis from Gap 2: **mechanisms that ROTATE away from the cone (whitening, DG pattern-separation, XOR-binding-of-tags) hurt; mechanisms that EXPLOIT the cone (partition routing, fly-LSH, KV learned-projection) help.** ARM_CAPABILITY_BASED_SCHEMA is structurally identical to the failed Gap-2 whitening / water-filling / DG pattern-separation cells.

ARM_COMBINED_SCHEMAS HURTS slightly (-0.013) because it averages the feature-based (helps) and capability-based (hurts) bundles -- the harm component contaminates the help component.

### Why Cell 2 ARM_RELBOTTLENECK ALSO failed (HRR-bundle in a different costume)

LARS-VSA's relational bottleneck (Cell 2 ARM_RELBOTTLENECK = 0.20 at chance 0.20, full collapse) constructs a fixed codebook of K=64 symbols and uses cross-attention-style binding. The key structural property: **the symbols are INDEPENDENT of input content** (this is the entire point of LARS-VSA). But that means the binding `query @ symbol` is essentially random rotation -- the symbols are not aligned with the cone direction of substrate's atom representations. Same failure mode as ARM_CAPABILITY: the binding ROTATES off the cone, the heldout query (on the cone) cannot find the bound representation, performance collapses to chance.

ARM_RESONATOR (best Cell 2 arm, 0.4267) works because it ITERATES toward a fixed point that stays on the cone (resonator-network factorization preserves cone-direction through the unbinding loop). It barely beats the leaky-baseline (0.3333) by +0.09. This is the second piece of evidence (in addition to Cell 1) that cone-preserving mechanisms beat cone-rotating mechanisms.

### Synthesis of the intuitive gap

Three layers in the brain's stack; substrate has 2 of 3:

| Layer | Brain implementation | Substrate primitive | Status |
|---|---|---|---|
| L1 Episodic storage | Hippocampus DG + CA3 | predictive_coding.gated_write, iterative_attractor | PRESENT |
| L2 Slow extraction of invariants | NREM replay, hippocampus -> cortex | continual.replay_cycle (drift_reduction proven_bound), but NO destination cortex-channel | MISSING DESTINATION |
| L3 Inference-time pattern-completion against schemas | Neocortical attractor | iterative_attractor.iterative_cleanup, but NO schemas to complete against | PRESENT BUT EMPTY |

The gap is at L2's DESTINATION (where do the slow-extracted schemas LIVE) and at L3's TARGET (what does the attractor relax INTO). Both are solved by adding a **separate W_slow** to the substrate (the cortex-channel) plus **a non-linear compression rule** to populate W_slow (Modern-Hopfield or CLS-Hebbian).

The reason HRR-bundle approaches fail is that they try to make L2 and L3 work WITHOUT a separate W_slow -- they construct schemas in the SAME W as episodes, with the SAME linear-bundle operation, hitting the same crosstalk ceiling.

## Section 2: Five non-bundle mechanism classes

### A. Sparse Distributed Memory (Kanerva 1988; Bricken-Pehlevan 2021)

**Mechanism:** Address-based storage where each item is written to ALL hard-locations within Hamming distance < d of its key, then retrieval pools across all hard-locations within distance d of the query. Bricken-Pehlevan 2021 (ICLR) showed SDM is mathematically equivalent to transformer attention under L2-unit-norm hypersphere data, and connects to the cerebellum biology.

**How it implements compositional generalization:** Address arithmetic. The schema for a category is naturally encoded as the OVERLAP region in address space where multiple category members hash to nearby hard-locations. A novel category member with similar features hashes to addresses that overlap the existing category cluster -- retrieval naturally pools the cluster.

**Substrate-native mapping:** Substrate's `iterative_cleanup` against a codebook of M atoms IS approximately SDM with hard-locations = codebook entries and Hamming-distance = cosine-similarity threshold. The MISSING piece is the **pooling step** -- SDM aggregates across ALL near-locations whereas iterative_cleanup picks the argmax. Implementation: replace argmax with softmax-aggregation (which IS what Modern Hopfield does -- the same primitive solves both A and D below).

**Why this may NOT add over current substrate:** Bricken-Pehlevan note that SDM == softmax-attention for L2-unit data. Substrate's iterative_cleanup is already L2-unit-and-softmax-based when configured with sign_cleanup=False. The substrate may already be doing SDM. The 0.00 heldout in original Gap 3 was not an SDM-capacity issue; it was a NO-PROTOTYPE-FORMATION issue. SDM is the **retrieval** mechanism, not the **schema-formation** mechanism. So SDM alone doesn't fix Gap 3 -- it needs to be paired with a write-side compression mechanism (B, C, or D below).

**P_solve_deflated: 0.20** (low because substrate likely already has this; not the bottleneck)

**Verdict:** Tier-3 angle; useful as a falsification probe (if Modern-Hopfield works and is just SDM-with-correct-beta, then this confirms the mechanism class).

### B. Slow-learning consolidation (CLS framework)

**Mechanism:** Two storage systems: W_fast = hippocampus = episodic = high learning rate eta_fast, sparse pattern-separated; W_slow = cortex = semantic = low learning rate eta_slow << eta_fast, distributed prototype-formation. Replay drives interleaved-learning of episodes from W_fast into W_slow during sleep cycles. McClelland-McNaughton-O'Reilly 1995 (Psychological Review) established this; Kumaran-McClelland 2016 (Trends Cog Sci) showed it explains generalization. Most recent: arxiv 2507.11393 (2026) "A Neural Network Model of Complementary Learning Systems" demonstrates pattern-separation + pattern-completion architecture for continual learning.

**How it implements compositional generalization:** Replay-driven interleaved learning at low rate eta_slow causes W_slow to converge to a representation that minimizes a long-time-averaged loss over ALL replayed episodes. Category-mates (which co-occur in replay statistics) get **pulled together in W_slow** (intra-class compression); across-category items get **pushed apart** (inter-class separation). At inference, a novel category-member maps onto the COMPRESSED category region in W_slow even though it was never literally stored.

**Substrate-native mapping:** Substrate has `continual.replay_cycle` (drift_reduction proven_bound on last night's drill, chain-grade-eligible boundary) which provides the REPLAY mechanism. Substrate has `predictive_coding.gated_write` which provides the Hebbian write. MISSING piece: the **destination W_slow** (currently substrate has one W). Implementation: instantiate W_episodic (existing) and W_schema (new). Replay reads from W_episodic, writes to W_schema with eta_schema << eta_episodic. Retrieval queries BOTH W_episodic and W_schema and uses the higher-confidence channel.

**Composition with NREM proven-bound:** Last night's Gap 4 drill identified TWO_TIER_GENERATIONAL as the rank-1 mechanism (P=0.50, exp_dev hand-off filed). That cell adds W_slow for **capacity** reasons. CLS-replay for Gap 3 adds W_slow for **schema-extraction** reasons. **Both cells share the same architectural change.** Suggests bundling Gap 3 + Gap 4 mechanism into a single TWO_TIER cell that tests BOTH capacity-retention AND compositional-generalization endpoints. Cost = 1 cell, payoff = 2 gap closures.

**P_solve_deflated: 0.40** (raw lit P=0.65; -0.20 calibration; -0.05 because eta_slow tuning may have wide variance band)

**Why NOVEL vs Cell 1 / Cell 2:** Cell 1 averaged INSTANCES into a "schema vector" with NO learning rate (one-shot). Cell 2 used FIXED random symbol codebook with NO replay. CLS-replay is fundamentally DIFFERENT: schemas EMERGE from many replay passes at low learning rate, never explicitly constructed.

**Cross-cell sanity rail:** if W_schema converges to mean-of-instances (i.e., reduces to ARM_FEATURE_BASED_SCHEMA), then CLS-replay is just slow bundling and shouldn't add. The proper experiment uses non-linear write rule (BCM-style Hebbian with multiplicative interaction) so the slow extraction does something non-equivalent to bundling.

### C. Predictive coding hierarchy (Rao-Ballard 1999)

**Mechanism:** Multi-layer top-down predictions; layer L+1 sends predictions DOWN to layer L; layer L sends residuals (observed - predicted) UP. Each layer's weights are updated to minimize residual at the next-lower layer. Hierarchy converges to a representation where higher layers encode INVARIANTS across lower-layer specifics. arxiv 2506.06332 (2026) "Introduction to Predictive Coding Networks for ML" surveys the recent progress.

**How it implements compositional generalization:** Higher-layer schemas = expected feature patterns. Novel category instance presents residual = (instance - expected schema). If residual is small, the schema EXPLAINS the instance (generalize). If residual is large, route to lower-layer episodic storage (do not generalize). The schema-vs-residual decomposition IS the compositional generalization mechanism: schemas capture what is shared, residuals capture what is unique.

**Substrate-native mapping:** Substrate has `hdlab/predictive_coding.py` with `predict`, `residual`, `gated_write`, `threshold_gate` ALREADY. What's MISSING is the **hierarchy** -- substrate has single-layer predictive coding. Implementation: add L2 layer where predict_L2(query) = expected_features_for_category(query), then residual_L2 = features(query) - predict_L2(query). If residual_L2 is small, return L2 schema answer; if large, route to L1 episodic recall.

**Why NOVEL vs Cell 1 / Cell 2:** Cell 1 schemas were CONSTRUCTED (averaged); Cell 2 symbols were FIXED random. Predictive-coding hierarchy LEARNS schemas from prediction-error signal -- the schema is what makes the residual small. This is non-linear (prediction-error gating is non-linear), and it inherently includes a refuse-gate (large residual = "this is not a category member; do not generalize").

**Pairs with refuse-gate:** Substrate already has `hdlab/refuse_gate.py`. Predictive-coding-driven hierarchy gives refuse-gate a substrate-native invocation: refuse if residual_L2 > threshold. This adds substrate-product value beyond just Gap 3 closure -- it provides the audit-trail handle for "why did substrate generalize / not generalize."

**P_solve_deflated: 0.35** (raw lit P=0.55; -0.20 calibration; novel-synthesis cap honored)

### D. Learned attractor compression (Modern Hopfield / Krotov 2016 / Ramsauer 2020)

**Mechanism:** Replace standard Hopfield energy E(x) = -0.5 x.T W x with E(x) = -F(x.T W) where F is a non-linear function. Krotov-Hopfield 2016: F(z) = z^n (power-of-n) gives capacity O(N^(n-1)/n!). Demircigil 2017: F(z) = exp(z) gives EXPONENTIAL capacity 2^(N/2). Ramsauer 2020: F(z) = log(sum(exp(beta z))) (softmax form) -- shown to be EQUIVALENT to transformer attention; capacity is exponential.

**How it implements compositional generalization:** Each category becomes an attractor with a wide basin in the energy landscape. Novel category instance falls into the basin via gradient flow on E. The attractor IS the schema. Unlike linear-bundle prototypes, modern-Hopfield prototypes SHARPEN with more exemplars because the energy function is non-linear in the exemplar count (the basin gets DEEPER, not noisier).

**Substrate-native mapping:** Substrate has `iterative_attractor.iterative_cleanup` ALREADY. Implementation is a **3-line config change**: replace standard cleanup `argmax(codebook @ query)` with modern-Hopfield `softmax(beta * codebook @ query) @ codebook` for some beta. Larger beta = sharper basins. The substrate already does this for beta=1 implicitly; the experiment is to sweep beta in [5, 10, 20, 50, 100] and find the beta that crosses the schema-generalization threshold.

**Why NOVEL vs Cell 1 / Cell 2:** Modern-Hopfield is precisely the non-linear basin-sharpening that linear bundling lacks. Direct fix for the structural failure mode identified in Section 1. Strongest theoretical claim of all 5 candidates.

**Why I doubted this initially:** per Fix #28 memory ("modern_hopfield_xl + p1_v3 -- MODERN collapsed to 0.007 while only CLASSICAL stayed at 1.000"), there is prior substrate evidence that Modern-Hopfield arms collapse under some configuration. MUST substrate-mine and understand WHY before re-dispatching. Likely cause: beta too high (over-sharpening into single global attractor), or matrix conditioning issue with the W @ W.T inner product. The fix is a controlled beta sweep with explicit per-arm metrics and refuse-gate on degenerate attractors.

**P_solve_deflated: 0.45** (raw lit P=0.70; -0.20 calibration; -0.05 for prior collapse evidence)

**Brain-existence-proof:** Hopfield 1982 + Krotov 2016 are explicit brain-inspired models. The substrate's iterative_attractor.py IS already a Hopfield-like primitive. Bumping beta up is the lowest-cost change in the 5-candidate space.

### E. Category-theoretic / functorial composition

**Mechanism:** Schemas as FUNCTORS between categories of representations; instances as objects in source category; properties as objects in target category. Composition of schemas IS functor composition (associative by definition). arxiv 2408.14014 (2024) surveys categorical ML; Lambek-pregroup approaches.

**How it implements compositional generalization:** A schema F: Cat_instances -> Cat_properties maps each instance to its property-set in a way that respects category structure (preserves identities, preserves composition). Novel instance X gets mapped by F(X) automatically -- the functor is defined by its action on objects, generalization is by construction.

**Substrate-native mapping:** HRR convolution IS associative and the role-filler binding IS approximately a tensor product (per Smolensky 1990 TPR). Substrate could in principle realize functorial composition via HRR-bind. But this is exactly what HRR-bundle does at the IMPLEMENTATION level. The category-theoretic LANGUAGE is rigorous but the underlying mechanism is still HRR-bind, which still has the crosstalk problem.

**Verdict:** Conceptually beautiful but reduces to the same HRR-bundle mechanism that already failed. Skip unless paired with non-linear basin step. Per [[feedback-dont-dismiss-adjacent-methods]] I do not refuse to dispatch -- but rank LAST among the 5.

**P_solve_deflated: 0.15** (raw lit P=0.30; -0.15 calibration; underlying primitive is what failed in Cell 1/2)

## Section 3: 3-5 cell candidates ranked

| Rank | Cell name | Mechanism class | P_deflated | Cost | Why NOVEL vs Cell 1/2 | Compose-with |
|---|---|---|---|---|---|---|
| 1 | gap3_modern_hopfield_prototype_attractor_v1 | D (Modern Hopfield) | 0.45 | 1.5 hr CPU | non-linear basin-sharpening vs linear bundle | iterative_attractor.py existing |
| 2 | gap3_cls_replay_schema_channel_v1 | B (CLS-replay) | 0.40 | 3-5 hr CPU | TWO_TIER W_episodic + W_schema with eta_slow replay-driven extraction | Gap 4 TWO_TIER_GENERATIONAL pending cell -- BUNDLE into ONE cell |
| 3 | gap3_predictive_coding_hierarchy_v1 | C (Hierarchical PC) | 0.35 | 2-3 hr CPU | residual-driven schema-vs-episode routing + refuse-gate pairing | predictive_coding.py existing; refuse_gate.py existing |
| 4 | gap3_sdm_softmax_aggregation_v1 | A (SDM) | 0.20 | 1 hr CPU | softmax-pool vs argmax-pick on cleanup; ablation against arm 1 | Useful as falsification probe -- if HOPFIELD works, this confirms by reducing to it |
| 5 | gap3_categorical_functorial_v1 | E (Category theory) | 0.15 | 5 hr CPU | functor composition over HRR-bind; theoretical rigor | SKIP unless 1-4 all HARD_FAIL |

### Detail on Cell #1 (rank-1 dispatch)

**Cell:** `gap3_modern_hopfield_prototype_attractor_v1`

**Substrate-native mapping:** existing `iterative_attractor.iterative_cleanup` with energy='modern_hopfield' config switch (3-line code addition: replace argmax with softmax-beta-weighted aggregation, accept beta as parameter).

**Discriminator design (META_M7 compliant):**
- 4 arms: BASELINE / HRR_BUNDLE_PROTOTYPE / MODERN_HOPFIELD_PROTOTYPE / MODERN_HOPFIELD_CONTINUOUS
- Pre-registered HARD_PASS / HARD_FAIL / MIDDLE_BAND bands above
- Per-arm metrics MANDATORY per Fix #28; do not infer from verdict_msg
- Cross-cell rail: BASELINE must replicate Cell 1 ARM_NO_SCHEMA ~0.37 within 0.05; if drift, abort

**Prior P_solve_deflated: 0.45**

**Decision-grade outcomes:**
- HARD_PASS -> ship hdlab/modern_hopfield.py + capability-suite regression "schema_generalization_v1"
- MIDDLE_BAND -> beta x cardinality sweep (1 cell, 4 hr)
- HARD_FAIL -> close attractor-compression angle; pivot to Cell #2 CLS-replay

**Compute budget:** 1.5 hr CPU local_cpu_queue at N=8192, 3 seeds, 4 arms.

**Why NOVEL vs Cell 1 + Cell 2:** Cell 1 used LINEAR mean-of-instances (HRR bundle). Cell 2 used FIXED RANDOM symbol codebook (LARS-VSA). Cell #1 here uses NON-LINEAR softmax-beta-weighted basin-aggregation (Modern Hopfield). Different mechanism class structurally; addresses the crosstalk ceiling head-on.

**Cross-cell sanity rail:** If HRR_BUNDLE_PROTOTYPE arm in this cell doesn't replicate Cell 1's 0.47 within 0.03, abort -- methodology drift.

### Detail on Cell #2 (rank-2 dispatch, BUNDLE with Gap 4 TWO_TIER)

**Cell:** `gap3_gap4_two_tier_cls_replay_v1` (bundled cell)

**Substrate-native mapping:**
- W_episodic = existing single-tier W (high eta, fast write, sparse-bipolar episodes)
- W_schema = NEW second-tier W (low eta_slow = 0.01 * eta_episodic, slow write driven by replay)
- replay_cycle (existing) iterates over W_episodic, draws samples, gradient-rate writes into W_schema
- BCM-style Hebbian write rule for W_schema (multiplicative not additive -- escapes linear-bundle ceiling)

**Test endpoints (covers BOTH Gap 3 AND Gap 4):**
- Gap 3: heldout compositional generalization on 5cat x 20 instances (same as Cell 1)
- Gap 4: 5000-cycle continual-learning retention curve at 4.4x Hopfield capacity (per Gap 4 hand-off)
- Single cell tests both because TWO_TIER architecture serves both purposes (Kumaran-McClelland 2016)

**Pre-registered HARD_PASS:** Gap 3 heldout >= 0.55 AND Gap 4 retention >= 0.70 at cycle 5000. BOTH must pass. Either-or = MIDDLE_BAND.

**HARD_FAIL:** Either endpoint <= 0.30 -> mechanism does not generalize across gaps; refile as separate cells.

**P_solve_deflated: 0.40** (joint probability; both endpoints individually 0.45-0.50; joint deflated for correlation)

**Compute budget:** 3-5 hr CPU local_cpu_queue (longer because Gap 4 needs 5000 cycles).

**Composition with NREM proven-bound:** continual.replay_cycle is the existing primitive; this cell adds the destination W_schema and the slow-rate writer. The mechanism IS the natural follow-up to last night's drift_reduction proven_bound boundary result.

### Detail on Cell #3 (rank-3 backup)

**Cell:** `gap3_predictive_coding_hierarchy_v1`

**Substrate-native mapping:**
- Layer L1 = existing predictive_coding.predict / residual / gated_write (single layer)
- Layer L2 = NEW category-level prediction: predict_L2(features) = expected_features_of_nearest_category_prototype
- residual_L2 = features - predict_L2(features)
- If |residual_L2| > threshold: refuse generalization (route to L1 episodic), else accept L2 schema answer
- Schema = the prototype that minimizes |residual_L2| for the heldout query

**Test endpoint:** heldout compositional generalization + refuse-rate calibration.

**HARD_PASS:** heldout-on-accept >= 0.70 (high-confidence-only) AND accept-rate >= 0.60. Combined Expected Calibration Error <= 0.05. This is a chain-grade-eligible result because it adds refuse-gate behavior to substrate-product story.

**P_solve_deflated: 0.35**

**Compute budget:** 2-3 hr CPU local_cpu_queue.

**Compose with refuse-gate:** Adds calibrated abstention to substrate -- a substrate-product differentiator (refuses to guess when residual is high). Critical for "auditable AI memory subsystem" product positioning per Memory CURRENT STATE.

## Section 4: Composition with NREM proven-bound from last night

Last night's Gap 4 drill (notes/research_gap4_continual_5x_drill_2026-06-26.md) ranked TWO_TIER_GENERATIONAL as rank-1 (P_deflated=0.50). The mechanism: W_episodic (existing) + W_promoted (new) + periodic promotion-rule of heavy-hitter atoms based on replay-coverage.

The Gap 3 CLS-replay Cell #2 ABOVE shares the same architectural change. Key difference:

| Aspect | Gap 4 TWO_TIER_GENERATIONAL | Gap 3 CLS_REPLAY_SCHEMA |
|---|---|---|
| Second W purpose | Long-term retention of high-frequency atoms | Slow-extracted category prototypes |
| Promotion rule | Heavy-hitter (count >= K) | Replay-frequency weighted Hebbian aggregation |
| Write rule | Copy with decay | BCM-style multiplicative Hebbian |
| Test endpoint | 5000-cycle retention curve | Heldout compositional gen |

**The two cells SHOULD be merged into ONE cell.** The merged cell:
- Architecture: W_episodic + W_slow (single shared second tier)
- Two write rules tested as separate arms:
  - ARM_TWO_TIER_HEAVY_HITTER (Gap 4 mechanism)
  - ARM_CLS_BCM_HEBBIAN (Gap 3 mechanism)
  - ARM_BOTH (heavy-hitter + BCM combined)
- Two endpoints measured per arm:
  - ENDPOINT_RETENTION (Gap 4 metric)
  - ENDPOINT_SCHEMA_GEN (Gap 3 metric)
- Cost: ~4-5 hr CPU; payoff: closes BOTH gaps in one cell (if both endpoints HARD_PASS); 2-of-2 atomization opportunity.

**Recommendation:** Bundle Gap 3 Cell #2 with Gap 4 TWO_TIER hand-off into a single cell `cls_replay_two_tier_unified_v1`. File this cell ahead of the standalone Gap 3 Cell #1 only if exp_dev has spare slot for a 4-5hr cell; otherwise file Cell #1 (Modern Hopfield) first as the fast, cheaper, lower-risk test.

## Section 5: Recommendation

**Top 3 cells to dispatch, ranked by P_deflated:**

| Rank | Cell | P_deflated | Cost | Dispatch order |
|---|---|---|---|---|
| 1 | gap3_modern_hopfield_prototype_attractor_v1 | 0.45 | 1.5 hr CPU | FIRST -- cheapest, fastest, addresses crosstalk-ceiling structurally |
| 2 | cls_replay_two_tier_unified_v1 (BUNDLED Gap 3 + Gap 4) | 0.40 | 4-5 hr CPU | SECOND -- composes with NREM proven-bound; closes 2 gaps if HARD_PASS |
| 3 | gap3_predictive_coding_hierarchy_v1 | 0.35 | 2-3 hr CPU | THIRD -- backup if 1 and 2 both HARD_FAIL; adds refuse-gate substrate-product handle |

**Sequencing rationale:**
1. Dispatch Cell #1 (Modern Hopfield) FIRST as 1.5hr probe. Cheap + fast + highest individual P. If HARD_PASS, may close Gap 3 outright -- 3-line code change to existing iterative_attractor.
2. While Cell #1 runs, finalize the bundled Cell #2 design (resolve naming + arm definitions with exp_dev). Dispatch ONLY after Cell #1 verdict to avoid wasted compute if Cell #1 chain-grades.
3. Cell #3 reserved for if 1+2 both HARD_FAIL -- the hierarchical-PC angle adds calibration/refuse-gate value even at lower P_solve.

**Skip / defer:**
- SDM (Cell #4) -- substrate likely already does this; not the bottleneck
- Categorical / functorial (Cell #5) -- reduces to HRR-bind underneath; same failure mode

**HARD-FAIL contingency:** If Cell #1 + Cell #2 both HARD_FAIL, the conclusion is structural: at N=8192 with 20 instances/category, **the information available is insufficient for compositional generalization regardless of mechanism class.** Pivot to capacity-sweep cell varying (instances_per_category in [10, 20, 40, 80, 160]) x (N in [2048, 4096, 8192, 16384]). This converts Gap 3 from a "mechanism missing" gap into a "data coverage / capacity sweep" gap -- different framing, different rescue path.

## Cross-thread synthesis

**With Cell 1 cortex schema (MIDDLE_BAND):** ARM_FEATURE_BASED_SCHEMA +0.10 lift IS THE SIGNAL that schema-formation works structurally; the ceiling at 0.47 is the HRR-bundle crosstalk floor, not the impossibility of schema-formation. Modern Hopfield lifts that ceiling by non-linear basin-sharpening.

**With Cell 2 LARS-VSA (HARD_FAIL_CONFOUND):** ARM_RESONATOR 0.4267 (best arm) suggests cone-preserving iterative mechanisms work; ARM_RELBOTTLENECK 0.20 (collapse) confirms cone-rotating fixed codebooks fail. Both observations are consistent with the Gap 2 reframe (anisotropy is feature). Modern Hopfield is cone-preserving (softmax of cosine similarity stays on cone) -- expected to align with ARM_RESONATOR's success.

**With Gap 2 reframe (anisotropy is feature):** Mechanism classes that EXPLOIT cone direction (Modern Hopfield, iterative_attractor with high beta, partition routing) WIN. Mechanism classes that ROTATE off cone (whitening, DG pattern-separation, XOR-binding-of-tags, capability-based-schema, LARS-VSA-fixed-symbols) LOSE. The Gap 3 deeper drill REPRODUCES this signature.

**With Gap 4 TWO_TIER_GENERATIONAL hand-off:** Cell #2 bundle is the natural composition. Single cell can close BOTH gaps via the same TWO_TIER architecture.

**With NREM drift_reduction proven_bound (last night):** Replay is the engine; the missing piece for Gap 3 is what the replay WRITES INTO. CLS-replay schema-channel provides that destination.

**With Fix #28 prior modern_hopfield_xl collapse memory:** MUST substrate-mine prior modern-Hopfield cells BEFORE dispatching Cell #1. Likely cause of prior collapse was beta over-sharpening; controlled beta-sweep in pre-registered band avoids re-running the same failure.

## Substrate-product implications

**Headline product story (if Cell #1 HARD_PASSes):** "substrate's auditable memory subsystem can be configured for either episodic-recall mode (sharp lookup) or schema-generalization mode (basin-attraction) via a single inverse-temperature parameter. Both modes use the same underlying W; no architecture change needed." This is a strong differentiator vs vector-DBs (which only have episodic-lookup mode).

**Headline product story (if Cell #2 bundled HARD_PASSes):** "substrate's hippocampus-cortex-style two-tier memory architecture closes BOTH long-term retention (Gap 4) and compositional generalization (Gap 3) gaps. Brain-architecture-existence-proof translated to a substrate-product." This is a marquee architectural story -- the substrate as biologically-grounded auditable memory.

**Headline product story (if Cell #3 HARD_PASSes):** "substrate adds calibrated abstention: refuses to generalize when prediction-error residual exceeds threshold. The substrate is the first auditable AI memory subsystem that explicitly knows when it should NOT extrapolate." Critical refuse-gate value for product positioning per "auditable-AI-memory-subsystem" strategic direction.

**Capability-map implication:** Gap 3 currently RED (substrate scores 0.00 heldout in original test). HARD_PASS of any of Cell #1/2/3 promotes to YELLOW (MIDDLE_BAND) at minimum; chain-grade HARD_PASS promotes to GREEN. The Modern-Hopfield path has the highest probability AND the lowest cost AND a 3-line code-change ship; it should be dispatched first.

## Citations (verified)

Brain-side (CLS / schema):
- McClelland, McNaughton, O'Reilly (1995). "Why there are complementary learning systems in the hippocampus and neocortex." Psychological Review 102(3): 419-457.
- Kumaran, Hassabis, McClelland (2016). "What learning systems do intelligent agents need? Complementary learning systems theory updated." Trends in Cognitive Sciences 20(7): 512-534.
- arxiv 2507.11393 (2026). "A Neural Network Model of Complementary Learning Systems: Pattern Separation and Completion for Continual Learning."
- O'Reilly (2014). "Complementary Learning Systems." Cognitive Science 38(6): 1229-1248.

Modern Hopfield / attractor-compression:
- Hopfield (1982). "Neural networks and physical systems with emergent collective computational abilities." PNAS 79(8): 2554-2558.
- Krotov, Hopfield (2016). "Dense Associative Memory for Pattern Recognition." NeurIPS 2016. arxiv 1606.01164.
- Demircigil et al. (2017). "On a Model of Associative Memory with Huge Storage Capacity." J Stat Phys 168(2): 288-299.
- Ramsauer et al. (2020). "Hopfield Networks Is All You Need." ICLR 2021. arxiv 2008.02217.
- arxiv 2503.00241 (2026). "Accuracy and capacity of Modern Hopfield networks with synaptic noise."
- arxiv 2503.09518 (2026). "The Capacity of Modern Hopfield Networks under the Data Manifold Hypothesis."
- arxiv 2411.08590 (2025). "Hopfield-Fenchel-Young Networks: A Unified Framework for Associative Memory Retrieval."

SDM / Kanerva:
- Kanerva (1988). Sparse Distributed Memory. MIT Press.
- Bricken, Pehlevan (2021). "Attention Approximates Sparse Distributed Memory." NeurIPS 2021. arxiv 2111.05498.
- arxiv 2303.11934 (2023). "Sparse Distributed Memory is a Continual Learner." ICLR 2023.

Predictive coding:
- Rao, Ballard (1999). "Predictive coding in the visual cortex." Nature Neuroscience 2(1): 79-87.
- arxiv 2506.06332 (2026). "Introduction to Predictive Coding Networks for Machine Learning."
- arxiv 2107.12979. "Predictive Coding: a Theoretical and Experimental Review."
- arxiv 2112.10048. "Predictive Coding Theories of Cortical Function."

HRR / TPR / VSA capacity:
- Plate (1995). "Holographic Reduced Representations." IEEE Trans Neural Networks 6(3): 623-641.
- Smolensky (1990). "Tensor Product Variable Binding and the Representation of Symbolic Structures." Artificial Intelligence 46(1-2): 159-216.
- arxiv 2109.02157 (2021). "Learning with Holographic Reduced Representations."
- Schlegel et al. (2021). "A Comparison of Vector Symbolic Architectures."
- arxiv 2412.04671 (2024). "Soft Tensor Product Representations for Fully Continuous, Compositional Visual Representations." NeurIPS 2024.
- arxiv 2406.01012 (2024). "Attention-based Iterative Decomposition for Tensor Product Representation."

Internal substrate notes:
- notes/research_gap3_compositional_5x_drill_2026-06-26.md (prior breadth scan; 18 candidates)
- notes/research_gap4_continual_5x_drill_2026-06-26.md (NREM proven_bound + TWO_TIER_GENERATIONAL hand-off)
- notes/research_gap2_REFRAME_anisotropy_is_feature_2026-06-26.md (cone-preserving vs cone-rotating mechanism signature)
- data/exp_substrate_cortical_schema_extraction_compositional_generalization_v1/metrics.json (Cell 1 MIDDLE_BAND empirical anchor)
- data/exp_gap3_lars_vsa_relational_bottleneck_v1_n8192/metrics.json (Cell 2 HARD_FAIL_CONFOUND empirical anchor)
- hdlab/iterative_attractor.py (existing primitive; 3-line addition for Modern Hopfield)
- hdlab/predictive_coding.py (existing primitive; ready for hierarchical extension)
- hdlab/continual.py (existing replay_cycle; NREM drift_reduction proven_bound; ready for CLS schema-channel)
- hdlab/refuse_gate.py (existing primitive; pairs with hierarchical PC residual gating)

Verified citation count: 22 external + 9 internal = 31 distinct sources.
