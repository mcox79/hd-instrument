# Cell design + pre-reg: exp_role_gate_hold_revise_oracle_probe_v1 (2026-08-01)

Cell: `experiments/exp_role_gate_hold_revise_oracle_probe_v1.py`
Anchor: `exp_role_gate_hold_revise_oracle_probe_v1`
Dispatch: local CPU, foreground, deterministic (no RNG-heavy compute) -- closed-form oracle-gate
probe, no encoder, no training loop. `local_cpu_queue` not even required; ran directly to completion.

## Prior-work check (mandatory, before authoring)

`bash tools/substrate_query.sh "prediction-error gated hold-then-revise role assignment mention slot
spawn PBWM"` -> top cosine=0.3135 (FrameNet 'Mention' frame-element graph, VerbNet/WordNet 'mention'
synset -- generic lexical concept-graph entries, not a prior probe of this mechanism) and cosine=0.2852
("ROLE ASSIGNMENTS", an unrelated M4d cortex-milestone note). **No prior cell or atom at cosine>0.30
tests this mechanism (oracle-PE-gated hold-then-revise commit/spawn discipline in isolation from
encoder quality). Genuinely novel, not a rediscovery.**

## What this de-risks

The single load-bearing NOVEL inference in
`notes/brain_syntax_to_role_mechanism_and_forward_predictive_encoder_spec_2026-07-30.md` Part 2(b):
that a prediction-error-GATED hold-then-REPLACE state can (a) revise a provisional canonical-default
role assignment on a later disambiguation cue, and (b) spawn a new mention slot at referent
introduction. Fed an ORACLE PE signal (clean spike exactly at the true cue/introduction position) to
isolate the GATE DISCIPLINE from encoder-signal quality (that is Probe 2, separate, later, gated on
this one passing). Reuses `hdlab/slot_attention_wm.py`'s PBWM gate formula VERBATIM
(`boundary_k = sigmoid((surprise_k - theta) / tau)`), not reinvented; does not instantiate the full
trainable `SlotAttentionWM` class because that module's PE signal and content candidates are
themselves LEARNED (assumes a trained encoder + trained keys) -- exactly the two things this probe
must NOT assume yet.

## Pre-registered bands (set in code BEFORE any run; see module docstring + top-of-file constants)

Task 1 (ROLE, 5 arms: ORACLE_REPLACE / NO_GATE / BLEND / RANDOM_POSITION / RANDOM_GUESS):
- `ROLE_REVISE_HARD_PASS = 0.90` -- ORACLE_REPLACE final-role accuracy on non-canonical
  (PASSIVE + OBJREL) items >= this. THEORETICAL@ feasibility: reachable at exactly 1.0 by
  construction (cue always fires within the item span for both templates; see
  `band_feasibility_note()` in the cell).
- `ROLE_INVERSION_HARD_FAIL_MAX = 0.20` -- NO_GATE accuracy on non-canonical items <= this
  (systematic reversal). THEORETICAL@: reachable at exactly 0.0 by construction (no-revise always
  keeps the wrong default on a full-reversal item).
- `UNDERPERFORM_MARGIN = 0.15` -- BLEND and RANDOM_POSITION must each trail ORACLE_REPLACE by
  >= this margin on non-canonical accuracy.
- `ROLE_ACTIVE_PRESERVED >= 0.90` -- canonical (ACTIVE) items must stay correct under ORACLE_REPLACE
  (revision discipline must not corrupt items that never needed revision).

Task 2 (MENTION, 4 arms: ORACLE_GATE / RANDOM_GATE / ALWAYS_SPAWN / ALWAYS_REACTIVATE):
- `MENTION_GATE_HARD_PASS = 0.90` -- ORACLE_GATE balanced (macro-averaged spawn/reactivate recall)
  accuracy >= this.
- `MENTION_CONTROL_MAX_F1 = 0.60` -- RANDOM_GATE balanced accuracy, and ALWAYS_SPAWN's recall on
  the reactivate class / ALWAYS_REACTIVATE's recall on the spawn class, must each land <= this.
  (Scored on the SPECIFIC class each naive control structurally ignores, not the imbalanced
  positive-class F1 -- an early self-test iteration caught F1 being inflated to ~0.86 for
  ALWAYS_SPAWN purely from class imbalance (~75% of gold decisions are legitimately "spawn" in
  this construction); fixed before dispatch, not after seeing a bad full-run result.)
- `MENTION_GENERALIZES_ACROSS_INTRO_TYPES` -- ORACLE_GATE per-intro-type accuracy (INDEFINITE,
  BARE_PLURAL, PROPER_NAME) each >= 0.85, confirming the mechanism is not just an "a/an" detector
  (contract requirement).

## BRAIN-FIDELITY gates (added mid-cycle per USER steer -- ADDED alongside, not instead of, the
above task-accuracy bands; judge the mechanism on the brain's OWN metric, not just downstream
accuracy)

- `SHAPE_FIDELITY_STAGED` -- ORACLE_REPLACE must genuinely HOLD the canonical default then REPLACE
  it in a single step (not blend, not jitter/oscillate) on >=95% of non-canonical items. Measured via
  an explicit per-TOKEN trajectory simulation of h_role[NOUN1] (not a single closed-form final
  value), per Grodzinsky TDH / Bornkessel-Schlesewsky eADM / Friederici's staged model.
