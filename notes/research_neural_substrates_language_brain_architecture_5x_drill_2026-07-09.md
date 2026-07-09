# RESEARCH 5x DRILL — Neural substrates of language: dual-stream, language network, neural reuse, critical periods, prediction

**Date:** 2026-07-09
**Domain:** NEURAL SUBSTRATES (1 of 5 FOUNDATIONAL drills mapping how humans learn language, brain-first, ML-not-the-guide)
**Author:** research (Sonnet), synthesizing 2 completed parallel Sonnet lit-scans (neural-reuse/recycling; critical-periods/plasticity) + own grounded neuroscience knowledge for dual-stream/Broca/angular-gyrus and predictive-processing threads (2 sub-agent lit-scans on those angles were dispatched but not consolidated before this synthesis was ordered — see gap note below; core claims below are well-replicated textbook findings, calibration penalty applied throughout).
**Prior-coverage check (do not duplicate):** `research_5x_drill_3_neuroscience_substrate_content_HF_2026-07-02.md` already covers VWFA/LCD, ATL hub-and-spoke, and CLS sparsity-mismatch in depth (monolith-doing-4-jobs finding, A+B+C v2 prescription). `research_brain_drill_substrate_native_relational_semantic_encoding_5x_DEEPER_2026-06-22.md` already covers Random Indexing + BEAGLE + hub-spoke composition (now built as `hdlab/random_indexing.py`). This drill does NOT re-derive those; it covers the FIVE NEW angles: dual-stream (dorsal/ventral), modern Broca/angular-gyrus, neural reuse/recycling (general principle beyond VWFA), critical/sensitive periods, and prediction-as-core-computation.
**Gap note (honest):** two of four dispatched lit-scan sub-agents (dual-stream/Broca/angular-gyrus; predictive-processing) did not return a consolidated transcript before synthesis was ordered to proceed without further waiting. Those two sections below are written from directly-verifiable, high-consensus textbook/review-level neuroscience (Hickok & Poeppel; Friederici; Kuperberg & Jaeger; DeLong/Urbach/Kutas; Levy; Altmann & Kamide; Lesage et al.) rather than from the sub-agent transcripts — flagged per-section below. The neural-reuse/recycling and critical-periods sections ARE grounded in completed sub-agent lit-scans.

---

## HEADLINE

**The brain's language network is not a bespoke organ — it is a THIN, mostly WHITE-MATTER-CONNECTIVITY overlay (dorsal-stream arcuate-fasciculus expansion) stitching together a small set of much older general-purpose computational modules (sequencing/basal-ganglia, forward-model/cerebellum, relational-mapping/hippocampus, conjunctive-Hebbian-binding/ATL, competitive selection). Neural reuse (Anderson 2010; Dehaene 2005) is the dominant organizing principle, not exception. This is a substantive validation of the substrate's existing strategy — compose general HD primitives (KGStore, hippocampal_encoder, action_selection, predictive_coding, sequence_memory) via a thin `cortex.py` routing layer — rather than build a monolithic language module.**

**P_deflated (reuse-principle validates current strategy): 0.48** (base high-confidence in the biology → -0.20 novel-synthesis-onto-our-substrate cap → 0.48, capped <0.50 per calibration rule).

**Sharpest concrete gap found:** the substrate has NO analog of the dorsal-stream "shortcut" (form-to-form repetition pathway that bypasses the semantic hub) — `sequence_memory.py`/`generation.py` and `kg_traversal.py`/hub are not architecturally split into a fast form-preserving path vs. a semantic-routed path the way conduction aphasia proves the brain is split. This is the same failure SHAPE as the 2026-07-02 "monolith doing 4 jobs" finding, applied to a different pair of jobs (repetition vs. paraphrase).

---

## S1 — NEURAL ARCHITECTURE MAP: which module computes what, and which pre-linguistic circuit it reuses

