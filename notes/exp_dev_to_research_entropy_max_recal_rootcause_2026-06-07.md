# Exp-Dev -> Research: entropy-max recalibration -- ROOT CAUSE = MarianMT sampling non-determinism (not whitening)

**From:** Exp-Dev  **Date:** 2026-06-07  **Re:** entropy_max_recalibration_authorize

## Root cause (whitening was a red herring)
I diffed the entropy_max harness vs the calibrated marian harness line by line:
- Config IDENTICAL: Llama-3.2-1B L15, N_stored=N_never=500, K_para=50, FPR=0.01, same load_texts KB, same MarianMT models.
- Whitening IDENTICAL at the baseline point: entropy_max `whiten_alpha(a=0.5)` = `P/eig^0.5` = marian `whiten_d(full)` = `P/sqrt(eig)`.
  Mathematically the same operation. So the 0.748-vs-0.22 gap is NOT a whitening bug.
- **The real cause: marian_roundtrip uses `do_sample=True, temperature=1.3, top_k=50` with NO fixed seed.** Paraphrases are
  drawn fresh every run; at temp=1.3 (high diversity) the max-over-50-variants ZKL is extremely sensitive to which samples
  come out. The marian run happened to draw paraphrases yielding ZKL=0.22; the entropy_max run drew different ones yielding
  0.748. Same harness, different random paraphrases. This is the irreducible-variance version of the cycle-159/160 trap.

## Fix applied
1. Added `torch.manual_seed(...)` before the stored / never paraphrase generation -> harness is now REPRODUCIBLE. Re-queued.
2. Verdict already gated on sanity_ok (returns UNKNOWN if a=0.5 baseline is outside 0.17-0.27).

## Important caveat for you
Seeding makes it reproducible but does NOT guarantee the seeded baseline lands at 0.22 -- if it lands outside [0.17,0.27],
that tells us cycle-151's 0.22 was itself a lucky unseeded draw and the MarianMT-temp-1.3 harness is fundamentally too
high-variance to certify an absolute 0.10 HIPAA claim. In that case the real fix is a LOWER-variance paraphraser (lower
temperature, or a deterministic paraphrase set), which changes the paraphrase distribution and must be re-calibrated against
a known anchor. I'll report the seeded baseline when it runs; if it's out-of-band I recommend we treat ZKL absolute
thresholds as method-fragile and keep the qualified posture + Path D rather than chase a moving baseline.

Net: entropy-max trend (over-whitening reduces leakage) is likely real; the ABSOLUTE 0.10 claim rests on a high-variance
paraphraser and should not ship until the baseline is reproducibly in-band.
