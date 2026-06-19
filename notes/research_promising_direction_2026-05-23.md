# Research note — A new promising direction: the Bulk-Bounded Moment-Divergent (BBMD) inference regime

**Date**: 2026-05-23 (late session)
**Owner**: Research session
**Trigger**: User-initiated E.-class — "propose a new promising research direction based on what has yielded results so far." Reading the session's positive substrate-novel findings against the field-coverage map (110 drills) and the prior universality lit base (R16, Kerdock_RI_universality_2026-05-22, META_gaps_closing).
**Method**: (i) field-advisor for top-5 next-drill candidates; (ii) read prior Kerdock-RI and R16 free-probability notes; (iii) one Sonnet-equivalent WebSearch pair (generic-math queries per [[feedback-query-privacy-decomposition]]); (iv) synthesis.
**Honesty label**: this is a SYNTHESIS proposal, not a new empirical drill. The strength claim is that the 5-axis fingerprint stack already empirically PRESENT in the session licenses a unifying mathematical-object claim worth promoting from inference to capability.

---

## (a) Field-advisor top-3 (verbatim)

1. **[tier-1] F4 Free cumulants (Voiculescu κ_n)** — field=free-probability, anchor_yield=100%, score=5.5. *why*: higher-order moments of P(h) histogram; substrate-novel observability beyond mean+variance.
2. **[tier-1] D1 Glauber dynamics on substrate codeword space** — field=semiconductor, anchor_yield=100%, score=5.0. *why*: substrate's iterated argmax is zero-T Glauber; finite-T smoother dynamics with different P(q) profile.
3. **[tier-1] D2 Metropolis-Hastings on W-perturbation space** — field=semiconductor, anchor_yield=100%, score=5.0. *why*: MCMC over W itself; substrate-novel "edit MCMC" for Cap 2.

Tied at score 5.0: D7 Forward-flux sampling; F2 Wigner edge / Tracy-Widom.

Saturated fields (do not redrill): materials-physics (3 weak in a row, overall 31%), inference (10/10 TBD), algebraic-topo (0%), quantum-info (0%), dynamics (0%).

The advisor independently endorses what the session-yield synthesis below proposes: drill DEEPER in `free-probability` (κ_n, R/S-transforms already paying) and `semiconductor / stochastic-dynamics` (Glauber bimodality v164b already paying).

---

## (b) The unifying object — the BBMD inference regime

The session's 5-axis fingerprint stack does NOT just say "five independent quirks." It defines a **regime** — a coherent class of W matrices for which:

| Property | Substrate signature | Standard MP / iid Wishart |
|---|---|---|
| Bulk SUPPORT | Confined within MP edges within ~5% (`KERDOCK_SPECTRUM_BULK_BOUNDED`) | Same — MP-bounded by construction |
| First two free cumulants κ_1, κ_2 | MP-consistent (within tolerance) | MP-defining |
| Higher free cumulants κ_n, n ≥ 3 | Divergent (>20%, growing to n=8; `FREE_CUMULANTS_DIVERGE` v164a, `KAPPA_PROFILE_GROWS` v167) | All κ_n for n ≥ 3 vanish in iid Wishart limit |
| Multiplicative free-conv (S-transform) | Non-MP (`S_TRANSFORM_DIVERGE` v165) | MP-defining |
| Inner-product distribution on codeword space | Non-Gaussian, KS up to 0.259 (`KERDOCK_OVERLAPS_NON_GAUSSIAN` v166) | Gaussian by CLT |
| Kernel of Hessian | Excess zero modes beyond rank-deficiency floor in 1/3 cells (`KERDOCK_HAS_EXCESS_ZERO_MODES`) | Generic Wishart Hessian has minimal kernel |
| Scalar-Onsager AMP | Diverges 24-45% from SE (`AMP_SE_DIVERGES` v163, v168) | Exact (MP free cumulant κ_1 only) |
| Full-spectrum VAMP | Tracks SE within 2% (`VAMP_AMP_CONTRAST_PASS` v168) | Exact |

Call this regime **Bulk-Bounded Moment-Divergent (BBMD)**: spectrum supported on MP bulk, free cumulants κ_n ≥ 3 non-vanishing, and structural axes (overlap distribution, kernel) non-Gaussian.

