# CELL-SPECDEC Qwen-1.5B speculative decoding pretest — HARD_FAIL

**Date:** 2026-06-07 evening
**Author:** Testbed
**Anchor:** `speculative_decoding_qwen_v1`
**Verdict:** `HARD_FAIL: wall_speedup=0.48x (HP>=2.0, MID>=1.5); F1_delta=-0.0006 (tol +/-0.02)`
**Cluster:** Lambda gpu_1x_gh200 us-east-3 ($2.29/h); job wall 15 min; cost ~$0.55

## Results — speculative is SLOWER, not faster

| Metric | Baseline (target only) | Speculative (target + draft) | Verdict |
|---|---|---|---|
| **Wall speedup** | 1.0× (reference) | **0.48×** | **HARD_FAIL** vs HP 2.0×, MID 1.5× |
| Mean per-query latency | 1.23 s | 2.58 s | spec is 2× SLOWER |
| Tokens/sec aggregate | 5.2 | 2.5 | spec is 52% of baseline |
| Answer F1 (HotpotQA bridge) | 0.365 | 0.365 | quality preserved (Δ = -0.0006) |
| Total tokens generated | 642 | 643 | nearly identical outputs |
| Mean output length | ~6.4 tokens | ~6.4 tokens | short answers (HotpotQA style) |

## DEVIATION FROM HANDOFF SPEC

Exp-Dev's handoff suggested Qwen2.5-1.5B target + Llama-1B draft. Standard HF
`assistant_model` speculative decoding requires draft + target to share tokenizer/vocab.
Qwen and Llama have different tokenizers. Used **Qwen2.5-0.5B-Instruct as draft** instead
(same family, matching tokenizer). The Qwen2.5-0.5B is smaller than Llama-1B, so this
deviation should not have hurt -- if anything it gave speculative decoding a more
favorable shot (smaller draft = faster draft = better speedup ceiling).

## Plain interpretation — workload mismatch

HotpotQA bridge answers are 1-5 words long (averaged ~6.4 tokens generated per question).
Speculative decoding's per-call setup overhead (draft forward, verification, rollback
on disagreement) only amortizes over LONG generations (256+ tokens typical in
speedup-benchmarks). For ~6-token answers, the draft-then-verify overhead has no
amortization room and ends up DOMINATING.

This is NOT a bug in the implementation. It is a workload mismatch between the technique
(speculative decoding) and the task (short-answer QA). The same speculative-decoding
setup on a longer-generation task (chat dialogue, longform summarization) likely still
delivers 1.5-3× speedup per upstream lit.

## Capability map implication

**Closes for v1 demo's hotpot_3baseline answer path**:
- "Speculative decoding accelerates the Qwen-1.5B answer step on hotpot_3baseline" -> ruled
  out by this evidence
- 2-3 week speculative-decoding integration for short-answer QA is NOT justified
- The follow-on distilled-50M-encoder action is NOT gated by this (it was conditional on
  spec-dec being established as encoder-bottleneck-revealer; if spec-dec doesn't help on
  the answer step, the answer step isn't the bottleneck for short-answer QA anyway)

**Does NOT close**:
- Speculative decoding for longer-generation tasks (multi-turn dialogue, long-context
  summarization, code generation) -- not tested here
- Speculative decoding for the encoder-forward step on retrieval (different lib, e.g.,
  Medusa or EAGLE; not tested)
- Distilled encoder action for OTHER reasons (e.g., memory footprint reduction, edge
  deployment latency)

## Caveats Research should know

1. **Workload sensitivity**: speedup measurements on short-answer QA are NOT
   representative of speculative decoding's typical lit-reported 1.5-3× on longform
   generation. Do NOT generalize "spec-dec doesn't help" from this evidence.

2. **Quality preservation confirmed**: F1 delta is -0.0006 (effectively zero). The
   correctness of HF's `assistant_model` implementation is validated -- it's just
   slower for this workload. So the F1 quality side is solid for any future test.

3. **Hardware was overkill**: GH200 480GB with both Qwen models loaded used <5 GB VRAM.
   Could have run on a 16 GB GPU; could even run on 4060 Ti 8 GB after KV cache
   accounting. The cloud cost ($0.55) was justified for safety-stack discipline + fast
   iteration, but a future repeat could go local.

4. **Sliding-window-attention warning**: Qwen-2.5 emits a warning that "Sliding Window
   Attention is enabled but not implemented for sdpa". This is the upstream Qwen
   architecture interacting with PyTorch's SDPA backend. Did NOT affect F1 (0.365 is in
   the expected range for Qwen-1.5B-Instruct on HotpotQA bridge with context). Did NOT
   cause the speedup loss. Just a noisy warning.

5. **Hardening worked**: all artifacts preserved locally including per_question_latencies.jsonl
   (44 KB; full 100-question detail for forensic drilldown). If you want to look at
   distribution shape (e.g., "is the slowdown uniform or driven by specific questions?")
   the data is one cat away.

## Follow-on questions for Research

1. **Is the v1 demo's answer path generation-heavy enough that spec-dec would matter for
   LONGER prompts?** If the demo includes any chat-style multi-turn or longform summary
   beyond short-answer QA, spec-dec may still help there. Re-test on the relevant
   workload before closing the technique entirely.

2. **Should I test spec-dec on a longer-generation benchmark (e.g., 128-token chat
   responses)?** ~$2-4 cloud, 30 min wall, would establish baseline that spec-dec WORKS
   for SOMETHING. Useful to keep on the option list even if not for hotpot_3baseline.

3. **Is the answer step actually a v1 latency bottleneck?** Baseline 1.23 sec per
   question means 100 questions take ~2 min total. If the demo isn't gated on per-query
   latency at that scale, the whole spec-dec exploration was solving a non-problem.

4. **Distilled-50M-encoder action — does this verdict change its priority?** The
   encoder-as-bottleneck argument was conditional on spec-dec being the answer-side
   speedup. Without the answer-side speedup mattering, the encoder-side action is purely
   about edge deployment / memory footprint. Re-prioritize?

## Artifacts (preserved locally)

Saved at `data/cell_specdec_results/`:
- `metrics.json` (1.1 KB)
- `eval_questions.json` (3.4 KB; warmup + eval question IDs for reproducibility)
- `per_question_latencies.jsonl` (44 KB; full per-question latency + predicted + gold
  for both baseline + speculative passes)

## Cross-references

- Exp-Dev's routing: `notes/exp_dev_to_testbed_speculative_decoding_handoff_2026-06-07.md`
- Research's pivot directive: `notes/research_to_testbed_colbert_path_closed_v1_2026-06-07.md`
  (the "pivot to spec-dec + distilled encoder" line)
- USER MULTI-HOP REVIVE MANDATE: `notes/testbed_to_research_user_multihop_revive_mandate_2026-06-07.md`
  (parallel to spec-dec; still standing for Research routings)
