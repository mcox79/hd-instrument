# Prereg: multihop_reasoning_depth_45_to_60_gpu_v1

**Date**: 2026-07-01
**Author**: exp_dev (spawned by hdi_research)
**Anchor**: `multihop_reasoning_depth_45_to_60_gpu_v1`
**Cell**: `experiments/exp_multihop_reasoning_depth_45_to_60_gpu_v1.py`
**Routing**: overnight_queue (GPU) - needs Orchestrator push+queue_add
**Compute**: N=8192, 3 seeds [7,13,19], 5 arms, 5 Ws per seed

## Substrate-KB prior-work check (2026-07-01)

Q1: `bash tools/substrate_query.sh "multihop reasoning depth 45 50 60 half line crossing partition oracle"`
Top hit cosine=0.282 (prereg depth_extension_v1; below novelty threshold 0.30).

Q2: `bash tools/substrate_query.sh "multihop depth ceiling extension beyond 40 substrate cliff"`
Top hit cosine=0.372 (director_cell_H_extended_multihop_consolidation).

**Prior work status:**
- `data/exp_phase_diagram_multihop_depth_extension_via_partition_oracle_v1/metrics.json`:
  MM/CG at PART_15HOP=0.808 MEASURED
- `data/exp_phase_diagram_multihop_depth_ceiling_sweep_20_25_30_v1/metrics.json`:
  CG at PART_15HOP=0.810 / PART_20HOP=0.708 / PART_25HOP=0.673 / PART_30HOP=0.637
- `data/exp_multihop_reasoning_depth_20_to_40_gpu_v1/metrics.json` (LANDED TODAY 10th CG):
  DEPTH_40_STILL_ABOVE_HALF; PART_20HOP=0.708 PART_30HOP=0.637 PART_40HOP=0.533
  per-step empirical ~0.985 across d20-d40

**Rediscovery-vs-novel:** depths 15/20/30 are chain-grade MEASURED prior rails.
**Depths 45 and 60 are GENUINELY NEW** phase points. This cell extends today's
d20-40 CG by two-point-probing the USER-requested 0.50 crossing depth d*.

## Motivation

USER 2026-07-01 spawn prompt: extend today's just-landed d20-40 CG to find the
actual 0.50 crossing depth. USER-declared informational tier: report d* even if
it lands between 45 and 60 (no hard gate on informational). Keep GPU fed.

Today's d20-40 landing measured PART_40HOP=0.533 (per-step ~0.985). Simple
extrapolation:
- d45 at 0.985 per-step: 0.5066 (borderline half; PROBABLY above)
- d60 at 0.985 per-step: 0.4038 (below half; DISCRIMINATOR fires)
- d45 at 0.98  per-step: 0.4029 (below)
- d60 at 0.98  per-step: 0.2976 (below)
- d45 at 0.99  per-step: 0.6362 (above)
- d60 at 0.99  per-step: 0.5472 (above)

Two-point probe (d45, d60) brackets the crossing under all plausible per-step
decay regimes.

## Arms (5)

| Arm                        | Mechanism                        | Purpose                                    |
|----------------------------|----------------------------------|--------------------------------------------|
| ARM_PART_ORACLE_15HOP      | partition-oracle per-hop cleanup | rail: reproduce prior 0.808 +/- 0.05       |
| ARM_PART_ORACLE_20HOP      | partition-oracle per-hop cleanup | rail: reproduce prior 0.708 +/- 0.05       |
| ARM_PART_ORACLE_30HOP      | partition-oracle per-hop cleanup | rail: reproduce prior 0.637 +/- 0.05       |
| ARM_PART_ORACLE_45HOP      | partition-oracle per-hop cleanup | NEW borderline-half phase point            |
| ARM_PART_ORACLE_60HOP      | partition-oracle per-hop cleanup | NEW below-half phase point (crossing)      |

## Pre-reg bands (LOCKED at module init)

### Sanity rails (verdict pre-emption on majority-seed breach)

- `RAIL_15`: PART_15HOP in [0.758, 0.858] else RAIL_BREACH (target 0.808)
- `RAIL_20`: PART_20HOP in [0.658, 0.758] else RAIL_BREACH (target 0.708)
- `RAIL_30`: PART_30HOP in [0.587, 0.687] else RAIL_BREACH (target 0.637)

### Novel phase points (USER-supplied gates)

- `HP_45HOP_STILL_ABOVE_HALF = 0.50` (d45 HP if mean >= 0.50)
- `HP_60HOP_CROSSED         = 0.50` (d60 HP if mean <= 0.50 -> answers USER)
- `HF_MECHANISM_DEATH_45    = 0.10` (d45 mechanism cliff)
- `DISCRIMINATOR_HALF_LINE  = 0.50` (informational)
- `PHASE_CV_MAX             = 0.10` (per-arm seed cv cap for HP)

### Verdicts (LOCKED at module init; 5-way tier)

