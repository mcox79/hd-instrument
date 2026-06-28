# exp_dev -> orchestrator: dispatch parietal_phase_diagram_v1 (3 seeds) to remote_cpu_queue

**Date:** 2026-06-28
**Commit:** 1acabb228b4bf5b4d9af463dc18b543e40cb7350
**Pre-reg:** preregs/2026-06-28_substrate_parietal_movable_rebind_phase_diagram_v1.md

## Smoke verdict (seed_7, local CPU)
**HARD_PASS:** n_sat=3 n_fail=1 n_strong=3 arms_distinct=True (elapsed 7.3s)
- (grid=8, n_obj=8, mf=0.5): substrate=1.000 static=0.000 (rebind discriminator fires)
- (grid=16, n_obj=20, mf=0.5): substrate=1.000 static=0.000
- (grid=32, n_obj=200, mf=0.5): substrate=0.250 static=0.000 (CLIFF at over-cap)
- (grid=4, n_obj=8, mf=0.0): substrate=1.000 static=1.000 (sanity: no-rebind baseline)

Arms SHA-256 distinct (META_RULE_AF PASS):
- substrate: a76c5966...
- random:    9bfe702c...
- static:    57ee4a85...

META_RULE_AM PASS (no point with substrate <= random + 0.02).

## Dispatch ask
Please `bash tools/orchestrator/queue_add.sh remote_cpu_queue` the following 3 FULL cells:

1. `substrate_parietal_movable_rebind_phase_diagram_v1_seed_7`
   - script: `experiments/exp_substrate_parietal_movable_rebind_phase_diagram_v1_seed_7.py`
   - prereg: `preregs/2026-06-28_substrate_parietal_movable_rebind_phase_diagram_v1.md`
   - timeout: 4500s (estimate ~100-200s; generous ceiling for phase-diagram)

2. `substrate_parietal_movable_rebind_phase_diagram_v1_seed_13` (same script suffix _seed_13.py)
3. `substrate_parietal_movable_rebind_phase_diagram_v1_seed_19` (same script suffix _seed_19.py)

Each runs the same 56-point sweep at seed = {7, 13, 19} respectively.

## Why remote_cpu_queue
- numpy-only; FHRR complex64 ops; no GPU acceleration needed
- ~56 points * 20 scenes * 3 arms ≈ 3360 evaluations per seed; CPU-friendly
- remote_cpu_queue is currently the chunked-cell standard per CHUNKED architecture rule

## Expected FULL output
- Each seed writes `data/exp_substrate_parietal_movable_rebind_phase_diagram_v1_seed_<N>/metrics.json`
- HARD_PASS criteria (per pre-reg): cardinality_ok=56, arms_distinct, no META_AM_breach, >=30% points with lift_over_static>=0.30, >=1 saturate AND >=1 cliff
- Phase-diagram structure: cliff predicted at n_obj=100-200, especially at large grid

## REMOTE VERIFY ask
After scp + ssh queue_add, please confirm:
- `experiments/_parietal_phase_diagram_v1_base.py` + 3 sibling scripts on remote at commit 1acabb22
- `preregs/2026-06-28_substrate_parietal_movable_rebind_phase_diagram_v1.md` on remote
- queue.json on remote shows 3 entries (NOT just local data/remote_cpu_queue/queue.json)

## Coordination
- Skunkworks: notify on landing for landed-VET (chain-grade-eligible: phase diagram with predicted cliff structure for parietal MOVABLE-rebind primitive)
- Research: aware via this teammate (sub-agent spawn-only architecture; this routing-note path is per Orchestrator's lane)

exp_dev (hdi_exp_dev sub-agent)
