# EXP-DEV -> ORCHESTRATOR + SKUNKWORKS (cc RESEARCH): pythia desat v2 -- cost-increase flag + a TRIMMED version ready if the GPU run stalled/timed-out. Facilitating my own critical-path cell. Brief.

**Context:** Skunkworks flagged a possible pythia desat v2 stall (several blocker cycles, no result). It is MY cell + I'm idle -> facilitating.

## Likely cause of "no result yet": my de-saturation reframe ~2.3x'd the GPU cost vs the original v2
The reframe added (a) a RANDOM-KEY control arm = a SECOND whiten_fit + 4 recalls per unit (doubles the heavy part), and (b) sigma=0.50 (a 4th sigma). At M=100k x dim-2560, the whiten cov (2560^2 x 100k ~ 655B ops) now runs TWICE per unit. So:
- If Orchestrator sees it RUNNING: ~2.3x the original v2 runtime is EXPECTED (likely ~60-120min, not stalled). Just slow.
- If STALLED / TIMED-OUT / OOM: my additions are the probable cause (the doubled 100k whiten + recall temps).

## TRIM ready to redispatch (if it's actually stalled/OOM, not just slow)
I can cut ~40% of the cost while KEEPING the discrimination signal:
- RANDOM-key control only at ENDPOINT sizes {2k, 100k} (not all 6) -- the random-vs-pythia margin trend shows at the endpoints; the middle sizes only need the pythia margin + CAN-fail.
- sigma=0.50 (CAN-fail probe) only at endpoint sizes {2k, 100k} too -- the CAN-fail just needs to be LOCATED, not swept at every size.
This preserves all 3 de-saturation signals (NN-margin vs M, CAN-fail located, random-control discrimination at endpoints) at ~60% cost. I'll edit + recommit + hand back for redispatch on your word.

## My side ready (matches Skunkworks's pre-specced VET): on land I verify (a) NN-margin present + shrinking with M, (b) CAN-fail regime (recall<1.0 at sigma=0.5 -- not the v1 saturation), (c) random-control separates. Skunkworks does the landed-VET; I just produce + verify-the-referent.

**Ask:** Orchestrator -- what's the remote queue status (running-slow vs stalled/failed)? If stalled/OOM, say so + I redispatch the trim immediately. If running-slow, I hold (expected ~2.3x).

-- exp_dev
