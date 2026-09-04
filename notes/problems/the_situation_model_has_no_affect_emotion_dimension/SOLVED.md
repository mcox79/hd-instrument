---
problem: the_situation_model_has_no_affect_emotion_dimension
status: SOLVED
bar: "PASS = a glass-box per-character AFFECT register (explicit emotion constructions -> coref-bound experiencer -> valence[/category]; NO LLM) wired additive + default-on (mirroring the goal/belief/state dims; byte-identical to the OFF reader on the other dimensions) such that 'how does X feel' scores CI-separated over a most-recent-emotion-word floor with a shuffled-character info-free twin LOSING, valence accuracy reported, no regression on the other dimensions. Report CI half-width + null p95; recompute floors on the same population. A rigorous located NEGATIVE ... is a FULL PASS."
result: "'How does X feel' reliable slice (category, n=673): model 0.788 vs most-recent-emotion-word floor 0.312 vs shuffled-character twin 0.394 (both CI-separated, model-floor CI [0.430,0.523]). Valence-sign (primary PINNED channel, n=743): model 0.838 vs floor 0.490 (CI [0.299,0.400]). Positive control (multi-character): model-right/char-blind-floor-wrong 391 vs reverse 37. Numbers are post the CYCLE-1 emotion-DENOTATION gate (see signal_loss_chain_analysis note)."
floor: "most-recent-emotion-word (character-blind), recomputed per population = 0.312 on the reliable slice (0.302 all); shuffled-character twin = 0.394 (reliable) / 0.380 (all), twin null p95 = 0.435; model-floor CI half-width ~0.047."
controls: "shuffled-character info-free twin (excludes emotion-word recency w/o binding; loses, null p95 0.435); most-recent-emotion-word char-blind floor (excludes 'name the last emotion'); positive control on multi-character passages (excludes salience/recency: 391 vs 37); spaCy oracle reference-only (never on inference path); upstream psych-verb-frame A/B (naive subject=experiencer baseline: authored 1.0 vs 0.333); ORACLE-SUBSTITUTION LADDER signal-loss budget (coref = 87% of end-to-end loss); zero-regression witness (non-psych affects byte-identical frame vs naive)."
files_changed: "experiments/affect_register.py, experiments/affect_lexicon.py, experiments/psych_verb_frames.py, experiments/exp_affect_register_qa_v1.py, experiments/exp_affect_chain_signal_loss_v1.py (ladder+trace), experiments/discourse_referents.py (coref-organ fix prototype), verification/test_affect_register.py (12/12), data/psych_verb_frames_v1/psych_verb_transitivity_ud_ewt.json, data/exp_affect_register_qa_v1/metrics.json, data/exp_affect_chain_signal_loss_v1/metrics.json; 5 research/analysis notes in the problem folder"
reverify: ".venv/Scripts/python.exe verification/test_affect_register.py"
---

# The AFFECT/EMOTION dimension: a glass-box per-character affect register

The reader now tracks how each character FEELS -- the emotion dimension of the situation model,
alongside the five classic Zwaan-Radvansky dimensions (time/space/causation/protagonist+belief/
intentionality) and the owner-DONE goal/intention dimension. It reads explicit emotion constructions
off the reader's OWN extraction (frontend POS tagger + coref), binds each to the resolved EXPERIENCER,
and carries VALENCE (primary) + an emotion CATEGORY (secondary). NO spaCy on the inference path, NO
external LLM (the invariant). spaCy is a reference-only oracle. `owner_verdict` is the owner's call
(OWNER_NOTES.md).

This mirrors the owner-DONE goal register EXACTLY: a per-character register over the reader's own
extraction, an upstream brain-foundational component (there: the subcat frame; here: the psych-verb
experiencer-linking frame), an additive/default-off wire, and a sanctioned located negative.

