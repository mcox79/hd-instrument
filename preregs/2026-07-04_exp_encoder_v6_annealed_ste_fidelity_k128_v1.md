# Pre-registration: encoder_v6_annealed_ste_fidelity_k128_v1

Date: 2026-07-04
Author: exp_dev (hdi_exp_dev)
Anchor: encoder_v6_annealed_ste_fidelity_k128_v1
Cells:
- core: experiments/exp_encoder_v6_annealed_ste_fidelity_k128_v1_core.py
- seed 7: experiments/exp_encoder_v6_annealed_ste_fidelity_k128_v1_seed_7.py
- seed 13: experiments/exp_encoder_v6_annealed_ste_fidelity_k128_v1_seed_13.py

## Question

At K=128 / 3.125%-active block code, the TRAINED student reaches ret_agree10
~0.21 while the CODE CEILING (teacher vectors through the same block sparsifier,
zero training error) is 0.4295 -- a TRAINING-FIDELITY gap, not a code/sparsity
limit. A 4-field-convergent research drill ranks the live levers
B (discrete-gradient fidelity) > A (capacity) > C (schedule) > D (data). The #1
reported reason a trained model UNDERUSES an available discrete code is the HARD
straight-through estimator on block-argmax: it starves the near-winner gradient
that decides fine near-neighbor rank (ret_agree10). This cell tests lever B:
does a temperature-annealed soft-to-hard block STE + a soft/hard consistency
term lift ret_agree10 over the hard-STE control? Capacity (A) rides along as a
paired secondary arm on top of B, and every arm logs its train-loss trajectory
as a FREE capacity-killer diagnostic.

## Source numbers (tagged)

- code ceiling ret_agree10 (K128): 0.4295278
  MEASURED@data/exp_encoder_teacher_sparsifier_bypass_v1/metrics.json:/recovery/ortho_k128_ret_agree10
- ortho-vs-random ret_agree10 gap (K128): +0.0047 (rotation dead)
  MEASURED@same:/recovery/random_k128_ret_agree10 = 0.4248791
- trained hard-STE baseline (hidden=2048) K128 final ret_agree10: 0.2112; hi80_cos: 0.8320
  MEASURED@data/exp_encoder_v3e_decline_vs_plateau_v1_seed7/metrics.json
- B-alone expected lift: +0.06 to +0.10 -> ~0.26-0.30
  HYPOTHESIZED@notes/research_drill_sparse_distill_fidelity_lever_ladder_2026-07-04.md
- P_deflated(B lead reaches >=0.35 @ 2% sparse) ~= 0.25 (partially structural)
  HYPOTHESIZED@same
- max attainable B-lift: 0.4295 - 0.2112 = 0.2183 (ret_agree10 cannot exceed the ceiling)

## Arms (PAIRED nested ablation; same seed/data/split/objective/LR/steps)

FIXED for all arms: kb=128, blk_l=32, N_DIM=4096 (3.125% active); in_batch RKD
only; nce_weight=0 (NCE dropped, zero gradient); batch=128; cosine-decay LR;
STEPS=8000 (longer than v3e's 6000 -- lever C as B's delivery vehicle, HELD
CONSTANT across arms so C is not confounded with B).

| arm            | ste_mode | MLP hidden | isolates                       |
|----------------|----------|-----------|---------------------------------|
| HARD_STE       | hard     | 2048      | control == v3e (Gate-D posctrl) |
| ANNEAL_STE     | anneal   | 2048      | +B (lever B, vs HARD_STE)       |
| ANNEAL_STE_W2X | anneal   | 4096      | +B+A (capacity on top of B)     |

