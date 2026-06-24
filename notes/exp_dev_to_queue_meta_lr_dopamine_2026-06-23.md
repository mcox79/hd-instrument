# exp_dev -> queue: substrate_meta_lr_dopamine_analog_v1

Date: 2026-06-23
Filed-by: exp_dev

## Shipment record

```
queue=overnight_queue name=substrate_meta_lr_dopamine_analog_v1 script=experiments/exp_substrate_meta_lr_dopamine_analog_v1.py prereg=preregs/2026-06-23_substrate_meta_lr_dopamine_analog_v1.md timeout=7200
```

## Status

SHIPPED. queue_add.sh exit code 0. Remote verify PASS (present in remote overnight_queue/queue.json).

## What this tests

Per-token RPE-modulated learning rate (phasic dopamine analog) for BPC lift on text8 LM.
Extends chain-grade ARM_CFRPE_ONLY (BPC=7.1052) from heterogeneous_plasticity_v1.
Three arms: FIXED_LR / GLOBAL_RPE_LR (tonic) / PER_TOKEN_RPE_LR (phasic).

Pre-reg HARD_PASS: per_token lift >= +0.15 bits vs fixed AND >= +0.05 vs global.

## Smoke findings (pre-ship)

- ARM_FIXED_LR: BPC=4.8934 (N_DIM=512, N_TRAIN=2k, smoke scale)
- ARM_GLOBAL_RPE_LR: BPC=4.7741 (+0.119 lift over FIXED; interesting even at tiny scale)
- ARM_PER_TOKEN_RPE_LR: BPC=4.8903 (+0.003 lift over FIXED; tied at smoke scale)
- All metrics non-null, non-sentinel; instruments pass
- Walk-back gate: N_STEPS doubled from 1000 to 2000 for FULL run
- elapsed_s at smoke: 360s (includes gensim cold-load ~180s)

The GLOBAL arm showing lift at smoke scale but per-token not is scientifically interesting:
at 80 steps the EMA is too noisy for per-token use; at 1000-2000 steps the per-token signal
may emerge.

## Routing source

notes/exp_dev_handoff_research_brain_to_lm_relevance_audit_2026-06-23.md (Anchor 1)
