# Pre-reg (RE-REG): encoder-retrain SCALE -- CORRECTED collapse guard

Cell: `experiments/exp_situation_model_assembly_encoder_retrain_scale_v1.py`
Anchor: `situation_model_assembly_encoder_retrain_scale_v1`
Supersedes: `preregs/2026-07-31_encoder_retrain_scale_bounded.md` (the collapse guard ONLY; question,
fairness gate, floors, one-variable design UNCHANGED).
Predecessor data: prior grid run (units.jsonl 2026-07-31, 8 conditions) + lite `8eb1b3129`.
Date: 2026-07-31 | Author: exp_dev | Mode: INLINE-LOCAL CPU foreground (push-free), resumable per-condition.

## WHY A RE-REG (honest, not post-hoc)
The prior run emitted MIDDLE_TRAJECTORY only because its pre-registered collapse guard
`held-out within-minus-cross (wc) >= 0.30` FAILED for every genuinely-strong config. Landed-VET confirmed
that bar is BACKWARDS -- wc is ANTI-CORRELATED with loop performance in this harness:

  MEASURED@data/exp_situation_model_assembly_encoder_retrain_scale_v1/units.jsonl (prior run):
    d1_div80_s13 : tuned_loop 0.830, wc_held 0.209  (STRONG, but wc < 0.30 -> old bar FAILS it)
    d1_div40_s13 : tuned_loop 0.799, wc_held 0.192  (STRONG, wc < 0.30 -> old bar FAILS it)
    d6_div40_s7  : tuned_loop 0.292, wc_held 0.552  (DEGENERATE full-unfreeze; ONLY config passing wc>=0.30)

  The one config that passed the old wc bar (d6, full unfreeze) is exactly the one whose loop CRATERS
  (0.292 < frozen 0.470) via representation drift. So `wc>=0.30` rubber-stamps the collapse and rejects the
  real breaks. A pre-registered bar cannot be silently discarded post-hoc to claim a pass; so we REPLACE it
  with a mechanistically-correct guard, RE-REGISTER here, and RE-RUN.

  The frozen (un-retrained) encoder itself sits at wc_frozen ~0.18-0.21 and decodes fine (loop 0.47-0.52);
  a healthy retrain stays NEAR that geometry. wc SPIKING far above frozen (d6: 0.552 vs 0.198) is the drift
  signature, NOT a health signature. Raw within-minus-cross cosine is not a loop-relevant health metric here.

