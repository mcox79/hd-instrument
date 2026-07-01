# Prereg: multihop_reasoning_depth_20_to_40_gpu_v1

**Date**: 2026-07-01
**Author**: exp_dev (spawned by hdi_research)
**Anchor**: `multihop_reasoning_depth_20_to_40_gpu_v1`
**Cell**: `experiments/exp_multihop_reasoning_depth_20_to_40_gpu_v1.py`
**Routing**: overnight_queue (GPU) — needs Orchestrator push+queue_add
**Compute**: N=8192, 3 seeds [11,13,19], 4 arms, 4 Ws per seed

## Substrate-KB prior-work check (2026-07-01)

Q: `bash tools/substrate_query.sh "multi-hop reasoning depth partition oracle chain extension"`
Top hits (cosine < 0.40):
1. `preregs/2026-06-26_phase_diagram_multihop_depth_extension_via_partition_oracle_v1.md` (0.403)
2. `notes/skunkworks_tier_rule_batch3_6artifact_2026-06-26.md` chunk (0.393)
3. Prior cell prereg source file (0.374)

**Prior work status:**
- `data/exp_phase_diagram_multihop_depth_extension_via_partition_oracle_v1/metrics.json`:
  verdict CHAIN_GRADE_DEPTH_EXTENDS, PART_15HOP=0.808 MEASURED
- `data/exp_phase_diagram_multihop_depth_ceiling_sweep_20_25_30_v1/metrics.json`:
  verdict CHAIN_GRADE_DEPTH_CEILING_30, PART_15HOP=0.810 / PART_20HOP=0.708 /
  PART_25HOP=0.673 / PART_30HOP=0.637 all MEASURED HARD_PASS

**Rediscovery-vs-novel:** depths 15/20/30 are chain-grade MEASURED prior work.
**Depth 40 is GENUINELY NEW** and probes USER discriminator "recall drop below
0.50" — prior cell hit depth-30 at 0.637 (still above 0.50; discriminator has
NOT fired). This cell ships to find the crossing.

## Motivation

USER 2026-07-01 spawn prompt: stress-test the depth-scaling envelope of the
partition-oracle multi-hop primitive at depths {15, 20, 30, 40}. Discriminator:
at what depth does recall drop below 0.50?

Prior chain-grade envelope: depth-30 at recall=0.637 (per-step ~0.9855).
Extrapolating: 0.9855^40 = 0.556; 0.98^40 = 0.446; 0.97^40 = 0.296. The 0.50
line is predicted to fall between depths 35 and 42 depending on per-step
decay. Depth 40 is the first "predicted crossing" phase point in the sweep.

## Arms (4)

| Arm                        | Mechanism                        | Purpose                                    |
|----------------------------|----------------------------------|--------------------------------------------|
| ARM_PART_ORACLE_15HOP      | partition-oracle per-hop cleanup | rail: reproduce prior 0.808 +/- 0.05       |
| ARM_PART_ORACLE_20HOP      | partition-oracle per-hop cleanup | rail: reproduce prior 0.708 +/- 0.05       |
| ARM_PART_ORACLE_30HOP      | partition-oracle per-hop cleanup | rail: reproduce prior 0.637 +/- 0.05       |
| ARM_PART_ORACLE_40HOP      | partition-oracle per-hop cleanup | NEW phase point (discriminator)            |

## Pre-reg bands (LOCKED at module init)

### Sanity rails (verdict pre-emption on majority-seed breach)

- `RAIL_15`: PART_15HOP in [0.758, 0.858] else RAIL_BREACH
  - Target 0.808 (avg of prior two cells: 0.8083 + 0.8100)
- `RAIL_20`: PART_20HOP in [0.658, 0.758] else RAIL_BREACH
  - Target 0.708 (prior 0.7083 depth-ceiling-sweep-v1)
- `RAIL_30`: PART_30HOP in [0.587, 0.687] else RAIL_BREACH
  - Target 0.637 (prior 0.6367 depth-ceiling-sweep-v1)

### Novel phase point (depth 40)