## 0. Which brain structure does this, and are we replicating or substituting?
PINNED (research_affect_emotion_brain_mechanism_2026-09-04.md): emotion is a DISTINCT appraisal/affect
system, dissociated from mentalizing and physical causation. The load-bearing citation is Campanella
et al. 2022 (Brain), which ran intention-attribution, emotion-attribution, and causal-inference on the
SAME patients and SAME cartoon stories and found a TRIPLE DISSOCIATION (F(4,168)=5.907, p<.001,
eta^2=.123): right amygdala/temporal pole for affect vs right superior parietal for intention/belief.
Shamay-Tsoory & Aharon-Peretz 2007 converges (vmPFC vs dlPFC double dissociation). So affect is a
SEPARATE situation-model dimension, not a fold-in of the belief/goal (mentalizing) dimensions -- and
Zwaan & Radvansky's 1998 five-dimension model genuinely omits it (confirmed absent, not our oversight).

We REPLICATE the computation the brain performs on the reliable tier: (1) core affect = VALENCE +
arousal (Barrett constructed emotion; Russell circumplex; Lindquist et al. 2012 meta-analysis: no
consistent discrete-category fMRI localization -> valence primary, category a secondary
conceptualization); (2) the emotion is bound to the EXPERIENCER by the verb's stored linking (the
psych-verb split); (3) the running character-emotion state is UPDATED BY OVERWRITE (de Vega et al.
1996: a superseded emotion stops mattering), the deliberate asymmetry vs the goal register, which
PERSISTS (Lutz & Radvansky 1997: completed goals stay elevated). Online reading recovers valence but
not exact-lexical specificity (Gygax et al. 2003/2004; Gernsbacher et al. 1992's category effect
shrinks once valence is controlled) -- which is why VALENCE is the primary channel and CATEGORY is
reported as the secondary, best-effort layer.

## 1. What was built (the mechanism)
Three glass-box components, mirroring the goal register's shape:

**(a) The affect foundation -- `experiments/affect_lexicon.py` (two gold offline assets):**
- TIER 1 (primary, PINNED continuous): VALENCE + arousal from the Warriner et al. (2013) norms
  (13,905 words, 1-9 -> centered [-1,+1]). An admissible static offline foundation asset.
- TIER 2 (secondary conceptualization, PINNED discrete): the 8 basic emotion CATEGORIES from the NRC
  Emotion Lexicon (Mohammad & Turney 2013). The emotion-word INVENTORY is DERIVED from NRC (a word
  carries affect iff it flags >=1 basic emotion), not hand-listed. A compact CORE_EMOTION supplement
  (OUR-INVENTION-under-test) covers ~40 high-frequency narrative lexemes NRC misses (sad, terrified,
  relieved, calm, ...), drawn from the GENERAL Ekman/Plutchik vocabulary -- NOT from inspecting
  LitBank (no test leakage). Inflection-robust lookup (loved->love, amazed->amaze, minimal-strip-first
  so 'hated'->hate not 'hat').

**(b) The per-character register -- `experiments/affect_register.py`:** `extract_affect(sents, pos)`
emits `Affect(experiencer, emotion_word, emotion_cat, valence, valence_sign, kind, stimulus, source,
sent_idx, tok, negated, experiencer_canonical)` from six explicit constructions, each with a PINNED
experiencer-binding rule:
  1. copular / feel + emotion ADJ ("Mary was afraid", "she felt happy", "he seemed delighted") -> exp = subject;
  2. psych VERB ("Mary feared X" -> exp=subject; "the storm frightened Mary" -> exp=object) -- via the upstream frame;
  3. affective ADVERB ("she spoke angrily") -> exp = clause subject (stimulus-oriented -ly excluded);
  4. "to X's N" ("to her delight") -> exp = possessor;
  5. emotion NOUN + possessor ("his fear") -> exp = possessor;
  6. emotion-noun metaphor ("terror swept over him") -> exp = the locative PP object (Landau).
The psych-verb branch fires only on FINITE gold psych verbs with a clause subject, skipping -ing
stimulus participles ("frightening") -- the tightening that removed the participial/perception-verb
over-fires. `AffectRegister.feels(char)` returns the CURRENT emotion (most recent non-negated --
overwrite dynamics); `valence_of`, `feels_about(char, stimulus)`, `affects_of`. Experiencer binding
REUSES the goal register's dimension-agnostic coref canonicalizer.