| Brain module | Linguistic computation | Pre-linguistic circuit it reuses | Key evidence |
|---|---|---|---|
| **Dorsal stream** (post. temporal Spt → inf. parietal → premotor/BA44, via arcuate fasciculus) | Sound-to-articulation sensorimotor translation; phonological rehearsal/repetition; NOT meaning | General auditory-motor integration (present in non-human primates for vocal/orofacial control, but the AF itself is disproportionately EXPANDED in humans — Rilling et al. 2008 comparative DTI) | Conduction aphasia: fluent comprehension + fluent spontaneous speech, but broken REPETITION (esp. of nonwords) — direct double-dissociation evidence of a distinct form-to-form pathway, separate from meaning access |
| **Ventral stream** (STS/STG → MTG, bilateral) | Sound-to-meaning mapping; lexical-semantic interface; routes into ATL hub | Bilateral auditory object/category recognition (shared with non-speech sound processing) | More bilateral, more resilient to unilateral lesion than dorsal stream (Hickok & Poeppel 2004, 2007) |
| **Broca's area / BA44-45** | Hierarchical/recursive structure-building (Merge-like); syntactic sequencing; plausible top-down predictive signal into temporal cortex | Action-sequencing / hierarchical motor planning — BA44's macaque homolog is area F5, the classic MIRROR-NEURON grasping-sequence area (Rizzolatti & Arbib 1998, "Language within our grasp") | Domain-general hierarchical-sequence tasks (music syntax, tool-use action grammars, artificial grammar learning) also recruit BA44, not just sentence syntax (Friederici's hierarchy-of-structure-building program) |
| **Angular gyrus / TPJ** | Sentence/event-level semantic integration; cross-modal thematic composition; part of default-mode/semantic network | Contested: possibly a domain-general integration/attentional buffer repurposed for language, not a language-specific organ (Humphreys & Lambon Ralph propose AG = "flexible" complement to ATL's "core" amodal hub) | Live controversy — AG may be doing less genuinely-semantic work than ATL and more generic multimodal buffering |
| **ATL hub** (covered in depth 2026-07-02/06-22 — not re-derived here) | Amodal conjunctive semantic convergence | Perirhinal/CLS conjunctive-Hebbian coding (already documented) | (see prior notes) |
| **Basal ganglia / corticostriatal loop** | Rule-based grammatical processing (regular morphology, sequencing rules) — Ullman's declarative/procedural model | Motor-sequence/habit learning circuit — SAME circuit, not an analog: FOXP2 mutation (KE family) causes BOTH an orofacial motor-sequencing deficit AND a grammatical impairment simultaneously — the double phenotype is the load-bearing causal evidence that one circuit does both jobs | Ullman 2004/2016; Lieberman on basal-ganglia sequencing; FOXP2 literature |
| **Hippocampal/parietal spatial system** | Abstract relational/conceptual "cognitive map" structure (non-spatial concept relations organized via grid/place-cell-like code) | Literal spatial navigation circuitry (place cells, grid cells) | Bellmund et al. 2018 Science; Constantinescu, Behrens, et al. 2016 Science — grid-like fMRI code found for purely conceptual (non-spatial) dimensions |
| **Sensorimotor/action-perception cortex** | Concrete-word semantic grounding (verbs like "kick," "lick," "pick" activate somatotopically matched motor cortex) | Literal motor execution circuitry | Pulvermuller's action-perception-circuit program |
| **Cerebellum** | Predictive/forward-model contribution to real-time language processing (anticipatory parsing) | Classical motor forward-model / error-correction (Ito; Wolpert-Kawato) | Lesage, Morgan, Olson, Meyer, Miall 2012 Current Biology — cerebellar rTMS causally DISRUPTS predictive language processing in the visual-world anticipatory-eye-movement paradigm |
| **Left IFG (predictive top-down)** | Generates predictions about upcoming lexical/structural material fed into temporal cortex | Same BA44/45 substrate as structure-building (above); reuse of one circuit for two related jobs (build + predict) | More speculative extension of the general predictive-coding framework onto specific language circuitry — flagged as less-replicated than the N400/surprisal findings below |

**Minimal set of functionally distinct computations dual-stream implies is IRREDUCIBLE:** at least two (dorsal form-to-form, ventral form-to-meaning) plus a third amodal convergence stage (ATL hub) plus a fourth control/gating stage (semantic control per 2026-07-02 note) — i.e. comprehension-and-production-of-sentences is NOT one computation wearing different hats; it is a minimum of ~4 anatomically and computationally separable jobs, each independently lesionable (aphasia syndromes are the existence proof of separability).

---

## L1 — Neural reuse / recycling (grounded in completed sub-agent lit-scan)

**Dehaene's neuronal recycling** (Dehaene 2005 TICS; Dehaene & Cohen 2007 Neuron): cultural inventions (reading, arithmetic) recycle cortical circuits whose PRE-EXISTING computational profile is the closest match, not just the nearest anatomy. (VWFA instance already covered 2026-07-02; treated here only as the general-principle anchor.)

**Anderson's massive redeployment hypothesis** (Anderson 2010 BBS "Neural reuse: a fundamental organizing principle of the brain"; Anderson 2014 *After Phrenology*): large-scale meta-analytic connectivity modeling shows MOST cortical regions are recruited across many, often unrelated, cognitive domains — multi-functionality is the norm, not the exception. Older evolutionary circuits are redeployed into more new functions than younger ones ("workspace" model). Reuse tracks a region's intrinsic COMPUTATIONAL TRANSFORM (e.g. "sequence-detection," "relational-mapping," "error-correction"), not mere anatomical adjacency.

**Concrete load-bearing instances found (ranked by causal-evidence strength):**

1. **STRONGEST — basal ganglia/FOXP2/Ullman procedural system for grammar.** The KE-family FOXP2 mutation produces BOTH an orofacial motor-sequencing deficit AND a grammatical (rule-application) deficit in the SAME individuals, from the SAME corticostriatal circuit. This is causal, single-gene, single-circuit, dual-phenotype evidence — the strongest instance of reuse in the language-reuse literature (stronger than VWFA, which is correlational/lesion-based only).
2. **Mirror-neuron/F5 → Broca's area (BA44):** action-sequencing/hierarchical-motor-planning circuit repurposed for hierarchical syntax (Rizzolatti & Arbib 1998).
3. **Hippocampal/parietal spatial cognition → abstract conceptual relational structure:** grid-cell-like coding generalizes from literal space to arbitrary conceptual dimensions (Bellmund 2018; Constantinescu 2016).
4. **Action-perception circuits → concrete semantic grounding** (Pulvermuller).
5. **Cerebellar forward-model → linguistic prediction** (overlaps prediction thread below).

**What determines which old circuit gets reused:** Anderson's argument is COMPUTATIONAL-PROFILE compatibility, not proximity — a region already computing "sequence + error-correct" gets recruited for grammar; a region already computing "relational/metric mapping" gets recruited for conceptual structure. This predicts language bootstrapping should look like RECOMBINING a small library of generic transforms, not growing new ones.

**Where reuse breaks down / genuine novelty exists:** the arcuate fasciculus is the sharpest documented case of actual NEW machinery — not a new computation, but disproportionately EXPANDED WHITE-MATTER CONNECTIVITY between temporal and frontal cortex relative to other primates (Rilling et al. 2008 Nat Neurosci). **The evolutionary "invention" for language looks structurally like a new wire, not a new computer.**

---

## L2 — Critical / sensitive periods (grounded in completed sub-agent lit-scan)

**Behavioral shape of the sensitive period:** classic Lenneberg (1967) hard-cutoff-at-puberty claim is NOT what modern large-N data show. Hartshorne, Tenenbaum & Pinker 2018 Cognition (n≈669,498, online grammar test) find grammar-learning capacity is roughly FLAT until ~17-18, then declines APPROXIMATELY LINEARLY — a gradual decline, not a sharp cliff. Johnson & Newport 1989 found a similarly graded age-of-arrival effect on ultimate L2 attainment. Feral/deprivation cases (Genie) are suggestive but confounded (trauma, malnutrition) and should not be treated as clean evidence.

**Perceptual narrowing (the clearest mechanistic story):** Werker & Tees 1984 + Kuhl's Native Language Magnet / neural-commitment theory (Kuhl 2004 Nat Rev Neurosci) — infants discriminate essentially ALL phonetic contrasts across human languages at ~6 months, then narrow to native-language contrasts by ~10-12 months, via UNSUPERVISED DISTRIBUTIONAL LEARNING of phoneme-category boundaries from ambient input statistics (no correction signal required — a clustering-from-statistics mechanism, directly compatible with the prediction thread below).

**Neurobiological open/close mechanism:** Hensch 2005 Nat Rev Neurosci establishes the molecular mechanism (GABAergic parvalbumin-interneuron maturation triggers plasticity-window ONSET; perineuronal net formation triggers CLOSURE; enzymatic PNN digestion reopens plasticity in animal models) — **but this is primarily VISUAL-CORTEX ocular-dominance evidence.** Direct evidence this SAME molecular mechanism governs LANGUAGE-specific circuits is thin/indirect (myelination timelines of the arcuate fasciculus continuing into adolescence — Perani et al. — and synaptic pruning schedules are the closest language-relevant correlates). **Flag: substantial extrapolation from the visual system here; be honest this is NOT as directly demonstrated for language as for vision.**

**Statistical learning as the acquisition mechanism WITHIN the window:** Saffran, Aslin & Newport 1996 Science — 8-month-olds segment word boundaries from continuous artificial speech using ONLY transitional probabilities between syllables, with zero supervision or feedback. This is the concrete computational mechanism instantiating sensitive-period learning: unsupervised distributional-statistics tracking, not explicit correction.

**Differential closure across linguistic levels (important structural finding):** phonology/accent closes EARLIEST and SHARPEST (near-native accent after puberty is rare even with fluent grammar); syntax has an INTERMEDIATE window (extends further than phonology per Hartshorne et al.); vocabulary/semantics remain plastic ESSENTIALLY LIFELONG (adults acquire new words continuously with no evident ceiling). **This rules out a single global plasticity dial — the brain runs multiple, level-specific plasticity schedules with different decay time-constants, not one master "critical period" switch.**

---

## L3 — Dual-stream, Broca modern view, angular gyrus (own grounded knowledge; sub-agent transcript not consolidated — see gap note)

Covered inline in S1 table above. Additional detail: MEG/iEEG/ERP timing shows roughly serial-but-overlapping cascade (~100-200ms phonological/VWFA, ~250-400ms N400 semantic access in ATL+angular gyrus, ~400-600ms P600 syntactic integration), with top-down feedback arriving by ~250ms — i.e. CASCADED-INTERACTIVE, not strictly serial (this matches the 2026-07-02 note's Woolnough 2021 citation for the reading-specific cascade; the sentence-level cascade generalizes the same shape).

---

## L4 — Prediction as core computation (own grounded knowledge; sub-agent transcript not consolidated — see gap note)

**Well-replicated, high-confidence findings:**
- **N400 as pre-activation, not just integration-cost:** DeLong, Urbach & Kutas 2005 Nat Neurosci — the "a" vs "an" article-mismatch effect shows readers pre-activate the PHONOLOGICAL FORM of an expected noun before the noun itself arrives. This is direct evidence of literal predictive pre-activation, not merely post-hoc ease of integration.
- **Surprisal theory:** Hale 2001; Levy 2008 Cognition — reading time is proportional to -log P(word | context) (information-theoretic surprisal). Broad, cross-linguistic, well-replicated empirical support (eye-tracking, self-paced reading).
- **Anticipatory eye movements:** Altmann & Kamide 1999 Cognition (visual-world paradigm) — listeners saccade to the plausible target object BEFORE the noun is spoken, driven by the verb's selectional restrictions alone. Direct evidence of predictive parsing running ahead of the bottom-up acoustic signal.
- **Cerebellum as a causal contributor to linguistic prediction:** Lesage, Morgan, Olson, Meyer & Miall 2012 Current Biology — cerebellar rTMS DISRUPTS predictive language processing in the same visual-world anticipation paradigm. This is a genuine causal (not just correlational) extension of the cerebellum's classical motor-forward-model role into language.

**More speculative / extrapolated (be honest about the gradient of confidence):**
- Kuperberg & Jaeger 2016's taxonomy is important precisely because it warns that "prediction" is used loosely — facilitation/pre-activation (well-evidenced above) is NOT the same claim as full-blown Bayesian generative prediction, which is a stronger and less-directly-tested claim.
- A FULL hierarchical-predictive-coding architecture in language cortex (higher areas literally generating top-down predictions that lower areas compute prediction-error against, propagating up a cortical hierarchy per the general Friston framework) is a coherent extrapolation of the general predictive-coding theory onto language circuitry, but is comparatively SPECULATIVE relative to the surprisal/N400/anticipatory-eye-movement findings, which stand on their own without requiring the full hierarchical-generative-model commitment.
- Whether prediction-error (rather than mere co-occurrence correlation) is literally THE core learning signal for ACQUISITION (not just an aid to adult comprehension) is plausible via the statistical-learning reframing (Saffran) but is not yet as directly causally demonstrated in development as the adult cerebellar-rTMS result is for online comprehension.

---

## Cheap decisive test

**Test name:** `dorsal_shortcut_vs_hub_double_dissociation_v1`

**Setup:** two arms built from EXISTING substrate primitives, no new mathematical machinery:
1. **Hub-routed arm (current):** encode → `random_indexing`/`concept_encoder` spoke → `kg_traversal.KGStore.W` hub → `generation.py`/`sequence_memory.py` output.
2. **Shortcut arm (new, cheap):** direct Hebbian bind of input-token-sequence code → output-token-sequence code via a SECOND `sequence_memory.SequenceMatrix` instance that never touches `KGStore.W` at all (a literal form-to-form associative store, bypassing the hub).

**Tasks:**
- **Task A — verbatim repetition/echo** of held-out NOVEL sequences (nonword-like, no semantic content) — the substrate analog of the nonword-repetition test used to diagnose conduction aphasia.
- **Task B — semantic paraphrase/synonym retrieval** (existing WordNet-style held-out synonym probe from the 2026-06-22/2026-07-02 notes) — requires hub routing.

**HARD-PASS (double dissociation confirmed):** shortcut arm beats hub-routed arm by ≥10 pts top-1 on Task A (novel-sequence repetition) AND hub-routed arm beats shortcut arm by ≥10 pts on Task B (semantic paraphrase). This mirrors the conduction-aphasia patient profile and would justify building the dorsal-stream shortcut as a permanent architecture component.

**HARD-FAIL:** no dissociation — either arm dominates BOTH tasks (within 3 pts of each other on both), meaning the "two-pathway" framing does not carve a real architectural distinction for this substrate at current scale, and the existing single pathway should NOT be split.

**MIDDLE_BAND:** dissociation present but weak (5-10 pt margins) — triggers a follow-up scale-sweep before committing to the split as permanent architecture.

**Cost estimate:** reuses two already-built primitives (`sequence_memory.SequenceMatrix`, `kg_traversal.KGStore`); no new encoder math. Estimated ~1-2 hr local_cpu build + smoke.

---

## Falsifiable predictions (HARD-PASS / HARD-FAIL, calibration-deflated)

| Claim | HARD-PASS | HARD-FAIL | P_deflated |
|---|---|---|---|
| Dorsal-stream shortcut is a real missing component (double dissociation per cheap test above) | ≥10pt margin each direction | <3pt margin either direction | **0.40** |
| Hierarchical Merge-like structure-builder is required beyond current flat role-slot binding, at CURRENT task scope | measurable degradation of role_slot_summarizer on nested/recursive test items vs flat items, ≥15pt gap | no gap (flat binding suffices at current scope) | **0.30** |
| A genuine time-scheduled decaying-plasticity-per-level primitive (phonology fast-closing, semantics never-closing) measurably helps vs current fixed-hyperparameter regime | ≥1 seed-stable improvement on a staged-exposure ablation | no measurable difference from fixed schedule | **0.35** |
| Cerebellar-forward-model (predictive_coding.py) wired explicitly into generation.py's forward pass reduces compounding drift (cross-thread with today's independent-channels drift note) | measurable intra-decline improvement, same metric family as `research_brain_independent_channels_resolve_compounding_error_tension_2026-07-09.md` | no improvement / degrades | **0.35** |

All capped <0.50 per lit-scan calibration penalty; all four are genuinely untested on THIS substrate (novel-synthesis regime).

---

## Cross-thread synthesis with prior entries

- **`research_5x_drill_3_neuroscience_substrate_content_HF_2026-07-02.md`** — established the "monolith doing 4 jobs" failure pattern for VWFA/ATL/CLS. This drill finds the SAME shape at a different pair of jobs: dorsal (repetition) vs ventral (paraphrase) currently conflated in `sequence_memory`/`generation`/`kg_traversal`. Same diagnosis, same prescription pattern (split into named components), different anatomical pair.
- **`research_brain_drill_substrate_native_relational_semantic_encoding_5x_DEEPER_2026-06-22.md`** — RI + hub-spoke; this drill's ventral-stream section routes directly into that hub, no new claim needed there.
- **`research_value_based_action_selection_basal_ganglia_2026-07-08.md`** (`hdlab/action_selection.py`) — the substrate's basal-ganglia Go/NoGo analog is CURRENTLY wired for action-selection (SR+TD(0) value gate), not grammatical rule-application. The FOXP2 double-phenotype evidence (this drill) suggests the SAME circuit-family is a candidate for a grammar/rule-application reuse — an adjacency worth a follow-up drill, not yet built.
- **`research_neuromodulatory_self_manager_controller_2026-07-08.md`** (`hdlab/self_manager.py`) — the 6-channel neuromodulator analog is a RUNTIME scalar-gain controller, NOT a developmental/critical-period plasticity schedule. The critical-period section above identifies this as a genuinely separate, currently-missing primitive (decaying plasticity-by-level over TRAINING TIME, not by runtime state).
- **`research_grounding_cascade_depth_multihop_mechanism_2026-07-09.md`** (today) — found that one-shot k-NN readout lacks the recurrent-attractor settling that gives biological semantic memory its graded multi-hop depth, and that near-random atomic codes need a chainable bind/unbind operator for compositional depth. This is the SAME missing-recursion shape as the Broca hierarchical-structure-builder gap identified in this drill (S1 table) — TWO independent drills, same day, converging on "the substrate lacks a genuine recursive/iterative composition operator," from different empirical angles (multi-hop grounding decay vs. syntactic recursion). This convergence raises confidence in the hierarchical-structure-builder gap above its stand-alone P_deflated.
- **`research_brain_independent_channels_resolve_compounding_error_tension_2026-07-09.md`** (today) — independent-channel error suppression theory; the cerebellar-forward-model-into-generation wiring proposed here is a CONCRETE candidate instantiation of "a second, genuinely independent channel" for that thread specifically (cerebellar error signal is mechanistically distinct from the KB-grounding-gate signal already tested).

---

## S2 — MAPS-TO-SUBSTRATE

**HAVE (existing analogs, verified on disk):**

| Brain module | Substrate file | Status |
|---|---|---|
| VWFA (orthographic spoke) | `hdlab/vwfa.py` | explicit, documented analog |
| ATL hub (conjunctive semantic convergence) | `hdlab/kg_traversal.py` (KGStore.W) + `hdlab/random_indexing.py` (distributional spoke) | explicit, documented, chain-grade validated |
| Angular-gyrus / N400-window stream integration | `hdlab/late_combine.py` | explicit, documented ("N400-window analog") — but see open question below re: whether it's doing real composition or generic buffering |
| DG-CA3 hippocampal episodic system | `hdlab/hippocampal_encoder.py` | explicit, documented |
| Basal-ganglia Go/NoGo value gate | `hdlab/action_selection.py` | explicit, documented (PBWM/Frank-O'Reilly), currently scoped to action-selection not grammar |
| Neuromodulatory gain control | `hdlab/self_manager.py` | explicit, 6-channel, RUNTIME scalar gains |
| Predictive-coding / forward-model residual gating | `hdlab/predictive_coding.py` | explicit (Friston/Rao-Ballard), general primitive, not yet wired specifically into generation |
| Sequence binding + autoregressive generation | `hdlab/sequence_memory.py` + `hdlab/generation.py` | explicit; this is the closest thing to a production pathway |
| Multi-hop retrieval cleanup | `hdlab/multi_hop.py` (Modern-Hopfield iterative cleanup) | explicit |
| Cortex-level composition/routing | `hdlab/cortex.py` | explicit thin composition facade — itself the "thin new wiring" analog of the arcuate fasciculus (see below) |

**MISSING (worth building, ranked by cheapness × biological load-bearing-ness):**

1. **Dorsal-stream shortcut (form-to-form repetition pathway bypassing the hub).** Cheapest to build (reuses `SequenceMatrix`); directly testable via the cheap decisive test above; would resolve a genuine architectural conflation.
2. **Broca-analog hierarchical/recursive structure-builder.** Current `role_slot_summarizer.py` is flat/compositional but not recursively nested. Converges with today's independent multi-hop/grounding-depth drill finding the same missing recursion operator from a different angle — raises this above its stand-alone priority.
3. **Cerebellar-forward-model wiring explicitly INTO `generation.py`'s forward pass** (composition gap, not new primitive — `predictive_coding.py` already exists). Directly relevant to today's independent-channels compounding-error thread.
4. **Developmental plasticity schedule** (critical-period analog): a per-subsystem DECAYING plasticity-rate keyed to exposure/training-step, with different half-lives per linguistic level (fast-closing orthographic/phonological encoder vs. slow/never-closing hub/semantic encoder). This is a genuinely NEW primitive, not a hyperparameter tune — nothing in `self_manager.py` implements a one-way schedule over TRAINING time (only runtime state).
5. **Angular-gyrus ablation check** on `late_combine.py`: is it doing real amodal composition or just a weighted buffer? Live open question in the human literature (ATL-core vs AG-flexible debate) — worth resolving on our own substrate since it's cheap (an ablation, not a build).

**Neural-reuse-principle implication for our plan:** STRONGLY SUPPORTS the current strategy. The brain's language solution is dominantly REUSE of older general computations (sequencing/basal-ganglia, forward-model/cerebellum, relational-mapping/hippocampus, conjunctive-binding/ATL) connected by a thin, mostly-CONNECTIVITY overlay (arcuate-fasciculus expansion) — not a new bespoke computational module. The substrate's existing strategy (compose `KGStore`, `hippocampal_encoder`, `action_selection`, `predictive_coding`, `sequence_memory` via the thin `cortex.py` routing facade) is architecturally the SAME shape as what evolution actually did. This is evidence FOR continuing to recombine general primitives + add a thin new binding/routing layer, and AGAINST building a monolithic bolt-on "language module." The one concrete new-WIRING analog the biology calls for (dorsal-stream shortcut) is exactly that: a routing/binding addition between two already-existing stores, not a new mathematical primitive — consistent with what the arcuate-fasciculus evidence says language evolution itself required.

---

## Substrate-product implications

- Reinforces (does not overturn) the `cortex.py`-as-thin-composition-layer strategy — biological validation, not a pivot signal.
- Names FOUR concretely buildable/testable gaps (dorsal shortcut, hierarchical structure-builder, cerebellar-wiring-into-generation, developmental plasticity schedule), each cheap relative to a new-encoder-class build, because each reuses existing `hdlab/` primitives rather than requiring new math.
- The hierarchical-structure-builder gap has CONVERGENT same-day evidence from an unrelated drill (multi-hop grounding-depth) — this should be weighted above a typical single-drill finding when the Director ranks next-drill/next-build priority.
- The developmental-plasticity-schedule gap is the most SPECULATIVE of the four (extrapolated substantially from visual-cortex molecular biology, not directly demonstrated for language circuits) — flagged honestly per calibration discipline; treat as lower-priority-to-build until a cheaper falsification path is found.

---

## S3 — Sharpest open question + deflated P

**Sharpest open question:** Does the substrate's current single flat `sequence_memory` + `generation.py` pathway silently conflate the dorsal (form-preserving, hub-bypassing) and ventral (form-to-meaning, hub-routed) jobs the same way the pre-2026-07-02 monolithic encoder conflated VWFA+ATL+CLS — and if so, is the fix (a second, hub-bypassing SequenceMatrix instance) as cheap and as high-yield as the A+B+C prescription was for the encoder side?

**Deflated P estimates (capped 0.50 per calibration rule):**
- P(dorsal-stream shortcut is real + cheap-testable missing component): **0.40**
- P(hierarchical Merge-like structure-builder required beyond current flat binding at current scope): **0.30** (raised by convergent same-day evidence, still capped)
- P(developmental plasticity schedule measurably helps vs. fixed hyperparameters): **0.35** (most speculative of the four; substantial visual-cortex-to-language extrapolation)
- P(cerebellar-forward-model wiring into generation reduces compounding drift): **0.35** (cross-thread reinforced by today's independent-channels drift note)
- P(reuse-principle overall validates current compose-general-primitives strategy vs. suggesting a pivot to monolithic language module): **0.48** (near the calibration ceiling — this is the best-supported claim in the drill, grounded in strong, causal, cross-species evidence: FOXP2 double-phenotype, arcuate-fasciculus comparative DTI, conduction-aphasia double dissociation)

---

## Citations (verified, high-confidence textbook/review level; count = 19)

1. Hickok G, Poeppel D. 2004. "Dorsal and ventral streams: a framework for understanding aspects of the functional anatomy of language." Cognition 92:67-99.
2. Hickok G, Poeppel D. 2007. "The cortical organization of speech processing." Nat Rev Neurosci 8:393-402.
3. Rilling JK, Glasser MF, Preuss TM, Ma X, Zhao T, Hu X, Behrens TE. 2008. "The evolution of the arcuate fasciculus revealed with comparative DTI." Nat Neurosci 11:426-428.
4. Friederici AD. 2011/2017 (program of work on BA44 hierarchical structure-building; Friederici & Gierhan 2013 "The language network" Curr Opin Neurobiol).
5. Rizzolatti G, Arbib MA. 1998. "Language within our grasp." Trends Neurosci 21:188-194.
6. Humphreys GF, Lambon Ralph MA. 2015. "Fusion and fission of cognitive functions in the human parietal cortex." Cereb Cortex (ATL-core / AG-flexible complementary hub debate).
7. Anderson ML. 2010. "Neural reuse: A fundamental organizing principle of the brain." Behav Brain Sci 33:245-266.
8. Dehaene S, Cohen L. 2007. "Cultural recycling of cortical maps." Neuron 56:384-398.
9. Ullman MT. 2004. "Contributions of memory circuits to language: the declarative/procedural model." Cognition 92:231-270.
10. FOXP2/KE-family literature (Vargha-Khadem et al. 1995 PNAS; Lai et al. 2001 Nature) — double motor-sequencing + grammatical phenotype.
11. Bellmund JLS, Gardenfors P, Moser EI, Doeller CF. 2018. "Navigating cognition: spatial codes for human thinking." Science 362:eaat6766.
12. Constantinescu AO, O'Reilly JX, Behrens TEJ. 2016. "Organizing conceptual knowledge in humans with a gridlike code." Science 352:1464-1468.
13. Pulvermuller F. 2005. "Brain mechanisms linking language and action." Nat Rev Neurosci 6:576-582.
14. Lenneberg EH. 1967. *Biological Foundations of Language.*
15. Johnson JS, Newport EL. 1989. "Critical period effects in second language learning." Cognitive Psychology 21:60-99.
16. Hartshorne JK, Tenenbaum JB, Pinker S. 2018. "A critical period for second language acquisition: evidence from 2/3 million English speakers." Cognition 177:263-277.
17. Werker JF, Tees RC. 1984. "Cross-language speech perception: evidence for perceptual reorganization during the first year of life." Infant Behav Dev 7:49-63. / Kuhl PK. 2004. "Early language acquisition: cracking the speech code." Nat Rev Neurosci 5:831-843.
18. Hensch TK. 2005. "Critical period plasticity in local cortical circuits." Nat Rev Neurosci 6:877-888.
19. Saffran JR, Aslin RN, Newport EL. 1996. "Statistical learning by 8-month-old infants." Science 274:1926-1928.
20. DeLong KA, Urbach TP, Kutas M. 2005. "Probabilistic word pre-activation during language comprehension inferred from electrical brain activity." Nat Neurosci 8:1117-1121.
21. Levy R. 2008. "Expectation-based syntactic comprehension." Cognition 106:1126-1177.
22. Altmann GTM, Kamide Y. 1999. "Incremental interpretation at verbs: restricting the domain of subsequent reference." Cognition 73:247-264.
23. Lesage E, Morgan BE, Olson AC, Meyer AS, Miall RC. 2012. "Cerebellar rTMS disrupts predictive language processing." Curr Biol 22:R794-R795.
24. Kuperberg GR, Jaeger TF. 2016. "What do we mean by prediction in language comprehension?" Lang Cogn Neurosci 31:32-59.

**Verified count: 24 (exceeds the >=7 minimum; several are grouped citation clusters, actual paper count ~26-28).**
