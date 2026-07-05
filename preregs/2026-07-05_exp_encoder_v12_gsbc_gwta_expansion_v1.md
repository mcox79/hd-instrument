# Prereg: encoder v12 GSBC global-WTA + expansion ceiling-push + composition-depth VET

Date: 2026-07-05
Anchor: `encoder_v12_gsbc_gwta_expansion_v1` (siblings `_seed_7`, `_seed_13`)
Core: `experiments/exp_encoder_v12_gsbc_gwta_expansion_v1_core.py`
Parent (read-only): v3 landmark-RKD core + v11 GSBC graded-sparse core.

## Question
The v11 GSBC graded code landed HARD_PASS both seeds. Off-disk FINAL-step winner
is the SIMPLER `GSBC_RKD` (graded top-m block code + plain RKD, no ListNet/anchor):
`ret_agree10` 0.4447 (seed7) / 0.4664 (seed13), hi80_cos ~0.842, calib ~0.002,
keyed@J5 1.000 (MEASURED@data/exp_encoder_v11_gsbc_graded_sparse_v1_seed{7,13}/metrics.json).
The graded code ceiling is ~0.7-0.9 (CITED@arXiv:2303.13957 Frady/Kleyko;
dense-float=1.0) -> large headroom. **Which code-geometry lever, built on the
GSBC_RKD base, gives the best JOINT (ret_agree10 + keyed@J5>=0.95 + hi80 no-collapse
+ calib) at ~2% active?** And, on the same deployed codes, **where does the GSBC
circular-conv bind/unbind algebra hold under composition depth (J-sweep)?**

## Arms (PAIRED; recipe=rkd_only for ALL; ONLY the code geometry differs; 2.34% active)
- `GSBC_RKD_BLOCK` -- block top-m=3 (kb32/blk128), out4096. BASELINE == v11 GSBC_RKD (Gate-D).
- `GSBC_GWTA` -- GLOBAL top-96 over out4096, graded positive global-L1, reshape (32,128). PRIMARY lever (strict superset of block-top-m; ceiling can only rise).
- `GSBC_EXPAND2X` -- 2x-wide student out8192 + GLOBAL top-192, reshape (64,128). SECONDARY lever (FlyHash-style expansion at fixed 2.34% sparsity fraction).

All arms share seed/data/split/steps(8000)/LR/width(2048)/objective. Retrieval eval
is PAIRED (same seed+3 pair-sampling + same held pool across arms). keyed J-sweep is
PAIRED (same generator seed per J across arms).

## Composition architecture (mandatory declaration)
- Compute class: **(a) batched-GPU** -- student fwd/bwd, graded top-m / global top-K,
  block circular-conv (FFT) are batched on cuda; retrieval pairs batched; keyed loops
  J per trial (cheap). PROT-020 satisfied (imports torch).
- Storage strategy: **no_composition** for retrieval (single-hop agreement metric).
  The keyed J-sweep is a bounded-bundle **composition-depth VET** (J items bound, one
  unbound, cleanup@1 vs the disjoint held pool). Not a chained-retrieval store.

## Bands (envelope-fail-bands)
FINAL-step deployed-code `ret_agree10` is the gated number. keyed@J5 >= 0.95 is a HARD
co-gate. Paired lift = `ret(lever) - ret(GSBC_RKD_BLOCK)` within the same seed.

- HARD_PASS: a LEVER arm has `ret_lift >= +0.03` AND keyed@J5 >= 0.95 AND hi80_cos >= 0.30
  (no coarse collapse) AND hi80_calib_err < 0.10. -> the lever climbs toward the GSBC ceiling JOINTLY.
- MIDDLE_BAND (algebra-degrades): a lever lifts `ret >= +0.03` but keyed@J5 < 0.95
  (global allocation empties blocks and trades bind/unbind SNR for retrieval -- a real finding).
