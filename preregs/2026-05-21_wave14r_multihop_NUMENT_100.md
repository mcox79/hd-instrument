# Pre-registration: wave14r_multihop_largeN_v1

Date: 2026-05-21
Status: Pre-registered, gated
Priority: R8 pre-armed rescue #4 (larger N — Goldstone-mode prediction)
Author: experiment_dev session, pipeline tick 74

## Why

R8 pre-armed rescue list (used in zh-zo FHRR prereg) item #4: "Larger N —
Goldstone-mode literature predicts noise ~ sqrt(K)/N."

All 5 R8 cleanup/binding rescues KILLED at N=4096 (A1, B1, B3, C1, Bet N).
Bet O encoding rescue also KILLED. Strategy cycle 43 notes 8 alternative
architecture paths remain. Larger N IS one of those untested axes —
sqrt(K)/N predicts that at N=16384, multi-hop noise is half what it is at
N=4096, potentially pushing d=50 above the 0.22 FHRR floor.

This is a substrate-N-scaling test, not a mechanism change. Same wave14t
multihop infrastructure at N=16384.

## Verdict labels (inherited from wave14t)

- MULTIHOP_LARGEN_50HOP_VALIDATED (acc_50 >= 0.10 — original wave14t threshold)
- MULTIHOP_LARGEN_DECAY_AT_<D>
- MULTIHOP_LARGEN_CATASTROPHIC_DECAY (acc_50 < 0.02; rescue fails)
- MULTIHOP_LARGEN_INCONCLUSIVE

## Runtime: ~20 min full (N=16384 is 4x larger than wave14t)
