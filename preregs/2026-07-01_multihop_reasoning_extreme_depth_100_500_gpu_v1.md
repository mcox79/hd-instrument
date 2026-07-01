# Prereg: multihop_reasoning_extreme_depth_100_500_gpu_v1

**Date**: 2026-07-01
**Author**: exp_dev (spawned by hdi_research)
**Anchor**: `multihop_reasoning_extreme_depth_100_500_gpu_v1`
**Cell**: `experiments/exp_multihop_reasoning_extreme_depth_100_500_gpu_v1.py`
**Routing**: overnight_queue (GPU) - Orchestrator push+queue_add (post-smoke)
**Compute**: N=8192, 3 seeds [7,13,19], 6 arms, 6 Ws per seed

## Substrate-KB prior-work check (2026-07-01)

Q: `bash tools/substrate_query.sh "multihop depth 100 200 500 mechanism death boundary partition oracle"`
  Top-1: `testbed_per_characteristic_phase_diagram_audit_2026-06-26.md::chunk` at cosine 0.292 (below 0.30 novelty threshold).
  Top-2: `phase_diagram_multihop_depth_extension_via_partition_oracle_v1` at cosine 0.290 (predecessor lineage).
  Top-3-4: `depth_ceiling_sweep_20_25_30_v1` at cosine 0.278 (predecessor).

Q: `python tools/predispatch_check.py multihop_reasoning_extreme_depth_100_500_gpu_v1`
  matching landings: 0 (HARD_FAIL=0, HARD_PASS=0, MIDDLE=0)
  matching atoms: 0 -> RECOMMENDATION: PROCEED

**Rediscovery-vs-novel:**
- All cosine hits below 0.30 novelty threshold.
- Predecessor lineage covers d<=100 only (Wave 17 landed d=80/100 as newest phase points).
- d=200/500/1000 with partition-oracle at N=8192, 200 chains, V_C=200 are GENUINELY NEW phase points, extending Wave 17's d=100 endpoint by 2x/5x/10x.
- Rails 15/60/100 reproduce prior chain-grade MEASURED targets from d20-40, d45-60, and Wave 17 respectively.

## Motivation

**Atom 11** (per-step scale-invariance in partition-oracle multihop) predicts per-step 0.9853 -> d=155 death floor (0.10).

**Wave 17 landing** (`multihop_reasoning_extended_depth_80_100_gpu_v1`, 2026-07-01):
- d=80 landed 0.390 (Atom 11 predicted 0.303; +0.087 deviation, HP passed)
- d=100 landed 0.372 (Atom 11 predicted 0.222; +0.150 deviation, HP failed, substrate OUT-PERFORMS)
- Empirical per-step = 0.372^(1/100) = 0.9902 (higher than 0.9853 pin)

**Wave 17 verdict was PARTIAL_LAW_EXTENDS** but the ACTUAL finding is: substrate holds up systematically better than Atom 11's per-step model at deep depth. The empirical per-step is IMPROVING with depth (0.988 at d=80 -> 0.990 at d=100). This suggests either:
- (a) Atom 11 pin at 0.9853 is systematically too low; true per-step is higher.
- (b) Per-step accuracy is depth-DEPENDENT (higher at greater depth per binding-density asymptote).

**This cell (Wave 18) characterizes the actual mechanism-death boundary:**
- d=100 rail reproduces Wave 17 (verifies reproducibility at same regime).
- d=200 tests whether substrate stays past Atom 11 death floor (empirical predicts 0.140).
- d=500 tests whether substrate holds past empirical extrapolation death (~0.007).
- d=1000 tests frontier (capacity M/N=24.4; expected fully saturated).

**Substantive potential:**
- If HP_UNDER_PREDICTS_D200 fires (PART_200 > 0.20): substrate wildly out-performs Atom 11 -> new physics finding + Atom 11 revision required.
- If HP_LIVES_D500 fires (PART_500 > 0.05): substrate holds far past predicted death -> mechanism is fundamentally stronger than empirical extrapolation.
- If HF_MECHANISM_DEATH_D200 fires: mechanism-death boundary is at or before d=200 -> maps actual death floor.

## Arms (6)