Annealed STE: s_soft = softmax(|z|/tau) * sign(z) per 32-block (tau cosine
anneal 2.0->0.1 over first 80% of steps then held; as tau->0, s_soft -> the hard
argmax code the eval uses); loss = in_batch_RKD(norm(s_soft)) + 0.5 *
MSE(norm(s_soft), norm(hard_code).detach()). Eval ALWAYS uses the hard code
(v3._encode_hard_block), so the annealed arm's benefit must show up in the HARD
code's retrieval. ONE trainer for all arms (nce=0) -> HARD_STE and ANNEAL_STE
are bit-paired to each other.

Smoke uses narrower widths {256,256,512} to keep the machinery gate fast while
exercising the SAME hard/anneal STE branches.

## Bands (HARD-PASS / HARD-FAIL declared BEFORE running)

Primary discriminator: delta_B = ANNEAL_STE_final_ret - HARD_STE_final_ret
(FINAL-step BLOCK codes; paired within seed). Secondary (reported, not gated):
delta_A_given_B = ANNEAL_STE_W2X_final_ret - ANNEAL_STE_final_ret.

- HARD_PASS (LEVER_B_ANNEALED_STE_LIFTS_RETRIEVAL): delta_B >= 0.05, no calib
  regression -> the hard-STE gradient bias WAS the bottleneck; annealed STE is
  the lever. (Below the research-expected +0.06-0.10, above noise; strict floor.)
- HARD_FAIL (LEVER_B_DEAD_STE_BIAS_NOT_THE_GAP): delta_B <= 0.02 -> STE-bias
  hypothesis REFUTED at K128; the 0.43 ceiling is structural (k-WTA rank cap) or
  the gap is elsewhere. Decisive negative; routes to the sparsity-honest fallback.
- MIDDLE_BAND (LEVER_B_MARGINAL_LIFT): 0.02 < delta_B < 0.05 -> small real
  estimator effect; needs a tau-schedule sweep or 2nd-seed confirmation.
- HARD_FAIL guardrails (any arm):
  - ANNEAL_REGRESSES_CALIBRATION: delta_B hi80_cos < -0.02.
  - Gate-D: HARD_STE final ret NOT in [0.15, 0.28] -> REGIME_OR_INVOCATION_MISMATCH.
  - FALSE_WIN_ALGEBRA_LAST_STEP_<arm>: keyed J5 SBC acc_at1 < 0.90.
  - HARD_FAIL_SHUFFLED_KEY_LEAK: shuffled-key J5 acc_at1 > 0.05 or hit > 0.10.
  - RANDOM_BLOCK keyed J5 < 0.98; cardinality n_units < 28.

FREE capacity diagnostic (reported field capacity_hypothesis_diagnostic): if
HARD_STE train-loss floored while its ret < 0.30 -> capacity NOT the bottleneck
(favors B). Not a gate; it interprets a HARD_FAIL/MIDDLE outcome.

Aggregation across the 2 seeds at verdict time (Director/Skunkworks read both).

## SCHEMA-VET fields

- cardinality_ok: EXPECTED_N_UNITS = 28 = 3 arms x 9 (4 semantic + 1 semantic
  RANDOM_BLOCK + 4 keyed RANDOM_BLOCK/BLOCK_LAST/BLOCK_BESTVAL/shuffled) + 1
  shared CHARPOS. Same both run modes (SMOKE=FULL code path).
- arms_differ_verified: true (sha256 over each arm's codes; hard vs anneal STE
  and width produce distinct students -> distinct codes). arms_differ_exempted: [].
- final_metrics_atomicity: tmp_replace.
- except SystemExit: raise before except Exception (no BaseException / bare).
- crlb / capacity-feasibility: ret_agree10 reachability via the empirical code
  ceiling 0.4295 (max lift 0.2183 >> HARD_PASS delta_B 0.05). crlb_n_a declared;
  spearman r_max(128)=0.901 recorded. discriminator_reachability: true.
