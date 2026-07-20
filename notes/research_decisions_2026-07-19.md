# Research decisions log — 2026-07-19

- 2026-07-19: BRAIN-DRILL (5x) on the COHERENCE/SCHEMA-FIT GATE component (N400/P600 neuroscience +
  predictive coding + Kintsch Construction-Integration settling + garden-path/good-enough/comprehension-
  monitoring failure modes) -> `notes/research_coherence_schema_fit_gate_brain_drill_2026-07-19.md`.
  Load-bearing disk finding: a first-draft coherence gate ALREADY EXISTS
  (`experiments/exp_role_filler_factorization_reader_coupled_cg_v1.py::schema_fit_gate`, `real_reader_gated`
  condition) and has NOT yet been dispatched — cheapest next action is running it as-is (zero new code)
  before building any upgrade. Ranked brain mechanism: two-signal gate (graded N400/prediction-error score
  conditioned on the CURRENT situation-model, not a static centroid; + a discrete P600-style structural-
  incoherence flag that escalates to CI-style bounded settling) plus a DEFERRED (not silently
  accept/reject) third state for genuinely ambiguous cases — mirrors the reactivation/reconsolidation shape
  already landed in the sibling memory-consolidation drill. Brain-check: settling-to-a-wrong-answer is a
  real shared bound (garden-path lingering misinterpretation) -> accept, design the DEFERRED state around
  it; good-enough/Moses-illusion ~40-50% miss rate is a brain FAILURE mode, not a capability to imitate ->
  fix is substrate-native always-on verification (beats brain baseline, doesn't just match it).
  P_deflated=0.50 (capped, novel-synthesis) for the two-signal design; individual cited mechanisms
  P~=0.55-0.65. No routing file written per USER-locked no-ferry discipline — the cheap decisive test
  (dispatch the already-existing cell) and the full FAIR can-fail spec are delivered inline in the note for
  the Director to hand to a cell-author directly.

- 2026-07-19: BRAIN-DRILL (5x) on LEARNED PARSING / ARGUMENT-STRUCTURE ASSIGNMENT (syntactic/semantic
  bootstrapping + Competition Model cue-weight learning + usage-based construction induction/retreat +
  neural/error-driven reanalysis) -> `notes/research_learned_argument_structure_parser_5x_brain_drill_2026-07-19.md`.
  Confirmed load-bearing bottleneck: hand-rule reader mis-attaches arguments in grammatical-but-wrong ways
  ("came,boy,eyes" etc.) that the sibling coherence-gate drill's gate cannot catch (they cohere). Ranked
  brain mechanism: LEARNED CUE-COMPETITION PARSING (Competition Model, language/construction-specific
  learned cue weights) scaffolded by usage-based CONSTRUCTION ABSTRACTION (generalization unit, not
  per-verb) + PREEMPTION/ENTRENCHMENT retreat (fixes coherent-but-wrong FPs without treebank, purely
  distributional) + a genuine PREDICTION-ERROR learning signal (Fitz & Chang 2019's literal
  error-propagation account of N400/P600 -- brain-validates "coherence as training signal, not treebank").
  Designed a concrete glass-box Learned Cue-Competition Parser (LCCP, 6 steps) that composes with the
  existing candidate-generator, the 07-17 dependency-stack WM finding, and the sibling coherence-gate's
  accept/flag/reject output as its only training signal. FAIR Arm A(baseline)/B(cue-learning only)/
  C(full, construction-shared) can-fail test with a held-out verb x construction split isolating
  compositional generalization. P_deflated=0.30-0.45 (novel-synthesis capped); largest named risk =
  Prediction 4 (whether coherence-only feedback is informative enough to drive retreat on cases that are,
  by construction, coherent). Brain-check: coherent-but-wrong is a real SHARED human limitation too
  (garden-path lingering misinterpretation, Moses illusion) -- if it HARD-FAILs even so, the honest
  substrate-native fallback (not brain-imitative) is an always-on document-scope consistency check a
  biological reader's attention economy cannot afford. No routing file written per USER-locked no-ferry
  discipline -- ranked actionable anchors, full design, and FAIR test delivered inline in the note.

- 2026-07-19: BRAIN-DRILL (5x) on the COMPRESS-AND-CARRY / SITUATION-MODEL-GUIDED comprehension LOOP
  (Kintsch CI-as-computational-loop + constraint-based/referential-theory top-down parsing + Bransford/
  Stanovich compounding-schema literature + van Dijk-Kintsch macrorules/Ericsson-Kintsch LTWM/Zwaan-
  Gernsbacher event-segmentation) -> `notes/research_situation_model_guided_comprehension_loop_compress_and_carry_2026-07-19.md`.
  The culminating same-day synthesis: wires the WSM's Tier 2/3 (from the 07-17 discourse-state-of-mind
  note) into the LCCP's Step 2/3 scorer (from today's parser note) as a new document-coherence feature,
  reusing the coherence-gate's settling/DEFERRED machinery for conflicts, and fulfills the LCCP note's own
  contingent anchor #3 (substrate-native document-scope consistency check) directly rather than waiting for
  its Prediction 4 to HARD-FAIL first. Ranked mechanism: SITUATION-MODEL-GUIDED CONSTRUCTION-INTEGRATION
  with MACROSTRUCTURE-COMPRESSED CARRY -- over-inclusive candidate construction (unchanged), document-
  coherence integrated as ONE weighted parallel feature (not a late rerank -- resolved via constraint-based/
  referential-theory literature), a carried reference that is macrorule-compressed and LTWM-cue-addressable
  rather than raw-accreted, checkpointed at PE-detected discontinuity boundaries (MAP vs SHIFT). Honest
  finding: NO direct human-literature precedent, in either direction, exists for a within-single-document
  compounding curve (Stanovich's Matthew effect and Bransford-Johnson schema-priming are developmental/
  cross-session, not within-one-document) -- the compounding prediction is a genuinely novel test, not a
  replay of known human data. 3-arm FAIR test (Arm 1 LCCP baseline / Arm 2 +situation-model feature, no
  compression / Arm 3 full compress-and-carry) isolates precision-raise, compounding, and whether
  compression specifically (vs. just having a carried state) drives it. P_deflated=0.32 (composes three
  already-capped novel-synthesis notes); Prediction 2 (compounding) lowest at P=0.25, reflecting the total
  absence of a literature floor. Brain-check: settling-to-wrong and the LTWM relocated-not-lifted WM bound
  are real shared limits (accept, DEFERRED state and compression discipline already designed around them);
  some mis-attachments resist even human discourse-context override (Mitchell/Corley/Garnham, Britt) --
  accept as an honest ceiling, not a design failure. No routing file written per USER-locked no-ferry
  discipline -- cheap decisive test, full FAIR arm/threshold spec, and cross-thread pointers delivered
  inline in the note.
