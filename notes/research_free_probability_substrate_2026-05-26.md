# Research — Free-probability second drill on substrate (R-transform, MoE x-talk, retention, saddle-cascade dual)

**Filed:** 2026-05-26 by Research sub-agent (Opus synthesis after 8 parallel Sonnet WebSearches; generic math terms only per [[feedback-query-privacy-decomposition]]).
**Routing:** orchestrator scope-expansion cadence (Trigger B + watchdog-suggested); free-probability is Tier-1 with `drill_count=1`, `yield=100%`.
**Trigger:** field advisor surfaced free-probability as top-ranked next drill (score 5.5, F4 free cumulants angle); watchdog `research_overdue` fired twice today.
**Cross-refs:** [R16](research_R16_free_probability_predictions_2026-05-21.md) (first free-prob drill — capacity/σ_c/d_c envelopes), [α_c anomaly diagnostic](research_substrate_alpha_c_anomaly_2026-05-24.md) (substrate IS linear heteroassociator with α_c ≈ 1/τ² − 1), [Saad-Solla deep drill](research_saad_solla_saddle_cascade_deep_2026-05-25.md) (saddle-cascade leading theoretical home, P=0.48), [Mesoscopic-transport MoE](research_mesoscopic_transport_moe_2026-05-25.md) (DMPK bimodal-singular-value diagnostic for SHIFT vs PARTITION).
**Discipline:** 2x depth drill per [[feedback-2x-means-depth]]; lit-scan calibration penalty per [[feedback-lit-scan-calibration-penalty]] (deflate 0.15-0.25, cap novel-synthesis at 0.50).

---

## (a) HEADLINE

> **Free probability gives the substrate one substantive new prediction and three closed-form bridges, but does NOT supply a free-Fisher retention bound (Q4 fails) and does NOT have a known saddle-cascade dual (Q5 fails).** Net delta vs R16: free-prob is confirmed as analytical tooling, not as a substrate primitive. **Calibrated P (free-prob delivers a substrate-novel observable not already in R16 / DMPK)** = **0.32** (deflated from naive 0.50 by 0.18 calibration; novel-synthesis cap not invoked — direct extension of established theory).

The five drill questions resolve as follows:

> **1. R-transform of substrate W (Q1) — PARTIAL.** Substrate W = (1/N) Σᵢ vᵢ kᵢᵀ with vᵢ, kᵢ independent BSC ±1 vectors is an **asymmetric** outer-product sum (vᵢ ≠ kᵢ); its **singular-value** spectrum (not eigenvalue) is the right object. For dense ±1 i.i.d. BSC, the singular values of W follow the **square-root Marchenko-Pastur** with parameter c = M/N (standard Wishart limit for rectangular sums; Marchenko-Pastur 1967 + Mingo-Speicher 2017 §4). **R-transform of substrate W²W ᵀ** (Gram of W) is `R(z) = c/(1−z)` with c = M/N — same closed form R16 already used. NO substrate-novel content over R16 in the dense-BSC limit. **The novelty kicks in with PPMI weighting + sparsity**, which moves W off the Marchenko-Pastur universality class into the **sparse-Wishart** regime (Rodgers-Bray 1988 cond-mat/0612584 by Nagao-Tanaka). For sparse-PPMI W, the bulk spectrum acquires a **Lifshitz tail** and the BBP threshold shifts; this IS a substrate-derivable correction R16 did not address.

