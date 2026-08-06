# Brain-Foundational Audit: Affective/Goal Comprehension Components (CODE-READ, 2026-08-05)

AUDIT-ONLY (Skunkworks). Every performance number verified off-disk from the cited
metrics.json. Mechanism claims read from the CODE, not docstrings/labels. Deflationary:
MEASURED vs claimed distinguished throughout.

Bottom line up front: the converged bottleneck (the affect/valence reader) is not merely a
"weak lexicon" -- it is the visible symptom of a WHOLE MISSING ORGAN. We have NO
lexical-semantic hub and NO context-driven word-sense selection anywhere over text. Every
lexical signal into the affect/goal pipeline is either (a) a fixed hand-authored word-class
table or (b) a fixed hash-seeded random-projection bag-of-words. Two senses of "hard" get the
byte-identical vector. That absence is the root cause of the affect-reader failures, CONFIRMED
below from the code.

============================================================================
COMPONENT 1 -- AFFECT/VALENCE READER  (the converged bottleneck)
============================================================================
(i) FILES+fn:
    - experiments/exp_grounded_structure_phase0_probe_v1.py :: resolve_valence_blind (L133)
    - experiments/exp_situated_goal_structure_valence_v1.py :: HARM_WORDS (L73), HELP_WORDS
      (L78), resolve_valence (L144), resolve_target (L131)
    - experiments/exp_grounded_appraisal_transfer_to_text_v1.py :: resolve_valence_context /
      arm_c (L177-208), context_features (L123), _true_label_rule (L140)

(ii) WHAT IT ACTUALLY DOES (from code):
    resolve_valence_blind tokenizes the target span, counts how many tokens fall in the fixed
    22-word HARM_WORDS set vs the 20-word HELP_WORDS set, returns argmax ("HARM"/"HELP"/"NA").
    That is the ENTIRE affect reader. It is a context-free bag-of-words vote over a single span.
    No negation handling, no sense selection, no syntax, no subject/experiencer awareness.
    resolve_target (L131) is NOT a coreference call -- it is a reflexive-marker regex
    ("herself"/"his own"...) defaulting to OTHER, explicitly a scope-limited single-clause proxy.
    arm_c (the "learned context-sensitive" extractor) does NOT learn valence semantics: it fits
    a ruleind/estimation hypothesis over 5 DISCRETE hand-defined features (blind-lexicon vote +
    hand-listed sarcasm/sincere tone words + negation words + contrast + quote), trained on a
    72-cell combinatorial grid labeled by a hand-written invert-on-sarcasm/negation rule
    (_true_label_rule). It is a hand-specified correction table on top of the same blind vote,
    trained on synthetic labels, NOT an earned lexical-semantic representation.

(iii) BRAIN ANALOG: this is trying to stand in for the confluence of (a) the ATL semantic hub
    (lexical concept meaning) + (b) IFG/pMTG semantic control / word-sense selection + (c)
    ventromedial/amygdala valuation tagging. It implements NONE of those computations; it is a
    fixed affective-norm lookup (a crude ANEW/affect-lexicon stand-in) with zero control.

(iv) FOUNDATIONAL STATUS:
    SHAPE: WRONG. The brain does not read affect by span-local keyword voting; it retrieves a
    contextualized lexical concept then selects the sense/valence under semantic control. No
    sense selection = no organ. arm_c's hand-listed tone words are a patch, not the mechanism.
    POSITION: roughly right slot (affect feeds the appraisal congruence dimension), but it sits
    at the pipeline point where a semantic-hub->control output should arrive, and there is
    nothing upstream of it.
    METRIC: judged on end-task classification accuracy, not on any lexical/valence-fidelity
    objective. No sense-disambiguation objective is measured anywhere.
    DEVIATION: polysemy collision. VERIFIED off-disk: {"hard","trick","pay","cross"} are ALL in
    HARM_WORDS. "studied hard" -> false HARM; "played a trick"/"a card trick" -> always HARM;
    "pay attention"/"pay a visit" -> always HARM. This is exactly the 'studied hard'/'trick'
    word-sense collision the frontier named.

