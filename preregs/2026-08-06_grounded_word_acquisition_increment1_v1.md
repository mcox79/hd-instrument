# Pre-reg: online grounded-word-acquisition loop, increment 1 (outcome-verb POLARITY axis)

Date: 2026-08-06. Status: **PRE-REGISTERED, NOT YET EXECUTED** (per task brief -- this cycle delivers
the spec + this pre-reg only; a cell-author executes it in a later cycle). Companion build-spec:
`notes/drill_online_grounded_word_acquisition_loop_2026-08-06.md` (read first -- has the full
brain-mechanism -> owned-organ map and the honest-scope boundary this pre-reg operationalizes).

Task: close audit gap #1 ("FEATURES: supplied vs LEARNED+GROUNDED",
`notes/audit_SYNTHESIS_semantic_meaning_barrier_2026-08-06.md`) for the ONE decision-relevant axis
gating `OUTCOME_NEVER_TYPED`: outcome-verb RESULT_VALENCE (POS/NEG). Today's Tier-2 coverage
(`hdlab/verb_lexical_similarity.py`, `preregs/2026-08-06_verb_class_openvocab_similarity_v1.md`) is
classification-by-similarity-to-HAND-TAGGED seeds -- every seed a human fast-mapped by hand. This
increment builds a TIER-3: the substrate proposes, cross-checks, grounds, and writes back its own
candidate entries for genuinely novel words, with zero human seed-authoring for the target words.

## What is being built

1. **Channel A (structural, `hdlab/frame_induction.py`-pattern reuse)**: a NEW construction-cue atom
   set `POLARITY_CONSTRUCTION_ATOMS = [has_direct_object, patient_np_present, result_particle_present,
   subject_is_animate_agent]` (the last via `hdlab/animacy_lexicon.py`, already wired) -> MDL-induce
   (reuse `hdlab.learner.registry.learn`/`apply`, config-only, zero new learner code, exact pattern of
   `frame_induction.py::induce`/`predict_subj_role`) a construction -> {POS-like, NEG-like} classifier,
   TRAINED on the EXISTING `OUTCOME_SEED_POS`/`OUTCOME_SEED_NEG` verbs' own corpus sentential contexts
   (not the target word's identity -- the word itself is never a feature, matching
   `frame_induction.py` L22-24's discipline verbatim).
2. **Channel B (affective, `grounded_appraisal_sim_earned` reuse + ONE new adapter)**: a NEW,
   explicitly-thin adapter function `goal_congruence_appraisal_type(goal_sentences, outcome_sentence,
   target_word) -> {"RECIPROCITY", "BLOCK_HIGH", None}` built from ALREADY-OWNED primitives
   (`hdlab/goal_typing.py`'s `find_desired_state`, `SUBJECT_IS_REFERENT_CLASSES`/
   `OBJECT_IS_REFERENT_CLASSES`, `_referent_links`) -- decides whether the outcome clause's referent
   trajectory reads as goal-COMPLETING (-> "RECIPROCITY") or goal-THWARTING (-> "BLOCK_HIGH") using
   ONLY the antecedent goal's referent + the clause's argument structure (subject-is-referent vs
   object-is-referent, from the SAME achievement/change-of-state distinction `SUBJECT_IS_REFERENT_
   CLASSES`/`OBJECT_IS_REFERENT_CLASSES` already encode) -- never the target verb's own identity or
   any text co-occurrence statistic. Feeds `hdlab/context_grounded_valence.py::score_item`'s
   `situation_type` parameter path (already accepts exactly this 2-value domain, see that module's
   `combine_biased_competition` call, L161) -> reads `valence = Q(harm@coherent) - Q(help@coherent)`
   from the FROZEN theta (`experiments/exp_grounded_appraisal_sim_earned_v1.py`, zero new training,
   zero text). `sign(valence)` is Channel B's candidate POS/NEG vote.
3. **Propose/gate/confirm/consolidate skeleton (reuse verbatim)**: `hdlab/predictive_coding.py::
   threshold_gate` as the per-occurrence PROPOSE trigger (fires when Channel A+B jointly produce a
   candidate for a word not in Tier-1/Tier-2); signature-matching consolidation identical to
   `exp_self_extension_loop_v1.py::run_loop`'s `MIN_CONFIRM=2` rule (L353-372) -- a candidate word
   promotes only once the SAME polarity vote recurs across >=2 independent sentences AND clears
   `hdlab/self_improving_loop.py::decide_keep_or_revert`'s abstain band (`ABSTAIN_BAND_DEFAULT=0.02`).
4. **Write-back (NEW, small)**: `ACQUIRED_OUTCOME_VERB_FEATURES: Dict[str, FrozenSet[str]]`, a
   module-level runtime-mutable dict in `hdlab/verb_lexical_similarity.py`, populated only by the
   consolidation step above. `in_lexicon`/`mean_similarity_to_seeds`/`classify_2way` extended to check
   it as Tier-3, strictly AFTER Tier-1 (exact) and Tier-2 (fixed-seed similarity) -- abstain-preserving,
   strict ADD, cannot regress any call site that already resolves today (same discipline as every
   existing Tier in this file).

## Held-out set (non-circular; real corpus text; gold assigned BEFORE any mechanism was run)

**Selection procedure (documented, followed exactly, not adjusted post-hoc):** candidate words drawn
from a frequency scan of `data/corpora/mcguffey_graded/*.txt` + `data/corpora/graded_readers_grade1/
cleaned/*.txt` for result-state verbs ABSENT from the union of {`CLASS_REGISTRY` members,
`OUTCOME_VERB_FEATURES` keys (incl. `OUTCOME_HELDOUT_POS`/`_NEG`), `V2_OUTCOME_MET`/`_UNMET`} as of
this pre-reg's date (verified by direct `in_lexicon(lemma, "outcome")` query against the live module,
disk-confirmed False for every word below). Gold polarity assigned via a WRITTEN RUBRIC, decided before
inspecting any classifier output: **POS = the verb denotes the referent successfully attaining,
securing, or perceptually/epistemically achieving something (achievement semantics, valence attaches
to the ACHIEVING, matching how `ARRIVE_SUCCEED` already works in `CLASS_REGISTRY` -- not to whatever is
achieved); NEG = the verb denotes abandonment, dissipation, or decline of something (loss/decay
semantics).**

