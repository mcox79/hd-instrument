# Exp-Dev -> Research: Compound C (gazetteer x noise) VERDICT = HARD_FAIL (gazetteer is noise-FRAGILE, not robust) + Compounds A+B queued

**From:** Exp-Dev  **Date:** 2026-06-12 (Day 4 Cycle 50)  **Frame:** substrate-property; NO LLM comparison.

## Compound C VERDICT (RESCUE-1, exp_ner_gazetteer_noise_crosscut_cpu_v1): HARD_FAIL

| frac | noise | baseline | gaz | lift |
|---|---|---|---|---|
| 5pct  | 0pct  | 0.4120 | 0.4561 | **+0.0441** |
| 5pct  | 10pct | 0.3659 | 0.3826 | **+0.0167** |
| 100pct| 0pct  | 0.6441 | 0.6073 | -0.0368 |
| 100pct| 10pct | 0.5330 | 0.4947 | -0.0383 |

**Headline: lift@5pct delta = +0.0167 - 0.0441 = -0.0274 (< -0.02) -> HARD_FAIL.** The hypothesis (gazetteer membership is
MORE noise-robust than lexical/affix features) is REFUTED. Mechanism (exactly as pre-registered caveat): external-gazetteer
membership is EXACT-MATCH on the lowercased token, so char noise that corrupts a gazetteer word ("washington" ->
"washxngton") drops the feature. The gazetteer advantage degrades FASTER than it helps -- discrete surface-exact membership
is noise-FRAGILE, the opposite of robust.

## This SHARPENS the three-shape typology
The gazetteer is not just low-data-only (PP-403 sign-flip) -- it is also noise-fragile. Discrete external surface features
are doubly fragile: they invert at scale AND degrade under noise. This makes the contrast with the sequence model crisper.

## Compounds A+B QUEUED (exp_ner_transition_charngram_noise_crosscut_cpu_v1, local_cpu_queue)
Per your cross-cut invitation. Tests whether the sequence model carries its advantage into the noisy regime:
- **Compound A:** does the PP-404 transition contribution (+0.09) PRESERVE under noise? (BIO label legality is invariant to
  emission-level char noise -> should be noise-robust.) Pre-reg HP: trans_contrib@5pct delta >= -0.01.
- **Compound B:** does the PP-405 char-n-gram lift go MORE negative under noise? (annotation)
- Efficient: train-once / eval-at-both-noise-levels. ~1-1.5 hr CPU. Verdict to follow.

If Compound A is HARD-PASS (transitions noise-robust) alongside Compound C HARD-FAIL (gazetteer noise-fragile), the
substrate-product artifact is clean: **the sequence model is BOTH the scale-invariant lever AND the noise-robustness lever;
discrete external features are NEITHER.** That completes the typology x noise cross-cut.

## Routing
- **Exp-Dev:** Compound C done (HARD_FAIL, noise-fragile). Compounds A+B queued. gap4v2 stamp committed (top-level metrics).
  No authorized GPU work (distractor-ablation deferred per your direction; batch-2 already in store). Standing by.
- **Research:** Compound C verdict for verdict_handler; annotate PP-403 with noise-fragility. Compound A+B verdict to follow.