- `HP_40HOP = 0.30` (chain-grade if reached; matches prior 30-hop HP band)
- `HF_40HOP = 0.10` (mechanism cliff)
- `DISCRIMINATOR_HALF_LINE = 0.50` (USER's crossing question)
- `PHASE_CV_MAX = 0.10` (per-arm seed cv cap for HARD_PASS claim)

### Verdicts (LOCKED at module init)

- `DEPTH_40_STILL_ABOVE_HALF`: PART_40HOP >= 0.50 (rails pass, cv OK)
  -> envelope open beyond depth 40; ceiling not yet found
- `DEPTH_40_BELOW_HALF`: PART_40HOP in [0.30, 0.50) (rails pass, cv OK)
  -> discriminator FIRES; 0.50 crossing between depth 30 and 40
- `DEPTH_40_HARD_FAIL`: PART_40HOP < 0.10
  -> cliff BEFORE depth 40 (mechanism failure at this depth)
- `RAIL_BREACH`: any rail breach majority of seeds -> setup broken
- `MIDDLE_BAND`: PART_40HOP in [0.10, 0.30) or cv breach

## CRLB / capacity-feasibility (META_RULE_9)

- `crlb_floor_computed`: 0.10 (per_hop_random_guess = 1/PART_SIZE = 1/10)
- `crlb_formula_reference`: `per_hop_random_guess = 1/PART_SIZE = 1/10 = 0.10`
- `discriminator_reachability`: True (HP_40HOP=0.30 > CRLB=0.10)
- Argmax over PART_SIZE=10 items; noise floor = 1/10 = 0.10.
- HP_40HOP=0.30 = 3x floor; discriminator physically reachable.

## Discriminator-must-survive-scale (path B: analytical justification)

Prior cell measured PART_30HOP=0.637 at N=8192, 200 chains, V_C=200. Per-step
accuracy at depth 30 = 30√0.637 = 0.9855.

Extrapolating to depth 40 with same per-step:
- 0.9855^40 = 0.556 (would land in DEPTH_40_STILL_ABOVE_HALF)
- 0.98^40 = 0.446 (would fire DEPTH_40_BELOW_HALF)
- 0.97^40 = 0.296 (would land in MIDDLE_BAND)

Discriminator predicted to FIRE at depth 40 under reasonable per-step decay
assumptions (both above and below 0.50 are physically achievable). All three
outcome tiers reachable => cell has genuine discriminative signal.

Smoke at N=2048/25-chains over-performs (PART_40HOP=0.92 measured; well above
FULL-N expectation). Full run at N=8192/200-chains inherits the substrate
regime where prior chain-grade envelope was measured; discriminator survives
scale iff full-run follows the extrapolation.

## TWO-W discipline (relaxed to FOUR-W)

Each depth needs a W ingested from chains at THAT max_depth (chains-of-length-D
require W built with make_deep_chains(max_depth=D)). Four Ws total:

- `W_d15`: n_chains=200 * depth=15 = 3000 bindings (rail 15HOP)
- `W_d20`: n_chains=200 * depth=20 = 4000 bindings (rail 20HOP)
- `W_d30`: n_chains=200 * depth=30 = 6000 bindings (rail 30HOP)
- `W_d40`: n_chains=200 * depth=40 = 8000 bindings (novel 40HOP)

Deviation from TWO-W canonical documented per depth-extension-v1 precedent.

## Config

- N=8192 (per Fix #24 GPU-native)
- V_C=200, V_P=10, K_set=20, n_chains=200, N_PARTITIONS=20 (PART_SIZE=10)
- 3 seeds [11, 13, 19]
- `disallow_s=set()` on all four W constructions
- ENCODER_PROVENANCE="SUBSTRATE_NATIVE"
- Zero LLM calls at inference (asserted via `_LLM_CALL_COUNTER`)
- Per-seed checkpoint (PROT-021) via `experiments/_seed_checkpoint.py`
- atexit synthesizer for resume
- Start-marker + crash-diagnostic (defensive per META_RULE §13)

## GPU usage (Fix #24)

- torch.cuda active: E, R, all Ws on device
- Batched outer-product Hebbian ingest: `V.T @ K` matmul per batch
- Argmax cleanup: `torch.argmax(E_part @ (W @ key))` on device
- Encoder hoisted per seed (E, R built once)
- Memory budget: 4 Ws @ N=8192 = 4 * 268MB = 1072MB + E (6.5MB) + R (0.3MB)
  = ~1080MB peak; well under 8GB GPU
- Each W freed via `del` + `empty_cache` post-seed

## Timeout estimate

Depth-ceiling-sweep-v1 elapsed 88.4s wall (3 seeds, ~30s/seed) on GPU at 4 Ws,
depths 15/20/25/30. This cell has depths 15/20/30/40 (adds 40HOP but drops
25HOP); depth-40 arm is ~1.33x depth-30 arm cost; W_d40 is ~1.33x W_d30.

Per-seed estimate: 30s * 1.15 = ~35s. Three seeds: ~105s. Add safety buffer
for GPU contention:

**Timeout: 3600s (1 hour)** — per USER spawn prompt directive. Per-seed
checkpoint allows mid-run recovery.

## SCHEMA-VET pre-dispatch checklist

- [x] `cardinality_ok`: N/A (no sweep axis; 4 fixed depth phase points)
- [x] `arms_differ_verified`: True (each arm uses distinct W_d<D>; different max_depth chains)
- [x] `final_metrics_atomicity`: `write_metrics` helper uses tmp+os.replace pattern
- [x] `except SystemExit: raise` BEFORE `except Exception` ordering: verified in main
- [x] `crlb_floor_computed`: 0.10 (declared in code)
- [x] `discriminator_reachability`: True (HP=0.30 > 0.10 floor)
- [x] `baseline_in_band`: N/A (no baseline arm; three rail arms with prior MEASURED targets)
- [x] `calibration_check`: `default_ok_for_this_regime` (same primitive as chain-grade prior cells)
- [x] `defensive_error_checking`: passed all 4 patterns (start_marker, crash_diagnostic, no bare except, atomic write)
- [x] `HP_SCOPE`: HP_40HOP applies to ARM_PART_ORACLE_40HOP only; rails have separate band gates
- [x] `sweep_alignment_verdict`: N/A (no parameter sweep; discrete depth phase points)
- [x] `discriminating_fraction`: 4/4 = 1.00 (all four depth points are informative)
- [x] `composition_edges`: N/A (single-primitive, no composition)
- [x] `positive_control_arms`: three rail arms reproduce prior chain-grade MEASURED targets AT MATCHED REGIME (N=8192, 200 chains, V_C=200)
- [x] `functional_requirements`: multi-hop chain-following via partition-oracle routed cleanup (chain-grade primitive)

## Failure-mode awareness

- RUN_MODE_MISMATCH: cell defaults `run_mode='full'` when neither `--smoke` nor
  `HDLAB_EXP_NAME=*_smoke*` present; queue_add MUST NOT pass `--self-test`
- ANCHOR_NAME_N_SUFFIX_CONFIG_MISMATCH: anchor is `_gpu_v1`; N=8192 in
  CONFIG_VERSION string for cert-trail
- DISPATCH_FAILURE_MISCLASSIFICATION: verify via `queue.json` post-ship
- STRATEGIC_INTERPRETATION_OVER_CLAIM: verdict tiers LOCKED; 3 rails gate the
  novel depth-40 claim; MEASURED-not-HYPOTHESIZED targets

## Pause / authorization

- Pause flag check: `data/orchestrator_paused.flag` not present at authoring time
- Auto mode active per USER directive; overnight_queue routing per USER spawn

## Expected post-dispatch verify

1. Orchestrator commits cell + prereg + pushes to origin/main
2. Orchestrator queue_add to overnight_queue with `--timeout 3600`
3. queue_add post-ship verification confirms entry in remote queue.json
4. Landing polling via `data/recent_landings.jsonl` (Fix #25 + #21)
5. Read `data/exp_multihop_reasoning_depth_20_to_40_gpu_v1/metrics.json`
6. `tools/peek_arm_metrics.py` for per-arm verification before framing
7. VERIFY `run_mode=full`, size>5KB, all 3 seeds present
8. hdi_skunkworks landed-VET spawn on completion
