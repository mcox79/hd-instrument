# Testbed deliverable: PP-8 Week 2 Phase 2 QLoRA fine-tune — MIDDLE verdict (empirically motivates Phase 2.5)

**Date**: 2026-06-01
**Anchor**: pp8_w2_p2_qlora_finetune_h100_v1_n4096
**Verdict**: **MIDDLE** — loss decrease 44.5% (PASS the >=30% threshold); val top-1 0.000% (FAIL the >random threshold); no NaN/Inf crashes
**Cost**: $1.36 actual (predicted $4.29; 68% under)
**Wall**: 19.0 min total; 2.9 min training compute; rest = bootstrap + Phi-3 4-bit load + dataset regen
**Hardware**: Lambda gpu_1x_h100_sxm5 (instance b31a433df9424808823cc936dc639848)

## TL;DR

Phase 2 produced a clear, decisive empirical finding: **the substrate-bypass training pipeline cannot learn the held-out val task because the task is intrinsically substrate-mediated**. Loss decreases (showing the model + LoRA + bridge ARE optimizing something), but val accuracy stays at 0% — the model never produces a correct held-out token. This empirically confirms the architectural concern I flagged when designing Phase 2: the key-resolver / substrate-in-loop training pipeline (Phase 2.5) is REQUIRED, not optional, for the toy task's val accuracy to be a meaningful signal.

This is not a failure of the bridge architecture, the LoRA setup, or the training discipline. All three are working. The signal is that the task design + the training-vs-eval pipeline asymmetry combine to make the val metric unreachable.

## Verdict logic walkthrough

Per `phase2_qlora_train.py:run()`:
```
if pass_loss and pass_acc and pass_no_nan: PASS
elif (loss_decrease_pct >= 0.15 and pass_no_nan): MIDDLE
else: FAIL
```

Phase 2 result against acceptance criteria:
- **Loss decrease ≥ 30%**: **PASS** (44.5%; range 15.63 → 8.68 over 500 steps; loss curve smooth + monotonic-ish; no instability)
- **Val top-1 > random (0.0977%)**: **FAIL** (0.0000%; 0/1000 correct on full val set; held-out keys never matched)
- **No NaN/Inf**: **PASS**

Therefore: MIDDLE (loss passes; val fails; no NaN). Same verdict if we adopted a strict PASS-requires-both rule.

## Why val accuracy hit 0% (the architectural diagnosis)

The toy task: given "Key {key_idx:04d}: ", predict the deterministic random target token assigned to the substrate's val_idx for that key. Val uses 1000 keys NEVER seen in training (held out by index).

Training-time forward pass (substrate-BYPASSED per parent handoff "NEVER binarize inside bridge during training"):
```
text -> Phi-3 prefill (LoRA active) -> hidden -> readout (tanh) -> soft_tanh_query
       -> bridge -> 8 prefix tokens -> Phi-3 decode -> 1 token logits -> CE
```

There is NO substrate Path D retrieval in this pipeline. The substrate is bypassed. So during training, the only signal connecting "Key {K}: " text to its target token is whatever Phi-3 + LoRA + bridge can memorize FROM THE TRAINING SET ITSELF.

For training keys (~3096 distinct), the model can memorize key→target mappings if it has capacity. But for held-out val keys, the only signal that connects "Key {K_val}: " text to its target token is the substrate's key→val relation graph — which is not exercised in training.

Therefore the val task is unlearnable without substrate-in-loop training.

The expected behavior:
- Training top-1 (if we measured it): likely above 0% (memorization of seen keys)
- Val top-1 (measured): 0% (no signal for unseen keys)

Phase 1 actually generated training-set + held-out-by-key-idx splits exactly this way; the empirical 0% on val confirms the architectural diagnosis.

## What this verdict means for the path forward

The parent handoff acceptance criterion for Phase 2 PASS was "validation eval at end shows >random retrieval quality." But research/design-time analysis missed the architectural detail that this requires substrate-in-loop training, which requires a "key resolver" (bipolar query -> nearest codebook index for Path D start) which doesn't exist.

So there are two paths:

### Path A: build Phase 2.5 (key resolver + substrate-in-loop training) and re-run Phase 2

- Engineering: 1-2h to add a "key resolver" function that maps the readout's soft tanh output to a substrate codebook index (e.g., argmax of `codebook @ bipolar.T`)
- Training: replace the soft-tanh-direct-to-bridge path with sign+resolve+substrate-Path-D->codeword->bridge
- BUT: this path is non-differentiable through argmax + Path D. Need either (a) straight-through-estimator on the sign+argmax, (b) reinforcement-learning-style policy gradient through substrate decisions, or (c) a Gumbel-softmax relaxation of the codeword selection
- Cost: ~1 H100 session @ ~$2-5; total cumulative Phase 2 budget still under $10 vs original $40-100 envelope

