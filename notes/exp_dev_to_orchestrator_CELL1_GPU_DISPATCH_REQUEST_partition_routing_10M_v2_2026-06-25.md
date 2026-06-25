# Orchestrator: GPU dispatch request — partition_routing_10M v2 (Cell 1 of 5-cell USER batch)

**From:** exp_dev
**To:** orchestrator
**Filed:** 2026-06-25T16:00:00Z
**Type:** dispatch_request
**Anchor:** substrate_partition_routing_10M_full_v2
**Queue:** overnight_queue (GPU)
**Reason:** push is harness-DENIED to exp_dev; need Orchestrator to dispatch.

## Cell-spec

- **Script:** `experiments/exp_substrate_partition_routing_10M_full_v2.py` (commit c20f5d75)
- **Prereg:** `preregs/2026-06-25_substrate_partition_routing_10M_full_v2.md`
- **Smoke metrics:** `data/exp_substrate_partition_routing_10M_full_v2_smoke/metrics.json` (HARD_PASS routed=0.9667 @ N=100k cv=0 1 seed)
- **Seeds:** [11, 13, 19] (cross-cell consistent with today's 5-cell batch)
- **N_SWEEP:** [10000, 100000, 1000000]
- **PART_SIZE:** 2000 (LOCKED across smoke/full; USER directive)
- **Timeout:** 3600s (1 hour; per prereg estimate)
- **Routing:** overnight_queue (per Fix #24: torch.cuda explicit; matmul-dominated chunked queries)

## Dispatch command

```bash
cd d:/AI/hd-instrument && bash tools/orchestrator/queue_add.sh \
  overnight_queue \
  substrate_partition_routing_10M_full_v2 \
  experiments/exp_substrate_partition_routing_10M_full_v2.py \
  preregs/2026-06-25_substrate_partition_routing_10M_full_v2.md \
  3600 \
  --purpose "Cell 1 of 5-cell USER 2026-06-25 batch: partition-routing 10M v2 3-seed FULL promotion — closes substrate-product KG envelope at M=100k+ if HARD_PASS"
```

PROT compliance (verified):
- PROT-018 (`_n<N>` suffix): N/A (no `_n<N>` in anchor name)
- PROT-019 (timeout floor): N/A
- PROT-020 (GPU queue requires torch): VERIFIED `import torch` at line 105
- PROT-021 (long timeout needs checkpoint): VERIFIED `from experiments._seed_checkpoint import ...` at line 46

## Strategic significance (Cell 1 = HIGHEST PRIORITY)

If full at N=1M holds:
- Substrate KG chain-grade to 1M atoms via partition-routing.
- Closes substrate-product KG envelope question Cell B's dense-KV cliff at M=50k left open.
- The partition-routing rescue PRIMITIVE becomes chain-grade-eligible (currently smoke-only).

If full at N=100k holds but 1M fails:
- CHAIN_GRADE_AT_LOWER_M_CLIFF tier; envelope = 100k via partition-routing (still beats dense-KV's 50k cliff by 2x).

If 100k fails:
- HARD_FAIL_PARTITION_DEGRADES; v1 smoke result was artifact.

## Smoke run vs full diff

- smoke: 1 seed (11), N=[10k,100k], CPU fallback OK
- full: 3 seeds [11,13,19], N=[10k,100k,1M], requires GPU

Smoke verified per-N partition rebuild + verdict logic working correctly. Smoke routed @100k = 0.9667 (close to v1's 0.9333
at different seed) — chain-grade-eligible at smoke regime; full should confirm + extend to 1M.

## Q-discipline (USER 2026-06-25)

If full produces routed @ any N >= 0.995, the verdict carries a `[Q-DISCIPLINE: suspect saturation]` note. Cert-owner
(Skunkworks) tier-rules; default UNDER-claim if >=0.95 without mechanism story.

## Post-dispatch verify-the-referent (Orchestrator)

After dispatch:
1. Confirm queue entry in `data/overnight_queue/queue.json` on REMOTE marsh@home.
2. Per Fix #24 verify GPU actually used: smoke timing on remote should show CUDA tensor allocation; full metrics will
   include `gpu_available + gpu_name` fields.
3. Notify exp_dev/skunkworks on cell-land (per landing_notifier scheduled task).

## Companion batch state

Cells 2-5 (CPU) ALREADY LANDED on local_cpu_queue:
- Cell 2 (refuse-gate nonlinear-readout v2): HARD_PASS gap_refuse=1.000 cv=0 (Q-discipline saturation suspect)
- Cell 3 (distill-verify operator equivalence v2): MIDDLE_BAND distill=0.7778 cv=0.2020 (honest negative on chain-grade
  band; NAMED operators by chance landed in training fold; per-seed [0.6667, 1.0, 0.6667])
- Cell 4 (permutation-binding multi-occ v2): HARD_PASS perm=1.000 cv=0 lift=0.9371 cv=0.0078 (chain-grade eligible)
- Cell 5 (b_delta readout lever transfer v2): HARD_PASS extension=1.000/1.000 cv=0 BOTH tasks (Q-discipline saturation
  suspect; corrected v1 mechanism)

Cell 1 will be the GPU lander in this batch. Skunkworks will VET all 5 when complete.

— exp_dev (committed c20f5d75 / f03c523d / b119ee56 / 85f616d1 / 15982cd5)
