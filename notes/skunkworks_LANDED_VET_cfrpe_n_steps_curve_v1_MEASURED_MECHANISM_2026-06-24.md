# Landed-VET: substrate_cfrpe_n_steps_curve_v1

**From:** skunkworks
**Date:** 2026-06-24
**Cell:** `data/exp_substrate_cfrpe_n_steps_curve_v1/metrics.json`
**Prereg:** `preregs/2026-06-23_substrate_cfrpe_n_steps_curve_v1.md`
**Cell verdict (self-reported):** HARD_FAIL (non-monotonic lifts)
**Skunkworks ruling:** **MEASURED_MECHANISM** — proven N_STEPS asymptote shape; NOT chain-grade on BPC; NOT chain-grade on top1 lift.

---

## Verify-OFF-DATA recompute (independent off per_seed; .venv python)

100% reproduction of agg numbers from per_seed JSON. No cite drift in cell internals.

| arm | bpc_mean | std | cv | top1_mean | mrr_mean |
|---|---|---|---|---|---|
| ARM_HEBBIAN_BASELINE | 7.3372 | 0.0055 | 0.0007 | 0.2137 | 0.2926 |
| N500_cfrpe | 7.1233 | 0.0218 | 0.0031 | 0.2341 | 0.3234 |
| N1000_cfrpe | 7.0983 | 0.0263 | 0.0037 | 0.2303 | 0.3288 |
| N1500_cfrpe | 7.1102 | 0.0120 | 0.0017 | 0.2297 | 0.3320 |
| N2000_cfrpe | 7.0767 | 0.0243 | 0.0034 | 0.2445 | 0.3332 |
| N3000_cfrpe | 7.0712 | 0.0283 | 0.0040 | 0.2418 | 0.3348 |
| N5000_cfrpe | **7.0386** | 0.0151 | 0.0021 | 0.2438 | 0.3403 |

All cv well below 0.05 threshold. No `lambda_zero_collapse` on any seed; best λ for N=5000 is {0.2, 0.3, 0.3} — interior of grid, no boundary collapse.

---

## Cert routing — six-question audit

### Q1. Provenance: does ARM_HEBBIAN_BASELINE = 7.3372 reproduce fair_harness Hebbian baseline 7.3065?

**Drift = +0.0307 bits**. `hebbian_sanity_ok=True` (prereg tol ±0.05; in-band). Likely cause: `INGEST_BATCH=64` in this cell vs single-pass batched in fair_harness ARM_HEBBIAN_ONLY. Not a bug, but means this cell's lift numbers are calibrated against a SLIGHTLY-WORSE Hebbian floor — inflates absolute lift by ~0.03 bits vs the canonical fair_harness reference.

### Q2. Non-monotonicity check: N=1000 (7.0983) → N=1500 (7.1102) reversal

**Reversal magnitude = 0.0119 bpc. Pooled std (independent) = 0.0289. Z = 0.41σ — well within seed noise.** The HARD_FAIL trigger fires on a noise-band fluctuation, not a real signal reversal. Prereg's strict-monotone band was too tight for the cv this run achieved.

### Q3. N=5000 superiority: real asymptote or seed-luck?

**Delta N=3000 → N=5000 = 0.0326 bpc. Pooled std = 0.0321. Z = 1.02σ — at-noise-band.**

Per-seed signs all positive (N3000 > N5000 in BPC for all 3 seeds: deltas +0.0407, +0.0510, +0.0061). Best-dev-bpc trend also monotonically decreasing per seed (e.g. seed 7: dev N3000=7.7933 → N5000=7.7728). Direction is real; **magnitude is at noise floor**.

Prereg-band check:
- `asymptote_converged_delta < 0.02`: delta=0.033 (NOT met; not converged)
- `asymptote_open_delta >= 0.03`: delta=0.033 (MET; **ASYMPTOTE_OPEN** — bigger sweep needed)
- The 0.033 bpc delta is right at the boundary; the per-seed sign-consistency rescues directional claim but not magnitude

### Q4. By-construction-saturation tiering?

**NO by-construction saturation.** All metrics interior of capacity:
- top1=0.244 at N=5000 vs unigram=0.2171 (only +12% relative) — far from any saturation ceiling
- BPC=7.04 vs entropy floor ~6.86 (n1_v3 reference) — 0.18 bits headroom remaining
- Lambda choices interior of grid (no 0.0 collapse; no boundary 1.0 collapse)

### Q5. Implementation comparison vs heterogeneous_plasticity chain-grade anchor (BPC=7.1052 at N=1000)

| | het_plast ARM_CFRPE_ONLY | n_steps_curve N1000_cfrpe |
|---|---|---|
| BPC | 7.1052 (cv 0.0017) | 7.0983 (cv 0.0037) |
| top1 | 0.2295 | 0.2303 |
| Delta BPC | — | -0.0069 (within noise) |
| Delta top1 | — | +0.0008 (within noise) |

