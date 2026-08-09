# Pre-registration: exp_direction_b_M2_speechact_result_generalization_v1

**Filed by:** exp_dev, 2026-08-09. **Task source:** Director spawn prompt (Direction-B milestone
M2, the decisive test of whether the COMMON COMPOSITIONAL CORE of the DesireDB outcome residual
GENERALIZES via a learned speech-act/result-type classifier, vs M1's idiom-lexicon long-tail
memorization), citing `notes/direction_b_grounded_knowledge_build_plan_2026-08-09.md` M2 + the
landed M1 result (`data/exp_direction_b_M1_idiom_grounding_recovery_v1/metrics.json`, verdict
MIDDLE_BAND, PRIMARY recovery 2/8=0.25, ENLARGED-cohort breadth recovery 0/37=0.0).

## Prior-work check (SUBSTRATE-KB, mandatory before authoring)
`bash tools/substrate_query.sh "speech act result type classification learned construction cue
generalization refusal grant block achieve fail"` -> top hit cosine=0.3389
(`notes/prior_art_classical_symbolic_story_understanding_2026-08-06.md::chunk009`, Lehnert's QUALM
question-type taxonomy / plot-unit M/+/- motivation-actualization-termination-equivalence
vocabulary -- background LITERATURE context, not a prior cell/mechanism attempt in this arc); next
4 hits cosine 0.334/0.333/0.333/0.330 are unrelated noise (a WordNet antonym entry "nationalization",
a Gene Ontology mRNA-localization term, an unrelated regime-classification research note, and
`exp_learned_composition_glue_pun_selectional_generalization_v1`, a different MIDDLE_BAND cell about
pun selectional generalization, not result-type/speech-act classification). **Verdict: genuinely
novel cell for this arc, not a rediscovery** -- Lehnert's plot-unit vocabulary is a useful CITED
conceptual precedent for "a small closed taxonomy of goal-relevant outcome TYPES" but this is the
first cell that induces such a taxonomy as a LEARNED, held-out-surface-form-generalizing classifier
via `hdlab.learner.registry.learn`.

## What / why
M1 (`hdlab/idiom_grounding.py`) supplemented the WordNet-only evidence vote with a 29-entry
HAND-AUTHORED idiom/colloquialism phrase lexicon: PRIMARY-cohort recovery 2/8=0.25 (MIDDLE_BAND) but
ENLARGED-cohort (900-row subsample) breadth recovery **0/37=0.0** -- every one of the 29 patterns
literally never fired on the larger sample's gold-Unfulfilled items (`idiom_match_frequency: {}`,
`idiom_never_fired_patterns`: all 29). This is the exact signature of a NON-COMPOSITIONAL LONG-TAIL
memorization mechanism: it only works on the handful of exact phrases it was authored to match.

M2 tests a DIFFERENT, complementary hypothesis: can a LEARNED classifier over CONSTRUCTION-CUE
features (never the surface lemma) induce GENERALIZED result-TYPE categories
(REFUSAL/GRANT/BLOCK/ACHIEVE/FAIL) that TRANSFER to surface forms never seen during training, the
way `hdlab/frame_induction.py` already proved for OOV-verb thematic-role induction (subj-axis
held-out acc 0.833, transferring construction cues -- has_scomp/degree_mod/progressive/order_pre --
to unseen psych verbs, never the verb lemma itself)? If yes, the COMMON COMPOSITIONAL CORE is
tractable and the multi-month M3 (full concept/script inventory scaling) is worth committing to; if
no, M1's finding generalizes -- the residual needs broad world-knowledge, not compositional
construction-cue induction, and M3 should be banked/reconsidered.

