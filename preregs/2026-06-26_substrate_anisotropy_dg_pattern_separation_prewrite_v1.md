# PRE-REG: substrate_anisotropy_dg_pattern_separation_prewrite_v1

**Date:** 2026-06-26
**Author:** exp_dev (cell author; spawn-and-die)
**Cell:** `experiments/exp_substrate_anisotropy_dg_pattern_separation_prewrite_v1.py`
**Anchor:** `substrate_anisotropy_dg_pattern_separation_prewrite_v1`
**Queue routing:** local_cpu_queue (numpy CPU; ~3-5hr wall full per handoff)

## Source documents (AUTHORITATIVE)

- Research drill: `notes/research_gap2_anisotropy_5x_drill_2026-06-26.md` section N1 (Tier A Anchor #2)
- Handoff: `notes/exp_dev_handoff_research_gap2_anisotropy_5x_drill_2026-06-26.md` ANCHOR CANDIDATE #2
- Anchor #1 falsification: `notes/exp_dev_anisotropy_mimo_waterfill_v1_SMOKE_HARD_FAIL_2026-06-26.md`
  (revival angle #3: pivot to N1)
- Prior architectural ranking: `notes/research_anisotropy_drill_2_solutions_brain_substrate_2026-06-25.md`
  (drill 2 ranked DG #1 architecturally)
- v2 fixture (cone-collapse anchor): `data/exp_substrate_anisotropy_rescue_4arm_sweep_v2_calibrated_meter_full/metrics.json`

## Mechanism (one paragraph)

Anchor #1 (MIMO water-filling) attacked the READOUT side and HARD_FAILed because Tikhonov pseudo-
inverse already correctly down-weights cone-null directions. DG pattern separation attacks a
DIFFERENT intervention point: BEFORE writing keys to W, push them through a Dentate-Gyrus-style
pattern separator that orthogonalizes the input cone. The separator composes EXISTING substrate
primitives only -- (a) 6x expansion via fixed-random binary projection (K=5 fan-in per granule, DG
mossy-fiber sparsity), (b) k-WTA at 2% activity via sign-preserving top-K (sparse-bipolar codebook
is already chain-grade at N=2048 per substrate-mine 600K patterns), (c) per-row divisive
normalization (Carandini-Heeger canonical), (d) per-axis homeostatic threshold (Vogels-Sprekeler
E/I balance via EWMA over batch). Substrate-novel claim: PRE-WRITE separation yields dense-KV recall
on real Pythia keys at M=10k WITHOUT requiring partition routing -- the W matrix stores already-
orthogonalized patterns from the start. Brain existence proof: hippocampal DG IS the solved instance
of this problem (+0.10 prior per brain-existence-proof feedback).

**Key difference from Anchor #1:** MIMO = readout-side regularizer redistribution; DG = input-side
decorrelation. If passes, substrate gets a cleaner dense-KV product NOT requiring partition routing.

## ARMS (per handoff contract)

CROSS-CELL SANITY RAIL (Fix #28 by-construction-saturation sentinel):
- `ARM_KNN_BASELINE` at M=400 -- rank-blind cosine top-1 on RAW Pythia keys (NOT through separator).
  Must >= 0.90. If KNN drops, RAW keys are corrupted (not just anisotropic) and any separator-arm
  lift is artifact.

MECHANISM ARMS (intervention-point ladder):
- `ARM_UNIFORM_NO_PRESEP`        -- current substrate; raw Pythia keys + uniform-Tikhonov dense-KV
                                    cleanup. Reproduces Anchor #1's UNIFORM baseline (~0.39 at M=10k
                                    expected per Anchor #1 smoke uniform=0.386 at M=1000).
- `ARM_WHITENING_PRESEP`         -- ZCA-whiten K, then uniform cleanup. Rotation-only ablation;
                                    drill 1 ceiling. Should fail similarly to Anchor #1 whitening
                                    collapse (~0.02 at smoke).
- `ARM_DG_KWTA_PRESEP`           -- k-WTA at 2% in original D (no expansion, no normalization).
                                    Tests whether sparsity ALONE separates the cone.
- `ARM_DG_LATERAL_INHIB_PRESEP`  -- k-WTA + per-row divisive normalization. Tests divisive gain
                                    control on top of sparsity.
- `ARM_DG_FULL`                  -- 6x expansion + k-WTA at 2% + divisive norm + per-axis homeostatic
                                    threshold. Strongest; full DG composition.

DIAGNOSTIC (per handoff item 3):
- `effective_rank` (PR/D) of K BEFORE separator AND AFTER each separator arm
- `off_diag_cos_mass` (average abs cosine over 2000 random pairs) of K raw vs DG_FULL -- a working
  separator should push off-diagonal mass toward zero

M-SCALING SWEEP (per handoff item 4):
- Full: M = [400, 10000] (M=400 = KNN sentinel; M=10k = cone-collapse regime).
- Smoke: M = [400, 1000] (smoke MUST trigger UNIFORM collapse at M=1000 vs M=400).
- M=100k tier deferred: dispatch decision after Tier A full reads.

## Configuration (CAPACITY-SENSITIVE -- META_M7 identical smoke/full)

- PROJ_DIM = 768
- C = 256
- EXPAND_RATIO = 6 (DG mossy-fiber ratio)
- KWTA_FRAC = 0.02 (2% activity per pattern; DG canonical)
- NORM_EPS = 1e-6 (divisive normalization epsilon)
- HOMEO_TAU = 0.1 (EWMA timescale for homeostatic threshold)
- REG_LAMBDA = 1.0 (uniform-baseline Tikhonov regularizer; matches Anchor #1)
- WHITEN_EPS = 1e-3 (matches Anchor #1)
- KNN_TOPK = 1
- SIGMA = 0.1 (matches v2 fixture + Anchor #1)
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

`HARD_PASS_DG_PRESEP_RESCUES`:
- `ARM_DG_FULL` recall at M=10k >= **0.50**
- AND lift over `ARM_UNIFORM_NO_PRESEP` >= **0.20** absolute
- AND effective_rank lift (after / before) >= **1.30x**
- AND std across 3 seeds <= **0.05**
- AND `ARM_KNN_BASELINE` at M=400 >= **0.90**

`HARD_PASS_PARTIAL`:
- Recall lift over `ARM_UNIFORM_NO_PRESEP` >= **0.15** at M=10k
- AND KNN sentinel preserved
- (some of the other HARD_PASS conditions not met)

`MIDDLE_BAND`:
- Lift in (**0.05**, **0.15**] at M=10k

`HARD_FAIL_DG_PRESEP_DOESNT_HELP`:
- Lift <= **0.05** at M=10k
- OR effective_rank lift <= **1.05x** (no rank addition; same failure mode as whitening)
- OR `ARM_KNN_BASELINE` drops below **0.90** (corruption catch on RAW keys)

`SIGN_FLIP_GATE` (smoke critical):
- At smoke, if `lift_dg_full_over_uniform < -0.02` at the larger smoke M, GATE the full dispatch.
  (Don't burn 3-5hr on a known sign-wrong cell -- same discipline that caught MIMO HARD_FAIL.)

Q-DISCIPLINE: any arm >= 0.995 flags `[Q-DISCIPLINE: suspect saturation]`; bands favor under-claim.

## Cross-cell rail (load-bearing)

- KNN at M=400 on RAW keys must stay >= 0.90 (Fix #28 by-construction-saturation contamination catch)
- Saturation sentinel: if dg_full hits 1.000 at M=10k, flag Q-DISCIPLINE and consider M=100k
- Symmetric verify (per [[feedback-negativity-bias]]): report lifts for all 3 DG arms (k-WTA only /
  k-WTA + lateral / full); if k-WTA-only outperforms FULL by > 0.05 the extra DG components are
  ablative-noise (interesting MIDDLE finding)
- Off-diag cosine mass: if DG_FULL doesn't drop off-diag mass vs RAW by at least 0.10, the
  separator is not orthogonalizing -- diagnostic, not gating

## Q-discipline + bias-checklist

- BIAS-Q (>=0.995 saturation): handled in compute_verdict
- BIAS-N (verify-referent on verdict-field) -- per_arm metrics returned, NOT verdict_msg framing (Fix #28)
- BIAS-P (anisotropy-hurts-retrieval Mu-Viswanath) -- this cell DIRECTLY tests; bands set for "REAL
  rank added" (effrank_lift >= 1.30) not just "recall lifted"
- BIAS-O (basis-vs-use-case) -- separator is at INPUT; raw K storage is the basis-before-separator;
  arms test pre-write transform not the basis itself
- BIAS-R (BIAS-13 contamination) -- KNN sentinel on RAW catches contamination; HARD_FAIL gate triggers
  if RAW KNN drops below 0.90
- BIAS-S (band calibration regime) -- bands set after reviewing Anchor #1 smoke (uniform=0.386 at
  M=1000 collapsed from 0.79 at M=400); HP_ABS=0.50 represents a CONCRETE substrate-product
  improvement; HF_LIFT=0.05 matches research-note N1 falsification threshold

## Discipline (per CLAUDE.md + exp_dev memory)

- ASCII only; substrate-only at inference (encoder is setup-time only)
- Per-arm metrics + per-seed checkpoint via `_seed_checkpoint`
- atexit partial-flush via `write_partial_key` after every seed
- META_M7 capacity-sensitive dims identical smoke/full
- D1 roofline probe: skipped (cell is numpy-CPU; matmul-bound; no GPU dispatch)
- Self-test asserts: (a) anisotropic synthetic has eff_rank_raw < 0.50, (b) DG_FULL raises eff_rank
  vs raw, (c) DG_FULL drops off-diag cosine mass, (d) isotropic small-M KNN >= 0.90, (e) k-WTA
  preserves exactly KWTA_FRAC*D nonzeros per row, (f) lifts numerically sane, (g) expander shape
  correct with K=5 fan-in
- Smoke gate FIRST + SIGN_FLIP gate per task spec

## Routing decision

- **local_cpu_queue** -- per handoff "Local CPU preferred for Tier A; do NOT route Tier A to GPU
  queue without exp_dev decision"
- Cell is numpy-only matmul-bound at M=10k with d=768 (expanded to 4608 for DG_FULL); CPU acceptable
  (~3-5 hr full wall)
- No torch.cuda in inference path; encoder uses GPU if available (setup-time only)
- M=100k tier deferred: dispatch decision after Tier A full reads land

## Substrate-product implications (from research note N1)

If `HARD_PASS_DG_PRESEP_RESCUES`: substrate gains a real-data dense-KV product NOT requiring
partition routing. Cleaner positioning than today's "partition routing as workaround". Anisotropy
rescue becomes a deterministic pre-write transform composing existing chain-grade primitives.

If `HARD_FAIL`: DG-style PRE-WRITE separation is NOT a chain-grade rescue; Tier A Anchor #2
falsified. Per research-drill Tier A ranking, route to Anchor #3 (Brenier-map cone-to-ball
pretransform, P=0.40) or Anchor #5 (compressed-sensing coherence-aware fly-LSH, P=0.35).

## Estimated wall time

- Smoke: ~3-5 min CPU (pythia-160m + M=400+1000 + 1 seed)
- Full: ~3-5 hr CPU (pythia-2.8b + M=400+10000 + 3 seeds; per handoff "~6 hr" capped at smoke
  scaling: smoke_wall_s * (10000/1000) * (3/1) * 1.5 safety = ~10800-18000s)
- Timeout: **18000s** (5 hours; matches Anchor #1)
- PROT-019 floor N/A (no _n suffix)

## Cites

- `notes/research_gap2_anisotropy_5x_drill_2026-06-26.md` (N1 candidate)
- `notes/exp_dev_handoff_research_gap2_anisotropy_5x_drill_2026-06-26.md`
- `notes/exp_dev_anisotropy_mimo_waterfill_v1_SMOKE_HARD_FAIL_2026-06-26.md` (Anchor #1 falsification)
- `data/exp_substrate_anisotropy_rescue_4arm_sweep_v2_calibrated_meter_full/metrics.json`
- Marr 1971 hippocampus
- Carandini-Heeger 2012 divisive normalization
- Vogels-Sprekeler inhibitory plasticity
- Mu-Viswanath all-but-the-top anisotropy paper