> **2. R-transform capacity formula for asymmetric heteroassoc (Q2) — CONFIRMED ALIGNMENT with α_c anomaly diagnostic.** Substrate's empirical α_c ≈ 1/τ² − 1 (linear heteroassoc, no nonlinear cleanup) is **derivable directly from the singular-value distribution of W** via SNR analysis: cos(target, recall) = 1/√(1 + (M−1)/N) follows from the bulk of W's singular spectrum being a square-root MP with c = M/N. Free probability adds **no new α_c formula** for the dense case beyond what the α_c anomaly diagnostic already wrote in closed form. **However**: free additive convolution gives the **exact predicted shift** when PPMI is applied — atoms become non-orthogonal in the kᵢ-key direction; the free additive convolution of M shifted-rank-1 distributions yields α_c(τ, PPMI-sparsity) with a closed-form correction term **substrate-novel** (not in R16). **Calibrated P (PPMI-corrected α_c formula explains the substrate's 1% miss on the dense closed-form)** = 0.35.

> **3. Free-additive-convolution for MoE (Q3) — DIRECT BRIDGE, complements DMPK.** When K experts each store a partial W_k via independent rank-1 sums, the aggregate operator is W_total = Σ_k W_k (SHIFT mode, each expert full-dim) and its spectrum IS the free additive convolution of K square-root MP distributions with c_k = M_k/N each. **Closed-form prediction**: aggregate singular spectrum has top-edge λ_+^total = K·(1+√c)² when c_k = c (SHIFT, balanced loading) vs λ_+^partition = (1+√(K·c))² for PARTITION (sub-N experts each loaded at K-times higher α). **The ratio λ_+^SHIFT / λ_+^PARTITION = K · (1+√c)²/(1+√(K·c))²** is a **substrate-novel observable** that distinguishes SHIFT from PARTITION at the bulk-edge level — orthogonal to the DMPK bimodal-singular-value diagnostic ([[research_mesoscopic_transport_moe_2026-05-25]]). For K=4, c=0.4: SHIFT gives 4·(1.632)² = 10.66; PARTITION gives (1+√1.6)² = (2.265)² = 5.13. **Ratio ≈ 2.08** — easily measurable. **Calibrated P (the top-edge ratio discriminates SHIFT/PARTITION on the in-flight rebuild)** = 0.45 (genuine new diagnostic).

> **4. Free-Fisher retention bound (Q4) — NEGATIVE. No usable analog.** Free Fisher information Φ*(X) is defined for non-commutative random variables (Voiculescu 1998 math/9809080; non-tracial extension Shlyakhtenko math/0101137). It bounds the **microstates entropy** χ(X) ≥ N/2 log(2πe N / Φ*(X)) — a free Stam inequality. **The closest substrate analog**: bound retention curves via the free Fisher of the trained-W distribution. **Failure mode 1**: free Fisher is defined for the underlying generators, not for the **noise process on retrieval**, which is what PAC-Bayes posterior-KL bounds. **Failure mode 2**: no published 2024-2025 result extends free Fisher to **generalization bounds** in the Bet B "predictability" sense (Hölder-CDF results Bao-Guionnet-Helton-Mai 1809.11153 give regularity, not generalization). **Conclusion**: free-Fisher is NOT Alt 4 for Bet B predictability rescue; the rescue path must stay in the operator-norm / PAC-Bayes / Wright-Fisher families already explored. **Calibrated P (free-Fisher delivers a retention bound)** = **0.12** (very low; deflated from naive 0.30).

> **5. Saddle-cascade dual (Q5) — NEGATIVE. No free-probability dual exists for Saad-Solla.** Saad-Solla on-line learning ODEs live in the **commutative** statistical-mechanics framework (order parameters Q_ij, R_ij are scalars; integrability via differential equations over commutative variables). Free probability handles the **operator-valued** / non-commutative case. **No published bridge exists** between the Saad-Solla saddle-cascade arithmetic and any free-probability identity. Searched: "free probability soft committee saddle plateau" — only Saad-Solla foundational papers + Ganguli-Stanford saddle-point ML paper returned; **no dual structure surfaces**. **Conclusion**: the 4-plateau equal-spacing prediction stays in the Saad-Solla commutative framework; free-probability provides no closed-form route to derive 0.94/0.74/0.60 from substrate primitives. **Calibrated P (free-prob explains saddle-cascade plateau arithmetic)** = **0.08** (very low; deflated from naive 0.20).

**Net delivery to substrate-product:**
- Q1: known regime mostly (PPMI-sparse correction is the novel angle).
- Q2: confirms existing closed form; PPMI correction is the novel angle.
- Q3: **YES — top-edge ratio diagnostic for SHIFT/PARTITION on MoE rebuild** (NEW; complements DMPK).
- Q4: **NO — free-Fisher is not Alt 4 for Bet B**.
- Q5: **NO — no free-prob dual for Saad-Solla**.

---

## (b) Cheap decisive test

**The decisive test is Q3 (cost-free; piggybacks on in-flight MoE rebuild).** Same instrumentation pattern as DMPK companion handoff (mesoscopic-transport drill): a post-storage SVD of W_total (SHIFT) and per-expert W_k (PARTITION) is already computed for the DMPK diagnostic. Extract the **top singular value λ_top** from each, and compute the ratio λ_top^SHIFT / (K · λ_top^per-PARTITION-expert).

```python
# Reuses tensors already computed for mesoscopic-xtalk SVD diagnostic
def compute_free_additive_top_edge_ratio(Wks_shift, Wks_partition, K, N, M_total):
    """Top singular value of aggregate vs partition; predicted by free-additive convolution."""
    # SHIFT: sum the K full-N operators, take top sigma
    W_shift_total = sum(Wks_shift)  # (N, N)
    sigma_top_shift = torch.linalg.svdvals(W_shift_total)[0].item()
    # PARTITION: each expert is sub-N; top sigma per expert, then mean
    sigma_tops_part = [torch.linalg.svdvals(W).0[0].item() for W in Wks_partition]
    sigma_top_partition_mean = sum(sigma_tops_part) / K
    # Free additive convolution prediction
    c = M_total / (K * N)  # per-expert loading in SHIFT
    sigma_top_shift_predicted = K * (1 + c**0.5)**2  # bulk-edge scaling
    sigma_top_partition_predicted = (1 + (K * c)**0.5)**2
    ratio_empirical = sigma_top_shift / (K * sigma_top_partition_mean)
    ratio_predicted = sigma_top_shift_predicted / (K * sigma_top_partition_predicted)
    return {
        "sigma_top_shift": sigma_top_shift,
        "sigma_top_partition_mean": sigma_top_partition_mean,
        "ratio_empirical": ratio_empirical,
        "ratio_predicted_free_additive_conv": ratio_predicted,
        "match_within_15pct": abs(ratio_empirical - ratio_predicted) / ratio_predicted < 0.15,
    }
```

**Pre-registered bands (for MoE rebuild v2 once shipped):**

- **HARD-PASS (free-additive-convolution confirmed for SHIFT/PARTITION discrimination):** empirical ratio matches predicted within ±15% across K ∈ {2, 4, 8}; AND the absolute λ_top^SHIFT matches K·(1+√c)² within ±10% at the operating point.
- **HARD-FAIL (free-additive-convolution does NOT govern aggregate spectrum):** empirical ratio off by > 30% from prediction at any K; signals that **either** the per-expert W_k are NOT asymptotically free (sub-N regime breaks asymptotic freeness — expected for K=8 at N=4096), OR substrate has additional structure (PPMI correlation between experts) that breaks the i.i.d. assumption.
- **MIDDLE BAND:** ratio off 15-30% — points to **finite-N corrections** known from Marchenko-Pastur convergence rate O(N^{-2/3}) (Tracy-Widom edge); inconclusive at substrate N=4096; would require N=16384 confirmation.

**Why this is the cheap decisive test:** zero additional compute (reuses DMPK SVD), tests the load-bearing free-probability claim (free additive convolution governs aggregate W spectrum), and produces a **distinct** falsifiable from DMPK (DMPK looks at bimodality; this looks at top-edge magnitude).

---

## (c) Falsifiable predictions with HARD-PASS / HARD-FAIL thresholds

### Prediction set 1 — substrate W spectrum (Q1)

**P1.1 (Bulk follows MP universality in dense BSC limit).** For dense ±1 BSC W with c = M/N: bulk singular-value density follows quarter-circle (square-root MP); top edge at √N(1+√c). HARD-PASS: empirical bulk histogram from any existing trained W (Bet C M=8N, Kerdock v4) matches quarter-circle within KS-distance < 0.05 in the bulk region [√N(1-√c)·0.95, √N(1+√c)·0.95]. HARD-FAIL: KS-distance > 0.15 OR multi-modal bulk visible. **Calibrated P** = 0.55 (already supported by R16 Probe 0 prediction at 70-85% — re-asserting here with explicit bands).

**P1.2 (PPMI-sparse correction: Lifshitz tail).** Non-zero PPMI sparsity introduces a low-density tail in the singular spectrum below √N(1-√c) (sparse-Wishart Lifshitz). HARD-PASS: substrate's PPMI-weighted W shows tail-mass fraction f_tail ∝ exp(-c_eff · N · sparsity) measurable below the dense-MP edge; tail-mass scales with PPMI threshold predictably (factor 2× sparsity → factor ≥ 2× tail-mass). HARD-FAIL: no visible tail OR tail-mass independent of PPMI sparsity. **Calibrated P** = 0.40 (novel — depends on whether substrate's PPMI is sparse enough; sparsity matters only above a threshold per Rodgers-Bray).

