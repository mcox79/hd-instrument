# WAVE 5 CLOUD BUNDLE AMENDMENT — ADD-1, ADD-2, ADD-3 (2026-06-02)

**From:** Research session
**To:** Orchestrator / Strategy / exp_dev (cloud cell design)
**Trigger:** v333 cap_map confirmed Wave-5 Cells 1-4 AUTHORIZED; Cell 5 DEFERRED pending COMBO-1 v3; user authorized 3 additions to the cloud bundle based on v324 + COMBO-3 + Q-B1 + Q-C5 + κ_3@N=8192 results overshooting Phase-2 predictions.
**Supersedes:** scope of Wave 5 section in `research_high_priority_tests_v324_synthesis_2026-06-02.md`.
**Discipline:** capability questions + pre-registered HARD/MIDDLE/FAIL bands only; cell design (anchor names, sweep grids, queue choice, timeout) resolved by strategy + exp_dev. Pre-PROT-018 anchor-name `_n<N>` binding contract holds.

---

## 0. CURRENT WAVE-5 STATE (v333)

```
Authorized cells (gated by v324+v332+v333 confirmations):
  Cell 1: Q-D1 spectral primitives at N=32768 (gated by kappa3 N=8192 HP)
  Cell 2: kappa_4 / kappa_6 fingerprint at N=32768 (gated by kappa3 HP)
  Cell 3: Deletion-cert Z-ratio at N=32768 (gated by Q-C5 HP)
  Cell 4: COMBO-3 unified API at N=32768 (gated by COMBO-3 HP)

Deferred:
  Cell 5: COMBO-1 implicit Gram-solve at N=32768 — awaits COMBO-1 v3 redesign
          (HP1+HP2 algebraic identities FIXED in v2; HP3 slope=1.958
          super-linear scaling FAIL; HP4 SNR FAIL)

NEW additions (this amendment):
  Cell 6: Depth-5 + depth-10 heteroassociative chain at N=32768 (ADD-1)
  Cell 2-refined: kappa_3 sensitivity at refined delta-alpha sweep (ADD-2)
  Cell 7: PP-12 L=2 cross-layer composition at N=32768 (ADD-3)
```

---

## 1. ADD-1 — Depth-5 + depth-10 heteroassociative chain at N=32768

### Capability question

Does the substrate maintain production-grade fidelity on directed heteroassociative chains at depth 5 AND depth 10 at N=32768, given that Q-B1 at N={4096, 8192} delivered 0.986-0.993 at depth-3 (per-hop fidelity ~0.995)?

### Algebraic basis

Q-B1 v324 results: depth-1 = 0.991/0.996, depth-3 = 0.986/0.993 across N={4096, 8192}, unanimous. Per-hop fidelity:
- depth-3 = 0.986 → per-hop = 0.986^(1/3) ≈ 0.9953
- depth-3 = 0.993 → per-hop = 0.993^(1/3) ≈ 0.9977

Geometric extrapolation (assuming per-hop independence, which Q-B1 confirmed via per-hop independence test at rho=0.0000):
- **Depth-5 prediction: 0.9953^5 to 0.9977^5 ≈ 0.977 to 0.989**
- **Depth-10 prediction: 0.9953^10 to 0.9977^10 ≈ 0.954 to 0.977**

At N=32768 the finite-N noise floor 1/sqrt(N) ≈ 0.0055 is half of N=8192's. Substrate should maintain or improve per-hop fidelity at N=32768, not degrade.

### Pre-registered bands

**HARD-PASS:** depth-5 ≥ 0.95 AND depth-10 ≥ 0.90 across 5 seeds at N=32768.

**HARD-FAIL:** depth-5 < 0.85 OR depth-10 < 0.75 — would mean per-hop independence breaks at production N (substantial cap_map impact: would force re-derivation of chain-depth ceiling).

**MIDDLE BAND:** depth-5 in [0.85, 0.95] OR depth-10 in [0.75, 0.90] — finite-N corrections present but capability survives. Resolution: re-run at N=16384 to fit the N-scaling curve.