## CORRECTED COLLAPSE GUARD (loop-anchored distinct-not-collapsed; FIXED before the re-run)
A condition is "distinct-not-collapsed" iff ALL of (each bar justified vs frozen baseline + the d6 degenerate):
  (C1) loop-not-cratered: tuned_loop_mean >= frozen_loop_mean.
       Justify: a collapsed encoder decodes WORSE than the frozen wall. PRIMARY, loop-anchored.
       d6 FAILS (0.292 < 0.470); all d1/d3 PASS. [replaces the discarded raw-cosine bar's role]
  (C2) no-drift: (wc_held - wc_frozen) <= WC_DRIFT_MAX (0.15).
       Justify: healthy retrain keeps within-color geometry near the frozen baseline (delta ~ +0.00..+0.06);
       drift inflates within-cosine far above frozen. d6 delta +0.354 FAILS; all d1/d3 delta <= 0.058 PASS.
       This is the CORRECTED direction of the old wc gate: an UPPER bound vs frozen, not a raw lower bound.
  (C3) entcons-genuine: tuned_entity_consistency >= ENTCONS_MIN (0.85).
       Justify: cross-frame binding must actually be happening (frozen is 0.813 = below the bar = the wall;
       healthy retrains 0.94-0.98). NOTE entcons alone is ambiguous (a total collapse saturates it to 1.000,
       as d6 does) -- which is exactly why C1 (loop) is the DISAMBIGUATOR: high entcons is only meaningful
       when loop is NOT cratered.
  (C4) q-agree-floor: tuned_q_agree >= Q_AGREE_GUARD_MIN (0.60). Cross-frame query agreement genuine.

  The guard is loop-anchored on purpose: entcons/q_agree/wc are all individually foolable by a degenerate
  encoder (d6 saturates entcons=1.000, q_agree=1.000, and "passes" the OLD wc bar), so the guard is
  ANCHORED to loop decode (C1) and a frozen-referenced drift cap (C2). Verified on prior data: d6 FAILS on
  BOTH C1 and C2 (doubly robust); every d1/d3 config PASSES all four.

## MUST-FAIL CONTROL (proves the guard is not a rubber stamp)
The verdict logic ASSERTS: `d6_div40_s7` (full unfreeze, cratered loop 0.292) FAILS the corrected guard. If
the guard ever passes d6, emit INVALID_GUARD_RUBBER_STAMP. (d6 is re-run this pass so the assertion binds on
FRESH data, not just stored.)

## TUNED-ORACLE CEILING (fixes the "exceeds-oracle" red flag; NEW measurement this re-run)
The prior run reported ONLY the FROZEN-arm oracle (oracle built on ext_fz). But the oracle fixes ONLY the
ENT-address (entity routing); the S/P role/state FILLS are still read via the encoder decode
(exp_situation_model_assembly_entity_file_v1.py:359-366). So a BETTER (tuned) encoder RAISES the oracle
ceiling -- a frozen-built oracle is NOT the ceiling for the tuned arm. The prior "tuned 0.830 > oracle 0.730"
red flag was a MISLABEL: 0.730 was the FROZEN-arm oracle. This re-run computes the TUNED-oracle per condition
(oracle built on ext_tn) and CLEAN_PASS requires tuned_loop <= tuned_oracle + ORACLE_TOL (0.02). VET recompute
(the standout): tuned-oracle 0.854 > tuned loop 0.830 -> NO violation. We reconfirm on fresh runs.

## CLEAN_PASS (can-fail; FIXED before the re-run) -- unchanged loop bar, corrected guard
CLEAN_PASS iff EXISTS a config (depth,nctx) where, robust across >= 2 seeds, EVERY seed-run satisfies ALL:
  - held-out per-type tuned loop acc >= 0.60 for ALL 3 query types (a,b,c)   [INHERITED unchanged]
  - the CORRECTED collapse guard (C1-C4) HOLDS
  - memorization gap (train_loop_mean - tuned_loop_mean) <= 0.15                [INHERITED unchanged]
  - tuned_loop_mean <= tuned_oracle_loop_mean + 0.02 (below the CORRECT ceiling)  [NEW]
  AND (validity, across all conditions) all can-fail floors collapse near chance.
  => certified break -> escalate to scale (Director+USER).
HARD-FAIL/MIDDLE otherwise:
  - PLATEAU: best tuned_loop_mean within 0.03 of lite 0.534 across ALL conditions.
  - MIDDLE_TRAJECTORY: moved but no config clears CLEAN_PASS across its seeds.
  - INVALID: a can-fail floor did not collapse OR pooled_reader reservoir-decodable OR guard rubber-stamps d6.

## Can-fail floors (must collapse near chance 0.05; validity gate, UNCHANGED)
random_addr, no_coref, wrongrole, shuffled, most_recent, pooled_reader.

## q_agree REFERENT reconciliation (honest baseline framing)
THIS harness's frozen-arm q_agree ~0.73 (MEASURED frozen_q_agree 0.739, role_attn-DECODED cross-frame query
agreement). The bolt-on WM arc's "0.31" q_agree is a DIFFERENT addressing scheme (learned-key-commit), a
different harness/mechanism -- NOT comparable. So the honest claim is: "loop 0.52->0.83 via cross-frame entity
re-id on the role_attn-decoded harness (frozen q_agree 0.73 -> tuned ~0.99)", NOT "breaks the 0.31 wall."

## Re-run grid (7 decisive conditions; d1 standout replicated + d6 must-fail control)
  d1_div40 seeds {7,13,19}; d1_div80 seeds {7,13,19}; d6_div40_s7 (must-fail control).
  ONE variable per condition = encoder weights (top-1 unfreeze for d1; top-6 for the d6 control) vs the frozen
  v2 baseline, identical DRIFT-guarded eval pipeline. div40->80 = contexts-per-train-entity (diversity lever;
  palette hard-capped at V_FILL=20 so contexts, not palette, is the honest diversity axis). Fresh execution
  (deterministic seeds reproduce prior loop numbers; the NEW field is tuned_oracle).

## Bars (module constants, fixed here)
  LOOP_TYPE_CLEAN_PASS=0.60  MEMORIZE_GAP_MAX=0.15  (inherited)
  WC_DRIFT_MAX=0.15  ENTCONS_MIN=0.85  Q_AGREE_GUARD_MIN=0.60  ORACLE_TOL=0.02  (corrected guard)

## Hardening (unchanged)
arms_differ (frozen vs tuned), tmp_replace atomic + per-condition units.jsonl resume, except SystemExit before
Exception (no BaseException), start_marker, crash_diagnostic, print-flush, DRIFT GUARD, real_code_path
self-test, per-call --budget-sec so each foreground call stays under the 10-min timeout.