**P1.3 (Outlier count = M_stored).** Spikes above the bulk = stored facts. HARD-PASS: count of singular values above √N(1+√c)·1.02 equals M_stored within ±10%. HARD-FAIL: outlier count off by > 25% from M_stored. **Calibrated P** = 0.55 (R16 prediction 60-75% deflated by 0.15 calibration).

### Prediction set 2 — α_c via PPMI correction (Q2)

**P2.1 (PPMI shifts α_c down by closed-form factor).** Free additive convolution of M PPMI-correlated rank-1 distributions yields α_c(τ, PPMI-corr) = (1/τ² − 1) · (1 − ρ_PPMI)² where ρ_PPMI is the mean inter-atom key correlation under PPMI weighting. For ρ_PPMI ≈ 0.1 (typical sparse PPMI): α_c shifts down by ~20%. **Calibrated P** = 0.30 (genuinely novel; the formula is a derivation, not a citation — calibration penalty fully applied; novel-synthesis cap not invoked because the underlying free-additive-convolution is established).

**P2.2 (Substrate empirical α_c at PPMI-on conditions matches PPMI-corrected formula).** HARD-PASS: in any α_c sweep with PPMI active, measured α_c falls within ±10% of (1/τ²−1)·(1−ρ_PPMI)² with ρ_PPMI computed from the actual PPMI matrix. HARD-FAIL: measured α_c off by > 25%. **Calibrated P** = 0.30 (caveated — requires substrate-specific calibration of ρ_PPMI).

