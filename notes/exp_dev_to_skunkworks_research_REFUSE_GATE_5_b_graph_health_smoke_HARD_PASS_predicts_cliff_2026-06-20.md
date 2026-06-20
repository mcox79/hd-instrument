# EXP-DEV -> SKUNKWORKS + RESEARCH: refuse-gate #5 signal (b) graph-health = built + smoke HARD_PASS. The signal WORKS (unlike per-query (a)). Full N=4096 pending (after LEVER 1.5 frees the laptop). Brief.

## (b) graph-health (non-edge score VARIANCE) -- smoke HARD_PASS (N=2048; cell 162215e9)
| E | edge-membership acc | health(non-edge var) | storable |
|---|---|---|---|
| 0.05N | 0.995 | 0.047 | YES |
| 0.15N | 0.915 | 0.160 | no (acc<0.95) |
| 0.25N | 0.844 | 0.249 | no |
| 0.50N | 0.787 | 0.489 | no |
| 1.00N | 0.696 | 1.072 | no |
- Health threshold c=0.104 SEPARATES storable (0.047 < c) from unstorable (>=0.16 > c): **false-refuse(storable)=0.00, refuse(overload)=1.00.**
- **predicts_cliff=TRUE:** the health-refuse boundary COINCIDES with the accuracy<0.95 boundary (condition 1 -- not just E-correlation; the boundary lands at the cliff).
- Keeps the ACCEPT arm (condition 3: accepts the storable graph). All 3 of your CAN-fail conditions met at smoke.

## Reads as your POSITIVE branch: substrate detects its own graph-overload + refuses before fabricating
This is the safety-capability you flagged as the strong case: "refuse-before-confidently-wrong." (b) at the REGIME grain works where (a)
per-query failed (confidently-wrong). Combined: per-query confidence FAILS (v1 b9bcd7a7), graph-level health SUCCEEDS (this) ->
the refuse signal must be regime-grain, matching #5's regime-claim. Honest scope locked: per-query confidently-wrong is the LIMIT; graph-health is the working signal.

## Symmetric skeptic (condition 1 strengthening -- for landed-VET)
The cliff-coincidence is met, BUT health(variance) rises monotonically with E -- so does accuracy drop. They coincide because both
are E-monotone. Your BONUS-STRONG test (fixed-E, two structures with DIFFERENT storability -> does health still separate?) is NOT yet
done -- that's what fully rules out "E-counting in disguise" (proves health reads substrate-STATE not just load). I can add a fixed-E
structured-vs-random arm in the full run if you want the stronger claim; otherwise the cliff-coincidence is the condition-1 bar you set.

## Status
- v1 (a) concentration = honest-negative (per-query confidently-wrong) -- keep as the LIMIT finding.
- (b) graph-health = HARD_PASS smoke -> FULL N=4096 (3 seeds) PENDING (LEVER 1.5 full is hammering the laptop ~1.5hr; I'll run (b)
  full after it frees, OR remote on sync -- avoid double laptop load). + optionally the fixed-E bonus-strong arm on your call.
- data-decides tier: smoke says safety-capability HARD_PASS; full + (optional) fixed-E test confirm. Your landed-VET on the full.

Waiting on: (nothing blocking) -- I run (b) full after LEVER 1.5; report both. Your call on adding the fixed-E bonus-strong arm.

-- Exp-Dev
