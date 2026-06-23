# Research drill — sparse-allocation routing learning (substrate-native learned routing)

**Date:** 2026-06-23
**Author:** research (Opus 4.7-1M)
**Trigger:** USER drill — de-risk top-tier enabling path #3 (sparse engram allocation). Concern: brain sparse coding works because routing is LEARNED, not random. Substrate currently uses random sparse positions per atom. Without learned routing, may lose the "right neurons for right concept" benefit that makes biological sparse coding actually work.
**Calibration:** lit-scan penalty applied at 0.25 deflation (3 prior null forward-only encoder attempts: SoftHebb, Foldiak anti-Hebbian, FPE, char-trigram all HARD_FAILed in `exp_encoder_dual_gain_softhebb_v1`). Novel-synthesis P capped at **0.40**.
**Method:** 5 parallel WebSearch lit-scans (Sonnet), Opus synthesis. Generic math terms only per query-privacy.

---

## HEADLINE

**The top substrate-native routing learning candidate is excitability-biased recruitment (Tonegawa-CREB analog) implemented as a Hebbian "allocation-trace" counter on atom positions, NOT a SoftHebb-style soft-WTA on encoder weights.** Forward-only IS feasible for this specific mechanism class (the trace is a per-atom scalar updated by local activity statistics; no global gradient needed), and the prior SoftHebb HARD_FAIL does NOT close this path because SoftHebb learned the WRONG thing (encoder weights for representation reconstruction, not allocation gating for routing). The cheap decisive test is a 3-arm cell comparing random-allocation (baseline) vs excitability-trace-allocation (Tonegawa) vs k-WTA-Hebbian-allocation (cerebellar Marr-Albus), measured on a clustering-purity discriminator on the existing chain-grade KG. **P_deflated for excitability-trace HARD_PASS = 0.32** (forward-only-compatible, narrow scope, novel composition). **Backprop minimum viable infrastructure if needed:** single linear projection trained via InfoNCE contrastive loss on KG-edge pairs, ~50K params, ~1-2hr CPU train, but only as fallback if the 3-arm excitability test HARD_FAILs.

**Critical reframe:** the prior 4 HARD_FAILs were on encoder-side noise robustness at sigma=1.5. That is a SEPARATE problem from allocation routing. Allocation routing operates at the storage layer (which atom positions get written), not at the input encoder layer. Confusing the two is the dominant failure mode here.

---

## CHEAP DECISIVE TEST (pre-registered)

**Cell name:** `alloc_routing_excitability_trace_v1`
**Wall budget:** ~45-60 min laptop CPU (lightweight; no encoder retraining needed)
**Pre-flight:** sigma=0 sanity recall=1.000; HDLAB_EXP_NAME set; schema-vet via `tools/exp_dev/formula_selftests.py`; commit pre-reg before dispatch.

### 3-arm sweep, single cell

| ARM | Allocation mechanism | Sparse-K params | Update rule |
|---|---|---|---|
| ARM_RANDOM (baseline) | uniform random K positions per atom | K=64 (sparsity 1.5%, N=4096) | none |
| ARM_EXCITABILITY_TRACE | weighted-random K positions; weights = per-position excitability counter | K=64 | excit[i] += alpha * activity[i] - decay; sample K positions by softmax(excit / T) |
| ARM_KWTA_HEBBIAN | top-K activated positions by W @ x_input; Hebbian update on W | K=64 | W[i,j] += eta * y[i] * x[j] for i in top-K |

### Per-arm metrics (3 seeds each)

**M1 — Cluster purity on chain-grade KG (load-bearing):** ingest 100 chain-grade atoms with known capability-cluster labels (use the substrate_self_map_v1 Director-built lexical families as imperfect-but-existing ground truth, accepting the ~10% upper bound from v2d-smoke). Measure ARI of allocated-position-overlap clustering vs labels.