| Arm                        | Mechanism                        | Purpose                                          |
|----------------------------|----------------------------------|--------------------------------------------------|
| ARM_PART_ORACLE_15HOP      | partition-oracle per-hop cleanup | rail: reproduce prior 0.808 +/- 0.05             |
| ARM_PART_ORACLE_60HOP      | partition-oracle per-hop cleanup | rail: reproduce prior 0.480 +/- 0.05             |
| ARM_PART_ORACLE_100HOP     | partition-oracle per-hop cleanup | rail: reproduce Wave 17 0.372 +/- 0.05           |
| ARM_PART_ORACLE_200HOP     | partition-oracle per-hop cleanup | NEW (empirical 0.140; atom11 0.052)              |
| ARM_PART_ORACLE_500HOP     | partition-oracle per-hop cleanup | NEW (empirical 0.007; expected DEAD)             |
| ARM_PART_ORACLE_1000HOP    | partition-oracle per-hop cleanup | frontier (capacity-saturated; M/N=24.4)          |

## Pre-reg bands (LOCKED at module init)

### Sanity rails (verdict pre-emption on majority-seed breach)

- `RAIL_15`:  PART_15HOP  in [0.758, 0.858]  (target 0.808; MEASURED@depth_20_to_40_gpu_v1)
- `RAIL_60`:  PART_60HOP  in [0.430, 0.530]  (target 0.480; MEASURED@depth_45_to_60_gpu_v1 Landing 10)
- `RAIL_100`: PART_100HOP in [0.320, 0.420]  (target 0.372; MEASURED@extended_depth_80_100_gpu_v1 Wave 17)

### Novel extreme-depth phase points

- `HP_MECHANISM_LIVES_D200`: PART_200HOP > 0.10 (past Atom 11 death floor 0.052; empirical 0.140 predicts LIVES)
- `HP_ATOM11_UNDER_PREDICTS_D200`: PART_200HOP > 0.20 (dramatic OUT-PERFORM vs Atom 11 0.052)
- `HP_MECHANISM_LIVES_D500`: PART_500HOP > 0.05 (past empirical extrapolation death 0.007)
- `HP_MECHANISM_LIVES_D1000`: PART_1000HOP > 0.05 (frontier)
- `HF_MECHANISM_DEATH_D200`: PART_200HOP < 0.02 (mechanism collapse before empirical)
- `HF_MECHANISM_DEATH_D500`: PART_500HOP < 0.02 (expected outcome per empirical extrapolation)
- `PHASE_CV_MAX = 0.15`: per-arm seed cv cap for HP_ claims (relaxed from 0.10 for M/N >= 4.88 regime)

### Verdicts (LOCKED at module init; 7-way tier)

- `CHAIN_GRADE_ATOM11_REVISION`: rails + HP_UNDER_PREDICTS_D200 fires cross-seed + cv OK
  -> **Substrate fundamentally OUT-PERFORMS Atom 11 per-step model; envelope extends >65% past Atom 11 predicted death floor; requires Atom 11 revision**
- `MECHANISM_LIVES_EXTREME_DEPTH`: rails + HP_LIVES_D500 fires + cv OK
  -> substrate holds far past empirical extrapolation death; new physics finding
- `MECHANISM_LIVES_TO_D200_ONLY`: rails + LIVES_D200 fires but D500 dies + cv OK
  -> death boundary is in [200, 500]; charted for first time
- `MECHANISM_DEATH_BEFORE_D200`: rails + DEATH_D200 fires
  -> mechanism collapse earlier than empirical predicts; Atom 11-adjacent
- `RAIL_BREACH`: any rail majority breach -> setup broken
- `MIDDLE_BAND`: partial passes, cv breach, or missing metrics

### Informational field

`mechanism_death_verdict`:
- "LIVES_TO_D1000" if HP_LIVES_D1000 fires
- "LIVES_TO_D500" if HP_LIVES_D500 fires but D1000 dies
- "ATOM11_REVISION_UNDER_PREDICTS" if HP_UNDER_PREDICTS_D200 fires + rails clean
- "LIVES_TO_D200" if HP_LIVES_D200 fires but D500 dies
- "DEATH_IN_100_200" if HF_DEATH_D200 fires (rails clean)
- "unknown" otherwise

