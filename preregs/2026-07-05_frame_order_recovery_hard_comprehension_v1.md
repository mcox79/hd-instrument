# Pre-registration: frame_order_recovery_hard_comprehension_v1

Date: 2026-07-05
Cell: `experiments/exp_frame_order_recovery_hard_comprehension_v1.py`
Anchor: `frame_order_recovery_hard_comprehension_v1`
Queue (FULL): `remote_cpu_queue` (CPU; numpy matched-filter + block-argmax; no GPU)

## Why this cell (Skunkworks VET scope-down)

`frame_classify_then_known_decode_v1` opened comprehension but its 1.000 was TRIVIAL-BY-CONSTRUCTION.
Its "frame" was a sorted D-subset with role d -> the d-th smallest occupied block, so recovering
WHICH-BLOCKS-OCCUPIED (the SET) fully determined role->block ORDER. Per-block occupancy energy = k
(constant) -> the classifier hit 1.000 even on random fillers, scoped to the SET at the EASY decode
regime (V1024/D3=1.000). The genuine hard comprehension -- recover role->block ORDER when occupancy is
DEGENERATE, survive SUPERPOSITION, and hold at the HARD decode regime -- was UNTESTED.

- prior (SET only): `data/exp_frame_classify_then_known_decode_v1/metrics.json:arms.sparse_block.parse_mean=1.0`  MEASURED
- decode hard cliff: `data/exp_generation_decoder_gsbc_native_blocklocal_v1:blocklocal_gsbc@V8192D26=0.856` (per_token 0.9945)  CITED

## The hard test (constructive; understand an UNKNOWN bound proposition at the HARD regime; NOT vs-LLM)

A frame is now an ASSIGNMENT (ordered map role d -> block frame[d]), NOT a sorted subset. Two frames with
the same occupied SET but different role->block ORDER have IDENTICAL per-block occupancy energy ->
occupancy is PROVABLY DEGENERATE for order (bias_audit proves energy(frame)==energy(role_swapped)). Each
role draws fillers from its OWN disjoint vocab partition (selectional restriction; brain-grounded thematic
typing) -> order is CONTENT-recoverable but occupancy-invisible.

Three conditions (all at N=8192; smoke reduces only trials/seeds, never geometry):
- ORDER:     B_TOTAL=8, bs=1024, D=3, V_ROLE=1024, one filler/block (chance order = 1/3! = 0.167)
- SUPERPOSE: B_TOTAL=8, bs=1024, D=4, V_ROLE=1024, B_OCC=2 (2 fillers/block; occupancy no longer 0/k)
- SCALE:     B_TOTAL=32, bs=256, D=26, V_ROLE=300 (V~7800 ~ cited V8192/D26 hard cliff)

## Arms (PAIRED -- same propositions + true frames across arms)

- `content_frame` (PRIMARY): role-typed matched filter -- for role r, assign r -> block with max
  partition-restricted correlation; decode by partition-restricted per-block argmax. Reads CONTENT-TYPE.
- `occupancy_baseline` (negative control, live): recognize SET (top-D energy blocks), then random order
  assignment (no order info). ORDER collapses to 1/D! by construction (the stressor bites).
- `decode_at_scale_posctrl`: full-codebook block-local decode GIVEN true frame (reproduces cited cliff).

## Metrics (report SEPARATELY per Fix #28)

- `set_recognition_acc`    -- P[recognized occupied SET == true SET]        (both arms; ~1.0 = the easy part)
- `order_recovery_acc`     -- P[role->block ASSIGNMENT == true]            (content vs occupancy = discriminator)
- `superposition_survival` -- P[full parse | >1 filler/block]              (content mechanism)
- `decode_at_scale_acc`    -- P[full-codebook exact_ordered decode | true frame] at V~8192/D26

## Pre-registered bands (envelope-fail-bands)

- HARD-PASS: order_content >= 0.75 AND order_occupancy <= 0.32 (near chance 0.167) AND gap >= 0.45 AND
  superposition_survival >= 0.50 AND decode_at_scale_full >= 0.60 (cited 0.856) AND order_cv <= 0.15, >=3 seeds.
  -> comprehension HOLDS at the hard regime.
- HARD-FAIL: order_content <= 0.25 (~chance) -> occupancy-degeneracy CONFIRMED; comprehension of ORDER needs
  a different mechanism than role-typed matched filtering.
- MIDDLE: SET recognized and ORDER above chance, but superposition_survival OR decode_at_scale below floor
  (set works, order/superposition/scale partial).

## BIAS audit (stressor must bite)

- Structural: per-block occupancy energy provably INVARIANT to role-swap within a fixed SET
  (`occupancy_degenerate_for_order == True`). If not, BLOCK_DISPATCH_BIAS_DEGENERATE.
- Empirical: occupancy_baseline order-recovery near chance (<= 0.32). If occupancy recovers order it should
  not, BLOCK_DISPATCH_BIAS_OCC_NOT_AT_CHANCE (degenerate test).
- Discriminator fires: order_content - order_occupancy >= 0.45.
- Gate D (positive control): full-codebook decode at scale reproduces the cited cliff (>= 0.60).

## SCHEMA-VET fields

- cardinality_ok: EXPECTED_N_UNITS = n_seeds * n_conditions = 3 * 3 = 9 (FULL).
- arms_differ_verified: content vs occupancy order-predictions hash-distinct per unit.
- final_metrics_atomicity: tmp_replace (os.replace).
- except SystemExit: raise BEFORE except Exception (no BaseException / bare except).
- crlb_n_a: order recovery in the clean single-filler regime is deterministic by self-correlation dominance
  (THEORETICAL); decode ceiling is CITED (0.856). No closed-form floor for the assignment step.
- baseline_in_band: occupancy at chance on ORDER (structural + empirical), not saturated; content is the arm.
- discriminator survives scale: smoke runs at full N=8192 and full block geometry (only trials/seeds reduced);
  the order gap + decode cliff both fire in smoke.
- HP strictly above floor: order 0.75 >> chance 0.167; decode 0.60 vs cited 0.856.
- HP_SCOPE: chain-grade HP gates apply ONLY to content_frame; occupancy carries only the near-chance BIAS gate.
- calibration_check: default_ok_for_this_regime (block-local sparse-code decode reproduces cited cliff at
  V~8192/D26 via the decode_at_scale posctrl; verified in smoke = 0.700 at 20 trials).
- progress_logging: line_buffered_stdout (sys.stdout.reconfigure line_buffering) + per-unit heartbeat.
- defensive_error_checking: start_marker + crash_diagnostic + heartbeat + atomic write (all 4).
- Referent: KB_REFERENT declares the GSBC pool npz (untracked; must exist on remote before FULL dispatch).

## Smoke result (MEASURED @ data/exp_frame_order_recovery_hard_comprehension_v1_smoke/metrics.json)

- SELFTEST PASS 1.6s; SMOKE HARD_PASS (SMOKE_MACHINERY_OK) 4.0s compute.
- BIAS occupancy_degenerate_for_order=True; order content=1.000 vs occupancy=0.200 (chance 0.167), gap=0.800;
  superposition parse=0.800; decode_at_scale(full,true)=0.700 (cited 0.856); scale content parse=0.700.

## Dispatch

- FULL -> remote_cpu_queue, timeout 600s (fast numpy; no _n suffix -> no PROT-019 floor). 3 seeds (7,13,19).
- PREREQ: SCP `data/gen_decoder_gsbc_fillers/gsbc_expand2x_pool_v1.npz` to remote (queue_add does NOT ship it).
