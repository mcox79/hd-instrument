# Prereg: phase_diagram_multihop_depth_at_production_V_C_2000_v1

**Date**: 2026-06-25
**Author**: exp_dev
**Anchor**: `phase_diagram_multihop_depth_at_production_V_C_2000_v1`
**Cell**: `experiments/exp_phase_diagram_multihop_depth_at_production_V_C_2000_v1.py`
**Routing**: overnight_queue (GPU; Fix #24 active GPU use; GPU idle per USER)
**Compute**: N=8192, V_C=2000 (PRODUCTION; 10x of v1), 3 seeds [11,13,19], 7 arms, 4 Ws per seed

## Motivation

Today's `phase_diagram_multihop_depth_extension_via_partition_oracle_v1` landed
**CHAIN_GRADE_DEPTH_EXTENDS_ALL_4_PHASE_POINTS** at V_C=200:
- 5HOP = 0.965
- 7HOP = 0.882
- 10HOP = 0.857
- 15HOP = 0.808

This proved the substrate handles depth-15 multi-hop with ORACLE routing on a
1000-vector retrieval space. **UNTESTED**: does the chain-grade hold at
PRODUCTION V_C=2000 (10x retrieval-space size = audit-device deployment scale)?
This is the right-side phase boundary we have NOT pushed.

Per phase-portrait v1 framework (USER 2026-06-22 latent-capability directive):
substrate must act at ANY phase-diagram position; production-scale is the
deployment regime, not just the calibration regime. If chain-grade holds at
V_C=2000, depth-multi-hop is production-ready.

## Arms (7)

| Arm                                       | Mechanism                                 | Source W                       | Purpose                              |
| ----------------------------------------- | ----------------------------------------- | ------------------------------ | ------------------------------------ |
| ARM_BASELINE_HRR_2HOP                     | beta-sweep 2-hop HRR naive                | local                          | sanity rail                          |
| ARM_REPRODUCE_POINTER_CHAIN_V2_5HOP       | verbatim pointer-v2 _retrieve_1hop fwd    | W_pointer_v2 (2000 @ V_C=2000) | META_M7 mandatory                    |
| ARM_PART_ORACLE_5HOP                      | partition-oracle per-hop cleanup          | W_v1_rail (1000 @ V_C=200)     | CROSS-CELL RAIL to v1 anchor at V_C=200 |
| ARM_PART_ORACLE_5HOP_VC2000               | partition-oracle per-hop cleanup          | W_v1_regime (1000 @ V_C=2000)  | PRODUCTION 5-hop at scale            |
| ARM_PART_ORACLE_7HOP_VC2000               | partition-oracle per-hop cleanup          | W_pointer_v2 (2000 @ V_C=2000) | PRODUCTION 7-hop at scale            |
| ARM_PART_ORACLE_10HOP_VC2000              | partition-oracle per-hop cleanup          | W_pointer_v2 (2000 @ V_C=2000) | PRODUCTION 10-hop at scale           |
| ARM_PART_ORACLE_15HOP_VC2000              | partition-oracle per-hop cleanup          | W_d15 (3000 @ V_C=2000)        | PRODUCTION 15-hop at scale           |

## Pre-reg bands (LOCKED at module init)

### Sanity rails (verdict pre-emption on majority-seed breach)

- `RAIL_BASELINE`: BASELINE in [0.62, 0.68] else SANITY_BREACH
- `RAIL_META_M7`: REPRODUCE in [0.08, 0.25] else META_M7_BREACH
  - (pointer-chain-v2's known 0.122 +/- noise band; tested on E at V_C=2000)
- `RAIL_CROSS_CELL_5HOP_VC200`: PART_ORACLE_5HOP in [0.935, 0.975] else CROSS_CELL_BREACH
  - (v1 anchor target 0.9550 +/- 0.02; this arm uses SEPARATE E_VC200 codebook
    to reproduce v1 conditions; rail proves the production cell can still
    achieve v1's chain-grade signal when run at V_C=200)

### PRODUCTION V_C=2000 phase points (per-arm; PASS/FAIL with cv discipline)

| Depth        | HARD_PASS  | HARD_FAIL | cv cap |
| ------------ | ---------- | --------- | ------ |
| 5HOP_VC2000  | >= 0.85    | < 0.50    | 0.10   |
| 7HOP_VC2000  | >= 0.65    | < 0.40    | 0.10   |
| 10HOP_VC2000 | >= 0.50    | < 0.25    | 0.10   |
| 15HOP_VC2000 | >= 0.30    | < 0.15    | 0.10   |

These thresholds are **identical to v1's** per directive. The compounding
prediction (per-hop 0.95) under-bounds depth=5 (oracle routing makes it ~0.99
per-hop) and is the band for depths 7/10/15.

### Verdicts (LOCKED at module init)

- `CHAIN_GRADE_DEPTH_HOLDS_AT_PRODUCTION_V_C`: all 4 V_C=2000 depths HARD_PASS
  -> depth chain-grade ROBUST at production retrieval-space size
- `PARTIAL_DEPTH_HOLDS_TO_10`: 5+7+10 HARD_PASS, 15 below
  -> cliff between 10-15 at production
- `PARTIAL_DEPTH_HOLDS_TO_7`: 5+7 HARD_PASS, 10 below
  -> cliff between 7-10 at production
- `DEPTH_5_IS_PRODUCTION_CEILING`: depth=5 only at V_C=2000
  -> 10x retrieval-space cost is depth-5
- `CROSS_CELL_BREACH`: 5HOP_RAIL breach -> v1 reproduce failed
- `META_M7_BREACH`: reproduce breach -> regime drifted
- `SANITY_BREACH`: baseline breach -> setup broken
- `MIDDLE_BAND`: mixed phase points

## TWO-W canonical (+ extensions documented)

The directive specifies TWO-W discipline (W_pointer_v2 + W_v1_regime) with
`disallow_s=set()`. This cell builds:

- `W_v1_regime`: `make_deep_chains(n_chains=200, max_depth=5)` on E_VC2000 = 1000 bindings
  - For ARM_PART_ORACLE_5HOP_VC2000 (production 5-hop)
- `W_pointer_v2`: `make_deep_chains(n_chains=200, max_depth=10)` on E_VC2000 = 2000 bindings
  - For ARM_REPRODUCE_POINTER_CHAIN_V2_5HOP (META_M7 at production V_C)
  - For ARM_PART_ORACLE_7HOP_VC2000 (chains[:7]) and 10HOP_VC2000 (full)
- `W_depth15_extended`: `make_deep_chains(n_chains=200, max_depth=15)` on E_VC2000 = 3000 bindings
  - For ARM_PART_ORACLE_15HOP_VC2000 only (W_pv2's depth-10 doesn't contain 15-hop chains)
- `W_v1_rail_vc200`: `make_deep_chains(n_chains=200, max_depth=5)` on E_VC200 = 1000 bindings
  - For ARM_PART_ORACLE_5HOP CROSS-CELL RAIL ONLY (separate V_C=200 codebook to reproduce v1 anchor exactly)

This is FOUR Ws total: two main + one extension + one rail-arm. All scoped
explicitly. `disallow_s=set()` preserved on all four. Documented because the
TWO-W discipline applies to the canonical pair; extensions are cleanly scoped
(one for depth-15 chains; one to reproduce v1 anchor at V_C=200 for rail).

## Config

- N=8192 (per directive)
- V_C=2000 (PRODUCTION; 10x v1's V_C=200, per directive)
- V_C_RAIL=200 (cross-cell rail only)
- V_P=10, K_set=20, n_chains=200, N_PARTITIONS=20
- PART_SIZE: 100 at production V_C=2000; 10 at rail V_C=200
- 3 seeds [11, 13, 19]
- `disallow_s=set()` preserved on all four W constructions
- ENCODER_PROVENANCE="SUBSTRATE_NATIVE"
- Substrate-only at inference; zero LLM forward calls (asserted via
  `_LLM_CALL_COUNTER` before metrics write)
- Per-seed checkpoint (PROT-021) via `experiments/_seed_checkpoint.py`
- atexit partial-flush for resume

## GPU usage (Fix #24)

- torch.cuda actively used: E_main (V_C=2000), E_rail (V_C=200), R, all Ws on device
- Batched outer-product Hebbian ingest: `V.T @ K` matmul per batch
- argmax cleanup is `torch.argmax(E_parts @ (W @ key))` on device
- Encoders hoisted (E_main, E_rail, R built once per seed, not per arm)
- gpu_avail + gpu_name + gpu_max_mem_alloc_mb logged per seed
- **Module-init memory projection** (per `hdlab/gpu_memory_budget.py`):
  - Persistent (per seed): 4 Ws @ (8192,8192)f32 = 1024 MB + E_main (62.5 MB)
    + E_rail (6.5 MB) + R (0.3 MB) = ~1093 MB resident
  - Transient: ingest batches 1000xN ~ 62 MB peak
  - **Projected peak: ~1155 MB** under 6 GB budget (5.0 GB headroom)
  - `assert_under_budget(proj, 6*1024)` enforces at module init
- All Ws freed after seed via `del` + `empty_cache`

## Timeout estimate (per-formula)

v1 cell timeout: 14400s for 3 seeds at V_C=200 + 3 Ws.

V_C=2000 scaling cost (incremental over v1):
- E_main: 10x larger codebook (more rows) but used in cleanup via E_parts slicing
  -> per-hop argmax cost grows ~10x at no-routing; with partition oracle and PART_SIZE=100,
  the local-partition argmax is constant cost; only ingest cost grows
- Ingest: same n_chains x depth = same #triples; per-triple cost is
  outer(o, s*p)/N which is N^2 matmul per batch (V_C invariant!) -> COST UNCHANGED
- Cross-cell rail: extra W build at V_C=200 + 5-hop arm (small; ~ 1/10 of main)

**Conclusion**: ingest + partition cleanup are V_C-invariant on the per-W axis;
total cost is ~v1 cost + small rail overhead. Estimate 6000-9000s per 3-seed run.

**Timeout: 14400s (4 hours)** — same as v1 with 50% buffer; ample headroom.

`smoke_wall_s = 5.3s (N=2048, 1 seed, V_C=400 smoke, 30 chains)`
`scaling_exp = 1.5 (matmul N^2 + slight V_C)`
`(8192/2048)^1.5 * (2000/400)^0.5 * (200/30) * (3/1) = 8 * 2.24 * 6.67 * 3 = 358x = ~1900s`

Conservative 14400s budget driven by 4 W builds at N=8192 plus 5 partition arms.

## Disciplines applied

- ASCII only (script + prereg)
- TWO-W canonical + 1 documented extension W + 1 documented rail-arm W
- Per-arm metrics in `per_seed[i]` (Fix #28: read per-arm before framing)
- META_M7 capacity-sensitive dims identical smoke/full
- Per-seed checkpoint (PROT-021) + atexit partial-flush
- Path-scoped commit; route through Orchestrator for SCP+SSH dispatch
- REMOTE VERIFY post-dispatch (queue_add.sh has built-in)
- Smoke gate FIRST + GPU memory check (5.0 GB headroom verified) + cross-cell
  rail check via PART_ORACLE_5HOP at V_C=200 (must reproduce v1 0.9550)
- Fix #26 predispatch_check.py: PROCEED (zero matching landings/atoms)
- ORACLE routing identical to v1 (mechanism unchanged; only V_C scales)

## Failure-mode awareness

- DISPATCH_FAILURE_MISCLASSIFICATION: queue_add.sh post-ship verification confirms
  entry in REMOTE queue.json (exit 5 if missing)
- SCRIPT_PRECONDITION_VIOLATION: self-test passes on local CPU; module-init
  GPU memory projection refuses to start if over 6 GB at full;
  `RUN_MODE != "smoke" -> GPU_AVAIL` enforces GPU at full
- ANCHOR_NAME_N_SUFFIX_CONFIG_MISMATCH: anchor has NO `_n<N>` suffix; PROT-018
  no-op; N=8192 + V_C=2000 in CONFIG_VERSION string for cert-trail
- STRATEGIC_INTERPRETATION_OVER_CLAIM: verdict tiers are LOCKED at module init;
  cross-cell rail at 5HOP_VC200 gates the depth-extension claim
- GPU_DISPATCH_NOT_USING_GPU (Fix #24): module-init torch.cuda probe + budget
  projection + production-mode GPU_AVAIL assert; per-seed gpu_max_mem_alloc_mb
  logged

## Pause / authorization

- Pause flag check: `data/orchestrator_paused.flag` NOT present at dispatch
- USER full-auto authorized + traveling (per directive)
- GPU idle (per directive); routing to overnight_queue exercises Fix #24

## Expected post-dispatch verify

After SCP+SSH queue_add:
1. `queue_add.sh` post-ship verification confirms entry in remote queue.json (exit 5 if missing)
2. Check `data/recent_landings.jsonl` after estimated wall (Fix #25 + #21)
3. Read `data/exp_phase_diagram_multihop_depth_at_production_V_C_2000_v1/metrics.json`
4. `tools/peek_arm_metrics.py` for per-arm verification before framing
5. Notify Skunkworks via SendMessage on landing (cert-VET request)
