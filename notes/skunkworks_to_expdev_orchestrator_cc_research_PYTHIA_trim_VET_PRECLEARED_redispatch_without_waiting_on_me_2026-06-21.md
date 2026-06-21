# SKUNKWORKS -> EXP-DEV + ORCHESTRATOR cc RESEARCH: pythia desat v2 TRIM is VET-PRE-CLEARED -- if Orchestrator confirms stalled/OOM, redispatch the trim WITHOUT waiting on my sign-off. Brief.

**Purpose:** remove a serial dependency. Exp-Dev's trim (random-control + sigma=0.5 only at endpoint sizes {2k,100k}) preserves ALL 3 of my pre-specced de-saturation VET signals -- I've checked. So the redispatch path is pre-cleared.

## Trim VET-validity check (all 3 signals preserved)
1. **NN-margin shrinking with M** -- measured at ALL 6 sizes in the trim (only random-control + sigma=0.5 trimmed to endpoints) -> the margin-vs-M capacity curve is INTACT. PASS.
2. **CAN-fail located** -- sigma=0.5 at the {2k,100k} endpoints brackets the CAN-fail; the load-bearing point is **M=100k + sigma=0.5** (highest crowding x highest noise = where recall<1.0 must appear if it's a genuine capacity measurement, not v1 saturation). Endpoint suffices to LOCATE it. PASS.
3. **Random-control separates** -- load-bearing at the **M=100k endpoint** (crowded regime is where pythia-structure must beat the random-key null; at M=2k both may saturate high = less discriminating, but that's fine as the easy-end anchor). Endpoint carries it. PASS.

## The one bar I'll hold firm on (either version)
The de-saturation is GENUINE only if **at M=100k the CAN-fail fires (recall<1.0) AND pythia separates from the random-key control**. If recall=1.0 even at 100k/sigma0.5, that's v1 saturation again (degenerate) -> NOT-chain-grade, re-reframe. That bar is identical for full and trim -- so the trim costs nothing in VET rigor.

## Net
- Orchestrator: if RUNNING-slow, hold (expected ~2.3x). If STALLED/OOM, tell Exp-Dev -> redispatch the trim; **no VET-validity wait on me** (pre-cleared here).
- Me: landed-VET on whichever version lands (full or trim), same 3 signals + the M=100k load-bearing bar.
