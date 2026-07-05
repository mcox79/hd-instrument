# PRE-REG: exp_reasoning_depth_keyslots_sharding_v1

Author: exp_dev 2026-07-05. Cell: `experiments/exp_reasoning_depth_keyslots_sharding_v1.py`.
Status: SELFTEST PASS + SMOKE HARD_PASS (local, N=8192). FULL staged (remote_cpu_queue).

## Question / redirect under test
A prior cell (`exp_cortex_iterative_attractor_cleanup_depth_ceiling_v1`) proved the
reasoning-depth ceiling of a shared Hebbian associative store is COLLISION-BOUND (chain-key
capacity), N-INDEPENDENT -- NOT crosstalk, NOT cleanup-bound. Its recorded redirect: deeper
chains come from MORE KEY SLOTS (richer relation/node vocab -> lower collision) + SHARDED
storage (partition chains across shards to reduce per-shard collision). THIS CELL tests that
redirect and confirms the collision model quantitatively.

## Arms (paired by (seed, N_TEST, N); matched difficulty + fidelity floor)
- ARM_BASELINE     P_REL=8,  S=1. K=V_CHAIN*8=2048. Reproduces the prior collision-bound ceiling (REFERENCE).
- ARM_KEYSLOTS_2x  P_REL=16, S=1. K=4096 (2x). Richer RELATION vocab. Lever 1.
- ARM_KEYSLOTS_4x  P_REL=32, S=1. K=8192 (4x). Lever 1 (stronger).
- ARM_SHARD_2      P_REL=8,  S=2. Same base chains sharded by chain-id -> eff cap 4096. Lever 2.
- ARM_SHARD_4      P_REL=8,  S=4. eff cap 8192. Lever 2 (stronger).
- ARM_SHUFFLED_CTL P_REL=32, S=1, objects shuffled -> chance (broken-discriminator rail).
Cleanup = single-shot argmax (MAP decoder; prior cell PROVED iterative==single-shot, so
cleanup-type is FIXED and key-capacity is the sole mechanism axis).

## HP_SCOPE (per-arm gate scope)
- mechanism arms (keyslots_*, shard_*): the HARD_PASS extension gate (best_delta>=2).
- baseline: the in-band gate only (SS_BAND_LO<=usable<=D_MAX-1, d1>=0.80).
- control: the chance gate only (usable<=HP_CTL_USABLE_MAX=1).

## Bands (envelope-fail-bands)
- HARD_PASS: base in band AND best mechanism (usable-base_usable) >= HP_DEPTH_MARGIN=2 (a real
  rightward shift of the collision cliff; censored-high mechanism arm counts usable=D_MAX) AND
  control usable<=1 AND arms differ AND base d1>=0.80. AGG: majority seeds PASS AND cross-seed
  cv<0.10 on continuous crossing_depth (base + disc) AND no HARD_FAIL_CTL.
- HARD_FAIL: base in band AND best_delta<=0 (NO lever extends -> ceiling NOT collision-bound,
  or sharding does not help).
- HARD_FAIL_CTL: control usable>1. HARD_FAIL_ARMS: base bit-identical to a mechanism arm (AF).
- ITERATE_REGIME: base not in band (REPORTED, not a refutation). MIDDLE_BAND: 0<best_delta<2, or
  extends-but-cv-unstable, or all-N ITERATE_REGIME.

## Collision model (prediction; REPORTED to confirm mechanism)
effective_key_capacity = V_CHAIN*P_REL*S. eff_fill_per_store = (N_TEST/S)*D_MAX/(V_CHAIN*P_REL).
collision_frac_theo = 1-((K-1)/K)^(M-1) (occupancy). predicted_usable ~ ln(0.5)/ln(1-coll_frac).
PREDICTION: usable_depth rises with eff capacity, falls with collision_frac; KEYSLOTS_2x and
SHARD_2 (equal eff cap 4096) predict EQUAL usable_depth -- both levers act through the same
collision physics (parameter-free cross-check).

## SCHEMA-VET mandatory fields
- cardinality_ok: EXPECTED_N_UNITS = seeds x N x N_TEST. smoke 3x1x1=3; full 5x2x3=30. Verdict gates on count.
- arms_differ_verified: true (smoke: arms_all_distinct=True; base differs from all mechanism arms; AF hash logged).
- final_metrics_atomicity: tmp_replace (os.replace of metrics.json.tmp).
- except SystemExit: raise BEFORE except Exception (no BaseException; grep-clean).
- crlb_n/a: no closed-form noise floor; the discriminating band [0.30,0.70] is richly populated by
  every arm's depth curve (baseline spans 0.96->chance across D=1..18). discriminator_reachability: true.
