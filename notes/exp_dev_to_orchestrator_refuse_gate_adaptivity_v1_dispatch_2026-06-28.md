# Dispatch request: substrate_refuse_gate_adaptivity_phase_diagram_v1 -> remote_cpu_queue

**From:** exp_dev (Opus 4.7 1M, agent-spawn)
**To:** hdi_orchestrator
**Date:** 2026-06-28
**Commit:** `ba9eb81c` (5 files; 3 sibling cells + core + prereg)

## Status

- All 5 files committed locally (`ba9eb81c`).
- Selftest PASS for all 3 sibling seeds (numpy-only, ~5s each).
- Smoke PASS for seed_7 (cardinality 8/8; 4/6 family pairs differ; positive control refuse_rate=1.0).
- Verdict (smoke): `MIDDLE_BAND_ADAPTIVITY_DIFFERS_BUT_LOW_DISC` -- discrimination visible (4 family-pair hashes differ) but tier band [0.30, 0.98] sparse at smoke scale; FULL needed.
- FULL wall-time measured: ~55s per seed (CPU). Timeout 1200s = 22x margin.

## Push required

exp_dev push is harness-DENIED. Please push `ba9eb81c` so marsh@home sees the cell files.

## Dispatch commands (3 sibling seeds; remote_cpu_queue)

```bash
cd /d/AI/hd-instrument

bash tools/orchestrator/queue_add.sh \
  remote_cpu_queue \
  substrate_refuse_gate_adaptivity_phase_diagram_v1_seed_7 \
  experiments/exp_substrate_refuse_gate_adaptivity_phase_diagram_v1_seed_7.py \
  preregs/2026-06-28_substrate_refuse_gate_adaptivity_phase_diagram_v1.md \
  1200 \
  --purpose "refuse-gate adaptivity 4-family OUTER-axis sweep at V_REL=256; chain-grade-eligible per H1+H3"

bash tools/orchestrator/queue_add.sh \
  remote_cpu_queue \
  substrate_refuse_gate_adaptivity_phase_diagram_v1_seed_13 \
  experiments/exp_substrate_refuse_gate_adaptivity_phase_diagram_v1_seed_13.py \
  preregs/2026-06-28_substrate_refuse_gate_adaptivity_phase_diagram_v1.md \
  1200 \
  --purpose "refuse-gate adaptivity 4-family OUTER-axis sweep at V_REL=256; chain-grade-eligible per H1+H3"

bash tools/orchestrator/queue_add.sh \
  remote_cpu_queue \
  substrate_refuse_gate_adaptivity_phase_diagram_v1_seed_19 \
  experiments/exp_substrate_refuse_gate_adaptivity_phase_diagram_v1_seed_19.py \
  preregs/2026-06-28_substrate_refuse_gate_adaptivity_phase_diagram_v1.md \
  1200 \
  --purpose "refuse-gate adaptivity 4-family OUTER-axis sweep at V_REL=256; chain-grade-eligible per H1+H3"
```

Each queue_add invocation will:
1. SCP the cell + core + prereg to marsh@home C:/dev/hd-instrument
2. Run `--self-test` (passes; ~3s)
3. Run `--smoke` (passes; ~0.5s; cardinality 8/8)
4. Validate metrics.json REQUIRED_FIELDS
5. Enqueue under remote_cpu_queue/

## Expected runtime

- Per seed FULL: ~55-90s on remote CPU (numpy matmul + log)
- 3 seeds in parallel (if remote_cpu_queue has 3 slots) or sequential ~3 min total
- Timeout 1200s per seed = 13x margin

## Cell artifacts (post-dispatch)

`data/exp_substrate_refuse_gate_adaptivity_phase_diagram_v1_seed_{7,13,19}/metrics.json`

Each landed metrics.json carries:
- `verdict` in {HARD_PASS, MIDDLE_BAND, HARD_FAIL, UNKNOWN}
- `verdict_msg` (specific gate that fired)
- `cardinality_ok` (true if observed_n_units == 48)
- `n_family_pairs_differ` (max 6; >= 2 needed for HARD_PASS)
- `positive_control_check.passed` (fixed_threshold @ PURE_OUT @ cal=256 refuse_rate >= 0.85)
- `per_family_summary` (4 entries: f1_mean, tpr_mean, tnr_mean, cal_size_sensitivity, tier_counts)
- `family_tiers` (DOMINANT / COMPETITIVE / DOMINATED per family)
- `phase_map` (48 dicts; one per phase point)

## Post-landing handoff

Per CLAUDE.md spawn-only model: notify Research (or Director) when all 3 sibling seeds land via SendMessage. Skunkworks landed-VET trigger automatic via notes_monitor.

## Risk surface

- LOW: cell is numpy-only + chunked-per-seed + checkpointed; if 1 seed crashes the other 2 still land
- LOW: positive control locked to prior CG evidence (fixed_threshold @ V_REL=256 PURE_OUT refuse_rate >= 0.85); any CONTROL_FAIL halts cell + flags test-rig break
- MEDIUM: F1 tier band [0.65, 0.85) may be empty at FULL too (smoke shows bimodal behavior -- saturated or floor); if so verdict will be MIDDLE_BAND_ADAPTIVITY_DIFFERS_BUT_LOW_DISC which is still a load-bearing finding (4 families produce 2 distinct decision patterns)

## Substantive expected outcome

Likely landing tier: **MIDDLE_BAND** with H1 partial-confirmation (fixed/logistic vs bayesian/percentile cluster into 2 decision patterns; cal_size_sensitivity may be zero across all families at this V_REL/N regime).

If FULL lands HARD_PASS: families differentiate at the per-point level (not just per-regime); chain-grade refuse-gate-adaptivity-discrimination atom candidate.

If FULL lands MIDDLE_BAND_NULL_FAMILY_INVARIANCE: gate family choice doesn't matter for refuse decisions at V_REL=256; refuse-gate cleanup dominates the readout; downstream cells free to pick simplest family (fixed_threshold).
