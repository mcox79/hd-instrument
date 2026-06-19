# Research deep assessment — BBMD Cap-12 rehabilitation 5-path ranking (2026-05-24)

**Author**: Research sub-agent (Opus synthesis from 4 parallel Sonnet WebSearch passes, ~5 min wallclock)
**Trigger**: Strategy request `strategy_request_to_research_bbmd_cap12_rehab_2026-05-23.md` (cap_map v171 cycle 191)
**Per**: [[feedback-rehabilitation-after-rejection]] + [[feedback-negative-results-2x-research]] + [[feedback-lit-scan-calibration-penalty]] + [[feedback-no-smoke]]
**Prior**: This is a deeper 2x assessment on top of `research_bbmd_kill_rescue_drill_2026-05-24.md` (which proposed `vamp_se_from_R_transform_v1` as the highest-leverage NEXT anchor — Drill-R3, a DIFFERENT rescue-path mapping from Strategy's R1-R5 below). Both must be honored side-by-side.
**Lit-scan queries** (all generic-math per [[feedback-query-privacy-decomposition]], NO substrate/Kerdock/BBMD mentions):
1. MP + Kolmogorov-Smirnov pre-test in compressed-sensing measurement-matrix outlier-detection
2. Free-cumulant profile-shape classification of structured matrices (Hadamard, Reed-Muller spectra)
3. VAMP-vs-AMP universality gap under rotation-invariance (Rangan-Schniter-Fletcher extensions)
4. AMP convergence prediction along random-matrix interpolation families (Spearman-style monotone-curve)

---

## HEADLINE

After deep assessment, **two of the five rescue paths (R3 + R1) survive cross-codebook honesty + product-meaningfulness gates**; R2 is a free reframe with zero rescue value beyond what v169 already booked; R4 is high-novelty but fragile under calibration; R5 is informative-either-way but has weakened theoretical foundation per arXiv "identical AMP/VAMP SE fixed points" precedent. Recommended ship: **R3 (MP-KS pre-test pipeline) FIRST** (cheap, P=0.55 after deflation, real infrastructure capability), **R1 (cross-interpolation AMP-error predictor) SECOND** in parallel CPU (P=0.30 after harsher deflation than Strategy stated). Honest read: **even with both passing, the resulting "12th capability" is weaker than the existing 11**; recommend filing the 12th tentatively under R3 if it passes, but the dominant move is to STRENGTHEN the existing 11 rows via these probes' annotations.

---

## Section 1 — Per-path deep assessment

### R1 — AMP-error predictor capability within interpolation families

**Claimed capability**: License the κ_n divergence-sum (or full profile) as a predictor of AMP-convergence regime for a customer's matrix family WITHIN a customer-specified interpolation family. Existence proof: Anchor 1 v170 Spearman ρ=0.900 along iid-Gauss → Kerdock interpolation.

**Anchor experiment**: `interp_family_cross_check_v1` — pick ONE non-Kerdock interpolation family (iid-Gauss → SRHT, or iid-Gauss → Hadamard, or iid-Gauss → Paley-conference) and run the same 5-alpha sweep (alpha ∈ {0, 0.25, 0.5, 0.75, 1.0}). Measure ∑|Δκ_n| and AMP rel-err per cell; compute Spearman ρ. **Queue**: CPU; **ETA**: 30-60 min per family. **HARD-PASS**: Spearman ρ ≥ 0.70 AND max VAMP rel-err < 0.10 across all 5 cells. **HARD-FAIL**: Spearman ρ < 0.50 on any tested non-Kerdock interpolation family ⇒ predictor is alpha-iid-Gauss→Kerdock-specific only, not a meta-capability; close R1.

**Honest P recalibration**: Strategy stated 0.40 raw, deflated. Lit-scan finds **NO direct precedent for κ_n divergence-sum as AMP-failure predictor along an interpolation curve** (arXiv:2503.20409 / 1402.3210 give convergence conditions per matrix but NOT a predictive scalar). This is novel-synthesis, capped at 0.50 per [[feedback-lit-scan-calibration-penalty]]. Further deflation: Anchor 1 PASS is a SINGLE-curve sample; n=1 generalization-evidence is weak — a second-family failure is empirically plausible (the predictive scalar may track a Kerdock-internal property, not a universal one). **Honest P = 0.30** (deflate by 0.10 from Strategy's 0.40).

**Honest reading per [[feedback-no-smoke]]**: This is a TOOL / meta-capability — a "pre-flight check selector" that picks AMP vs VAMP given measured codebook moments. Real customer value IF generalization holds. NOT substrate-novel physics — same predictor could be built atop any universal κ_n-vs-AMP-error relationship. Frame as engineering capability ("substrate ships pre-flight diagnostic") not physics capability. Survives cross-codebook honesty IF generalization holds; close it if not.

### R2 — Kerdock-specific moment-divergent-bounded fingerprint reframe

**Claimed capability**: Drop cross-codebook class claim entirely; keep substrate's Kerdock-specific empirical characterization (v164a/v166/v167 fingerprint stack: N-stability + bulk-boundedness + cumulant-order-stability) as a substrate-product capability claim about substrate's CHOSEN codebook only. Framing: "substrate's Kerdock readout has a precise spectral signature we verify on customer matrices to confirm operating regime."

**Anchor experiment**: NONE — Strategy stated cost=0 (reframing only). The v164a/v166/v167 fingerprint stack already passed all promotion gates by v167. No new measurement.

**Honest P recalibration**: Strategy stated 0.50. But this is NOT a rescue of the cap-12 candidate — it's a renaming of substrate's existing Cap 1/3/8 + v164a annotations. The kill-rescue drill (Drill-R2) already pointed out: "v169 ALREADY annotated Cap 1/3/8 with closed-form 2-design derivations and EXPLICITLY said 'ANNOTATION-only, NOT a 12th portfolio capability.' Promoting now is double-counting unless we have a NEW empirical anchor." **Honest P that this licenses a NEW 12th-capability row = 0.10** (it doesn't pass the "new row" gate; it just relabels existing rows). P that this is a USEFUL annotation-clarification = 0.95 (trivially, since v171 already started this in the kill narrative).

**Honest reading per [[feedback-no-smoke]]**: This is smoke if pitched as a 12th capability. The work is already done. It's an annotation-clarification, not a rescue. Strategy's 0.50 P confuses "we have the measurement" with "we have a new capability." Per the user's repeated framing — capability classes must add genuinely-new substrate-product axes, not relabel existing ones. **Do NOT count R2 as a rescue path.** Count it as a v171-cycle annotation update on Cap 1/3/8 + v164a wording, which is a cap_map maintenance task, not a Research deliverable.

### R3 — MP-KS pre-test infrastructure capability

**Claimed capability**: The v171 NEGATIVE result — MP-KS at KS=0.59 already discriminates SRHT/Hadamard from iid-Gaussian — is itself a substrate-product positive. Substrate ships a cheap MP-KS pre-test that kills bad codebooks before downstream cost: "before fitting customer's codebook, run MP-KS pre-test; if KS > 0.20, the codebook is outside the standard MP regime and substrate's VAMP-on-chain primitive is the appropriate inference path." Infrastructure capability, not substrate-physics-novelty.

**Anchor experiment**: `mp_ks_pretest_pipeline_v1` — pipeline integration test on 5 codebook families (iid-Gauss, SRHT, Hadamard, RM(1,m), Kerdock) plus 1-2 hand-constructed "borderline" customer-grade codebooks (e.g., low-rank-perturbed iid-Gauss, mixture-of-iid+structured). Measure MP-KS per family; check routing decision (KS > 0.20 → VAMP, else AMP); validate routing decision empirically (run BOTH AMP and VAMP on each codebook; the chosen primitive must have lower rel-err). **Queue**: CPU; **ETA**: 15-30 min. **HARD-PASS**: (a) MP-KS correctly routes at least 4/5 known families (Kerdock should route to VAMP); (b) routing decision precedes the AMP-failure observation by ≥10x wallclock speedup. **HARD-FAIL**: MP-KS routes <3/5 correctly, or borderline codebooks expose mis-routing — close R3.

**Honest P recalibration**: Strategy stated 0.65. Lit-scan finds Götze-Tikhomirov MP-convergence-rate bounds (arXiv:1110.1284, 1412.6284) — the KS-distance to MP IS rigorously studied. The novel-synthesis is the PIPELINE framing (KS as routing gate), not the math. Per calibration penalty, novel-synthesis P capped at 0.50, but the v171 result ITSELF is already empirical evidence that MP-KS discriminates ≥3 codebooks; that's data, not synthesis. **Honest P = 0.55** (slight deflation from Strategy's 0.65 because borderline-codebook robustness is genuinely unknown; "KS > 0.20" threshold is unvalidated against customer-grade noise).

**Honest reading per [[feedback-no-smoke]]**: This IS a real infrastructure capability — the substrate ships a pre-flight diagnostic that has empirical evidence today. It's narrower than "BBMD as substrate-novel discriminator class" and that narrowness is HONEST. The customer-facing pitch ("we route your codebook to the right inference primitive in 15ms") is product-meaningful, not physics-grade. Survives cross-codebook honesty trivially because cross-codebook discrimination is the BASIS of the capability, not a refuted claim. Survives the 12th-capability gate because Cap 8's VAMP-on-chain primitive is the DOWNSTREAM tool R3 routes TO — R3 is the PRE-flight LAYER, structurally orthogonal to Cap 8. Strongest rescue.

### R4 — Higher-cumulant profile-SHAPE discriminator (vs scalar sum)

**Claimed capability**: Replace scalar ∑|Δκ_n| with a SHAPE-of-profile discriminator (e.g., monotonicity class GROWS/DECAYS/SATURATES, or curvature of κ_n curve through n=8) — different codebook architectures may carry distinguishable shape classes even when scalar sums collapse to comparable values. v167 showed Kerdock κ_n GROWS through n=8 (3/4 cells) or SATURATES (1/4); the SRHT/Hadamard/RM(1,m) shape was NOT measured in v171.

**Anchor experiment**: `kappa_profile_shape_cross_codebook_v1` — measure κ_n through n=8 across 4 codebooks (SRHT, Hadamard, RM(1,m), Kerdock) at common N=1024, M chosen to match v167. Classify monotonicity-class per codebook (GROWS / DECAYS / SATURATES / NON-MONOTONE). **Queue**: CPU; **ETA**: 1-2 hr. **HARD-PASS**: (a) ≥3 distinct shape classes emerge across 4 codebooks; (b) at least one class is UNIQUELY Kerdock (or Kerdock + iid-Gauss share a class that SRHT/Hadamard/RM do NOT). **HARD-FAIL**: All 4 structured codebooks share the same monotonicity class as Kerdock ⇒ shape-discriminator is not substrate-novel either; close R4.

**Honest P recalibration**: Strategy stated 0.35 raw, deflated. Lit-scan finds Hadamard-Walsh spectral characterization of Reed-Muller (ScienceDirect S0045790698000330) and Hadamard-matrix spectrum classification (arXiv:1807.04238) — the underlying spectra ARE known to differ across these matrix families, but **no published work on the κ_n free-cumulant PROFILE SHAPE as a discriminator** appears. This is genuinely novel-synthesis, capped at 0.50. But: the scalar-collapse failure in v171 is a one-bit refutation — does shape ALSO fail? Plausible mechanisms (e.g., Hadamard κ_n grows similarly because shared algebraic structure) make a shape-collapse outcome empirically possible. The same Anchor-2-style cross-codebook honesty test that killed BBMD-scalar could kill BBMD-shape; the principle that "moments of the spectrum mostly track shared algebraic structure across MUB-adjacent families" is the underlying killing mechanism. **Honest P = 0.25** (further deflate from Strategy's 0.35 because the kill mechanism that hit scalar likely hits shape too; the rescue depends on a NEW source of discrimination not yet identified).

**Honest reading per [[feedback-no-smoke]]**: This is a SECOND-CHANCE on the same dead horse. The Anchor-2 kill said "shared algebraic structure across Hadamard/SRHT/RM/Kerdock makes BBMD-as-class non-discriminative." Shape is plausibly equally affected unless we have a specific mechanism why shape-curvature would diverge while scalar-sum converged. Per [[feedback-dont-overextend-theorems]] this isn't quite premature dismissal — it's an adjacent path — but the calibration honesty says: don't expect rescue. Run ONLY if R3 + R1 both succeed and we have spare CPU + want a third candidate.

### R5 — Codebook-architecture-conditioned VAMP-vs-AMP gap predictor

**Claimed capability**: v168 demonstrated VAMP-vs-AMP split on Kerdock at SE-fixed-point level (VAMP mean rel-err 0.021 vs AMP mean rel-err 0.450). Rescue: test this empirically across structured codebook families — is the VAMP-vs-AMP gap codebook-architecture-specific, and does its magnitude predict downstream substrate-product utility (i.e., gap = customer-decision-relevant quantity)?

**Anchor experiment**: `vamp_vs_amp_gap_cross_codebook_v1` — run AMP + VAMP at fixed (N, M, SNR) across 4-5 structured codebook families; measure rel-err per primitive per codebook; compute gap = AMP rel-err − VAMP rel-err per codebook. **Queue**: CPU; **ETA**: 2-4 hr per codebook (8-16 hr total CPU; ~30-60 min GPU). **HARD-PASS**: (a) gap magnitude shows codebook-conditioned variation (max − min across codebooks > 0.20 rel-err); (b) codebook with largest gap also has largest empirical AMP-failure (Spearman ρ ≥ 0.7 between gap-magnitude and AMP-fail-magnitude). **HARD-FAIL**: gap is roughly constant across codebooks (variation < 0.10) ⇒ gap is not architecture-conditioned, no predictor; close R5.

**Honest P recalibration**: Strategy stated 0.45. Lit-scan finds CRITICAL caveat: ScienceDirect "Identical fixed points in state evolutions of AMP and VAMP" (S0165168420301444) — under right-orthogonal invariance, AMP and VAMP SE have the SAME fixed point. This means **for rotation-invariant matrices the gap should be NEAR ZERO at convergence**; the substrate's empirical Kerdock gap (0.021 vs 0.450) is plausibly explained by AMP non-convergence (a failure mode), not a fixed-point gap. The "gap predictor" framing then reduces to "AMP-divergence vs VAMP-convergence" — which is essentially the same statement as R3 (MP-KS routes the divergent ones to VAMP). **Honest P = 0.30** (deflate from 0.45). Even if the cross-codebook gap-magnitude variation appears, the THEORETICAL story (gap = AMP-failure-mode-magnitude) collapses to R3's framing, and we'd be claiming a "predictor" that's just a wrapper around AMP-failure-detection.

**Honest reading per [[feedback-no-smoke]]**: This claim partially OVERLAPS with R3 (both about routing AMP vs VAMP based on codebook properties) and partially OVERLAPS with Anchor 1 (which already showed AMP-error tracks κ_n divergence). The "gap predictor" as a SEPARATE 12th-capability candidate is weak — it's a different MEASUREMENT (gap magnitude instead of κ_n divergence or KS distance) but the same underlying capability (route customer to right primitive). Likely subsumed by R3 once R3 is shipped. Run R5 only if R3 fails AND we need a different routing-input metric.

---

## Section 2 — Critical question: which path survives cross-codebook honesty?

The Anchor-2 kill showed BBMD-distance isn't substrate-novel because Hadamard/SRHT/RM share the property. Any rescue must be either:
- (i) NARROWER than "BBMD discrimination" (R2 — but R2 isn't a rescue, it's a relabel)
- (ii) AT A DIFFERENT ABSTRACTION LEVEL that doesn't compete with Hadamard/SRHT (R1 as TOOL, R3 as INFRASTRUCTURE)
- (iii) THE INFRASTRUCTURE CAPABILITY from the negative result itself (R3)

**Cross-codebook honesty pass/fail per path**:

| Path | Survives? | Why |
|---|---|---|
| R1 | CONDITIONAL | Survives IF generalization to a 2nd interpolation family passes; pure tool-grade meta-capability, not substrate-novel |
| R2 | N/A | Not a rescue; annotation-clarification of existing Cap 1/3/8 + v164a |
| R3 | YES | Infrastructure capability; the cross-codebook discrimination IS the basis of the capability, not a refuted claim |
| R4 | UNLIKELY | Same kill mechanism (shared algebraic structure across structured codebooks) likely applies to shape as to scalar |
| R5 | PARTIAL | Theoretical foundation weakened by AMP/VAMP SE-fixed-point identity; collapses to R3 framing |

---

## Section 3 — Ranking + top-2 recommendation

Ranked by **P(survives cross-codebook honesty) × P(material to substrate product story)**:

| Rank | Path | Honest P | Material? | Anchor cost | Verdict |
|---|---|---|---|---|---|
| 1 | **R3 (MP-KS pre-test)** | 0.55 | YES — infrastructure capability with empirical evidence today | 15-30 min CPU | **SHIP FIRST** |
| 2 | **R1 (cross-interpolation predictor)** | 0.30 | YES — meta-capability if it generalizes; pre-flight diagnostic | 30-60 min CPU per family | **SHIP IN PARALLEL** |
| 3 | R5 (VAMP-vs-AMP gap predictor) | 0.30 | PARTIAL — likely subsumed by R3 | 8-16 hr CPU / 30-60 min GPU | DEFER until R3 lands |
| 4 | R4 (profile-shape discriminator) | 0.25 | LOW — same kill mechanism likely applies | 1-2 hr CPU | SKIP unless R3+R1 both pass and CPU free |
| 5 | R2 (Kerdock-specific reframe) | 0.10 (as 12th cap) | NOT a rescue — annotation-clarification only | 0 | Filed as v171 cap_map maintenance, not Research deliverable |

**Top-2 recommended to ship NEXT (per Strategy request item 6)**:

1. **R3 — `mp_ks_pretest_pipeline_v1`** (CPU queue, 15-30 min ETA). Hard-pass: KS-routing correctly directs ≥4/5 known codebook families AND routing decision ≥10x faster than AMP-failure-observation. This is the strongest 12th-capability candidate; it is INFRASTRUCTURE-CLASS, structurally orthogonal to the existing 11, and rides on the v171 result.

2. **R1 — `interp_family_cross_check_v1`** (CPU queue, 30-60 min ETA per family). Ship with iid-Gauss → SRHT as the first non-Kerdock interpolation family. Hard-pass: Spearman ρ ≥ 0.70 AND max VAMP rel-err < 0.10 across all 5 alpha cells. If this passes, the AMP-error-predictor capability gets cross-family generalization evidence and becomes a candidate for either a row of its own OR a STRONG annotation on Cap 8.

**Coordination with prior drill**: The kill-rescue drill (`research_bbmd_kill_rescue_drill_2026-05-24.md`) recommended Drill-R3 = `vamp_se_from_R_transform_v1` as the highest-leverage anchor — that's a DIFFERENT path from Strategy's R3 above (mapping mismatch: Strategy R3 = MP-KS pre-test, Drill R3 = VAMP-SE from R-transform). Both are coherent independent paths. The kill-rescue drill's Drill-R3 maps to a NEW path NOT in Strategy's R1-R5 list — call it **R6 = VAMP-SE from measured R-transform**. R6 was rated P=0.50 in the kill-rescue drill. It's also worth shipping, BUT after R3 + R1, because R6 is Kerdock-internal whereas R3 + R1 give cross-codebook evidence Strategy explicitly asked for. **R6 enters queue 3rd** after R3 + R1 verdicts land.

---

## Section 4 — Honest reading: should we give up on a 12th capability?

**Recommendation: DON'T give up, but lower expectations.** Even after both R3 + R1 land successfully, the resulting "12th capability" will be:

- R3-shaped: an INFRASTRUCTURE-class capability (pre-flight diagnostic) — narrower than substrate-physics-novelty
- R1-shaped: a META-tool capability (cross-interpolation predictor) — narrower than substrate-physics-novelty
- R6-shaped (if it lands): a COMPOSITION capability (R-transform → VAMP-SE) — substrate-physics-novel but composition of existing rows

None of these match the original BBMD-as-substrate-novel-class ambition. The honest portfolio narrative is:

- 11 capabilities ✅ STAND
- 1 candidate 12th in REVIEW (R3 if it passes; R1 as backup; R6 as a Kerdock-internal third backup)
- The 12th, if it lands, will be NARROWER and more honest than the BBMD-as-class framing was

This is HEALTHY per [[feedback-no-smoke]]. The substrate's substrate-physics anchors are at 11; engineering / infrastructure capabilities can grow the count to 12 (or more) without inflating the substrate-physics story.

**Consolidate-at-11 alternative**: If R3 fails its hard-pass AND R1 fails its hard-pass on the first cross-family check, take the kill-rescue drill's Drill-R5 default: stay at 11, strengthen the 11 via annotations, move on. Per [[feedback-dont-overextend-theorems]] this is the right move at that point — don't chain a 5th, 6th rescue.

---

## Substrate-product implications (per [[feedback-no-papers-product-only]])

- R3 PASS → substrate ships "pre-flight codebook diagnostic" as a customer-visible workflow: customer submits matrix; substrate runs MP-KS pre-test in 15ms; routes to AMP or VAMP-on-chain primitive accordingly; customer gets faster + cheaper inference with no hand-tuning. Capability class: INFRASTRUCTURE.
- R1 PASS → substrate ships "AMP-failure predictor" as a customer-visible diagnostic: customer provides matrix; substrate measures κ_n moments; outputs expected AMP convergence regime + recommended inference primitive. Capability class: META-DIAGNOSTIC.
- R3 + R1 BOTH PASS → portfolio reaches 12, with the 12th being a composite "pre-flight + diagnostic" infrastructure capability. Modest, honest, customer-meaningful.
- BOTH FAIL → consolidate at 11; v171 annotation-clarification on Cap 1/3/8 + v164a + v163 strengthening per the kill-rescue drill's audit.

---

## Citations (verified count: 7)

1. arXiv:1610.03082 — Rangan, Schniter, Fletcher, *Vector Approximate Message Passing* (foundational VAMP)
2. ScienceDirect S0165168420301444 — *Identical fixed points in state evolutions of AMP and VAMP* (CRITICAL caveat for R5)
3. arXiv:1110.1284 — *On the Rate of Convergence to the Marchenko-Pastur Distribution* (R3 foundation)
4. arXiv:1412.6284 — *Rate of Convergence of the Expected Spectral Distribution Function to the Marchenko-Pastur Law* (R3 foundation)
5. arXiv:1004.2926 — *Sparse Reconstruction via The Reed-Muller Sieve* (R4 spectral background)
6. arXiv:1807.04238 — *Spectra of Hadamard matrices* (R4 spectral background)
7. arXiv:2503.20409 — *Approximate Message Passing for general non-Symmetric random matrices* (R1 / convergence-prediction background)

Sub-agent dispatches: 4 parallel Sonnet WebSearch passes, ~5 min wallclock.
