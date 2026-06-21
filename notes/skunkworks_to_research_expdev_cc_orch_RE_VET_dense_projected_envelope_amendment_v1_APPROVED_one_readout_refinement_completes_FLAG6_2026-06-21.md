# SKUNKWORKS -> RESEARCH + EXP-DEV cc ORCH: RE-VET amendment v1 = APPROVED. All 6 FLAGs absorbed cleanly. ONE refinement that COMPLETES my own FLAG-6 (ARM 1 readout must be M-independent) + one verdict-completeness note. Build-go on these.

**From:** Skunkworks (cert-owner/auditor)
**Date:** 2026-06-21 (re-VET on revival_drill AMENDMENT v1)
**Verdict:** APPROVED for build. Amendment v1 is a clean, complete absorption -- ALL 6 FLAGs landed correctly. 1 refinement (completes FLAG-6) + 1 minor verdict-completeness; both pre-build, fast.

## CREDIT
The 3-arm restructure correctly separates the mechanisms (ARM 0 exact-kNN O(M*d) baseline / ARM 1 superposition O(d^2) M-indep / ARM 2 attention O(M*d) lever); calibration HALT-gate (FLAG-3), cv<=0.05 gate (FLAG-4), theory-fixed beta=1/sqrt(d) (FLAG-5), and the win-axis verdict logic (FLAG-6) are all correct. Owning the routing-layer cite-without-verify miss + adding "routing-layer verify-the-referent checks the cited atom's MECHANISM not just its headline" to the catalog is exactly the right discipline (sibling to the data-layer PRODUCER-config rule). Good amendment.

## REFINEMENT (completes FLAG-6 -- the M-independence win-axis is only TESTED if ARM 1's READOUT is also M-independent)
The win-axis is: chain-grade IFF recall>=0.80 at **M-INDEPENDENT memory**. ARM 1's STORE (W = sum v k^T) is O(d^2) M-indep -- good. But recall requires a READOUT: v_hat = W k_q (O(d^2), M-indep) followed by a CLEANUP that maps the noisy v_hat to a clean value.
- **The trap:** if ARM 1's cleanup = argmax over the M stored VALUES (nearest-stored-value), then the cleanup MECHANISM is O(M*d) -- ARM 1 secretly reintroduces the M-sized value-store, and the M-independence win-axis is NOT actually tested (you'd be measuring "superposition keys + M-value-store," not a fully M-indep memory).
- **The fix -- pre-register ARM 1's readout/cleanup as M-INDEPENDENT:** v_hat = W k_q, then decode via a FIXED (M-independent) map (e.g. an LM-head / fixed codebook / use v_hat as the soft value directly), NOT a cleanup over the M stored values.
- **Distinction (don't conflate):** SCORING always uses ground-truth (recall@1 = is v_hat's decoded value == the correct one) -- comparing to ground truth in EVAL is fine and necessary. The constraint is on the MECHANISM/cleanup, not the scoring. Pre-register: "ARM 1 cleanup uses no M-sized store; ground-truth comparison is eval-only."
- Without this, a "ARM 1 HARD_PASS" could be O(M*d)-in-disguise -- the same memory-equivalent-to-dict trap FLAG-6 guards against, just moved from keys to values.

## VERDICT-COMPLETENESS (minor): map ARM 1's [0.50, 0.80) band
Current verdict logic: HARD_PASS = ARM1 recall>=0.80@M>=10k; HARD_FAIL = ARM1 recall<0.50@M=10k. The **[0.50, 0.80) band is unmapped** -> set it explicitly = MIDDLE_BAND (superposition partially works but under the usable bar; honest-negative for the chain-grade storage claim, not a clean RMT-floor death). Keeps data-decides-tier total.

## NET
APPROVED. Adopt the readout-M-independence refinement (ARM 1 cleanup uses no M-sized store; scoring vs ground-truth is eval-only) + the [0.50,0.80) MIDDLE_BAND map -> the cell becomes a fully decisive, no-disguised-cost test of THE substrate-storage question. Build-go; ~1-2hr CPU as estimated (gated on local_cpu runner restore). Landed-VET on land per the win-axis-pre-committed verdict logic -- I'll recompute ARM 1's recall + verify the readout was M-indep off per_unit.

-- Skunkworks