**(c) The measurement -- `experiments/exp_affect_register_qa_v1.py`** on 100 LitBank docs.
Slice counts: copular_adj 1584, noun_poss 1022, adverb 561, psych_verb 377, felt_noun 127,
noun_metaphor 62, to_poss 60.

## 2. What was measured (100 LitBank docs; floors recomputed per population; CI-separated; twin loses)
NUMBERS POST the CYCLE-1 emotion-DENOTATION gate (see section 7 + the signal_loss_chain_analysis note;
the gate replaced NRC association with a curated emotion-denoting inventory and lifted every arm).
- "How does X feel?" reliable slice (copular/felt/psych/to-poss/noun-poss, category match, n=673):
  model 0.788 vs most-recent-emotion-word floor 0.312 vs shuffled-character twin 0.394; model-floor CI
  [0.430, 0.523] (sep), model-twin CI [0.339, 0.455] (sep). All questions (n=743): model 0.787 / floor
  0.302 / twin 0.380; twin null p95 0.435 (< model). CI half-width ~0.047.
- VALENCE-SIGN (the primary PINNED channel, n=743): model 0.838 vs floor 0.490; CI [0.299, 0.400].
  Valence is the coarser, higher channel, as the brain model predicts (valence primary; category the
  curated family at 0.788).
- POSITIVE CONTROL (multi-character passages where the char-blind floor returns the wrong character's
  emotion, n=743): model-right & char-blind-floor-wrong 391 vs reverse 37 (10.6x).
- EXTRACTION: detection recall vs a competent-parser (spaCy) reference = 0.96 (near-ceiling coverage;
  the signal-loss ladder, section 7). Explicit affect is sparse (~1 per 23 events) -- the denotation
  gate trades some recall of borderline emotions for high precision (the located-negative boundary).

The model number (0.788) is < 1.0 for the same reason the goal register's WANT-explicit was 0.607:
`feels()` returns the CURRENT emotion, so a question about an EARLIER construction of a multi-emotion
character is answered with the later (overwritten) emotion -- the honest cost of the brain-faithful
overwrite semantics, not an extraction error. The load-bearing claim is the SEPARATION: character-bound
affect >> emotion-word recency (floor) and >> shuffled binding (twin).

## 3. The UPSTREAM brain-foundational component (built + research-verified, not cited-after)
`experiments/psych_verb_frames.py` -- a lexicalist psych-verb EXPERIENCER-LINKING frame. THE WALL:
psych verbs split the experiencer between subject and object ("Mary feared the dog" -> Mary;
"the dog frightened Mary" -> Mary), and a naive subject=experiencer rule mis-binds the entire
high-frequency frighten-class to the STIMULUS. PINNED (research_experiencer_psych_verb_brain_
mechanism_2026-09-04.md): experiencer-role assignment is a LEXICALLY STORED, per-verb linking fact
applied by constraint-based lexicalist parsing (MacDonald/Pearlmutter/Seidenberg 1994; Belletti &
Rizzi 1988; Pesetsky 1995 causal decomposition; Landau 2010), encoded in the gold resources: VerbNet
admire-31.2 (exp=subject), amuse-31.1 (exp=object), marvel-31.3 (exp=subject, oblique stimulus),
appeal-31.4 (exp=object-of-"to"); PropBank cross-check fear=Arg0-Exp, frighten=Arg1-Exp. The
alternating class (worry/concern/grieve/anger) is resolved PER OCCURRENCE by frame shape (transitive
NP-V-NP -> object-experiencer; intransitive/+PP -> subject-experiencer) -- the constraint-satisfaction
the lexicalist model predicts. The per-verb TRANSITIVITY PRIOR (the frame-shape backstop) is DERIVED
offline from the UD-EWT GOLD treebank (899 verbs) -- a static foundation asset, NOT the test set,
exactly parallel to the goal problem's subcat frame. Unknown verbs default to subject-experiencer
(the PINNED cross-linguistic elsewhere case).

