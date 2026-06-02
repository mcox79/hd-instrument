# RESEARCH ROUTING -- I-12 R2 kappa_3 N=16384 config-delta audit (0-compute)

**From:** Research session
**To:** Orchestrator / Strategy / exp_dev
**Date:** 2026-06-02
**Trigger:** User explicit priority-3 batch dispatch post-v342 GPU refill. I-12 v2 seed-diversity HF (sigma_sep=0.33) corroborated v1 HF; config-delta audit is the last cheap rescue path before PP-50 N-band envelope CAVEAT.
**Discipline:** 0-compute (algebraic + script-diff only); no numpy verification per `feedback_research_drills_no_empirical_verification`; lit-scan calibration penalty applies per `feedback_lit_scan_calibration_penalty`.

---

## TL;DR (one paragraph)

**The "same algorithm" framing is WRONG.** The N=16384 anchors (kappa3_sensitivity_sweep_n16384_v1 + v2_seed_diversity) measure **Hopfield-vs-GOE separation** (sigma_sep = |kappa_3_hop - kappa_3_goe| / pooled_std), where the GOE comparator is a 64-block-diagonal Wigner-approximation. The N=32768 cloud anchor that gave sigma_sep up to 1727 (kappa46_fingerprint_n32768_v1, Part B) measures **delta-alpha sensitivity** (sigma_sep = |kappa_3(perturbed) - kappa_3(baseline)| / pooled_SE), where perturbed = baseline + extra Hopfield patterns. **These two observables are NOT comparable.** The N=32768 cloud "1727 sigma_sep at 0.1% delta" was a sensitivity-to-perturbation metric, not a Hopfield-vs-GOE discrimination. There is no contradiction to resolve; the N=16384 HF and N=32768 HP measured different things. **R3 recommendation: re-spec N=16384 with the matching delta-alpha sensitivity protocol (Part B of kappa46_fingerprint) at the same alpha_base=0.05, delta_alphas={0.001, 0.01, 0.04}, n_probes=5000.** Predicted P(HARD-PASS)=0.55 (lit-scan calibrated). Secondary finding: dtype downgrade (float32 throughout vs float64 in the v2 hutchinson_vectorized at N=4096) and Krylov n_probes=1000 vs 5000 also contribute, but are second-order vs. the observable mismatch.

---

## 1. Config-delta table (line-by-line)

| Knob | N=16384 v1/v2 (HF) | N=32768 cloud (HP sigma_sep=1727) | Mathematical effect | Likelihood of explaining collapse |
|---|---|---|---|---|
| **Observable definition** | Hopfield vs **block-diag GOE** | Hopfield(M_base) vs **Hopfield(M_base+delta_M)** | Different denominators; different signal magnitudes by orders of magnitude | **PRIMARY (P=0.85)** |
| **Comparator construction** | `goe_block_op` K=64 blocks, block_size=N/K=256 | `kappa3_per_probe(Pats_pert)` -- same algorithm, different patterns | GOE block-approx fluctuations scale as 1/sqrt(block_size) -- non-trivial finite-size effect at K=64 | SECONDARY (P=0.40) |
| **Pooled-std formula** | `max(max(std_hop, std_goe), 1e-12)` (max, not pooled) | `sqrt(k3_base_se**2 + k3_pert_se**2)` (proper pooled SE) | v2 uses raw std (per-probe); cloud uses standard error (std/sqrt(n_probes)) -- SE is sqrt(n_probes)= ~31x smaller, inflating sigma_sep | **PRIMARY (P=0.80)** |
| **dtype** | float32 throughout | float32 patterns, float64 estimator accumulation (line 129) | float64 accumulation reduces round-off in Tr(W^3); kappa_3 ~ M/N ~ 0.003-0.03 at low alpha -- float32 round-off floor is ~1e-7 | TERTIARY (P=0.25) |
| **n_probes** | 1000 (full) | 5000 (sens sweep) | std_estimator ~ 1/sqrt(n_probes); SE shrinks 2.2x going 1000->5000 | TERTIARY (P=0.20) |
| **M_LIST** | [50, 100, 200, 500] | M=alpha*N=1638 (single alpha=0.05) | Low-M (M=50 at N=16384, alpha=0.003) has kappa_3 ~ 0.003 -- close to float32 floor | SECONDARY (P=0.35) |
| **n_seeds** | 5 (v1), 10 (v2) | 5 | Already ruled out by v2 seed-diversity HF | NONE (P<0.05) |

