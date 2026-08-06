# Pre-reg: consequence-learning loop with a SIGNAL-A-PRIMARY teacher (decisive re-score)

Date: 2026-08-06. Status: **PRE-REGISTERED (bands fixed BEFORE running); LOCAL-only decisive re-run.**
Parent: `preregs/2026-08-06_consequence_learning_loop_oov_outcome_verb_valence_v1.md` (contract reused
verbatim). Parent cell + engine: `experiments/exp_consequence_learning_loop_oov_outcome_verb_valence_
v1.py` + `hdlab/consequence_learning_loop.py` (commit a892153ea, HARD_FAIL INSUFFICIENT_YIELD). This
pre-reg is the Director-directed CHEAP FIX named in the parent's drill (backup doc 2026-08-06): a
Signal-A-PRIMARY teacher, scored as PRIMARY on the eval, to answer the ONE open question the HARD_FAIL
left: **when the loop DOES ground words, are they grounded CORRECTLY?**

## Prior-work check (per exp_dev standing discipline)

Prior hits at cosine>0.30: the direct parent cell/engine (commit a892153ea) is the sole close prior --
this is its explicitly-named revival criterion, NOT a rediscovery. Backup doc line 65: "CHEAP FIX (own
pre-reg): Signal-A-PRIMARY teacher (drop the over-strict AND-gate) -> 3->11." Registry: parent SHELVEd
with revival = "raise teacher-signal density via Signal-A-primary + multi-organ goal-resolution teacher
so >=6 eval-OOV lemmas reach MIN_CONFIRM." This cell measures the Signal-A-primary half of that revival
criterion. (The substrate-KB wrapper `tools/substrate_query.sh` timed out at 2min this session; the
prior-work check is instead satisfied by direct on-disk reading of the parent prereg + backup doc +
capability-registry revival note, which name this exact cell.)

## The change (single variable)

DROP the dual-signal AND-gate. Make the TEACHER = Signal A alone (`congruence_decision`'s own structural
MET/UNMET verdict). Everything else IDENTICAL to the parent: structural referent-linked credit
assignment (`_credit_targets`), anti-drift `MIN_CONFIRM=3`, mandatory eval-passage exclusion
(non-circularity), 3-way POS/NEG/NEUTRAL consolidation (`consolidate`), the same W=3 window, the same
LIGHT_VERB / NOISE canaries, the same `congruence_with_lexicon_fallback` live scorer.

