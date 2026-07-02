# 5x Drill 3/5 — Neuroscience + Biology: Does PC Earn Complexity in Real Cortex?

**Filed:** 2026-07-02 late evening
**Drill component:** 3 of 5 (companion: math/info-theory, physics/statmech, ML/AI lit, empirical ablation)
**Question:** Does predictive coding (PC) earn its complexity in HD substrate composition with competitive allocation, or is competitive-Hebbian sufficient? Judged via brain evidence.
**Empirical trigger:** Spoke 1 v2 smoke — ARM_FULL_HYBRID (PC+WTA) gap=0.517 vs ARM_COMPETITIVE_ONLY gap=0.507. Delta 0.010 within cv 0.377. If brain does PC+WTA, why can't we replicate composition?
**Calibration:** lit-scan penalty applied (deflate P by 0.15-0.25; novel-synthesis P cap 0.50). Brain-best-in-class discipline USER-locked 2026-07-02.

---

## 1. Prior-work check

**Substrate-KB status:** director_kb_query.py failed with `Unable to allocate 7.40 GiB for an array with shape (970069, 2048)` — embedding matrix too large for local RAM. Fallback: filename Glob + focused reads.

**Relevant prior drills already on disk:**
- `research_brain_generation_cerebellar_forward_prediction_5x_drill_2026-06-22.md` — cerebellar PC angle
- `research_brain_cortical_microcircuit_W_matrix_architecture_5x_drill_2026-06-22.md` — cortical microcircuit
- `research_rank1_hebbian_brain_escape_mechanisms_2026-06-23.md` — Hebbian mechanism escapes
- `research_multi_iter_cleanup_brain_analog_2x_drill_2026-06-23.md` — iterative cleanup as brain analog
- `research_brain_within_concept_floor_5x_drill_2026-06-22.md` — within-concept floor
- `research_neuromodulator_orthogonal_composition_brain_mechanism_2026-06-23.md` — orthogonal composition
- `design_stage2_concept_encoder_spoke1_predictive_coding_competitive_allocation_2026-07-02.md` — the specific composition being probed here

**Overlap check:** No prior drill directly tests "PC vs WTA complexity trade-off with 6-brain-property constraint" — this is a novel synthesis. Cerebellar drill 2026-06-22 covered forward prediction as separate mechanism from competitive coding. Cortical microcircuit drill 2026-06-22 examined W-matrix laminar structure but did not address the PC-vs-competitive-only alternative for concept encoding. Confidence adjustment: novel-synthesis cap P≤0.50 applies.

---

## 2. Cortical laminar organization — is the PC/WTA distinction real at circuit level?

**Canonical microcircuit (Bastos et al 2012, "Canonical microcircuits for predictive coding"; Douglas & Martin 2004):**
- L4: sensory input from thalamus (feedforward)
- L2/3: cortico-cortical feedforward output; lateral competition prominent
- L5: cortico-thalamic + cortico-subcortical output; deep pyramidal cells
- L6: cortico-thalamic feedback; modulatory loops

**Bastos-Friston PC-mapping claim:** feedforward = prediction error carriers (superficial pyramids in L2/3); feedback = prediction carriers (deep pyramids in L5/6). Prediction errors and predictions travel in DIFFERENT laminae with DIFFERENT frequencies (gamma vs alpha/beta oscillations).

**Empirical strength:** MEDIUM-HIGH. Bastos 2015 showed frequency-selective directed connectivity in monkey visual cortex consistent with PC map. van Kerkoerle 2014 showed alpha/beta feedback vs gamma feedforward. BUT — Aitchison & Lengyel 2017 review notes the frequency-directionality claim survives, but the PC INTERPRETATION does not uniquely explain the data (other models predict same frequency split).

**Where WTA sits in the laminae:** L2/3 lateral inhibition (Adesnik & Scanziani 2010) implements competitive normalization — this is competitive-Hebbian territory. Chandelier cells + PV+ interneurons drive fast WTA within L2/3.

**Key evidence PC and WTA are distinct at circuit level:**
- Different cell types: PC-relevant deep pyramids (L5/6) vs WTA-relevant PV+/chandelier interneurons (L2/3)
- Different timescales: PC updates on prediction-error timescale (tens to hundreds of ms); WTA on gamma cycle (~25 ms)
- Different lesion effects: PV+ inhibition disruption breaks WTA sparsity; L5/6 top-down disruption breaks context modulation without breaking sparsity

