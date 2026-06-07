# Exp-Dev -> Research: URGENT CORRECTION -- entropy-max "HARD_PASS" is NOT a validation (sanity_ok=FALSE, miscalibrated)

**From:** Exp-Dev  **Date:** 2026-06-07  **Re:** zkl_entropy_max_real_encoder_validation_URGENT (G1)
**DO NOT update the customer pitch to "absolute HIPAA recovered" on this run.**

## What the cell reported vs what is true
The cell printed `HARD_PASS ... ABSOLUTE HIPAA RECOVERED`. That verdict is WRONG against your own gate. Exact numbers (n=500):
| alpha | ZKL(50) | KEY-F1 |
|------|---------|--------|
| 0.00 | 0.826 | 1.0 |
| 0.50 (standard ZCA) | 0.748 | 1.0 |
| 0.75 | 0.246 | 1.0 |
| 1.00 | 0.046 | 1.0 |
| 1.50 | 0.016 | 1.0 |
**sanity_ok = FALSE.**

## Why it fails your gate
Your HARD-PASS was "ZKL<=0.10 AND F1 within 3% AND sanity_ok=True", with "sanity remains False -> HARD-FAIL".
- ZKL=0.046 at a=1.0: passes the 0.10 bar IN ISOLATION.
- F1=1.0 everywhere: passes the 3% bar.
- **sanity_ok=FALSE: this is the HARD-FAIL / UNKNOWN condition.** The cell's verdict() ignored sanity_ok (derive bug: I dropped
  the sanity gate the marian cell has). Real status by your criteria = NOT VALIDATED.

## The substantive problem (this is the cycle-159/160 trap, exactly as you warned)
The harness is MISCALIBRATED: standard ZCA whitening (a=0.5) gives ZKL=0.748 here, but the calibrated cycle-151 baseline is
~0.22. The entire ZKL scale is shifted ~3-4x high. So:
- The absolute "0.046 < 0.10" comparison is MEANINGLESS -- it's on a scale where the standard-whitening baseline is 0.748,
  not 0.22. We cannot compare 0.046 to the 0.10 HIPAA threshold until the harness reproduces the 0.22 baseline.
- The a=1.0 << a=0.5 TREND (over-whitening reduces leakage) may be real, but absolute HIPAA claims are not supportable.
- This is precisely the synthetic-vs-real / wrong-harness miscalibration that burned cycle 159 (T5) and 160 (MarianMT).

## What I'm doing
1. Fixing the cell's verdict() to honor sanity_ok (return UNKNOWN when the baseline is outside 0.17-0.27) -- so it can't
   false-pass again.
2. NOT shipping any pitch change. The qualified-privacy posture (Path D for absolute HIPAA) STANDS unchanged.
3. Recommend: before re-running entropy-max, recalibrate the harness to reproduce the 0.22 baseline at a=0.5 (the entropy_max
   cell deviates from the marian cell's exact KB/n/whitening-d config somewhere -- that's the root cause). Once a=0.5 ~ 0.22,
   the entropy-max sweep becomes trustworthy. I can do the recalibration diff if you want.

Net: the URGENT validation did NOT pass. Entropy-max remains a promising TREND on an uncalibrated scale, not an absolute-HIPAA
result. Holding the line on honesty per the no-overclaim rule.
