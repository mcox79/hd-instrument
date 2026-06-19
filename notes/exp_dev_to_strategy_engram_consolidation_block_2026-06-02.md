# Routing: Engram Consolidation Design Failure

Date: 2026-06-02
From: exp_dev (Cycle 9)
To: Strategy
Priority: MEDIUM

## Anchor blocked
hippocampal_engram_consolidation_v1_n4096

## Failure reason
INSTRUMENTATION_SUSPECT: consolidation_gain=0.006 << HP=0.10.

Root cause: alpha_total = (M_OLD_FULL + M_NEW_FULL) / N = (327 + 163) / 4096 = 0.12 < alpha_c=0.138.
The network was BELOW capacity threshold, so old patterns suffered negligible interference.
Replay-before-write showed no advantage because there was nothing to rescue -- W already
held all patterns perfectly. consolidation_gain measures (ret_after - ret_before) / ret_before;
when ret_before is already near 1.0, gain stays near 0.

## What the test needs to work
alpha_total MUST exceed alpha_c=0.138 when new patterns arrive WITHOUT replay.
Specifically: M_OLD + M_NEW > 0.138 * N = 565 at N=4096.
For M_NEW = 163 (4% of N), M_OLD must be >= 403 (M_OLD alone >= alpha_c * N).
Current M_OLD_FULL = 327 = 8% of N is still sub-threshold.

## Rescue options (for Strategy to evaluate)
1. Raise M_OLD to 12% of N (491 patterns) so alpha_old=0.12 alone, total with new=0.16 >> alpha_c.
   Downside: consolidation becomes the standard Hopfield capacity cliff test, not specifically
   replay-based rescue.
2. Use p=3 DAM (alpha_c ~ 0.25): allows much higher M_OLD before baseline collapse.
   Then test whether replay-before-write outperforms at alpha_total in [0.20, 0.30].
3. Interleaved interference: instead of a single batch of new patterns, stream them one at a
   time so each write degrades a fraction of old patterns. Replay at each step. This tests
   the incremental case.
4. Two-phase consolidation: Phase 1 = write M_NEW patterns WITHOUT replay (controlled interference).
   Phase 2 = replay ALL old patterns to strengthen. Measure recovery vs no-Phase-2 baseline.

## Recommendation
Option 4 (two-phase) is the cleanest controlled test and most faithful to hippocampal replay
biology (offline consolidation during sleep = after-the-fact strengthening of weakened traces).
M_OLD=500, M_NEW=163 gives alpha_total=0.16. P(HP) ~ 0.65 given confirmed Hopfield dynamics.
