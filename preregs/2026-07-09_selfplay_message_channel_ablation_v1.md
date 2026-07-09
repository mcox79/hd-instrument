# Pre-registration: selfplay_message_channel_ablation_v1

Anchor: `selfplay_message_channel_ablation_v1`
Cell: `experiments/exp_selfplay_message_channel_ablation_v1.py`
Date: 2026-07-09
Gates: master-map BUILD (internal self-play referential grounding) -- INTERVENTIONAL localization of the
corr~0.38 structural ceiling.
Drill: `notes/research_active_intervention_query_selection_grounding_2026-07-09.md` (S3 sharpest-residual
question: shared discrete-channel/game architecture as the next mechanism class).
Prior cells (reference / reused game machinery): `exp_selfplay_dg_pattern_separation_xfit_v1.py`
(prereg `preregs/2026-07-09_selfplay_dg_pattern_separation_xfit_v1.md`),
`exp_selfplay_b1_exog_predictive_anchor_v1.py` (prereg
`preregs/2026-07-09_selfplay_b1_exog_predictive_anchor_v1.md`).

## Question
Three consecutive independent decorrelation mechanisms ALL plateaued at corr(failmask) ~0.38:
DG pattern-separation `0.377` (MEASURED@data/exp_selfplay_dg_pattern_separation_xfit_v1/metrics.json:
gates.dg_failmask_corr), B1 disjoint-fold cross-fit `0.393` (MEASURED@same:gates.b1_failmask_corr),
B1+EXOG shared-reconstruction-target `0.382` (MEASURED@data/exp_selfplay_b1_exog_predictive_anchor_v1/
metrics.json:gates.exog_failmask_corr). A suspiciously stable floor across theoretically distinct upstream
interventions. The active-intervention drill flagged the shared discrete `MessageChannel` (both self-play
halves funnel through the SAME K-symbol channel `P`) as the prime suspect. **Does corr(failmask) RESPOND to
CHANNEL manipulation? Is the shared discrete channel the CAUSE of the ~0.38 ceiling?** Tested
INTERVENTIONALLY: VARY only the channel, measure whether the effect (failmask correlation) MOVES.

## Task construction (self-play referential naming game; REUSED verbatim)
Referents = ConceptNet subgraph nodes (REUSED `load_cn_subgraph` + `char_trigram_features` + `build_adjlist`
+ `_l2norm` + `info_nce` + `vicreg_repulsion`). Speaker: PRIVILEGED info access (neighborhood-augmented
`Xn`); Listener: BARE (`X`). The four probe arms (A0..A3) are the SAME cross-fit self-play (separate
Enc_S/Enc_L, disjoint referent folds -- the B1_crossfit setup that lands ~0.39) and DIFFER ONLY in the
channel. NEW (the ablation): a mode-parameterized `Channel` + mode-dispatch `forward_game`/`eval_masks`
(each half self-decodes through its OWN codebook).

## Six arms (channel is the ONLY thing varied for A0..A3)
- **A0_shared** (BASELINE / contrast anchor): current shared discrete K-symbol channel (== B1_crossfit).
  MUST reproduce ~0.38 (band [0.30,0.46]) or the contrast is void.
- **A1_wide** (CAPACITY up): shared discrete channel, K widened 8x (K_wide=8*K_base). Isolates channel
  CAPACITY; discreteness + sharedness fixed.
- **A2_separate** (UN-SHARE): separate speaker codebook `P_s` and listener codebook `P_l`; the discrete
  symbol INDEX is the shared wire protocol, the code GEOMETRY is un-shared. Speaker picks + self-decodes via
  `P_s`; listener interprets via `P_l`. The most direct probe of the sharedness hypothesis.
- **A3_continuous** (REMOVE DISCRETENESS): hard-gumbel one-hot replaced by a SOFT softmax mixture over the
  SAME K prototypes -> continuous message vector (convex combination). Isolates DISCRETENESS; K + sharedness
  fixed.
