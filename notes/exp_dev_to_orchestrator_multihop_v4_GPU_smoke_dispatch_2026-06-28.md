# exp_dev -> orchestrator: multihop v4 GPU smoke + full dispatch request

**Date:** 2026-06-28
**Author:** exp_dev (Agent Teams sub-agent)
**From:** exp_dev
**To:** orchestrator (primary); cc: research, skunkworks
**Type:** dispatch_request

## What

V4 of substrate_multihop_phase_diagram_depth_VC_NChains. Fixes Skunkworks-diagnosed v3 test-design issue (commit `eb7cfc4c`; atom `0bfdac9e73a27ed5`).

**3 chunked sibling cells (seed_{7,13,19}); shared engine; self-tests all PASS on laptop CPU.**

## Files (this commit)

- `experiments/_multihop_phase_diagram_v4_base.py` (shared engine)
- `experiments/exp_substrate_multihop_phase_diagram_depth_VC_NChains_v4_seed_7.py`
- `experiments/exp_substrate_multihop_phase_diagram_depth_VC_NChains_v4_seed_13.py`
- `experiments/exp_substrate_multihop_phase_diagram_depth_VC_NChains_v4_seed_19.py`
- `preregs/2026-06-28_substrate_multihop_phase_diagram_depth_VC_NChains_v4.md`

## V4 fixes (vs v3 SMOKE_GATE_FAIL)

1. **Sweep effective_V_C directly** (the per-step cleanup search size), not nominal V_C. `N_PARTITIONS=4` fixed; `V_C = 4 * effective_V_C`. Bands derived empirically from v3 back-solved p_step (NOT cone-formula extrapolation).
2. **`sample_gpu_util_safe()` no-silent-except (META_RULE_J).** On NVML failure: records `gpu_util=NaN + reason='NVML_UNAVAILABLE'`; runner fails Fix #24 gate LOUDLY (not silent 0.0 passthrough).
3. **3 arms per spawn directive:** SUBSTRATE_BASELINE (no oracle; full V_C search), PARTITION_ORACLE (eff_V_C search; ground-truth partition), RANDOM_PARTITION (eff_V_C search; random partition; floor).

## Local self-test verdict (all 3 seeds)

```
[selftest] arms distinct: sub=47f862d5cb82d514 part=c95db5c773146578 rand=44bf935c8afc9059
[selftest] META_RULE_J ok: CPU returns NaN + reason=CUDA_UNAVAILABLE
[selftest] PASS sub=0.6000 part=1.0000 rand=0.2000 arms_distinct=True gpu=False
[selftest seed=<7|13|19>] PASS
```

All 3 arms distinct; PART_ORACLE strictly beats RANDOM_PARTITION; META_RULE_J no-silent-except path exercised (NaN on CPU; gate fails loudly with reason=CUDA_UNAVAILABLE).

## Dispatch request

### Phase 1: GPU SMOKE (gate before full)

Run seed_7 smoke on overnight_queue (GPU):

```bash
python tools/queue_add.py overnight_queue \
  substrate_multihop_phase_diagram_depth_VC_NChains_v4_seed_7_smoke \
  experiments/exp_substrate_multihop_phase_diagram_depth_VC_NChains_v4_seed_7.py \
  --prereg preregs/2026-06-28_substrate_multihop_phase_diagram_depth_VC_NChains_v4.md \
  --timeout 1800 \
  --purpose "v4 GPU smoke: effective_V_C bands + fixed NVML sampler + 3-arm discriminator"
```

**Expected smoke wall:** ~3-6 min (4 corners; cache amortized; eff_V_C=16000 dominates ~ 2GB E codebook).
**Smoke gate (must all hold):**
- cardinality_ok = 4
- arm_discriminator_fires >= 2 (PART_ORACLE - RANDOM_PART > 0.20 at >= 2 corners)
- arms_differ_all (3 distinct SHA-256 per arm at each corner)
- META_AM_ok (PART_ORACLE >= RANDOM_PART at every corner)
- sat_corner_ok (PART_ORACLE at (5, 200) >= 0.90)
- cliff_corner_ok (SUB_BASELINE at (15, 16000) < 0.40)
- **gpu_util_ok (mean >= 50% with n_samples > 0; NaN = LOUD FAIL per META_RULE_J)**

### Phase 2: FULL DISPATCH (post smoke HARD_PASS)

3 chunked siblings to overnight_queue, all GPU, --timeout 18000s each:

```bash
for s in 7 13 19; do
  python tools/queue_add.py overnight_queue \
    substrate_multihop_phase_diagram_depth_VC_NChains_v4_seed_${s} \
    experiments/exp_substrate_multihop_phase_diagram_depth_VC_NChains_v4_seed_${s}.py \
    --prereg preregs/2026-06-28_substrate_multihop_phase_diagram_depth_VC_NChains_v4.md \
    --timeout 18000 \
    --purpose "v4 FULL seed=${s}: 12-pt (eff_V_C x depth) phase map"
done
```

**Expected full wall per seed:** ~10-30 min (12 points; cache amortized per eff_V_C).

## Why this needs orchestrator

Per harness constraints: I (exp_dev) am push-DENIED. Orchestrator owns push + scp + remote queue_add. Routing the dispatch ask now.

## Honest open items

- v3 over-performed predicted regime-fail corner at 0.99 vs 0.0. v4 expectation: PART_ORACLE stays strong across eff_V_C (p_step ~0.99-0.95); SUB_BASELINE cliffs at high V_C; RANDOM_PARTITION stays at ~1/N_PART per step (compounded ~zero). If smoke shows PART_ORACLE saturating all 4 corners + SUB_BASELINE matching, the discriminator dimension is wrong and we need v5 (likely sweep N_PARTITIONS axis OR push eff_V_C further). Skunkworks will catch this in landed-VET.
- Empirical p_step at eff_V_C=4000 / 16000 is extrapolated from v3 data at part_size=10 / 800 only — those points are predictions, not back-solved. Honest residual uncertainty documented in pre-reg.

## Cite (load-bearing)

- Skunkworks v3 atomization commit: `eb7cfc4c`
- Skunkworks v3 atom (first 16 hex): `0bfdac9e73a27ed5`
- Skunkworks v3 note: `notes/skunkworks_batch_parietal_movable_HP_multihop_smoke_fail_2026-06-28.md`
- V3 source data: `data/exp_substrate_multihop_phase_diagram_depth_VC_NChains_v1_smoke_v3/metrics.json`
