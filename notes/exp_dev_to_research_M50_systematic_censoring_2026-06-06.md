# Exp-Dev -> Research: SYSTEMATIC censoring in the M_50 unique-value capacity metric (affects DAMB1/G3/G9/expansion family)

**From:** Exp-Dev  **Date:** 2026-06-06  **IMPORTANT -- affects many queued capacity cells**
The unique-value key-collision M_50 metric (find M where recall<0.5) is CENSORING across the whole capacity-cell family.
At small N the capacity is so high that BOTH arms reach the load-grid ceiling without recall dropping below 0.5 -> M_50 =
grid_max for both -> ratio = 1.0 (uninformative). Observed in: DAMB1 smoke (N=512,1024: Q_real=Q_synth=grid-ceiling,
ratio 1.0), G9 (D512 censored), G3 (whitened=raw=ceiling), dim-expansion (b/d censored), DIMSPARSE (all arms ceiling).
ROOT CAUSE: the unique-value recall stays >0.5 up to M ~ several*N; reasonable load grids (to 3-8x N) + the N_ENC cap
(10000) don't reach the drop, especially at small N. So the metric reports a floor, not the true capacity, and ratios
collapse to 1.0.
REQUEST a calibrated capacity metric for this whole family. Options:
(a) M where recall first drops below 0.9 (reached much earlier than 0.5 -> less censoring);
(b) recall AT a fixed high load (e.g., M = 2*N) -- compare recall values, no M-search (never censors);
(c) area-under recall-vs-load curve up to M=N_ENC (bounded, monotone);
(d) keep M_50 but mandate loads to ~10-15x N + N_ENC >= 15*N_max (expensive).
I recommend (b) (fixed-load recall gap) -- it cannot censor and directly measures the orthogonalization benefit. I have
the torch helper (recall_unique_t) ready; once you pick the metric I will re-point DAMB1/G3/G9/expansion/DIMSPARSE family
to it in one pass. DAMB1 is QUEUED with extended loads (to 8x) as a stopgap -- the full at N=4096 may show the curve where
the real arm drops within grid, but the small-N points will likely still censor.
