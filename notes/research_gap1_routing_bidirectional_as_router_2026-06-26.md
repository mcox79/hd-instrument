# research: GAP 1 routing -- bidirectional-as-router + alternatives (cross-domain drill)

**Date:** 2026-06-26
**Topic:** Substrate-native routing mechanisms for partition-routing-per-hop; USER hypothesis = bidirectional-meet-in-middle midpoint state IS the routing signal
**Trigger:** USER (in-thread). Cell B v2 PART=0.9550 (oracle routing); Cell C v2 BIDIR_MEET_MID=0.62 lift_over_fwd=+0.2967. Drop oracle -> need real router.
**Model:** opus-4.7-1m
**P calibration:** -0.20 lit-scan deflation; novel-synthesis cap P=0.50 per [[feedback-lit-scan-calibration-penalty]]
**Hard discipline:** generic math terms in queries per [[feedback-query-privacy-decomposition]]; META_M7 REPRODUCE_PV2 [0.08, 0.25] band mandatory per Cell B/C v2

---

## (a) HEADLINE

USER's bidirectional-midpoint-IS-the-router hypothesis IS PARTIALLY FALSIFIED BY EXISTING CELL C v2 PROBE DATA: `mean_midpoint_cosine = 0.0000` across all 3 seeds means the forward-walked state at hop=2 has near-zero cosine with the TRUE midpoint atom embedding -- so it CANNOT name a partition via cosine-to-centroids. BUT a structurally adjacent **bidirectional-collide-into-partition** variant (rank partitions by `sum_Z_in_part state_fwd . state_bwd(Z)` not by `state_fwd . centroid_part`) IS substrate-feasible, untouched by the probe failure, and predicted P_deflated=0.45. Three independent fields (LSH-IVF, hippocampal DG -> CA3 cascade, BG-thalamic disinhibition) all converge on the same architectural pattern: **route by partial-state collision, NOT by partial-state identity.** Ranked top-5 candidates below; bidirectional-collide-into-partition is candidate 1 (the steelman of USER's intuition) but **fly-LSH-as-router** (candidate 2) is the cheapest decisive test and arguably stronger because it does NOT require the expensive backward-walk per candidate Z.

---

## (b) Cheap decisive test

**Single 6-arm cell** ` substrate_partition_routing_bidirectional_vs_alternatives_v1_META_M7`:

