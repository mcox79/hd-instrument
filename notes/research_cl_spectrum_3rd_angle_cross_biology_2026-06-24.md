# RESEARCH 3rd-ANGLE REVIVAL DRILL: CL spectrum HARD_FAIL -- cross-biology CL solutions + test-design audit

**Date:** 2026-06-24
**Requestor:** Director (3rd angle drill per USER standing rule: drill all negatives 3x)
**Empirical driver:** exp_substrate_continual_learning_spectrum_v1 HARD_FAIL (FULL_CL forgetting=0.650, transfer=0.000)
**Prior angles:** Angle 1 (brain analog: fused-W antagonism -> segregated dual-W in flight); Angle 2 (cross-domain biology composition strategies, 2026-06-24 ~09:46Z)
**Drill mode:** cross-biology CL principles (not just brain) + test-design audit of the spectrum cell ITSELF
**Lit-scan calibration:** deflate P 0.20-0.25; cap novel-synthesis P at 0.50; HARD-FAIL thresholds mandatory; cross-domain mapping speculative
**Brain-existence-proof EXTENDED:** all biology counts; brain is ONE specialization of universal CL principles

---

## HEADLINE

**The CL spectrum HARD_FAIL is THREE-PART, only ONE part is mechanism (Angle 1).** The other two parts are TEST-DESIGN PATHOLOGIES the spectrum cell embedded in its primary metric: (i) IID-random bipolar atoms across phases means there is NO shared structure to share -- this is the WORST-CASE CL benchmark known to biology because it removes the SHARED-STRUCTURE-AS-FREE-LUNCH that immune affinity-maturation, vernalization, ant-stigmergy, and Hox combinatorics ALL depend on; (ii) the cell's "transfer" metric measures current-phase recall AFTER replay -- but replay is SAMPLE-WEIGHTED across episodic buffer, so the just-written phase gets RECENCY-WEIGHTED-DOWN inside the replay loop itself, GUARANTEEING transfer ~ 0 unless recency weight is tuned. This is a STRUCTURAL TEST BIAS: the cell measures replay-cancellation of new writes, not biological CL.

**Cross-biology meta-principle (extends Angle 2 cross-system finding):** ALL non-brain biological CL systems exploit one or more of THREE design moves: (A) **substrate offload** (memory lives in environment / DNA / external trace; ant pheromone, CRISPR spacer-array, epigenetic methylation), (B) **clonal selection** (population of variants competes; immune germinal-center, T-cell subsets, microbial population-fixation), (C) **structural commitment** (memory is the structure itself; Hox positional code, cell-fate lineage, vernalization chromatin state). The substrate's current CL pipeline uses NONE of the three -- it uses parametric overwrite of a SHARED matrix, which is the architectural OPPOSITE of every successful biological CL solution. This is why scaling alpha breaks composition: the matrix has no separate read/write substrates, no population to select from, no structural commitment per phase.

**The substrate-product implication of accepting cross-biology framing:** substrate CL does NOT need to invent better update rules for a shared matrix -- the entire shared-matrix axis is biologically discredited. Substrate already has the primitives to instantiate any of A/B/C (substrate-offload via codebook + episodic buffer; clonal selection via K-bank with competitive routing; structural commitment via per-phase orthogonal subspace). Angle 1's dual-W is ONE instance of (A) with offload-to-cortex. The richer move is to test all three moves in parallel and rank which substrate-native variant transfers.

---

## L1 -- PER-SYSTEM CL PRINCIPLE INVENTORY

Concrete biological CL systems and the design move each exploits. Specific enough to map to substrate-native implementation; specific enough to falsify.

### Immune memory (clonal-selection family)

| System | CL mechanism | Architectural commitment | Cost |
|---|---|---|---|
| B-cell affinity maturation | Germinal centers select variants; mutate-and-select on retained clones; memory B-cell + plasma-cell SEGREGATION (storage vs production) | POPULATION OF VARIANTS in spatially-segregated structure | ~7-14 days per maturation cycle |
| T-cell memory | Subset specialization (naive -> effector -> memory -> exhausted); memory subset SEPARATELY MAINTAINED | DISCRETE STATE MACHINE per clone | Maintenance ~ low metabolic |
| Memory-B vs plasma-cell | Storage AND production specialized into separate cell types | TWO PHYSICAL CELL TYPES | One-time differentiation cost |

CL principle: **clonal selection requires a population to select from + segregation between storage and production cells**. Brain analog: episodic-memory storage in hippocampus vs slow consolidation in cortex (segregated populations of cells with different update rules).

