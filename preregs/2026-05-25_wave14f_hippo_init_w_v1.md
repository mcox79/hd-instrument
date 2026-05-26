# Pre-registration: wave14f_hippo_init_w_v1

**Filed:** 2026-05-25 by exp_dev  
**Trigger:** SSM-HiPPO handoff (notes/exp_dev_handoff_ssm_hippo_design_2026-05-25.md)  
**Upstream research:** notes/research_ssm_hippo_compatibility_2026-05-25.md  
**Script:** experiments/exp_wave14f_hippo_init_w_v1.py  

---

## Background

v190 wave14e_s4_depth_smoke CLOSED-FAILED (binding_depth=200, ssm_depth=0).
SSM-as-overlay framing closed by Jelassi 2024 Theorem 2.7 (|U| >= |V|^n state-size
lower bound). Surviving substrate-compatible framing: HiPPO-LegS as INITIALIZER for W.

---

## Three pre-registered predictions

### Prediction 1: HiPPO-init W vs random-init W (chain-cleanup depth-at-half)

HiPPO-LegS-structured W_0 (built from HiPPO eigenvalue-weighted outer-product) will
show better chain-cleanup depth-at-half than zero-init W on Cap 3 chain task at
d_max=200.

**HARD PASS:** depth_at_half(HiPPO-init) >= 1.5x depth_at_half(random-init) ACROSS
ALL seeds (mean ratio >= 1.5 AND no individual seed has ratio <= 1.0).

**HARD FAIL:** depth_at_half(HiPPO-init) <= 1.0x depth_at_half(random-init) on ANY
seed (HiPPO-init provides no improvement; framing closed).

**MIDDLE:** mean ratio in (1.0, 1.5); some improvement but below category-defining bar.

### Prediction 2: N-doubling is INSUFFICIENT (Jelassi bound observable)

Doubling N (N_FULL -> N_2X=8192) while using random-init and no replay will NOT
recover chain-cleanup at d=200. The depth_at_half should NOT scale super-linearly
with N -- confirming substrate sits in the SSM recall-bound regime.

**HARD PASS (Jelassi confirmed):**  
- depth_at_half(N_2x) / depth_at_half(N) < 1.2 (N-doubling does not help meaningfully)

**HARD FAIL (Jelassi rejected):**  
- depth_at_half(N_2x) / depth_at_half(N) >= 1.8 (N-doubling rescues; substrate not SSM-class)

**MIDDLE:** ratio in [1.2, 1.8).

### Prediction 3: HiPPO eigenspace in post-training W

The top-32 singular values of HiPPO-init W and post-Hebbian-training random-init W
should be correlated > 0.5 if the substrate implicitly learns a HiPPO-like eigenspace.

**HARD PASS:** Pearson correlation of top-32 singular values > 0.5  
**HARD FAIL:** correlation < 0.2 (spectra uncorrelated; HiPPO not implicitly learned)

---

## Calibration note

No prior empirical anchor for HiPPO-init on BSC outer-product W. Bands set per
[[feedback-envelope-expansion-fail-bands]] and [[feedback-lit-scan-calibration-penalty]]:
- Lit-scan calibration penalty applied: P(category-defining) = 0.18 (from research note)
- First-measurement probe; bands widened as noted above

---

## Self-test cells (formula verification)

hippo_legs_eigenvalues self-tests (verified in _instrumentation_selftest):
- H=32: magnitudes.shape == (32,), all > 0, not all equal
- W_hippo shape (64, 64), no NaN, not all-zero

chain_cleanup_depth self-tests:
- N=64, d_max=10, n_probes=5, W_zero: dah >= 0, cos_profile len=11, no NaN

spectral_correlation:
- W_hippo (64,64) vs random W_b (64,64): corr is not NaN

compute_verdict self-tests:
- p1_ratio=2.0, p2=1.1, p3=0.7 -> P1_HARD_PASS + P2_HARD_PASS + P3_HARD_PASS
- p1_ratio=0.8, p2=2.5, p3=0.1 -> P1_HARD_FAIL + P2_HARD_FAIL + P3_HARD_FAIL

---

## Queue and runtime

Queue: overnight_queue (remote GPU; N=4096 + N=8192 at full scale, 3 seeds x d_max=200)
Smoke: local CPU (N=1024, d_max=50, 1 seed; estimated ~2-5 min; P2 skipped on smoke)
Full: estimated 2-4 hours GPU

---

## Pre-commit cap_map outcome mapping

- P1_HARD_PASS: open new cap_map row "HiPPO-init W capability" 🟡 promoted;
  bump R-PRIME-5 to 🟡 promotion; cross-ref Cap class 2 (editable memory) + class 4
- P1_HARD_FAIL on all: close "HiPPO-init W" as inapplicable; promote P2 result alone
- P2_HARD_PASS: annotate ALL multi-hop/depth-cliff rows (Cap 10, Cap 12, Bet S4)
  "Jelassi state-size lower bound CONFIRMED empirically; depth-extension via SSM-class
  mechanisms is structurally closed; pivot toward attention-class primitives"
- P2_HARD_FAIL: open new annotation "substrate-novel N-scaling regime; substrate NOT
  bound by Jelassi lower bound; investigate mechanism"
- Negative on both P1+P2: file negative-result-2x research drill per
  [[feedback-negative-results-2x-research]] targeting attention-class alternatives
