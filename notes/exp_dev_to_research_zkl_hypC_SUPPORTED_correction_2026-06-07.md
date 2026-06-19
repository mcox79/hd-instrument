# Exp-Dev -> Research: CORRECTION -- Hyp C IS supported (confound removed); reopens a mitigation avenue

**From:** Exp-Dev  **Date:** 2026-06-07  **Re:** zkl_hypC_confirmatory_authorize

The confound I flagged was real and decisive. Confirmatory re-run (smoke n=100):
  RAW (unwhitened):        MM=0.683 MN=0.653  gap=+0.030  KS p=1.5e-70
  NEUTRAL (held-out basis): MM=0.132 MN=0.078  gap=+0.055  KS p=5.8e-136
Both show member-member cosines SYSTEMATICALLY HIGHER than member-nonmember (gap>0, p<<0.01). **Hyp C is SUPPORTED.**
The earlier HARD_FAIL (gap=-0.008) was purely the stored-cohort whitening artificially isotropizing MM -- a confound, not
a real negative.

## Implication: the privacy thread should NOT be fully closed yet
The leak has (at least) TWO structural mechanisms: Hyp B (token-position concentration, top-3=86%) AND Hyp C (member-member
Gram/rank structure). The lock-qualified decision was based on Hyp-B mitigations failing -- but the Hyp-C mitigation family
(rank-randomization at scoring AND retrieval; cosine-entropy whitening) was NEVER tested (I'd prematurely ruled C out on the
confounded result). This is a fresh, untested avenue that could still reach ZKL<=0.10.

## Recommendation
1. Authorize Hyp-C mitigation tests on the calibrated MarianMT harness:
   - Rank-randomization at SCORING: add calibrated rank noise to the membership score (Mallows-style) -- but this is an
     ATTACK-side defense; the real question is whether a STORAGE-side transform flattens the MM>MN gap.
   - Cosine-entropy whitening: a whitening variant that equalizes the MM/MN cosine distributions (maximize cosine entropy).
   - Test ZKL(50) + KEY-job F1 for each.
2. HOLD the "absolute-HIPAA-impossible-via-linear-methods" conclusion -- Hyp-C-targeted transforms are a distinct linear
   family from the Hyp-B (position) ones that failed. The qualified posture stands as the SAFE interim claim, but the door
   is not closed.
Queued: zkl_hypC_confirmatory_v1 (full n=400) to confirm MM>MN at scale.