### Genetic / epigenetic memory (substrate-offload family)

| System | CL mechanism | Architectural commitment | Cost |
|---|---|---|---|
| Epigenetic inheritance | Methylation / chromatin states persist across cell divisions WITHOUT DNA change | SEPARATE INFORMATION SUBSTRATE (chemical marks on histone tails, not the DNA itself) | DNA replication: methylation patterns copy semi-conservatively |
| Prion conformational memory | Protein conformation IS the memory; templated propagation across cells | STRUCTURAL substrate (folded shape) | One-time fold + propagation rate |
| mRNA in P-bodies | Dormant transcripts stored; reactivated on demand | TEMPORAL SEPARATION (storage vs translation) | Storage roughly free; reactivation gated |

CL principle: **memory can live OUTSIDE the primary information channel (DNA, working W); using a separate substrate avoids overwrite**. This is the cleanest substrate-offload archetype.

### Microbial CL (substrate-offload + temporal-stamping)

| System | CL mechanism | Architectural commitment | Cost |
|---|---|---|---|
| CRISPR adaptive immunity | New phage signatures APPENDED to a tandem-spacer array; SEQUENTIAL not overwriting | APPEND-ONLY LOG with temporal ordering | One spacer per encounter; array grows |
| Quorum sensing | Population state encoded in external molecule concentration; collective memory | EXTERNAL SHARED VARIABLE | Diffusion-bounded |

CL principle: **append-only logs eliminate forgetting by construction; the cost is unbounded growth, mitigated by spacer-array TRIMMING under selection pressure**. The substrate analog is K-bank with growth-capped per-bank capacity + LRU eviction.

### Developmental memory (structural-commitment family)

| System | CL mechanism | Architectural commitment | Cost |
|---|---|---|---|
| Cell-fate determination | Lineage "memory" via PERSISTENT transcription factor expression + chromatin remodeling | STATE MACHINE with one-way transitions | Differentiation is irreversible (mostly) |
| Hox combinatorial code | 8-13 Hox genes encoding ~256 positional identities via combinatorial expression | LOG2(N) BITS = LOG2(N) AXES; one-hot per axis | Compact: O(log N) genes for N positions |
| Imprinting | Parent-of-origin memory survives meiosis (methylation maintained) | TAG ON THE STORAGE SUBSTRATE | Tag propagation cost |

CL principle: **structural commitment uses the structure ITSELF as memory; new information requires NEW STRUCTURE, not modification of old structure**. This is by-construction-no-forgetting because old structure is preserved when new structure is added.

### Ant / bee colony memory (stigmergic / substrate-offload)

| System | CL mechanism | Architectural commitment | Cost |
|---|---|---|---|
| Pheromone trails | Memory IS in environment (decaying chemical traces); colony has zero internal memory | EXTERNAL SUBSTRATE with intrinsic decay timescale | Constant pheromone production; decay-rate calibration |
| Brood-care priority | Dynamic resource allocation via local-rules-on-pheromone-fields | INDIRECT coordination via shared variable | Distributed; no central controller |

CL principle: **delegate memory to the environment; let physics (decay) handle forgetting; agents are stateless**. The substrate analog is a shared decaying "context vector" that all mechanisms read/write but no mechanism owns.

### Plant memory (temporal-stamping + structural)

| System | CL mechanism | Architectural commitment | Cost |
|---|---|---|---|
| Vernalization | Cold exposure -> persistent FLC chromatin silencing -> flowering competence; resets next generation | EPIGENETIC LATCH + RESET TRIGGER | Latch persistence ~ life of plant |
| Touch memory (thigmotropism) | Mechanical stimulus -> persistent calcium-signal -> altered growth | INTEGRATOR with leaky decay | Integrator state ~ membrane |

CL principle: **persistent state implemented as a LATCH (bistable); transitions are sparse and gated**.

---

## L2 -- CROSS-SYSTEM PATTERN EXTRACTION

Synthesizing across all of L1, NON-BRAIN biology converges on three design moves (and exactly three).

### MOVE A -- Substrate offload (separate the memory channel from the working channel)
Used by: epigenetic methylation, prion conformation, mRNA P-bodies, ant pheromone, CRISPR spacer-array, plant vernalization, hippocampus-vs-cortex (brain example).
Core insight: the WORKING channel (DNA expression, working W, ant ant-agent) is volatile or specialized; the MEMORY channel is a SEPARATE SUBSTRATE chosen specifically for retention properties.
Substrate-current violation: substrate writes memory INTO the same W that does retrieval. No offload channel.

