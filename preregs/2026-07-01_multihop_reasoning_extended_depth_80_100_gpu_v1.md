# Prereg: multihop_reasoning_extended_depth_80_100_gpu_v1

**Date**: 2026-07-01
**Author**: exp_dev (spawned by hdi_research)
**Anchor**: `multihop_reasoning_extended_depth_80_100_gpu_v1`
**Cell**: `experiments/exp_multihop_reasoning_extended_depth_80_100_gpu_v1.py`
**Routing**: overnight_queue (GPU) - Orchestrator push+queue_add (post-smoke)
**Compute**: N=8192, 3 seeds [7,13,19], 5 arms, 5 Ws per seed

## Substrate-KB prior-work check (2026-07-01)

Q1: `bash tools/substrate_query.sh "multihop reasoning depth 80 100 extended depth per step accuracy scale invariance"`
  Top-1: `preregs/2026-05-21_wave14yp_multihop_depth_100.md::chunk001` at cosine 0.2861 (below 0.30 novelty threshold).

Q2: `bash tools/substrate_query.sh "multihop chain length 80 100 partition oracle beyond depth 60"`
  Top-1: `Prereg: phase_diagram_multihop_depth_extension_via_partition_oracle_v1` at cosine 0.3223.

Q3: `python tools/predispatch_check.py multihop_reasoning_extended_depth_80_100_gpu_v1`
  matching landings: 0 (HARD_FAIL=0, HARD_PASS=0, MIDDLE=0)
  matching atoms: 0 -> RECOMMENDATION: PROCEED

**Rediscovery-vs-novel:**
- `2026-05-21_wave14yp_multihop_depth_100.md`: a stale exploratory prereg from wave14 series (7 weeks old); not run under partition-oracle chain-routing regime; used different substrate config. NOT a rediscovery.
- `phase_diagram_multihop_depth_extension_via_partition_oracle_v1` (2026-06-26): the ORIGINATING partition-oracle envelope prereg that led to the d15 chain-grade at 0.808. Predecessor lineage, not duplicate.
- Depths 80, 100 with partition-oracle routing at N=8192, 200 chains, V_C=200 are GENUINELY NEW phase points.
- Rails 15/30/60 reproduce prior chain-grade MEASURED targets.

## Motivation

**Atom 11** (per-step scale-invariance in partition-oracle multihop) predicts:
- per-step 0.9853 -> d=80 -> 0.306; d=100 -> 0.227; d=155 -> 0.10 (mechanism death floor)

**Landing 21** (Atom 19 crossing-bracket cell d50-55) narrowed the 0.50 crossing to (50, 55].

**This cell tests Atom 11 expansion criterion (c)** by probing extreme depth d=80 and d=100:
- (a) does per-step scale-invariance survive at 2.7x depth vs largest prior CG (d=60)?
- (b) where does mechanism death actually manifest? Atom 11 predicts d~155; d=80/100 samples the tail.
- If both HP gates pass -> **Atom 11 CG-lift on criterion (c)** + extends multihop envelope by 67%.
- If law BREAKS at extreme depth -> substantive finding that mechanism death is earlier than predicted d=155.

**Empirical per-step from landed data** (computed 2026-07-01):
- d=45 landing: per-step 0.986 (slightly above 0.9853 Atom 11 pin)
- d=60 landing: per-step 0.988
- These bound the per-step estimate; d=80/100 test whether per-step continues to hold at extreme depth (i.e., d=80 predicted from empirical 0.986 -> 0.328).

## Arms (5)

| Arm                        | Mechanism                        | Purpose                                       |
|----------------------------|----------------------------------|-----------------------------------------------|
| ARM_PART_ORACLE_15HOP      | partition-oracle per-hop cleanup | rail: reproduce prior 0.808 +/- 0.05          |
| ARM_PART_ORACLE_30HOP      | partition-oracle per-hop cleanup | rail: reproduce prior 0.637 +/- 0.05          |
| ARM_PART_ORACLE_60HOP      | partition-oracle per-hop cleanup | rail: reproduce prior 0.480 +/- 0.05          |
| ARM_PART_ORACLE_80HOP      | partition-oracle per-hop cleanup | NEW phase point (Atom 11 predicts 0.306)      |
| ARM_PART_ORACLE_100HOP     | partition-oracle per-hop cleanup | NEW phase point (Atom 11 predicts 0.227)      |

