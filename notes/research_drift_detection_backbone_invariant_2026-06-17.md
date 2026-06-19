# research: backbone-invariant drift detection methodologies (3x deep drill)

date: 2026-06-17
type: 3x deep research drill (3 parallel Sonnet lit-scans + Opus synthesis)
trigger: kappa_3 drift detection MIDDLE_BAND 2/3 -- pythia + GPT-2 PASS at smoke; llama HARD_FAIL. Need backbone-invariant drift theory + better metrics.

## (a) HEADLINE

Cross-backbone drift detection is best framed as a TWO-STAGE pipeline: (1) map activations into a backbone-invariant geometric coordinate (depth-relative-shared geometry, Procrustes-aligned linear concept space, or local intrinsic dimension) and (2) apply a distribution-free two-sample test (MMD with characteristic kernel, or Wasserstein with Gaussian-Frechet closed-form). The kappa-statistic family is fundamentally backbone-coupled (rater-agreement on labels, not on representations) and is the LIKELY ROOT of the llama HARD_FAIL: kappa values do not transport across backbones whose label-emission geometry differs, even when underlying drift is identical. This drill found 22 verified citations across the 3 angles, with the strongest portability evidence from Platonic Representation Hypothesis (Huh 2024), Linear Representation Transferability (2025), depth-shared activations (2504.08775, 2025), and local intrinsic dimension (Tulchinskii 2023).

## (b) Cheap decisive test

Pre-registered HARD-PASS / HARD-FAIL on a single GPU-cell:

1. Pick 2 reference distributions D0, D1 with known semantic drift (e.g. wiki -> code).
2. Extract activations from {pythia-1B, GPT-2-large, llama-7B} at relative depth 0.6-0.7 (depth-normalized).
3. Compute 3 drift scores per backbone: kappa_3 (current), MMD with RBF characteristic kernel (Gretton 2012), Frechet-distance closed-form (Xiang 2021 BERT-Frechet adapted).
4. Pre-register: ratio (drift-score-llama / drift-score-pythia) on (D0,D1) pair.

Cost: ~30 min CPU per backbone for activation extraction; MMD + Frechet are sub-second post-extraction.

## (c) Falsifiable predictions

HARD-PASS thresholds (method works backbone-invariantly):
- MMD ratio (llama / pythia) lies in [0.5, 2.0] on the same (D0,D1) pair (within 2x = same-magnitude signal).
- Frechet-distance ratio (llama / pythia) lies in [0.5, 2.0].
- Both methods agree on drift-vs-no-drift direction at p<0.05 (permutation test, B=1000).

HARD-FAIL thresholds (method backbone-coupled like kappa):
- Ratio > 5x or < 0.2x: backbone-coupled, do NOT promote.
- Disagreement on drift direction between any two backbones at p<0.05: backbone-coupled.

Calibration penalty applied: deflated P estimates by 0.20 (substrate is in uncharted regime for cross-backbone HD drift); novel-synthesis cap P=0.50.

Per-method P estimates (deflated):
- MMD-on-depth-normalized: P_deflated = 0.45 (high prior from Gretton 2012 distribution-free guarantee + 2504.08775 depth-shared geometry; deflated for cross-backbone novelty)
- Frechet-on-Procrustes-aligned: P_deflated = 0.35 (Procrustes adds estimation noise; Gaussian assumption may fail on HD activations)
- LID-stability (Tulchinskii 2023): P_deflated = 0.40 (already evidenced backbone-portable for AI-detection; drift not directly tested)
- kappa-3 fix (current): P_deflated = 0.15 (kappa is on labels not reps; expected to keep failing on llama)

## (d) Cross-thread synthesis with prior entries

