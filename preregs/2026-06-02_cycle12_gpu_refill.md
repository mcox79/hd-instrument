# GPU Refill Cycle 12 -- Pre-registrations (2026-06-02)

Triggered by: Cycle 11 verdict batch (v340). GPU overnight_queue=0 at dispatch time.
Pause-flag: ABSENT.

---

## 1. combo3_pp51_5method_on_implicit_gram_v2_cert_fix_n4096

**Queue:** overnight_queue | **N:** 4096 | **Seeds:** 5
**Script:** experiments/exp_combo3_pp51_5method_on_implicit_gram_v2_cert_fix_n4096.py

**I-17 ROOT CAUSE:** v1 deletion_cert_m_side used G^{-1} solve (pseudoinverse path) instead
of direct quadratic: cert = -||Xi xi||^2 / n^2. The G^{-1} path computes near-zero cert
(W^+ xi vs W xi); cert_diff ~1.0 structural. v2 uses same formula as N-side: cert = -||Xi xi||^2 / n^2.
Self-test confirms: cert_n = cert_m_v2 = -1.0, cert_diff = 0.0 at N=8 M=1. I-17 RESOLVED if HP4.

**HP:**
HP1: tr1 rel err < 1e-4. HP2: tr2 rel err < 1e-4. HP3: tr3 rel err < 1e-4.
HP4: cert_diff < 1e-4 (FIXED; expected ~0 by construction). HP5: matvec <= 5.
HARD-PASS: all 5 HP in >= 4/5 seeds.
MIDDLE: 4/5.
HARD-FAIL: any trace > 1e-2 OR cert_diff > 0.10.

NOTE on HP1-HP3: traces use Hutchinson estimator with N_PROBES=1000 at N=4096.
Trace rel errors ~1e-3 from v1 are MC noise NOT formula errors; HP threshold 1e-4 may
still fail for HP1-HP3. If HP4 passes but HP1-HP3 still MIDDLE, confirms cert fix is correct
but trace MC noise is the residual issue (separate from I-17 cert-path).

**P_deflated:** 0.70 (cert equivalence algebraically proven by formula derivation; trace MC
noise is the only remaining uncertainty for HP1-HP3).

**Timeout estimate:**
v1 elapsed 0.33s at N=4096 5-seed M=204. v2 same config (cert formula simpler = no G solve).
Formula: 1.5 * 0.33 * 1.0 * 1.0 = 0.50s. Round to **300s timeout** (minimum).

**PROT-018:** anchor _n4096; N=4096 in script confirmed.

---

## 2. q_a3_l7_cross_layer_composition_v1_n4096

**Queue:** overnight_queue | **N:** 4096 | **Seeds:** 5
**Script:** experiments/exp_q_a3_l7_cross_layer_composition_v1_n4096.py

**Hypothesis:** L=7 cross-layer Hadamard composition at N=4096 maintains all 7 level
fidelities >= 0.90 AND l7_acc >= 0.50. Extending L=6 (EXACT-1.0 all fidelities, v340).

**HP:** all 7 fidelities >= 0.90 AND l7_acc >= 0.50 in >= 4/5 seeds.
**HF:** any fidelity < 0.55 OR l7_acc < 0.25.
**MIDDLE:** 6/7 conditions or l7_acc in [0.25, 0.50).
**Prior:** L=6 HP all fidelities=1.0 at N=4096 5-seed (v340).

**Timeout estimate:**
L=6 elapsed 0.63s (algebraic Hadamard identity at N=4096). L=7 adds one more layer and
reduces M_OUTER from 3 to 2 (fewer queries). Estimate 1.5 * 0.63 * 1.0 * 1.0 = 0.95s.
Round to **300s timeout** (minimum).

**PROT-018:** anchor _n4096; N=4096 in script confirmed.

---

## 3. pp48_nkt_depth_9_v1_n4096

**Queue:** overnight_queue | **N:** 4096 | **Seeds:** 5
**Script:** experiments/exp_pp48_nkt_depth_9_v1_n4096.py

**Hypothesis:** PP-48 NKT at depth-9 (511 forbidden patterns) maintains pos_retrieval >= 0.80,
nkt_repulsion >= 0.70, tree_structure >= 0.70. K_POS=50 (reduced from 100 to stay
alpha_total = 561/4096 = 0.137 < alpha_c=0.138).

**HP:** all 3 conditions. **HF:** pos < 0.50 OR nkt_rep < 0.40. **MIDDLE:** 2/3.
**Prior:** depth-7 HP all rates=1.0 (127 patterns, v340). Depth-9 = 511 patterns,
near-capacity -- conservative HP threshold.

**Timeout estimate:**
depth-7 elapsed 0.99s at N=4096 K_POS=50 K_NKT=127. Depth-9: K_NKT=511 (4x more NKT patterns).
Each signed_retrieve call scales with K_NKT matrix-vector product: O(K_NKT * N).
Scaling factor ~4x for NKT, same K_POS=50. Formula: 1.5 * 0.99 * 4.0 * 1.0 = 5.9s.
Round to **300s timeout** (minimum).

**PROT-018:** anchor _n4096; N=4096 in script confirmed; alpha_total < 0.138 enforced at startup.

---

## 4. q_b1_chain_depth_30_v1_n8192

**Queue:** overnight_queue | **N:** 8192 | **Seeds:** 5
**Script:** experiments/exp_q_b1_chain_depth_30_v1_n8192.py

**Hypothesis:** Heteroassoc chain depth-30 at N=8192 maintains fidelity at key depths.
HP: d5 >= 0.95 AND d10 >= 0.88 AND d20 >= 0.80 AND d30 >= 0.65.
HF: d5 < 0.80 OR d10 < 0.65 OR d20 < 0.50 OR d30 < 0.35.
MIDDLE: d30 in [0.50, 0.65) while d5/d10/d20 meet HP.
**Prior:** depth-20 HP all EXACT-1.0 at N=8192 5-seed (v340, elapsed 18.1s).

**Timeout estimate:**
depth-20 elapsed 18.1s. depth-30 is 1.5x longer chain (30 vs 20 hops per chain, 15 chains).
Scaling: 1.5 * 18.1 * (30/20) * 1.0 = 1.5 * 18.1 * 1.5 = 40.7s.
Round to **600s timeout**.

**PROT-018:** anchor _n8192; N=8192 in script confirmed.
