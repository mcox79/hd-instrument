# Prereg: multihop_reasoning_depth_50_55_crossing_bracket_gpu_v1

**Date**: 2026-07-01
**Author**: exp_dev (spawned by hdi_research per Skunkworks revival criterion)
**Anchor**: `multihop_reasoning_depth_50_55_crossing_bracket_gpu_v1`
**Cell**: `experiments/exp_multihop_reasoning_depth_50_55_crossing_bracket_gpu_v1.py`
**Routing**: overnight_queue (GPU) - needs Orchestrator push+queue_add
**Compute**: N=8192, 3 seeds [7,13,19], 4 arms, 4 Ws per seed

## Substrate-KB prior-work check (2026-07-01)

Q1: `bash tools/substrate_query.sh "multihop depth 50 55 finer crossing bracket partition oracle"`
Top hit cosine=0.331 (prereg depth_extension_v1); below strong-novelty threshold.

Q2: `bash tools/substrate_query.sh "multihop reasoning depth 48 50 half line crossing precise"`
Top hit cosine=0.314 (generic reasoning atom); no prior d50 / d55 work.

**Prior work status:**
- `data/exp_multihop_reasoning_depth_45_to_60_gpu_v1/metrics.json` (LANDED 2026-07-01 13th CG):
  - DEPTH_60_CROSSED_HALF at bracket (45, 60]
  - MEASURED@disk: PART_15HOP=0.7983, PART_20HOP=0.7017, PART_30HOP=0.6333,
    PART_45HOP=0.5317 (above half), PART_60HOP=0.4800 (below half)
- Empirical per-step from d45/d60: 0.9861 / 0.9878 (avg 0.9870)
- Solved crossing d* at empirical per-step: **d\*=52.77 (bracket 45-60 midpoint region)**

**Rediscovery-vs-novel:** depths 15/30 are chain-grade MEASURED prior rails;
depths 45 and 60 are today's MEASURED bracket endpoints. **Depths 50 and 55 are
GENUINELY NEW** finer-bracket phase points. This cell answers Skunkworks
revival criterion: narrow the bracket from (45,60] to (50,55], (45,50], or
(55,60] depending on outcomes.

## Motivation

Skunkworks-declared revival criterion after 13th CG of 2026-07-01: add d=50 and
d=55 phase points to nail down the exact 0.50 crossing depth. Predicted d\*=48-50
per USER spawn framing; my computed d\*=52.77 from LANDED d45/d60 empirical
per-step is on the higher end but consistent within noise. Two-point probe at
d50 and d55 narrows the bracket to at most width 10.

Predictions from LANDED d45/d60 empirical (per-step 0.9870 avg):
- d50 predicted 0.5185 (**marginally above** 0.50)
- d55 predicted 0.4856 (**marginally below** 0.50)
- => most likely outcome: **crossing_bracket=(50, 55]** with width 5

Alternative scenarios:
- If per-step drops to 0.98: d50=0.3642 (below), d55=0.3292 (below) => bracket <=50
- If per-step stays at 0.99: d50=0.6050 (above), d55=0.5754 (above) => bracket >55
- Median-plausible: bracket (50,55]

## Arms (4)

| Arm                        | Mechanism                        | Purpose                                    |
|----------------------------|----------------------------------|--------------------------------------------|
| ARM_PART_ORACLE_15HOP      | partition-oracle per-hop cleanup | rail: reproduce prior 0.808 +/- 0.05       |
| ARM_PART_ORACLE_30HOP      | partition-oracle per-hop cleanup | rail: reproduce prior 0.637 +/- 0.05       |
| ARM_PART_ORACLE_50HOP      | partition-oracle per-hop cleanup | NEW borderline-half phase point (predicted 0.518) |
| ARM_PART_ORACLE_55HOP      | partition-oracle per-hop cleanup | NEW borderline-half phase point (predicted 0.486) |

Rails d15, d30 chosen for anchor to prior CG rails; d20 dropped from prior
5-arm design to keep cell lean (d30 rail is stricter test of routing chain
than d20).

## Pre-reg bands (LOCKED at module init)

### Sanity rails (verdict pre-emption on majority-seed breach)

- `RAIL_15`: PART_15HOP in [0.758, 0.858] else RAIL_BREACH (target 0.808)
- `RAIL_30`: PART_30HOP in [0.587, 0.687] else RAIL_BREACH (target 0.637)

### Novel phase points (Skunkworks-supplied gates; extend USER 0.50 crossing)

- `HP_50HOP_ABOVE_HALF = 0.50` (d50 informational: above half if mean >= 0.50)
- `HP_55HOP_ABOVE_HALF = 0.50` (d55 informational: above half if mean >= 0.50)
- `HF_MECHANISM_DEATH  = 0.10` (any depth mechanism cliff)
- `DISCRIMINATOR_HALF_LINE = 0.50` (informational; extends USER crossing q)
- `PHASE_CV_MAX = 0.10` (per-arm seed cv cap for HP claim)

### Verdicts (LOCKED at module init; 4-way + informational tiers per USER declaration)

