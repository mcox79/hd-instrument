# Strategy request: PP-8 Option A HARD-FAIL escalation (with LR-bug honest re-read)

**From**: testbed
**To**: strategy (orchestrator) + user
**Date**: 2026-06-01
**Trigger**: Option A held-out test landed final val 0.000% (HARD-FAIL by strict threshold) but with **mid-training peak val 57.5% at step 250** (588x random; well above HARD-PASS); strategy's HARD-FAIL routing rule prescribes D1-2 layer ablation but honest re-read says the issue is LR-schedule not architecture
**Related**: `notes/testbed_pp8_week2_option_a_held_out_2026-06-01.md` (full deliverable)

## TL;DR

The strict-pre-reg verdict for Option A is HARD-FAIL (final val 0.000%). The HARD-FAIL routing rule says to defer D2/D3 and authorize D1-2 layer ablation. But the empirical pattern doesn't match the failure modes that routing rule was designed to address:

- **Mechanism 1 dominant?** REFUTED by mid-training peak of 57.5% on held-out (requires Phi-3 embedding generalization)
- **FM-5 train/val leak?** REFUTED by the peak being mid-training and val keys being explicitly held-out by index

What actually happened: catastrophic forgetting around step 250-300, same pattern as v1+v1' bundle (98% peak → 38% final on overlap) but more severe here because held-out has no memorization fallback. The cosine-decay LR schedule is destroying a learned retrieval calibration.

Surfacing for strategy re-direction before consuming D1-2 budget on what's likely the wrong probe.

## The empirical pattern (held-out val_top-1 trajectory)

| Step | Val | Comment |
|---|---|---|
| 200 | 1.0% (2/200) | Modest signal; pre-warmup-finish |
| **250** | **57.5% (115/200)** | **PEAK; 588x random** |
| 300 | 0.0% (0/200) | Catastrophic forgetting |
| 350-499 | 0.0% throughout | Unrecovered |
| **Final (1000-sample)** | **0.000%** | HARD-FAIL by threshold |

Loss: 7.43 → 0.09 (98.8% decrease). Model IS optimizing something just not what produces correct argmax.

## Compare v1+v1' bundle (overlap; 38.2% final)

| Step | Val |
|---|---|
| 250 | 98.000% (peak) |
| 300 | 27.500% |
| 400 | 83.000% |
| 450 | 35.000% |
| Final | 38.200% |

Same step-250 peak pattern. v1+v1' bundle recovered partially (overlap = memorization fallback). Option A held-out had no fallback so val crashed to 0% and stayed.

## Recommended decision tree update

### Path 1 (recommended): v1b LR fix on held-out (~$1-2)

Single-anchor dispatch. Same Option A setup but with one or more of:
- Longer warmup (25% vs current 10%)
- Reduced cosine-decay floor (e.g., decay to 30% peak LR, not 0%)
- Early-stopping checkpoint save on best val

**Pre-reg**:
- HARD-PASS (LR-bug interpretation confirmed): held-out val >= 25% stably (within HARD-PASS for original Option A)
- HARD-FAIL (architectural issue exists below LR-bug): held-out val < 5% stably
- MIDDLE (5-25% stably): partial; layer ablation may still help

If v1b PASS, Option A's HARD-FAIL is reversed; D2 + D3 unlock.

### Path 2 (alternative): off-line eval at step 200/250 checkpoint (~free; 5 min eng)

We have checkpoint_step200.pt and checkpoint_step300.pt SCPed back. Load step 200 weights (just before the peak) and run full 1000-sample eval offline. This proves out the peak signal cheaply without a new H100 dispatch.

Actually this might give a different peak number since the SAVED checkpoint is just before step 250, not exactly at it. But we can also load step 300 (post-collapse) and confirm the val crashed there too.

Empirical validation that mid-training was real. Quick + free.

### Path 3 (strategy's original): D1-2 layer ablation (~$3-6)

Tests "is Phi-3 last-layer hidden the right probe point?" by sweeping over earlier layers. The empirical 57.5% mid-training peak says last-layer IS load-bearing — the answer is likely "yes, last layer is fine; LR is the bug." So D1-2 is now lower-priority by the LR-bug interpretation.

## My recommendation

**Path 2 first (~free; 5 min)**: prove the mid-training peak is real via offline checkpoint eval. If checkpoint_step200 + checkpoint_step300 reproduce the val trajectory (1% → peak → 0%), the LR-bug interpretation is locked in.

**Then Path 1 (~$1-2)**: v1b LR fix dispatch. If it produces stable held-out val >= 25%, we have a clean Option A PASS by-honest-reading and D2 + D3 unlock.

**Defer Path 3** unless Path 1 fails (lower-likelihood now).

## Cap_map implications (your scope)

- PP-8 row currently at 0.55-0.65 → 0.60-0.75 (after v1+v1' HARD-PASS LIFT)
- If v1b confirms stable held-out PASS: full Mechanism 2 (Phi-3 embedding generalization) validated → consider further LIFT
- If v1b fails: leave at current band + caveat about LR-tuning headroom

## Cost state

- Cumulative session Lambda: $13.34 (well under $50 cap; well under $50-150 envelope)
- Path 2: free
- Path 1: ~$1-2
- Cumulative if both: ~$15

## Open: D1-1 still pending

D1-1 control test (frozen-random keys) has stuck-boot fast-failed TWICE (~$0.72 sunk). Need to re-dispatch when Lambda capacity opens (likely both Option A retry + D1-1 attempts hit the simultaneous-instance capacity wall the account has 2-instance limit on H100 SXM5 today). Will re-dispatch D1-1 as a 3rd attempt now that Option A is terminated.

## Files referenced

- This routing
- `notes/testbed_pp8_week2_option_a_held_out_2026-06-01.md` (full deliverable with trajectory data)
- `notes/testbed_pp8_week2_phase25_v1_v1prime_2026-06-01.md` (v1+v1' bundle for comparison)
- `notes/routed_completed/strategy_response_to_testbed_pp8_round4_d1_1_plus_a_authorized_2026-06-01.md` (original authorization + HARD-FAIL routing rule)
- `data/lambda_batch_results/pp8_w2_option_a_held_out_h100_n4096_335bf875/checkpoint_step{200,300}.pt` (for offline Path 2 eval)


Acted-on 2026-06-01: rolled up into research's v1b+Path A 2-drill synthesis; v1b WSD+EMA mitigation authorized via testbed routing pp8_v1b_lr_fix_plus_path_a_10cell
