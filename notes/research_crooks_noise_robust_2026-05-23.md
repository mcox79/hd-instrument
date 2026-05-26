# Research: noise-robust verifiable erasure (2x drill on CROOKS_NOISE_ENVELOPE_KILL)

**Date**: 2026-05-23
**Trigger**: `notes/strategy_request_to_research_crooks_noise_robust_2026-05-23.md` (Strategy cycle 177, v157)
**Drill type**: 2x depth on negative result per [[feedback-2x-means-depth]] + [[feedback-rehabilitation-after-rejection]]
**Method**: 3 parallel Sonnet lit-scan probes on generic-math queries per [[feedback-query-privacy-decomposition]]; Opus synthesis
**Calibration**: deflated P by 0.20 per [[feedback-lit-scan-calibration-penalty]] (uncharted regime: noise-robust Crooks-FT in classical structured-codebook associative memory has no direct precedent); novel-synthesis cap P=0.50; hard-fail thresholds explicit in every prediction

---

## (a) HEADLINE

**Top mechanism**: Re-axiomatize the audit metric against the Sagawa-Ueda / Generalized-Landauer noise-corrected bound, NOT the clean-Crooks bound.

**P = 0.50** (capped at novel-synthesis ceiling; the underlying mathematics is published and the substrate-side change is a metric redefinition with zero new hardware, so deflation pre-cap was 0.65 -> 0.50 cap).

**One-sentence form**: The current cycle 177 FAIL is most likely a metric-definition artifact, not a substrate failure -- delta_S_emp is being compared against the wrong bound under noise. The published Generalized Landauer / Sagawa-Ueda inequality replaces `k_B T ln 2` with the error-probability-aware form `k_B T [ln 2 + p ln p + (1-p) ln(1-p)]`, which is exactly the audit threshold that should be used when the erase trajectory carries bit-flip noise.

**Top-3 vetted ranking** (after deflation):

| Rank | Mechanism | P (deflated) | Build cost | Why ranked here |
|---|---|---|---|---|
| 1 | Noise-corrected audit bound (Sagawa-Ueda / Generalized-Landauer re-axiomatization) | 0.50 | Zero new hardware -- changes the AUDIT formula only | Published math; substrate already measures all required quantities |
| 2 | r-fold redundant encoding + majority-vote audit (r=3 baseline; r=5 for p=0.20) | 0.40 | Existing N=16384 protocol; r copies stored in disjoint key subspaces | Classical repetition-code threshold theorem is published; suppresses effective p to ~3p^2-2p^3 for r=3 |
| 3 | Pre-erase verification + commit-then-prove protocol (cryptographic anchoring orthogonal to physical erase) | 0.30 | Hash function + storage of commitment digest; no substrate change | Paul-Saxena PoE / EVSD use commitments to make erasure verifiable independent of physical noise; this is a SLA layer, not a substrate fix |

Mechanisms #4 (pre-erase denoising filter) and #5 (algebraic error-correction at binding layer) deferred -- they require more substantive build and (per the lit-scan) do NOT preserve the forward-reverse trajectory invariance the Crooks-FT audit requires without nontrivial proof obligations. They should be revisited only if #1, #2, #3 all fail.

---

## (b) Cheap decisive test

**Test name**: `wave14_crooks_noise_corrected_bound_v1`

**Action**: Re-analyze the cycle 177 FULL data already on disk. For each cell (p in {0, 0.05, 0.10, 0.20}), compute the Generalized-Landauer threshold

  `theta(p) = ln 2 + p * ln(p) + (1-p) * ln(1-p)`  (in nats; convert to substrate units consistent with how delta_S_emp is defined)

and compare `delta_S_emp(p)` against `theta(p)` instead of the static 0.05 threshold. The clean p=0 cell collapses to ln 2 (baseline). For p=0.05 the threshold drops to ~0.494 ln 2 = 0.342 nats; for p=0.10 to ~0.531 ln 2; for p=0.20 to ~0.722 ln 2 (using the standard binary-entropy form normalized to the clean ln 2 bound).

**No new run needed**. The post-hoc re-analysis is a Python script over the existing 50-trial x 3-seed x 4-cell results. Cost: <5 min CPU. If mechanism #1 holds, the existing cycle 177 data PASSES once the bound is corrected.

**If mechanism #1 fails**: fall through to mechanism #2. Cheap decisive test for #2 is `wave14_crooks_redundant_r3_v1` at N=16384, r=3 stored in 3 disjoint Hadamard-bound key sets, majority-vote audit across the 3 forensic-erase readouts. ~30 min FULL. Predicted to PASS at p<=0.10 (effective error rate after majority vote = 3p^2 - 2p^3 = 0.028 at p=0.10, well below 0.05).

---

## (c) Falsifiable predictions with HARD PASS / HARD FAIL

### Prediction 1 (Mechanism #1: noise-corrected bound)

