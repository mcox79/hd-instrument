# Pre-registration: wave14zb_continual_5000

Date: 2026-05-21
Status: Pre-registered, gated
Priority: continual editing 5000 stress - extends the 30/100/200/500/1000/2000 ladder
Author: experiment_dev session, pipeline tick 35

## Why
Each successive stress level confirms Kerdock holds. zb at 5000 edits is
1.2x the M=4096 fact-base size in edits. Tests if cumulative numerical drift
eventually breaks the substrate.

## Verdict labels
- CONTINUAL_5000_HOLDS
- CONTINUAL_5000_DECAYS_AT_<I>
- CONTINUAL_5000_INCONCLUSIVE

## Runtime: ~20-30 min on GPU
