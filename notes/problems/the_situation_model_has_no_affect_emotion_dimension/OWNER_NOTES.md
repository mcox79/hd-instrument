---
owner_verdict:
---

SOLVED (pending your verdict) -- the_situation_model_has_no_affect_emotion_dimension (opus 4.8 solver)

WHAT: the reader now tracks how each character FEELS -- the EMOTION dimension of the situation model,
alongside time/space/causation/protagonist+belief/intentionality and the goal/intention dimension you
just accepted. It reads explicit emotion cues off the reader's own extraction ("was afraid", "felt
joy", "angrily", "to her delight", "the dog frightened her"), ties each to the right character, and
records positive/negative valence (+ emotion category). NO outside AI; spaCy is a reference-only
checker, never on the inference path. Built the SAME way as the goal register.

RESULT (100 LitBank docs; floors recomputed per population; twin loses; CI-separated):
- "How does X feel?" reliable slice (which emotion, n=673): model 0.788 vs 'name the last emotion word'
  floor 0.312 vs shuffled-character twin 0.394 (both CI-separated).
- Valence (positive/negative, the primary channel, n=743): model 0.838 vs floor 0.490 (CI-separated).
- Binds the RIGHT character (multi-character positive control): 391 vs 37.

WE THEN BUILT THE FULL BRAIN-FOUNDATIONAL CHAIN AND MEASURED WHERE IT LOSES SIGNAL (an
oracle-substitution ladder: swap each stage for a competent-reader oracle, measure the recovery):
- The chain is raw text -> tagger -> parse -> emotion lexicon + valence -> experiencer-linking ->
  COREFERENCE -> affect register -> answer.
- FINDING: 87% of the end-to-end signal loss is COREFERENCE. With perfect coreference the whole chain
  scores 0.945 (near-perfect); the emotion reading, valence, and experiencer-linking are essentially
  solved. The single highest-value thing we could do to improve character-emotion tracking is improve
  the coreference organ (a separate component, already its own open problem).
- Emotion DETECTION is near-ceiling (0.96 recall vs a competent parser). POS costs ~4%.

ITERATION (getting closer, with research + drilling):
- CYCLE 1 (landed): the ladder revealed our emotion word-list (NRC) was flagging emotion-ASSOCIATED
  concepts ("war", "death", "money", "friends", "married", "excellent") rather than words that name a
  FELT STATE. We swapped it for a curated emotion-DENOTING vocabulary (an established distinction:
  emotion-label vs emotion-laden words, which even dissociate in brain recordings). That single fix
  raised "how does X feel" from 0.63 to 0.79 and positive/negative from 0.77 to 0.84.
- CYCLE 2 (the dominant loss): added a brain-faithful fallback -- when coreference cannot resolve an
  experiencer pronoun, bind it to the most-salient matching character (Centering theory's topic
  salience). Measured as a ladder rung; the full coref gap belongs to the coref organ.

LOCATED NEGATIVE (a full pass per the brief): the reader cannot recover UNSTATED emotion ("she slammed
the door" implies anger) -- that needs a separate world-knowledge/meaning component (the same
explicit-vs-inferred split the goal dimension found). Anchored on the explicit, reliable tier.

files: experiments/{affect_register.py, affect_lexicon.py, psych_verb_frames.py,
exp_affect_register_qa_v1.py, exp_affect_chain_signal_loss_v1.py}, verification/test_affect_register.py
(12/12 PASS), data/psych_verb_frames_v1/..., data/exp_affect_register_qa_v1/metrics.json,
data/exp_affect_chain_signal_loss_v1/metrics.json. Four research notes + a signal-loss chain analysis
note in this folder. NO hdlab written (Q111 -- strategy lands the wire + the board `affect` arm).

Reverify (re-runs NO landed cell): .venv/Scripts/python.exe verification/test_affect_register.py  # 12/12