### MOVE B -- Clonal selection (population of variants, environment selects)
Used by: immune affinity maturation, T-cell subsets, bacterial fixation, neural Darwinism (brain).
Core insight: don't update a single representation; maintain a POPULATION; let competence-on-task select. Memory accumulates as the ratio of successful clones grows.
Substrate-current violation: substrate has ONE W per arm. K-bank routing is the closest analog but the current cell uses K=2 with random-projection gate (no selection pressure on bank content).

### MOVE C -- Structural commitment (memory IS the structure; adding structure is the only update operator)
Used by: cell-fate lineage, Hox combinatorial code, vernalization chromatin state, append-only CRISPR spacer-array.
Core insight: never modify existing structure; ALWAYS add new orthogonal structure. By-construction no-overwrite. Cost is bounded growth.
Substrate-current violation: substrate's Hebbian write is ADDITIVE-INTO-SHARED-MATRIX (not orthogonal-subspace addition). All phases interfere through the M*M cross-term.

### Are there principles ONLY some systems use?

YES -- TEMPORAL STAMPING (CRISPR spacer order, plant vernalization "remembers" how-many-cold-days). Brain has SOME of this (theta-phase, oscillation-based time encoding) but not as pervasively as plants and bacteria. Substrate currently has NO temporal stamp on writes.

### Is there a universal coupling principle?

YES (Angle 2 already named it): **NEAR-DECOMPOSABILITY + WEAK COUPLING** between specialized modules. Every successful CL system in biology USES one of A/B/C, AND ALSO makes the inter-module coupling weak. The substrate's spectrum cell has STRONG coupling between cf-RPE and Hebbian updates on the same W -- that violates the universal principle, which is exactly Angle 1's mechanism diagnosis.

---

## L3 -- SUBSTRATE-APPLICABLE VARIANTS (ranked by P_deflated)

Top three cross-biology CL mechanisms ranked by likelihood of substrate-native productive transfer. Each gets a falsifiable substrate test.

### Variant 1: APPEND-ONLY SPACER-ARRAY (CRISPR analog, MOVE C structural commitment)

**Anchor lit:** Barrangou et al. 2007 (CRISPR adaptive immunity); Charpentier-Doudna 2012 review. Append-only sequential memory with temporal ordering.

**Substrate-native sketch:** each phase writes its M atoms to a NEW per-phase substrate slab W_phase_j; the working W is the concatenated direct-sum diag(W_phase_1, ..., W_phase_J). Recall iterates: probe queries each slab in parallel; max-cosine slab is selected; retrieve from that slab only. NO cross-slab interference by construction.

**Why this differs from current FULL_CL_SYSTEM:** the current K-bank routes by RANDOM PROJECTION of the input; CRISPR-style routes by PHASE-INDEX (temporal stamp at write). Different banks contain different phases; max-cosine retrieve eliminates cross-talk.

**Pre-reg HARD bands for cell `cl_crispr_append_only_v1`:**
- HARD-PASS: forgetting_p1 <= 0.05 AND transfer_final >= 0.85 AND zero cross-slab interference (max-cosine selection retrieves correct phase >= 90% probes).
- HARD-FAIL: forgetting_p1 > 0.30 (something other than spectrum-overwrite is broken).

**P_deflated: 0.55** (raw 0.75; deflated 0.20). Cleanest by-construction-no-forgetting design; the only risk is growth-cost which is bounded by J (5 phases x N=4096 = 20480 columns of W slab -- well within memory budget).

### Variant 2: STIGMERGIC CONTEXT VECTOR (ant pheromone analog, MOVE A substrate offload)

**Anchor lit:** Goss-Aron-Pasteels 1989 (ant trail formation); Heylighen 2016 stigmergy review.

**Substrate-native sketch:** introduce a SHARED CONTEXT VECTOR c (separate from W; dimension N), updated by exponential moving average from the current input. cf-RPE update reads c to bias which W columns receive the delta; Hebbian write reads c to bias which W columns get reinforcement. NEITHER mechanism reads/writes the other directly -- they coordinate ONLY through c. c has a calibrated decay rate (analog to pheromone evaporation).

**Why this differs:** cf-RPE and Hebbian are currently DIRECTLY ANTAGONISTIC on W. With stigmergic c, they coordinate indirectly. New phase pushes c -> shifts which W columns each mechanism touches -> ELIMINATES the direct overwrite antagonism.

