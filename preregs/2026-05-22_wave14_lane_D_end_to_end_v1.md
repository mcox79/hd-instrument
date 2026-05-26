# Pre-reg: Wave 14 Lane D End-to-End Cognitive Architecture v1

**Filed:** 2026-05-22
**Bet:** Lane D end-to-end demo (per cap_map v79 Phase 4)
**Predecessor:** `wave14_lane_D_cognitive_arch_smoke_v1` (COMPOSE, S=0.98 T=0.98 U=1.00 X=1.00)

## Question

Can the 4 Lane D primitives chain into a single PIPELINE (output of stage N feeds stage N+1), not just co-exist side-by-side?

The Phase 3 COMPOSE smoke verified primitives don't interfere on a shared substrate. The Phase 4 end-to-end demo verifies they actually wire together — Bet U's accumulated working memory feeds Bet S's pattern completer, the trace feeds Bet T's hypothesis tracker, and the chosen hypothesis indexes Bet X's skill program.

## Hypothesis

H_e2e: composed_acc (all 4 stages right on the same trial) ≥ 0.50. With strong per-stage accuracy (~0.85+), chained multiplication still yields ≥0.50.

H_null: chained errors compound below 0.25 — pipeline collapses; substrate primitives don't actually integrate.

## Pre-declared verdicts

- `LANE_D_E2E_PASS` — composed_acc ≥ 0.50.
- `LANE_D_E2E_PARTIAL` — 0.25 ≤ composed_acc < 0.50 (weakest link identifiable from per-stage rates).
- `LANE_D_E2E_BROKEN` — composed_acc < 0.25 (errors compound; substrate doesn't pipeline).
- `LANE_D_E2E_INCONCLUSIVE` — metric collection error.

## Method

Per trial:
1. Pick true hypothesis k* (1 of K=3).
2. Stream the signature facts of hypothesis k* + 5 noise facts into Bet U EMA buffer B (decay=0.95).
3. Stage 2: probe B for last fact's object via Bet S. Record s_correct.
4. Stage 3: build joint M_T = sum_k h_k * bundle_k; score each hypothesis k by `<M_T * h_k, B_q>` similarity; pred_k = argmax. Record t_correct.
5. Stage 4: decode pred_k's skill program via position-indexed Bet X; record x_correct iff ALL skill_len positions decode correctly.
6. composed = s_correct AND t_correct AND x_correct.

Aggregate: composed_acc = mean(composed) over (seeds × n_trials).

## Acceptance thresholds

- 0.50 threshold accounts for chained-error compounding: at ~0.85 per stage, expected composed ≈ 0.85^3 = 0.61.
- 0.25 lower bound flags pipeline collapse (would imply at least one stage near chance).

## Config

- N=1024 smoke, 4096 full.
- K=3 hypotheses, F=10 facts per hyp (full).
- skill_len=4, skill_alphabet=5.
- n_trials=100/seed, seeds=[17, 23, 31] full.

## Pre-declared interpretation

- **PASS**: substrate-product cognitive architecture is end-to-end viable. Next: stress-test (capacity, noise injection, longer pipelines).
- **PARTIAL**: per-stage rates identify the weakest link. Improve that primitive.
- **BROKEN**: substrate primitives interfere when pipelined despite COMPOSE. Need cross-primitive isolation.

## Not in scope

- Comparison to LLM cognitive architectures.
- Long-horizon pipelines (>4 stages).
- Mixed-precision or quantized substrate.