**Confidence P(PC and WTA are architecturally distinct in cortex) = 0.70** (after lit-scan penalty from 0.85). High enough to treat as separate mechanisms in substrate.

---

## 3. Where PC clearly EARNS its complexity in real brain

Ranking by evidence strength:

**(a) Cerebellum — CLEAR EARN (P=0.85):** Marr-Albus-Ito model; climbing fiber = supervised error signal; parallel fiber weights update via LTD contingent on climbing-fiber-driven complex spikes. This is prediction-error learning with strong evidence spanning 60 years. BUT — this is SUPERVISED error, not PC in Rao-Ballard sense. Cerebellum has external teacher (climbing fiber); Rao-Ballard PC has INTERNAL error via reconstruction.

**(b) Motor cortex M1 for forward models — CLEAR EARN (P=0.75):** Sensorimotor prediction (efference copy → sensory cancellation) is well-established. Shadmehr, Wolpert, Krakauer show clear forward-model behavior. This is PC-like: predict sensory consequences of action, minimize surprise. Timescale: hundreds of ms.

**(c) V1 for oriented-edge prediction (Rao-Ballard 1999) — MIXED (P=0.45 after penalty from 0.60):** Original Rao-Ballard demonstrated V1 receptive field emergence from prediction of natural images. Zhu-Rozell 2013 replicated. BUT — competitive sparse coding (Olshausen-Field 1996) produces IDENTICAL V1 receptive fields WITHOUT prediction. Rehn & Sommer 2007 showed both mechanisms converge on same solution. So V1 does NOT distinguish PC from competitive sparse coding.

**(d) IT cortex for invariant object recognition — WEAK PC (P=0.25):** Evidence is more consistent with slow-feature analysis (Wiskott-Sejnowski) + hierarchical sparse coding (DiCarlo lab). PC contributions are subtle at best. Yamins & DiCarlo 2016 goal-driven modeling shows feedforward CNNs match IT well without explicit PC.

**(e) Hippocampus for episodic prediction — SPECULATIVE (P=0.35):** Successor representation (Stachenfeld-Botvinick-Gershman 2017) frames HC as predicting future states — but this is TD-learning, not Rao-Ballard PC. Recent Whittington et al 2020 Tolman-Eichenbaum Machine bakes in PC but this is a model, not evidence.

**(f) Auditory cortex mismatch negativity (MMN) — MEDIUM (P=0.55):** MMN is a robust PC signature. Prediction violation drives error signal. Garrido et al 2013 review. Strong evidence PC operates in A1 for temporal expectation.

**Where does PC clearly beat competitive-alone in CONCEPT encoding specifically?**

Concept encoding maps most closely to IT / higher temporal cortex — where evidence for PC is WEAK. The regions where PC clearly earns complexity are:
1. Sensorimotor prediction loops (M1, cerebellum) — WRONG domain for concept encoding
2. Temporal-sequence prediction (A1, hippocampus MMN) — POSSIBLE relevance for text streams
3. Reconstruction of low-level sensory inputs (V1) — but competitive sparse coding EQUALS PC here

**Substrate implication:** For Spoke 1 (text-to-concept), the brain evidence for PC earning complexity is MEDIUM at best. The clearest wins for PC are in domains substrate does NOT operate in yet (motor, sensorimotor).

---

## 4. Where competitive-Hebbian ALONE clearly works in real brain

**(a) Barrel cortex somatotopy (Simons 1978; Petersen 2007):** whisker→barrel mapping is competitive-Hebbian with activity-dependent refinement. No PC required. Ferrets rewired to route visual input to A1 develop visual receptive fields via competitive-Hebbian alone (Sur & Leamey 2001). This is the CLEANEST "competitive alone works" evidence.

**(b) Kohonen SOM biological analog:** Motor cortex somatotopy, retinotopy in V1, tonotopy in A1 — all self-organize via competitive-Hebbian with lateral inhibition. Erwin, Obermayer, Schulten 1995 showed elastic-net = competitive-Hebbian reproduces cortical map layout.

