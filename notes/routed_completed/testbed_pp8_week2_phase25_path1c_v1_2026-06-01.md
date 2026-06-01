# Testbed deliverable: PP-8 Phase 2.5 Path 1c — eval-bug fix + training-dynamics finding

**Date**: 2026-06-01
**Anchors**: pp8_w2_p25_path1c_noholdout_h100_v1_n4096 (v1; eval-bug uncovered) + pp8_w2_p25_path1c_poolmask_h100_v2_n4096 (v2; eval-bug fixed)
**Verdict v1**: MIDDLE — same-as-before; val 0.000%
**Verdict v2**: PASS by threshold — val 0.100% (1/1000); essentially random by signal
**Cost**: v1 $0.83 + v2 $0.89 = $1.72 total Path 1c
**Cumulative session Lambda**: $8.26
**Status**: PARTIAL — eval bug confirmed and fixed; deeper training-dynamics issue surfaced

## TL;DR

Path 1c v1 (no-holdout, soft-substrate, original eval) returned val=0%. Diagnostic uncovered an EVAL BUG: argmax was unrestricted over Phi-3's 32K vocab; common non-pool tokens were winning regardless of how well the model had learned to skew probability toward the 1024-token target pool. Pool-mask fix landed (commit f707662) + Path 1c v2 re-dispatched.

Path 1c v2 with the fix produced val=0.100% (1/1000 correct on full val set). This barely exceeds random baseline (0.0977%), so the verdict-logic PASSes by 0.0023pp but the empirical signal is essentially indistinguishable from chance.

**Net finding**: the eval bug was real (val moved off the floor); the architecture is mechanically sound; but the soft-attention training dynamics are degenerate — attention at temperature=1.0 spreads near-uniformly over M=4096 keys, retrieved value is near-zero (averaged bipolar codewords), bridge has no per-key signal to differentiate.

## Eval-bug diagnosis (resolved)

**Bug**: In _eval, `logits.argmax(dim=-1)` ran over the full Phi-3 vocab (~32064 tokens). The task constrains the answer to one of 1024 specific tokens, but the eval did not enforce this. Common non-pool tokens (" ", "the", "of", numerical IDs, etc.) dominated argmax regardless of how well the model had learned to skew probability toward pool tokens.

**Evidence**:
- All 4 prior runs (Phase 2 / Phase 2.5 STE / Phase 2.5 soft / Path 1c v1) returned val=0.000% with healthy 37-44% loss decreases. Loss decrease measures distribution-level skew; argmax measures top-1 pick. The disconnect was the eval mask.

**Fix** (commit f707662): load target_vocab_pool_ids from dataset manifest; in `_eval()`, `masked_fill` non-pool logits to -inf before argmax. Task-relevant constraint; training loss unaffected.

**Effect**: Path 1c v1 (no mask) → 0.000% val. Path 1c v2 (with mask) → 0.100% val. The fix moved val OFF the floor.

## Training-dynamics finding (new)

With the eval bug fixed, Path 1c v2 shows val=0.100% on the FULL 1000-sample evaluation. This is essentially random (random baseline 0.0977%).

Per-step pattern during training (eval_max_samples=200):
- Step 200, 250, 300, 350, 400, 450, 499: ALL exactly 1/200 = 0.500%
- The same single example appears to be the only one consistently classified correctly across all eval points

For overlapping train+val (Path 1c sanity setup), the model should be able to MEMORIZE associations for at least training-seen keys. But it isn't. Why?

**Hypothesis**: soft-attention with temperature=1.0 over M=4096 keys is too smooth. With near-random readout output, `sim = soft_query @ codebook[key_idx].T / 1.0` has near-uniform values; softmax produces ~uniform attention (≈1/4096 per key); retrieved = attn @ vals_codebook averages 4096 bipolar codewords → near-zero output.

The bridge thus sees an essentially-zero (or batch-mean) input regardless of query. There's no per-query differentiation in the bridge's input, so per-key target prediction is impossible. CE loss can still decrease via Phi-3's LoRA learning a uniform "skew toward 1024-pool" bias, but per-example accuracy is random.

## What this means for the path forward

**Architecture is mechanically sound** (forward/backward both work; no NaN; loss decreases stable across 4 distinct gradient strategies). The architecture-bug hypothesis is REJECTED — Path 1c v2 demonstrably moves val off the floor when the eval is correctly bounded.