- `DEPTH_60_CROSSED_HALF`: d45 >= 0.50 AND d60 <= 0.50 (rails pass, cv OK)
  -> USER's crossing question answered; d* in bracket (45, 60]
- `DEPTH_45_ALREADY_CROSSED`: d45 < 0.50 AND d60 <= 0.50 (rails pass, cv OK)
  -> crossing tighter than 45; informational d* < 45; needs finer sweep
- `DEPTH_60_STILL_ABOVE_HALF`: d45 >= 0.50 AND d60 > 0.50 (rails pass, cv OK)
  -> envelope open beyond depth 60; ceiling not found
- `DEPTH_45_MECHANISM_DEATH`: d45 < 0.10
  -> cliff before depth 45 (mechanism failure)
- `RAIL_BREACH`: any rail breach majority of seeds -> setup broken
- `MIDDLE_BAND`: partial passes, cv breach, or non-monotonic (d45<half AND d60>half)

### Informational field (USER-requested)

`crossing_bracket`:
- "45-60"  if DEPTH_60_CROSSED_HALF
- "<45"    if DEPTH_45_ALREADY_CROSSED
- ">60"    if DEPTH_60_STILL_ABOVE_HALF
- "non_monotonic" if d45<half and d60>=half (physically implausible)
- "unknown" if metrics missing

## CRLB / capacity-feasibility (META_RULE_9)

- `crlb_floor_computed`: 0.10 (per_hop_random_guess = 1/PART_SIZE = 1/10)
- `crlb_formula_reference`: `per_hop_random_guess = 1/PART_SIZE = 1/10 = 0.10`
- `discriminator_reachability`: True

**HP_45HOP >= 0.50** reachable iff per-step > 0.5^(1/45) = 0.9847. Empirical
per-step from today's d20-40 landing is 0.985 > 0.9847 (marginally). Below-half
outcome is more probable than above-half at d45. Both sides physically
achievable.

**HP_60HOP <= 0.50** reachable at 0.985 per-step: predicted 0.404 << 0.50.
Below-half outcome very probable at d60.

Cell has genuine discriminative signal across all 5-way tiers.

## Discriminator-must-survive-scale (path B: analytical justification)

Prior d20-40 cell measured PART_40HOP=0.533 at N=8192, 200 chains, V_C=200.
Per-step accuracy at depth 40 = 40sqrt(0.533) = 0.9843 (which matches
independent estimate from d30: (0.637)^(1/30) = 0.9855).

Extrapolating to depth 45 with per-step in [0.98, 0.99]:
- 0.9855^45 = 0.518 (STILL above 0.50)
- 0.9847^45 = 0.500 (AT half line)
- 0.980^45 = 0.403 (BELOW)

Extrapolating to depth 60:
- 0.9855^60 = 0.417 (BELOW)
- 0.9847^60 = 0.396 (BELOW)
- 0.980^60 = 0.298 (BELOW)

d60 is predicted BELOW half across all plausible per-step regimes; d45 is
borderline. This gives clean binary discrimination at d60 with informational
resolution at d45. Discriminator survives full-N scale by extrapolation from
matched-regime prior CG data.

Smoke at N=2048/25-chains over-performs (like prior d20-40 smoke); full run at
N=8192/200-chains inherits the substrate regime where prior CG was measured.

## FIVE-W discipline

Each depth needs a W ingested from chains at THAT max_depth. Five Ws total:

- `W_d15`: n_chains=200 * depth=15 = 3000 bindings
- `W_d20`: n_chains=200 * depth=20 = 4000 bindings
- `W_d30`: n_chains=200 * depth=30 = 6000 bindings
- `W_d45`: n_chains=200 * depth=45 = 9000 bindings (NEW)
- `W_d60`: n_chains=200 * depth=60 = 12000 bindings (NEW)

W_d60 has M=12000 bindings > N=8192 => below-capacity SNR per binding of
N/M=0.683. Per-hop accuracy signal degradation at d60 vs d40 is expected;
empirical d60 top1 tests this. If d60 mechanism-death (< 0.10), the cell logs
DEPTH_45_MECHANISM_DEATH tier as the honest report.

## Config

