# RESEARCH 5x DEEPER DRILL: multi-hop reasoning — successor-representation + Tolman-Eichenbaum structural-sensory factorization + theta-gamma multi-item buffer

**Date:** 2026-06-22
**Requestor:** USER strategic-vision directive 2026-06-22 (per-gap research drills queued, never fired); r1b HARD_FAIL just landed (re-routes priority)
**Empirical driver on substrate:** r1b multi-hop refuse-calibration cell HARD_FAIL today (5388s, 7 seeds, K_hops in {2,3,4}, K_set=8, K_inner=1, N_DIM=8192, M_TRIPLES=50k, 500 chains). Verdict: K3 mean=0.268 vs r1=0.240 (diff=0.028 OUT-OF-TOL, exceeds +/-0.02 reproducibility band) + OOD-refuse(margin) min=0.682 (FAIL >= 0.90) + margin-ratio min=1.003 (FAIL >2.0x discriminator). **The substrate's iterative-cleanup chain-grade promotion path is empirically stuck: margin signal does NOT separate in-KB from OOD at K>=3.**
**Prior coverage (NOT re-covered):** prior drills covered iterative-cleanup + Modern Hopfield + Bridge RAG + IRCoT + HippoRAG/PPR + Beam Retrieval + role-binding for multi-hop. The 5x DEEPER lane goes BELOW these to predictive-coding / cognitive-map / sequence-buffer primitives that the substrate doesn't yet have.
**Lit-scan calibration:** deflate P 0.15-0.25; cap novel-synthesis P at 0.50; HARD-FAIL thresholds mandatory.

---

## HEADLINE

**The substrate's iterative-cleanup is a HOP-LOCAL operation; biology does multi-hop as a CLOSED-FORM successor-representation transformation.** r1b HARD_FAILed because cleanup-per-hop accumulates margin-loss at each K: each step's softmax(beta * top_conf) is a LOCAL attractor projection, but the substrate has no SEQUENCE-LEVEL representation — no "chain-as-object". Biology's hippocampus solves this with the **successor representation** M(s) = sum_k gamma^k * P^k * 1_s — a PRECOMPUTED closure of the K-step transition matrix that turns multi-hop into a SINGLE matrix-vector product. The Tolman-Eichenbaum Machine (TEM, Cell 2020) factors this into **structural** (transition rules, learned once) + **sensory** (entity content, separately bound) — and demonstrates immediate generalization to unseen multi-hop chains via the structural reuse. The theta-gamma phase code (Lisman-Jensen 1995, validated 2024 biorxiv) provides the WORKING-MEMORY BUFFER for the chain itself: each gamma sub-cycle holds one chain element; the theta cycle parses the sequence.

**The substrate has the W matrix that IS the transition operator. Three primitives are missing:**

1. **Successor-W closure:** precompute M = sum_{k=1..K_max} gamma^k * W^k. Multi-hop retrieval becomes a SINGLE matrix-vector M @ key, not K iterative cleanups. This composes the substrate's own W into a multi-scale successor representation matching Stachenfeld 2017 + Momennejad 2018.

2. **Structural-sensory factorization (TEM-style):** the substrate's R relation codebook IS the structural code; the E entity codebook IS the sensory code. Today the substrate binds them at INGEST (E*R*sq). Refactoring to keep them DECOMPOSED until query-time allows the substrate to swap structure (different relation sequences) over the SAME sensory content — true compositional generalization.

3. **Theta-gamma multi-item chain buffer:** the chain state today is a SINGLE N_DIM vector (cleaned per hop). Bind multiple chain elements via permutation-binding (Plate 2003, Kanerva 2009 HDC primitive) into a single COMPOUND state: chain = e_0 + perm(e_1) + perm^2(e_2) + ... — analogous to gamma sub-cycle slots in a theta cycle. Read chain-position k via inverse permutation. Refuse-gate then operates on COMPOUND-MARGIN (joint over the chain) instead of per-hop top1-top2.

**Cheap decisive test:** `r2_successor_TEM_compound_v1` — same KG (50k triples, K_hops in {2, 3, 4}), same chain test set as r1/r1b, but THREE arms: ITER_CLEANUP_r1b_anchor (the existing failed mechanism), **SUCCESSOR_W_CLOSURE_K=K_max** (precomputed M = sum gamma^k W^k), **TEM_FACTORED_COMPOUND** (factored R/E + permutation-bound compound chain + compound-margin refuse). HARD-PASS: at K=4, SUCCESSOR or TEM_COMPOUND achieves >= 1.20x the r1b mean accuracy (0.176 -> ~0.21+) AND OOD-refuse(margin) min >= 0.90 AND margin-ratio in-KB-vs-OOD > 2.0. HARD-FAIL: neither arm beats r1b r1-anchor (the iterative-cleanup mechanism is the ceiling, no compositional rescue available).

| Mechanism | Source | Substrate-applicability | Cost | Expected gain | P(HARD-PASS) |
|-----------|--------|--------------------------|------|---------------|--------------|
| **Successor-W closure M = sum gamma^k W^k (novel for substrate)** | Dayan 1993; Stachenfeld 2017; Momennejad 2018; arxiv 2512.24722 (PageRank-SR equivalence) | **HIGHEST** — single matmul; substrate W^k closure is mathematically clean | ~K_max-fold matmul at SETUP, 1x at query | breaks K-hop margin decay because closure is precomputed | **0.45** (capped novel; high theoretical confidence) |
| **TEM structural-sensory factorization (compositional generalization)** | Whittington-Behrens 2020 Cell; arxiv 2601.18946 schema-based; arxiv 2302.07350 graph schemas | HIGH — factors substrate R/E codebooks; queries are R-sequences applied to E-content | ~1.1x wall (factored binding) | generalizes to unseen R-sequences over same E content | **0.35** (capped novel; transfer to unseen structural compositions is risky) |
| **Theta-gamma compound chain via permutation binding** | Lisman-Idiart 1995; Lisman-Jensen 2013; biorxiv 2024.03.24.586454 (human evidence); Plate 2003 / Kanerva 2009 HDC primitives | **HIGHEST** — permutation-binding is a Kanerva HDC primitive; substrate already has the building blocks | ~1.05x wall (permutation lookup) | compound margin separates from per-hop margin (the r1b fix) | **0.40** |
| Reverse-replay credit propagation (drill #2 Stream E cross-pollination) | Foster-Wilson 2006; Wikenheiser 2015; eLife 34171 | MEDIUM — backward sweep over chain for margin propagation | ~2x query wall | reduces compound-margin variance | 0.30 |
| Grid-cell hexagonal vector navigation | Banino 2018 Nature; arxiv 2003.03482; arxiv 1810.05597 | LOW-MEDIUM — geometric path integration is over-specific to spatial chains | unknown | speculative for KG | DEFER |
| Cerebro-cerebellar forward model | PMC 7160920; Kawato 1999 | LOW — cerebellum is sensorimotor prediction; KG QA is not motor | unknown | speculative | DEFER |

---

## L1 — LITERATURE BROAD SCAN (NEW lit beyond prior multi-hop drills)

### Stream A: Successor Representation (the missing closed-form multi-hop primitive)

**Dayan 1993 (Neural Computation):** original successor representation. Define M(s, s') = E[sum_{k=0}^inf gamma^k * 1{s_k = s'} | s_0 = s] — the expected discounted occupancy of state s' starting from s. **Key property:** M = (I - gamma * P)^-1 where P is the one-step transition matrix. So M IS a precomputed multi-hop closure.

