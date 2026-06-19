# Testbed deliverable: PP-8 Week 2 Phase 2.5 (STE iteration) — MIDDLE; STE bypasses substrate gradient signal

**Date**: 2026-06-01
**Anchor**: pp8_w2_p25_qlora_substrate_in_loop_h100_v1_n4096
**Verdict**: **MIDDLE** — loss decrease 37.8% (PASS the >=30% criterion); val top-1 0.0000% (FAIL the >random criterion); **essentially identical to Phase 2 substrate-bypass baseline** (44.5% / 0.0000%)
**Cost**: $1.30 actual / $3.58 predicted (63% under)
**Wall**: 18.2 min total; 2.9 min training compute
**Hardware**: Lambda gpu_1x_h100_sxm5 (instance 1b776a3d450e4a1a8b9b6584a18ddda1)

## TL;DR

The STE (straight-through estimator) implementation of substrate-in-loop training produced VAL ACCURACY IDENTICAL to the Phase 2 substrate-bypass baseline. This is the kind of result the orchestrator's pre-approval contingency was anticipating: STE through the substrate's discrete cleanup-and-relation-lookup empirically does not produce a useful training signal for the held-out val task. **Iteration 1 of 3 in the pre-approved STE/Gumbel contingency budget is now consumed**; next attempt should switch to Gumbel-softmax or a "soft substrate" formulation.

## Result comparison vs Phase 2 baseline

| Metric | Phase 2 (bypass) | Phase 2.5 STE (this) |
|---|---|---|
| Loss decrease | 44.5% | 37.8% |
| Val top-1 | 0.000% | 0.000% |
| NaN/Inf | none | none |
| Cost | $1.36 | $1.30 |
| Wall | 19.0 min | 18.2 min |

The substrate-in-loop training added essentially zero learning signal compared to bypass. This is the empirical "STE gradient pathology" the orchestrator's pre-approval anticipated.

## Diagnosis: why STE doesn't carry val-relevant signal

The STE formulation:

```
substrate_retrieve_ste(soft_query):
  with no_grad:
    bipolar = sign(soft_query)
    nearest_pos = argmax(codebook[key_idx] @ bipolar.T)
    nearest_key = key_idx[nearest_pos]
    v = relation[nearest_key]
    retrieved = codebook[v]
  return soft_query + (retrieved - soft_query).detach()
```

Forward: returns `retrieved` (the correct value codeword if cleanup succeeded).
Backward (d/d_soft_query): returns identity. The gradient flowing back to soft_query tells it "be more like the bridge input that produces a better prefix" — but does NOT tell it "produce a different bipolar query that would cause the discrete cleanup to select a different key (and therefore a different value)."

In other words: the STE gradient TREATS substrate retrieval as a no-op for backward purposes. The optimizer learns to make `soft_query ≈ retrieved` (since gradient pushes them together), which is degenerate — the readout can either:
- (a) directly produce value codewords (which doesn't generalize to held-out keys, since readout doesn't see val keys in training)
- (b) learn to produce queries that the bridge can use AFTER fixed retrieval (which is just substrate-bypass under a different name)

Either way, the substrate's key→value discriminative function (the relation graph that's the whole POINT of the substrate) does not contribute to the gradient signal that updates the readout.

## What loss-decrease is measuring (not val task)

Loss decreased 37.8% over 500 steps but val accuracy stayed at 0%. The model IS optimizing something:
- Phi-3 vocab ~32K; CE at uniform = ln(32064) ≈ 10.37 nats
- Loss range: 14.16 → 8.80 (final below uniform; model is beating random)

What it's learning: probably a "skew the output distribution toward the 1024-token target pool" prior. CE loss measures this kind of pool-level bias regardless of per-key correctness. But argmax for any specific val example picks one specific token; if that token isn't the held-out target, accuracy = 0%.

Phase 2.5 LOSS-LEVEL signal is the same kind of pool-level skew Phase 2 learned. The STE didn't enable per-example key→value learning because the substrate's discrete cleanup never contributes to the gradient.

## SCP-back hardening continues to work

All 6 result files preserved: summary.json + train_progress.jsonl + 4 checkpoints (step 100/200/300/400). Local path `data/lambda_batch_results/pp8_w2_p25_qlora_substrate_in_loop_h100_v1_n4096_1b776a3d/`.