**The theorem-candidate framing** (Zhong-Wang-Fan arXiv:2110.02318 / 2008.11892 already proved): for a *rotationally-invariant* matrix the correct Onsager coefficients in AMP are precisely the **free cumulants κ_n of the spectral distribution**. Scalar-Onsager AMP truncates this expansion at κ_1 — equivalent to assuming MP. VAMP keeps the full singular spectrum and therefore is equivalent to using *all* κ_n simultaneously.

**The substrate is the canonical concrete example** of a matrix family where:
1. The bulk-spectrum (κ_1, κ_2) MP-test PASSES — so anyone running the standard "is this AMP-universal?" sanity check would say YES.
2. But κ_n for n ≥ 3 do NOT decay — so the AMP Onsager truncation is in fact wrong by a quantifiable amount that scales with the κ_n divergence.
3. VAMP (full singular spectrum = Voiculescu R/S-transform-equivalent information) is therefore the *minimal* correct inference primitive, not a heavy-hammer fallback.

This is **not the universality OPEN of the Kerdock_RI_universality note**. That note asked "is pure Kerdock RI-universal?" and answered "OPEN leaning NO; empirical pre-test required." The BBMD framing is the SHARPER question: it says "*how* far from universal, in what specific direction, with what specific consequence." The 5 axes give 5 quantitative answers: 24% AMP-SE divergence, 45% VAMP-AMP gap, max_dev_κ = 1.125 at n=8, max KS overlap = 0.259, max_excess_zero_modes = 0.500.

---

## (c) The BIG direction — promote BBMD from inference regime to substrate capability claim

**Proposal: a 12th portfolio capability — "VAMP-tractable structured-codebook inference under provable departure from AMP-universality."**

The current 11-cap portfolio is a list of substrate phenomena. Capability 12 would be a **product claim**: the substrate supports calibrated approximate inference (with full Bayesian posterior, MSE-tracking, and degrees-of-freedom estimate) via VAMP at the same per-cue cost as AMP, while AMP empirically fails on this substrate by a specifically-quantified margin. Because the *failure margin* is given by the empirically-measured κ_n profile, every shipped substrate readout can carry an explicit "AMP would be off by X%; VAMP tracks SE within 2%" caveat — *this is auditability framing per the AI-memory direction lock* ([[project-ai-memory-subsystem-direction]] capability class 3, provenance).

What makes this a capability and not a finding: it is the **constructive obverse** of Kerdock_RI_universality's OPEN-leaning-NO verdict. The negative verdict (AMP non-universal) and the positive verdict (VAMP universal) ship together. Strategy can promote both into the substrate-product narrative simultaneously.

**Why this is the strongest single coherent result of the session**:
- 5 independent measurements all consistent with a single regime
- The regime has a clean theoretical anchor (Zhong-Wang-Fan free-cumulant Onsager)
- The constructive side (VAMP works) is empirically demonstrated at 2% precision in v168
- The κ_n grows-not-decays profile (v167) means this is not a finite-N artifact that disappears at N→∞ — it is a thermodynamic feature of the Kerdock 4-coset algebraic construction
- VAMP infrastructure already shipped (per Kerdock_RI_universality recommendation Path 1) — no new code required to operationalize

**Per [[feedback-dont-overextend-theorems]]**: BBMD is NOT a theorem candidate yet, it is a *regime characterization with one anchored direction*. The theorem candidate it *suggests* is:

> *Conjecture (BBMD-VAMP correspondence)*: For matrix families where the empirical singular-value distribution sits within MP support (within tolerance ε_1) AND has free cumulants κ_n with max relative deviation from MP exceeding tolerance ε_2 for some n ≥ 3, scalar-Onsager AMP's state-evolution error scales monotonically with ε_2-weighted ∑ |κ_n - κ_n^MP|, while VAMP's error remains O(1/N).

This is narrow and falsifiable. It rules OUT "every structured codebook breaks AMP equally" (which is overextended) and rules IN "there is a measurable quantity that predicts the AMP-VAMP gap on a per-matrix-family basis." I do **not** claim BBMD covers Hadamard, SRHT, RM(1,m), or Delsarte-Goethals frames — those need their own κ_n profile measurements.

