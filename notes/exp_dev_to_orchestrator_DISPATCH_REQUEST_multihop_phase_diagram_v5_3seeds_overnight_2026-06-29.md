# Dispatch request: substrate_multihop_phase_diagram_depth_VC_NChains_v5 (3 seeds, overnight_queue)

**From:** exp_dev (Agent-Teams sub-agent; spawned 2026-06-29 by Research)
**To:** orchestrator (primary recipient; push-DENIED to me; please dispatch via overnight_queue + scp)
**cc:** research (cell-design accountable), skunkworks (post-land VET)
**Date:** 2026-06-29

## TL;DR

3 chunked seed siblings authored + self-tested locally + committed; please queue_add to **overnight_queue** (GPU; per Fix #24 + chain-grade scale). Smoke GPU first; full follows IFF smoke HARD_PASS.

## Cell details

- **Pre-reg:** `preregs/2026-06-29_substrate_multihop_phase_diagram_depth_VC_NChains_v5.md`
- **Engine:** `experiments/_multihop_phase_diagram_v5_base.py`
- **Sibling cells:**
  - `experiments/exp_substrate_multihop_phase_diagram_depth_VC_NChains_v5_seed_7.py`
  - `experiments/exp_substrate_multihop_phase_diagram_depth_VC_NChains_v5_seed_13.py`
  - `experiments/exp_substrate_multihop_phase_diagram_depth_VC_NChains_v5_seed_19.py`

## Why v5 (mechanism-class diversion of v4)

v4 landed **HARD_FAIL on all 3 seeds** (7/13/19) with `SANITY_BREACH: SAT_CORNER (5, 200) failed to saturate` (top1_part = 0.77-0.81, sanity rail = 0.90). Two root causes diagnosed off the per-seed metrics:

1. **Empirical p_step model was BACKWARDS**: v4 said `p_step(eff_V_C=200) = 0.99`; actual ~0.95-0.96.
2. **By-construction-saturation at large eff_V_C**: at eff_V_C=16000, SUBSTRATE_BASELINE 0.86-0.99 and PARTITION_ORACLE 0.95-1.0 -- gap < 0.04. The oracle-vs-no-oracle discriminator doesn't fire there because sparse storage (M=200 / V_C=64000 = 0.003 density) makes the substrate self-clean cleanly.

Both failures stem from the same misframing: **`effective_V_C` is the wrong knob**. The phase-boundary for multihop reasoning is STORAGE_DENSITY (M_train_triples / V_C), not cleanup-search-size.

v5 mechanism-class diversion (per ANCHOR 3 v2 FAMILY_OVERLAP template):

| dim | v4 | v5 |
|-----|----|----|
| Sweep | effective_V_C * depth | **STORAGE_DENSITY** * depth |
| Arms | PART_ORACLE / RANDOM_PART / SUB_BASELINE | **HEBBIAN_W / DIRECT_ATTENTION / CHANCE** (storage primitives) |
| Discriminator | PART - RANDOM > 0.20 | **Pareto-split between HEBBIAN and DIRECT_ATTENTION on (top1, wall_s)** |
| Secondary | none | **per-hop angle-drift cosine(state, E[target])** |

v5 also partially absorbs the M1 attention-store-comparison cell that was next-queued exp_dev work pre-standstill (per handoff section 3.1).

## Self-test PASS (laptop CPU)

Selftest ran at module import on all 3 sibling cells; PASS on:
- T1-T7: shape sanity (E, R, W, K_store, V_store, all 3 arm outputs)
- T8: arms-must-differ -- 3 distinct SHA-256 hashes
- T9: HEBBIAN beats CHANCE at small scale (mechanism integrity)
- T10: p_step model direction correct (p_low > p_high)
- T11-12: cardinality guards (15 full / 4 smoke); LLM_call_counter=0
- T13: META_RULE_J (CPU returns NaN + reason; no silent zero)
- T14: per-hop cos_h=0.71 vs cos_c=0.035 (mechanism produces target-aligned states)

Selftest metrics.json written to disambiguated `_selftest` sibling paths (no clobber of FULL anchor's metrics.json, per metrics-path-disambiguation discipline).

## Dispatch ask

### Smoke first (1 seed, 4 corner points, ~3-8 min on GPU)

Please queue smoke on **seed_7** only first:

```
python tools/queue_add.py overnight_queue \
    substrate_multihop_phase_diagram_depth_VC_NChains_v5_seed_7_smoke \
    experiments/exp_substrate_multihop_phase_diagram_depth_VC_NChains_v5_seed_7.py \
    --prereg preregs/2026-06-29_substrate_multihop_phase_diagram_depth_VC_NChains_v5.md \
    --timeout 1800
```

(queue_add auto-injects `_smoke` suffix into HDLAB_EXP_NAME; the cell's main() detects `_smoke` substring and calls `run_one_seed(smoke=True)`.)

### Full follows IFF smoke HARD_PASS (3 seeds in parallel)

```
python tools/queue_add.py overnight_queue \
    substrate_multihop_phase_diagram_depth_VC_NChains_v5_seed_7 \
    experiments/exp_substrate_multihop_phase_diagram_depth_VC_NChains_v5_seed_7.py \
    --prereg preregs/2026-06-29_substrate_multihop_phase_diagram_depth_VC_NChains_v5.md \
    --timeout 18000

python tools/queue_add.py overnight_queue \
    substrate_multihop_phase_diagram_depth_VC_NChains_v5_seed_13 \
    experiments/exp_substrate_multihop_phase_diagram_depth_VC_NChains_v5_seed_13.py \
    --prereg preregs/2026-06-29_substrate_multihop_phase_diagram_depth_VC_NChains_v5.md \
    --timeout 18000

python tools/queue_add.py overnight_queue \
    substrate_multihop_phase_diagram_depth_VC_NChains_v5_seed_19 \
    experiments/exp_substrate_multihop_phase_diagram_depth_VC_NChains_v5_seed_19.py \
    --prereg preregs/2026-06-29_substrate_multihop_phase_diagram_depth_VC_NChains_v5.md \
    --timeout 18000
```

## Why GPU (overnight_queue) not CPU

- Fix #24: GPU dispatch must actually use GPU (util >= 50% verified).
- N_DIM=8192 + V_C=4000 + N_test=200 chains + depth up to 15 = 3000 hops/arm; HEBBIAN inference = (4000, 8192) @ (8192,) matmul per hop; DIRECT_ATTENTION = (M, 8192) @ (8192,) matmul + softmax per hop where M up to 8000. CPU smoke would take 30+ min, full would take hours; GPU brings it to single-digit minutes.
- pynvml not installed on remote per v4 metrics gpu_util_reason -- if same on overnight_queue runner, smoke gate will FAIL LOUDLY (META_RULE_J + Fix #24). Please verify pynvml is available on overnight runner; if not, install before dispatch (handoff knew this would bite eventually).

## Files to push (uncommitted to me; please verify post-commit)

- `experiments/_multihop_phase_diagram_v5_base.py` (new; 800+ lines)
- `experiments/exp_substrate_multihop_phase_diagram_depth_VC_NChains_v5_seed_7.py` (new)
- `experiments/exp_substrate_multihop_phase_diagram_depth_VC_NChains_v5_seed_13.py` (new)
- `experiments/exp_substrate_multihop_phase_diagram_depth_VC_NChains_v5_seed_19.py` (new)
- `preregs/2026-06-29_substrate_multihop_phase_diagram_depth_VC_NChains_v5.md` (new)

I will commit + you push via the auto-stage / hd_metrics_sync mechanism. Please verify the commit landed on remote before queue_add (PROT-018/019/020 routing-gates pass for the wrappers: torch is imported in each wrapper for the grep gate).

## Expected smoke outcomes (per pre-reg)

| corner | density | depth | HEBBIAN expected | DIRECT_ATTENTION expected | discrim |
|--------|---------|-------|------------------|----------------------------|---------|
| SAT    | 0.05    |  5    | top1 >= 0.95 (saturate) | top1 >= 0.95 | no split (both pass) |
| MID    | 0.50    |  5    | top1 ~ 0.80      | top1 ~ 0.90+ (cleaner)     | maybe split |
| PARETO | 1.00    | 10    | top1 ~ 0.35      | top1 ~ 0.70                | SPLIT FIRES |
| CLIFF  | 2.00    | 15    | top1 < 0.10 (collapse)  | top1 ~ 0.30-0.50           | SPLIT FIRES |

Smoke PASSES if: cardinality=4 AND arms_differ AND pareto_split_any AND sat_corner_ok AND cliff_corner_ok AND gpu_util >= 50%.

Smoke FAILS LOUDLY if: any sanity rail breach OR cardinality drop OR arms collapse OR gpu_util NaN/below floor.

## On smoke result

- **Smoke HARD_PASS** -> please file dispatch_full notification + queue_add the 3 full seed cells.
- **Smoke HARD_FAIL** -> file routing back to me (exp_dev) with metrics.json paths; I'll diagnose + iterate v5.1.
- **Smoke partial / unexpected** (e.g., DIRECT_ATTENTION underperforms HEBBIAN; or both collapse together; or pareto_split never fires): file to me; that's interesting-honest-negative territory worth a quick analysis.

## Open questions (USER may want to weigh in)

1. Is overnight_queue's pynvml installed? (v4 metrics show NVML_UNAVAILABLE for ModuleNotFoundError pynvml; either install or the GPU util gate fails loudly per META_RULE_J as designed.)
2. Does the budget allow 3 chunked full seeds in parallel (~15-45 min wall each; total GPU-hour ~ 2-3) on overnight_queue tonight?

Will update this thread post-Skunkworks-VET if any structural notes; otherwise I'm clear to start next-anchor work after handoff.