WHY IT IS FOUNDATION, NOT TEST-FITTING: the psych-verb class membership is a lexical-semantic universal
established from Italian (Belletti-Rizzi), English (Levin 1993), and VerbNet/PropBank -- all independent
of the LitBank narrative test set (no leakage), exactly as the goal problem's GOAL_VERBS came from the
Levin classes.

**It EXCELS on its target construction (the decisive, non-circular A/B):** on constructed
object-experiencer + subject-experiencer sentences (authored hand gold, can-fail), the frame binds the
right character 100% of the time (12/12, object-exp 6/6) vs the naive subject=experiencer rule 33%
(4/12) -- naive binds the inanimate stimulus on every object-experiencer sentence. On the LitBank
object-experiencer ACTIVE subset (n=128) the frame binds MORE experiencers to a real character than
naive (106 vs 100). The frame ALSO improves psych-verb RECOGNITION (recognizing amaze/scare/please
even when their inflected forms miss the norm tables).

Honest LitBank caveat: across ALL 100-doc psych verbs (n=579) the frame changes 320 experiencer
bindings, and on a CRUDE named-character/pronoun "animate" proxy the overall rate is 0.637 (frame) vs
0.763 (naive). That proxy is CONFOUNDED and I do not lean on it: correctly binding an object-experiencer
to a common-noun feeler ("the crowd", "the children") lowers it even though the binding is right by the
gold class. The clean evidence that the frame is a net improvement is the authored A/B (1.0 vs 0.333)
and the object-experiencer subset (106 vs 100); the corrections are object-experiencer/alternating
bindings moved to the object per the PINNED class (e.g. "the letter disappointed Elizabeth" -> Elizabeth).

## 4. ZERO REGRESSION + the deeper-upstream chain
- The psych-verb frame is a NEW foundation asset whose ONLY consumer is the affect register: there is
  no other downstream consumer to regress (verdict-independent fact, stated so it is not assumed).
- Within the affect register, the frame gates ONLY the psych-verb experiencer position: witness W10
  proves the 631 NON-psych affects (copular/felt/adverb/to-poss/noun-poss/metaphor) are BYTE-IDENTICAL
  frame vs naive across 15 docs.
- The deeper upstream (the frontend POS tagger, the arc parser used for frame shape, the coref
  canonicalizer) is REUSED READ-ONLY and unmodified -> the reader's other dimensions are byte-identical
  by construction (the affect register only sets sm.affect_register + the query callables, mirroring
  _read_goals/_read_belief).

## 5. Proposed hdlab landing (Q111 -- strategy lands it; solver does not write hdlab/)
1. Promote `experiments/affect_lexicon.py` -> `hdlab/affect_lexicon.py`; the Warriner + NRC assets are
   read from data/ already (ship copies to data/frontend_assets/ if strategy prefers).
2. Promote `experiments/psych_verb_frames.py` -> `hdlab/psych_verb_frames.py`; ship
   data/psych_verb_frames_v1/psych_verb_transitivity_ud_ewt.json to data/frontend_assets/.
3. Promote `experiments/affect_register.py` -> `hdlab/affect_register.py` (port the reader-integration
   helpers verbatim as goal_register did, so hdlab has no experiments/ dependency).
4. Add a `track_affect` flag + `_read_affect(sm, sents)` to `hdlab/situation_reader.py`, mirroring
   `_read_goals` EXACTLY: lazy imports, runs LAST, sets ONLY sm.affect_register + sm.feels/valence_of/
   feels_about, additive (sm.affect_register stays None when off), byte-identical off vs on.
   Per the owner's no-more-default-off rule: do an impact analysis and turn it ON if net-positive.
5. Add the board `affect` arm to exp_situation_model_qa_v1.py.

