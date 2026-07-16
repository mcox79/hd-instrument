# Pre-registration: rank_matched_readout_tunable_plant_v1

Filed 2026-07-15. Cell: `experiments/exp_rank_matched_readout_tunable_plant_v1.py`.
Metrics: `data/exp_rank_matched_readout_tunable_plant_v1/metrics.json`.

## Purpose (closes one flagged operator-story gap)

The joint-code VET (`exp_joint_operator_capstone_selective_readouts_v1`, commit a23cfd71) flagged the LEARNED
RANK-R lever as SATURATED/UNTESTED on that arena (the count target already solved at R=1, so R was never
exercised). The detection decider found SYM is a RANK-1 DIAGONAL readout that degrades monotonically with
interaction rank (measured elsewhere: rank1 0.975 -> rank4 0.693). The rank-vs-dimensionality drill concluded the
FIX = explicit LEARNED rank-R (tax-free, not blind expansion). This cell CLOSES that with a construction-grade
synthetic validation of the rank-matching lever on a TUNABLE-INTERACTION-RANK plant, isolating the rank mechanism
the noisy real-data dense cell could not.

HONEST SCOPE: synthetic, noise-free, glass-box CONSTRUCTION-GRADE validation of the rank lever. Not a real-data
capability win. On a clean HARD_PASS -> route to Skunkworks landed-VET (it is an operator claim).

## Arena (plant)

- Two roles a,b; each draws a fixed CONSTITUENT CODE from a vocabulary of `L_VOCAB=48` codes, `phi_a,psi_b in R^m`,
  `m=64`. Codes are centered (`sum_a phi_a = 0`, `sum_b psi_b = 0`) so the plant carries ZERO additive/main-effect
  signal (the additive floor is chance by construction).
- Interaction target is a rank-`R_plant` BILINEAR FORM: `score(a,b) = phi_a^T M psi_b`,
  `M = U_plant diag(sigma) V_plant^T`, `rank(M) = R_plant`, `sigma == 1` (EQUAL singular values).
  `y = 1[score > median(score)]` (balanced binary, chance=0.5).
- EQUAL singular values are deliberate: no dominant component for a low-rank readout to hide behind -> matching the
  readout rank to `R_plant` is NECESSARY (Eckart-Young).
- `R_plant in {1,2,4,8}`. SEEN-vs-NOVEL held out by PAIRING (`QUERY_FRAC=0.35`). The readout reads the GIVEN code
  vector (no per-pair params) -> NOVEL accuracy is a genuine FORM-recovery test, not lookup.

## Arms

| arm | definition | role |
|---|---|---|
| LEARN_RANK_R, R in {1,2,4,8,16} | low-rank bilinear pooling `z=(phi.U)(*)(psi.V)`, R-dim -> logits | the lever; R=1 == rank-1 diagonal SYM |
| LEARN_BIND_DIAG | LITERAL substrate elementwise bind `z=phi(*)psi` -> logits | "the current bind"; reported |
| LEARN_ADD | `logits = phi.Wa + psi.Wb + b` (no interaction) | additive floor (~chance) |
| ORACLE | true score thresholded at train-median | ceiling sanity |
| SCRAMBLE | rank-16 readout on SHUFFLED train labels | MUST-FAIL |
| FREQ / POP | majority class | chance |

CITED@Kim et al. 2016 (low-rank bilinear pooling / Hadamard product); parietal gain-field analog.

## Predicted accuracy (THEORETICAL@Eckart-Young + Gaussian-threshold; NOT asserted, used to set bands)

For equal singular values, captured signal fraction `f = min(1, R/R_plant)`, correlation `rho ~= sqrt(f)`, and
binary median-threshold accuracy `acc ~= 0.5 + arcsin(rho)/pi`:

| R_plant \ readout R | 1 | 2 | 4 | 8 | 16 |
|---|---|---|---|---|---|
| 1 | ~0.97 | ~ceil | ~ceil | ~ceil | ~ceil |
| 2 | 0.75 | ~ceil | ~ceil | ~ceil | ~ceil |
| 4 | 0.667 | 0.75 | ~ceil | ~ceil | ~ceil |
| 8 | 0.615 | 0.667 | 0.75 | ~ceil | ~ceil |

The rank-1 staircase (0.97 -> 0.75 -> 0.667 -> 0.615 down the R_plant column) reproduces the flagged
0.975 -> 0.693 degradation. Matched-rank recovery gap at R_plant=4 predicted ~0.30 (ceiling - 0.667); the
HARD_PASS threshold (0.15) sits well under it.

## Gates / bands (registered BEFORE running; NOVEL stratum, mean over seeds)

- **G1 RECOVERY (rank is the lever):** for each R_plant, `acc[Rp][R=Rp] >= ORACLE[Rp] - 0.10`; and for
  Rp in {2,4,8}, `acc[Rp][R=Rp] - acc[Rp][R=1] >= 0.15`.