## CRLB / capacity-feasibility (META_RULE_9)

- `crlb_floor_computed`: 0.10 (per_hop_random_guess = 1/PART_SIZE = 1/10)
- `crlb_formula_reference`: `per_hop_random_guess = 1/PART_SIZE = 1/10 = 0.10`
- `discriminator_reachability`: True

**HP_LIVES_D200 reachable?** Predicted band > 0.10. Broken mechanism hits floor 0.10 exactly (out of band). Empirical extrapolation 0.140 (in band). Atom 11 extrapolation 0.052 (below band). Discriminator has clean 3-way signal.

**HP_UNDER_PREDICTS_D200 reachable?** Predicted band > 0.20. Empirical 0.140 does NOT clear this cleanly; fires only if substrate overshoots empirical by ~50%. Would indicate substrate is even stronger than d=100 landing implies.

**HP_LIVES_D500 reachable?** Predicted band > 0.05. Empirical 0.007 out-of-band; atom11 0.0006 out-of-band. Fires only if substrate holds past extrapolation; substantive positive if fires.

**HF_MECHANISM_DEATH_D200 reachable?** Predicted band < 0.02. Empirical 0.140 far above; atom11 0.052 above. Fires only if substrate collapses faster than any prediction; substantive negative.

**HF_MECHANISM_DEATH_D500 reachable?** Predicted band < 0.02. Empirical 0.007 already below this threshold (fires by default per empirical). Expected default outcome unless substrate genuinely holds.

Cell has genuine discriminative signal across all 6-way tiers.

## Discriminator-must-survive-scale (path A: smoke at full-N=8192)

Smoke config: N=8192 (SAME AS FULL), 1 seed, N_CHAINS=25 (25 vs 200 for compute budget), full 6 arms.

Rationale: substrate tolerance scales with N; discriminator (mechanism-death vs alive) at d=200 must be visible at full-N. Reducing to N=2048 changes per-step regime (M/N binding-density changes SNR). Path A (full-N smoke) locks the regime.

Expected smoke wall: 6 W-builds (d15/60/100/200/500/1000), Hebbian ingest scaling with M = 25 * depth = ~1.6x per doubling of depth. On CPU: 25 * 1000 = 25000 bindings for W_d1000 alone; matmul at N=8192 is slow on CPU. Wall estimate: 5-15min CPU smoke.

**Local smoke routes to Bash timeout 10-15min**; if exceeds, escalate to remote via Orchestrator.

## SIX-W discipline (per-depth W ingest)

- `W_d15`:   n_chains=200 * depth=15   = 3000 bindings   (M/N=0.37)
- `W_d60`:   n_chains=200 * depth=60   = 12000 bindings  (M/N=1.46)
- `W_d100`:  n_chains=200 * depth=100  = 20000 bindings  (M/N=2.44)
- `W_d200`:  n_chains=200 * depth=200  = 40000 bindings  (M/N=4.88)
- `W_d500`:  n_chains=200 * depth=500  = 100000 bindings (M/N=12.20)
- `W_d1000`: n_chains=200 * depth=1000 = 200000 bindings (M/N=24.41)

W_d200 through W_d1000 are in extreme over-capacity regime. Binding-density saturation is expected to dominate the mechanism death boundary. If d=500/1000 dies while d=200 holds, that's the capacity-saturation crossing point.

**Chain construction:** For max_depth >= V_C-1 = 199, `make_deep_chains` cannot build distinct-node chains (need > V_C distinct nodes). Cell uses `_make_deep_chains_repeatable` for d=200/500/1000, where nodes may repeat WITHIN a chain (only immediate self-loops avoided). This is the natural regime for very deep chains through a fixed concept space.

## Config

