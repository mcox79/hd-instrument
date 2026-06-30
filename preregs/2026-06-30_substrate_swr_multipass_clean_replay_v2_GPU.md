# Pre-registration: substrate_swr_multipass_clean_replay_v2_GPU

**Filed:** 2026-06-30
**Anchor:** substrate_swr_multipass_clean_replay_v2_GPU
**Script:** experiments/exp_substrate_swr_multipass_clean_replay_v2_GPU.py
**Queue:** overnight_queue (GPU)
**Tier:** MEASURED_MECHANISM (ceiling-confirmation / multi-pass dynamics)
**N_h / N_c:** 8192 / 2048
**M:** 2048 (alpha_simple=0.25; matches hippo_bottleneck v2)
**Seeds:** [7, 17, 23]

## v1 abort + v2 redesign
v1 (commit f27b65bc) modeled SWR as bundled outer-product (K items summed).
Smoke HARD_FAILED: bundling creates K^2 cross-terms; recall dropped to 0.001
at K=50. Honest abort. v2 redesigns as MULTI-PASS CLEAN REPLAY (brain's
actual SWR: many short re-extraction events per NREM3 cycle).

## Brain mechanism (CITED@brain_lit_NREM3_SWR_multipass)
NREM3 emits 50-200 sharp-wave-ripples per sleep cycle; each ripple is a brief
clean reactivation packet. Cumulative effect strengthens cortical engrams
over many ripples.

## Hypothesis (THEORETICAL)
Cumulative outer-product writes with shared keys amplify signal (each pass
adds eta*v outer c at matching pattern); noise from cross-terms partially
cancels under different permutation orders.

## Arms (5)

| Arm | N_replay | Mechanism |
|-----|----------|-----------|
| ARM_REPLAY_1 | 1 | Single clean pass (= v2 CLEAN_VALS baseline) |
| ARM_REPLAY_2 | 2 | 2 passes; different perm each |
| ARM_REPLAY_5 | 5 | 5 passes |
| ARM_REPLAY_10 | 10 | 10 passes (brain-realistic) |
| ARM_REPLAY_20 | 20 | 20 passes (saturation test) |

## Pre-registered bands

Let R_X = mean(recall) across 3 seeds.

**HARD_PASS:**
- Ceiling-confirmation: ALL N_REPLAY arms >= 0.90 (clean multi-pass reaches
  near-DIRECT), OR
- Lift-confirmed: best_lift over ARM_REPLAY_1 >= 0.05
**MIDDLE_BAND:** best_lift in [0.01, 0.05)
**HARD_FAIL:**
- best recall < 0.5 (substrate broken)
- META_RULE_AF violation
- Cardinality breach

## Discriminator-must-survive-scale (META_RULE_AG)

Smoke at M=512 (alpha=0.25 SAME as full) HARD_PASS ceiling-confirmed: all
arms 1.000 (smoke too small, trivially solved). At full M=2048 the v2
CLEAN_VALS arm measured 0.985 single-pass — this cell tests whether N_replay
>= 2 reaches 1.0 or stays at 0.985 ceiling. EITHER outcome is informative:

- Ceiling at 0.985 across all N_replay = single-pass clean is the ceiling;
  no multi-pass benefit; chain-grade negative result.
- Lift > 0.985 at some N_replay = multi-pass consolidation works; brain
  literature aligned.

AF hashes all distinct at smoke. Mechanism arms genuinely differ.

## Pre-reg schema fields
- cardinality_ok: true (5 * 3 = 15 units)
- arms_differ_verified: true (smoke confirmed)
- final_metrics_atomicity: "tmp_replace"
- crlb_n/a: "associative-memory capacity not CRLB"
- baseline_in_band: smoke saturates; full baseline known 0.985 (above 0.5
  band; below 1.0 ceiling -> in band)
- discriminator_reachability: true (ceiling-confirmation OR lift both valid)
- calibration_check: "default_ok_for_this_regime"
- cell_chunked: false
- start_marker_written: true
- crash_diagnostic_present: true
- heartbeat_present: true
- defensive_error_checking: "passed_all_4_patterns"

## Dispatch destination + timeout
- Queue: overnight_queue (GPU; torch matmul + 20-pass replay)
- timeout_s: 1800 (30 min; ~10s/seed at full * 3 + margin)
- No PROT-018/019 _n suffix

## Coordination
- Cell-author: exp_dev
- Landed-VET: skunkworks
- Push gate: hd_metrics_sync auto-push
