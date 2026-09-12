# SIGNAL-FLOW MAP — what every downstream component needs from the organs the current wave changes

Owner directive (board Q131, 2026-09-12): *"systematically, from the top down of the live substrate ... fully understand the
signals that all downstream, brain foundational (mathematically) components need, and that these upstream changes are
accommodating them."* This map is built BEFORE the landing and is the checklist the landing runs against (OVERNIGHT_PLAN
2026-09-12 STEP 1). Enumeration method: `grep` of every `.tag(` / `.label(` / `harm_help` / `force_dynamics_event_type` call
site under `hdlab/` plus the board (`exp_situation_model_qa_modern_v1.py`); every consumer named here has a witness or a
board arm named beside it. Extend this file for every future upstream change (one section per changed organ).

## 0. Top of the live substrate: what the reader emits
`SituationReader.read()` → `sm` with the board-scored dimensions (coref, salience, common-noun coref, who-did-what agent /
patient, state, word sense) + the new-arm dimensions (affect harm/help, affected entity, causal sign, temporal, spatial,
negation, goals, beliefs, …). Every upstream organ below feeds one or more of these through the chains listed.

## 1. `hdlab/pos_tagger.py` — change 3a: Bayesian DP-head category correction (ADJ→NOUN) as a post-pass on `tag()`
**Signal emitted:** `tag(tokens) -> list[str]`, one UPOS string per token (17-tag UD set, Viterbi-decoded). The change
retags a token ADJ→NOUN ONLY when it heads a determiner phrase (a DET precedes with only ADJ/ADV between and no nominal
follows) AND it has a noun reading AND the Bayesian posterior odds favour NOUN. Tag SET unchanged; sequence length unchanged;
no other position touched.
**Invariants consumers rely on:** same tag vocabulary; one tag per token; determinism per token sequence (the reader caches
tags per sentence — `situation_reader._frontend_tagger` / `_CachedTagShim`).
**Consumers (25) and what they need:**
| consumer | uses tags for | accommodation | check |
|---|---|---|---|
| `situation_reader` (per-read tag cache, L2080/2549/854) | every downstream structural read | post-pass inside `tag()` → the cache sees corrected tags once | board `--self-test` (7 dims) |
| `arceager_parser` / `arc_parser` / `arc_labeler` (tags as parse/label features) | head + label decisions | a DP-head noun now parses as the object it is (the cascade fix: "medic"/"intern") — EXPECTED movement, measured | `who_did_what_*` rows; `test_pos_nominal_head_correction` W4a/W4b |
| `predicate_argument_frontend`, `predicate_detector` (verb detection via VERB tags) | role frames | unaffected (ADJ→NOUN only) | `test_predarg*` witnesses; `who_did_what_patient` row |
| `referent_per_np` (NP heads = NOUN/PROPN) | discourse referents | MORE referents where a DP-head was mis-tagged ADJ (desired) | `coref`, `common_noun_coref` rows |
| `copular_binding` (state: is-a / property) | holder/property typing | a DP-head NOUN is a holder, not a property → fewer false properties | `state` row |
| `belief_reader`, `space_reader`, `temporal_model`, `causation_typing`, `joint_relation_frontend`, `perceptual_access_ledger`, `predictive_world_model`, `consequence_learning_loop`, `completeness_checker`, `candidate_generator`, `crosstype_live_adapter`, `definitional_*`, `goal_achievement`, `mcscript_extraction`, `outcome_event_extraction`, `parse_goal_extraction`, `reading_grounding_loop` (content-word filter), `crf_tagger`, `perceptron` | NOUN/VERB/ADJ class tests | receive a strictly more correct NOUN set; none depends on the ADJ mis-tag | their module self-tests + the board arms they feed (temporal_*, spatial_*, theory_of_mind, event_goal, causal_*) |
**Landing requirement (BF):** the Bayesian terms (lexical prior P(cat|word), syntactic likelihood ratio) must be a PERSISTED
offline asset under `data/frontend_assets/` built once from UD-EWT train — NOT a treebank read at inference (the experiment's
`_fit()` reads the treebank at call time; that is an ingest-time-only operation). The `_has_noun_reading` guard queries
WordNet (the same admissible-foundation-at-inference residual as pri-12; record, do not expand).

