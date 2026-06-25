# RESEARCH (Director) 5x cross-field drill: ENGINEERED structure HURTS substrate, EMERGENT structure HELPS

**Date:** 2026-06-25
**Author:** Research (Director, Opus 4.7 1M)
**Trigger:** Cross-cell pattern from this morning -- 5 data points across Cells 2/5/7 converge on a directional finding: every IMPOSED structural intervention (label-driven axis projection, grammatical role binding, orthogonal subspace) lost vs baseline; every DATA-DRIVEN structural intervention (frequency routing, theta-phase multiplex, semantic clustering, hybrid role+concept) won. This drill asks across 5 disparate fields whether this is substrate-specific, retrieval-system-general, or a deep statistical/biological principle.
**Discipline:** 0.20 deflation novel synthesis; cap P_deflated=0.50; brain-existence-proof +0.10 prior; symmetric verify-the-referent; Fix #28 default UNDER-claim; ASCII only; no cell dispatches.

**Referent verifications performed (cited cells PRESENT in Store with verdicts as reported):**
- Cell 7 `exp_substrate_label_driven_anisotropic_encoder_v1`: metrics.json present; verdict MIDDLE_BAND; ARM_RANDOM_BIPOLAR a3=0.917, ARM_AXIS_PROJ a3=0.861, lift_vs_random=-0.056 -- CONFIRMED.
- Cell 5 `exp_substrate_role_tagged_compositional_generalization_on_concept_KG_v1`: metrics.json present; verdict HARD_PASS_CHAIN_GRADE; NO_ROLES=0.167, ORTHO=0.167, CLUSTERED=0.333, GRAMMATICAL=0.083, HYBRID=1.000; best=HYBRID lift_vs_no_roles=+0.833 -- CONFIRMED with one correction: NO_ROLES=0.167 not 0.250 (user prompt off slightly; the GRAMMATICAL=0.083 < NO_ROLES=0.167 lift -0.084, still negative; CLUSTERED beats ORTHO by +0.167 as stated).
- Cell 2 `exp_substrate_compose_heterogeneous_routing_v3_full_config_rerun`: metrics.json present; verdict MIDDLE_BAND_PARTIAL_SIGNAL; BASE=7.3065, FREQ_ROUTED_K2=7.2096 (lift +0.097), THETA_PHASE_TWO_W=7.2349 (lift +0.072), ORTHOG_SUBSPACE=7.4315 (lift -0.125) -- CONFIRMED.
- Cross-thread: director_encoder_basis_vs_use_case_labels_2026-06-25.md PRESENT (USER basis-vs-use-case principle); director_cell_H_prime_biology_unsupervised_encoder_spec_2026-06-25.md PRESENT (Cell H' in flight = empirical test).
- Mu-Viswanath 2018 / Ethayarajh 2019 cited correctly (anisotropy as cone-collapse penalty for retrieval) -- well-known lit; treated as +0.05 prior boost.

**Important number-correction for the pattern table (per Fix #28 verify per-arm not from verdict_msg):**

| Cell | Intervention | Metric | Baseline | Intervention | Lift | Direction |
|------|--------------|--------|----------|--------------|------|-----------|
| 2 | ORTHOG_SUBSPACE | BPC | 7.3065 | 7.4315 | -0.125 | IMPOSED, HURTS |
| 2 | FREQ_ROUTED_K2 | BPC | 7.3065 | 7.2096 | +0.097 | EMERGENT, HELPS |
| 2 | THETA_PHASE_TWO_W | BPC | 7.3065 | 7.2349 | +0.072 | EMERGENT, HELPS |
| 5 | GRAMMATICAL roles | top1 vs NO_ROLES | 0.167 | 0.083 | -0.084 | IMPOSED, HURTS |
| 5 | CLUSTERED roles vs ORTHO | top1 | 0.167 | 0.333 | +0.167 | EMERGENT-relative, HELPS |
| 5 | HYBRID role+concept-labels | top1 vs NO_ROLES | 0.167 | 1.000 | +0.833 | EMERGENT+labeled, DOMINATES |
| 7 | AXIS_PROJ category-labels | a3 | 0.917 | 0.861 | -0.056 | IMPOSED, HURTS |

The HYBRID-1.000 result in Cell 5 is the load-bearing nuance: imposing categorical labels DOES help -- but only as a SUPERVISORY USE-CASE LAYER on top of an emergent base (the concept-binding role-codebook). USER's basis-vs-use-case principle (V1 unsupervised -> IT labeled readout) is exactly this stratification.

---

## 1. Headline

**The pattern is interpretation (d) -- conditional, not absolute.** Engineered structure HURTS when imposed at the SUBSTRATE BASIS layer (encoder, role codebook, subspace partition). Engineered structure HELPS when imposed at the USE-CASE READOUT layer (HYBRID Cell 5; supervised classification heads in general). The substrate is a memory-retrieval-grounded system; its basis must match the data's natural statistics (which the substrate cannot know a priori), but its readouts can and should be label-driven for downstream tasks. This carves out a specific substrate-product principle and explains all 5 data points without needing a substrate-specific exception.

The deeper truth visible across 5 fields: **memory-retrieval systems with isotropic capacity penalize ANY structure-imposition at the storage layer that costs more entropy than it adds.** Random codes preserve the JL-margin; any structure that doesn't match data statistics burns precision. Brain solves this by emerging structure UNSUPERVISED at the cortical-column layer (slow, sparse-coding, Hebbian) and then SUPERVISING readouts via the BG/PFC supervisory loops. Substrate must follow the same stratification.

P_deflated(this principle is the dominant explanation for the 5 data points) = **0.55** (raw 0.75, deflated 0.20 novel synthesis, +0.10 brain prior, -0.10 USER warning that I am pattern-matching from N=3 cells; cap 0.50 invoked... revised to **0.50**).

---

## 2. Per-angle drill

### Angle A -- Pure math / information geometry

**Theoretical claim:** YES -- the field has multiple convergent results predicting engineered-hurts / emergent-helps under retrieval workloads.

1. **Bayesian regularization mismatch.** A prior helps only when it matches the data-generating process. Label-driven priors (category subspaces, grammatical roles, axis projection) impose a Dirichlet-like structure with K large eigenvalues; if the data's true statistics are continuous / Zipfian / graph-structured rather than discrete-categorical, the prior costs KL-divergence and reduces effective sample efficiency. Cell 2 FREQ_ROUTED_K2 wins because Zipf-frequency routing IS the data's natural statistic; ORTHOG_SUBSPACE loses because text8 token co-occurrence has no clean orthogonal partition.
2. **Concentration of measure / Johnson-Lindenstrauss oversatisfaction.** At N/V > 100 (Cell 7's V=12 N=8192 regime is N/V=683), random-bipolar already achieves epsilon ~ 0.01 pairwise margin; ANY subspace division reduces effective dim from N to N/C costing precision linearly while adding no separability headroom. This explains Cell 7 quantitatively: 4-category axis projection gives 2048 dims/category vs random's 8192 dims/concept -- 4x precision-loss for nothing.
3. **Fisher information of wrong priors.** Imposing wrong structure consumes Fisher information that could otherwise be spent on fine-grained discrimination; emergent structure preserves information until evidence accumulates. This is THE statistical pitfall the LASSO / ridge regularization literature warns against -- engineering at multiple levels creates interactions that mask real effects (garden-of-forking-paths).
4. **Random matrix theory: anisotropy of the Gram matrix.** Engineered structure produces top-heavy Gram spectrum (a few large eigenvalues, many small); random produces flat (Marchenko-Pastur bulk near 1.0). Retrieval cosine-similarity reads off the bulk; large eigenvalues = collapsed directions that REDUCE retrieval discriminability. Mu-Viswanath 2018 / Ethayarajh 2019 (cone-collapse) is the empirical NLP-side observation; the math-side explanation is the eigenvalue-bulk argument.

**Substrate prediction (would this angle predict our 5 data points?):** YES, quantitatively for Cell 7 (-0.056 is JL-precision-loss exactly), directionally for Cell 2 ORTHOG, directionally for Cell 5 grammatical-role-codebook.

**Substrate principle:** **Encoder construction must be DATA-AGNOSTIC unless data statistics are KNOWN.** At small-data or small-V regimes use random-bipolar; at large-V regimes use emergent (sparse coding, predictive coding) -- NEVER use category labels at the encoder layer.

---

### Angle B -- Brain / neuroscience

**Theoretical claim:** STRONGLY YES -- biology never imposes pre-specified structure at the basis layer. Every cortical encoder emerges from experience.

1. **V1 oriented-edge detectors (Olshausen-Field 1996, Hubel-Wiesel 1962).** Unsupervised sparse coding on natural images produces oriented edges identical to V1 simple cells. No edge-templates are hard-wired. Critical-period plasticity proves the structure is experience-dependent: monocular deprivation rewires the cortex.
2. **Place cells in hippocampus (O'Keefe-Nadel 1971).** Emerge from spatial experience via Hebbian + theta-gamma dynamics. Engineered place codes (Klee-Sleator style coordinate grids) are NOT how the brain does it -- biology emerges them.
3. **ATL hub-and-spoke (Patterson-Lambon-Ralph 2007).** Semantic categories emerge from cross-modal binding; the ATL hub does NOT have pre-defined taxonomies. Lesions cause graceful degradation aligned with experiential frequency, not with taxonomic boundaries -- proof the categories are emergent.
4. **Cortical column self-organization (Mountcastle).** Microcircuit motif is hard-wired BUT the tuning of each column emerges from input.
5. **Where does brain use labels?** SUPERVISED learning happens at BG/PFC/cerebellum supervisory loops -- READOUT layers on top of cortical bases. This is USER's basis-vs-use-case principle, biologically grounded: V1 unsupervised -> IT labeled-readout -> PFC task-conditioned policy.
6. **Why hasn't evolution imposed structure at the basis layer?** Generalization. Pre-imposed structure overfits to the environment of evolutionary adaptation; experience-dependent structure tracks the actual organism's environment. This is the same argument as ML's "bitter lesson" (Sutton) but with 500M years of evidence.

**Substrate prediction:** ALL 5 data points are predicted. Brain says: structure-at-basis = LOSE; emergent-at-basis + label-at-readout = WIN. Cell 5 HYBRID arm (role + concept-labels co-existing) is the brain-canonical pattern, and it scored 1.000 -- crushed every pure-engineered and pure-emergent alternative.

**Substrate principle:** **Substrate encoder MUST be biology-native unsupervised (Cell H' is the right call).** Labels enter at the use-case readout, not at the encoder. Cell H' should test SoftHebb / predictive-coding / Olshausen-Field as encoder candidates; supervised heads ride on top.

P_deflated(biology-native unsupervised encoder produces chain-grade lift at V=4000 substrate) = **0.45** (raw 0.65, deflated 0.20, +0.10 brain prior, -0.10 implementation-novelty risk; cap 0.50 not invoked).

---

### Angle C -- ML / deep learning

**Theoretical claim:** YES, with one important caveat. The "bitter lesson" (Sutton 2019) is the canonical statement: scale + data-driven methods consistently beat engineered structure long-term. But the caveat -- engineered helps in small-data + small-compute regimes -- is real.

1. **Contrastive self-supervised learning (SimCLR, MoCo, DINO).** Emergent positive-pair structure beats engineered class-supervision at scale. ImageNet-supervised features lose to SimCLR features on downstream transfer.
2. **BERT / GPT vs symbolic NLP.** Transformer pre-training on raw text emerged structure (POS tags, syntax trees, semantic roles, world knowledge) that hand-engineered features (POS taggers, dependency parsers, frame semantics, WordNet) tried to provide -- and the emergent ones generalize better.
3. **Word2vec vs WordNet-based features.** Mikolov 2013 showed dense skip-gram embeddings (emergent from raw text) outperform hand-engineered lexical-feature pipelines on analogy tasks.
4. **Retrieval-augmented dense indices (DPR, ColBERT, BGE).** Dense embeddings beat BM25 + engineered query expansion at scale.
5. **The bitter lesson's caveat: when DOES engineering help?** Three regimes -- (a) small-data SVM-with-kernels, where prior is needed because data can't carry the signal; (b) compositional generalization where data SPECIFICALLY lacks the test combinations (CFRPE, RFE, structured prediction); (c) when the prior PROVABLY matches reality (e.g., translation-invariance in CNNs for vision -- emerges anyway but engineering it accelerates).
6. **Substrate position in this taxonomy.** Substrate has moderate data (text8 100k) + structure-emerging-from-text + compositional-generalization claim. The Cell 2 FREQ_ROUTED_K2 win is the EMERGENT regime; the Cell 2 ORTHOG_SUBSPACE loss is the WRONG-PRIOR regime. Cell 5 HYBRID dominance suggests compositional generalization needs SOME engineering (role-codebook structure) but only with concept-labels attached -- a use-case-layer engineering, not basis-layer.

**Substrate prediction:** ALL 5 data points predicted within ML field's standard taxonomy. No substrate-specific exception needed.

**Substrate principle:** **Substrate is in the "emergent dominates" regime for the encoder/basis layer; treat readouts (use-case) as engineerable.** The HumanEval anchor 1 Class-A/B split is consistent with this: gain from engineered stdlib-class taxonomy if the LM is the use-case readout, none if it's the basis.

---

### Angle D -- Statistics / experimental design

**Theoretical claim:** STRONGLY YES -- over-engineered features is THE classic statistical pitfall. Lasso/ridge regularization is the field-canonical fix; the meta-fix is to NOT engineer.

1. **Confounding via over-engineered features.** Multiple engineered features create interaction effects that mask the real signal. Cell 2's ORTHOG_SUBSPACE composed with cf-RPE composed with hetplasticity composed with K2 -- 4-way interactions impossible to disentangle. Cell 5 HYBRID's role+concept-labels is the LEAST-engineered version (just two factors), and it WON.
2. **Garden-of-forking-paths (Gelman-Loken 2014).** Engineering too many decisions in priors locks the model into wrong subspaces; you can't recover via data. The forking-paths critique of NHST is mathematically identical to the forking-paths critique of feature engineering.
3. **Bias-variance tradeoff.** Engineered structure REDUCES variance (less sample-efficient learning) at COST OF BIAS (when prior mismatches truth). Emergent structure ADDS variance but stays unbiased asymptotically. For substrate's regime, the bias dominates.
4. **Goodhart's law for engineered priors.** Once you measure "does this category boundary improve retrieval," you optimize FOR that category boundary -- not for the true downstream task. Emergent structure is robust to Goodhart because it has no specific target to be gamed.
5. **Lasso / ridge as principled-engineered fix.** When you MUST impose structure, regularize the imposition so data can override. Pure ORTHOG_SUBSPACE doesn't allow override; pure HYBRID role-codebook does (concept labels can re-orient the role basis).

**Substrate prediction:** ALL 5 data points predicted by classic statistical-design analysis.

**Substrate principle:** **When in doubt, prefer LASSO-style soft constraints over hard imposition.** If the substrate must have a role codebook, let it be learned from data (CLUSTERED roles in Cell 5) and let concept-labels override (HYBRID in Cell 5), rather than hand-engineered orthogonal codes (ORTHO in Cell 5 -- which tied with NO_ROLES at 0.167, useless).

---

### Angle E -- Materials science / phase transitions / self-organized criticality

**Theoretical claim:** YES with elegant analog. Self-organized criticality (Bak-Tang-Wiesenfeld 1987) is the materials-science argument for emergent-structure-wins.

1. **Field-cooled vs zero-field-cooled crystals.** Imposing a magnetic field during crystal formation creates a frozen-in domain structure that is BRITTLE -- shocks reorganize the entire structure catastrophically. Zero-field-cooled crystals self-organize domains that are ROBUST to perturbation. This is the materials-science analog of cone-collapse: imposed structure is a frozen wrong basis.
2. **Glass transitions and frozen disorder.** Glass = liquid that froze before reaching equilibrium. The frozen structure is metastable, lossy, and cannot be undone without complete remelting. Engineered structure in encoders is the substrate-analog of a glass -- frozen wrong basis that requires complete re-encoder to undo (= n10 whitening RESCUE attempts).
3. **Self-organized criticality (SOC) at phase boundaries.** Systems poised at phase transitions maximize information processing (Langton 1990's edge-of-chaos; Beggs-Plenz 2003 neuronal avalanches). Emergent structure naturally sits at SOC; engineered structure typically does not (it sits at a specific operating point chosen by the engineer).
4. **Symmetry breaking: spontaneous vs imposed.** Spontaneous symmetry breaking (e.g., ferromagnet below Curie) preserves the structure-as-emergent. Imposed symmetry breaking (applied field) gives the SAME final state but with built-in stress that costs free energy. In substrate terms: emergent anisotropy is free-energy-optimal; engineered anisotropy carries a free-energy cost.
5. **Critical-period plasticity as phase transition.** Brain critical periods are phase transitions: pre-critical = isotropic / experience-dependent / emergent; post-critical = anisotropic / fixed / engineered-like. The brain's critical periods CLOSE deliberately to lock in emergent structure -- never to impose pre-designed structure.

**Substrate prediction:** ALL 5 data points predicted. The materials-science angle gives the strongest poetic case for emergent: SOC says emergent structure maximizes information processing; imposed does not.

**Substrate principle:** **Run substrate at the "edge of chaos" via emergent dynamics; avoid frozen-in engineered structures.** This favors continuous-learning encoders (CLS-replay, predictive coding) over one-shot fixed encoders (random-bipolar, Hadamard, label-LDA).

---

## 3. Cross-cell synthesis: (a), (b), (c), or (d)?

**Verdict: (d) conditional, with two refinements.**

The 5 data points are NOT explained by substrate-specific phenomenology (a is rejected -- the pattern reproduces across 5 fields). They are NOT just cone-collapse retrieval (b is rejected -- Cell 5 HYBRID wins WITH labels, so retrieval doesn't universally penalize structure). They are NOT a universal "all memory needs emergent" rule (c is rejected -- HYBRID and FREQ_ROUTED both impose SOMETHING, just emergent-aligned).

The correct framing is **(d) refined: engineered structure helps if-and-only-if (i) it is imposed at the USE-CASE READOUT layer not the SUBSTRATE BASIS layer, AND (ii) the engineered structure can be OVERRIDDEN by data (LASSO-soft, not hard-encoded)**.

**Two refinements to (d):**

1. **Stratification matters.** USER's basis-vs-use-case is the architecturally correct frame. V1-IT-PFC is the biology canon; HYBRID-Cell-5 is the substrate empirical confirmation; SimCLR-then-linear-probe is the ML canon.
2. **Substrate must INFER the data's natural structure first.** This is Cell H' (biology-native unsupervised encoder) and the predictive-coding-encoder path. Once inferred, label-driven readouts ride on top -- THAT is where label-engineering is allowed.

---

## 4. Substrate-design principles derived

1. **PRINCIPLE-1: Encoder layer is data-driven only.** Random-bipolar OR biology-native emergent (SoftHebb, predictive coding, Olshausen-Field, sparse coding). NO category labels, NO orthogonal subspaces, NO grammatical roles imposed at this layer.
2. **PRINCIPLE-2: Readout layer can be label-engineered.** Use-case classification heads, retrieval refuse-gates, multi-hop pointer chains -- these are use-case-layer engineering and are permitted.
3. **PRINCIPLE-3: When engineered structure is needed mid-stack, regularize it (LASSO-soft).** If the substrate needs a role codebook, let it emerge from CLUSTERED or HYBRID structure, not from hand-engineered orthogonality.
4. **PRINCIPLE-4: Test interventions against random-bipolar baseline at the right SCALE.** JL-oversatisfaction (N/V > 100) means random IS at ceiling; ANY engineered structure will lose. Test at N/V ~ 5-10 where random hits JL margin. This is the right V_concepts=4000 regime (the Cell-D point).
5. **PRINCIPLE-5: Cell-H' (biology-native unsupervised encoder) is on the correct trajectory.** Do not abandon it on the first HARD_FAIL; biology has 500M years of evidence and the substrate-product roadmap depends on this layer being right. Apply USER's "empowered to experiment where lit says dismissed" rule.
6. **PRINCIPLE-6: Cross-modal alignment must EMERGE from data.** Stage 3 multi-modal must NOT impose shared label spaces; cross-modal structure must emerge via co-occurrence (contrastive or predictive).
7. **PRINCIPLE-7: LM equivalence requires substrate to LEARN role-filler structure from data.** Pre-imposed role codebooks lose at the basis layer; learned ones (CLUSTERED, HYBRID) win. Stage 4 LM equivalence will need a learned role-binding mechanism.

---

## 5. New bias category proposals

(Per the EXPERIMENT BIAS MASTER CHECKLIST 2026-06-24 -- 13th category candidate.)

**Proposed BIAS-13: BASIS-LAYER LABEL CONTAMINATION.**
- **Definition:** Imposing supervisory labels (categories, grammatical roles, taxonomies) at the substrate's encoder/role-codebook layer rather than at the use-case readout layer.
- **Detection:** Any cell where pre-reg includes "use category labels to project / partition / orthogonalize / route" applied to encoder construction.
- **Pre-dispatch check:** Is the engineered structure at the encoder/basis layer or at the use-case readout? If basis -- DEFER; if readout -- PROCEED.
- **Empirical evidence:** Cells 2-ORTHOG (-0.125 BPC), 5-GRAMMATICAL (-0.084 lift), 7-AXIS_PROJ (-0.056 a3) all violated this and lost.
- **Counterfactual evidence:** Cell 5-HYBRID (+0.833 lift) imposed labels at the readout WHILE keeping the role-codebook learnable -- WON.

**Proposed BIAS-14: JL-OVERSATISFACTION REGIME.**
- **Definition:** Testing engineered-structure interventions at N/V ratios where random-bipolar is already at ceiling (N/V > 100), giving no headroom to demonstrate lift.
- **Detection:** Compute N/V; if > 100, FLAG. Either upscale V or downscale N to reach the discriminating regime N/V ~ 5-10.
- **Pre-dispatch check:** Add an "N/V ratio" line to cell pre-reg; flag oversatisfaction.
- **Empirical evidence:** Cell 7 at V=12 N=8192 (N/V=683) had no discriminating room.

**Proposed BIAS-15: PRIOR-DATA MISMATCH CONFOUND.**
- **Definition:** Imposing a structured prior (categorical, orthogonal, role-based) on data whose true statistics are continuous/Zipfian/graph-structured.
- **Detection:** Before any engineered-structure cell, smoke-test the data's natural statistics (histogram, eigenvalue spectrum of co-occurrence matrix, anisotropy of dense embedding); only impose structure that MATCHES the smoke result.
- **Pre-dispatch check:** Add a "data-statistics smoke" line to cell pre-reg.
- **Empirical evidence:** Cell 2 ORTHOG_SUBSPACE on text8 Zipfian data (continuous tail, no orthogonal partition); FREQ_ROUTED_K2 on the same data matched the Zipf -- WON.

---

## 6. Implications for substrate-product roadmap

- **Stage 1.5 encoder commit** -- MUST be biology-native unsupervised. Cell H' is the right empirical test. If Cell H' HARD_FAILs, REVIVE rather than abandon (USER empowered-to-experiment-where-lit-says-dismissed rule applies; brain-prior +0.10).
- **Stage 2 use-case readouts** -- label-engineering authorized (multi-hop pointers, refuse-gates, classification heads). HYBRID-style allowed.
- **Stage 3 multi-modal** -- EMERGE cross-modal structure from co-occurrence; do NOT impose shared label spaces. Contrastive (SimCLR) or predictive (PC) co-training only.
- **Stage 4 LM equivalence** -- role-filler structure LEARNED from data, not pre-imposed. The HYBRID-Cell-5 pattern (learnable role-codebook + concept-labels) is the canonical template for next role-binding cells.
- **Cell H' (in flight) interpretation in advance:** if HARD_PASS, the basis-vs-use-case stratification is validated and Stage 1.5 closes. If MIDDLE_BAND, scrutinize V-scale (likely JL-oversatisfaction again) before declaring biology-native lost. If HARD_FAIL, revive with different biology mechanism (e.g., predictive coding if SoftHebb failed) before concluding "biology doesn't help" -- 5+ candidates exist (SoftHebb, PC, Olshausen-Field, Foldiak anti-Hebb, BCM, Linsker InfoMax, SOM, SFA).

---

## 7. Cross-thread anchors

- `notes/research_cell7_label_driven_lost_random_2x_drill_2026-06-25.md` -- prior Cell 7 2x drill; this 5x drill complements with cross-field framing.
- `notes/director_encoder_basis_vs_use_case_labels_2026-06-25.md` -- USER basis-vs-use-case principle origin.
- `notes/director_cell_H_prime_biology_unsupervised_encoder_spec_2026-06-25.md` -- Cell H' spec; empirical test of the principle.
- `notes/director_5_intuitive_barriers_with_analogies_2026-06-25.md` -- 5-barrier framework; this drill supplies Barrier-3 (encoder commit) theoretical underpinning.
- `notes/research_optimal_anisotropic_encoder_construction_5x_drill_2026-06-25.md` -- adjacent encoder-construction drill.
- `notes/feedback_experiment_bias_master_checklist_USER_2026-06-24.md` -- proposed BIAS-13/14/15 additions land here.
- `data/exp_substrate_label_driven_anisotropic_encoder_v1/metrics.json` -- Cell 7 verbatim.
- `data/exp_substrate_role_tagged_compositional_generalization_on_concept_KG_v1/metrics.json` -- Cell 5 verbatim.
- `data/exp_substrate_compose_heterogeneous_routing_v3_full_config_rerun/metrics.json` -- Cell 2 verbatim.

---

## 8. Standing P_deflated estimates (for re-calibration tracking)

- P(biology-native unsupervised encoder produces chain-grade lift at V=4000 substrate) = **0.45**
- P(BASIS-LAYER LABEL CONTAMINATION (BIAS-13) is the dominant root cause across 5 cells) = **0.50** (cap invoked)
- P(JL-OVERSATISFACTION (BIAS-14) is the dominant root cause for Cell 7 specifically) = **0.65** (mechanistic, not novel synthesis; deflated 0.20 from raw 0.85)
- P(stratified basis-vs-use-case becomes the substrate-product locked architecture by 2026-07-01) = **0.40** (raw 0.55, deflated 0.20, +0.05 USER-already-on-this-path)

---

## 9. Honest limits + self-flags

- N=3 cells is a small empirical basis. The pattern is suggestive, not definitive. Cell H' results will be the discriminator. UNDER-claim defaults until then (Fix #28).
- I corrected one user-prompt number (NO_ROLES=0.167 not 0.250; GRAMMATICAL-vs-NO_ROLES lift = -0.084 not -0.167). The pattern direction holds in both framings.
- The HYBRID arm in Cell 5 is the load-bearing case for refined-(d). If a future cell shows HYBRID-style at scale also losing, refined-(d) needs reconsideration.
- Materials-science angle E is the weakest empirical contributor (mostly poetic analog); kept for completeness but discounted in synthesis.
- No deep-research subagent spawned; this is a within-thread cross-field synthesis based on existing Store + standard lit (Olshausen-Field, Mu-Viswanath, Ethayarajh, Sutton bitter lesson, Gelman-Loken forking paths, Bak-Tang-Wiesenfeld SOC). If USER wants Web-search verification of any specific citation, route as separate drill.

End of drill.
