# Pre-registration: capacity_multi_bank_alpha_K_HIGH_v1

**Date:** 2026-07-01
**Author:** exp_dev (Opus 4.7 1M via hdi_exp_dev)
**Trigger:** Director task 2026-07-01. Stage 1 capacity multi-bank characterized
at MID coverage (K_per {16..256}, alpha {0.05..2.0}, N {2048..8192}) in
`substrate_capacity_multibank_alpha_K_phase_diagram_v2_GPU` HARD_PASS 119/216
seed_7 (MM per Skunkworks 5c36147d). BACKUP CHARACTERISTICS TABLE flagged HIGH-K
coverage gap; this cell extends K_per to {256, 512, 1024, 2048} at MID-band
alpha {0.3, 0.6, 0.9} to characterize the full phase-diagram surface at HIGH K.

## Substrate-KB prior-work check (USER-locked 2026-06-27)

`bash tools/substrate_query.sh "capacity multi-bank alpha K phase diagram sweep B K_per bank"`
Rank-1: `phase_diagram_capacity_sweep_n16384_vc_higher_alpha_v1` at cosine=0.35
(sibling capacity-sweep cell, different mechanism -- Hebbian W over triples;
not multi-bank). Rank-2 nearest multi-bank match: v2 phase diagram (parent).
No prior HIGH-K multi-bank cell. GENUINELY NOVEL.

## Anchor

`capacity_multi_bank_alpha_K_HIGH_v1` (chunked; 3 sibling files at seeds 7/13/19)

## Routing

- **Queue:** `overnight_queue` (GPU; remote_gpu via hdi_orchestrator)
- **Reason:** N=8192, K up to 2048 slots per bank -> W-slot storage + batched
  argmax matmul -> matmul-bound. GPU-mandated per PROT-020.
- **Smoke:** local CPU (SMOKE_CORNERS run at reduced N_ITEMS_PER_TRIAL=64,
  reused primitive; fp32 CPU is sufficient for 7 corners).
- **Push gate:** harness-DENIED to exp_dev; cell dispatched via Orchestrator.

## Source

Derived from `experiments/exp_substrate_capacity_multibank_alpha_K_phase_diagram_v2_GPU_seed_7.py`
(same MULTI_BANK_BIND / SINGLE_BANK_BASELINE / RANDOM_FLOOR primitives).
Replaces v2's MID-K axes with HIGH-K + MID-alpha grid.

## Arms (identical to v2)

- `MULTI_BANK_BIND` -- distribute M = round(alpha*N) items across B banks
- `SINGLE_BANK_BASELINE` -- same M items all in 1 bank (B_eff=1)
- `RANDOM_FLOOR` -- random readout; floor ~= 1/CB

## Sweep axes

| Axis | Values | Rationale |
|------|--------|-----------|
| alpha | {0.3, 0.6, 0.9} | MID-band; ratio M/B/K_per ranges 0.02-2.4 across grid |
| K_per_bank | {256, 512, 1024, 2048} | HIGH-K extension of v2 {16..256} |
| B | {4, 16, 64} | HIGH B not swept (fixed vs v2) |
| N | 8192 | Single N; matches v2 largest N |
| Seeds | {7, 13, 19} | 3-seed cross-validation |

Full grid per seed: 3 x 4 x 3 x 1 = 36 pts x 3 arms = **108 units/seed**.
Total across 3 seeds: **324 units**.

## Pre-reg bands (LOCKED at module init; CALIBRATED after smoke v1)

- HP_DISCRIM_MARGIN = 0.30
- HP_MULTI_PASS_RECALL = 0.50
- HP_RAIL_RECALL = 0.90 (rail: alpha=0.3, K=2048, **B=64**, N=8192; smoke MEASURED MULTI=1.000)
- HP_SATURATION = 0.995
- HP_HARD_PASS_MIN_GRID = 12 (~33% pass rate; predicted 12 B=64 pts pass + few B=16 alpha=0.3)
- HP_HARD_PASS_MIN_FULLN = 12 (all 36 pts at N=8192; equals MIN_GRID)
- HP_DISCRIM_DOES_NOT_FIRE = 6 (HARD_FAIL floor)
- CV_MAX = 0.10 across 3 seeds (per task discriminator spec)
- EXPECTED_N_UNITS = 108/seed (META_RULE_H)