- baseline_in_band (AG): MEASURED smoke base usable 5-6 (d1 0.81-0.91) at N_TEST=32/D=18 -- in band, not saturated/floored.
- discriminator survives scale: collision law is N-INDEPENDENT (occupancy over key slots, not dim;
  MEASURED N-independent by prior cell). smoke ran at FULL N=8192 (option A/C preview). FULL adds N=16384 to confirm.
- calibration_check: default_ok_for_this_regime (P_REL/S/floor are FIXED principled; the equivalence
  KEYSLOTS_2x==SHARD_2 is parameter-free, not tuned-for-PASS).
- sweep_alignment_verdict: ALIGNED (the swept axis = effective key capacity; each arm's store
  literally experiences its declared K and S; no nominal/effective mismatch).
- discriminating_fraction: >=0.30 (all 6 arms trace full depth curves through the band).
- composition_edges: SHAPE_MATCH (single primitive: factored Hebbian retrieve -> argmax cleanup -> carry).
- positive_control_arms (Gate D): ARM_BASELINE reproduces the prior collision-bound ceiling AT THE
  TEST REGIME (V=512/V_CHAIN=256/P=8, N=8192); MEASURED base ud=5-6 vs prior K=2048/NT=25/D=12 ud~9
  (scaled by fill; d1>=0.80 single-hop works, graceful decay). regime_extension_audit: SHAPE_MATCH
  (identical scaffold to prior cell, reused FactoredStore/walk_curve/argmax_clean).
- functional_requirements: (1) store N chains recallably [factored Hebbian store]; (2) walk a chain
  regeneratively [argmax cleanup + clean-codeword carry]; (3) expand key capacity [P_REL vocab / shard-by-chain-id].
- shard routing correctness: self-test T3 (sharded retrieve == single-store-over-that-shard; mis-route changes retrieval).
- progress_logging: line_buffered_stdout + print(flush=True) on every progress line (timeout_s>=1800).
- start_marker_written / crash_diagnostic_present / heartbeat_present: true. cell_chunked: false (per-seed checkpoint via resumable_seeds).
- defensive_error_checking: passed_all_4_patterns.

## Compute architecture
SEQUENCE-DEPENDENT CPU (each hop depends on hop k-1 -- genuine chained-retrieval dependency
exemption) + cell IS the substrate cleanup primitive being validated. Storage = MIXED: bundled-
Hebbian per shard; sharding IS the swept mechanism axis (S=1 bundled baseline is the discriminator
reference per META_STORAGE_STRATEGY exemption (b)). Factored store (no NxN materialization),
M-chunked numpy batched matmul; sharded retrieval routes each chain to its shard by chain-id.

## SMOKE RESULT (local, N=8192, N_TEST=32, seeds 7/17/23, D_MAX=18)
HARD_PASS. base_usable=5.33 (d1 0.81-0.91, in band); best_delta=+12.67; keyslots_delta=+12.67;
shard_delta=+12.67; control usable=0.0; cv_base=0.030, cv_disc=0.0 (cross-seed stable); arms distinct.
Capacity law (arm: eff_cap, fill, mean_usable_depth, mean_collision_emp):
  baseline 2048/0.28/5.33/0.249 ; keyslots_2x 4096/0.14/8.0/0.138 ; keyslots_4x 8192/0.07/18(censored)/0.066 ;
  shard_2 4096/0.14/9.0/0.146 ; shard_4 8192/0.07/18(censored)/0.068 ; control 8192/0.07/0.0/0.066.
MECHANISM CONFIRMED: usable_depth monotone-decreasing in collision_frac; KEYSLOTS_2x (coll .138,
ud 8.0) == SHARD_2 (coll .146, ud 9.0) at equal eff cap 4096 (both levers, same physics); control at
same store size (coll .066) but ud=0 (extension is from STRUCTURE not store size). predicted_usable
(occupancy lower bound 2.5/4.9/9.9) under-predicts measured (colliding keys still resolve ~50%); the
ORDERING + EQUIVALENCE are the confirmations, absolute prediction is a conservative floor.
Note: 4x arms CENSORED at D_MAX=18 in this easy regime (+12.67 is a LOWER BOUND); FULL N_TEST=40
un-censors the 4x collapse for a measured 4x depth.
MEASURED@data/exp_reasoning_depth_keyslots_sharding_v1_smoke/metrics.json

## FULL grid (staged; remote_cpu_queue -- SMOKE-only-local rule)
N in {8192,16384} (N-independence confirm); N_TEST in {24,32,40} (rightward cliff-shift at 3
difficulties; NT=40 un-censors 4x); seeds {7,17,23,31,41}. EXPECTED_N_UNITS=30. run_mode=full.
timeout: ~60min est (t_unit ~ NT*N^2; smoke 48s @ NT32/N8192); recommend --timeout 9000 (2.5h,
checkpointed per-seed so a timeout resumes).
