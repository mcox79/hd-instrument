---
owner_verdict:
---

SOLVED (pending your verdict) -- the_situation_model_has_no_affect_emotion_dimension (opus 4.8 solver)

WHAT: the reader now tracks how each character FEELS -- the EMOTION dimension of the situation model,
alongside time/space/causation/protagonist+belief/intentionality and the goal/intention dimension you
just accepted. It reads explicit emotion cues off the reader's own extraction ("was afraid", "felt
joy", "angrily", "to her delight", "the dog frightened her"), ties each to the right character, and
records positive/negative valence (+ the emotion category where possible). NO outside AI; spaCy is a
reference-only checker, never on the inference path. Built the SAME way as the goal register.

RESULT (100 LitBank docs; floors recomputed per population; twin loses; CI-separated):
- "How does X feel?" reliable slice (which emotion, n=3170): model 0.625 vs 'name the last emotion
  word' floor 0.257 vs shuffled-character twin 0.265 (both CI-separated; twin null p95 0.271).
- Valence (positive/negative, the primary channel, n=3793): model 0.766 vs floor 0.519 (CI-separated).
- Binds the RIGHT character (multi-character positive control): model-right / char-blind-floor-wrong
  1760 vs reverse 296.
- Extraction faithfulness vs a fair spaCy oracle (reference-only): precision 0.587.

UPSTREAM brain-foundational component (built + research-verified, not cited-after): a psych-verb
EXPERIENCER-LINKING frame. English splits WHO feels the emotion between the subject ("Mary FEARED the
dog" -> Mary) and the object ("the dog FRIGHTENED Mary" -> Mary); a naive "the subject feels it" rule
mis-binds the entire frighten-class to the thing that CAUSED the feeling. The frame (from the standard
VerbNet/PropBank verb classes + a transitivity prior derived from a gold treebank) fixes this: on
constructed test sentences it binds the right character 100% of the time (12/12) vs 33% (4/12) for the
naive rule, and it changes NOTHING else (the 631 non-psych emotions are byte-identical with and without
it -- witness W10). On real narrative the object-experiencer case is rarer (most emotion is stated as
"she was frightened", where both agree); on that subset the frame still binds more feelings to a real
character than naive (106 vs 100), and the corrections are genuine fixes (e.g. "the letter disappointed
Elizabeth" -> Elizabeth, not the letter).

LOCATED NEGATIVE (a full pass per the brief): the reader cannot recover UNSTATED emotion ("she slammed
the door" implies anger) -- that needs a separate world-knowledge/meaning component (the same
explicit-vs-inferred split the goal dimension found). The pass is anchored on the explicit, reliable
tier.

BRAIN FIDELITY: emotion is a genuinely separate brain system (Campanella et al. 2022 found affect,
intention, and causation dissociate in the same patients on the same stories) -- so it is a new
register, not folded into belief/goal. We store valence as primary and category as secondary (how the
brain represents emotion), bind the feeler by the verb's stored linking, and OVERWRITE the current
emotion as it changes (unlike goals, which persist) -- each choice is PINNED to the literature. The
single biggest quality lever was TIGHTENING extraction to only finite emotion verbs (removing ~2600
false fires), which lifted the vs-oracle precision from 0.26 to 0.587.

files: experiments/{affect_register.py, affect_lexicon.py, psych_verb_frames.py,
exp_affect_register_qa_v1.py}, verification/test_affect_register.py (12/12 PASS),
data/psych_verb_frames_v1/psych_verb_transitivity_ud_ewt.json, data/exp_affect_register_qa_v1/metrics.json.
NO hdlab written (Q111 -- strategy lands the wire + the board `affect` arm; proposed diff in SOLVED.md).

Reverify (re-runs NO landed cell): .venv/Scripts/python.exe verification/test_affect_register.py  # 12/12
