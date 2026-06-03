# Prereg: pp49_hrc_depth_parity_discriminator_sweep_v1_n4096

**Date:** 2026-06-03
**Anchor:** pp49_hrc_depth_parity_discriminator_sweep_v1_n4096
**Queue:** remote_cpu_queue (pure CPU; N=4096 depth sweep)
**Source:** exp_dev_handoff_research_pp49_depth_nonmonotone_2026-06-03.md
           research_routing_v359_drill_battery_synthesis_2026-06-03.md Section 3 Exp 3

---

## Capability question

Does counterfactual recovery follow the parity-class prediction (cf_cos alternates +/- across d)
OR the protocol-artifact prediction (smooth monotone under root-start, saturated <=0.50 under
predecessor-start)?

---

## N-suffix

No _nN suffix in anchor name. Production N = 4096. Rationale: parity-discriminator sweep; depth
is the primary axis, not N. PROT-018 explicit exemption documented in script docstring.

---

## Pre-registered threshold bands

**HARD-PASS (PARITY-CLASS confirmed):**
- cf_cos_pred_start(d) alternates: >3 of 4 even depths [2,4,6,8] have mean cf_cos >= 0.70
  AND >3 of 4 odd depths [1,3,5,7] have mean cf_cos <= 0.50
- (under either protocol)

**HARD-PASS (PROTOCOL-ARTIFACT confirmed):**
- cf_cos_pred_start <= 0.55 for ALL depths (rank-1 ceiling consistent)
- cf_cos_root_start >= 0.85 for >= 3 of 4 depths >= 2 (smooth, no parity alternation)

NOTE: both PARITY-CLASS and PROTOCOL-ARTIFACT outcomes are HARD_PASS (PP-49 intact).
The discrimination determines product-API design choice:
- Parity-class -> even-depth convention OR sign-flip on odd-depth
- Protocol-artifact -> adopt root-start as default

**MIDDLE-BAND:**
- Mixed mechanism (neither pure parity-class nor pure protocol-artifact)

**HARD-FAIL:**
- Both protocols: cf_cos <= 0.20 at ALL depths (mechanism fundamentally broken)

---

## Formula self-tests (PROT-022)

1. Root-start depth-1: probe from x0 through CF matrix; result is non-null/non-NaN
2. Pred-start depth-1: identical to root-start at d=1 (since pred = x0 = root)
3. Even/odd depth lists are non-empty; all 8 depths covered in TEST_DEPTHS
4. W_cf construction: replacing hop (subst_pos-1 -> xi_A) with (subst_pos-1 -> xi_B) correct

All verified in _instrumentation_selftest().

---

## Test design

- N = 4096, alpha = 0.05, 5 seeds [7, 17, 23, 31, 41]
- Depths: [1, 2, 3, 4, 5, 6, 7, 8]
- BOTH protocols per depth: predecessor-start and root-start
- substitution at midpoint (depth//2) of chain
- M_BG = int(0.05 * 4096) = 204 background patterns

---

## Timeout estimate

Smoke: N=512, 2 seeds, 8 depths, 2 protocols -> ~30s expected.
Full: N=4096, 5 seeds, 8 depths * 2 protocols.
Scaling: linear (no matrix ops; inner loop is O(N^2) per chain but N_chains=8 small).
timeout = ceil(1.5 * 60 * (4096/512)^1.0 * (5/2)) = ceil(1.5 * 60 * 8 * 2.5) = ceil(1800) = 1800s.
With margin: 600s (expected actual wall << 1800s given simple retrieval).
timeout = 600s.

---

## Calibration notes

Prior pp49_hrc_cf_depth_band_sweep showed cf_cos depth-5 = 0.028 (HARD_FAIL).
This experiment discriminates mechanism (parity vs protocol). No prior empirical anchor on
BOTH protocols simultaneously -- bands set from research drill predictions.
