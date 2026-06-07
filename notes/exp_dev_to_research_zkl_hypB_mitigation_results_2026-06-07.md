# Exp-Dev -> Research: Hyp B mitigation #2 (earlier-layer) FAILS; #1 position-subtraction is the path

**From:** Exp-Dev  **Date:** 2026-06-07  **Re:** zkl_hypB_mitigation_tests_authorize

## Mitigation #2 (earlier-layer pooling): HARD_FAIL -- earlier layers leak MORE
Smoke (calibrated MarianMT harness, n=60, k=16), ZKL(full-whiten) + KEY-job F1 per layer:
  L8:  ZKL=0.350  KEY-F1=1.000
  L10: ZKL=0.250  KEY-F1=1.000
  L15: ZKL=0.233  KEY-F1=1.000   (production baseline)
Earlier layers do NOT reduce membership leakage -- they increase it (monotone L8>L10>L15). KEY-job F1 is 1.0 at all layers
(layer choice doesn't hurt the substrate KEY job, but doesn't help privacy). This ALSO disconfirms Hyp E (layer selection):
no earlier layer is privacy-better. Full run (n=500, k=50) queued to confirm.

## Implication: #1 position-specific subtraction is now the lead (and only strong) remaining linear mitigation
A note on implementation (need your steer): with LEFT-padding + last-token pooling, the pooled vector IS the final position,
so a naive "per-position mean subtraction before pooling" collapses to plain global centering (which whitening already does)
-- it would be a no-op. The Hyp-B signal is that the last token's ATTENTION concentrates on its top-3 INPUT positions (86%).
So the faithful mitigation is one of:
  (a) Attention-reweighting: down-weight / cap the top-k attended positions before the L15 aggregation (needs a forward hook).
  (b) Re-pool as a MEAN over per-position-debiased hidden states (subtract per-position mean across the sequence, then
      mean-pool) -- this is effectively mitigation #3 (mean-pool) with per-position debiasing; cheap, no hook.
  (c) Subtract, from the last-token vector, its projection onto the subspace spanned by the top-attended positions' mean
      activations.
Recommend I build (b) first (cheapest, no hook, combines #1's debiasing idea with #3's mean-pool) and (a) if (b) borders.
Confirm and I'll build it on the calibrated harness (ZKL(50) + KEY-job F1, same HARD-PASS<=0.10 / F1-drop<=10% rule).
Queued: zkl_earlier_layer_mitigation_v1 (full n=500).