Connects to:
- MEMORY index: "USER 2026-06-16: a measured bound is METHOD/CONFIG-contingent" -- the llama HARD_FAIL is method-contingent (kappa_3 on this backbone with current config); reframing drift as MMD-on-depth-normalized changes the method-frame.
- Platonic Representation Hypothesis (Huh 2024) provides the cross-backbone convergence justification for ANY method built on shared-depth-geometry; it does not certify the convergence at any particular scale band (pythia-1B may sit below the convergence onset that llama-7B clears).
- Layers-at-Similar-Depths (2504.08775, 2025) is the empirical anchor: nearest-neighbor activation geometry approximately shared across Pythia, GPT-2, LLaMA, Mamba at matched RELATIVE depth -- this directly explains why ABSOLUTE-layer kappa_3 fails on llama (depth normalization needed).
- Linear Representation Transferability (arXiv:2506.00653) supplies the affine map for porting drift directions across families; concept-specific affine maps reach ~99.9% transfer.
- MMD (Gretton 2012) is the dominant distribution-free two-sample test with finite-sample guarantees; CUSUM/EWMA are parametric and Gaussian-assumption-bound -- worse fit for HD activations.
- kappa-statistic family (Cohen 1960, McHugh 2012) is fundamentally a rater-agreement statistic on LABELS; the prevalence/bias paradox (McHugh 2012) predicts that high label agreement can yield low kappa when backbones emit labels with different prior frequencies -- this matches the llama HARD_FAIL signature.

## (e) Substrate-product implications

For the substrate-product:
1. The cap_map row "drift detection works cross-backbone" should bump to YELLOW (method-contingent, depends on which method) not RED.
2. Concrete swap candidate: replace kappa_3 smoke gate with MMD-on-depth-normalized-activations. Implementation: (i) extract activations at relative depth 0.6-0.7, (ii) compute MMD with RBF kernel (median heuristic for bandwidth), (iii) compare to permutation null. Distribution-free guarantee + backbone-invariant geometric anchor.
3. Fallback if MMD-on-depth fails llama: try LID-stability per Tulchinskii 2023 (already empirically backbone-portable for AI-text detection).
4. Tracking-document framing only -- no paper drafting per 10th USER-LOCKED rule.

## (f) Citations (verified count)

22 verified citations across 3 angles:
- Angle 1 (backbone-invariant detection): Gama 2014, Lu 2018, Yang 2024 OOD survey, Wu 2023 representation dissimilarity (arXiv 2310.14993), Layers-at-Similar-Depths 2025 (arXiv 2504.08775), Mechanistic Universality 2024 (arXiv 2410.06672), LLM OOD Survey 2024 (arXiv 2409.01980), Intermediate Reps OOD 2025 (arXiv 2510.05782).
- Angle 2 (better metrics + validity): Gretton 2012 MMD, Gibbs-Su 2002 metric bounds, Wasserstein/Frechet-BERT 2021, Kifer 2004 stream change detection, Page 1954 CUSUM, Roberts 1959 EWMA, Lai 1995/2010 sequential change-point, Cohen 1960 / Fleiss 1971 / McHugh 2012 kappa.
- Angle 3 (backbone-portable theory): Huh 2024 Platonic (arXiv 2405.07987), Kornblith 2019 CKA (arXiv 1905.00414), Raghu 2017 SVCCA, Park 2023 Linear Representation Hypothesis (arXiv 2311.03658), Marks 2023 Geometry of Truth (arXiv 2310.06824), Linear Representation Transferability 2025 (arXiv 2506.00653), Maiorca 2024 Latent Communication (arXiv 2406.11014), Tulchinskii 2023 Intrinsic Dimension (arXiv 2306.04723).

Coverage gaps:
- No direct 2024-2025 head-to-head MMD vs Wasserstein vs KL vs CUSUM benchmark surfaced.
- Bu 2018 MMD-streaming paper not retrievable via WebSearch.
- Mathur 2024 representation drift in LMs not confirmed (may not exist as cited).

## Next-drill candidate

Field: AMP/VAMP (tier-2, drill_count=3) -- adjacent angle: MMD-AMP-state-evolution for streaming drift detection on high-dim activations. This composes Angle 2 (MMD validity) with Angle 3 (backbone-invariant geometry) under a single analytic framework. P_pre-deflated = 0.55; P_deflated = 0.35.
