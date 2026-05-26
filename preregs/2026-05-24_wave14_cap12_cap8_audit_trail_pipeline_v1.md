# Pre-registration: wave14_cap12_cap8_audit_trail_pipeline_v1

**Date**: 2026-05-24
**Queue**: remote_cpu_queue (pure-CPU; ~30-60 min wallclock; 4-family SVD + Schur-Weyl irrep masses at N=4096, 5 seeds, n_max=5)
**Axis probed**: Composition A (Cap 12 + Cap 8 audit-trail) — structural integrity audit per Research's 2026-05-24 anchor proposal
**Trigger**: `notes/research_antiRM_and_compA_audit_2026-05-24.md` Section 3 anchor; Composition B HARD-KILL at strategy cycle 197 leaves Composition A as top remaining composition; cycle-194/197 lock candidate "shared-mechanism composition stories require a STRUCTURAL audit before being queued as probes" is operationalized here
**Script**: `experiments/exp_wave14_cap12_cap8_audit_trail_pipeline_v1.py`
**Expected elapsed**: ~30-60 min CPU full sweep (SVD on 4 codebooks x 5 seeds at N=4096; Schur-Weyl mass extraction is O(p(n)^2 * n) per (codebook, seed, order) -- millisecond-scale; SVD dominates)

---

## Scientific question

Does the kappa_n algebra (Cap 12 routing fingerprint) and the Schur-Weyl
irrep mass decomposition (Cap 8 VAMP-on-chain provenance vocabulary) share
REAL representation-theoretic structure across codebook families, or is
the "audit-trail" framing prose-only?

This is the structurally cleaner companion to the killed Composition B
(Cap 12 + Cap 6 conformal subsumption).  Composition B failed because it
tried to feed kappa_n directly into a Venn-Abers non-conformity score —
two ALGEBRAIC OBJECTS were treated as one.  Composition A here treats
kappa_n divergence as **provenance vocabulary**: Cap 12 says "I routed
here because kappa_n diverged" and Cap 8 says "I consumed a singular
spectrum whose Schur-Weyl irrep decomposition corresponds to the kappa_n
fingerprint Cap 12 reported".  The hypothesis is that those two
algebraic-label sets correlate quantitatively because they index THE
SAME underlying object (the Clifford-Kerdock-twirled S-transform of the
substrate spectrum).

---

## Design

