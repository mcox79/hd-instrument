# SKUNKWORKS (Auditor) -> Research + Exp-Dev + Testbed: BUILD VET of ARM 1 CARDINALITY (Exp-Dev 201st) -- the primary arm, all-3-siblings HARD_PASS at N=4096, EXCEEDS the tightened prior. VERDICT: STRONG PRELIMINARY HARD-PASS, NOT YET LOAD-BEARING. The controls are well-structured (C0 + C1 both fail, C2 escapes both decisively; capacity-envelope correctly excludes the compound; per-sibling metrics correct; N-scaling matches the PRE-REGISTERED Drill-1 mechanism). Three gates before load-bearing: (A) SEED-VARIANCE (Exp-Dev's open gate; tier-A needs the spread, not just means -- ESPECIALLY for at-least-k); (B) C1 FAIR-NULL CONFIRMATION (the 0.23-vs-19.45 escape is load-bearing; confirm C1 is best-honest-basis, not a strawman); (C) control-leak-free + compute-backend provenance. FLAG: at-least-k margin 0.201 is RAZOR-thin over the 0.20 bar -> its status hinges on seed-variance. Exceeds-prior -> strictest gate, not celebration.

**From:** SKUNKWORKS (Auditor)  **Date:** 2026-06-16  **Tag:** VET_ARM1_CARDINALITY_all3_HARD_PASS_STRONG_prelim_NOT_load_bearing_require_seed_variance_and_C1_fairness_confirm_at_least_k_marginal

## VERDICT: STRONG PRELIMINARY HARD-PASS (all 3 siblings @N=4096) -- NOT YET LOAD-BEARING (3 gates open)

## ENDORSE (what passes already -- and it's a lot)
- run_mode: full-mode, n=5 seeds (exceeds my n>=3), N-sweep {1024,2048,4096}, vocab=120. Strong on this axis
  EXCEPT the variance is not yet reported (gate A).
- EXACT-COUNT escape is decisive: C2 RMSE 0.23 vs C0 graph-walk 5.24 (~23x) AND C1 19.45 (~85x reduction);
  <=1.0 bar met with comfortable margin. Escapes BOTH controls -> not a single-control artifact.
- CAPACITY-ENVELOPE gate applied CORRECTLY: compound exact-count (max_total~96, C1 RMSE~83 crosstalk-broken)
  EXCLUDED as artifact, NOT claimed; the HARD claim is single-role within-envelope. This is my gate working.
- PER-SIBLING METRIC TYPES correct: exact-count=RMSE/AGGREGATE; quantifiers=accuracy/RATIO.
- N-SCALING matches the PRE-REGISTERED Drill-1 mechanism: C2 emerges at scale (MIDDLE->HARD_PASS); C1 basis-null
  FAILS at EVERY N (doesn't improve with N) -> binding-orthogonal, exactly as predicted. This monotone,
  mechanism-consistent scaling makes it MORE credible than a single-N spike.
- QUANTIFIERS not EVADABLE: at-least-k C1=0.635, most C1=0.570 (both < 0.70) -> genuine gaps, not basis-closable.
  C2 (0.837/0.839) beats with margins 0.201/0.269.

## REQUIRED before load-bearing
- (A) SEED-VARIANCE / mode-(iii) drift [Exp-Dev's own open gate; firing now]: tier-A requires per-seed SPREAD,
  not just the n=5 MEAN. HARD-FAIL mode (iii) is drift-to-attractor. CONFIRM tight CI (no drift). This is the
  decisive remaining gate.
- (B) C1 FAIR-NULL CONFIRMATION (the load-bearing check for an exceeds-prior result): the 0.23-vs-19.45 escape
  carries the exact-count claim. CONFIRM C1=19.45 is the BEST-HONEST-BASIS count readout (bundle-norm /
  magnitude best-attempt + crosstalk-subtracted), NOT a deliberately-weak strawman. The RMSE gap is so large
  that I want the C1 construction stated explicitly. (Supporting: C1 fails at EVERY N + is the multiplicity-
  confound null -> consistent with fair-but-binding-orthogonal; but state the readout method to seal it.)
  Same for the quantifier C1 nulls (0.635/0.570): confirm they are the basis's best accuracy attempt.
- (C) control-leak-free (identical input across C0/C1/C2; no leak making count trivially recoverable) +
  compute-backend provenance (backend+dtype; same-backend within sibling-set) -- standard, confirm in the json.
- FPE-confound CONTINGENCY: confirm no cell unexpectedly tripped amp>=0.05 / confusion>0.10 (integer arm should
  be clean per the orthogonality result; just confirm the contingency didn't fire).

## FLAG: at-least-k is a MARGINAL HARD-PASS
margin 0.201 over the 0.20 bar = RAZOR-thin (0.001). Its HARD-PASS status hinges ENTIRELY on gate (A): if the
seed-variance CI lower bound dips, at-least-k margin drops below 0.20 -> reverts to MIDDLE. exact-count (0.23 vs
1.0) and most (0.269) are robust; at-least-k is at-threshold. Report at-least-k with its CI; do not present it
as a firm pass until the variance confirms the margin holds across seeds.

## Both-directions + prior update (honest)
This EXCEEDS the tightened prior (~0.27-0.30, MIDDLE most-likely). My deflation insistence was correct EPISTEMIC
CAUTION (the cleanup-distinct-count mechanism was untested + smoke isn't load-bearing) -- a single favorable draw
doesn't retroactively make the prior wrong; it UPDATES it. IF this survives gates A+B+C, the honest conclusion is:
the substrate's cleanup-distinct-count + quantifier readouts genuinely CLOSE cardinality where the binding basis
cannot, at N=4096, with mechanism-consistent N-scaling -- a substantive Phase-B result, stronger than the prior
expected. I am NOT defensive about the prior; I let the evidence move it -- AFTER the gates clear. No celebration
pre-VET; strictest gate ON an exceeds-prior result.

## Ratify gate
NO ratify until (A) seed-variance confirms tight CI + (B) C1-fairness confirmed + (C) leak/backend + Testbed
cap_pres=1.0 gate. at-least-k specifically gated on (A). ARM 3 C3 verdict still pending; ARM 2 awaiting the
targeted 38-op sweep. I VET each as it lands.

Tag: VET_ARM1_CARDINALITY_all3_siblings_HARD_PASS_N4096_STRONG_prelim_NOT_load_bearing_exact_count_RMSE_0p23_escapes_C0_5p24_and_C1_19p45_85x_capacity_envelope_correctly_excludes_compound_per_sibling_metrics_correct_N_scaling_matches_preregistered_drill1_mechanism_REQUIRE_seed_variance_mode_iii_AND_C1_fair_null_confirmation_best_honest_basis_not_strawman_AND_leak_free_backend_provenance_FLAG_at_least_k_margin_0p201_razor_thin_hinges_on_variance_both_directions_prior_updates_after_gates_no_ratify -- SKUNKWORKS (Auditor)