(v) PERFORMANCE (MEASURED@ disk):
    - data/exp_grounded_structure_phase0_probe_v1/metrics.json (ts 2026-08-03):
      verdict=PREMISE_PAYS_ORACLE_ONLY. confused_4: AUTO_BLIND=0.500, ORACLE_NARRATIVE=0.750,
      SCRAMBLED_VALENCE=0.750, lexical=0.250.
      LOAD-BEARING FINDING (recomputed off-disk): SCRAMBLED == ORACLE == 0.750. Swapping the
      HARM/HELP word classes WHOLESALE did NOT change the oracle result. => on the 4 confused
      items the valence reader contributes LITERALLY ZERO discriminative signal; the entire lift
      came from the ORACLE prior-block (causal attribution), not from valence. The cell's own
      scramble gate passed only because of a +0.25 (1-item) tolerance. This is stronger than
      "weak lexicon": on the hard subset the valence reader is INERT.
    - data/exp_grounded_appraisal_transfer_to_text_v1/metrics.json (ts 2026-08-05):
      verdict=EXTRACTION_BOTTLENECK. causal arm_a(oracle)=1.000 arm_b(blind valence)=0.629
      arm_c(learned context)=0.514 -> gap_closure = -0.308 (arm_c HURTS vs arm_b on causal).
      irony arm_a=0.600 arm_b=0.500 arm_c=0.700 surface=0.500. arm_c_verdict=ARM_C_PARTIAL.
      Reading: the appraisal->action theta transfers PERFECTLY when fed ORACLE structure
      (arm_a causal=1.0) but real extraction (arm_b/arm_c) collapses toward chance. The
      hand-patched context learner helps irony (+0.20 over surface) but REGRESSES causal. Net:
      the extraction organ, not the appraisal organ, is the bottleneck -- confirmed by the cell's
      own verdict name.
    WIRED-STATE: resolve_valence_blind/arm_c live only in experiment cells; NOT promoted to
    hdlab, NOT in capability_registry as a wired capability. Effectively ISLAND/experimental.
    LABEL-vs-CODE FLAG: arm_c is described in-cell as "LEARNED, CONTEXT-SENSITIVE VALENCE
    EXTRACTOR ... reuses hdlab/learner". CODE: it learns a correction over hand-authored discrete
    tone/negation cues from a hand-labeled synthetic grid. It is NOT a learned lexical-semantic
    or valence representation. The "context window" it reads is +-2 raw corpus lines scanned for
    membership in ~17 hand-listed tone words. Honest label: hand-specified cue-correction table,
    MDL-selected. (Not dishonest in-cell -- the docstring is careful -- but the one-word summary
    "learned valence extractor" over-reads what the mechanism is.)

============================================================================
COMPONENT 2 -- GROUNDED APPRAISAL / VALUATION organ (the earned valuation)
============================================================================
(i) FILE+fn: experiments/exp_grounded_appraisal_sim_earned_v1.py :: train_theta (L267),
    phi (L226), reward (L167), eval_theta (L284), coherence_vs_recency_readout (L324).
(ii) WHAT IT DOES: an online reward-modulated delta-rule (LMS) contextual bandit over FHRR
    features. State encodes action-type + target(coherence,recency) + congruence + coping as
    role-bound FHRR bundles (identity-free in the FULL arm). It learns, from +1/-0.5 reward
    consequence in a discrete no-text simulation, to direct harm at the CAUSALLY COHERENT
    candidate on BLOCK_HIGH episodes (revenge), withdraw on BLOCK_LOW, help on RECIPROCITY,
    pursue on NEUTRAL. Glass-box theta (linear weights, inspectable). No text ever touched.
(iii) BRAIN ANALOG: reasonable stand-in for basal-ganglia/striatal reinforcement valuation +
    OFC appraisal (congruence/coping = Lazarus/Scherer appraisal dims). The "earn from
    consequence, not from a label" framing is brain-appropriate.
(iv) FOUNDATIONAL STATUS:
    SHAPE: defensible. RL-from-consequence over an appraisal-structured state is a legitimate
    valuation-learning shape; revenge EMERGES (not a retaliate label). Caveat: it is a single
    linear bandit, not a full actor-critic/DA-prediction-error circuit -- a simplification, not
    a misfit.
    POSITION: correct as the DOWNSTREAM valuation consumer. Its declared limit is honest: no
    beneficiary-vs-patient slot (Component-1 GAP), so it cannot represent that distinction.
    METRIC: judged on its OWN brain-relevant metrics (revenge_emergence, targeting_specificity,
    coherence-over-recency readout, generalization gap) with real can-fail floors. Good.