- NP-head/argument-head candidate-generation brain-drill delivered -> notes/research_np_head_candidate_generation_grounding_gate_5x_brain_drill_2026-07-19.md (two non-redundant gates: structural-position + graded grounding/entity-hood; fields/table = position failures, regular = entity-hood failure; single-gate fix insufficient; P_deflated 0.30-0.50 per component)

- 2026-07-19: BRAIN-DRILL (5x) on the ARGUMENT vs ADJUNCT distinction (why "came HOME"/"stood THERE" get
  mis-licensed as PATIENT, since selectional coherence is orthogonal to subcategorization here) ->
  `notes/research_argument_adjunct_distinction_brain_drill_2026-07-19.md`. Third, non-redundant layer atop
  same-day GHC (fixes wrong-TOKEN candidates) and LCCP (fixes wrong-candidate-scored-highest): this drill
  fixes wrong-ROLE-ELIGIBILITY -- a correctly-grounded, correctly-positioned constituent offered as PATIENT
  when it should never be role-eligible for PATIENT at all. Found the linguistic-theory literature itself
  treats argument/adjunct as gradient, not binary (Przepiorkowski, Toivonen -- classic diagnostics
  mutually inconsistent), with a documented intermediate "derived argument" category (Needham & Toivonen
  2011) formalizing exactly the "came home" case (VerbNet Destination role + PropBank's own AM-DIR-vs-ARG4
  hedge). Ranked mechanism: GRADIENT VERB-FRAME-SPECIFICITY GATING (distributional verb-diversity/entropy,
  mirroring PropBank's own ARG-N-vs-AM-* design logic, computationally validated by Korhonen/Villavicencio/
  Kim et al. 2019) + verb-class-conditioned FRAME-TYPE membership (Friederici & Frisch 2000's ERP
  dissociation: frame-TYPE violations are P600-only, frame-NUMBER violations are N400+P600 biphasic -- a
  real, distinct brain gate) + an explicit DERIVED-ARGUMENT/DEFERRED middle state (reusing the sibling
  coherence-gate's pattern) instead of a forced binary. Designed the Role-Eligibility Cascade (REC): Signal
  0 (cheap categorial prior -- bare locative/temporal/manner adverbial categories excluded from PATIENT
  candidacy by default) + Signal 1 (learned verb-diversity entropy, generalizes to bare-NP adjuncts like
  temporals) + Signal 2 (construction-level frame-type membership). FAIR Arm A/B/C/D test targets the
  ~23-case came-home-class residual on the existing LCCP/GHC gold, with a gate-decomposition check
  (mirrors GHC Prediction 3) isolating whether the cheap category prior alone does most of the work.
  P_deflated=0.35-0.45 (novel-synthesis capped); cheapest highest-confidence first build = Signal 0 alone.
  Brain-check: the field's own diagnostic tests conflicting (same-limit, accept -- design the three-way,
  not binary, outcome around it, per Needham & Toivonen); corpus-sparsity for Signal 1's entropy estimates
  is a real, separately-tested bound (Prediction 4) -- if it HARD-FAILs that is a corpus-scale limit, not
  an REC design defect, and Signal 0 should be weighted more heavily until more corpus is ingested. No
  routing file written per USER-locked no-ferry discipline -- ranked actionable anchors, full REC design,
  and FAIR arm/threshold spec delivered inline in the note.

