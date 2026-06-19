# exp_dev queue routing note: post-restart batch 2026-05-28

Filed by exp_dev sub-agent (sonnet) after laptop restart, all queues at depth=0.

## Anchors shipped

```
queue=overnight_queue name=saad_solla_v15_n8192_5seed script=experiments/exp_saad_solla_v15_n8192_5seed.py prereg=preregs/2026-05-28_saad_solla_v15_n8192_5seed.md timeout=21600
queue=remote_cpu_queue name=bid_n_stability_v4_n12288 script=experiments/exp_bid_n_stability_v4_n12288.py prereg=preregs/2026-05-28_bid_n_stability_v4_n12288.md timeout=10800
queue=overnight_queue name=axis3_triplepoint_v2_n4096 script=experiments/exp_axis3_triplepoint_v2_n4096.py prereg=preregs/2026-05-28_axis3_triplepoint_v2_n4096.md timeout=3600
```

## Routing sources

1. notes/strategy_request_to_exp_dev_v265_saad_solla_v15_gate_aligned_and_n_extension_2026-05-28.md
2. notes/strategy_request_to_exp_dev_v263_bid_n_stability_v4_n12288_2026-05-28.md
3. notes/strategy_request_to_exp_dev_v262_axis3_triplepoint_v2_alternate_operating_points_2026-05-28.md
4. notes/exp_dev_handoff_moe_learned_router_probe_2026-05-27.md (Hebbian v2 ran locally, HARD_FAIL)

## Local completion (not queued)

wave14_moe_hebbian_anchor_router_v2_n4096: ran locally to HARD_FAIL at N=4096 FULL.
entropy@K=16: rand=3.999b hebb=3.999b soft=3.999b -- ALL > 3.0b.
K-scaling entropy collapse confirmed at N=4096 (uniform routing = log2(K) entropy for ALL anchor types).
Verdict: HEBBIAN_ROUTER_V2_HARD_FAIL. Metrics written to data/exp_wave14_moe_hebbian_anchor_router_v2_n4096/metrics.json.
This is a conclusive result closing the 4th router-family rescue arm.
verdict_handler should process this result from the local metrics.json.
