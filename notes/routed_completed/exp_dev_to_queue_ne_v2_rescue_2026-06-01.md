# exp_dev -> queue: PP-33 NE-1/NE-2 v2 rescue dispatch

**Date:** 2026-06-01
**Context:** v321 cap_map; PP-33 at 0.40-0.55 EXPLORATORY; NE-1 + NE-2 both MIDDLE_BAND;
rescue dispatch authorized by user.

## Root cause of MIDDLE_BAND

NE-1 v1: N=1024 finite-size effects smeared C(t,t_w)~f(t/t_w) scaling.
NE-2 v1: Cliff at ~alpha=0.155-0.165 at N=1024 (smeared), vs predicted 0.138.
Both: 4x increase in N (-> N=8192) should resolve signal.

## Shipped

```
queue=remote_cpu_queue name=ne1_mct_aging_signature_v2_n8192 script=experiments/exp_ne1_mct_aging_signature_v2_n8192.py prereg=preregs/2026-06-01_ne1_mct_aging_signature_v2_n8192.md timeout=21600
queue=remote_cpu_queue name=ne2_dmft_retrieval_cliff_v2_n8192 script=experiments/exp_ne2_dmft_retrieval_cliff_v2_n8192.py prereg=preregs/2026-06-01_ne2_dmft_retrieval_cliff_v2_n8192.md timeout=21600
```

## Smoke gate results

- NE-1 v2 smoke (N=1024, 2 seeds, 3 trials): MIDDLE_BAND in 5.7s;
  seed=7 shows strong aging (|r|=0.838, collapse=164.83), seed=17 does not;
  expected at N=1024 finite-N noise; not SUSPICIOUS (variance non-zero, >100ms).
- NE-2 v2 smoke (N=1024, 2 seeds, 13 alpha values, 3 trials): MIDDLE_BAND in 0.9s;
  avg cliff at 0.153 (outside HP window [0.125,0.152] at N=1024);
  expected from v1 analysis; not SUSPICIOUS.

## Remote verify

Both: queue_add.sh exit=0; VERIFIED present in remote remote_cpu_queue/queue.json.

## PROT compliance

- PROT-018: N=8192 in both scripts at top-level config; gate confirmed match.
- PROT-019: timeout=21600s (floor for _n8192 anchors).
- PROT-021: get_output_dir() helper used; no hardcoded out_dir paths.

## If BOTH HARD_PASS

-> PP-33 lift from 0.40-0.55 EXPLORATORY to 0.55-0.70 (MCT/DMFT universality CONFIRMED)
-> route to Strategy for cap_map v322 bump

## If MIDDLE_BAND (again)

-> Route to Strategy: NE-1 MIDDLE rescue options: (a) N=16384, (b) longer trajectory t_w_max=500,
   (c) different initial condition (deep quench). NE-2 MIDDLE rescue: (a) N=16384, (b) report
   observed cliff_midpoint as substrate-specific deviation from DMFT theory.

Acted-on 2026-06-02: NE v2 anchors shipped cycle 5; processed in v330