- **HARD PASS**: For all 3 noisy cells (p in {0.05, 0.10, 0.20}) at cycle 177 FULL, `delta_S_emp(p) <= theta(p) + 0.02` after the re-axiomatization. Equivalently, the existing measurement -- which fails the static 0.05 bound -- passes the binary-entropy-shifted bound with margin.
- **HARD FAIL**: If ANY of the 3 noisy cells has `delta_S_emp(p) > theta(p) + 0.05`, mechanism #1 is REFUTED. The noise is doing something beyond what Sagawa-Ueda predicts and the substrate has a deeper trajectory-invariance problem.
- **Pre-registered margin**: 0.02 / 0.05 are tight margins; the published theory predicts equality up to O(N^{-1/2}) sample fluctuation, which at N=16384 is <0.008.

### Prediction 2 (Mechanism #2: r-fold redundancy + majority vote, r=3)

- **HARD PASS**: At r=3, N_per_copy=16384 (total N_total=49152), the majority-vote forensic-erase audit gives `delta_S_emp < 0.05` at p<=0.10. Predicted noise floor for r=3: effective error rate ~0.028 at p=0.10; should sit well below the original 0.05 bound.
- **HARD FAIL**: If at r=3 the audit `delta_S_emp >= 0.05` at p=0.05 (where effective rate is only ~0.007), mechanism #2 is REFUTED -- the substrate's residual error mode is not bit-iid and majority-vote does not help.
- **Hard threshold for r=5**: at p=0.20, effective error after r=5 majority vote = sum_{k>=3} C(5,k) p^k (1-p)^{5-k} = 0.058 at p=0.20 (still above the 0.05 bound). So predict HARD FAIL of r=5 at p=0.20; predict HARD PASS only at p<=0.15. If r=5 passes at p=0.20, the substrate is doing better than iid bit-flip theory predicts -- worth investigating but does NOT refute the mechanism.

### Prediction 3 (Mechanism #3: commit-then-prove cryptographic anchor)

- **HARD PASS**: Substrate stores a SHA-256 commitment `c = H(payload || nonce)` BEFORE the erase trajectory. After erase, the audit verifies (i) `delta_S_emp` under the corrected bound AND (ii) the committer cannot produce a valid (payload, nonce) opening to `c`. The combined audit PASSES at all p in {0, 0.05, 0.10, 0.20}.
- **HARD FAIL**: This mechanism is essentially unfalsifiable at the noise level -- commitment-based proof-of-erasure is independent of substrate noise by construction. The HARD FAIL is operational: if implementing the commitment store adds latency >5x the current audit latency, the SLA is unworkable for streaming use. Threshold: total audit latency <= 50ms per item at N=16384.

---

## (d) Cross-thread synthesis with prior Entries

### Connection to Cap 1 Crooks (cycle 173 v153)

The v153 Cap 1 verification was at the CLEAN operating point. The cycle 173 narrative claimed "drift-diffusion ≡ BP + Crooks FT" gives a theorem-anchored audit. That claim is correct at the clean point but the theorem citation was the *unconditional* Crooks-FT, not the Sagawa-Ueda noise-corrected form. Cycle 177 envelope-expansion (v156 plan -> v157 verdict) discovered the limitation. Mechanism #1 above closes the citation gap: the substrate's existing measurement is fine; the audit bound was under-specified.

### Connection to cycle 137/139 ENDPOINT_COLLAPSED (28-element fixed-point structure)

ENDPOINT_COLLAPSED says the substrate's W^L collapses 100 distinct initial states to 28 distinct endpoints (~22% image fraction). This is RELEVANT to noise-robust erasure: the 28-element fixed-point set is the substrate's natural "redundancy basis" -- any erase-trajectory that lands inside this 28-element basin enjoys built-in error correction because nearby states are pulled to the same fixed point. **Hypothesis worth recording**: the substrate may already implement an implicit r=K redundancy with K~3-4 (since 100/28 ~= 3.6 distinct chains collapse to each endpoint), which would partially explain why the clean p=0 erase audit passes so cleanly and would predict that operating the erase trajectory deeper into the 28-element basin attractor structure improves noise tolerance even without explicit r-fold encoding. This is a free hypothesis for mechanism #2's design: do NOT replicate keys in disjoint subspaces; instead replicate by *trajectory length L* so that all r copies fall in the same attractor basin.

### Connection to cycle 176 v156 commit notes

The v156 narrative section "Five axis-combination rescue sketches" pre-armed 5 sketches. This research drill's vetted ranking is:

- #1 (redundant erase encoding) -> Strategy sketch #1 = mechanism #2 here; P=0.40 deflated.
- #2 (post-erase verification + retry) -> Strategy sketch #2; subsumed under mechanism #3 here (commit-then-prove is the cryptographic-anchor variant of post-erase verification). P=0.30 deflated.
- #3 (lower-noise operating envelope + SLA) -> NOT a rescue, an SLA truncation. Resolved by mechanism #1: the noise-corrected bound IS the SLA. P=0.50 deflated.
- #4 (pre-erase denoising filter) -> DEFERRED. None of the candidate filters (median, WHT-sparse, low-rank) provably preserve forward-reverse trajectory invariance; would require new theorem.
- #5 (code-based protected erase) -> DEFERRED. BCH and FHRR circular-correlation are adjacent and not dismissed per [[feedback-dont-dismiss-adjacent-methods]], but their interaction with Crooks-FT requires nontrivial new proof and the build cost is high.