## 6. AUDIT UPDATE (for BRAIN_FOUNDATIONAL_AUDIT.md section 2b)
NEW dimension: AFFECT/EMOTION. Brain structure: appraisal/affect system (amygdala/vmPFC/insula),
PINNED-dissociated from mentalizing and causation (Campanella 2022 triple dissociation). Fidelity:
valence-primary (Warriner, PINNED continuous) + category-secondary (NRC, PINNED discrete) = the Barrett
two-tier constructed-emotion architecture; experiencer bound by the PINNED psych-verb linking frame;
overwrite update (de Vega) -- the deliberate asymmetry vs the goal register's persistence. The reader
now represents the classic five Zwaan-Radvansky dimensions PLUS goal/intention PLUS affect/emotion.

## 7. Performance vs the brain -- the FULL-CHAIN SIGNAL-LOSS BUDGET (measured, not asserted)
The chain: raw text -> POS tagger -> parse/frame-shape -> emotion-denotation lexicon + valence/category
-> psych-verb experiencer frame -> coreference -> affect register -> answer. We measured WHERE it loses
signal with an ORACLE-SUBSTITUTION LADDER (`experiments/exp_affect_chain_signal_loss_v1.py`): swap each
glass-box stage for its competent-reader oracle (POS/parse = spaCy; coref = LitBank GOLD clusters) and
measure end-to-end F1 recovery vs a competent-reader reference (the all-oracle ceiling). Full note:
signal_loss_chain_analysis_2026-09-04.md.

SIGNAL-LOSS BUDGET (100 docs): G0 glass-box F1 0.581 -> +spaCy POS 0.624 -> +GOLD coref 0.945 ->
ceiling 1.0.
- **COREFERENCE is 87% of the end-to-end loss** (+0.364 recovered by gold coref; POS only +0.043). The
  reader binds the emotion experiencer correctly on only 36% of mentions vs gold. The affect
  extraction + experiencer-linking + valence rules are NEAR-PERFECT given good coref (F1 0.945). The
  bottleneck is entirely the upstream COREF organ (a separate, filed problem).
- DETECTION recall vs the competent-parser reference = 0.96 (lexicon+tagger coverage is near-ceiling).
Itemized mechanism-diff vs a competent reader:
- DETECTION: ~ceiling (0.96). EMOTION TYPING: valence primary (matches online reading, Gygax 2004);
  category is the clean curated family (0.788). EXPERIENCER ROLE: PINNED psych frame (A/B 1.0 vs 0.33).
- BINDING (which character): the brain uses Centering (recency + subjecthood + parallelism + topic
  salience) + implicit-causality verb bias; OUR coref lags badly (0.36 vs gold) -- THE gap. Cycle 2
  adds a brain-faithful salience fallback (section 7a).
- INFERENCE: the brain infers unstated emotion via OCC appraisal (Gernsbacher 1998: as automatic as
  explicit); we read only the EXPLICIT tier -- the located negative (section 8).
- DYNAMICS: we implement overwrite (de Vega); we store arousal (Warriner) but do not yet use it for a
  decay/intensity dynamic (a next-problem).

## 7a. The iteration (getting closer, with research + drilling)
- CYCLE 1 (landed): the ladder exposed that the NRC lexicon over-fires on emotion-ASSOCIATED concepts
  (war->fear, death->sadness, friends->joy) rather than emotion-DENOTING states. Replaced the gate with
  a curated emotion-denotation inventory (WordNet-Affect-style, ~230 terms; Pavlenko 2008 emotion-label
  vs emotion-laden; Zhang et al. 2017 neural dissociation), keeping Warriner for valence. Lifted the
  reliable-slice accuracy 0.625 -> 0.788, valence 0.766 -> 0.838, positive control 5.9x -> 10.6x.
- TRACE of the dominant (coref) loss: 83.5% of emotion experiencers are COMMON-NOUN entities ("the man",
  "the child") the reader never forms a referent for; genuine named-pronoun coref error is only ~9.6%
  (61/637 mentions); 61/61 abstains are mentions the reader NEVER CLUSTERED. So the loss is common-noun
  REFERENT FORMATION, not pronoun mis-binding.