- 12:26: cross-document compounding via consolidation drilled (3 lit-scans: Documents Model/knowledge-threshold/self-training-decorrelation theory) -> notes/research_cross_document_compounding_consolidation_viability_2026-07-19.md ; P_deflated=0.22; cheap pre-check = confidence-correctness correlation on existing eval data (free, decisive before any build); next-drill candidate: F4 free cumulants or the decorrelated-second-view build if pre-check passes.
- Open-licensed modern graded-reader corpus scan (second series alongside McGuffey) -> notes/research_open_licensed_modern_graded_reader_corpus_second_series_2026-07-19.md ; rank#1 Bloom Library (sil-ai/bloom-lm HF), translation-risk unconfirmed; recommend cheap pilot acquire now, defer full ladder.
- 2026-07-19: McGuffey source-apparatus distillation (teacher-pedagogy, primary-text mining) -> notes/research_mcguffey_source_apparatus_teacher_pedagogy_distillation_2026-07-19.md

- 2026-07-19: BRAIN-DRILL FORK-C (compounding + end-to-end-in-substrate; 2 lit-scans -- native-binding-
  acquisition/predictive-coding; Zacks Event Segmentation Theory/hippocampal-boundary/indexing/prioritized-
  replay) -> `notes/research_fork_c_compounding_end_to_end_substrate_loop_2026-07-19.md`. Composes with, does
  not re-derive, the three same-day sibling notes (CCL compress-and-carry HARD_FAIL + redirect, cross-doc
  consolidation viability 0.22, VSA envelope). Two NEW findings, outcome not pre-assumed: (1) NO brain-model
  precedent exists for LEARNING the binding operator itself (synchrony models learn grouping not a
  compositional operator; every VSA/HRR/SPA brain model treats the bind algebra as GIVEN, only content is
  learned) -- since the substrate's Stage-1 bridge already gives a validated zero-training FHRR bind, this
  DEPRIORITIZES "reader-forms-HD-natively" as a build target; all FORK-C learning routes to the
  selection/scoring/consolidation POLICY layer instead (matches both biology and the already-built LCCP/
  coherence-gate/consolidation designs). (2) Zacks EST + hippocampal-boundary/indexing/Mattar-Daw replay-
  priority literature independently reinforces (7th convergent literature) the sibling notes' PE-triggered
  MAP/SHIFT + LTWM-cue design, with two honest new caveats: PE-vs-generic-discontinuity as boundary trigger
  is an active unresolved debate; Mattar-Daw gain x need has no literature precedent at event-segment
  granularity (this drill's own capped-P bridge). Ranked mechanism: FIXED-OPERATOR, LEARNED-POLICY
  STRUCTURED COMPREHENSION-CONSOLIDATION LOOP -- the SAME live FHRR bind/bundle map at every scale (Tier-2
  event-scoped, Tier-3 cross-document via compression at PE-detected SHIFT boundaries). First buildable
  component, sequenced: Step 0 (near-zero-cost, mostly already run) = redundancy-signal decorrelation check
  vs the coherence gate (cross-doc note's own Prediction B, still missing) -- gates cross-doc consolidation
  viability independent of representation. Step 1 (the actual build) = the structured within-document
  role/event FHRR carry, CCL's own named non-closed/untested variant, reusing CCL's harness verbatim with
  ONE substitution (FHRR bind/bundle replaces the HARD-FAILED topical centroid), directly exercising 2 of
  the VSA-envelope note's named GAPS (incremental bundling; consolidation-over-time fidelity). P_deflated
  =0.30 for the composed design; Predictions 1/2/3 = 0.30/0.20/0.25 (Prediction 2 deflated BELOW CCL's own
  0.25 -- the bar is now "beat CCL's already-measured +0.189 order-effect floor," not merely "positive
  slope"). No routing file written per USER-locked no-ferry discipline -- sequenced Step 0/Step 1 build
  order, cheap decisive test, and full FAIR arm/threshold spec delivered inline in the note.

- **Integrated graded-experiential reader viability + corpus precondition** (decisive fork-check on the SCV
  post-hoc-contrastive HARD_FAIL): notes/research_integrated_graded_experiential_reader_viability_corpus_precondition_2026-07-19.md.
  Escapes post-hoc closure YES (P=0.45, deflated) on the general per-step-vs-global-scalar credit-assignment
  argument (RL credit-assignment + SSL-collapse literatures converge); concrete architecture = McRae/Spivey-Knowlton
  CIM normalized-recurrence weighted-sum-plus-feedback for USE, per-step delta-rule for LEARN (CIM's own paper
  fits weights offline, doesn't demonstrate online learning -- that's the novel piece). Corpus precondition
  resolved as a SCOPE split, not a single verdict: learning NEW distributional thematic-fit values is corpus-gated
  (needs >=1M words minimum per Resnik, realistically 100M-1B+ per Erk/Baroni-Lenci) -- 99k words is far below
  every precedent; but learning only the LOW-DIMENSIONAL cue-integration weights ON TOP OF the already-built
  WordNet/VerbNet categorical scaffold is buildable now, same scale as the LCCP's existing cue-weight vector.
  Recommendation: BUILD NOW, narrowly scoped, with a mandatory firing-rate diagnostic (Control 1) to distinguish
  "sparse-event coverage gap" from "mechanism null" -- this is the same ambiguity that could be silently hiding
  inside the SCV's own already-per-cue-attributed but 0.000-delta result.
- structural residual + learned-reader-pivot brain drill -> notes/research_structural_residual_and_learned_in_substrate_reader_pivot_2026-07-19.md (case-b=constructional not world-knowledge; carry-context=same-wall; factorization-core=shared-binding-formalism not literal-shared-circuit; next build=preposition-class feature on symbolic front-end)
- 2026-07-19: BRAIN-DRILL + strategic edge-check on INCOMPLETE-KG REASONING (link prediction /
  conjunctive-query answering): NO genuine glass-box VSA edge found, confirmed both externally
  (HRR/FHRR parity with RotatE single-hop, chance-level at 2-hop; BetaE conjunction gain = generic
  answer-set-shrinkage math) and via this project own already-landed in-house history (native
  Hebbian KGStore ceiling 0.0231 MRR vs SGD-trained additive map 0.1282 MRR on real CSKG; crux-engine
  pure-VSA attempt HARD_FAILed on real FB15k-237). Gap-filling IS a learned brain capability but the
  brain solves it via slow statistical extraction (biological analog of training), not glass-box
  algebra. VERDICT: path (A) incomplete-KG chain-grade CLOSED; path (B) extraction/grounding confirmed
  as the sole genuine chain-grade thread -> `notes/research_brain_incomplete_kg_reasoning_substrate_edge_or_extraction_pivot_2026-07-19.md`.

- Platform maturity audit (5x drill, base-element brain-sufficiency): capacity MATURE (brain-matched
  headroom, m<=24 robust vs brain's ~4-24 relational ceiling); discourse/WM buffer SETTLED (two-layer,
  already built+VET'd this session, independently converges with situation-model lit); cleanup/attractor
  memory IMMATURE (measured hard step-function sigma 2.0->3.0, brain has graded experience-shaped basins;
  cheap fix available, modern-Hopfield already validated on disk); encoding PARTIALLY mature (structure/
  content split correct+validated, content vectors not yet similarity-structured in production); MOST
  LOAD-BEARING MISSING element = error-driven/predictive-coding correction loop around the extractor (does
  not exist in any form; the closed SCV was one candidate implementation, not the general requirement;
  independently explains both construction-determined chain-grade attempts and the closed glass-box
  extraction ceiling). Build order: (1) cleanup swap, (2) correction loop [crux], (3) similarity-structured
  content. -> `notes/drill_platform_maturity_base_elements_brain_sufficient_5x_2026-07-20.md`.

- 2026-07-19/20: Deep brain drill (5x, given session failures) -> notes/drill_brain_how_it_does_it_given_failures_5x_2026-07-20.md.
  Geometry-learning is a hybrid (scaffolded attractor manifold + learned predictive binding, TEM/SR), NOT
  simply "learned from grounded experience"; grounding demoted to sufficient-not-necessary for a trainable
  error signal (strongest N400 models are amodal). Single unifying mechanism whose absence explains all 3
  failures: contrastive predictive coding over RIVAL hypotheses scored against real exogenous data (not a
  single scalar coherence score) -- explains why the gold-perfect SCV oracle still didn't train (no rivalry,
  no real-data target). Buildable now via re-wiring existing parts (predictive_coding.py + SCV rival
  candidates + corpus-precondition cue-weight scope). P_deflated=0.42, 3-arm must-fail test pre-registered.

- drill_all_negatives_3x_unifying_root_2026-07-20.md -- deep 3x drill across all 7 VET-confirmed negatives (N1-N7): TWO roots not one (Root1=free-algebra/construction-determined [N1,N2,N5, truly closed] vs Root2=learning-signal preconditions [N3,N4,N6,N7, each a DIFFERENT proximate blocker: rivalry/N4-open-cheapest, codebook-SNR/N6-closed-for-rule-open-for-code, corpus-discriminability/N7-honest-null-open]); highest-leverage next move = retest N4 CPC-rival-vs-real-data 3-arm before N6 codebook redesign or N7 corpus effort.

- drill_uncertainties_4x_learning_loop_target_and_corpus_2026-07-20.md -- 4x drill on the CPCL null (3.7%
  vs 20% discriminator threshold): best predictive target = entity-recurrence/coherence (Centering/entity-
  grid), not bag-of-words content bundle; "richer corpus" is more likely a scapegoat than real requirement
  (ALBERT NSP-vs-SOP precedent = near-exact structural match, fix = scoring-design not data-acquisition),
  with a narrower unverified residual risk (distinct-entity/character diversity, not vocab size); brain
  prediction distinctiveness-vs-competitors is a genuine open/unstudied question for graded-reader text
  specifically; loop-redesign + learned similarity-structured codebook (Random-Indexing/BEAGLE glass-box)
  converge on the same skip-gram-equivalent mechanism, build as one staged sequence (codebook first).
  Cheap decisive test pre-registered (Test A: re-target CPCL's continuation_vec + within-lesson shuffle,
  reuse existing harness, before any corpus change).

- scour_self_monitoring_build_and_prior_art_3x_2026-07-20.md -- 4 parallel lit-scans on the self-monitoring
  layer (metacognition/abstain + attention/salience), both flagged as LOAD-BEARING TOTAL GAPS. Metacognition:
  Chow reject-rule + post-hoc OOD scores (margin/entropy/Mahalanobis) + meta-d'/M-ratio all ADOPT closed-form;
  `hdlab/conformal.py` correct but INCOMPLETE (needs Mondrian per-partition quantile + Gibbs-Candes adaptive-
  alpha for drift + explicit set-size abstain rule) before production-ready. Attention: Kalman-gain precision-
  weighting + Reynolds-Heeger divisive normalization + sparsemax are the 3 strongest zero-training candidates;
  existing surprise ingest signal likely already implements IDF/contrast-style salience -- missing piece is a
  reliability multiplier + hard-gate, not a new signal. P_deflated<=0.45 all claims (cap 0.50). 41 citations
  (sub-agent-reported, not independently re-verified this cycle). Cheap decisive tests pre-registered (both
  pure-CPU synthetic, no corpus needed): Test A (drift-schedule conformal coverage), Test B (noisy-channel
  precision@k).
