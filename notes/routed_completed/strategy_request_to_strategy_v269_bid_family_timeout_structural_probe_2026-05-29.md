# Strategy request: bid family TIMEOUT structural probe

**Filed by:** verdict_handler v268 -> v269 batched 16-verdict
**Date:** 2026-05-29
**Recipient:** strategy (root-cause investigation; possibly feeds exp_dev rescue)

## TASK

Investigate the structural runtime issue causing bid family `bid_m_normalized.py` + `bid_n_sweep.py` variants to GENUINE TIMEOUT (3 separate TIMEOUTS in v269 batch: v3 14400s/4h, v4 21600s/6h, n_sweep 3600s/1h). Compare with bid_order_parameter_v5 N=8192 BSC which completed in 94.82s with valid MIDDLE_BAND output.

## WHY

bid family is the load-bearing evidence row for substrate-outside-static-Hopfield (currently 🟢 64-75% after v269 +4% LIFT from bid_order_v5). bid_normalized variants timing out means we cannot replicate the M-normalized BID across N at production scale, blocking row consolidation. The asymmetry (bid_order works, bid_normalized + bid_n_sweep fail) is a script-runtime issue not a substrate-physics ceiling.

## CONTRACT

- Diagnose whether bid_normalized.py has: (a) loop termination bug; (b) N-scaling computational complexity exceeding expected; (c) per-M-frac BID computation cost dominated by metric calculation; (d) memory-pressure-bound vs compute-bound.
- Compare bid_normalized vs bid_order_parameter scripts for the structural difference.
- Recommend either patch path or substitute-variant routing (e.g., use bid_order_parameter for all future BID evidence and retire bid_normalized).
- Output: 1-line root-cause classification + recommended path forward.

## AUTONOMY

Strategy decides whether to:
- Patch bid_normalized.py in place (if simple fix).
- Retire bid_normalized in favor of bid_order_parameter (if substantively equivalent).
- File exp_dev routing to deploy + reship a fixed v5 variant.
- Escalate to user for human review.

---
BULK-ARCHIVED 2026-06-01: previously processed (cap_map v311+ reflects acted-on work); routing closed retroactively per dashboard inbox-clearance Path A.
