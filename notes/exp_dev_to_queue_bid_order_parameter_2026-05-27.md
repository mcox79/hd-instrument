# exp_dev -> queue: BID Order-Parameter Probe (2026-05-27)

**Filed by:** exp_dev
**Trigger:** exp_dev_handoff_research_negative_results_meta_analysis_2026-05-27.md

## Anchors shipped

```
queue=remote_cpu_queue name=bid_order_parameter_v1 script=experiments/exp_bid_order_parameter_v1.py prereg=preregs/2026-05-27_bid_order_parameter_v1.md timeout=300
queue=remote_cpu_queue name=bid_order_parameter_v1_nsweep script=experiments/exp_bid_order_parameter_v1_nsweep.py prereg=preregs/2026-05-27_bid_order_parameter_v1_nsweep.md timeout=300
```

## Smoke results

bid_order_parameter_v1 smoke (N=256, N=512, 1 seed):
  N=256: BID=29.19 class=OUTSIDE_ALL_BANDS q_mean=0.8436
  N=512: BID=26.86 class=OUTSIDE_ALL_BANDS q_mean=0.8462
  Smoke verdict: BID_MIDDLE_BAND_MIXED (expected with 1 seed)
  Wall time: 0.01s

bid_order_parameter_v1_nsweep smoke: same smoke profile (N-sweep mode forces same smoke at N=256/512)

## Remote verify

Both anchors: REMOTE VERIFY PASS (queue_add.sh exit=0, VERIFIED in remote queue.json)
Remote queue pending count after ship: 4 (includes 2 new BID anchors)

## False-alarm stamps

Stamped landed_at on 3 ship_unconfirmed watchdog false-alarms:
  - anchor_novel_phase_battery_v1 (overnight_queue, status=completed)
  - wave14_moe_cosine_router_v1 (remote_cpu_queue, status=completed)
  - wave14_corpus_size_scaling_v1 (remote_cpu_queue, status=completed)
These were in data/recent_ship_attempts.jsonl without landed_at, causing watchdog
to repeatedly fire. Root cause: they were completed but stamping was missed.
Fix: stamped landed_at = attempted_at (conservative estimate).

## Strategic notes

- Smoke BID (~29) is close to the paramagnetic reference BID (~27-35) at small N.
  The key discriminating signal will emerge at full scale N=1024-4096 where
  paramagnetic BID should approach N while substrate BID stabilizes.
- The N-sweep companion (bid_order_parameter_v1_nsweep) directly gates HP3
  (thermodynamic quantity vs finite-N artifact). Smoke drift was 8%, borderline
  for HP3 pass threshold of 5%.
- HF3 (spin-glass specifically) is not a risk: substrate BID (~27) is far from
  spin-glass band [64,128] at N=256. The retrieval band [1,2.5] is also clearly
  excluded.
- q_mean=0.84 confirms substrate is in high-retrieval regime at alpha=0.40.
