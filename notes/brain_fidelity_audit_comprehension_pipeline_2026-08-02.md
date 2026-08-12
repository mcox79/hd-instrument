BRAIN-FIDELITY AUDIT: comprehension pipeline built this session (2026-08-02)
LOCAL ONLY, no push. Director-authored (read-only audit, no cell dispatch).

PURPOSE: honest classification of every component in the current extraction/situation-model/
self-correction pipeline as (A) brain-faithful learned mechanism, (B) brain-compatible but
hand-coded scaffold (computes the right thing via engineered rules, NOT learned -- flag for
replacement), (C) supplied data (allowed), or (D) not brain-faithful. Triggered by a USER check
("are we staying brain-foundational or just improving?") after this session hand-coded several
clause-parser fixes (segmentation, PP-disqualification, relative-clause rules) that compute the
brain's default (subject=agent per clause) via engineered rules rather than a learned mechanism.

Every claim below is tagged CITED (specific paper/finding), REASONED (my inference, no direct
citation), or MEASURED (read off metrics.json / code, not interpretation). Deflated per standing
discipline -- no claim of "brain-faithful" is made without naming what would make it NOT so.

=================================================================================================
PER-COMPONENT TABLE
=================================================================================================

1. MENTION FEATURE CONSTRUCTION (mention_features_multi, sent_summary construction in
   build_sentence_multi / build_sentence_multi5 / build_sentence_multi6)
   Files: exp_extraction_construction_conditional_multirole_v1.py (imported),
   exp_extraction_commit_then_revise_v2.py / v3_theme.py.
   CLASS: (B) hand-coded scaffold.
   WHAT IT DOES: computes a fixed set of boolean/scalar cues per mention (in_quote, after_close,
   follows_verb, is_subject, in_passive_ctx [token-distance window], follows_by [token-distance
   window], comma_after) and per-sentence (verb_after_close, frac_in_quote, has_be, has_by,
   is_copular). These are the INPUT FEATURES to the learned softmax (component 2).
   BRAIN-GROUNDING: cue-based sentence comprehension (Bornkessel-Schlesewsky & Schlesewsky's
   eADM / MacWhinney & Bates Competition Model) posits that comprehension integrates a small set
   of morphosyntactic/positional/prosodic CUES (word order, case marking, animacy, prosodic
   boundary) [CITED: Bornkessel-Schlesewsky & Schlesewsky 2009 eADM; MacWhinney, Bates & Kliegl
   1984 Competition Model]. The EXISTENCE of a small cue vocabulary is well supported. What is NOT
   supported by citation is that cues like "token is followed by a comma" or "token is within 3
   tokens of a BY-tagged ADP" are the brain's actual primitives -- these are ENGINEERING
   approximations of the cues the literature describes (case marking, prosodic phrasing, animacy),
   built because we have no learned phrase-structure/prosody detector yet [REASONED].
   LEARNED REPLACEMENT: a feature-learning front end (e.g. a small recurrent/attention encoder
   trained end-to-end with the role-classification objective, or trained first via distributional/
   statistical segmentation on unlabeled text -- Saffran-style statistical learning of boundaries
   [CITED: Saffran, Aslin & Newport 1996] -- then frozen as a primitive) that DISCOVERS which local
   token contexts predict passive/quotative/subject structure, rather than a hand-specified
   window-and-tag rule.

2. REVISE SOFTMAX (fit_softmax / mention_features_multi -> per-mention role logits; L2_LAMBDA,
   LR, N_ITERS gradient descent)
   Files: exp_extraction_construction_conditional_multirole_v1.py, reused across v2/v3/v4.
   CLASS: (A) brain-faithful learned mechanism, GIVEN (B)'s features as input.
   WHAT IT DOES: a multinomial logistic regression fit by gradient descent (L2-regularized) over
   the hand-built feature vectors, per LOOCV fold.
   BRAIN-GROUNDING: cue-INTEGRATION weights (as opposed to cue detection) are argued to be
   LEARNED from exposure -- the Competition Model's "cue validity/strength" is explicitly a
   learned, experience-tuned quantity [CITED: MacWhinney & Bates 1989, "The Crosslinguistic Study
   of Sentence Processing" -- cue strength as a function of frequency+reliability, acquired via
   exposure]. A linear/softmax weighting over fixed cues, fit by gradient descent, is a reasonable
   coarse analog of this cue-weight learning (a connectionist unit, not the cue detectors
   themselves) [REASONED at the level of "gradient descent over interpretable features" as a
   stand-in for the brain's cue-weight tuning; this is NOT a claim that logistic regression is
   itself a neural mechanism].
   HONEST CAVEAT: the softmax is a SHALLOW linear model over hand-features -- genuinely learned
   PARAMETERS, but a very small hypothesis class. This is fine as the calibration/integration
   layer but should not be over-read as "the reader learns roles" when the feature layer beneath
   it (component 1) is doing most of the representational work.