- **G2 DEGRADATION (rank-1 fails; reproduce 0.975->0.6x; telemetry-sensitivity):** `acc[Rp=1][R=1] >= 0.90`;
  `acc[Rp=1][R=1] - acc[Rp=4][R=1] >= 0.15`; `acc[Rp=4][R=1] >= 0.55` (above chance); rank-1 curve monotone
  non-increasing in R_plant within 0.03 (perturbing R_plant MOVES rank-1 accuracy).
- **G3 MONOTONE + SATURATION:** for each R_plant, `acc[Rp][R]` non-decreasing in R up to R=Rp within 0.03; over-rank
  `acc[Rp][R=16] >= acc[Rp][R=Rp] - 0.05` (over-rank does not hurt much).
- **G4 CONTROLS:** `min ORACLE >= 0.90`; `max SCRAMBLE <= 0.55` (must-fail fires); `max LEARN_ADD <= 0.60` (additive
  floor near chance).

**HARD_PASS** = G1 AND G2 AND G3 AND G4.
**HARD_FAIL** = NOT G1 (rank-R does not recover -> rank isn't the lever) OR NOT G2 (rank-1 does not degrade -> no
rank effect) OR NOT G4 (controls). **MIDDLE_BAND** = partial recovery / non-monotone.

## Compute architecture

- Class: **(b) sequential-CPU with justification.** ~8 small Adam fits per (R_plant, seed) unit; grid
  4 R_plant x 5 seeds = 20 units; ~160 fits total; each fit is a tiny matmul (`n~1500 x m=64`, R<=16, 400 epochs
  full-batch). Total wall predicted < 5 min single-core. The cell IS the readout-primitive being validated
  (glass-box CPU reference); GPU batching would speed it but is unnecessary at this size. Justified per the
  GPU-batching-mandatory exemption ("cell IS the substrate-primitive being validated").
- Storage strategy: `no_storage / no_composition` (self-contained readout-fit cell; no PartitionedStore / KGStore).

## SCHEMA-VET fields

- `cardinality_ok: true` (EXPECTED_N_UNITS = len(R_PLANT_GRID) = 4 per seed; verdict gates on count).
- `arms_differ_verified: true` (self-test ARMS-MUST-DIFFER hash over RANK_ARMS + BIND_DIAG + ADD + SCRAMBLE;
  ORACLE exempted -- a fully-recovered readout legitimately equals the oracle).
- `final_metrics_atomicity: "tmp_replace"`.
- `crlb_n/a: "noise-free deterministic plant; no per-sample noise floor. The accuracy ceiling is ~1.0 by
  Eckart-Young (exact rank-R representation). Discriminator = the rank-matching gap; reachability set by singular
  spectrum (equal sigma) -> predicted gap 0.30 at R_plant=4 >> HARD_PASS 0.15."`
- `discriminator_reachability: true`.
- `baseline_in_band: true` (baseline arms = LEARN_ADD, FREQ sit ~chance 0.5, in (0.05,0.95); self-test verifies).
  The rank-1-on-R_plant=1 ceiling (~0.97) is the intended RECOVERY case, declared not-a-baseline.
- `baseline_arms: [LEARN_ADD, FREQ]`.
- `calibration_check: "default_ok_for_this_regime"` (all hyperparams fixed a priori; no per-run tuning).
- `discriminator_fires: "rank_recovery_gap acc[Rp=4][R=4]-acc[Rp=4][R=1] >= 0.10 at smoke scale"` (META_RULE_K).
- Discriminator-survives-scale: **(B) analytical** -- the equal-sigma rank gap is m-INDEPENDENT for m>=R_plant
  (Eckart-Young captured-fraction depends only on R/R_plant, not m) -- **plus (C) preview**: smoke runs Rp=4 at
  reduced m=32 and must show the gap.
- `progress_logging: "print_flush_true"` (per-seed flush lines; line-buffered stdout; timeout < 1800s).
- `start_marker_written: true`; `crash_diagnostic_present: true`; `cell_chunked: false` (seed loop is fast,
  in-process; single-cell); `heartbeat_present: false` (cell < 5 min; per-seed flush lines suffice).
- `deterministic_seeding: true` (all RNG from `np.random.default_rng(int)` / `torch.Generator().manual_seed(int)`;
  no `hash()`, no `list(set())`; PROT-023 source scan clean).
- Real substrate exercised: `hd_bind` tie-check in self-test (LEARN_BIND_DIAG elementwise == FHRR bind on real
  codes as complex64). No KGStore/fit-module -> F.1-F.4 N/A.
- HP_SCOPE: {ORACLE: [G4 ceiling], SCRAMBLE: [G4 must-fail], LEARN_ADD: [G4 floor],
  LEARN_RANK_R: [G1 recovery, G2 degradation, G3 monotone], FREQ/POP: [none -- chance reference]}.

## Dispatch

Local re-authorized for this task (Director spawn prompt). Arena small -> author + self-test gate + smoke local,
then FULL. Full grid predicted < 5 min single-core.