## Anti-circular design (the 3 confounds Stage-1/Stage-2/M1 all had; explicitly avoided here)
1. **Result-TYPE cue features, never the surface lemma/idiom.** The 7 CONSTRUCTION_ATOMS
   (`hdlab/result_type_induction.py::span_feats`) are: `comm_verb`/`give_verb`/`achieve_verb`/
   `fail_verb` (verb-CLASS membership via a small 2-3-word TRAIN-only exemplar pool + WordNet
   primary-sense-synonym-set overlap, `hdlab.goal_achievement._pool_related`'s already-vetted
   technique, self-contained-copied to avoid a circular import -- see that module's docstring),
   `neg_present` (any clausal negator anywhere in the span, `goal_typing.NEGATORS` incl. bare "no"),
   `modal_neg` (a modal immediately followed by a negator, or a modal n't-contraction -- one
   structural cue for "would not give"), and `no_verb_class_cue` (an explicit POSITIVE marker for
   "none of the 4 verb pools fired", added because `ruleind`'s conjunction search only supports
   PRESENT-feature conjuncts, no negated-feature primitive -- needed so bare discourse-negation,
   "Uh. No.", is inducible as `{neg_present, no_verb_class_cue} -> REFUSAL`). No atom is ever a
   literal verb-lemma string.
2. **Held-out-SURFACE-FORM split, not held-out sentences of the same seed words.**
   `TRAIN_EXAMPLES` (34 episodes) uses ONLY the seed pool words (say/decline/reply,
   give/offer/grant, achieve/finish/succeed, fail/lose) plus bare "No."/"Uh. No.".
   `HELDOUT_EXAMPLES` (26 episodes) uses ONLY DIFFERENT verbs/phrases never in TRAIN
   (told/answered/objected/refused/responded/"Never." for REFUSAL; handed/permitted/allowed/
   awarded/provided for GRANT; the SAME 5 under modal-negation for BLOCK; completed/accomplished/
   won/reached for ACHIEVE; negated-achieve forms + missed/flunked/quit for FAIL). Disjointness of
   the `tag` field between the two banks is asserted by the module self-test.
3. **DesireDB training separation.** `hdlab.result_type_induction.get_induced_hypothesis()` fits
   ONLY on `TRAIN_EXAMPLES` (module-level cache, trained once, reused unmodified for both GATE-1's
   held-out eval AND GATE-2's DesireDB scoring) -- it NEVER sees a DesireDB row. GATE-2's
   `utility_channel_resulttype_grounded` call sites pass `(chosen_name, hypothesis)` explicitly
   (rather than importing the getter internally) so this is visually obvious at every call site.

## GATE-1 design (generalization, run first, no DesireDB)
Fit `hdlab.learner.registry.learn` (candidate_plugins = estimation / ruleind / proginduction, MDL
auto-select, mirroring `hdlab/frame_induction.py::default_spec`'s structure) on the 34 TRAIN
episodes; evaluate on the 26 HELD-OUT episodes. Three numbers, computed identically by
`hdlab.result_type_induction.self_test()` and this cell's own `run_gate1()` (cross-checked in this
cell's `--self-test` mode):
- **held_out_acc** -- fraction of HELD-OUT items the induced hypothesis classifies correctly
  (default-to-TRAIN-majority-class on abstain, matching frame_induction's honest-degrade
  convention).
- **memorization_baseline_acc** -- an EXACT TRAIN-surface-form-tag lookup (no WordNet, no
  construction cues); by construction every HELD-OUT tag is absent from TRAIN, so this can only
  ever return the fixed default -- the "a system that can only recall exact seen forms" strawman
  GATE-1 must clearly beat.
- **scramble_control_acc** -- TRAIN gold labels permuted (fixed seed 20260809, `random.Random`, not
  `hash()`-derived) before an IDENTICAL re-fit; must collapse toward chance/majority-class-rate
  (HELD-OUT majority-class share = 6/26=0.231; `GATE1_SCRAMBLE_COLLAPSE_MAX=0.35` gives headroom
  above that share while still requiring clear non-informativeness).

**MEASURED (this session, both the module self-test AND this cell's own GATE-1 reproduce
identically):** `held_out_acc=0.8846` (23/26), `memorization_baseline_acc=0.2308`,
`delta_vs_memorization=0.6538`, `scramble_control_acc=0.0769`. Chosen plugin: `ruleind` (MDL-beat
`estimation`/`proginduction`; induced a fully interpretable 7-rule decision list --
`comm_verb->REFUSAL`, `modal_neg->BLOCK`, `give_verb->GRANT`, `fail_verb->FAIL`,
`{achieve_verb,neg_present}->FAIL`, `achieve_verb->ACHIEVE`, default->REFUSAL -- see
`data/exp_direction_b_M2_speechact_result_generalization_v1/metrics.json:gate1`). The 3 misses are
honest, disclosed coverage gaps: "objected"/"quit" (neither pool-relates to their intended class via
WordNet primary-sense overlap) and "awarded"+"provided" under BLOCK (fire `modal_neg` but not
`give_verb`, an unseen atom-combination the induced rules do not cover).

## GATE-1 pre-registered bands
- **HARD-PASS:** `held_out_acc >= 0.60` AND `delta_vs_memorization >= 0.15` AND
  `scramble_control_acc <= 0.35`.
- **HARD-FAIL (kill criterion -- STOP, do not run GATE-2):** `held_out_acc < 0.40`.
- **MIDDLE_BAND:** everything in `[0.40, 0.60)` or clearing 0.60 but missing the delta/scramble
  conjuncts.
- **MEASURED result: HARD_PASS** (0.8846 >= 0.60; 0.6538 >= 0.15; 0.0769 <= 0.35, all three
  comfortably clear).

## GATE-2 design (recovery, only runs because GATE-1 cleared the 0.40 floor)
Reuses the IDENTICAL M1/Stage-2 abstain-to-majority PRIMARY cohort (seed 20260808,
`FULL_N_PER_CLASS=80` -> n=160 draw -> cohort n=22, 8 gold-Unfulfilled -- via
`import exp_utility_satisfaction_channel_v1 as _s2`, same loader/cohort/metrics helpers, no
duplication) plus the IDENTICAL M1 ENLARGED context cohort (`ENLARGED_N_ROWS=900`,
`ENLARGED_SEED=20260809`, same as M1, for head-to-head comparability with M1's measured 0/37).

### Arms (PRIMARY cohort)
- **(i) majority-only baseline** -- identical to Stage-2/M1's arm i.
- **(ii) utility_channel (Stage-2, WordNet-only)** -- identical to Stage-2/M1's arm ii, kept for
  delta-attribution.
- **(iii) utility_channel_resulttype_grounded** -- THE M2 MECHANISM ARM the gate applies to. New
  `hdlab.goal_achievement._attribute_outcome_state_resulttype_grounded` combines the SAME per-token
  WordNet vote (`_token_vote`, unchanged) with a supplementary result-type vote
  (`hdlab.result_type_induction.result_type_votes`, weighted `_RESULTTYPE_VOTE_WEIGHT=2`x a single
  token vote -- the SAME fixed pre-declared weight M1 used for its idiom vote). Applies
  `hdlab.idiom_grounding.dedupe_repeated_sentences` first (DesireDB's own verbatim-repeated-sentence
  scraping artifact, reused general-purpose utility -- an early self-test run caught this: without
  the dedupe, a duplicated "calls" token inflated the WordNet sub-vote 3x and masked the correct
  result-type flip on the flagship "told her no" case; fixed before any scored run).
- **(iv) utility_channel_resulttype_grounded, SCRAMBLED goal cue** -- MANDATORY pairscramble control
  (task-mandated). `_s2._scrambled_desires`, deterministic derangement, PROT-023 compliant.

### GATE-2 pre-registered bands (reused verbatim from M1's own thresholds)
- **HARD-PASS:** PRIMARY `recovery_rate(arm iii) >= 0.40` AND pairscramble collapses
  (`abs(acc_iv-acc_i) <= 0.05`) AND does not leak (`abs(acc_iv-acc_iii) > 0.03`).
- **MIDDLE_BAND:** `0.15 <= recovery_rate < 0.40`, pairscramble collapses.
- **HARD-FAIL:** `recovery_rate < 0.15` OR pairscramble does not collapse OR leaks.
- **INVALID:** `harness_validity_check` (same n=80/seed=20260808 3-channel reproduction Stage-2/M1
  use) delta `> 0.03` macro-F1 vs documented 0.686, OR cohort n `< 15`, OR 0 gold-Unfulfilled items.

## MEASURED results (this session, `--full`, elapsed_s=417.2)
- `harness_validity_check`: n=80, measured_macro_f1=0.6992, delta=+0.0132 (valid, tolerance 0.03).
- **GATE-2 PRIMARY cohort (n=22, 8 gold-Unfulfilled):** `recovery_iii = 3/8 = 0.375` -- BEATS M1's
  own PRIMARY-cohort recovery (2/8=0.25). `acc_i=0.6364, acc_ii=0.6364, acc_iii=0.7727, acc_iv=0.5909`.
  Pairscramble: `|acc_iv-acc_i|=0.0455 <= 0.05` (collapses=True); `|acc_iv-acc_iii|=0.1818 > 0.03`
  (leaks=False). **GATE-2 component verdict: MIDDLE_BAND** (0.375 is in `[0.15,0.40)`, just under
  the 0.40 HARD-PASS bar; pairscramble clean).
- **ENLARGED cohort context (900-row subsample, cohort n=152, 37 gold-Unfulfilled -- the EXACT
  denominator M1 measured 0/37 on):** `recovery_arm_iii = 9/37 = 0.2432`. This is the headline
  BREADTH finding: unlike M1's idiom lexicon (zero generalization beyond its 29 hand-authored
  phrases), M2's learned construction-cue classifier recovers real signal on a 5x-larger,
  independently-drawn sample it was never tuned against. Pairscramble at scale:
  `acc_i=0.7566, acc_scrambled=0.7303, delta=0.0263 <= 0.05` (collapses_at_scale=True) -- confirms
  the mechanism stays genuinely goal-conditioned (not a content-only bias) at the larger scale too.
  `resulttype_match_frequency` on this subsample's gold-Unfulfilled items: REFUSAL=18, ACHIEVE=4,
  FAIL=1 (no GRANT/BLOCK matches in this particular gold-Unfulfilled subset -- expected, since a
  granted/permitted outcome is rarely itself the reason a desire ends up Unfulfilled).
- **Overall combined verdict: MIDDLE_BAND** (`combine_verdicts`: GATE-1=HARD_PASS,
  GATE-2=MIDDLE_BAND -> MIDDLE_BAND; HARD-PASS requires BOTH gates to HARD-PASS).

## Compute architecture
(b) sequential-CPU with justification: construction-cue extraction (regex + WordNet
`_pool_related` lookups, `lru_cache`/module-cache-memoized where the underlying primitive already
caches) + `hdlab.learner.registry.learn` fit (MEASURED@this session's design probe: 7 atoms,
`max_nodes=5` -> proginduction enumeration 0.26s; the reason this module caps at 7 atoms, not the
9 initially considered, which measured 91s at `max_nodes=7` -- compute-proportionality gate) + FHRR
bind/bundle/unbind over N=2048 complex64 vectors (unchanged from Stage-2/M1). PRIMARY cohort ~22
items x 4 arms; ENLARGED cohort is a single pass over the SAME 900-row subsample M1 used. No
matmul-heavy batchable primitive at this scale. Storage: no_storage/no_composition.

## Cell-template mandatory fields
- `cell_chunked`: false (single-process; smoke=54s, full=417s, both single foreground calls).
- `start_marker_written` / `crash_diagnostic_present` / `heartbeat_present`: true.
- `arms_differ_verified`: true (hash-check on arms i/ii/iii/iv's full prediction vectors, PRIMARY
  cohort, smoke + full -- MEASURED: arms i/ii bit-identical at PRIMARY-cohort scale as expected
  (arm iii's mechanism did not change any items where WordNet-only already predicted correctly, at
  THIS particular n=22 draw), arm iii and arm iv both distinct digests from i/ii and each other).
- `final_metrics_atomicity`: `tmp_replace`.
- `except SystemExit: raise` before `except Exception` (no bare except, no `except BaseException`)
  -- grep-verified clean.
- `crlb_n/a`: "deterministic construction-cue-vote learner (ruleind/estimation/proginduction over a
  fixed 7-atom boolean feature space) + FHRR bind/bundle/cleanup over a fixed 6-role x 3-filler
  codebook, no decoded/noisy continuous signal from a swept capacity regime -- identical
  justification to Stage-2/M1's crlb_n/a, unchanged FHRR mechanism layer."
- `baseline_in_band` / `discriminator_reachability`: n/a per META_RULE_AG (channel-comparison cell,
  not a swept-difficulty cell).
- `HP_SCOPE`: `{arm_iii: [gate2_recovery_rate, pairscramble_collapse_vs_i, pairscramble_leak_vs_iii]}`
  -- arms i/ii/iv are comparators/controls, not independently gated. GATE-1's own bands apply to the
  induced `(chosen_name, hypothesis)` as a whole, not a per-arm split (there is only one induced
  classifier).
- `cardinality_ok`: `EXPECTED_N_UNITS = 4` (one unit per PRIMARY-cohort arm: i, ii, iii, iv). GATE-1
  and the ENLARGED-cohort pass are separate context computations, not cardinality units (same
  convention M1 used for its own ENLARGED pass).
- `deterministic_seeding`: true (GATE-1 scramble seed 20260809 via `random.Random`, not `hash()`;
  DesireDB draw seed 20260808 reused from Stage-2/M1; ENLARGED seed 20260809 reused from M1;
  FHRR role/filler vectors seeded 20260809 (unchanged from Stage-2); derangement offset `n//2`, not
  `hash()`-derived).
- `calibration_check`: `adaptive_with_discriminator_gate` -- the verb-class exemplar pools
  (say/decline/reply, give/offer/grant, achieve/finish/succeed, fail/lose) and the 7 CONSTRUCTION_
  ATOMS were fixed BEFORE any GATE-1/GATE-2 number was computed; the ONE adjustment made mid-build
  (adding `no_verb_class_cue` as an explicit positive atom, and applying `dedupe_repeated_sentences`
  to the M2 evidence path) was a MECHANISM-LEVEL fix (ruleind's conjunct search has no
  negated-feature primitive; DesireDB's own repeated-text artifact, general data hygiene, not an
  idiom/result-type-specific tune) made BEFORE the first scored `--full` run, not a post-hoc
  label-fit. Two KNOWN, DISCLOSED noise sources (not patched away, to avoid p-hacking the atom set
  to the eval set): (1) partial pool coverage -- "objected"/"quit"/"awarded"/"provided" do not
  pool-relate to their intended verb class via WordNet primary-sense overlap; (2) a genuine
  WordNet polysemy collision -- "handed"'s primary sense (`pass.v.05`, "place into the hands of")
  shares the lemma "reach" with `achieve.v.01` ("attain"), so "handed" spuriously also fires
  `achieve_verb` alongside the correct `give_verb` (harmless here because ruleind's decision-list
  matching only requires a rule's conjunct to be a SUBSET of the fired features, but reported
  honestly as measured noise, consistent with this arc's repeated finding that first/primary-sense
  WordNet grounding is noisy).
- `functional_requirements`: "classify a short/terse/idiomatic-adjacent outcome span into a
  goal-relevant result-TYPE that GENERALIZES to unseen surface forms" ->
  `hdlab.result_type_induction.span_feats` (construction-cue encoder) +
  `hdlab.learner.registry.learn` (MDL-auto-selected induction, the SAME centralized learner
  `hdlab/frame_induction.py` already proved this pattern with) + a new
  `result_type_votes`/`_attribute_outcome_state_resulttype_grounded`/
  `utility_channel_trace_resulttype_grounded` bridge into the EXISTING FHRR utility_channel scoring
  layer (Stage-2/M1's organs, reused unmodified).
- `real_code_path_exercised`: `[span_feats, registry.learn, ruleind_plugin.apply,
  result_type_votes, _attribute_outcome_state_resulttype_grounded, bind, unbind, bundle,
  utility_channel_trace_resulttype_grounded]` -- self-test (`hdlab.result_type_induction.self_test`
  + `hdlab.goal_achievement.self_test_resulttype_grounded_channel`) constructs the REAL construction-
  cue extraction + a REAL `registry.learn` fit + the REAL FHRR primitives on the two flagship
  real-DesireDB cohort cases (the SAME two M1's self-test uses, "Uh. No." and "told her no" --
  both real held-out-surface-form cases, not synthetic), not a synthetic-only branch.
- `progress_logging`: `print_flush_true` (this cell's `timeout_s` is well under 1800s in practice --
  smoke 54s, full 417s -- but prints `[smoke]`/`[full]` progress lines with `flush=True` throughout
  for auditability regardless).

## Autonomy notes (exp_dev-owned, per the task's contract)
Exact result-type taxonomy (5 classes) + cue-feature definitions (7 CONSTRUCTION_ATOMS), the
train/held-out surface-form split (34 TRAIN / 26 HELD-OUT items, exact wording), the verb-class
exemplar pools (2-3 words each), learner spec (candidate_plugins/max_nodes/purity_thresh, mirroring
`frame_induction.default_spec`'s structure), cell/module naming, seeds (20260809 for the GATE-1
scramble control, reusing 20260808/20260809 from Stage-2/M1 elsewhere for direct comparability) --
all exp_dev's own design choices, documented above. The anti-circular design (held-out surface
forms, result-type-not-lemma features, TRAIN/DesireDB separation), the two-gate sequencing (GATE-1
before GATE-2, STOP on GATE-1 HARD-FAIL), the GATE-1/GATE-2 band thresholds, the mandatory
pairscramble control, and the enlarged-cohort breadth report are NOT exp_dev's to drop and were not
altered.