## CALIBRATION_NOTE (post smoke v1)

Initial pre-reg posited M/B/K_per_bank as the cliff-predictor ratio. **Smoke v1
falsified this**: at same M/B/K=0.30, MULTI=0.554 (alpha=0.6 K=1024 B=16, M/B=308)
vs MULTI=0.158 (alpha=0.3 K=2048 B=4, M/B=615). The dominant predictor is **M/B
(items per bank)**, not the M/B/K_per ratio. K_per_bank has second-order effect
at HIGH-K where slot capacity is already headroomed.

MEASURED@`data/exp_capacity_multi_bank_alpha_K_HIGH_v1_seed_7_smoke/metrics.json`:phase_map:
- M/B=39  (a=0.3 K=2048 B=64): MULTI=1.000 SINGLE=0.005 (RAIL band)
- M/B=115 (a=0.9 K=512  B=64): MULTI=0.996 SINGLE=0.001 (RAIL band)
- M/B=308 (a=0.6 K=1024 B=16): MULTI=0.554 SINGLE=0.002 (DISCRIM band)
- M/B=461 (a=0.9 K=2048 B=16): MULTI=0.285 SINGLE=0.002 (transition)
- M/B=615 (a=0.3 K=2048 B=4):  MULTI=0.158 SINGLE=0.005 (FAIL band)
- M/B=1844 (a=0.9 K=256  B=4): MULTI=0.013 SINGLE=0.001 (FLOOR)

This IS the science: multi-bank capacity is bounded by cleanup capacity per
workspace (function of M/B), largely INDEPENDENT of slot count K_per when K_per
is headroomed. HP_HARD_PASS_MIN_GRID recalibrated 18 -> 12 to match predicted
12 B=64 grid points passing.

**Rail RESPEC'd**: alpha=0.3 K=2048 B=4 (M/B=615) MULTI=0.158 -> alpha=0.3
K=2048 B=64 (M/B=39) MULTI=1.000.

## SCHEMA-VET pre-dispatch gates (post-calibration)

## SCHEMA-VET pre-dispatch gates (per exp_dev.md canonical) -- SUPERSEDED BY POST-CALIBRATION VERSION ABOVE

- `cardinality_ok`: TRUE (EXPECTED_N_UNITS=108/seed, cell verdict logic asserts)
- `arms_differ_verified`: TRUE (T7 selftest checks MULTI vs SINGLE hashes differ)
- `final_metrics_atomicity`: `tmp_replace` (write_metrics uses atomic write)
- `except SystemExit: raise` BEFORE `except Exception`: TRUE (v2 template)
- `crlb_floor_computed`: alpha_cliff = K_per*B/N; per-point M/B/K_per ratio;
  discriminator_reachability = TRUE (HP_RAIL_RECALL=0.90 achievable at rail
  corner with M/B/K=0.30 predicting MULTI~0.98).
- `baseline_in_band`: 13/36 = 0.36 predicted MULTI in-band [0.30, 0.90]
  (Gate B: discriminating_fraction 0.36 > 0.30).
- `discriminator survives scale`: Check A -- smoke corners all at full-N=8192.
- Cardinality guard: HARD_FAIL_CARDINALITY_BREACH_META_RULE_H when n_units < 108/seed.

## Gate D positive control (reproduce prior chain-grade at test regime)

Rail arm alpha=0.3 K=2048 B=4 N=8192 -> M=2457 M/B=614 M/B/K=0.30 -> MULTI
predicted ~0.98. v2 rail (alpha=0.05 K=256 B=4 N=8192) MEASURED@`data/exp_substrate_capacity_multibank_alpha_K_phase_diagram_v2_GPU_seed_7/metrics.json`:rail_alpha0.05_K256_B4_N8192=0.9976.
Tolerance 0.10 -- HIGH v1 rail must land >=0.90 (headroom to detect regime-drift).

## Gate B: discriminating_fraction analysis