| word | gold | corpus freq (mcguffey+grade1) | 2 ACQUISITION sentences (verbatim, cited) | 1 HELD-OUT generalization sentence (verbatim, cited) |
|---|---|---|---|---|
| catch/caught | POS | 83/47 | "Four soft paws had little kitty, ... And they caught the little mousie, Long time ago." (g2_second.txt) / "Papa and Mamma caught at him to save him, and before we knew it we were all in the water." (g2_second.txt) | **"The rat stole out, and she jumped at it and caught it."** (g1_first.txt) -- this is the LIVE, currently-unresolved blocker for `mg1_nero_puss_rat` in `experiments/data/real_text_goal_owner_diagnostic_v1.jsonl` (row 4); this is the decisive real-bank item, not a synthetic stand-in. |
| obtain/obtained | POS | 23 | "Harry, at length, obtained permission for the little dog to remain as a sort of outdoor pensioner..." (g4_fourth.txt) / "Reverse the process, and repeat as before until the lowest pitch is obtained." (g5_fifth.txt) | "Having on several days obtained sight of some of them, he, with his attendants, ... gave chase; but they baffled all pursuit." (g4_fourth.txt) -- NOTE the coordinated later clause ("baffled all pursuit") describes a DIFFERENT action; gold scores the `obtained` clause's own local polarity (POS, per rubric), not the sentence's overall outcome. |
| gain/gained | POS | 35 | "A distinct articulation can only be gained by constant and careful practice of the elementary sounds." (g3_third.txt) / "His writings in poetry and prose are well known, and he also gained distinction in his profession as a sculptor." (g4_fourth.txt) | "...suggestions and criticisms gained from their daily work in the schoolroom." (g1_first.txt, front matter) |
| earn/earned | POS | 12 | "He earned almost enough to support his mother and his little sister." (g2_second.txt) / "In a few years, while still a small boy, he earned money enough to support his father." (g3_third.txt) | "\"You have earned the orange, my boy;\" and she gave it to him with a smile." (g3_third.txt) |
| desert/deserted | NEG | 11 | "But sleep seemed to have deserted the pillow of poor Tom." (g4_fourth.txt) / "Frank started up in great consternation ... and, from that time, almost entirely deserted the library." (g6_sixth.txt) | "They both consequently deserted the little family circle every evening after tea..." (g6_sixth.txt) |
| waste/wasted | NEG | 8 | "His wasted form, his aching head, And all that now remains of him, Lies, shuddering, on a felon's bed." (g5_fifth.txt) / "But his bodily energies wasted and declined under incessant toil." (g6_sixth.txt) | "With fire and sword, the country round Was wasted, far and wide..." (g5_fifth.txt) |
| fade/faded | NEG | 15 | "I can see her--the beggar girl, I mean--as she stood there in front of the store, in her old hood and faded dress..." (g3_third.txt) / "...looking up at a faded picture of an old gentleman..." (g5_fifth.txt) | "And then I think of one, who in Her youthful beauty died, The fair, meek blossom that grew up And faded by my side." (g5_fifth.txt) |

