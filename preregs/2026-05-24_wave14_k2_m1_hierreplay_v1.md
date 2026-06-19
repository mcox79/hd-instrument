# Prereg: wave14_k2_m1_hierreplay_v1

**Filed**: 2026-05-24 exp_dev
**Anchor**: K2 mechanism-class rescue M1 -- hierarchical sub-task chunk replay
**Trigger**: v193 K2 axis 3 Phase-D A-weighted SATURATION; all 3 in-design tuning axes exhausted at retA~0.74 floor.
**Handoff**: `notes/exp_dev_handoff_v195_pipeline_refill_2026-05-24.md` anchor 3

## Hypothesis

M1: replay sub-task CHUNKS (windows of CHUNK_SIZE tokens) not entire prior-task sequences.
Brain-inspired: hippocampal episode replay selects representative fragments.
Reduces gradient interference between task-level outer-product directions at load.
Expected to break the retA~0.74 substrate-intrinsic 4-stage ceiling.

## Design (exp_dev autonomy)

- N = 4096 (FULL), 1024 (smoke)
- Batch = 64 (FULL), 32 (smoke)
- Epochs = 5 (FULL), 1 (smoke)
- Phase-A epochs = 8 (FULL), 1 (smoke)
- Bytes per corpus = 200000 (FULL), 5000 (smoke)
- Seeds = {7, 17, 23, 31, 41} (FULL)
- chunk_fraction = 0.5 (each prior pool thinned to 50% before replay)
- CHUNK_SIZE = 64 tokens
- Queue: overnight_queue (GPU -- 4-stage continual learning, torch, multi-seed)
- ETA: ~4-5 hours GPU

## Pre-registered falsifier bands (before FULL run)

- **HARD-PASS**: mean retention_A >= 0.80 AND retention_B >= 0.70 AND retention_C >= 0.70 across 5 seeds.
  -> K2 M1 hierarchical chunk-replay BREAKS 4-stage ceiling; K2 PARTIAL -> promotion candidate.
- **HARD-FAIL**: mean retention_A <= 0.65 AND delta_A < 0.03 vs baseline retA=0.74.
  -> M1 chunk-replay REJECTED; M2/M3/M4 remain as untested mechanism-class paths.
- **MIDDLE**: retention_A in (0.65, 0.80); partial improvement; sequence M2 (attention-gated readout) next.

## Self-test cells (per [[feedback-strategy-spec-formula-selftests]])

verdict logic verified: (retA=0.83, retB=0.72, retC=0.73) -> HARD_PASS; (retA=0.62, retB=0.60, retC=0.65) -> HARD_FAIL; (retA=0.76, retB=0.65, retC=0.65) -> MIDDLE_BAND. All 8/8 self-test cases pass.

## Smoke outcome

Single seed 17, N=1024, 5000 bytes, 1 epoch: retention_A=0.888, retention_B=0.921, retention_C=0.941 -> K2_M1_HARD_PASS. Delta from baseline = +0.148. Smoke clears; ship FULL.

## Queue entry

`queue=overnight_queue name=wave14_k2_m1_hierreplay_v1 script=experiments/exp_wave14_k2_m1_hierreplay_v1.py prereg=preregs/2026-05-24_wave14_k2_m1_hierreplay_v1.md timeout=21600`
