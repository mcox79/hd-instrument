# Pre-registration: encoder_v11_gsbc_graded_sparse_v1

Date: 2026-07-04
Author: exp_dev (hdi_exp_dev)
Anchor: encoder_v11_gsbc_graded_sparse_v1
Cells:
- core: experiments/exp_encoder_v11_gsbc_graded_sparse_v1_core.py
- seed 7: experiments/exp_encoder_v11_gsbc_graded_sparse_v1_seed_7.py
- seed 13: experiments/exp_encoder_v11_gsbc_graded_sparse_v1_seed_13.py

## Question

The sign-only block-argmax code caps at ret_agree10 ~0.43 (MEASURED@ceiling
ORTHO_K128) and the trained student plateaus at ~0.21 -- a LOCAL-WTA /
sign-quantization penalty, NOT a density limit (dense-float ceiling = 1.0). Does
a GRADED Sparse-Block-Code (Frady/Kleyko/Rahimi GSBC, arXiv:2303.13957) -- keep
the block-wise top-m graded positive survivors (unit-L1 per block), bind with
block-wise CIRCULAR CONVOLUTION -- reach ret_agree10 >= 0.35 at ~2% active WHILE
keeping keyed@J5 SBC algebra >= 0.95? Trained with the proven annealed soft->hard
estimator + a listwise-rank term + a MANDATORY absolute-cosine anchor.

## Source numbers (tagged)

- sign-only K128 ceiling ret_agree10 = 0.4295
  MEASURED@data/exp_encoder_ceiling_density_curve_v1/metrics.json:/ceiling_curve[K=128]
- dense-float ceiling ret_agree10 = 1.0000 (RAW_ISOMETRIC)  MEASURED@same
- v3e sign trained baseline ret_agree10 = 0.2112  MEASURED@exp_encoder_v3e_.../seed7
- v6 lever B CLOSED: ANNEAL_STE cons_last 0.000132 (soft==hard converged), block
  ret 0.048 keyed@J5 0.233  MEASURED@exp_encoder_v6_annealed_ste_..._seed7
- GSBC ceiling estimate ret ~0.7-0.9  CITED@arXiv:2303.13957 (Frady/Kleyko GSBC)
- GSBC algebra at format scale: keyed@J5 = 1.0000 (pos-shift keys AND +-1 keys),
  shuffled 0.0000, zero-training ORTHO lift
  MEASURED@scratchpad/gsbc_format_probe.py
- GSBC zero-train retrieval (kb32/L128/m3, 2.34%) = 0.5499 vs sign 0.5392
  MEASURED@same
- global-topk graded (dual readout) zero-train +0.086 over sign; sign readout of
  global survivors keyed@J5=1.00 despite 36.5% empty blocks
  MEASURED@scratchpad/dual_readout_format_probe.py
- smoke keyed@J5 = 1.000 for SIGN (sbc) AND both GSBC arms (gsbc_circconv) under
  (tiny-data) training  MEASURED@data/exp_encoder_v11_gsbc_graded_sparse_v1_seed7_smoke/metrics.json

## Arms (PAIRED; same seed/data/split/objective backbone/LR/steps/WIDTH=2048)

FIXED N_DIM=4096; in_batch RKD backbone; nce_weight=0; batch=128; cosine LR;
STEPS=8000. Per-arm block geometry (kb*blk_l=4096).

| arm        | mode | kb  | blk_l | m | active% | recipe   | isolates                    |
|------------|------|-----|-------|---|---------|----------|-----------------------------|
| SIGN_BLOCK | sign | 128 | 32    | 1 | 3.12    | rkd_only | control == v3e (Gate-D)     |
| GSBC_RKD   | gsbc | 32  | 128   | 3 | 2.34    | rkd_only | the CODE (graded vs sign)   |
| GSBC_FULL  | gsbc | 32  | 128   | 3 | 2.34    | full     | the training RECIPE (PRIMARY)|

PRIMARY (pre-declared): GSBC_FULL. Nested ablation SIGN -> GSBC_RKD (code
effect) -> GSBC_FULL (recipe effect). NOTE (confound, declared): GSBC arms differ
from SIGN in BOTH code and (for FULL) objective; SIGN is the v3e reference, not a
recipe-matched control. GSBC_RKD isolates the code alone.

## GSBC code + binding

- CODE: per block, top-m graded positive survivors = |z| at the top-m argmax
  positions, unit-L1 normalized per block (positive per-block distribution). Same
  ~2% support as a sign block code but a CONTINUOUS Gram (no sign quantization).
- BINDING (keyed@J5 algebra gate): block-wise circular convolution
  (hdlab.binding.bind/unbind over the (kb,blk_l) reshape = FFT over blk_l) with
  POSITIVE one-hot shift keys (preserve the unit-L1 invariant). The ideal GSBC
  binding (Frady/Kleyko); element-wise product is lossy for graded. SIGN arm uses
  the existing v3._keyed_unit SBC path (its ideal binding).
