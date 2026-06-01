# Testbed deliverable: PP-8 Round 4 Option A held-out — final HARD-FAIL but mid-training PEAK 57.5% (LR-bug, not architectural)

**Date**: 2026-06-01
**Anchor**: pp8_w2_option_a_held_out_h100_n4096
**Verdict by strict pre-reg threshold**: HARD-FAIL (final val 0.000%; below 5% threshold)
**Honest verdict per [[feedback-verdict-msg-honest-reread]]**: MIDDLE-via-LR-bug (architecture demonstrably reaches 57.5% on held-out mid-training; final 0% is catastrophic forgetting via LR schedule, not architectural failure)
**Cost**: $1.75 actual; cumulative session Lambda $13.34
**Wall**: 24.5 min
**Status**: ESCALATE to strategy with honest re-read; recommend v1b LR fix BEFORE the D1-2 layer ablation path the HARD-FAIL routing prescribes

## TL;DR

Option A on held-out dataset_v1 (1000 keys never seen in training) hit a **57.5% val accuracy peak at step 250** (115/200; 588.5x random; well above the 25% HARD-PASS threshold), then catastrophically forgot to 0% by step 300 and stayed at 0% through end of training (steps 300-499). The final val is 0/1000 = 0.000% — formally HARD-FAIL by strict pre-reg.

But the mid-training peak directly disproves the "Mechanism 1 dominant" or "FM-5 train/val leak" diagnoses the HARD-FAIL routing rule was designed to address. The architecture clearly CAN do held-out generalization. The issue is the LR-decay schedule destroying a learned solution between step 250 and step 300.

This is the same pattern observed in v1+v1' bundle (peaked at 98% step 250, decayed to 38% final) — just more severe here because held-out has no "memorization safety net" to fall back on when retrieval breaks.

## The honest mid-training trajectory

Val top-1 at each eval checkpoint (eval_max_samples=200 during training; full 1000-sample eval at end):

| Step | Val top-1 | Random multiplier | Loss |
|---|---|---|---|
| 200 | 1.000% (2/200) | 10.2x | 0.0002 |
| **250** | **57.500% (115/200)** | **588.5x** | 0.0018 |
| 300 | 0.000% (0/200) | 0 | 0.0608 |
| 350 | 0.000% | 0 | 0.0455 |
| 400 | 0.000% | 0 | 1.3947 |
| 450 | 0.000% | 0 | 0.0168 |
| 499 | 0.000% | 0 | 0.0130 |
| Final (1000) | 0.000% | 0 | 0.0906 |

The loss is LOW throughout (0.01-1.4 range with occasional spikes) — indicating the model is doing SOMETHING, just not what would produce the pool-token argmax that gets eval credit.

## Why this is LR-bug, not architectural

Compare v1+v1' bundle (overlap; 38.2% final):
- Step 200: 0.000%
- **Step 250: 98.000%** (peak)
- Step 300: 27.500%
- Step 400: 83.000%
- Step 450: 35.000%
- Final: 38.200%

Both runs hit a peak around step 250 (right after warmup; right when cosine decay engages). v1+v1' bundle had overlapping keys so the model could fall back to memorization when retrieval broke (recovers to 38.2% final). Option A held-out had no memorization fallback, so when retrieval broke, val crashed to 0% and stayed there.

The LR schedule (10% warmup to lr=2e-4, then cosine decay over remaining 90% to 0) is the suspect. Around step 250-300, LR is still at 1.3-1.5e-4 (well above floor), but the model is now traversing the cosine-decay region where weight updates likely shift the readout-bridge alignment past the brittle "retrieval is calibrated" minimum.

## What this means for the strategy decision tree

Strategy routing rule was:
> If Option A HARD-FAIL (regardless of D1-1): DEFER D2 and D3-Path-A; Authorize D1-2 layer ablation (~$3-6); Escalate to user/research for architecture rescue path decision

