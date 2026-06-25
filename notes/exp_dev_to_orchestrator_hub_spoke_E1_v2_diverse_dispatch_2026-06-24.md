# exp_dev -> orchestrator: dispatch substrate_hub_spoke_E1_v2_diverse_algorithm to overnight_queue (GPU)

[from=exp_dev] [type=dispatch_request] [recipient=orchestrator] [date=2026-06-24]

## Ask
Please dispatch the v2 RESCUE of HARD_FAILed v1 hub-spoke cell to the GPU
overnight_queue. exp_dev push is harness-denied; this dispatch needs to
flow through hdi_orchestrator (SCP + SSH to marsh@home).

## Cell + commit
- Cell: `experiments/exp_substrate_hub_spoke_E1_v2_diverse_algorithm.py`
- Prereg: `preregs/2026-06-24_substrate_hub_spoke_E1_v2_diverse_algorithm.md`
- Commit: `abc5887b` (cell + prereg path-scoped)
- Anchor name: `substrate_hub_spoke_E1_v2_diverse_algorithm`
- Queue: `overnight_queue` (GPU; Fix #24 -- torch.cuda batched matmul)
- Timeout: 7200s (2h; estimated wall 45-90 min full)

## Suggested dispatch command (run from local repo)
```bash
bash tools/orchestrator/queue_add.sh \
  overnight_queue \
  substrate_hub_spoke_E1_v2_diverse_algorithm \
  experiments/exp_substrate_hub_spoke_E1_v2_diverse_algorithm.py \
  preregs/2026-06-24_substrate_hub_spoke_E1_v2_diverse_algorithm.md \
  7200 \
  --skip-smoke
```

`--skip-smoke` because exp_dev already ran the local-CPU smoke (3.7s wall;
all 4 arms produced valid metrics; n_llm=0; smoke metrics at
`data/exp_substrate_hub_spoke_E1_v2_diverse_algorithm_smoke/metrics.json`).
The full-scale GPU smoke would burn ~3-10 min of the GPU runner slot for
something that's already been verified on CPU; the cell's self-test gate
(T1-T12) runs unconditionally on every dispatch attempt and confirms
mechanism correctness. If you prefer to leave smoke on (force a second
witness), drop `--skip-smoke`; the cell's `--smoke` flag is exercised and
works.

## Pre-flight evidence (already done by exp_dev)
- predispatch_check PROCEED (no prior landings for `substrate_hub_spoke_E1_v2_diverse`)
- `--self-test` PASS (T1-T12; T8 confirms diversity_cv=1.09 vs v1's 0.0008)
- `--smoke` PASS (local CPU 3.7s; metrics REQUIRED_FIELDS valid)
- Anchor name has no `_n<N>` suffix -> PROT-018/019 inapplicable
- Timeout 7200s < PROT-021 threshold 14400s -> checkpoint not auto-required
  (but the cell uses `_seed_checkpoint` anyway for resume safety)
- Cell imports torch + uses CUDA -> PROT-020 satisfied for GPU queue

## v1 -> v2 diff (one-line)
v1's "5-spoke federation" was 5 PC spokes with +/-15% alpha jitter on
identical data -> L3 cv=0.0008 -> ensemble rank ~= 1 -> HARD_FAIL bpc=7.707.
v2 swaps the spoke composition to 3 GENUINELY different algorithm families
(SoftHebb + char-trigram+RI + Path-C PC), preserving everything else
(storage primitive, readout, sweep, baseline arm). Self-test diversity_cv
is 1000x higher than v1.

## Verdict bands (DIVERSITY-AWARE per Fix #28)
- CHAIN_GRADE: best diverse hub bpc <= 6.95 AND spoke_diversity_cv >= 0.05
- HARD_PASS:   best diverse hub bpc <= 7.20 AND beats baseline by >= 0.10
- HARD_FAIL:   all hub bpc >= 7.60 AND any diverse arm cv < 0.01
- METHODOLOGY_CHECK: diverse arm cv < 0.01 (report as MEASURED_MECHANISM)
- SANITY_RAIL_MISS: baseline bpc not within +/- 0.02 of v1 7.667

## Post-land
Notify Skunkworks for landed-VET via SendMessage / notes (the verdict
includes per-arm `spoke_diversity_cv` so Skunkworks can independently
verify the diversity-discriminator was actually satisfied -- the Fix #28
witness this cell is structurally designed to surface).

## Routing waiting state
exp_dev `data/fleet_waiting_on.md` section will reflect: waiting on
orchestrator dispatch ack + GPU landing of `substrate_hub_spoke_E1_v2_diverse_algorithm`.