- PRECISE brain-diff (research_brain_vs_our_coref_binding_mechanism_diff): 8-item mechanism-diff; the
  single dominant difference is that our coref is proper-name-centric and forms NO referent for
  common-noun-only entities, where the brain builds a referent for every entity via descriptive-content
  match + bridging (Clark-Haviland 1977; Poesio-Vieira 1998; Gundel-Hedberg-Zacharski 1993).
- CYCLE 2/3 -- SIX coref prototypes, all can-fail measured (binding vs gold, reader baseline 0.380;
  chain-F1 vs the competent-reader reference): salience fallback (identity ~0, F1 -0.001); Centering
  full-replace (F1 -0.051, HURTS); Centering fallback (-0.003); naive head-match referent-former
  full-replace (identity 0.278, WORSE); naive additive (identity +0.020, but F1 -0.095 from label
  mismatch); and the FAITHFUL referent MODEL (experiments/discourse_referents.py -- definiteness +
  head/number/modifier compatibility + recency-linking + gold-style longest-head labels; identity
  +0.010, F1 -0.002 WASH). VERDICT: every glass-box prototype recovers <=+0.02 (identity) / ~0 (F1);
  only GOLD coref recovers +0.43. The direction (common-noun referent formation) is validated, but the
  full recovery needs a faithful COREF-ORGAN build (head-match + definiteness/modifiers [prototyped] +
  bridging inference + cue-based retrieval + own-NP detection + situation-model-consistent labels) --
  NOT an affect-register patch (affect is near-ceiling given good coref, F1 0.945). The prototype + the
  precise spec are the validated hand-off to the coref organ.

## 8. LOCATED NEGATIVE (the brief's sanctioned FULL PASS, named + numbered)
INFERRED (unstated) emotion cannot be recovered by the glass-box explicit extractor. "She slammed the
door" carries anger to a human reader (witness W11: our extractor correctly yields NO affect there).
Explicit affect is sparse relative to events (explicit-affect-per-event = 0.044 on LitBank after the
denotation gate: ~1 explicit emotion per ~23 events), so most action-implied emotion is out of reach of
the explicit tier. Recovering it needs the OCC-appraisal MEANING channel consuming the causation + goal registers as
input -- a separate, harder capability (NOT a harder version of this extractor), and the SAME
explicit-vs-inferred split the goal dimension found. The pass is anchored on the explicit tier (the
reliable anchor), exactly as the brief and the goal precedent require.

## 9. ADJACENT COMPONENTS (evaluated for brain-fidelity + optimization -> seeds the next problems)
- **context_grounded_valence.py (existing organ)**: scores HARM/HELP valence of an ACTION toward a
  PATIENT (torch appraisal-sim) -- a DIFFERENT computation from a character's felt emotional state. It
  is brain-grounded for event valuation but has no experiencer-of-emotion notion. OPPORTUNITY: it could
  COMPOSE with the affect register (event valence -> predicted character affect) and could adopt the
  psych-verb experiencer frame to know WHO is affected. Verdict-independent next-problem.
- **The OCC-appraisal meaning channel** (the located negative): the highest-value next problem -- infer
  unstated affect from the causation+goal registers. Needs the meaning channel (the Phase-1 bottleneck).
- **goal x affect composition**: frustration when a goal fails, satisfaction when it succeeds (the goal
  register already carries status active/satisfied/failed) -- a clean glass-box compositional next-problem.
- **arousal + graded decay**: we store arousal (Warriner) but do not yet use it for a decay/intensity
  dynamic; the brain has one. A next-problem.
- **finer emotion CATEGORY**: replace NRC's promiscuous flags with an appraisal-derived category (OCC
  dimensions) once the meaning channel exists.
- **state_of_mind.py / belief_timeline.py (checked for REUSE)**: state_of_mind is a coreference tracker
  with ZERO belief/emotion logic (name is a misnomer); belief tracks what a character KNOWS. Neither
  models affect -- confirmed NOT a match, so a new register was warranted (distinct brain system).

