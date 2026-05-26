# Pre-reg: Wave 14 Kerdock 4-coset AMP Universality 4-Step Pre-Test v1

**Filed:** 2026-05-22
**Source:** `research_Kerdock_RI_universality_2026-05-22.md` (Research 15:42 EDT) — Path P3 empirical 4-step verdict.

## Question

Does the substrate's Kerdock 4-coset codebook satisfy the empirical conditions for AMP State Evolution universality (sub-Gaussian-like spectral profile, eigenvector delocalization, and empirical SE matching)?

If YES → Bet Z.3-AMP (Bayes-AMP / VAMP posterior readout) is viable on substrate without codebook modification (the highest-value Research F1 capacity-extension mechanism, P=0.75).

If NO → Fall back to VAMP with cached SVD (P1, P=0.90; substantially more expensive online).

## Hypothesis

H_pass: all 4 steps pass — Kerdock effectively in AMP RI universality class via the Gorini et al. 2026 traffic-distribution machinery extension.

H_kill: 0-1 steps pass — Kerdock's Z_4 coset phase structure creates correlations that violate AMP's matrix-class assumption. Use VAMP.

## Pre-declared verdicts

- `AMP_KERDOCK_PASS` — 4 of 4 steps pass.
- `AMP_KERDOCK_PARTIAL` — 2 or 3 of 4 pass (tentative; VAMP recommended).
- `AMP_KERDOCK_KILLED` — 0 or 1 of 4 pass.
- `AMP_KERDOCK_INCONCLUSIVE` — metric collection error.

## Method

1. **SVD of A**: build Kerdock 4-coset codebook (4N codewords); pick M = ⌈0.5 · 4N⌉ rows; normalize by √N. Compute `torch.linalg.svd(A)`. Always pass (setup).
2. **MP spectral fit**: empirical singular-value² distribution vs Marchenko-Pastur theoretical bulk at α=M/N. KS statistic D < 0.05 threshold.
3. **Eigenvector delocalization**: N · max|V_ij|² < 5 (Dudeja-Lu-Kini 2022 engineering tolerance; IID Gaussian baseline = 1).
4. **AMP SE empirical diagnostic**: run AMP soft-threshold with Onsager correction for 20 iterations on 5 random Bernoulli-Gaussian sparse signals (sparsity=0.1, σ_noise=0.05); measure plateau MSE vs SE prediction. Max relative error < 0.05.

## Acceptance thresholds

- 0.05 KS-statistic (canonical sub-Gaussian fit acceptance).
- 5.0 delocalization (Dudeja-Lu-Kini engineering tolerance).
- 0.05 SE relative error (Bayati-Montanari 2011 universality margin).

## Config

- N=256 smoke, 4096 full.
- M/N=0.5 (substrate's standard operating range).
- 20 AMP iterations × 5 trials full.

## Pre-declared interpretation

- **PASS**: Bet Z.3-AMP viable. Strategy promotes "Bayes-AMP readout" as new substrate-product capability primitive (substrate-novel; couples to Lane D + Lane A).
- **PARTIAL**: AMP works "mostly" but VAMP is the safe choice. Update Bet Z.3 to VAMP-default.
- **KILLED**: Pure Kerdock NOT in AMP class. Two fallbacks: (a) VAMP with cached SVD (P1, expensive), (b) Randomized Kerdock = Kerdock × random ±1 diagonal (P2, substrate codebook change).

## Substrate-product context

Research found "no published RS-phase paper gives closed-form α_c for 4-coset Reed-Muller codebooks exceeding 0.138" but substrate empirically achieves M/N=8 (57× above AGS). If Kerdock satisfies AMP universality, this opens info-theoretic-limit readout (α → α_IT = Shannon capacity).

## Not in scope

- VAMP implementation (P1 — separate experiment if PASS fails).
- Randomized Kerdock (P2 — separate experiment).
- Spatially coupled codebook (Krzakala 2012 spatial coupling — separate experiment).
