# exp_dev dispatch request -- substrate_pc_hierarchy_fair_harness_v1
## [from=exp_dev] [type=dispatch_request] [recipient=hdi_orchestrator] 2026-06-24T15:20Z

## Ask
Push origin/main + dispatch `substrate_pc_hierarchy_fair_harness_v1` to
`overnight_queue` (GPU, marsh@home) with timeout 14400s.

## Why
Meta-skepticism drill Anchor 1 (USER 2026-06-24). Resolves A12 contradiction (PC
hierarchy chain-grade for 5-corpus aggregation BUT degraded capacity 0.25x).
Prior cells SUSPENDED METHCONF per cert row 588; re-tests under fair_harness rail.

## Status (exp_dev complete; awaiting Orchestrator push + queue_add)
- Local commit: `106e74e5` on `main` (cell + prereg + smoke metrics).
- predispatch_check: PROCEED (0 matching landings; 0 atoms; fresh anchor).
- Selftest: PASS (T1-T10 including PC layers + cf-RPE + verdict bands).
- Smoke: PASS (84s laptop CPU; all 4 arms finite; SANITY_RAIL_FAIL expected at
  smoke scale because 7.3065 ref is full-scale V=4000).
- REQUIRED_FIELDS verified in smoke metrics.json.

## Dispatch parameters
- Queue: `overnight_queue` (GPU; routes through marsh@home reading origin/main)
- Entry name: `substrate_pc_hierarchy_fair_harness_v1`
- Script: `experiments/exp_substrate_pc_hierarchy_fair_harness_v1.py`
- Prereg: `preregs/2026-06-24_substrate_pc_hierarchy_fair_harness_v1.md`
- Timeout: 14400s (4h safety margin on 3-4h GPU wall estimate)
- Anchor has no `_n<N>` suffix => PROT-018/019 not applicable
- PROT-021: cell uses `_seed_checkpoint` for per-seed resume; satisfies >=14400 requirement
- GPU REQUIRED per Fix #24 (torch.cuda for matmul / PC training / sparse-bipolar)

## Pre-reg HARD bands (full summary)
- Sanity rail (load-bearing; FAIL aborts interpretation): ARM_RANK_1_BASELINE BPC
  within +/- 0.05 of 7.3065.
- HARD_PASS: any PC arm beats RANK_1 by >= 0.05 top-1 OR >= 0.05 BPC under
  selection-mixer joint (T, lambda) sweep.
- MIDDLE_BAND: top-1 lift in [0.02, 0.05).
- HARD_FAIL: all PC arms <= RANK_1 on all 3 metrics.
- CHAIN_GRADE_BONUS: any PC arm top-1 >= 0.55.

## Cell-author findings during authoring (atomized in prereg)
- cf-RPE refinement on PC features requires zero-init W_pred + L2-normalized
  top_out. Initial design re-used Hebbian-init W_pred + raw bipolar top_out
  (norm = sqrt(dim) ~ 22.6 for dim=512); cf-RPE updates diverged geometrically
  (W_pred norm doubled ~ every 2 steps to inf at step 50). Fix: discard Hebbian
  W_pred for cf-RPE arm; start cf-RPE from W_pred=0; L2-normalize top_out per row;
  forward at inference uses `l2_top=True` to match training scale. Worth atomizing
  as discipline: "cf-RPE refinement scale-matching of training inputs is
  load-bearing; bipolar features must be L2-normalized before cf-RPE update."

## Routing rationale per dispatch architecture
- Push is harness-DENIED to exp_dev session; only `hd_metrics_sync` authorized
  to push. GPU/overnight + remote_cpu queues both read origin/main on marsh@home.
- Therefore: Orchestrator owns push + queue_add for this anchor.
- Local commit is path-scoped to 3 files (cell + prereg + smoke metrics); no
  blanket-add risk to canonical Store partition.

## Expected verdict-handler flow
- Land -> Skunkworks landed-VET (recompute lifts off per_unit; check cv).
- If HARD_PASS: chain-grade-eligible (USER Anchor 1 resolved; hierarchy IS LM-lift
  regime). Route to atomization + hdlab/ primitive update if appropriate per
  results-to-application cadence (USER 2026-06-22).
- If HARD_FAIL: A12 resolved DOWNWARD (hierarchy is capacity-degradation regime
  only); SUSPENDED METHCONF cells (588) now CONFIRMED HARD_FAIL under fair harness.
- If MIDDLE_BAND: partial signal; route to Research for 2x-revival drill (per
  standing rule).
- If SANITY_RAIL_FAIL: harness drift detected; back to exp_dev for harness
  recalibration BEFORE PC interpretation.

## Files
- experiments/exp_substrate_pc_hierarchy_fair_harness_v1.py
- preregs/2026-06-24_substrate_pc_hierarchy_fair_harness_v1.md
- data/exp_substrate_pc_hierarchy_fair_harness_v1_smoke/metrics.json
- (commit 106e74e5)

End.
