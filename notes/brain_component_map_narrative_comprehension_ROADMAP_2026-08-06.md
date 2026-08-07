# BRAIN-COMPONENT MAP for narrative goal-outcome comprehension -> substrate status + prior art (ROADMAP)

**Purpose (USER-requested 2026-08-06):** the full set of brain components that contribute to reading a narrative and
understanding "who wanted what, and did it work out" -- each tagged for its status in OUR glass-box HDC/VSA substrate
(OWNED / PARTIAL / MISSING) and cross-referenced to what prior art actually IMPLEMENTED. Doubles as a build roadmap:
MISSING + PARTIAL = the frontier. Brain = the project's reference standard (existence proof).
Companion detail: notes/audit_SYNTHESIS_semantic_meaning_barrier_2026-08-06.md + notes/drill_brain_grounding_wall_definitive_2026-08-06.md
+ the prior-art scans (notes/prior_art_*_2026-08-06.md).

## MASTER TABLE

| # | Function (contribution to the task) | Brain region(s) | How | OUR substrate status | Our organ |
|---|---|---|---|---|---|
| 1 | Read marks -> word form -> lexical access | VWFA (fusiform), posterior MTG | orthography->wordform->meaning entry | N/A (we start from tokens) | tokenizer / lexicon lookup |
| 2 | **Word MEANING (semantics) + its GROUNDING** | **ATL semantic hub** + grounded SPOKES: sensorimotor, **OFC/vmPFC, amygdala, insula (affective/interoceptive)** | amodal concept = graded pattern distilled from experience; abstract/eval words grounded in felt affect | **PARTIAL (hub) / MISSING (grounding)** = THE WALL | lexical_similarity (ATL analog, but SUPPLIED features); affective spokes ungrounded |
| 3 | Sentence structure (who-did-what-to-whom) | LIFG (unification), hippocampus (relational binding); role-filler tensor code | bind fillers to roles; combine into propositions | **OWNED (most brain-faithful)** | FHRR bind (role*filler)+bundle; fMRI-vindicated (Lalisse-Smolensky) |
| 4 | Track entities across the story (coref) | hippocampus/MTL; medial PFC, precuneus | maintain distinct entity reps; resolve pronouns | **PARTIAL (debugging now)** | coref / event_centrality_coref -- the negator-poisoning bug is here |
| 5 | **Integrated running SITUATION MODEL** | **Default Mode Network** (mPFC, PCC/precuneus, angular gyrus, lat. temporal); event-segmentation net | one integrated, continuously-updated model: entities/space/time/cause/**intent/protagonist**; segment at prediction-error boundaries | **MISSING (the big frontier)** | thin goal/outcome/causal registers only; no integrated DMN-style model |
| 6 | **Read minds -- goals & intentions** | **mentalizing net: mPFC, TPJ, precuneus, STS** | attribute wants/beliefs to agents; inverse-planning (Bayesian ToM) | **PARTIAL** | goal-recognition (find_desired_state, conative/intention); ToM organ (islanded HARD_PASS, unwired); goal-owner select |
| 7 | Hold the goal + monitor the outcome | dlPFC (maintenance), **ACC (expectancy-violation/monitoring)**, frontopolar (superordinate) | keep goal active; flag outcome-vs-goal mismatch | **PARTIAL / BUILDING** | congruence_decision (monitor); **did-it-happen occurrence-gate = the ACC analog (in progress)** |
| 8 | **Value the outcome -- did it happen, good/bad** | **OFC/vmPFC (content-blind value), ventral striatum + dopaminergic VTA/SNc (reward-prediction-error)** | value outcome vs goal in common currency; RPE reads value AND is the teaching signal that GROUNDS meaning over development | **PARTIAL (structural) / MISSING (grounded)** | congruence (structural MET/UNMET); grounded_appraisal_sim_earned (RPE-earned but TOY-WORLD only, not wired to words) |
| 9 | Feel the stakes (narrative affect) | amygdala, insula, vmPFC | felt emotional response to events -> outcomes MATTER | **PARTIAL / MISSING** | EventRecord.affect dim + affect-bridge; felt stakes grounding-limited (=the wall) |
| 10 | Bridge gaps / causal inference | constructionist inference (Graesser); hippocampus (assoc retrieval) + LIFG + ATL/DMN; integration = settling | infer unstated resolutions; integrate to coherence | **OWNED (a genuine success)** | bridging-inference (praise/affect bridges, HARD_PASS) |
| 11 | Prediction (the engine underneath) | pervasive predictive coding across the hierarchy | predict next word/event/outcome; prediction-error drives updating+learning+segmentation | **OWNED (thin)** | predictive_coding novelty organ |

## PER-COMPONENT NOTES (status honesty)
- **#2 GROUNDING = the load-bearing wall.** We have the ATL-hub MECHANISM (shared-feature cosine, brain-faithful) but the FEATURES are supplied, and the AFFECTIVE spokes (where "waste=bad" is grounded via felt loss) are what we cannot fully give a program. This session PROVED no text/structure/dictionary shortcut earns it (5 HARD_FAILs). Reward-PE (grounded_appraisal_sim_earned) is the brain's grounding route AND we own a toy-world version -- but it grounds situation-TYPES in a wordless world, not word meanings. This is the deepest gap.
- **#3 BINDING + #10 BRIDGING = our two genuinely brain-faithful, working pieces.** Leverage these.
- **#5 SITUATION MODEL = the biggest structural gap.** The brain reads outcomes off ONE integrated model relative to the goal; we have a pipeline of local organs that fire on explicit cues and miss the implicit. This is the "read situations, not words" pivot's true endpoint. The did-it-happen work (#7) is a first component of it.
- **#7 did-it-happen** is literally the ACC expectancy-violation function -- comparing the arriving outcome against the maintained goal. Brain-foundationally exact. (Currently starved by #4 referent extraction -- the fix in flight.)
- **#8 valuation is content-blind in the brain** -- it values whatever comprehension hands it. Our MET/UNMET is structural (congruence), which is the right shape for the "did the goal get satisfied" judgment; the FELT valence (grounding) is the separate #2/#9 gap.

## ROADMAP (derived)
- **OWNED -> LEVERAGE:** role-filler binding (#3), bridging inference (#10), predictive-coding (#11 thin).
- **PARTIAL -> STRENGTHEN (current session's convergence):** referent tracking (#4, fixing now), mentalizing/goal-recognition (#6), goal-monitoring/**did-it-happen** (#7, building), coref-owner-attribution (#4/#6, sized+queued). These are the near-term targets, evidence-confirmed.
- **MISSING -> FRONTIER:** the integrated **situation model** (#5) and **grounded affective valuation** (#2/#8/#9 = the grounding wall). The situation-model is buildable incrementally (did-it-happen is a first piece); the grounding wall is the deep, field-oldest hard problem.

## PRIOR-ART CROSS-REFERENCE
### Area 1 -- CLASSICAL SYMBOLIC (DONE, notes/prior_art_classical_symbolic_story_understanding_2026-08-06.md, b9d618cfa)
- **No working robust open-domain glass-box goal-outcome story-understander ever existed.** The REPRESENTATION was solved well: Lehnert **Plot Units** (1981, goal success/failure = event-polarity linked to a character goal-state; ownership structural) = our #7+#6+#4; Trabasso & van den Broek **causal-network episode** (1985: Setting/Event/Internal-Response/**Goal/Attempt/Outcome**, explicit Outcome node, human-recall-validated) = a completeness checklist for #5/#7; TALE-SPIN (1976) explicit SUCCEEDED/FAILED flag = #7, its drowning-failure a warning about implicit world-model preconditions.
- **THE UNIFORM 45-YEAR KILLER: hand-coded input; no automatic route from raw open-domain prose to the representation** (AESOP 2010 only partway with modern NLP). => "mechanism correct but starved on real prose" is the FIELD'S OLDEST terminal failure mode, NOT our design error. This is the #2-grounding / #5-situation-model bottleneck restated historically.
- **Reusable, ranked:** (1) Trabasso Goal->Attempt->Outcome schema as a structural completeness check for our registers; (2) Lehnert 4-type causal-link taxonomy (motivation/actualization/termination/equivalence) as a vocabulary check for our relation types; (3) TALE-SPIN outcome-flag + its world-model-precondition warning.
### Area 2 -- MODERN NEURO-SYMBOLIC (PENDING, a801807a) -- to fold in.
### Area 3 -- VSA/HDC FOR LANGUAGE (PENDING, a21f0721) -- to fold in.

## BOTTOM LINE
The brain does this with a DISTRIBUTED, INTEGRATED system centered on (a) a grounded semantic hub (#2), (b) an integrated situation model (#5) built by mentalizing+entity-tracking+prediction, and (c) reward-grounded valuation (#8). We are genuinely brain-faithful on binding (#3) + bridging (#10); the frontier is the situation model (#5) + grounded valuation (#2/#8). The classical lineage confirms the goal/outcome REPRESENTATION is sound and the bottleneck is the raw-prose->representation route = exactly the wall we are attacking with grounding + situation-state reading. NOT a design error; the field's central hard problem, which the brain proves is solvable.
