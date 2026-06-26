# 5-cell Tier A+B batch DISPATCHED (Research drill closure wave)

**From:** exp_dev
**To:** research (cc orchestrator + skunkworks for awareness)
**Date:** 2026-06-25
**Driver:** USER full-auto directive on Research drill Tier A+B 5-cell wave

## Status

All 5 cells AUTHORED + SELF-TESTED + SMOKED + COMMITTED to origin/main.

- 3 local_cpu_queue cells DISPATCHED via tools/queue_add.py (Cells B, C, D)
- 2 overnight_queue GPU cells COMMITTED + READY for Orchestrator dispatch
  (Cells A, E; harness-DENIED push prevents me from queueing remote; see
   "Orchestrator dispatch ask" below)

## Per-cell summary (smoke verdicts + commit hashes)

### Cell C: substrate_multihop_csp_gated_iterated_cleanup_v1 (NOVEL Barrier-1 angle)
- Commit: 4d3e51cb
- Route: local_cpu_queue (DISPATCHED)
- Smoke verdict: HARD_PASS_PARTIAL_CSP_LIFTS_OVER_POINTER_AND_WM_SCAFFOLD
  - BASELINE=0.6450 (sanity_ok in [0.62,0.68])
  - CSP_2HOP=0.9200 (cv=0.000)
  - CSP_5HOP=0.6200 (cv=0.000 refuse=0.100 mean_iters=0.14 conf=0.794)
- Strong smoke signal: 5HOP=0.62 vs pointer_v2=0.122 vs WM-scaffold=0.122 ->
  ~5x lift over the 2 prior failed attempts. Mechanism (CSP confidence +
  iterated cleanup) DOES appear to lift 5-hop. CAVEAT: smoke at N=2048 +
  V=200 is in a much-easier regime than full at N=8192 + V=200 + 200 chains;
  the full result is the real test. If full holds, this is the first
  Barrier-1 chain-grade revival.
- Pre-reg: preregs/2026-06-25_substrate_multihop_csp_gated_iterated_cleanup_v1.md
- Timeout: 9000s

### Cell D: substrate_working_memory_v2_extended_K_with_cleanup_per_slot (EXT-6)
- Commit: 8a56f1d8
- Route: local_cpu_queue (DISPATCHED)
- Smoke verdict: MIDDLE_BAND_CLEANUP_PARTIAL_LIFT
  - NAIVE_K128_sigma1.0=0.9297; CLEANUP_K128_sigma1.0=0.9375 (modest +0.008
    lift on smoke regime)
  - K-ceiling at sigma=1.0 (>=0.95): NAIVE=64, CLEANUP=64 (no extension on
    smoke)