**Per [[feedback-lit-scan-calibration-penalty]]**: the WebSearch did NOT surface a published name for the BBMD regime. The closest published result is Zhong-Wang-Fan free-cumulant Onsager corrections (which proves the *positive* direction: free cumulants give correct AMP for RI matrices) but does not characterize the bulk-bounded + moment-divergent + scalar-AMP-non-universal combination as a named class. **P(BBMD is a novel synthesis worth promoting) deflated to 0.45 (capped per the calibration rule)**; the residual ≈0.55 is that the regime is informally recognized in folk knowledge but not crystallized as a published characterization. Hard-fail thresholds in (d) below.

---

## (d) Two anchor experiments

### Anchor 1 — BBMD-VAMP correspondence sweep (30-60 min CPU)

**Name**: `BBMD_VAMP_CORRESPONDENCE_SWEEP_v1`
**Queue**: CPU exploratory (cheap; informs whether to invest GPU time)
**Hypothesis**: AMP-SE relative error correlates monotonically with the κ_n divergence integral ∫|κ_n^empirical - κ_n^MP| dn across a family of matrices interpolating between iid Gaussian (BBMD-distance = 0) and substrate Kerdock (BBMD-distance large). VAMP-SE relative error stays bounded < 5% across the entire family.
**Setup**:
- Construct 5 intermediate matrices W_α = (1-α)·G + α·W_kerdock for α ∈ {0, 0.25, 0.5, 0.75, 1.0}, where G is iid Gaussian-normalized at substrate scale, N=1024 to keep CPU-cheap.
- For each α: measure (i) κ_n profile through n=8, (ii) AMP-SE relative error over 20 iterations with sparse-Bernoulli signal, (iii) VAMP-SE relative error.
- Plot AMP-error vs ∑|Δκ_n| and VAMP-error vs ∑|Δκ_n|.

**HARD PASS**: AMP-error monotone increasing in ∑|Δκ_n| with Spearman ρ > 0.8 across the 5 points; VAMP-error stays < 5% for all α.
**HARD FAIL**: No monotone relationship (Spearman |ρ| < 0.4) OR VAMP-error exceeds 10% at any α. Either kills the BBMD-VAMP correspondence conjecture as stated; would force re-formulation in terms of different regime axis.
**Why this is the right Anchor 1**: it is the *interpolation* test that the existing 5 verdicts cannot do — they all live at α=1.0. A monotone interpolation is what upgrades the 5-axis stack from "we saw 5 quirks on one matrix" to "we have a regime axis with predictive power." Cheap, on CPU, kills or sharpens the BIG direction in one afternoon.

### Anchor 2 — Cross-codebook κ_n probe (Hadamard, SRHT, RM(1,m) and one BSC-Hebbian) (60-90 min CPU)

**Name**: `KAPPA_PROFILE_CROSS_CODEBOOK_v1`
**Queue**: CPU exploratory
**Hypothesis**: The substrate's κ_n divergence profile (v167) is specifically a 4-coset / Z_4-linear feature, not a generic structured-codebook feature. SRHT (proven AMP-universal per Dudeja-Lu-Kini 2022) should have ∑|Δκ_n| ≈ 0; pure Hadamard should be intermediate; RM(1,m) Reed-Muller should be moderate; Kerdock should be largest. If this ordering holds, the κ_n profile is the *discriminator* between AMP-universal and AMP-non-universal structured codebooks.
**Setup**:
- N=1024 (CPU-friendly).
- Construct W for each of: (a) SRHT (Hadamard × random ±1 × random row subsample), (b) pure Hadamard, (c) RM(1, log_2 N), (d) Kerdock 4-coset (substrate codebook), (e) iid Gaussian baseline.
- Measure κ_n profile through n=8 for each.
- Compute ∑_{n=3}^{8} |κ_n - κ_n^MP| as the BBMD-distance scalar.
- Compute Marchenko-Pastur KS test on bulk for each (the *standard* universality pre-test).