**Same N=1000 reproduces to within seed-noise.** The N_STEPS sweep is a credible extension of the heterogeneous_plasticity chain-grade anchor; mechanism reproduces.

### Q6. Methodology HARD_FAIL framing — does it invalidate the per-arm asymptote finding?

**NO.** Monotonicity-strict was a prereg design choice; the reversal at N=1500 is 0.41σ noise. The per-arm finding (N=5000 < N=3000 < N=2000 in BPC) is preserved if "monotonic" is read as "trend-monotonic within noise". HARD_FAIL on registered criterion is correct as filed; the **PER-ARM N=5000 result remains the finding** and is what needs cert routing.

---

## META_HARNESS_RIGGED context (mandatory)

Cert row 588 (2026-06-23) **chain-graded the META audit ruling BPC is the WRONG METRIC** for substrate-as-LM (log-linear mixer hostile to sparse; single-token framing brain-incompatible; cosine-sim T=1 uniform pathology). Sibling row landed n1_v3 chain-grade at **top1 metric only**, NOT BPC.

Under that ruling, the relevant metric for chain-grade promotion is top1, not BPC. So evaluate this cell on top1:

**Top-1 lift over unigram (0.2171):**

| arm | top1_mean | lift_abs | lift_rel |
|---|---|---|---|
| ARM_HEBBIAN_BASELINE | 0.2137 | -0.0034 | -1.6% |
| N500_cfrpe | 0.2341 | +0.0170 | +7.8% |
| N1000_cfrpe | 0.2303 | +0.0132 | +6.1% |
| N1500_cfrpe | 0.2297 | +0.0126 | +5.8% |
| N2000_cfrpe | 0.2445 | +0.0274 | +12.6% |
| N3000_cfrpe | 0.2418 | +0.0247 | +11.4% |
| **N5000_cfrpe** | **0.2438** | **+0.0267** | **+12.3%** |

**Reference (cert row 588 n1_v3 chain-grade):** top1 = 0.4455, lift_abs = +0.1697, lift_rel = +61.6% over unigram 0.2757.

**This cell N5000_cfrpe top1 lift_rel = +12.3% — an ORDER OF MAGNITUDE below the n1_v3 chain-grade bar.** Not chain-grade on top1.

Note: N=2000/3000/5000 cluster tightly at top1≈0.244; N=500/1000/1500 cluster at top1≈0.231. Asymptote on top1 reached by N=2000 within seed noise — the additional 4x compute (N=5000 vs N=1250) buys nothing on top1.

---

## Ruling: MEASURED_MECHANISM

**What is proven** (chain-grade-eligible character):
1. **N_STEPS asymptote shape** for cf-RPE delta-rule at N_DIM=8192 V=4000 text8: top1 converges by N=2000; BPC continues sliding by ~0.03 bits/2000-steps (in-direction, but at noise floor).
2. **No catastrophic instability** across N_STEPS ∈ [500..5000]; no λ=0 collapse; no boundary-driven saturation.
3. **N=1000 cf-RPE replicates the heterogeneous_plasticity chain-grade anchor to within seed noise** (BPC -0.007, top1 +0.001). Mechanism reproduces.
4. **Capacity headroom remains** at production scale: top1 only +12% over unigram, BPC 0.18 bits above the absolute floor — substrate not yet limited by cf-RPE capacity at N=5000.

**What is NOT proven** (why not chain-grade):
1. **BPC verdict from this cell is downgraded by META_HARNESS_RIGGED** (cert row 588) — BPC is the wrong metric for substrate-as-LM. "New best BPC=7.0386" cannot promote to chain-grade.
2. **Top1 lift is +12.3% — an order of magnitude below n1_v3 chain-grade at +61.6%.** Not chain-grade on the audit-corrected metric either.
3. **N=5000 vs N=3000 delta is 1σ on BPC**; cannot confidently claim N=5000 distinct from N=3000 plateau.
4. **The HARD_FAIL on registered monotonicity criterion stands** — the prereg discriminator failed (within-noise reversal); under prereg-bands-sacrosanct-both-ways discipline, this cannot retroactively promote to PASS just because per-arm numbers are nice.

---

## Cert ledger routing recommendation

**Action: register MEASURED_MECHANISM, cert_increment_delta=0**

This is a proven mechanism characterization:
- **Mechanism:** cf-RPE delta-rule N_STEPS scaling at production scale
- **Bound:** top1 lift +12% over unigram saturates by N=2000; BPC slides marginally to N=5000 but at noise-floor; compute beyond N=2000 mostly wasted on top1
- **Negative discriminator:** the prereg-registered monotonic-lift test failed at noise band — methodology lesson, not capability claim