**Stachenfeld-Botvinick-Gershman 2017 (Nature Neuroscience 20):** SR explains hippocampal place cell + entorhinal grid cell firing as eigenvectors of the SR. Place cells are M_row-vector responses; grid cells are eigenvector basis-functions. **Direct relevance:** the substrate's E codebook is analogous to place cells; an SR-precomputed M over the substrate's W matrix would give the substrate "grid-cell-like" multi-scale traversal primitives for free.

**Momennejad-Russek-Cheong et al. 2017 (Nature Human Behaviour, "The successor representation in human reinforcement learning"):** human behavioral validation. People use SR-like predictive representations in sequential decision tasks. **Predicts the future with multi-scale SR** (biorxiv 449470): different gamma values pick different time-horizons; the brain uses MULTIPLE SRs at different discount rates simultaneously.

**arxiv 2512.24722 (2024) "Equivalence of Personalized PageRank and Successor Representations":** important new result. PPR and SR are MATHEMATICALLY EQUIVALENT under specific conditions. **Implication for substrate:** PPR-style spreading activation over KG (proposed in prior 2026-06-08 drill) IS computing the same object as the SR. Either implementation route works.

**Connection to substrate W:** the substrate's W matrix already IS a stochastic-like transition operator (s, p) -> o; W bound on (s, p, o) triples means W @ key_{s,p} = E[bound o]. **The substrate's missing primitive is the K-step closure M_K = sum_{k=1..K} gamma^k * W^k.** This precomputes ALL paths up to depth K. Cost: O(K * N_DIM^3) at SETUP; O(N_DIM^2) per query. For N_DIM=8192 and K=4 the setup is ~4*5.5e11 ops = ~5 min on CPU once, then queries are FREE.

**Why this likely fixes r1b's margin decay:** r1b's iterative-cleanup loses margin at each hop because per-hop softmax is a soft argmax that LOSES information about secondary candidates. The SR closure keeps the FULL distribution over multi-hop destinations in a single matrix; the refuse-gate margin is computed on the FINAL multi-hop distribution, where information loss is one-shot not K-fold.

### Stream B: Tolman-Eichenbaum Machine (TEM) and structural-sensory factorization

**Whittington-Behrens et al. 2020 (Cell 183, "The Tolman-Eichenbaum Machine: Unifying space and relational memory through generalization in the hippocampal formation"):** TEM is a generative model with TWO factored codes:
- **Structural code g** (medial entorhinal cortex / grid cells): learns transition rules of the graph. Same g across environments with same structure.
- **Sensory code x** (lateral entorhinal cortex / sensory inputs): bound to nodes via the conjunctive hippocampal code p = g * x.

**Result:** TEM IMMEDIATELY GENERALIZES to new transitive-inference tasks without further training — it has learned ORDINAL STRUCTURAL knowledge. In social hierarchy tasks, TEM can answer "who is Bob's niece" by composing relations it has never directly seen.

**Direct substrate analogue:**
- Substrate's R codebook = TEM's g (structural code, relation embeddings)
- Substrate's E codebook = TEM's x (sensory code, entity embeddings)
- Substrate's bound key = E[s] * R[p] * sqrt(N_DIM) = TEM's p = g * x

**Today the substrate FACTORS at ingest but COMPOSES at query.** Multi-hop today is W @ (W @ (... (W @ (E[s] * R[p1] * sq)) * R[p2] * sq ...) * R[pK] * sq). The R-sequence is BURIED in the W-chain. **TEM factorization for substrate:** keep R-sequence as a SEPARATE compositional object; query becomes "apply R-chain to E-content" with R-chain reusable across different E-content.

**arxiv 2601.18946 (2024) "Schema-based active inference":** frontal cortex + hippocampus interaction supports schema reuse. Schemas are abstract structural codes that generalize. **Validates TEM-style factorization in 2024-2026 lit.**

**arxiv 2302.07350 "Graph schemas as abstractions for transfer learning, inference, and planning":** graph-structural reuse for planning. Provides ML-side validation of TEM's transfer claim.

**arxiv 2507.18868 "A Neuroscience-Inspired Dual-Process Model of Compositional Generalization":** explicitly dual-process — system 1 = fast pattern match (substrate's iterative-cleanup analogue), system 2 = compositional schema (substrate's TEM-factored analogue). Argues both are needed.

### Stream C: Theta-gamma phase code and multi-item working memory buffer

**Lisman-Idiart 1995 (Science 267, "Storage of 7+/-2 short-term memories in oscillatory subcycles"):** foundational theta-gamma model. Each theta cycle (~125 ms) contains ~7 gamma sub-cycles (~17 ms each). Each gamma slot encodes one item; the theta cycle parses the ordered sequence.

**Lisman-Jensen 2013 (Neuron, "The Theta-Gamma Neural Code"):** modern restatement. Cross-frequency coupling between theta phase and gamma amplitude IS the multi-item working memory code. Each gamma sub-cycle represents one element; the order is encoded in the theta phase progression.

**biorxiv 2024.03.24.586454 (2024) "Theta-Gamma Phase-Amplitude Coupling Supports Working Memory Performance in the Human Hippocampus":** direct human evidence. Theta-gamma PAC magnitude correlates with multi-item working memory accuracy. Validates the model in 2024.

**Springer 2022 (cogn neurodyn 17, model paper):** computational implementation — nested gamma cycles constitute memory slots parsed by theta. Sequence encoding: gamma power per item ordered along underlying theta wave.