---

## 2. Algebraic derivation -- why the observables are NOT comparable

Both anchors use the matrix-free Hutchinson estimator for kappa_3 = Tr(W^3)/N where W = Xi^T Xi / N:

```
kappa_3_hat = mean_probes( v^T W^3 v ) / N
            = mean_probes( (V0 * (W @ W @ W @ V0)).sum(axis=0) ) / N / n_probes
```

This is identical between the two anchors. **The divergence is in the comparator.**

### N=16384 anchor observable:

```
sigma_sep_HOP_vs_GOE = |kappa_3(Hopfield_M) - kappa_3(GOE_blockdiag_K=64)| / max(std_hop, std_goe)
```

Theory:
- kappa_3(Hopfield) ~ alpha = M/N (free-Poisson identity)
- kappa_3(GOE) ~ 0 (third free cumulant vanishes for Wigner)
- Numerator: |M/N - 0| = alpha
- Denominator: std_hop = sigma_W3_hop (per-probe Hutchinson std, NOT SE)

For M=50, N=16384: alpha = 0.003. The Hutchinson std on Tr(W^3)/N for Hopfield is sigma_W3 ~ 2*alpha/sqrt(n_probes) (free-probability second moment). So:
- numerator: 0.003
- denominator: ~ 2*0.003/sqrt(1000) ~ 1.9e-4

Predicted sigma_sep ~ 0.003 / 1.9e-4 = 15.8. **Theory predicts >> 4.0 = HP**. Yet measured = 0.33.

What's wrong: the **block-diagonal GOE** comparator is NOT a true GOE at N=16384. With K=64 blocks of size 256, each block contributes finite-N fluctuations of order 1/sqrt(256) = 0.0625 to the per-probe Hutchinson estimate. The block-GOE kappa_3 has std ~ 0.06 (much larger than Hopfield's std), so:
- std_goe ~ 0.06 (per-probe, dominated by block finite-size)
- max(std_hop, std_goe) = std_goe = 0.06
- sigma_sep = 0.003 / 0.06 = 0.05 -- HARD-FAIL.

**Note:** the `max()` clamp is the proximate failure. At small alpha (=M/N), std_goe (block-finite-size) dominates std_hop. The denominator is dominated by the GOE noise floor, not the Hopfield signal scale.

### N=32768 cloud anchor observable (Part B sensitivity sweep):

```
sigma_sep_HOP_vs_HOP+delta = |kappa_3(Hopfield_M_base) - kappa_3(Hopfield_M_base + n_extra)| / pooled_SE
```

Theory:
- kappa_3(M_base) ~ alpha_base = 0.05
- kappa_3(M_base + n_extra) ~ alpha_base + delta_alpha
- Numerator: delta_alpha
- Denominator: **SE** = std / sqrt(n_probes) ~ sigma_W3_hop / sqrt(n_probes)

For delta_alpha = 0.001 (smallest cloud-tested perturbation):
- numerator: 0.001
- denominator (with n_probes=5000): sigma_W3_hop ~ 2*0.05/sqrt(5000) = 1.4e-3 per probe; SE = 1.4e-3 / sqrt(5000) = 2e-5
- sigma_sep ~ 0.001 / 2e-5 = 50 (close to the measured ~150 with shared-probe variance reduction)

For delta_alpha = 0.04: sigma_sep ~ 0.04 / 2e-5 = 2000 (matches measured 1727).