(v) PERFORMANCE (MEASURED@ data/exp_grounded_appraisal_sim_earned_v1/metrics.json, ts
    2026-08-03): verdict=MECHANISM_EARNS. FULL_heldout=1.000 FULL_train=1.000 RANDOM=0.168
    MEMORIZED=0.206 NO_APPRAISAL=0.239 | revenge=1.000 specificity=1.000 bystander=0.000 |
    earned_restore=1.000 recency_restore=0.303 | coh-rec_readout=1.146. 5 seeds. Three floors
    (random/memorized/no-appraisal) all fail as designed; beats recency by +0.70.
    HONEST DEFLATION: FULL_heldout=1.000 is on a SYNTHETIC, construction-controlled discrete
    world with N_CAND=3 and a separable linear problem. It is a clean MECHANISM_EARNS proof, NOT
    a capability number over real input. Its own docstring states "sim-to-text transfer NOT
    claimed here" -- and Component-1 above is exactly where that transfer breaks.
    WIRED-STATE: capability_registry status = "validated_mechanism_earns_islanded_2026-08-05".
    ISLAND. It is the theta reused (behaviorally, verified) by the transfer cell, but not wired
    into any production reader.

============================================================================
COMPONENT 3 -- SITUATION MODEL
============================================================================
(i) FILE+fn: hdlab/situation_reader.py :: SituationReader.read (L466), _read_events (L364),
    _read_entities (L343), _read_timeline (L421), _read_causation (L442).
(ii) WHAT IT DOES: thin composition layer. Reads a LitBank-style CoNLL passage; builds tracked
    entities + per-sentence events (predicate via temporal POS tagger; agent=subject-mention,
    patient=nearest post-predicate mention -- POSITIONAL head selection), stores each event in a
    Cowan-4 bounded FHRR role-slot focus; reconstructs timeline on past-perfect sentences;
    extracts causal links on connective sentences. NO affect/valence dimension at all (confirmed:
    EventRecord has predicate/agent/patient/tense + the additive subj_role/obj_role, no valence).
(iii) BRAIN ANALOG: Kintsch/van-Dijk situation model + Zwaan event-indexing held in a Cowan-4
    working-memory focus. Mapping is apt.
(iv) FOUNDATIONAL STATUS:
    SHAPE: mostly faithful for entities/events/time; the CAUSATION dim is honestly flagged in
    its own docstring as REDUCIBLE to connective-else-most-recent (no genuine force-dynamics).
    POSITION: correct as the integrating substrate; it is the natural HOME for an affect
    dimension that DOES NOT EXIST yet -- the missing valence organ would slot in here.
    METRIC: only coref is scored vs gold on-passage; events are structural-only (no LitBank role
    gold), honestly not re-scored. Reasonable.
    DEVIATION: no affect/goal/valuation dimension; events are positional, not thematic (see
    Component-5) except for the additive frame labels.
(v) PERFORMANCE: no aggregate metrics.json (it is a library + self-tests; the module's
    __main__ runs 4 self-tests that pass). coref accuracy is inherited from the coref backbone
    (Component-4). WIRED-STATE: registry row working_overlay_situation_reader = validated,
    split out 2026-08-03; it is one of the pipeline-reachable modules.

============================================================================
COMPONENT 4 -- COREFERENCE / RELATIONAL BINDING
============================================================================
(i) FILE+fn: hdlab/coreference_resolver.py :: run_match_or_allocate (L296), run_strict_cb
    (L372), run_principle_b (L429), run_principle_b_deixis (L583, RECOMMENDED CANONICAL).
(ii) WHAT IT DOES: glass-box symbolic match-or-allocate. Pronouns MATCH an existing tracked
    entity (never allocate) via gender/number filter then a pick rule: salience (freq+recency
    Centering) OR strict-Cb (literal backward-looking-center = most-recent subject-like clause),
    plus Binding Principle B (exclude own-clause agent) and speaker/addressee deixis inside
    quotes. Names/nominals resolve by normalized-token Jaccard + determiner bridging. Honest-mode
    flags near-ties/no-compat as unresolved rather than fabricating.
