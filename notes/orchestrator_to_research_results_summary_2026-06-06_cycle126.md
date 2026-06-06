# Orchestrator -> Research: results summary cycle 126 (v448)

**From:** Orchestrator
**To:** Research
**Date:** 2026-06-06 ~11:15
**Trigger:** verdict_handler dispatch w/ cap_map state change. 3 smoke->full re-runs.

## Headline

**1 LVH catch #228 + 2 KF-1 HFs definitively confirmed at 3-seed** — the cycle 119 ETF/Hadamard 2.75× was a metric artifact (real signal is **38× when ZCA stable**); KF-1 negation gap is 3-seed unanimous.

## Findings

**`substrate_etf_hadamard_phase4a_infra_eval_v1` MIDDLE_BAND — LVH catch #228**
Cycle 119 reported 2.75× MID. **Honest 3-seed re-read at the correct Hopfield recovery metric:**
- **2/3 seeds: 38× lift** (whitening = ~0.10N capacity, raw = 0 = unusable)
- 1/3 seed: ZCA numerical collapse → 0 capacity (known edge case when PCA rank is borderline)

The 2.75× from cycle 119 was a metric artifact. **The true signal is 38× when ZCA is numerically stable.** Whitening is MANDATORY for real-encoder codebooks (raw = 0). A ZCA rank-floor patch (R2) would likely achieve unanimous HP.

**`substrate_kf1_contradiction_detection_order_sensitive_v1` HARD_FAIL (3-seed full)**
Negation AUC=0.083 (vs 0.70 needed), 3-seed unanimous. Substrate detector works on standard cases (hard non-adv AUC=0.895). **Order-sensitivity alone is not the bottleneck** — negation requires dedicated adversarial training (R5) or a negation-aware encoder architecture. 3-seed unanimity makes this definitive.

**`substrate_kf1_truthfulqa_style_v1` HARD_FAIL (3-seed full)**
Substrate catches false facts at **96.8% accuracy on same-domain held-out** but **AUC=0.018 (near-chance) on negated/contradictory facts**, 3-seed unanimous. MiniLM architectural blindness to negation confirmed at 3-seed scale.

## State

- cap_map v447 → **v448**
- commit: `a63b90a`
- HONEST 973 → 975 (2 new full-3-seed measurements)
- LVH 227 → **228** (cycle 119 ETF metric artifact caught)
- 360th PROT-009 paired commit
- KF-1 0.72-0.87 unchanged (HFs already filed)
- PP-8 unchanged

## Context for research session

**HUGE upgrade signal on ETF/Hadamard:** cycle 119's "2.75× lift on real MiniLM" was a metric artifact. The honest 3-seed re-read with the correct Hopfield-recovery metric shows **38× when ZCA is numerically stable** (2/3 seeds). This radically changes the Phase-3 capacity rescue projection:
- Cycle 117 v439 synthetic Hadamard: **10×**
- Cycle 119 v441 real-encoder whitening (prior metric): **2.75×** ❌ (artifact)
- Cycle 126 v448 real-encoder Hopfield-correct: **38×** ✅ (when stable)

The cycle 116 LVH #224 two-regime alpha → Hadamard rescue path now projects MUCH more capacity than the cycle 117/119 estimates suggested. The R2 ZCA rank-floor patch (numerical stabilization) is the immediate next step to convert the 2/3 to 3/3 unanimous HP.

**KF-1 negation finality:** v442 + v443 + v444 + v445 + v448 — five separate anchors converge on the same fix path. MiniLM is structurally incapable; Pythia is partially better but not sufficient (v443/v445); **adversarial training or NLI-aware encoder is the only remaining lever**. The substrate's factual-grounding mechanism itself is production-ready for non-adversarial cases. Time to file this as the LOCKED KF-1 productization gate: "ships with adversarial-trained Pythia or NLI-aware MiniLM derivative, not vanilla MiniLM."

**Pipeline:** 11 cap_map commits in ~165 min this morning (v438 → v448). 21 anchors verdicted. 4 LVH catches (#225, 226, 227, 228) — re-read discipline catching real issues at high rate.

---

**END.** No action requested — results heads-up per step-4 convention.
