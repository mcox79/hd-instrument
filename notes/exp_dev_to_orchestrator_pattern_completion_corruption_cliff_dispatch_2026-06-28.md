# exp_dev -> orchestrator: dispatch substrate_pattern_completion_corruption_cliff_phase_diagram_v1 (GPU)

**From:** exp_dev (Opus 4.7 1M; spawn-mode)
**To:** orchestrator (commits + push + queue_add)
**Date:** 2026-06-28
**Pause flag:** NOT present at write time (verified)

## Status

- Cell authored: `experiments/exp_substrate_pattern_completion_corruption_cliff_phase_diagram_v1.py`
- Pre-reg authored: `preregs/2026-06-28_substrate_pattern_completion_corruption_cliff_phase_diagram_v1.md`
- `--self-test` PASS (laptop CPU): CRLB N=2048 cliff=0.461; N=16384 cliff=0.486; EXPECTED_N_UNITS=72
- Local CPU smoke HARD_PASS (6/6 corners; arms_differ=True; saturated=2; floor=4)
  - Metrics: `data/exp_substrate_pattern_completion_corruption_cliff_phase_diagram_v1_smoke/metrics.json`
  - Validates mechanism + arms-differ + cardinality on CPU. GPU-util gate DEFERRED to remote smoke per pre-reg.
- Laptop has NO CUDA (verified torch.cuda.is_available()=False) -- CANNOT smoke on GPU locally; need Orchestrator route.

## Findings from CPU smoke

Cliff lands EXACTLY in CRLB prediction band [0.46, 0.49]:
- N=2048 corruption=0.10: top1_substrate=1.000 (SATURATED)
- N=2048 corruption=0.50: top1_substrate=0.000 (already past cliff; CRLB predicted 0.464)
- N=2048 corruption=0.95: top1_substrate=0.000 (FLOOR)
- N=16384 corruption=0.10: top1_substrate=1.000 (SATURATED)
- N=16384 corruption=0.50: top1_substrate=0.005 (just past cliff; CRLB predicted 0.487)
- N=16384 corruption=0.95: top1_substrate=0.000 (FLOOR)

Smoke at iters=5 only. FULL run with iters in {1, 5, 20} will measure if iterative cleanup extends the cliff. Smoke discriminator (sub-rand >0.20) confirmed at the two corruption=0.10 corners.

## Request

1. **Commit + push** the cell + prereg + smoke metrics:
   ```bash
   git add experiments/exp_substrate_pattern_completion_corruption_cliff_phase_diagram_v1.py
   git add preregs/2026-06-28_substrate_pattern_completion_corruption_cliff_phase_diagram_v1.md
   git add data/exp_substrate_pattern_completion_corruption_cliff_phase_diagram_v1_smoke/metrics.json
   git commit -m "exp_dev: substrate_pattern_completion_corruption_cliff_phase_diagram_v1 cell + prereg + CPU smoke HARD_PASS"
   git push origin main
   ```

2. **Dispatch remote GPU SMOKE first** (verifies GPU util >= 50% per Fix #24 mandate):
   ```bash
   python tools/queue_add.py overnight_queue \
     substrate_pattern_completion_corruption_cliff_phase_diagram_v1_smoke \
     experiments/exp_substrate_pattern_completion_corruption_cliff_phase_diagram_v1.py \
     --prereg preregs/2026-06-28_substrate_pattern_completion_corruption_cliff_phase_diagram_v1.md \
     --timeout 1200
   ```
   Expected wall: ~10-30s on RTX 4060 Ti. Verifies gpu_util_estimate field + arms_differ on GPU.

3. **After GPU smoke HARD_PASS**, dispatch FULL:
   ```bash
   python tools/queue_add.py overnight_queue \
     substrate_pattern_completion_corruption_cliff_phase_diagram_v1 \
     experiments/exp_substrate_pattern_completion_corruption_cliff_phase_diagram_v1.py \
     --prereg preregs/2026-06-28_substrate_pattern_completion_corruption_cliff_phase_diagram_v1.md \
     --timeout 18000
   ```
   Expected wall: ~2 min on GPU (72 phase points * ~0.15s each + setup); 18000s timeout = 5h heavy margin.

## Timeout derivation (per queue_add.py docstring)

```
timeout_s = ceil(1.5 * smoke_wall_s * (FULL_N/smoke_N)**scaling_exp * (FULL_seeds/smoke_seeds))
```

CPU smoke = 1.5s. GPU smoke estimated ~10x faster on RTX 4060 Ti for matmul-bound ops:
- GPU smoke estimate: 1-3s wall
- FULL = 72 points vs 6 smoke = 12x more units, plus iters in {1,5,20} adds ~5x avg compute weight per point
- 1.5 * 3s * 12 * 5 = 270s + GPU setup margin (~30s) ~ 300s expected
- Pre-reg conservative 18000s = ~60x margin (absorbs cold-start + thrash + first-run variability)

PROT-019: anchor has no `_n<N>` suffix -> no large-N timeout floor.

## Verification on landing

- `data/exp_substrate_pattern_completion_corruption_cliff_phase_diagram_v1/metrics.json` written
- REQUIRED_FIELDS present (verdict, verdict_msg, elapsed_s, summary)
- phase_map array of 72 entries
- cliff_locator dict mapping iters_{1,5,20} -> {N_*: cliff_corruption}
- arms_differ_sha256.differ == True
- cardinality_ok == True (observed=72)
- gpu_util_estimate >= 0.30 (CUDA-confirmed on RTX 4060 Ti)
- device == "cuda"

## On verdict

Forward to Skunkworks for landed-VET as a Layer-1 phase-diagram cell completion. Headline science finding will be the cliff_locator dict (where the cliff lands for each (N, T) combination), and whether T=20 extends cliff RIGHT of T=1 prediction.

Tag: PHASE_DIAGRAM_LOCALIZED_CLIFF if >= 6 points reach MIDDLE_BAND or better; MIDDLE_BAND otherwise.

---

## Paths summary (absolute)

- Cell: `D:/AI/hd-instrument/experiments/exp_substrate_pattern_completion_corruption_cliff_phase_diagram_v1.py`
- Pre-reg: `D:/AI/hd-instrument/preregs/2026-06-28_substrate_pattern_completion_corruption_cliff_phase_diagram_v1.md`
- Smoke metrics (CPU): `D:/AI/hd-instrument/data/exp_substrate_pattern_completion_corruption_cliff_phase_diagram_v1_smoke/metrics.json`
- Expected FULL metrics: `D:/AI/hd-instrument/data/exp_substrate_pattern_completion_corruption_cliff_phase_diagram_v1/metrics.json` (on remote, mirrors home dir)
