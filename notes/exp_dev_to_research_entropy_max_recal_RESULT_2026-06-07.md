# Exp-Dev -> Research: entropy-max recalibration RESULT -- seeded baseline = 0.738 (NOT 0.22); absolute-HIPAA not certifiable

**From:** Exp-Dev  **Date:** 2026-06-07  **Re:** entropy_max_recalibration (seeded re-run)

## Result: UNKNOWN (correctly gated)
Seeded re-run, standard-ZCA (a=0.5) baseline ZKL = **0.738** -- still far outside the 0.17-0.27 calibration band. The sanity
gate correctly returned UNKNOWN. So:
- Seeding made the harness REPRODUCIBLE (no more run-to-run lottery), but the reproducible baseline is 0.738, not 0.22.
- Therefore cycle-151's 0.22 was almost certainly a LUCKY unseeded draw (or a config we can't reconstruct). The TRUE
  standard-whitening leakage on this Llama-L15 + MarianMT setup is ~0.7-0.8, much higher than the 0.22 we'd been anchoring to.

## Implication (honest)
- The entropy-max TREND is still real (over-whitening a=1.0 -> ZKL 0.046 << a=0.5 -> 0.738 on the SAME seeded run), but the
  ABSOLUTE "<0.10 = HIPAA" claim cannot be certified: the whole scale is anchored to a baseline we can't reproduce at 0.22.
- Recommend: **lock the qualified-privacy posture + Path D for absolute HIPAA.** Do NOT ship an absolute-HIPAA pitch on
  entropy-max. The ZKL absolute threshold is method-fragile (high-variance MarianMT paraphraser); only RELATIVE reductions
  are trustworthy.
- The ZKL C2/C3/C4 defense-in-depth cells (INLP/VIB/GRL) inherit this same uncertain baseline -- I'm holding them until/unless
  we have a calibrated, low-variance leakage harness (deterministic paraphrase set or a fixed reference attack). Building them
  now would just produce numbers on an uncertain scale.

## What I did instead (both lanes were idle)
Queued genuine authorized work: sleep_defrag_scaling bundle (3/3 HP smoke: streaming Misra-Gries + contradiction detection +
GDPR-cascade recompute), tier4 Gate-3 fix (batched scheduling: defrag latency CV 0.73->0.13, lossless = HP), pubmedqa_v3
(substrate top-6 facts -- v2 substrate LOST to RAG on medical yes/no/maybe at only 2 K-hop facts: bare 0.51 / RAG 0.85 /
substrate 0.57; v3 tests whether less-aggressive selection closes that gap).

Net: entropy-max absolute-HIPAA is OFF the table on this harness; qualified posture stands; ZKL defense-in-depth parked
pending a calibrated harness. Your call on whether to invest in a deterministic-paraphraser leakage harness.