- MIDDLE_BAND (calib/hi80): a lever lifts ret + holds algebra but hi80 < 0.30 or calib >= 0.10.
- MIDDLE_BAND (marginal): best lever lift in (0, +0.03), algebra held.
- HARD_FAIL (no-lift): best lever `ret_lift <= 0` (block-top-m already optimal at 2.34%; route to density dial).
- HARD_FAIL (Gate-D): `GSBC_RKD_BLOCK` ret outside [0.38, 0.55] (baseline drifted; comparison void).
- HARD_FAIL (control-algebra): `GSBC_RKD_BLOCK` keyed@J5 < 0.95.
- HARD_FAIL (integrity): any arm RANDOM keyed@J5 < 0.98, or any shuffled_key@J5 > 0.05.
- HARD_FAIL (cardinality): n_units != 37.

Composition-depth envelope (REPORTED, not gated beyond the J5 co-gate): per arm, the
largest contiguous J in {1,2,5,8,16,32,64} holding keyed acc >= 0.95.

## Discriminator-survives-scale (option C hybrid)
The keyed ALGEBRA co-gate (keyed@J5 + shuffled leak + full J-sweep) FIRES AT SMOKE for
all 3 arms (codes exist; circular-conv runs at every J). The mechanism-fires check
(global-WTA block-occupancy std > 0 vs block-top-m std 0) FIRES AT SMOKE. The ret-LIFT
discriminator is FULL-only (smoke's tiny V_train cannot reproduce ret_agree10 coverage);
global-WTA is analytically a strict superset of block-top-m so its ceiling can only rise
(THEORETICAL). CANONICAL = remote-queue official landing, not local smoke.

## Cardinality
EXPECTED_N_UNITS = 37 = 3 arms x (3 semantic [CODE_LAST, DENSE_LAST, RANDOM] + 7 keyed
J-sweep on CODE_LAST + RANDOM@J5 + shuffled_key@J5) + CHARPOS(1) = 3*(3+9) + 1 = 37.
Same for smoke and full (SMOKE=FULL code path).

## SCHEMA-VET gates
- `cardinality_ok`: EXPECTED_N_UNITS=37 both modes; verdict emits HARD_FAIL_CARDINALITY if breached.
- `arms_differ_verified`: sha256 over each arm's code; block/gwta/expand codes distinct.
- `final_metrics_atomicity`: tmp_replace (write_metrics + atomic os.replace ckpt saves).
- `except SystemExit: raise` before `except Exception` (no BaseException / bare except).
- `discriminator_reachability`: True (SIGN K128 ceiling 0.4295 MEASURED@bypass; global-WTA superset; GSBC dense=1.0).
- `crlb_n_a`: ret_agree10 has no closed-form sigma CRLB; reachability via ceiling + superset argument.
- `baseline_in_band`: CHARPOS ret in (0.05,0.95); GSBC_RKD_BLOCK in [0.38,0.55].
- `calibration_check`: default_ok_for_this_regime.
- `cell_chunked` / `start_marker_written` / `crash_diagnostic_present` / `heartbeat_present` / `defensive_error_checking`: all satisfied.
- `progress_logging`: print_flush_true (train + unit loops flush).
- effective==nominal: sparsity fraction 2.34% is EFFECTIVE for every arm (block kb*m/out, gwta K/out).
- discriminating band: the paired-lift discriminator has headroom (baseline 0.44 vs ceiling 0.7-0.9).
- composition edges: single primitive (student -> code -> bind/unbind); SHAPE_MATCH (code reshapes to (kb,blk_l)).
- positive control: `GSBC_RKD_BLOCK` reproduces v11 GSBC_RKD ret AT the same regime (Gate-D tolerance band [0.38,0.55]).
- functional requirements: (1) retrieval agreement -> ret_agree10; (2) algebra survives binding -> keyed@J5 co-gate; (3) composition depth -> J-sweep envelope.

## Sequenced next
- HARD_PASS: density dial + full-M=177899 composition VET on the winning code + 3rd seed.
- ALGEBRA_DEGRADES: add a per-block min-occupancy constraint to global-WTA; re-test.
- NO_LIFT: block allocation is optimal at 2.34%; route to density dial (K256).

## Timeout
Smoke wall estimated ~60-120s (3 arms x 200 steps, width 256). FULL per seed ~ v11
(~465-700s at 8000 steps width 2048 + J-sweep keyed). timeout_s = 10800 (3h) per seed
(generous headroom for the added J-sweep keyed units; below the 14400s PROT-021 threshold,
but the cell imports _seed_checkpoint / checkpoints per-arm anyway).