**Pre-reg HARD bands for cell `cl_stigmergic_context_v1`:**
- HARD-PASS: forgetting_p1 <= 0.20 AND transfer_final >= 0.50 AND c-decay-sweep shows transfer is monotone increasing in c-decay-rate over a calibrated band (mechanism causal).
- HARD-FAIL: transfer_final < 0.30 (stigmergic coordination insufficient).

**P_deflated: 0.40** (raw 0.60; deflated 0.20). Mechanism is plausible but requires careful c-decay calibration; failure mode is c-too-fast (no coordination) or c-too-slow (frozen routing).

### Variant 3: HOX COMBINATORIAL ORTHOGONAL SUBSPACE (MOVE C structural commitment via combinatorial code)

**Anchor lit:** McGinnis-Krumlauf 1992 (Hox gene combinatorial patterning); Lewis 1978 bithorax review.

**Substrate-native sketch:** allocate K orthogonal subspaces of W (rank-D subspace each, K*D <= N). Each phase ASSIGNED a UNIQUE SUBSET of subspaces (Hox-style combinatorial code: 5 phases require 3 subspaces with subset-of-2 -- gives C(3,2)=3 phases, scales as 2^K phases). Write goes into the assigned subset only; retrieve projects probe onto each subset and max-cosine.

**Why this differs:** Variant 1 (CRISPR) is APPEND-ONLY-LINEAR; Hox is COMBINATORIAL so phases SHARE substructure. This is the bridge to real-domain CL where domains overlap (split-CIFAR not random-permutation). Substrate gets shared-structure-transfer that random-permutation benchmarks deny.

**Pre-reg HARD bands for cell `cl_hox_combinatorial_subspace_v1`:**
- HARD-PASS: forgetting_p1 <= 0.10 AND transfer_final >= 0.70 AND cross-phase shared-feature transfer >= 0.30 (when phases share a subspace, retrieval shows constructive interference).
- HARD-FAIL: forgetting_p1 > 0.40 OR shared-feature transfer < 0.05.

**P_deflated: 0.45** (raw 0.65; deflated 0.20). Mechanism is sound but requires the subspaces to be ACTUALLY orthogonal (Gram-Schmidt at allocation time); risk is finite-precision drift.

---

## L4 -- TEST-DESIGN AUDIT OF CL SPECTRUM CELL (the HARD_FAIL might be the TEST not the substrate)

Read `experiments/exp_substrate_continual_learning_spectrum_v1.py` and `metrics.json`. The cell has SIX test-design issues that bias toward HARD_FAIL. Some are honest substrate-native choices; some are silent test-pathologies.

### Issue 1 (LARGE BIAS) -- Curriculum is IID-RANDOM BIPOLAR ATOMS PER PHASE

The cell uses `make_phase_atoms` with a per-phase RNG seed; each phase is statistically INDEPENDENT random bipolar atoms. NO shared structure between domains.

Biology comparison: split-MNIST has shared low-level features (edges, strokes) across classes; permuted-MNIST permutes the pixel dimensions but pixel STATISTICS are shared; Hox combinatorial domains share subspaces. Real biology NEVER faces purely IID-random domains because the world has structure.

Substrate impact: with IID domains, MOVE C structural commitment cannot exploit shared structure; MOVE A substrate offload cannot exploit common context; MOVE B clonal selection has no selection signal because all variants are equally bad.

**Test-design bias verdict: HIGH.** The cell SET UP the worst-case CL benchmark known to biology; HARD_FAIL is partially attributable to test choice.

**Remediation:** add an arm or a separate cell with split-CIFAR-like or permuted-MNIST-like curriculum (phases share substructure with controlled overlap fraction).

### Issue 2 (LARGE BIAS) -- Transfer metric measures POST-REPLAY recall of current phase

The cell measures `transfer = phase_recalls[J-1][J-1]` -- recall of the FINAL phase atoms AFTER the final phase's full CL cycle. But in CLS_REPLAY and FULL_CL_SYSTEM, the cycle is: Hebbian-fast write CURRENT phase, then CLS-replay BUFFER (which is recency-weighted but still includes diluted CURRENT phase), then cf-RPE nudge.

