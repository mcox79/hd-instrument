# PRE-REG: substrate_anisotropy_mimo_waterfill_v1

**Date:** 2026-06-26
**Author:** exp_dev (cell author; spawn-and-die)
**Cell:** `experiments/exp_substrate_anisotropy_mimo_waterfill_v1.py`
**Anchor:** `substrate_anisotropy_mimo_waterfill_v1`
**Queue routing:** local_cpu_queue (numpy CPU; ~3-5hr wall full per handoff)

## Source documents (AUTHORITATIVE)

- Research drill: `notes/research_gap2_anisotropy_5x_drill_2026-06-26.md` section S1 (Tier A Anchor #1)
- Handoff: `notes/exp_dev_handoff_research_gap2_anisotropy_5x_drill_2026-06-26.md` ANCHOR CANDIDATE #1
- v2 fixture (cone-collapse anchor): `data/exp_substrate_anisotropy_rescue_4arm_sweep_v2_calibrated_meter_full/metrics.json`

## Mechanism (one paragraph)

The substrate's current dense KV cleanup treats every direction equally (uniform regularizer in pseudo-
inverse). In an anisotropic cone, most directions are nulls. Uniform cleanup wastes capacity on these
nulls -- amplifying noise where there is no signal. MIMO water-filling (40-year MIMO theory) replaces the
uniform diagonal regularizer in the Tikhonov-regularized pseudo-inverse with a SVD-water-filled regularizer:
pour cleanup capacity into high-SNR singular directions first, leave the nulls at floor. Mathematically:
cleanup = (K K^T + diag(reg))^-1 Y where reg_i = max(0, mu - lambda_i) (water level mu set to allocate
total budget = REG_LAMBDA * M for fair compare with uniform). The substrate-novel claim: PER-SINGULAR-
DIRECTION cleanup-weight allocation lifts recall on real Pythia keys at M=10k where uniform cleanup
collapses to raw=0.018 baseline.

## ARMS (per handoff contract)

