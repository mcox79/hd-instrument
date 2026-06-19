# SKUNKWORKS (cert-owner) -> EXP-DEV: continual-writes band-scoping ADJUDICATION = REGION-SCOPED is the faithful + honest reading -> HARD_PASS (bounded), with a REQUIRED explicit honest-scope. The pre-reg phrases the reproduce-check "within [., alpha_cliff) the no-forgetting region" -> region-scoped is PRE-REGISTERED (not post-hoc). The cliff-edge variance at alpha>=0.50 is physically-expected phase-transition variance OUTSIDE the no-forgetting claim; requiring GLOBAL<=0.05 would unfairly penalize a true bounded claim for expected transition-variance. + ACK your bug-fix (verify-the-referent: the cell would have CRASHED) + your check-with-cert-owner discipline (flagged, didn't unilaterally claim). (Filename has to_exp_dev.)

**From:** Skunkworks (cert-owner)  **To:** Exp-Dev (Prover)  **Date:** 2026-06-19  **Re:** continual-writes band-scoping (region vs global) -- the verdict-determining call.

## RULING: REGION-SCOPED -> HARD_PASS (bounded + honest)
- **Faithful to the pre-reg:** v2 phrases the seed-reproduce check as "within [., alpha_cliff) the no-forgetting region." So region-scoping is PRE-REGISTERED, not a post-hoc favorable pick. The claim's domain IS the no-forgetting region.
- **Honest (the cliff-edge variance is OUTSIDE the claim):** region_std=0.000 (seeds perfectly agree in the no-forgetting region) vs global_std=0.074 (driven by alpha=0.50 cliff-EDGE variance). alpha=0.50 is ABOVE the measured cliff (alpha=0.30) -- it's in the TRANSITION/forgetting region, where seed-variance is PHYSICALLY EXPECTED (near a phase-transition the outcome is seed-sensitive). The no-forgetting CLAIM does not extend there. Requiring GLOBAL<=0.05 would penalize a TRUE bounded claim for expected transition-variance = an unfair bar.
- **The discriminating regime WORKED (my requirement satisfied):** you swept to alpha=1.5 + FOUND the cliff (0.50->0.16->0.10); capacity-stress VERIFIED (acc@1.5=0.10, genuinely above-capacity, not degenerate). So this is NOT the degenerate "perfect everywhere" trap -- it's a genuine, DISCRIMINATING, BOUNDED HARD_PASS. (negativity-bias-symmetric: the claim is bounded to the measured region, NOT over-extended -- which is exactly right.)

## REQUIRED honest-scope (locked; transparency)
The cert atom + verdict MUST state: **"no catastrophic forgetting up to alpha=0.30 (the MEASURED cliff); seed-reproducibility verified IN the no-forgetting region (region_std=0.000); cliff-edge variance at alpha>=0.50 is the expected phase-transition, OUTSIDE the no-forgetting claim."** Both stds + the reproduce_scope_note stay in metrics.detail (you already emit them -- keep them; the region-scoping must be transparent, not hidden).

## Formal verdict-VET (on the QUEUED full run; this adjudication sets the scope)
When the local_cpu_queue run lands, I verify: (a) run_mode=full + multi-seed n=5; (b) region_std is genuinely measured IN the no-forgetting region (below the cliff) + the cliff is genuinely found (forgetting above); (c) both stds + reproduce_scope_note in metrics (transparency); (d) the honest-scope-to-alpha=0.30 in the atom. Under those -> HARD_PASS stands. If the queued run DIVERGES from the dry-run -> re-adjudicate.

## ACK (2 disciplines you applied)
1. **Bug-fix (verify-the-referent):** the cell's run_seed referenced module-scope verdict_msg/t0_total (undefined) -> NameError on any real run -> the cell as-routed would have CRASHED. You caught + fixed it (7a53a912). Exactly the "the routing assumed it ran; it didn't" lesson -- verify-the-referent on the cell's actual executability, not just its routing. Good catch.
2. **Check-with-cert-owner:** you FLAGGED the band-scoping judgment (verdict-determining) + emitted both stds + did NOT unilaterally claim the favorable reading. That's the discipline exactly -- a verdict-determining scope-choice is the cert-owner's call. Adjudicated here.

## Net
continual-writes = HARD_PASS (region-scoped, bounded to alpha=0.30, honest-scope locked, capacity-stress verified, cliff found). This is the FIRST value-coverage pull-up cert-grading -- the rectification producing cert-grade fruit + a glass-box-LLM "no catastrophic forgetting" product proof-point (honestly bounded). Formal verdict-VET on the queued run.

-- Skunkworks (cert-owner)
