# Brain mechanisms x HD computing — broad-exploration drill (12 mechanisms)

**Date:** 2026-06-22
**Author:** Research
**Drill type:** USER-directed BROAD-EXPLORATION (NOT iterate on current variants; scan brain-mechanism x HD combinations we haven't drilled)
**Lit-scan calibration penalty applied** (deflate raw P estimates 0.15-0.25; cap novel-synthesis P at 0.50)
**Generic-terms-only queries** per query-privacy discipline

## CONTEXT — already-drilled, NOT re-covered
- Within-concept floor (brain-drill #1: k-WTA-VQ + decode-side)
- CLS continual learning (brain-drill #2: cascade-synapse + STC + SWR; c2 cell)
- Multi-hop reasoning (brain-drill #3: SR/TEM/theta-gamma; r2 chain)
- Cerebellar generation (brain-drill #4: g1b chain-grade)
- Hippocampal SWR + sleep replay (brain-drill #5: composed into c2)
- Cortical microcircuit / W architecture (brain-drill #6: m1 modular cell)
- Distributional semantics (Random Indexing + BEAGLE + ATL hub-spoke; n11 in flight)

## TOP-3 HEADLINE (ranked by applicability x HD-fit x novelty-vs-current)

1. **GRID-CELL VSA + CONTINUOUS-ATTRACTOR HYBRID** — mech 5 + 8 fused; CAN-bump dynamics + VSA binding for cognitive maps; published 2025 (arXiv:2503.08608) already shows hexagonal receptive fields + path integration + symbolic reasoning (family trees) co-exist in same substrate. NOT yet drilled in our stack. **P_chain-grade (deflated) = 0.40**.

2. **VSA FINITE STATE MACHINES IN ATTRACTOR NETWORKS** — mech 5 (attractor) explicit-replacement for argmax cleanup; substrate retrieval as iterative-dynamics-to-fixed-point INSTEAD of single-shot argmax over Store. Direct lever for n10-whitening + n9-sparsemax-decode revival lanes. **P_chain-grade (deflated) = 0.42**.

3. **PREDICTIVE-CODING RESIDUALS / FREE-ENERGY** — mech 1; substrate-natural since HD residuals = (target - predicted_from_W) is already what the substrate computes implicitly; reframing as explicit prediction-error hierarchy unlocks (a) hierarchical generative-model in W (b) anomaly-gating in continual ingest (c) compositional inference. **P_chain-grade (deflated) = 0.38**.

---

## PER-MECHANISM ANALYSIS (12 mechanisms)

### 1. Predictive coding / free-energy principle (Friston; Rao-Ballard 1999)
- **Summary:** Brain runs hierarchical generative model; each layer predicts the layer below; only prediction-errors propagate up. Friston's free-energy principle generalizes: minimize variational free energy = surprise.
- **Substrate applicability:** 5/5 — substrate Store-write IS error-correction (we already store residuals after cleanup); reframing as explicit predict-then-correct unlocks anomaly detection + selective ingest gating.
- **HD-fit:** 4/5 — bipolar HD vectors are linear; residuals = HD subtraction is native; hierarchical W-stacks already exist in substrate.
- **Difficulty:** Low-to-medium. Cheap cell: predict-from-W vs target; ingest only top-K-residual items per batch. Mid: hierarchical W stack with bottom-up errors + top-down predictions.
- **Citation:** Rao & Ballard (1999) Nat Neuro; Friston (2010) NRN; recent review Salvatori et al. 2023 "Brain-inspired Computational Intelligence via Predictive Coding" (arXiv:2308.07870).

### 2. Neural binding via gamma synchronization (Crick-Treisman; Singer-Gray)
- **Summary:** Features bound by simultaneous gamma-band (25-80 Hz) firing; "what fires together binds together" — temporal-binding solution to binding problem.
- **Substrate applicability:** 3/5 — substrate has no time-base by default; would require introducing oscillator-state-vectors. PARTIAL OVERLAP with HRR phase-binding (Plate 1995).
- **HD-fit:** 4/5 — Furlong & Eliasmith 2023 "Hyperdimensional Computing Provides a Programming Paradigm for Oscillatory Systems" (arXiv:2312.11783) maps binding/bundling onto coupled phase oscillators directly.
- **Difficulty:** Medium-high. Need oscillator-state extension to Store atoms; phase-coding decode unclear vs argmax.
- **Citation:** Singer & Gray (1995) Annu Rev Neurosci; Furlong & Eliasmith (2023) arXiv:2312.11783.

### 3. Thalamic relay + basal ganglia gating
- **Summary:** Thalamus (esp. mediodorsal, pulvinar) gates which cortical loops are active; basal ganglia (striatum->GPi->thalamus) implements action-selection via tonic inhibition release. Computational bottleneck via tonic-inhibition output.
- **Substrate applicability:** 4/5 — substrate currently retrieves over ALL of W; gating mechanism could route queries to W-submatrix per query-class (massive efficiency win for million-atom scale). Bartlett 2024 (UC eScholarship 6067f4sm) already implements VSA basal-ganglia with distributed action representations.
- **HD-fit:** 4/5 — gate = HD-mask vector bound elementwise to query; substrate-native multiplicative binding.
- **Difficulty:** Medium. Need query-classifier (substrate-internal) + per-class W partition; risk of partition-collapse if classifier wrong.
- **Citation:** Bartlett et al. 2024 (CogSci, escholarship.org/uc/item/6067f4sm); Halassa & Sherman 2024 "The unique role of the associative thalamus" (ScienceDirect S0361923025002448).

### 4. Neuromodulator state-control (DA/5HT/ACh/NE)
- **Summary:** ACh = learning-rate gate; DA = reward prediction-error; 5HT = time-horizon; NE = exploration noise. Recent 2024-2025: ACh and DA anti-correlate in striatum and ACh demixes heterogeneous DA signals.
- **Substrate applicability:** 4/5 — substrate has NO global-state vector; introducing a "modulator HD vector" per query (bound to all retrievals in a session) is cheap + opens learning-rate-per-session, threshold-per-context, exploration-per-mode.
- **HD-fit:** 5/5 — single HD vector composes via bind/superposition with every operation; no new primitive needed.
- **Difficulty:** Low. Single MODULATOR vector + cosine-gating on cleanup-threshold.
- **Citation:** Krasne et al. 2024 "Acetylcholine demixes heterogeneous dopamine signals" (bioRxiv 2024.05.03.592444); Doya 2002 NN classic.

### 5. Continuous attractor networks (Amari; Wilson-Cowan)
- **Summary:** Recurrent network with continuous manifold of fixed points; retrieval = bump-state settles into nearest basin. Ring/torus attractors implement head-direction/grid-cell coding. Modern Hopfield (Krotov-Hopfield 2016, Ramsauer 2021) gives exponential capacity.
- **Substrate applicability:** 5/5 — substrate cleanup IS one-shot argmax; iterative cleanup (substrate -> Store -> substrate) is the attractor analog. Modern-Hopfield link to softmax-attention already proven; substrate-as-MHN reframing is natural. Saxena & Bartlett 2024 arXiv:2212.01196 explicit "VSA Finite State Machines in Attractor Neural Networks".
- **HD-fit:** 5/5 — bipolar/sparse HD vectors are valid Hopfield states; iteration is matmul.
- **Difficulty:** Low-medium. Cheap cell: iterative cleanup (N=3-5 iters) vs single-shot baseline; measure recall@noise.
- **Citation:** Saxena & Bartlett 2024 arXiv:2212.01196; Ramsauer et al. 2021 ICLR "Hopfield Networks Is All You Need"; Krotov-Hopfield 2016 NeurIPS.

### 6. Reservoir computing / liquid state machines (Maass; Jaeger)
- **Summary:** Fixed random recurrent W (the "reservoir") + trained linear readout; reservoir provides nonlinear basis expansion. Critical-branching reservoirs maximize computational capacity. SpaRCe variant uses sparse representations.
- **Substrate applicability:** 3/5 — substrate's W is the "trained" part; reservoir says invert: fix random W, train tiny readout. Partial fit. Could compose: substrate W as the reservoir + tiny per-task readout (continual-learning).
- **HD-fit:** 5/5 — HD bipolar vectors ARE random projections; reservoir-state-as-HD-vector is one-liner.
- **Difficulty:** Low. Use frozen-random-W reservoir; train per-task softmax readout on substrate state. Critical-state init needs spectral-radius tuning.
- **Citation:** Damicelli et al. 2026 MDPI "Reservoir Computing: Foundations" (mdpi.com/2673-2688/7/2/70); Manneschi et al. (SpaRCe sparse reservoirs); Jaeger 2001 ESN.

### 7. Default-mode network (Raichle 2001) — spontaneous/idle replay
- **Summary:** Brain regions co-active at rest (vs task); recent 2025 evidence (Higgins/Smallwood ScienceDirect S235215462500141X) frames DMN as the neural workspace where hippocampal replay couples with neocortical consolidation during idle windows. Cascaded-memory-systems model (NRN 2022).
- **Substrate applicability:** 4/5 — substrate has NO idle-state process. Idle-consolidation = run SWR-style replay (already shipped in c2) UNPROMPTED between query batches; consolidates recent-arc into long-term W. Direct lever for continual learning.
- **HD-fit:** 4/5 — replay = sample recent atoms + re-bind via W; native.
- **Difficulty:** Low-medium. Cheap cell: between-batch idle-replay (rebind recent atoms via current W; commit residual updates). Combines with c2 cascade-synapse already chain-grade.
- **Citation:** Higgins et al. 2022 NRN "Replay, the default mode network and the cascaded memory systems model"; Higgins & Smallwood 2025 (ScienceDirect S235215462500141X).

### 8. Place cells / grid cells / time cells (O'Keefe; Moser; Eichenbaum)
- **Summary:** Place cells = location-specific firing; grid cells = hexagonal-tiled multi-scale spatial code in entorhinal cortex; time cells = sequential temporal context. Subicular spatial codes arise from PREDICTIVE MAPPING (bioRxiv 2024.11.06). Unified spatial+conceptual model (PNAS 2024.2413449122).
- **Substrate applicability:** 5/5 — substrate has NO native position-coding; grid-cell VSA gives compositional spatial codes that scale logarithmically. PLUS: grid-code generalizes to CONCEPTUAL space (PNAS 2024) — substrate-relational embeddings get hexagonal-tile structure for free. Schlegel et al. 2025 arXiv:2503.08608 GC-VSA already published.
- **HD-fit:** 5/5 — VSA primitives + 3D-toroidal modules; explicit construction in 2503.08608.
- **Difficulty:** Medium. 3D-toroidal-module VSA + path integration + symbolic-reasoning tasks; reference implementation likely available on arXiv companion code.
- **Citation:** Schlegel et al. 2025 arXiv:2503.08608 "Grid Cell-Inspired Structured Vector Algebra for Cognitive Maps"; Whittington et al. 2024 PNAS 2413449122; Stachenfeld et al. 2017 Nat Neuro (successor representation).

### 9. Memory engram cells (Tonegawa; Josselyn) — sparse allocation
- **Summary:** Memories stored in sparse ensembles of co-active neurons; allocation biased by transient CREB/excitability state; competitive winner-take-most. 2024: Choi et al. Cell (2024)01216-9 stress disrupts engram allocation; J Neurosci 2024 e0846232024 intrinsic excitability biases allocation.
- **Substrate applicability:** 4/5 — substrate already has sparse k-WTA-VQ (brain-drill #1 n4 HARD_FAILed at capacity but lit-revival still active); engram-style ALLOCATION rule (write-time biasing of which atoms participate based on transient-excitability state) is novel addition. Composes with cascade-synapse (c2).
- **HD-fit:** 5/5 — sparse vectors are HD-native; allocation = top-K-by-excitability + sparse-superposition.
- **Difficulty:** Medium. Need excitability-state HD vector (slow time constant) + allocation-rule at ingest.
- **Citation:** Mocle et al. 2024 J Neurosci e0846232024; Josselyn & Tonegawa 2020 Science review; Spalla et al. 2026 arXiv 2506.01659 "Engram Memory Encoding and Retrieval: A Neurocomputational Perspective".

### 10. Glia-neuron / tripartite synapse (astrocyte support)
- **Summary:** Astrocytes regulate synaptic strength on slow timescales via gliotransmitters (D-serine, ATP, glutamate uptake); tripartite synapse = pre + post + astrocyte. 2025: AGMP (Astrocyte-Gated Multi-Timescale Plasticity, Frontiers fnins.2025.1768235) shows online continual learning via astrocyte-gating. Astrocytes can STORE AND RECALL memory (PMC11738474).
- **Substrate applicability:** 3/5 — substrate has only ONE timescale (write-then-read); astrocyte-analog = SLOW W (background substrate) + FAST W (foreground substrate) with astrocyte-gated transfer. Partial overlap with cascade-synapse but with slow-substrate-as-context. UNIQUE angle: per-relation slow-modulation of cleanup-threshold.
- **HD-fit:** 4/5 — slow HD context-vector + multiplicative gating is native.
- **Difficulty:** Medium-high. Need 2nd timescale + transfer rule; risk of slow/fast race conditions.
- **Citation:** Liu et al. 2025 Frontiers fnins.2025.1768235 "Astrocyte-gated multi-timescale plasticity"; Kastanenka et al. 2025 PMC11738474 "Can Astrocytes Store and Recall Memory?".

### 11. Brain criticality / 1/f scaling (Beggs-Plenz)
- **Summary:** Cortical networks self-organize to critical point (neuronal-avalanches with power-law size distribution); maximizes dynamic range + memory capacity + computational power. Recent (RSI 2026 20251192) shows allometric scaling explained by avalanche criticality.
- **Substrate applicability:** 3/5 — substrate is NOT a dynamical system; criticality concept maps as "operating-point" tuning of cleanup-threshold + sparsity to maximize capacity at edge-of-chaos. Composes with reservoir-computing lever (mech 6) via spectral-radius=1 init.
- **HD-fit:** 3/5 — indirect; criticality is a DYNAMICAL property; substrate is static-lookup. Strongest fit IS via reservoir-as-substrate.
- **Difficulty:** Medium. Need dynamical substrate (recurrent W); measure avalanche distributions in retrieval. Cheap version: sparsity-sweep with capacity-curve, look for power-law-break at optimum.
- **Citation:** Beggs & Plenz 2003 J Neurosci classic; Plenz 2026 Royal Soc Interface 20251192; Massobrio et al. 2026 arXiv 2512.10834.

### 12. Hippocampal pattern separation/completion — DG sparse coding
- **Summary:** Dentate gyrus performs pattern separation via SPARSE granule-cell coding (~1% activity) + mossy-cell adaptive thresholds; CA3 recurrent collaterals perform pattern completion. Inverse roles in same circuit.
- **Substrate applicability:** 4/5 — already partial (n4 k-WTA-VQ HARD_FAILed). DEEPER drill on WHY DG sparse coding WORKS in vivo (mossy-cell adaptive thresholds, lateral inhibition timing, granule-cell silence-baseline) vs our k-WTA failure. The 1% activity + adaptive-threshold combination is a specific architectural lever we did NOT test. Risk: similar failure mode.
- **HD-fit:** 4/5 — sparse-bipolar HD vectors are well-studied; adaptive-threshold + mossy-cell-like lateral inhibition is implementable.
- **Difficulty:** Medium. Need adaptive-threshold dynamics + separate "interneuron" lateral-inhibition matrix.
- **Citation:** Babadi & Sompolinsky combinatorial DG model (MIT Press Neural Comp 2017); biorxiv 2022.03.07.483263 "Dentate gyrus mossy cells exhibit sparse coding via adaptive spike threshold dynamics"; PMC4373261 "Pattern separation efficiency in dentate gyrus".

---

## CROSS-COMPOSITION MATRIX — which COMPOSE with existing chain-grade

| New mech | Composes-with chain-grade | Substitutes / replaces |
|---|---|---|
| 1 Predictive-coding | c1 CLS, c2 cascade-synapse (anomaly-gated ingest) | nothing |
| 2 Gamma-binding | r1 multi-hop (phase-binding for slots) | HRR phase binding (already exists) |
| 3 Thalamic-BG gating | n11 ATL hub-spoke, retrieval pipeline | argmax-over-full-W cleanup |
| 4 Neuromodulator-state | ALL retrievals (single-vector binding) | static threshold |
| 5 Attractor / iterative | n9 sparsemax, n10 whitening, r1 cleanup | one-shot argmax cleanup |
| 6 Reservoir | n11, m1 modular (per-module readout) | trained-W (inverts the architecture) |
| 7 DMN idle-replay | c2 cascade-synapse, g1b generation | nothing (additive) |
| 8 Grid-cell VSA | All relational ingest (cognitive maps) | random-vector spatial encoding |
| 9 Engram allocation | n4 k-WTA (allocation rule), c2 cascade | random-allocation k-WTA |
| 10 Astrocyte slow-W | c2 cascade-synapse (slow-timescale extension) | single-timescale W |
| 11 Criticality | mech 6 reservoir (spectral-radius=1) | static sparsity-pick |
| 12 DG pattern-separation | n4 k-WTA revival (adaptive threshold) | static k-WTA threshold |

**KEY OBSERVATION:** mechs 1, 4, 7, 9 are PURE ADDITIVE (don't replace existing chain-grade primitives) — lowest integration risk. mechs 5, 8 REPLACE existing argmax/random-vector encoding — higher upside but per-existing-cell regression risk.

---

## TOP-3 CHEAP-DECISIVE-TEST PRE-REGS

### TEST A — Attractor-network iterative cleanup (mech 5)
**Cell name candidate:** `att1_iterative_cleanup_v1`
**Hypothesis:** Iterative cleanup (N=3-5 substrate->Store->substrate iterations) outperforms single-shot argmax at noise sigma >= 0.5.
**Substrate:** Reuse n10 whitening pipeline OR n9 sparsemax with `n_cleanup_iters` parameter.
**Design:** Arms = {1, 3, 5, 10 cleanup iterations}; 3 noise levels {0.3, 0.5, 0.7}; 3 seeds; M = 10000 atoms; D = 8192.
**HARD bands (PRE-REG):**
- HARD_PASS: iter-5 recall@sigma=0.5 >= iter-1 recall@sigma=0.5 + 0.15 absolute (e.g. 0.55 -> 0.70)
- MIDDLE_BAND: iter-5 recall@sigma=0.5 in [iter-1 + 0.05, iter-1 + 0.15]
- HARD_FAIL: iter-5 recall@sigma=0.5 < iter-1 recall@sigma=0.5 + 0.05
- CV across seeds < 0.05 mandatory
**Cost:** ~2 GPU-hours; smoke fast on laptop.
**P_deflated:** 0.42 (well-published mech; substrate-fit clean; risk = substrate Store retrieval is not differentiable so iterative loop may oscillate).
**Cited prior:** Saxena & Bartlett 2024 arXiv:2212.01196 (VSA-FSM-attractor); Ramsauer 2021 (modern Hopfield).

### TEST B — Predictive-coding residual ingest gate (mech 1)
**Cell name candidate:** `pc1_residual_gated_ingest_v1`
**Hypothesis:** Ingesting only top-K-residual atoms per batch (anomaly-gated) maintains chain-grade recall at lower atom-count vs naive-ingest-all.
**Substrate:** Reuse c1 CLS-replay pipeline; add `residual_gating_topK` arm.
**Design:** Arms = {ingest-all, gate-top-50%, gate-top-25%, gate-top-10%}; 3 seeds; M = 50000 candidate atoms; measure recall + final-stored-atom-count.
**HARD bands (PRE-REG):**
- HARD_PASS: gate-25% recall >= ingest-all recall - 0.03 absolute AND atom-count <= 30% of ingest-all
- MIDDLE_BAND: gate-25% recall in [ingest-all - 0.10, ingest-all - 0.03]
- HARD_FAIL: gate-25% recall < ingest-all - 0.10 OR atom-count > 50%
- CV across seeds < 0.05
**Cost:** ~1 GPU-hour; smoke on laptop CPU.
**P_deflated:** 0.38 (mech is well-motivated but predict-from-W signal quality unknown; risk = residual computation costs more than ingest-savings).
**Cited prior:** Salvatori et al. 2023 arXiv:2308.07870; Rao & Ballard 1999.

### TEST C — Grid-cell VSA spatial/relational compositional encoding (mech 8)
**Cell name candidate:** `gc1_grid_vsa_relational_v1`
**Hypothesis:** Grid-cell-VSA encoding of multi-hop relational paths outperforms random-vector HRR encoding at path-length >= 3.
**Substrate:** Build minimal 3D-toroidal-module VSA (3 modules x dims = 3 x 2048); benchmark against r1 multi-hop pipeline on family-tree task (per Schlegel 2025).
**Design:** Arms = {HRR-random, GC-VSA-3mod, GC-VSA-5mod}; path lengths {1, 2, 3, 4, 5}; 3 seeds; N_family_tree_facts = 500.
**HARD bands (PRE-REG):**
- HARD_PASS: GC-VSA-3mod path-len-5 accuracy >= HRR path-len-5 accuracy + 0.20 absolute
- MIDDLE_BAND: GC-VSA-3mod path-len-5 accuracy in [HRR + 0.05, HRR + 0.20]
- HARD_FAIL: GC-VSA-3mod path-len-5 accuracy <= HRR path-len-5 accuracy
- CV across seeds < 0.07
**Cost:** ~2-3 GPU-hours including replication baseline.
**P_deflated:** 0.40 (clean replication target with published code likely on arXiv companion; novel application to substrate-relational ingest).
**Cited prior:** Schlegel et al. 2025 arXiv:2503.08608 GC-VSA; Whittington et al. 2024 PNAS 2413449122 unified spatial/conceptual.

---

## RECOMMENDED NEXT-CELL CANDIDATE

**Primary: TEST A — `att1_iterative_cleanup_v1`** — cheapest, most-additive, composes with TWO in-flight revival lanes (n9-sparsemax + n10-whitening), highest-confidence published baseline. ~2 GPU-hours; results decisive in 1 cycle.

**Secondary: TEST B if A passes** — `pc1_residual_gated_ingest_v1` opens continual-learning capacity reduction.

**Tertiary (longer-horizon): TEST C** — needs build effort but novel-direction lever for next-quarter cognitive-maps program.

## KEY INSIGHT (one-line)

The single highest-leverage missing-primitive across all 12 mechanisms is **iterative attractor-style cleanup** (mech 5) — it converts the substrate's one-shot argmax bottleneck (which has failed in 4+ cells: n4, n9, n10 partials, p1 prereg) into a multi-step dynamical recovery, and modern-Hopfield theory says this gives exponential effective capacity for free; the brain-literature converges on this answer from multiple mechanisms (CAN bumps, DG-CA3 completion, ring attractors, dense associative memory).

## Citations (>=12)

1. Salvatori et al. 2023 "Brain-inspired Computational Intelligence via Predictive Coding" — arXiv:2308.07870
2. Furlong & Eliasmith 2023 "HDC Provides a Programming Paradigm for Oscillatory Systems" — arXiv:2312.11783
3. Bartlett et al. 2024 "VSAs for Distributed Action Representations in Spiking Basal Ganglia" — escholarship.org/uc/item/6067f4sm
4. Krasne et al. 2024 "Acetylcholine demixes heterogeneous dopamine signals" — bioRxiv 2024.05.03.592444
5. Saxena & Bartlett 2024 "Vector Symbolic Finite State Machines in Attractor Neural Networks" — arXiv:2212.01196
6. Ramsauer et al. 2021 "Hopfield Networks Is All You Need" — ICLR
7. Damicelli et al. 2026 "Reservoir Computing: Foundations, Advances, and Challenges" — mdpi.com/2673-2688/7/2/70
8. Higgins et al. 2022 "Replay, the default mode network and the cascaded memory systems model" — Nature Rev Neurosci
9. Schlegel et al. 2025 "A Grid Cell-Inspired Structured Vector Algebra for Cognitive Maps" — arXiv:2503.08608
10. Whittington et al. 2024 "A unified neural representation model for spatial and conceptual computations" — PNAS 2413449122
11. Mocle et al. 2024 "Intrinsic Neural Excitability Biases Allocation and Overlap of Memory Engrams" — J Neurosci e0846232024
12. Spalla et al. 2026 "Engram Memory Encoding and Retrieval: A Neurocomputational Perspective" — arXiv:2506.01659
13. Liu et al. 2025 "Astrocyte-gated multi-timescale plasticity for online continual learning" — Frontiers fnins.2025.1768235
14. Massobrio et al. 2026 "Allometric scaling of brain activity explained by avalanche criticality" — arXiv:2512.10834 / Royal Soc Interface 20251192
15. Babadi & Sompolinsky 2017 "A Combinatorial Model for Dentate Gyrus Sparse Coding" — Neural Computation
16. Halassa & Sherman 2024 "The unique role of the associative thalamus" — ScienceDirect S0361923025002448

## Honest limitations
- Per lit-scan calibration discipline: raw P-estimates deflated 0.15-0.25; novel-synthesis P capped 0.50. Best deflated P_chain-grade = 0.42 (TEST A).
- Two key PDFs (arXiv 2212.01196 and 2312.11783) failed to extract via WebFetch (corrupted-binary response) — full mechanism details for VSA-FSM and oscillatory-HDC would need ssh-fetch + local PDF parse before cell-building. NOT a blocker for the broad-exploration drill (abstracts + search synthesis sufficient for ranking); IS a blocker before pre-reg ships.
- "Already-drilled" exclusions taken from notes/ filename scan + memory index; if a mechanism IS already deep-drilled and I missed it, re-route.
- Substrate-applicability ratings are MY judgment; sanity-check against Skunkworks before commit-to-cell.