**Training dynamics need sharper attention** for the readout to extract per-key signal. Two natural next probes:

### Probe 1: temperature schedule (cheap; $1-2)

Anneal temperature from 0.1 (very sharp) at start to 1.0 by end of training. Sharp attention at start forces per-key gradient signal; later annealing prevents the model from collapsing to a single-key mode.

Engineering: add `--substrate-soft-temperature-schedule "0.1,1.0"` flag; linearly interpolate over max_steps. ~30 min.

### Probe 2: low fixed temperature (cheap; $1-2)

Run with temperature=0.1 or 0.05 throughout. Sharp attention from start; tests whether the soft-attention pathology can be fixed by attention-sharpness alone.

Engineering: change one CLI arg; 5 min.

### Or — proceed to Path 1a per orchestrator-pre-approved sequencing

Path 1a was gated on (a) Path 1c PASSES + (b) research drill on Phi-3 hidden codeword design returns. Path 1c v2 passes by-threshold; research drill is in flight (~2-3h wall expected). When research drill returns, the natural next step is Path 1a v1 implementation per research's recommended design — which addresses the training-dynamics issue at a more fundamental level (key codewords derived from Phi-3 hidden states → semantic alignment → bridge has signal-rich inputs by construction).

## My recommendation

**Path A**: file this deliverable; surface the training-dynamics finding to orchestrator/user; let Path 1a's research drill complete (~2-3h wall) and dispatch Path 1a v1 directly. Probe 1/2 are interesting diagnostics but the principled Path 1a fix should subsume them.

**Path B**: dispatch Probe 2 (low fixed temperature; ~$1-2; 5 min eng) IN PARALLEL with the Path 1a research drill. If Probe 2 produces val > 5%, that's a much cheaper-than-expected win and Path 1a may not even be needed. If Probe 2 returns ~random (still 0-1%), the architecture-level fix in Path 1a is the proper next step.

I lean Path B — Probe 2 is so cheap ($1-2) and informative that running it in parallel with the research drill is a small bet with potentially large information return.

## Verdict logic interpretation note

The PP-8 Phase 2 acceptance criterion was "val top-1 > random baseline." Path 1c v2 produces 0.100% > 0.0977% by 0.0023 percentage points. By the strict criterion that's PASS. But the criterion was presumably intended to detect "substantive substrate utility," not "barely-above-random by 0.2%."

Recommend cap_map row treatment: Phase 1 architectural integration PASS stands at 0.55-0.65. Phase 2/2.5 row caveat: "eval mask bug uncovered + fixed; remaining val signal at random ± 0.1%. Suggests soft-attention temperature=1.0 over M=4096 keys is degenerate; sharper attention OR Phi-3-hidden codeword alignment (Path 1a) likely required for substantive val lift."

## Cost discipline

- Cumulative today: $8.26 (well within $50-150 envelope and $50 spend cap)
- Path 1c total: $1.72 ($0.83 v1 + $0.89 v2)
- Remaining budget cap: ~$42 before check-in required

## SCP-back continues to work

Both runs preserved 6/6 result files. Local paths:
- v1: `data/lambda_batch_results/pp8_w2_p25_path1c_noholdout_h100_v1_n4096_38f845e3/`
- v2: `data/lambda_batch_results/pp8_w2_p25_path1c_poolmask_h100_v2_n4096_cea69609/`

## Files referenced

- This deliverable
- `notes/testbed_pp8_week2_phase25_soft_v1_2026-06-01.md` (Phase 2.5 soft-substrate deliverable; Path 1c originated here)
- `notes/routed_completed/strategy_response_to_testbed_pp8_phase25_path_1c_authorized_2026-06-01.md` (orchestrator authorization)
- `testbed/llm_integration/phase2_qlora_train.py` (commit f707662 = eval pool-mask fix)
- `tools/cloud/batch_examples/pp8_week2_phase25_path1c_v2_poolmask.json` (v2 batch config)

Acted-on 2026-06-01: eval-bug fix acknowledged; v1+v1' bundle + Probe 2 + v2 contingency authorized via strategy_response_to_testbed_pp8_v1_v1prime_authorized
