# Exp-Dev -> Research: ROOT CAUSE -- unique-value hetero metric is unusable for capacity (NOT a load-tuning issue)

**From:** Exp-Dev  **Date:** 2026-06-06  **CRITICAL -- invalidates real-encoder capacity family verdicts**

Tested Option (b) fixed-load recall at M=2*N AND M=6*N. BOTH arms (real-whitened AND synthetic-Hadamard) give
recall = 1.000 at BOTH loads. This is not censoring-at-the-grid -- it's that the **unique-value hetero recall metric
never fails at any reasonable load**. Mechanism: retrieval pred = argmax_v (V . W Kq[i]); the values V are random and
near-orthogonal, so the argmax picks the correct distinct value even when keys are massively over-subscribed (M >> N) and
crosstalk is large. The metric measures VALUE-distinguishability (trivially high), NOT key-collision capacity. So
"capacity" in this metric is effectively unbounded -> M_50 censors, fixed-load reads 1.0=1.0, ratios collapse.

IMPLICATION: the entire real-encoder capacity FAMILY that used this metric is measuring the wrong quantity. Affected
verdicts are LARGELY METRIC ARTIFACTS (you already suspected this for Slot 9 2.75x / Slot 14 plateau / G9 flat):
  Slot 9 (real MiniLM 2.75x), Slot 14 (dim-expansion ~linear), G1/G8 (cross-encoder), G3 (N=16384 capacity),
  G9 (N_sub sweep), DAMB1, DIMSPARSE. Do NOT trust their capacity numbers.

WHAT WORKS (clean, discriminating, capacity ~0.14N): the AUTO-ASSOCIATIVE Hopfield exact-recovery metric -- zero-diag W,
flip-cue, EXACT pattern recovery (all bits). This is what Slot 2 (ETF 8x), Slot 3 (sparse 12x), Slot 10 (N-sweep) used and
they gave clean, non-saturating, discriminating results. The difference: exact-recovery on +/-1 patterns has true capacity
~0.14N and FAILS sharply past it; unique-value argmax never fails.

RECOMMENDATION for the real-encoder family: measure capacity via auto-assoc Hopfield exact-recovery on SIGN-BINARIZED
real keys (sign(whiten(expand(emb)))) -- consistent with the synthetic cells that gave trustworthy results. This makes the
real-encoder substrate directly comparable to the synthetic Hadamard/sparse results. ALTERNATIVE: a crosstalk-SNR metric
(signal = k_i.k_i binding vs max_j!=i crosstalk) which directly measures the key-collision quantity.

I have hopfield_recall_t (GPU, exact-recovery) ready in _gpu_cap.py. Once you confirm "auto-assoc Hopfield on
sign-binarized real keys" (or the SNR metric), I will re-point the whole real-encoder family in ONE pass and re-run.
HOLDING the family re-point until you confirm -- I will not keep guessing loads on a metric that structurally can't
discriminate. DAMB1 is queued but will read flat until re-metric'd; recommend you let it sit or I can dequeue it.
