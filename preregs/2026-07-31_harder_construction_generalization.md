# Pre-reg: Harder-construction generalization test of the certified encoder retrain

Cell: `experiments/exp_situation_model_harder_construction_generalization_v1.py`
Anchor: `situation_model_harder_construction_generalization_v1`
Date: 2026-07-31
Validates: atom 29593 / `exp_situation_model_assembly_encoder_retrain_scale_v1.py` (certified minimal-unfreeze
encoder retrain, held-out situation-model loop lift over frozen). VALIDATION-BEFORE-WIRE. Director+USER gated:
NOT a wire/deploy/full-retrain.

## Question
The certified fine-tune lifts held-out loop over frozen on a harness where an entity is mentioned by the
IDENTICAL color-word token across statement / tag / question frames -> cross-frame entity re-id is solvable
by exact-token repetition. Does the learned cross-frame entity-stability GENERALIZE beyond the exact
template, or was it template-specific (exploiting exact-token copy)?

## Harder construction (ONE variable = front-end surface form)
Each ENT mention rendered "the <MOD> <color>" with <MOD> drawn from a SHARED pool of 8 distinct single-token
adjectives, DETERMINISTICALLY keyed on (frame, entity, args) so the same entity has DIFFERENT surface forms
across its statement / tag / query frames. Exact-surface cross-frame copy fails; correct re-id requires a
surface/context-invariant, color-determined ENT representation. Color word (shared handle) stays present ->
FAIR on held-out COLORS (modifier pool shared train/held; "ignore modifier, bind on entity" is a general
rule that must transfer). MARK-addressed (b-type) frames LEFT UNMODIFIED = built-in did-not-change control.
Implemented by monkeypatching eb's 3 ENT render functions; every consumer (oracle, eval, geometry probes,
fine-tune text) flips together. clean.render_passage_text (structural POOLED floor) NOT patched.

SCOPE (honest): harder-synthetic surface variation, NOT arbitrary lexical-synonym knowledge (unfair on
held-out by construction) and NOT a naturalistic corpus. Cheap intermediate validation.

## Tests (HARD held-out; all arms share identical hard eval passages; only ENCODER WEIGHTS differ)
- TRANSFER (test 1): certified fine-tune (trained EASY) evaluated on HARD. Reported sub-result.
- METHOD-ROBUSTNESS (test 2, pre-registered can-fail): fine-tune same objective (minimal-unfreeze depth=1
  standout, nctx=40, 220 steps) ON hard; does it still lift loop over frozen?
- EASY-ANCHOR positive control: reproduce certified frozen->tuned lift on EASY held-out (reuse faithful).

Config: depth=1 (certified standout), nctx=40, steps=220, seeds (7,13), eval_n=60. CPU, push-free,
resumable per-seed, --budget-sec keeps each call < 10 min.

## Pre-registered bands (gate on METHOD-ROBUSTNESS test 2)
- HARD_PASS (GENERALIZES): mean(tuned_hard_loop - frozen_hard_loop) >= 0.05 AND capture >= 0.35 of
  (tuned_hard_ORACLE - frozen_hard) headroom AND every seed lift > 0 AND loop-anchored collapse guard HOLDS
  [C1 tuned>=frozen; C2 wc_drift<=0.15; C3 entcons>=0.85; C4 q_agree>=0.55] AND memorization gap
  (train-minus-held) <= 0.15.
- HARD_FAIL (TEMPLATE-SPECIFIC): mean lift <= 0.02 OR collapse (guard C1/C3 fail with cratered loop).
- MIDDLE: moved but did not clear HARD_PASS.
- INVALID: a can-fail floor did not collapse OR POOLED_READER reservoir-decodable OR PROOF-OF-HARDNESS fails
  (frozen representation not degraded: loop_degrade < 0.03 AND entcons_degrade < 0.05) OR construction
  uninformative (tuned_hard_ORACLE - frozen_hard headroom < 0.05).

## Proof-of-hardness (measurement-first; CORRECTED after smoke)
The initial plan gated on an exact-surface string-matcher (`token_copy_reid`). MEASURED@probe 2026-07-31 this
does NOT crater on hard (0.75): the color HANDLE token persists in the surface, so a matcher keying on the
embedded color word still wins -- surface NOISE (modifiers) does not remove literal-token repetition of the
entity handle. Removing it fairly on HELD-OUT entities would require lexical-synonym knowledge (a naturalistic
problem, out of cheap-synthetic scope). The CORRECT, honest proof that the construction is genuinely harder is
that the surface variation DEGRADES the frozen CONTEXTUAL representation: MEASURED@probe easy frozen loop 0.449
/ entcons 0.817 -> hard frozen loop 0.388 / entcons 0.708 (degrade 0.061 loop / 0.109 entcons) with oracle
headroom 0.271. So the test measures whether the retrain objective GENERALIZES to producing surface/context-
INVARIANT entity reps on held-out entities -- a real representation-generalization property the easy identical-
token template never stressed. The string-matcher number is REPORTED as an honest limitation diagnostic, not a
gate. HONEST SCOPE: this is representation-robustness-to-surface-variation, NOT literal-synonym re-id.

## Schema-vet
- arms_differ_verified: frozen vs tuned-hard main_enc distinct (inert fine-tune bug-catch).
- final_metrics_atomicity: tmp_replace + per-seed units.jsonl (resumable).
- except SystemExit: raise before except Exception (no BaseException / bare except).
- crlb_n/a: zero-learned-param FHRR loop; learned params only in encoder top layer (depth=1).
- baseline_in_band: FROZEN on HARD is the wall; ORACLE the ceiling; 4 floors + POOLED + MOST_RECENT collapse.
- discriminator survives scale: real encoder + real fine-tune + real loop at real N; self-test real_code_path
  under both easy/hard renders + drift guard + token-copy proof.
- calibration_check: default_ok_for_this_regime (reuses certified cell's calibrated tau / conditioner).
- cardinality_ok: EXPECTED_N_UNITS = len(seeds); verdict counts loaded units.
- start_marker_written / crash_diagnostic_present / heartbeat: per-seed checkpoint = progress durability;
  print_flush_true.
- HYPOTHESIZED vs MEASURED: all numeric bars are HYPOTHESIZED@this prereg (pre-registered); certified
  reference numbers MEASURED@data/exp_situation_model_assembly_encoder_retrain_scale_v1.
