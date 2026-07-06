# Prereg: fhrr_bundle_capacity_exact_margin_v1

## Anchor
fhrr_bundle_capacity_exact_margin_v1

## Queue
overnight_queue (GPU) for FULL. SMOKE = local torch-CPU (USER-lock smoke-only-local).
Cell: experiments/exp_fhrr_bundle_capacity_exact_margin_v1.py
Timeout (FULL): 1800 s (heartbeat + flush progress logging present; wall estimate ~1-2 min on GPU
based on landed largeN_gpu 5.9s for 2 N; generous headroom for GPU-queue variance).

## One-line
The substrate predicts its OWN FHRR/HRR bundle-cleanup capacity K_crit (how many role-filler pairs
superpose before recall@1 drops below 0.9) via an EXACT order-statistic formula, vs the loose
N/(2 ln N) asymptotic the 3 landed bundle-capacity cells currently use. Extends the just-landed RNS
exact-prefactor self-margin CG candidate to a SECOND codebook family AND closes the open MIDDLE_BAND
gap on exp_bundle_capacity_largeN_gpu_v1.

## Non-parked / referent
NON-PARKED. Self-contained synthetic phasor codebooks; no pool / re-encode / cert_ledger dependency;
zero referent. Monitor-not-control: REPORTS a tighter prediction number only; never edits N/K/V or any
landed cell's config/artifacts. NOT self-improvement. Brain-grounding: HONESTLY engineering (BIST /
noise-margin analysis -- conservative margin BOUND -> tight margin PREDICTION).

## Mechanism / derivation (THEORETICAL@notes/research_codebook_design_space_generalization_2026-07-06.md Sec.1/4)
bundle B = sum_k roles_k * book[fidx_k]; unbind rec = B * conj(roles_q) = book[fidx_q] + crosstalk
(sum of K-1 iid unit-random-phase vectors summed INCOHERENTLY -> variance ~K). Scoring rec against a
book of V iid codewords:
  sc[true]       ~ N(N, N*(K-1)/2)
  sc[competitor] ~ N(0, N*K/2)   iid across the V-1 non-true book entries
  P_correct = E_x[ Phi(x/sqrt(N*K/2))^(V-1) ], x ~ N(N, N*(K-1)/2).  K_crit = largest K with P>=0.9.
Same order-statistic family as the RNS codebook (independently re-derived; different mean/variance
terms), not a copy of the RNS formula.

## Arms
- measured            [MECHANISM]        fresh empirical K_crit (recall@1>=0.9 binary search; machinery
                                          reused VERBATIM from the 3 landed bundle cells).
- theory_exact        [PREDICTION]       kcrit_exact(N,V) order statistic -- the genuine new discriminator.
- theory_asymptotic   [CONTROL/BASELINE] N/(2 ln N), the landed cells' loose Plate-1995-style law (must
                                          stay 15-58% off).
- wrong_scaling       [CONTROL 1]        crosstalk summed COHERENTLY (amplitude) not INCOHERENTLY (power)
                                          -> variance ~K^2 -> predicts K_crit ~ sqrt(N). Must be clearly
                                          separated (isolates the power-summation scaling is load-bearing).
- degenerate_book     [CONTROL 2]        rank-1 (all-V-rows-identical) book -> cleanup at chance (~1/V).
                                          Must collapse (isolates distinguishable book STRUCTURE is
                                          load-bearing, not merely N dims).
- pointwise (N=4096)  [DIAGNOSTIC]       cliff-style K-sweep recall@1 vs pred_acc_exact (RMS).

## Config
V_book_cap = 5000; V_eff = min(5000, 4*N) per N (VERBATIM from landed theory_cpu book cap; exact pred
uses the SAME V_eff -> apples-to-apples). N_grid FULL = {1024, 2048, 4096, 8192, 16384}; SMOKE = {1024,
2048}. Pointwise N=4096, Ks FULL={50,100,200,400,600,800} SMOKE={50,200,400}. TR_kcrit FULL=12/SMOKE=6;
TR_point FULL=30/SMOKE=10. seed FULL=21/SMOKE=11. Predictions: numpy Gauss-Hermite 64pt + stdlib
math.erfc (NO scipy; GH64 MEASURED-converged to 5e-6 vs 96pt).

## Deviation metric
dev_X = |K_crit_measured - K_crit_X| / K_crit_measured (relative prediction error vs ground-truth
measurement), for X in {exact, asymptotic, wrong}. Pointwise: RMS(measured_recall, pred_exact_recall).

## Pre-registered bands (envelope-fail-bands)
### HARD-PASS (FULL)
- exact-arm dev_exact <= 0.05 at EVERY N in {1024,2048,4096,8192,16384}, AND
- exact >= 3x tighter than asymptotic at N >= 8192 (dev_asymptotic / dev_exact >= 3.0), AND
- pointwise recall-curve RMS <= 0.01 at N=4096, AND
- wrong-scaling control clearly separated (max dev_wrong >= 0.20), AND
- degenerate-book control collapses (max recall <= 0.02).
### HARD-FAIL
- dev_exact > 0.15 at ANY N (exact no tighter than the loose asymptotic -> iid-crosstalk independence
  did not generalize to fresh seeds/this V; keep reporting the asymptotic law), OR
- exact not >= 3x tighter than asymptotic at N >= 8192, OR
- a control fails (wrong-scaling not separated OR degenerate book does not collapse).
### MIDDLE
- exact relatively tighter than asymptotic (rel_improve holds at N>=8192) but dev_exact in (0.05, 0.15]
  at some N, OR pointwise RMS > 0.01.