## Pre-reg bands (LOCKED at module init)

### Sanity rails (verdict pre-emption on majority-seed breach)

- `RAIL_15`: PART_15HOP in [0.758, 0.858] else RAIL_BREACH (target 0.808)
- `RAIL_30`: PART_30HOP in [0.587, 0.687] else RAIL_BREACH (target 0.637)
- `RAIL_60`: PART_60HOP in [0.430, 0.530] else RAIL_BREACH (target 0.480 from Landing 10)

### Novel phase points (Atom 11 extension criterion c)

- `HP_80HOP_ATOM11_EXTENDS`: |PART_80HOP - 0.303| <= 0.10 (predicted 0.9853^80)
- `HP_100HOP_ATOM11_EXTENDS`: |PART_100HOP - 0.222| <= 0.10 (predicted 0.9853^100)
- `HF_MECHANISM_DEATH_80`: PART_80HOP < 0.10 -> mechanism dies EARLIER than Atom 11's d~155 prediction
- `HF_LAW_BREAKS_80`: |PART_80HOP - 0.303| > 0.15 -> Atom 11 does NOT extend
- `HF_LAW_BREAKS_100`: |PART_100HOP - 0.222| > 0.15 -> Atom 11 does NOT extend
- `PHASE_CV_MAX = 0.10`: per-arm seed cv cap for HP_ claims

### Verdicts (LOCKED at module init; 6-way tier)

- `CHAIN_GRADE_LAW_EXTENDS_TO_EXTREME_DEPTH`: all 3 rails pass + both HP_80/100 pass + cv OK
  -> **Atom 11 CG-lift on criterion (c); envelope extends 67% beyond d=60 Landing 10 CG**
- `PARTIAL_LAW_EXTENDS`: rails pass + one HP passes (either d=80 or d=100 but not both)
  -> partial extension; mechanism weakens between d=80 and d=100
- `LAW_BREAKS_AT_EXTREME_DEPTH`: rails pass + either HP fails outside +/- 0.15 band
  -> Atom 11's per-step formula does NOT extend to extreme depth (substantive negative finding)
- `MECHANISM_DEATH_EARLIER_THAN_155`: PART_80HOP < 0.10 (mechanism cliff before predicted d~155)
  -> substantive negative: mechanism death boundary earlier than Atom 11 predicts
- `RAIL_BREACH`: any rail majority breach -> setup broken
- `MIDDLE_BAND`: partial passes, cv breach, or missing metrics

### Informational field

`atom11_extension_verdict`:
- "CG_LIFT_C" if CHAIN_GRADE_LAW_EXTENDS_TO_EXTREME_DEPTH
- "PARTIAL_80_ONLY" if d=80 passes, d=100 fails
- "PARTIAL_100_ONLY" if d=100 passes, d=80 fails
- "LAW_BREAKS" if LAW_BREAKS_AT_EXTREME_DEPTH
- "EARLY_DEATH" if MECHANISM_DEATH_EARLIER_THAN_155
- "unknown" otherwise

## CRLB / capacity-feasibility (META_RULE_9)

- `crlb_floor_computed`: 0.10 (per_hop_random_guess = 1/PART_SIZE = 1/10)
- `crlb_formula_reference`: `per_hop_random_guess = 1/PART_SIZE = 1/10 = 0.10`
- `discriminator_reachability`: True (verified below)

**HP_80HOP_ATOM11_EXTENDS reachable?** Predicted target 0.303. Broken mechanism hits floor 0.10 (0.20 away, > 0.10 band). Fully working at 0.986 per-step gives 0.325 (well within band). Discriminator has genuine 3-way signal: pass / weak / broken.

**HP_100HOP_ATOM11_EXTENDS reachable?** Predicted target 0.222. Broken hits 0.10 (0.12 away, slightly outside 0.10 band). Working at 0.986 gives 0.247 (within band). Discriminator active.

**HF_MECHANISM_DEATH_80 reachable?** Requires PART_80HOP < 0.10, which is the CRLB floor exactly. Achievable only if mechanism completely broken (worse than random). Realistically this fires if per-step drops below 0.972 -> at 0.972^80 = 0.101.