N=7 words (4 POS, 3 NEG), 21 real corpus sentences total, all verified present via direct grep against
the source files listed (re-run to reproduce: `grep -o -i ".\{0,80\}\bWORD\b.\{0,80\}"
data/corpora/mcguffey_graded/*.txt data/corpora/graded_readers_grade1/cleaned/*.txt`).

**Fall-through baseline (MEASURED, disk-verified, NOT hypothesized):** all 7 words confirmed
`in_lexicon(lemma, "outcome") == False` against the live `hdlab/verb_lexical_similarity.py` (checked
directly, this session) -> `classify_2way`/`mean_similarity_to_seeds` structurally return `None` for
every one (short-circuit on `in_lexicon` check, `verb_lexical_similarity.py` L382-383) ->
`congruence_with_lexicon_fallback`/`lexicon_predict` abstain (`NONE`/`NA`) on all 7 today, verified
directly for catch/obtain/gain/earn via `lexicon_predict(sentence)` returning `"NONE"` on each. **Fall-
through accuracy = 0/7 = 0.0.**

**Noise-probe set (anti-drift control, hand-authored, same convention as `exp_self_extension_loop_v1.
py`'s `NOISE_TMPLS` -- deliberately hand-built, not corpus-mined, so neutrality is guaranteed rather
than hoped for):** 8 valence-neutral verbs in the SAME transitive/achievement clause shape as the real
items, each given 2 sentences (mirroring the acquisition-exposure count so the noise arm is a fair
apples-to-apples test of the SAME consolidation path, not a shorter/easier one): `walked, sat, spoke,
turned, answered, asked, stood, carried`. Example: "He walked to the well and carried the pail home." /
"She turned and spoke to her brother." (full 16-sentence bank authored by the implementing cell-author
per this same shape, no per-sentence tuning to force a null result).

