# PRE-REG: kmax_ness_envelope_gpu_v1 (Research Component-2) -- substrate NESS chain-recall depth vs INDEPENDENT Hopfield equilibrium K_eq, in the MODERATE discriminating regime. DATA DECIDES tier.

**Anchor:** `kmax_ness_envelope_gpu_v1`  **cell:** experiments/exp_kmax_ness_envelope_gpu_v1.py (committed f6878848)  **GPU.**
**Tier:** DATA-DECIDES (Skunkworks pinned): chain-grade candidate IF >=2x + genuine across >=4/5; else MEASURED_MECHANISM (equilibrium-match). CERT 591 unless data supports chain-grade (Skunkworks rules 592).

## Hypothesis (pre-registered, symmetric -- a HYPOTHESIS to TEST, not a given)
Substrate NESS write-decay chain-recall depth K_obs vs the INDEPENDENT classical-Hopfield equilibrium ceiling
K_eq = 3.3*(1-alpha/alpha_c)^2/alpha (alpha_c=0.138, parameter-free theory constant -- NON-CIRCULAR baseline). Question:
does single-substrate NESS depth EXCEED the equilibrium ceiling by >=2x in the discriminating regime, or MATCH it (~1.0)?

## Regime (Skunkworks COMPLETE divide-by-zero guard -- the load-bearing referent)
K_eq has TWO bad limits: alpha->0 -> K_eq->inf (/alpha) -> unfair fail (smoke-caught); alpha->alpha_c -> K_eq->0
((1-a/ac)^2) -> trivial pass. GATE ONLY in the MODERATE regime where K_eq is BOUNDED (the ratio CAN pass OR fail):
- alpha in [0.30, 0.70]*alpha_c -> K_eq ~ {39, 21, 12, 6, 3} -> safe_gate = (2.5 <= K_eq <= 45).
- K-grid extended to {3..120} so K_obs is MEASURED (cliff found), NOT grid-capped (the smoke caps K_obs at the grid max).
- Report K_eq + ratio per-point so the bounded-regime is VET-able off data.

## Metrics + DATA-DECIDES verdict
- K_obs (cleanup-ON cand2 depth at recall>=0.9), ctrl_K_obs (cleanup-OFF), cleanup_boost = K_obs/ctrl_K_obs, K_eq, ratio_to_eq.
- **GENUINE (load-bearing, CORRECTED per Skunkworks landed-VET -- doc-code parity):** TWO artifact-free checks.
  (1) **genuine_control = (control K_obs > K_eq):** the cleanup-OFF (control) arm has NO codebook snap -> CANNOT be a cleanup
  artifact; control K_obs exceeding K_eq = genuine multi-hop beyond equilibrium. [Replaces the OLD mis-spec'd "cleanup-OFF
  recall >= 0.30 at cand2's deep_K", which read False on ANY cleanup boost because cand2's deep_K is by-design past control's cliff.]
  (2) **extension_genuine = (ext_hopfrac >= 0.85):** ext_hopfrac = fraction of cand2 hops that snap to the CORRECT next chain-node
  a_{h+1} (genuine denoise-and-traverse) vs jump to a_K (cleanup-RECOVERY artifact). Per-depth + REPORT curve.
- **Bands (data decides):** UNKNOWN if <4 safe points. HARD_FAIL if control does NOT exceed K_eq on >=4/5 (substrate does not
  genuinely exceed equilibrium). HARD_PASS (chain-grade -> Skunkworks rules 592) if cand2 ratio_to_eq>=2x on >=4/5 AND
  all_extension_genuine AND control exceeds K_eq on >=4/5. Else STRONG MEASURED_MECHANISM (CERT 591) -- control genuinely exceeds
  equilibrium (the verified floor) but cleanup-extension not verified-genuine-enough / control<2x on >=4/5.
- **UP-guard:** any ratio_to_eq driven by K_eq near the bounded edges -> verify (report K_eq per-point).

## SMOKE (N=1024, [0.4,0.6]ac) -- mechanically validated
af=0.40: K_obs=40(grid-capped) ratio_to_eq=1.86 cleanup_boost=1.53x; af=0.60: K_obs=27 ratio_to_eq=4.27 cleanup_boost=1.95x
genuine=True. (Promising: moderate regime CAN exceed 2x. Full N=8192 + K to 120 decides; grid-cap at af=0.40 resolved by deeper grid.)

## What STAYS / what the cell does NOT claim
- alpha_c=0.138 + formula (a) provenance (independent Hopfield, non-circular). Genuine-multi-hop. Divide-by-zero (now COMPLETE: both limits). 
- The NESS predictive ALGEBRA (fitted eta/f_c/tau) stays T3-CONJECTURE (NOT this cell). Hierarchical D-fold depth = separate mechanism (not here).
- Does NOT pre-decide the tier: the smoke's wrong-regime result is NOT evidence; the moderate regime TESTS it (Research self-catch #11: no preemptive-downgrade-without-data).

## SCHEMA-VET (Skunkworks pre-dispatch focus)
metrics REQUIRED_FIELDS: anchor_name, verdict, verdict_msg, run_mode, detail.per_alpha_frac, detail.ratios_to_eq_safe,
detail.cleanup_boost_safe, detail.mean_ratio_to_eq, detail.all_genuine_multihop, detail.n_safe_points, per_unit (with cand_curve+ctrl_curve), elapsed_s.
checkpoint per (alpha_frac,seed) [dot-sanitized key]; restartable. import torch first; CUDA-required full.

## Version-marker
FULL: N=8192, alpha_fracs [0.30,0.40,0.50,0.60,0.70], K_grid to 120, seeds 1-3, n_chains=24. EXPECTED: detail.n_safe_points>=4,
per-point K_eq in [~3,40] (bounded-regime confirmed). Verify-the-referent at dispatch: on-origin(f6878848) + this marker.