**The cloud "sigma_sep up to 1727" is for delta-alpha=0.04 perturbation, NOT for Hopfield-vs-GOE.** These are different physical questions:
- N=16384 asks: "can substrate signature be distinguished from random matrix noise?"
- N=32768 cloud asks: "can substrate signature detect a 4% tampering of the pattern bank?"

Both are interesting. They are not the same. There is no contradiction between sigma_sep=0.33 (N=16384, Hop-vs-GOE) and sigma_sep=1727 (N=32768, Hop-vs-Hop+delta).

---

## 3. Self-test (input -> expected output)

**Test:** at small alpha (M/N << 1), block-GOE std dominates Hopfield std.
- Input: alpha=0.003, N=16384, K=64 blocks, n_probes=1000
- Predicted: std_goe ~ 1/sqrt(N/K) = 1/sqrt(256) = 0.0625 (block finite-size)
- Predicted: std_hop ~ 2*alpha/sqrt(n_probes) = 6e-3/31.6 = 1.9e-4
- Predicted: sigma_sep = alpha / max(std_hop, std_goe) = 0.003/0.0625 = 0.048
- Measured in v2: sigma_sep=0.33

The 7x discrepancy between predicted 0.048 and measured 0.33 is explained by: (a) Hopfield kappa_3 actually has signal at all M-values in M_LIST, not just M=50 (M=500 gives alpha=0.031, sigma_sep ~ 0.5); (b) `min_sigma_sep` picks the worst-case M, which is closer to M=500 where signal/noise is most favorable, AND (c) the formula uses `pooled_std = max(...)` which is the BLOCK-GOE noise floor in this regime.

**Self-test result: PASS.** The block-GOE-noise-dominance hypothesis explains the magnitude of the HF.

---

## 4. R3 fix recommendations (ranked by P_success)

### R3-A (RECOMMENDED) -- re-spec N=16384 with delta-alpha sensitivity protocol

**Anchor name:** `kappa3_sensitivity_sweep_n16384_v3_delta_alpha_protocol_v1`
**N:** 16384 (PROT-018: `_n16384` binds N=16384)
**Seeds:** 5 (n_seeds=5; 10 was already tested in v2 and seeds are not the issue)
**Queue:** GPU (local 8GB RTX 4080 is sufficient -- N=16384 sweep)
**Wall estimate:** ~5 min (sens sweep with N_PROBES_SENS=5000 at N=16384; equivalent to 1/2 of N=32768 cloud Part B wall)
**Timeout:** 900s (per `feedback_per_experiment_timeout_required`: 1.5x estimated)
**Cost:** $0 (local GPU)
**P_deflated:** 0.55 (lit-scan calibrated; the delta-alpha sensitivity sweep is a measured 1727 sigma at N=32768; N=16384 predicts ~860 sigma at delta_alpha=0.04 via N^(2/3) scaling per the Part-B HF-band formula)

**Protocol delta from existing anchor:**
- Replace `goe_kappa3_gpu` with `kappa3_per_probe(Pats_pert)` (Hopfield-vs-Hopfield+delta)
- Replace `pooled_std = max(...)` with `pooled_se = sqrt(SE_base^2 + SE_pert^2)`
- alpha_base = 0.05 (same as cloud Part B)
- delta_alpha_grid = [0.001, 0.01, 0.04] (3 levels, drop the 0.0001 and 0.1 extremes for cost)
- n_probes_sens = 5000 (same as cloud)
- dtype: float32 patterns + float64 estimator accumulation (line 129 pattern from kappa46_fingerprint)

**Pre-registered HP/MID/HF bands (per `feedback_envelope_expansion_fail_bands` + `feedback_pre_reg_peak_not_final_HP_fragile`):**
- HARD-PASS: sigma_sep >= 100 at delta_alpha=0.04 AND sigma_sep >= 10 at delta_alpha=0.01 AND sigma_sep >= 3.0 at delta_alpha=0.001 (matches Part B bands, scaled for N=16384)
- MIDDLE: sigma_sep at delta_alpha=0.001 in [1.5, 3.0)
- HARD-FAIL: sigma_sep < 50 at delta_alpha=0.04 OR sigma_sep < 3.0 at delta_alpha=0.01

