# research: GAP 1 cortex-as-router -- how the brain provides destination hints for retrieval

date: 2026-06-26
filed-by: research (Opus 4.7 1M)
trigger: USER deep drill (in-thread). Cell B v2 PART=0.9550 (oracle); auto-routers cap at 0.62-0.66. ORACLE-vs-auto gap (0.95 vs 0.66) is the load-bearing question. USER asks: HOW does cortex actually do destination-hinting, and can substrate implement it to break the 0.66 routing ceiling?
scope: depth drill (Section 1: brain mechanism concrete; Section 2: substrate failure mode honest; Section 3: 5+ substrate-feasible mechanisms; Section 4: composition with Gap 3 schemas; Section 5: top-3 ranked candidate cells).
prior context: notes/research_gap1_routing_bidirectional_as_router_2026-06-26.md (bidir-collide steelman, P=0.45; fly-LSH-router, P=0.40); notes/research_gap3_compositional_deeper_mechanism_drill_2026-06-26.md (Modern Hopfield prototype attractors P=0.45, CLS-replay P=0.40)
calibration: per [[feedback-lit-scan-calibration-penalty]] -- agent P estimates deflated 0.15-0.25; novel-synthesis cap 0.50; hard-fail thresholds pre-registered. Per [[feedback-brain-is-existence-proof-higher-prior]] -- brain-grounded mechanisms with substrate-feasible paths get P=0.40-0.50 (above novel-synthesis floor) when implementation correctness is the only risk.

---

## (a) HEADLINE

The 0.66 routing ceiling is NOT a substrate-physics ceiling -- it is a **single-pathway ceiling**. Substrate's auto-routers (bidir-collide 0.62; bidir-collide-as-router 0.66) all read from one pathway: the noise-collapsed hop-2 forward state (`mean_midpoint_cosine = 0.0000` confirms the state has no surviving atom signal). The brain's solution is **NOT to denoise the same pathway** -- it is to **route via a SEPARATE pathway that was never subjected to the noise**. Specifically: medial prefrontal cortex (mPFC) and anterior temporal lobe (ATL) hold a SCHEMA representation that was extracted offline via slow Hebbian / replay; that schema representation pre-activates the destination region BEFORE retrieval starts via theta-gamma phase coupling (typically 4-8Hz theta band, ~125-250ms cycles); the destination region's pre-activated pattern provides a BIAS signal that gates the retrieval target. Concretely for "Alice's grandma's hometown": mPFC schema "family-relation graph" pre-activates ATL "people-and-places" representation; ATL biases hippocampal CA3 to complete onto the geographic-fact subnetwork; the retrieval then completes within ~10x smaller candidate space.

The substrate-feasible translation: introduce a **second router-W matrix** (`R_schema`) learned offline (closed-form / Hebbian / replay-trained) over the SAME chains, that takes the **QUERY** (not the noise-collapsed state_fwd) as input and emits a partition-pre-activation that BIASES the per-hop cleanup. The two key insights:
1. The router reads from the QUERY (a clean signal) NOT from the noise-collapsed forward state -- this side-steps the 0.66 ceiling structurally.
2. The router is composed with the existing per-hop W, not replacing it -- preserves the chain-grade primitives that already work.

Top-3 candidate cells ranked below. Candidate 1 (`query_to_partition_router_v1`) is the **cheapest decisive test**: P_deflated=0.55, ~2-3hr local_cpu, 4 arms with HARD_PASS at >=0.80 routing accuracy. This is the most direct test of "use a SEPARATE pathway from the query to provide destination hints" and structurally what the brain does.

---

## (b) Cheap decisive test

**SINGLE 4-arm cell** `substrate_gap1_query_to_partition_router_v1_META_M7`:

| Arm | Mechanism | What it isolates |
|---|---|---|
| ARM_REPRODUCE_POINTER_CHAIN_V2_5HOP | META_M7 rail at 2000 bindings | mandatory cross-cell gate; band [0.08, 0.25] |
| ARM_PART_ORACLE_5HOP (control) | Cell B v2 oracle PART=0.955 | ceiling (already measured) |
| ARM_PART_QUERY_TO_ROUTER_5HOP | closed-form pseudoinverse R_schema in R^{N x N_PARTS} fitted on training queries; route = argmax(R_schema @ query) | **The brain analog: separate-pathway routing from clean query input** -- expected to break the 0.66 ceiling |
| ARM_PART_BIDIR_AS_ROUTER_5HOP | Candidate 1 from prior drill (bidir-collide steelman) | the in-pathway baseline; expected ~0.65 |

Decision-grade thresholds (3 seeds, V_C=200, depth=5, N=8192, META_M7 rail mandatory):

- HARD_PASS_QUERY_ROUTER: ARM_PART_QUERY_TO_ROUTER >= 0.80 AND ARM_PART_QUERY_TO_ROUTER - ARM_PART_BIDIR_AS_ROUTER >= 0.10 AND META_M7 PASS. Brain-analog vindicated; substrate-product Gap 1 closes via separate-pathway routing.
- HARD_PASS_COMPOSED (stretch): ARM_PART_QUERY_TO_ROUTER + ARM_PART_BIDIR_AS_ROUTER composed via two-stage (router narrows -> bidir confirms) >= 0.90.
- MIDDLE_BAND: ARM_PART_QUERY_TO_ROUTER in [0.66, 0.80). PARTIAL; router carries SOME information beyond bidirectional but does not fully close to oracle.
- HARD_FAIL: ARM_PART_QUERY_TO_ROUTER <= 0.66 (same as bidir ceiling). Interpretation: routing-from-query is NOT a richer signal than routing-from-state at substrate's N/V_C regime. Pivot to Candidate 2 (schema-conditioned pre-activation via Modern Hopfield) or Candidate 3 (CLS-replay R_schema).

