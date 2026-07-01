# M1.4 Refuse-Gate Mechanism-Class Research Drill

**Filed:** 2026-07-01 post-compaction
**Trigger:** BACKUP priority #2 — v3/v4/v5 all HF; USER-locked M3 milestone blocker
**Method:** Sonnet research spawn; off-disk metrics inspection + adjacent-field survey (conformal / SDT / LLM-abstention / selective-classification / IR / cortex-external)

---

## Headline

**Root cause of v3/v4/v5 failure is distributional non-separability under adaptive-tau, not a wrong update rule.**

Adaptive tau (sliding-window / Bayesian-CI / percentile / 2-sided percentile) converges to running-mean noisy-confidence ~0.42 which coincidentally matches FIXED tau=0.40 — that is why lift=0.000 (SLIDING_WINDOW) or negative (BAYESIAN_CI at -0.193). No scalar streaming-history-based update rule can climb the precision gradient because the substrate does not expose regime-conditional structure differentially in the score stream.

**Fix mechanism class:** score-based split-conformal prediction with calibration set — tau set from an empirical quantile of known in-KB max_sim scores, NOT from streaming history.

**P_deflated:** 0.38 aggregate (0.55 for conformal path; 0.55 for cortex-external; 0.35 for SDT; 0.20-0.28 for others).

---

## Ranked Mechanism Candidates

### Rank 1 — Score-Based Split Conformal (P_deflated 0.55) ← RECOMMENDED

- **Enters:** held-out calibration set of ~50 items (25 in-KB, 25 OOD) with known labels + substrate's max_sim on those
- **Exits:** tau = (1-alpha)-quantile of in-KB calibration scores; coverage-guaranteed refuse rate ≤ alpha
- **Discriminates:** calibration items and query items exchangeable → same distribution → quantile threshold separates modes
- **Why it works when v3/v4 don't:** decouples calibration problem (how substrate scores known items) from query problem (is this item known?) — no streaming update needed
- **Prior substrate work:** `notes/research_drill_substrate_confidence_continuous_3x_2026-06-10.md` sec 5.1 (CP is coverage-guaranteed for binary decisions); `notes/research_multihop_2x_revival_compound_margin_path_to_2x_drill_2026-06-22.md` (CONFLARE arXiv:2404.04287)
- **Analytical prediction from V_REL sweep result:** noise floor = sqrt(log V_REL / N) → at N=8192, V_C=600, floor=0.040; in-KB max_sim=N(0.80, 0.15), OOD=N(0.04, 0.15) → d'=5.1 SEPARABLE

### Rank 2 — M3-Cortex-External Calibrator (P_deflated 0.55) — PRODUCTION ARCH

- **Enters:** substrate's (max_sim, V_REL, session_entropy) to cortex-side classifier
- **Exits:** binary refuse/accept from cortex
- **Discriminates:** cortex-side context (session history, query rank) that substrate structurally lacks
- **Subsumes Rank 1** — conformal is the special case where cortex classifier = single threshold on max_sim
- Ranked #2 because requires M3 cortex integration; conformal cell (Rank 1) is cheaper proof-of-concept

### Rank 3 — SDT Unequal-Variance (P_deflated 0.35)

- v4 already tried empirical 2-sided tau — TWO_SIDED_SLIDING_WINDOW lift=0.000, TWO_SIDED_PERCENTILE lift=-0.067
- Formal SDT derivation gives same threshold at same distributions
- Only useful IF conformal cheap decisive test shows distributions overlap (d' < 1.5) — currently predicted d'=5.1

### Ranks 4-6 — LLM abstention / selective classification / IR k-cutoff (P_deflated 0.20-0.28)

- LLM abstention (Kadavath / Kuhn / SelfCheckGPT) requires softmax head + temp>0 — substrate has none
- Selective classification (Geifman/El-Yaniv 2017) reduces to conformal for substrate's binary confidence
- IR k-cutoff — substrate refuse is binary, not top-k depth choice

---

## Recommended Cell Design (v6-conformal)

**Arms (4):**
- ARM_FIXED_BASELINE (tau=0.40 v2 CG reproducer, positive control)
- ARM_CONFORMAL_10 (tau = P10 of cal_set max_sim; alpha=0.10)
- ARM_CONFORMAL_20 (tau = P20 of cal_set max_sim; alpha=0.20)
- ARM_CONFORMAL_REGIME (per-regime tau via noise-matched synthetic cal set)

**Gates:**
- HP: ARM_CONFORMAL_10 or _20 refuse-precision ≥ 0.82 at moderate regime (FIXED 0.6667 + 0.15)
- HF: no conformal arm beats FIXED at any regime
- HF_POSITIVE_CONTROL: FIXED @ clean @ OOD refuse_rate < 0.85
- HF_REGIME_COLLAPSE: cal set refuse_spread=0.000 (would falsify d'=5.1)

**Phase axes:** 3 regimes × 3 bands (in-KB, borderline, OOD) × 4 arms = 36 phase points

**Cheap decisive check:** quantile(max_sim of 25 in-KB items @ moderate) vs quantile(max_sim of 25 OOD items @ moderate) — if in-KB quantile > OOD quantile, conformal can separate

**Scale:** N=8192, V_C=600 (v2 CG regime); numpy CPU; 3 seeds (7, 13, 19)

**Cal set size:** 50 items — small enough not to need separate collection

**Discriminator-survives-scale (Fix #C):** smoke at full-N=8192 (numpy CPU-cheap)

---

## Falsifiable Predictions

- **HP-1:** ARM_CONFORMAL_10 refuse-precision ≥ 0.82 at moderate regime (from predicted d'=5.1)
- **HP-2:** quantile(in-KB) - quantile(OOD) ≥ 0.30 on cal set
- **HF-1:** ARM_CONFORMAL_10 refuse-precision ≤ 0.72 (no lift over FIXED)
- **HF-2:** cal-set refuse_spread=0.000 (analytical d' prediction wrong)

---

## Substrate-Design Implications

1. **V_REL sweep HP calibration finding is load-bearing** for this design — sqrt(log V_REL / N) analytical floor gives the OOD mean; conformal quantile lands at 0.50-0.55 predicted, clean mode separator
2. **Calibration set is a natural product primitive** — operator provides anchor examples at M3 deployment; substrate stores quantile
3. **M1.4 should re-scope from "adaptive tau" to "calibration-set tau"** in M3 milestone doc
4. **Cortex-external calibrator is the M3 production architecture** — conformal is the substrate-side proof-of-concept

---

## Citations (7 verified)

1. Vovk, Gammerman, Shafer (2005) — Algorithmic Learning in a Random World. Springer.
2. Angelopoulos & Bates (2021) arXiv:2107.07511 — Gentle Introduction to Conformal Prediction.
3. Shafer & Vovk (2008) — JMLR Tutorial on Conformal Prediction.
4. CONFLARE arXiv:2404.04287 — Conformal LLM Retrieval.
5. Geifman & El-Yaniv (2017) — Selective Classification for DNNs.
6. Macmillan & Creelman (2005) — Detection Theory. 2nd ed.
7. Kadavath et al. (2022) arXiv:2207.05221 — LLMs (Mostly) Know What They Know.
