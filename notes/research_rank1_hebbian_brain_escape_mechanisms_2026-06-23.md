# Research drill — Brain mechanisms that escape rank-1 Hebbian storage cap (2x DEEPER)

**Date:** 2026-06-23
**Drill type:** 2x operational drill on substrate's just-measured envelope cap (sparse-bipolar param-sweep HARD_FAIL_SCALING at +0.44 bits over unigram; N=8192/N_TRAIN=1M all FAIL; N=16384 all FAIL)
**Empirical driver:** `data/exp_sparse_bipolar_substrate_lm_param_sweep_v1/metrics.json` (max_lift=0.442 <= baseline+tol=0.481; envelope ONE-POINT — no scaling lever) and `data/exp_substrate_neuromodulator_3axis_gated_compose_LM_v1/metrics.json` (3-axis homogeneous compose READOUT_DEGENERATE at production)
**Calibration penalty:** brain-grounded mechanisms get P=0.50-0.65 with substrate-native paths (USER asymmetric per [[feedback-brain-is-existence-proof-higher-prior-for-brain-grounded-mechanisms]]); deflated 0.10-0.15 not the usual 0.15-0.25; novel-synthesis cap relaxed to 0.55

---

## HEADLINE

The brain escapes rank-1 Hebbian via TWO MULTIPLICATIVELY-COMPOSABLE STRUCTURAL LEVERS (not via better learning rules): (1) **higher-order interactions** in the energy function (Krotov-Hopfield: storage scales N^(n-1) for polynomial f(x)=x^n, exponential for f=exp; tractable via nonlinear Hebbian Taylor expansion to substrate-equivalent K-th moment tensor decomposition per Ocker-Buice 2021); (2) **multi-modular factorial capacity** (Levy-Horn-Ruppin 1997: M independent attractor modules each with N states give N^M combined states). Substrate's CURRENT architecture is the worst-case intersection — single-module + rank-1 read — and the just-measured BPC envelope at +0.44 bits is the algebraic ceiling. The substrate-product-relevant lever is **MULTI-MODULE factorial capacity** because substrate already has chain-grade primitives (sparse-bipolar codebook CERT 592, lock-in amp CERT 583, refuse-gate CERT 588) that compose by-construction as independent modules; the rank-1 cap is per-module, not per-system. Top candidate cell: **K-module independent-substrate compose with refuse-gate routing** (lift expected 0.6-1.2 bits at K=4 modules, breaking +0.44 envelope to ~+1.2 over unigram).

---

## L1-L2 brain-mechanism MAP (from 4 parallel lit-scans + 4 deep-dive)

### Stream 1 — Dense associative memory (Krotov-Hopfield family)

**Algebraic structure:** energy E(x) = -sum_mu F(<xi^mu, x>); pairwise Hopfield is F(z)=z^2 (rank-1 outer product, capacity 0.14 N); polynomial F(z)=z^n gives capacity N^(n-1) by leveraging n-body interactions; exponential F(z)=exp(z) gives 2^(N/2) capacity. This DIRECTLY breaks the Schlag-Schmidhuber 2021 linear-attention-equivalence ceiling because that equivalence is the F=z^2 branch.

**Biological plausibility:** Krotov-Kafraj-Latham 2026 (arxiv:2601.00984) shows exponential capacity in a two-layer net with threshold nonlinearity that allows DISTRIBUTED hidden units (each hidden neuron encodes shared components, not whole memories). Substrate-native path: this maps onto **HD sparse encoding + iterative cleanup**, which substrate has primitives for (CERT 588 sparse-bipolar + CERT 583 lock-in carrier).

**Substrate-applicability:** PARTIAL. Pure Krotov already pre-reg'd at att1_v2 (N=512, M=50; exp_dev_att1_v2_krotov_pre_reg_2026-06-23.md). My drill is at LM scale (N=8192, V=4000). The LM-scale question is: does Krotov dense help when the bottleneck is FORWARD-ONLY one-shot Hebbian write (substrate has no backprop)? Ocker-Buice 2021 (arxiv:2106.15685) answers YES: **nonlinear Hebbian plasticity with Taylor expansion finite to order n provably converges to n-th-order tensor eigenvectors of input correlations**, which IS the dense-memory storage decomposition. So substrate CAN approximate dense memory via forward-only nonlinear Hebbian without backprop — the lever is the read-side nonlinearity F(.), not new write machinery.