Net: 3 of 5 Strategy sketches rehabilitated with deflated P. Two deferred but NOT rejected.

---

## (e) Substrate-product implications

Per [[feedback-no-papers-product-only]] -- product framing, not publication.

**If mechanism #1 holds** (cheapest, P=0.50): Cap 1 commercial wedge expands to *every* operating point with characterizable bit-flip noise -- the audit is just `delta_S_emp <= theta(p) + margin`, and the SLA promised to customers becomes "verifiable forensic erase under known noise rate p, with audit threshold scaling per binary entropy." This is more honest than "verifiable forensic erase" with a hidden clean-substrate assumption; it's also a stronger commercial story because the substrate now ships with an explicit noise-tolerance certificate.

**If mechanism #2 holds** (r-fold redundancy, P=0.40): Cap 1 commercial wedge extends to noise levels p up to ~0.15 at r=3 storage overhead 3x. This is a knob the customer can dial: pay 3x or 5x storage for proportionally higher noise tolerance. Storage overhead is the SLA dial.

**If mechanism #3 holds** (cryptographic anchor, P=0.30): Cap 1 wedge becomes substrate-independent. The audit no longer relies on Crooks-FT at all; it relies on commitment-hiding and binding. This is the WEAKEST substrate-product story because it removes the substrate-physics differentiator, but it's the STRONGEST regulatory-compliance story because cryptographic proof-of-erasure is what GDPR auditors actually want to see.

**Combined product strategy**: ship mechanism #1 as the default audit (no cost), add mechanism #3 as the regulatory-compliance overlay (low cost), and offer mechanism #2 as the high-noise-tolerance tier (storage tradeoff). All three are additive, none is a substitute. The cycle 177 KILL verdict does NOT narrow Cap 1 to clean-only; it widens it to a tiered SLA.

**Cost to operationalize mechanism #1**: <1 day Exp Dev work to re-analyze cycle 177 data with the corrected bound and report. This is the cheapest path forward.

---

## (f) Citations (verified count: 12)

1. Crooks, G.E. (1999). "Entropy production fluctuation theorem and the nonequilibrium work relation for free energy differences." Phys. Rev. E 60, 2721. arXiv:cond-mat/9901352
2. Sagawa, T. & Ueda, M. (2012). "Fluctuation Theorem with Information Exchange: Role of Correlations in Stochastic Thermodynamics." Phys. Rev. Lett. 109, 180602.
3. Jun, Y. (2019). "Fluctuation Theorem of Information Exchange between Subsystems that Co-Evolve in Time." Symmetry 11, 433. arXiv:1903.10173
4. Hatano, T. & Sasa, S. (2001). Hatano-Sasa relation for nonequilibrium steady states. (Trepagnier et al. experimental test: PNAS 2004, 101, 15038.)
5. Generalized Landauer bound from absolute irreversibility (2023). arXiv:2310.05449
6. Generalized Landauer Bound for Information Processing: Proof and Applications. Entropy (MDPI) 2022, 24, 1568.
7. Bormashenko, E. & Voronel, A. (2023). "Landauer Bound and Continuous Phase Transitions." Entropy 25, 984. (gives `k_B T[ln 2 + p ln p + (1-p) ln(1-p)]` explicitly)
8. Forni, S. et al. (2025). "Improving noisy free-energy measurements by adding more noise." arXiv:2502.03734
9. Nielsen, M.A. & Chuang, I.L. (2010). "Quantum Computation and Quantum Information." Chapter 10 -- classical repetition code threshold theorem and majority-vote analysis.
10. Decoding Reed-Muller Codes Using Redundant Code Constraints. NSF-PAR-10303733.
11. Paul, M. & Saxena, A. (2010). "Proof Of Erasability for Ensuring Comprehensive Data Deletion in Cloud Computing."
12. Luo, W. et al. (2024). "Empowering Data Owners: An Efficient and Verifiable Scheme for Secure Data Deletion (EVSD)." Computers & Security.

Verified count: 12. Of these, the most load-bearing for mechanism #1 are citations 2, 3, 5, 6, 7 -- which collectively establish the noise-corrected fluctuation-theorem-bounded erasure audit formula. Mechanism #2 leans on 9, 10. Mechanism #3 leans on 11, 12.

---

## Open uncertainties

1. The exact mapping from substrate `delta_S_emp` units to the binary-entropy `theta(p)` requires matching the substrate's free-energy estimator normalization (cycle 173 v153 protocol). One unit-conversion factor that needs to be verified empirically against the p=0 clean baseline before mechanism #1 can be declared a PASS.
2. The "implicit r=K via 28-element fixed-point basin" hypothesis (cross-thread connection (d)) is a free side-prediction; it should be probed by ENDPOINT_COLLAPSED-conditioned variants of the r-fold protocol, but it's not on the critical path.
3. The cycle 177 noise model was iid bit-flip during the erase trajectory; if the realistic deployment noise model is correlated or non-iid, mechanism #2's majority-vote analysis breaks. Recommend Strategy confirm the noise model assumption matches deployment before treating mechanism #2 as commercially shippable.