**HF_LAW_BREAKS_80 reachable?** Predicted 0.303 +/- 0.15 band is [0.153, 0.453]. Real per-step 0.983 gives 0.256 (in band). Per-step 0.97 gives 0.088 (out of band, fires HF). Per-step 0.99 gives 0.448 (in band). Reachability: signal only when per-step degrades below 0.975 or exceeds 0.994 at d=80.

Cell has genuine discriminative signal across all 6-way tiers.

## Discriminator-must-survive-scale (path A: smoke at full-N=8192)

Smoke config: N=8192 (SAME AS FULL), 1 seed, N_CHAINS=25 (25 vs 200 for compute budget), full 5 arms.

Rationale: substrate tolerance scales with N; discriminator at 0.10 (mechanism death) vs 0.303 (Atom 11 prediction) at d=80 must be visible at full-N. Reducing to N=2048 changes per-step regime (M/N binding-density changes SNR). Path A (full-N smoke) locks the regime.

Expected smoke arm timings (from prior d45-60 cell): ~10s per W-ingest at N=8192, 25 chains, +5s argmax scan. Five Ws: 50s + 25s = 75s smoke wall. Full 3-seed run: 200 chains x 5 Ws with 5-arm scans -> extrapolate from d45-60 (~4 min per seed at 200 chains, 5 Ws) -> ~5 min per seed with longer chains -> ~15-25 min total wall.

## FIVE-W discipline (per-depth W ingest)

- `W_d15`: n_chains=200 * depth=15 = 3000 bindings
- `W_d30`: n_chains=200 * depth=30 = 6000 bindings
- `W_d60`: n_chains=200 * depth=60 = 12000 bindings (M/N = 1.46)
- `W_d80`: n_chains=200 * depth=80 = 16000 bindings (M/N = 1.95)
- `W_d100`: n_chains=200 * depth=100 = 20000 bindings (M/N = 2.44)

W_d100 has M=20000 bindings > N=8192 -> M/N = 2.44 (below-capacity SNR).
Per-hop accuracy signal degradation at d100 vs d60 is expected due to binding-density
increase. If d=100 hits floor 0.10 with rails clean, that's `MECHANISM_DEATH_EARLIER_THAN_155`
tier: substantive negative finding that binding-density hits saturation earlier than
Atom 11's per-step-invariance formula predicts.

## Config