- N=8192 (per Fix #24 GPU-native)
- V_C=200, V_P=10, K_set=20, n_chains=200, N_PARTITIONS=20 (PART_SIZE=10)
- 3 seeds [7, 13, 19] (USER-specified; distinct from prior d20-40 [11,13,19])
- `disallow_s=set()` on all five W constructions
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
- Memory budget: 5 Ws @ N=8192 = 5 * 268MB = 1340MB + E (6.5MB) + R (0.3MB)
  = ~1350MB peak; well under 8GB GPU (prior d20-40 used 1.69GB with 4 Ws +
  scratch, so ~1.7GB expected for 5-W variant)
- Each W freed via `del` + `empty_cache` post-seed

## Timeout estimate

Prior d20-40 cell elapsed 103s wall (3 seeds, ~34s/seed) on GPU at 4 Ws,
depths 15/20/30/40. This cell has 5 Ws with depths 15/20/30/45/60. Per-seed
cost scales with W-ingest + arm-scan cost:

W-ingest: sum of bindings = 3000+4000+6000+9000+12000 = 34000 (vs 21000 prior; 1.62x)
Arm-scan: sum of chain*depth = 200*(15+20+30+45+60) = 34000 (vs 21000 prior; 1.62x)

Per-seed estimate: 34s * 1.62 = ~55s. Three seeds: ~165s (~3 min). Add safety
buffer for GPU contention:

**Timeout: 3600s (1 hour)** - per USER spawn prompt directive. Per-seed
checkpoint allows mid-run recovery.

## SCHEMA-VET pre-dispatch checklist

- [x] `cardinality_ok`: True (5 arms x 3 seeds = 15 unit measurements; EXPECTED_N_UNITS=3 seeds)
- [x] `arms_differ_verified`: True (each arm uses distinct W_d<D>; different max_depth chains)
- [x] `final_metrics_atomicity`: `write_metrics` helper uses tmp+os.replace pattern
- [x] `except SystemExit: raise` BEFORE `except Exception` ordering: verified in main
- [x] `crlb_floor_computed`: 0.10 (declared in code)
- [x] `discriminator_reachability`: True (both HP_45 above and HP_60 crossed on live-decay branch)
- [x] `baseline_in_band`: N/A (no baseline arm; three rail arms with prior MEASURED targets)
- [x] `calibration_check`: `default_ok_for_this_regime` (same primitive as chain-grade prior cells)
- [x] `defensive_error_checking`: passed all 4 patterns (start_marker, crash_diagnostic, no bare except, atomic write)
- [x] `HP_SCOPE`: HP_45HOP_STILL_ABOVE_HALF applies to ARM_PART_ORACLE_45HOP only; HP_60HOP_CROSSED applies to ARM_PART_ORACLE_60HOP only; rails have separate band gates
- [x] `sweep_alignment_verdict`: N/A (no parameter sweep; discrete depth phase points)
- [x] `discriminating_fraction`: 5/5 = 1.00 (all five depth points are informative)
- [x] `composition_edges`: N/A (single-primitive, no composition)
- [x] `positive_control_arms`: three rail arms reproduce prior chain-grade MEASURED targets AT MATCHED REGIME (N=8192, 200 chains, V_C=200)
- [x] `functional_requirements`: multi-hop chain-following via partition-oracle routed cleanup (chain-grade primitive)
- [x] `no_silent_except`: verified no `except: pass` or bare-except silent-swallows
- [x] `smoke_fires_discriminator`: smoke has 5 depth arms; each with distinct W; discriminator (crossing bracket) computed in smoke verdict

## Failure-mode awareness

- RUN_MODE_MISMATCH: cell defaults `run_mode='full'` when neither `--smoke` nor
  `HDLAB_EXP_NAME=*_smoke*` present; queue_add MUST NOT pass `--self-test`
- ANCHOR_NAME_N_SUFFIX_CONFIG_MISMATCH: anchor is `_gpu_v1`; N=8192 in
  CONFIG_VERSION string for cert-trail
- DISPATCH_FAILURE_MISCLASSIFICATION: verify via `queue.json` post-ship
- STRATEGIC_INTERPRETATION_OVER_CLAIM: verdict tiers LOCKED; 3 rails gate the
  novel depth-45/60 claims; MEASURED-not-HYPOTHESIZED targets
- NON_MONOTONIC_ANOMALY: cell logs "non_monotonic" bracket + MIDDLE_BAND
  verdict if d45<half AND d60>=half (physically implausible; retest signal)

## Pause / authorization

- Pause flag check: `data/orchestrator_paused.flag` not present at authoring time
- Auto mode active per USER directive; overnight_queue routing per USER spawn
- USER-declared informational tier for the 0.50 crossing depth

## Expected post-dispatch verify

1. Orchestrator commits cell + prereg + pushes to origin/main
2. Orchestrator queue_add to overnight_queue with `--timeout 3600`
3. queue_add post-ship verification confirms entry in remote queue.json
4. Landing polling via `data/recent_landings.jsonl` (Fix #25 + #21)
5. Read `data/exp_multihop_reasoning_depth_45_to_60_gpu_v1/metrics.json`
6. `tools/peek_arm_metrics.py` for per-arm verification before framing
7. VERIFY `run_mode=full`, size>5KB, all 3 seeds present
8. hdi_skunkworks landed-VET spawn on completion; report `crossing_bracket`

## Cross-reference

- Prior cell: `preregs/2026-07-01_multihop_reasoning_depth_20_to_40_gpu_v1.md`
- Prior data: `data/exp_multihop_reasoning_depth_20_to_40_gpu_v1/metrics.json`
  (PART_20HOP=0.708 PART_30HOP=0.637 PART_40HOP=0.533; per-step empirical 0.985)
- USER directive: continue the 10th CG of 2026-07-01 into depths 45-60 for
  crossing localization; keep GPU fed