### Anchor / cost

- Anchor name (pre-PROT-018): `q_b1_depth_extended_n32768` per binding contract.
- Cell construction: ONE chain at depth-10 with readout snapshots at depth-1, depth-3, depth-5, depth-7, depth-10. Single ξ chain, multiple readout depths — does not multiply cost.
- 5 seeds, R=200 random source patterns per seed.
- Estimated cloud instance wall: ~30-60 min added to the existing bundle. Single instance.

### Product unlock if HARD-PASS

- **Hierarchical Refusal Cert at depth 5+** extends COMBO-2's Negative-Knowledge Tree feature. The 3-level refusal cert proposed in COMBO-2 (concept → pointer → instance) generalizes to 5+ levels of forbidden-composition certificates.
- **Counterfactual reasoning chains at depth 5-10** unlock multi-step Pearl L3 abduction over directed bindings.
- Cap_map sub-property candidate: **PP-B1-extended** depth ceiling at 5+ (currently the row is at depth-3 confirmed).

---

## 2. ADD-2 — Refined kappa_3 sensitivity sweep at N=32768

### Capability question

At N=32768, does the kappa_3 fingerprint discriminate substrate perturbations at delta-alpha = {0.0001, 0.001, 0.01, 0.04, 0.1} with σ_sep above the 3-sigma detection threshold at each level?

### Algebraic basis

Phase-2 kappa_3 drill predicted 4.2% delta-alpha sensitivity at 5000 complex probes. v324 kappa_3@N=8192 result delivered σ_sep = 150-1112 — i.e., 37x to 278x the predicted margin at the 4σ threshold. This means the operative sensitivity at N=8192 is in the 0.04-0.3% delta-alpha range, not 4.2%.

Scaling argument: σ_TW shrinks as N^(-2/3). N=32768 / N=8192 = 4 → σ_TW shrinks by 4^(2/3) ≈ 2.52x. Expected sensitivity at N=32768 lands in the **0.01-0.1% delta-alpha range** at 4σ threshold.

The Phase-2 drill's 5000-probe budget was calibrated against the 4.2% threshold; at the new sensitivity level the probe count is over-provisioned, but no harm in keeping 5000 for backward consistency.

### Pre-registered bands

**HARD-PASS (all three must hold):**
- σ_sep ≥ 100 at delta-alpha = 0.04 (4%, the Phase-2 baseline operating point)
- σ_sep ≥ 10 at delta-alpha = 0.01 (1%)
- σ_sep ≥ 3.0 at delta-alpha = 0.001 (0.1%)

**HARD-FAIL (any of):**
- σ_sep < 50 at delta-alpha = 0.04 (would mean kappa_3 fingerprint LESS sensitive at N=32768 than at N=8192 — violates N^(-2/3) scaling story)
- σ_sep < 3.0 at delta-alpha = 0.01

**MIDDLE BAND:** σ_sep at delta-alpha = 0.001 in [1.5, 3.0] — detectable but marginal; the spectral-MAC tamper-detection use case requires the lower delta-alpha range; falls back to delta-alpha = 0.005 as the production threshold.

### Anchor / cost

- Anchor name: `kappa3_sensitivity_sweep_n32768`.
- Cell construction: 5 delta-alpha perturbation levels, 5 seeds per level, single Hutchinson estimator with 5000 complex probes. ONE substrate construction at N=32768; multiple kappa_3 measurements via the same probe set.
- Marginal cost over current Cell 2: ~10-15 min added to the bundle (the perturbations are deterministic shifts; Hutchinson reuses probe set).

### Product unlock if HARD-PASS

- **kappa_3 spectral-MAC operates at 0.1% drift detection at production N** — substantially upgrades the spectral-tamper-evidence primitive from Phase-2's 4.2% sensitivity.
- Cap_map sub-property: extends PP-44b (kappa_3 monitor latency, just confirmed) to a sensitivity-vs-threshold curve at production N.

---

## 3. ADD-3 — PP-12 L=2 cross-layer composition at N=32768

### Capability question