- N=8192 (per Fix #24 GPU-native)
- V_C=200, V_P=10, K_set=20, n_chains=200, N_PARTITIONS=20 (PART_SIZE=10)
- 3 seeds [7, 13, 19] (matching Wave 17 for cross-cell reproducibility of rails)
- `disallow_s=set()` on all six W constructions
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
- Memory budget: 6 Ws @ N=8192 = 6 * 268MB = 1.61GB + E (6.5MB) + R (0.3MB) = ~1.62GB peak; well under 8GB GPU
- Each W freed via `del` + `empty_cache` post-seed

## Timeout estimate

Wave 17 (5 Ws, sum-depths=285): elapsed 247s wall for 3 seeds full.
This cell has 6 Ws with sum-depths = 15+60+100+200+500+1000 = 1875 (6.6x larger).

- Ingest cost scales with M (bindings), so ingest is ~6.6x more.
- Argmax scan cost: 25 chains * (15+60+100+200+500+1000) = 46875 argmax ops (smoke); 375000 (full).
- W_d1000 alone: 200*1000 = 200k bindings ingest -> single largest cost.

Per-seed estimate: 247s * 6.6 = ~1630s per seed. Three seeds: ~4900s (~82 min).

**Timeout: 3600s per USER spawn prompt (if fails, drop d=1000 arm).**

If d=1000 arm exceeds timeout, cell will have written partial metrics via atexit synthesizer at seeds 7, 13; retry sans d=1000 as a follow-up cell.

Given the aggressive timeout vs. estimated 82min wall, timeout=3600s (60min) is tight but feasible on GPU (matmul on GPU is 10-30x faster than the CPU-derived Wave 17 baseline).

## SCHEMA-VET pre-dispatch checklist

- [x] `cardinality_ok`: True (6 arms x 3 seeds = 18 unit measurements; EXPECTED_N_UNITS=3 seeds)
- [x] `arms_differ_verified`: True (each arm uses distinct W_d<D>; different max_depth chains)
- [x] `final_metrics_atomicity`: `write_metrics` helper uses tmp+os.replace pattern
- [x] `except SystemExit: raise` BEFORE `except Exception` ordering: verified in main
- [x] `crlb_floor_computed`: 0.10 (declared in code)
- [x] `discriminator_reachability`: True (verified 5 gates on live-decay branch above)
- [x] `baseline_in_band`: N/A (no baseline arm; three rail arms with prior MEASURED targets)
- [x] `calibration_check`: `default_ok_for_this_regime` (same primitive as Wave 17 CG cells at N=8192)
- [x] `defensive_error_checking`: passed all 4 patterns (start_marker, crash_diagnostic, no bare except, atomic write)
- [x] `HP_SCOPE`: HP_LIVES_D200/UNDER_PREDICTS_D200 -> ARM_200HOP only; HP_LIVES_D500 -> ARM_500HOP only; HP_LIVES_D1000 -> ARM_1000HOP only; rails have separate band gates
- [x] `sweep_alignment_verdict`: N/A (no parameter sweep; discrete depth phase points)
- [x] `discriminating_fraction`: 6/6 = 1.00 (all six depth points are informative)
- [x] `composition_edges`: N/A (single-primitive, no composition)
- [x] `positive_control_arms`: three rail arms reproduce prior chain-grade MEASURED targets AT MATCHED REGIME (N=8192, 200 chains, V_C=200)
- [x] `functional_requirements`: multi-hop chain-following via partition-oracle routed cleanup (CG primitive from d=15 through d=100 per Wave 17)
- [x] `no_silent_except`: verified no `except: pass` or bare-except silent-swallows
- [x] `smoke_fires_discriminator`: smoke at FULL-N=8192; each arm with distinct W; discriminator (rails firing + d=200 in-band) computed in smoke verdict
- [x] `cell_chunked`: False (single-cell; smoke sufficient without chunking per Wave 17 pattern)
- [x] `start_marker_written`: True
- [x] `crash_diagnostic_present`: True
- [x] `heartbeat_present`: False (relies on print-flush + atexit synth; Wave 17 pattern)
- [x] `progress_logging`: `print_flush_true` (all print calls use flush=True)

## Numbers tagging (META_RULE_AC)

- Rail d=15 target 0.808: `MEASURED@data/exp_multihop_reasoning_depth_20_to_40_gpu_v1/metrics.json`
- Rail d=60 target 0.480: `MEASURED@data/exp_multihop_reasoning_depth_45_to_60_gpu_v1/metrics.json`
- Rail d=100 target 0.372: `MEASURED@data/exp_multihop_reasoning_extended_depth_80_100_gpu_v1/metrics.json:per_seed[0].arm_part_oracle_100hop.top1` (Wave 17 landing)
- Atom 11 per-step 0.9853: `CITED@Atom 11 canonical pin`
- Atom 11 d=200 -> 0.052: `THEORETICAL@0.9853^200`
- Atom 11 d=500 -> 0.0006: `THEORETICAL@0.9853^500`
- Empirical per-step 0.9902: `THEORETICAL@Wave17_d100_landing^(1/100) = 0.372^0.01`
- Empirical d=200 -> 0.140: `THEORETICAL@0.9902^200`
- Empirical d=500 -> 0.007: `THEORETICAL@0.9902^500`
- HP_LIVES_D200 threshold 0.10: `HYPOTHESIZED@this_prereg` (past atom11 death floor)
- HP_LIVES_D500 threshold 0.05: `HYPOTHESIZED@this_prereg` (past empirical extrapolation)
- HF_DEATH thresholds 0.02: `HYPOTHESIZED@this_prereg` (well below CRLB)
- CRLB floor 0.10: `THEORETICAL@1/PART_SIZE = 1/10`

## Discipline: DISCRIMINATOR-MUST-SURVIVE-SCALE (path A)

Smoke runs at N=8192 (full production N). Only n_chains reduced to 25 (from 200) for wall budget. Substrate tolerance regime preserved; discriminator (mechanism-death vs alive at d=200) fires in smoke on real full-N binding-density conditions.

## Failure-mode awareness

- RUN_MODE_MISMATCH: cell defaults `run_mode='full'` when neither `--smoke` nor `HDLAB_EXP_NAME=*_smoke*` present
- ANCHOR_NAME_N_SUFFIX_CONFIG_MISMATCH: anchor is `_gpu_v1`; N=8192 in CONFIG_VERSION for cert-trail
- DISPATCH_FAILURE_MISCLASSIFICATION: verify via `queue.json` post-ship
- STRATEGIC_INTERPRETATION_OVER_CLAIM: verdict tiers LOCKED; 3 rails gate the novel extreme-depth claims
- BROKEN_PC_CHECK: d=15/60/100 rails serve as positive control; if all three fail, cell is broken not the extreme-depth result
- TIMEOUT_RISK: d=1000 arm is largest; if timeout hits, atexit synth writes partial metrics for seeds 7 (and possibly 13); follow-up cell can drop d=1000

## Pause / authorization

- Pause flag check: `data/orchestrator_paused.flag` not present at authoring time
- Auto mode active per USER directive; overnight_queue routing per spawn prompt
- USER-declared substantive potential: Atom 11 revision if HP_UNDER_PREDICTS_D200 fires; commercial deployment upside for deeper multi-hop viability

## Expected post-dispatch verify

1. Local smoke run at N=8192, 1 seed, 25 chains -> `data/exp_multihop_reasoning_extreme_depth_100_500_gpu_v1_smoke/metrics.json`
2. Verify smoke fires discriminator (rails at rail_bands, d=200 above 0.02 floor)
3. Commit cell + prereg
4. Route to Orchestrator: overnight_queue with `--timeout 3600` (per USER spawn prompt)
5. Post-ship: verify entry in queue.json + landing_notifier picks up completion
6. Read `data/exp_multihop_reasoning_extreme_depth_100_500_gpu_v1/metrics.json`
7. `tools/peek_arm_metrics.py` per-arm before framing
8. VERIFY `run_mode=full`, size > 5KB, all 3 seeds present
9. hdi_skunkworks landed-VET spawn on completion; report `mechanism_death_verdict`

## Cross-reference

- Prior cells (rails):
  - `data/exp_multihop_reasoning_depth_20_to_40_gpu_v1/metrics.json`: d15=0.810 d30=0.637
  - `data/exp_multihop_reasoning_depth_45_to_60_gpu_v1/metrics.json`: d60=0.480 (Landing 10 CG)
  - `data/exp_multihop_reasoning_extended_depth_80_100_gpu_v1/metrics.json`: d100=0.372 (Wave 17)
- Atom 11 CG per-step scale-invariance: cited in spawn prompt (0.9853 per-step -> d=155 death floor)
- USER directive: characterize actual mechanism-death boundary + test whether substrate genuinely OUT-PERFORMS Atom 11 at extreme depth