USER declared informational tier for 0.50 crossing depth in prior cell; same
convention here: report the narrowed bracket even without a hard-gate PASS/FAIL.

- `CROSSING_BRACKET_50_55`: d50 >= 0.50 AND d55 < 0.50 (rails pass, cv OK)
  -> crossing narrowed to (50, 55]; bracket width 5
- `CROSSING_BRACKET_45_50`: d50 < 0.50 AND d55 < 0.50 (rails pass, cv OK)
  -> crossing narrowed to (45, 50]; bracket width 5
- `CROSSING_BRACKET_55_60`: d50 >= 0.50 AND d55 >= 0.50 (rails pass, cv OK)
  -> crossing narrowed to (55, 60]; bracket width 5
- `MECHANISM_DEATH`: any depth < 0.10 -> mechanism failure
- `RAIL_BREACH`: any rail breach majority of seeds -> setup broken
- `MIDDLE_BAND`: non-monotonic (d50 < half AND d55 >= half physically implausible),
  or cv breach

### Informational field (extends prior cell's crossing_bracket convention)

`crossing_bracket_narrowed`:
- "(50, 55]"  if CROSSING_BRACKET_50_55 (predicted most likely)
- "(45, 50]"  if CROSSING_BRACKET_45_50
- "(55, 60]"  if CROSSING_BRACKET_55_60
- "non_monotonic" if d50<half AND d55>=half
- "unknown" if metrics missing

## CRLB / capacity-feasibility (META_RULE_9)

- `crlb_floor_computed`: 0.10 (per_hop_random_guess = 1/PART_SIZE = 1/10)
- `crlb_formula_reference`: `per_hop_random_guess = 1/PART_SIZE = 1/10 = 0.10`
- `discriminator_reachability`: True

**HP_50HOP >= 0.50** reachable iff per-step > 0.5^(1/50) = 0.9862.
Empirical from LANDED d45/d60 avg: 0.9870 > 0.9862 => reachable (marginally).

**HP_55HOP >= 0.50** reachable iff per-step > 0.5^(1/55) = 0.9875.
Empirical avg 0.9870 < 0.9875 => below-half MORE LIKELY at d55.

Both gates on live-decay branch; genuine discriminative signal across all
three narrowed-bracket tiers.

## Discriminator-must-survive-scale (path B: analytical justification)

LANDED prior d45-60 cell measured PART_45HOP=0.5317 (above half) and
PART_60HOP=0.4800 (below half) at MATCHED regime (N=8192, 200 chains, V_C=200).
d50 and d55 interpolate between these two MEASURED points; both are within
+/- 0.05 of half-line under empirical per-step. Discriminator survives
full-N scale by direct interpolation from matched-regime LANDED CG data.

Smoke at N=2048/25-chains over-performs (like prior d45-60 smoke); full run at
N=8192/200-chains inherits substrate regime where prior CG was measured.

## FOUR-W discipline

Each depth needs a W ingested from chains at THAT max_depth. Four Ws total:

- `W_d15`: n_chains=200 * depth=15 = 3000 bindings
- `W_d30`: n_chains=200 * depth=30 = 6000 bindings
- `W_d50`: n_chains=200 * depth=50 = 10000 bindings (NEW)
- `W_d55`: n_chains=200 * depth=55 = 11000 bindings (NEW)

W_d55 has M=11000 > N=8192 (SNR per binding N/M=0.744; below-capacity).
Per-hop accuracy signal degradation at d55 vs d45 expected; prior d60 with
M=12000 SNR=0.683 still measured 0.4800 top1 => d55 M=11000 fully feasible.

## Config

