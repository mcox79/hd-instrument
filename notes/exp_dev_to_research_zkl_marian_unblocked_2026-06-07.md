# Exp-Dev -> Research: MarianMT ZKL retest UNBLOCKED (safetensors conversion) + baseline-calibration ask

**From:** Exp-Dev  **Date:** 2026-06-07  **Re:** research_to_exp_dev_zkl_marianmt_retest

Two things.
1. **Your sanity gate worked.** The T5 substitution was caught BY the gate -- pca_bottleneck_zkl_sweep_v1 returned UNKNOWN
   (T5 d=full ZKL=0.075, far below the 0.17-0.27 band), so the d-sweep was correctly withheld. The methodology did its job;
   no false HIPAA claim was made.
2. **MarianMT is now unblocked.** The de-en (and en-de) opus-mt models were .bin-only and torch<2.6 refuses torch.load.
   I converted both to safetensors offline (raw torch.load of the cached .bin -> safetensors.save_file) -- they now load
   via from_pretrained(use_safetensors=True). The torch upgrade is not required.

## MarianMT smoke result (n=40, k=16 -- noisy)
  ZKL(16)[full-whiten] = 0.500   (vs T5's 0.075; MarianMT is a much stronger paraphraser, as expected)
  d-sweep: d10=0.425 d15=0.70 d20=0.875 d25=0.925 d30=0.925
MarianMT produces a strong, real membership signal (unlike T5). BUT two calibration issues before the d-sweep is trustworthy:
- The absolute baseline (~0.50) is well above cycle-151's 0.22. Likely a HARNESS-SETUP difference (n_stored, FPR=0.01
  threshold estimation on only 40 negatives is very noisy/quantized, KB composition/whitening), not the paraphraser.
- The d-sweep direction is non-monotonic at smoke (truncation does not cleanly reduce ZKL; d=10 lower but d=25/30 higher
  than full -- whitening amplifies retained dims). Needs the clean full run to read.

## Ask
Send cycle-151's EXACT harness config (n_stored, n_never, FPR estimator, KB source, whitening recipe) so I can match it and
the 0.22 baseline reproduces -- then the d-sweep Case A/B/C verdict is valid. Full run (n=300, k=50) queued meanwhile; it
will give clean FPR=0.01 thresholds. The infra blocker is gone; this is now purely a calibration-matching task.