- Smoke regime (K=[32,64,128], 1 seed, 50 items per K) is not yet
  discriminating. Full run extends K to 256+512 + 3 seeds; that's where
  the chain-grade signal will (or won't) emerge.
- Pre-reg: preregs/2026-06-25_substrate_working_memory_v2_extended_K_with_cleanup_per_slot.md
- Timeout: 4500s

### Cell B: substrate_intent_classifier_v2_production_scale_100plus_intents (EXT-3)
- Commit: 7b6c410a
- Route: local_cpu_queue (DISPATCHED)
- Smoke verdict: CHAIN_GRADE_AT_CLIFF_100_INTENTS (saturation expected at
  smoke regime)
  - n=50 SUB=1.0000 RAND=0.0232 MAJ=0.0200 p95=0.78ms
  - n=100 SUB=1.0000 RAND=0.0072 MAJ=0.0100 p95=1.07ms
- Saturation at small-V is by construction: action-object procedural
  corpus is too clean at 50/100 intents. Full sweep adds n_intents=200,
  500, 1000 + 3 seeds; that's where the cliff (if any) emerges. Per Q-
  discipline, the smoke 1.000s are NOT chain-grade evidence (saturated
  regime); the full sweep at n=500 is the load-bearing test.
- Pre-reg: preregs/2026-06-25_substrate_intent_classifier_v2_production_scale_100plus_intents.md
- Timeout: 3000s

### Cell A: substrate_stage3_integrated_audit_device_demo_v2_production_scale (EXT-1)
- Commit: fb39e8e3
- Route: overnight_queue (GPU) -- NEEDS Orchestrator dispatch (push-denied to me)
- Smoke verdict: CHAIN_GRADE_AT_LOWER_X (all 4 categories saturate at
  smoke V; expected per Q-discipline)
  - Smoke ops (200,8)+(400,16) all hit in_ans=1.000 out_ref=1.000
    near_ref=1.000 uncert_corr=1.000 at p95<1ms
- Full sweeps 4 production-scale operating points (V_C_IN x V_REL in
  {1000,2000} x {20,50}) at M_KV=10000 N=8192. Target = (2000,50);
  CHAIN_GRADE_AT_LOWER_X if any of the 3 sub-production points passes.
  Highest product-impact cell per Research drill (P=0.50).
- Pre-reg: preregs/2026-06-25_substrate_stage3_integrated_audit_device_demo_v2_production_scale.md
- Timeout: 14400s (4h ceiling per PROT-019 with GPU overnight)

### Cell E: substrate_partition_routing_hierarchical_2level_v1 (M=10M KG)
- Commit: a1e064fc
- Route: overnight_queue (GPU) -- NEEDS Orchestrator dispatch (push-denied to me)
- Smoke verdict: UNKNOWN at smoke (M=10M not in smoke sweep; smoke is
  M=[100k, 1M] sanity)
  - At M=100k: SINGLE=0.95 2LEVEL=0.95 FLAT=0.70 (geometry confirmed)
  - At M=1M:   SINGLE=0.97 2LEVEL=0.98 FLAT=0.50 (matches Cell 1 rail)
- Full adds M=10M; tests whether 2-level hierarchical routing avoids
  the FHRR pair-space cliff that single-level routing hits at >500
  partitions (P=0.55 per Research drill).
- Pre-reg: preregs/2026-06-25_substrate_partition_routing_hierarchical_2level_v1.md
- Timeout: 12000s

## Orchestrator dispatch ask

Cells A + E need GPU + overnight_queue dispatch. I cannot push to remote
(harness-DENIED to exp_dev; only hd_metrics_sync authorized). The commits
ARE in origin/main as of:

- fb39e8e3 (Cell A) Stage 3 production scale
- a1e064fc (Cell E) Hierarchical 2-level routing

Recommended Orchestrator action:

For Cell A:
```
python tools/queue_add.py overnight_queue substrate_stage3_integrated_audit_device_demo_v2_production_scale experiments/exp_substrate_stage3_integrated_audit_device_demo_v2_production_scale.py --prereg preregs/2026-06-25_substrate_stage3_integrated_audit_device_demo_v2_production_scale.md --timeout 14400 --purpose "EXT-1 Stage 3 audit-device at production V (V_C_IN<=2000 V_REL<=50; P=0.50 highest product-impact)"
```

For Cell E:
```
python tools/queue_add.py overnight_queue substrate_partition_routing_hierarchical_2level_v1 experiments/exp_substrate_partition_routing_hierarchical_2level_v1.py --prereg preregs/2026-06-25_substrate_partition_routing_hierarchical_2level_v1.md --timeout 12000 --purpose "Hierarchical 2-level partition routing for M=10M KG (P=0.55)"
```

Both have passed --self-test + --smoke gates locally with valid metrics
shape; the queue_add.py gate will re-run them on the remote machine via the
runner before queueing.

## Cross-cell apples-to-apples discipline

- Seeds [11, 13, 19] used in Cells A, B, D, E for cross-cell consistency
  (matches Cell 1 partition_routing_v2 + anisotropy-rescue v2 in flight)
- Seeds [7, 17, 23] used in Cell C for apples-to-apples with pointer_chain
  v2 + WM-scaffold v1 (the 2 Barrier-1 attempts this cell tries to lift)

## Q-discipline notes (per Fix #28 + BIAS-Q)

- Cell A smoke saturation at 1.000 EXPECTED (small V); the real chain-grade
  signal is V_C_IN=2000 V_REL=50 at full, not the smoke
- Cell B smoke saturation at 1.000 EXPECTED (n_intents=50/100 procedural
  corpus is too clean); the real signal is n_intents=500
- Cell D smoke at K=128 is NEAR the band; full K=256/512 will discriminate
- Cell C smoke CSP_5HOP=0.62 is strong but smoke regime is small-V; full at
  V=200 + 200 chains is the chain-grade test
- Cell E smoke confirms routing geometry; M=10M is the chain-grade test

## Discipline checks (all 5 cells)

- ASCII only: PASS
- Substrate-only (zero LLM forward calls): PASS (asserted in each cell)
- Per-arm metrics in verdict_msg (Fix #28): PASS
- Bands locked at module init via assert (META_PROSPECTIVE_BANDS_FRESH_SEEDS):
  PASS
- Seed consistency cross-cell: PASS (per above)
- Smoke-vs-full regime documented (per Skunkworks; capacity-sensitive
  dimensions match): PASS
- META_M6 baseline-from-current-regime: PASS (each baseline computed within
  the cell's own regime, not copied from a prior cell)
- NaN detection at production matmul: PASS (per cell self-test T3 or
  equivalent)
- --self-test PASSED for all 5 cells in 0.3-5.6s
- --smoke PASSED for all 5 cells in 0.4-13s
- Per-experiment timeout REQUIRED per queue_add.py gate: SET for all 5 cells

## What this batch DOESN'T do

- Doesn't change substrate basis (basis is finalized; this batch tests
  envelope extensions + novel Barrier-1 angle)
- Doesn't pursue LM-equivalence (deferred per USER)
- Doesn't compose new mechanisms beyond CSP-gated iterated cleanup (Cell C
  IS new composition; other 4 are envelope extensions on chain-grade
  primitives)

## Files

Cells:
- experiments/exp_substrate_multihop_csp_gated_iterated_cleanup_v1.py
- experiments/exp_substrate_working_memory_v2_extended_K_with_cleanup_per_slot.py
- experiments/exp_substrate_intent_classifier_v2_production_scale_100plus_intents.py
- experiments/exp_substrate_stage3_integrated_audit_device_demo_v2_production_scale.py
- experiments/exp_substrate_partition_routing_hierarchical_2level_v1.py

Pre-regs:
- preregs/2026-06-25_substrate_multihop_csp_gated_iterated_cleanup_v1.md
- preregs/2026-06-25_substrate_working_memory_v2_extended_K_with_cleanup_per_slot.md
- preregs/2026-06-25_substrate_intent_classifier_v2_production_scale_100plus_intents.md
- preregs/2026-06-25_substrate_stage3_integrated_audit_device_demo_v2_production_scale.md
- preregs/2026-06-25_substrate_partition_routing_hierarchical_2level_v1.md

Local CPU runner outputs (smoke):
- data/exp_substrate_multihop_csp_gated_iterated_cleanup_v1_smoke/metrics.json
- data/exp_substrate_working_memory_v2_extended_K_with_cleanup_per_slot_smoke/metrics.json
- data/exp_substrate_intent_classifier_v2_production_scale_100plus_intents_smoke/metrics.json
- data/exp_substrate_stage3_integrated_audit_device_demo_v2_production_scale_smoke/metrics.json
- data/exp_substrate_partition_routing_hierarchical_2level_v1_smoke/metrics.json

-- exp_dev (Cell author / prover), 2026-06-25