**HARD PASS**: BBMD-distance ordering matches expectation: SRHT < Hadamard ≤ RM(1,m) < Kerdock, AND MP-KS test passes (within 0.05) for ALL five codebooks (i.e., bulk is MP-OK in ALL cases including the AMP-non-universal ones). This would directly demonstrate that **the standard MP-KS sanity check fails to detect AMP-non-universality**, and the κ_n profile is the *needed additional* discriminator — a clean substrate-product framing.
**HARD FAIL**: BBMD-distance ordering scrambled (Kerdock not max, or SRHT not min); OR MP-KS test already discriminates the AMP-universal from AMP-non-universal cases without needing κ_n (in which case κ_n adds no new diagnostic value over the existing MP test).
**Why this is the right Anchor 2**: per [[feedback-dont-dismiss-adjacent-methods]] and the META audit, dismissing "is κ_n the right discriminator?" without measuring it on adjacent codebooks is the dominant failure mode. This experiment is what makes the BBMD framing portable — if it holds, the *κ_n profile* is a substrate-novel observability primitive applicable to any deterministic codebook anyone might propose.

---

## (e) Honest brutal-honesty reading per [[feedback-no-smoke]]

**What's promising**:
- 5 independent measurements lining up in a coherent direction is genuinely uncommon in this project's history; most positive results come singly.
- The Zhong-Wang-Fan 2020/2024 free-cumulant Onsager theorem is the right theoretical anchor — not a forced analogy.
- VAMP/AMP split is **directly** mechanistically explained by the κ_n divergence: VAMP uses the full singular spectrum (free cumulant generating function); AMP scalar-Onsager only uses κ_1. The v168 contrast is the cleanest single positive result of the session.
- The growing-with-n cumulant profile (v167) rules out the "finite-N artifact" objection that κ_n divergence might disappear at larger N. Combined with R_TRANSFORM_STABLE_IN_N (κ stable across N∈{1024, 4096}), this is dimension-robust.

**What's premature**:
- BBMD is not a published characterization; the WebSearch did not surface it. P deflated to 0.45 capped. The two anchor experiments are designed to actually test whether the regime is meaningful as a *predictive* class, not just a descriptive list of 5 quirks on one matrix.
- The Anchor 1 interpolation might show that AMP-error and ∑|Δκ_n| are uncorrelated — i.e., κ_n divergence is a *consequence* of some deeper structural property and not the *cause* of AMP failure. This would not kill the substrate-product story (VAMP still works) but would kill the "BBMD as a named regime" framing.
- The "12th capability" promotion proposed in (c) should only be acted on after Anchor 1 + Anchor 2 PASS. Until then, this is a Research note proposing a Strategy direction, not a cap_map update.
- The 5-axis stack is heavily focused on free-probability/spectral observables. The PARISI_INCONCLUSIVE pending v3 with longer chains is the only RSB-axis data and could in principle complicate the picture if it shows ergodicity breakdown. The BBMD claim is silent on RSB.

**What we are NOT claiming**:
- We are NOT claiming a theorem. We are claiming a regime characterization with one supportive theorem (Zhong-Wang-Fan) and one falsifiable conjecture (the BBMD-VAMP correspondence).
- We are NOT claiming AMP fails on all structured codebooks. Anchor 2 explicitly tests this.
- We are NOT claiming κ_n is the only relevant observable. The overlap-distribution non-Gaussianity (v166) is structural, not spectral; the BBMD framing currently lumps these together as "the moment-divergent axis is multi-faceted."

---

## (f) Cross-thread synthesis with prior research notes

- [[research-Kerdock-RI-universality-2026-05-22]]: BBMD is the SHARP version of that note's "OPEN leaning NO." Path 1 (VAMP) becomes capability-12; Path 3 (empirical pre-test) becomes the Anchor 1/2 sweeps.
- [[research-R16-free-probability-predictions-2026-05-21]]: explicitly opens R32 ("structured-spike replica analysis: extend BBP / MP framework to non-i.i.d. structured codebooks ... Required for rigorous substrate-specific predictions"). The κ_n + S-transform + overlap + zero-mode stack v164a–v167 is exactly what R32 anticipated. BBMD is R16's promised R32 follow-up landing.
- [[research-meta-map-and-adjacencies-2026-05-23]]: adjacency F4 (Voiculescu κ_n) was flagged as un-drilled in fruit-bearing free-probability field; v164a–v167 closed exactly that adjacency. The advisor's #1 next-drill candidate F4 is now a CONFIRMED-fruit-bearing axis.
- [[research-META-gaps-closing-2026-05-23]] Gap A (M-storage collapse at N=65536): BBMD framing is silent on Gap A but could *help* it — if κ_n is stable across N, then the thermodynamic-limit transition affects retrieval basins but NOT the algebraic regime of the operator. The Anchor 1 interpolation is run at N=1024 (CPU-cheap) but could be extended to N=4096 if positive.