At N=32768, does p=3-outer / p=2-inner L=2 composition deliver per-level fidelity ≥ 0.95 and confirm the 5.7B addressable-pair envelope at production scale?

### Algebraic basis

PP-12 LIFTED at v333 cap_map (L=2 cross-layer sub-property confirmed at production scale at smaller N). Phase-2 drill predicted per-level fidelity at p=3-outer ≈ 0.93-0.97 due to squared-inner-product crosstalk suppression. At N=32768 the SNR formula gives marginal gain via reduced finite-N corrections; per-level fidelity should NOT degrade vs N=8192.

Addressable-pair envelope claim from Phase-2: 5.7×10⁹ at N=8192. At N=32768 the capacity formula M_c(p=3) ≈ N²/(6·ln N) gives ~3.5×10⁷ outer slots vs N=8192's 1.24×10⁶ — a 28x envelope expansion. Addressable pairs scale as M_outer × M_inner, so the envelope at N=32768 is potentially ~6×10¹⁰ (if both layers scale).

### Pre-registered bands

**HARD-PASS:**
- Per-level fidelity ≥ 0.95 at N=32768 across 5 seeds, evaluated on 10K randomly-sampled test pairs
- End-to-end L=2 fidelity ≥ 0.90 across 5 seeds
- Outer-layer capacity sweep confirms ≥ 1×10⁷ usable outer slots before 90% accuracy cliff

**HARD-FAIL:**
- Per-level fidelity < 0.85 (squared-inner-product crosstalk suppression fails at production N — unexpected, would force re-derivation)
- End-to-end L=2 fidelity < 0.75
- Outer-layer capacity cliff at M_outer ≤ 1.24×10⁶ (would mean N²/(6 ln N) capacity formula does not hold at N=32768)

**MIDDLE BAND:** per-level fidelity in [0.85, 0.95] OR L=2 in [0.75, 0.90] — capability survives but finite-N or Kerdock-residual corrections are present; re-run at N=16384 for scaling fit.

### Anchor / cost — STORAGE BUDGET FLAG

- Anchor name: `pp12_l2_xlayer_n32768`.
- **Storage budget concern:** at N=32768 with float32, each pattern is 128 KB. A test pair (concept + pointer + chain + instance) at L=2 needs 4 patterns ≈ 512 KB per pair. For a sweep over 10K test pairs: ~5.1 GB working memory. Plus the outer-layer W tensor at p=3 implicit storage: O(M_outer × N) = 1.24×10⁶ × 128 KB ≈ 159 GB — **DOES NOT FIT in a single A100 80 GB instance.**
- **Resolution:** restrict the test to M_outer ≈ 5×10⁵ outer patterns (storage ≈ 64 GB, fits A100 80 GB with headroom), or use INT8 quantization at M_outer = 1×10⁶ (storage ≈ 128 GB INT4 = 64 GB INT8 — still tight). **Strategy + exp_dev resolve the exact M_outer.**
- Alternative: restrict ADD-3 to a fixed M_outer = 5×10⁵ at N=32768 with 5×10⁵ inner slots → 2.5×10¹¹ addressable pairs (still a 44x envelope expansion over N=8192). Less ambitious but production-tractable.
- Estimated cloud instance wall: ~1-2 hr added IF storage budget resolves to ~5×10⁵ outer slots. If storage budget forces deferral, ADD-3 should be DROPPED from this cloud bundle and the routing should be amended.

### Product unlock if HARD-PASS

- **5.7B addressable-pair envelope confirmed at production scale** — this is the entire substrate-capacity moat for compositional retrieval.
- Cap_map sub-property: PP-12-extended to N=32768.
- Combined with COMBO-2 (p=4 + L3 + signed-AM) Wave 4 results, this anchors the **negative-knowledge tree at L=3 + capacity envelope at production N** story.

---

## 4. AMENDED CLOUD BUNDLE COMPOSITION

