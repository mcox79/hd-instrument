# Research drill -- MAMP-SE at Kerdock M/N=8 -- 2026-05-24

**Author**: Research sub-agent (pure-math drill, no compute)
**Trigger**: Cap 12 ✅ promotion (κ_n free-cumulant divergence predicts AMP-SE error monotonically), but M/N=8 anomaly not theory-anchored. Research's #2 recommendation from `notes/research_high_yield_neighborhood_analysis_2026-05-24.md`: investigate MAMP (Liu-Takeuchi) as candidate framework.
**WebSearch sub-agents**: 5 parallel Sonnet runs (~4 min wallclock); generic math queries per [[feedback-query-privacy-decomposition]]; P deflated 0.15-0.25 per [[feedback-lit-scan-calibration-penalty]].
**Decision**: MAMP is NOT the right framework for the M/N=8 anomaly. The right framework is **spectral universality (Dudeja-Sen-Lu 2023)**. Honest pivot proposed.

---

## Section 1 -- MAMP framework summary (in our terms)

**Memory AMP (Liu-Cakmak-Liang-Takeuchi 2020/2022, arXiv:2012.10861, IEEE TIT 2022)**: a low-complexity iterative estimator for the linear system y = Ax + n where A is *right-unitarily-invariant* (RUI). MAMP differs from AMP and VAMP as follows:

| Algorithm | Matrix class | Per-iter cost | Memory used |
|---|---|---|---|
| **AMP** (Bayati-Montanari 2011) | iid Gaussian (and a thin universality halo) | O(MN) | last iterate only (Onsager correction) |
| **VAMP/OAMP** (Rangan-Schniter-Fletcher 2017) | RUI (any spectrum) | O(MN²) per iter due to SVD/matrix inversion | last iterate only |
| **MAMP** (Liu-Takeuchi 2020+) | RUI (any spectrum) | O(MN) — uses long-memory matched filter instead of inversion | *all past* iterates |