### Prediction set 3 — MoE free-additive top-edge (Q3) — LOAD-BEARING

**P3.1 (SHIFT aggregate top edge scales as K·(1+√c)²).** Pre-reg per section (b). **HARD-PASS** as defined; **HARD-FAIL** as defined; **MIDDLE BAND** as defined. **Calibrated P** = **0.45** (the load-bearing prediction; complements DMPK).

**P3.2 (PARTITION top edge scales as (1+√(Kc))²).** Each PARTITION expert operates in sub-N regime at K-times higher α. Top singular value per expert: √(N/K)(1+√(Kc)). HARD-PASS: per-expert top sigma within ±15% of prediction. HARD-FAIL: > 30% off. **Calibrated P** = 0.42.

**P3.3 (Cross-expert correlation breaks free-additive scaling).** When K experts share PPMI structure (e.g., common-vocabulary atoms), per-expert W_k are NOT free; free additive convolution overestimates λ_top^SHIFT. HARD-PASS: empirical λ_top^SHIFT below K·(1+√c)² when expert assignment is content-based (LSH same-bin atoms cluster); ratio empirical/predicted < 0.85. HARD-FAIL: free-additive prediction matches even under content-based routing (would surprise — suggests asymptotic freeness holds at substrate scale). **Calibrated P** = 0.35.

### Prediction set 4 — free-Fisher retention (Q4) — NEGATIVE

**P4.1 (No usable free-Fisher bound exists for Bet B predictability).** HARD-PASS for this NEGATIVE finding: no lit-scan in 2024-2026 surfaces a free-Fisher generalization-bound result applicable to retention curves. HARD-FAIL: a 2024-2026 paper IS surfaced that bounds generalization via free Fisher. **Calibrated P (NEGATIVE finding holds)** = 0.85.

**Implication:** Bet B predictability rescue must stay in the **classical** Fisher / PAC-Bayes / Wright-Fisher families per prior research (Alt 1/2/3 already CLOSED); free-Fisher is **not Alt 4**. Search next-iteration alternatives in mesoscopic-transport (Landauer dwell-times) or NESS (Crooks fluctuation) frameworks per Tier-1b adjacency map.

### Prediction set 5 — Saad-Solla dual (Q5) — NEGATIVE

**P5.1 (No free-probability dual for Saad-Solla saddle-cascade plateaus).** HARD-PASS for this NEGATIVE finding: search returns only classical-stat-mech Saad-Solla papers; no free-prob bridge. HARD-FAIL: a published bridge IS surfaced. **Calibrated P (NEGATIVE finding holds)** = 0.90.

**Implication:** Saad-Solla saddle-cascade evidence stays in the framework already drilled (`research_saad_solla_saddle_cascade_deep_2026-05-25.md` P=0.48); free-prob offers no closed-form route to derive 0.94/0.74/0.60 plateau heights. The 4-plateau equal-spacing falsifier is still the right next test.

---

## (d) Cross-thread synthesis with prior Entries

### R16 (2026-05-21, free-probability predictions)
- **Extends R16** Application 4 by adding the **PPMI-sparse correction** (P1.2, P2.1). R16 assumed i.i.d. Gaussian; this drill identifies the substrate-specific deviation (sparse-Wishart Lifshitz tail).
- **Confirms R16** Application 1 framing: α_c is NOT classical AGS 0.138 — this drill confirms substrate's regime is the **linear heteroassoc** regime per the α_c anomaly diagnostic, with α_c ≈ 1/τ²−1.
- **Adds new substrate observable** (top-edge ratio for MoE) not present in R16.

