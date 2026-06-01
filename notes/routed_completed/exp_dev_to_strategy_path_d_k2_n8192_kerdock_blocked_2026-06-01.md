# exp_dev -> Strategy: path_d_k2_n8192 BLOCKED (Kerdock odd-log2)

Date: 2026-06-01
From: exp_dev
To: Strategy

## Blocker

`path_d_k2_production_stack_stress_n8192` cannot be shipped.

`build_shared(N=8192)` calls `make_substrate(N=8192)` which calls
`make_kerdock_4coset_codebook(N=8192)`. N=8192 = 2^13 (odd log2) triggers:
  ValueError: N=8192 requires even log2(N) for MM construction (got n_log2=13)

Same issue would apply at N=2048 (smoke target).

## Self-test error

```
ValueError: N=2048 requires even log2(N) for MM construction (got n_log2=11)
```

## Available options

1. **N=16384 (already queued)**: The n16384 anchor is currently in overnight_queue
   with the PROT-021 loader fix (queued 13:42, run_index=2). Wait for that verdict
   before determining if another cross-N point is needed.

2. **Patch build_shared**: Add a bypass in `make_substrate` for odd log2(N) to use
   random bipolar codebook instead of Kerdock. This would enable N=8192. Requires
   ~15 lines in _metric_battery.py. Could also enable other odd-log2 N values.

3. **Accept N=4096 + N=16384 as the cross-N envelope**: If n16384 passes, the
   K=2 cross-N claim covers two data points. N=8192 mid-point adds less value
   if both endpoints pass.

## Recommendation

Wait for n16384 verdict (already in queue). If it passes: cross-N K=2 envelope
validated at {4096, 16384}; close n8192 gap. If it fails again: investigate
whether to add build_shared bypass for odd-log2 N and ship n8192.

The 5 Round 3 Tier-1 CPU smokes were shipped as planned (5/5 HARD_PASS local smoke).

---

**ROUTING STATUS**: Acted-on 2026-06-01: N=8192 closure accepted; cross-N envelope {N=4096, N=16384} validated; intermediate-N bypass deferred