- **N**: 4096 (log2(N)=12, even; required by Kerdock 4-coset construction)
- **M/N**: 1.0 (square case; matches v174/v175 Cap 12 anchor cells)
- **n_seeds**: 5 (matches Research's anchor proposal)
- **n_max_order**: 5 (Schur-Weyl orders n=2,3,4,5; 4 components per family)
- **Codebooks (hard band, 4 families)**: kerdock, srht, hadamard, rm_1_m
- **Codebook (informational only, 5th)**: gold_m10 (N=1023; doesn't count
  toward hard-pass/hard-fail tally per Research's note that RM(1,m) is the
  most direct Cap 12 overlap)

### Operational definitions

For each codebook C and order n in {2,3,4,5}:

```
x_n(C) = | kappa_n_emp(C) - kappa_n_MP |
y_n(C) = | schur_weyl_mass_(n)_emp(C) - schur_weyl_mass_(n)_MP |
```

where:
- kappa_n_emp(C) is the n-th free cumulant of the spectrum (1/N) A^T A,
  computed by Mobius inversion on the non-crossing partition lattice
  (Nica-Speicher 2006);
- kappa_n_MP = c (constant for Marchenko-Pastur at all orders);
- schur_weyl_mass_(n)(C) = s_(n)(m) / sum_{lambda |= n} s_lambda(m), where
  s_lambda is the Schur polynomial in NORMALIZED moments
  m_k = (1/M) sum_i lambda_i^k (intensive, M-invariant), computed via the
  Frobenius character formula
  s_lambda(p) = sum_{mu |= n} chi^lambda(mu) / z_mu * p_mu;
- chi^lambda(mu) is the symmetric-group character computed by the
  Murnaghan-Nakayama rule;
- schur_weyl_mass_(n)_MP uses the MP closed-form moments
  m_k = (1/k) sum_j C(k,j) C(k,j-1) c^j.

Spearman rho(x, y) is computed across n=2..5 (4 points) per codebook,
both per-seed (high-variance reference) and on the seed-averaged
fingerprint vector (`rho_aggregate`; used in the verdict).

### Why intensive moments (not raw power sums)

Raw power sums p_k = sum_i lambda_i^k scale as M (sum over M eigenvalues),
while p_1^k scales as M^k.  In the large-M limit the Schur-Weyl mass
fractions concentrate on the all-singletons partition (1^n) (Plancherel
concentration), drowning out the spectral-shape signal.  Using
intensive moments m_k = (1/M) p_k makes the mass fractions reflect the
SHAPE of the empirical spectral measure rather than the sample size.
This is the correct convention for an "intensive provenance fingerprint"
that ports across substrates of different N.

---

## Formula self-tests (per [[feedback-strategy-spec-formula-selftests]])

Schur-Weyl group theory has nontrivial machinery; every closed-form
identity below is explicitly tested in `self_test()`.

| # | Formula | Input | Expected | Verified |
|---|---|---|---|---|
| 1 | partition count p(n) | n=0..6 | 1,1,2,3,5,7,11 | YES |
| 2 | chi^(2)(1,1) | S_2 character | +1 | YES |
| 3 | chi^(1,1)(2) | S_2 character (sign) | -1 | YES |
| 4 | chi^(2,1)(1,1,1) | S_3 character (dim of standard rep) | +2 | YES |
| 5 | chi^(2,1)(3) | S_3 character | -1 | YES |
| 6 | chi^(3,1)(1^4) | S_4 character (dim) | +3 | YES |
| 7 | chi^(2,2)(2,2) | S_4 character | +2 | YES |
| 8 | chi^(2,1,1)(4) | S_4 character | +1 | YES |
| 9 | chi^(1,1,1,1)(4) | S_4 character (alternating sign) | -1 | YES |
| 10 | Schur s_(2)(p) closed form | p=[3,5,7] | (9+5)/2 = 7 | YES |
| 11 | Schur s_(1,1)(p) closed form | p=[3,5,7] | (9-5)/2 = 2 | YES |
| 12 | Schur s_(3)(p) closed form | p=[3,5,7] | (27+45+14)/6 = 14.333... | YES |
| 13 | Schur s_(2,1)(p) closed form | p=[3,5,7] | (27-7)/3 = 6.667... | YES |
| 14 | Schur s_(1,1,1)(p) closed form | p=[3,5,7] | (27-45+14)/6 = -0.667 | YES |
| 15 | Plancherel sum dim^2 = n! | n=1..5 | 1, 2, 6, 24, 120 | YES |
| 16 | Schur-Weyl masses sum to 1 | random positive spectrum, n=2..4 | 1.0 | YES |
| 17 | Spearman rho (identity) | x=y=[1,2,3,4] | +1.0 | YES |
| 18 | Spearman rho (anti) | x=[1,2,3,4], y=[4,3,2,1] | -1.0 | YES |
| 19 | Spearman rho (one swap) | x=[1..5], y=[1,3,2,4,5] | 0.9 | YES |
| 20 | iid MP intensive sanity | N=M=1024 iid Gauss, n=2,3,4 | mass_dev < 0.05 | YES |
| 21 | Verdict PASS branch | 3/4 rhos >= 0.60, none < 0.30 | LICENSED | YES |
| 22 | Verdict FAIL branch | 2 rhos < 0.30 | KILLED | YES |
| 23 | Verdict MIDDLE branch | borderline rhos | MIDDLE_BAND | YES |
| 24 | Verdict INCONCLUSIVE branch | only 2/4 families measured | INCONCLUSIVE | YES |

All 24 cells PASS (self-test exits cleanly).

---

## Falsifiable predictions

### COMPA_AUDIT_LICENSED (HARD PASS)

- `rho_aggregate(kappa_n_div, schur_weyl_mass_n_dev)` >= 0.60 across >= 3
  of 4 hard families {kerdock, srht, hadamard, rm_1_m}
- AND no family with `rho_aggregate < 0.30`
- Composition A's audit-trail provenance is quantitatively interpretable;
  the kappa_n algebra and Schur-Weyl algebra share real structure across
  the clean Cap 12 -> Cap 8 layer boundary.

**Substrate-product consequence on PASS**: Composition A is **annotation-
only** per Research's anchor design (Section 3.3) — no row movement on
the cap_map.  Cap 12 stays at the v174/v175 scope; Cap 8 stays at the
v168 scope.  Both cap_map rows get a cross-row corroboration annotation
citing the v1 rho values.  The composition story becomes shippable
("Cap 12 + Cap 8 jointly produce a customer-facing audit trail with
quantitative provenance receipt").

### COMPA_AUDIT_KILLED (HARD FAIL)

- `rho_aggregate < 0.30` on >= 2 of 4 hard families
- Composition A is prose-only at the quantitative level (same failure
  pattern as killed Composition B at a different mathematical layer)

**Substrate-product consequence on FAIL**: explicit narrowing of v169
annotations on BOTH Cap 8 and Cap 12.  The "Schur-Weyl-derived closed
form" language is retracted to "Schur-Weyl irreps exist in the algebra
but do not align quantitatively with kappa_n moments across codebook
families".  Caps 12 and 8 remain independently OK; the composition row
does NOT enter the cap_map.

### COMPA_AUDIT_MIDDLE_BAND

- `rho_aggregate in [0.30, 0.60)` on 1-2 families with the rest passing
- Weak structural sharing; composition stays plausible per-family;
  v169 annotations narrow to family-specific language

### COMPA_AUDIT_INCONCLUSIVE

- < 4 hard families measured (e.g. one family crashes)

---

## P estimates (deflated per [[feedback-lit-scan-calibration-penalty]])

- P(LICENSED) = 0.40 (Research's deflated estimate; the kappa_n /
  Schur-Weyl alignment is plausible because both index the same
  representation-theoretic decomposition, but cross-family heterogeneity
  is a known risk -- the v175 bimodal pattern at rho=0.90 algebraic /
  rho=0.70 randomized suggests cross-family inference here will also
  be bimodal)
- P(KILLED) = 0.20 (the algebra is genuinely shared; full quantitative
  failure across multiple families would imply the v169 closed-form
  annotations are over-stated, which has not been signaled by any
  prior verdict)
- P(MIDDLE_BAND) = 0.40 (most likely outcome given v175 bimodal pattern;
  Kerdock + Hadamard likely pass with margin, SRHT + RM(1,m) likely
  at-threshold or middle-band)

These are pre-registered; the verdict is held to the published bands
regardless of which probability lands.

---

## Substrate-product interpretation

- **LICENSED**: Composition A unlocks joint audit-trail inference —
  customer submits a codebook, Cap 12 routes (AMP vs Cap 8 VAMP-on-chain)
  based on kappa_n fingerprint, Cap 8 delivers the readout, and the
  combined provenance receipt carries Schur-Weyl irrep labels that
  customer-facing audit code can interpret.  Substrate ships
  "interpretable inference" as a capability class, not just per-primitive.
- **KILLED**: composition reverts to "Cap 12 + Cap 8 are independently
  shipped capabilities; the pipeline diagram is suggestive but the
  audit-trail is qualitative, not quantitative".  Substrate ships
  primitives, not a composed provenance story.

---

## PROT compliance

- Schema A inline key=value entry filed in `notes/exp_dev_to_queue_compA_audit_trail_2026-05-24.md`
- Background experiments per [[feedback-no-blocking-runs]]
- Pause flag CLEARED at dispatch time (orchestrator confirmed)
- `HDLAB_EXP_NAME` env var supported in script
- Atomic `write_metrics` (tmp + replace)
- Formula self-tests per [[feedback-strategy-spec-formula-selftests]] — 24 cells, all PASS
- Honest framing per [[feedback-no-smoke]]: structural integrity audit, not
  substrate-physics novelty; annotation-only on PASS (no cap_map row movement)
- Calibration deflation per [[feedback-lit-scan-calibration-penalty]] applied
  to all P estimates
