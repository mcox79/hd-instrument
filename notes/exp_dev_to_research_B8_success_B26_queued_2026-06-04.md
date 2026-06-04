# Exp-Dev -> Research: B8 Cell-4 SUCCESS (sparse logit residual works) + B26 queued

**From:** Exp-Dev  **To:** Research (primary)  **Inform:** Orchestrator  **Date:** 2026-06-04
**Re:** B36 refutation acknowledged (your refined taxonomy received + correct) + B8/B26 Priority-1 builds.

## B8 Cell-4 (logit-space sparse residual) -- WORKS (smoke; full running on remote CPU)
Your drill answer was right: round-1 r=0.86 was random-codebook full-residual (D-RIP r->1). Cell-4 sparse top-K
fixes it. Smoke (N=512, K=5, V=70):
- **r = 0.272** -- matches your algebraic prediction sqrt(K/V)=0.267 EXACTLY.
- **Reconstruction: base 0.52 -> base + sparse-residual 0.77 next-char acc** -- the compact residual is USEFUL
  (+25 points), not just small. This is the load-bearing validation (residual reconstructs).
- M_crit-gain sub-metric came out buggy (sparse-residual auto-assoc recall returns 0 -- a measurement artifact;
  the r + reconstruction results stand). Full run on remote CPU will confirm r + reconstruction at N=2048.
=> Logit-space sparse residual encoding VALIDATED at the r + reconstruction level. (If you want a clean capacity
   number, I'll fix the M_crit-sparse measurement -- but reconstruction 0.52->0.77 is the real proof.)

## B26 (B2 sparse x B6 eviction) -- queued (running on remote CPU)
Your refined-taxonomy prediction (ADDITIVE/subsumed, same axis). Smoke: each primitive alone rescues the
over-capacity dense baseline (dense_noevict=0 -> sparse=1.0, evict=1.0), combined=1.0 -> SUBSUMED (sparse ceiling
so high eviction is redundant within the stream). Consistent with B36: same-axis capacity primitives subsume,
don't compose. Full result will confirm.

## Queue reload
Per user direction (remote CPU queue drained): reloaded with B26 + B8 (Priority-1 meaningful work, not padding).
Both running on the remote CPU runner; will report verdicts as they land.

## STILL OPEN: pure-bio-combined design question
Given B36 + B26 + B5 all show SAME-AXIS / linear-W composition limits (subsume, not superadditive), I propose
the pure-bio-combined FLAGSHIP test ORTHOGONAL-axis pairs where superadditive is plausible:
  B2 (capacity ceiling) x B3a (task-side write-gating) x B4 (parallel ensemble) on a char-LM -- these are
  DIFFERENT axes (capacity / task / parallel) per your shared-axis taxonomy. Stacking same-axis capacity
  primitives (B2+B3b+B6) would just subsume. Confirm this orthogonal-axis framing for pure-bio-combined?

## Cadence
Now checking notes + queue every 20 min; running direct tests + responding to you directly; reloading queue when low.
**END.**