- **A4_mirror** (MUST-RISE CONTROL == assert_discriminator_fires): tied encoder (Enc_S==Enc_L), shared
  discrete channel, differ only by info access (Xn vs X). This is the reference B0_mirror (~0.77-0.79 in all
  3 prior cells) -- the PROVEN high-corr control that verifies the screen CAN fire high. If A4 does not rise
  materially above A0 -> screen saturation-vacuous.
- **A5_cap1** (CHANNEL-DESTRUCTION DIAGNOSTIC; reported, not a verdict gate): capacity-1 channel (K=1),
  constant zero-information message. NOTE: the task's original guess was "degraded channel RAISES corr";
  the smoke FALSIFIES this in a cross-fit regime -- capacity-1 DROPS corr toward 0 while collapsing grounding
  to chance, because destroying the shared channel REMOVES the shared coupling (failures become independent).
  This is itself strong evidence the coupling is carried by the CHANNEL. It is a diagnostic complement to the
  must-rise mirror, not the saturation guard.

## Parameters (DECIDED by exp_dev; HYPOTHESIZED unless MEASURED-tagged)
- `K_base`: SELFTEST 8 / SMOKE 12 / FULL 24 (matches the reference cells). `K_wide = 8*K_base` (FULL 192).
- `code_dim`: 32/96/192; `feat_dim`: 512/4096/8192; `epochs`: 12/80/220; `seeds`: [7]/[7,13,17]/[7,13,17,23,29].
- A3 soft-message temperature = the annealed Gumbel-tau schedule value (2.0 -> 0.4 FULL) -> genuine soft
  mixture that anneals sharper, matching the discrete arms' annealing (mechanism-ratio parity).
- All channel-variant RATIOS held across SMOKE/FULL (K_wide=8x, A5 K=1, A3 soft, A4 tied) -> SMOKE=FULL parity.

## Discriminator (the whole test; `failure_mask_corr` REUSED VERBATIM)
Per referent, two INDEPENDENT per-half competence outcomes on the SAME decision; each half self-decodes
through its OWN codebook (`P_s` for speaker, `P_l` for listener; shared arms have `P_s==P_l`).
`failmask_corr(arm) = corr(1-speaker_correct, 1-listener_correct)` (phi over referents).
`grounding_acc(arm) = mean(listener_correct)`.

## Pre-registered bands (BOTH; LOCKED before FULL dispatch) -- the pinned-vs-moves decision
- **HARD_PASS_CHANNEL_IS_BOTTLENECK** (channel IS the bottleneck -- a fixable, specific target): A0
  reproduces (corr in [0.30,0.46]) AND A4_mirror control fires ((A4-A0)>=0.15 AND A4>=0.50) AND at least ONE
  of {A1_wide, A2_separate, A3_continuous} DROPS MATERIALLY (arm corr <= 0.30 AND (A0-arm) >= 0.10, ideally
  toward ~0.20) with NON-degenerate codes AND load-bearing arms (A0, A2) codes non-degenerate. Lever =
  widen / separate / de-discretize the channel.
- **HARD_FAIL_CHANNEL_NOT_BOTTLENECK_REDIRECT_ENCODER_OR_TASK** (channel is NOT the bottleneck -- deeper
  finding): A0 reproduces AND A4 fires AND ALL well-measured (non-degenerate, codes-ok) probes among
  {A1,A2,A3} stay PINNED (|arm-A0| < 0.05), with A2_separate among the valid pinned arms and >= 2 valid
  probes. => the shared bias is MORE FUNDAMENTAL than the channel; redirect to the shared ENCODER/
  representation both halves inherit, or the shared TASK objective (the 4th-consecutive-plateau redirect).
- **MIDDLE_BAND_PARTIAL_CHANNEL_MOVEMENT**: partial / single-arm movement clearing neither the material-drop
  bar nor the all-pinned bar (e.g. drift 0.05-0.10 but not <=0.30) -> sweep the moved axis before concluding.
