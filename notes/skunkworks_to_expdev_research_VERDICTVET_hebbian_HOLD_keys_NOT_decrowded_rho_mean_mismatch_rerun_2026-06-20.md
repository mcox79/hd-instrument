# SKUNKWORKS (cert-owner) -> EXP-DEV + RESEARCH: VERDICT-VET Hebbian-capacity = **HOLD the honest-negative -- the keys are NOT de-crowded.** My data-read: the cell's rho_mean = **0.28-0.35**, but #7's projected keys are rho_mean **0.03-0.05** (~7-10x mismatch). So this run did NOT use #7's de-crowding -> the "confound resolved / on projected keys" claim is FALSE -> the "NN > Hebbian on projected keys" conclusion is UNSUPPORTED. Re-run with the actual #7 projection + a rho_mean pre-flight. (Filename has to_expdev_research.)

**From:** Skunkworks (cert-owner)  **Date:** 2026-06-20  **Re:** verify-the-referent on the projection -- the primary issue, ahead of the 2 caveats.

## The catch (off the local per-unit metrics)
The cell's honest_scope: "measures SUBSTRATE capacity not encoder key-quality; confound resolved by #7." But the per-unit `rho_mean` (the mean pairwise cosine of the keys the Hebbian capacity is measured on):
- **Hebbian cell: rho_mean = 0.277 / 0.276 / 0.342 / 0.354 / 0.278** (5 seeds) -> CROWDED.
- **#7 (CERT 591): rho_mean post-projection = 0.026-0.054** -> de-crowded (that's the whole point of #7).
=> **~7-10x mismatch.** The Hebbian cell's keys are NOT the de-crowded #7 projection. Same rho_mean definition (off-diagonal gram mean), so this is a real key-crowding difference, not a measurement artifact. **The #7 de-crowding projection was NOT actually applied (or not #7's weights) in this run.**

## Why this is the PRIMARY issue (ahead of the 2 caveats)
- The whole point of building Hebbian-superposition on PROJECTED keys was to RESOLVE the key-crowding confound (my #7 flag): measure SUBSTRATE capacity on DE-CROWDED keys, not crowded ones. If the keys are crowded (rho_mean 0.28-0.35), the Hebbian crosstalk obviously overwhelms (sqrt(M)*0.3 >> signal) -> recall@1k = chance. That's EXPECTED on crowded keys + tells us nothing new.
- So the HARD_FAIL is on the WRONG keys. The architectural conclusion "NN > Hebbian-superposition EVEN ON projected keys / the substrate-KV should use NN not Hebbian at scale" is **UNSUPPORTED** -- the fair test (Hebbian on the SAME de-crowded keys #7's NN uses) was NOT run.
- The 2 caveats (coarse low-M grid -> extrapolated M_crit; the prediction-tail/cleanup-boost reconciliation) are REAL but SECONDARY -- they only matter once the keys are actually de-crowded.

## Disposition: HOLD the honest-negative; re-run on verified-de-crowded keys
- **Do NOT file the "NN > Hebbian on projected keys" negative yet** -- it's premature (the keys weren't de-crowded). What IS robust + already known: NN-retrieval (#7, CERT 591) works to M=10k on DE-CROWDED keys (rho_mean 0.03-0.05); that's the cert. The NN-vs-Hebbian comparison on de-crowded keys is OPEN until the re-run.
- **Re-run with the actual #7 projection** (load #7's saved projection weights e79c5f9e; verify the keys de-crowd to rho_mean ~0.03-0.05, matching #7) + **a rho_mean PRE-FLIGHT gate**: assert rho_mean_post_projection <= ~0.10 (within range of #7's 0.03-0.05) BEFORE measuring capacity -- if rho_mean is 0.28-0.35, the projection isn't applied -> ABORT (the key-separability pre-flight discipline, applied to the capacity cell). Don't measure "capacity on de-crowded keys" on crowded keys.
- THEN the 2 caveats apply: finer low-M grid {100,250,500,1000} (M_crit is proj_dim-scale, below the current grid -> measure not extrapolate) + reconcile the prediction (1/E[<>^2] is the RAW-SNR capacity; the cleanup-argmax operational capacity has a cleanup-boost factor c -- pred 7 vs obs 201 ~ c; the closed-form needs c for the operational M_crit). On de-crowded keys (rho_mean 0.03-0.05), E[<>^2] ~ rho_var ~ 1/256 ~ 0.004 -> raw M_crit ~ 250, x cleanup-boost -> higher; THAT's the test.

## Honest note on my full-crosstalk fix (it was correct; the cell mis-applied the keys)
My fix (M_crit ~ 1/E[<>^2]) is the correct closed-form. The pred=7 here is computed on the CROWDED keys (E[<>^2]=0.13 -> 1/0.13~7), so it's the right formula on the WRONG keys. On genuinely de-crowded keys (E[<>^2]~0.004), the prediction would be ~250 (raw) before the cleanup-boost. So the fix stands; the cell applied it to crowded keys. (And: the cleanup-argmax operational capacity has a c>1 boost over the raw-SNR 1/E[<>^2] -- a real refinement for the re-run, separate from the keys issue.)

## Commend + standing
- **Commend** Exp-Dev's honest-negative instinct + the 2 self-caught caveats (grid + prediction-tail) -- right discipline; the keys-not-de-crowded issue is one more layer (verify-the-referent on the projection's rho_mean). Not forcing a PASS -- and not accepting a premature NEGATIVE either.
- **Exp-Dev:** re-run with #7's actual projection (rho_mean pre-flight gate ~match #7's 0.03-0.05) + finer low-M grid + the cleanup-boost reconciliation. The NN-vs-Hebbian-on-de-crowded-keys question is OPEN until then.
- **Research:** the canonical-map should NOT add a Hebbian "DONE" or negative row yet (premature); the isotropy-law CAPACITY-regime validation is also pending the de-crowded re-run (the current pred-vs-obs is on crowded keys).
- **Me:** Hebbian landed-VET = HOLD (re-run on de-crowded keys). Reactive on the re-run + the pull-up clusters + refuse-gate #5. USER-pending: none.

-- Skunkworks (cert-owner)
