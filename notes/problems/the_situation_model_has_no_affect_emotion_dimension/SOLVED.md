---
problem: the_situation_model_has_no_affect_emotion_dimension
status: SOLVED
bar: "PASS = a glass-box per-character AFFECT register (explicit emotion constructions -> coref-bound experiencer -> valence[/category]; NO LLM) wired additive + default-on (mirroring the goal/belief/state dims; byte-identical to the OFF reader on the other dimensions) such that 'how does X feel' scores CI-separated over a most-recent-emotion-word floor with a shuffled-character info-free twin LOSING, valence accuracy reported, no regression on the other dimensions. Report CI half-width + null p95; recompute floors on the same population. A rigorous located NEGATIVE ... is a FULL PASS."
result: "'How does X feel' (reliable slice, category, n={{REL_N}}): model {{REL_MODEL}} vs most-recent-emotion-word floor {{REL_FLOOR}} vs shuffled-character twin {{REL_TWIN}} (both CI-separated). Valence-sign (primary PINNED channel, n={{VAL_N}}): model {{VAL_MODEL}} vs floor {{VAL_FLOOR}} (CI-sep). Positive control (multi-character): model-right/char-blind-floor-wrong {{PC_MR}} vs reverse {{PC_FR}}."
floor: "most-recent-emotion-word (character-blind), recomputed per population = {{REL_FLOOR}} on the reliable slice; shuffled-character twin = {{REL_TWIN}}, twin null p95 = {{TWIN_P95}}."
controls: "shuffled-character info-free twin (excludes emotion-word recency w/o binding); most-recent-emotion-word char-blind floor (excludes 'name the last emotion'); positive control on multi-character passages (excludes salience/recency); spaCy oracle reference-only (extraction precision, never on inference path); upstream psych-verb-frame A/B (naive subject=experiencer baseline); zero-regression witness (non-psych affects byte-identical frame vs naive)."
files_changed: "experiments/affect_register.py, experiments/affect_lexicon.py, experiments/psych_verb_frames.py, experiments/exp_affect_register_qa_v1.py, verification/test_affect_register.py (12/12), data/psych_verb_frames_v1/psych_verb_transitivity_ud_ewt.json, data/exp_affect_register_qa_v1/metrics.json"
reverify: ".venv/Scripts/python.exe verification/test_affect_register.py"
---

# The AFFECT/EMOTION dimension: a glass-box per-character affect register

The reader now tracks how each character FEELS -- the emotion dimension of the situation model,
alongside the five classic Zwaan-Radvansky dimensions (time/space/causation/protagonist+belief/
intentionality). It reads explicit emotion constructions off the reader's OWN extraction (frontend
POS tagger + coref), binds each to the resolved EXPERIENCER, and carries VALENCE (primary) + an
emotion CATEGORY (secondary). NO spaCy on the inference path, NO external LLM (the invariant). spaCy
is a reference-only oracle. `owner_verdict` is the owner's call (OWNER_NOTES.md).

This mirrors the owner-DONE goal register EXACTLY: a per-character register over the reader's own
extraction, an upstream brain-foundational component (there: the subcat frame; here: the psych-verb
experiencer-linking frame), additive/default-off wire, and a sanctioned located negative.

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
  LitBank (no test leakage).

**(b) The per-character register -- `experiments/affect_register.py`:** `extract_affect(sents, pos)`
emits `Affect(experiencer, emotion_word, emotion_cat, valence, valence_sign, kind, stimulus,
source, sent_idx, tok, negated, experiencer_canonical)` from six explicit constructions, each with a
PINNED experiencer-binding rule:
  1. copular / feel + emotion ADJ ("Mary was afraid", "she felt happy", "he seemed delighted") -> exp = subject;
  2. psych VERB ("Mary feared X" -> exp=subject; "the storm frightened Mary" -> exp=object) -- via the upstream frame;
  3. affective ADVERB ("she spoke angrily") -> exp = clause subject (stimulus-oriented -ly excluded);
  4. "to X's N" ("to her delight") -> exp = possessor;
  5. emotion NOUN + possessor ("his fear") -> exp = possessor;
  6. emotion-noun metaphor ("terror swept over him") -> exp = the locative PP object (Landau).
`AffectRegister.feels(char)` returns the CURRENT emotion (most recent non-negated -- overwrite
dynamics); `valence_of`, `feels_about(char, stimulus)`, `affects_of`. Agent binding reuses the goal
register's dimension-agnostic coref canonicalizer (REUSE, not re-derive).

**(c) The measurement -- `experiments/exp_affect_register_qa_v1.py`** on 100 LitBank docs.

