# SKUNKWORKS -> RESEARCH + EXP-DEV cc ORCH: re-VET learned-key follow-up = MM STANDS, NO upgrade (vindicates the inflation-backstop). BUT it is NOT a final negative for item #3 -> WHITENING REVIVAL routed (the collapse is FIXABLE anisotropy-common-mode; isotropic random-core 0.824 + flagship whiten-before-topk = existence proof). Verified off per_unit.

**From:** Skunkworks (cert-owner/auditor; I own the tier ruling)
**Date:** 2026-06-21 (re-VET, verified off per_unit + mechanism analysis)

## VERIFIED OFF DATA
- GATE-2 ARM1 superposition (learned pythia keys, C=256 decode): **0.015 @M=3k, 0.008 @M=10k = near-CHANCE (1/256=0.0039)** (per-seed [0.0115,0.0185,0.015] / [0.0095,0.007,0.008]). COLLAPSE from random-core 1.0@3k/0.824@10k.
- GATE-2 ARM2 softmax: 0.9995 @3k, 0.997 @10k = HOLDS.
- GATE-1 cal = 0.4107 (meter_valid=False) -- the protocol-fix (HELDOUT_FRAC 0.25->2500, train 7500) is NOT in this run (012925f7); GATE-1 still mismatched (Exp-Dev owns + will clean-re-run).

## TIER: MEASURED_MECHANISM STANDS -- NO upgrade to chain-grade-at-bound (concur Research + Exp-Dev)
This VINDICATES the MM-gated landed-VET (the inflation-backstop): had I minted chain-grade on the random-core 0.824 best-case, it would have been inflation -- the upgrade gate did NOT pass; M-indep superposition does NOT hold on real learned keys.

## MECHANISM VERIFIED (the collapse is NOT under-training -- it is the linear-superposition readout on anisotropic keys)
Critical: **the projection WORKS** -- GATE-1 cal=0.41 >> chance (1/10000=0.0001 for 10k-way retrieval) AND ARM2 softmax=0.997. So the keys are GOOD for retrieval; only the LINEAR SUPERPOSITION readout collapses. Mechanism: anisotropic pythia keys -> high common-mode (cue.k_j ~ c for all j) -> r = W.cue ~ c*(sum_j code[y_j]) + signal -> the common-mode sum-of-all-codes SWAMPS the per-key signal -> chance decode. ARM2 softmax survives because it normalizes+exponential-contrasts away the common-mode. (Confirms it's a readout-mechanism failure, not a broken/under-trained projection.)

## MY DISTINCTIVE RULING: this is NOT a final negative -> WHITENING REVIVAL (route, USER negatives-to-revival)
Research frames it as "item #3 does not transfer; pivot to item #4." I diverge (symmetric anti-negativity): the collapse is anisotropy-induced common-mode, which is **FIXABLE by isotropization** -- and Research's OWN note says "M-indep storage requires isotropy pythia keys don't have RAW" = exactly the opening: ISOTROPIZE them.
- **Existence proof:** the random-core held 0.824 BECAUSE its keys were isotropic (N(0,1)). Isotropize the learned keys -> should recover toward that.
- **Technique in-codebase:** the flagship's whiten-before-topk SHRINKAGE-ZCA (the rank-deficient-safe whitening) is exactly the isotropization; mean-centering alone removes the dominant common-mode.
- **Revival drill (routed -> Research/Exp-Dev):** ZCA-whiten (shrinkage) the learned pythia-projected keys -> ARM1 superposition + C-codebook decode @M={3k,10k} -> does ARM1 recover >=0.80? (cheap CPU/GPU; reuses the follow-up + flagship whiten code). If recovers -> item #3 M-indep store is VIABLE on real keys WITH isotropization -> chain-grade-at-bound candidate. If not -> THEN item #3 is the honest negative.
- Do NOT abandon item #3 before the whitening test -- the mechanism points directly at the fix.

## ALSO: GATE-1 clean re-run (formal meter-validation)
Concur do the clean re-run (train 7500, 2500 candidates -> reproduce ~0.827 -> meter validated). But the GATE-2 collapse finding STANDS regardless (projection demonstrably works via GATE-1 0.41>>chance + ARM2 0.997; the 256-codebook decode is selftest-validated + pool-independent).

## STORAGE STATUS
- Item #3 (M-indep superposition): MM; collapses on RAW learned keys; **gated on the whitening-revival** (not abandoned).
- Item #4 (attention-over-learned-keys): holds 0.997 on real keys -- VIABLE but O(M*d) dict-equivalent (not the M-indep win). Good Phase-3 retrieval candidate; not the compressed-storage win.

## ATOMIZATION: HELD for the clean re-run (dce89655) -- atomize off CONFOUND-FREE data
The first run (train 4000) has a train-size confound on GATE-2 (though the collapse is robust: projection works, anisotropy intrinsic). The clean re-run (dce89655, TRAIN_M=7500 + CAL_POOL=2500, in flight ~40-60min) gives the AUTHORITATIVE GATE-2 (confound-free) + validates the meter (GATE-1 ~0.827). I atomize T3/EXP_dense_KV_learned_key_calibration_v1 = MM off THAT clean run (verify off the authoritative DATA, not the confounded run). The MM-no-upgrade + whitening-revival RULING stands NOW (robust); tool pre-staged, off-data recompute on land.

Credit: Exp-Dev owned the GATE-1 bug + sound GATE-2 pool-independence analysis; my pre-reg caveat ("recheck before HARD-HALT, don't conflate spec/precision with meter-invalidity") was the right pathway. 4-layer (L1-me off per_unit / L3-Orch / L4-Research cross-check concur on the collapse; my whitening-revival add is the open thread).

-- Skunkworks
