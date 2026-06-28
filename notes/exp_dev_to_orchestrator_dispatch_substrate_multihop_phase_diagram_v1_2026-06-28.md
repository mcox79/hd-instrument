# DISPATCH REQUEST: substrate_multihop_phase_diagram_depth_VC_NChains_v1

**From:** exp_dev (cell-author sub-agent)
**To:** orchestrator
**Date:** 2026-06-28
**Pause flag:** NOT_PAUSED (verified before file)
**Commit:** 1e6e104a (hd_metrics_sync auto-staged; awaits next push to origin/main)

## What

Ship the FIRST Layer-1 phase-diagram MAP cell for substrate-product portfolio (USER strategic directive). Maps multi-hop reasoning over (depth x V_C x N_chains) cube. Anchored on v1 chain-grade 15-hop=0.808.

## Files (committed; pending push)

- `experiments/exp_substrate_multihop_phase_diagram_depth_VC_NChains_v1.py`
- `preregs/2026-06-28_substrate_multihop_phase_diagram_depth_VC_NChains_v1.md`

## Status

- **Local self-test:** PASS (arms_differ SHA-256 verified; formula reproduces v1 anchor 15-hop=0.808 exact; SUBSTRATE=1.0 RANDOM=0.0 at small substrate)
- **CRLB compute:** done in Python pre-pre-reg; 26/40 points predicted discriminable
- **Local CPU smoke:** NOT_RUN (laptop has NO CUDA; Fix #24 requires real GPU for util gate)
- **Local push:** harness-DENIED to exp_dev per role spec; relying on hd_metrics_sync

## Dispatch ask (TWO actions)

### Action 1: SMOKE first (4 corners; GPU)

```bash
bash tools/orchestrator/queue_add.sh overnight_queue \
  exp_substrate_multihop_phase_diagram_depth_VC_NChains_v1_smoke \
  experiments/exp_substrate_multihop_phase_diagram_depth_VC_NChains_v1.py \
  preregs/2026-06-28_substrate_multihop_phase_diagram_depth_VC_NChains_v1.md \
  600
```

(timeout 600s = 10 min; 4 corners x ~7min each on GPU = ~28 min worst case but cache amortizes across depth queries so ~10 min real)

### Action 2: FULL after smoke HARD_PASS (40 points; GPU)

```bash
bash tools/orchestrator/queue_add.sh overnight_queue \
  exp_substrate_multihop_phase_diagram_depth_VC_NChains_v1 \
  experiments/exp_substrate_multihop_phase_diagram_depth_VC_NChains_v1.py \
  preregs/2026-06-28_substrate_multihop_phase_diagram_depth_VC_NChains_v1.md \
  18000
```

(timeout 18000s = 5h; 40 points; cache amortizes 8 (V_C, N_chains) pairs across 5 depths each)

## Smoke gate (must pass before Action 2)

Implemented in `verdict_smoke()` in the cell:
- cardinality_ok: observed == 4
- arm_discrim_count >= 2 (SUBSTRATE - RANDOM > 0.20 at >= 2 corners)
- saturation_observed at corner (5, 200, 50)
- regime_fail_observed at corner (15, 16000, 200)
- arms_differ_all SHA-256 across 4 corners
- sat_corner_ok: top1 >= 0.95 at (5, 200, 50)
- cross_cell_ok: top1 in [0.75, 0.86] at (15, 200, 200) [reproduces v1 0.808]
- fail_corner_ok: top1 < 0.10 at (15, 16000, 200)
- gpu_util_ok: mean util >= 50% (Fix #24)

## CRLB pre-validation table (computed Python pre-dispatch)

```
depth   V_C  N_ch  p_step  top1_pred  rand_floor
  5    200    50   0.9965    0.9824   0.005000  <- SATURATION SMOKE CORNER
 15    200   200   0.9859    0.8082   0.005000  <- V1 RAIL SMOKE CORNER
  5  16000    50   0.7528    0.2417   0.000063  <- DISCRIMINATOR SMOKE CORNER
 15  16000   200   0.3211    0.0000   0.000063  <- REGIME-FAIL SMOKE CORNER

26/40 points predicted discriminable (top1_pred > 5x random_floor)
```

## After-landing handoff

- Skunkworks: landed-VET on full-grid phase map; classify per-point tiers; emit phase-map atom (chain-grade if >= 50% PASS; cliff coordinates atomized regardless)
- Research: Layer-2 phase-operations design (which procedure to switch to in REGIME_BOUNDS_NARROW region) gated on this landing

## Notes

- Cell is GPU-native; CPU fallback will not pass Fix #24 util gate
- Single-seed phase-map per point (no cross-seed CV; each point has 50-200 chain trials internally)
- W matrices cached per (V_C, N_chains) pair; reused across depth queries for the same pair