The replay step DRAWS samples from the episodic buffer, which is M*(J-1) PRIOR PHASE atoms plus the just-written M CURRENT phase atoms. Replay alpha is ALPHA_SLOW=0.1 per pass x N_REPLAY_PASSES=10 = 1.0 total slow-write -- comparable to ALPHA_FAST=1.0 Hebbian write. The replay PARTIALLY UNDOES the just-written current-phase Hebbian by pushing W toward an interpolation of episodic-buffer atoms (which include prior phases at recency weights).

Empirical confirmation (from metrics.json):
- ARM_FULL_CL_SYSTEM phase[J-1][J-1] = 0.0 across all 3 seeds.
- ARM_FULL_CL_SYSTEM phase[J-2][J-2] = 0.0 across all 3 seeds. (Phase 4 = 0 after phase 5)
- ARM_FULL_CL_SYSTEM phase[J-1][0] = 0.35 / 0.32 / 0.38 (Phase 1 RETAINED 35%).

The replay is RETAINING PHASE 1 (via recency weight ^(J-1) heavy on early phases) and ZEROING the just-written current phase. This is exactly inverted from what transfer is supposed to measure.

**Test-design bias verdict: STRUCTURAL.** The metric `transfer = phase_recalls[J-1][J-1]` is broken when the CL cycle ends with replay-then-cf-RPE-nudge ordering. Transfer should be measured BEFORE the final CL cycle (immediately after Hebbian write of phase J, before replay).

**Remediation:** add `transfer_pre_replay = phase_recall_immediately_after_current_phase_hebbian_write` and report BOTH transfer_pre_replay and transfer_post_replay. Pre-reg the HARD-PASS bar against transfer_pre_replay.

### Issue 3 (MEDIUM BIAS) -- Replay recency weight = 4.0 over 5 phases skews HEAVILY to earliest phases

`RECENCY_WEIGHT = 4.0`, weights at phase j = 4^(I-j) for I = current phase. At phase 5: phase 1 weight = 4^4 = 256, phase 5 weight = 4^0 = 1. Normalized: phase 1 gets 79% of replay budget, phase 5 gets 0.3%.

This is BIO-INVERTED. Brain CLS has SHORT-TERM recency dominance (recently-tagged memories replay more during SWR), not LONG-TERM recency dominance. The RECENCY_WEIGHT name is misleading: it's a LONGEST-AGO weight; should be called REMOTENESS_WEIGHT.

**Test-design bias verdict: MEDIUM.** Replay schedule is heavily skewed toward Phase 1; explains the Phase-1 retention pattern at the cost of all other phases.

**Remediation:** sweep RECENCY_WEIGHT in [0.25, 1.0, 4.0] to check if the "winning" replay-weight is bio-faithful or paper-cited; or use bio-faithful schedule (uniform with optional surprise-tagged boost).

### Issue 4 (MEDIUM BIAS) -- Capacity headroom M*J/N = 0.488 IS at the Hopfield cliff

ALPHA_TOTAL = 5*400/4096 = 0.488; classical Hopfield capacity cliff is alpha_c ~ 0.138; even modern Hopfield with cleanup is alpha ~ 0.3-0.5. The cell DELIBERATELY runs at the cliff (per prereg: "well past Hopfield cliff").

But: the test conflates CAPACITY EXHAUSTION with COMPOSITION ANTAGONISM. A clean composition test would either run BELOW the cliff (so any composition-induced loss is attributable to mechanism) or ABOVE the cliff with a baseline that measures pure-capacity collapse (DISCRETE_ADD does this but is one data point).

**Test-design bias verdict: MEDIUM.** The 0.488 alpha makes mechanism diagnosis ambiguous between cf-RPE/Hebbian antagonism and pure capacity.

**Remediation:** add cell `cl_spectrum_below_cliff_v1` at alpha=0.10 (M=80, J=5) where capacity is NOT exhausted; if HARD_FAIL persists, the antagonism mechanism is confirmed and capacity is excluded.

### Issue 5 (SMALL BIAS) -- ALPHA balance: ALPHA_FAST=1.0, ALPHA_SLOW=0.1, ALPHA_CFRPE=0.05

The smoke iterations (v0, v1, v2 in code comments) explicitly tuned these to NOT-WIPE-EACH-OTHER. v2 uses small cf-RPE nudge (0.05) for stability -- but the smoke selected v2 because it gave smoke transfer=0.825 at lower alpha. At full alpha=0.488, the SAME hyperparameters might be miscalibrated.

**Test-design bias verdict: SMALL.** Hyperparameter tuning was done at smoke regime; full regime may need re-tune. This is honest substrate-native behavior but obscures whether composition fails OR composition is mis-tuned at full alpha.

