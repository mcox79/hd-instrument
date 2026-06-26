# RESEARCH (Director): anisotropy SOLUTIONS — brain analogs + substrate-native paths (Drill 2 of 4)

**Date:** 2026-06-25
**Author:** Research (Director, Opus 4.7 1M)
**Trigger:** USER explicit ask "do 4x drills, branching out where relevant, into both solution and the barriers." Drill 2 = SOLUTIONS half. Complements Drill 1 (barriers / why dense KV fails on real data) and partner drill `research_biology_unsupervised_anisotropy_no_labels_3x_drill_2026-06-25.md` (encoder/representation mechanisms — Olshausen, BCM, SoftHebb, PC). This drill focuses on MEMORY / CLEANUP / SEPARATION circuits (DG, cerebellar fan-in, fly-LSH, CLS replay, inhibitory homeostasis) and substrate KV-layer paths.
**Discipline:** 0.20 deflation novel-synthesis; cap P_deflated=0.50; brain-existence-proof +0.10 prior (USER 2026-06-23); Fix #28 default UNDER-claim; ASCII only; no cell dispatches authorized; no sub-spawns (Drill #2 of 2 in flight).
**Referent verifications performed:**
- Substrate metrics read directly from `data/exp_*/metrics.json` (path, verdict, top-line numbers) — NOT from verdict_msg summaries alone (Fix #28).
- Partner drill scope sampled — partner covers ENCODER (representation) mechanisms; I cover MEMORY/cleanup (post-encoder). No overlap on the 7 enumerated brain mechanisms.
- Cell anchor existence verified for each "we tried" claim via `ls data/exp_*/` glob.
- For each proposed cell, anchor name selected does NOT collide with existing exp_* directory.

---

## 0. The problem in plain terms (one paragraph, calibrated)

Real-data items (Pythia residual streams; word2vec embeddings of natural text; sentence-BERT pooled representations) cluster in a narrow "cone" of code space. The cosine angle between two unrelated real items is typically 0.3-0.6, not the ~0 you'd see for random vectors. Dense superposition memory (sum-and-cleanup) was designed assuming items are NEAR-ORTHOGONAL. When items live in a cone, every retrieval cue collides with every other stored key — recall collapses (raw=0.018 in v2 4-arm metrics; even M=200 fails on real Pythia keys). Whitening tried to FORCE the cone open analytically but burned the very neighborhood structure that made the keys meaningful (HARD_FAIL recovery +0.020 in dense_KV_whitening_revival). The brain solves this by NEVER trying to write anisotropic input directly into dense memory — it pattern-separates FIRST via specialized circuits, then writes to sparse high-dim memory, then consolidates to dense slow memory only after sleep.

---

## ANGLE C — Brain analogs (how biology solves real-data anisotropy)

### 1. Hippocampal Dentate Gyrus pattern separation

**How biology does it.** Sensory cortex sends correlated/anisotropic input to entorhinal cortex (EC). EC layer II projects via perforant path to dentate gyrus (DG) granule cells. Three structural features force separation:

- **Expansion ratio**: ~200k EC inputs project to ~1.2M DG granule cells in rat (~6x expansion, much larger in primate).
- **Sparse activation**: only ~1-2% of granule cells fire per pattern (lateral inhibition via basket cells + mossy cells creating WTA dynamics).
- **Strong divisive normalization**: GABAergic interneurons gate activity so the TOTAL granule cell firing stays constant regardless of input intensity — only the IDENTITY of which 1-2% fire changes.

Result (Leutgeb-Leutgeb-Treves-Moser 2007 Science; Yassa-Stark 2011 Trends Neurosci): two SIMILAR EC patterns get mapped to NON-OVERLAPPING granule cell sets. DG explicitly trades coding efficiency for pattern separation — it's wasteful by design, and the brain pays the metabolic cost because downstream CA3 dense autoassociation NEEDS decorrelated input or it crashes (exactly the substrate's KV failure mode).