## 2. `hdlab/arc_labeler.py` — change 3b: voice post-correction (`nsubj` under be/get-aux + past participle → `nsubj:pass`)
**Signal emitted:** `label(tokens, pos, heads) -> {dep_idx: deprel}`; `norm_label` collapses subtypes but KEEPS `:pass`.
The change relabels only an `nsubj` whose head verb carries a be/get auxiliary and is a past participle.
**Consumers (7) and what they need:**
| consumer | reads | handles `nsubj:pass`? | check |
|---|---|---|---|
| `predicate_argument_frontend` (patient = obj active / nsubj:pass passive, L259-264) | exactly this distinction | YES — the correction FEEDS it the label it already wants | `who_did_what_patient`, `affected_entity` rows; `test_fd_harm_help_learned_extraction` 3/3 |
| `copular_binding` (holder = nsubj / nsubj:pass / csubj, L118) | subject set | YES | `state` row |
| `causation_typing` (maps nsubj:pass → nsubjpass, L721) | ClearNLP-style labels | YES | `causal_*` arms |
| `perceptual_access_ledger` (main-clause subject incl. nsubj:pass, L328/457) | subject set | YES | `theory_of_mind` arm |
| `crosstype_live_adapter` | experiencer/stimulus roles | reads labels through the frontend; passive subject = stimulus-side handled by the frontend remap | `crosstype_experiencer` arm |
| `reading_grounding_loop` (structural encoder, default OFF) | role-bound context | unaffected on the live path (encoder off) | loop self-tests |
| `situation_reader` (frontend labeler) | all of the above via the cache | — | `--self-test` |
**Accommodation verdict:** every live consumer already distinguishes `nsubj:pass`; the correction removes a class of mislabels
they were silently absorbing. Expected movement: patient/affected rows up; no consumer loses a signal it used.

## 3. `hdlab/force_dynamics_valence.py` — change 3c: frame-list → force-dynamic arithmetic
**Signal emitted:** `harm_help(verb, animacy) -> HARM | HELP | NA | None(abstain)`; `force_dynamics_event_type(item, …) ->
(BLOCK_HIGH | RECIPROCITY | NEUTRAL | None, category, gov_word)` (the structural gate, UNCHANGED).
**Live consumer chain:** `situation_reader` → `context_grounded_valence` (L225) → `force_dynamics_event_type` → `harm_help` →
the affect/valence read (`sm` affect fields) → board `affect_harm_help` arm (0.778 standing) and the OCC/appraisal reads.
**What the consumer needs:** the same 4-valued output; abstention (`None`) must stay a first-class value (the arm treats
abstain as no claim, never as NEUTRAL). The arithmetic's live bare-SVO path (`endstate_reached=None`) returns exactly that set.
**Accommodation:** signature-identical drop-in; `force_dynamics_event_type` and `_lex()` untouched. Expected movement:
`affect_harm_help` up (solver: 0.778 → 0.944 on the 36-item gold); social/emotional verbs stop abstaining. The `valence_only`
arm is a control, NOT landed. Removing the read-path FrameNet enumeration removes an external-tool-at-inference defect.

## 4. Who-affected reranker — change 4: typed selectional preference (gated arm)
**Signal:** `A(v, class(noun))` (Resnik association) consumed ONLY when its margin clears τ (swept ≈0.3); otherwise the
syntax pick stands (the located negative: dense types do not beat syntax on the ambiguous residual).
**Consumer:** the who-affected patient decision (`affected_entity_resolver` / the reranker it sits in); board `affected_entity`
arm (0.373 standing) must not regress; the clean-signal subset is where it may move.

## 5. `causation_typing._frontend` — change 5: CRF tagger interface, OFF
No live signal changes. The option exists for the parser joint decode; standalone it measured −0.010 on who-affected.

## 6. Order of landing (top-down) and the gate after each
3a tagger → (board self-test + the 25 consumers' arms) → 3b labeler → (self-test + 7) → 3c harm/help → (self-test +
`affect_harm_help`) → 3d ranker routing → FULL `--run` + per-dimension trend gate → 4 → 5. A regression that a
consumer's witness explains as "receiving the corrected signal" is ACCEPTED and the consumer fixed to receive it (owner
directive 09-07); an unexplained regression is reverted.

## 7. What the landing REVEALED (2026-09-12, recorded as the map predicted)
- **Board-proxy caveat confirmed on `affect_harm_help`:** the arm scored an experiment copy of the decision (stuck at 0.778)
  while the live reader scored 0.972 on the same 36-item gold. Re-pointed: model = `FDV.harm_help` (the live organ), twin =
  the same arithmetic with valence map + force lexicon scrambled (0.583). A cache keyed by verb only had let the twin read
  the live valences (twin 0.972) — fixed: the endstate-valence cache is used only for the live lexicon.
- **Valence coverage boundary:** verbs whose word-level norm is absent or near-neutral (batter, bludgeon, wrench, throttle —
  the food / engine senses dominate the rating) now ABSTAIN where the old verb list said HARM. A sense-level synonym backoff
  was tried and WITHDRAWN the same night (it turned them into HELP). The brain-faithful fix is a resulting-state valence read
  (the solver's filed deepest step). Recorded boundary, not hidden.
- **The positional governor gate was the fragile part:** with the decision answering on many more verbs, tokenizer/tagger
  divergences in WHICH verb the nearest-verb gate picked surfaced (84/591 on 19c text). STEP 3d: the reader now hands the
  affect decision the predicate it already bound the patient to (`gov_idx` = the event's verb index) — one structure, one
  binding; the positional gate is only the fallback. Passive patients ("the intern was bullied") now reach the decision.
- Three landing-era witnesses that asserted "nothing changed" under the OLD decision were re-based to the live organ's
  decision or to recorded, bounded divergence rates; each edit says why in place.
