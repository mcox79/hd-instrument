# Pre-reg: frame_order_recovery_hard_comprehension_v2 (DECODE-REGIME posctrl fix of v1 REGIME_POSCTRL_FAIL)

- anchor: `frame_order_recovery_hard_comprehension_v2`
- cell: `experiments/exp_frame_order_recovery_hard_comprehension_v2.py`
- date: 2026-07-06
- author: exp_dev
- supersedes: v1 (`exp_frame_order_recovery_hard_comprehension_v1`, landed `REGIME_POSCTRL_FAIL`). v1 metrics
  are NOT mutated; v2 writes to `data/exp_frame_order_recovery_hard_comprehension_v2/`.

## What v1 did (mechanism SOUND, positive control MIS-SPECIFIED)

v1 tested role->block ORDER recovery from a block-superposition composite. The mechanism is sound:
- content_frame ORDER recovery = 1.000  MEASURED@data/exp_frame_order_recovery_hard_comprehension_v1/metrics.json:arms.content_frame.order_recovery_mean
- occupancy_baseline ORDER    = 0.192  MEASURED@.../v1/metrics.json:arms.occupancy_baseline.order_recovery_mean
- real-vs-control ORDER gap   = 0.808
- partition-restricted decode = 0.983  MEASURED@.../v1/metrics.json:arms.decode_at_scale_posctrl.partition_restricted_true_frame_mean

v1 landed `REGIME_POSCTRL_FAIL` because its full-codebook DECODE positive control floored:
- decode_at_scale(full-codebook) = 0.525  per_seed=[0.575,0.25,0.75]  MEASURED@.../v1/metrics.json:arms.decode_at_scale_posctrl.full_codebook_true_frame_mean  (< 0.60 floor)

## Root cause (verified off-disk + diagnostic recompute)

The positive control exists to REPRODUCE the cited hard cliff:
- CITED@data/exp_generation_decoder_gsbc_native_blocklocal_v1:blocklocal_gsbc@V8192D26 exact_ordered=0.856 per_token=0.9945

That cited cliff was measured at the cited cell's block size:
- CITED@experiments/exp_generation_decoder_gsbc_native_blocklocal_v1.py:517  `bs = N_DIM // D = 8192 // 26 = 315` (k=round(0.02*315)=6), D disjoint blocks, full-codebook argmax.

v1 instead decoded the positive control in the ORDER-mechanism's block geometry:
- `bs = N_DIM // B_TOTAL = 8192 // 32 = 256` (k=round(0.02*256)=5).

bs=256 is SMALLER + sparser than the cited bs=315 -> per-token decode margin drops (0.970 vs 0.994), and
compounded across D=26 the frame-exact decode collapses to ~0.48-0.52 with enormous seed variance (CV~0.5).
This is the SAME capacity-vs-decode-regime family as Tier-3 global_consistency (N_DIM starvation cured a
decode-starved control). Here the cure is decoding the posctrl at the CITED block size, not a bigger N.

