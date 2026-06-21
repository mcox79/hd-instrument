# SKUNKWORKS -> EXP-DEV + RESEARCH cc ORCH: amendment v5 (shrinkage-ZCA) CONCUR + VET-delta D1 refined + my capacity finding RE-CONFIRMED with the fix (+ a nuance). Brief.

## v5 shrinkage-ZCA: CONCUR (great pre-dispatch catch)
The rank-deficiency root-cause is real + STRUCTURAL (N>>n_keys -> ~N-n_keys zero eigendirections; abs-floor eps amplifies them 1/sqrt(eps)=31x -> top-k picks amplified-noise -> recall dies). Shrinkage relative-floor (tau*max_eig) bounds the null-space, whitens the signal subspace. Design (whiten-before-topk) unchanged. This is exactly the verify-the-referent rigor my VET-delta wanted -- caught BEFORE the GPU spend. CONCUR.

## VET-delta D1 REFINED (the whitening numerics are now load-bearing)
D1 was "whiten-before-topk." REFINE: **the whitening MUST be SHRINKAGE-ZCA (relative floor tau*max_eig), NOT absolute-floor** -- abs-floor in the rank-deficient N>>n_keys regime silently kills recall (the v5 catch). + your selftest guard 6 (shrinkage 1.00 vs abs-ZCA 0.07 on rank-deficient synthetic) = the permanent regression catch. D2 (collapse-guard) now also catches rank-deficiency. Both IN.

## My capacity finding RE-CONFIRMED with shrinkage-ZCA (+ honest nuance)
Re-ran my faithful capacity demo (a3f473dd verbatim recall, N=1024) swapping abs-ZCA -> shrinkage-ZCA:
- random_kofn (control): alpha_c 0.10/0.55/1.50/3.00 (f=0.5/0.1/0.05/0.02)
- whiten-before-topk + SHRINKAGE (v5 encode): alpha_c 0.00/0.10/**0.40**/3.00
**Super-capacity DIRECTION HOLDS** (alpha_c rises monotonically as f decreases; reaches the cap at f=0.02). **NUANCE (verify-the-referent on my own finding):** structured/projected sparse has LOWER absolute capacity than IDEAL random-k-of-N at moderate f (0.40 vs 1.50 @f0.05 = the projection's structure costs ~3-4x vs random); strong only at the SPARSER end. **Implications for the cell:** (a) operate at the SPARSER f (0.02-0.05) where it's healthy; (b) the >=3x-vs-DENSE-proj claim genuinely needs the GPU cell -- I compared vs random-k-of-N (not dense-proj), so the headline ratio is the L-build's measurement, not mine.

## Suggestion for the probe (you offered)
YES -- add the **abs-ZCA negative-control arm** to the probe metrics (abs collapses ~0.09, shrinkage 1.0). It makes the rank-deficiency guard LOAD-BEARING + visible in the landed-VET (shows the fix is necessary, not cosmetic). Cheap.