- `TIMING_FIDELITY_AT_CUE` -- ORACLE_REPLACE's revision must fire with mean |flip_position -
  cue_position| == 0 (P600-locus analog; Osterhout & Holcomb -- revision AT the disambiguating
  word, not early/late/diffuse).
- `TIMING_FIDELITY_RANDOM_IS_DIFFUSE` -- RANDOM_POSITION's mean |flip_offset| must exceed 1.0
  token, confirming the timing metric is genuinely discriminating (not vacuous -- i.e. it can tell
  correctly-timed from incorrectly-timed revision).
- `METRIC_FIDELITY_DIRECTIONAL_INVERSION` -- NO_GATE must underperform a genuine chance-noise
  baseline (RANDOM_GUESS, ~0.50 expected) by >= 0.20 margin. This is the brain's OWN diagnostic
  distinction (Caramazza & Zurif 1976 / Grodzinsky TDH): agrammatism produces SYSTEMATIC REVERSAL
  (below-chance, directional), not merely degraded/noisy performance (at-chance). A no-revise
  control landing at ~0.50 would have been the WRONG failure shape even if it "failed" the
  ROLE_INVERSION_HARD_FAIL_MAX<=0.20 band by some other route; this gate makes the shape explicit.
- `NO_GATE_CORRECTLY_NEVER_STAGED` -- sanity cross-check: NO_GATE's frac_staged must be <=0.05
  (it never performs the revise stage at all when required), confirming the shape metric and the
  inversion metric agree on WHY NO_GATE fails, not two unrelated numbers.
- The P600 analog (`pe_at_revision`, the oracle PE value AT the measured flip position) and the
  final-commit decisiveness (`final_margin` = cos-to-correct minus cos-to-wrong at the last token)
  are reported per arm as descriptive brain-fidelity diagnostics, not separate pass/fail gates --
  contrasting ORACLE_REPLACE's large positive final_margin (a decisive commit) against BLEND's
  near-zero final_margin (an ambiguous, undecided representation) is the qualitative signature the
  spec's "replace, not blend" claim predicts.

Honest scoping note (per the steer's own instruction): mention-side (Task 2) timing-fidelity is NOT
separately measured -- the mention items only carry a discrete oracle novelty signal AT the mention
token itself (no surrounding token stream to measure "diffuseness" against), so the
position/timing-offset concept doesn't transfer cleanly to Task 2 the way it does to Task 1's
multi-token clause stream. Not forced; flagged honestly rather than fabricated.

## SCHEMA-VET checklist (see in-file CELL-TEMPLATE MANDATORY header comment for the full mapping)

arms_differ_verified (sha256 digest per arm per seed, 5 role arms + 4 mention arms, all pairwise
distinct -- 45 digest checks on the FULL run) | final_metrics_atomicity=tmp_replace |
except-SystemExit-before-except-Exception (no bare except, no except BaseException; grep-gate clean)
| crlb_n/a (closed-form, no noise-limited estimator) | cardinality_ok (EXPECTED_N_UNITS = seeds*2,
counted via `tools/exp_checkpoint.py` unit records) | calibration_check=default_ok_for_this_regime
(theta/tau are the UNCHANGED values already used in slot_attention_wm.py's late-training/bistable
regime) | deterministic_seeding (only `torch.Generator().manual_seed(int)`, no `hash()`, no
`list(set())`) | HP_SCOPE declared per-arm in-file.

## MEASURED results (FULL run, 5 seeds {7,13,19,23,29}, 40 items/construction, 30 items/(intro-type,
condition), elapsed 1.20s)

MEASURED@d:/AI/hd-instrument/data/exp_role_gate_hold_revise_oracle_probe_v1/metrics.json:

- **verdict: HARD_PASS** -- all 15 gates (5 task-accuracy + 5 role brain-fidelity + 5 mention/control)
  pass.
- ROLE: `oracle_acc_noncanon=1.000`, `nogate_acc_noncanon=0.000`, `blend_acc_noncanon=0.500`,
  `randpos_acc_noncanon=0.459`, `randguess_acc_noncanon=0.496`, `oracle_acc_active=1.000`.
- MENTION: `mention_oracle_f1(balanced_acc)=1.000`, `mention_random_f1=0.500`,
  `mention_always_spawn(recall_reactivate)=0.000`, `mention_always_react(recall_spawn)=0.000`,
  per-intro-type accuracy INDEFINITE/BARE_PLURAL/PROPER_NAME all = 1.000 (generalizes across all 3
  intro types, not just "a/an").
- BRAIN-FIDELITY: `oracle_frac_staged=1.000`, `oracle_mean_abs_flip_offset=0.000` (revision fires
  exactly at the cue, every time), `oracle_mean_pe_at_revision(P600 analog)=1.000`,
  `oracle_mean_final_margin=1.181` (decisive commit) vs `blend_mean_final_margin=1.2e-7`
  (near-zero, ambiguous commit -- the qualitative "replace decisively vs blend ambiguously"
  contrast the spec predicts), `randpos_mean_abs_flip_offset=1.187` tokens (genuinely diffuse vs
  oracle's exact 0), `nogate_frac_staged=0.000` (correctly never performs the revise stage),
  `directional_inversion_gap_vs_chance=0.496` (NO_GATE lands ~0.50 BELOW the chance-noise baseline,
  the systematic-reversal signature, not mere noise).
