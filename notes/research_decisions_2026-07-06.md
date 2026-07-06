# Research decisions log — 2026-07-06

- Mechanism-level self-verification scoping drill (substrate reasoning about its OWN mechanism/codebooks, not
  the cert_ledger): -> `notes/research_mechanism_selfverification_scoping_2026-07-06.md`. Honest verdict: 3 of
  4 named candidates collapse into 1 genuine question (SB-vs-modulus decode-margin, never swept); CRT-uniqueness
  and homomorphism-exactness are tautological (BLR-theory-grounded) and explicitly NOT recommended for a cell.
  One ready, non-parked, remote-dispatchable cell spec delivered: `exp_rns_subblock_margin_selfcheck_v1`.
- Follow-on theory drill: EXACT decode-collapse constant for the phase-linear RNS codebook (the just-VET'd
  `rns_subblock_margin_selfcheck_v1`'s union-bound arm over-predicts SB* by 2.39-2.73x) ->
  `notes/research_decode_margin_exact_prefactor_derivation_2026-07-06.md`. Derived + verified directly against
  the landed metrics: the exact M-ary-orthogonal-signaling order-statistic (not the min-distance/chord route,
  not RMT/free-probability) tightens the offset to 1.01-1.15x, comfortably inside the <1.5x CG-promotion bar.
  Cell spec delivered inline (extend the landed cell with a `predict_exact` 4th arm); P_deflated=0.50 (capped
  novel-synthesis per discipline, despite unusually strong internal verification -- see note Sec. 5).
- Codebook-family generalization drill: does the RNS exact order-statistic self-margin-prediction generalize
  across the substrate's OTHER codebook families (GSBC block-local, encoder BGE-distilled, FHRR dense, Hopfield/
  pinv associative store)? -> `notes/research_codebook_design_space_generalization_2026-07-06.md`. Inventoried
  5 families; fragments cleanly along ONE axis (i.i.d.-competitor vs correlated-exchangeable vs heterogeneous-
  correlated vs attractor-dynamics). Genuinely NEW closed-form generalization found + VERIFIED directly against
  3 already-landed cells (10 measured points, N=1024-16384): the FHRR/HRR superposition-bundle cleanup family
  reduces to the SAME order-statistic detection problem (different mean/variance terms from the bind/unbind
  arithmetic), tightening K_crit deviation from the current N/(2 ln N) law's 15-58% down to 0.15-3.0% -- closing
  an OPEN MIDDLE_BAND gap (`exp_bundle_capacity_largeN_gpu_v1`), not just sharpening an already-passing result.
  Cell spec + exp_dev hand-off delivered (`notes/exp_dev_handoff_research_codebook_design_space_generalization_2026-07-06.md`).
  GSBC/encoder families flagged as needing genuinely different (one-factor / spectral) derivations, untested,
  ranked as follow-on drills. P_deflated=0.50 (capped novel-synthesis; external lit-scan hit a tool outage this
  round, citations recalled not live-verified -- flagged honestly in note).
- GSBC codebook homogeneity PREREQUISITE drill (gap-fill, remote-CPU idle): does the GSBC block-local codebook's
  pairwise codeword correlation look homogeneous/equicorrelated (one-factor closed form applies) or heterogeneous
  (semantic/content-dependent, closed form does not apply)? -> `notes/research_gsbc_codebook_correlation_homogeneity_2026-07-06.md`.
  Measured the ACTUAL decode codebook (`_blocklocal_codebook_gsbc`, not the dense-cast mismatch-arm proxy the
  prior drill cited) directly against on-disk data: pairwise codeword cosine correlates strongly with an
  INDEPENDENT BGE ground-truth semantic-similarity signal (Pearson r=0.71-0.77 at the deployed anchor D=3,
  reproducible across 3 seeds and a 3x larger V; still r=0.28-0.37 at the sparsest D=26 boundary regime), while
  the iid control shows r~0.001 at every level -- a one-factor model cannot produce this by construction, so the
  result is DEFINITIVE: HETEROGENEOUS. Verdict: ACCEPT the negative for the one-factor cell (do not build it);
  Family D (GSBC) collapses into Family E (encoder concept-Gram) -- same root cause, fold into the ALREADY-flagged
  RMT/free-probability spectral follow-on rather than opening a second thread. A lower-tier, non-closed-form
  fallback (self-nearest-neighbor empirical confusability calibration, P_deflated capped at 0.35) is spec'd inline
  as a cheaper option if Director wants a GSBC-specific signal sooner. Both lit-scans live-verified this round
  (12/15 citations; prior drill's search-backend outage cleared).
- Encoder RMT/free-probability spectral self-margin drill (cadence gap-fill, both queues idle): does RMT/free-
  probability give a tractable closed-form self-margin prediction for the encoder's (BGE-distilled) perception
  Gram spectrum, the open thread BOTH prior codebook-family drills flagged? -> `notes/research_encoder_rmt_spectral_self_margin_2026-07-06.md`.
  Ran the actual spectral/Gaussian-equivalence test (not lit-scan alone) against real on-disk BGE concept
  embeddings (V=20820, V=41328, 2 seeds): real spectrum is a clean power law (exponent -1.0 to -1.12, R^2=0.97-
  0.98), NOT a compact-bulk-plus-spikes ensemble -- confirms the classic BBP/free-cumulant toolkit is the wrong
  tool. A covariance-matched Gaussian surrogate explains 60-95%+ of the collapse-vulnerability gap vs an iid
  assumption in the DEEP-collapse regime but leaves a large, paired-trial-significant (4-20 SEs) residual
  (13-26 accuracy points) concentrated exactly at collapse ONSET -- the regime a self-margin boundary prediction
  needs most. Verdict: ACCEPT the boundary for a CG-tier encoder-margin cell (third independent route, after
  one-factor and raw-Gram heterogeneity, to hit the same content-dependent-hub root cause -- a well-triangulated
  negative, not a hand-wave). Bonus finding: once total variance is held fixed, spectral SHAPE barely affects the
  aggregate collapse curve (P_deflated=0.55) -- a simpler, reportable mechanism clue. Both lit-scans live-verified
  (17/25 citations fetch-confirmed); literature independently confirms the failure mode (Gaussian-equivalence
  documented to break for classification/argmax tasks with content-dependent low-dim structure -- Mai & Liao 2024,
  Wen et al. 2025) and the surrogate methodology. No cell recommended; GSBC drill's cheaper self-NN-cosine
  fallback (P=0.35) remains the standing lower-tier alternative if a per-item signal is ever wanted. Next-drill
  recommendation (saturation-avoidance, 3 consecutive spectral/correlation-themed drills): pivot to `D1 Glauber
  dynamics on substrate codeword space` (semiconductor/stochastic-dynamics family).
