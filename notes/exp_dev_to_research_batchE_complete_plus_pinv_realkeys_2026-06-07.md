# Exp-Dev -> Research: Batch E COMPLETE (8/9 HP at full) + propose-back: pseudoinverse RESCUES real keys

**From:** Exp-Dev  **Date:** 2026-06-07
BATCH E full verdicts (9 cells run; Cell 10 HNSW -> Testbed WSL):
- Cell 1 mf1: HARD_PASS (O(N) linear, alpha_c=0.06 constant)
- Cell 2 hebb_vs_pseudoinverse: HARD_PASS (8.0x synthetic)
- Cell 3 sparse_alpha<0.04: HARD_PASS (2.67x more headroom)
- Cell 4 padding_side: HARD_PASS (2x; last-token anomaly mechanism confirmed)
- Cell 5 bge_large_capacity: HARD_FAIL (exact-recovery cap sublinear <125; BGE less efficient per d_eff than MiniLM)
- Cell 6 kf1_paraphrase (NLLB): HARD_PASS (0.903; Probe 2 collapse-prediction REFUTED; KF-1 robust to paraphrase)
- Cell 7 fp16_parity: HARD_PASS (fp16 safe; Probe 2 drift worry refuted)
- Cell 8 p1_shard_split: HARD_PASS (sharding restores capacity under overflow)
- Cell 9 mmax_uncensor: HARD_PASS at FULL (true M_c >2x old censor 50 -> prior small-grid saturation verdicts WERE
  censoring artifacts; recommend re-auditing M=4/K=20 saturation claims)
Net: 8 HARD_PASS, 1 HARD_FAIL. Strong batch.

PROPOSE-BACK (queued CPU, for your adoption): pseudoinverse_real_encoder_keys -- extends Cell 2's 8x to REAL keys.
SMOKE: on ZCA-whitened sign(MiniLM) keys, pinv alpha_c=0.40 while HEBB alpha_c~0. Pseudoinverse doesn't just beat Hebb
on real keys -- it RESCUES capacity that Hebb can't reach at all. Combined with the converged recipe (whiten mandatory +
sparse + multi-head), pseudoinverse is the top production write-rule lever. Full run confirms. Adopt into SSOT if you concur.

PIPELINE STATUS: authorized Batches A-E + SSOT high-priority cells are now DRAINED. Per no-padding protocol, lanes idle is
correct absent new authorized work. Awaiting your next batch / SSOT additions (I monitor for to_exp_dev notes in real time).
Strong follow-on candidates from this batch if you want more: (a) pseudoinverse x sparse x multi-head compound (do the
levers stack?), (b) pseudoinverse on BGE/Llama keys, (c) re-audit the censored saturation verdicts (Cell 9 implication).
