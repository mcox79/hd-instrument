# Testbed deliverable: PP-8 Path 1a v1-only — HARD-FAIL (as research predicted)

**Date**: 2026-06-01
**Anchor**: pp8_w2_path1a_v1_h100_v1_n4096
**Verdict**: HARD-FAIL by strategy's revised pre-reg (val 0.100% < 0.3% threshold)
**Cost**: $1.06; cumulative session Lambda $9.31
**Status**: expected per research P=0.65 HARD-FAIL deflated for v1-alone (without v1'); dispatching v1+v1' bundle + Probe 2 per strategy authorization

## Result

- Loss decrease: 42.9% (15.07 → 8.61 over 500 steps; healthy)
- Val top-1: 0.100% (1/1000; 1.0x random); HARD-FAIL by strategy threshold
- During-training eval: 1/200 = 0.500% from step 400+ (same 5x-random-but-small-sample artifact seen in Path 1c v2)
- No NaN/Inf

## Context

This dispatch was made BEFORE the strategy v1+v1' bundle authorization landed. Research had only filed v1 (key-side SimHash projection) when I built the engineering. Strategy's subsequent authorization (`notes/routed_completed/strategy_response_to_testbed_pp8_v1_v1prime_authorized_2026-06-01.md`) explicitly noted that v1-alone is predicted to HARD-FAIL (research P_deflated=0.65) and that the bundle v1+v1' raises P to 0.42.

This result confirms the v1-alone HARD-FAIL prediction quantitatively: 0.100% val matches Path 1c v2's 0.100% (same architectural-mechanics issue, even with derived key codebook). The bottleneck is empirically on the val side: random val_idx -> target_token map has no LLM-output-distribution alignment for the bridge's downstream prefix-injection to optimize against.

## What's actually happening (re-diagnosis with v1 data)

With v1 (derived key codebook from `sign(R @ phi3_hidden("Key {K:04d}: "))`):
- Key codewords now ARE deterministic functions of Phi-3 hidden states
- But val targets are still randomly assigned to val_idx values
- For training key K: bridge gets sign(R @ h_i) -> retrieved val codeword (random) -> prefix -> Phi-3 should output val_to_token[V_i] (random pool token)
- The model has NO signal connecting prefix -> specific pool token because val_to_token[V_i] is random by construction
- CE loss can still decrease (pool-skew bias) but per-key prediction stays at random

This confirms research's diagnosis: BOTH sides (v1 key + v1' val) are required. v1' replaces the random val mapping with Phi-3-most-likely next-token of "Val {V:04d}: " over the alphabetic pool. This gives the bridge a target distribution that's actually predictable from a substrate-retrieved codeword + LLM context.

## What testbed does next

Per strategy routing rules + autonomy budget:
1. This deliverable filed
2. Dispatch v1+v1' BUNDLE (Prong A; ~$2-3) -- the proper test
3. Dispatch Probe 2 (Prong B; ~$1-2) -- training-dynamics diagnostic in parallel

Both dispatches are within strategy's pre-authorization; no further user gate.

## Cost discipline

- Cumulative session Lambda: $9.31 (entering v1+v1' + Probe 2 phase)
- v1+v1' estimate: $2-3
- Probe 2 estimate: $1-2
- Projected after both: $13-15 of remaining $42 contingency
- Well within $50 testbed check-in cap; far under $50-150 envelope

## SCP-back continues to work

6/6 files preserved at `data/lambda_batch_results/pp8_w2_path1a_v1_h100_v1_n4096_8449c9d8/`.

## Files referenced

- This deliverable
- `notes/routed_completed/strategy_response_to_testbed_pp8_v1_v1prime_authorized_2026-06-01.md` (the 3-prong authorization)
- `notes/research_pp8_phi3_hidden_codeword_design_v1_2026-06-01.md` (v1 design)
- `notes/testbed_pp8_week2_phase25_path1c_v1_2026-06-01.md` (Path 1c v2 0.100% match)

---

**ROUTING STATUS**: Acted-on 2026-06-01: HARD-FAIL verdict already logged in cap_map v316 batch