## Author pre-dispatch verification (MEASURED@author recompute + smoke; zero new full trials)
- Exact vs 3 LANDED metrics.json (kcrit_exact recompute): dev 2.35%(N1024,V4096) 0.61%(N2048,V5000)
  0.30%(N8192,V4000) 0.15%(N16384,V4000); cliff pointwise RMS 0.0015. Asymptotic dev 15-58%.
  (Reproduces notes/research_codebook_design_space_generalization_2026-07-06.md Sec.1 table.)
- SMOKE (torch-CPU local, seed=11): HARD_PASS. dev_exact {N1024: 0.0000, N2048: 0.0182}; dev_asymptotic
  {0.110, 0.186}; dev_wrong ~0.89-0.93; degenerate recall max 0.001; pointwise RMS 0.0012.
- Expected FULL exact K_crit targets (V_eff): N1024=83 N2048=162 N4096=324 N8192=649 N16384=1298.

## DISCRIMINATOR-MUST-SURVIVE-SCALE
Option (B) analytical + already-verified-at-scale: the exact formula is EXACT by derivation and already
matches the LANDED large-N (8192, 16384) measured data at 0.15-0.30% dev (author recompute). The
asymptotic law's looseness GROWS with N (11% at N=1024 -> 58% at N=16384), so the discriminator is
STRONGEST at the large-N points re-measured fresh in FULL. Smoke additionally fires the discriminator at
the small N (exact <=1.82% vs asymptotic 11-19%, rel_improve >=2.5x, both controls fire).

## SCHEMA-VET fields
- cardinality_ok: true. EXPECTED_N_UNITS = len(N_grid) + len(pointwise_ks) = 5+6=11 (FULL) / 2+3=5 (SMOKE).
  Verdict emits cardinality_ok = (n_units >= expected).
- discriminator_fires: exact-arm demonstrably tighter than asymptotic + wrong-scaling separated +
  degenerate collapse; smoke gates on all three (ERROR-CORRECTION/PREDICTION-MATCH pattern).
- baseline_in_band (META_RULE_AG): PREDICTION-MATCH test, not a difficulty baseline. asymptotic arm is a
  declared loose CONTROL (15-58%); degenerate arm is a declared must-collapse CONTROL (~1/V) -- both
  exempt from the 0.05<score<0.95 rule. Measured recall spans chance..1.0 by construction.
- crlb / capacity-feasibility: this cell IS the capacity-feasibility instrument (K_crit is the M-ary
  order-statistic detection threshold). discriminator_reachability=True: K_crit bracketed in [10, 0.2*N]
  (retrospective K_crit 83-1298 < 0.2*16384=3276).
- discriminating_fraction (Gate B): pointwise K-sweep {50..800} at N=4096 spans measured recall 1.0->0.33;
  points at 400/600/800 in [0.30,0.70] band -> discriminating_fraction ~0.5 (>=0.30).
- sweep_alignment_verdict (Gate A): ALIGNED. V_eff is EXPLICIT per N; the exact prediction uses the SAME
  V_eff the measurement experiences (no nominal-vs-effective mismatch).
- positive_control (Gate D): the measurement machinery reproduces the landed bundle-capacity surface
  (verbatim cphasor/bind/unbind/argmax + book cap); fresh measured K_crit expected within seed tolerance
  of the landed cells (regime-extension: synthetic-phasor -> synthetic-phasor, SHAPE_MATCH).
- composition_edges (Gate C): none (single algebraic decode, no primitive->primitive chain). SHAPE n/a.
- functional_requirements (Gate E): FR = "self-predict bundle K_crit exactly" -> new closed-form
  order-statistic predictor (declared new mechanism; no prior primitive maps to the exact prefactor).
- arms_differ_verified: hash-distinct measured/exact/asymptotic/wrong surfaces + normal/degenerate curves.
- final_metrics_atomicity: tmp_replace (os.replace).
- except SystemExit: raise BEFORE except Exception (no BaseException / bare except; grep-gate clean).
- cell_chunked: false (single-seed sweep, no seed axis).
- start_marker_written / crash_diagnostic_present / heartbeat_present: true.
- progress_logging: print_flush_true (sys.stdout line_buffered + per-unit flush=True prints + heartbeat).
- calibration_check: default_ok_for_this_regime (RECALL_THRESH=0.9 + book cap inherited verbatim from the
  landed synthetic-phasor bundle cells; same synthetic regime).
- storage_strategy: bundled_capacity_characterization -- bundled is the OBJECT of study (the cell measures
  the bundle-superposition capacity boundary itself), the sanctioned exception to SHARDED-DEFAULT; not a
  compositional retrieval that should be sharded.

## Compute architecture
Class (a) batched-GPU for FULL. The heavy op (cleanup sc = rec[K,N] @ conj(book)[V,N].T -> [K,V]) is a
batched matmul over all K queries at once; the outer TR / binary-search loops are light control flow
reusing the landed verbatim machinery. Per-N GPU wall ~seconds (landed largeN 5.9s for 2 N). SMOKE runs
the SAME torch code on CPU (torch 2.12.0+cpu local; device=cpu) at small N -> identical code path
(SMOKE=FULL), only DEV differs. Predictions are pure-numpy closed forms (identical in smoke and full).

## Tier hint
If FULL HARD_PASSes on fresh seeds with firing controls, this is a parameter-free order-statistic
derivation clearing the bar -- a CG candidate parallel to the RNS sibling (exp_rns_subblock_margin_exact
_prefactor_v2). P_deflated = 0.50 (capped novel-synthesis; kept despite the near-perfect retrospective
fit -- fresh dispatch is a separate event; the drill's external lit-scan hit a web outage so citations
are recalled-not-live-verified). VET decides the tier.
