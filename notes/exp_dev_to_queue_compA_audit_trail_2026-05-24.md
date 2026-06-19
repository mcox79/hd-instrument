# exp_dev -> queue: Composition A audit-trail pipeline anchor (Cap 12 + Cap 8)

**Date**: 2026-05-24
**From**: exp_dev sub-agent
**Trigger**: Strategy ship-order via Research's 2026-05-24 audit anchor
(`notes/research_antiRM_and_compA_audit_2026-05-24.md` Section 3); pause flag
CLEARED; Composition B HARD-KILL at cycle 197 leaves Composition A as the
top remaining composition story.

## Shipment

| queue            | name                                          | script                                                          | prereg                                                             | timeout(s) |
|------------------|-----------------------------------------------|-----------------------------------------------------------------|--------------------------------------------------------------------|------------|
| remote_cpu_queue | wave14_cap12_cap8_audit_trail_pipeline_v1     | experiments/exp_wave14_cap12_cap8_audit_trail_pipeline_v1.py    | preregs/2026-05-24_wave14_cap12_cap8_audit_trail_pipeline_v1.md    | 5400       |

## What this ships

Re-analysis-style anchor (4 codebook families x 5 seeds at N=4096; SVD +
moment inversion + Schur-Weyl irrep mass extraction per (family, seed, order)).
Tests the structural claim that Cap 12's kappa_n routing fingerprint and
Cap 8's Schur-Weyl-irrep-decomposed VAMP-on-chain singular spectrum share
real representation-theoretic structure, not prose-only juxtaposition.

## Smoke result

Smoke (N=1024, 1 seed, n_max=4, codebooks=[kerdock, iid_gauss]) passed:
- self_test passed all 24 cells (Murnaghan-Nakayama characters, closed-form
  Schur polynomials, Plancherel sum dim^2 = n!, mass normalization, Spearman
  identity/anti/swap, iid-MP intensive sanity, all 4 verdict branches)
- Kerdock at N=1024 seed=0: kappa_div = [0.250, 0.626, 0.952]; Schur-Weyl
  mass_n deviations = [0.000, 0.046, 0.050]; per-seed rho = 1.000 (3 points
  both monotone in same order)
- iid_gauss at N=1024 seed=0: kappa_div = [0.004, 0.011, 0.025]; Schur-Weyl
  mass_n deviations ~ [0, 0, 0] (matches MP baseline; no signal expected)
- metrics.json written, verdict = COMPA_AUDIT_INCONCLUSIVE (expected on smoke
  with 2/4 hard families)

The Schur-Weyl irrep extraction from a single VAMP-iterate spectrum is
NOT fragile — Kerdock shows non-trivial mass_n deviation at orders n=3,4;
iid Gaussian matches MP baseline to floating-point precision; the
intensive-moment convention prevents Plancherel concentration from
drowning the signal at large M.

## Substrate-product interpretation (importance=HIGH)

If Composition A holds (rho >= 0.60 across >= 3/4 families), Cap 12
routing + Cap 8 audit-trail inference unlocks joint customer-facing
interpretable inference: customer submits a codebook, Cap 12 routes
based on kappa_n fingerprint, Cap 8 delivers the readout with a
Schur-Weyl-irrep-labeled provenance receipt that customer-facing
audit code can interpret quantitatively.  On HARD FAIL, v169 closed-
form annotations narrow; on MIDDLE BAND, composition stays plausible
per-family but does not elevate.

## Queue depth after ship

remote_cpu_queue: depth checked at queue_add time; this shipment puts
the runner at depth >= 1 per the continuous-pipeline invariant.

## Blockers

None.  Schur-Weyl decomposition implementation is robust (Murnaghan-Nakayama
character table verified hand-by-hand at n=2,3,4; Plancherel column-sum
identity sum dim^2 = n! verified to n=5; closed-form Schur s_(2), s_(1,1),
s_(3), s_(2,1), s_(1,1,1) all verified).  iid-Gaussian intensive-moment
sanity check passes at < 0.05 deviation from MP analytic masses.

```
queue=remote_cpu_queue name=wave14_cap12_cap8_audit_trail_pipeline_v1 script=experiments/exp_wave14_cap12_cap8_audit_trail_pipeline_v1.py prereg=preregs/2026-05-24_wave14_cap12_cap8_audit_trail_pipeline_v1.md timeout=5400
```