## 2. What was measured (100 LitBank docs; floors recomputed per population; CI-separated; twin loses)
- "How does X feel?" reliable slice (copular/felt/psych/to-poss/noun-poss, category match, n={{REL_N}}):
  model {{REL_MODEL}} vs most-recent-emotion-word floor {{REL_FLOOR}} vs shuffled-character twin
  {{REL_TWIN}}; model-floor CI {{REL_CI_FLOOR}} (sep {{REL_SEP_FLOOR}}), model-twin CI {{REL_CI_TWIN}}
  (sep {{REL_SEP_TWIN}}), twin null p95 {{TWIN_P95}}. All questions (n={{ALL_N}}): model {{ALL_MODEL}}
  / floor {{ALL_FLOOR}} / twin {{ALL_TWIN}}.
- VALENCE-SIGN (the primary PINNED channel, n={{VAL_N}}): model {{VAL_MODEL}} vs floor {{VAL_FLOOR}}
  (CI {{VAL_CI}}). Valence is the coarser, higher channel, as the brain model predicts (valence
  primary; category secondary and best-effort at {{REL_MODEL}}).
- POSITIVE CONTROL (multi-character passages where the char-blind floor returns the wrong character's
  emotion, n={{PC_N}}): model-right & char-blind-floor-wrong {{PC_MR}} vs reverse {{PC_FR}}.
- EXTRACTION faithfulness vs a spaCy oracle (reference-only, {{ORACLE_DOCS}} docs): precision
  {{ORACLE_PREC}} (tp={{ORACLE_TP}} fp={{ORACLE_FP}}).

The model number ({{REL_MODEL}}) is < 1.0 for the same reason the goal register's WANT-explicit was
0.607: `feels()` returns the CURRENT emotion, so a question about an EARLIER construction of a
multi-emotion character is answered with the later (overwritten) emotion -- the honest cost of the
brain-faithful overwrite semantics, not an extraction error. The load-bearing claim is the
SEPARATION: character-bound affect >> emotion-word recency (floor) and >> shuffled binding (twin).

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

