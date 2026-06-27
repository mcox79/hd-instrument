# Research — CORTEX content-extraction failures: 4x cross-discipline drill on SELECTIVE ABSTRACTION

**Filed-by:** Research (Opus 4.7 1M)
**Date:** 2026-06-26
**Drill type:** 4x cross-disciplinary REVIVAL drill (USER directive) on FIVE related CORTEX content-extraction HARD_FAILs / MIDDLE_BAND PARTIALs
**Trigger:** Substrate has working CORTEX scaffolding (NREM replay chain-grade, TWO_TIER generational HARD_PASS) but failing CORTEX content-extraction. Five cells reviewed (see Section 0). Unifying diagnosis: substrate has **no working selectivity primitive** — every tested mechanism either preserves nothing (global downscale, narrow-budget STC) or preserves everything (infinite-budget STC, no-combine cold storage). The CRITERION for "this is important; protect it / abstract this" does not exist as a substrate primitive.
**Prior closely-adjacent drill:** `notes/research_gap4_brain_selective_homeostasis_2026-06-26.md` (proposed M5 STC tagging → **REFUTED** by `exp_gap4_stc_capture_selective_downscale_v1` HARD_FAIL); this 4x drill therefore goes BEYOND brain-only into 4 disciplines for mechanism-class diversity.

---

## HEADLINE

The five failed cortex cells all share a single root defect: **substrate has no per-atom IMPORTANCE signal that is independent of weight magnitude**. STC tried to derive importance from `|dW|>theta` (write-amplitude) and failed because all writes have ~similar amplitude in HRR/Hebbian regime. Global downscale tried magnitude-thresholding implicitly and failed because magnitude IS noise-floor proximity (Section 3 of parent drill). Schema-extraction tried capability-relations and failed because capability/affordance composition doesn't map onto HRR role-filler arithmetic. R-schema closed-form routing tried linear extraction and failed because partition-membership is non-linearly encoded.

**The unified frame:** the brain solves "what's important" with a **separate, pre-existing, neuron-level excitability biasing signal** (CREB / dopamine / novelty / VTA) that operates BEFORE / ORTHOGONAL TO the per-synapse plasticity rule. Substrate has only the synapse rule. **Missing primitive: a per-atom EXCITABILITY / ALLOCATION TOKEN that biases consolidation independently of weight magnitude.**

The four disciplines converge on a shared answer with different math:
- **PURE MATH**: Information bottleneck Lagrangian `min I(X;T) - beta*I(T;Y)` requires a TARGET `Y` (the side-information / labels-at-readout); MDL requires a separately-encoded MODEL; sparse-coding K-SVD requires a separately-tracked DICTIONARY USAGE counter; persistent homology requires a separately-computed PERSISTENCE score (death - birth).
- **BIOLOGY**: PKMzeta + AMPA-trafficking maintain late-LTP at *specific synapses* selected by separate calcium-coincidence signal; CREB excitability biasing pre-selects which neurons can BECOME engram cells before the experience.
- **BRAIN**: Engram-allocation theory (Josselyn-Frankland): the brain picks consolidation targets via EXCITABILITY-BASED COMPETITION operating on time-scales of minutes-hours BEFORE the to-be-consolidated event arrives; novelty/dopamine elevates excitability of HC neurons via VTA-HC loop, biasing which atoms get tagged; the BRAIN-CRITICAL POINT — selectivity is upstream of plasticity, not downstream.
- **MATERIALS**: Self-organized criticality (BTW sandpile) achieves selective avalanche-cluster formation via SEPARATE drive-vs-dissipation dynamics; the "what gets reorganized" emerges from drive imbalance, NOT from current pile-height alone.

**All four disciplines tell substrate: importance must be a SEPARATE TENSOR that is updated ORTHOGONALLY to W.** Substrate has been trying to read importance OFF OF W. That cannot work because W is the thing being homeostatically pressured; using W to decide what to protect is reading the noise to suppress the noise.

**P_deflated for at least one of the 4 ranked anchors closing one cortex-content-extraction failure:** **0.45** (capped at novel-synthesis ceiling; calibration penalty applied per [[feedback-lit-scan-calibration-penalty]]).

---

## Section 0 — The 5 failed/partial cells (re-read carefully)

