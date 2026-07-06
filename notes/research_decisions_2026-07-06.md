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