Diagnostic recompute (SAME fillers, this cell's helpers; MEASURED@scratch_diag):
- bs=256 (v1 regime):        full_frame_exact mean=0.483  per_seed=[0.375,0.25,0.825]  per_token=0.970
- bs=315 (cited regime):     full_frame_exact mean=0.867  per_seed=[0.9,0.875,0.825]   per_token=0.9949
- V=8192 bs=315 (cited exact): full_frame_exact mean=0.850  per_token=0.9936  (reproduces CITED 0.856/0.9945)

## The fix (surgical; DECODE regime only; ORDER mechanism UNTOUCHED)

The positive control now reproduces the cited cliff at the CITED regime: each true-frame filler is placed in
its OWN disjoint block of size `bs_cited = N_DIM // D` (matching the cited cell), full-codebook argmax, using
the SAME sampled GSBC concepts. Reported as `decode_at_scale_posctrl.cited_regime_true_frame_mean` (GATED).
The v1 razor-edge bs=256 number is STILL reported as `cellbs_full_codebook_true_frame_mean` (INFORMATIONAL --
nothing hidden). A pos-ctrl CV guard rejects a razor-edge control from clearing the floor by seed luck.

The ORDER-recovery arms (content_frame vs occupancy_baseline), their B_TOTAL=32 / bs=256 geometry, the
partition-restricted decode the mechanism actually uses, and the gap discriminator are BIT-FOR-BIT v1.

## PRE-REGISTERED BANDS (fixed a-priori; NOT reverse-engineered from smoke)

Band 1 -- POSITIVE-CONTROL-CLEARS-FLOOR (the fix target):
- `decode_at_scale cited-regime (bs=N//D) >= 0.60`  (POS_CTRL_DECODE_FLOOR; inherited UNCHANGED from v1)
  - source: CITED cliff 0.856; floor 0.60 = comfortable margin below the cited value.  CITED@generation_decoder_gsbc_native_blocklocal_v1
- `decode_at_scale cited-regime CV <= 0.20`  (POS_CTRL_CV_MAX; NEW stability guard)
  - rejects a razor-edge control (v1 bs=256 CV~0.5) that would clear a mean floor by seed luck.  THEORETICAL

Band 2 -- ORDER-RECOVERY-GAP GUARD (proves the fix did not disturb the sound mechanism):
- `gap = order_content - order_occupancy >= 0.45`  (ORDER_GAP_MIN; inherited UNCHANGED from v1)
  - v1 measured gap=0.808; expected unchanged in v2 (mechanism identical).  HYPOTHESIZED (v2 == v1 mechanism)

FULL HARD_PASS (all must hold, >= 5 seeds): order_content>=0.75 AND order_occupancy<=0.32 AND gap>=0.45 AND
superposition_survival>=0.50 AND decode_at_scale_cited>=0.60 AND order_content_cv<=0.15.
FULL HARD_FAIL: order_content<=0.25 (occupancy-degeneracy confirmed; mechanism cannot beat chance).
Default tier: MIDDLE (cert-owner tiers up at landed-VET).

Honest alternative outcome pre-declared: if the cited-regime posctrl could NOT clear 0.60 at any sane regime,
that would be reported as a REAL positive-control bound (not forced to pass). It clears (see preview below).

## Preview verification (5-seed local FULL; canonical = remote)

MEASURED@data/exp_frame_order_recovery_hard_comprehension_v2_preview5/metrics.json:
- decode_at_scale cited-regime = 0.870  per_seed=[0.775,0.800,0.925,0.925,0.925]  cv=0.078  -> clears 0.60, cv<=0.20  PASS
- cellbs razor-edge (info)     = 0.465  (documents why v1 floored)
- ORDER gap = 0.805 (content 1.000 vs occupancy 0.195) -> guard PASS (matches v1's 0.808)
- superposition parse = 0.800; partition-restricted decode = 0.980
- verdict = HARD_PASS ; elapsed = 96.6s (5 seeds x 3 conds x 40 trials)

## SCHEMA-VET gates

- cardinality_ok: EXPECTED_N_UNITS = 5 seeds x 3 conditions = 15; verdict HARD_FAIL_CARDINALITY_BREACH if fewer.
- arms_differ_verified: content vs occupancy order-predictions hash-distinct per unit (META_RULE_AF).
- final_metrics_atomicity: tmp_replace.
- except SystemExit: raise before except Exception (no BaseException / bare except; grep-gated PASS).
- crlb_n_a: clean single-filler order recovery is deterministic-1.0 by self-correlation dominance
  (THEORETICAL); the stressed quantity is the CITED decode ceiling (CITED, not a closed-form floor).
- baseline_in_band: occupancy_baseline ORDER MUST collapse to chance 1/D! (structural energy-invariance;
  bias_audit proves it). content_frame order (D=3) = 1.000 is by self-corr dominance (not saturation-vacuous:
  occupancy at chance in the SAME regime proves the stressor bites).
- discriminator survives scale: decode + order measured AT full N=8192 in ALL modes (smoke reduces trials +
  seeds only). Smoke (seed 7) fires: gap=0.800, occupancy=0.200, cited-decode=0.700>=0.60. 5-seed preview
  confirms at scale.
- calibration_check: default_ok_for_this_regime (block-local F_SPARSE=0.02 inherited from the cited proven cell).
- progress_logging: print_flush_true (line_buffered stdout; per-unit _say + heartbeat). timeout_s < 1800 so
  not strictly mandatory, but present.
- start_marker_written / crash_diagnostic_present / heartbeat_present: yes.
- KB_REFERENT: data/gen_decoder_gsbc_fillers/gsbc_expand2x_pool_v1.npz (untracked npz; must be present on the
  remote before FULL dispatch -- PROT-022 will SSH-probe it).

## Functional requirements (Gate E)

1. Recover role->block ORDER from a block-superposition when the SET is fixed (occupancy degenerate) ->
   role-typed matched filter over disjoint vocab partitions (content_frame). [MEASURED gap=0.805]
2. Reproduce the cited decode cliff as a positive control that the ORDER results depend on ->
   full-codebook block-local decode AT THE CITED regime bs=N//D (decode_at_scale_cited). [MEASURED 0.870]
3. Prove occupancy energy cannot see ORDER -> bias_audit energy-invariance (structural). [PASS]

## Effective-vs-nominal parameter audit (Gate A)

- ORDER mechanism block size: bs = N_DIM // B_TOTAL (order/superpose bs=1024; scale bs=256). ALIGNED (the
  mechanism's own decode operates here; partition-restricted = 0.980).
- POSCTRL decode block size: bs_cited = N_DIM // D (scale bs_cited=315). ALIGNED with the CITED cliff regime
  (this is the v1->v2 fix; v1 was MISALIGNED, decoding the posctrl at N//B_TOTAL=256).
- sweep_alignment_verdict: ALIGNED.

## Positive-control arm (Gate D)

- arm: DECODE_CITED_CLIFF_REPRODUCE_AT_TEST_REGIME
- primitive: block-local full-codebook decode
- cited_prior_atom/metric: generation_decoder_gsbc_native_blocklocal_v1 blocklocal_gsbc@V8192D26 = 0.856
- cited_prior_regime: {N: 8192, D: 26, bs: N//D=315, full_codebook_argmax}
- test_regime: {N: 8192, D: 26, bs: N//D=315, V: 7800, full_codebook_argmax}  (SAME regime; ~8192 codebook)
- tolerance: posctrl must reach >= 0.60 (cited 0.856); MEASURED 0.870 -> SHAPE_MATCH.

## Compute architecture

- class: (b) sequential-CPU with justification. numpy matched-filter + block-argmax; per-unit wall ~6s; total
  5-seed FULL ~97s. No GPU speedup warranted (small matmuls, no chained dependency). remote_cpu_queue.
- storage strategy: no_storage (read-only synthetic composition; no substrate writes; re-encode HELD).

## Dispatch

- SMOKE local: PASS (HARD_PASS machinery, gap=0.800, cited-decode=0.700>=0.60).  self-test PASS (5.9s).
- FULL: 5 seeds (7,13,19,23,29) -> remote_cpu_queue via tools/orchestrator/queue_add.sh.
- timeout: 900s (preview 97s x 1.5 safety x remote-CPU margin; < 14400 so no PROT-021 checkpoint mandate;
  no _n suffix so no PROT-018/019).
- PREREQ: SCP data/gen_decoder_gsbc_fillers/gsbc_expand2x_pool_v1.npz to the remote (queue_add does NOT
  auto-ship the untracked npz; PROT-022 SSH-probe blocks otherwise).