```
unified_n32768_v1 (single instance, single bootstrap):

  Cell 1: Q-D1 spectral primitives at N=32768
          (sigma_TW measurement; cross-ref to N=8192 for N^(-2/3) validation)
  
  Cell 2 [REFINED via ADD-2]: kappa_4 / kappa_6 fingerprint extraction
          WITH refined delta-alpha sensitivity sweep
          {0.0001, 0.001, 0.01, 0.04, 0.1}
  
  Cell 3: Deletion-cert Z-ratio at N=32768 (uses bare rank-1 subtraction,
          unaffected by COMBO-1 v2 HP3+HP4 failure)
  
  Cell 4: COMBO-3 unified-API smoke at N=32768
          (validates 5-method API algebraic theorem at production scale)
  
  Cell 6 [NEW via ADD-1]: heteroassociative chain depth-5 + depth-10
          at N=32768, ONE chain construction, multiple readout depths
  
  Cell 7 [NEW via ADD-3]: PP-12 L=2 cross-layer composition at N=32768
          STORAGE BUDGET: strategy + exp_dev resolve M_outer
          (recommend M_outer ≈ 5×10^5 for 80 GB A100 fit)
          IF storage budget forces deferral, DROP from bundle
  
  DEFERRED: Cell 5 (COMBO-1 implicit Gram-solve) — pending v3
```

### Bundle economics

- Wall time: ~6-10 hr (Cells 1-4) + ~30-60 min (Cell 6) + ~10-15 min (Cell 2 ADD-2 refinement) + ~1-2 hr (Cell 7 IF storage allows)
- **Total: ~7-12 hr single instance.** Single bootstrap, single model load.
- **Cost estimate: ~$11-18** at A100 ~$1.50/hr. No doubling of bootstrap cost.

### Pre-dispatch checks (strategy / exp_dev to confirm before launching)

1. **Storage budget for Cell 7** — confirm M_outer fits A100 80 GB with all other cells loaded simultaneously. If tight, defer Cell 7 to a separate cloud batch later.
2. **Probe-set reuse** — Cell 2 ADD-2 refinement should reuse the same Hutchinson probe set across delta-alpha levels to keep per-cell cost minimal.
3. **Single-bootstrap commit** — per `feedback_batch_cloud_experiments`, do NOT split this bundle across two cloud instances.
4. **Pre-register HARD bands per cell** explicitly in the launch script.

---

## 5. DISCIPLINE DECLARATIONS

- Capability questions only; HARD/MIDDLE/FAIL bands pre-registered. Cell design (anchor names full form, sweep grids, queue, timeout) resolved by strategy + exp_dev.
- Pre-PROT-018 `_n<N>` binding contract: all 3 new cells embed `_n32768` in anchor.
- ASCII-only print; per-experiment `--timeout` required; verbose tracing if remote-dispatched.
- HARD-FAIL conditions explicit; MIDDLE BAND resolution paths specified.
- No padding: if storage budget forces Cell 7 deferral, drop it cleanly rather than padding with a smaller-scope variant.

---

## 6. WHAT THIS AMENDMENT DOES NOT TOUCH

- **Cell 5 (COMBO-1 implicit Gram-solve at N=32768) stays DEFERRED.** Awaits COMBO-1 v3 PASS at smaller N.
- **Real-time learning Features #6-9 product demos at N=32768** stay gated on Wave 4 Streaming Predictions 2-4 completing first.
- **PP-47 hippocampal place-field at N=32768** — not in this bundle; awaits clarification on what test produced PP-47 and whether N=32768 extension is informative.
- **alpha^(p-1) audit-sensitivity scaling test** — depends on COMBO-1 v3 PASS first.

---

**END OF AMENDMENT.** Orchestrator: fold ADD-1 + ADD-2 + ADD-3 into the Wave 5 cloud dispatch IF storage budget for ADD-3 resolves to single-instance fit. Strategy + exp_dev: resolve cell design from capability questions + HARD bands. Single cloud bootstrap, ~$11-18 total.

Acted-on 2026-06-02: amendment ADD-1+ADD-2+ADD-3 routed to testbed via handoff update; testbed executed cloud bundle ($3.81 actual vs $11-18 estimate)