## Cost discipline

Cumulative session Lambda: $5.68 today ($4.93 yesterday + Phase 1 + Phase 2 + this Phase 2.5 STE). Remaining contingency budget (per pre-approval): 2 more iterations + ~$28 + most of a working-day before architectural-pivot escalation.

## Path forward — within pre-approval contingency budget

Per orchestrator pre-approval:
> "if STE attempts fail to converge and Gumbel-softmax also fails, testbed has the engineering bandwidth to iterate (~2-3 additional 1-2h engineering cycles) WITHIN the existing PP-8 Week 2 envelope before escalating to user for architectural-pivot decision."

I've consumed 1 of those iterations (STE). The natural next attempt is **Gumbel-softmax** OR an even simpler **"soft substrate"** (attention-weighted retrieval over keys).

### Iteration 2 candidate: soft-substrate-readout (recommended)

The cleanest mathematical formulation: replace the argmax + relation-lookup with a SOFT attention-weighted retrieval that flows gradients naturally.

```
substrate_retrieve_soft(soft_query):
  # sim: (B, M) similarity between query and each key
  sim = soft_query @ codebook[key_idx].T / temperature
  attn = softmax(sim, dim=-1)  # (B, M) over keys
  # Look up val codewords for ALL keys
  val_codewords = codebook[val_idx_per_key]  # (M, n_sub)
  # Attention-weighted sum
  retrieved = attn @ val_codewords  # (B, n_sub)
  return retrieved
```

This is fully differentiable. The gradient tells the readout: "the way to get a better retrieval is to put more attention weight on key K_i, which means making soft_query more similar to codebook[key_idx_K_i]."

The temperature parameter controls how "discrete" the retrieval is:
- High temperature (>10): smooth average over all keys; weak inductive bias but easy gradient
- Low temperature (<0.1): nearly argmax; strong substrate signal but vanishing gradient
- Schedule: start at temperature=10 (smooth), anneal to 1.0 by end of training

This is in spirit the orchestrator's "Gumbel-softmax" suggestion but simpler (no stochastic sampling needed for inference; just softmax-weighted average).

### Iteration 3 candidate (if soft-substrate fails): Gumbel-softmax with hard ST

Use Gumbel-softmax with the "hard" output during forward (one-hot key selection) but soft gradient during backward. Adds noise at training time which can help escape the "soft-substrate" optimization plateau. More complex; only attempt if soft-substrate doesn't show val lift.

## Recommendation

**Dispatch iteration 2 (soft-substrate-readout)** within pre-approval budget. Engineering: ~30-60 min (modify `_substrate_retrieve_ste` → `_substrate_retrieve_soft` with temperature parameter; add `--substrate-soft-temperature` arg). Cost: ~$1.30-2 per H100 session.

Acceptance criterion for iteration 2:
- **STRONG PASS**: val top-1 > 5% (50x random; substrate signal demonstrably contributes)
- **WEAK PASS**: val top-1 in [1%, 5%] (substrate signal contributes but training pipeline needs further refinement; consider iteration 3 Gumbel)
- **FAIL**: val top-1 < 1% (soft-substrate also doesn't extract substrate signal; escalate to user for architectural pivot)

## Files referenced

- This deliverable
- `data/lambda_batch_results/pp8_w2_p25_qlora_substrate_in_loop_h100_v1_n4096_1b776a3d/data/testbed_pp8_week2/train_v25/summary.json` (verdict summary)
- `data/lambda_batch_results/.../train_progress.jsonl` (per-step records)
- `data/lambda_batch_results/.../checkpoint_step{100,200,300,400}.pt`
- `notes/testbed_pp8_week2_phase2_qlora_v1_2026-06-01.md` (Phase 2 baseline comparison)
- `notes/routed_completed/strategy_response_to_testbed_pp8_phase25_path_a_authorized_2026-06-01.md` (pre-approval w/ 3-iteration contingency budget)
- `testbed/llm_integration/phase2_qlora_train.py` (training script; STE implementation in `_substrate_retrieve_ste`)


---

Acted-on 2026-06-01: STE iteration MIDDLE identical to Phase 2 baseline; pattern recognized; superseded by Path 1a v1+v1 breakthrough


Acted-on 2026-06-01: STE iteration MIDDLE; superseded by Path 1a v1+v1' breakthrough
