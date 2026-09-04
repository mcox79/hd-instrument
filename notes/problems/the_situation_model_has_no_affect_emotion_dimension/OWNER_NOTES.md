---
owner_verdict: DONE
---

SOLVED (pending your verdict) — the_situation_model_has_no_affect_emotion_dimension (opus 4.8 solver)

Write-up: notes/problems/the_situation_model_has_no_affect_emotion_dimension/
  {SOLVED.md, OWNER_NOTES.md, signal_loss_chain_analysis_2026-09-04.md,
   research_affect_emotion_brain_mechanism_*, research_experiencer_psych_verb_brain_mechanism_*,
   research_emotion_term_denotation_and_experiencer_coref_*, research_brain_vs_our_coref_binding_mechanism_diff_*}
Reverify (re-runs NO landed cell): .venv/Scripts/python.exe verification/test_affect_register.py   # 12/12

WHAT: the reader now has the EMOTION dimension of the situation model — a glass-box per-character AFFECT
register over the reader's OWN extraction (frontend POS + coref; NO spaCy at inference, NO LLM). It reads
explicit emotion constructions ("was afraid", "felt joy", "angrily", "to her delight", "the dog frightened
her"), binds each to the resolved EXPERIENCER, and carries VALENCE (primary) + emotion CATEGORY (secondary).
Built exactly like the owner-DONE goal register.

RESULT (100 LitBank docs; floors recomputed per population; twin loses; CI-separated):
- "How does X feel?" reliable slice (category, n=673): model 0.788 vs most-recent-emotion-word floor 0.312
  vs shuffled-character twin 0.394 (both CI-separated; twin null p95 0.435).
- VALENCE sign (primary PINNED channel, n=743): model 0.838 vs floor 0.490 (CI-sep).
- Binds the RIGHT character (multi-character positive control): 391 vs 37.

BRAIN-FOUNDATIONAL: emotion is a genuinely SEPARATE system (Campanella 2022 triple dissociation on the same
patients/stories) — a new register, not folded into belief/goal. Valence-primary + category-secondary
(Barrett/Lindquist; Gygax online reading). Experiencer bound by the PINNED psych-verb linking frame
(VerbNet admire-31.2 exp=subject vs amuse-31.1 exp=object; authored A/B frame 1.0 vs naive 0.333). Affect
OVERWRITES (de Vega) where goals PERSIST (Lutz-Radvansky). Emotion words gated by DENOTATION not ASSOCIATION
(Pavlenko 2008; WordNet-Affect) — this cycle-1 fix lifted the reliable slice 0.625->0.788, valence
0.766->0.838, positive control 5.9x->10.6x.

UPSTREAM components (built + research-verified): experiments/psych_verb_frames.py (experiencer-linking,
UD-EWT transitivity prior) + experiments/affect_lexicon.py (Warriner valence + curated emotion-denoting
inventory). Zero regression: the psych frame gates ONLY psych-verb experiencer position; non-psych affects
byte-identical (witness W10).

FULL-CHAIN SIGNAL-LOSS STUDY (oracle-substitution ladder, exp_affect_chain_signal_loss_v1.py): measured
WHERE the chain loses signal. G0 glass-box F1 0.581 -> +spaCy POS 0.624 -> +GOLD coref 0.945 -> ceiling 1.0.
COREFERENCE = 87% of the end-to-end loss. TRACED precisely: 83.5% of emotion experiencers are COMMON-NOUN
entities ("the man", "the child") the reader never forms a referent for; genuine named-pronoun error is
only ~9.6%. Detection recall 0.96, POS ~4%. The affect extraction/valence/experiencer-linking are
NEAR-CEILING given good coref (F1 0.945) — the bottleneck is entirely upstream coref.

PRECISE brain-vs-implementation mechanism-diff (8 items, cited): the dominant difference is that our coref
is proper-name-centric and forms NO referent for common-noun-only entities, where the brain builds a
referent for every entity (Gernsbacher Structure Building; Poesio-Vieira direct anaphora; cue-based
retrieval Lewis-Vasishth 2005). We PROTOTYPED the fix SIX ways (salience fallback, Centering resolver,
faithful discourse-referent former with definiteness+modifiers+recency): all recover <=+0.02 (identity) /
~0 (chain-F1); only gold coref recovers +0.43. The direction is validated; the faithful fix (+ bridging +
cue-based retrieval + own-NP detection) is a substantial COREF-ORGAN build, precisely spec'd and handed off.

LOCATED NEGATIVE (a full pass per the brief): UNSTATED emotion ("she slammed the door" -> anger) needs the
OCC-appraisal meaning channel — the explicit-vs-inferred split the goal dimension found. Anchored on the
explicit tier.

>>> THE NEXT FOCUS <<< : COREFERENCE — specifically COMMON-NOUN DISCOURSE-REFERENT FORMATION (build an
identity for every character, not just named ones). Highest-value lever (+0.43 F1 ceiling); lifts affect
AND every character-bound dimension. Prototype experiments/discourse_referents.py + fix spec in the
signal-loss note; owned by the coref / name-clustering problem, NOT this affect problem.

files: experiments/{affect_register, affect_lexicon, psych_verb_frames, exp_affect_register_qa_v1,
exp_affect_chain_signal_loss_v1, discourse_referents}.py + verification/test_affect_register.py (12/12) +
data/{psych_verb_frames_v1, exp_affect_register_qa_v1, exp_affect_chain_signal_loss_v1}. NO hdlab written
(Q111 — proposed wire + board `affect` arm in SOLVED.md §5). AUDIT UPDATE for BRAIN_FOUNDATIONAL_AUDIT §2b
(new AFFECT/EMOTION dimension; the reader now has all five Zwaan-Radvansky dimensions + goal + affect).
Ledger malformed/incomplete: 0.