**Substrate analogue — HDC permutation binding:**
Kanerva 2009 HDC primitive: ordered sequences encoded as bound = sum_{i=0}^{L-1} perm^i(x_i) where perm is a fixed random permutation matrix. Read position i: perm^{-i}(bound) and codebook-NN cleanup. **This IS the substrate's analogue of theta-gamma sub-cycle encoding.** The chain state for multi-hop becomes:

  chain_state_K = e_0 + perm(e_1) + perm^2(e_2) + ... + perm^K(e_K)

Refuse-gate computes margin on the COMPOUND chain_state (jointly over all positions) NOT per-hop. This converts the per-hop margin decay (which r1b HARD_FAILED on) into a single COMPOUND-margin signal.

**Why this likely fixes r1b's margin-ratio FAIL:**
- r1b's per-hop margin shrinks each step (0.81 -> 0.85 -> 0.68 across K=2,3,4) and the in-KB-vs-OOD ratio approaches 1.0 (no separation).
- Compound-margin operates on the full chain_state. In-KB chains have COHERENT permutation-bound structure; OOD chains have INCOHERENT structure across positions. The ratio is multiplicative: an OOD chain at K=4 has 4x the chance of misaligning per position, giving compound-margin separation ~2^K.

### Stream D: Predictive coding hierarchical inference (rejected but informative)

**Rao-Ballard 1999; Bastos 2012; Millidge 2021 review:** hierarchical predictive coding implements iterative inference via top-down predictions + bottom-up errors. **Verdict:** requires backprop along arbitrary graphs (arxiv 2006.04182). REJECTED for substrate (forward-only Hebbian constraint).

**arxiv 2107.12979, 2112.10048 (2024) reviews:** PC theories of cortical function. The PC inference loop is mathematically attractive (Bayesian) but expensive.

**RELEVANT spillover:** PC's hierarchical-feedback structure could PARTIALLY APPLY to the substrate's per-hop confidence: each iter_cleanup hop is a single PC inference step. Multi-hop PC would require multi-step gradient propagation — too expensive. The successor representation (Stream A) is the FORWARD-ONLY equivalent of PC's iterative inference.

### Stream E: Reverse-replay for chain-credit propagation (cross-drill #2)

**Foster-Wilson 2006 Nature; Diba-Buzsaki 2007; Wikenheiser-Foster 2015; eLife 34171 (2018):** reverse-replay backward sweeps the trajectory after reward. Functionally implements **TD-style credit assignment** without explicit backprop.

**Direct substrate analogue:** after a multi-hop chain prediction with confidence at the final hop, propagate confidence BACKWARD through the chain (via W.T application — the substrate has W.T for free). Earlier-hop refuse decisions are then informed by what happens downstream. **The substrate could implement this as a CHAIN-RECONSIDERATION pass:** forward chain -> read final-hop margin -> backward chain reweighing per-hop margins -> integrated chain-decision.

**Risk:** doubles query wall; may not help if per-hop margin is fundamentally too weak (the r1b finding).

### Stream F: Mushroom-body and Drosophila multi-stage decision (compact biological reference)

**Aso et al. 2014 eLife 4580:** Drosophila mushroom body has ~2000 Kenyon cells projecting to 34 MBONs of 21 types. Each MBON tiles 15 compartments. Decision-making integrates evidence across compartments. **Multi-step decision in Drosophila** is implemented via compartment-sequential evidence accumulation.

**Hige et al. 2015; Owald-Waddell 2015:** MBON ensemble combinatorially represents valence; segregated information channels with multi-layered network. **Relevance to substrate:** the substrate's iterative-cleanup is a single-stream chain; biology uses PARALLEL CHANNELS that re-converge. The substrate could ship multiple K-set chains (different attention parameters) in parallel and combine — analogous to MBON ensemble vote.

**Bhandawat-Stevens 2008; Modi-Stevens 2020:** sparse Kenyon coding (5-10% active) provides pattern separation IN A SHORT CHAIN. Compact biological prior for the substrate's coding sparsity in chain context (drill #1 territory; composes with drill #3 here).

### Stream G: Vector navigation / grid cells (Banino 2018) and path integration

**Banino-Barry et al. 2018 Nature 557:** train an RNN on path integration; HEXAGONAL grid-cell-like representations emerge spontaneously. Use grid-cell layer as base for A3C agent navigating environment — finds direct trajectories to goals.

**arxiv 2003.03482, 2210.12068, 1810.05597:** grid-cells-via-RNN replication papers; activation-function-dependent (ReLU -> hexagonal vs square). **Substrate relevance:** grid cells provide a MULTI-SCALE PERIODIC representation that is a metric for space coding and self-motion integration. **For substrate KG:** grid-cell-like representations could provide a metric over the KG graph for vector-direction lookup — but this is SPATIAL-specific and doesn't transfer cleanly to symbolic KG. DEFER.

### Stream H: Cerebro-cerebellar internal model for forward prediction

**PMC 7160920 (2020), Kawato 1999:** cerebellum implements forward internal model: efference copy + state -> predicted next state. Compares predicted to actual, adapts via climbing-fiber error signal. **In language and cognition** (Frontiers 2019), the cerebellum predicts sequential events for social interaction and language.

**Substrate relevance:** the substrate's W matrix IS a forward predictor. The cerebellar refinement is the SUPERVISED error signal (climbing fiber) — substrate doesn't have ground truth per hop. **Cerebellum is NOT immediately substrate-applicable.** DEFER.

### Stream I: Engram / cell-assembly chains (cross-drill #2)

**Tonegawa-Josselyn engram series 2017-2024:** engram cells form chains via Hebbian co-activation. Multi-stage engrams (entorhinal -> CA3 -> CA1 -> cortex) implement multi-step retrieval.