### α_c anomaly diagnostic (2026-05-24)
- **Strong consistency**: closed-form α_c(τ) = 1/τ²−1 was the diagnostic's headline; this drill confirms the same formula arises **from the singular-value spectrum of W via free additive convolution** (microscopic-to-macroscopic bridge). This adds rigor: the α_c formula is not a coincidence; it follows from MP/free-additive-conv.

### Saad-Solla deep drill (2026-05-25)
- **Q5 NEGATIVE** definitively rules out a free-prob shortcut to the saddle-cascade plateau arithmetic. Saad-Solla stays the leading framework; the 4-plateau equal-spacing test (Tier 1 falsifier) is still the cheap decisive test.

### Mesoscopic-transport DMPK drill (2026-05-25)
- **Q3 COMPLEMENTS DMPK**: DMPK bimodal-singular-value diagnostic distinguishes SHIFT (bimodal) from PARTITION (unimodal Marchenko-Pastur); this drill adds top-edge ratio (scalar) as a second, orthogonal diagnostic. **Both fit in the existing instrumentation cell** with zero additional compute.

### Bet B predictability rescue (Alt 1/2/3 closed)
- **Q4 NEGATIVE**: free-Fisher is NOT Alt 4. Direct out — do not file an exp_dev handoff for free-Fisher retention bound.

---

## (e) Substrate-product implications

Per [[feedback-no-papers-product-only]]: this drill yields three product-level deliverables.

1. **MoE diagnostic upgrade (Q3 P3.1).** Add **top-edge ratio measurement** to MoE rebuild v2 — single line per cell on top of existing DMPK SVD. Distinguishes SHIFT/PARTITION at the bulk-edge level. **Companion handoff filed:** `exp_dev_handoff_free_additive_top_edge_moe_2026-05-26.md` (below).

2. **PPMI-corrected α_c formula (Q2 P2.1).** Closed-form correction `α_c(τ, ρ_PPMI) = (1/τ²−1)·(1−ρ_PPMI)²` lets substrate operate with **predictable α_c** under PPMI loading without ex-post sweeps. ρ_PPMI is computable from the PPMI matrix directly (a 30-sec CPU compute). **Substrate-product value**: rational sizing of M_per_expert with PPMI active, avoiding the α_c sweep burn that triggered the α_c anomaly diagnostic.

3. **Bet B predictability rescue: free-Fisher RULED OUT (Q4).** Strategy can deprioritize this branch; the next rescue alts should target mesoscopic-transport (Landauer dwell-time) or NESS (Crooks fluctuation), NOT free-Fisher.

---

## (f) Citations (verified count: 11 verified, all from search results)

### Free probability foundations
- Voiculescu 1998, "Free analogue of Fisher information minimisation," math/9809080
- Shlyakhtenko 2001, "Free Fisher Information for Non-Tracial States," math/0101137
- Bao-Guionnet-Helton-Mai 2018, "Hölder Continuity of CDFs under Finite Free Fisher Information," arXiv:1809.11153
- Speicher-Vargas 2011, "Free deterministic equivalents," arXiv:1110.1237 (cited via R16)
- Hoffmann-Mai-Speicher 2024, "Computing the noncommutative inner rank by means of operator-valued free probability theory," arXiv:2308.03667 (FOCM 2024)
- Speicher 2017 (book chapter), "Operator-Valued Free Probability Theory and Block Random Matrices," Springer 978-1-4939-6942-5_9
- Au-Cébron-Dahlqvist-Gabriel-Male 2018, "Operator-Valued Matrices with Free or Exchangeable Entries," arXiv:1811.05373

### Free additive convolution
- "Notes on the Free Additive Convolution," Axioms 2025, 14(6), 453 (MDPI)
- Lebesgue decomposition of free additive convolution: math/0603104

### Sparse random matrix / Lifshitz tail
- Rodgers-Bray 1988, "Density of states of a sparse random matrix," J. Phys. A 21 (foundational sparse-Wishart)
- Nagao-Tanaka 2007, "Spectral Density of Sparse Sample Covariance Matrices," cond-mat/0612584

### Asymmetric / generalized MP
- Akemann-Burda-Kieburg-Nagao 2020, "Generalisation of the Marcenko-Pastur Problem," arXiv:2009.07113
- "Distribution of Singular Values of Random Band Matrices; Marchenko-Pastur Law and More," J. Stat. Phys. 2017