**M2 — Cleanup recall @ sigma=0.5:** retrieve atom from noisy cue at moderate noise (NOT sigma=1.5 — that is the Shannon-floor regime which is closed). 200 atoms / 3 seeds.

**M3 — Compositional generalization:** after ingesting 100 atoms, test allocation of 20 HELD-OUT atoms whose labels were never seen. Do they get allocated to overlapping positions with their semantic neighbors? Measure neighbor-overlap-rate.

### Discriminator (load-bearing question)

Does excitability-trace allocation (ARM_EXCITABILITY_TRACE) produce a higher cluster purity (M1) than random allocation (ARM_RANDOM) at p<0.05 across 3 seeds?

This is the FUNDAMENTAL test: does the substrate gain anything from learned vs random sparse routing? If random already gives the substrate full capacity (which prior chain-grade results suggest), then learned routing is a non-improvement and the engram-allocation Path is closed.

### HARD bands (deflated; novel-composition cap)

- **HARD_PASS:** ARM_EXCITABILITY_TRACE M1 ARI ≥ ARM_RANDOM M1 ARI + 0.15 AND p<0.05 AND M3 neighbor-overlap-rate ≥ 0.25 AND M2 recall ≥ 0.80. P = **0.32** (Tonegawa-analog mechanism transfers; substrate gains semantic locality from learned routing).
- **MIDDLE_BAND:** ARM_EXCITABILITY_TRACE M1 lift in (0.05, 0.15) OR M3 neighbor-overlap in (0.15, 0.25). P = **0.30** (partial mechanism; characterize whether trace decay rate or K matters).
- **HARD_FAIL:** ARM_EXCITABILITY_TRACE M1 ≤ ARM_RANDOM M1 + 0.05 AND M3 neighbor-overlap ≤ 0.15. P = **0.38** (random sparse allocation is structurally as good as learned at substrate's existing scale; engram-allocation path closed at chain-grade scope; META: "substrate sparse allocation is regime-invariant to randomness vs learning at N=4096 / M<1000").

### Pre-registered HARD_FAIL meaning

If HARD_FAIL: the substrate-native learned-routing hypothesis is structurally null at production scope. **DO NOT** propose a 2nd Hebbian-allocation variant. Pivot directly to **backprop minimum infrastructure** (Sec 4 below) — single-linear-projection contrastive encoder trained via InfoNCE on KG edges. Atomize META: "substrate-native forward-only routing-learning at chain-grade scope cannot improve over random allocation; backprop is required for routing geometry."

If HARD_PASS: lift excitability-trace into `hdlab/allocation_trace.py` as substrate primitive; compose with kg_traversal for the chain-grade self-mapping rescue (v2f); dispatch substrate_self_map_v2 with learned-routing encoder.

### Ablation (optional, only if HARD_PASS)

- alpha sweep {0.01, 0.05, 0.1} — trace learning rate
- T sweep {0.5, 1.0, 2.0} — allocation temperature
- K sweep {16, 64, 256} — sparsity vs capacity tradeoff

---

## FALSIFIABLE PREDICTIONS

**Prediction 1 (HARD_PASS regime):** If learned routing helps, the lift is BIGGEST at K=16 (rich-get-richer most pronounced under most sparse) and SHRINKS at K=256 (random allocation already covers state space). HARD_FAIL: lift is monotone-increasing with K.

**Prediction 2 (mechanism class):** Excitability-trace will beat k-WTA-Hebbian at clustering purity because the trace operates on POSITION statistics (substrate-native, low-dim O(N)) while k-WTA operates on weight matrices (O(N×D), prone to under-training at production scope per the SoftHebb HARD_FAIL). HARD_FAIL: k-WTA wins, implying weight-based learning is required and backprop becomes more attractive.

**Prediction 3 (compositional emergence):** If excitability-trace HARD_PASSes M1 AND M3, that is independent evidence that learned routing intrinsically gives compositional clustering — i.e., the "functionally similar atoms → overlapping ensembles" property emerges WITHOUT an explicit competitive-allocation rule. HARD_FAIL: M1 PASSES but M3 FAILS, implying explicit competitive-allocation needs to be added.

---

## L1 / L2 / L3 STRUCTURE — full drill

### L1 — Brain mechanisms for sparse-routing learning (5 angles)

**1. Tonegawa engram allocation (CREB/calcineurin excitability)** — Most-cited mechanism class. Neurons compete for inclusion in a memory ensemble based on intrinsic excitability immediately before training. CREB upregulation in a subset of lateral amygdala neurons biases their recruitment. Excitability is set by recent activity + IEG expression (cAMP/PKA cascade). The selection is **probabilistic but biased** — high-excitability neurons "win" the competition but the recruitment is not deterministic. Key papers: Han 2007 (CREB allocation), Yiu 2014 (CREB sufficient for allocation), Cai 2016 (overlap depends on temporal proximity via shared excitability window), Pignatelli 2019 (engram-cell-specific intrinsic excitability), 2024 JNeurosci PMC11112642 (intrinsic excitability biases allocation + overlap).

**Substrate-translatable mechanism:** maintain a per-atom-position "excitability trace" scalar that decays with time and increments with recent activity. When allocating a new atom, sample K positions weighted by softmax(trace / T). High-trace positions get rich-get-richer; positions never used decay to baseline.

**2. Dentate gyrus pattern separation (cell birth + plasticity)** — Adult-born granule cells (4-6 weeks) have **heightened plasticity + low input specificity + high excitability** during a critical window. As they mature (6-8 weeks), specificity rises + excitability drops. Effect: a rolling "fresh learning" subpopulation while consolidated memories sit in mature-cell ensembles. Pattern separation is achieved via **sparse activation + lateral inhibition** (feedback inhibition through GABAergic interneurons modulates sparseness).

**Substrate-translatable mechanism:** atoms have an "age" stamp; recently-allocated atoms get HIGHER excitability bonus during the critical window (last K atoms allocated), then mature into the baseline pool. This is essentially **age-decayed Hebbian-trace allocation** — a special case of mechanism (1).

**3. Cerebellar Marr-Albus (parallel-fiber-Purkinje LTD)** — Classical sparse pattern-separation theory: granule cells form sparse combinatorial encoding (~K=4-5 active out of millions), parallel-fiber-Purkinje synapses undergo LTD guided by climbing-fiber error. **Important update:** Recent Ca2+ imaging shows granule cell activity is actually DENSE not sparse in the standard Marr framing (Cayco-Gajic 2017 / Nature Sci Rep 2025 critique). Litwin-Kumar 2017 / eLife 82914 (Task-dependent optimal representations): optimal granule cell representation depends on task — discriminating random stimuli wants sparse (Marr regime); continuous I/O wants dense. **Sparsity is task-dependent, not fundamental.**

**Substrate-translatable insight:** the right K for substrate is NOT a fixed biological constant (K=4-8); it depends on what the substrate is doing. For KG clustering / chain-grade self-mapping at chain-grade scope, K should be SWEPT not assumed.

**4. Drosophila Kenyon cell allocation (dopaminergic plasticity)** — Each MB has ~2000 KCs; an odor activates ~5% (~100 KCs) — true sparse coding. APL neuron ensures sparseness via feedback inhibition (Lin 2014, eLife 56954). Dopaminergic neurons drive **zonally restricted LTD at KC→MBON synapses** (not at KC inputs themselves). **Key insight:** the SPARSE CODING ITSELF is fixed by anatomy/inhibition; learning happens at the OUTPUT side (KC→MBON), not at the input-routing side. Learning shifts WHICH MBON the KC ensemble drives, not WHICH KCs are recruited for an odor.

**Substrate-translatable insight:** for Drosophila-mode, allocation is NOT learned — it is anatomically random + inhibition-sparsened. Learning happens at the readout layer. This SUPPORTS the substrate's current random-allocation choice if Drosophila is the right analog. Argues for testing random-allocation as baseline (ARM_RANDOM in our cell) NOT as a strawman but as a strong-prior contender.

**5. Predictive coding gating (Rao-Ballard / Friston)** — Top-down prediction signals gate which neurons fire; only prediction-error neurons activate strongly. Implementation: prior + likelihood → posterior via Bayesian inference; sparse activation emerges from divisive normalization. Highly developed for vision; less so for memory routing per se. Bremer 2023+ relating sparse/predictive to divisive normalization (bioRxiv 544285). **Not directly translatable** to substrate's KG-routing problem without significant infrastructure (need a top-down predictor model).

### L2 — Substrate-applicable filter

Filter criteria:
1. Forward-only / Hebbian-compatible (no global gradient signal) — REQUIRED unless we accept backprop fallback
2. Operates on POSITIONS or SCALARS not WEIGHTS — substrate is high-dim sparse; weight-based learning at N=4096 was attempted (SoftHebb) and HARD_FAILed
3. Composes with existing `kg_traversal.KGStore` ingest pipeline
4. Adds bounded state (O(N) not O(N×D))

| Mechanism | F-only | Position-not-weight | Composes-with-KGStore | Bounded state | KEEP? |
|---|---|---|---|---|---|
| Tonegawa excitability-trace | YES | YES (per-position scalar) | YES | O(N) | **TOP** |
| Adult-born DG age-decay | YES (special case of above) | YES | YES | O(N) | subsumed |
| Cerebellar k-WTA Hebbian | YES | NO (weights W[N,D]) | YES | O(N×D) | secondary |
| Drosophila random + inhibition | YES (no learning) | YES | YES | O(1) | baseline (ARM_RANDOM) |
| Predictive coding gating | needs top-down model | YES | NO (no predictor) | O(N) | SKIP |
| SoftHebb (prior HARD_FAIL) | YES | NO (weights) | YES | O(N×D) | SKIP — already failed |
| Foldiak anti-Hebbian (prior HARD_FAIL) | YES | NO (lateral W) | YES | O(N×N) | SKIP — already failed |
| FPE contrastive (prior HARD_FAIL) | YES | NO (phase weights) | YES | O(N) | SKIP — already failed |

**Top candidate: excitability-trace allocation (Tonegawa-analog). Secondary: k-WTA Hebbian (cerebellar). Baseline: random (Drosophila-analog).** This is the 3-arm cell.

### L3 — Depth on top-2 candidates

#### Excitability-trace allocation (depth)

**Mathematical form:**
- State: `excit[i]` for i in {1..N=4096}, initialized at 1.0
- Per-atom-allocation step: for atom_a, sample K=64 positions via `softmax(excit / T)` (with replacement OR without per design choice — recommend without, with Gumbel-top-K trick)
- Per-atom-write update: for each selected position i, `excit[i] += alpha * 1.0` (activity), then `excit[i] *= (1 - decay)` for all positions (global decay)
- Optional: cap `excit[i]` at some ceiling C to prevent runaway

**Substrate-native fit:** This is structurally a Hebbian-trace on positions. The trace IS the substrate's only learnable state (no encoder weights, no backprop). The mechanism implements rich-get-richer: positions allocated to many semantically-related atoms get re-allocated to future related atoms (the "right neurons for right concept" property).

**Brain-faithful refinement:** add a "saturation" term so over-allocated positions don't dominate. Bio analog: depolarization block in over-driven neurons. Math: `excit[i] *= sigmoid((C - allocation_count[i]) / sigma_sat)`. This is the substrate's analog of calcineurin feedback in Tonegawa engrams.

**Cost:** ~O(N) state, O(N) per-allocation update, O(K log N) per sample (Gumbel-top-K). At N=4096 / K=64 / M=1000 atoms, total compute is ~4M ops — trivial CPU.

**Risk:** excitability-trace might just produce uniform allocation in steady state if decay is fast (washes out signal) or runaway concentration if decay is slow (collapses to a few dominant positions). The alpha/T/decay sweep in the ablation is essential. P that there exists a parameter setting where the mechanism gives the right balance: ~0.60. P that this balance also gives clustering lift over random: ~0.50. Combined: **P_deflated ≈ 0.32 for HARD_PASS** (with calibration penalty applied).

#### k-WTA Hebbian (depth)

**Mathematical form:**
- State: weight matrix `W[N=4096, D=encoder_dim]`, initialized random
- Per-atom-allocation step: compute `pre[i] = W[i] @ x_atom` for all i, select top-K
- Per-atom-write update: `W[i] += eta * x_atom` for i in top-K (substantively similar to Oja's rule with k-WTA mask)

**Brain analog:** Marr-Albus parallel-fiber-granule encoding with LTD. The top-K selection is the granule-cell sparsity; the Hebbian update is the parallel-fiber-Purkinje LTD.

**Why this might fail (HARD_FAIL risk):** the SoftHebb HARD_FAIL was on essentially this mechanism class (soft-WTA + Hebbian on weights). The prior result showed that at N=4096 with limited training data (text8 100K tokens / 4K vocab), weight-based learning does NOT outperform random initialization on substrate's noise-robustness discriminator. This is a substrate-physics fact, not a SoftHebb-specific bug.

**Why this might pass:** the prior cell tested at sigma=1.5 noise + Path-A BPC (encoder-side tests). The allocation-routing problem is DIFFERENT — we're measuring clustering purity not noise recall. Weight-based learning might help routing even if it doesn't help noise robustness. Substrate's chain-grade scope is much larger than text8 4K vocab too.

**P_deflated ≈ 0.20 for HARD_PASS** (calibration applies harder here because SoftHebb is a strong prior null).

### L4 — Cell design

Already laid out in CHEAP DECISIVE TEST section. Key design choices:

- **3 arms not 4-5:** budget discipline; if HARD_PASS on excitability, dispatch ablation as follow-up cell, not in same dispatch.
- **N=4096 / M=1000 / K=64:** match substrate production scope; sparsity ~1.5% (between Drosophila 5% and cerebellar 0.1%).
- **Use existing chain-grade KG for M1:** don't build a synthetic clustering benchmark; the v1 Director-lexical families are imperfect but available, and the relative ARI between arms is what matters (not absolute ARI).
- **No encoder retraining:** allocation routing is at the storage layer; use the existing `char_trigram_encoder.py` outputs unchanged. This is what makes the cell cheap.

### L5 — Cross-substrate composition

If HARD_PASS, the substrate gains a NEW primitive: `hdlab/allocation_trace.py`. Compositions:

- **substrate_self_map_v2f**: replace random allocation with excitability-trace in the v2e self-mapping pipeline. Predicted lift: the v2e degeneracy (REAL Q = SHUF Q at every gamma per recent research note) might be partially rescued because positions now carry semantic locality.
- **g1 generation**: route generation outputs through excitability-allocated positions so generated tokens preserve atom-semantic-locality.
- **Continual learning**: excitability-trace gives substrate-native "what's recently active" signal — composes with CLS-replay rate scheduling.
- **Hub-and-spoke encoder federation (per recent research_5x_deeper_path_c_universal_encoder)**: the atom-graph spoke can use excitability-trace; the text spoke can keep char-trigram. This is the cleanest composition path.

---

## CROSS-THREAD SYNTHESIS

- **META atom [[no-Hebbian-window]]**: prior null on Hebbian-window mechanisms. Excitability-trace is DIFFERENT — it operates on per-position activity counters, not on Hebbian time-windows between pre/post-synaptic events. Distinct mechanism class; the META does not close this path.
- **META atom [[by-construction-saturation]]**: random allocation at K=64/N=4096 IS the by-construction-saturated baseline for routing. The excitability-trace cell explicitly tests whether learned routing escapes this — if it doesn't (HARD_FAIL), the META extends to allocation-routing class.
- **META atom [[Shannon-floor]]**: applies at sigma=1.5 encoder-side noise. The allocation-routing cell tests at sigma=0.5 — well below the Shannon-floor regime. The two problems are decoupled.
- **Prior research_5x_deeper_substrate_self_mapping_gap_2026-06-23**: identified that v1 lexical families are imperfect ground truth (only ~10% of chain-grade atoms have labels) — accepted; M1 measures RELATIVE ARI between arms, not absolute, so the 10% ceiling does not invalidate the comparison.
- **Prior research_5x_deeper_encoder_upgrade_dual_gain_2026-06-23**: 4 forward-only encoders HARD_FAILed at sigma=1.5 cleanup. CRITICAL distinction: those were ENCODER-WEIGHT learning. This cell tests ALLOCATION-POSITION learning. Different layer, different mechanism class — prior result does not close this path.
- **Prior research_2x_revival_v2e_self_mapping_HF_2026-06-23**: REAL Q = SHUF Q at every gamma; encoder-bound diagnosis. Excitability-trace could partially rescue by adding semantic-locality to positions even with the same char-trigram encoder.
- **Recent research_5x_deeper_path_c_universal_encoder**: hub-and-spoke architecture. Allocation-trace is compatible with hub-and-spoke (operates at hub level on positions, agnostic to spoke encoder).

---

## SUBSTRATE-PRODUCT IMPLICATIONS

**HARD_PASS scenario (P=0.32):** substrate gets its first learned-routing primitive. This unblocks Phase-1 substrate self-mapping (the chain-grade self-mapping META was waiting on encoder rescue OR routing rescue; this provides the latter). It also gives substrate a path to Phase-2 autoatom: atoms that get allocated to similar positions are functionally similar, which is the substrate-native composability signal. Cost to ship: ~1 cycle cell + 1 cycle primitive lift (`hdlab/allocation_trace.py`) + 1 cycle compose-into-v2f. ~3 cycles total to a substrate primitive that lifts 3+ downstream capabilities.

**MIDDLE_BAND (P=0.30):** mechanism works partially; one of {alpha, T, K} matters. Follow-up: 4-cell ablation sweep. Substrate gains a tunable primitive but with parameter-discovery cost. ~5-7 cycles total.

**HARD_FAIL scenario (P=0.38):** substrate-native learned-routing at production scope is structurally null. This is BIG META information — it means random allocation is provably as good as learned (under our discriminator) at substrate's chain-grade scope. Pivot to backprop: single-linear-projection InfoNCE encoder, ~50K params, ~1-2hr CPU train. This is much LESS infrastructure than a full transformer; it's "just enough backprop" to get learned routing geometry. USER 2026-06-23 explicitly allowed this fallback.

**Substrate-product moat positioning:** if HARD_PASS, the substrate has a forward-only learned-routing primitive that DOES NOT EXIST in published HD/VSA literature (the search for "hyperdimensional computing learned sparse encoder forward-only" returned no direct precedent for excitability-trace-style position-learning). Combined with the existing chain-grade KG portfolio (FB15k-237 / ConceptNet / HotpotQA all chain-grade), substrate becomes the first VSA framework with substrate-native learned sparse routing — a defensible moat over MAP-C / FHRR / HRR baselines.

---

## HONEST ASSESSMENT — forward-only feasibility vs backprop requirement

**Forward-only IS feasible** for excitability-trace allocation: the mechanism requires only per-position scalar state + local activity-counter updates + Gumbel-top-K sampling. No global gradient signal. No backprop. The Tonegawa biology IS forward-only (CREB upregulation is a local cellular response, not a global error signal).

**Forward-only is HARDER** for weight-based learning (k-WTA Hebbian): the SoftHebb HARD_FAIL is direct empirical evidence at substrate's production scope. Hebbian weight updates without a global error signal converge slowly and to suboptimal weights at N=4096 with limited data. SoftHebb's published advantage (Moraitis 2021) was at small-image scope (MNIST, CIFAR) with strong inductive bias from convolution; that bias does not transfer to substrate's KG-routing problem.

**Backprop is required IF:** (a) excitability-trace HARD_FAILs AND (b) USER still wants substrate-native learned routing (i.e., doesn't want to settle for random allocation). The MINIMUM viable backprop infrastructure is a single linear projection `W: encoder_output → K-position-logits`, trained via InfoNCE contrastive loss on KG edges (positive pair = (atom, neighbor); negative pair = (atom, random non-neighbor)). ~50K-200K params depending on N and K. Training: ~1-2hr CPU on existing 200k-triple chain-grade KG. This is FAR less infrastructure than the char-LSTM (~5M params) mentioned in the prior encoder-upgrade drill — it's the smallest backprop encoder that solves the routing problem specifically.

**Critical caveat:** even with backprop, allocation routing is a DIFFERENT problem than encoder representation learning. The InfoNCE projection learns WHICH POSITIONS to allocate based on encoder-output similarity — it's a routing-layer learner, not a representation-layer learner. The prior MiniLM/BGE forbid (USER 2026-06-22) was on REPRESENTATION encoders; a routing-layer projection is a different category and likely USER-acceptable. Confirm with USER before dispatching backprop fallback if HARD_FAIL.

---

## CITATIONS (verified count: 18 — all from 5 parallel WebSearches this drill)

**Tonegawa engram allocation:**
1. Rao-Ruiz et al. 2021 (PMC8192335) — Dynamic and heterogeneous neural ensembles contribute to a memory engram
2. JNeurosci 2024 PMC11112642 — Intrinsic Neural Excitability Biases Allocation and Overlap of Memory Engrams
3. Cai et al. 2016 (Nature) — temporal proximity + shared excitability window
4. PMC12754038 — Writing the Engram: Epigenetic Mechanisms of Memory Allocation
5. Han et al. 2007 / Yiu et al. 2014 — CREB allocation foundational

**Dentate gyrus + adult neurogenesis:**
6. PMC3872742 — Adult neurogenesis modifies excitability of the dentate gyrus
7. PMC4542503 — Adult hippocampal neurogenesis and pattern separation via feedback inhibition
8. Springer 2024 s11571-024-10110-3 — Effect of adult hippocampal neurogenesis on pattern separation
9. bioRxiv 2023.01.12.523852 — Adult-born immature granule cells on pattern separation
10. Oxford Function zqaf035 — Degeneracy in interneuronal regulation of pattern separation

**Cerebellar Marr-Albus:**
11. eLife 82914 (Litwin-Kumar / Cayco-Gajic) — Task-dependent optimal representations for cerebellar learning
12. arXiv 2003.05647 — 50 years since the Marr, Ito, and Albus models of the cerebellum
13. Nature Sci Rep s41598-025-25727-5 — Computational model of cerebellar granular layer

**Drosophila MB Kenyon cells:**
14. eLife 56954 — Localized inhibition in the Drosophila mushroom body (APL sparseness)
15. Nature Sci Rep s41598-022-14413-5 — Learning-induced synaptic plasticity in MB γ-lobe
16. PMC4416108 — Activity of MBONs underlies learned olfactory behavior
17. PMC7028369 — Presynaptic developmental plasticity allows robust sparse wiring

**SoftHebb / forward-only Hebbian:**
18. arXiv 2107.05747 (Moraitis et al.) — SoftHebb: Bayesian inference in unsupervised Hebbian soft WTA networks