3. CLAUSE-LEVEL AGENT=SUBJECT DEFAULT (segment_clauses / segment_clauses_v3, BOUNDARY_WORDS,
   RELATIVE_BOUNDARY_WORDS, clause_position_predict / clause_position_predict5,
   _immediately_follows_prep)
   Files: exp_extraction_commit_then_revise_v2.py (segment_clauses, clause_position_predict),
   exp_extraction_commit_then_revise_v3_theme.py (segment_clauses_v3, clause_position_predict5,
   _immediately_follows_prep -- the two additive 2026-08-02 fixes named in the task).
   CLASS: (B) hand-coded scaffold -- THE KEY CATEGORY the USER asked to surface.
   WHAT IT DOES: splits token stream into clause spans by a fixed CCONJ/SCONJ word-list plus
   surface-form special cases ("when" mistagged ADV, "which/who/whom" added in v3), then within
   each span picks the first non-quoted, non-PP-object mention as agent, everything else patient.
   Zero learned parameters anywhere in this path -- pure hand-specified control flow, including
   the token-distance PP-disqualification lookback window.
   BRAIN-GROUNDING: the TARGET behavior (default first-mention/subject = agent, revised only
   under marked cues) is well-grounded -- canonical-sentence / "first-NP = agent" default
   strategies are documented cross-linguistically as an OVERLEARNED heuristic used pending
   further cues [CITED: Bever 1970 "canonical sentoid strategy"; MacWhinney & Bates Competition
   Model word-order cue]. Clause-by-clause (not whole-sentence) incremental structure-building is
   also well-grounded [CITED: Friederici's neurocognitive model of sentence processing, phase-based
   incremental structure building ~ELAN/N400/P600 stages]. So the WHAT (clause-local default,
   subject-first bias) is brain-target-correct. The HOW (a fixed English conjunction word-list,
   an ad hoc token-distance disqualification rule for fronted PPs, and a hand-added relative-
   pronoun boundary set) is NOT how the brain does clause segmentation -- human clause-boundary
   detection is argued to draw on PROSODY (pause, pitch reset, final lengthening) and statistical/
   distributional co-occurrence learned over childhood exposure [CITED: Cutler & Isard on prosodic
   phrase boundaries as clause-boundary cues; de Villiers & de Villiers on syntactic bootstrapping
   from distributional regularities], not a memorized closed-class word list assembled by an
   engineer reading failure cases. This cell's own docstring is explicit that BOUNDARY_WORDS,
   RELATIVE_BOUNDARY_WORDS, and _immediately_follows_prep were each authored in direct response to
   specific measured failures (13/26 end-to-end mislabels) -- i.e., these are HAND-PATCHES to
   specific observed errors, the textbook definition of a scaffold rather than a generalizing
   learned mechanism [MEASURED, from the module docstring's own GAP 1/GAP 2 diagnosis].
   LEARNED REPLACEMENT: a clause/constituent-boundary DETECTOR trained on annotated boundaries
   (even a small logistic/sequence model over POS-tag n-grams + punctuation + prosodic-proxy
   features, analogous to component 2's softmax but for BOUNDARIES instead of roles) so that
   "does a PP precede this mention" and "is this a relative-clause opening" are discovered cue
   WEIGHTS rather than hand-listed word sets. This is the single most actionable B-to-A conversion
   named in the task's framing, and I agree it is the most drift-flagged component in the pipeline.

4. is_copular GATE / GATE_FIRES (gate_fires_v2, gate_fires_v3, THRESH, is_copular boolean logic)
   Files: exp_extraction_commit_then_revise_v2.py / v3_theme.py.
   CLASS: (B) hand-coded scaffold (construction-cue DETECTION), feeding an (A) MARGIN mechanism
   (see component 5).
   WHAT IT DOES: boolean disjunction of has_by, quotative_cue (frac_in_quote > hand-picked THRESH),
   is_copular (has_be AND NOT has_by AND NOT be_then_verb) -- each conjunct is a hand-specified
   surface-pattern rule, and THRESH itself is a value reused verbatim from a prior grid-search
   (not re-learned here).
   BRAIN-GROUNDING: detecting that a MARKED CONSTRUCTION is present (passive, quotative inversion,
   copular-identity) before applying construction-specific reanalysis is grounded in eADM's
   construction-cue detection stage and in P600/reanalysis literature (a marked-construction cue
   like "by" or inverted word order triggers reanalysis) [CITED: Bornkessel-Schlesewsky &
   Schlesewsky eADM; Osterhout & Holcomb 1992 P600 reanalysis-on-cue]. Again the WHAT (detect a
   construction cue, then reanalyze) is right; the HOW (a hand-enumerated set of surface patterns,
   one added per construction discovered) is not learned -- it is architecturally identical to
   component 3's problem: each new construction gets its own hand-added boolean rule (v3's own
   docstring explicitly frames is_copular as "a THIRD instance of that SAME mechanism" as
   quotative/byagent, i.e., the scaling behavior of this design is "add one more hand rule per
   construction," not "learn to detect novel constructions") [MEASURED from docstring].
   LEARNED REPLACEMENT: fold construction-cue detection into the SAME learned softmax as
   component 2 (a construction classifier trained on labeled construction-type examples, sharing
   representational machinery with role assignment) rather than a parallel, ever-growing hand-rule
   gate. This is the same fix as component 3, generalized: stop hand-writing one new gate per
   construction; learn a construction-detector from the gold pools that already exist per
   construction (canonical/quotative/byagent/passive/copular_theme pools are already labeled by
   construction kind -- this is directly learnable today, not blocked on new data).

5. MARGIN-GATED GRACEFUL DEGRADE (revise_predict_one_with_margin[_with_margin6], MARGIN_THRESH
   selection, fallback-to-COMMIT-default logic)
   Files: exp_extraction_commit_then_revise_v2.py / v3_theme.py.
   CLASS: (A) brain-faithful MECHANISM in principle, with an honest (B) caveat on the threshold.
   WHAT IT DOES: uses the ALREADY-LEARNED softmax's own top1-top2 probability margin as a
   confidence signal; REVISE's output is accepted per-mention only when margin >= MARGIN_THRESH,
   else the clause-level default is kept. MARGIN_THRESH itself is chosen by an offline grid sweep
   with a fixed, pre-registered 3-tier selection rule (not learned online, not gradient-fit).
   BRAIN-GROUNDING: reliability/precision-weighted integration of a bottom-up signal versus a
   prior/default is the central claim of predictive-coding accounts of perception and language
   [CITED: Friston 2005/2010 predictive coding, precision-weighting of prediction error;
   Bornkessel-Schlesewsky & Schlesewsky eADM's explicit claim that REVISION is gated by cue
   RELIABILITY, not forced through on a weak signal]. Using the model's own softmax margin as a
   confidence/precision proxy is a reasonable computational stand-in for reliability-weighting
   [REASONED -- margin-as-confidence is standard in ML but the mapping to neural "precision" is an
   analogy, not a demonstrated equivalence]. This is the strongest brain-grounding claim in the
   pipeline because the GATING PRINCIPLE (not just its output) matches an established mechanism
   class, and margin is a genuinely LEARNED, non-hand-authored quantity (a direct readout of
   component 2's fitted weights).
   HONEST CAVEAT: the THRESHOLD is hand-selected via an offline grid, not learned/calibrated
   online per new data (no analog of trial-by-trial precision estimation here) -- classify the
   selection PROCEDURE as (B), the underlying MECHANISM (precision-gated cue acceptance) as (A).

6. ANIMACY LEXICON (hdlab/animacy_lexicon.py)
   CLASS: (C) supplied data -- allowed, correctly scoped.
   WHAT IT DOES: WordNet first-sense hypernym-closure lookup -> {animacy, category,
   agent_capable}, with an explicit pronoun table (guards I->iodine/He->helium WordNet symbol
   collisions) and a deliberate proper-noun exclusion (guards Dash/Patty/Read homograph
   collisions, honestly reported as an uncovered gap rather than guessed).
   BRAIN-GROUNDING: this is a LOOKUP, not an encoder -- consistent with the project's own
   MEANING=ASSIGNMENT lock (a dictionary is a lookup, not a learned representation) [project
   USER-locked principle, not an external citation]. Animacy as a real, early-available cue to
   role assignment is well-established [CITED: Comrie 1989 animacy hierarchy in role assignment;
   Bornkessel-Schlesewsky & Schlesewsky's own animacy-cue weighting in eADM]. No concern here --
   this is squarely "supplying knowledge," not "supplying the reading mechanism," and it is
   consumed by the same learned softmax as any other feature (component 2), not given special
   hand-coded veto power.

7. ACCUMULATE SITUATION-MODEL REGISTER (hdlab/situation_model_accumulate.py: unit_phase_vec,
   AccumulateRegister.add_event/register/decode, bind/bundle/unbind primitives)
   CLASS: (A) brain-faithful at the algorithmic/computational level, with an honest ACTIVE-
   RESEARCH caveat on the neural-implementation claim.
   WHAT IT DOES: FHRR bind(role_vec, event_idx_vec) per event, ACCUMULATE = bundle (normalized
   superposition) of all of an entity's bound events, decode = unbind + cosine-argmax cleanup.
   Role/event-index vectors are RANDOM atomic phase vectors (not learned, not meant to be --
   standard VSA practice, since key-vectors need only be quasi-orthogonal, not semantically
   informative).
   BRAIN-GROUNDING: multi-event ACCUMULATION into a single situation-model representation
   (rather than overwrite) directly matches the Construction-Integration and Event-Indexing
   models of discourse comprehension, where a situation model integrates information across
   multiple clauses/events rather than replacing it [CITED: Kintsch 1988 Construction-Integration;
   Zwaan & Radvansky 1998 Event-Indexing Model]. This atom itself is VET-confirmed to structurally
   distinguish accumulate (1.00) from overwrite (0.46) from floor (0.21) on real multiclause gold
   [MEASURED@atom 29609]. HONEST CAVEAT (per this session's own lit audit, atom 29604): using
   VSA algebraic binding (bind/bundle/unbind over random phase vectors) as a MODEL of neural
   relational binding is a THEORY (Smolensky tensor-product, Plate HRR, Eliasmith SPA), not an
   established neural fact -- and the same audit found that binding-BY-SYNCHRONY specifically is
   largely refuted as a general cortical mechanism [CITED: Shadlen & Movshon 1999; Ray & Maunsell,
   per atom 29604], while noting the brain's actual binding solution looks more like CONJUNCTIVE/
   mixed-selective coding than a clean orthogonal algebraic bind [CITED, same atom]. FHRR bind is
   not literally synchrony-binding, so that specific refutation does not directly hit this organ,
   but it means the "this IS how the brain binds" framing should be held as CONTESTED/ACTIVE-
   RESEARCH, not settled -- classify as (A) at the COMPUTATIONAL/behavioral-analog level (the
   accumulate-vs-overwrite distinction reproduces a real cognitive-science result), NOT as a
   proven claim about cortical implementation.

8. SELF-ERROR-DETECTION SIGNALS (S1-S4, exp_self_error_detection_internal_signals_v1.py,
   compute_signals_no_gold)
   CLASS: mixed, itemized:
   - S1 RULE_VIOLATION (is_subject AND pred_role != agent): (B) hand-coded boolean check, but
     brain-grounding is unusually good: this is structurally a RESPONSE-CONFLICT signal (the
     reader's own default heuristic disagrees with its committed output), which is the core claim
     of conflict-monitoring/ERN theories of error detection [CITED: Botvinick, Braver, Barch,
     Carter & Cohen 2001 conflict monitoring; Yeung, Botvinick & Cohen 2004 ERN-as-conflict].
     The TARGET (detect disagreement between a default and the actual decision) is well-grounded;
     the IMPLEMENTATION (one hand-written boolean) is not a learned conflict-detector.
   - S2 NO_AGENT_IN_CLAUSE (structural completeness check): (B) hand-coded; loosely grounded in
     schema/standard-violation comprehension-monitoring accounts [REASONED, generic connection to
     Baker & Brown 1984 comprehension-monitoring standards, not a tight citation for this specific
     check].
   - S3 LOW_CONFIDENCE (reused REVISE margin, thresholded): (A)-leaning -- same margin discussed
     in component 5, i.e., a genuinely learned-model-derived signal being reused as its own error
     cue, which matches confidence-based/metacognitive error-monitoring accounts where subjective
     confidence predicts objective accuracy [CITED: Fleming & Lau 2014 metacognitive sensitivity;
     Kepecs & Mainen 2012 neural basis of confidence]. Threshold reuse caveat as in component 5.
   - S4 WM_READBACK_MISMATCH (VSA round-trip self-consistency): (B/D borderline) hand-coded
     algebraic consistency check with only a loose, REASONED analogy to familiarity/consistency-
     based monitoring -- no specific citation found for this exact mechanism; more honestly
     described as "diagnoses VSA bundling-capacity crosstalk" than "models a cognitive-monitoring
     process." Grounding is weak; report as REASONED, not CITED.
   - COMBINED = unweighted OR / count of S1-S4: (B) hand-coded logical combination. This is the
     clearest near-term B-to-A conversion in the self-detection stack: the four signals are
     already computed per-event, so a small LOGISTIC CLASSIFIER over [s1,s2,s3,s4] fit to predict
     genuine-error (the same gradient-descent machinery as component 2, applied to a 4-dim input
     instead of hand-picking OR-combination) would convert this from a hand-tuned ensemble rule to
     a learned one, with no new data collection required (the labels already exist in this same
     eval file for offline fitting/held-out validation).
   MEASURED RESULT (honesty check on the whole S1-S4 stack, read off the cells rather than
   assumed): the self-error-detection cell's own verdict machinery allows for
   NULL_RESULT_NO_INTERNAL_SIGNAL_BEATS_CHANCE and MIDDLE_BAND outcomes as legitimate, and the
   self-correct cell explicitly allows NET_NEGATIVE / NET_NEUTRAL as legitimate verdicts (not
   cell failures) -- i.e., the cells are honestly instrumented to report a null result rather than
   built to only report a positive one. I did not re-run these cells in this audit (out of scope,
   research-only per contract); the verdict a specific run landed at should be read from
   data/exp_self_error_detection_internal_signals_v1/metrics.json and
   data/exp_self_correct_loop_powered_eval_v1/metrics.json before citing a specific number.

9. SELF-CORRECT ACCEPT RULE (exp_self_correct_loop_powered_eval_v1.py: candidate = S1 fires;
   accept iff clause_n_agent == 0 at the time of correction)
   CLASS: (B) hand-coded scaffold.
   WHAT IT DOES: proposes reverting to the reader's OWN base rule (clause subject -> agent) only
   when S1 fires, and accepts only when doing so fills a clause that currently has ZERO predicted
   agents (a general internal-coherence check, not a per-construction rule -- correctly NOT
   another hand-added construction-specific patch, to the cell's credit).
   BRAIN-GROUNDING: self-correction gated by an internal coherence/completeness check (does this
   interpretation leave the local structure well-formed?) has a loose analog in reanalysis-repair
   literature (P600-indexed reanalysis is itself a repair-triggered-by-violation process)
   [REASONED connection to Friederici reanalysis models, not a tight citation for this exact
   accept-rule]. The rule ("propose = revert to own default, accept = iff coherence-restoring")
   is a sensible, cheap, non-per-construction heuristic, but it is still a single hand-authored
   accept/reject boundary, not something learned from outcomes.
   LEARNED REPLACEMENT: an accept/reject decision could be fit from OUTCOME LABELS (recovered vs.
   false-correction, both already computed by this cell's own analyze_correction()) -- i.e., a
   held-out-validated small classifier over [S1, S2, S3, S4, clause_n_agent, margin] predicting
   "will accepting this correction net-help," trained the same way as component 2. This closes
   the loop: the self-correct mechanism could learn WHEN to trust itself from its own measured
   track record, rather than a single hand-picked coherence rule -- this is the most direct
   "hand rule-learning handed to the loop" opportunity named in the locked ROUTE ERRORS discipline.

10. INTERACTIVE EXTRACTION<->SITUATION-MODEL COUPLING / "TOP-DOWN" FRAMING (atoms 29604-29606;
    the CURRENT FOCUS framing that commit-then-revise IS the top-down-construction-mapping loop)
    CLASS: PARTIALLY VERIFIED, with an honest scope gap flagged.
    WHAT I CONFIRMED (MEASURED, from atom 29604's banked text): the underlying literature claim
    -- comprehension is interactive, situation-model/plausibility information feeds back to
    constrain parsing within ~200ms, not strictly feed-forward -- is well-cited [CITED: Trueswell,
    Tanenhaus & Garnsey 1994; Altmann & Kamide 1999; Crain & Steedman] and is explicitly flagged
    in the atom itself as the best-replicated finding of that audit (versus the CONTESTED binding-
    by-synchrony claim, correctly kept separate).
    WHAT I COULD NOT CONFIRM in this audit's scope (out of the files actually read: v2/v3/v4
    commit-then-revise, the two self-* cells, the two hdlab modules): whether the WM/situation-
    model REGISTER (built from prior clauses/entities) is actually fed BACK as an input FEATURE
    into the CURRENT clause's REVISE decision. What I DID verify is that gate_fires_v2/v3's
    "construction cue -> override the clause-local default" pattern is a WITHIN-SENTENCE top-down
    effect (lexical/construction knowledge overriding a positional default), which is a real and
    citable instance of top-down constraint [CITED: same eADM/reanalysis literature as component
    4], but it is a NARROWER claim than "situation-model feeds back to parsing" -- the latter
    would require the ACCUMULATED entity-register state from earlier clauses to influence role
    decisions in later ones, which I did not find wired in the three cells I read (v2/v3/v4 build
    each clause's features independently of any WM register; the WM register is only built
    AFTER role predictions are finalized, per exp_wire_extraction_accumulate_wm_oracle_vs_real_*
    and the self-* cells' pipeline order: STAGE 1 predict roles -> STAGE 2 build register). The
    file exp_interactive_loop_real_gold_mcguffey_v1.py (imported for quote_spans in v2) likely
    contains the actual cross-clause interactive-loop experiment referenced by atoms 29605/29606,
    but I did NOT read it in this audit -- flagging this explicitly as an UNVERIFIED CLAIM rather
    than asserting it either way. RECOMMENDATION: before citing "the interactive loop is wired
    end-to-end" in any future framing, re-run this audit against
    exp_interactive_loop_real_gold_mcguffey_v1.py specifically to confirm whether WM-register
    state is actually read back into role-assignment features, or whether "interactive" currently
    means only "construction-cue overrides positional default within one sentence."

=================================================================================================
OVERALL VERDICT
=================================================================================================

ROUGH COMPOSITION OF THE PIPELINE (component-count basis, not weighted by code volume or impact):
  - (A) brain-faithful learned mechanism: component 2 (REVISE softmax weights), component 5's
    mechanism-class (margin-gated precision-weighted acceptance), component 7 (accumulate-vs-
    overwrite situation-model organ, algorithmic-level), S3 signal.
  - (B) brain-compatible hand-coded scaffold: component 1 (feature construction), component 3
    (clause segmentation + PP/relative-clause disqualification -- THE component the USER flagged),
    component 4 (construction-cue gate booleans), component 5's threshold-selection procedure,
    S1/S2/S4 signals, component 9 (accept rule), and the COMBINED signal's OR-logic.
  - (C) supplied data: component 6 (animacy lexicon) -- correctly scoped, no concern.
  - (D) not brain-faithful: none identified as clearly D; S4's grounding is weak enough to be a
    borderline B/D but it is at minimum a legitimate diagnostic, not a shortcut of the kind the
    project's locked anti-patterns (borrowed embeddings, bolt-on parsers) forbid.

HONEST READ: this session's NEW additive work (the two clause-parser fixes named in the task,
segment_clauses_v3 + _immediately_follows_prep) is CLEANLY CATEGORY B -- it computes the right
target (clause-local subject-default-agent, matching Bever's canonical-sentoid strategy and
Friederici's incremental clause-building) via hand-specified rules that were authored by reading
specific measured failures (13/26 mislabels) and patching each one. This is legitimate
BOOTSTRAP-BY-HAND work under the locked "bootstrap primitive by hand THEN hand rule-learning to
the loop" discipline -- it is NOT a violation of brain-foundational-ness by itself, PROVIDED the
next step (handing rule-LEARNING to the loop) actually happens. The risk the USER is right to
flag is that this session's velocity has been entirely on the B side (add another rule, add
another gate, add another boundary word) without yet closing the loop back to A (make the NEXT
construction/boundary/gate be discovered/learned rather than hand-added). Every NEW construction
this arc has added (quotative, byagent, passive, copular_theme) has been implemented as "detect a
new hand-written surface cue, gate the SAME learned softmax on it" -- the softmax-weight-fitting
step is genuinely learned each time, but the CUE-DISCOVERY step has been 100% hand-authored, 4
times in a row. That repetition is itself evidence this is a scaffold that should be replaced,
not a series of one-off exceptions.

PRIORITIZED LIST -- WHICH SCAFFOLDS TO REPLACE WITH LEARNED MECHANISMS NEXT:

1. HIGHEST PRIORITY, LOWEST COST: learn the S1-S4 COMBINATION (self-detection ensemble) and the
   self-correct ACCEPT rule (component 9) via a small logistic classifier fit on the labels these
   cells ALREADY COMPUTE (genuine_error, recovered/false_correction). No new data collection
   needed; this converts two hand-coded decision rules into gradient-fit ones using the exact
   same mechanism already proven in component 2, and it is the most direct instance of the locked
   "hand rule-learning to the loop" discipline -- the loop already exists (self_correct_loop), it
   just needs its OWN decision gate to be learned rather than a single hand-picked boolean.

2. NEXT: replace the per-construction GATE (component 4: has_by / quotative_cue / is_copular,
   with a new hand rule added each construction) with a single learned construction-TYPE
   classifier trained across all the already-labeled construction pools (canonical/quotative/
   byagent/passive/copular_theme all have kind labels already) -- this directly stops the
   "add one more hand rule per construction" scaling pattern the v3_theme docstring itself
   names as the mechanism's own structure ("a THIRD instance of the SAME mechanism").

3. HARDEST, HIGHEST-VALUE: replace clause/constituent-BOUNDARY detection (component 3:
   segment_clauses/_v3, BOUNDARY_WORDS, RELATIVE_BOUNDARY_WORDS, _immediately_follows_prep) with
   a learned boundary detector. This is the component the USER specifically flagged and it is
   the most work (needs boundary-labeled training data, likely derivable for free from the
   existing clause-annotated gold sentences without new annotation) but it is also the component
   most likely to keep needing ad hoc patches indefinitely if left hand-coded (this session
   already needed a second patch -- GAP 1 fronted-PP and GAP 2 relative clauses -- on TOP of v2's
   original segment_clauses; a third construction that breaks the current rule set is a matter of
   when, not if, on continued real-text scale-up).

4. LOWER PRIORITY (mechanism-class already sound, only the calibration procedure is hand-tuned):
   move MARGIN_THRESH (component 5) and per-construction THRESH (component 4) from an offline
   grid-search-and-freeze to an online/adaptive calibration (even a simple per-session recompute
   against a held-out slice would remove the "hand-picked and frozen" character while keeping the
   already-sound precision-weighting mechanism).

5. WATCH, DO NOT YET ACT: component 7's algorithmic-level grounding is solid (Kintsch/Zwaan
   accumulate-vs-overwrite is a real, VET-confirmed result) but its neural-implementation framing
   (VSA bind/bundle as THE way the brain binds) should stay labeled CONTESTED/ACTIVE-RESEARCH per
   this session's own lit audit (atom 29604) rather than escalated to a settled claim -- no action
   needed, just discipline on how it is described going forward.

UNRESOLVED SCOPE GAP (flagged, not resolved, in this audit): whether the "interactive
extraction<->situation-model loop" claimed in current-focus framing is actually wired (WM
register state feeding back into role-assignment features across clauses) or whether "top-down"
currently only means within-sentence construction-cue override. This needs a follow-up read of
exp_interactive_loop_real_gold_mcguffey_v1.py specifically before any future claim asserts the
fuller cross-clause interactive loop is implemented, not just the within-sentence gate.