(iii) BRAIN ANALOG: hippocampal relational antecedent retrieval + Centering-Theory discourse
    salience. This is the faithful organ MEMORY.md says to REUSE for causal-attribution bridging.
(iv) FOUNDATIONAL STATUS:
    SHAPE: faithful (Centering/Cb, Principle B, dialogue deixis are the actual linguistic
    theory, implemented glass-box, no borrowed embeddings). POSITION: correct upstream identity
    backbone. METRIC: B-cubed P/R/F1 vs real cross-clause gold, with recency-floor + random
    fair-test floors. Well-judged.
(v) PERFORMANCE: source atoms 29613 (match-or-allocate fair-test HARD_PASS vs recency+random),
    29614/29618/29621 (strict-Cb, Principle B, deixis lever, each net-positive on powered evals:
    identity-demanding query +0.035, g5g6 +0.08). WIRED-STATE: registry
    coreference_resolver_match_or_allocate_strict_cb_principle_b =
    "vet_confirmed_promoted_2026-08-02_plus_deixis_lever_plus_honest_mode"; pipeline-reachable.
    This is the strongest, most brain-faithful, genuinely-WIRED organ in the set.
    NOTE (MEMORY.md correction carried): coref is FAITHFUL (Centering-Cb), NOT "recency-falsified".
    CAVEAT (2026-08-05 VET-B, disk-verified): the PRODUCTION situation_reader event-extraction path
    does NOT call THIS module. situation_reader.py:412-420 instantiates EventCentralityReader
    (hdlab/event_centrality_coref.py -> coref_distractor_suppress.py -> coref.py), a DIFFERENT coref
    lineage, and until 2026-08-05 passed centrality_mode="recency" (perirhinal FAMILIARITY) overriding
    that fn's "event_role" default (hippocampal CA3 RECOLLECTION). exp_c5_real_coref_endtoend_v1
    (commit f3f88f752) showed event_role 0.8889 vs recency 0.0 in goal-owner end-to-end -> the flip to
    event_role is being promoted (certification-gated). So the "strongest/WIRED" verdict describes
    coreference_resolver.py on ITS OWN evals, but the production extraction+goal-owner pipeline runs the
    event_centrality lineage. RECONCILE which coref organ is canonical for production (two parallel
    organs, not one).