**Engine is UNCHANGED.** `hdlab/consequence_learning_loop.py` ALREADY threads `signal_mode=
"signal_a_only"` through `teacher_verdict -> credit_window -> run_pass -> learn_corpus` (validated in
the parent's own self-test, gate (6)). The parent cell ran `signal_a_only` only as an ABLATION and
collected noise/light-verb rates but NEVER SCORED it on the 36-item eval as primary, never computed
`n_learnable` or per-verb correctness. This cell makes `signal_a_only` the PRIMARY teacher and SCORES
it -- a re-score of an existing validated engine, not a new build. The engine module gets ZERO edits.

FIDELITY (Director will VET by reading code + metrics):
1. Teacher stays `congruence_decision`'s MET/UNMET (NOT reward theta). The module still never imports
   `pfc_gate_cfrpe` / `context_grounded_valence` / `grounded_appraisal_sim` (engine unchanged; new cell
   imports only `hdlab.consequence_learning_loop`, `hdlab.goal_typing`, `hdlab.verb_lexical_similarity`,
   the parent cell's helpers, `tools.exp_checkpoint`, `numpy`).
2. Credit-assignment stays STRUCTURAL referent-linked; anti-drift `MIN_CONFIRM=3` unchanged;
   passage-exclusion MANDATORY (a verb is learned from OTHER episodes, never its own test item).
3. NON-CIRCULARITY gates: (a) label-SCRAMBLE -> grounding must collapse; (b) OOV-INTEGRITY -- every
   grounded lemma must be genuinely OOV of the seed lexicon at learn-time (`in_lexicon(lemma,"outcome")
   is False` with the acquired overlay cleared), so its polarity came from CONSEQUENCE not surface form
   / not a re-derived seed lexicon; (c) RANDOM-CREDIT ablation; (d) EXCLUSION-INTEGRITY re-check.
4. LIGHT-VERB NEUTRALITY must still hold (light verbs converge to GROUNDED_NEUTRAL, not forced polarity).

## Decisive metrics (MEASURED, per-axis, no tuning toward gold)

- `primary_accuracy` = fraction of the 36 OOV items live `congruence_with_lexicon_fallback` types
  correctly WITH the Signal-A-primary overlay live (untyped/abstain = MISS, coverage-inclusive).
  Empty-overlay floor = 0.1667 (== parent's measured fallthrough, 6/36).
- `n_learnable` = # unique eval-OOV lemmas that consolidated POS/NEG under the Signal-A-primary teacher.
- `learnable_subset_accuracy` = per-item accuracy on eval OOV items whose outcome verb consolidated
  POS/NEG (scored live with the overlay). **THE decisive number** -- when the loop grounds a word, does
  it type that word's eval items correctly? Chance = 0.5.
- `grounded_verb_polarity_match_rate` = per-grounded-eval-verb, learned polarity vs eval gold polarity.
  Chance = 0.5. Reported as a per-verb table (which words grounded, learned polarity, gold, match).
- `light_verb_canary_neutral_rate`, `noise_canary_consolidated_count` -- anti-drift / neutrality.
- Controls: `scrambled_learnable_subset_accuracy` (+per-seed), `scrambled_primary_accuracy`,
  `random_credit_learnable_subset_accuracy`, `oov_integrity` (0 seed leaks), `exclusion_integrity`.

## Falsifiable bands (fixed before running)

**HARD-PASS (ALL):**
1. `learnable_subset_accuracy >= 0.70` (materially beats chance 0.5) AND `n_learnable >= 4`.
2. `primary_accuracy >= 0.25` (materially lifts the 0.1667 empty-overlay floor -- grounded words add
   real, correctly-typed coverage).
3. Non-circularity clean:
   - SCRAMBLE: `(learnable_subset_accuracy - scrambled_learnable_subset_accuracy) >= 0.15` AND
     `scrambled_learnable_subset_accuracy <= 0.60` (collapses toward chance).
   - RANDOM-CREDIT: `(learnable_subset_accuracy - random_credit_learnable_subset_accuracy) >= 0.15`
     (referent-linkage load-bearing); if random-credit grounds < 3 eval-lemmas, report that honestly
     (the ablation grounded too little to compare -- still non-circular, noted not silently passed).
   - OOV-INTEGRITY: `oov_integrity_seed_leaks == 0` (every grounded lemma genuinely OOV of the seed).
   - EXCLUSION-INTEGRITY: `exclusion_integrity.clean == True`.
   - `noise_canary_consolidated_count == 0`.

**HARD-FAIL (ANY):**
- `learnable_subset_accuracy <= 0.55` (grounded words type NO BETTER THAN CHANCE -- the loop grounds
  but grounds WRONG; the decisive negative -- would refute the learning-loop direction as currently
  wired).
- `n_learnable < 3` (INSUFFICIENT_YIELD persists even Signal-A-primary -> congruence's ~15-window
  recall is the hard floor -> points to the multi-organ-teacher densification as the next lever).
- SCRAMBLE stays within 0.08 of real on the learnable subset (polarity not consequence-derived ->
  circular).
- RANDOM-CREDIT stays within 0.08 of real on the learnable subset AND random-credit grounded >= 3
  eval-lemmas (referent-linkage not doing the credit work).
- `oov_integrity_seed_leaks >= 1` (a seed word was credited -> non-circularity breach).
- `noise_canary_consolidated_count >= 2` (anti-drift leak).
- `light_verb_canary_neutral_rate < 0.30` (light verbs spuriously POS/NEG-locked from noise).

**MIDDLE-BAND:** `learnable_subset_accuracy` in (0.55, 0.70), OR `n_learnable` in [3,4), OR
`primary_accuracy` in (0.1667, 0.25), OR one non-circularity gate borderline (scramble subset in
[0.55,0.65] -- partial not full collapse), OR `light_verb_canary_neutral_rate` in [0.30,0.70). Report
honestly (parent's signal_a ablation measured `light_verb_neutral=0.5333`, so lv-neutral is NOT a
HARD-PASS gate here -- >=0.70 would be a pre-doomed/unreachable gate for this variant; lv-neutral is a
REPORTED metric + a HARD-FAIL floor at 0.30 only, per discriminator-reachability discipline).

## Positive control (Gate D, reproduce prior at test regime)

`andgate_reference` arm: run the ORIGINAL `signal_mode="and_gate"` on the SAME full corpus and confirm
it reproduces the parent's starvation (`n_registered == 0`, primary == 0.1667). This proves the ONLY
difference between this cell and the HARD_FAIL parent is the single swapped variable (signal mode), and
that the corpus/window/exclusion pipeline is byte-reproduced. Tolerance: `andgate n_registered == 0`
(exact, matches parent metrics.json:n_registered=0).

## Compute architecture

Sequential-CPU. No GPU, no training, no gradient. Deterministic corpus scan + counting + threshold
consolidation (same class as parent; parent full ran 231s). `crlb: n/a` (not a capacity/argmax-noise
cell). `storage_strategy`: `ACQUIRED_OUTCOME_VERB_FEATURES` process-local in-memory overlay, cleared on
entry + exit (hygiene). Expected wall time: ~3-5 min FULL (four ~25K-sentence passes; signal_a teacher
is slightly cheaper per window than the AND-gate -- skips the Signal-B lexicon_predict call).
**LOCAL-only, foreground-to-completion (remote/push NOT authorized): run FULL with an explicit Bash
`timeout: 600000` (10 min); it fits (parent 231s).** `progress_logging: print_flush_true`.

## SCHEMA-VET checklist

- `cardinality_ok`: EXPECTED_N_UNITS = corpus + main(signal_a) + baseline + scramble(5 seeds) +
  random_credit + andgate_reference = 6 resumable units (per-unit via `tools/exp_checkpoint.py`).
- `discriminator_reachability`: TRUE -- 36-item binary classification, empty floor 0.1667, ceiling 1.0.
  learnable_subset_accuracy chance = 0.5; HARD-PASS 0.70 is strictly above chance and physics-feasible
  IF >=4 of the ~11 Signal-A-grounded words are eval-OOV lemmas (UNKNOWN a priori -> can-fail on yield,
  a valid informative outcome).
- `baseline_in_band`: N/A (direct measurement vs fixed gold); empty-overlay floor 0.1667 re-derived at
  runtime, not assumed.
- `arms_differ_verified`: signal_a registered map must differ from andgate_reference map (11 vs 0
  expected) and from any scramble-seed registered map (permuted polarity); asserted at smoke.
- `final_metrics_atomicity`: `tmp_replace` (os.replace).
- `deterministic_seeding`: fixed integer seeds only (scramble 2000+s, random-credit 3000); no
  hash()-derived seeding; PROT-023/F.5 compliant.
- `except SystemExit: raise` BEFORE `except Exception` (no BaseException); start_marker +
  crash_diagnostic + resumable-per-unit; `progress_logging: print_flush_true`.
- `real_code_path`: self-test constructs the REAL engine at tiny scale (imports the engine self_test +
  the parent cell's real corpus reader on the real little_women file), asserts determinism.

## Cert gate

Engine + all production `hdlab/*` UNCHANGED (this cell only ADDs a new experiment file + reads the
existing engine's `signal_a_only` path + populates the already-empty-at-import
`ACQUIRED_OUTCOME_VERB_FEATURES` overlay via the existing `register_acquired_outcome` API, cleared on
exit). Cert baseline to confirm UNCHANGED: 220 passed, 3 skipped. Run `python verification/run_
certification.py` via `.venv/Scripts/python.exe` ONCE to confirm 220/3 (no before/after needed since no
cert-covered production file is touched).

## Files touched

- `experiments/exp_consequence_learning_loop_signal_a_primary_v1.py` (NEW) -- imports the parent cell's
  corpus/scoring/canary/scramble helpers verbatim + the unchanged engine; runs `signal_a_only` as the
  PRIMARY teacher with full scoring + per-verb correctness + non-circularity battery.
- `preregs/2026-08-06_consequence_learning_loop_signal_a_primary_v1.md` (this file, NEW).
- `hdlab/consequence_learning_loop.py`, `experiments/exp_consequence_learning_loop_oov_outcome_verb_
  valence_v1.py`, `experiments/data/goal_bearing_modern_eval_v1.jsonl` -- UNTOUCHED.