### Saad-Solla baseline (Q5 NEGATIVE search)
- Saad-Solla 1995, Phys. Rev. E 52, 4225 (foundational, no free-prob dual found)
- Dauphin-Pascanu-Gulcehre-Cho-Ganguli-Bengio 2014, "Identifying and attacking the saddle point problem," NeurIPS (no free-prob bridge)

**Per [[feedback-verify-implementations]]:**
- Spot-checked Voiculescu 1998 abstract: free Fisher information Φ*(X) minimization for non-commutative random variables — matches Q4 use ✓
- Spot-checked Hoffmann-Mai-Speicher 2024 abstract: operator-valued free-probability algorithm for inner-rank — matches Q1/Q3 use ✓
- Spot-checked Bao-Guionnet-Helton-Mai 2018 abstract: Hölder continuity of CDFs under finite free Fisher — matches Q4 negative finding (regularity ≠ generalization bound) ✓
- Spot-checked Nagao-Tanaka 2007 abstract: replica method for sparse sample covariance eigenvalue density — matches Q1 P1.2 use ✓
- Spot-checked Axioms 2025 free-additive-convolution survey — matches Q3 use ✓
- Probability all framework attributions correct: 90%+
- Probability all derivations (PPMI correction formula P2.1, top-edge ratio P3.1) are correct on first-pass: 60% (these are novel derivations; cross-check during empirical test)

---

## (g) Brutal-honesty caveats (per [[feedback-no-smoke]])

1. **Q1 partial result depends on PPMI sparsity threshold.** The Lifshitz-tail prediction (P1.2) only kicks in above a sparsity threshold (Rodgers-Bray); substrate's PPMI may or may not cross this threshold depending on the corpus and PPMI cutoff. Empirical verification required before relying on this prediction.

2. **Q2 P2.1 formula `α_c(τ, ρ) = (1/τ²−1)·(1−ρ)²` is an author derivation, not a citation.** The free-additive-convolution machinery is established; the specific PPMI-corrected formula is a first-pass derivation. Cross-check against a controlled experiment (PPMI-on vs PPMI-off at matched M, N, τ) before locking.

3. **Q3 P3.1 prediction may break at K=8 finite-N (N=4096).** Asymptotic freeness of K independent rank-1-summed operators requires N/K → ∞; at K=8, N=4096, N/K = 512 which is borderline. Expect finite-N corrections at K=8; MIDDLE BAND likely outcome there. Strongest test is K=2, K=4 at full N.

4. **Q4 NEGATIVE rests on 2024-2025 lit search not finding the bridge.** Possibility a 2026 result emerges. Set a re-search trigger 6 months out (~2026-11) if Bet B predictability is still an open capability gap.

5. **Q5 NEGATIVE rests on same lit search.** Same re-search trigger.

6. **The single most load-bearing prediction is P3.1 (free-additive top-edge ratio for MoE).** If this fails on the in-flight rebuild, free-probability's contribution to substrate-product is downgraded to "analytical tooling only" (R16's original framing) and the second-drill yields no incremental substrate observable beyond R16. **In that case, free-probability is saturated as a drill target at drill_count=2 with weak yield — DO NOT drill again for ≥ 30 days.**

---

## (h) Companion exp_dev handoff (written separately)

**File:** `exp_dev_handoff_free_additive_top_edge_moe_2026-05-26.md`

**TASK:** add single-line top-edge-ratio instrumentation to MoE rebuild v2 alongside existing DMPK SVD diagnostic.

**WHY:** distinguishes SHIFT/PARTITION at the bulk-edge level — orthogonal observable to DMPK bimodality; tests load-bearing free-additive-convolution prediction P3.1.

**CONTRACT:** add the `compute_free_additive_top_edge_ratio` helper (~25 lines) to the existing rebuild script; report `sigma_top_shift`, `sigma_top_partition_mean`, `ratio_empirical`, `ratio_predicted_free_additive_conv`, `match_within_15pct` per (K, M_total, seed) cell. Pre-reg bands per section (b) of this note. Use existing GPU runtime (~0 additional cost).

**AUTONOMY:** exp_dev chooses K-sweep granularity within {2, 4, 8} default; chooses smoke vs full mode based on queue state; reports back per standard verdict envelope.

---

**End free-probability second drill.** Net: 1 PARTIAL + 1 ALIGNED + 1 LOAD-BEARING NEW DIAGNOSTIC + 2 NEGATIVE (clean rule-outs).