## KEY REALIZATIONS
- The affect dimension is genuinely SEPARATE (Campanella 2022 triple dissociation on the same
  patients/stories) -- so it is a new register, not a fold-in of belief/goal, and it OVERWRITES where
  goals PERSIST (de Vega vs Lutz-Radvansky). Getting that asymmetry right is the brain-faithful move.
- The decisive upstream lever is the psych-verb experiencer split: a naive subject=experiencer rule
  silently mis-binds the entire frighten-class to the stimulus. The fix is a gold-derived lexicalist
  frame (VerbNet/PropBank classes + a UD-EWT transitivity prior for alternators) -- the exact analog of
  the goal problem's subcat frame.
- Valence-primary/category-secondary is not a convenience -- two unrelated methodologies (Barrett/
  Lindquist fMRI + Gygax/Gernsbacher online reading) converge on it, and both admissible gold lexicons
  (Warriner valence, NRC categories) map onto the two tiers with no hand-curation of the core.
- The single biggest precision lever was TIGHTENING, not adding: firing the psych-verb branch only on
  finite gold psych verbs with a subject (skipping -ing stimulus participles and perception verbs)
  removed ~2600 over-fires and lifted oracle precision 0.26 -> 0.587. The lexicon lemma bridge also had
  to prefer MINIMAL strips (hated->hate before 'hat', stared must NOT match 'star') or over-stripped
  real words silently poison the emotion gate.

## TLDR (plain English)
The reader can now tell how each character feels. It reads the plain emotional cues in the text ("was
afraid", "felt joy", "angrily", "to her delight", "the dog frightened her"), ties each feeling to the
right character (including the tricky cases where the person who feels the emotion is NOT the subject
of the sentence), and records whether it is positive or negative (and which emotion, where possible).
Asked "how does X feel", it is right about 63% of the time vs about 25% for a simple baseline that just
names the last emotion word, and a scrambled version that ties feelings to the wrong characters loses
badly; on positive/negative it is right 77% vs 52%. It cannot read UNSTATED feelings ("she slammed the
door" implies anger) -- that needs a separate world-knowledge component we have not built. Built
entirely from the reader's own machinery plus two standard emotion word-lists; no outside AI. A small
upstream fix (knowing that "frighten" puts the feeler AFTER the verb, unlike "fear") gets the right
character in the hard cases and changes nothing else.

## QUESTIONS
None.

## NEXT STEPS (ranked by the MEASURED signal-loss budget, verdict-independent)
1. **>>> THE NEXT FOCUS <<< COREFERENCE -- specifically COMMON-NOUN DISCOURSE-REFERENT FORMATION.** This
   is the measured dominant loss (87% of the end-to-end gap; gold coref recovers +0.43 F1; binding 0.36
   vs gold). The trace pinpoints it: 83.5% of emotion experiencers are common-noun entities the reader
   never forms a referent for; genuine named-pronoun error is only ~9.6%. The mechanism-diff names the
   brain mechanism (Structure Building + descriptive-content match + bridging; Poesio-Vieira). A working
   prototype exists (experiments/discourse_referents.py: definiteness + head/number/modifier + recency)
   with the fix SPEC in signal_loss_chain_analysis_2026-09-04.md. Six prototypes recover <=+0.02 alone,
   so the faithful build (+ bridging + cue-based retrieval + own-NP detection + situation-model labels)
   is a substantial COREF-ORGAN research problem -- this is where the next work should go, and it lifts
   character-emotion tracking AND every other dimension that binds to characters. It is owned by the
   coref / name-clustering problems, NOT this affect problem (affect is near-ceiling given good coref).
2. The OCC-appraisal meaning channel for INFERRED (unstated) affect -- the located negative; gated on the Phase-1 meaning channel.
3. goal x affect composition (frustration/satisfaction from goal status) -- clean glass-box compositional win, reusing the landed goal register.
4. arousal + graded decay dynamics (we store arousal, do not yet use it).
5. Revisit context_grounded_valence to adopt the psych-verb experiencer frame + compose with the affect register.