**(c) Grandmother/concept cells (Quiroga 2005, "Jennifer Aniston cells"):** Sparse invariant representations in medial temporal lobe (hippocampus, entorhinal, parahippocampal). Emergence mechanism is DEBATED but recent Quiroga 2020 review favors competitive sparse coding + slow-feature invariance + Hebbian consolidation — NOT explicit PC. Rey et al 2020 showed concept-cell emergence in convergent recurrent networks without PC.

**(d) Cerebellar granule cell layer expansion coding (Cayco-Gajic et al 2017; Litwin-Kumar 2017):** K=4-8 fan-in from mossy fibers; sparse expansion into ~50 billion granule cells. This is competitive-sparse-coding for expansion representation — NO PC internal to granule layer. The supervised error (climbing fiber) trains OUTPUT weights (parallel fiber → Purkinje LTD), not the granule-cell expansion code itself. So granule-cell code is competitive-Hebbian; PC is at a different layer.

**Substrate implication:** Cortical MAPS + concept cells + expansion codes ALL work brain-side with competitive-Hebbian alone. The PC contribution is at prediction/error/context modulation, not at REPRESENTATIONAL BASIS formation.

---

## 5. Dendritic-level evidence — is PC vs WTA one mechanism or two?

**Larkum 2013, "Cellular mechanism for cortical associations":** basal dendrites of L5 pyramids integrate feedforward (competitive/WTA-like), apical dendrites integrate top-down feedback (PC-like). BAC firing (backpropagating AP + apical calcium) requires BOTH. This is the strongest single-neuron argument that PC and WTA are DIFFERENT compartmentalized computations.

**Poirazi & Papoutsi 2020, "Illuminating dendritic function":** apical vs basal specialization now confirmed with 2P imaging + optogenetics. Distinct plasticity rules per compartment.

**Häusser & Mel 2003; more recently Kastellakis & Poirazi 2019:** clustered synapse plasticity + NMDA spikes in basal → local Hebbian competition. Apical NMDA spikes → context/prediction integration.

**Substrate implication:** at the single-neuron level, PC (apical) and WTA/Hebbian (basal) are architecturally distinct AND both are required for BAC firing (the canonical L5 output signal). This is the STRONGEST evidence for "PC and WTA are different mechanisms and BOTH matter." However — this is about MODULATION and BINDING top-down context, not about representational basis formation for concepts.

**Reframe:** the dendritic evidence supports "PC is a MODULATION mechanism on top of competitive-Hebbian representation base." Not "PC is an alternative representation-forming mechanism to competitive." Big difference for substrate architecture.

---

## 6. CLS + hippocampal-cortical evidence

**McClelland & O'Reilly 1995 CLS:** hippocampus = fast, sparse, pattern-separating (competitive); cortex = slow, overlapping, generalizing.

- Hippocampal side (DG especially): CLEARLY competitive-Hebbian. DG mossy cells + granule cells + interneurons implement pattern separation via strong sparsity + competitive inhibition. This is the CANONICAL brain-side competitive-Hebbian architecture. No PC needed.
- Cortical side (slow schema learning): PC framework is a good FIT (Friston has argued cortical hierarchy = PC hierarchy) but not the only fit. Slow-feature analysis + competitive sparse coding also explain the phenomena.

**Recent Kumaran et al 2016 "What learning systems do intelligent agents need":** update to CLS. Even here, PC is not the required cortical mechanism; the requirement is "slow gradient-consistent updates preserving structure."

**Substrate implication:** for a concept encoder targeting the CORTICAL (slow, generalizing) side, PC is one option among several. For the HIPPOCAMPAL (fast, pattern-separating) side (which is what Spoke 3 targets), competitive-Hebbian is the answer.

---

## 7. Failure modes — what does PC-impairment look like?

**Schizophrenia (Adams, Stephan, Brown, Friston, Friston 2013):** aberrant PC hypothesis. Positive symptoms (hallucinations) framed as failed top-down prediction cancellation → aberrant prediction errors → false percepts. Negative symptoms framed as impaired precision-weighting.

**Empirical support:** MEDIUM. NMDA-antagonist ketamine reproduces some schizophrenic symptoms and disrupts prediction-error signals. BUT — same evidence supports alternative accounts (attention dysregulation, gain control failure).