- N=8192 (per Fix #24 GPU-native)
- V_C=200, V_P=10, K_set=20, n_chains=200, N_PARTITIONS=20 (PART_SIZE=10)
- 3 seeds [7, 13, 19] (matching d45-60 for cross-cell reproducibility of rails)
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
  = ~1.35GB peak; well under 8GB GPU (extrapolation from d45-60 landing at 1.7GB)
- Each W freed via `del` + `empty_cache` post-seed

## Timeout estimate

Prior d45-60 cell (5 Ws, depths 15/20/30/45/60): elapsed 165s wall (3 seeds, 5 Ws with sum-depths=170).

This cell has 5 Ws with sum-depths=15+30+60+80+100=285 (1.68x). Per-seed estimate: 55s * 1.68 = ~92s. Three seeds: ~276s (~5 min). Add safety buffer for GPU contention:

**Timeout: 3600s (1 hour)** - matches prior d45-60 timeout budget. Per-seed checkpoint allows mid-run recovery.

## SCHEMA-VET pre-dispatch checklist

- [x] `cardinality_ok`: True (5 arms x 3 seeds = 15 unit measurements; EXPECTED_N_UNITS=3 seeds)
- [x] `arms_differ_verified`: True (each arm uses distinct W_d<D>; different max_depth chains)
- [x] `final_metrics_atomicity`: `write_metrics` helper uses tmp+os.replace pattern
- [x] `except SystemExit: raise` BEFORE `except Exception` ordering: verified in main
- [x] `crlb_floor_computed`: 0.10 (declared in code)
- [x] `discriminator_reachability`: True (verified 3 gates on live-decay branch above)
- [x] `baseline_in_band`: N/A (no baseline arm; three rail arms with prior MEASURED targets from d20-40, d45-60, d50-55 landings)
- [x] `calibration_check`: `default_ok_for_this_regime` (same primitive as chain-grade prior cells at N=8192)
- [x] `defensive_error_checking`: passed all 4 patterns (start_marker, crash_diagnostic, no bare except, atomic write)
- [x] `HP_SCOPE`: HP_80HOP_ATOM11_EXTENDS applies to ARM_PART_ORACLE_80HOP only; HP_100HOP_ATOM11_EXTENDS applies to ARM_PART_ORACLE_100HOP only; rails have separate band gates
- [x] `sweep_alignment_verdict`: N/A (no parameter sweep; discrete depth phase points)
- [x] `discriminating_fraction`: 5/5 = 1.00 (all five depth points are informative)
- [x] `composition_edges`: N/A (single-primitive, no composition)
- [x] `positive_control_arms`: three rail arms reproduce prior chain-grade MEASURED targets AT MATCHED REGIME (N=8192, 200 chains, V_C=200)
- [x] `functional_requirements`: multi-hop chain-following via partition-oracle routed cleanup (chain-grade primitive from d15 through d60)
- [x] `no_silent_except`: verified no `except: pass` or bare-except silent-swallows
- [x] `smoke_fires_discriminator`: smoke at FULL-N=8192; each arm with distinct W; discriminator (Atom 11 extends) computed in smoke verdict

## Discipline: DISCRIMINATOR-MUST-SURVIVE-SCALE (path A)

Smoke runs at N=8192 (full production N, not down-sized). Only n_chains reduced to 25 (from 200) to keep smoke wall < 120s. Substrate tolerance regime preserved; discriminator (Atom 11 extension check) fires in smoke on real full-N binding-density conditions.

## Failure-mode awareness

- RUN_MODE_MISMATCH: cell defaults `run_mode='full'` when neither `--smoke` nor `HDLAB_EXP_NAME=*_smoke*` present; queue_add MUST NOT pass `--self-test`
- ANCHOR_NAME_N_SUFFIX_CONFIG_MISMATCH: anchor is `_gpu_v1`; N=8192 in CONFIG_VERSION for cert-trail
- DISPATCH_FAILURE_MISCLASSIFICATION: verify via `queue.json` post-ship
- STRATEGIC_INTERPRETATION_OVER_CLAIM: verdict tiers LOCKED; 3 rails gate the novel d=80/100 claims; MEASURED-not-HYPOTHESIZED targets from empirical per-step
- BROKEN_PC_CHECK: d=15/30/60 rails serve as positive control; if all three fail, cell is broken not the extreme-depth result

## Pause / authorization

- Pause flag check: `data/orchestrator_paused.flag` not present at authoring time
- Auto mode active per USER directive; overnight_queue routing per spawn prompt
- USER-declared substantive potential: CG-lift on Atom 11 criterion (c) if HP passes

## Expected post-dispatch verify

1. Local smoke run at N=8192, 1 seed, 25 chains -> `data/exp_multihop_reasoning_extended_depth_80_100_gpu_v1_smoke/metrics.json`
2. Verify smoke fires discriminator (mechanism operates at all 5 depths, top1 > CRLB floor 0.10)
3. Commit cell + prereg
4. Route to Orchestrator: overnight_queue with `--timeout 3600` after Wave 14 completes
5. Post-ship: verify entry in queue.json + Fix #25 landing notifier picks up completion
6. Read `data/exp_multihop_reasoning_extended_depth_80_100_gpu_v1/metrics.json`
7. `tools/peek_arm_metrics.py` per-arm before framing
8. VERIFY `run_mode=full`, size > 5KB, all 3 seeds present
9. hdi_skunkworks landed-VET spawn on completion; report `atom11_extension_verdict`

## Cross-reference

- Prior cells (rails):
  - `data/exp_multihop_reasoning_depth_20_to_40_gpu_v1/metrics.json`: d15=0.810 d20=0.708 d30=0.637 d40=0.533
  - `data/exp_multihop_reasoning_depth_45_to_60_gpu_v1/metrics.json`: d15=0.798 d30=0.633 d60=0.480 (per Landing 10)
  - `data/exp_multihop_reasoning_depth_50_55_crossing_bracket_gpu_v1/metrics.json`: d15=0.798 d30=0.625 d50=0.502 d55=0.455
- Atom 11 CG per-step scale-invariance: cited in spawn prompt (0.9853 per-step -> d=155 death floor)
- Landing 21 (Atom 19 crossing bracket): d50-55 CG confirms crossing in (50, 55]
- USER directive: extend to d=80 / d=100 as Atom 11 expansion criterion (c) + explore frontier of scale-invariance
