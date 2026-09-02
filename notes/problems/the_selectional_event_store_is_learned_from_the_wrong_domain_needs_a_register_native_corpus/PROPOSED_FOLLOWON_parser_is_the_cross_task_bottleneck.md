# PROPOSED FOLLOW-ON (draft brief for the strategy session to file) -- THE #1 CROSS-TASK LEVER

**Proposed slug:** `the_extraction_front_end_parser_is_the_cross_task_bottleneck_needs_a_significantly_better_parse`
**Proposed priority:** 1 (the highest-compounding lever in the reader -- it gates who-did-what roles, world-state
roles, AND meaning lemma/POS; three independent solver lines converge on it).
**Author:** solver of `the_selectional_event_store...register_native_corpus` (owner: "we need to improve the
parser significantly so it performs well for all tasks"). Strategy: lift into `notes/problems/<slug>/PROBLEM.md`.

## 1. THE PROBLEM IN PLAIN LANGUAGE
The reader works out who-did-what, who-has-what, and what-a-word-means all on top of the SAME first step: read
the sentence's grammar (which noun is the subject, which is the object, what the verb is). That first step --
the parser -- is the weakest part of the whole system, and because everything sits on top of it, its errors
cap every downstream ability at once. Making the parser significantly more accurate (and robust to unfamiliar
text) is the single change that raises the most capabilities.

## 2. WHY THIS ONE -- it is the DEFINITIVELY-MEASURED cross-task ceiling
- **Who-did-what is PARSER-BOUND, quantified exactly.** When the parse is correct, patient selection is 0.989;
  the ENTIRE deficit to ~0.66 is parser failure (47% of gold patients are attach-misses; a further 25% on the
  eager incremental parser are confident-WRONG attachments). Knowledge + integration are SATURATED: a
  register-native selectional store + the brain-foundational precision-weighted integration
  (`convergent_cue_reader`) reach 0.658 (68% of the chance->human range), and NO integration trick
  (store-gate / agreement-gate / conflict-driven precision) moves it -- only a better parse does.
- **The substrate's OWN parser LOSES to an off-the-shelf small model.** On the QA-SRL science who-did-what
  test, structural role assignment driven by the frontend `arc_parser` = 0.515 and by `incremental_parser` =
  0.514, but by spaCy `en_core_web_sm` = 0.588 (+0.073 CI-sep). We are below `en_core_web_sm`.
- **It is cross-task by independent evidence, not assertion:** `situation_model_has_no_mutable_world_state_
  register` named "parser/extraction front-end = highest-COMPOUNDING lever -- gates roles (register) + lemma/POS
  (meaning channel)"; the p5 audit concluded "the sole lever is a better parser." This solver adds the who-did-
  what quantification. THREE lines, one target.
- **It COLLAPSES out of register.** On 19c LitBank both `arc_parser` and spaCy fall to ~0.26 (FULL) / ~0.005
  (non-canonical HARD) -- archaic syntax breaks them. A reader that only parses modern edited prose is brittle.

## 3. HOW THE BRAIN DOES THIS (the opening move)
PINNED: comprehension builds structure INCREMENTALLY, left-to-right, under a bounded buffer (Now-or-Never,
Christiansen & Chater 2016), and structure-building and role-binding are SEPARATE but interacting pools
(Matchin-Hickok 2020; Friederici 2011). Crucially the parse is not hard-committed: it is co-inferred with
plausibility (constraint-based, McRae 1998; noisy-channel, Levy 2008 / Gibson 2013), and the parser maintains a
DISTRIBUTION over attachments (graded, not 1-best) collapsed only when a task presses (`graded_competition`).
Register-robustness comes from having READ the register (experience-based statistics), not a fixed grammar.

## MEASURED vs INFERRED
- **MEASURED (do NOT re-derive):** parse-correct -> 0.989 who-did-what; 47% attach-miss + 25% confident-wrong
  buckets; frontend/incremental 0.515/0.514 < spaCy 0.588 (+0.073); 19c collapse ~0.26/0.005; integration
  saturates at 0.658 (all in `exp_error_decomposition_v1.py`, `exp_parser_headroom_v1.py`,
  `exp_full_brain_foundational_reader_v1.py`, `exp_brain_foundational_integrator_v1.py`).
- **INFERRED (measure):** whether closing the arc_parser->spaCy UAS/LAS gap (via the substrate's parser-training
  infra) recovers the +0.073 downstream; whether a distribution-emitting / confidence-exposing parser lets the
  graded organs recover the confident-wrong bucket; whether register-native parse training (gold target-register
  data, NOT self-training -- self-training was REFUTED for 19c) fixes the out-of-register collapse.

## ALREADY TRIED / DO NOT REDO
- Do NOT re-run: parser register-adaptation via SELF-TRAINING (REFUTED, stalls -- p5); richer selectional
  features / a cleverer combiner / more integration tricks (SATURATED at 0.658 -- this solver); the incremental
  parser as a patient selector (it is position-like, 0.514, WORSE than spaCy's grammatical-relation labels).
- BUILD ON (reuse): `hdlab/arc_parser.py` + `arc_parser_richfeat` / `arc_parser_mst_retrain` assets and the
  `experiments/exp_depparse_transition_*` / `exp_depparse_global_beam_*` TRAINING cells (the parser-improvement
  infra already exists); `hdlab/incremental_parser.py` (incremental structure + confidence); `graded_competition`
  (maintained distribution); spaCy `en_core_web_sm` as a glass-box REFERENCE/target (NOT an LLM; already used in
  the substrate) -- the goal is to match/exceed its UAS/LAS in the substrate's own glass-box parser.

## THE BAR (can-fail; CI-separated)
PASS = the substrate's OWN glass-box parser, improved, RAISES a DOWNSTREAM capability CI-separated over the
current `arc_parser`: specifically who-did-what structural role assignment from 0.515 toward the spaCy level
(0.588+) on the held-out QA-SRL science test, AND holds a measured UAS/LAS gain on UD-EWT test, with the gain
COMPOUNDING (measure at least one second task -- world-state role recovery or meaning lemma/POS). A rigorous
located negative (the arc_parser cannot be brought to spaCy level with the available infra, with a named reason)
is a full PASS. Report the parse-attach PRECISION on arguments, not just overall UAS. Register-robustness (19c)
is a SEPARATE sub-goal -- gold target-register parse data, not self-training.

## DO NOT QUOTE
- Do NOT quote 0.658 as a who-did-what ceiling -- it is the INTEGRATION ceiling at the CURRENT parser; the
  parser is what caps it. Do NOT claim the incremental parser is worse in general -- it is better at argument
  RECALL (F1 +0.035) but position-like for PATIENT selection; the deficit is attachment PRECISION + labels.