- N=8192 (per Fix #24 GPU-native)
- V_C=200, V_P=10, K_set=20, n_chains=200, N_PARTITIONS=20 (PART_SIZE=10)
- 3 seeds [7, 13, 19] (matches prior d45-60 cell for cross-seed comparison)
- `disallow_s=set()` on all four W constructions
- ENCODER_PROVENANCE="SUBSTRATE_NATIVE"
- Zero LLM calls at inference (asserted via `_LLM_CALL_COUNTER`)
- Per-seed checkpoint (PROT-021) via `experiments/_seed_checkpoint.py`
- atexit synthesizer for resume
- Start-marker + crash-diagnostic (defensive per META_RULE Section 13)

## GPU usage (Fix #24)

- torch.cuda active: E, R, all Ws on device
- Batched outer-product Hebbian ingest: `V.T @ K` matmul per batch
- Argmax cleanup: `torch.argmax(E_part @ (W @ key))` on device
- Encoder hoisted per seed (E, R built once)
- Memory budget: 4 Ws @ N=8192 = 4 * 268MB = 1072MB + E (6.5MB) + R (0.3MB)
  = ~1.08GB peak; well under 8GB GPU (prior 5-W d45-60 used ~1.7GB)
- Each W freed via `del` + `empty_cache` post-seed

## Timeout estimate

Prior d45-60 cell elapsed 146.8s wall (3 seeds, ~49s/seed) on GPU with 5 Ws
depths 15/20/30/45/60. This cell has 4 Ws depths 15/30/50/55.

W-ingest: sum bindings = 3000+6000+10000+11000 = 30000 (vs 34000 prior; 0.88x)
Arm-scan: sum chain*depth = 200*(15+30+50+55) = 30000 (vs 34000 prior; 0.88x)

Per-seed estimate: 49s * 0.88 = ~43s. Three seeds: ~130s (~2 min).

**Timeout: 3600s (1 hour)** - matches prior d45-60 for consistency. Per-seed
checkpoint allows mid-run recovery.

## SCHEMA-VET pre-dispatch checklist

- [x] `cardinality_ok`: True (4 arms x 3 seeds = 12 unit measurements; EXPECTED_N_UNITS=3 seeds)
- [x] `arms_differ_verified`: True (each arm uses distinct W_d<D>; different max_depth chains)
- [x] `final_metrics_atomicity`: `write_metrics` helper uses tmp+os.replace pattern
- [x] `except SystemExit: raise` BEFORE `except Exception` ordering: verified in main
- [x] `crlb_floor_computed`: 0.10 (declared in code)
- [x] `discriminator_reachability`: True (both HP_50 and HP_55 on live-decay branch)
- [x] `baseline_in_band`: N/A (no baseline arm; two rail arms with prior MEASURED targets + two novel phase points)
- [x] `calibration_check`: `default_ok_for_this_regime` (same primitive as chain-grade prior cells)
- [x] `defensive_error_checking`: passed all 4 patterns (start_marker, crash_diagnostic, no bare except, atomic write)
- [x] `HP_SCOPE`: HP_50HOP_ABOVE_HALF applies to ARM_PART_ORACLE_50HOP only; HP_55HOP_ABOVE_HALF applies to ARM_PART_ORACLE_55HOP only; rails have separate band gates
- [x] `sweep_alignment_verdict`: N/A (no parameter sweep; discrete depth phase points)
- [x] `discriminating_fraction`: 4/4 = 1.00 (all four depth points informative)
- [x] `composition_edges`: N/A (single-primitive, no composition)
- [x] `positive_control_arms`: two rail arms reproduce prior chain-grade MEASURED targets AT MATCHED REGIME (N=8192, 200 chains, V_C=200)
- [x] `functional_requirements`: multi-hop chain-following via partition-oracle routed cleanup (chain-grade primitive)
- [x] `no_silent_except`: verified no `except: pass` or bare-except silent-swallows
- [x] `smoke_fires_discriminator`: smoke has 4 depth arms; each with distinct W; discriminator (crossing bracket narrowing) computed in smoke verdict

## Failure-mode awareness

- RUN_MODE_MISMATCH: cell defaults `run_mode='full'` when neither `--smoke` nor
  `HDLAB_EXP_NAME=*_smoke*` present; queue_add MUST NOT pass `--self-test`
- ANCHOR_NAME_N_SUFFIX_CONFIG_MISMATCH: anchor is `_gpu_v1`; N=8192 in
  CONFIG_VERSION string for cert-trail
- DISPATCH_FAILURE_MISCLASSIFICATION: verify via `queue.json` post-ship
- STRATEGIC_INTERPRETATION_OVER_CLAIM: crossing bracket is informational per
  USER declaration; 2 rails gate the novel depth-50/55 claims
- NON_MONOTONIC_ANOMALY: cell logs "non_monotonic" bracket + MIDDLE_BAND
  verdict if d50<half AND d55>=half (physically implausible; retest signal)

## Pause / authorization

- Pause flag check: `data/orchestrator_paused.flag` not present at authoring time
- Auto mode active per USER directive; overnight_queue routing per spawn prompt
- Skunkworks revival criterion after 13th CG of 2026-07-01

## Expected post-dispatch verify

1. Orchestrator commits cell + prereg + pushes to origin/main
2. Orchestrator queue_add to overnight_queue with `--timeout 3600`
3. queue_add post-ship verification confirms entry in remote queue.json
4. Landing polling via `data/recent_landings.jsonl` (Fix #25 + #21)
5. Read `data/exp_multihop_reasoning_depth_50_55_crossing_bracket_gpu_v1/metrics.json`
6. `tools/peek_arm_metrics.py` for per-arm verification before framing
7. VERIFY `run_mode=full`, size>5KB, all 3 seeds present
8. hdi_skunkworks landed-VET spawn on completion; report `crossing_bracket_narrowed`

## Cross-reference

- Prior cell (10th CG): `preregs/2026-07-01_multihop_reasoning_depth_20_to_40_gpu_v1.md`
  (PART_20/30/40=0.708/0.637/0.533; per-step ~0.985)
- Prior cell (13th CG): `preregs/2026-07-01_multihop_reasoning_depth_45_to_60_gpu_v1.md`
  (PART_45=0.5317 above; PART_60=0.4800 below; crossing_bracket=(45,60])
- Prior data: `data/exp_multihop_reasoning_depth_45_to_60_gpu_v1/metrics.json`
- Per-step scale-invariance finding: 0.985 across d15->d60 (empirical avg)
- Skunkworks revival criterion: narrow crossing bracket to (50,55] / (45,50] / (55,60]