- Dual readout compatible: graded survivors -> retrieval; the block structure ->
  algebra. (Global-topk + FlyHash-expansion dual readout is the sequenced-next.)

## Training recipe (research drill 2026-07-04; recipe=full only)

- ESTIMATOR: annealed SOFT->HARD graded top-m straight-through (forward = exact
  hard graded top-m unit-L1 = the deployed code; backward via annealed per-block
  softmax, tau 2.0->0.1 over 80% of steps) + a soft/hard-consistency MSE. This is
  the SAME estimator that learned the 0.65 dense geometry in v6; the graded code
  removes the block-argmax carrier bottleneck.
- OBJECTIVE: graded-RKD backbone + LISTWISE-RANK (ListNet top-1 listwise CE) +
  a MANDATORY absolute-cosine ANCHOR (MSE(code_cos, teacher_cos) on the T>=0.5
  band). Weights: rkd 1.0, cons 0.5, rank 0.5, anchor 1.0.
- THE ANCHOR IS NOT OPTIONAL: every ranking lever tried (OPQ, KL-RANK,
  annealed-dense) won on ret by INFLATING cosine and wrecking calibration = a
  joint-gate FALSE PASS. The anchor is the designed guard; the verdict JOINT-GATES
  ret AND calib AND hi80 AND keyed@J5 so a calibration-collapse cannot pass.

## #1 RISK (declared + readable)

The MANDATORY anchor may CAP trained ret below 0.35 even though the graded code
ceiling is ~0.7-0.9 (drill P_deflated 0.44). This tension is the real risk. The
cell reports it READABLY in metrics `anchor_ret_cap_readout`: trained_ret,
trained_calib_err, trained_hi80_cos, GSBC_RKD ret, sign baseline ret, and the
ret-vs-sign-ceiling gap. A ret < 0.35 with GOOD calib is an HONEST result (the
anchor working), not a code failure -- do not re-tune the anchor away to force a
FALSE PASS.

## Bands (both directions; JOINT instrument)

- ALGEBRA HARD co-gate: keyed@J5 (deployed BLOCK_LAST) >= 0.95 per GSBC arm. GSBC
  theory + the format probe predict 1.00; if a GSBC arm LIFTS ret but keyed drops
  below 0.95 -> HARD_FAIL GSBC_BREAKS_ALGEBRA (THAT is the finding).
- PRIMARY HARD_PASS: GSBC_FULL ret_agree10 >= 0.35 AND keyed@J5 >= 0.95 AND
  hi80_cos >= 0.30 (no coarse collapse). calib_err reported.
- HARD_FAIL: (a) SIGN control ret outside [0.15,0.28] (Gate-D drift) or SIGN
  keyed < 0.95 (machinery); (b) a GSBC arm lifts + breaks algebra (FALSE_WIN);
  (c) neither GSBC arm ret > 0.25 (no lift -> density dial).
- MIDDLE_BAND: primary ret>=0.35+algebra but hi80<0.30 (calib cost); OR only
  GSBC_RKD clears (density/recipe interplay); OR best GSBC ret in (0.25,0.35).
- Reachability: sign ceiling 0.4295 + GSBC graded ceiling higher (dense=1.0) +
  zero-train probe GSBC>=sign -> 0.35 reachable. HARD_PASS floor 0.35 is strictly
  above the 0.25 fail floor by >5% of the (0.25..~0.9) band (META_RULE_L).

## Schema-vet fields

- cardinality_ok: EXPECTED_N_UNITS = 3 arms x 9 + CHARPOS = 28 (both run modes)
- discriminator-survives-scale: option (C) -- the make-or-break ALGEBRA is shown
  at FULL FORMAT SCALE by the zero-training probe (GSBC keyed@J5=1.00) AND smoke
  (1.00 under tiny-data training); the ret>=0.35 discriminator is FULL-only.
- baseline_in_band: CHARPOS ret in (0.05,0.95); Gate-D SIGN in [0.15,0.28]
- calibration_check: default_ok_for_this_regime (+ the mandatory anchor)
- final_metrics_atomicity: tmp_replace; arms_differ_verified (sha256 per code)
- crlb_n_a: ret_agree10 has no closed-form sigma CRLB; reachability via probes
- storage_strategy: no_composition (single-hop retrieval + bounded keyed control)
- compute_architecture: batched-GPU (student fwd/bwd + graded top-m + block FFT)
- progress_logging: print_flush_true (timeout_s >= 1800)
- HYPOTHESIZED: GSBC_FULL trained ret 0.35-0.7 (drill); the anchor-cap is the risk.

## Dispatch

overnight_queue (GPU), both seeds, timeout 1800s. SCP-based (local commit
suffices, no origin push). CANONICAL = remote-queue official landing.
sequenced_next: density dial (m/blk sweep) + composition-depth VET + global-WTA/
FlyHash-expansion dual-readout arm + B-dim block-energy side channel.
