# Prereg: wave14_mp_ks_pretest_tau_robustness_v1

**Date**: 2026-05-24
**Vertex**: MP_KS_TAU_ROBUSTNESS_PASS / KILLED / INCONCLUSIVE
**Capability target**: Cap 12 (AMP-vs-VAMP inference routing infrastructure) — **Gate A** of the 🟢 → ✅ promotion pre-reg gate set.
**Queue**: `remote_cpu_queue` (~30 min CPU)

## Background

Cap 12 was promoted to 🟢 at cap_map v174 by the joint MP-KS pretest pipeline + interp-family SRHT PASSes (verdicts MP_KS_PRETEST_PIPELINE_PASS at 4/5 routing accuracy / 1383x speedup; INTERP_FAMILY_SRHT_PASS at Spearman rho=0.700 / max VAMP rel-err 0.0938). Promotion from 🟢 to ✅ requires TWO pre-registered gates.

This experiment is **Gate A**: tau-robustness across tau in {0.15, 0.20, 0.25}.

## Hypothesis

The tau=0.20 routing threshold from the v174 pretest PASS is **robust**, not a hand-picked fragile point. KS values for the 5 known codebooks (iid_gauss ~0.02, SRHT ~0.59, Hadamard ~0.59, RM(1,m) ~0.34, Kerdock ~0.70) leave a clean gap around tau=0.20 such that moving tau by ±0.05 does not collapse routing accuracy.

## Design

- 5 codebooks: iid_gauss (AMP_OK), SRHT (AMP_OK), Hadamard (VAMP_REQUIRED), RM(1,m) (VAMP_REQUIRED), Kerdock (VAMP_REQUIRED) — same labels as the v174 pretest pipeline.
- N=1024, M/N=1.0, 5 seeds per codebook.
- Compute MP-KS once per seed; AMP + VAMP once per seed to establish empirical truth label (`AMP_OK` if AMP rel-err < 0.10 else `VAMP_REQUIRED`).
- For each tau in {0.15, 0.20, 0.25}: compute `route_from_ks(ks_mean, tau)` per codebook -> per-tau routing-correctness count.

## Routing-accuracy matrix output

```
                     tau=0.15  tau=0.20  tau=0.25
iid_gauss   (~0.02)
srht        (~0.59)
hadamard    (~0.59)
rm_1_m      (~0.34)
kerdock     (~0.70)
                       N/5       N/5       N/5
```

## HARD PASS (Cap 12 Gate A satisfied)

- **>=4/5 codebooks routed correctly at EACH of tau in {0.15, 0.20, 0.25}.**

## HARD FAIL (Cap 12 Gate A fails)

- **<3/5 routed correctly at ANY tau value.** Threshold is fragile across tau; the pretest is not a robust pre-flight.

## MIDDLE BAND

- **3-4/5 at one or two tau values** — marginal; further investigation needed before Gate A can be called PASS.

## Formula self-tests (verified in script `--self-test`, 6/6 cases)

1. `route_from_ks(ks, tau)` — boundary-inclusive at ks==tau, AMP_OK on either side at multiple tau values.
2. `empirical_truth_from_errs(amp_rel, vamp_rel, fail_thresh=0.10)` — boundary-exclusive at amp_rel==0.10.
3. Synthetic 5-codebook PASS case at all three tau values.
4. HARD FAIL synthetic case — <3 correct at one tau.
5. MIDDLE BAND synthetic case — 3 correct at one tau.
6. Missing-codebook INCONCLUSIVE.

## Honest framing

This is narrow infrastructure-class hardening, not substrate-physics novelty. Even a clean PASS only confirms tau-stability of an already-classical MP-KS routine. The product framing is "pre-flight diagnostic is not a tuned threshold" — load-bearing for shipping the diagnostic to customers.