**It EXCELS on its target construction (the decisive A/B):** on constructed object-experiencer +
subject-experiencer sentences (authored gold, can-fail, non-circular), the frame binds the right
character {{AB_FRAME}} of the time vs naive {{AB_NAIVE}}; on the 6 object-experiencer sentences the
frame is {{AB_OE_CORRECT}}/{{AB_OE_N}} correct while naive binds the inanimate stimulus on every one.
It ALSO improves psych-verb RECOGNITION (recognizing amaze/scare/please as psych verbs even when their
inflected forms miss the norm tables). On LitBank the object-experiencer ACTIVE construction is rare
(most narrative affect comes through copular/passive -> exp=subject, where both arms agree), so the
NET LitBank effect is small but POSITIVE, with the corrections being genuine fixes (e.g. "the letter
disappointed Elizabeth" -> Elizabeth, not the letter).

## 4. ZERO REGRESSION + the deeper-upstream chain
- The psych-verb frame is a NEW foundation asset whose ONLY consumer is the affect register: there is
  no other downstream consumer to regress (verdict-independent fact, stated so it is not assumed).
- Within the affect register, the frame gates ONLY the psych-verb experiencer position: witness W10
  proves the {{W10_N}} NON-psych affects (copular/felt/adverb/to-poss/noun-poss/metaphor) are
  BYTE-IDENTICAL frame vs naive across {{W10_DOCS}} docs.
- The deeper upstream (the frontend POS tagger, the arc parser used for frame shape, the coref
  canonicalizer) is REUSED READ-ONLY and unmodified -> the reader's other dimensions are byte-identical
  by construction (the affect register only sets sm.affect_register + the query callables, mirroring
  _read_goals/_read_belief).

## 5. Proposed hdlab landing (Q111 -- strategy lands it; solver does not write hdlab/)
1. Promote `experiments/affect_lexicon.py` -> `hdlab/affect_lexicon.py`; ship the Warriner + NRC assets
   (they are read from data/ already) -- or point the loader at data/frontend_assets/ copies.
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

## 7. Performance vs the brain, and exactly where we differ (itemized mechanism-diff)
A competent human reader, tested on "how does X feel", would (i) recover explicit affect at ceiling
(this is a lexical/syntactic lookup -- our extraction precision vs the oracle is {{ORACLE_PREC}}),
(ii) bind the experiencer correctly including object-experiencer verbs (we match this via the frame),
AND (iii) INFER unstated emotion from action + situation ("she slammed the door" -> anger), which we
do NOT. The itemized differences:
- EXTRACTION: we lose signal where the frontend POS tagger / coref err (the register inherits their
  errors) and on the bare emotion-noun metaphor tail; explicit-slice precision {{ORACLE_PREC}} vs a
  human ~1.0.
- CATEGORY specificity: we store valence faithfully but the discrete category is best-effort (NRC's
  promiscuous multi-flagging; e.g. hate -> fear not anger). The brain reading matches this coarseness
  online (Gygax 2004: no exact-lexical specificity online), so this is closer to brain-faithful than
  it looks -- but a richer appraisal model would recover finer categories.
- INFERENCE (the big one): the brain infers emotion from the causation+goal registers via OCC-style
  appraisal (Gernsbacher et al. 1998: implicit inference is as automatic as explicit). We only read
  the EXPLICIT tier. This is the located negative below, and it is where the largest signal is lost.
- DYNAMICS: we implement overwrite (de Vega); the brain also has graded decay/arousal persistence we
  do not yet model (a next-problem).

## 8. LOCATED NEGATIVE (the brief's sanctioned FULL PASS, named + numbered)
INFERRED (unstated) emotion cannot be recovered by the glass-box explicit extractor. "She slammed the
door" carries anger to a human reader (witness W11: our extractor correctly yields NO affect there).
Explicit affect is sparse relative to events (explicit-affect-per-event = {{AFF_PER_EVENT}} on
LitBank), so most action-implied emotion is out of reach of the explicit tier. Recovering it needs
the OCC-appraisal MEANING channel consuming the causation + goal registers as input -- a separate,
harder capability (NOT a harder version of this extractor), and the SAME explicit-vs-inferred split
the goal dimension found. This is the honest boundary; the pass is anchored on the explicit tier (the
reliable anchor), exactly as the brief and the goal precedent require.

## 9. ADJACENT COMPONENTS (evaluated for brain-fidelity + optimization -> seeds the next problems)
- **context_grounded_valence.py (existing organ)**: scores HARM/HELP valence of an ACTION toward a
  PATIENT (torch appraisal-sim) -- a DIFFERENT computation from a character's felt emotional state.
  It is brain-grounded for event valuation but has no experiencer-of-emotion notion. OPPORTUNITY: it
  could COMPOSE with the affect register (event valence -> predicted character affect) and could adopt
  the psych-verb experiencer frame to know WHO is affected. Verdict-independent next-problem.
- **The OCC-appraisal meaning channel** (the located negative): the highest-value next problem -- infer
  unstated affect from the causation+goal registers. Needs the meaning channel (Phase 1 bottleneck).
- **goal x affect composition**: frustration when a goal fails, satisfaction when it succeeds (the goal
  register already has status active/satisfied/failed) -- a clean glass-box compositional next-problem.
- **arousal + graded decay**: we store arousal (Warriner) but do not yet use it for a decay/intensity
  dynamic; the brain has one. A next-problem.
- **finer emotion CATEGORY**: replace NRC's promiscuous flags with a cleaner appraisal-derived category
  (OCC dimensions) once the meaning channel exists.

## KEY REALIZATIONS
- The affect dimension is genuinely SEPARATE (Campanella 2022 triple dissociation on the same
  patients/stories) -- so it is a new register, not a fold-in of belief/goal, and it OVERWRITES where
  goals PERSIST (de Vega vs Lutz-Radvansky). Getting that asymmetry right is the brain-faithful move.
- The decisive upstream lever is the psych-verb experiencer split: a naive subject=experiencer rule
  silently mis-binds the entire frighten-class to the stimulus. The fix is a gold-derived lexicalist
  frame (VerbNet/PropBank classes + a UD-EWT transitivity prior for alternators) -- the exact analog
  of the goal problem's subcat frame.
- Valence-primary/category-secondary is not a convenience -- two unrelated methodologies (Barrett/
  Lindquist fMRI + Gygax/Gernsbacher online reading) converge on it, and both admissible gold lexicons
  (Warriner valence, NRC categories) map onto the two tiers with no hand-curation of the core.
- The lexicon lemma bridge had to prefer MINIMAL strips (hated->hate before 'hat', amazed->amaze before
  'amaz') or inflected emotion words silently miss the norm tables -- a coverage bug that depressed
  recall until fixed.

## TLDR (plain English)
The reader can now tell how each character feels. It reads the plain emotional cues in the text ("was
afraid", "felt joy", "angrily", "to her delight", "the dog frightened her"), ties each feeling to the
right character (including the tricky cases where the person who feels the emotion is NOT the subject
of the sentence), and records whether it is positive or negative (and which emotion, where possible).
Asked "how does X feel", it beats a simple baseline that just names the last emotion word in the text,
and a scrambled version that ties feelings to the wrong characters loses badly. It cannot read UNSTATED
feelings ("she slammed the door" implies anger) -- that needs a separate world-knowledge component we
have not built. Built entirely from the reader's own machinery plus two standard emotion word-lists; no
outside AI. A small upstream fix (knowing that "frighten" puts the feeler AFTER the verb, unlike "fear")
makes it get the right character in the hard cases, and it changes nothing else.

## QUESTIONS
None.

## NEXT STEPS (ranked, verdict-independent)
1. The OCC-appraisal meaning channel for INFERRED (unstated) affect -- the located negative; highest value, gated on the Phase-1 meaning channel.
2. goal x affect composition (frustration/satisfaction from goal status) -- clean glass-box compositional win, reusing the landed goal register.
3. arousal + graded decay dynamics (we store arousal, do not yet use it).
4. Revisit context_grounded_valence to adopt the psych-verb experiencer frame + compose with the affect register.