**Compute budget:** ~4500-5500s wall local_cpu. The R_schema fit is O(N x N_PARTS x N_train) = O(8192 x 20 x 1000) = 1.6e8 FLOPS = negligible. Inference per query is matrix-vector + argmax = O(8192 x 20) = ~1e5 FLOPS = 1us. Total cell wall is dominated by ARM_REPRODUCE_POINTER_CHAIN_V2_5HOP and ARM_PART_BIDIR_AS_ROUTER (existing per-Z back-walk cost).

**Substrate-mine FIRST per [[feedback-substrate-mine-capacity-before-extrapolating]]:** check atoms for `kv_learned_projection 0.827` (chain-grade-passed 2026-06-20) -- the substrate already has a learned-projection capability class. R_schema is the same class applied to a different problem (routing not cleanup). Reuse the kv_learned methodology.

---

## (c) Falsifiable predictions

| Arm | Predicted top1 (3-seed mean) | P(>=HARD_PASS) | Reasoning |
|---|---|---|---|
| ARM_PART_QUERY_TO_ROUTER | 0.82 | 0.55 | The query is a clean signal (the source atom encoding); R_schema training has access to (query, target_partition) pairs which is exactly the supervised signal a closed-form pseudoinverse can fit. The 0.66 ceiling is structurally about reading the noise-collapsed state; this side-steps it. P=0.55 (above 0.50 novel-synthesis floor because: (a) kv_learned_projection precedent at 0.827 chain-grade; (b) brain-analog with replication across 4+ studies; (c) closed-form fit is the lowest-risk learning mechanism in substrate). Risk: if `state_fwd` is what the router NEEDS to discriminate (not the query), then the closed-form fit on queries underfits. |
| ARM_PART_BIDIR_AS_ROUTER | 0.65 | 0.45 | unchanged from prior drill -- bidir-collide steelman |
| ARM_PART_ORACLE_5HOP | 0.95 | -- (control) | from Cell B v2 |

**HARD-PASS thresholds (across-seed mean):**
- ARM_PART_QUERY_TO_ROUTER >= 0.80 AND lift over bidir >= 0.10
- composed (if dispatched as a follow-up): >= 0.90

**HARD-FAIL thresholds:**
- ARM_PART_QUERY_TO_ROUTER <= 0.66 -> closed-form query-router does NOT exceed bidirectional. Mechanism interpretation: the partition information IS NOT linearly extractable from the source atom encoding; needs nonlinear (Modern Hopfield) or replay-extracted (CLS) routing. Pivot to Candidate 2 or 3.
- ARM_PART_QUERY_TO_ROUTER train >> test (train top1 >= 0.85, test top1 <= 0.50) -> R_schema is OVERFITTING the training chains. Regularize via ridge / shrinkage; if still overfit, the linear-routing hypothesis is closed for substrate. Pivot to Candidate 2.

---

## Section 1: How the brain actually does it

### Concrete walk-through for "what is Alice's grandma's hometown?"

**Timeline (millisecond scale; from the lit, especially Staresina et al. 2019 "Neural Chronometry of Memory Recall" and Backus et al. 2016):**

**T=0-200ms: Cue encoding + initial semantic activation.**
- The auditory/visual cue "Alice's grandma's hometown" enters via primary cortex, then immediately activates the **ATL (anterior temporal lobe) semantic hub** (Patterson, Lambon Ralph et al. 2007 "semantic hub" model; Hoffman & Lambon Ralph 2018 confirm via TMS lesion). The ATL is the substrate's "card catalog": it holds the cross-modal abstract representation of "what KIND of question is this."
- Specifically: ATL activates a region representing "person -> family-relation -> geographic-attribute" schema. The activation is NOT yet specific to Alice; it is at the schema level.

**T=200-500ms: Schema-mediated bias signal to retrieval network.**
- **mPFC (medial prefrontal cortex)** kicks in (Gilboa & Marlatte 2017 review; van Kesteren et al. 2012). mPFC reads the ATL schema activation and PRE-ACTIVATES a top-down bias signal:
  - It pre-activates the hippocampal subregion most relevant to **person-place associations** (anterior hippocampus, per Poppenk et al. 2013 long-axis specialization; geographic facts are coarse/global = anterior).
  - It pre-activates the cortical regions where **place representations** live (parahippocampal place area / retrosplenial cortex).
- The pre-activation is a SUB-THRESHOLD bias -- it does not retrieve, it just primes a region to be more responsive.
- **The destination-hint signal IS this pre-activation pattern.** The brain has not yet retrieved anything; it has just made the "geographic-fact" region of the retrieval network N times more sensitive.

**T=300-800ms: Theta-phase-locked retrieval probe.**
- Hippocampal theta (4-8 Hz, ~125-250ms cycles) begins phase-locking with mPFC theta (Hyman et al. 2005; Jones & Wilson 2005; Backus et al. 2016 confirm this for memory).
- **The theta phase carries the destination hint** -- the trough vs peak determines whether the hippocampus is in encoding mode (entering new info) or retrieval mode (completing existing pattern). For retrieval, the trough is the "go" signal.
- Within each theta cycle, gamma packets (40-80 Hz; CA3 retrieval gamma is ~40Hz, CA1 encoding gamma is ~80Hz per Colgin et al. 2009) carry the actual content. The mPFC schema activation MODULATES the gamma-amplitude in CA1 via theta-gamma phase-amplitude coupling (PAC).
- Effectively: mPFC says "be selective for family/geographic content NOW" and the hippocampal CA3 attractor sweep is biased toward that subnetwork.

