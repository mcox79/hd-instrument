# PRE-REG: substrate_multihop_phase_diagram_depth_VC_NChains_v4

**Cell files (CHUNKED across 3 sibling seeds; shared engine in `_multihop_phase_diagram_v4_base.py`):**
- `experiments/exp_substrate_multihop_phase_diagram_depth_VC_NChains_v4_seed_7.py`
- `experiments/exp_substrate_multihop_phase_diagram_depth_VC_NChains_v4_seed_13.py`
- `experiments/exp_substrate_multihop_phase_diagram_depth_VC_NChains_v4_seed_19.py`

**Author:** exp_dev (Agent-Teams sub-agent spawned by research lead)
**Date:** 2026-06-28
**Anchor (per seed):** `substrate_multihop_phase_diagram_depth_VC_NChains_v4_seed_<7|13|19>`
**Stage:** Stage-3 (composition / multi-hop)
**Layer:** Layer-1 phase-diagram MAP cell
**Supersedes:** v1 / v3 (test-design issue: v1 cone-formula extrapolated `top1_pred` from nominal V_C, but the partition-routed oracle holds `effective_V_C = V_C / N_PARTITIONS = part_size ~ 800` constant at nominal V_C=16000. Substrate over-performed v3 fail-corner (0.99 vs predicted 0.0) because the model didn't match the mechanism. Secondary: `sample_gpu_util()` silent-except on `torch.cuda.utilization()` swallowed NVML errors -> n_samples=0 -> gpu_util_ok=False.)

## Why v4

Skunkworks v3 atomization (commit `eb7cfc4c`; atom `0bfdac9e73a27ed5`) diagnosed v3 as SMOKE_GATE_FAIL due to test-design issue, NOT substrate failure. v3 substrate did its job; the bands were wrong because they didn't account for partition-routing.

**Two fixes baked into v4:**
1. **Sweep `effective_V_C` directly** (the per-step cleanup search size) instead of nominal `V_C`. Realize via `N_PARTITIONS = 4` fixed and `V_C = 4 * effective_V_C`. Bands derived empirically from v3 data (back-solved p_step per part_size, NOT extrapolated cone-formula).
2. **Fix `sample_gpu_util()` silent-except**. Replace bare `except Exception: return 0.0` with explicit NVML-availability detection: record `gpu_util=NaN + reason="NVML_UNAVAILABLE"` on failure; let runner mark Fix #24 gate FAIL loudly. META_RULE_J no-silent-except.

## What v4 actually sweeps

| axis | values | count |
|------|--------|-------|
| `effective_V_C` (per-step cleanup search size) | {200, 800, 4000, 16000} | 4 |
| `depth` | {5, 10, 15} | 3 |
| `N_chains` (production load on W matrix) | 200 (fixed) | 1 |
| **full grid** | | **12 points / seed** |
| **smoke grid** | 4 corner points | 4 |

`N_PARTITIONS = 4` fixed; `V_C = 4 * effective_V_C`; so V_C ranges {800, 3200, 16000, 64000}. E codebook ~ V_C * N_DIM * 4 bytes; eff_V_C=16000 -> V_C=64000 -> E=2.1GB (fits 6GB GPU budget).

## Arms (per phase point) — 3 arms per spawn directive

1. **SUBSTRATE_BASELINE**: per-step cleanup over FULL V_C codebook (no oracle); upper bound at small V_C; falls off as V_C grows beyond W's effective storage capacity. Per-step search size = V_C.
2. **PARTITION_ORACLE**: goal-conditioning with GROUND-TRUTH target partition; per-step cleanup search over part_size=`effective_V_C` codewords. Per-step search size = effective_V_C.
3. **RANDOM_PARTITION**: per-step cleanup over a RANDOM partition of size `effective_V_C` (random partition assignment; sanity floor). Per-step accuracy bounded above by `1/N_PARTITIONS = 0.25` per step (chance of right partition).

**Arms-must-differ (META_RULE_AF):** SHA-256 over concatenated per-step prediction sequences MUST differ between all 3 arms at EVERY (depth, eff_V_C) point.

**Discriminator (load-bearing):** PARTITION_ORACLE - RANDOM_PARTITION > 0.20 at >= 2 of 4 smoke corners. This proves goal-conditioning (oracle partition info) is what's driving accuracy, not free per-step luck.

## Smoke 4 corner points

| depth | eff_V_C | V_C   | role                                                                              |
|-------|---------|-------|-----------------------------------------------------------------------------------|
|   5   |   200   |   800 | SAT_CORNER (all 3 arms expected to saturate at small effective search space; PART_ORACLE >= 0.95) |
|  15   |   200   |   800 | DISCRIM_LOW_EFFV (PART_ORACLE saturates; SUB_BASELINE saturates; RANDOM_PART tiny) |
|   5   | 16000   | 64000 | DISCRIM_HIGH_EFFV (PART_ORACLE strong; SUB_BASELINE WEAK; RANDOM_PART tiny)        |
|  15   | 16000   | 64000 | CLIFF_CORNER (PART_ORACLE moderate; SUB_BASELINE collapse; RANDOM_PART tiny)       |

## Empirical p_step model (back-solved from v3 smoke; META_RULE_AH; cite source)

Source: `data/exp_substrate_multihop_phase_diagram_depth_VC_NChains_v1_smoke_v3/metrics.json` (4 corners; Skunkworks-verified). Back-solved p_step:

| v3 corner          | part_size (eff_V_C) | top1   | depth | p_step = top1^(1/depth) |
|--------------------|---------------------|--------|-------|--------------------------|
| (5,  200, 50)      | 10                  | 0.940  | 5     | 0.988                    |
| (15, 200, 200)     | 10                  | 0.820  | 15    | 0.987                    |
| (5, 16000, 50)     | 800                 | 1.000  | 5     | 1.000                    |
| (15, 16000, 200)   | 800                 | 0.990  | 15    | 0.9993                   |

**Empirical p_step is roughly INDEPENDENT of eff_V_C in the 10-800 range** (substrate-internal; W storage handles V_C up to 16000 cleanly with N_chains=200). p_step degrades as part_size grows beyond W's effective resolution.

Conservative extrapolation for v4 PARTITION_ORACLE arm bands (margin-deflated):
- `p_step_est(eff_V_C <= 800) = 0.99` (matches v3 directly)
- `p_step_est(eff_V_C = 4000) = 0.98` (extrapolated; moderate margin)
- `p_step_est(eff_V_C = 16000) = 0.95` (extrapolated cautiously; this corner is the cliff)

`top1_pred = p_step_est ** depth` for PARTITION_ORACLE arm.

## Predicted PARTITION_ORACLE arm bands (12 points)

| eff_V_C | p_step | d=5    | d=10   | d=15   |
|---------|--------|--------|--------|--------|
|   200   | 0.99   | 0.951  | 0.904  | 0.860  |
|   800   | 0.99   | 0.951  | 0.904  | 0.860  |
|  4000   | 0.98   | 0.904  | 0.817  | 0.739  |
| 16000   | 0.95   | 0.774  | 0.599  | 0.463  |

HP / HF bands (tracked to top1_pred, clamped above 5x random_floor):
- `top1_pred >= 0.60`: HP=0.50 HF=0.25
- `top1_pred >= 0.30`: HP=0.25 HF=0.10
- `top1_pred >= 0.10`: HP=0.10 HF=0.05
- `top1_pred  < 0.10`: HP=0.05 HF=0.02

Random floor: SUBSTRATE_BASELINE arm picks one of V_C codewords -> `1/V_C`; PARTITION_ORACLE / RANDOM_PARTITION arms pick one of eff_V_C codewords -> `1/effective_V_C`.

## Verdict tiers

- **CHAIN_GRADE_PHASE_MAP_COMPLETE**: >= 50% (6/12) phase points HARD_PASS on PART_ORACLE arm + cliffs identified
- **PARTIAL_PHASE_MAP_SHALLOW**: 30-49% HARD_PASS
- **REGIME_BOUNDS_NARROW**: 10-29% HARD_PASS
- **PHASE_FRONTIER_COLLAPSED**: <10% HARD_PASS
- **SANITY_BREACH**: SAT_CORNER (5, 200) PART_ORACLE < 0.90 OR DISCRIM at >= 1 corner fails (PART_ORACLE - RANDOM_PART < 0.20)

## Sanity rails (ALL must hold or SANITY_BREACH verdict)

- SAT_CORNER (5, 200): PART_ORACLE_recall >= 0.90 (must saturate at easy regime)
- DISCRIM at >= 2 smoke corners: PART_ORACLE - RANDOM_PART > 0.20 (oracle benefit visible)
- ARMS_DISTINCT: SHA-256(SUB_BASELINE_preds) != SHA-256(PART_ORACLE_preds) != SHA-256(RANDOM_PART_preds) at ALL 4 corners
- META_AM: PART_ORACLE >= RANDOM_PART at every point (no inversions; tolerance 0.02)

## Smoke gate (MUST pass before full)

Per META_RULE_J (no silent except) + spawn directive:
- `cardinality_ok`: observed_points == 4 (all 4 corners ran; no silent drops)
- `arm_discriminator_fires`: >= 2 corners have PART_ORACLE - RANDOM_PART > 0.20
- `saturation_observed`: PART_ORACLE at SAT_CORNER >= 0.90
- `cliff_observed`: SUB_BASELINE at CLIFF_CORNER < 0.40 (proves V_C scaling cliff)
- `gpu_util_ok`: GPU util mean >= 50% measured via fixed `sample_gpu_util_safe()` (META_RULE_J; if NVML unavailable, record `gpu_util_pct_mean=NaN + reason='NVML_UNAVAILABLE'` and gate FAILS LOUDLY -- no silent passthrough)
- `arms_differ_sha256`: SHA-256 differs across all 3 arms at all 4 corners (3 distinct hashes per arm)
- `no_silent_exceptions`: zero bare `except: pass` blocks; per-point crashes propagate (META_RULE_AG)

## Cardinality discipline (META_RULE_H / CARDINALITY_OK)

- `EXPECTED_N_POINTS_FULL = 12` (4 eff_V_C * 3 depth)
- `EXPECTED_N_POINTS_SMOKE = 4`
- HARD_FAIL if `len(phase_map) != expected` per seed.

## Chunked seed checkpoint (USER 2026-06-28 + exp_dev §13 + §14)

- 3 sibling cells: `_seed_7.py`, `_seed_13.py`, `_seed_19.py` (thin wrappers)
- Shared engine: `experiments/_multihop_phase_diagram_v4_base.py`
- Each sibling writes its own `data/exp_<anchor>_seed_<N>/metrics.json` via atomic `tmp+os.replace`.
- Per-unit checkpointing via `experiments/_seed_checkpoint.py`.
- Defensive patterns: (1) IMPORT_CRASH sentinel writes metrics.json with verdict=UNKNOWN on import failure; (2) per-point try/except logs + re-raises (NO silent swallow); (3) OUTER_CRASH guard in `main()`; (4) heartbeat via per-point flush.

## Disciplines locked

- META_RULE_AC (band-floor != HARD_PASS; band-floor is MIDDLE_BAND)
- META_RULE_AE (per-arm verification not summary text)
- META_RULE_AF (arms-must-differ SHA-256 at every point; 3 distinct hashes per arm)
- META_RULE_AG (no silent except per point; explicit propagation)
- META_RULE_AH (no hallucinated numbers; bands derived from v3 measured data with citations)
- META_RULE_AN (substrate-empirical scaling; NOT cone-formula extrapolation)
- META_RULE_AP (composition-adapter discipline; partition-routed oracle composed with multihop)
- META_RULE_J (no silent except for instrumentation; gpu_util fails loudly if NVML unavailable)
- Fix #24 (GPU dispatch must actually use GPU; util >= 50% measured loudly)
- Fix #28 (verify per-arm metrics before cross-cell convergence claims)

## Signal-shape audit (per chain-grade-primitives-not-trivially-composable rule)

The partition-routed oracle is composed with multihop substrate. Shape compatibility:
- W matrix (N_DIM x N_DIM) produces state vectors (N_DIM,) at each step.
- Per-step cleanup at PART_ORACLE arm: `E_target_part @ state` -> (part_size,) scores; argmax -> predicted ID.
- `s_pred = target_part * part_size + local_idx` reconstructs full-V_C ID.
- RANDOM_PARTITION arm same shape but searches a random partition.
- SUBSTRATE_BASELINE arm: `E_full @ state` -> (V_C,) scores; argmax over all V_C codewords.
- Compatible shapes; no broadcast surprises; no information leakage between arms (separate code paths; same chains data).

## Output (per-seed metrics.json)

```
{
  "anchor_name": "substrate_multihop_phase_diagram_depth_VC_NChains_v4_seed_<N>",
  "verdict": "<verdict_tier>",
  "verdict_msg": "...",
  "run_mode": "smoke" | "full",
  "seed": <N>,
  "config_version": "ANCHOR=...,N=...,eff_V_Cs=...,N_PARTITIONS=4,...",
  "phase_map": [
    {"depth": 5, "eff_V_C": 200, "V_C": 800, "N_chains": 200,
     "top1_substrate_baseline": <float>, "top1_partition_oracle": <float>,
     "top1_random_partition": <float>,
     "top1_pred_part_oracle": <float>, "HP": <float>, "HF": <float>,
     "random_floor_eff_V_C": <float>, "random_floor_full_V_C": <float>,
     "verdict_tier_per_point": "HARD_PASS|MIDDLE_BAND|HARD_FAIL",
     "discriminator_fires": <bool>,
     "arms_differ_sha256": <bool>,
     "sha256_substrate_baseline": "<hex>",
     "sha256_partition_oracle": "<hex>",
     "sha256_random_partition": "<hex>",
     "elapsed_s_point": <float>},
    ... 12 rows (full) or 4 rows (smoke) ...
  ],
  "smoke_gate": {...} | "extra": {...},
  "gpu_util_pct_mean": <float | NaN>,
  "gpu_util_n_samples": <int>,
  "gpu_util_reason_if_failed": "NVML_UNAVAILABLE" | null,
  "_llm_forward_calls_at_inference": 0,
  "elapsed_s": <float>,
  "summary": "<verdict_msg>"
}
```

## Dispatch plan

1. **Local self-test** (laptop has NO CUDA; verifies formula + arms-differ + scaffold-soundness only; CPU fallback). Per-point timeout for self-test: 5s; total `--timeout` for self-test = 60s.
2. **GPU smoke** to overnight_queue via Orchestrator (Fix #24: util gate needs real GPU). 4 corner points x 1 seed; expected ~3-6 min wall. `--timeout 1800` (30 min budget).
3. **Full dispatch** (post smoke HARD_PASS): 3 chunked seed_{7,13,19} sibling cells to overnight_queue via Orchestrator. 12 points x 1 seed each; expected ~10-30 min wall per seed. `--timeout 18000` (5h budget per spawn directive).

Per `--timeout` rule:
- self-test timeout = 60s
- smoke timeout = 1800s (30 min)
- full timeout = 18000s (5h) per seed sibling

## Routing

- Laptop = D:/AI/hd-instrument (Author here; commit; push-DENIED to me)
- Remote = C:/dev/hd-instrument (reads origin/main); harness-push routes via hd_metrics_sync
- I (exp_dev) file the routing-request for Orchestrator; Orchestrator runs `tools/queue_add.py overnight_queue ...` and pushes via the auto-stage commit.

## Anti-bias checklist (BIAS-13/14/15 + S-band-calibration + N-Q-R)

- BIAS-13 (contamination): chains freshly generated per seed; no leakage between Ws; per-arm separate code paths reading same chains.
- BIAS-14 (regime): bands span 2 orders of magnitude in eff_V_C (200 -> 16000); regime check is the cell.
- BIAS-15 (mismatch): 3 arms use IDENTICAL chains at each point; per-step prediction comparison via SHA-256 hash of preds.
- S-band-calibration: HP / HF tracked to top1_pred per point; NOT a global threshold.
- N-Q-R: predictions from empirical v3 data (cited); no fabricated numbers; Cramer-Rao only approximate (substrate per-step floor is empirical).

## Honest residual uncertainty

- p_step extrapolation to eff_V_C=4000 / 16000 is from v3 data at part_size=10 / 800 only. The eff_V_C=4000 / 16000 points are predictions, not back-solved. If smoke shows PART_ORACLE >> 0.95 at all 4 corners, the discriminator dimension is wrong and bands need re-derivation (would be a v4 -> v5 iteration).
- SUBSTRATE_BASELINE arm at V_C=64000 may collapse below RANDOM_PARTITION arm; that's expected (no oracle benefit; V_C too large for W's resolution). It's NOT a META_AM breach because the META_AM check is PART_ORACLE >= RANDOM_PART (not SUB_BASELINE >= RANDOM_PART).

## Skunkworks v3 atomization references (load-bearing)

- Commit: `eb7cfc4c`
- Atom ID (first 16 chars of SHA-256): `0bfdac9e73a27ed5`
- Note: `notes/skunkworks_batch_parietal_movable_HP_multihop_smoke_fail_2026-06-28.md`
- v3 diagnosis: test-design issue (partition-routed oracle holds effective_V_C constant; bands derived from wrong model); secondary gpu_util silent-except.
