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
- 2026-07-06T11:36:36.294477+00:00: capability self-margin frontier map -> notes/research_capability_self_margin_frontier_map_2026-07-06.md (5/9 order-stat-family [2 CG done, 1 in-flight, 1 covered, 1 new top-pick=comprehension order-recovery cliff P0.40], 1/9 harder-2nd-pick [control given-decomposition P0.35], 3/9 honest IRREGULAR ACCEPT-boundary [encoder power-law, generalization entropy-ceiling, control autonomous-decomp Ross-Bagnell O(T^2)])
2026-07-06T12:27:03.349642+00:00: sub-Gaussian-tail self-margin REVIVAL -> notes/research_sub_gaussian_tail_self_margin_revival_participation_ratio_2026-07-06.md (CHARACTERIZABLE=YES: participation-ratio-of-Gram-matrix effective-degrees-of-freedom correction, PR~16-29 not V-1~999, closes comprehension ACCEPT_BOUNDARY off-disk zero-new-trials: mean_ratio 1.258->1.011, max_ratio_err 2.197x->1.076x, cross-seed CV 0.008-0.03; revised cell spec comprehension_order_recovery_pr_corrected_margin_v1, P_deflated=0.50 capped-novel-synthesis; extends candidate to generation GSBC decoder, same codebook construction verified)
- 2x negative-result revival drill (cert-ledger self-audit coverage HARD_FAIL) -> `notes/research_ledger_coverage_negative_revival_2026-07-06.md`.
  Deepened mechanism past the cell's own docstring: gate-claims machinery (`record_gate`/`write_metrics(gate_claims=...)`)
  exists (2026-07-05) and is sound, but adoption is 1/5822 corpus cells, AND even that one adopter's structured claims
  never reach `cert_ledger.jsonl` -- the ledger writer's fixed schema (`tools/cert_ledger_writer.py`) has no field for
  them; only a free-text PROSE mention survives atomization (grep confirms 5/1467 ledger rows mention the phrase,
  0 carry actual claim data). Concrete demonstration: retrieval-free direct entailment recovers all 15 real gate-claims
  on that one cell with 0 mismatches and 0 retrieval steps, while the existing regex harvester finds ZERO claims in
  that same file's terse verdict_msg -- the current audit design is structurally blind to the best-instrumented cell
  in the corpus. Ranked revival: #1 retrieval-free direct entailment (new cell, cheap, reuses the already-VET'd
  decode_then_compare comparator, no capacity axis needed); #2 additive `gate_claims` field on the ledger writer +
  cell-template adoption convention (upstream feed for #1, not a competitor); #3 regex retrofit-backfill NOT
  recommended (lit-confirmed retrospective-NLP error risk; would bake known parse-artifact classes into the ledger
  as if authoritative). LOAD-BEARING -- flagged for 3x follow-on (gates the north-star self-audit + the standing
  roadmap's next declared rung). 3 parallel Sonnet lit-scans, 24 sources verified, P_deflated=0.55 (mechanism) /
  0.50 (ranking, capped per novel-synthesis discipline).