============================================================================
COMPONENT 5 -- THEMATIC-ROLE LABELING (Component-3 in the frontier's numbering)
============================================================================
(i) FILES+fn: hdlab/thematic_role_labeler.py :: VERB_FRAMES (L88), frame_slot_role (L97),
    PSYCH_VERBS (L53), train_perceptron (L245); hdlab/frame_induction.py :: frame_primary_role
    (L337), induce (L160), real_construction_feats (L216); wired via
    hdlab/situation_reader.py :: _assign_frame_primary_roles (L289).
(ii) WHAT IT ACTUALLY DOES (from code -- important, multiple layers with different status):
    - PRODUCTION PATH (what situation_reader actually calls): frame_primary_role. For a KNOWN
      lemma (in VERB_FRAMES, a hand-authored ~150-lemma table) it returns frame_slot_role
      UNCONDITIONALLY -- pure dictionary lookup (psych verb subj -> EXPERIENCER, else AGENT).
      For an OOV verb with NO hypothesis wired (the production default), subj -> "AGENT"
      (positional default), obj -> DEFAULT_FRAME. So in production this is a FIXED TABLE +
      positional fallback. The induced OOV hypothesis is deliberately NOT wired into the reader.
    - OFFLINE/EXERCISED-SEPARATELY: induce() fits a construction-cue hypothesis (Gleitman
      syntactic bootstrapping: scomp/degree/progressive/passive/order/animacy atoms, lemma NEVER
      a feature) via hdlab/learner MDL selection, for OOV psych verbs.
    - SHELVED (do NOT revive): the flat averaged perceptron train_perceptron -- it learned
      "order:pre -> AGENT" and OVERRODE the frame signal (experiencer-axis 0.614 vs frame_only
      0.857, a -0.24 regression). frame_primary_role is the fix that removed the re-ranker.
(iii) BRAIN ANALOG: MacWhinney Competition-Model cue integration + verb selectional frames
    (lexical-syntactic). Frame-primary (frame wins over position) is the brain-faithful choice.
(iv) FOUNDATIONAL STATUS:
    SHAPE: the frame-primary decision is faithful (frame beats position); the KNOWN-verb path is
    a hand table (SUPPLIED knowledge, honest). The OOV LEARNING path is faithful (construction
    bootstrapping) but NOT in production. POSITION: correct (labels the same heads
    situation_reader already picks; additive). METRIC: known-lemma acc=1.0 by construction; OOV
    earned-acc measured ~0.767 (coarse animacy proxy on sparse data) per the re-VET.
    DEVIATION: production reader does NOT use the induced OOV learner -> OOV psych verbs silently
    fall to AGENT (known-bad, but honestly labeled, zero-regression).
(v) PERFORMANCE: registry frame_primary_role_assigner_v1 =
    "registered_2026-08-05_wired_into_situation_reader_at_corrected_MIDDLE_BAND_tier". The
    re-VET (notes/skunkworks_reVET_frame_primary_role_assigner_v1.md) tiered it MIDDLE_BAND:
    the ARCHITECTURE (frame-primary) is the win; the OOV induced path is data-starved. WIRED
    (known-verb table path) but the earned OOV path is exercised offline only.
    LABEL-vs-CODE FLAG: "thematic role labeling is wired/earned" over-reads. WIRED part =
    hand-authored frame TABLE + positional fallback. EARNED part (OOV induction) = NOT in the
    production reader path. The self-test in situation_reader even asserts cherished->AGENT
    (OOV psych verb falls to the wrong-but-honest default).

============================================================================
COMPONENT 6 -- MENTALIZING / ToM
============================================================================
(i) FILE: experiments/exp_theory_of_mind_sally_anne_nested_hrr_v1.py.
(ii) WHAT IT DOES: nested-HRR false-belief (Sally-Anne) representation with agent-partitioned
    belief stores; Q2 = false-belief question ("where will Sally look?") answered from Sally's
    partitioned belief bundle, not the true world state.
(iii) BRAIN ANALOG: TPJ/mPFC mentalizing (belief-desire reasoning, decoupled agent models).
(iv) FOUNDATIONAL STATUS: SHAPE plausible (agent-partitioned nested binding is a reasonable
    substrate for belief decoupling). POSITION: island -- not connected to the reading pipeline.
    METRIC: false-belief accuracy vs a no-partition base floor, 5 seeds, cv reported.
(v) PERFORMANCE (MEASURED@ data/exp_theory_of_mind_sally_anne_nested_hrr_v1/metrics.json):
    verdict=HARD_PASS. Q2_full=0.806 Q1_full=0.781 Q3_full=0.924 Q2_base=0.138 gap=0.668
    oracle_avg=1.000 cv_Q2=0.034 n_seeds=5, arms_distinct, baseline_in_band, cardinality_ok.
    A genuine HARD_PASS. WIRED-STATE: registry theory_of_mind_sally_anne_nested_hrr =
    "validated_hard_pass_islanded_2026-08-05". ISLAND -- HARD_PASS organ not wired into
    comprehension. (This is the invisible-island class MEMORY.md flags.)

============================================================================
COMPONENT 7 -- LEARNING / PLASTICITY (hdlab/learner)
============================================================================
(i) FILES: hdlab/learner/registry.py (learn/apply), core.py (MDL selection, KEEP_EPISODIC),
    plugins/{estimation,ruleind,proginduction,gam}_plugin.py.
(ii) WHAT IT DOES: a centralized MDL model-selection engine. Given episodes + a feature fn + a
    hypothesis-space spec, it fits each candidate plugin (estimation = frequency/MDL table;
    ruleind = conjunctive rule induction; proginduction = boolean-program enumeration over
    declared atoms; gam) and MDL-selects the best, or returns KEEP_EPISODIC if nothing
    compresses (refuses a lookup-table fit). Glass-box, deterministic.
(iii) BRAIN ANALOG: a domain-general structure-learning / MDL prior (loosely, cortical
    rule abstraction). Not a specific circuit; a learning-services layer.
(iv) FOUNDATIONAL STATUS:
    SHAPE: sound for DISCRETE-SYMBOLIC rule induction over hand-declared feature atoms. It can
    learn: conjunctive rules, frequency estimates, small boolean programs over supplied atoms.
    It CANNOT learn: a continuous lexical-semantic space, word senses, or any representation
    whose feature atoms are not hand-declared. It only ever sees the atoms a cell hands it.
    POSITION: correctly reused config-only by frame_induction and arm_c (zero edits to learner
    core -- verified). METRIC: compression_ratio + held-out; refuses non-compressing fits.
    DEVIATION vs the need: the affect bottleneck needs a LEARNED LEXICAL-SEMANTIC/SENSE
    representation; this engine cannot supply that -- it needs the atoms pre-named, which is
    exactly what is missing. It is the right learner for RULES over features, wrong tool for
    inducing the FEATURES/semantics themselves.
(v) WIRED-STATE: reused by frame_induction (offline) and arm_c (experiment). The engine itself
    is a library; its consumers are islanded/experimental for the affect line.

============================================================================
COMPONENT 8 -- LEXICAL-SEMANTIC HUB (ATL analog) + SEMANTIC CONTROL / WSD (IFG/pMTG analog)
                THE MOST IMPORTANT CELL
============================================================================
HYPOTHESIS TESTED: this is MISSING or only a fixed lexicon, and that absence is the root of the
affect-reader failures. RESULT: CONFIRMED -- MISSING ENTIRELY.

Searched the whole repo (hdlab/ + experiments/) for word-sense / disambiguation / a learned
lexical-semantic space over text. Findings from the code:
  - hdlab/semantic.py: NOT a semantic hub. It is a TRACING helper (emits "semantic.hop" /
    "semantic.cleanup_hit" trace-bus events). Label collision only.
  - hdlab/semantic_parser.py: operates on PRE-COMPOSED HD BUNDLES built from known codebooks,
    explicitly "does NOT test language understanding: the substrate never sees characters,
    tokens, words". Not a text lexical-semantic space.
  - The only "meaning" representation over actual text is word_vector() in
    exp_construction_integration_relation_inference_v1.py (L113): a FIXED HASH-SEEDED RANDOM
    FHRR vector per surface form (torch.Generator().manual_seed(_digest_seed(word))). text_bundle
    = L2-normalized SUM of those random vectors (bag-of-words). VERIFIED: this is random
    indexing / random projection -- ZERO semantics, ZERO context, ZERO sense. Two senses of
    "hard" -> byte-identical vector. It is used only as a tie-breaker cosine in classify_grounded.
  - The "disambiguat" grep hits (event_centrality_coref.py, slot_attention_wm.py) are about
    situation-structure disambiguating REFERENCE (which entity), NOT word-sense.
  - Lexical knowledge over text = three FIXED hand-authored tables only: HARM/HELP_WORDS
    (affect), VERB_FRAMES (syntactic frame), animacy_lexicon (animacy). None is contextual;
    none does sense selection.

CONCLUSION: there is NO ATL-style learned lexical-semantic hub and NO IFG/pMTG-style
context-driven semantic control / word-sense disambiguation anywhere over text. The affect
reader fails on "studied hard"/"a trick"/"pay attention" because the SINGLE surface token is
mapped to a SINGLE fixed valence with no sense selection and no context gating -- there is no
organ that could do otherwise. VERIFIED: hard/trick/pay/cross all in HARM_WORDS. This is a
MISSING-COMPONENT (per MEMORY.md's "every negative: check the missing component, esp.
LEARNING") root cause, not a tuning problem. arm_c's -0.308 causal regression is consistent:
patching cues cannot substitute for the missing sense-selection organ.

============================================================================
SUMMARY TABLE
============================================================================
| Component | Brain analog | Foundational (shape/pos/metric) | Performance on disk | Wired |
|---|---|---|---|---|
| 1 Valence reader | ATL+IFG+valuation tag | WRONG shape / right slot / task-metric only | INERT on confused-4 (scrambled==oracle==0.750); EXTRACTION_BOTTLENECK, arm_c causal -0.308 | Island/experimental |
| 2 Appraisal sim | striatal RL + OFC appraisal | OK shape / correct downstream / own brain-metrics | MECHANISM_EARNS FULL=1.000 rev=1.000 (synthetic, 5 seeds) | Island (validated) |
| 3 Situation model | Kintsch/Zwaan + Cowan-4 WM | faithful ent/event/time; causation reducible / correct home / coref-scored | self-tests pass; coref inherited; NO affect dim | Wired (pipeline-reachable) |
| 4 Coreference | hippocampal relational + Centering | FAITHFUL / correct / B-cubed fair-test | HARD_PASS atoms 29613/14/18; +0.035/+0.08 powered | WIRED (strongest) |
| 5 Thematic roles | Competition-Model + verb frames | frame-primary faithful; prod=hand table+positional / correct / MIDDLE_BAND | known acc=1.0 by-constr; OOV earned ~0.767 not in prod | Wired (table); OOV earned offline |
| 6 ToM | TPJ/mPFC mentalizing | plausible / ISLAND / false-belief fair-test | HARD_PASS Q2=0.806 gap=0.668 5 seeds | ISLAND |
| 7 Learner (MDL) | domain-general rule abstraction | sound for symbolic rules / reused config-only / MDL+heldout | refuses non-compressing; used offline | Library (islanded consumers) |
| 8 Lexical-semantic hub + WSD | ATL + IFG/pMTG | ABSENT | n/a -- does not exist | MISSING |

============================================================================
BOTTOM LINE
============================================================================
MISSING ENTIRELY (brain-necessary for contextual affective comprehension):
  - The lexical-semantic HUB (ATL analog): a learned, contextualized concept representation over
    text. We have only fixed hash-random bag-of-words + hand tables.
  - Semantic CONTROL / word-sense disambiguation (IFG/pMTG analog): context-driven sense
    selection. Completely absent. THIS is the root of the affect-reader failures (confirmed).
  - A learned affect/valence representation: the current one is a fixed keyword table that is
    demonstrably INERT on the hard items (scrambled==oracle).

PRESENT-BUT-NOT-FAITHFUL (or not-in-production):
  - Component 1 valence reader: wrong shape (keyword vote, no sense/context); arm_c "learned"
    label over-reads a hand-cue correction table.
  - Component 5 thematic roles: architecture (frame-primary) is faithful, but the PRODUCTION
    path is a hand table + positional OOV fallback; the earned OOV induction is not wired.
  - Component 3 situation model: faithful for entities/time, but causation is reducible and
    there is NO affect dimension (the natural home for the missing organ).

FAITHFUL + PERFORMANT:
  - Component 4 coreference (WIRED, HARD_PASS, brain-faithful Centering/Cb/Principle-B/deixis).
  - Component 2 appraisal sim (MECHANISM_EARNS, own brain-metrics) -- but ISLANDED and on
    SYNTHETIC input; its 1.000 is a mechanism proof, not a text-capability number.
  - Component 6 ToM (HARD_PASS) -- but ISLANDED, not connected to reading.

INVISIBLE-ISLAND HIGH-TIER ORGANS relevant to affective/semantic comprehension (from
capability_registry_audit 2026-08-05: rows=64 WIRED=35 ISLAND=19; of 35 WIRED hdlab modules
only 7 are pipeline-reachable, 28 WIRED-BUT-NOT-PIPELINE-REACHABLE):
  - grounded_appraisal_sim_earned -> islanded (Component 2).
  - theory_of_mind_sally_anne_nested_hrr -> islanded HARD_PASS (Component 6).
  - action_selection_basal_ganglia_gonogo -> validated HARD_PASS, TRAPPED_SHARED (a valuation/
    go-nogo selector that a wired appraisal->action pipeline would want).
  - slot_attention_wm_stateful_core -> trapped_shared secondary track.
  - Audit also FLAGS 60 hdlab/*.py modules with NO registry row (coverage gap), including
    hdlab/semantic.py, hdlab/semantic_parser.py, hdlab/hippocampal_encoder.py,
    hdlab/bayesian_inference.py, hdlab/perceptron.py -- none of which is a lexical-semantic hub.

STRATEGIC READ (flagged hypothesis-pending, not a directive -- Skunkworks is audit-only): the
frontier's "one bottleneck = the valence reader" is CODE-CONFIRMED but UNDER-states it. The
valence reader is the visible tip; the load-bearing absence is the whole ATL-hub + IFG-control
(sense-selection) organ. A better lexicon or more cue-patches (arm_c) will not close it -- the
-0.308 causal regression is the evidence. The brain-foundational fix is to BUILD the missing
learned lexical-semantic representation + context-driven sense selection (glass-box, no borrowed
embedding as the meaning organ per the standing ban), then let valence ride on a
sense-resolved concept rather than a raw surface token.