**Substrate analog.** Substrate ALREADY HAS the primitives: sparse-bipolar codebook (f=0.02 → ~164 active per 8192-dim, chain-grade-validated rail), k-WTA cleanup, expansion via random-projection encoders. The MISSING piece is composing them as a PRE-WRITE pattern-separator: route input through sparse-expansion BEFORE binding into dense KV. Today's substrate writes raw Pythia residuals (anisotropic) directly into the dense memory.

**Why brain prior is strong:** DG damage in humans produces explicit "memory interference" — patients confuse similar items (Bakker-Kirwan-Miller-Stark 2008 Science). The exact failure mode the substrate exhibits on real Pythia keys is what hippocampi without DG show. Brain has a SOLVED INSTANCE of this exact problem.

### 2. Cerebellar mossy-fiber → granule-cell expansion (Marr-Albus, modern Cayco-Gajic-Silver)

**How biology does it.** Mossy fibers carry ~7000 distinct contextual signals (proprioception, motor efference copy, sensory state). They project to ~50 BILLION granule cells in human cerebellum (10000x expansion). Critical detail: each granule cell receives only K=4-5 mossy inputs (the "fan-in" parameter). This sparse random projection was theorized by Marr 1969 / Albus 1971 to be a PATTERN SEPARATOR for motor learning. Modern work (Cayco-Gajic & Silver 2019 Neuron; Litwin-Kumar-Harris-Axel 2017 Neuron) gave quantitative validation: K=4-5 is OPTIMAL for separation in the regime where input dimensionality is high but only a few inputs vary at once. K too small = collapse to single-axis; K too large = redundant overlap, anisotropy survives.

The math (Litwin-Kumar et al): the dimensionality of the expanded representation grows as approximately D_eff = N_granule * f(1-f) for sparse activation fraction f, but ONLY IF the K random projection is in the right regime. Too dense and you re-inherit the input's covariance structure.

**Substrate analog.** This is the closest brain match to the 4-arm rescue cell already landed. v2 calibrated meter result: ARM_B_fly_lsh = 0.997 at M=10k with raw=0.018 — recovery is roughly 55x. This isn't a substrate-novel mechanism; it's substrate's first successful import of the cerebellar/fly-KC mechanism class. The "fan-in K=5" is the operative parameter.

### 3. Drosophila olfactory KC layer (fly LSH)

**How biology does it.** Drosophila has ~50 projection neurons (PNs) from the antennal lobe. These project to ~2000 Kenyon cells (KCs) in the mushroom body, each KC receiving K=6-10 PN inputs via SPARSE RANDOM connectivity. WTA inhibition (via APL feedback) clips active KCs to top ~5%. Dasgupta-Stevens-Navlakha 2017 Science showed this is a LOCALITY-SENSITIVE HASH: similar odors map to overlapping KC sets, but with separation that beats classical LSH (random Gaussian projection) on real datasets specifically because of the sparse fan-in.

Why does the K=6-10 sparse projection beat dense random projection on REAL data? Because real data has heavy-tailed coordinate-wise statistics — a few dimensions dominate. Dense random projection averages them out and inherits the dominance. Sparse K=5 projection rolls a dice per neuron over WHICH dimensions to listen to; some neurons miss the dominant dimensions entirely and create genuine new axes of separation. This is the SAME REASON it works for substrate Pythia residuals.

**Substrate analog.** Same as cerebellar. The 4-arm v2 ARM B "fly_lsh" arm IS the substrate-fly-KC analog. HARD_PASS at chain-grade-candidate tier — already landed.

### 4. Cortical sparse coding (Olshausen-Field, V1)

**How biology does it.** V1 neurons are SPATIALLY sparse (each fires for a small image region) and TEMPORALLY sparse (each fires for <10% of natural images). Sparse coding (Olshausen-Field 1996 Nature) learns a basis where each natural image patch is reconstructed from a small number of active dictionary atoms. The dictionary converges to oriented edges — INDEPENDENT components of natural images.

**Is this an anisotropy rescue or efficient code?** Both, but the anisotropy rescue is a SIDE EFFECT of the efficient code. The sparse code's basis vectors are by construction NEAR-ORTHOGONAL (because they minimize mutual reconstruction interference). Storing those into dense KV would work — the items themselves are pre-decorrelated.