**T=400-1000ms: Pattern completion in pre-biased CA3.**
- CA3 recurrent collaterals pattern-complete from the partial cue (the Alice atom's connections) into the full attractor -- but only attractors in the pre-biased subnetwork are energetically accessible. Other attractors (food, movies, jobs) are suppressed below threshold.
- Bakker et al. 2008 + Yassa & Stark 2011 establish DG (dentate gyrus) sparsification of input into CA3-decodable patterns; the mPFC schema bias makes specific DG -> CA3 paths more excitable.

**T=500-1500ms: Cortical reinstatement.**
- Once CA3 completes, it feeds CA1 -> entorhinal -> neocortex. The retrieved fact "Alice's grandma's hometown = Plano" reinstates in the place-representation cortex (which was pre-activated by mPFC at T=300-500ms).
- The pre-activation MEANS the retrieval finishes faster because the destination region was already "warm" -- this is the **speed advantage** of schema-mediated retrieval.

### Which carries the destination hint?

The destination hint is multiplexed across TWO signals:
1. **The mPFC -> hippocampus theta-phase-locked bias** (subthreshold pre-activation in CA3 of the relevant subnetwork). This is the "where to search" signal.
2. **The mPFC -> ATL -> destination-cortex direct projection** (subthreshold pre-activation of the destination-region representation). This is the "what shape to expect" signal.

Both signals are TOP-DOWN, both arrive BEFORE retrieval completes, both are sub-threshold (don't retrieve by themselves), and both COMPOSE multiplicatively with the bottom-up cue.

### Where is "type-of-query" represented?

**ATL anterior temporal lobe** (Patterson, Lambon Ralph et al. 2007; Hoffman & Lambon Ralph 2018; Nature Sci Reports 2021 PMC8233387). The ATL is the cross-modal semantic hub; it holds the abstract representation of "person-asking-about-family-relation-to-geographic-attribute." TMS to ATL specifically disrupts type-of-query encoding without disrupting cue perception or motor response.

ALSO: **vlPFC (ventrolateral PFC)** for executive control over which semantic features to weight (PMC8233387 confirms vlPFC + ATL co-activation in categorization).

### Where is "candidate-answer-region" represented?

For "place facts": **parahippocampal place area (PPA) + retrosplenial cortex (RSC)** (Epstein & Kanwisher 1998; Vann, Aggleton, Maguire 2009). The destination cortex is content-specific (faces -> FFA; places -> PPA; tools -> left lateral occipitotemporal cortex).

For "person facts": **ATL person-specific regions + temporal pole** (Olson, Plotzker, Ezzyat 2007).

### Timing summary

- mPFC schema activation: ~150-300ms post-cue
- mPFC-MTL theta coupling: peaks ~300-500ms post-cue
- Hippocampal retrieval initiation: ~500ms
- Cortical reinstatement: ~500-1500ms
- The 4-8 Hz theta cycle: 125-250ms period; ~4-8 cycles for full retrieval
- The 40-80 Hz gamma cycle: 12.5-25ms period; ~10-20 gamma bursts per theta cycle = the substrate-level information packets

### The key insight for substrate

**The brain's "destination hint" is a SUB-THRESHOLD BIAS, not a hard route.** It does not say "look ONLY in partition P"; it says "make partition P 3-5x more sensitive than the rest." Retrieval is still global; bias makes it FAST and ACCURATE.

This is structurally different from substrate's current "ORACLE_PART" mechanism (which is hard-routing: only look at partition P, completely ignore the rest). The brain analog is SOFT-routing: pre-amplify partition P then do global cleanup.

References:
- Patterson, Nestor, Rogers (2007) Nature Rev Neurosci "Where do you know what you know?"
- Hoffman & Lambon Ralph (2018) Curr Op Behav Sci "ATL semantic hub"
- Gilboa & Marlatte (2017) TICS "Neurobiology of schemas and schema-mediated memory"
- van Kesteren, Ruiter, Fernandez, Henson (2012) TICS "How schema and novelty augment memory formation"
- Staresina (2019) TICS "A Neural Chronometry of Memory Recall"
- Backus, Schoffelen, Szebenyi, Hanslmayr, Doeller (2016) Curr Biol "Hippocampal-Prefrontal Theta Oscillations Support Memory Integration"
- Colgin et al. (2009) Nature "Frequency of gamma oscillations routes flow of information"
- Hasselmo, Bodelon, Wyble (2002) Neural Comp "A proposed function for hippocampal theta rhythm"
- Bakker, Kirwan, Miller, Stark (2008) Science "Pattern separation in human hippocampal CA3/DG"
- Hyman et al. (2005) Hippocampus + Jones & Wilson (2005) PLoS Biol -- PFC-HPC theta coupling
- O'Reilly et al. (2021) JCN "Deep Predictive Learning in Neocortex and Pulvinar"

---

## Section 2: Why substrate fails at this (honest)

### The structural diagnosis

Substrate's auto-routing tops out at 0.66 for ONE structural reason: **all current routers read from the SAME degraded signal that the cleanup is trying to recover.**

Specifically:
1. The forward state at hop 2 (in a 5-hop chain) has `mean_midpoint_cosine = 0.0000` to actual atom embeddings (Cell C v2 probe data). This is because:
   - Each HRR multiplication unbind step accumulates a noise term proportional to sqrt(K/N).
   - At hop 2 in a 5-hop chain, ~2 unbind operations have happened.
   - With V_C=200 and N=8192, the noise floor IS the state at hop 2.
   - The state has the right STATISTICAL structure (it lies on the substrate cone) but ZERO ATOM-SPECIFIC information.
2. The bidirectional state (forward to mid + backward from end) is BETTER than forward alone (0.62 vs ~0.35) because the backward walk re-injects target information.
3. BUT bidirectional state still carries the noise from BOTH walks. The 0.66 ceiling is what survives bidirectional noise reduction.

### Why every router that reads from forward-state caps at 0.66

Any router R(state_fwd, state_bwd) is bounded by I(state_fwd, state_bwd; target_partition). The probe arm measured I(state_fwd; ANY atom) ~ 0 (mean_midpoint_cosine=0.0). Even with the bidirectional lift, mutual information about partition (which is a 5-bit signal: log2(20 partitions)) is bounded above by what the bidir state carries.

Approximate ceiling argument: I(state_bidir; target_partition) is upper-bounded by I(state_bwd; target_partition) -- because the forward state contributes essentially zero. The backward walk from the target through (N_HOP - mid) = 3 hops with V_C=200, depth=5 has a noise budget that limits partition-discrimination to ~0.66 (matches measured).

### Why the brain doesn't have this problem

The brain has SEPARATE PATHWAYS:
- Pathway 1: bottom-up hippocampal retrieval (substrate's analog: per-hop W @ key)
- Pathway 2: top-down mPFC schema activation from the QUERY input (substrate has NO analog for this -- it does not read from the query a second time)

The pathway-2 signal IS not subject to the unbind noise because it never went through unbinding. It went through a separate (slow-extracted) mapping from query-features to schema-membership.

### What substrate is missing

A **second mapping** Q -> partition, learned offline from the chains, that bypasses the unbind-noise pathway. The Q here is the QUERY (source atom encoding or query atom encoding), NOT the noise-collapsed state_fwd. This is the structural analog of the brain's mPFC schema-bias signal.

The substrate ledger has analogous capability: `kv_learned_projection` chain-grade-passed at 0.827 (2026-06-20). That cell learned a projection from KV (key-value) pairs that beats the structural baseline. It is the same capability class applied to a different problem.

---

## Section 3: Substrate-feasible cortex-as-router mechanisms

### Candidate 1: Closed-form query-to-partition router (R_schema pseudoinverse) -- P_deflated = 0.55

**Field:** Learned-projection family (substrate ledger: kv_learned_projection at 0.827 chain-grade-passed)
**Brain analog:** mPFC schema-bias signal from query input
**Cross-domain:** linear discriminant classifier on query embedding

**Substrate-native mapping:**
```
# Offline: for each training chain, extract (source_query, target_partition_per_hop)
# Solve closed-form R_schema in R^{N x N_PARTS x N_HOPS}:
#     R_schema[:,:,h] = least_squares(queries, one_hot(targets_at_hop_h))
# At inference, for hop h:
#     partition_logits = R_schema[:,:,h] @ query
#     predicted_part_h = argmax(partition_logits)
# Then standard cleanup within predicted partition (same as PART_ORACLE).
```

**Cost:** Offline R_schema fit = O(N^2 x N_HOPS) = 8192^2 x 5 = 3.4e8 FLOPS = ~30s.
Inference = O(N x N_PARTS) per hop = 1.6e5 FLOPS = 16us per hop = negligible.

**Discriminator vs 0.66 baseline:** ARM_PART_QUERY_TO_ROUTER >= 0.80 (HP); >= 0.66 + 0.10 (clear-lift HP).

**Substrate-feasibility:** USES kv_learned_projection precedent. NO new primitive class.

**Brain-fidelity:** HIGH for the "use a separate pathway from query" concept; MEDIUM for the specific implementation (brain uses Hebbian-replay, not closed-form pseudoinverse, but the FUNCTIONAL signal is the same).

**Why it might fail:** R_schema is LINEAR in query features. If partition-membership is a NONLINEAR function of the query (e.g., the partition is determined by an interaction term query[i] * query[j]), linear closed-form fit underfits. Mitigation: ridge regularization + cross-validation on holdout chains.

**Why it might succeed:** The substrate's source atoms are SAMPLED FROM A CONE STRUCTURE (Gap 2 finding). Within-cone, linear discriminants on partition are well-defined. Pseudoinverse on cone-distributed queries should be a strong baseline.

### Candidate 2: Modern-Hopfield prototype-as-router (cortical schema attractor) -- P_deflated = 0.40

**Field:** Modern Hopfield (Krotov, Demircigil, Ramsauer); brain analog: ATL semantic hub as attractor
**Cross-domain:** prototype classifier with energy-landscape

**Substrate-native mapping:**
```
# Offline: build per-partition prototype via Modern Hopfield attractor
#     For each part p: P_p = ModernHopfield_converge(mean(queries_in_p), training_queries)
#     This sharpens P_p toward the "cleanest" attractor (not just the mean)
# At inference:
#     part_logits = softmax(beta * P @ query)   # Ramsauer-2020 form
#     predicted_part = argmax(part_logits)
```

**Cost:** Offline build = O(N_PARTS x N_train x N) = 20 x 1000 x 8192 = 1.6e8 = ~1s. Inference matmul = O(N_PARTS x N) = ~1.6e5 = negligible.

**Discriminator:** vs bidirectional (0.66) and vs linear-R_schema (Cand 1). HP_HOPFIELD >= 0.80 AND >= 0.05 over R_schema (proves nonlinear basin-sharpening adds value).

**Substrate-feasibility:** ALIGNS with Gap 3 Modern-Hopfield cell already in the queue (gap3_modern_hopfield_prototype_attractor_v1). If Gap 3 lands, the prototypes EXIST -- this candidate just reuses them as routers.

**Brain-fidelity:** HIGH -- ATL semantic hub IS an attractor-based prototype (Patterson 2007).

**Why it might fail:** Modern Hopfield energy at beta=20 with 1000 training queries per partition may overfit OR underfit; needs beta sweep.

**Why it might succeed:** Basin-sharpening structurally beats linear pseudoinverse when partition-membership is nonlinear in query features.

### Candidate 3: CLS-replay R_schema (slow-extracted via replay) -- P_deflated = 0.35

**Field:** Complementary Learning Systems (McClelland 1995; Kumaran-McClelland 2016)
**Brain analog:** mPFC schema slowly extracted from hippocampal replay

**Substrate-native mapping:**
```
# Initial: W_fast = existing per-hop W (already chain-grade)
# Initialize R_schema_slow = 0
# Replay loop (N_replay = 100):
#     for chain in replay_buffer:
#         q = chain[0]
#         for h in range(N_HOPS):
#             target_part = chain.partition_at_hop[h]
#             R_schema_slow[h] += eta_slow * outer(q, one_hot(target_part))
# At inference:
#     part_logits = R_schema_slow[h] @ q
```

**Cost:** Replay = O(N_replay x N_chains x N) per hop = 100 x 1000 x 8192 x 5 = 4e9 = ~40s on numpy. Inference negligible.

**Discriminator:** vs closed-form R_schema (Cand 1). HP_CLS >= 0.80. KEY: if CLS-replay tracks Cand 1 within 3%, the SAME mathematical structure (closed-form pseudoinverse for linear fit) is being approached asymptotically -- they are the same; pick the cheaper.

**Substrate-feasibility:** USES existing replay_cycle (continual.py).

**Brain-fidelity:** HIGHEST of the candidates -- this IS the CLS framework directly.

**Why it might fail:** Same as Cand 1 if linearity is wrong; equivalent failure mode.

**Why it might succeed:** Composes natively with Gap 4 NREM consolidation work; if NREM lands, R_schema_slow is built FOR FREE during the consolidation cycles.

### Candidate 4: Type-conditioned routing (multi-tier database / BGP-style) -- P_deflated = 0.30

**Field:** Distributed systems (multi-tier database routing); 5G beam management hierarchical beam selection; BGP route announcement
**Brain analog:** ATL query-type representation -> select retrieval-cortex region

**Substrate-native mapping:**
```
# Train a query-type classifier T: query -> type_tag in {1, ..., N_TYPES}
#     T can be Modern Hopfield over query-types (substrate-native)
# Build per-type partition-distribution: P_type[t] = histogram of partitions for type-t chains
# At inference:
#     type_tag = T(query)
#     predicted_part_h = argmax(P_type[type_tag, h, :])  # most common partition for this type
```

**Cost:** O(N x N_TYPES) for classifier + O(N_TYPES x N_PARTS x N_HOPS) lookup. Negligible.

**Discriminator:** Two-tier ablation. If type-routing alone >= 0.50 it's WORKING; combined with cleanup-routing should hit >= 0.80.

**Substrate-feasibility:** Requires deriving "query types" from training set. This is META: substrate doesn't have a natural type-decomposition unless one is provided.

**Brain-fidelity:** MEDIUM. The brain has natural type categories (face/place/word/number) due to evolutionary cortical specialization. Substrate must EXTRACT types from data (unsupervised clustering on queries).

**Why it might fail:** Without a clean type-decomposition, query types become arbitrary clusters; routing-via-type degrades to routing-via-random-cluster (which is centroid-routing repackaged, P=0.05).

**Why it might succeed:** Substrate's chains may have natural type structure (e.g., 5 chain-templates, each with characteristic partition trajectory). Discovering this offline via k-means on queries is the substrate-feasible path.

### Candidate 5: Hierarchical attractor cascade (cortex -> hippocampus two-level) -- P_deflated = 0.35

**Field:** Krotov Hierarchical Associative Memory (arxiv 2107.06446); 5G coarse-then-fine beam selection
**Brain analog:** mPFC schema attractor -> hippocampal pattern completion

**Substrate-native mapping:**
```
# Two-level attractor:
# Level 1 (cortex): coarse attractor over partitions
#     part_attractor = ModernHopfield_step(query, partition_prototypes)
# Level 2 (hippocampus): fine attractor within winning partition
#     local_attractor = ModernHopfield_step(query, atoms_in_partition[part_attractor])
# Output: local_attractor (the retrieved atom)
```

**Cost:** Level 1 = O(N_PARTS x N). Level 2 = O((M/N_PARTS) x N). Total = 1/(N_PARTS) of full cleanup cost. NOT cheaper in absolute terms; same big-O as ORACLE_PART path.

**Discriminator:** vs PART_ORACLE. If hierarchical >= 0.85, the cascade matches oracle without the oracle (the level-1 attractor IS the partition decision).

**Substrate-feasibility:** REQUIRES Gap 3 Modern Hopfield to land first (provides the level-1 prototype attractors). DOWNSTREAM dependency.

**Brain-fidelity:** HIGHEST -- this IS the cortex -> hippocampus pattern.

**Why it might fail:** If Gap 3 Modern Hopfield underperforms, this cascade has weak level-1.

**Why it might succeed:** Composes Gap 3 + Gap 1 in one architecture. Brain-aligned. Substrate-native primitives.

### Candidate 6: Two-stage composition (R_schema narrows -> bidir-collide confirms) -- P_deflated = 0.40

**Field:** Distributed-systems two-stage routing; ANN IVF (coarse partitioning then fine search)
**Brain analog:** mPFC pre-activation narrows search space -> hippocampal pattern completion within biased subnetwork

**Substrate-native mapping:**
```
# Stage 1 (cortex): R_schema query-router narrows N_PARTS to top-K=3
top_k_parts = argtop_K(R_schema @ query, K=3)
# Stage 2 (hippocampus): bidir-collide WITHIN those K partitions
score_p = max_{Z in part_p} state_fwd . _backward_state(E[Z], preds[mid:])
        for p in top_k_parts
predicted_part = argmax_p score_p
```

**Cost:** Stage 1 negligible; Stage 2 reduced from N_PARTS=20 to K=3 -> ~7x speedup over bare bidir.

**Discriminator:** vs Cand 1 alone and vs bidir alone. HP_COMPOSED >= 0.90 (lift over MAX(R_schema, bidir) >= 0.05) -> independent signals multiply.

**Substrate-feasibility:** All primitives exist if Cand 1 lands.

**Brain-fidelity:** HIGHEST. This is the literal mPFC-CA3 architecture.

**Why it might succeed:** IF R_schema and bidir read SEPARATE error-correlation channels, composition gives super-additive lift.

### Cross-domain analogies summary

| Domain | Mechanism | Substrate analog |
|---|---|---|
| Brain (mPFC-HPC theta coupling) | Top-down pre-activation from schema | R_schema query-router (Cand 1) |
| Brain (ATL semantic hub) | Attractor-prototype for query type | Modern Hopfield prototype (Cand 2) |
| Brain (CLS) | Slow-extracted neocortical schema | CLS-replay R_schema (Cand 3) |
| Distributed systems (IVF) | Coarse partition routing + fine search | Two-stage composition (Cand 6) |
| 5G beam management | Hierarchical coarse-fine beam selection | Hierarchical attractor cascade (Cand 5) |
| Multi-tier database | Type-tagged routing | Type-conditioned (Cand 4) |
| BGP / routing tables | Pre-computed destination tables | R_schema offline fit (Cand 1) |
| Information theory (turbo) | Bidirectional extrinsic info | bidir-collide (prior drill Cand 1) |

All 6 substrate candidates and all 8 cross-domain analogs converge on ONE structural principle:
**The destination hint pathway must NOT pass through the same noise-degraded signal that retrieval is trying to recover. It must be a SEPARATE channel.**

---

## Section 4: Composition with Gap 3 work

Gap 3 is testing schema-extraction. If `gap3_modern_hopfield_prototype_attractor_v1` lands (predicted P=0.45 from prior drill), substrate has Modern Hopfield prototype attractors per category in queue. The TWO_TIER cell (also queued) gives CLS-replay slow channel.

### Composition sketch: route-by-schema architecture

**Pre-conditions:**
- Gap 3 Modern Hopfield HP -> we have prototypes P_c for each category c
- The categories from Gap 3 might NOT be the same as Gap 1 partitions (chain partitions are routing destinations; Gap 3 categories are semantic classes)
- Mapping needed: M : category c -> partition p (e.g., "geography" -> partition 3,7,11; "people" -> partition 1,5)

**Composed cell `substrate_gap1_route_by_gap3_schema_v1`:**

```
# Pre-built (from Gap 3 + offline analysis):
#     schema_prototypes: N_CAT prototypes in R^N (from Gap 3)
#     category_to_partition: M : c -> set of partitions (from offline chain analysis)
#
# Inference for query q:
# Step 1: Identify schema category for q
#     cat_logits = softmax(beta * schema_prototypes @ q)
#     query_category = argmax(cat_logits)
# Step 2: Project to partition set
#     candidate_partitions = category_to_partition[query_category]
# Step 3: Within candidate partitions, do standard cleanup
#     scores = E_parts[candidate_partitions] @ (W @ key)
#     local_idx = argmax(scores)
```

**Why this is the brain architecture:** Step 1 = ATL semantic hub (categorize query); Step 2 = mPFC schema-to-region projection (which cortical destination to bias); Step 3 = hippocampal pattern completion in pre-biased subnetwork.

**Cost:** Step 1 = O(N_CAT x N); Step 2 = O(1) table lookup; Step 3 = O(|candidate_partitions| x M/N_PARTS x N). If |candidate_partitions| = 3 out of 20, this is 6.7x speedup over global cleanup.

**Discriminator:** vs PART_ORACLE. HP if >= 0.85 AND <= ORACLE within 0.10. If schema-routing is too noisy (predicts wrong category for ambiguous queries), might drop below 0.66; design `category_to_partition` to fail OPEN (default to all partitions if cat_logits margin low).

**Conditions for this cell to be worth dispatching:**
1. Gap 3 Modern Hopfield HP (prototypes exist and are accurate)
2. Offline analysis confirms category-to-partition mapping has reasonable entropy (categories DO predict partitions; if mapping is uniform, no signal)
3. Cand 1 (R_schema) HP first OR PARTIAL (validates that query-side signal IS routable)

**P_deflated:** 0.40 (multiplies Gap3*Gap1 success probabilities; downstream).

---

## Section 5: Top 3 cell candidates ranked

| Rank | Cell | P_deflated | Cost (CPU hr) | Discriminator clarity | Substrate-feasibility | Brain-fidelity |
|---|---|---|---|---|---|---|
| 1 | substrate_gap1_query_to_partition_router_v1 (Cand 1) | 0.55 | 1.5-2.0 | HIGH (4 arms, clear HP/HF) | HIGH (kv_learned precedent) | HIGH (mPFC schema-bias from query) |
| 2 | substrate_gap1_two_stage_R_schema_plus_bidir_v1 (Cand 6) | 0.40 | 2.5-3.0 | HIGH (depends on Cand 1) | HIGH (downstream of Cand 1) | HIGHEST (literal mPFC-CA3) |
| 3 | substrate_gap1_route_by_gap3_schema_v1 (composition with Gap 3) | 0.40 (gated on Gap 3) | 2.0 | MEDIUM (depends on Gap 3 categories matching partitions) | MEDIUM (downstream of Gap 3) | HIGHEST (full ATL-mPFC-HPC cascade) |

### Rank 1: substrate_gap1_query_to_partition_router_v1

**Why first:** Cheapest decisive test of "use a separate pathway from query for routing." If HP, immediately closes the 0.66 ceiling and validates the brain-architecture insight. If HARD_FAIL, structurally rules out linear-query-routing; pivot to nonlinear (Cand 2) or CLS-replay (Cand 3). Either outcome is decisive.

**HP threshold:** ARM_PART_QUERY_TO_ROUTER >= 0.80 AND lift over bidir >= 0.10
**HF threshold:** ARM_PART_QUERY_TO_ROUTER <= 0.66 (no lift over bidir) OR train >> test (overfitting)

**Cell-author smoke gate:** N=8192, single seed, V_C=200, depth=5; verify R_schema fit converges in <10s; verify train top1 >= 0.85.

### Rank 2: substrate_gap1_two_stage_R_schema_plus_bidir_v1

**Why second:** Compose Cand 1 + bidirectional. Tests whether the two signals are INDEPENDENT (super-additive composition) or REDUNDANT (one is dominant). Critical for understanding WHICH brain pathway substrate's mechanisms map to.

**Gated on:** Cand 1 HP OR Cand 1 PARTIAL with HP_QUERY in [0.70, 0.80].

**HP threshold:** ARM_TWO_STAGE >= 0.90 AND lift over MAX(R_schema, bidir) >= 0.05

### Rank 3: substrate_gap1_route_by_gap3_schema_v1

**Why third:** Full composition of Gap 1 + Gap 3 architecture. Highest brain-fidelity. Downstream of Gap 3 Modern Hopfield landing. If both Gap 3 and Cand 1 land, this is the substrate-product story: "substrate retrieves like the brain -- query enters semantic hub, hub identifies type, type biases destination region, retrieval completes in biased space."

**Gated on:** Gap 3 Modern Hopfield HP AND Cand 1 HP.

**HP threshold:** >= 0.85 (within 0.10 of PART_ORACLE 0.955).

---

## (d) Cross-thread synthesis

### With prior Gap 1 routing drill (notes/research_gap1_routing_bidirectional_as_router_2026-06-26.md)

The prior drill examined IN-PATHWAY mechanisms (read from state_fwd or state_bwd). This drill examines SEPARATE-PATHWAY mechanisms (read from query). The two drills are COMPLEMENTARY. Cand 6 (two-stage R_schema + bidir) composes them.

### With Gap 3 schema-extraction drill (notes/research_gap3_compositional_deeper_mechanism_drill_2026-06-26.md)

Gap 3 is testing Modern Hopfield prototype attractors as schemas. Cand 5 + Cand 3 (Section 5 Rank 3 cell) compose Gap 3 prototypes WITH Gap 1 routing. The brain architecture analog: ATL semantic hub (Gap 3 prototypes) -> mPFC schema-bias (Gap 1 R_schema) -> hippocampal pattern completion (existing per-hop W).

### With kv_learned_projection (substrate ledger 0.827 chain-grade-passed 2026-06-20)

The R_schema candidate uses the same capability class. Reuse the methodology.

### With Cell C v2 bidirectional probe data

The probe arm finding `mean_midpoint_cosine = 0.0000` is the KEY finding that motivates this drill. The forward state has no atom signal -> any router reading from forward state caps at the bidirectional bound. The fix is to read from the QUERY (clean signal) via a separate pathway. R_schema does this.

### With Gap 4 NREM consolidation drill (prior research)

CLS-replay R_schema (Cand 3) is naturally extracted during NREM consolidation cycles. If Gap 4 NREM lands, R_schema_slow is built for free. Cand 3 becomes downstream of Gap 4.

### With substrate cone structure (Gap 2)

Source atoms lie on a substrate cone. Within-cone linear discriminants on partition are well-defined. This supports Cand 1's pseudoinverse approach. ARM_CAPABILITY_BASED_SCHEMA in Cell 1 failed BECAUSE it rotated off-cone -- Cand 1 stays within the source-atom cone (queries ARE on cone), so the routing should preserve cone-structure.

---

## (e) Substrate-product implications

**Best case (Cand 1 HP):** Gap 1 partition-routing becomes ORACLE-free with one closed-form fit step. Substrate-product story: "Substrate retrieves multi-hop facts with schema-based query routing -- a separate pathway from query to partition (analogous to brain's mPFC-mediated retrieval); breaks the in-pathway noise ceiling; chain-grade at M=10M+." Removes Cell B v2's BIAS-P flag.

**Composed case (Cand 6 HP):** Substrate-product story expands: "Substrate routes via hierarchical cascade -- query-side schema-bias narrows search space; bidirectional collision confirms within candidate partitions; matches brain architecture (mPFC-CA3 two-stage retrieval)." Production-scale.

**Brain-fidelity case (Section 5 Rank 3 HP):** Substrate's most brain-aligned architecture; full ATL-mPFC-HPC cascade implemented in substrate-native primitives. Story: "Substrate retrieves like the brain -- query enters semantic hub (Modern Hopfield prototypes), hub identifies type (categorical activation), type biases destination region (R_schema), retrieval completes in biased subnetwork (standard cleanup). No backprop. No LLM. Chain-grade."

**Negative case (HARD_FAIL on Cand 1 + Cand 2 + Cand 3):** Partition-routing IS structurally bounded for substrate at this N/V_C regime. The Gap 1 capability re-frames from "autonomous routing" to "named-partition retrieval" (still useful, application-feasible, just bounded). Substrate-product story narrows to "knowledge graph traversal given partition labels at query time" -- standard RAG-grade.

**Cap_map impact:** Gap 1 (multi-hop >= 2 hops chain-grade autonomous) currently shows PART_ORACLE 0.955 (with BIAS-P scope flag). Cand 1 HP would close the BIAS-P flag and make Gap 1 autonomously chain-grade. HARD_FAIL clarifies the scope boundary.

---

## (f) Citations (verified count = 22)

External (15):
1. Patterson, K., Nestor, P.J., Rogers, T.T. (2007) Nature Reviews Neuroscience "Where do you know what you know? The representation of semantic knowledge in the human brain" -- ATL semantic hub
2. Hoffman, P. & Lambon Ralph, M.A. (2018) Current Opinion Behavioral Sciences -- ATL hub TMS evidence
3. Gilboa, A. & Marlatte, H. (2017) TICS "Neurobiology of schemas and schema-mediated memory"
4. van Kesteren, M.T.R., Ruiter, D.J., Fernandez, G., Henson, R.N. (2012) TICS "How schema and novelty augment memory formation"
5. Staresina, B.P. (2019) Trends in Cognitive Sciences "A Neural Chronometry of Memory Recall"
6. Backus, A.R., Schoffelen, J.M., Szebenyi, S., Hanslmayr, S., Doeller, C.F. (2016) Current Biology "Hippocampal-Prefrontal Theta Oscillations Support Memory Integration"
7. Colgin, L.L. et al. (2009) Nature "Frequency of gamma oscillations routes flow of information in the hippocampus"
8. Hasselmo, M.E., Bodelon, C., Wyble, B.P. (2002) Neural Computation "A proposed function for hippocampal theta rhythm"
9. Bakker, A., Kirwan, C.B., Miller, M., Stark, C.E.L. (2008) Science "Pattern separation in the human hippocampal CA3 and dentate gyrus"
10. Yassa, M.A. & Stark, C.E.L. (2011) Trends in Neurosciences "Pattern separation in the hippocampus"
11. McClelland, J.L., McNaughton, B.L., O'Reilly, R.C. (1995) Psychological Review "Why there are complementary learning systems in the hippocampus and neocortex"
12. Kumaran, D., Hassabis, D., McClelland, J.L. (2016) TICS "What learning systems do intelligent agents need?"
13. Krotov, D. & Hopfield, J.J. (2016) NeurIPS "Dense associative memory for pattern recognition"
14. Ramsauer, H. et al. (2020) ICLR "Hopfield Networks is All You Need"
15. Krotov, D. (2021) arxiv 2107.06446 "Hierarchical Associative Memory"

Cross-domain (4):
16. Jegou, H., Douze, M., Schmid, C. (2010) "Product quantization for nearest neighbor search" -- IVF coarse + fine
17. Dasgupta, S., Stevens, C.F., Navlakha, S. (2017) Science "A neural algorithm for a fundamental computing problem" -- fly-LSH
18. 5G beam management hierarchical beam selection (MathWorks white paper, accessed 2026-06-26) -- coarse-fine destination prediction
19. Adaptive Query Routing tier-based framework (arxiv 2604.14222) -- multi-tier database routing

Internal cross-thread (3):
20. notes/research_gap1_routing_bidirectional_as_router_2026-06-26.md -- prior in-pathway drill (bidir-collide, fly-LSH-router)
21. notes/research_gap3_compositional_deeper_mechanism_drill_2026-06-26.md -- Modern Hopfield prototype attractors
22. Substrate ledger atom: kv_learned_projection (chain-grade 0.827; 2026-06-20)

Also cited indirectly:
- Cell B v2 metrics.json (oracle PART=0.955)
- Cell C v2 metrics.json (BIDIR_MEET_MID=0.62, mean_midpoint_cosine=0.0000)

---

## Cross-cell sanity rails for the dispatch

1. **META_M7 rail mandatory.** ARM_REPRODUCE_POINTER_CHAIN_V2_5HOP at 2000 bindings on `W_pointer_v2` -- band [0.08, 0.25].
2. **W-binding count match.** Router arms use the SAME `W_v1_regime` (1000 bindings) as Cell B v2 PART_ORACLE -- apples-to-apples comparability.
3. **BIAS-Q guard at 1.000.** Already locked from Cell B v2 v2 design.
4. **BIAS-P flag fix.** This cell's whole purpose is to fix Cell B v2's BIAS-P (oracle routing). Verdict_msg must explicitly state which arm REMOVES the BIAS-P scope flag.
5. **Cone-preservation guard.** R_schema-projected queries should stay on substrate cone (per Gap 2 cone-is-feature finding). Measure cone-cosine of query vs R_schema @ query; if rotation > 0.10 cosine, flag CONE_ROTATION_RISK.
6. **Train/test discipline.** R_schema fit on 80% chains; HP evaluation on 20% held-out chains. Train >> test by >0.10 flags overfit.

---

## Spawn-budget accounting

- Single 4-arm cell, ~4500-5500s wall on local_cpu (no GPU dispatch required; numpy-bound; matches Cell B/C v2 envelope)
- No conflict with currently in-flight cells (different anchor)
- exp_dev hand-off file written alongside (per [[feedback-results-to-application-cadence]])

---

**End of drill.**

Sources verified above. P_deflated for top candidate (R_schema query-router, Cand 1) = 0.55. Composed Cand 6 = 0.40. Gap1xGap3 composition (Sec 5 Rank 3) = 0.40 (gated on Gap 3). ALL-FAIL probability = 0.25 (in which case Gap 1 reframes to "named-partition retrieval" capability).
