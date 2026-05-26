# Prereg: wave14_k2_m1_hierreplay_deeperN_v1

**Filed**: 2026-05-24 exp_dev
**Anchor**: K2 M1 hierarchical chunk replay deeper-N probe at N=8192
**Trigger**: wave14_k2_m1_hierreplay_v1 K2_M1_MIDDLE_BAND (retention_A=0.719,
             baseline=0.74, HARD-PASS=0.80). N-scaling gap: smoke at N=1024
             gave HARD_PASS (retention_A=0.888), full at N=4096 gave MIDDLE.
             Hypothesis: M1 mechanism scales with N; N=8192 breaks the ceiling.

## Hypothesis

At N=8192, the outer-product weight matrix W (8192 x 8192 = 67M entries) has
substantially more capacity than N=4096 (17M entries). The M1 chunk-replay mechanism
may show a phase transition at larger N: chunk boundaries stored in a higher-N
W can be more cleanly separated, reducing gradient interference between task-level
outer-product directions during 4-stage continual learning.

Prediction: retention_A at N=8192 >= 0.80 (HARD-PASS threshold).

## Design

Single change from v1: N_FULL = 8192 (was 4096). All other parameters identical:
- Batch = 64 (FULL), 32 (smoke)
- Epochs = 5 (FULL), 1 (smoke); phase_a_epochs = 8 (FULL), 1 (smoke)
- Bytes = 200k (FULL), 5k (smoke)
- Seeds: [7, 17, 23, 31, 41] (FULL), [17] (smoke)
- Chunk fraction = 0.50
- Queue: overnight_queue (GPU required for N=8192 x 5 seeds)
- ETA: ~60-90 min GPU

## Pre-registered bands (same verdict logic as v1, same thresholds)

HARD-PASS: mean retention_A >= 0.80 AND mean retention_B >= 0.70 AND mean retention_C >= 0.70
  -> M1 at N=8192 BREAKS ceiling; N-scaling confirms M1 mechanism class.
  -> K2 partial -> 🟢 promotion candidate; cap_map bump.

HARD-FAIL: mean retention_A <= 0.65 AND delta_A < 0.03 vs baseline 0.74
  -> M1 chunk-replay REJECTED even at N=8192; N-scaling does not rescue M1.
  -> Rehab: M2 (attention-gated readout), M3 (sparse interference reduction).

MIDDLE: retention_A in (0.65, 0.80)
  -> Partial improvement; M1 partially N-scaling-dependent.
  -> If delta_A > +0.03 vs v1 N=4096 (delta > 0.719+0.03=0.749), counts as positive trend.

## Self-test verification (inherited from v1)

Same 8 self-test cases as k2_m1_hierreplay_v1:
- mk(0.83, 0.72, 0.73) -> K2_M1_HARD_PASS
- mk(0.81, 0.70, 0.71) -> K2_M1_HARD_PASS
- mk(0.62, 0.60, 0.65) -> K2_M1_HARD_FAIL
- mk(0.65, 0.60, 0.65) -> K2_M1_HARD_FAIL
- mk(0.76, 0.65, 0.65) -> K2_M1_MIDDLE_BAND
- mk(0.70, 0.55, 0.55) -> K2_M1_MIDDLE_BAND
- mk(0.78, 0.72, 0.71) -> K2_M1_MIDDLE_BAND
- {} -> K2_M1_INCONCLUSIVE

## Risk

N=8192 W matrix is 256 MB float32 on GPU (8192^2 * 4 bytes).
With 5 seeds and pool tensors, peak VRAM may approach 2-3 GB. Should fit on
a GPU with 6+ GB VRAM. If OOM, reduce to N=6144 or 3 seeds in a v2.