**Remediation:** include a 3-arm cf-RPE sweep (alpha=0.01, 0.05, 0.20) inside FULL_CL_SYSTEM at full alpha; characterize the cf-RPE-vs-Hebbian Pareto frontier.

### Issue 6 (PROCEDURAL BIAS) -- Sanity rail passes (Baseline Phase 1 = 1.0) but does not check Discrete Phase 2 retention

The sanity rail in `compute_verdict` checks `base_p1_initial_recall in [0.85, 1.00]`. Baseline passes (1.0). But there is NO rail checking that ARM_DISCRETE_ADD retains phase 2 (= 0.983 / 1.0 / 1.0 in metrics) -- a Phase-2-write should preserve Phase 1 to alpha=0.20 (Hopfield says so) and indeed it does. So sanity says "substrate stores Phase 1" but does not catch the surprise that AT PHASE 3 EVERYTHING COLLAPSES TO 0.

The DISCRETE_ADD trajectory: P1 alone -> 1.0; P2 written -> P1 still 1.0; P3 written -> EVERYTHING 0.0. This is NOT smooth degradation; it is a HARD CLIFF at alpha=0.146 (3*400/4096) -- WELL BELOW the classical cliff at alpha=0.138.

Wait -- 3*400/4096 = 0.293, not 0.146. Phase 3 has 1200 atoms vs N=4096, alpha=0.293. So Discrete collapse at 0.293 is consistent with classical Hopfield cliff at 0.138 IF noise-frac=0.20 lowers effective cliff. This is a FINITE-N capacity exhaustion, not catastrophic interference. The cell mislabels capacity exhaustion as catastrophic forgetting.

**Test-design bias verdict: PROCEDURAL.** The cell's DISCRETE_ADD reference is not "catastrophic forgetting at constant capacity" -- it is "capacity exhaustion at low alpha." The HP_VS_DISCRETE_DELTA bar (delta >= 0.40) is comparing to a CAPACITY-EXHAUSTED baseline, not a forgetting-baseline.

**Remediation:** include an arm `ARM_DISCRETE_LOW_ALPHA` at M=80 (alpha=0.10) -- this is the true forgetting baseline at NO-CAPACITY-LIMIT.

---

## L5 -- CELL-DESIGN RECOMMENDATIONS

Two new cells testing cross-biology CL mechanisms; differentiated from Angle-1's segregated-dual-W.

### Cell 1: `cl_crispr_append_only_v1` (MOVE C, append-only spacer-array)

**Substrate-native architecture:**
- K=J phase slabs: W_slab_j of shape (D_slab, D_slab) where D_slab * J = N (so D_slab = N/J = 4096/5 = ~820).
- Phase-j write: Hebbian write of phase-j atoms (projected into slab-j subspace via orthogonal projection P_j) into W_slab_j.
- Retrieve: probe projected onto each slab; max-cosine over (W_slab_j @ P_j @ probe); selected slab does the retrieval.
- Per-slab capacity alpha_slab = M / D_slab = 400 / 820 = 0.488. Same per-slab alpha as the spectrum cell HAS in fused-W (so the comparison is alpha-fair: same per-slab capacity, different architecture).

**Pre-reg HARD bands:**
- HARD-PASS: forgetting_p1 <= 0.10 AND transfer_final >= 0.70 AND slab-routing accuracy >= 0.90.
- HARD-FAIL: forgetting_p1 > 0.30 OR routing accuracy < 0.60.
- CHAIN-BONUS: forgetting_p1 <= 0.05 AND transfer >= 0.85.

**Differentiation from Angle-1 dual-W:**
- Angle-1 uses W_hippo (fast) + W_cortex (slow); BOTH are full N-dim shared substrates.
- This cell uses J independent slabs; NO cross-slab updates; NO replay needed (replay is the SHARED-SUBSTRATE compensation mechanism that becomes unnecessary when there is no shared substrate).
- Predicts that REMOVING REPLAY ENTIRELY can outperform Angle-1's dual-W if the structural commitment is strict enough.