**Autism (Pellicano-Burr 2012, "attenuated prior"):** framed as reduced prediction precision → sensory information dominates over priors → hypersensitivity. Again — attractive framework, evidence NON-UNIQUE to PC.

**Cerebellar ataxia:** loss of forward-model prediction → dysmetria + intention tremor. This is the CLEAREST PC-failure evidence, but it is SENSORIMOTOR PC, not conceptual PC.

**Substrate implication:** the failure-mode evidence for CONCEPTUAL/COGNITIVE PC is weaker than for SENSORIMOTOR PC. This supports "PC clearly earns complexity in sensorimotor loops; conceptual PC is theoretically attractive but empirically weaker."

---

## 8. VERDICT — what does neuroscience say?

**The brain evidence supports THIS decomposition:**

1. **PC and competitive-Hebbian ARE architecturally distinct mechanisms** at circuit AND dendritic level (P=0.70). They occupy different laminae (L2/3 vs L5/6), different cell types (interneurons vs deep pyramids), different dendritic compartments (basal vs apical), different timescales (gamma vs alpha/beta).

2. **PC clearly earns complexity in SENSORIMOTOR + TEMPORAL-SEQUENCE prediction loops** (P=0.80 for cerebellum/M1; P=0.55 for A1-MMN). This is where the strongest evidence lives.

3. **PC's role in CONCEPT/REPRESENTATION formation is WEAKER** (P=0.35 for IT; P=0.45 for V1). Where PC is claimed to form representations, competitive sparse coding produces the SAME representations (Olshausen-Field ≈ Rao-Ballard on V1). Brain concept cells (Quiroga) look like competitive sparse coding + slow-feature invariance, NOT PC.

4. **PC operates as MODULATION on top of competitive-Hebbian representational base** (P=0.65). Dendritic evidence (apical=PC, basal=competitive/Hebbian) supports "top-down context modulation" role for PC, not "representation formation" role. This is a DIFFERENT COMPOSITION than "PC forms concepts, WTA sparsifies."

5. **CORTICAL MAPS + CONCEPT CELLS + EXPANSION CODES form via competitive-Hebbian ALONE** in brain (P=0.75). Barrel cortex rewire (Sur), Kohonen SOM analog, cerebellar granule layer, medial temporal concept cells — all work without PC.

**What this says for HD substrate Spoke 1 empirical result:**

Spoke 1 v2 smoke showed FULL_HYBRID gap=0.517 vs COMPETITIVE_ONLY gap=0.507 (delta 0.010 within cv 0.377). Under brain-best-in-class discipline, this is CONSISTENT with brain evidence:

- Concept-encoder formation (Spoke 1 target) is precisely the domain where PC contribution to representation formation is WEAK in brain
- Brain concept cells form via competitive sparse coding + slow-feature + Hebbian consolidation — NOT PC
- The "hybrid barely beats competitive-only" empirical result MATCHES what brain evidence predicts

**Our substrate composition is not obviously broken.** The near-null delta is what brain evidence predicts for CONCEPT ENCODING specifically. The prediction is:

- If Spoke 1 were sensorimotor prediction or MMN-style temporal expectation → PC would clearly earn complexity
- Because Spoke 1 is text-to-concept (analog to IT/perirhinal/entorhinal concept formation) → PC is expected to add little over competitive-Hebbian

---

## 9. IF PC and competitive-Hebbian are the SAME mechanism at different description levels

**Case FOR (P=0.30):** Rehn-Sommer 2007 showed sparse coding + PC converge on same V1 receptive fields. Some mathematical PC formulations are algebraically equivalent to sparse-recurrent settling networks (Rozell et al 2008 LCA). At a computational-level (Marr), PC and competitive sparse coding CAN be the same objective (minimize reconstruction + sparsity).

**Case AGAINST (P=0.70 accepted):** Dendritic compartmentalization + laminar segregation + cell-type separation is REAL. At the implementation level (Marr level 3), the mechanisms are distinct even if at the computational level (Marr level 1) they can be framed similarly.

**Substrate implication if same-mechanism:** our current Spoke 1 hybrid architecture is doing DOUBLE WORK on the same computation with two different mechanisms → the near-null delta is EXPECTED because we've implemented the same optimization twice. Fix: pick ONE mechanism, remove the other, get same result at half the cost.

---

## 10. IF PC and competitive-Hebbian are DIFFERENT and BOTH needed

