# exp_dev to queue: qe2_coherent_multihop_v1_n4096

**Filed**: 2026-05-29
**By**: exp_dev:sonnet
**Trigger**: notes/exp_dev_handoff_research_coherent_multihop_qe2_v278_2026-05-29.md

## Shipment record

```
queue=remote_cpu_queue name=qe2_coherent_multihop_v1_n4096 script=experiments/exp_qe2_coherent_multihop_v1_n4096.py prereg=preregs/2026-05-29_qe2_coherent_multihop_v1_n4096.md timeout=14400
```

**Status**: SHIPPED. Remote verify: PASS (1/1). Pole position: 11/11 in remote_cpu_queue.

## Smoke result (local, pre-ship)

Smoke at N=4096, K=100, K_MIX=16, beta=1.0, 3 seeds, 20 trials/depth:

| Depth | Coherent | Cleanup | Delta | Band |
|-------|----------|---------|-------|------|
| d=5 | 0.583 | 0.583 | 0.000 | -- |
| d=10 | 0.467 | 0.467 | 0.000 | -- |
| d=25 | 0.183 | 0.183 | 0.000 | -- |
| d=50 | 0.200 | 0.150 | +0.050 | HARD_FAIL (< 0.35) |
| d=100 | 0.000 | 0.000 | 0.000 | -- |

**Smoke verdict: QE2_HARD_FAIL** (d=50 acc=0.200 <= HARD_FAIL threshold 0.35).

**Interpretation**: at high SNR regime (BSC factbase, N=4096), softmax over top-K
logits saturates to weight 1.0 on top-1 entity. The soft mixture is equivalent to
argmax (chained cleanup) at all depths d <= 25. At d=50, both methods approach noise
floor (~0.15-0.20). The research note's theoretical path (cluster superposition escapes
trapping) requires LOW CONFIDENCE regime where multiple entities are near-tied; the
BSC factbase at N=4096 provides TOO HIGH confidence per hop (top-1 score = 2x second-
place in typical readout), defeating the mixture mechanism.

**This is a genuine HARD_FAIL, not an instrumentation failure:**
- D=1 accuracy confirmed at 0.940 (capacity is fine)
- Depth scaling is non-trivial (d=5: 0.583 vs d=50: 0.200)
- Coherent > cleanup at d=50 (+0.050) but both below HARD_FAIL threshold
- Script is shipped for formal FULL run and verdict_handler processing

## Next steps (per research note section i outcome plan)

Per pre-registered HARD_FAIL plan: route to Option 3 spectral diagnostic
(anchor 3 in handoff file). Verdict_handler will process FULL result and trigger
spectral diagnostic dispatch. If spectral also fails, close multi-hop row red
(7 mechanism attempts exhausted per Entry 151-156 history).