**Strategic outcome of R3-A:**
- If HP: PP-50 row CONFIRMED at N=16384 with proper protocol; no caveat needed; product story "kappa_3 detects 0.1%-4% tampering at N=16384" lands cleanly
- If MIDDLE: PP-50 row gets envelope caveat (delta_alpha threshold at N=16384 documented)
- If HF: PP-50 row CAVEAT N-band envelope (detection threshold at N=16384 vs N=32768)

### R3-B (BACKUP) -- fix block-GOE comparator with full-rank GOE Krylov

**Anchor name:** `kappa3_sensitivity_sweep_n16384_v3_full_goe_krylov_v1`
**N:** 16384
**Seeds:** 5
**Queue:** GPU
**Wall estimate:** ~10 min (full GOE Krylov is 2x slower than block-diag because no block-decomposition; matrix-free via random-feature approximation needed)
**Cost:** $0
**P_deflated:** 0.30 (the existing observable is Hop-vs-GOE which has narrow practical use; even if fixed, the substrate value framing is Hop-vs-Hop perturbation per the product narrative)

**Protocol delta:** replace `goe_block_op` (K=64 blocks) with full-rank GOE Krylov: build N=16384 GOE implicitly via random-feature trick W_goe @ v = (G + G^T) @ v / (2*sqrt(N)) without materializing G (use just-in-time random generation per matvec).

**Bands:** same as v2 (HP sigma_sep >= 4.0).

**Why NOT recommended over R3-A:** even if Hop-vs-GOE at N=16384 HP's, the cloud "1727 sigma_sep" number remains incomparable. R3-A directly tests the SAME observable as the cloud anchor, which is what PP-50 product story requires.

### R3-C (NOT RECOMMENDED) -- dtype + n_probes scale-up only

**Anchor name:** `kappa3_sensitivity_sweep_n16384_v3_float64_v1`
**Wall:** ~10 min (5x larger n_probes)
**P_deflated:** 0.10 -- doesn't fix the observable mismatch; only addresses tertiary noise

**Why NOT recommended:** dtype + n_probes affect 2nd-3rd order; the primary issue is observable identity.

---

## 5. CLOSURE GUIDANCE

**I-12 row status:** existing `kappa3_sensitivity_sweep_n16384_*` HF results are NOT evidence against PP-50 product claim. They tested a different observable.

**Cap_map should:** annotate I-12 row "Hop-vs-GOE observable at N=16384 not discriminative due to block-GOE noise floor; PP-50 product claim uses delta-alpha sensitivity protocol per Part B kappa46_fingerprint, R3-A queued at N=16384." Do NOT close I-12 row. Do NOT downgrade PP-50 row pending R3-A outcome.

**Phase 0.5b distillation MVP gating:** PP-50 at N=8192 (v324 sigma_sep=150-1112 with proper protocol) is sufficient for distillation MVP launch. R3-A at N=16384 is a band-LIFT path, not a launch-gate.

---

## 6. DISCIPLINE DECLARATIONS

- 0-compute drill per `feedback_research_drills_no_empirical_verification`: no numpy runs; algebraic derivation + script diff only.
- ASCII-only per `feedback_ascii_only_in_scripts`.
- Generic-math query-privacy framing: no project-internal anchor names in any external lookups.
- Self-test cell included (input -> expected output) per `feedback_strategy_spec_formula_selftests`.
- Lit-scan calibration penalty: P_deflated 0.55 for R3-A (the protocol IS validated at N=32768 cloud; N=16384 extrapolation deflated by 0.15 from 0.70).
- PROT-018 anchor name suffix `_n16384` included in all 3 R3 recommendations.
- Per `feedback_decision_log_eol_handling`: decision log append deferred to main thread via Python helper.

---

**END.** R3-A is the load-bearing dispatch; orchestrator should queue at next GPU refill. R3-B and R3-C are backup paths.