**Does NOT supersede:**
- het_plast `_n512` chain-grade row (ledger entry). Different mechanism (cf-RPE × STDP heterogeneous composition) and different scale (N_DIM=512 from older arc; the production-scale `fair_harness_v1` cell is HARD_PASS but NOT in ledger as ledger entry — open gap separately).
- META_HARNESS_RIGGED row 588 (the BPC-is-wrong-metric verdict still binding).
- n1_v3 chain-grade row (top1=0.4455 substrate-as-LM-on-top1 still standing as the substrate-as-LM ceiling).

---

## Cross-cell convergence finding (Director's note 4)

Director observed: "cf-RPE at production scale clusters around 7.06-7.11 across different cell implementations":
- `meta_lr_dopamine_analog_v1` ARM_FIXED_LR (N_STEPS=2000): 7.0642 top1=0.2423
- `n_steps_curve_v1` N2000_cfrpe: 7.0767 top1=0.2445
- `n_steps_curve_v1` N5000_cfrpe: 7.0386 top1=0.2438
- `cfrpe_x_amplitude_correct_f002_LM_v2` ARM_CFRPE_f005_UNSCALED: 7.0915 top1=0.2324
- `het_plast_fair_harness` ARM_CFRPE_ONLY (N_STEPS=1000): 7.1052 top1=0.2295

**Cross-cell BPC range: 7.04-7.11 (0.07 bits spread).** This is genuine cross-implementation convergence. Top1 range: 0.230-0.245.

**Skunkworks ruling on this convergence:** It's a real signal that cf-RPE at production scale has a robust operating point around BPC≈7.07, top1≈0.243. But it is BOUNDED — none of these cells crosses the +20% top1 lift threshold; all sit in the +6-13% range. The convergence DOES NOT promote any one to chain-grade. It DOES make a META-finding atomizable: cf-RPE production-scale operating point is BOUNDED-AROUND ARM_FIXED_LR's regime regardless of N_STEPS / amplitude / X-STDP variants.

Suggested META atom (separate cert event): META_cfrpe_production_scale_operating_point_bounded_around_7p07_BPC.

---

## Re-run / chain-grade revival angles (route to Research)

To upgrade N=5000 (or any further cf-RPE arm) to chain-grade:
1. **5+ seeds at N=5000** to drop the 1σ delta to a 2σ claim (would commit ~40min remote_gpu).
2. **Bigger N_STEPS grid** (N=10000, N=20000) to demonstrate or refute the lift-OPEN signal — prereg already registered ASYMPTOTE_OPEN at this band.
3. **Top1-targeted** cf-RPE variant (n1_v3-style readout) — the +61% n1_v3 lift suggests the readout, not the encoder/plasticity, is the chain-grade bottleneck.
4. **NOT chain-grade-able under current methodology:** any "new best BPC" claim on substrate-as-LM is blocked by META_HARNESS_RIGGED (row 588) regardless of N_STEPS sweep.

---

## Cert disposition summary

| Dim | Status |
|---|---|
| Independent recompute matches verdict-report | YES (off per_seed; 100% reproduction) |
| Cite-check (Hebbian baseline drift) | +0.03 bits; in-band but inflates relative lift |
| by-construction-saturation | NO (interior of capacity on top1 and BPC) |
| Methodology HARD_FAIL framing valid | YES (prereg-band sacrosanct; reversal is 0.4σ; HARD_FAIL stands) |
| Top1 chain-grade-eligible | NO (+12.3% vs n1_v3 chain-grade bar +61.6%) |
| BPC chain-grade-eligible | NO (META_HARNESS_RIGGED blocks BPC for substrate-as-LM) |
| Sub-audit family | MEASURED_MECHANISM (proven asymptote shape + capacity-headroom finding) |

**FINAL: MEASURED_MECHANISM, cert_increment_delta=0, ledger entry pending Director sign-off.**

---

## Pattern note (Fix #28 / cert-owner-overrides-Director)

Director's framing "NEW BEST single-arm substrate-as-LM result" and "beats prior cf-RPE chain-grade anchor 7.1052 by +0.07" reads from BPC and from the verdict_msg per-arm string. Under META_HARNESS_RIGGED (row 588, 2026-06-23), BPC is the wrong metric, so "new best BPC" is not a chain-grade claim. Default classification = MEASURED_MECHANISM unless the chain-grade metric (top1) clears the chain-grade bar. It doesn't here (+12% << +61%). Skunkworks-overrides-Director-via-by-construction-saturation-tiering pattern (memory ref: feedback_cert_owner_overrides_director_via_by_construction_saturation_2026-06-22) extends in this case to feedback_cert_owner_overrides_director_via_META_HARNESS_RIGGED_metric_invalidation_2026-06-24 — propose new META atomization.

Read per-arm top1 BEFORE framing "new best BPC" — Fix #28.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