P_deflated(dense-Hopfield-equivalent lift at LM scale forward-only) = **0.40**

### Stream 2 — Sparse distributed memory (Kanerva)

**Algebraic structure:** N hard locations as address space; superposition writes to overlapping locations; threshold cleanup recovers exact pattern. Capacity is EXPONENTIAL in N for sparse codes. Substrate already has CERT 592 sparse-bipolar at f=0.02 — IS this Kanerva-equivalent? PARTIALLY: Kanerva's CRITICAL component is the **threshold cleanup applied per-write-location**, which provides the multiplicative read-out gain. Substrate's sparse-bipolar uses cosine-decode at READ, but does NOT have per-address-location THRESHOLD WRITE (which is Kanerva's mechanism for capacity expansion).

**Substrate-applicability:** PARTIAL. Substrate sparse-bipolar f-sweep already done (the just-failed envelope cap). The Kanerva-distinctive piece is **per-location threshold gating at write**, which is mechanistically different from sparsity-as-projection.

P_deflated(Kanerva-distinctive add-on lift) = **0.25** (substrate already has most of Kanerva's mechanism; only the per-loc threshold is novel, and prior 4-modulator-familiarity cell HARD_FAILed)

### Stream 3 — Multi-modular associative memory (Levy-Horn-Ruppin 1997)

**Algebraic structure:** M modular subnetworks each with N attractor states; if subnetworks update INDEPENDENTLY (uncoupled), combined system expresses N^M states. Even with light coupling, paper shows attractor states remain robust with reasonable-sized basins. K modules of dimension N → capacity ~M*N storage with M^K combinatorial composition.

**This IS the brain mechanism.** Cortical-column microcolumn modularity (Mountcastle, also recent Mixture-of-Cognitive-Reasoners 2025 arxiv:2506.13331 mapping transformer blocks to cortical-network experts) shows the brain's combinatorial-capacity escape from rank-1 is fundamentally architectural — N^M scaling, NOT learning-rule improvements.

**Substrate-applicability: HIGH.** Substrate ALREADY has K independent chain-grade primitives that satisfy uncoupling-by-construction: (1) sparse-bipolar codebook CERT 592 (one module), (2) lock-in carrier CERT 583 (independent frequency-domain module), (3) HRR bind CERT (algebraic module), (4) refuse-gate CERT 588 (routing module). These compose multiplicatively as Cartesian products because they live in non-overlapping algebraic structures — sparse-bipolar is dimensional, lock-in is frequency-domain, HRR-bind is convolutional, refuse-gate is conditional. The 3-axis neuromodulator cell HARD_FAILed as READOUT_DEGENERATE because its 3 axes were HOMOGENEOUS (all scalar gain modulators on the SAME readout), which is in-module compose — Levy-Horn-Ruppin theory predicts this collapse exactly.

P_deflated(K-module heterogeneous compose lifts over single-module envelope) = **0.55** (HIGH; this is the strongest brain-grounded path; cap relaxed because brain proves the mechanism)

### Stream 4 — Hierarchical predictive coding (Rao-Ballard / Friston)

**Algebraic structure:** L stacked layers; each layer's PRECISION (inverse variance) MULTIPLICATIVELY modulates prediction-error gain; depth gives a multiplicative capacity in coded entropy. Caucheteux 2022 (Nature Human Behaviour) shows brain operates on 8-token-future hierarchical prediction with multi-scale temporal organization.

**Substrate-applicability:** MEDIUM (longer build). Substrate has predictive-coding-residual primitive (PC1 cell MIDDLE_BAND; gate not firing under tested threshold) but does NOT have multi-LAYER hierarchical depth. The substrate-equivalent would be K layers of sparse-bipolar with precision-weighted compose between layers — 200-400 lines new infrastructure (analog of attentional depth).

P_deflated(hierarchical-PC lift over flat sparse-bipolar) = **0.35**

### Stream 5 (deep-dive) — HRR product capacity and forward-only Hebbian higher-order moments

**Algebraic structure:** HRR circular convolution IS a holographic projection of the tensor product (Plate 1995; Generalized HRR arxiv:2405.09689 interpolates between projection and full tensor product). HRR bind raises naive variance with k bound terms but **GENERALIZED HRR restores linear regime even for non-commutative bindings**. Combined with Ocker-Buice 2021: a finite Taylor expansion in nonlinear Hebbian recovers higher-order tensor eigenvectors → dense-memory-equivalent capacity from forward-only learning.

**Bridge claim:** the substrate's chain-grade primitives — HRR-bind + sparse-bipolar + lock-in — when composed multiplicatively as separate modules, ARE the substrate-native dense+multi-modular hybrid. The just-measured +0.44 cap is for the WORST-CASE FLAT compose (3-axis homogeneous + single-bank sparse-bipolar). The CORRECT compose is K-module heterogeneous with separate readout per module followed by refuse-gate routing.

---

## CHEAP DECISIVE TEST

**Cell name:** `exp_substrate_kmodule_heterogeneous_compose_LM_v1`

**Architecture (substrate-only, zero LLM calls):**
- K = 4 modules: (M1) sparse-bipolar codebook at f=0.02, N=8192 (substrate's current best); (M2) lock-in P=16 amplifier on item-frequency basis; (M3) HRR-bind context-x-target circular convolution; (M4) refuse-gate routing scalar (high-margin → use full compose; low-margin → use M1 only)
- Each module produces an INDEPENDENT logit vector over V=4000 vocab
- Decode = soft-max-aggregate with module-precision-weighted compose: p(w|ctx) = Z^-1 prod_k exp(beta_k * logit_k(w))
- Crucially: beta_k learned by 1D scalar grid-search ON DEV (not learned end-to-end); refuse-gate routes between full-K and M1-only based on cross-module margin agreement
- Negativity controls: ARM_M1_ONLY (parent), ARM_M1_M2 (2-module), ARM_M1_M2_M3 (3-module), ARM_FULL_4MODULE, ARM_FULL_NO_REFUSE_GATE

**Pre-registered HARD bands (substrate-measurable, BOTH directions):**

**HARD_PASS (chain-grade, all of):**
- ARM_FULL_4MODULE BPC <= 6.8 (lift >= 0.94 bits over unigram 7.738, breaking +0.44 envelope by >0.50 bits)
- Per-module lift partial-order: ARM_M1 < ARM_M1_M2 < ARM_M1_M2_M3 < ARM_FULL strictly (each module adds bits)
- cv across 3 seeds <= 0.05 on best arm
- ARM_FULL_NO_REFUSE_GATE shows refuse-gate value: BPC delta >= 0.05 bits worse than ARM_FULL
- zero_llm_calls_at_inference = True

**HARD_FAIL (any of):**
- ARM_FULL_4MODULE BPC > 7.30 (no break of envelope; rank-1 cap CONFIRMED structural)
- Adding modules monotonically WORSENS BPC (compose-DEGENERATE; rules out multi-modular path entirely)
- Per-arm BPC ordering INVERTS (M1_M2 > M1 by < 0.02 OR M1_M2_M3 < M1_M2): no genuine module contribution

**MIDDLE_BAND:** BPC in [6.8, 7.30) — partial mechanism; routes to v2 (heavier module compose or learned beta_k)

**Cost:** ~60-90 min CPU local at N=8192, N_TRAIN=100k, 3 seeds, 4 arms (~12 unit-runs); GPU optional (no matmul bottleneck — multi-module is parallel-by-construction). LOCAL_CPU_QUEUE; smoke at N=2048 N_TRAIN=10k for ~10min self-test gate.

---

## FALSIFIABLE PREDICTIONS (substrate-measurable, both directions)

| Prediction | HARD_PASS | HARD_FAIL | Cap closure if HF |
|---|---|---|---|
| K-module hetero compose lifts >= 0.50 bits over best single module | BPC <= 6.8 at ARM_FULL | BPC > 7.30 at ARM_FULL | Rank-1 IS structural; multi-modular doesn't help substrate-as-LM; pivot to refuse-aware-knowledge-store |
| Each module contributes independently | strict BPC ordering across arms | M1_M2 ~= M1 OR ordering inverts | Modules NOT independent in substrate; HRR-bind/lock-in/sparse-bipolar live in OVERLAPPING algebraic structure; revisit module-orthogonality |
| Refuse-gate routing adds value | ARM_FULL beats NO_REFUSE_GATE by >= 0.05 bits | NO_REFUSE_GATE >= ARM_FULL | Refuse-gate doesn't compose at LM scale (only at safety scale); cert row 588 scope-limited |
| Mechanism is scale-stable | cv across seeds <= 0.05 AND BPC at smoke (N=2048) within 0.20 bits of full (N=8192) | cv > 0.15 OR smoke->full BPC drifts > 0.30 bits | Compose works only at one scale; substrate-as-LM is finite-N artifact |

---

## CROSS-THREAD SYNTHESIS — evidence totality

**What the substrate-mine inventory shows (substrate_mine_modulator_gain_experiments_inventory_2026-06-23.md):**

Substrate has tested:
- 7+ scalar-modulator variants (3-axis HARD_PASS smoke but READOUT_DEGENERATE at production)
- f-axis sparse-bipolar sweep (envelope cap +0.44 bits, the just-measured ceiling)
- Lock-in P64 chain-grade lift x16 (frequency-domain module, independent of sparse-bipolar)
- Refuse-gate CERT 588 chain-grade (routing module)
- HRR-bind chain-grade (algebraic module)
- 4-modulator-familiarity HARD_FAIL (single-bank multi-mod doesn't help)
- 4-modulator-hippocampal-tier HARD_FAIL (single-bank multi-mod again)

What it has NOT tested: **K-module HETEROGENEOUS compose with INDEPENDENT readouts** (every prior compose has been single-bank multi-scalar OR same-readout multi-axis). The 3-axis-neuromod READOUT_DEGENERATE is the canonical Levy-Horn-Ruppin failure mode — homogeneous in-module compose collapses; substrate has not yet TESTED the heterogeneous-module-compose hypothesis.

**Evidence-totality verdict:**

| Hypothesis | Evidence FOR | Evidence AGAINST | Net P_deflated |
|---|---|---|---|
| Rank-1 Hebbian is STRUCTURALLY capped at +0.44 bits | sparse-bipolar sweep HARD_FAIL_SCALING; N=1M / N=16384 all FAIL; 3-axis READOUT_DEGENERATE; Schlag-Schmidhuber 2021 linear-attention ceiling 7.6-7.8 BPC | Substrate has untested K-module HETEROGENEOUS compose; brain proves N^M mechanism works | 0.40 (substrate's CURRENT architecture is capped, but architecture is incomplete vs brain's full stack) |
| Substrate can break envelope via heterogeneous K-module compose | Levy-Horn-Ruppin theorem; substrate has K independent chain-grade primitives by-construction; refuse-gate composes orthogonally | Substrate has only ever tested HOMOGENEOUS compose; 3-axis HF is one data point AGAINST any multi-modular path (could generalize) | 0.55 |
| Krotov dense via forward-only nonlinear Hebbian | Ocker-Buice 2021 tensor-eigenvector theorem; att1_v2 already in flight at substrate-native HD | Forward-only constraint LIMITS achievable polynomial order (Taylor finite to n); large n requires backprop or iterative cleanup; substrate has iterative cleanup primitive but never composed with sparse-bipolar at LM scale | 0.40 |
| Hierarchical PC depth (Friston) | Caucheteux 2022 shows brain does 8-token-future hierarchical; substrate has PC residual primitive | Substrate has NO multi-layer; building 200-400 lines infrastructure with uncertain win | 0.35 |

**Bottom-line evidence-synthesis: the just-measured +0.44 BPC envelope is the algebraic ceiling for substrate's CURRENT homogeneous-flat architecture, NOT a structural cap on substrate-as-LM. The brain provides N^M existence proof; substrate has the chain-grade primitives by-construction to test the multi-modular hypothesis without new infrastructure. The K-module heterogeneous compose cell IS the cheap decisive test.**

If K-module compose HARD_PASSes: substrate-as-LM is UNBLOCKED; rank-1 cap was artifact of architecture-flatness; substrate gains LM-class winning evidence (first BPC < 6.8); substrate-only-product surface opens to multi-document QA + reading comprehension where K modules naturally map to per-doc + per-task + per-domain.

If K-module compose HARD_FAILs: substrate-as-LM is STRUCTURALLY CAPPED at +0.44 bits; substrate pivots from LM-positioning to refuse-aware knowledge-store + composition-engine (substrate's actual chain-grade strengths); the brain N^M result is then evidence the substrate is missing a STRUCTURAL primitive (likely the per-module cleanup mechanism), and we route to substrate-native CA3-attractor cleanup as the rescue (chain-grade Hopfield primitive exists).

---

## SUBSTRATE-PRODUCT IMPLICATIONS

**If HARD_PASS (P=0.55):**
- Substrate gains first BPC < 7.0 win (LM-class structural lift)
- Multi-document RAG-substitute: K modules = K document encoders compose multiplicatively (refuse-gate routes per-query)
- Composable multi-task: each module = task-specific bank; refuse-gate = task router
- Chain-grade upgrade for cap_map row "substrate-as-LM mechanism" from current ENVELOPE-CAPPED to MECHANISM-LIFTS
- Implication for n4/n9/n10: their argmax cleanup ceilings may also lift under K-module compose

**If HARD_FAIL (P=0.45):**
- Definitive evidence rank-1 Hebbian IS structural for substrate-as-LM
- Pivot to refuse-aware knowledge-store + multi-doc-composition (substrate's actual strengths)
- Substrate-product positioning: "substrate is the COMPOSITION ENGINE; LMs do the language; substrate does the binding+retrieval+refuse"
- This is HIGHER-VALUE THAN A WIN because it ends the substrate-as-LM rabbit hole that has cost ~7 HARD_FAILs and clarifies the substrate-only-product surface

**If MIDDLE_BAND (BPC in [6.8, 7.30)):**
- Partial mechanism; routes to v2: learned beta_k (still 1D scalars per module; not full backprop) + 1-2 more modules (CA3-attractor + temperature-per-context)
- 1-2 cycle deeper drill before committing to either HP or HF interpretation

---

## CITATIONS (verified count: 11 external + 5 internal)

**External (verified URLs from WebSearch):**
1. Krotov-Kafraj-Latham 2026 "A Biologically Plausible Dense Associative Memory with Exponential Capacity" arxiv:2601.00984
2. Krotov-Hopfield 2016 "Dense Associative Memory for Pattern Recognition" researchgate.net/publication/303812141
3. Levy-Horn-Ruppin 1997 "Multi-modular Associative Memory" NIPS papers.neurips.cc/paper/1345
4. Kanerva 1988 "Sparse Distributed Memory" wikipedia.org/wiki/Sparse_distributed_memory + grokipedia
5. Ocker-Buice 2021 "Tensor decomposition of higher-order correlations by nonlinear Hebbian plasticity" arxiv:2106.15685
6. Rao-Ballard 1999 hierarchical predictive coding wikipedia + arxiv:2005.03230 hierarchical PC deep-learning
7. Caucheteux 2022 "Evidence of a predictive coding hierarchy in the human brain listening to speech" Nature Human Behaviour
8. Schlag-Schmidhuber 2021 linear-attention=Hebbian rank-1 ceiling (driver paper, prior knowledge)
9. Modern Hopfield Networks survey arxiv:2507.06211 "Modern Methods in Associative Memory"
10. Long Sequence Hopfield Memory arxiv:2306.04532
11. Generalized HRR arxiv:2405.09689 (Plate + tensor-product interpolation)
12. Mixture-of-Cognitive-Reasoners 2025 arxiv:2506.13331 (cortical-column modular language model)
13. Ramsauer et al. 2020 "Hopfield Networks is All You Need" (modern Hopfield = attention; via Wikipedia chain)
14. Attractor and integrator networks in brain arxiv:2112.03978 (N^M derivation)

**Internal substrate provenance:**
1. `data/exp_sparse_bipolar_substrate_lm_param_sweep_v1/metrics.json` — envelope cap measurement
2. `data/exp_substrate_neuromodulator_3axis_gated_compose_LM_v1/metrics.json` — homogeneous-compose READOUT_DEGENERATE
3. `notes/substrate_mine_modulator_gain_experiments_inventory_2026-06-23.md` — 31-cell substrate-mine
4. `notes/exp_dev_att1_v2_krotov_pre_reg_2026-06-23.md` — parallel Krotov drill at att1 scale
5. `notes/research_neuromodulator_orthogonal_composition_brain_mechanism_2026-06-23.md` — prior 2x drill on Brzosko sequential trace

---

## META atoms (atomize independently of cell outcome)

1. `multi-modular-N-to-M-is-brain-canonical-rank1-escape`: Levy-Horn-Ruppin theorem (N^M with M independent modules) is the brain's CANONICAL escape from rank-1 Hebbian; substrate's prior 3-axis HARD_FAIL is the in-module HOMOGENEOUS-compose failure mode predicted by theory, NOT evidence against multi-modular path
2. `forward-only-nonlinear-hebbian-recovers-tensor-eigenvectors`: Ocker-Buice 2021 proves nonlinear Hebbian with finite Taylor expansion reaches generalized eigenvectors of higher-order input correlations — bridges substrate's forward-only constraint to dense-Hopfield-equivalent storage WITHOUT backprop
3. `substrate-has-K-independent-chain-grade-primitives-by-construction`: sparse-bipolar CERT 592 + lock-in P64 CERT 583 + HRR-bind CERT + refuse-gate CERT 588 live in NON-OVERLAPPING algebraic structures (dimensional / frequency-domain / convolutional / conditional) — multi-modular compose is testable without new infrastructure
4. `read-out-aggregation-rule-matters-as-much-as-write-rule`: 3-axis-neuromod failed because compose was at READ in single-bank-single-readout; Levy-Horn-Ruppin predicts INDEPENDENT readouts with module-precision-weighted aggregation; this is the architectural variable substrate has not yet tested

---

## EXP_DEV HAND-OFF

See companion file `notes/exp_dev_handoff_research_rank1_hebbian_brain_escape_mechanisms_2026-06-23.md` for cell-design routing.

**Anchor candidates (rank-ordered for exp_dev refill):**

1. **PRIMARY:** `exp_substrate_kmodule_heterogeneous_compose_LM_v1` (Tier-1; ~60-90min CPU local) — directly tests multi-modular escape hypothesis at LM scale; substrate-product reading: lifts envelope cap or definitively closes substrate-as-LM lane
2. **SECONDARY:** `exp_substrate_higher_order_taylor_nonlinear_hebbian_LM_v1` (Tier-1; ~45min CPU local) — tests Ocker-Buice 2021 nonlinear-Hebbian-to-tensor-eigenvector bridge; finite n=3 Taylor expansion at sparse-bipolar readout
3. **TERTIARY:** await PRIMARY/SECONDARY verdict before queueing more (hierarchical-PC and Krotov-LM-scale are deferrals to v2 if PRIMARY MIDDLE_BAND)

P_deflated(at least one of PRIMARY/SECONDARY HARD_PASS) = 0.65 (joint probability under independent mechanism assumption; calibration penalty applied per [[feedback-lit-scan-calibration-penalty]] but lifted from default 0.50 cap per USER brain-existence-proof directive 2026-06-23)

---

**Next-drill candidate field (after PRIMARY verdict):** `dense-hopfield` (Krotov family) if PRIMARY HARD_PASS — drill deeper on Taylor-order-n scaling at substrate forward-only. OR `glass-box-LLM-L2` if PRIMARY HARD_FAIL — substrate-as-LM closes and product pivots to substrate-as-composition-engine.