**Scramble control:** fixed-seed permutation of (word -> {Channel-A signature, Channel-B valence sign})
assignment across the 7 acquisition-sentence-pairs (5 permutation seeds, same convention as
`hdlab/verb_lexical_similarity.py::self_test`'s own circularity check) -- reported as
`scrambled_heldout_accuracy` (mean across seeds).

## Falsifiable predictions (HARD-PASS / HARD-FAIL / MIDDLE-BAND)

**Primary metric:** `heldout_accuracy` = fraction of the 7 held-out (generalization) sentences where
the LIVE Tier-3-acquired entry (written back after the 2 acquisition sentences run through
propose/gate/confirm/consolidate) now correctly types MET/UNMET matching gold, via the SAME production
call (`congruence_with_lexicon_fallback` or `lexicon_predict`, whichever the target clause structurally
reaches) with the acquired overlay live.

**HARD-PASS** (ALL of the following must hold):
1. `heldout_accuracy >= 5/7` (~0.714), AND at least 2/4 POS held-out items AND at least 2/3 NEG
   held-out items individually correct (rules out a degenerate always-guess-POS/NEG strategy riding
   the 4:3 class imbalance to a passing score).
2. `noise_consolidated_count == 0/8` (anti-drift: zero noise-probe words get written back to
   `ACQUIRED_OUTCOME_VERB_FEATURES`).
3. `scrambled_heldout_accuracy` within +/-0.15 of chance (0.50), i.e. in `[0.35, 0.65]`, while REAL
   `heldout_accuracy` clears gate 1 -- non-vacuous collapse (same convention as
   `hdlab/lexical_similarity.py`/`verb_lexical_similarity.py`'s own scramble self-tests).
4. `mg1_nero_puss_rat`'s specific held-out item ("...jumped at it and caught it.") types correctly
   AND, re-run through `experiments/exp_real_text_goal_owner_generalization_diagnostic_v1.py`'s
   existing harness (not modified by this increment), that item's `outcome_typeable` flips
   True/correct if it was the sole remaining blocker for that row (informational end-to-end check,
   not itself a new mechanism).

**HARD-FAIL** (ANY of the following):
- `heldout_accuracy <= fallthrough baseline` (i.e. `<= 0/7`) -- no real movement over abstain.
- `noise_consolidated_count >= 1/8` -- anti-drift gate leaks (a neutral verb gets written back with a
  polarity tag).
- `scrambled_heldout_accuracy` is NOT within the chance band (stays close to real accuracy, delta
  `< 0.10`) -- the mechanism is not earning genuine construction/valence correspondence.

**MIDDLE-BAND** (neither clean pass nor clean fail): `heldout_accuracy` in `(0/7, 5/7)`, OR gate 1
clears but gate 2 or 3 is borderline (e.g. `noise_consolidated_count == 1/8` with an identifiable,
non-systematic cause, or scramble collapse is partial). Report honestly; do not force a label either
direction (matches `outcome_valence_goal_congruence_v2`'s own MIDDLE_BAND precedent, cited in
`hdlab/goal_typing.py`'s module docstring).

## Ablation prediction (informational, pre-registered, tests the audit's own hypothesis)

Report `channel_A_only_heldout_accuracy` and `channel_B_only_heldout_accuracy` alongside the combined
result (each computed by re-running consolidation with the OTHER channel's vote forced to abstain).
**Falsifiable sub-prediction, stated before running (per Kousta/Vigliocco 2011's affective-embodiment
account for evaluative/abstract words, and per the syntactic-bootstrapping literature's own scope --
argument structure predicts event TYPE/arity, not documented to predict emotional/evaluative VALENCE):
Channel B (affective, reward-grounded) alone should reproduce most or all of the combined
`heldout_accuracy`; Channel A (structural) alone should land close to chance (~0.5).** If instead
Channel A alone matches or beats Channel B alone, that is a genuine, useful FALSIFICATION of this
project's extrapolated claim that reward-earned appraisal is the operative grounding channel for
outcome-verb valence specifically (see calibration note in the companion build-spec) -- report either
outcome as a finding, not a failure of the cell.

## Compute architecture

Sequential-CPU. This is lexicon lookup + FHRR bundle/cosine (Channel A/B) + a fixed-size MDL induction
over 4 boolean atoms (Channel A, identical cost class to `frame_induction.py`'s own induction) + a
frozen-theta lookup (Channel B, zero training). N=7 acquisition words x 2 exposures + 7 held-out +
16 noise sentences + 5 scramble seeds -- low tens of forward passes total, wall time expected in
seconds, matching `preregs/2026-08-06_verb_class_openvocab_similarity_v1.md`'s compute class exactly.
`crlb_n/a`: bounded held-out classification accuracy against a fixed 7-item gold set, not a
capacity/argmax-noise-floor cell. `storage_strategy`: `ACQUIRED_OUTCOME_VERB_FEATURES` is
process-local/in-memory for this increment (no cross-session persistence -- explicitly out of scope,
see build-spec "Honest scope").

## Cardinality / discriminator / atomicity gates (SCHEMA-VET checklist, for the implementing cell)

- `cardinality_ok`: `EXPECTED_N_UNITS` = 7 (per-word acquire+test) + 1 (noise anti-drift batch) + 1
  (scramble, 5 seeds averaged) + 1 (end-to-end `mg1_nero_puss_rat` re-check) = 10 units minimum;
  resumable per-unit via `tools/exp_checkpoint.py` (project MANDATORY convention).
- `discriminator_reachability`: TRUE -- 7-item binary classification against fixed gold is not
  saturated-by-construction (chance = 0.5, ceiling = 1.0, both reachable).
- `baseline_in_band`: N/A for the primary held-out-accuracy arm (a direct measurement against fixed
  gold, not a baseline-vs-mechanism ratio); the fall-through baseline (0/7) is reported as a REAL
  measured floor, not assumed.
- `arms_differ_verified`: real vs scrambled `ACQUIRED_OUTCOME_VERB_FEATURES` entries must hash-differ
  (META_RULE_AF-style check, same pattern as every existing self-test in this file family).
- `final_metrics_atomicity`: `tmp_replace`.
- `deterministic_seeding`: fixed integer seeds throughout (no `hash()`-derived seeding, PROT-023/F.5
  compliant); scramble perm seeds and any MDL-induction tie-breaks fixed and documented.
- `progress_logging`: N/A expected (cell should complete in well under 60s; add print_flush heartbeats
  if actual wall time exceeds that during implementation).

## Cert gate (MANDATORY if this touches production `hdlab/goal_typing.py` / `hdlab/verb_lexical_
similarity.py`)

`python verification/run_certification.py` via `.venv/Scripts/python.exe` BEFORE and AFTER the edit;
baseline to reproduce at implementation time: 220 passed, 3 skipped (per
`preregs/2026-08-06_verb_class_openvocab_similarity_v1.md`'s own measured baseline the same day) --
must stay 220/3 unchanged (strict ADD; Tier-3 only fires on words OOV of Tier-1 AND Tier-2, so no
existing test item's verb vocabulary can collide unless it is independently OOV of both today, in
which case trace it by hand against `verification/test_outcome_valence_goal_congruence.py`'s decisive
items before dispatch, same discipline as the Tier-2 pre-reg applied).

## Files to be touched (by the implementing cell-author; NOT touched this cycle)

- `hdlab/verb_lexical_similarity.py` (EDIT) -- add `ACQUIRED_OUTCOME_VERB_FEATURES` runtime dict +
  Tier-3 fallback wiring in `in_lexicon`/`mean_similarity_to_seeds`/`classify_2way` (or equivalent
  strict-ADD extension points).
- `hdlab/goal_typing.py` (EDIT, small) -- expose `goal_congruence_appraisal_type` adapter (Channel B),
  strict-ADD, only consulted by the new acquisition path, no change to any existing call site's
  behavior.
- `hdlab/word_acquisition_loop.py` (NEW, suggested name) -- the propose/gate/confirm/consolidate
  orchestration (Channel A construction-cue MDL induction + Channel B adapter call + `MIN_CONFIRM`
  consolidation + write-back), composed from the reused primitives named above; this is the one
  module that is genuinely new besides the two small adapters.
- `experiments/exp_grounded_word_acquisition_increment1_v1.py` (NEW) -- the pre-reg'd cell reproducing
  every metric above from a clean process, self-test + resumable + atomic-write per the mandates.

`experiments/exp_real_text_goal_owner_generalization_diagnostic_v1.py` and its existing gold bank are
LEFT UNTOUCHED (source-of-truth convention); the new cell calls the same harness functions for the
end-to-end informational check (HARD-PASS gate 4) without mutating the historical snapshot.

## Prior-work check (per exp_dev standing discipline)

`hdlab/lexical_similarity.py` / `hdlab/verb_lexical_similarity.py` (Tier-1/Tier-2, same-day prior art,
disk-verified, cited throughout) are the only existing coverage; no acquired-lexicon / runtime
write-back / persistent-mint pattern exists elsewhere in `hdlab/` (checked: no hit for `ACQUIRED`,
`acquired_lexicon`, `runtime_overlay`, or `write.?back`-adjacent naming outside
`hdlab/hippocampal_encoder.py`, which is an unrelated CLS pattern-separation primitive, not a lexicon).
`data/capability_registry.jsonl`'s `binder_direct_supply_grounding` row (SHELVED, "Binder-65 not even
on disk") is prior art for what NOT to repeat -- this increment supplies mechanism definitions (the 4
Channel-A atoms, the reward function used to train Channel B's theta, already spent) and per-word DATA
only for the 7 gold-labeled held-out items used to SCORE the mechanism, not to seed it.