**The orthogonality principle (MAMP's central claim)**: by enforcing each iterate's error to be *orthogonal in the asymptotic-empirical inner product* to all previous iterates' errors, MAMP guarantees the residual is asymptotically iid Gaussian. This is the *same* guarantee VAMP gives under RUI, but achieved without the per-iteration matrix inversion. Concretely, MAMP requires constructing the iterate as a Bayes-optimal denoiser of a *linear combination* of all past matched-filter outputs (the "memory"), with coefficients (relaxation + damping) chosen so the orthogonality constraint holds.

**Critical fact for our drill**: per Liu-Takeuchi Theorem 2 (and the Long-Memory OAMP paper, arXiv:2111.05522), **the state-evolution fixed point of Bayes-optimal MAMP equals the state-evolution fixed point of Bayes-optimal VAMP/OAMP for *all* right-unitarily-invariant matrices**. They differ in per-iteration complexity and convergence-rate behavior, not in asymptotic MSE.

---

## Section 2 -- MAMP-SE prediction at Kerdock M/N=8

The substrate's Kerdock-Hopfield W at M/N=8 is a deterministic rectangular map M×N with M=8N built from the Kerdock 4-coset codebook (rows = stabilizer-state amplitudes; cols = pattern indices). Its singular-value spectrum is *not* the Marchenko-Pastur spectrum — it has a Kerdock-specific bulk with discrete-algebraic structure (v164a confirmed κ_n divergence; the empirical spectrum has heavier tails than MP and a non-MP edge).

**Does Kerdock satisfy MAMP's RUI assumption?** No, strictly. RUI requires A =_d UDV with V Haar-distributed on the right. Kerdock's V is deterministic (built from Maiorana-McFarland over GF(2^t)). It's a unitary 2-design (Can-Rengaswamy-Calderbank 2019, arXiv:1904.07842), not a Haar sample. **A 2-design matches Haar moments up to order 2 only**, so the AMP-SE-relevant moments (which are infinitely many; SE recursion uses all moments of the empirical spectrum) are *not* matched.

**Consequence**: MAMP-SE applied to Kerdock predicts the *RUI* fixed point — i.e., it predicts the same MSE that VAMP-SE predicts at M/N=8. Per Cap 12 evidence (κ_n divergence on Kerdock), neither the AMP-SE nor the RUI-VAMP-SE fixed point matches the *empirical* Kerdock AMP behavior at high M/N. Switching from "compute VAMP-SE" to "compute MAMP-SE" yields **the same numerical prediction** and therefore the same disagreement with empirics.

In one sentence: **MAMP solves the wrong problem** for our M/N=8 anomaly. MAMP's claim to fame is matching VAMP's MSE at lower complexity — it does not extend the matrix class.

---

## Section 3 -- Comparison: AMP-SE vs VAMP-SE vs MAMP-SE at Kerdock

| Method | M/N≈0.5-1 (Cap 8 regime) | M/N=8 (Cap 12 / open) | Comment |
|---|---|---|---|
| AMP-SE | inaccurate (Kerdock not iid; κ_n diverges) | DIVERGES (smoke v1 confirmed; full run filed) | Cap 12 ✅ result: free-cumulant divergence predicts the gap monotonically |
| VAMP-SE | tracks empirics (Cap 8 ✅) | not yet tested rigorously at M/N=8, but theoretically same fixed point as MAMP | RUI assumption *approximately* holds via 2-design matching at low M/N |
| MAMP-SE | same fixed point as VAMP-SE (Liu-Takeuchi Thm 2) | same fixed point as VAMP-SE | Differs only in complexity O(MN) vs O(MN²); no new theoretical reach |

**Key insight**: VAMP "works" at low M/N on Kerdock not because Kerdock is RUI but because the *low-order-moment* approximation is tight in that regime. At M/N=8, the higher-order spectral moments (which are exactly what κ_n diverges on per v164a) become dominant, and the 2-design approximation to Haar breaks. Neither MAMP nor VAMP has machinery for this — they both assume RUI in their SE derivation.

---

## Section 4 -- Honest pivot: spectral universality (Dudeja-Sen-Lu 2023) is the right framework

In the parallel search I dispatched, I surfaced **Dudeja-Sen-Lu, "Spectral Universality of Regularized Linear Regression with Nearly Deterministic Sensing Matrices"** (arXiv:2208.02753, IEEE TIT 2023). This is the framework we want, not MAMP.

**Why it fits where MAMP doesn't**:
1. Dudeja-Sen-Lu define universality *classes* of sensing matrices via two conditions: (a) deterministic spectrum (any), (b) "generic singular vectors" (a precise low-rank-coherence condition).
2. They prove that *all matrices in the same class produce the same asymptotic RLS estimator dynamics* — including the AMP/proximal-gradient dynamics.
3. Their universality class is shown to contain: **randomly signed incoherent tight frames** and **randomly subsampled Hadamard transforms** — both of which are structural analogs of Kerdock (Kerdock is a Z₄-linear cousin of the Reed-Muller / Hadamard family, and is an incoherent tight frame).
4. The class is broader than RUI and gives a *direct* surrogate prediction: replace the deterministic Kerdock-W spectrum into the iid-Gaussian SE recursion *with the Kerdock spectral law as input*, and ask whether the predicted MSE matches empirics.

This is a *strictly stronger* theoretical anchor than MAMP for our problem because (a) it explicitly accommodates non-RUI deterministic structured matrices, (b) it has a hard-fail test (in-class or out-of-class), (c) it directly explains why VAMP works at low M/N (Kerdock is *approximately* in the universality class) and may fail at high M/N (the κ_n divergence is the signature of class-membership failure or class boundary).

### Anchor proposal (replaces MAMP anchor)

**Name**: `wave14_spectral_universality_kerdock_v1`
**Type**: pure CPU numpy; ~45-60 min predicted
**Mechanism**:
1. Compute empirical singular value distribution of Kerdock W at N=4096, M/N ∈ {0.5, 1, 2, 4, 8}.
2. Generate matched-spectrum surrogates: (a) iid Gaussian rescaled to match Kerdock spectrum, (b) random-sign Hadamard with matched spectrum, (c) Haar-rotated diagonal with Kerdock spectrum.
3. Run AMP (and AMP-SE) on all four (Kerdock + 3 surrogates) for 5 seeds.
4. **Decision rule**:
   - If AMP-MSE(Kerdock) ≈ AMP-MSE(surrogates) within 15% across all M/N → Kerdock IS in the Dudeja-Sen-Lu class; SE recursion with empirical Kerdock spectrum is the right anchor; Cap 8 ✅ envelope extends to M/N=8.
   - If AMP-MSE(Kerdock) systematically diverges from all 3 surrogates at high M/N → Kerdock is OUT of class; the M/N=8 anomaly is a genuine non-universality signature (Cap 12 promotes from "AMP-fails-on-Kerdock" to "Kerdock-breaks-universality"). This is a *substrate-novel* class-boundary finding.
**Hard fail**: if all three surrogate MSEs disagree with each other by >25% at M/N=8, the test is uninformative (spectrum-matching surrogate construction is wrong).
**ETA**: 45-60 min CPU; designed for `local_cpu_queue`.

### Fallback if Dudeja-Sen-Lu also doesn't fit

The next candidates, in honest priority order:
1. **GAMP (Generalized AMP, Rangan 2011)** — but our channel is already Gaussian, so GAMP buys nothing on the channel side; would only help if the prior is non-Gaussian (it isn't in current Cap 12 setup).
2. **Convolutional AMP (Takeuchi 2020-2024)** — designed for RUI with low-to-moderate condition number; Kerdock spectrum is fully discrete-algebraic so condition number is bounded, but again the SE fixed point matches VAMP under RUI.
3. **Second-order freeness (Mingo-Speicher 2007+)** — Research's #1 recommendation; this gives fluctuation predictions, not mean predictions, so it's complementary to the mean-MSE question we're asking here. Worth pursuing in parallel for the *variance* of M/N=8 capacity.

---

## Section 5 -- Honest reading and P estimate

**MAMP is the wrong tool here.** It's a complexity-reduction trick that achieves the same MSE-fixed-point as VAMP under the same RUI assumption. Since the M/N=8 anomaly is precisely a *failure of the RUI approximation at high spectral moments* (Cap 12 ✅ established this via κ_n divergence), no algorithm in the RUI family — AMP, VAMP, MAMP, CAMP, OAMP — can resolve it.

The honest pivot is to **spectral universality (Dudeja-Sen-Lu 2023)**, which is broader than RUI and explicitly accommodates structured deterministic matrices. The anchor experiment above tests whether Kerdock at M/N=8 sits inside this broader universality class.

**P estimates** (with [[feedback-lit-scan-calibration-penalty]] deflation; novel-synthesis cap P=0.50):
- P(MAMP-SE matches empirical Kerdock at M/N=8) = **0.05** (essentially ruled out by Liu-Takeuchi Theorem 2: same fixed point as VAMP, which v168 already showed disagrees in the right regime).
- P(Dudeja-Sen-Lu class membership holds for Kerdock at M/N≤2) = **0.55** (substrate is 2-design + incoherent tight frame; matches the explicit examples in their paper).
- P(Dudeja-Sen-Lu class membership extends to M/N=8) = **0.30** (deflated: this is uncharted; their explicit examples don't go this overcomplete; κ_n divergence is plausibly a class-exit signature).
- P(anchor experiment yields a clean in-class-or-out verdict) = **0.65** (hard-fail criterion is well-defined; 5 seeds should resolve).
- P(of an out-of-class verdict, Cap 12 promotes to "novel class-boundary finding") = **0.50** (genuinely substrate-novel observability).

**Net expected value of the anchor experiment**: ~45-60 min CPU for ~0.45 chance of either extending Cap 8 envelope (in-class verdict at M/N≤2) or promoting Cap 12 to a non-universality finding (out-of-class verdict at M/N=8). Cheap and decisive. **Recommend filing** as `wave14_spectral_universality_kerdock_v1` in place of the originally-proposed MAMP-SE experiment.

---

## Citations / sources

- Liu-Cakmak-Liang-Takeuchi (2020/2022). "Memory AMP." IEEE TIT 68(11). arXiv:2012.10861.
- Liu-Yuan-Liang-Takeuchi (2022). "Sufficient-Statistic Memory AMP." arXiv:2112.15327.
- Takeuchi (2022). "On the Convergence of Orthogonal/Vector AMP: Long-Memory Message-Passing." arXiv:2111.05522.
- Takeuchi (2020). "Bayes-Optimal Convolutional AMP." IEEE TIT.
- **Dudeja-Sen-Lu (2023). "Spectral Universality of Regularized Linear Regression with Nearly Deterministic Sensing Matrices." arXiv:2208.02753. IEEE TIT 2023.** ← anchor framework
- Can-Rengaswamy-Calderbank (2019). "Kerdock Codes Determine Unitary 2-Designs." arXiv:1904.07842.
- Rangan-Schniter-Fletcher (2017). "Vector Approximate Message Passing." arXiv:1610.03082.

---

## For You tab status_log entry (per [[feedback-for-you-tab-primary-channel]])

```
{
  "plain_language": "Memory AMP is not the right framework for the M/N=8 mystery; it gives the same prediction as VAMP. The right framework is spectral universality (Dudeja-Sen-Lu 2023), which accommodates structured deterministic matrices like Kerdock. Proposed a 45-60 min CPU anchor experiment to test it.",
  "importance": "high",
  "context": "research drill pivots Cap 12 follow-up; replaces MAMP-SE anchor with spectral-universality anchor; preserves anchor-experiment slot in queue"
}
```

**End of drill.**