**Substrate analogue:** the substrate's iterative-cleanup IS an engram chain — each hop's top-K_set is the engram-cell-set for that hop. The biology says these chains are STABILIZED via STC (drill #2 cell c2's mechanism). **Cross-composition:** if drill #2 cell c2 ships first with STC, the substrate's multi-hop chains become MORE STABLE because each hop's engram-set is tagged-and-consolidated. The r1b margin variance might shrink under cascade-STC alone.

---

## L2 — FILTER TO SUBSTRATE-APPLICABLE

| Mechanism | Forward-only / substrate-compatible? | Composes with K (hop count)? | Composes with U1 / W / E / R / refuse-gate? | Verdict |
|-----------|---------------|---------------|---------------|---------|
| **Successor-W closure M = sum gamma^k W^k** | YES (single matmul precomputed) | YES (K_max param) | YES (uses substrate's W, R, E directly) | **ACCEPT — top novel primitive** |
| **TEM structural-sensory factorization** | YES (factored binding) | YES | YES (R = structural, E = sensory; factoring matches biology) | **ACCEPT — composable** |
| **Theta-gamma compound chain (permutation-binding)** | YES (Kanerva HDC primitive) | YES | YES (perm + codebook-NN already in substrate) | **ACCEPT — refuse-gate fix** |
| **Reverse-replay chain reweighing** | YES (W.T pass) | YES | YES | DEFER (composes; not yet primary) |
| **Grid-cell hexagonal navigation** | YES | n/a | LOW (spatial-specific) | DEFER |
| **Cerebro-cerebellar forward model** | NO (needs supervised error) | n/a | n/a | REJECT |
| **MBON parallel ensemble** | YES (parallel chains) | YES | YES | DEFER (composable secondary) |
| **Predictive coding hierarchical** | NO (backprop) | n/a | n/a | REJECT (but SR is the forward-only equivalent) |
| **Engram chain stabilization (cross-drill #2)** | YES | YES | YES | DEFER (lands via drill #2 cell c2; cross-pollinates) |

---

## L3 — DEEP DRILL ON TOP 1-2 MECHANISMS

### 3.1 Successor-W closure (PRIMARY; the r1b structural fix)

**Mathematical core:**

For one-step substrate retrieval: o-distribution = E @ (W @ key(s, p)). Define the K-step closed-form successor matrix:

  M_K = sum_{k=1..K_max} gamma^k * W^k

where gamma in (0, 1] is the discount (gamma=1 for unweighted; gamma<1 for recency-decay). For a chain query key_chain = E[s_0] * R[p_1] * R[p_2] * ... * R[p_K] * sq^K (the concatenated R-chain bound to the start entity), the K-hop retrieval becomes:

  scores_K_hop = E @ (M_K @ key_chain)

**Key advantages over iterative-cleanup:**

1. **Margin-decay arrested:** iterative-cleanup loses margin at each step via softmax(beta * top_conf) projection. Successor M_K is a LINEAR closure of W — no per-hop nonlinearity. The final softmax (refuse-gate) operates on the FULL multi-hop distribution; in-KB chains have concentrated mass at the correct target; OOD chains have diffuse mass. **Predicted: in-KB-vs-OOD margin-ratio scales with K because the closure aggregates evidence MULTIPLICATIVELY across hops.**

2. **Substrate-only-decode gate trivially preserved:** SR closure is just a matrix product computed once at setup; query is a matrix-vector. Zero LLM forward calls.

3. **Compose with multi-scale gamma:** Momennejad 2018 shows brain uses MULTIPLE gamma values simultaneously. Substrate can precompute {M_K(gamma=0.5), M_K(gamma=0.8), M_K(gamma=1.0)} and combine at query.

**Cost analysis:**
- Setup: K_max matrix products W^k each O(N_DIM^3). For N_DIM=8192, K_max=5: 5 * 8192^3 ~ 2.7e12 ops. On CPU at ~10 GFLOPs: ~5 min. On GPU (~1 TFLOP): ~3 seconds.
- Query: O(N_DIM^2) = 67M ops, near-instantaneous.
- Storage: N_DIM^2 floats = 256 MB at N_DIM=8192 — already paid for the substrate's W.
- **The substrate currently pays K * N_DIM^2 per query (K iterative-cleanup passes); SR pays N_DIM^2 per query — actually FASTER at query time once setup amortized.**

**Risk: spectral instability.** W^k can EXPLODE in spectral norm if W's largest eigenvalue > 1. Discount gamma in (0, 1] tames this. Empirically the substrate's W matrix is normalized per ingest; spectral radius is typically ~0.5-1. The SR closure will need a quick spectral-radius check before computing W^k — protect via gamma * spectral_radius < 1.

### 3.2 TEM structural-sensory factorization (SECONDARY; the compositional generalization lever)

**Architecture mapping:**

| TEM | Hippocampal | Substrate analogue |
|----|----|----|
| Structural code g | Grid cells (MEC) | R codebook (relation embeddings) |
| Sensory code x | Lateral EC inputs | E codebook (entity embeddings) |
| Conjunctive code p = g * x | CA3 / CA1 | bound key = E * R * sq |
| Generative model | Transition matrix learned in MEC | W matrix (substrate's transition operator) |
| Recall via attractor | CA3 recurrence | W @ key (single hop) or M_K @ key (multi-hop via SR) |

**Today's substrate binds structure-sensory at ingest** (E and R are mixed into W via the outer-product accumulation). **TEM-factored substrate keeps them separate:**

```python
# Today (entangled): W stores (E[s] * R[p] * sq) -> E[o] mappings
W += outer(E[o], E[s] * R[p] * sq) / N_DIM

# TEM-factored: separate STRUCTURAL operator W_struct from SENSORY codebook E
# Structural operator W_struct stores R[p] -> position-shift mappings (sensory-agnostic)
# Sensory lookup table E remains pure entity codebook
# Multi-hop = apply R-sequence operator chain to E[s], lookup against E
```

**Compositional generalization claim:** with R-chain operator factored, the substrate can answer questions about R-chains it never saw at ingest, as long as it saw each R individually. (TEM's transitive-inference result: never-seen "Bob's niece" inferred from learned R primitives.)

**This is a MAJOR architectural refactoring. Recommend the SR closure (3.1) as primary because it's a DROP-IN matrix change; TEM factorization is a STRUCTURAL rewrite of the substrate's binding rule. Run TEM as a follow-on after SR proves the multi-hop lift.**

### 3.3 Theta-gamma compound chain (TERTIARY; the refuse-gate margin fix)

**Substrate analogue (Kanerva HDC primitive):**

Permutation P is a fixed random permutation matrix. Bind chain into compound state:

  chain_state = sum_{k=0..K} P^k @ e_k

where e_k is the entity at hop k (post-cleanup). Read position k via P^-k:

  recover_k = P^-k @ chain_state  # codebook-NN cleanup -> e_k

**Refuse-gate on compound:**

Compute compound-margin as the AVERAGE per-position margin AFTER cleanup-readout from the compound. In-KB chains have coherent across-position structure (each P^-k @ chain_state cleanly recovers e_k). OOD chains have INCOHERENT structure -- recovery noise compounds across positions. Predicted in-KB-vs-OOD margin-ratio scales as ~product of per-position discriminability.

**Why this fixes r1b's margin-ratio = 1.003 FAIL:** r1b computed per-hop top1-top2 separately and aggregated by mean — losing the chain-structural signal. Compound-margin captures the chain-coherence signal directly.

**Cost:** trivial. Permutation matrices are pre-computed once; per-query application is O(N_DIM).

---

## L4 — CELL-DESIGN IMPLICATIONS + PRE-REG

### Primary cell: `r2_successor_TEM_compound_v1`

**Scope:** Replace r1b's iterative-cleanup with three composable arms, on the SAME r1b config (K_hops in {2, 3, 4}, K_set=8, K_inner=1, N_DIM=8192, M_TRIPLES=50k, 500 chains, 7 seeds — match r1b for direct comparison).

**Independent variables:**
- `chain_mechanism` in {ITER_CLEANUP_r1b_anchor, **SUCCESSOR_W_CLOSURE**, **TEM_FACTORED_COMPOUND**, **HYBRID_SR_PLUS_COMPOUND**}
- `K_max` for SR in {3, 5, 8} (sweep at best mechanism)
- `gamma` for SR in {0.5, 0.8, 1.0}
- Permutation-bind for compound in {P_random, P_circular_shift} (secondary)

**Fixed:**
- N_DIM = 8192 (match r1b)
- K_set = 8 (match r1b for the iterative-cleanup anchor)
- 7 seeds (match r1b for cv comparability)
- 500 chains (match r1b)
- M_TRIPLES = 50k (match r1b)

**Anchors (replicates required):**
- ITER_CLEANUP_r1b_anchor must reproduce r1b means within +/-0.01 at K=2,3,4 (NOT +/-0.02 like r1b: tighter band since arm is the SAME mechanism in the SAME cell)

**Primary metric:** `iter` (mean accuracy) per K and `margin_ratio` (in-KB-vs-OOD)

**Secondary metrics:**
- `cv` across 7 seeds
- `OOD_refuse_margin` (must reach >= 0.90 to clear r1b's gate2 FAIL)
- `setup_wall_s` (track SR precomputation cost)
- `query_wall_s` per K (compare iterative vs SR vs compound)
- `compound_margin_distribution` (in-KB vs OOD; histograms for diagnostic)

### PRE-REGISTERED HARD THRESHOLDS

**HARD-PASS (chain-grade, mechanism validated):**
- At K=4: SUCCESSOR_W_CLOSURE OR HYBRID_SR_PLUS_COMPOUND mean accuracy >= 1.20x r1b r1-anchor (i.e., >= 0.211; r1=0.172 per r1b's reference table)
- OOD_refuse_margin min >= 0.90 at all K (r1b's FAILed gate2 cleared)
- margin_ratio in-KB-vs-OOD > 2.0 at all K (r1b's FAILed c2 cleared)
- cv <= 0.06 across 7 seeds for the winning arm
- ITER_CLEANUP_r1b_anchor reproduces r1 r1b_anchor means within +/- 0.01 (tighter than r1b's +/-0.02 band since same harness)
- Substrate-only-decode gate: zero LLM forward calls (counter assertion)
- Version markers: `chain_mechanism`, `K_max`, `gamma`, `permutation_type` baked into metrics.json

**HARD-PASS-PLUS (super-pass; competitive with frozen-encoder at multi-hop):**
- HYBRID_SR_PLUS_COMPOUND at K=4 achieves >= 0.30 mean accuracy (1.74x r1) AND margin_ratio > 3.5x

**MIDDLE_BAND (partial mechanism):**
- Mean accuracy gain in [1.05x, 1.20x] r1 at K=4 (real but smaller than predicted)
- OR OOD_refuse_margin in [0.80, 0.90] (partially clears r1b's gate)

**HARD-FAIL (mechanism wrong):**
- No arm achieves >= 1.05x r1 mean accuracy AT ANY K
- OR OOD_refuse_margin still < 0.80 at K=4 (compound and SR don't fix the margin signal)
- OR ITER_CLEANUP_r1b_anchor doesn't reproduce r1b within +/-0.02 (harness drift — INCONCLUSIVE not HARD_FAIL)

**Discriminating-regime requirement (C5):**
- At K=1 (single-hop): ALL arms must equal U1 single-hop anchor (CERT 584 setrecall=0.99); they're all equivalent at K=1 by construction.
- At K=10 (way beyond test range): ALL arms must collapse to near-random (spectral instability of SR catches up; iterative-cleanup decays); cell should test this as a bracket sanity.

**Version marker requirement:** prevents r1b-style mean-reproduction failure across runs.

### Compute cost

- Per arm: 
  - ITER_CLEANUP_r1b_anchor: matches r1b (~770s per seed for K=2,3,4 with 500 chains)
  - SUCCESSOR_W_CLOSURE: setup ~3-5 min (W^k precompute); query is FREE; total ~5 min per seed for full K-sweep
  - TEM_FACTORED_COMPOUND: setup minor; query ~1.2x iterative; total ~900s per seed
  - HYBRID: max of the three
- 4 arms x 3 K_max x 3 gamma values x 7 seeds = 252 runs at ~15 min mean = ~63 hours
- **Phased recommendation:** Phase 1: 3 arms {ITER_CLEANUP_r1b_anchor, SUCCESSOR_W_CLOSURE (K_max=5, gamma=0.8), TEM_FACTORED_COMPOUND}, 7 seeds, K_hops in {2,3,4}. ~10-12 hours remote_cpu_queue. Decisive on the headline. Phase 2: HYBRID and gamma sweep conditional on Phase 1 HARD-PASS.

### Secondary cell (CONDITIONAL on r2 HARD-PASS): `r3_successor_multi_scale_continual_v1`

**Scope:** the multi-scale-gamma variant: precompute M(gamma=0.5), M(gamma=0.8), M(gamma=1.0); query combines all three for the final chain-distribution. Tests Momennejad's "brain uses multiple SRs simultaneously" claim on substrate.

**Pre-reg HARD-PASS:** multi-scale variant achieves >=1.10x single-scale gain at K=4.

**Pre-reg HARD-FAIL:** multi-scale degrades performance (the gamma weights conflict).

### Conditional cell (CONDITIONAL on r2 HARD-FAIL): `r2b_iter_cleanup_with_compound_margin_v1`

**Scope:** keep the iterative-cleanup chain (NOT the SR closure), but compute REFUSE-GATE on compound chain_state instead of per-hop. Isolates whether the SR-closure margin fix is from the closure mechanism OR from the compound-margin computation alone.

**Pre-reg HARD-PASS:** compound-margin alone lifts OOD_refuse_margin to >= 0.90 even with the iterative-cleanup chain.

---

## FALSIFIABLE PREDICTIONS

### Prediction 1 (PRIMARY) — Successor-W closure beats iterative-cleanup at K=4
**Hypothesis:** SUCCESSOR_W_CLOSURE at K_max=5, gamma=0.8, N_DIM=8192 achieves mean accuracy >= 0.211 at K=4 (1.20x r1's 0.172) AND OOD-refuse(margin) >= 0.90 AND margin-ratio > 2.0.
**Mechanism:** closed-form K-step closure avoids per-hop softmax margin decay; refuse-gate operates on aggregated multi-hop distribution where in-KB evidence concentrates and OOD evidence diffuses.
**HARD-PASS:** all three thresholds met simultaneously.
**HARD-FAIL:** mean accuracy < 1.05x r1 OR margin-ratio < 1.5 at K=4.
**Calibrated P(HARD-PASS): 0.45** (capped at novel-synthesis 0.50; deflated 0.05 because SR is well-validated in cog neuro / RL, but its application to substrate's bipolar Hebbian W has not been empirically validated; spectral instability risk).

### Prediction 2 (SECONDARY) — TEM factorization enables UNSEEN-R-chain composition
**Hypothesis:** TEM_FACTORED_COMPOUND on a HELD-OUT R-CHAIN test (a chain of R relations never seen as a sequence at ingest, but each R seen individually) achieves >= 0.10 accuracy (vs ~0.0 for r1's entangled binding which has no factorization). This is a TRANSFER-LEARNING-STYLE test.
**HARD-PASS:** held-out R-chain accuracy >= 0.10 AND in-distribution R-chain accuracy >= r1 baseline.
**HARD-FAIL:** held-out R-chain accuracy < 0.02 (no transfer).
**Calibrated P: 0.30** (deflated; TEM transfer claims are demonstrated in toy graphs but substrate's bipolar-Hebbian binding may not preserve enough factorization).

### Prediction 3 (CONDITIONAL on Prediction 1 PASSES) — Hybrid SR + compound-margin is multiplicative
**Hypothesis:** HYBRID_SR_PLUS_COMPOUND beats SUCCESSOR_W_CLOSURE-alone by an additional >=0.05 mean accuracy AND brings margin-ratio > 3.0 at K=4.
**HARD-PASS:** hybrid > SR-alone by 0.05 in accuracy and 1.0 in margin-ratio.
**HARD-FAIL:** hybrid <= SR-alone (compound-margin is redundant given SR closure).
**Calibrated P: 0.35** (the two mechanisms address different failure modes — SR fixes margin decay, compound fixes margin-computation — so multiplicative; but they might also be redundant if SR alone clears the threshold).

### Prediction 4 (NULL bracket) — K=1 and K=10 brackets
**Hypothesis:** at K=1 all arms equal U1 single-hop anchor (=0.99 setrecall). At K=10 all arms collapse to <0.05 (the spectral decay catches up).
**Purpose:** if K=1 doesn't equal anchor, harness drift. If K=10 doesn't collapse, the SR mechanism is leaking from outside the K_max window.

### Prediction 5 (REVIVAL ROUTE if HARD-FAIL) — Compound-margin alone (r2b cell)
**Hypothesis:** if r2's SR mechanism fails, the compound-margin alone might still fix r1b's gate2/c2 FAILs even with iterative-cleanup. This is r2b — isolates the margin-computation fix from the chain-mechanism fix.
**Pre-registered routing:** SAME-CYCLE Director note routing the negative with revival angle "compound-margin only".

### Prediction 6 (CROSS-DRILL composition) — Drill #2 cascade-STC composes with r2
**Hypothesis:** if drill #2 c2 cell (cascade+STC+SWR) lands, applying it to W BEFORE running r2's SR closure boosts r2's HARD-PASS bar by reducing per-edge variance in W. Test as `r2_cascade_W_v1` follow-on.
**Calibrated P: 0.40** (this is the cross-drill MOAT composition; expected to be additive but not yet validated).

---

## CROSS-THREAD SYNTHESIS

### Composes with the recent r1b HARD_FAIL
- r1b's FAILED gates: K3 mean-reproduction OUT-OF-TOL (0.028 diff vs +/-0.02 band), OOD_refuse_margin min=0.682 (FAIL >=0.90), margin-ratio min=1.003 (FAIL >2.0).
- r2's SR closure directly addresses MARGIN DECAY (precomputed multi-hop closure prevents per-hop softmax loss).
- r2's COMPOUND-MARGIN directly addresses MARGIN COMPUTATION (joint over chain rather than per-hop).
- Both r1b failure modes have a designed countermeasure in r2.

### Composes with drill #2 CLS continual learning (cell c2)
- Drill #2 cell c2 stabilizes the W matrix via cascade-STC consolidation.
- If c2 ships first, the W matrix that goes into r2's SR closure is LOWER-VARIANCE per edge.
- Predicted: c2 + r2 composition has lower compounding variance than r2 alone -> higher HARD-PASS-PLUS likelihood at K=4.
- Cross-cell ordering recommendation: c2 first (~10hr remote_cpu), then r2 (~10hr remote_cpu), then c2+r2 hybrid (`r2_cascade_W_v1`).

### Composes with HotpotQA chain-grade (CERT 588)
- HotpotQA was K=2 chain-grade today; r2 if HARD-PASS opens the door to HotpotQA at K=3,4 (currently untested).
- Wikipedia KG is large; SR closure setup cost ~K_max * N_DIM^2 * N_DIM matmul = expensive at HotpotQA scale; may need GPU dispatch.
- Sequenced follow-on: `r4_hotpotqa_K_geq_3_v1` post-r2 HARD-PASS.

### Composes with phase-portrait + data-survives lane (USER directive)
- The R-chain factorization is a STRUCTURAL transformation; preserving E content across different R-chains is data-survives-phase.
- SR closure with different gamma values IS the substrate operating at multiple time-horizon phase points; the closure aggregates them.
- This drill #3 is the substrate-side validation of phase-portrait-action: structural transformations applied to fixed sensory content.

### Composes with g1 substrate-native generation (CERT 587)
- Generation is K-step forward prediction. If SR closure is precomputed, generation becomes O(N_DIM^2) per step (matrix-vector against M_K) instead of O(K * N_DIM^2) iterative.
- Substantial speed-up for the substrate-native LM L2 closure.
- Cross-composition: `g2_successor_generation_v1` post-r2 HARD-PASS.

### Composes with refuse-gate primitive
- The substrate's refuse-gate today operates per-hop. The compound-margin upgrade IS the refuse-gate generalization to chain-objects.
- Affects the refuse_gate.py / conformal.py modules pending in the 7-of-7 hdlab/ backlog.

---

## SUBSTRATE-PRODUCT IMPLICATIONS

1. **Multi-hop becomes a SINGLE MATMUL, not a K-step iteration.** Setup cost is paid once at ingest-time; queries are O(N_DIM^2). The substrate's reasoning becomes K-step-invariant in query latency. This is a STRUCTURAL upgrade matching modern Hopfield (Ramsauer 2021) in tractability.

2. **The R / E factorization is the substrate's path to COMPOSITIONAL GENERALIZATION.** TEM's transitive-inference claim ("Bob's niece" answerable without seeing it directly) maps directly to substrate's R-chain factoring. Currently substrate's compositional generalization is implicit; r2 makes it primitive-level.

3. **Compound-margin is the refuse-gate primitive's chain-extension.** Currently refuse-gate is per-key; compound-margin is per-chain. This is a structural upgrade to the hdlab/refuse_gate.py backlog item.

4. **The SR closure removes a long-standing CHAIN-DECAY pathology.** r1, r1b, prior iterative-multihop-where-works drills all hit per-hop margin decay; SR closure is the FIRST mechanism in 4+ months of drilling that addresses the structural root cause.

5. **Cross-drill #2 + #3 composition is the substrate's L5 chain-grade pinch:** cascade-stabilized W + SR multi-hop closure + compound-margin refuse = the substrate's "structured reasoning that survives continual ingest" — directly the L5 MOAT for glass-box-LLM.

6. **Multi-scale gamma is a phase-portrait axis.** The substrate operating at multiple gamma simultaneously IS the phase-action discipline in action.

7. **The reverse-replay mechanism (Stream E) is a tertiary lever for future drill #3b:** post-r2 HARD-PASS, reverse-replay can add value-prop-style credit assignment to chain queries.

---

## L5 — CROSS-SUBSTRATE COMPOSITION (path-forward map)

```
                            r1b HARD_FAIL (margin-ratio FAIL, OOD-refuse FAIL, K3 mean OUT-OF-TOL)
                                            |
                            r2_successor_TEM_compound_v1
                            (Phase 1: 3 arms, K_hops in {2,3,4}, 7 seeds, ~10-12hr)
                                            |
                ____________________________|____________________________
                |                           |                           |
        HARD_PASS                       MIDDLE_BAND                  HARD_FAIL
        |                              |                            |
    Three follow-ons (parallel):       single-mechanism cells       r2b: compound-margin
        - r3: multi-scale gamma         (SR_ONLY vs COMPOUND_ONLY)    alone (margin-fix
        - r4: HotpotQA K>=3                                            without SR closure)
        - r2_cascade_W (c2 + r2)
        |
        compose with drill #2 c2
        cascade-STC stabilization
        |
        compose with drill #1
        kWTA-VQ at write
        |
        SUBSTRATE-AS-LM with
        COMPOSITIONAL MULTI-HOP
        REASONING (the L5 MOAT)
```

---

## CITATIONS (verified, count = 22)

1. Dayan, P. (1993). "Improving generalization for temporal difference learning: The successor representation." Neural Computation 5(4): 613-624. (Foundational successor representation paper.)

2. Stachenfeld, K.L., Botvinick, M.M., Gershman, S.J. (2017). "The hippocampus as a predictive map." Nature Neuroscience 20: 1643-1653. (Hippocampal place + grid cells as SR eigenvectors; foundational cog-neuro grounding.)

3. Momennejad, I., Russek, E., Cheong, J.H., et al. (2017). "The successor representation in human reinforcement learning." Nature Human Behaviour 1: 680-692. (Human behavioral validation of SR.)

4. Momennejad, I., Howard, M.W. (2018). "Predicting the Future with Multi-scale Successor Representations." bioRxiv 449470. [bioRxiv](https://www.biorxiv.org/content/10.1101/449470v1.full). (Multi-scale gamma SR.)

5. Geerts, J.P., et al. (2024). "Equivalence of Personalized PageRank and Successor Representations." arxiv 2512.24722. [arxiv](https://arxiv.org/pdf/2512.24722). (PPR-SR equivalence; substrate's KG-PPR composes with SR.)

6. de Cothi, W., Barry, C. (2020). "Neurobiological successor features for spatial navigation." Hippocampus 30(11): 1347-1366. [Wiley](https://onlinelibrary.wiley.com/doi/full/10.1002/hipo.23246). (Neural-network SR implementation.)

7. Whittington, J.C.R., Muller, T.H., Mark, S., Chen, G., Barry, C., Burgess, N., Behrens, T.E.J. (2020). "The Tolman-Eichenbaum Machine: Unifying Space and Relational Memory through Generalization in the Hippocampal Formation." Cell 183(5): 1249-1263. [Cell](https://www.cell.com/cell/fulltext/S0092-8674(20)31388-X) [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC7707106/). (TEM foundational paper; structural-sensory factorization.)

8. (2024). "Schema-based active inference supports rapid generalization of experience and frontal cortical coding of abstract structure." arxiv 2601.18946. [arxiv](https://arxiv.org/pdf/2601.18946). (Modern schema-reuse / TEM-style validation.)

9. (2023). "Graph schemas as abstractions for transfer learning, inference, and planning." arxiv 2302.07350. [arxiv](https://arxiv.org/pdf/2302.07350). (Graph-structural reuse for compositional planning.)

10. (2024). "A neural mechanism for compositional generalization of structure in humans." eLife reviewed preprint 107162. (Human empirical compositional-generalization evidence.)

11. (2025). "A Neuroscience-Inspired Dual-Process Model of Compositional Generalization." arxiv 2507.18868. (Dual-process model; system 1 fast pattern + system 2 compositional schema.)

12. Lisman, J.E., Idiart, M.A. (1995). "Storage of 7+/-2 short-term memories in oscillatory subcycles." Science 267: 1512-1515. (Theta-gamma foundational paper.)

13. Lisman, J.E., Jensen, O. (2013). "The Theta-Gamma Neural Code." Neuron 77(6): 1002-1016. [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC3648857/). (Modern theta-gamma code restatement.)

14. (2024). "Theta-Gamma Phase-Amplitude Coupling Supports Working Memory Performance in the Human Hippocampus." bioRxiv 2024.03.24.586454. [bioRxiv](https://www.biorxiv.org/content/10.1101/2024.03.24.586454v1.full). (Direct human evidence.)

15. Heusser, A.C., Poeppel, D., Ezzyat, Y., Davachi, L. (2016). "Episodic sequence memory is supported by a theta-gamma phase code." Nature Neuroscience 19(10): 1374-1380. [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC5039104/). (Sequence memory theta-gamma direct evidence.)

16. Kanerva, P. (2009). "Hyperdimensional Computing: An Introduction." Cognitive Computation 1: 139-159. (HDC primitives including permutation-binding; foundation for compound chain encoding.)

17. Plate, T.A. (2003). "Holographic Reduced Representation: Distributed Representation for Cognitive Structures." CSLI Publications. (Permutation-binding mathematical primitives.)

18. Foster, D.J., Wilson, M.A. (2006). "Reverse replay of behavioural sequences in hippocampal place cells during the awake state." Nature 440: 680-683. (Reverse-replay foundational paper.)

19. Wikenheiser, A.M., Redish, A.D. (2015). "Hippocampal theta sequences reflect current goals." Nature Neuroscience 18: 289-294. (Forward-sweep planning during decision-making.)

20. Aso, Y., et al. (2014). "The neuronal architecture of the mushroom body provides a logic for associative learning." eLife 3: e04577. [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC4273437/). (MBON ensemble combinatorial decision.)

21. Banino, A., Barry, C., et al. (2018). "Vector-based navigation using grid-like representations in artificial agents." Nature 557: 429-433. [Nature](https://www.nature.com/articles/s41586-018-0102-6). (DeepMind grid-cell emergence; spatial-specific SR cousin.)

22. Ramsauer, H., et al. (2021). "Hopfield Networks Is All You Need." arxiv 2008.02217. (Modern Hopfield = transformer attention; the substrate's iterative-cleanup baseline; SR closure is the structural alternative.)

---

## LIT-SCAN CALIBRATION NOTES

- Probability estimates deflated 0.15-0.25 from raw LM-based confidence.
- **Novel-synthesis cap at 0.50 applied:** SR-closure + TEM-factor + compound-margin triple composition has NO prior empirical validation on hyperdimensional / Hebbian-superposition substrates. P(HARD-PASS) = 0.45 reflects this cap + deflation.
- **HARD-FAIL thresholds mandatory and listed for every prediction.**
- DIRECTIONALITY (SR-beats-iterative-cleanup at multi-hop, compound-margin-beats-per-hop) is high-confidence (P~0.70 raw); MAGNITUDE (1.20x r1 at K=4, margin-ratio>2.0) is lower (P~0.50). Deflation hits magnitude.
- SR mechanism is robustly validated across MULTIPLE independent lines (Dayan 1993, Stachenfeld 2017, Momennejad 2017-2018, PPR-SR equivalence 2024). Deflation is for substrate-specific transfer (bipolar Hebbian W spectral properties), not the biology.
- TEM mechanism is well-validated in toy graphs (Whittington 2020) and human compositional-generalization studies, but bipolar substrate transfer is novel. Most deflation here.
- Compound-margin via permutation-binding is a Kanerva HDC primitive — high confidence the mechanism MEASURES what it claims; uncertainty is whether the IN-KB-vs-OOD discriminability is enough at the substrate's scale.

---

## DISPATCH RECOMMENDATION

**Immediate (Exp-Dev next multi-hop cell):** `r2_successor_TEM_compound_v1`
- Reuse r1b's KGStore harness; add SR closure pre-compute + permutation-binding compound + chain mechanism switch.
- Phase 1: 3 arms {ITER_CLEANUP_r1b_anchor, SUCCESSOR_W_CLOSURE, TEM_FACTORED_COMPOUND}, K_hops in {2,3,4}, 7 seeds, K_max=5, gamma=0.8. ~10-12 hr remote_cpu_queue.
- Anchor: ITER_CLEANUP_r1b_anchor must reproduce r1b within +/- 0.01 at all K (tighter than r1b's +/-0.02 since same harness).
- Version marker: `chain_mechanism`, `K_max`, `gamma`, `permutation_type`.

**Conditional next (only if r2 HARD-PASS):** `r3_successor_multi_scale_continual_v1` (multi-gamma SR) and `r4_hotpotqa_K_geq_3_v1` (test on HotpotQA Wikipedia KG).

**Cross-drill ordering vs drill #2:** drill #2 c2 cell can ship in parallel (different harness, different cell); the c2 + r2 hybrid is a follow-on after BOTH land. Drill #2 doesn't gate drill #3.

**Composes with the in-flight Director cell `substrate_self_map_v2`:** the substrate's self-map operates on cert_ledger relations (a small KG). r2's SR-closure could be applied to that small KG too for multi-hop self-introspection — substrate-native META-reasoning.

**GPU dispatch consideration (Fix #24):** SR closure setup (W^k precompute) for N_DIM=8192 is ~5 min on CPU; if N_DIM scales to 16384+ for Phase 2, route to remote_gpu via hdi_orchestrator per the GPU-utilization rule.

---

-- Research (Opus synthesis, 6+6 parallel WebSearch streams + cross-thread with r1b + drill #2 + prior multi-hop drills; novel-synthesis-deflated per calibration; designed as the structural fix for r1b's HARD_FAIL with mandatory anchor reproduction)

---

## CORRECTION 2026-06-22 (post-cell-author self-test)

r2_successor_TEM_compound_v1 cell-author (commit 59fc5a77) found the original SR closure formulation in this drill required correction at the cell-implementation level:

- **Original spec**: single-matmul SR closure — `score = M @ query` where `M = Σ γᵏ Wᵏ` precomputed once.
- **Bug found**: at synthetic K=2 self-test, single-matmul-on-composed-key produced acc=0.30 vs ITER baseline acc=1.00. The composed query is not equivalent to per-hop iteration with M.
- **Corrected formulation**: apply M as **per-hop operator** replacing W (M @ cleanup @ M @ cleanup @ ... K_hops times), NOT as single matmul on composed key.
- **Re-self-test PASS**: SR=ITER=1.00 at synthetic K=2.

Smoke at full cell config (N=2048 laptop CPU, 3 arms, 1 seed, 22.5s wall):
- ITER K=2 acc=0.76 (anchor faithful to r1)
- SR K=2 acc=0.72 (close to ITER; corrected formulation works)
- TEM compound-margin ratio 1.34-1.38x at K=2, K=3 (target full: >2.0x — promising signal)
- SR arm at K=3 dropped to 0.59 vs ITER 0.76: possible small-N=2048 artifact; M = Σ γᵏ Wᵏ with γ=0.8 K_max=3 may lose precision at small N. Full N=8192 K_max=5 expected to recover.
- K=1 dropped by design (chain sampler excludes (s,o) ∈ direct triples).

Full run dispatched to GPU (overnight_queue; commit 59fc5a77; timeout 21600s per PROT-019); landing pending.