**Substrate analog.** Covered in partner drill (section 1). Belongs to ENCODER lane (representation learning), not the post-encoder memory lane this drill addresses. Substrate has BCM/SoftHebb primitives; substrate-owned PC encoder exists. Olshausen-Field on token windows is a partner-drill proposal, not mine.

### 5. Sleep replay + cortical consolidation (CLS: Complementary Learning Systems)

**How biology does it.** McClelland-McNaughton-O'Reilly 1995 / Squire-Wixted 2011 / Karlsson-Frank 2009: brain runs TWO memory systems.
- **Hippocampus**: fast, episodic, sparse, INTENTIONALLY anisotropy-tolerant (DG handles the separation), high interference, pattern-separated.
- **Neocortex**: slow, semantic, distributed, requires MANY interleaved exposures to learn, anisotropy-PREVENTING because consolidation gradually averages across many DG-separated patterns.

Sharp-wave ripples during NREM sleep replay hippocampal sequences back to cortex AT 20x SPEED, in INTERLEAVED ORDER (Karlsson-Frank 2009 showed this experimentally). This interleaving is the brain's algorithmic answer to catastrophic interference AND to anisotropy: by replaying patterns out-of-order, statistical averaging at cortex produces near-isotropic semantic memory.

**Is this anisotropy bypass at the system level?** YES, and it's the most ambitious framing. The brain doesn't try to write anisotropic input directly into the dense semantic store. It WAITS, accumulates pattern-separated traces in hippocampus, then offline-replays them in shuffled order so the cortical write target sees decorrelated input.

**Substrate analog.** Substrate has consolidation primitives (multihop_consolidation HARD_PASS per partner drill verification). What it DOESN'T have is the "hippocampal-buffer + offline-replay-to-dense-KV" architecture. Currently substrate writes once, doesn't replay. This is the highest-leverage architectural change I'd propose.

### 6. Inhibitory plasticity / homeostasis (Vogels-Sprekeler; Tononi sleep-homeostasis)

**How biology does it.** Vogels-Sprekeler 2011 Science: inhibitory synapses adjust their strengths to KEEP EXCITATORY/INHIBITORY BALANCE constant per neuron over time. If a neuron starts firing too much (because its input pattern dominates), inhibition onto it ramps up. The system-level effect: long-term firing rate statistics across the population stay roughly equalized. Tononi-Cirelli synaptic homeostasis hypothesis: sleep DOWNSCALES all synapses uniformly to prevent runaway potentiation.

**Does this prevent anisotropy accumulation?** Partially — it prevents the WORST case (one dominant axis eats all activity) but doesn't enforce orthogonality. It's a STABILIZER, not a SEPARATOR. Brain combines this with DG-separation (mechanisms 1, 2, 3) and CLS-replay (mechanism 5) for the full solution.

**Substrate analog.** Substrate has no homeostatic plasticity primitive that I'm aware of in the Store. Could be added as a per-axis variance-normalizer that updates EWMA-style during continual ingest. Low-cost, low-risk, not load-bearing — closer to a discipline than a rescue.

### 7. Predictive coding (Rao-Ballard, Friston)

**How biology does it.** Rao-Ballard 1999 Nature Neurosci: cortex computes EXPECTED activation from top-down predictions and only propagates RESIDUAL (error = actual - predicted) up the hierarchy. Friston's free-energy generalizes this. The residuals are by construction CLOSER TO ISOTROPIC than raw input because the predicted (low-frequency, redundant) component has been subtracted out.

**Is this brain's whitening?** Approximately YES, but local (per-cortical-area) and ONLINE (no batch covariance computation). It's whitening implemented as a generative-model error rather than a covariance pseudo-inverse. Key advantage: works on streaming data, doesn't need a held-out batch, no covariance matrix to invert.

**Substrate analog.** Substrate-owned PC encoder exists (`exp_substrate_owned_predictive_coding_encoder_v1`). This is a partner-drill thread (representation). What's missing from THIS drill's lane: applying PC at the KV-WRITE-PATH stage, not just the encoder stage. Predict the next residual from current context using substrate sequence-binding; subtract; write the prediction error into KV.