Verified per `peek_arm_metrics.py`-style reading of metrics.json (per-arm not verdict_msg, per Fix #28):

| Cell | Verdict | Mechanism class | Why it failed (root cause) |
|---|---|---|---|
| `cortical_schema_extraction_compositional_generalization_v1` | **MIDDLE_BAND** | Schema-mediated retrieval | ARM_FEATURE_BASED lifts +10pp (0.473 vs 0.373 baseline); ARM_CAPABILITY_BASED HURTS by -8pp; ARM_COMBINED ≈ baseline. **Read:** feature-properties compose via simple vector addition (which substrate already does); capability/affordance relations require typed binding which HRR role-filler does NOT trivially provide for transitive relations. |
| `gap4_stc_capture_selective_downscale_v1` | **HARD_FAIL_DESTROYS_OLDER_LIKE_GLOBAL** | STC tagging (Frey-Morris brain mechanism) | budget=100 → only 2400/16M tagged (0.014%); budget=infinity → 100% tagged; tagging criterion `|dW|>theta_tag=0.5` fails because Hebbian writes have unit-norm amplitude, so theta_tag is either always-fires (everything tagged) or never-fires (nothing tagged). **Root: tag signal lives in same space as W; can't discriminate.** |
| `substrate_synaptic_homeostasis_global_downscale_v1` (Cell B) | **HARD_FAIL_DESTROYS_OLDER** | Global multiplicative downscale (Tononi-SHY) | All 3 schedules (0.99/100, 0.95/500, 0.999/50) destroy older patterns 100% by cycle ~1750-2500. **Root: multiplicative downscale is anti-selective on small weights near noise floor.** |
| `gap4_cold_storage_no_combine_v1_smoke` | **HARD_FAIL** | Two-pool cold-storage / no-combine retrieval | At 500-cycle smoke, baseline forget=0.0 (regime not saturating); all cure arms forget 100%. **Root: cold-storage migration criterion was magnitude-based (K_migrate=200/100); migrated tokens were not actually selectively preserved on retrieval.** |
| `gap1_partition_routing_cortex_R_schema_closed_form_v1_META_M7` | **HARD_FAIL** | Closed-form linear R-schema routing | PART_R_SCHEMA arm fails (cv=0.0, lift over bidir=-0.67); R_SCHEMA_OVERFIT (3/3 train >> test by >0.10); CONE_ROTATION_RISK (3/3 cone_cos<0.90). **Root: partition information NOT linearly extractable from query embedding; substrate's "which cortex partition does this go to" is non-linear and requires either Modern Hopfield-style attractor routing or replay-extracted CLS targets.** |

**Unifying diagnosis (CONFIRMED across 5 cells):** every mechanism tested tried to *read selectivity off of W* — `|dW|`, `|W|`, magnitude-threshold, linear-projection-of-query-embedding. **None of these worked because W is itself the noisy thing.** Importance is a property of the ATOM's meaning / re-access frequency / type / role in compositional structure — none of which is recoverable from W magnitude.

---

## Section 1 — PURE MATH lens on selective abstraction

### 1A. Information bottleneck (Tishby) and rate-distortion

The IB Lagrangian: minimize `I(X;T) - beta*I(T;Y)` where T is the compressed representation, X is raw input, Y is the side-information (downstream task / labels-at-readout). **The math REQUIRES a separately-specified Y to know what to keep.** Without Y, you get a max-compression representation that throws away signal (the substrate's failure mode).

[Information bottleneck and representation learning](https://yichaocai.com/posts/information-bottleneck.pdf): "With side information, information is maximized about one target variable and minimized about another."

**Substrate translation:** every "downscale / consolidate / abstract" operation needs an EXTERNAL Y — a side-information tensor that tells the operation which atoms have downstream-utility. Substrate has never tracked Y. The closest substrate primitive is the `cleanup_memory` retrieval log — IF that log were aggregated into a per-atom hit-count tensor, that would be a substrate-native Y.

**Math:** for a continual-ingest substrate, Y[i] = expected_future_retrievals(atom_i). Compute as EWMA over recent retrieval-events: `Y[i] = (1-alpha) * Y[i] + alpha * 1[atom_i retrieved at cycle t]`. Now the IB-style downscale rule is: `W[i] *= gamma` only where `Y[i] < y_thresh`. This is **utility-gated downscale** — substrate-feasible, substrate-novel, with a clean information-theoretic foundation.

### 1B. Sparse coding / dictionary learning (K-SVD, LASSO)

K-SVD (Aharon, Elad, Bruckstein 2006): alternates sparse-coding step (find which dictionary atoms best explain the data) with dictionary-update step. **The selectivity primitive is the per-atom USAGE COUNT** — how often an atom is selected during sparse-coding. Unused atoms get replaced with new directions; over-used atoms get split.

[K-SVD overcomplete dictionaries](https://www.ccs.neu.edu/home/eelhami/courses/EE290A/K-SVD_Elad.pdf): "Designing dictionaries to better fit this model can be done by ... adapting the dictionary to a set of training signals."

**Substrate translation:** the substrate's atoms (rows of cleanup matrix) are exactly a dictionary; the substrate's writes are exactly sparse-coding events (one atom is the matched target). The substrate has no usage-counter tensor — but it should. **Dictionary-usage-gated atom turnover** = increment U[i] on every cleanup-retrieval that hits atom_i; periodically REPLACE atoms with U[i] < u_thresh with fresh random directions OR with bound combinations of frequently-co-retrieved atoms.

This is **selective abstraction via composition** — the unused atoms get repurposed as bound combinations of useful ones (RG-style coarse-graining; see 1D).

### 1C. MDL / Kolmogorov complexity

MDL: best model M* minimizes `L(M) + L(D|M)` — model length + data-encoding-length-given-model. **The selectivity primitive is the description-length BUDGET** — only patterns that compress the data justify their inclusion in the model.

[MDL principle](http://www.modelselection.org/mdl/): "The best explanation for a set of data is one that allows you to compress the data as much as possible."

**Substrate translation:** MDL gives a substrate-native test for "is this atom worth keeping?" — keep atom_i IFF its inclusion in the cleanup memory reduces total bits-to-encode the recent retrieval history by more than the bits required to describe atom_i. For HRR vectors at N=4096 with bf16, atom_i costs ~8KB. It must encode at least 8KB of retrievable structure to be worth keeping. **MDL-gated atom turnover** = replace atoms whose `bits_saved < bits_cost`.

### 1D. Renormalization group / hierarchical coarse-graining (Mehta-Schwab)

Mehta-Schwab 2014: variational RG ↔ deep learning; each layer of an RBM/DBN is a coarse-graining step that extracts increasingly abstract features. **The selectivity primitive is the COARSE-GRAINING FUNCTION** — which microscopic degrees of freedom get pooled into a macroscopic one.

[Exact mapping between RG and Deep Learning](https://arxiv.org/abs/1410.3831).

**Substrate translation:** when 5 atoms (red_ball, blue_ball, green_ball, yellow_ball, black_ball) co-occur with the same role-binding pattern, RG says **replace them with a single coarse-grained atom (ball) plus a residual code (color)**. Substrate doesn't do this. **Substrate-native RG step** = detect atom clusters with high mutual overlap in their role-binding signatures (via cleanup-matrix block diagonal structure); replace the cluster with a single representative atom + a small set of residual codes. This is THE missing compositional-abstraction primitive.

### 1E. Persistent homology / topological feature selection

Persistent homology assigns birth-death pairs to topological features; **persistence = death - birth = selectivity score**. Long-persistence features are signal; short-persistence are noise.

[Persistent homology stability](https://arxiv.org/pdf/2511.04873): "Features with large persistence are typically interpreted as signal; short-lived features are attributed to noise."

**Substrate translation:** for each atom, track its BIRTH (cycle of first write) and current LIFETIME (cycles since last retrieval). Atoms that survive many cycles AND get re-retrieved have long persistence. Atoms born recently OR never re-retrieved have short persistence. **Persistence-gated retention** is exactly the brain's STC-with-real-importance-signal — it's the criterion STC was MISSING.

---

## Section 2 — BIOLOGY lens on selective consolidation

### 2A. PKMzeta as memory-maintenance kinase

PKMzeta is the kinase that *maintains* late-LTP by stabilizing AMPA receptors at potentiated synapses. **Crucially:** PKMzeta acts AT SYNAPSES THAT WERE ALREADY TAGGED. It does NOT decide WHICH synapses to maintain; that decision was made earlier by Ca-coincidence + STC tagging + PRP capture.

[PKMzeta and AMPA receptor trafficking](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1006147): "PKMζ maintains memories by regulating GluR2-dependent AMPA receptor trafficking ... late long-term potentiation by ... trafficking of postsynaptic AMPA receptors."

**Substrate translation:** PKMzeta is a MULTIPLIER on previously-tagged weights. Substrate-native: a separate PERSISTENCE tensor P[i] that, once set to 1 for atom_i, GUARANTEES atom_i's W is preserved through subsequent downscales (`W[i] *= 1.0` when `P[i]==1`, else `W[i] *= gamma`). This is what STC's "PRP" was supposed to provide — but STC failed because **TAGGING didn't pick the right atoms** (theta_tag=0.5 was wrong gate). PKMzeta tells us: the MAINTENANCE is fine; the GATING needs to come from somewhere else (Sections 1A/1E/2C/3A).

### 2B. Heterosynaptic plasticity and synaptic competition

STDP-with-BCM-sliding-threshold produces **competition** between synapses for limited resources: synapses that co-fire with strong postsynaptic spikes WIN; nearby synapses LOSE (LTD via heterosynaptic competition).

[STDP + BCM heterosynaptic plasticity](https://www.frontiersin.org/journals/synaptic-neuroscience/articles/10.3389/fnsyn.2011.00004/full): "Spike-time-dependent plasticity and heterosynaptic competition organize networks to produce long scale-free sequences of neural activity."

**Substrate translation:** when atom_i is reactivated during cleanup, COMPETING atoms (high cosine-similarity to atom_i but in different conceptual cluster) get DEPRESSED. This is the **noise-floor-management primitive substrate needs** — instead of trying to preserve everything, the substrate should ACTIVELY DEPRESS competitors-to-recently-used atoms, freeing capacity. Substrate-native: `W[j] *= (1 - eta * cos(i,j))` for all j in top-K nearest to recently-retrieved atom_i, where eta is small.

### 2C. CREB-mediated excitability allocation (THE most important biology lens insight)

**This is the key.** [Memory allocation via CREB](https://www.nature.com/articles/npp201673): "Neurons with higher intrinsic excitability, likely as a consequence of elevated CREB levels, exhibited enhanced synaptic strength compared to neighboring neurons, which increased their inclusion probability into the memory ensemble. ... A competitive nature of allocation emerged from these findings, whereby neurons with higher excitability 'win' the competition to encode the memory."

**The brain does NOT decide what's important DURING the experience.** It pre-biases WHICH NEURONS CAN ENCODE before the experience arrives, via slow CREB-dependent excitability fluctuations on minutes-to-hours timescales. **Selectivity is upstream of plasticity.**

[Dopamine + VTA + novelty + STC](https://www.cell.com/trends/neurosciences/fulltext/S0166-2236(18)30273-X): "Novelty-associated memory enhancement occurs through synaptic tagging and capture (STC), with dopamine signaling via D1/D5 receptors in the hippocampus being crucial for the persistence of synaptic plasticity and memory."

**Substrate translation (CORE INSIGHT):** substrate needs a **per-atom EXCITABILITY tensor E[i] that is updated SEPARATELY from W** based on:
- (a) novelty signal — atoms whose write triggered a refuse-gate fire (substrate detected the input was OOD relative to existing atoms) get high E
- (b) reward/utility signal — atoms involved in successful retrievals (queries where cleanup hit > some threshold) get E-boost
- (c) base-rate decay — E[i] decays slowly so old-and-unused atoms become low-E (eligible for replacement)

Downscale / replace operates on `E[i] < e_thresh`, NOT on `|W[i]| < w_thresh`. **This is the missing primitive.** No prior substrate cell has implemented per-atom excitability as a SEPARATE TENSOR.

### 2D. Glial pruning (microglia C1q + astrocyte tripartite synapse)

Activity-dependent: low-activity synapses get C1q-tagged for microglial engulfment over weeks. **Selectivity primitive: cumulative activity over LONG timescales.**

**Substrate translation:** astrocyte-pruning is the FINAL cleanup step that operates on E[i] AFTER E[i] has had time to drop to baseline via decay. Substrate-native: every 5000 cycles, atoms with `E[i] < e_min` get OVERWRITTEN by new bound combinations of frequently-co-retrieved atoms (per Section 1D RG step). This is **explicit capacity reset**.

---

## Section 3 — BRAIN lens on schema-grounded consolidation

### 3A. Engram-allocation theory (Josselyn-Frankland-Tonegawa) — refined

The engram literature has produced THE definitive recent result: [Writing the Engram (2025 review)](https://onlinelibrary.wiley.com/doi/10.1111/jnc.70328) — "memory allocation refers to the selective recruitment of neurons into ensembles that encode, store and retrieve experience."

The CORE mechanism (combining multiple papers in this lit):
1. Pre-learning, neurons fluctuate in excitability over hours (slow CREB cycles).
2. Novelty / dopamine surges bias which sub-population is high-excitability at experience time.
3. The experience drives strong Hebbian plasticity ONLY in the high-excitability subpopulation (since they're closer to spike threshold).
4. Those tagged-via-excitability neurons get PRP capture → late-LTP → engram cells.
5. Subsequent retrieval reactivates these specific cells; the engram is **READ via excitability bias**, not via weight magnitude.

**This is a 5-step pipeline with FOUR separate signals** (CREB, dopamine, Ca-coincidence, PRP). **Substrate has only 1: the weight matrix W.**

[Engram cells review 2023](https://pmc.ncbi.nlm.nih.gov/articles/PMC10618102/): "Consolidated engrams are selectively re-engaged when the memory is retrieved, with engram cells representing a select subset of neurons that undergo molecular and structural modifications."

### 3B. Schema-guided consolidation (Tse-Morris-Preston-Eichenbaum)

[Schema-dependent gene activation](https://www.science.org/doi/10.1126/science.1205274) and Tse 2007/2011: when new learning is CONSISTENT WITH an existing schema, consolidation is RAPID (hours not weeks) and bypasses hippocampus, going directly to cortex.

**Substrate translation:** the schema is the PRE-EXISTING structure in W; the test for "consistent with schema" is the cleanup-cosine to nearest existing atoms. If the new atom is high-cosine to an existing schema-anchor, it gets **fast-tracked to consolidated state** (e.g., immediately set E[i] = 1.0 and bound into the existing schema's role-filler structure). If low-cosine, it goes to a high-turnover transient pool until either reactivated or pruned.

This **schema-fast-track** is a substrate-novel architecture: most existing substrate cells treat all new atoms uniformly. The brain doesn't — well-anchored atoms get cheap fast consolidation, novel atoms get expensive episodic-tagged consolidation.

### 3C. CLS theory (McClelland-O'Reilly) — what substrate has and what it's missing

[Hippocampal-Inspired Continual Learning 2025](https://arxiv.org/pdf/2508.16651): substrate has the CLS architecture (TWO_TIER generational W_young/W_old, NREM replay between them). What CLS adds that substrate is MISSING:
- **Pattern separation in DG** (the substrate's writes don't go through an orthogonalization step before reaching W_young)
- **Indexing in CA3** (substrate's W_young has no explicit index from input-pattern to stored-atom)
- **Schema-vs-novelty routing** (substrate's TWO_TIER promotion is recall-based, not schema-similarity-based per Tse)

### 3D. Forward vs reverse replay direction

NREM SWR (sharp-wave ripples) include both forward replay (planning) and reverse replay (reward learning). **Selectivity primitive: replay direction encodes USE-CASE.** Forward = predict next; reverse = credit assignment to past.

**Substrate translation:** substrate's current NREM replay is bidirectional and uniform. Substrate-native: implement REVERSE REPLAY specifically for credit-assignment — when atom_i was retrieved at cycle T and contributed to a successful downstream query, REVERSE-REPLAY the predecessor atoms (atom_{i-1}, atom_{i-2}, ...) with PRIORITY, boosting their E. This is what makes the brain learn from rewards.

---

## Section 4 — MATERIALS SCIENCE lens on selective ordering

### 4A. Self-organized criticality (Bak-Tang-Wiesenfeld sandpile)

[BTW sandpile as percolation transition](https://link.aps.org/doi/10.1103/PhysRevE.111.024111): "The Bak, Tang, and Wiesenfeld (BTW) and Manna sandpile models are instances of percolation transitions from disordered to ordered phases. ... By introducing drop density as a continuously adjustable control variable that quantifies the average number of particles added to a site, researchers observe a transition in the sandpile from a subcritical to a critical phase."

**Substrate translation (POWERFUL):** the substrate's cleanup matrix at saturation is a SANDPILE. Each new write adds "grain" to a site (atom dimension); when an atom exceeds capacity (||W_i|| > threshold), it AVALANCHES — its capacity overflows to neighbors via heterosynaptic depression (Section 2B). This is **substrate-native homeostasis as SOC**.

Key prediction: at the critical drive-rate, avalanches form scale-free distributions (power-law). The brain runs at criticality. Substrate currently runs FAR from criticality (drives too aggressively → over-saturation → catastrophic forgetting). **Substrate-native critical-write-rate selection** = tune the write-rate so that avalanche-size distribution becomes scale-free.

### 4B. Spin glass replica symmetry breaking + ultrametric trees

[Spin glass ultrametric trees](https://www.pnas.org/doi/10.1073/pnas.2404973121): "A large number of pure states is organized in an ultrametric tree. The tree describes the probabilistic dependencies among the free energies and the distances of different pure states."

**Substrate translation:** the cleanup-matrix at saturation has a SPIN-GLASS ENERGY LANDSCAPE with many metastable basins (the stored atoms). Replica symmetry breaking says these basins are organized in an ULTRAMETRIC TREE — natural HIERARCHICAL CLUSTERING. **Substrate-native abstraction extraction** = compute the ultrametric distance matrix on the W rows; collapse near-leaves into representative atoms (this is RG-style coarse-graining per Section 1D, with the specific metric being ultrametric distance).

### 4C. Phase transitions (crystallization as selective ordering)

Crystallization from a melt: most molecules stay disordered until a NUCLEATION event seeds an ordered cluster, which then grows. **Selectivity primitive: nucleation is RARE-EVENT-DRIVEN, not magnitude-driven.**

**Substrate translation:** consolidated atoms should form via NUCLEATION — a single high-utility atom seeds a cluster of bound co-activated atoms; the cluster grows by adding atoms with high-cosine to existing cluster members. This is the **schema-fast-track of Section 3B with materials math** — schemas are crystal nuclei.

### 4D. Glass transition + slow relaxation modes

Glassy materials have multiple relaxation timescales: fast (vibrational), medium (cage-rattling), slow (alpha-relaxation = full restructuring). **Selectivity primitive: timescale-stratified retention** — fast modes carry signal, slow modes carry structure.

**Substrate translation:** the substrate's TWO_TIER architecture is exactly this — W_young is fast modes, W_old is slow modes. What's missing is the COUPLING — fast modes should DRIVE slow modes via a specific transfer rule (the brain's NREM-replay does this: fast hippocampal patterns drive slow cortical schema reorganization). Substrate's TWO_TIER promotion is recall-based — should be DRIVEN by repeated reactivation, exactly like glass alpha-relaxation under thermal driving.

---

## Section 5 — 4 RANKED ANCHOR CANDIDATES (cross-discipline composition)

Each anchor is a substrate-native experiment that uses EXISTING substrate primitives + ADDS one specific new primitive. Each anchor has:
- Substrate-physics grounding (which primitives, where it sits in cleanup_memory.py / continual.py)
- Mechanism-class clearly DIFFERENT from the 5 failed cells (no magnitude-only, no closed-form-linear, no global-uniform)
- HARD_PASS / MIDDLE / HARD_FAIL pre-reg suggestion (exp_dev refines)
- Cross-discipline composition tags (2+ of 4 disciplines)
- P_deflated estimate with 0.20 deflation from raw

### ANCHOR 1 (TOP PRIORITY): excitability_allocation_separate_tensor_v1

**Tagline:** Add a separate per-atom EXCITABILITY tensor E[i] updated orthogonally from W; downscale / replace gated on E, not on W.

**Cross-discipline composition:**
- **BIOLOGY (2C):** CREB excitability allocation — per-cell biasing signal upstream of plasticity
- **PURE MATH (1A):** Information bottleneck side-information Y as the right semantic frame for E
- **PURE MATH (1B):** K-SVD usage counter as the substrate-native E update rule
- **BRAIN (3A):** Engram allocation literature — substrate replicates the upstream-selectivity insight

**Substrate primitives used:**
- Existing: cleanup_memory.py (per-atom retrieval logging hookable), W matrix, refuse-gate (for novelty signal), TWO_TIER architecture
- NEW PRIMITIVE: `hdlab/excitability.py` — per-atom E[i] tensor, EWMA update on retrieval hits, decay rule, exposed to continual.py for E-gated downscale

**Mechanism:** at each cleanup retrieval that returns atom_i with cosine > tau_hit, increment `E[i] += alpha * (1 - E[i])`. Every cycle, `E[i] *= (1 - lambda_decay)`. At each global downscale step, `W[i] *= 1.0` if `E[i] > e_thresh` else `W[i] *= gamma`. At each replacement step (every J_replace cycles), atoms with E[i] < e_min get overwritten with fresh random directions.

**Pre-reg suggestion (exp_dev refines):**
- HARD_PASS: at J=2500 cycles continual ingest (matching `gap4_stc_capture_selective_downscale_v1` regime), recall_on_old_atoms (first 100 written) ≥ 0.60 AND recall_on_recent_atoms ≥ 0.85 AND total_active_capacity stays bounded (||W||_F doesn't grow unbounded). [P=0.30 deflated]
- MIDDLE_BAND: recall_old in 0.30-0.60 OR recall_recent in 0.60-0.85 [P=0.45]
- HARD_FAIL: recall_old < 0.30 (matching Cell B failure mode — excitability tensor didn't actually preserve right atoms) OR E[i] correlates too strongly with |W[i]| (excitability is just a magnitude proxy, no new signal). [P=0.25]

**P_deflated:** **0.45** (deflated from 0.65 raw; this is the brain-grounded mechanism most clearly missing from substrate; the engram-allocation literature is robust; main risk is that substrate retrieval-hit signal is too weak to drive E meaningfully).

**Why FIRST:** addresses the SHARED ROOT CAUSE of 3 of the 5 failed cells (STC tagging, global downscale, cold-storage migration) — all needed a per-atom importance signal that doesn't exist. P_deflated highest. Cost cheap (~3-5 CPU-hr on local; fits in one cycle's compute budget).

**Cost estimate:** ~3-5 CPU-hr local, single primary arm + 2 controls (E-gated vs random-gated vs no-gating).

---

### ANCHOR 2: ultrametric_clustering_coarse_grain_atoms_v1

**Tagline:** Detect atom clusters via ultrametric distance in W; collapse clusters to representative atom + residual codes; this is substrate-native RG coarse-graining = the missing compositional-abstraction primitive.

**Cross-discipline composition:**
- **MATERIALS (4B):** Spin glass ultrametric tree organizes metastable basins hierarchically
- **PURE MATH (1D):** Renormalization group / Mehta-Schwab variational RG as deep coarse-graining
- **PURE MATH (1E):** Persistent homology for selecting which clusters are stable enough to collapse
- **BRAIN (3B):** Schema-fast-track — collapsed clusters ARE schemas

**Substrate primitives used:**
- Existing: cleanup_memory.py (W matrix is the basin landscape), binding.py (HRR composition for cluster representative)
- NEW PRIMITIVE: `hdlab/ultrametric_clustering.py` — compute ultrametric distance matrix on W rows, agglomerative cluster, collapse cluster to representative atom + 1-of-K code

**Mechanism:** every J_collapse=2000 cycles, compute pairwise cosine matrix on active atoms; convert to ultrametric (single-linkage tree); identify clusters where within-cluster cosine > 0.85 AND cluster_size >= 5; collapse each cluster into ONE representative atom (cluster centroid) + K residual codes (cluster member identifiers); RE-WRITE the cluster's W rows as `W_rep = mean(cluster); W_residual_k = cluster_member_k - W_rep`. Now `K` original atoms become `1 + log2(K)` effective atoms, freeing capacity for new writes.

**Pre-reg suggestion:**
- HARD_PASS: at J=5000 cycles, capacity_used drops by ≥ 20% after collapse with recall_on_clustered_concepts ≥ 0.80 (concepts are still queryable through cluster representative) AND recall_on_unclustered ≥ 0.85 (collapse didn't damage non-clustered atoms). [P=0.25]
- MIDDLE_BAND: capacity_used drops 5-20% with recall_on_clustered 0.50-0.80. [P=0.40]
- HARD_FAIL: recall_on_clustered < 0.50 (cluster representative doesn't recover member meaning — collapse destroyed information) OR no clusters detected (ultrametric structure absent in substrate W). [P=0.35]

**P_deflated:** **0.40** (deflated from 0.55 raw; mechanism is mathematically clean but the cluster-representative-via-mean is approximation; HRR-bind composition might be wrong primitive for cluster representation).

**Why SECOND:** addresses the COMPOSITIONAL-GENERALIZATION failure (`cortical_schema_extraction` Cell — capability-based schema HURT performance because capability-relations weren't being properly composed). Ultrametric clustering FINDS the latent compositional structure substrate already has but isn't extracting. Cost moderate (~4-6 CPU-hr).

**Cost estimate:** ~4-6 CPU-hr local. Smoke test on N=2048; full on N=4096-8192.

---

### ANCHOR 3: SOC_critical_write_rate_avalanche_v1

**Tagline:** Self-organized criticality framework for substrate writes; tune write-rate to critical point where avalanche-size distribution is scale-free; this is the regime where homeostasis works WITHOUT explicit downscale.

**Cross-discipline composition:**
- **MATERIALS (4A):** Bak-Tang-Wiesenfeld sandpile self-organized criticality + percolation
- **BIOLOGY (2B):** Heterosynaptic competition as the local "avalanche" mechanism
- **PURE MATH (1D):** RG as the natural framework for scale-free dynamics

**Substrate primitives used:**
- Existing: cleanup_memory.py, continual.py
- NEW PRIMITIVE: `hdlab/avalanche_dynamics.py` — detect over-saturation events (per-atom ||W_i|| > c*threshold), distribute excess to top-K nearest neighbors via heterosynaptic depression, track avalanche-size distribution

**Mechanism:** every write triggers a check: if ||W_i|| > capacity_threshold, redistribute the excess `||W_i|| - threshold` via `W[j] -= eta * cos(i,j) * (||W_i|| - threshold)` for top-K nearest atoms; recursively check if the redistribution caused any j to also exceed threshold (cascade = avalanche). Track avalanche-size distribution; the system is "at criticality" when log(P(size=s)) vs log(s) has slope ≈ -3/2 (BTW universality class).

**Pre-reg suggestion:**
- HARD_PASS: at J=5000 cycles, avalanche-size distribution is scale-free (KS-test against power-law p > 0.05) AND recall_on_old ≥ 0.50 (heterosynaptic depression doesn't destroy old patterns) AND ||W||_F stays bounded WITHOUT explicit downscale. [P=0.20]
- MIDDLE_BAND: avalanche distribution has heavy tail but not pure power-law; recall_on_old in 0.30-0.50. [P=0.35]
- HARD_FAIL: heterosynaptic depression destroys old atoms (recall_old < 0.20) OR no avalanche dynamics emerge (substrate too far from critical regime to recover). [P=0.45]

**P_deflated:** **0.30** (deflated from 0.45 raw; high risk because substrate's continuous-valued W is different from BTW's integer-valued sandpile; needs the math to work in continuous limit; novel-synthesis ceiling enforced).

**Why THIRD:** most theoretically elegant but highest implementation risk. Tests a UNIFIED frame (the substrate IS a sandpile and just needs to find criticality) but requires careful tuning of avalanche redistribution rule. Worth dispatching AFTER Anchor 1 lands to know whether selectivity-via-E is sufficient OR whether substrate also needs the SOC frame.

**Cost estimate:** ~4-6 CPU-hr local. Cell can run alongside Anchor 1 (different mechanism, different W-modification path).

---

### ANCHOR 4: MDL_dictionary_turnover_atom_replacement_v1

**Tagline:** Use MDL principle to decide which atoms get REPLACED with new directions or with bound compositions of frequently-co-retrieved atoms; substrate's atoms become a learned dictionary.

**Cross-discipline composition:**
- **PURE MATH (1B):** K-SVD dictionary learning + sparse-coding usage counter
- **PURE MATH (1C):** MDL principle — replace atoms whose bits_saved < bits_cost
- **BIOLOGY (2D):** Glial pruning as long-timescale capacity reset
- **PURE MATH (1E):** Persistent homology — replace atoms with low persistence (short death-birth)

**Substrate primitives used:**
- Existing: cleanup_memory.py, atoms.py, refuse-gate (for OOD detection during replacement)
- NEW PRIMITIVE: `hdlab/mdl_turnover.py` — per-atom usage counter, per-atom bits-saved estimator (MDL approximation via cleanup-hit log-likelihood), atom replacement policy

**Mechanism:** maintain `U[i] = EWMA(cleanup_hit_count)` and `B[i] = EWMA(bits_saved_via_atom_i)`. Every J_turnover=2500 cycles, identify bottom-5% atoms by `B[i] - log(atom_cost)`; for each such atom, replace with EITHER (a) fresh random direction sampled near recent OOD inputs (50%) OR (b) bound composition of top-2 most-frequently-co-retrieved atoms (50%). This converts unused atoms into either novel-direction-probes or schema-anchors.

**Pre-reg suggestion:**
- HARD_PASS: at J=5000 cycles with active turnover, effective_capacity (number of distinct retrievable concepts) ≥ 1.5x baseline (cleanup memory at fixed size N stores 1.5x more concepts due to coarse-graining) AND recall_top1 ≥ 0.85. [P=0.25]
- MIDDLE_BAND: effective_capacity 1.1-1.5x baseline. [P=0.45]
- HARD_FAIL: turnover damages recall (recall_top1 < 0.50) OR no atoms qualify for turnover (B/U metrics too flat). [P=0.30]

**P_deflated:** **0.40** (deflated from 0.55 raw; MDL approximation has theoretical risk in the bits-saved estimator; bound-composition replacement is novel substrate operation).

**Why FOURTH:** addresses the "infinite W growth" problem differently from Anchor 1 — explicit replacement vs gated downscale. Complementary to Anchor 2 (Anchor 2 collapses clusters; Anchor 4 turns over individual atoms). Dispatch after Anchors 1+2 give signal on whether per-atom selectivity OR cluster-level coarse-graining is the right level.

**Cost estimate:** ~4-6 CPU-hr local.

---

### Summary table

| # | Anchor | Disciplines | P_deflated | Cost | Why-rank |
|---|---|---|---|---|---|
| 1 | excitability_allocation_separate_tensor_v1 | BIOLOGY + PURE MATH + BRAIN | **0.45** | ~3-5hr | Addresses shared root cause of 3/5 cells; highest P |
| 2 | ultrametric_clustering_coarse_grain_atoms_v1 | MATERIALS + PURE MATH + BRAIN | 0.40 | ~4-6hr | Addresses compositional-extraction failure; novel cross-discipline |
| 3 | SOC_critical_write_rate_avalanche_v1 | MATERIALS + BIOLOGY + PURE MATH | 0.30 | ~4-6hr | Unified theoretical frame; highest implementation risk |
| 4 | MDL_dictionary_turnover_atom_replacement_v1 | PURE MATH + BIOLOGY | 0.40 | ~4-6hr | Capacity-management complement to Anchor 1 |

---

## Cross-thread synthesis

- **Supersedes Section 5 of `notes/research_gap4_brain_selective_homeostasis_2026-06-26.md`** which proposed M5 STC tagging — that mechanism was REFUTED by `exp_gap4_stc_capture_selective_downscale_v1` HARD_FAIL. The root cause of the M5 failure is now diagnosed: STC's tagging criterion `|dW|>theta_tag` lives in W-space, where there's no signal. This drill's Anchor 1 (excitability tensor) provides the SEPARATE signal-space STC needed.

- **Composes with `gap4_two_tier_generational_W_v1` HARD_PASS:** TWO_TIER provides the destination architecture (W_young/W_old). Anchor 1's E tensor provides the PROMOTION CRITERION that TWO_TIER lacks — currently TWO_TIER uses recall-similarity as promotion gate; with E, promotion becomes "promote atom_i when E[i] > e_promote_thresh." This is the architectural completion of TWO_TIER.

- **Composes with `substrate_continual_NREM_replay_v1` HARD_PASS:** NREM replay strengthens patterns above noise; combined with Anchor 1's E-gated downscale, the full sleep-cycle pipeline becomes: NREM-replay strengthens E-high atoms; REM-style E-gated downscale weakens E-low atoms; net: capacity bounded, recall_old preserved.

- **Addresses `cortical_schema_extraction_compositional_generalization_v1` MIDDLE_BAND:** Anchor 2 (ultrametric clustering) extracts the latent compositional structure that capability-based schema arm tried but failed to leverage. The capability-arm failure was using HRR-bind for transitive relations — ultrametric clustering reveals the right cluster-representative-via-centroid structure that HRR can't synthesize directly.

- **Addresses `gap1_partition_routing_cortex_R_schema_closed_form_v1_META_M7` HARD_FAIL:** the R-schema verdict explicitly recommended "pivot to nonlinear (Modern Hopfield) or replay-extracted (CLS) routing." Anchor 1's E tensor can serve as the routing signal — partition-assignment becomes "send atom to partition argmax(E_partition[i])" where E_partition is a per-partition excitability tracking which atoms each partition successfully retrieves.

- **Cross-domain confirmation (Anchor 3):** the SOC frame appears INDEPENDENTLY in brain criticality literature (BAK-style neural avalanches), in JVM generational GC tuning (allocation-rate vs GC-rate equilibrium = critical-write-rate), and in materials. Substrate as sandpile is structurally consistent with how the brain operates near criticality.

- **No-Hebbian-window META atom (substrate META 2026-06-22):** Anchors 1, 2, 4 are compatible with non-Hebbian-window writes (E update is per-retrieval not per-write coincidence; clustering is offline; MDL turnover is offline). Anchor 3 requires per-write avalanche check which is Hebbian-window-adjacent but still local (no requirement for coincidence detection across atoms).

- **Cleanup-load-bearing META atom:** all 4 anchors interact with cleanup retrieval as the primary signal source — E updates on cleanup hits (Anchor 1), cluster detection uses cleanup-similarity matrix (Anchor 2), avalanche redistribution uses cleanup-nearest-neighbors (Anchor 3), MDL bits-saved estimated from cleanup-hit log-likelihood (Anchor 4). Cleanup integrity is the load-bearing prerequisite for all 4 anchors. The substrate's chain-grade cleanup-integrity 0.78-0.84 at 2500 cycles is sufficient for these mechanisms IF the mechanisms successfully prevent further degradation.

---

## Substrate-product implications

1. **Selectivity-via-separate-tensor is THE missing primitive class.** All 5 failed cortex cells failed because substrate has only W and tries to read importance OFF OF W. The brain, materials science, and information theory all converge on the same answer: importance must be a SEPARATE, ORTHOGONALLY-UPDATED signal. Anchor 1 is the simplest realization of this primitive. Once it exists, substrate has the structural piece needed for indefinite continual operation.

2. **Compositional understanding requires hierarchical coarse-graining.** Anchor 2's ultrametric clustering is substrate-native compositional abstraction — it FINDS the latent compositional structure rather than trying to impose one via HRR role-filler binding. This addresses the USER pivot directly: "compositional understanding first" requires substrate-native ability to EXTRACT composition from co-occurrence structure, not just to ENCODE composition via pre-specified roles.

3. **The substrate-product story (post-pivot):** with Anchor 1 + Anchor 2 landed chain-grade, substrate has (a) bounded continual ingest via E-gated selectivity (Anchor 1), (b) hierarchical compositional abstraction via ultrametric clustering (Anchor 2). These two together = the cortex-content-extraction layer that currently is failing. This unlocks the USER pivot vision: substrate can build compositional understanding from typed semantic ingest, then later derive language prediction from composed meaning.

4. **All 4 anchors are SUBSTRATE-NATIVE (no LLM forward calls).** Maintains substrate-only-decode gate. E updates from substrate cleanup hits; clustering uses substrate cosine-matrix; SOC uses substrate write events; MDL uses substrate retrieval log. Zero external dependencies.

5. **Cost calibration:** all 4 anchors run on local_cpu queue in 3-6 CPU-hr each. Total 12-24 CPU-hr to land all four if sequential; ~6-12 CPU-hr if parallel-dispatched (substrate has the bandwidth). This is well within one autonomous-arc cycle's budget.

6. **Negative outcome value:** if Anchors 1-4 ALL fail, the substrate's cortex-content-extraction problem is more fundamental than "missing selectivity primitive" and points to a deeper architectural limit — likely that HRR/bipolar-VSA is the wrong substrate algebra for compositional abstraction. That would be a major cap_map closure event and worth knowing. Cheap to determine via this drill.

---

## Calibration penalty applied

- Lit-scan calibration penalty: 0.20 deflation applied to all P estimates (raw → deflated).
- Novel-synthesis cap: 0.50 honored (Anchor 1 capped at 0.45; others below).
- HARD-FAIL thresholds explicit and falsifiable for all 4 anchors with quantitative metrics.
- Brain-grounded mechanisms (Anchor 1) get higher prior per USER 2026-06-23 ("brain is existence proof"); raw 0.65 deflated to 0.45.
- Per-arm metrics-vs-verdict-msg per Fix #28: all 5 failed cells' diagnoses come from per-arm metrics.json reads, not from verdict_msg framings.
- Pre-dispatch verify-the-referent per Fix #26: exp_dev should run `predispatch_check.py` against each anchor name before authoring to ensure no recent HARD_FAIL on same mechanism class.

---

## Citations (verified 12 unique URLs)

External (cross-discipline lit-scan):

**Pure math:**
1. Cai, Y. "How Information Bottleneck Helps Representation Learning" — https://yichaocai.com/posts/information-bottleneck.pdf
2. Information Bottleneck method — https://en.wikipedia.org/wiki/Information_bottleneck_method
3. Aharon, Elad, Bruckstein (2006). "K-SVD: An Algorithm for Designing Overcomplete Dictionaries for Sparse Representation" — https://www.ccs.neu.edu/home/eelhami/courses/EE290A/K-SVD_Elad.pdf
4. MDL principle — http://www.modelselection.org/mdl/
5. Mehta & Schwab (2014). "An Exact Mapping between the Variational Renormalization Group and Deep Learning" — https://arxiv.org/abs/1410.3831
6. PHEATPRUNER persistent homology feature selection — https://arxiv.org/pdf/2504.18329

**Biology:**
7. Coupled feedback loops PKMzeta + AMPA — https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1006147
8. STDP + BCM heterosynaptic plasticity — https://www.frontiersin.org/journals/synaptic-neuroscience/articles/10.3389/fnsyn.2011.00004/full
9. Memory allocation via CREB — https://www.nature.com/articles/npp201673
10. Writing the Engram 2025 review — https://onlinelibrary.wiley.com/doi/10.1111/jnc.70328

**Brain:**
11. Engram cells review 2023 — https://pmc.ncbi.nlm.nih.gov/articles/PMC10618102/
12. Dopamine + VTA + novelty + STC — https://www.cell.com/trends/neurosciences/fulltext/S0166-2236(18)30273-X
13. Tse-Morris schema-dependent gene activation — https://www.science.org/doi/10.1126/science.1205274
14. HiCL Hippocampal-Inspired Continual Learning 2025 — https://arxiv.org/pdf/2508.16651

**Materials:**
15. BTW sandpile as continuous phase transition — https://link.aps.org/doi/10.1103/PhysRevE.111.024111
16. Spin glass ultrametric tree PNAS 2024 — https://www.pnas.org/doi/10.1073/pnas.2404973121

Internal (cross-thread):
- `notes/research_gap4_brain_selective_homeostasis_2026-06-26.md` (parent drill; M5 STC since REFUTED)
- `notes/research_STRATEGIC_PIVOT_language_track_closed_compositional_understanding_opens_2026-06-26.md` (USER pivot)
- `memory/feedback_substrate_doesnt_know_anything_stop_testing_against_language_USER_LOCKED_2026-06-26.md`
- `data/exp_substrate_cortical_schema_extraction_compositional_generalization_v1/metrics.json` (Cell 1)
- `data/exp_gap4_stc_capture_selective_downscale_v1/metrics.json` (Cell 2 — REFUTES prior M5)
- `data/exp_substrate_synaptic_homeostasis_global_downscale_v1/metrics.json` (Cell 3 — Cell B baseline)
- `data/exp_gap4_cold_storage_no_combine_v1_smoke/metrics.json` (Cell 4)
- `data/exp_gap1_partition_routing_cortex_R_schema_closed_form_v1_META_M7/metrics.json` (Cell 5)
- `data/exp_substrate_continual_NREM_replay_v1/metrics.json` (composes with Anchor 1)
- `data/exp_gap4_two_tier_generational_W_v1/metrics.json` (composes with Anchor 1 as promotion criterion)

---

## Next-drill candidate field

`computational-neuroscience + engram-allocation` (at level-2 operational drill rather than scope expansion). After Anchor 1 lands verdict, the field-advisor would route next to:
- **stochastic-dynamics adjacents (Glauber/Metropolis on E updates)** for the time-domain stability of the E tensor under continual perturbation — Tier-1 unfilled per advisor.
- **free-probability (Tracy-Widom on cluster-eigenvalue spectrum)** for Anchor 2's ultrametric-clustering theoretical foundation.

If Anchor 1 HARD_PASS but Anchor 2 fails, drill into category-theory / functorial-composition for richer compositional primitives beyond HRR — this is the path to typed semantic ingest per USER pivot.

-- Research (Opus 4.7-1M), 2026-06-26