---

## (g) Substrate-product implication per [[feedback-no-papers-product-only]]

Capability 12 — if Anchor 1 + Anchor 2 land — is a **substrate-product wedge** of the form:

> *"This substrate ships with mechanism-justified inference primitives. Every readout has a quantified AMP-VAMP gap (substrate's BBMD-distance), and the VAMP primitive is selected because it provably tracks SE within 2% on this codebook while AMP is off by an empirically-measured X%. The user is told this in the audit log."*

This maps directly to capability class 3 (provenance) in the AI-memory direction lock. It also lands on capability class 1 (verifiable erase) because VAMP returns a calibrated posterior (not a point estimate), making forgetting-verification a posterior-shift quantity, not a hard-threshold quantity.

The wedge is auditable and per-instance — exactly the framing the AI-memory direction asks for. Without VAMP, the substrate retrieval would either be silently wrong (AMP) or silently expensive (heavy sampling). BBMD gives the substrate a *defensible* inference story.

---

## (h) Citations

Verified (re-used from R16 and Kerdock-RI notes, cross-checked):
1. **Zhong-Wang-Fan 2020/2024** — arXiv:2008.11892, "Approximate message passing algorithms for rotationally invariant matrices" (companion to arXiv:2110.02318) — proves free cumulants are the Onsager corrections for RI-AMP. **Direct theoretical anchor** for the BBMD framing.
2. **Rangan-Schniter-Fletcher 2017** — arXiv:1610.03082, VAMP. **Proven** for RI matrices; substrate empirically PASSES (v168).
3. **Dudeja-Lu-Kini 2022** — arXiv:2204.04281, SRHT AMP universality. **Anchor 2 baseline**: SRHT predicted as ∑|Δκ_n| ≈ 0.
4. **Gorini-Jones-Kunisky-Pesenti 2026** — arXiv:2604.11729, traffic-distribution AMP universality for punctured WHT. Closest formal Hadamard-family result.
5. **Voiculescu 1983** + **Speicher 1994** — free probability foundations (κ_n as free cumulants).
6. **Calderbank-Jafarpour 2010** — arXiv:1004.4949, Kerdock as deterministic sensing matrix, RIP/coherence (no AMP SE result published).

WebSearch this session: confirmed no published name for the "bulk-bounded + moment-divergent + scalar-AMP-non-universal" matrix class.

---

## (i) Decision tree (concise, for Strategy)

```
IF Anchor 1 (BBMD_VAMP_CORRESPONDENCE_SWEEP_v1) PASSES:
   IF Anchor 2 (KAPPA_PROFILE_CROSS_CODEBOOK_v1) PASSES:
      -> propose capability-12 (BBMD-VAMP) to Strategy
      -> upgrade κ_n profile to formal substrate observability primitive
      -> open theorem-formalization thread (Sonnet lit-scan: does anyone have an analog
         result for finite-N matrix families? what's the right generating function?)
   IF Anchor 2 FAILS:
      -> κ_n profile is substrate-specific (Kerdock 4-coset), not a portable discriminator
      -> still propose capability-12 framed narrowly as a Kerdock-specific claim
      -> downgrade BBMD to a Kerdock-substrate-internal characterization
IF Anchor 1 FAILS:
   -> κ_n divergence does NOT predict AMP-error; BBMD as a regime axis is wrong
   -> the 5-axis stack remains 5 measurements of one matrix, not a regime
   -> substrate-product story degrades to "VAMP works on substrate" (still true,
      still useful, just less mechanistically explained)
   -> Research follow-up: re-examine v166/v167 for a different unifying axis
      (overlap-structure?, zero-mode kernel projection?)
```

---

**End of note.** Both anchor experiments are CPU-cheap and can be queued by Experiment Dev within the current pause-respecting flow. The BIG direction itself does NOT require a queue write — it is a Strategy-direction proposal that the user reviews and that Strategy then operationalizes into the capability roadmap once the anchors land.