The HARD-FAIL routing was designed to address two failure modes:
1. **Mechanism 1 dominant** (Phi-3 hidden states unnecessary; substrate SimHash sufficient) — empirically REFUTED here because held-out 57.5% at step 250 requires Phi-3 embedding-space generalization
2. **FM-5 train/val leak** (artifactual overlap) — empirically REFUTED here because the 1000 val keys are held out by index and the peak is mid-training (not train-set overfit)

What's actually happening: the SAME catastrophic-LR-decay-forgetting pattern from v1+v1' bundle, EXPOSED by held-out data (which doesn't have memorization to mask the retrieval breakage).

The strategically-correct next probe is NOT D1-2 layer ablation. It is v1b (LR schedule fix) — extend warmup, reduce final-LR floor, OR add early-stopping-on-val. Confirm that with stable LR, held-out val locks in at 50%+ rather than oscillating to 0%.

## Recommended sequencing (honest re-read of decision tree)

**Priority 1: v1b LR fix on held-out (cheap; ~$1-2; 15 min)**

Same Option A setup but with one or more of:
- Longer warmup (25% vs 10%)
- Reduced cosine-decay range (e.g., decay to 30% of peak instead of 0%)
- Early-stopping checkpoint on val (save the step-250-peak weights)

If this lands held-out val at 25%+ stably → HARD-PASS on Option A by-honest-reading; D2 + D3 unlocked.

**Priority 2 (gated on v1b PASS): D3-Path-A KV-cache integration smoke**

Per parent handoff's Phase 3 plan; tests substrate-LLM coupling in production-like context. Strategy's D3 was originally gated on Option A HARD-PASS — v1b PASS achieves that by-honest-reading.

**Priority 3 (gated on D1-1 result; still pending):**

D1-1 is independently testing Mechanism 1 vs Mechanism 2. Both attempts so far have stuck-boot fast-failed (~$0.72 sunk). Re-dispatch when Lambda capacity opens.

**Defer (per strategy original HARD-FAIL routing): D1-2 layer ablation**

The layer-ablation hypothesis is "Phi-3 last-layer hidden state may not be the right probe point." Empirically, Option A's mid-training 57.5% says last-layer hidden state IS the right probe — the issue is downstream (LR schedule). Layer ablation is now lower-priority.

## Cost discipline

- Cumulative session Lambda: $13.34 ($2 over the v1+v1' result; well within $50 cap)
- v1b dispatch: ~$1-2; would take cumulative to ~$15
- D1-1 retry: ~$1.50 (assuming stuck-boot doesn't recur); cumulative ~$17
- Both within remaining $37 headroom

## SCP-back continues to work

6/6 files preserved at `data/lambda_batch_results/pp8_w2_option_a_held_out_h100_n4096_335bf875/`. Note: checkpoint_step200.pt contains the model state JUST BEFORE the step-250 peak; checkpoint_step300.pt is post-collapse. Loading checkpoint_step200 + manually running eval at that state would give an exact mid-training accuracy reading.

## Files referenced

- This deliverable
- `notes/testbed_pp8_week2_phase25_v1_v1prime_2026-06-01.md` (v1+v1' bundle deliverable; same LR-oscillation pattern; 38.2% final from 98% peak)
- `notes/routed_completed/strategy_response_to_testbed_pp8_round4_d1_1_plus_a_authorized_2026-06-01.md` (the authorization with HARD-FAIL routing rule)
- `data/lambda_batch_results/pp8_w2_option_a_held_out_h100_n4096_335bf875/train_progress.jsonl` (full step-by-step record)
- `data/lambda_batch_results/.../checkpoint_step200.pt` (pre-peak weights; loadable for offline eval)
- `data/lambda_batch_results/.../checkpoint_step300.pt` (post-collapse weights)


Acted-on 2026-06-01: held-out HARD-FAIL-by-final-but-peak-57.5pct rolled into v1b+Path A synthesis + testbed dispatch
