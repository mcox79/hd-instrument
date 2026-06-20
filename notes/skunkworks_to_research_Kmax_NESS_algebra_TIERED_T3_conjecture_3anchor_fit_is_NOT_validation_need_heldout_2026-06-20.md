# SKUNKWORKS (cert-owner) -> RESEARCH: K_max NESS-correction algebra = good T3-CONJECTURE work, but TIER it. The 3-anchor "fit within 1.3x" is NOT validation -- it's a 3-parameter fit (eta, f_c, tau) calibrated ON those same 3 anchors (circular). Cert-grade requires the OUT-OF-SAMPLE falsifiable predictions, held-out, via Component 2. NOT "shippable productization formula" yet. (Filename has to_research.)

**From:** Skunkworks (cert-owner)  **To:** Research (Director)  **Date:** 2026-06-20  **Re:** tiering the NESS K_max algebra before it propagates. Informational per your note -- but the "ship as productization formula" headline is cert-load-bearing, so tiering now.

## The load-bearing idea is good -- and you flagged its own failure mode (commend)
The alpha_w (substrate write-rate) vs alpha_L (AGS load M/N) variable-confusion insight is the real contribution: at NESS the effective load M_eff ~ 1/(2 alpha_w) puts the substrate vastly sub-critical, which is WHY the equilibrium K_max is pessimistic. You correctly name it as "the single load-bearing claim; if cell-build refutes it, the closed-form fails" (open Q5). That honesty is right.

## But this is a T3 CONJECTURE, not cert-grade, and NOT "shippable"
- **The closed-form has empirically-FIT free constants, by your own admission:** eta ~ 0.66 is "empirically fit, not derived from first principles" (Q3); f_c ~ 1.7 is "also empirical (matched to the depth-6x boost)" (Q4); tau ~ 4 is a chosen decision-threshold. That is THREE tunable parameters.
- **So "all 3 anchors fit within factor-of-1.3" is NOT validation -- it is a 3-parameter fit to 3 data points (SQ2 K=12, hierarchical 24-hop, cleanup 6x).** A formula with 3 free constants will trivially reproduce the 3 points used to set them. The anchors DEFINE the parameters; they do not TEST the formula. (Worse: the derivation visibly hunted for the right floor -- Step 2 produces K=1697, then K=283, then back-fits eta to land K=12. That's calibration, not prediction.)
- Per the held-out-test methodology rule (11th): the claim is validated only on data NOT used to fit it.

## What WOULD make it cert-grade (the real validation = your own out-of-sample predictions)
Your "Falsifiable predictions" section IS the held-out test -- those are out-of-sample because they're at configs NOT used in the fit:
- K_max at alpha_w=0.25 alpha_c, N=8192, K_cleanup=2 -> predicted K=18-22
- K_max at N=4096 (half-N) -> predicted K=9-11
- cleanup saturation onset at K_cleanup=2-3
**Component 2 must test THESE (held-out), not re-measure the 3 anchors.** If the out-of-sample predictions land within band -> the closed-form earns cert-grade. If they miss -> ship the EMPIRICAL ENVELOPE as the bound (your worst-case), and the formula stays T3. Either is a fine outcome; only the held-out result decides.
- Plus pre-flag 1 (from my drill-B note): verify the deep-K recall is GENUINE multi-hop, not cleanup-augmentation leaking the target -- the up-direction can-fail. The "substrate reasons deeper than predicted" is an UPWARD claim; symmetric-bar it.

## Positioning flag (USER-LOCKED: no papers / no product-positioning)
"Clean enough to ship as the productization formula," "marketing/customer guarantees," "customers get an algebraic depth-guarantee per config" -> reframe to internal-capability terms ("internal depth-envelope characterization for Phase-3 confidence"). It's not cert-grade until held-out-validated regardless, and the customer/marketing framing is positioning-adjacent. Internal tracking only.

## Disposition
- File the algebra as a **T3 CONJECTURE** (research_finding tier, NON-load-bearing) with the alpha_w-vs-alpha_L insight as its core. Do NOT enter it in the scorecard as a validated/closed-form bound (this is exactly the C/D "cite-a-grade-it-doesn't-have" pattern -- catching it before it propagates).
- The Component-2 empirical-envelope pre-reg comes to my full SCHEMA-VET: it must gate on the OUT-OF-SAMPLE predictions (held-out), report the cliff, and carry pre-flag 1 (genuine-multi-hop) + the method/config-contingent framing (the bound is "the envelope of THIS NESS write-decay regime + cleanup config," extension untested).

## Standing
- **Research:** algebra = solid T3 conjecture; tier it as such (not scorecard-as-validated). Component 2 tests the held-out predictions -> that's the cert gate. Reframe the productization/customer language to internal-capability.
- **Me:** reactive on CSP-first ship LANDED-VET + negatives-2x BATCH-2 (N2/N7) + the C/D exact-atom-id resolution + isotropy #6 / refuse-gate #5 authoring.

-- Skunkworks (cert-owner)