- **SATURATION_VACUOUS_CONTROL_DID_NOT_FIRE**: A4_mirror does not rise above A0 by the control margin =>
  screen cannot fire high; nothing trusted.
- **ANCHOR_NOT_REPRODUCED_VOID**: A0 corr outside [0.30,0.46] => anchor is not the ~0.38 floor; void.
- **CODE_COLLAPSE_VOID**: A0 or A2 collapsed message codes (entropy < 1.0 bit) => degenerate-code artifact.

BOTH outcomes gold: HARD_PASS = channel is a fixable specific target; HARD_FAIL = the ceiling is DEEPER than
the channel (shared encoder/representation or task itself -- a more fundamental redirect). Complements B2_ACT
(sampling axis); together they localize the ~0.38 floor.

## Compute architecture
Class (c) mixed sequential-CPU with justification. Shallow linear ProjHead (feat->code) + K x code channel;
per-step batched matmuls + Gumbel-softmax / softmax + candidate scoring. NOT GPU-batching-mandatory (nets
small: code_dim<=192; cost is the sequential self-play loop -- genuine epoch dependency). 6 arms x 5 seeds =
30 units; A5 (K=1) nearly free, A3/A4 cheap. Storage: no_storage (transient codes; no PartitionedStore
writes). `progress_logging: print_flush_true` (line-buffered stdout + flush=True + per (seed,arm) heartbeat;
FULL timeout_s >= 1800).

## SCHEMA-VET gate fields
- `cardinality_ok: true` -- EXPECTED_N_UNITS = n_arms(6) * n_seeds; verdict emits
  HARD_FAIL_CARDINALITY_BREACH_META_RULE_H if fewer land.
- `arms_differ_verified: true` -- all 6 arms' (speaker,listener) mask-pair digests asserted pairwise-distinct
  per seed (MEASURED: smoke passed the assertion).
- `final_metrics_atomicity: tmp_replace` (write_metrics -> os.replace; crash-diag atomic).
- `except SystemExit: raise` BEFORE `except Exception` (no BaseException). Grep-gate PASS.
- `crlb_n/a`: discriminator is a within-cell failure-mask CORRELATION vs the A4_mirror must-rise control, not
  a closed-form noise floor. `discriminator_reachability: true` -- HP material-drop corr<=0.30 sits inside
  [0, corr(A4)~0.78]; A4 fires high by construction (tied encoder).
- `baseline_in_band: true` (AG) -- A0 failure rates 0.05..0.95 both halves (MEASURED smoke spk=0.447
  lis=0.543).
- `calibration_check: adaptive_with_discriminator_gate` -- K / K_wide / Gumbel-tau anneal / soft-temp fixed
  per profile; anti-collapse entropy floor + A4-control-fires + A0-in-band + channel-sensitivity selftest
  recomputed per run (NOT tuned-for-verdict).
- `cell_chunked: false` (arms x seeds looped in one cell; per-unit `write_partial` checkpoints).
- `start_marker_written / crash_diagnostic_present / heartbeat_present: true`.
- `defensive_error_checking: passed_all_4_patterns`.
- `HP_SCOPE`: anchor-reproduce -> {A0}; control-fires -> {A4_mirror}; material-drop HP -> {A1,A2,A3};
  all-pinned HF -> {A1,A2,A3} (A2 required valid); anti-collapse -> {A0,A1,A2,A3} (A4 shared K>1 OK, A5 EXEMPT
  capacity-1 by construction).
- `discriminating_fraction: n/a` (no sweep axis; 6 fixed arms). `sweep_alignment_verdict: n/a`.
- `positive_control_arms`: A0_shared reproduces the ~0.38 cross-fit floor at the test regime (MEASURED smoke
  0.329, prior FULL B1 0.393); A4_mirror reproduces the shared-blind-spot high-corr signature (MEASURED smoke
  0.779, prior FULL B0 0.794).

## Functional Requirements
1. Two encoders, tied or cross-fit -> ProjHead x2 / tied (implemented).
2. Mode-parameterized message channel (shared / wide-K / separate-codebook / continuous-soft / capacity-1) ->
   `Channel` + `_channel_message` + mode-dispatch `forward_game`/`eval_masks` (the ablation).
