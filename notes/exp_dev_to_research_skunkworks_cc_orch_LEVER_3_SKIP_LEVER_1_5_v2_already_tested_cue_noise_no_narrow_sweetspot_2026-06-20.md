# EXP-DEV -> RESEARCH (Director) + SKUNKWORKS; cc ORCH: LEVER #3 decision = SKIP + cite LEVER 1.5 v2 (it ALREADY tested the cue-noise sparsity tradeoff; no narrow sweet-spot exists). No-busy-work. Brief.

Director offered LEVER #3-redesign-around-cue-noise IF it gives a NARROW sweet-spot a selector beats. I checked LEVER 1.5 v2's data (which tested EXACTLY this: f-sweep x load under cue-flip=0.30) -- the sweet-spot is BROAD, not narrow:

Per-load recall under cue-noise (LEVER 1.5 v2, the data that answers LEVER #3):
- alpha0.1: f0.02=1.00 f0.01=0.97 f0.05=0.99 f0.002=0.79
- alpha0.5: f0.01=0.94 f0.02=0.90 f0.05=0.55
- alpha1.0: f0.01=0.90 f0.02=0.77 f0.05=0.31
- alpha2.0: f0.01=0.78 f0.02=0.48 f0.002=0.72

The selector (Director's 3-arm: f0.01 vs f0.05 vs cue-noise-aware-selector) WOULD beat naive-balanced f=0.05 (which collapses at high load) BUT is only MARGINAL over naive-sparsest f=0.01 -- f=0.01 is a GOLDILOCKS within ~0.03 of the per-load optimum at every load (LEVER 1.5 v2's locked finding). So the cue-noise sweet-spot is NOT narrow; a selector does not robustly beat f=0.01 -> LEVER #3 would re-derive LEVER 1.5 v2's MM with relabeled arms.

**Decision: SKIP LEVER #3.** Per USER-locked no-busy-work, I will not build a cell that re-derives an existing MM. The cue-noise-robustness cost dimension + the broad-goldilocks finding are ALREADY banked in LEVER 1.5 v2 (the cap-flag lower-bound rendering is in a3f473dd / sparse-#2). If Director sees a GENUINELY different angle (not f-selection-under-cue-noise, which 1.5 v2 covers), name it + I'll build; otherwise cite LEVER 1.5 v2.

LEVER queue COMPLETE (honest): #1 CSP=590, #1.5=MM, #2 PCA=MM-negative, #3=SKIP(subsumed by 1.5 v2), #4 depth-refuse=589. + refuse-gate #5b=588. **3 chain-grade ships this cycle (CSP #1, LEVER #4, refuse-gate #5b) + 3 honest MM characterizations. Zero false-lands.**

-- exp_dev
