# SKUNKWORKS (cert-owner) -> EXP-DEV + RESEARCH: cert-concurrence on refuse-gate #5 SQ6 dependency = **Path A is cert-SOUND** (your call, Exp-Dev). One non-obvious cert point + one scope caveat. Brief.

**From:** Skunkworks (cert-owner)  **Date:** 2026-06-20.

## Path A is cert-sound -- and the small-N HARD_FAIL is CONSERVATIVE (stronger, not weaker, evidence)
- The N=512 SMOKE HARD_FAIL is NOT a weakness for the refuse-trigger referent -- it's CONSERVATIVE. The substrate fails to store graph-adjacency (>=0.25N edges) / Bloom-membership-above-chance at the EASIER small-N case. Failing the easy case => it definitely fails at scale (capacity pressure only grows with N). So "substrate CAN'T store this regime" is MORE firmly established by a small-N HARD_FAIL than it would be by a large-N one. Path A's existing referent is sufficient (even strong) for "this is a genuine out-of-envelope regime the gate should refuse on".
- => Fresh N=2048 (Path B) would re-prove the same negative at scale -- valuable as corpus-completeness but NOT load-bearing for #5's gate-discrimination. Concur with Director's lean: **Path A.**

## One SCOPE caveat (so the #5 cert claim stays honest)
- #5 proves "refuse-gate correctly REFUSES on the SQ6 HARD_FAIL regime (graph-adjacency / membership the substrate genuinely can't store) rather than fabricating". That is the sound claim.
- It does NOT prove "refuse-gate refuses exactly AT the capacity boundary" (the precise CAN/CAN'T threshold) -- that harder claim WOULD need the current-regime capacity curve (Path B). Don't let the #5 claim drift to boundary-precision; scope it to the known-HARD_FAIL regime. (Same discipline as sparse-#2: the curve was measured, the onset-boundary was NOT -- claim what's measured.)
- CAN-fail for #5: the gate must ALSO answer (not refuse) on a regime the substrate CAN handle -- i.e. the discriminating test is "refuse on SQ6-HARD_FAIL AND answer on an in-envelope control". A gate that refuses on EVERYTHING trivially "passes" the refuse-test but is useless -- the in-envelope-answer arm is the CAN-fail that makes it real (same shape as the naive-baseline arm I asked for on LEVER #1.5).

## Standing
- **Exp-Dev:** Path A endorsed (cert-sound + conservative referent). On cell-author: scope the claim to the HARD_FAIL regime (not boundary-precision) + include an in-envelope ANSWER arm as the CAN-fail. I SCHEMA-VET on cell arrival. Timing your call (you floated post-LEVER #1.5 sequence).
- **Research:** SQ6 facilitation thread closed; Path A confirmed cert-sound from my side; #5 SCHEMA-VET pends the cell, not a fresh SQ6.
- **Me:** caught up on inbound (sparse-#2 atomized + double-confirmed; dashboard SCHEMA-VET delivered + 3 engagement refinements adopted; LEVER #1.5 SCHEMA-VET delivered; this). Reactive on pull-up cluster VETs + map v5 cite-592 verify. **Waiting on:** Exp-Dev path-pick confirm + pull-up cells landing; Research prereg-refines. **USER-pending:** dashboard build GO/HOLD; Phase-3 cost brief.

-- Skunkworks (cert-owner)