**Case FOR (P=0.65 accepted):** brain evidence supports architectural distinction. Both are present. Both can be lesioned separately with different effects.

**Case AGAINST for CONCEPT-ENCODING specifically (P=0.55):** in the CONCEPT-encoding domain, brain evidence favors competitive-Hebbian doing the representation-formation work and PC doing top-down modulation. This is DIFFERENT composition than "PC + WTA compose to form concepts."

**Substrate implication if different-and-both-needed:**
Our current Spoke 1 composition may be theoretically correct at the mechanism level but implementing WRONG COMPOSITION. Specifically:
- Current: PC layer feeds forward to WTA layer; sequential composition
- Brain-analog: WTA/competitive forms base representation; PC modulates via top-down context
- Fix: invert the composition. Competitive-Hebbian layer forms concept base representation; PC layer provides top-down context modulation as a MODULATORY signal (multiplicative gain), NOT as a serial predecessor to WTA.

---

## 11. Substrate architecture implications

**Recommended concrete changes to Spoke 1 architecture, in priority order:**

**(A) Test the same-mechanism hypothesis (LOW cost, HIGH information):** run an arm that uses ONLY competitive-Hebbian with the EXACT sparsity target of FULL_HYBRID. If it matches FULL_HYBRID within cv, then PC+WTA are the same mechanism — collapse to WTA-only. Ship as v3. Cost: 1 arm addition.

**(B) Test the inverted composition (MEDIUM cost, HIGH information):** run an arm with WTA/competitive base + PC as multiplicative context gain (not serial predecessor). Brain-analog composition. Ship as v3 ARM_WTA_BASE_PC_GAIN. Cost: ~200 LOC.

**(C) Test PC in its actual competent domain (MEDIUM cost, DIAGNOSTIC):** Spoke 2 targets temporal contiguity / slow-feature analysis. That is a domain where MMN-style PC SHOULD earn complexity. If Spoke 2 also shows near-null PC delta → substrate PC implementation is broken. If Spoke 2 shows clear PC lift → substrate PC works, it just doesn't earn its complexity for CONCEPT-encoding.

**(D) Don't remove PC entirely yet:** brain evidence supports PC being real and distinct; substrate needs it for future spokes (temporal, motor-analog, hierarchical). Just don't expect it to earn complexity in the concept-formation-alone task.

---

## Top-line verdict for team

**Neuroscience says:** PC and competitive-Hebbian ARE architecturally distinct in cortex (dendritic + laminar + cell-type evidence, P=0.70). BUT — in the specific domain of CONCEPT ENCODING (analog to IT / medial temporal), competitive-Hebbian ALONE forms the representation base in brain (Quiroga concept cells, cortical maps, expansion codes). PC provides TOP-DOWN MODULATION on top of that base, not an alternative representation-forming mechanism.

**The Spoke 1 v2 near-null empirical result (delta 0.010 within cv 0.377) is CONSISTENT with brain evidence.** Our substrate composition is not obviously broken. What may be broken is the COMPOSITION ORDER: we've composed PC → WTA as if PC forms concepts and WTA sparsifies. Brain-analog is INVERTED: WTA/competitive forms concept base; PC modulates.

**Recommended next actions:**

1. Add ARM_WTA_ONLY_TUNED to v3 to test same-mechanism hypothesis (LOW cost)
2. Add ARM_WTA_BASE_PC_GAIN to v3 to test inverted brain-analog composition (MEDIUM cost)
3. Reserve full PC evaluation for Spoke 2 (temporal) where brain evidence predicts PC EARNS its complexity
4. Do NOT rip PC out — brain evidence supports keeping it in the architecture for future spokes

**Uncertainty bounds:** at high novel-synthesis P≤0.50 cap:
- P(our substrate composition is broken, PC should work here) = 0.20
- P(PC and WTA collapse to same mechanism computationally) = 0.30
- P(composition is right mechanism but wrong ORDER; inverted brain-analog would work) = 0.35 [preferred hypothesis]
- P(both mechanisms present but Spoke 1's specific task doesn't reward PC) = 0.50 [most consistent with brain evidence]

Bottom two hypotheses (0.35+0.50) both say "keep PC in architecture, redesign what it does in composition." That's the strongest signal from this drill.
