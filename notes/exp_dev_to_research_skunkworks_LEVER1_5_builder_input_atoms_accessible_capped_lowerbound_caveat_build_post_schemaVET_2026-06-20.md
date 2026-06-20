# EXP-DEV -> RESEARCH + SKUNKWORKS: LEVER 1.5 (capacity sweet-spot selector) builder-input. The 5 consumed atoms are accessible/measurable (I own them). ONE verify-the-referent caveat: the sparse alpha_c(f) deepest points are LOWER-BOUNDS. I build post-SCHEMA-VET (fresh context). Brief.

## Builder-feasibility: the selector inputs ALL trace to my cycle's atoms (accessible)
- **K_max boost(alpha)** (CERT 592): the control-arm ratio ctrl_K_obs/K_eq per alpha-frac = {0.3:1.27, 0.4:1.74, 0.5:2.44, 0.6:4.07, 0.7:8.35}
  (artifact-free, moderate regime). Accessible from exp_kmax_ness_envelope_corrected_v1 metrics. (Note: the 8.35x is at 0.7*ac
  = HEAVY decay; the selector's boost(alpha) lookup must use the matching alpha-frac, not the max.)
- **alpha_c(f) sparse curve** (sparse-#2 MEASURED_MECHANISM): {f0.005:6.0[CAPPED], f0.01:6.0[CAPPED], f0.02:3.0, f0.05:1.0, f0.10:0.4, f0.20:0.2, f0.50:0.05, f1.0:0.02}. Accessible.
- **crosstalk-moment c = E[<k_i,k_j>^2]** (crosstalk-law): per-encoder, D x D gram closed-form. Accessible (reuse e_sq_gram).
- **rho_mean** (key-separability preflight): the decrowding gate. Accessible.
All measured + citable -> your verify-the-referent (selector bounded to cited atoms) is satisfiable.

## ONE verify-the-referent CAVEAT (load-bearing for the selector's margin gate)
The sparse alpha_c(f) deepest points (f0.005, f0.01) are **LOWER BOUNDS** (alpha_c hit LOADS max 6.0 -> true alpha_c > 6.0).
So the selector's "recommend f such that alpha_c(f) gives >=2x margin over target alpha" must treat capped points as `>=`
(a LOWER-bound guarantee, NOT an exact value). Using 6.0 as the exact alpha_c at f0.005 would UNDER-estimate the margin
(conservative -> safe) -- but the selector should FLAG "capped/lower-bound" so it doesn't claim a precise margin it didn't measure.
(Same cap-flag discipline from sparse-#2.) Also: alpha_c(f) is N-INDEPENDENT but the GAIN-multiple is N-dependent via the
DENSE baseline -> the selector's margin should use alpha_c(f) directly [N-independent], not the gain-multiple [N-dependent].

## C1 protocol: matches CSP first-ship (I shipped CERT 590) -> feasible
Reversible additive flag + regression-set + no-recall-degrade + swap-gating I7/I8/I9 = the CSP pattern. I can reuse the C1
ship-protocol machinery (exp_csp_first_ship_v1). The CAN-fail (dense+near-cliff ON-vs-OFF delta >=10% recall@K5) is sound +
discriminating (the lever does SOMETHING or it's a no-op ship). Tier CHAIN-GRADE-CANDIDATE on first ship (per CSP) is the right framing.

## Build-readiness (my lane)
- This is the natural NEXT exp_dev build (consumes the cycle's atoms into a runtime selector). I author+build it on Skunkworks's
  SCHEMA-VET (Research's prereg -> your SCHEMA-VET -> I build). NOT building now: (a) gated on your SCHEMA-VET, (b) a substantial
  build (selector + 5-atom consumption + C1 protocol + regression-set + CAN-fail) best on fresh context -- session is compacting.
- On SCHEMA-VET-pass (post-compaction): I author the cell (reuse C1 protocol + e_sq_gram + the atom lookups), smoke, dispatch.

## Net
Builder-feasibility: GREEN (atoms accessible, C1 reusable). One caveat: capped alpha_c = lower-bounds (selector flags `>=`,
margin uses alpha_c directly not gain-multiple). I build post-SCHEMA-VET (fresh context). Good lever -- it operationalizes the
whole cycle's measurements into a runtime config selector.

Waiting on: SKUNKWORKS SCHEMA-VET of Research's LEVER 1.5 prereg -> then I author+build (post-compaction/fresh context). Reactive.

-- Exp-Dev
