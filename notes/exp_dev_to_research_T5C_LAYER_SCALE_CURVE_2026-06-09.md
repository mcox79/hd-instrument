# Exp-Dev -> Research: Path A layer/position/scale CURVE -- more layers monotonically help; EVERY-LAYER wins (28%)

**From:** Exp-Dev  **Date:** 2026-06-09  **Re:** BATCH_5 GPU-T5C sweep results (Pythia-160M unless noted, single-seed)

## Layer-COUNT curve (Pythia-160M, L4-centered): MORE LAYERS = MORE IMPROVEMENT (monotonic)
- 2-layer (L4+5): 0.836x (16%)  [the C1 baseline]
- 3-layer: 0.774x (23%)
- 6-layer: 0.765x (24%)
- **every-layer (12): 0.723x (28%) -- BEST**
=> Stacking adapters monotonically improves; every-layer rectangular is the strongest. NOTE: every-layer rectangular is also the
   KBLaM Path-B architecture -- the best LM-improver and the retrieval architecture are the same pattern. Strong convergence.

## Position (2-layer pairs, Pythia-160M): count dominates position; semantic-band (E4) prediction NOT confirmed
- early L2+3: 0.776x (22%)  | mid L4+5: 0.836x (16%) | late L8+9: 0.795x (20%)
- early/late pairs IMPROVED MORE than the mid pair -- contradicts the "L4-5 semantic-onset is special" prediction. (Single-seed;
  needs multi-seed to confirm, but the trend is clear: position matters less than layer count.)

## Scaling: holds / slightly grows with size
- Pythia-1.4B 2-layer: 0.814x (19%) vs Pythia-160M 2-layer 16% -- improvement holds and slightly grows at 10x scale.
- Qwen-2.5-3B: FAILED (OOM on the 8GB 4060 Ti; 3B frozen+bf16 + activations exceeds VRAM). Need 4-bit or a bigger card.

## Path B (KBLaM small-scale): consistently fails -- needs 50K+ / real DBpedia
- KBLaM discriminative (real distinct-entity subjects), every-layer + 1-layer + 4k-scale: ALL held-out < 0.20. Even with
  discriminative keys, 2-4k facts on Pythia-160M doesn't generalize -- matches your drill 1.3 memorization-bypass prediction.
  Confirms: Path B needs the 50K-120K regime + real DBpedia data (data plumbing is the gate, not architecture).

## Now queued (sweep-2, confirming every-layer-wins at scale + on Qwen)
Pythia-1.4B every-layer, Pythia-2.8B 2-layer + every-layer, Qwen-1.5B every-layer + 4-layer. Will report.
**Suggestion for demo:** the hero claim could strengthen from "15-17%" to "up to 28% (every-layer)" pending multi-seed confirmation.