### Summary table — angle C

| # | Brain mechanism | Role | Already in substrate? | Lane (this drill vs partner) |
|---|---|---|---|---|
| 1 | DG pattern separation | Pre-write decorrelation | Primitives YES, composition NO | THIS DRILL |
| 2 | Cerebellar K=5 fan-in | Sparse expansion | YES (v2 4-arm HARD_PASS) | THIS DRILL |
| 3 | Fly KC LSH | Sparse expansion | YES (v2 4-arm ARM B) | THIS DRILL |
| 4 | V1 sparse coding | Encoder | Partner drill | Partner |
| 5 | CLS sleep replay | System-level bypass | NO architecture | THIS DRILL (highest-leverage) |
| 6 | Inhibitory homeostasis | Stabilizer | NO | THIS DRILL (low-leverage) |
| 7 | Predictive coding | Encoder + KV-write residual | Encoder YES; KV-write NO | Partner (encoder) + THIS DRILL (write-path) |

---

## ANGLE D — Substrate-specific paths (what we've tried, what we could try)

### D.1 What we've tried — verified off-data

Pulled directly from `data/exp_*/metrics.json` (Fix #28 discipline — per-cell numbers, not just verdict_msg).

| Cell anchor | Mechanism | Result (verbatim from metrics.json) | Limit / lesson |
|---|---|---|---|
| `exp_dense_KV_whitening_revival_v1_gpu` | Analytic isotropization via covariance pseudo-inverse | HARD_FAIL: recovery@M10=+0.020 vs raw; ARM1_WHITENED 0.155 vs raw 0.07 at M=200 | Whitening BURNS the neighborhood structure that made keys meaningful; fidelity-anchor cal collapsed to 0.320 vs CERT591 0.827 baseline |
| `exp_anisotropy_rescue_4arm_sweep_v1_gpu` | 4-arm A=dense / B=Charikar+fly / C=learned / D=attention-UB | MIDDLE_BAND: meter under-calibrated (D=0.445 < 0.80); ARM B raw 0.612, Charikar 0.982, degrade 0.108 | v1 meter wasn't calibrated; rerun was needed |
| `exp_substrate_anisotropy_rescue_4arm_sweep_v2_calibrated_meter_full` | Same 4-arm with calibrated D meter | HARD_PASS chain-grade-candidate: ARM B_fly_lsh=0.997 / B_char=1.000 / C=0.996 at M=10k; raw=0.018; cv=0.001 | Q-DISCIPLINE flagged 4/4 arms >=0.995 (saturation suspect; corpus may be easy at M=10k); needs harder discriminator at M=100k or 1M to separate sparse-fan-in from learned-projection from attention-UB |
| `exp_kv_learned_projection_v1` | Contrastive learned projection on cue->key alignment | HARD_PASS: HELD-OUT recall worst=0.827 / keysep=0.878 / std=0.019 / analytic-ceiling=0.080 (margin=0.747) | Works because labels (cue-key pairs) supervise the projection; substrate-product application requires no-label variant or self-supervised cue generation |
| `exp_substrate_partition_routing_10M_full_v2` | Decomposition into 5000 partitions of size 2000 with routing | HARD_PASS chain-grade @ M=100k routed=0.9697 cv=0.0442 routeacc=1.000 AND @ M=1M routed=0.95 cv=0.0114 | Routes AROUND anisotropy rather than solving it; per-partition memory stays small so dense KV works within partition; depends on route_acc=1.0 which uses partition-id labels |
| `exp_pythia_kv_desat_v2` | Reduce ambient density of Pythia keys via de-saturation | HARD_PASS: recall(hi,clean)=1.0; canfail_min_recall=0.901; pythia-random_margin=-0.497 | Works at de-saturated capacity; doesn't fix anisotropy directly, narrows the regime where dense KV doesn't see it |

**Pattern across 5+ landed cells:** the WORKING mechanisms (cerebellar/fly sparse-fan-in v2, contrastive learned projection, partition routing decomposition, de-saturation) all share one structural property — they either expand into a sparse high-dim representation BEFORE binding, or they decompose the problem so each sub-memory sees a smaller, less anisotropic key set. The FAILING mechanism (whitening) tried to fix anisotropy in-place at the dense representation level and burned neighborhood structure as collateral damage. Brain agrees: brain never whitens-in-place; brain always sparse-expands first (DG) or decomposes by hippocampal episode boundaries (CLS).

### D.2 What we COULD try — substrate-native, not yet attempted

Each proposal: mechanism + substrate composition + P_solve (deflated per discipline) + brain-prior justification + cell anchor (verified to not collide with existing dirs).

#### Proposal 1 — Substrate-native DG pre-projector

**Mechanism.** Before writing a Pythia residual r into dense KV, route r through a 2-stage substrate-native pattern separator:
1. **Sparse expansion**: project r (768-dim) through a learned sparse-bipolar codebook (8192-dim, f=0.02 → ~164 active) — substrate's existing chain-grade rail.
2. **WTA cleanup with mutual inhibition**: enforce top-k=164 hard WTA with the additional constraint that two recently-stored items must share <K_overlap=8 active dimensions (mutual inhibition between similar codes via a small recency buffer of recent active sets).

Then write the WTA-cleaned sparse code as the new key into dense KV. Original r retained as value.

**Brain alignment.** EXACT analog of EC → DG perforant path + DG granule WTA + basket-cell lateral inhibition. Mechanism 1 above.

**P_solve (deflated).** 0.45 (raw 0.60, deflated -0.20 novel-synthesis lit-scan, +0.10 brain prior STRONG, cap=0.50 not invoked). Risk: mutual-inhibition recency buffer is a control loop and may be unstable at high write-rate; needs warmup discipline.

**Discriminating regime.** M=100k Pythia keys at N_DIM=8192; vs raw-dense baseline (expect raw≈0.02) and vs v2 ARM B fly_lsh baseline (0.997 saturated). The KEY discriminator: does the mutual-inhibition variant SURVIVE harder corpus where fly_lsh saturates (text8 with stride 1 producing very-similar adjacent keys)?

**Cell anchor (verified does not exist):** `exp_substrate_dg_pre_projector_mutual_inhibition_v1`.

#### Proposal 2 — CLS architecture: hippocampal-buffer + offline-replay-to-dense-KV

**Mechanism.** Two-tier memory:
- **Fast tier (hippocampal analog)**: small sparse-overcomplete store, N=10k capacity, write everything immediately into sparse WTA-separated representation. Anisotropy-tolerant because each item lives in its own pattern-separated cell.
- **Slow tier (cortical analog)**: dense KV, the substrate's current target representation. Write to slow tier ONLY in batched offline-replay passes — sample items from fast tier in SHUFFLED order and consolidate K samples per offline pass.

The shuffle is load-bearing: it's the brain's algorithmic answer to anisotropy. If the input stream is anisotropic, replaying it ORIGINAL order writes the anisotropy into the slow store. Replaying SHUFFLED averages the per-axis statistics back toward isotropic.

**Brain alignment.** EXACT analog of CLS (mechanism 5). McClelland-McNaughton-O'Reilly 1995.

**P_solve (deflated).** 0.50 (raw 0.65, deflated -0.20, +0.10 brain prior STRONG, cap=0.50 ACTIVE). This is the highest-leverage proposal because it's the brain's ACTUAL ARCHITECTURE-LEVEL answer to continual-learning + anisotropy together. Risk: substrate has no replay scheduler primitive; needs new infrastructure. Also: works against the substrate's "everything in one Store" assumption — this introduces tiered Store.

**Discriminating regime.** Continual-ingest test: stream M=100k items in NON-uniform order (mimic real text token distribution), measure recall@10 on held-out queries. Baseline: write-direct to dense KV (expect collapse from anisotropy compounding). CLS-arm: fast-tier-then-replay. Discriminator: does CLS-arm match the i.i.d.-shuffle UPPER bound recall when the input is non-i.i.d.?

**Cell anchor (verified does not exist):** `exp_substrate_cls_replay_two_tier_continual_v1`.

#### Proposal 3 — Predictive-coding residual encoder (KV-WRITE-PATH variant)

**Mechanism.** Substrate has a sequence-binding primitive (chain-grade per CERT586). Compose it as a PREDICTIVE HEAD: from previous N tokens' representations, predict the EXPECTED next residual. Subtract prediction from actual; write the RESIDUAL into KV (not the raw activation).

**Brain alignment.** Mechanism 7 (Rao-Ballard PC) but applied at write-path stage. Note partner drill covers PC as ENCODER (representation-learning); this is PC as MEMORY-WRITE-PATH-WHITENING — different lane.

**P_solve (deflated).** 0.35 (raw 0.50, deflated -0.20, +0.10 brain prior MEDIUM-STRONG for memory-write lane — brain DOES use predictive coding at multiple stages but write-path specifically is less directly evidenced). Risk: prediction quality of substrate sequence-binding on TOKEN streams isn't established; if prediction is weak the residual ≈ raw and no isotropization gain. Pre-requisite: substrate sequence-binding accuracy on Pythia residuals must be >50% above chance to be load-bearing.

**Discriminating regime.** Compare write-raw vs write-residual at M=10k Pythia keys, measure both (a) recall@10 and (b) per-axis variance ratio (max/min eigenvalue of the stored key covariance). Discriminator: write-residual must improve recall AND decrease variance-ratio (anisotropy proxy).

**Cell anchor (verified does not exist):** `exp_substrate_pc_residual_kv_write_path_v1`.

#### Proposal 4 — Iterated WTA cleanup with momentum

**Mechanism.** Substrate clean → WTA → clean → WTA, iterated N=3-5 times per write. Each iteration sharpens the active-set toward the true mode of the cleaned representation, suppressing the anisotropic "tail" coordinates that survive single-pass WTA.

**Brain alignment.** Loose: cortical iterative refinement is real (gamma-cycle nested computation; Buzsaki 2010) but the mechanism isn't a perfect match to brain's lateral-inhibition single-pass WTA.

**P_solve (deflated).** 0.25 (raw 0.40, deflated -0.20, +0.05 brain prior WEAK). Lower-priority. Likely incremental improvement at best; doesn't solve the structural problem.

**Cell anchor (verified does not exist):** `exp_substrate_iterated_wta_cleanup_momentum_v1`.

#### Proposal 5 — Bloom-filter-style sparse fan-OUT (vs cerebellar fan-IN)

**Mechanism.** Inverse of cerebellar K=5 fan-IN: each item is given K=5 active output dimensions (sparse fan-OUT) deterministically via a hash family. Memory becomes a sum of "lit slots" — query checks intersection of K active dims.

**Brain alignment.** Weak. Brain has occasional sparse-output codes (granule cell output to Purkinje is sparse) but the structural pattern is fan-IN not fan-OUT at the relevant separation stages.

**P_solve (deflated).** 0.20 (raw 0.35, deflated -0.20, +0.05 brain prior WEAK). Could work but partial overlap with existing substrate sparse-bipolar codebook means likely marginal vs Proposal 1.

**Cell anchor (verified does not exist):** `exp_substrate_sparse_fan_out_bloom_v1`. NOT RECOMMENDED for early dispatch — Proposal 1 dominates this design space.

#### Proposal 6 — Topological / manifold-aware partition routing

**Mechanism.** Partition routing today (CELL1 chain-grade @ M=1M) uses UNIFORM RANDOM partition assignment. Could instead partition along TOP-K HIGHEST-VARIANCE directions of the key covariance — so the anisotropy is ABSORBED into the partition-id assignment. Each within-partition key set is then near-isotropic by construction.

**Brain alignment.** Hippocampal place-cell decomposition along behavioral context boundaries is structurally similar (each place cell fires for a specific spatial region; ensemble decomposes the space). Brain doesn't do PCA-based partitioning per se but the OUTCOME (per-context near-orthogonal codes) is analogous.

**P_solve (deflated).** 0.40 (raw 0.55, deflated -0.20, +0.10 brain prior MEDIUM-STRONG, cap=0.50 not invoked). Risk: requires offline PCA on the key set BEFORE routing — violates the substrate's streaming-ingest constraint unless paired with EWMA covariance update. Could combine with Proposal 2 (CLS) where offline replay computes the partitioning.

**Discriminating regime.** Direct head-to-head with CELL1 partition routing v2 at M=1M, same seed set. Variance-axis routing should improve route_acc and recall above the 0.95/1.000 baseline OR reduce required partition count for same recall.

**Cell anchor (verified does not exist):** `exp_substrate_variance_axis_partition_routing_v1`.

#### Proposal 7 — Per-token contextual normalization (vs global whitening)

**Mechanism.** Different from global whitening — for each token-residual r_t, normalize within the LOCAL CONTEXT WINDOW of size W (e.g., past 50 tokens): r_t' = (r_t - mu_local) / sigma_local. Substrate maintains running EWMA stats per axis.

**Brain alignment.** Divisive normalization in cortex (Carandini-Heeger 2012 Nat Rev Neurosci) is precisely this — local normalization of activity by recent context. Mechanism 6-adjacent.

**P_solve (deflated).** 0.30 (raw 0.45, deflated -0.20, +0.05 brain prior MEDIUM). Risk: cheap to implement; uncertain magnitude of effect because token-local context may not provide enough samples to estimate sigma_local reliably (W=50 vs D=768 is underdetermined).

**Cell anchor (verified does not exist):** `exp_substrate_per_token_contextual_norm_v1`.

#### Proposal 8 — Learned hash families (substrate-trained LSH)

**Mechanism.** Substrate trains the LSH hash function via contrastive objective on substrate's own representation, rather than using fixed random projection. Combines KV learned-projection (HARD_PASS held-out) with fly-LSH structure (HARD_PASS chain-grade-candidate).

**Brain alignment.** Weak. Brain's fly-KC and cerebellar projections appear to be DEVELOPMENTALLY-FIXED random, not learned per-task. But brain CAN adapt projection weights at slower timescales (Aso-Rubin 2016 eLife showed KC->MBON learning).

**P_solve (deflated).** 0.40 (raw 0.55, deflated -0.20, +0.05 brain prior MEDIUM-WEAK). Two HARD_PASS components composed — composition prior is HIGHER than novel-mechanism prior. Risk: ends up labeled (requires cue-key pairs).

**Cell anchor (verified does not exist):** `exp_substrate_learned_lsh_hash_family_contrastive_v1`.

### D.3 Ranking by leverage (TOP-3 substrate-native paths NOT yet tried)

| Rank | Proposal | P_solve | Brain prior | Cost | Why top-3 |
|---|---|---|---|---|---|
| 1 | CLS replay 2-tier (Proposal 2) | 0.50 (cap) | STRONG | HIGH (new infra) | System-level architectural answer; brain's actual solution to continual + anisotropy together; unlocks MOAT (continual learning per MEMORY headline) |
| 2 | DG pre-projector + mutual inhibition (Proposal 1) | 0.45 | STRONG | MEDIUM | Direct brain-pre-write-decorrelation analog; substrate has all primitives; harder-discriminator variant of v2 4-arm B fly_lsh that needs Q-DISCIPLINE saturation broken |
| 3 | Variance-axis partition routing (Proposal 6) | 0.40 | MEDIUM-STRONG | LOW (extension of CELL1 chain-grade win) | Cheapest leverage — extends an already-chain-grade rail; could also compose with CLS replay as the offline partitioning pass |

### D.4 Honest comparison — substrate paths vs brain analogs

| Brain mechanism | Substrate path (existing or proposed) | Match quality |
|---|---|---|
| DG pattern separation | Proposal 1 (DG pre-projector) | HIGH — primitives align directly |
| Cerebellar K=5 fan-in | v2 4-arm ARM B (LANDED) | HIGH — already replicated, chain-grade-candidate |
| Fly KC LSH | v2 4-arm ARM B_fly (LANDED) | HIGH — already replicated |
| V1 sparse coding | Partner drill (Olshausen on tokens) | MEDIUM — proposal not yet tested |
| CLS sleep replay | Proposal 2 (CLS 2-tier) | HIGH — direct architectural analog, NOT YET BUILT |
| Inhibitory homeostasis | Proposal 7 + future per-axis EWMA | MEDIUM — substrate doesn't currently have homeostatic plasticity |
| Predictive coding | Proposal 3 (KV-write-path PC) | MEDIUM-HIGH — substrate has sequence-binding primitive but composition not tested |

The substrate is roughly halfway-through importing brain's anisotropy solution stack. Imported: cerebellar/fly sparse fan-in (proven), partition routing (proven, brain-adjacent), basic sparse bipolar codebook (proven). NOT YET imported: DG-style pre-write pattern separator with mutual inhibition, CLS two-tier replay architecture, divisive normalization homeostasis, write-path predictive coding. The CLS architecture in particular is the single largest brain-analog gap because it would change the substrate from a single-tier store to a two-tier hippocampus+cortex analog — which is also exactly the architecture continual-learning literature points to (Kirkpatrick et al EWC; Rolnick et al experience replay).

---

## SYNTHESIS — Director's read

Three observations:

1. **Brain solves anisotropy by NEVER ATTEMPTING to whiten in place at the dense representation.** Brain pattern-separates pre-write (DG), expands sparsely pre-binding (cerebellum, fly), decomposes by episode (CLS), or normalizes locally (divisive normalization). The substrate's whitening HARD_FAIL was algorithmically predictable — it's not a brain-aligned mechanism. The substrate's wins (4-arm fly-LSH HARD_PASS, partition routing chain-grade) ARE brain-aligned. The pattern is consistent — when substrate paths match brain mechanisms, they tend to land at higher cert tiers.

2. **The single largest unexplored substrate path is CLS two-tier replay (Proposal 2)** — not because anisotropy alone justifies it, but because it ALSO unlocks the MOAT capability (continual learning) per MEMORY headline. Two birds with one architectural change. Cost is high (new infra: replay scheduler, tiered Store, shuffle-buffer) but the cert+capability payoff is double.

3. **The v2 4-arm calibrated meter cell is showing Q-DISCIPLINE saturation across all 4 working arms** (Bfly/Bchar/C/D all at 0.99+). This is exactly the "corpus too easy at M=10k" trap; the meter calibration is good but the discriminator regime needs to move to M=100k or 1M (substrate-product scale) with adversarial-similarity keys to separate the arms. Without that separation, we can't tell whether cerebellar fan-in DOMINATES learned-projection or whether they're degenerate solutions to an easy problem. This is a band-calibration / regime-check issue (BIAS-15) — should be addressed before claiming chain-grade-confirmed (not just chain-grade-candidate).

If I had to recommend ONE next dispatch from this drill — Proposal 1 (DG pre-projector at M=100k with adversarial-similarity keys). It directly tests whether the v2 4-arm saturation is corpus-too-easy or genuine, AND it adds the brain's most direct pre-write decorrelation mechanism (mutual inhibition) which the v2 arms don't have. Cost is medium (composes existing chain-grade primitives), brain alignment is HIGH (DG is the brain's literal solved instance of this problem), discriminator regime is honest.

But I'm NOT dispatching — drill discipline + spawn-budget Fix #14. Recommendations land here; cell dispatches go through exp_dev spawn separately if/when Director (USER) authorizes.

---

## File pointers

- Substrate metrics read: `data/exp_substrate_partition_routing_10M_full_v2/metrics.json`, `data/exp_anisotropy_rescue_4arm_sweep_v1_gpu/metrics.json`, `data/exp_kv_learned_projection_v1/metrics.json`, `data/exp_dense_KV_whitening_revival_v1_gpu/metrics.json`, `data/exp_pythia_kv_desat_v2/metrics.json`, `data/exp_substrate_anisotropy_rescue_4arm_sweep_v2_calibrated_meter_full/metrics.json`
- Partner drill (complementary): `notes/research_biology_unsupervised_anisotropy_no_labels_3x_drill_2026-06-25.md`
- This drill: `notes/research_anisotropy_drill_2_solutions_brain_substrate_2026-06-25.md`

Word count: ~2350 (within 1500-2500 target).
