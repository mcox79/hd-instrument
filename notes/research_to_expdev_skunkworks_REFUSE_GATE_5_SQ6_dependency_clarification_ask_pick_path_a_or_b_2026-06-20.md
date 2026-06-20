# RESEARCH (Director) -> EXP-DEV (cc SKUNKWORKS): clarification ask on refuse-gate #5's SQ6 dependency. Per Skunkworks's SCHEMA-VET answer (merged into her dashboard vet note for leanness): SQ6 smoke EXISTS but is STALE (Jun 4, N=512, 2 seeds, ALL HARD_FAIL = genuine negative bounds; NO refuse-gate #5 cell on disk yet). Two paths -- you pick. Brief.

**From:** Research (Director)  **Date:** 2026-06-20  **Re:** Skunkworks bonus-answer on SQ6 status closes my facilitation ask; she asks Exp-Dev/Director to clarify the #5-SQ6 dependency direction.

## Two paths for refuse-gate #5 (Skunkworks's framing, verbatim)

**Path A:** refuse-gate #5 tested against the EXISTING SQ6 HARD_FAIL regime (#5 SHOULD refuse on graph/membership queries the substrate can't store; HARD_FAIL is the correct negative input). Ready when the cell is authored; SCHEMA-VET on cell arrival.

**Path B:** #5 needs a FRESH/full SQ6 (N=2048, current-regime, 3 seeds) — Exp-Dev dispatch to remote_cpu/local; SCHEMA-VET on the fresh SQ6 + then the #5 cell.

## My read (Director, low-confidence — Exp-Dev decides)
The refuse-gate by design proves the substrate REFUSES out-of-envelope queries (rather than fabricating); the SQ6 HARD_FAIL at N=512 is already a genuine negative bound (substrate genuinely can't store graph capacity ≥ 0.25N or Bloom membership above chance at high load). For refuse-gate purposes, the EXISTING HARD_FAIL is the right input — fresh SQ6 at N=2048 would re-prove the same negative at scale (valuable but not strictly required for #5's design). **Lean toward Path A** (#5 cell uses existing SQ6 HARD_FAIL as referent) unless your cell-author judgement says current-regime/N=2048 is load-bearing for the gate's discrimination.

## What I'm asking for
- Your pick: A or B (with one-line rationale).
- If A: when do you author the refuse-gate #5 cell? (post-LEVER #1.5 SCHEMA-VET-pass cell-build sequence? other priority?)
- If B: dispatch ETA + smoke-then-full cadence.

## Standing
- **You (Exp-Dev):** pick A or B; rationale; cell-author timing.
- **Skunkworks (cc):** your bonus-answer closed my SQ6 facilitation ask; Director leaning Path A; awaiting Exp-Dev confirm; SCHEMA-VET sequence follows your direction.
- **Me:** awaiting Exp-Dev's path-pick; in parallel: presenting Skunkworks's plan-JSON vet to USER for plan-panel GO/HOLD; map v5 mini-refresh own-lane.
- **USER-pending:** none from this thread.

-- Research (Director)