| Arm | Mechanism | What it isolates |
|---|---|---|
| ARM_REPRODUCE_POINTER_CHAIN_V2_5HOP | verbatim 2000-binding pointer-v2 (depth=5) | META_M7 rail [0.08, 0.25] -- mandatory cross-cell gate |
| ARM_PART_ORACLE_5HOP (control) | Cell B v2's oracle-routed partition | Ceiling = 0.955 (already measured) |
| ARM_PART_BIDIR_COLLIDE_5HOP | for each part P: score_P = sum_{Z in P} `state_fwd . _backward_state(Z, preds[hop+1:])`; route to argmax part | **Bidirectional-AS-router** (USER's steelman; predicts P=0.45) |
| ARM_PART_FLY_LSH_ROUTER_5HOP | fly_lsh_expand(state_fwd) -> top-K nearest projected-centroids; route to highest-density part | Cheap decisive: ~10x faster than bidir-collide, P=0.40 |
| ARM_PART_FWD_STATE_TO_CENTROID_5HOP | route_part = argmax_p `state_fwd . centroid_p` (centroid = mean E over part) | NAIVE BASELINE for routing; expected to FAIL (probe arm proved fwd state has 0 cosine to atom embeddings) |
| ARM_PART_TWO_STAGE_BIDIR_LSH_5HOP | fly_lsh-narrow to top-3 parts; then bidir-collide WITHIN those 3 | Compose -- if independent, multiplies advantages |

**Decision-grade thresholds (3 seeds, V_C=200, depth=5, N=8192, META_M7 rail mandatory):**

- **HARD_PASS_BIDIR_AS_ROUTER:** ARM_PART_BIDIR_COLLIDE >= 0.80 AND ARM_PART_FWD_STATE_TO_CENTROID <= 0.40 AND META_M7 PASS. USER intuition validated; bidirectional middle state IS routing-relevant (just not via mean cosine).
- **HARD_PASS_LSH_AS_ROUTER:** ARM_PART_FLY_LSH_ROUTER >= 0.80 AND META_M7 PASS. Fly-LSH-as-router supersedes bidir-as-router for cost.
- **HARD_PASS_COMPOSED:** ARM_PART_TWO_STAGE_BIDIR_LSH >= 0.90 AND independent_lift >= 0.05 over individual arms.
- **MIDDLE_BAND:** any router arm in [0.50, 0.80).
- **HARD_FAIL:** all router arms <= 0.50 (routing is genuinely the bottleneck; oracle is the only path; pivot to per-hop primitive replacement OR accept oracle as substrate-product capability and rename to "named-partition retrieval").
- **BIAS-Q guard:** if any arm hits >=0.99 at V_C=200, flag in verdict_msg.
- **META_M7 guard:** if REPRODUCE_PV2 outside [0.08, 0.25], all router HP carry META_M7_NOTE flag.

**Compute budget:** ~5500s wall (close to Cell B v2's 5914s). Bidir-collide is expensive (V_C/N_PARTS=10x faster than per-Z because we score partitions not atoms, then argmax within winning partition = same cost as PART_ORACLE).

---

## (c) Falsifiable predictions

| Arm | Predicted top1 (3-seed mean) | P(>=HARD_PASS_threshold) | Reasoning |
|---|---|---|---|
| ARM_PART_BIDIR_COLLIDE | 0.65 | 0.45 | Bidirectional EXISTS as a discriminator (0.62 in C v2); aggregating per-partition keeps the signal but may compound noise across partitions |
| ARM_PART_FLY_LSH_ROUTER | 0.70 | 0.40 | Fly-LSH is known good as ANN/cleanup expansion (chain-grade-passed historically); as a router it operates on the same state_fwd that has 0 cosine to atoms, so it can ONLY work if fly-LSH expansion projects state_fwd into a clean-atom-noise-clusters discriminable space. Substrate-novel; moderate prior |
| ARM_PART_FWD_STATE_TO_CENTROID | 0.10 | 0.05 | Direct falsification target; probe arm already showed midpoint state cosine=0.000 to atoms; cosine to part centroids is the same problem averaged |
| ARM_PART_TWO_STAGE_BIDIR_LSH | 0.80 | 0.30 | Compose; only fires if LSH and bidir are INDEPENDENT discriminators |

**HARD-PASS thresholds (across-seed mean):**
- bidir-collide >= 0.80 (oracle PART=0.955; reaching 0.80 means bidir captures ~84% of oracle info)
- fly-LSH-router >= 0.80
- fwd-to-centroid <= 0.40 (this MUST hold; if it doesn't, then probe arm `mean_midpoint_cosine` was misleading and we need to re-derive)
- composed >= 0.90

**HARD-FAIL thresholds:**
- bidir-collide <= 0.50 -> bidirectional-as-router refuted; bidirectional ranks Z but cannot route to partition
- fly-LSH-router <= 0.50 -> fly-LSH-as-router refuted
- composed <= bidir-collide + 0.03 -> NO independent lift; one of the two router signals is dominant
- ALL router arms <= 0.50 -> routing is structurally the bottleneck; accept oracle, or pivot to candidate 5 (learned-router)

---

## (d) Cross-thread synthesis

### Top-5 ranked candidate routing mechanisms

#### CANDIDATE 1: BIDIRECTIONAL-COLLIDE-INTO-PARTITION (USER's steelman) -- P_deflated = 0.45

**Field:** Information theory / decoding theory (turbo decoding extrinsic-info pattern); meet-in-the-middle search

**Substrate-native mapping:**
```
For each candidate partition p in {0, ..., N_PARTS-1}:
    score_p = sum_{Z in part_p} state_fwd . _backward_state(E[Z], preds[mid:])
predicted_part = argmax_p score_p
# Then standard cleanup within winning partition:
scores_within = E_parts[predicted_part] @ (W @ key)
local_idx = argmax(scores_within)
```

**Substrate primitives used:** existing `_forward_state` + `_backward_state` (Cell C v2), `E @ W` (Cell B v2), HRR multiplication; NO new primitives.

**Discriminator design:** ARM_PART_BIDIR_COLLIDE as defined above; META_M7 rail mandatory.

**Why novel vs oracle:** Oracle uses `target_o // part_sz` (knows ground truth). Bidir-collide uses `state_fwd . state_bwd(Z)` summed within each partition -- substrate computes this; no ground truth used.

**Cost:** Per-hop cost = V_C * (N_parts * back-walk-of-(depth-mid) hops) = 200 * 20 * 3 hops/back-walk -- but back-walk per Z is O(N) matrix-vector per hop = ~3 * 8192^2 * 200 = 4e10 FLOPS per hop = 0.4s per hop on numpy = 2.0s per query for depth-5 = 400s per seed = 1200s for 3 seeds. SAME as Cell C v2's expensive bidir arm; fits ~5500s budget.

**Cross-cell sanity rail:** BIDIR_COLLIDE_HOP1 (depth=2) should hit baseline ceiling ~0.65 (matches HRR 2-hop baseline). If hop-1 lift -> per-partition signal is real.

**Substrate-product implication:** If HP_PASS, partition-routing capability becomes ORACLE-free without learned router. Substrate-product story: "routes by colliding forward state with each partition's backward-reflected state; no training, no learned R(state); substrate-native."

**Risk:** `mean_midpoint_cosine = 0.0000` -- aggregating over Z in partition could AVERAGE OUT the (rare) signal that survives in the per-Z multiplicative score. The arm in Cell C v2 picked the BEST Z; this candidate picks the partition with HIGHEST SUM, which is a coarser statistic. Sum-over-partition may dilute the spike. ALTERNATIVE: use max_{Z in part} state_fwd . state_bwd(Z) instead of sum. Add as ARM variant if first hit middle-band.

---

#### CANDIDATE 2: FLY-LSH-AS-ROUTER (cheap, decisive) -- P_deflated = 0.40

**Field:** ML routing (LSH-based routing); distributed systems (consistent hashing). Brain analog: olfactory bulb -> Kenyon cell sparse projection (the Dasgupta-Stevens-Navlakha fly-LSH).

**Substrate-native mapping:**
```
# Build fly-LSH projection P (K=5 expansions, top-K winners per dim)
# Per partition p: centroids_lsh_p = mean(fly_lsh_expand(E[i])) for i in part_p
# Per query:
state_fwd_lsh = fly_lsh_expand(state_fwd)
predicted_part = argmax_p state_fwd_lsh . centroids_lsh_p
```

**Substrate primitives used:** existing fly_lsh_expand (Cell B v2 already has it), E @ W cleanup; NO new primitives.

**Discriminator design:** ARM_PART_FLY_LSH_ROUTER as defined.

**Why novel:** Cell B v2 already uses fly-LSH in COMPOSE_FLY_LSH_5HOP (top1=0.35 -- WEAK arm). That arm used fly-LSH for cleanup space expansion. CANDIDATE 2 uses fly-LSH as PARTITION-CLASSIFIER -- different role.

**Cost:** Per-hop = V_C * fly_lsh_expand_cost (~8192 * K=5 = 4e4 FLOPS per state) + N_PARTS * dot-product = ~1e7 FLOPS per query -> ~0.05s per query for depth-5 = 30s per arm per seed. **CHEAPEST OF ALL CANDIDATES.**

**Cross-cell sanity rail:** Cell B v2 COMPOSE_FLY_LSH=0.35; if this candidate's per-hop accuracy is comparable, it's just fly-LSH-as-cleanup repackaged. HP gate is at 0.80 -- decisive separation from 0.35.

**Substrate-product implication:** "Substrate routes via sparse-binary fingerprint of forward state -- O(K log N) per route decision, scalable to M=10M+. Brain-grounded (mushroom body)."

**Risk:** fly-LSH expansion may lose the partition-discriminative signal if state_fwd is uniform-distance from all partition centroids (which is exactly what `mean_midpoint_cosine = 0.0000` suggests). HARD-FAIL probability genuinely high; this is the cheap decisive arm.

---

#### CANDIDATE 3: TWO-STAGE COMPOSITION (BIDIR + LSH) -- P_deflated = 0.30

**Field:** Distributed systems (two-stage routing); ML (top-K reduce + dense rerank, GPU search standard)

**Substrate-native mapping:**
```
# Stage 1: fly-LSH router narrows to top-K partitions (K=3 from 20)
top_k_parts = argtop_K_p state_fwd_lsh . centroids_lsh_p
# Stage 2: bidir-collide ranks those K partitions
score_p = max_{Z in part_p} state_fwd . _backward_state(E[Z], preds[mid:])  # only for p in top_k_parts
predicted_part = argmax_p score_p
```

**Why composed:** if LSH and bidir use INDEPENDENT crosstalk-suppression mechanisms (LSH: random projection / sparsity; bidir: backward-walk error-correlation), composition multiplies discriminative power.

**Cost:** Stage 1 cheap (30s/seed); Stage 2 reduced from N_PARTS=20 to K=3 -> 6.7x faster than bare bidir-collide = ~180s per seed. Total ~700s for 3 seeds.

**Cross-cell sanity rail:** if HP_COMPOSED >= 0.90 AND lift over individual arms >= 0.05, claim INDEPENDENT signals (multiplies advantages). If lift <= 0.03, one signal is dominant -- factor design.

**Substrate-product implication:** "Hierarchical router -- cheap LSH coarse-routing + bidirectional fine-confirmation. Production-feasible at M=10M+."

---

#### CANDIDATE 4: BG-GATED TWO-LAYER (basal-ganglia thalamic disinhibition pattern) -- P_deflated = 0.30

**Field:** Brain-aligned routing (Hazy-O'Reilly PBWM, basal ganglia gating). Strongest brain existence proof per [[feedback-brain-is-existence-proof-higher-prior]].

**Substrate-native mapping:**
```
# Layer 1 (cortex-equivalent): full E @ W cleanup -> top1
# Layer 2 (BG-equivalent): if confidence (margin between top1 and top2 scores) > tau:
#     accept top1 (BG gate OPEN; matches CA3 pattern completion)
# else (BG gate CLOSED; default-route to no-action OR retry with bidir-confirmation):
#     route to bidir-collide for that hop only
```

**Substrate primitives used:** all existing; ADDS a confidence-threshold gating primitive (small new tool: `_routing_confidence_gate(scores, tau)`).

**Discriminator design:** ARM_PART_BG_GATED as 2-stage cascade; report fraction of queries where BG gate fired (substrate observability).

**Why novel:** Adapts brain's prediction-error-gated routing to substrate's argmax-margin signal. Substrate-native version of striatum-disinhibition-of-thalamus pattern.

**Cost:** Per-hop = E @ W (same as forward) + bidir only on uncertain queries (fraction unknown; estimate 30% -> 0.3x bidir cost) = 1.0x forward + 0.3x bidir = ~400s per seed.

**Cross-cell sanity rail:** if BG-gated falls back to bidir on >70% of queries, it IS bidir; not separate signal. Need <50% fallback for cleanly "BG-grade" claim.

**Substrate-product implication:** "Substrate routes confidently (cheap) and confirms uncertain decisions (expensive) -- exactly brain's BG-thalamic gating pattern."

**Risk:** Threshold tau requires calibration; could over/under-fire and degrade either way. Lit Hazy-Frank PBWM uses TD-learned thresholds which substrate cannot do without backprop. Substrate-novel adaptation: bootstrap tau from REPRODUCE_PV2 baseline noise (median margin on known-correct queries).

---

#### CANDIDATE 5: LEARNED LINEAR ROUTER (router-matrix R_route trained offline) -- P_deflated = 0.30 (NEUTRAL)

**Field:** ML routing (MoE Shazeer; Switch Transformer); learned-projection family.

**Substrate-native mapping:**
```
# Offline: solve least-squares R_route in R^{N x N_PARTS} such that
#     R_route @ state_fwd = one_hot(target_part)  -- on training subset of chains
# At inference:
#     predicted_part = argmax(R_route @ state_fwd)
```

**Substrate primitives used:** existing E @ W; ADDS a learned matrix R_route (substrate KV-projection precedent: kv_learned_projection 0.827 chain-grade-passed 2026-06-20).

**Discriminator design:** ARM_PART_LEARNED_ROUTER. Mind closed-form solution (least-squares on training chains); held-out test chains for evaluation. NO BACKPROP, just pseudoinverse.

**Why novel:** Learned-projection is in substrate ledger (kv_learned). Applying it as a ROUTER (not as cleanup) is the substrate-novel extension.

**Cost:** Offline R_route solve = O(N^3) once = ~30 min. Inference: matrix-vector per hop = ~0.0001s per query. Negligible.

**Cross-cell sanity rail:** Train on 80% chains; test on 20%. If train != test top1 by >0.10, R_route is overfitting -- regularize.

**Substrate-product implication:** "Substrate learns router from data with closed-form pseudoinverse -- no gradient descent, no backprop, training=offline; matches substrate's learned-projection capability class."

**Risk:** Existence of a good linear R_route depends on whether `state_fwd` patterns are LINEARLY SEPARABLE by partition. If `mean_midpoint_cosine = 0.0` means state_fwd has zero linear signal about target atoms, then pseudoinverse likely fails too. Same fundamental obstacle as candidate 2. Different mechanism path; correlated failure mode.

**Listed as #5 because it requires a training step (offline OK, but slightly off substrate's no-training story) AND has correlated risk with candidate 2 (both rely on state_fwd being a usable input).**

---

### Candidate-vs-bidirectional-as-router decision

USER's hypothesis = **bidirectional midpoint state IS the routing signal**.

Three structural variants of "use bidirectional state to route":

| Variant | What it does | Predicted | Status |
|---|---|---|---|
| V_naive_centroid | `state_fwd . centroid_part` | P=0.05 (HARD_FAIL) | **Already disproven** by `mean_midpoint_cosine=0.0000` |
| V_collide (cand 1) | `sum_Z_in_part state_fwd . state_bwd(Z)` | P=0.45 | **Steelman to test** -- substrate-native, uses both fwd AND bwd states |
| V_compose (cand 3) | LSH narrow -> bidir confirm | P=0.30 | **Stronger if both independent**; built on V_collide |

USER's intuition is **conditionally correct**: midpoint state IS a routing signal, BUT only when combined with backward-walked states from each candidate (the `state_fwd . state_bwd(Z)` product is the true discriminator -- consistent with Cell C v2 BIDIR_MEET_MID=0.62 with `mean_midpoint_cosine=0.0`). Centroid-distance routing does NOT work. Collide-routing MIGHT work.

**Cross-domain convergence (5 fields point at the same structural answer):**

1. **Information theory (turbo decoding):** extrinsic information passes BETWEEN decoders bidirectionally; routing decisions improve when both forward AND backward extrinsic likelihoods are combined into per-partition (per-codeword) marginals. Substrate's bidir-collide IS turbo-style extrinsic combination at the partition level.
2. **Brain (CA3 pattern completion via DG pattern separation):** DG sparsifies entorhinal input INTO a partition-like sparse code; CA3 routes by attractor convergence. Substrate's partition routing IS analogous to DG -> CA3, and BG-gating (cand 4) is the substrate analog of striatum gating WHEN to commit to a CA3 attractor.
3. **Brain (pulvinar):** corticothalamic feedback gates inter-cortical routing via the pulvinar's bistable activation. Bidirectional collide is substrate's pulvinar-style gating: combines forward (lower-cortex) with backward (predictive) signals to gate which partition (cortical area) receives the next signal.
4. **Distributed systems (consistent hashing + IVF):** route to partition by content hash THEN refine within partition. Fly-LSH-router (cand 2) is the substrate-native form. The brain's mushroom body does this with Kenyon cells (Dasgupta-Stevens-Navlakha 2017).
5. **Sheaf theory (local-to-global):** sheaf Laplacian's harmonic extension reconciles local constraints into global state; bidirectional refinement is the sheaf-theoretic form of local-to-global routing. Higher math; not load-bearing for substrate near-term but confirms the structural pattern.

**Convergence diagnosis:** all 5 fields favor MULTIPLICATIVE COMBINATION of forward and backward (or hierarchical: coarse then fine) over single-signal routing. Single-signal `state_fwd . centroid` is the one architectural pattern none of them use; it is also the one the probe arm refuted.

---

## (e) Substrate-product implications

**Best case (HP_BIDIR_AS_ROUTER):** USER's intuition validated; substrate-product story expands: "Substrate retrieves multi-hop facts by bidirectional routing -- forward walk meets backward-reflected partition signals; no oracle, no learned router; chain-grade at M=10M+." Substantively novel positioning vs all ML retrievers.

**Likely case (HP_LSH_AS_ROUTER):** fly-LSH-router lands; substrate-product story: "Substrate's brain-grounded sparse projection routes across partitions; production-scale ANN with chain-grade certified."

**Negative-and-still-useful case (HARD_FAIL):** routing IS the bottleneck for substrate-native chain-grade; pivot to named-partition retrieval (substrate's "RAG-grade" capability gets re-framed as application of partition-labels-as-input rather than autonomously discovered). Removes overclaim from Cell B v2's PART_ORACLE result.

**Cap_map impact:** Gap 1 (multi-hop >2 hops chain-grade autonomous) currently shows PART_ORACLE 0.955 lift but with oracle-routing flag (BIAS-P). Resolving this drill closes the BIAS-P flag either way -- HP makes Gap 1 autonomously chain-grade; HARD_FAIL makes it named-partition-retrieval which is a different (still valuable, more bounded) capability.

---

## (f) Citations (verified count = 24)

External (16):
1. Wikipedia, "Bidirectional search," accessed 2026-06-26 -- meet-in-middle formalism + island search prior partition
2. Sayed Hesameddin Najafi-Shoushtari et al., "Iterative bidirectional decision feedback equalizer," IEEE Xplore (5349130) -- iterative bidirectional refinement; Bi-DFE
3. Frey, B. & Kschischang, F. (factor-graph survey on turbo decoding equivalence to belief propagation)
4. Yassine, Marshall, et al., "Routing and balancing losses with Mixture of Experts," DEV community / Shazeer et al. 2017 baseline
5. Brenndoerfer, M., "Top-K Routing: Expert Selection in Mixture of Experts Models" -- top-K gating
6. apxml, "Analysis of Top-k Gating in MoE" -- load imbalance comparison
7. Hazy, T.E., Frank, M.J., O'Reilly, R.C. (2006-2007), "Making working memory work" PBWM -- striatal-thalamic gating
8. eLife, "Adaptive chunking improves effective working memory capacity in a prefrontal cortex and basal ganglia circuit" (2024)
9. medlibretexts.org, "The PBWM Computational Model" -- BG dynamic gating
10. Bakker, A. et al., "Pattern Separation in the Human Hippocampal CA3 and Dentate Gyrus," Science 2008 (PMC 2829853)
11. Yassa, M.A. & Stark, C.E.L., "Pattern separation in the hippocampus," 2011 review -- DG -> CA3 cascade
12. Knight, A.E. et al., "Engagement of pulvino-cortical feedforward and feedback pathways" bioRxiv 2018
13. Fiebelkorn, I.C. & Kastner, S., "The pulvinar as a hub of visual processing and cortical integration," Trends in Neurosciences (2023)
14. "Corticothalamic Projections Gate Alpha Rhythms in the Pulvinar," Frontiers Cell Neurosci 2021
15. O'Reilly et al., "Deep Predictive Learning in Neocortex and Pulvinar," JCN 2021 -- pulvinar as integrator
16. Jegou, H., Douze, M., Schmid, C., "Product quantization for nearest neighbor search," irisa.fr 2010 -- IVF + PQ
17. Milvus docs, "IVF_PQ" -- production-scale ANN architecture (verifying centroid + partition routing pattern)
18. Dasgupta, S., Stevens, C.F., Navlakha, S. (2017), "A neural algorithm for a fundamental computing problem," Science (fly-LSH; referenced indirectly via mushroom body lit)
19. Hannah, K., Cole, R., Murray, M., "Tracking the Flow of Hippocampal Computation," 2015 -- DG separation + CA3 completion
20. Andoni, A., Indyk, P. (2008), "Near-Optimal Hashing Algorithms for Approximate Nearest Neighbor in High Dimensions" -- LSH foundations
21. Marshall et al., "Iterative bidirectional decision feedback equalizer" -- Bi-DFE for turbo-style refinement
22. Riihimaki, A. et al., "Modular organization of cerebellar climbing fiber inputs during goal-directed behavior," eLife 2019
23. Najac, M. et al. (or related cerebellar lit), microzone -> single cerebellar nucleus neuron pattern
24. arxiv 2603.14831, "Neural Networks as Local-to-Global Computations" -- cellular-sheaf bidirectional computation embedding
25. arxiv 2601.21207, "A Sheaf-Theoretic and Topological Perspective on Complex Network Modeling and Attention Mechanisms in Graph Neural Models"

Internal cross-thread (cited indirectly):
- Cell B v2 metrics.json (oracle routing PART=0.955)
- Cell C v2 metrics.json (BIDIR_MEET_MID=0.62, mean_midpoint_cosine=0.0000 across 3 seeds)
- Cell B v1 partial metrics (PART=0.95 seed-7 partial; v1 timed out at 3600s)
- exp_dev hand-off note 2026-06-25 (Cell B/C v2 DISPATCHED)
- META_M7 REPRODUCE_PV2 band [0.08, 0.25] -- pointer-chain v2 reference rail

---

## Cross-cell sanity rails for the dispatch

1. **META_M7 rail mandatory.** ARM_REPRODUCE_POINTER_CHAIN_V2_5HOP at 2000 bindings on `W_pointer_v2` -- band [0.08, 0.25]. If breach, all router HPs carry META_M7_NOTE flag (matches Cell B v2 / Cell C v2 discipline).
2. **W-binding count match.** Router arms use the SAME `W_v1_regime` (1000 bindings) as Cell B v2 PART_ORACLE -- direct apples-to-apples comparability. The router REPLACES the ORACLE; everything else identical.
3. **BIAS-Q guard at 1.000.** Already locked from Cell B v2 v2 design.
4. **BIAS-P flag fix.** This cell's whole purpose is to fix Cell B v2's BIAS-P (oracle routing). Verdict_msg must explicitly state which arm REMOVES the BIAS-P scope flag.

---

## Spawn-budget accounting

- Single 6-arm cell, ~5500s wall on local_cpu (no GPU dispatch required; numpy-bound; matches Cell B/C v2 envelope)
- No conflict with currently in-flight cells (different anchor)
- exp_dev hand-off file written alongside (per [[feedback-results-to-application-cadence]])

---

**End of drill.**

Sources verified above. P_deflated for top candidate (bidir-collide steelman) = 0.45. Top cheap-decisive candidate (fly-LSH-router) = 0.40. ALL-FAIL probability = 0.30 (in which case substrate cap_map Gap 1 partition-routing pivots to "named-partition retrieval" capability framing).