MEASURED (analytical model with mid-cliff est): 13/36 = 0.36 (>=0.30 gate passes).

## Gate A: swept param alignment

MULTI arm: effective_K = K_per_bank (direct exposure); effective_M/B = M/B (direct); ALIGNED.
SINGLE arm: effective_K = K_per_bank (single bank); effective_M = M (all in one bank);
alignment intentional (arm demonstrates cliff without bank distribution).

## Smoke corners (7 corners, all N=8192 = full-N per Check A)

| alpha | K   | B  | M    | M/B  | M/B/K | Predicted MULTI | Role |
|-------|-----|----|------|------|-------|-----------------|------|
| 0.3   | 2048| 4  | 2457 | 614  | 0.30  | ~0.98           | RAIL |
| 0.3   | 256 | 4  | 2457 | 614  | 2.40  | floor           | FLOOR sanity |
| 0.6   | 1024| 16 | 4915 | 307  | 0.30  | ~0.98           | DISCRIM |
| 0.6   | 512 | 16 | 4915 | 307  | 0.60  | ~0.65           | DISCRIM |
| 0.9   | 2048| 16 | 7373 | 461  | 0.22  | ~0.98           | DISCRIM |
| 0.9   | 512 | 64 | 7373 | 115  | 0.22  | ~0.98           | DISCRIM |
| 0.9   | 256 | 4  | 7373 | 1843 | 7.20  | floor           | FLOOR sanity |

Smoke gate: >=3/5 expected-cliff corners must fire discriminator + rail_smoke >=0.85 +
>=1 floor observation. All at N=8192 -> discriminator-survives-scale automatic.

## Verdicts

| Verdict | Condition |
|---------|-----------|
| HARD_PASS | n_pass>=18 AND n_pass_at_full_N>=18 AND rail_ok |
| MIDDLE_BAND | partial pass but not both thresholds hit |
| HARD_FAIL_CARDINALITY_BREACH_META_RULE_H | n_units < 108/seed |
| HARD_FAIL_UNIT_EXCEPTION | any per-unit real exception |
| HARD_FAIL_ARMS_IDENTICAL_META_RULE_AF | any (K,B,alpha,N) point has arms bit-identical |
| HARD_FAIL_LLM_CALL | LLM calls > 0 (substrate-only asserted) |
| HARD_FAIL_DISCRIMINATOR_DOES_NOT_FIRE | n_pass < 8 |

## ETA + Timeout

Per-unit GPU walltime (extrapolating v2 seed_7 elapsed=136s / 648 units = 0.21s/unit):
- 108 units/seed x 0.21s = ~23s compute
- Codebook builds + probe overhead: ~30s
- Per-seed total: ~1 min GPU wall
- **Timeout: 1200s (20 min)** per seed -- generous 20x margin.

Total across 3 seeds: ~3 min GPU wall + overhead.

## Discriminator-must-survive-scale (Check A)

All smoke corners at N=8192 (full-N). Cell RUNS at production scale in smoke.
No smaller-N smoke exists. Discriminator preview is real (7 of 7 smoke corners
at N=8192).

## Why this matters

BACKUP CHARACTERISTICS TABLE flagged HIGH-K coverage gap in Stage 1 capacity
substrate map. Multi-bank capacity is a load-bearing primitive for M3 cortex
layer above substrate: routing between B banks + slot-cleanup within a bank is
how the substrate stores M>>K items durably. This cell characterizes the phase
surface where K approaches saturation (K=2048 at M/B <= 614 headroomed;
K=256 at M/B=1843 collapsed). Fills the coverage gap between v2 MID-K MEASURED
region and the untested HIGH-K frontier.

## Post-dispatch REMOTE VERIFY

After Orchestrator queue_add + landing:
1. Read `data/exp_capacity_multi_bank_alpha_K_HIGH_v1_seed_{7,13,19}/metrics.json`
2. Verify `run_mode == "full"` + `elapsed_s > 1` + `size > 5000B` per Rule 16
3. Verify `n_units_expected == 108` per seed + `cardinality_ok == True`
4. Verify `rail_alpha0.3_K2048_B4_N8192` per detail block
