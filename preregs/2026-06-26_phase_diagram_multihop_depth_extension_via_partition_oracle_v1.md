# Prereg: phase_diagram_multihop_depth_extension_via_partition_oracle_v1

**Date**: 2026-06-26
**Author**: exp_dev
**Anchor**: `phase_diagram_multihop_depth_extension_via_partition_oracle_v1`
**Cell**: `experiments/exp_phase_diagram_multihop_depth_extension_via_partition_oracle_v1.py`
**Routing**: overnight_queue (GPU; Fix #24 active GPU use)
**Compute**: N=8192, 3 seeds [11,13,19], 6 arms, 3 Ws per seed

## Motivation

Cell B v2 (`substrate_multihop_compose_fly_lsh_multibank_partition_v2_META_M7_rail`)
chain-graded the depth=5 multi-hop phase point at PART_ORACLE=0.9550 (cv=0.007;
META_M7 PASS at 0.122 reproduce). Known phase boundary point: depth=5 with
V_C=200, K_set=20, n_chains=200, partition-routed cleanup, N=8192.

**Unknown**: where does the chain-grade envelope cliff as depth scales? Brain
handles 10+ steps for reasoning. Substrate's per-hop accuracy at depth=5 is
~0.95 per step -> at depth=10, 0.95^10 = 0.60. Is that floor or chain-grade?

This cell maps the depth phase boundary by ADDING three new phase points
(7HOP, 10HOP, 15HOP) using oracle-routed partition cleanup, while reproducing
Cell B v2's cross-cell rail at 5HOP.

## Arms (6)

| Arm                                  | Mechanism                                    | Source W                  | Purpose                          |
| ------------------------------------ | -------------------------------------------- | ------------------------- | -------------------------------- |
| ARM_BASELINE_HRR_2HOP                | beta-sweep 2-hop HRR naive                   | local                     | sanity rail                      |
| ARM_REPRODUCE_POINTER_CHAIN_V2_5HOP  | verbatim pointer-v2 _retrieve_1hop forward-only | W_pointer_v2 (2000 bind)  | META_M7 mandatory                |
| ARM_PART_ORACLE_5HOP                 | partition-oracle per-hop cleanup             | W_v1_regime (1000 bind)   | Cell B v2 cross-cell rail        |
| ARM_PART_ORACLE_7HOP                 | partition-oracle per-hop cleanup             | W_pointer_v2 (2000 bind)  | NEW phase point                  |
| ARM_PART_ORACLE_10HOP                | partition-oracle per-hop cleanup             | W_pointer_v2 (2000 bind)  | NEW phase point                  |
| ARM_PART_ORACLE_15HOP                | partition-oracle per-hop cleanup             | W_depth15_extended (3000) | NEW deep phase point             |

## Pre-reg bands (LOCKED at module init)

### Sanity rails (verdict pre-emption on majority-seed breach)

- `RAIL_BASELINE`: BASELINE in [0.62, 0.68] else SANITY_BREACH
- `RAIL_META_M7`: REPRODUCE in [0.08, 0.25] else META_M7_BREACH
  - (pointer-chain-v2's known 0.122 +/- noise band)
- `RAIL_CROSS_CELL_5HOP`: PART_ORACLE_5HOP in [0.935, 0.975] else CROSS_CELL_BREACH
  - (Cell B v2 target 0.9550 +/- 0.02 per directive)

### Phase points (per-arm; PASS/FAIL with cv discipline)

Per-depth predicted by 0.95-per-step compounding (per_step at depth=5 was ~0.95):

| Depth | Predicted | HARD_PASS  | HARD_FAIL | cv cap |
| ----- | --------- | ---------- | --------- | ------ |
| 7HOP  | 0.95^7 = 0.6983 -> ~0.70 | >= 0.65 | < 0.40 | 0.10 |
| 10HOP | 0.95^10 = 0.5987 -> ~0.60 | >= 0.50 | < 0.25 | 0.10 |
| 15HOP | 0.95^15 = 0.4633 -> ~0.46 | >= 0.30 | < 0.15 | 0.10 |

### Verdicts (LOCKED at module init)

- `CHAIN_GRADE_DEPTH_EXTENDS`: all 4 depths (5/7/10/15) HARD_PASS -> deep reasoning scales
- `PARTIAL_DEPTH_EXTENDS_TO_10`: 5+7+10 HARD_PASS, 15 below -> cliff between 10-15
- `PARTIAL_DEPTH_EXTENDS_TO_7`: 5+7 HARD_PASS, 10 below -> cliff between 7-10
- `DEPTH_5_IS_CEILING`: depth=5 only -> Cell B v2 was the limit
- `CROSS_CELL_BREACH`: 5HOP rail breach -> reproduce failed (would invalidate phase comparison)
- `META_M7_BREACH`: reproduce breach -> regime drifted (META_M7 invariant violated)
- `SANITY_BREACH`: baseline breach -> setup broken
- `MIDDLE_BAND`: mixed phase points (e.g., 7 PASS but 10 not PASS, not FAIL)

## TWO-W canonical (+ one extended W for 15HOP)

The directive specifies TWO-W discipline (W_pointer_v2 2000 bindings + W_v1_regime
1000 bindings; disallow_s=set()). To honor that EXACTLY for the canonical Cell B
v2 rails (cross-cell 5HOP + META_M7 reproduce) while still being able to test
15HOP phase point (which needs depth-15 chains), this cell builds THREE Ws per seed:

- `W_v1_regime`: `make_deep_chains(n_chains=200, max_depth=5)` = 1000 bindings
  - For ARM_PART_ORACLE_5HOP (cross-cell rail)
- `W_pointer_v2`: `make_deep_chains(n_chains=200, max_depth=10)` = 2000 bindings
  - For ARM_REPRODUCE_POINTER_CHAIN_V2_5HOP (META_M7)
  - For ARM_PART_ORACLE_7HOP (chains[:7]) and ARM_PART_ORACLE_10HOP (full)
- `W_depth15_extended`: `make_deep_chains(n_chains=200, max_depth=15)` = 3000 bindings
  - For ARM_PART_ORACLE_15HOP only

The third W is a deliberate extension beyond TWO-W canonical pair, documented
because W_pointer_v2's max_depth=10 doesn't contain 15-hop chains.

## Config

- N=8192 (per directive)
- V_C=200, V_P=10, K_set=20, n_chains=200, N_PARTITIONS=20 (PART_SIZE=10)
- 3 seeds [11, 13, 19]
- `disallow_s=set()` preserved on all three W constructions
- ENCODER_PROVENANCE="SUBSTRATE_NATIVE"
- Substrate-only at inference; zero LLM forward calls (asserted via
  `_LLM_CALL_COUNTER` before metrics write)
- Per-seed checkpoint (PROT-021) via `experiments/_seed_checkpoint.py`
- atexit partial-flush for resume

## GPU usage (Fix #24)

- torch.cuda actively used: E, R, all Ws on device
- Batched outer-product Hebbian ingest: `V.T @ K` matmul per batch
- argmax cleanup is `torch.argmax(E_part @ (W @ key))` on device
- Encoder hoisted (E, R built once per seed, not per arm)
- gpu_avail + gpu_name + gpu_max_mem_alloc_mb logged per seed
- Memory budget: 3 Ws @ N=8192 = 805 MB total + E (6.5MB) + R (0.3MB) = ~812 MB
  resident; well under 8 GB GPU. Each W freed after seed via `del` + `empty_cache`.

## Timeout estimate (per-formula)

Cell B v2 full run: 5913.7s wall total (3 seeds, ~1970s/seed) on numpy CPU at
2 Ws (1000+2000 bindings) and 5 arms with fly-LSH expansion.

This cell removes fly-LSH (only partition-oracle remains) but adds:
- A THIRD W (depth-15; 3000 bindings; +50% of W_pointer_v2 cost)
- One more partition arm (5/7/10/15 = 4 part arms instead of 1)

GPU speedup expected: 3-5x for matmul-heavy ops (W build + W @ key).
Net per-seed estimate: ~1500-2500s on GPU.

**Timeout: 14400s (4 hours)** — covers 3 seeds at upper-bound per-seed
estimate plus 50% buffer. Per-seed checkpoint allows mid-run recovery.

`smoke_wall_s ~= 0.6s (N=2048, 1 seed, 30 chains)`
`scaling_exp = 1.5 (matmul-bound + chain-length sweep)`
`(8192/2048)^1.5 * (200/30) = 8 * 6.67 = 53.3x per-seed * 3 seeds = 160x = ~96s`

The conservative 14400s budget is **driven by the 3 W builds at N=8192 plus
the 4 partition arms** (each O(n_chains * depth * V_C * N) = O(200 * 15 * 200 *
8192) = ~5e9 ops on GPU). Smoke wall time is too short to extrapolate
linearly because smoke does the same fixed per-step ops at smaller N + V_C.

## Disciplines applied

- ASCII only (script + prereg)
- TWO-W canonical discipline (+ documented extended W for 15HOP)
- Per-arm metrics in `per_seed[i]` (Fix #28: read per-arm before framing)
- META_M7 capacity-sensitive dims identical smoke/full
- Per-seed checkpoint (PROT-021) + atexit partial-flush
- Path-scoped commit; push to origin/main before remote dispatch
- REMOTE VERIFY post-dispatch
- Smoke gate FIRST + cross-cell rail check (5HOP_ORACLE reproduces 0.9550)
- Fix #26 predispatch_check.py: PROCEED (zero matching landings/atoms)
- ORACLE routing fine — this cell tests DEPTH phase boundary, not routing
  scope (cortex R_schema separate cell tests that)

## Failure-mode awareness

- DISPATCH_FAILURE_MISCLASSIFICATION: verify after queue_add that anchor appears
  in remote queue.json (queue_add.sh has post-ship verification baked in)
- SCRIPT_PRECONDITION_VIOLATION: self-test passes on local CPU; assertion
  `RUN_MODE != "smoke" -> GPU_AVAIL` enforces GPU at full
- ANCHOR_NAME_N_SUFFIX_CONFIG_MISMATCH: anchor has NO `_n<N>` suffix; PROT-018
  doesn't trigger; N=8192 is in CONFIG_VERSION string for cert-trail
- STRATEGIC_INTERPRETATION_OVER_CLAIM: verdict tiers are LOCKED at module init;
  cross-cell rail at 5HOP gates the depth-extension claim

## Pause / authorization

- Pause flag check: `data/orchestrator_paused.flag` not present at dispatch time
- USER full-auto authorized + traveling (per directive)

## Expected post-dispatch verify

After SCP+SSH queue_add:
1. `queue_add.sh` post-ship verification confirms entry in remote queue.json
2. Check `data/recent_landings.jsonl` after estimated wall (Fix #25 + #21)
3. Read `data/exp_phase_diagram_multihop_depth_extension_via_partition_oracle_v1/metrics.json`
4. `tools/peek_arm_metrics.py` for per-arm verification before framing
5. Notify Skunkworks via SendMessage on landing (cert-VET request)