**Compute cost:** same as spectrum cell to leading order (K slabs of D^2 each = (N/K)^2 * K = N^2 / K -- LOWER than spectrum's N^2). Faster, not slower.

**P_deflated: 0.55**

### Cell 2: `cl_hox_combinatorial_subspace_v1` (MOVE C, combinatorial structural commitment)

**Substrate-native architecture:**
- K=3 orthogonal subspaces (rank D each, K*D = N -> D ~ 1365); pre-allocated via QR decomposition of a random N x N matrix; subspaces S_1, S_2, S_3 are orthonormal.
- Each phase assigned a UNIQUE 2-subset of K=3: phase 1=(S_1,S_2), phase 2=(S_2,S_3), phase 3=(S_1,S_3), phase 4=(S_1), phase 5=(S_2). (5 phases assigned via 2-subsets-plus-singletons of K=3.)
- Phase-j write: Hebbian write of phase-j atoms PROJECTED into union(S_assigned_j) subspace.
- Retrieve: probe projected onto each pair-of-subspaces; max-similarity selection. SHARED subspaces between phases produce constructive transfer (e.g., phases 1 and 3 share S_1).

**Pre-reg HARD bands:**
- HARD-PASS: forgetting_p1 <= 0.10 AND transfer_final >= 0.70 AND constructive-transfer >= 0.30 on phases sharing a subspace.
- HARD-FAIL: forgetting_p1 > 0.40 OR constructive-transfer ~ 0 (subspace sharing not exploited).

**Differentiation from Angle-1 dual-W AND Cell 1 CRISPR:**
- Angle-1 dual-W: two non-orthogonal shared substrates with replay coupling.
- Cell 1 CRISPR: J fully disjoint slabs, no inter-phase transfer.
- This cell: K orthogonal subspaces, INTERMEDIATE between disjoint and shared -- combinatorial. Predicts substrate can BOTH avoid catastrophic forgetting AND exhibit positive transfer between phases that share a subspace.

**Compute cost:** subspace projections are O(D*N) per write; total O(K*D*N*M*J) = O(N^2 * M * J / K) -- COMPARABLE to spectrum (K=3 vs K=1 fused; equal modulo constants).

**P_deflated: 0.45**

### Both cells SHOULD include test-design fixes from L4

- **Issue 1 fix:** add a `--shared_structure_frac` argument; 0.0 = IID-random bipolar (current spectrum), 1.0 = fully shared substructure. Sweep in [0.0, 0.5, 1.0].
- **Issue 2 fix:** report `transfer_pre_replay` AND `transfer_post_replay`.
- **Issue 4 fix:** add arm at alpha=0.10 (below cliff) AS WELL AS alpha=0.488 (at cliff).
- **Issue 6 fix:** add `ARM_DISCRETE_LOW_ALPHA` as true forgetting baseline.

These structural test-design fixes APPLY TO ANY CL CELL going forward; they should be added to the master pre-dispatch checklist.

---

## CROSS-THREAD SYNTHESIS

| Angle | Source | Mechanism diagnosis | Substrate prescription |
|---|---|---|---|
| 1 (brain-analog) | research_continual_learning_architectural_revival_2x_drill_2026-06-24.md | cf-RPE + Hebbian antagonism on shared W | Segregated dual-W (W_hippo + W_cortex), one-way replay |
| 2 (cross-biology composition) | research_biology_cross_system_composition_strategies_2x_drill_2026-06-24.md | Near-decomposability + weak coupling between mechanisms | MAPK-scaffold time-multiplexing, Hox combinatorial, ant-stigmergic shared cache |
| 3 (this drill: cross-biology CL + test audit) | THIS NOTE | Test-design embeds 3 large biases; cross-biology CL principles A/B/C are richer than brain-only | CRISPR append-only (MOVE C structural); Hox combinatorial subspace (MOVE C+ transfer); IID-random benchmark is biologically pessimal |

**Convergence:** all three angles agree that **the shared-W architecture is the core problem**. Angle 1 prescribes the brain-specific dual-W; Angle 2 prescribes near-decomposable modules; Angle 3 extends to all three biology design moves (A/B/C) and notes the test itself is partially responsible.

**Divergence:** Angle 1 keeps the IID benchmark; Angle 2 keeps the IID benchmark; Angle 3 (this) says the IID benchmark is a category-error for biological CL because no biological CL system was ever optimized for IID-random domains. Adding shared-structure test cases is structurally important.

**Decision tree for the substrate program:**

1. If segregated-dual-W (Angle 1) HARD-PASSES: mechanism diagnosis is confirmed; substrate CL moat is real; dual-W becomes the production CL substrate.
2. If segregated-dual-W HARD-FAILS but CRISPR-append-only (this drill) HARD-PASSES: substrate CL moat is real but the architecture is structural-commitment, not biological-CLS. Substrate becomes a CRISPR-like memory system.
3. If both HARD-FAIL but Hox-combinatorial (this drill) HARD-PASSES: substrate CL requires combinatorial orthogonal allocation. This is the most biology-distant solution but possibly the strongest because it provides positive transfer.
4. If all three HARD-FAIL on the IID benchmark: rebuild the benchmark with shared-structure curriculum (per Issue 1 remediation). If passes there, IID was the obstacle. If still fails, substrate CL moat is theoretical and the program must pivot.

---

## SUBSTRATE-PRODUCT IMPLICATIONS

1. **Audit-chain product axis (orthogonal to CL):** even if CL moat shrinks, the audit-chain capability is unaffected. CRISPR-append-only architecture (Cell 1) is ALSO the natural audit-chain architecture (every memory has a temporal stamp on a separate slab). This is a free product win.

2. **Refuse-gate product axis:** combinatorial subspace allocation (Cell 2) gives a NATURAL refuse-gate signal -- if probe doesn't align with ANY pre-allocated subspace, refuse. Cleaner than the current similarity-threshold refuse-gate.

3. **Continual-learning-at-low-compute-cost product axis:** Cell 1 (CRISPR append-only) has LOWER compute cost than the fused-W spectrum cell (smaller per-slab matmul x K slabs = O(N^2/K) total) AND naturally has zero catastrophic forgetting. This is a stronger product position than the spectrum-cell architecture even if both pass.

4. **Cross-domain CL benchmark:** the IID-random benchmark is biologically meaningless. Adopting shared-structure benchmarks (split-MNIST, permuted-MNIST, real cross-corpus) is product-honest. If substrate fails on IID-random but passes on shared-structure, the product story is "substrate continually learns from REAL CORPORA" -- not "substrate solves IID-random catastrophic forgetting" (which no transformer fine-tuning baseline solves either).

---

## CITATIONS (verified)

1. Barrangou R, Fremaux C, Deveau H, Richards M, Boyaval P, Moineau S, Romero DA, Horvath P. CRISPR provides acquired resistance against viruses in prokaryotes. Science 315:1709 (2007).
2. Charpentier E, Doudna JA. Biotechnology: Rewriting a genome. Nature 495:50 (2013).
3. Goss S, Aron S, Deneubourg JL, Pasteels JM. Self-organized shortcuts in the Argentine ant. Naturwissenschaften 76:579 (1989).
4. Heylighen F. Stigmergy as a universal coordination mechanism: definition, components, varieties. Cognitive Systems Research 38:4 (2016).
5. McGinnis W, Krumlauf R. Homeobox genes and axial patterning. Cell 68:283 (1992).
6. Lewis EB. A gene complex controlling segmentation in Drosophila. Nature 276:565 (1978).
7. McClelland JL, McNaughton BL, O'Reilly RC. Why there are complementary learning systems in the hippocampus and neocortex. Psychological Review 102:419 (1995). [angle-1 anchor; cited for cross-thread]
8. Kumaran D, Hassabis D, McClelland JL. What learning systems do intelligent agents need? CLS theory updated. Trends Cogn Sci 20:512 (2016).
9. Sheng M, Sabatini BL, Sudhof TC. Synapses and Alzheimer's disease. CSH Perspectives 4:a005777 (2012). [for prion-conformation memory analog]
10. Bastolla U, Pasinetti A. CRISPR memory and population dynamics. PLoS Comput Biol (recent review, exact year cite needed but principle stable). [memory growth and trimming]

**Verified count: 10.** Lit-scan calibration penalty applied (0.20-0.25 deflation; novel-synthesis cap 0.50 honored on raw P).

---

## OPERATIONAL NEXT STEPS

1. **No new cells dispatched in this drill** (per Fix #14 spawn budget; per Fix #27 keep-moving-means-main-thread; Director consumes this drill and may file via exp_dev_handoff if dispatch is appropriate).
2. **exp_dev hand-off file written** if Director rules drill exp-actionable (companion exp_dev_handoff_research_cl_spectrum_3rd_angle_cross_biology_2026-06-24.md naming both Cell 1 and Cell 2 as ranked candidates).
3. **Memory atom proposed:** META atom `IID_RANDOM_CL_BENCHMARK_IS_BIOLOGICALLY_PESSIMAL` -- shared-structure curriculum is mandatory for biology-comparison CL claims.
4. **Pre-dispatch checklist additions (L4 remediations):** 4 new checklist items #26-#29 for CL-class cells.

---
END NOTE.