- baseline_in_band: CHARPOS ret in (0.05, 0.95); HARD_STE in Gate-D band.
- discriminator-survives-scale: option (B) analytical -- smoke's tiny V_train
  cannot reproduce the near-neighbor coverage that drives ret_agree10; smoke is
  a MACHINERY gate only (both hard and anneal STE branches execute, codes
  differ, integrity gates fire, cardinality holds). B-lift is FULL-only; the
  REMOTE-QUEUE OFFICIAL landing is canonical.
- calibration_check: default_ok_for_this_regime (hyperparameters identical to
  the validated v3e/v5 lineage except the STE + width axes; tau/cons defaults are
  literature-grounded, flagged schedule-sensitive by the research drill).
- HP_SCOPE: delta_B band -> {HARD_STE,ANNEAL_STE}_BLOCK_LAST; delta_A_given_B ->
  {ANNEAL_STE,ANNEAL_STE_W2X}; DENSE_*/*_BESTVAL context; RANDOM_BLOCK/CHARPOS/
  shuffled_key integrity-only.
- cell_chunked: true; start_marker_written / crash_diagnostic_present /
  heartbeat_present: true; progress_logging: print_flush_true.

## Compute architecture

Class (a) batched-GPU: student forward/backward + annealed soft-block softmax
are batched matmul/elementwise on cuda (device auto -> cuda; overnight_queue GPU
dispatch); eval samples pairs batched. Storage strategy: no_composition
(single-hop retrieval-agreement is the metric; keyed-J5 SBC is a bounded 5-item
integrity control, not a chain -> bundled acceptable per SHARDED-DEFAULT carve-out).

## Functional requirements (Gate E)

1. Encode a BGE-large embedding into a K=128 block sparse code whose
   nearest-neighbor structure agrees with the teacher (ret_agree10) -> trained
   MLP student + block STE (annealed variant is the mechanism under test;
   HARD_STE == v3e is the positive control).
2. Preserve coarse cosine calibration (hi80_cos) while lifting retrieval ->
   guarded by ANNEAL_REGRESSES_CALIBRATION.
3. Preserve SBC keyed-composition validity (keyed J5) -> integrity control,
   independent of the STE (holds for any valid hard-block code).

## Gates A/B/C/D (composition/sweep gates)

- Gate A (sweep alignment): axis = STE mode + MLP width. Effective param each
  primitive experiences = the estimator bias (STE) and representational capacity
  (width); no routing holds them constant. ALIGNED.
- Gate B (discriminating band): HARD_STE ~0.21, ANNEAL_STE plausibly [0.21,0.30];
  the delta bracket [<=0.02 dead, 0.02-0.05 marginal, >=0.05 lift] partitions the
  reachable [0.20,0.43] band; all predicted points land in a discriminating band.
  discriminating_fraction: 1.0 (>= 0.30).
- Gate D (positive control): HARD_STE == v3e config; its final ret must reproduce
  v3e's 0.2112 within [0.15,0.28] at the FULL test regime, else the invocation
  drifted and the B comparison is void.

## Dispatch

- Smoke: local (bare `--smoke`) machinery gate first (SMOKE=FULL code path).
- Full: overnight_queue (GPU) -- GPU is IDLE (v7 K512 finished), lane free.
  SCP-based (local commit suffices, no origin push). timeout 7200s per seed cell
  (calibrated from v5's 335s FULL for 2 arms; 3 arms x 8000 steps + annealed
  double-STE + wider arm + more eval; generous headroom on idle GPU). 2 seed
  cells (seed 7, seed 13).
- Canonical = the remote-queue official landing, not the local smoke/preview.

## Sequenced next cell (contingent)

- IF LEVER_B lifts: tau-schedule sweep + student EMA + full B+A+C stack targeting
  0.35 (research: B+A+C needed for 0.35, P_deflated ~0.30-0.33).
- IF LEVER_B_DEAD: the 0.43 ceiling is structural (k-WTA rank-preservation cap);
  accept the ~0.30 sparsity-honest fallback (distill-from-BGE) per encoder goals.