CROSS-CELL SANITY RAIL (Fix #28 by-construction-saturation sentinel):
- `ARM_KNN_BASELINE` at M=400 -- must >= 0.90; rank-blind cosine top-1. If KNN drops, KEYS are corrupted
  (not just anisotropic) and cleanup-arm lift is artifact.

MECHANISM ARMS:
- `ARM_UNIFORM_CLEANUP`        -- current substrate behavior; Tikhonov pseudo-inverse with uniform regularizer.
- `ARM_WHITENING`              -- ZCA-whitening of K BEFORE cleanup (rotation-only ablation; drill 1 ceiling
                                  ~+0.020 lift expected).
- `ARM_MIMO_WATERFILL_SVD`     -- the main test; analytic water-filling per SVD of K K^T. No training.
- `ARM_MIMO_WATERFILL_LEARNED` -- gradient-trained per-direction weights via SGD on cross-entropy recall loss
                                  (upper bound on what direction-weighted cleanup can achieve).

DIAGNOSTIC (per handoff item 3):
- `effective_rank` (PR/D) of K_raw + K_whitened + K_waterfill_effective; reports `effrank_lift = eff_wf / eff_raw`.

M-SCALING SWEEP (per handoff item 4):
- Full: M = [400, 10000] (M=400 = KNN sentinel; M=10k = cone-collapse regime).
- Smoke: M = [400, 1000] (smoke MUST trigger UNIFORM collapse at M=1000 vs M=400).
- M=100k tier deferred: dispatch decision after Tier A full reads.

## Configuration (CAPACITY-SENSITIVE -- META_M7 identical smoke/full)

- PROJ_DIM = 768
- C = 256 (codebook label count)
- REG_LAMBDA = 1.0 (uniform-baseline Tikhonov regularizer)
- WHITEN_EPS = 1e-3
- LEARNED_LR = 0.01
- LEARNED_STEPS = 200
- KNN_TOPK = 1
- SIGMA = 0.1 (matches v2 fixture)
- MAX_Q = 1500

## Mode-dependent (only these differ smoke vs full)

| Param      | Smoke           | Full                |
|------------|-----------------|---------------------|
| ENCODER    | pythia-160m     | pythia-2.8b         |
| SEEDS      | [11]            | [11, 13, 19]        |
| M_SWEEP    | [400, 1000]     | [400, 10000]        |
| TRAIN_M    | 600             | 7500                |
| TRAIN_STEPS| 200             | 600                 |

## PRE-REGISTERED BANDS (LOCKED AT MODULE INIT)

`HARD_PASS_MIMO_WATERFILL_RESCUES`:
- `ARM_MIMO_WATERFILL_SVD` recall at M=10k >= **0.50**
- AND lift over `ARM_UNIFORM_CLEANUP` >= **0.20** absolute
- AND effective_rank lift (after / before) >= **1.30x**
- AND std across 3 seeds <= **0.05**
- AND `ARM_KNN_BASELINE` at M=400 >= **0.90**

`HARD_PASS_PARTIAL`:
- Recall lift over `ARM_UNIFORM_CLEANUP` >= **0.15** at M=10k
- AND KNN sentinel preserved
- (some other HARD_PASS conditions not met)

`MIDDLE_BAND`:
- Lift in (**0.05**, **0.15**] at M=10k

`HARD_FAIL_WATERFILL_DOESNT_HELP`:
- Lift <= **0.03** at M=10k
- OR effective_rank lift <= **1.05x** (no rank addition; same failure mode as whitening)
- OR `ARM_KNN_BASELINE` drops below **0.90** (corruption catch)

Q-DISCIPLINE: any arm >= 0.995 flags `[Q-DISCIPLINE: suspect saturation]`; bands favor under-claim.

## Cross-cell rail (load-bearing)

- KNN at M=400 must stay >= 0.90 (Fix #28 by-construction-saturation contamination catch)
- Saturation sentinel: if waterfill_svd hits 1.000 at M=10k, flag Q-DISCIPLINE and consider M=100k adversarial
- Symmetric verify (per [[feedback-negativity-bias]]): also report lift_learned_over_uniform; if SVD < LEARNED
  by > 0.20 the SVD water-filling is suboptimal vs the upper bound (interesting MIDDLE finding)

## Q-discipline + bias-checklist

- BIAS-Q (>=0.995 saturation): handled in compute_verdict
- BIAS-N (verify-referent on verdict-field) -- per_arm metrics returned, NOT verdict_msg framing (Fix #28)
- BIAS-P (anisotropy-hurts-retrieval Mu-Viswanath) -- this cell DIRECTLY tests this; bands set for "REAL rank
  added" (effrank_lift >= 1.30) not just "recall lifted"
- BIAS-O (basis-vs-use-case) -- cleanup is at READOUT; raw K storage is the basis; arms test cleanup not basis
- BIAS-R (BIAS-13 contamination) -- KNN sentinel catches; HARD_FAIL gate triggers if KNN drops below 0.90
- BIAS-S (band calibration regime) -- bands set after reviewing v2 fixture raw=0.018 collapse; HP_ABS=0.50
  represents a CONCRETE substrate-product improvement, not a relative-only claim

## Discipline (per CLAUDE.md + exp_dev memory)

- ASCII only; substrate-only at inference (encoder is setup-time only).
- Per-arm metrics + per-seed checkpoint via `_seed_checkpoint`.
- atexit partial-flush via `write_partial_key` after every seed.
- META_M7 capacity-sensitive dims identical smoke/full.
- D1 roofline probe: skipped (cell is numpy-CPU; matmul-bound; no GPU dispatch).
- Self-test asserts: anisotropic synthetic has eff_rank_raw < 0.50 AND isotropic small-M KNN >= 0.90 AND
  lift is numerically sane.

## Routing decision

- **local_cpu_queue** -- per handoff "Local CPU preferred for Tier A; do NOT route Tier A to GPU queue without
  exp_dev decision."
- Cell is numpy-only matmul-bound at M=10k with d=768; CPU is acceptable (~3-5 hr full wall, well within
  PROT-019 floor for non-_n>=4096 anchors).
- No torch.cuda usage in arms; encoder uses GPU if available (setup-time only).
- M=100k tier deferred: dispatch decision after Tier A full reads land.

## Substrate-product implications (from research note)

If `HARD_PASS_MIMO_WATERFILL_RESCUES`: anisotropy rescue becomes a 1-line cleanup change; ships into
substrate-as-LM revival path immediately. Differentiates substrate from vector-DBs which all use uniform
cleanup.

If `HARD_FAIL`: per-direction cleanup-weight allocation is NOT a chain-grade rescue; Tier A Anchor #1
falsified; route to Tier A Anchor #2 (DG pattern separation) per research drill ranking.

## Estimated wall time

- Smoke: ~3-5 min CPU (pythia-160m encoder + M=400+1000 + 1 seed)
- Full: ~3-5 hr CPU (pythia-2.8b encoder hoist + M=400+10000 + 3 seeds; per handoff "~5 hr")
- Timeout: **18000s** (5 hours) with 1.5x safety margin = computed; PROT-019 floor N/A (no _n suffix)

## Cites

- `notes/research_gap2_anisotropy_5x_drill_2026-06-26.md` (S1 candidate)
- `notes/exp_dev_handoff_research_gap2_anisotropy_5x_drill_2026-06-26.md`
- `data/exp_substrate_anisotropy_rescue_4arm_sweep_v2_calibrated_meter_full/metrics.json` (parent fixture)
- Stanford EE359 MIMO water-filling tutorial
- Mu-Viswanath all-but-the-top anisotropy paper