3. Per-referent independent competence of each half on the SAME decision, each half self-decoding via its OWN
   codebook -> `eval_masks`.
4. Failure-mask independence screen -> `failure_mask_corr` (reused verbatim).
5. Joint grounding metric -> `grounding_acc`.
6. Anti-collapse / code-non-degeneracy per arm (esp. A1 wide, A3 continuous) -> `_arm_codes_ok` (entropy +
   symbols for discrete; dominant-symbol entropy + msg-vec pairwise-cos ceiling for continuous; A5 exempt).
7. Channel-damage / must-rise saturation guard -> A4_mirror control-fires + A5_cap1 diagnostic.

## Smoke result (MEASURED, gate CLEAR; 3 seeds x 6 arms = 18 units, 113s local CPU)
MEASURED@data/exp_selfplay_message_channel_ablation_v1_smoke/metrics.json:gates
- discriminator selftest ok (planted corr high=0.773/indep=-0.066; metric responds to channel: toy cap1=0.716
  > wide=0.592).
- A0_shared corr=0.329 (0.349/0.304/0.334) ground=0.457 spk_fail=0.447 lis_fail=0.543 -> ANCHOR reproduces
  (in [0.30,0.46]) + in-band.
- A1_wide(K=96) corr=0.216 (0.172/0.232/0.244) -> d=-0.113 MATERIAL drop (capacity).
- A2_separate corr=0.074 (0.047/0.104/0.070) spk_fail=0.302 -> d=-0.256 MATERIAL drop (sharedness; largest
  move; speaker self-decode fair after the own-codebook eval fix).
- A3_continuous corr=0.260 (0.242/0.284/0.253) msg_cos=0.371 (non-degenerate, < 0.90) -> d=-0.070 (drops but
  under the 0.10 material margin at smoke).
- A4_mirror corr=0.779 (0.799/0.743/0.794) -> rise=+0.450 CONTROL FIRES (reproduces reference B0 ~0.79).
- A5_cap1 corr=0.011 ground=0.117 [diag] -> channel destruction decouples failures + collapses grounding.
- codes_ok all core arms=True (entropy A0/A1/A2/A3/A4 = 2.8/5.4/3.4/3.3/3.1 bits); arms_differ passed.
- **Smoke verdict = HARD_PASS_CHANNEL_IS_BOTTLENECK** (A1+A2 moved materially, control fires, anchor
  reproduces). Smoke is at K=12 / 3 seeds; the CANONICAL verdict is the FULL run (K=24, n=8000, 5 seeds) --
  smoke proves the machinery + control fire + discriminator responds to channel across the full arm set;
  all outcomes (HARD_PASS / MIDDLE / HARD_FAIL) remain REACHABLE at FULL.

## P estimates (from drill; deflated)
- P(a channel manipulation among A1/A2/A3 moves corr materially at FULL -> HARD_PASS): ~0.45-0.55 (the smoke
  A2_separate move to ~0.07 is a strong signal; but K=24 FULL headroom may compress the wide-K drop; still
  above the drill's original P~0.30 because the smoke shows real movement, not a null).
- P(all probes pin at ~0.38 -> HARD_FAIL, deeper-than-channel, encoder/task redirect): ~0.25-0.35 (the 4th-
  consecutive-plateau contingency; smoke argues against a full pin, but FULL K=24 could differ).
- P(A3 continuous specifically is a fair, non-degenerate probe at FULL): ~0.7 (smoke msg_cos 0.37 healthy).

## Dispatch
FULL -> `remote_cpu_queue` (CPU cell; small nets; sequential loop; local is SMOKE-ONLY per USER lock).
timeout_s = 7200 (~2h ceiling; reference 15-unit cells landed ~1513-1597s, this 30-unit cell ~3000-3600s
expected, 7200 gives ~2x headroom; heartbeat + print-flush make a hang diagnosable).
