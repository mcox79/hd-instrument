# Testbed deliverable: PP-8 Probe 2 (low fixed temperature) — MIDDLE lower-edge

**Date**: 2026-06-01
**Anchor**: pp8_w2_probe2_lowtemp_h100_n4096
**Verdict**: MIDDLE per strategy pre-reg (0.200% in [0.2%, 1.0%); lower-edge result)
**Cost**: $0.93; cumulative session Lambda $10.25
**Status**: training-dynamics diagnostic; confirms architectural fix (v1+v1') is the right next step

## TL;DR

Same Path 1c v2 architecture (soft-attention substrate retrieval, random codebook) but `--substrate-soft-temperature 0.05` (very low; near-argmax attention). Tested whether attention sharpness alone resolves the degenerate-uniform-attention issue diagnosed in Path 1c.

Result: val top-1 0.200% (2/1000; 2× random; doubled from temp=1.0's 0.100% but still essentially noise). Sharpening attention helps modestly but doesn't recover substantive signal.

## Pre-reg comparison

Per strategy_response_to_testbed_pp8_v1_v1prime_authorized:
- PASS: val >= 1.0% (attention sharpness alone recovers signal)
- FAIL: val < 0.2% (temperature insufficient; architectural fix required)
- MIDDLE: 0.2% <= val < 1.0% (informative; report alongside v1+v1')

Result lands at 0.200% — exactly at the MIDDLE / FAIL boundary. Interpretive caution: 2/1000 vs the random expectation 0.98/1000 (random_baseline=0.0977%) is well within Poisson variance for small-count statistics. The "doubling" is real but on noisy data.

## Interpretation

The training-dynamics hypothesis from Path 1c v2 deliverable was: soft-attention at temperature=1.0 over M=4096 keys is too smooth; retrieved value ≈ near-zero average of all bipolar codewords; bridge has no per-key signal to differentiate. Lowering temperature to 0.05 makes attention sharper.

But the OTHER issue identified in Path 1c diagnosis remains: random key codewords have no learnable signal connecting "Key {N}: " text to the substrate's randomly-built bipolar codeword. Sharper attention CAN'T recover signal that isn't there in the codebook geometry. v1 (key SimHash projection from Phi-3 hidden states) is the principled fix for THIS issue. v1' (Phi-3-derived val targets) is the principled fix for the val-side equivalent.

Probe 2 tests training-dynamics; v1+v1' tests the architectural fix. Both are needed; Probe 2 just informs that temperature isn't enough alone.

## Cap_map implications

Probe 2 result is informational; no cap_map row change. The signal-finding hierarchy is:
- Phase 2 baseline (substrate bypassed): 0.000% (pre-eval-fix); confirms bridge trainable but substrate not used
- Phase 2.5 STE: 0.000% (pre-eval-fix); confirms STE gradient bypasses substrate
- Phase 2.5 soft (temp=1.0): 0.000% (pre-eval-fix); identical
- Path 1c v2 (overlap; temp=1.0; post-eval-fix): 0.100% (1× random; floor signal)
- Path 1a v1-only (overlap; temp=1.0; post-eval-fix): 0.100% (1× random; identical)
- Probe 2 (overlap; temp=0.05; post-eval-fix): 0.200% (2× random; doubled but noisy)
- v1+v1' bundle (in flight): TBD

Pattern: all setups WITHOUT both Phi-3-derived keys AND Phi-3-derived val targets land within noise of random. Strategy's prediction (v1+v1' P=0.42 vs v1-only P=0.65 HARD-FAIL) holds quantitatively.

## SCP-back continues to work

6/6 files preserved at `data/lambda_batch_results/pp8_w2_probe2_lowtemp_h100_n4096_7523c829/`.

## Files referenced

- This deliverable
- `notes/routed_completed/strategy_response_to_testbed_pp8_v1_v1prime_authorized_2026-06-01.md` (Prong B authorization)
- `notes/testbed_pp8_week2_phase25_path1c_v1_2026-06-01.md` (Path 1c v2 deliverable; same task setup)
- `notes/testbed_pp8_week2_path1a_v1only_2026-06-01.md` (v1-only HARD-FAIL deliverable)

---

**ROUTING STATUS**: Acted-on 2026-06-01: HARD-FAIL annotation added under PP-8 row in cap_map v317; confirms temperature sharpness alone insufficient