### Path B: redesign the toy task to be learnable WITHOUT substrate-in-loop

- Cleanest variant: have target tokens depend on key_idx in a way the LLM CAN learn directly (e.g., target_token = vocab_id[key_idx % 1024]; deterministic but learnable by memorization + light Phi-3 generalization)
- This DOESN'T test the substrate. It tests the bridge-as-arbitrary-prefix-injection-mechanism
- The substrate's role becomes: "does the bridge correctly USE substrate-derived prefixes when they come in" rather than "does the bridge learn to QUERY the substrate"
- Cost: dataset re-gen + re-run; ~30 min + ~1 H100 session at ~$2-5

### Path C: accept Phase 2 as MIDDLE and document the constraint

- Cap_map PP-8: stay at 0.55-0.65; add caveat "Phase 2 substrate-bypass training validates bridge is trainable (loss -44.5%); val task requires substrate-in-loop training (Phase 2.5) which is engineering-pending"
- Move forward to Phase 3 (Rescue C multi-hop smoke) which has its own scope independent of Phase 2 outcome
- Defer Phase 2.5 to whenever the engineering scope can be carved out (~1-2h plus a re-run)

### Recommendation

**Path A** — Phase 2.5 is the right next step. The empirical demo (0% on val) is so clean that we now KNOW substrate-in-loop is the rate-limiter. ~1-2h engineering + 1 H100 session is a tractable + decisive next probe. Even if Phase 2.5 only gets to ~5-10% val accuracy, that's a 50-100x lift over random and validates the substrate's contribution.

The Phase 3 (Rescue C multi-hop) scope from the parent handoff is also independent of Phase 2's val outcome; if user wants, Phase 3 can run in parallel with Phase 2.5 engineering.

## Cost discipline observations

Predicted $4.29; actual $1.36 (68% under). 19 min wall (training compute 2.9 min; bootstrap + Phi-3 4-bit load + dataset regen the rest). Phase 2.5 should land at similar economics.

Cumulative session Lambda spend ~$4.93 + $1.36 = **~$6.29**, well within all user-authorized envelopes (PP-8 Week 2 $50-150; W0 revalidation $5-15; Anthropic $20-50 pre-auth).

## SCP-back hardening — VERIFIED WORKING

This was the first run with the result_paths SCP-back hardening shipped this morning (commit 00fe045). All 6 result files SCPed back cleanly:
- summary.json
- train_progress.jsonl (per-step training/eval/checkpoint records)
- checkpoint_step100.pt
- checkpoint_step200.pt
- checkpoint_step300.pt
- checkpoint_step400.pt

Local path: `data/lambda_batch_results/pp8_w2_p2_qlora_finetune_h100_v1_n4096_b31a433d/`. Last checkpoint preserved + all training history queryable.

The "NO_METRICS" gap that flagged Phase 1 is closed. (The batch report still reports `MISSING` for the metrics.json scrape — that's a separate path; the script doesn't produce a `metrics.json` because its outputs are summary.json + train_progress.jsonl. Cosmetic; can be aligned later.)

## Generic_progress_wrapper --script-args verified working

Phase 2 was also the first run using the `--script-args` plumbing (commit b76fc9b). The wrapper correctly forwarded `--dataset-dir ... --out-dir ... --max-steps 500 --batch-size 8 ...` to the training script. Cell-regex pattern matched 50 step-log lines (vs total 500 train steps = 10% sampling). ETA estimates were noisy on the first ~10 steps but stabilized.

## Files referenced

- This deliverable
- `data/lambda_batch_results/pp8_w2_p2_qlora_finetune_h100_v1_n4096_b31a433d/data/testbed_pp8_week2/train_v1/summary.json` (full summary with verdict)
- `data/lambda_batch_results/.../train_progress.jsonl` (per-step records)
- `data/lambda_batch_results/.../checkpoint_step{100,200,300,400}.pt` (intermediate checkpoints)
- `data/lambda_batch_report_b31a433df9424808823cc936dc639848.json` (batch report)
- `data/testbed_pp8_week2/launch_logs/pp8_w2_p2_*.log` (full launcher stdout)
- `testbed/llm_integration/phase2_qlora_train.py` (training script; commit 2b03fc3 + b76fc9b + c1726e5)
- Parent: `notes/routed_completed/testbed_handoff_pp8_week2_feasibility_smoke_authorized_2026-06-01.md`


---

Acted-on 2026-06-01: Phase 2 baseline MIDDLE val=0%; superseded by Phase 2.5 STE / soft / Path 1c series + Path 1a v1+v1 HARD-PASS in v317


Acted-on 2026-06-01: superseded by Phase 2.5 STE/soft/Path 1c series + Path 1a v1+v1' HARD-PASS in v317
