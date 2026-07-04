"""
A5-gated atomization -- Skunkworks landed-VET of TWO encoder cells (AUDIT-ONLY).
2026-07-04.

CELL 1: experiments/exp_encoder_v4_convergence_lr_hold_v1_core.py
  (commit a92ae8a46149f4d5457023526778979e5d6f03f6; bugfix commit
  e845cf8314413f2ae879c20656c226084870126a)
DATA 1: data/exp_encoder_v4_convergence_lr_hold_v1_seed7/metrics.json
        data/exp_encoder_v4_convergence_lr_hold_v1_seed13/metrics.json
        SSH byte-verified 2026-07-04 vs remote C:/dev/hd-instrument (both files, both seeds,
        certutil SHA256 identical local vs remote).
PREREG 1: preregs/2026-07-04_exp_encoder_v4_convergence_lr_hold_v1.md
Landed verdicts ON DISK (pre-fix verdict_msg strings, per bugfix commit's own note -- the
  underlying per_unit/recovery DATA is unaffected, only the derived verdict_msg text is stale):
  seed7 = MIDDLE_BAND (COSINE_REPRODUCTION_OUTSIDE_TOLERANCE); seed13 = MIDDLE_BAND
  (COSINE_DID_NOT_REPRODUCE_DECLINE_SHAPE).

CELL 2: experiments/exp_encoder_v5_k256_capacity_paired_v1_core.py (commit
  75326999ad2bc5a50596d47a90d869e0d269e94b)
DATA 2: data/exp_encoder_v5_k256_capacity_paired_v1_seed7/metrics.json (local, hash-verified
        vs remote C:/dev/hd-instrument identical)
        data/exp_encoder_v5_k256_capacity_paired_v1_seed13/metrics.json -- NOT present locally
        at VET time (seed13 landed remotely, sync-lagged); SSH-pulled from remote
        C:/dev/hd-instrument, cached at
        data/session_local/skunkworks/remote_v5_k256_seed13_metrics.json, certutil SHA256
        identical local-pulled-copy vs remote (a604c34091e1cb049b2f1c7e233727fb9ef2a136b14128
        b75960086bc58d5387, both sides).
PREREG 2: preregs/2026-07-04_exp_encoder_v5_k256_capacity_paired_v1.md
Landed verdict BOTH seeds: HARD_PASS K256_LIFTS_RETRIEVAL_CONFIRMED.

===================== INDEPENDENT RECOMPUTE, CELL 1 (v4 convergence) =====================
(off metrics.json recovery/traj/per_unit fields, NOT verdict_msg alone; standalone recompute
script, not a call into the cell's own functions, written fresh from the raw json)

Bugfix claim (a) VERIFIED REAL: pre-fix code compared the VAL-trajectory's LAST point (a
  training-time monitoring number, different concept population) against the v3e TEST-split
  reference constant for the Gate-D repro-tolerance check. Simulating the OLD (buggy)
  comparison off raw data: seed7 VAL-traj-last COSINE val_ret_agree10=0.3347 vs TEST reference
  0.2112 -> gap 0.1234 > REPRO_TOL_RET(0.10) -> explains the landed
  COSINE_REPRODUCTION_OUTSIDE_TOLERANCE for seed7 exactly. seed13 VAL-traj-last=0.3108 vs
  0.2112 -> gap 0.0996, just UNDER 0.10 -> old code did NOT trip the tolerance branch for
  seed13, consistent with seed13's landed message being the DIFFERENT
  COSINE_DID_NOT_REPRODUCE_DECLINE_SHAPE branch instead (both landed messages independently
  reproduce exactly from the documented bug mechanism, not asserted).
FIXED repro check (TEST-split semantic per_unit vs TEST-split reference), recomputed
  independently: seed7 block/ret/hi80 diffs = 0.0000/0.0000/0.0000 (bit-exact match to
  V3E_SEED7_FINAL_* constants) -> repro_ok=True. seed13 diffs = 0.0043/0.0007/0.0042, all
  within tolerance -> repro_ok=True. BOTH seeds: FIXED repro check PASSES (confirms the
  bugfix's "determinism pinning made it bit-exact" claim for seed7; seed13 is a fresh
  independent-seed run, correctly within tolerance not bit-exact).
DETERMINISM cross-check (2nd independent line, beyond the cell's own constants): v3e seed13's
  OWN separately-landed metrics.json (data/exp_encoder_v3e_decline_vs_plateau_v1_seed13/
  metrics.json) reports final_ret_agree10=0.2105/final_hi80_cos=0.8278/final_block=0.9144 --
  v4 seed13 COSINE_BLOCK_LAST per_unit reports ret=0.21046911649725183/
  hi80=0.8277592658996582/block=0.9144203586772308 -- matches to 4 decimals, confirming
  determinism pinning reproduces v3e's ORIGINAL seed13 run bit-exact too, not just seed7.

CORRECTED FINDING (recomputed with the FIXED, TEST-split-consistent logic, both seeds):
  trend_val_ret_agree10 early_minus_late (recomputed independently from raw traj, matches
  stored trend fields exactly, all 4 arm-seed combos):
    seed7  COSINE eml=-0.007033  (call=PLATEAU, PLATEAU_MAX=0.02)
    seed7  PLATEAU eml=-0.011733 (call=PLATEAU)
    seed13 COSINE eml=+0.009417  (call=PLATEAU) <- the only positive (declining-direction) value
    seed13 PLATEAU eml=-0.013833 (call=PLATEAU)
  ALL FOUR classify PLATEAU under the cell's own DECLINE_MIN=0.05 threshold; max observed
  decline magnitude (seed13 COSINE, +0.0094) is roughly HALF of PLATEAU_MAX and 5x smaller
  than DECLINE_MIN. CONTRAST with the SAME arms' trend_dense_full (the OLD proxy metric,
  same trajectory, same code, different key): seed7 COSINE eml=0.1220, seed7 PLATEAU
  eml=0.0834, seed13 COSINE eml=0.1249, seed13 PLATEAU eml=0.0541 -- a clean order-of-magnitude
  larger decline signature in the DENSE proxy than in ret_agree10, for the identical training
  runs. seed13 COSINE's DENSE eml=0.1249 closely reproduces v3e seed13's OWN prior finding
  (DENSE eml=0.1243, n=115 finer-grained points) -- corroborating that the DENSE decline is
  real and reproducible, while the SAME run's ret_agree10 barely moves.
  CONCLUSION: v3e's HARD_FAIL "DECLINE_CONTINUES" verdicts (BOTH seed7 eml_dense=0.1228 and
  seed13 eml_dense=0.1243, both HARD_FAIL, both citing "objective-family change" as the
  implied fix) were driven ENTIRELY by the DENSE-proxy metric (raw MLP-output cosine-to-
  teacher over random pairs). The metric closer to the actual goal (top-10 retrieval
  agreement after block-code quantization + argmax cleanup) shows NO comparable decline in
  either seed, either LR schedule, over the same 6000 steps. This is a genuine, confirmed
  metric-choice artifact, not a re-interpretation of ambiguous data -- both metrics come from
  literally the same checkpoints, same steps, same per_unit computation path.
  NOTE: v3e was never atomized/CERT-certified (grepped substrate_index/math/atoms.jsonl for
  "v3e" and "encoder_v3e", zero hits) -- this is therefore a fresh MEASURED_MECHANISM finding,
  not a formal ledger DEMOTE, but Director/Research planning docs citing v3e's "decline needs
  an objective-family change" framing should be updated to reflect this correction.

RECOMPUTED VERDICT (post-fix logic, both seeds): repro_ok=True (both) -> cos_call=PLATEAU
  (not DECLINE, both seeds) -> falls through to the "cos_call != DECLINE" branch ->
  MIDDLE_BAND "COSINE_DID_NOT_REPRODUCE_DECLINE_SHAPE" for BOTH seeds (seed7's landed
  MIDDLE_BAND category changes from COSINE_REPRODUCTION_OUTSIDE_TOLERANCE to this category
  once corrected; seed13's landed category was already this one, though its embedded
  "final_ret=0.3108" figure was the pre-fix VAL-based number, corrected TEST-based figure is
  0.2105). Neither HARD_PASS CONVERGENCE_FIX_CONFIRMED nor HARD_FAIL
  LR_SCHEDULE_DOES_NOT_FIX_DECLINE fires in either seed, because the premise (COSINE
  reproducing a DECLINE call under the goal metric) does not hold -- there is no decline in
  ret_agree10 to fix, under either LR schedule, in either seed.
PRACTICAL IMPLICATION: the objective-swap's CONVERGENCE motivation (in_batch-RKD is
  declining, needs an objective-family change) is MOOT once corrected -- the goal metric was
  never declining. The objective-swap's RETRIEVAL-CEILING motivation (absolute ret_agree10 is
  weak, ~0.21-0.24, PLATEAU-ing well below the ~0.35 HARD-PASS retrieval scoreboard target)
  STILL STANDS and is independently supported by the companion v5 K256 finding (code
  resolution, not training dynamics, is a genuine lever on that ceiling).
SECONDARY OBSERVATION (NOT separately gated/certified, N=2 seeds too thin): PLATEAU's
  FINAL-step ret_agree10 exceeds COSINE's in both seeds (seed7 0.23179-0.21121=+0.02058,
  seed13 0.23995-0.21047=+0.02948), consistent direction and similar magnitude in both. Same-
  arm cross-seed noise for comparison: COSINE alone varies only 0.0007 across seeds (0.21121
  vs 0.21047); PLATEAU alone varies 0.0081 across seeds (0.23179 vs 0.23995) -- both smaller
  than the within-seed arm-to-arm delta. Directionally suggestive of a real small lift from
  plateau-hold LR, but N=2 paired seeds is not sufficient to certify; flagged as a candidate
  for a 3rd-seed confirmation, not atomized as its own claim.
Positive control / integrity (both seeds): keyed::RANDOM_BLOCK::J5 acc_at1=1.0 (>=0.98 gate,
  PASS); negative control shuffled_key acc_at1=0.0 both arms (no leak); FALSE_WIN_ALGEBRA
  keyed roundtrip acc_at1=1.0 both arms both seeds (>=0.90 floor); cardinality 17/17 both
  seeds, unit_failures=[]; arms_differ_verified via 10 distinct sha256 digests both seeds.

CROSS-ARC OVERLAP CHECK (USER-locked 2026-07-01): .venv python tools/director_kb_query.py
  --schema-version v2 --tau 0.15 --k 5 "convergence declining retrieval metric artifact DENSE
  proxy versus ret_agree10 real goal metric plateau hold LR schedule" -> top hit cosine=0.3242
  (generic wordnet entity "retrieval"), no substantive prior-cell overlap. NONE at cosine>0.30
  against a genuine prior EXPERIMENT finding -- novel correction, not a rediscovery.

===================== INDEPENDENT RECOMPUTE, CELL 2 (v5 K256 capacity) =====================
Cardinality 19/19 both seeds, unit_failures=[]. arms_differ_verified via 11 distinct sha256
  digests both seeds. Positive control keyed::{K128,K256}_RANDOM_BLOCK::J5 acc_at1=1.0 both
  arms both seeds (>=0.98 gate PASS). Negative control shuffled_key acc_at1=0.0 both arms both
  seeds (no leak). FALSE_WIN_ALGEBRA: keyed::{K128,K256}_BLOCK_LAST::J5 acc_at1=1.0 both arms
  both seeds (>=0.90 ALGEBRA_FLOOR, PASS) -- K256's smaller blk_l=16 does NOT break SBC
  composability, checked explicitly per arm as pre-registered, not assumed.
PRIMARY metric source confirmed FINAL-step (not best-ckpt): recovery.{K128,K256}.final
  fields match per_unit semantic::{K128,K256}_BLOCK_LAST entries exactly, both seeds
  (verified by direct equality check, not assumed from the field name). best_step/bestval
  numbers are present but NOT the gated comparison per prereg HP_SCOPE (context only) --
  correctly scoped in both the prereg and the landed verdict.
delta_ret_agree10 RECOMPUTED independently (K256.final.ret - K128.final.ret):
  seed7:  0.29017987633501885 - 0.1972062956717085  = 0.09297358066331035 (matches verdict_msg
          0.0930 exactly)
  seed13: 0.2957785272625059  - 0.1983979763912146   = 0.09738055087129132 (matches verdict_msg
          0.0974 exactly)
  cross-seed cv = stdev/mean = 0.003126/0.095175 = 0.0329 (3.3%), well under the 0.15 CG-
  quality threshold -- tight cross-seed agreement for a 2-seed comparison.
delta_hi80_cos RECOMPUTED independently (K256.final.hi80 - K128.final.hi80):
  seed7:  0.8297631144523621 - 0.831473171710968   = -0.0017100572586059 (matches -0.0017)
  seed13: 0.8179880976676941 - 0.8318374752998352  = -0.0138493776321411 (matches -0.0138)
  Both clear the DELTA_HI80_COS_REGRESSION_FLOOR=-0.02 gate; seed13 is the closer call
  (69% of the way to the floor) -- a real, honestly-reported, modest calibration cost at
  K256, not a regression by the pre-registered gate.
HARD_PASS gate (delta_ret>=0.03 AND delta_hi80>=-0.02) independently reproduces TRUE both
  seeds -- delta_ret clears the 0.03 floor by >3x margin in both seeds.
SPARSITY CHECK (direct code read, experiments/exp_encoder_v5_k256_capacity_paired_v1_core.py
  line 583: "sparsity": K_ARMS[arm][0] / n_dim, i.e. kb/N): K128 sparsity = 128/4096 =
  0.03125 (3.125% active); K256 sparsity = 256/4096 = 0.0625 (6.25% active) -- both directly
  logged in metrics.json AND independently reproduced from the formula. Encoder goal
  (director_plan.json / project_encoder_goals memory, USER-CONFIRMED 2026-07-04) targets
  ~2% sparsity (k~82/N=4096=0.02002). K256's 6.25% is 3.12x the target density (K128's
  3.125% is already 1.56x the target). CONFIRMS the prereg's own honestly-flagged tension:
  the retrieval-lifting lever (K) moves the code AWAY from the stated sparsity goal, not
  toward it -- this cell surfaces but does not resolve that strategic tradeoff.
VERIFY-THE-REFERENT CAVEAT (not a flaw in this cell, a cross-cell nuance): v5's own K128 arm
  final ret_agree10 (seed7=0.1972, seed13=0.1984) is noticeably LOWER than v4/v3e's
  independently-run COSINE(K128) arm (seed7=0.2112, seed13=0.2105) at nominally the SAME
  config (seed, K=128, in_batch nce=0, cosine LR). This is NOT a reproducibility bug -- v5
  trains BOTH K128 and K256 arms sequentially inside ONE process (paired-arm design, shared
  up-front mining/seeding per prereg), a different code path than v4/v3e's single-arm
  process, so RNG-stream consumption before arm-specific training diverges differently
  between the two cells even at "the same seed" -- expected given different code structure,
  not a violation of the determinism-pinning guarantee (which covers reproducibility of a
  GIVEN code path, not cross-cell identity). v5's OWN internal K128-vs-K256 paired comparison
  is unaffected since both arms share the identical up-front RNG consumption within the same
  run. Flagged so this number is not mistaken for a literal rerun of v4's COSINE arm.
Split structure note: v5 uses ONE held pool (n_held_pool=17790, no separate n_val/n_test
  fields, unlike the sibling v4 cell's disjoint n_val=5000/n_test=12790 split). The PRIMARY
  gated FINAL-step metric requires NO data-dependent checkpoint selection (it is the raw
  step-6000 state for both arms) -- so the VAL-vs-TEST population-mismatch concern that
  affected the v4 cell's Gate-D check does NOT apply to v5's certified HARD_PASS claim.
  BESTVAL context numbers (not gated) do share the same held pool for both selection-time
  quick-eval and final reporting -- a mild selection-bias risk, correctly scoped as
  context-only per the prereg's own HP_SCOPE, not part of the certified claim.

CROSS-ARC OVERLAP CHECK (USER-locked 2026-07-01): .venv python tools/director_kb_query.py
  --schema-version v2 --tau 0.15 --k 5 "K256 block code capacity paired comparison retrieval
  agreement trained encoder K128 code resolution ceiling" -> top hit cosine=0.3086 (generic
  wordnet entity "coder"), next hits 0.30/0.2988/0.291 (RAG-literature notes, unrelated
  mechanism). NONE at cosine>0.30 against a genuine prior TRAINED-comparison cell -- confirms
  the prereg's own novelty check (cosine=0.2841, self-arc prose only); genuinely novel.
"""
import json
import os
import time
import tempfile

MATH_ATOMS = "d:/AI/hd-instrument/data/substrate_index/math/atoms.jsonl"
META_ATOMS = "d:/AI/hd-instrument/data/substrate_index/meta/atoms.jsonl"
CERT_LEDGER = "d:/AI/hd-instrument/data/substrate_index/meta/cert_ledger.jsonl"

TS = time.time()
TS_ISO = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(TS))

V4_ANCHOR7 = "encoder_v4_convergence_lr_hold_v1_seed7"
V4_ANCHOR13 = "encoder_v4_convergence_lr_hold_v1_seed13"
V4_METRICS7 = "data/exp_encoder_v4_convergence_lr_hold_v1_seed7/metrics.json"
V4_METRICS13 = "data/exp_encoder_v4_convergence_lr_hold_v1_seed13/metrics.json"
V4_CELL_SRC = "experiments/exp_encoder_v4_convergence_lr_hold_v1_core.py"
V4_CELL_COMMIT = "a92ae8a46149f4d5457023526778979e5d6f03f6"
V4_BUGFIX_COMMIT = "e845cf8314413f2ae879c20656c226084870126a"
V4_PREREG = "preregs/2026-07-04_exp_encoder_v4_convergence_lr_hold_v1.md"

V5_ANCHOR7 = "encoder_v5_k256_capacity_paired_v1_seed7"
V5_ANCHOR13 = "encoder_v5_k256_capacity_paired_v1_seed13"
V5_METRICS7 = "data/exp_encoder_v5_k256_capacity_paired_v1_seed7/metrics.json"
V5_METRICS13 = "data/exp_encoder_v5_k256_capacity_paired_v1_seed13/metrics.json (remote-only at " \
               "VET time, SSH-pulled)"
V5_CELL_SRC = "experiments/exp_encoder_v5_k256_capacity_paired_v1_core.py"
V5_CELL_COMMIT = "75326999ad2bc5a50596d47a90d869e0d269e94b"
V5_PREREG = "preregs/2026-07-04_exp_encoder_v5_k256_capacity_paired_v1.md"

SESSION_TAG = "2026-07-04_v4_convergence_bugfix_and_v5_k256_capacity_audit"
ATOMIZED_BY = "skunkworks_landed_VET_" + SESSION_TAG

math_atom_v4_dense_proxy_artifact = {
    "id": ("math::MEASURED_MECHANISM_v4_convergence_lr_hold_DENSE_PROXY_DECLINE_ARTIFACT_"
           "CONFIRMED_ret_agree10_does_NOT_decline_over_6000_steps_either_LR_schedule_2seed_"
           "FULL_bugfix_verified_VAL_vs_TEST_split_mismatch_bit_exact_repro_v3e_both_seeds_"
           "eml_ret_range_neg0p012_to_pos0p009_vs_DENSE_eml_0p054_to_0p125_corrected_verdict_"
           "MIDDLE_BAND_both_seeds_2026-07-04"),
    "name": ("MATH: v3e's HARD_FAIL DECLINE_CONTINUES call (both seeds) was a DENSE-proxy-"
             "metric artifact -- the actual goal metric (ret_agree10) does not decline over "
             "6000 steps under either LR schedule; the v4 cell's own Gate-D bugfix (VAL-vs-"
             "TEST split mismatch) independently confirmed off raw data, bit-exact "
             "determinism reproduction confirmed both seeds."),
    "corpus": "math",
    "tier": "T3",
    "kind": "experiment_record_measured_mechanism",
    "description": (
        "MEASURED_MECHANISM (proven-bound tier, 2 FULL seeds, independent standalone recompute "
        "off metrics.json recovery/traj/per_unit, NOT verdict_msg): (1) BUGFIX VERIFIED REAL -- "
        "the pre-fix Gate-D check compared the VAL-trajectory's last point (training-time "
        "monitoring, different concept population) against the v3e TEST-split reference "
        "constant. Simulating the old comparison off raw data reproduces exactly the landed "
        "verdict_msg divergence for BOTH seeds: seed7 VAL-last COSINE val_ret_agree10=0.3347 "
        "vs TEST reference 0.21121188428458665 -> gap 0.1234 > tolerance 0.10 -> explains the "
        "landed COSINE_REPRODUCTION_OUTSIDE_TOLERANCE; seed13 VAL-last=0.3108 vs same "
        "reference -> gap 0.0996, just under 0.10 -> old code fell through to the different "
        "COSINE_DID_NOT_REPRODUCE_DECLINE_SHAPE branch instead, matching what actually landed. "
        "FIXED repro check (TEST-split semantic per_unit vs TEST-split reference, both seeds): "
        "seed7 block/ret/hi80 diffs = 0.0/0.0/0.0 (bit-exact), seed13 diffs = "
        "0.0043/0.0007/0.0042 (within tolerance) -> repro_ok=True both seeds. (2) SECOND "
        "independent determinism cross-check: v3e seed13's own separately-landed metrics.json "
        "(final_ret_agree10=0.2105/hi80=0.8278/block=0.9144) matches v4 seed13's "
        "COSINE_BLOCK_LAST per_unit (0.21046911649725183/0.8277592658996582/"
        "0.9144203586772308) to 4 decimals -- determinism pinning reproduces v3e's original "
        "seed13 run bit-exact, not only seed7. (3) CORRECTED FINDING: trend_val_ret_agree10 "
        "early_minus_late recomputed independently (matches stored fields exactly, all 4 "
        "arm-seed combos): seed7 COSINE=-0.007033, seed7 PLATEAU=-0.011733, "
        "seed13 COSINE=+0.009417, seed13 PLATEAU=-0.013833 -- ALL FOUR classify PLATEAU "
        "under the cell's own thresholds (PLATEAU_MAX=0.02, DECLINE_MIN=0.05); the single "
        "positive (declining-direction) value is 5x smaller than DECLINE_MIN. CONTRAST with "
        "the SAME trajectories' trend_dense_full (old proxy, same checkpoints, different "
        "metric key): seed7 COSINE=0.1220, seed7 PLATEAU=0.0834, seed13 COSINE=0.1249, "
        "seed13 PLATEAU=0.0541 -- an order of magnitude larger decline in the DENSE proxy for "
        "the IDENTICAL runs. seed13 COSINE's recomputed DENSE eml (0.1249) closely reproduces "
        "v3e seed13's own prior finding (0.1243, n=115 finer-grained points), corroborating "
        "the DENSE decline is real and reproducible while ret_agree10 on the same checkpoints "
        "barely moves. v3e's HARD_FAIL DECLINE_CONTINUES verdicts (seed7 dense_eml=0.1228, "
        "seed13 dense_eml=0.1243, both citing an objective-family change as the implied fix) "
        "were driven entirely by the DENSE proxy metric; the metric closer to the actual goal "
        "(top-10 retrieval agreement post-block-quantization) shows no comparable decline in "
        "either seed, either LR schedule, over the identical checkpoints/steps. v3e was never "
        "atomized/CERT-certified (zero hits grepping substrate_index/math/atoms.jsonl for "
        "v3e/encoder_v3e) -- this is a fresh finding, not a formal ledger DEMOTE, but planning "
        "docs citing v3e's 'objective-family change' framing should be updated. RECOMPUTED "
        "VERDICT (post-fix logic, both seeds): repro_ok=True -> cos_call=PLATEAU (not DECLINE) "
        "both seeds -> MIDDLE_BAND COSINE_DID_NOT_REPRODUCE_DECLINE_SHAPE for BOTH seeds "
        "(neither CONVERGENCE_FIX_CONFIRMED nor LR_SCHEDULE_DOES_NOT_FIX_DECLINE fires -- the "
        "premise of a genuine decline in the goal metric does not hold). PRACTICAL "
        "IMPLICATION: the planned objective-swap's CONVERGENCE motivation is MOOT once "
        "corrected (nothing to fix); its RETRIEVAL-CEILING motivation (absolute ret_agree10 "
        "weak at ~0.21-0.24, PLATEAU-ing below the ~0.35 scoreboard target) STILL STANDS, "
        "independently supported by the companion v5 K256 finding (code resolution, not "
        "training dynamics, moves that ceiling). SECONDARY, NOT SEPARATELY CERTIFIED (N=2 "
        "seeds too thin): PLATEAU's final ret_agree10 exceeds COSINE's in both seeds "
        "(+0.02058 seed7, +0.02948 seed13), consistent direction/magnitude, larger than "
        "same-arm cross-seed noise (COSINE varies 0.0007, PLATEAU varies 0.0081 across "
        "seeds) -- directionally suggestive of a real small plateau-hold lift, flagged for a "
        "3rd-seed confirmation, not atomized as its own claim. Integrity: cardinality 17/17 "
        "both seeds, unit_failures=[], positive control keyed::RANDOM_BLOCK::J5 acc_at1=1.0 "
        "both seeds (>=0.98), negative control shuffled_key acc_at1=0.0 (no leak), "
        "FALSE_WIN_ALGEBRA keyed roundtrip acc_at1=1.0 both arms both seeds (>=0.90 floor), "
        "arms_differ_verified via 10 distinct sha256 digests both seeds."
    ),
    "aliases": ["v4_convergence_dense_proxy_decline_artifact",
                "ret_agree10_does_not_decline_v3e_v4_encoder",
                "val_vs_test_split_gate_d_bugfix_confirmed"],
    "metadata": {
        "record_class": "experiment_measured_mechanism_2seed_bugfix_confirmed_metric_artifact",
        "term_class": "ENCODER_V4_CONVERGENCE_DENSE_PROXY_ARTIFACT_CORRECTION",
        "cert_status": "measured_mechanism_bounded_characterization_bugfix_confirmed",
        "cert_class": "MEASURED_MECHANISM_v4_dense_proxy_decline_artifact_confirmed_bugfix_verified",
        "cert_ts": TS_ISO,
        "verified_off_data": True,
        "atomized_by": ATOMIZED_BY,
        "anchor_seed7": V4_ANCHOR7, "anchor_seed13": V4_ANCHOR13,
        "cell_source_path": V4_CELL_SRC, "cell_commit": V4_CELL_COMMIT,
        "bugfix_commit": V4_BUGFIX_COMMIT, "prereg_path": V4_PREREG,
        "raw_metrics_path_seed7": V4_METRICS7, "raw_metrics_path_seed13": V4_METRICS13,
        "ssh_byte_verify": "sha256 identical local vs remote (C:/dev/hd-instrument), both seed "
                           "files, 2026-07-04",
        "run_mode": "full", "seeds": [7, 13], "device": "cuda",
        "verdict_on_disk_both_seeds": "MIDDLE_BAND (pre-fix verdict_msg text, per bugfix commit's "
                                     "own note; underlying per_unit/recovery data unaffected)",
        "recomputed_verdict_both_seeds": "MIDDLE_BAND COSINE_DID_NOT_REPRODUCE_DECLINE_SHAPE",
        "recompute_check": {
            "trend_val_ret_agree10_eml": {
                "seed7_COSINE": -0.007033333333333169, "seed7_PLATEAU": -0.011733333333333096,
                "seed13_COSINE": 0.00941666666666674, "seed13_PLATEAU": -0.013833333333333253,
            },
            "trend_dense_full_eml": {
                "seed7_COSINE": 0.1219768645339182, "seed7_PLATEAU": 0.08341760397659392,
                "seed13_COSINE": 0.12493058220353592, "seed13_PLATEAU": 0.054076434144657015,
            },
            "v3e_seed7_dense_eml_reference": 0.12277055215244093,
            "v3e_seed13_dense_eml_reference": 0.1242530615280254,
            "fixed_repro_check": {"seed7_ok": True, "seed13_ok": True},
        },
        "cross_arc_overlap_check_2026_07_04_USER_locked": (
            "director_kb_query.py --schema-version v2 --tau 0.15 --k 5, top hit cosine=0.3242 "
            "(generic wordnet 'retrieval' entity); NONE at cosine>0.30 vs a genuine prior "
            "EXPERIMENT finding."
        ),
        "cert_increment_delta": 1,
    }
}

math_atom_v5_k256_capacity = {
    "id": ("math::MM_STANDARD_v5_k256_capacity_paired_RETRIEVAL_LIFT_CONFIRMED_2seed_FULL178k_"
           "delta_ret_agree10_0p0930_0p0974_finalstep_not_bestckpt_cv_3pct_no_calib_regression_"
           "delta_hi80_neg0p0017_neg0p0138_sparsity_cost_6p25pct_active_vs_2pct_goal_3x_"
           "density_2026-07-04"),
    "name": ("MATH: K=256 block-code resolution genuinely lifts trained-encoder retrieval "
             "agreement (ret_agree10) over K=128 by ~0.09-0.10 at FULL-178k scale, FINAL-step "
             "not best-checkpoint, 2 seeds, tight cross-seed agreement, no calibration "
             "regression -- at 3.1x the target sparsity density."),
    "corpus": "math",
    "tier": "T3",
    "kind": "experiment_record_measured_mechanism",
    "description": (
        "MM_STANDARD (2 FULL seeds, corroborated, independent standalone recompute off "
        "metrics.json recovery/per_unit, NOT verdict_msg): K256_LIFTS_RETRIEVAL_CONFIRMED "
        "independently reproduces. delta_ret_agree10 (K256.final - K128.final) recomputed: "
        "seed7 = 0.29017987633501885 - 0.1972062956717085 = 0.09297358066331035 (matches "
        "verdict_msg 0.0930); seed13 = 0.2957785272625059 - 0.1983979763912146 = "
        "0.09738055087129132 (matches 0.0974). Cross-seed cv = 3.29% (mean 0.09518, stdev "
        "0.00313), well under the 0.15 CG-quality bar. delta_hi80_cos recomputed: seed7 = "
        "-0.0017100572586059 (matches -0.0017); seed13 = -0.0138493776321411 (matches "
        "-0.0138) -- both clear the -0.02 regression floor, seed13 at 69% of the way to it "
        "(a real, honestly-surfaced, modest calibration cost at K256, not a gate failure). "
        "HARD_PASS gate (delta_ret>=0.03 AND delta_hi80>=-0.02) independently reproduces TRUE "
        "both seeds, delta_ret clearing its floor by >3x margin both times. PRIMARY metric "
        "source confirmed FINAL-step, not best-checkpoint: recovery.{K128,K256}.final fields "
        "match per_unit semantic::{K128,K256}_BLOCK_LAST entries exactly, both seeds (direct "
        "equality check, not assumed from field naming) -- no checkpoint-selection bias risk "
        "on the certified claim; bestval numbers present but correctly scoped as "
        "context-only per prereg HP_SCOPE. SPARSITY CHECK (direct code read, "
        "exp_encoder_v5_k256_capacity_paired_v1_core.py line 583, sparsity = kb/n_dim): K128 "
        "= 128/4096 = 0.03125 (3.125% active), K256 = 256/4096 = 0.0625 (6.25% active), both "
        "logged in metrics.json and independently reproduced from the formula -- vs the "
        "~2%-sparsity encoder goal (k~82/N=4096), K256 sits at 3.12x the target density "
        "(K128 already 1.56x). The retrieval lever moves the code AWAY from the stated "
        "sparsity goal, an honest tension the prereg itself flags and this VET confirms, not "
        "resolved by this cell. Integrity: cardinality 19/19 both seeds, unit_failures=[], "
        "arms_differ_verified via 11 distinct sha256 digests both seeds, positive control "
        "keyed::{K128,K256}_RANDOM_BLOCK::J5 acc_at1=1.0 both arms both seeds (>=0.98 gate), "
        "negative control shuffled_key acc_at1=0.0 both arms both seeds (no leak), "
        "FALSE_WIN_ALGEBRA keyed::{K128,K256}_BLOCK_LAST::J5 acc_at1=1.0 both arms both seeds "
        "(>=0.90 floor) -- K256's smaller blk_l=16 does not break SBC composability, checked "
        "per-arm as pre-registered, not assumed. SEED13 DATA WAS REMOTE-ONLY at VET time "
        "(local data/ dir had only seed7; sync-lagged) -- SSH-pulled from remote "
        "C:/dev/hd-instrument, certutil SHA256 identical local-pulled-copy vs remote "
        "(a604c34091e1cb049b2f1c7e233727fb9ef2a136b14128b75960086bc58d5387, both sides). "
        "VERIFY-THE-REFERENT CAVEAT (cross-cell nuance, not a flaw): v5's own K128 arm final "
        "ret_agree10 (seed7=0.1972, seed13=0.1984) is noticeably lower than v4/v3e's "
        "independently-run COSINE(K128) arm at the nominally same config (seed7=0.2112, "
        "seed13=0.2105) -- expected, not a reproducibility bug: v5 trains BOTH arms "
        "sequentially in ONE process (paired-arm design, shared up-front mining/seeding), a "
        "different code path than v4/v3e's single-arm process, so RNG-stream consumption "
        "before arm-specific divergence differs even at 'the same seed'. v5's own internal "
        "K128-vs-K256 comparison is unaffected (both arms share the same run's up-front RNG "
        "consumption). Split-structure note: v5 uses ONE held pool (no separate n_val/n_test "
        "unlike sibling v4), but the certified FINAL-step metric requires no data-dependent "
        "checkpoint selection at all (raw step-6000 state), so the VAL-vs-TEST "
        "population-mismatch concern from the sibling v4 cell's bug does not apply here."
    ),
    "aliases": ["v5_k256_capacity_lift_confirmed", "code_resolution_lifts_retrieval_ceiling",
                "k256_sparsity_cost_3x_target"],
    "metadata": {
        "record_class": "experiment_measured_mechanism_2seed_corroborated",
        "term_class": "ENCODER_V5_K256_CAPACITY_RETRIEVAL_LIFT",
        "cert_status": "mm_standard_2seed_corroborated_measured_mechanism",
        "cert_class": "MM_STANDARD_k256_retrieval_lift_confirmed_final_step_tight_cv",
        "cert_ts": TS_ISO,
        "verified_off_data": True,
        "atomized_by": ATOMIZED_BY,
        "anchor_seed7": V5_ANCHOR7, "anchor_seed13": V5_ANCHOR13,
        "cell_source_path": V5_CELL_SRC, "cell_commit": V5_CELL_COMMIT, "prereg_path": V5_PREREG,
        "raw_metrics_path_seed7": V5_METRICS7, "raw_metrics_path_seed13": V5_METRICS13,
        "ssh_byte_verify": "seed7 sha256 identical local vs remote; seed13 SSH-pulled "
                           "(local data/ dir lacked it at VET time), sha256 identical "
                           "pulled-copy vs remote, 2026-07-04",
        "run_mode": "full", "seeds": [7, 13], "device": "cuda",
        "verdict_on_disk_both_seeds": "HARD_PASS K256_LIFTS_RETRIEVAL_CONFIRMED",
        "recompute_check": {
            "delta_ret_agree10": {"seed7": 0.09297358066331035, "seed13": 0.09738055087129132,
                                  "cross_seed_cv": 0.0329},
            "delta_hi80_cos": {"seed7": -0.0017100572586059, "seed13": -0.0138493776321411},
            "sparsity_kb_over_N": {"K128": 0.03125, "K256": 0.0625, "goal": 0.02002,
                                   "K256_x_target": 3.12},
            "hard_pass_gate_reproduces": True,
        },
        "cross_arc_overlap_check_2026_07_04_USER_locked": (
            "director_kb_query.py --schema-version v2 --tau 0.15 --k 5, top hit cosine=0.3086 "
            "(generic wordnet 'coder' entity); NONE at cosine>0.30 vs a genuine prior TRAINED-"
            "comparison cell; confirms the prereg's own novelty check (cosine=0.2841, self-arc "
            "prose only)."
        ),
        "cert_increment_delta": 1,
    }
}

meta_atom_val_test_split_bug = {
    "id": ("meta::META_reproduction_tolerance_and_cross_arm_final_number_checks_must_read_"
           "SAME_SPLIT_as_reference_VAL_trajectory_endpoint_vs_TEST_split_reference_is_"
           "apples_to_oranges_even_under_determinism_pinning_case_study_v4_convergence_"
           "seed7_COSINE_REPRODUCTION_OUTSIDE_TOLERANCE_false_positive_MM_TENTATIVE_2026-07-04"),
    "name": ("META: a Gate-D reproduction-tolerance check (or any cross-arm final-number "
             "comparison) must read the reference number's SAME data split -- comparing a "
             "VAL-trajectory endpoint against a TEST-split reference is apples-to-oranges "
             "even with determinism pinning, and produces a false reproduction-failure."),
    "corpus": "meta",
    "tier": "T4",
    "kind": "methodology_rule",
    "description": (
        "MM_TENTATIVE methodology rule (first documented catch this lineage): a cell's "
        "training-time VAL-split trajectory (logged for monitoring/checkpoint-selection) and "
        "its final TEST-split semantic report are DIFFERENT concept populations, even under "
        "perfect determinism pinning. A reproduction-tolerance check (or any headline-number "
        "comparison against a prior cell's reference) must pull the reference-comparable "
        "number from the SAME split the reference was itself measured on, not from whichever "
        "trajectory happens to be conveniently in scope. CASE STUDY: "
        "exp_encoder_v4_convergence_lr_hold_v1 (commit a92ae8a46, bugfix e845cf831) originally "
        "compared its COSINE arm's VAL-trajectory LAST point (val_ret_agree10=0.3347, seed7) "
        "against a v3e TEST-split reference constant (0.21121188428458665) for its Gate-D "
        "repro-tolerance check, spuriously reporting COSINE_REPRODUCTION_OUTSIDE_TOLERANCE "
        "(gap 0.1234 > declared tolerance 0.10) even though the actual TEST-split per_unit "
        "number was a BIT-EXACT match to the reference (determinism pinning had in fact "
        "worked correctly the whole time). Fixed via a helper reading the TEST-split "
        "semantic per_unit entry directly, matching what is actually written to "
        "metrics.json['recovery'][mode]['final']. VERIFIED independently off raw data "
        "(standalone recompute, not the cell's own code): simulating the old comparison "
        "reproduces the exact failure for seed7 (gap 0.1234) and the exact non-failure for "
        "seed13 (gap 0.0996, just under the 0.10 tolerance) -- both landed verdict_msg "
        "categories are explained by this single mechanism. ACTIONABLE: when writing a "
        "Gate-D-style reproduction check against a prior cell's landed reference number, "
        "grep the prior cell's OWN metrics.json for exactly which field/split produced that "
        "reference number, and pull the new run's comparison number from the identically-"
        "named field, not from a differently-split trajectory that happens to carry a "
        "similar-sounding key name (e.g. 'ret_agree10' appearing in BOTH a VAL-trajectory "
        "dict and a TEST-split per_unit dict is the exact trap here)."
    ),
    "aliases": ["gate_d_val_vs_test_split_mismatch", "reproduction_check_same_split_rule",
                "v4_convergence_bugfix_val_test_apples_oranges"],
    "metadata": {
        "record_class": "methodology_rule_split_population_mismatch_detection",
        "cert_status": "mm_tentative_methodology_rule",
        "cert_class": "MM_TENTATIVE_META_RULE_reproduction_check_same_split_required",
        "cert_ts": TS_ISO,
        "verified_off_data": True,
        "atomized_by": ATOMIZED_BY,
        "cell_source_path": V4_CELL_SRC, "cell_commit": V4_CELL_COMMIT,
        "bugfix_commit": V4_BUGFIX_COMMIT,
        "raw_metrics_path_seed7": V4_METRICS7, "raw_metrics_path_seed13": V4_METRICS13,
        "composes_with_atoms": [math_atom_v4_dense_proxy_artifact["id"]],
        "promotion_path": "MM_TENTATIVE -> MM_STANDARD after 1 more independent catch of a "
                          "VAL-vs-TEST (or analogous cross-split) comparison bug in a "
                          "different cell/lineage.",
        "cert_increment_delta": 1,
    }
}

meta_atom_proxy_metric_decline_artifact = {
    "id": ("meta::META_training_time_cheap_proxy_metric_with_different_sampling_cadence_than_"
           "headline_capability_metric_can_show_SPURIOUS_decline_verify_decline_claims_"
           "against_the_ACTUAL_goal_metric_not_the_monitoring_proxy_case_study_v3e_v4_"
           "encoder_DENSE_spearman_declines_12pct_ret_agree10_flat_MM_TENTATIVE_2026-07-04"),
    "name": ("META: a cheap, frequently-sampled training-time monitoring metric (e.g. raw "
             "dense-output spearman over random pairs) can show a large, reproducible decline "
             "while the actual goal-relevant metric (e.g. retrieval-agreement after "
             "quantization/cleanup) on the IDENTICAL checkpoints shows no comparable decline -- "
             "decline claims must be verified against the goal metric itself, not the cheap "
             "monitoring proxy."),
    "corpus": "meta",
    "tier": "T4",
    "kind": "methodology_rule",
    "description": (
        "MM_TENTATIVE methodology rule (first documented catch this lineage): DENSE-proxy "
        "metrics (raw model output cosine/spearman-to-teacher over randomly-sampled pairs, "
        "cheap to compute at high cadence) and the actual capability-relevant metric (e.g. "
        "top-10 retrieval-agreement AFTER the code is quantized/argmax-cleaned-up) can "
        "diverge sharply in their step-trajectory SHAPE even though both are computed from "
        "the exact same checkpoints. CASE STUDY: v3e's HARD_FAIL DECLINE_CONTINUES verdict "
        "(both seed7 and seed13, dense-proxy early-half-mean-minus-late-half-mean = "
        "0.1228/0.1243 respectively, n=115 finely-sampled points) concluded the training "
        "objective needed a family-change to stop the decline. The sibling/successor cell "
        "exp_encoder_v4_convergence_lr_hold_v1 independently recomputed the SAME metric on "
        "the SAME checkpoints (trend_dense_full, coarser n=12 points, 2026-07-04) and "
        "reproduced the decline closely (0.1220-0.1249 depending on seed/arm) -- confirming "
        "the DENSE decline is real and reproducible, NOT noise. But the metric closer to the "
        "actual goal (val_ret_agree10, the headline retrieval-agreement trajectory, same "
        "checkpoints) showed early_minus_late in the range -0.012 to +0.009 across all 4 "
        "arm-seed combinations -- an order of magnitude smaller, classified PLATEAU (not "
        "DECLINE) under the cell's own thresholds in every case. The DENSE decline was real "
        "but irrelevant to the goal capability: the block-quantization + argmax-cleanup "
        "readout step is largely invariant to whatever global geometry drift the raw dense "
        "output undergoes late in training. ACTIONABLE: when a training-time monitoring "
        "metric shows a decline/instability signature, before concluding the underlying "
        "training dynamics or objective are broken, recompute the SAME trajectory using the "
        "actual capability/goal metric (not the cheap proxy) on the SAME checkpoints -- a "
        "metric-choice artifact can look identical to a genuine training pathology if you "
        "only ever look at the cheap proxy. Composes with the existing checkpoint-selection-"
        "bias / goal-metric-fidelity rule filed 2026-07-04 (v3c make-or-break audit) -- that "
        "rule addressed BEST-vs-FINAL selection bias and rank-corr-vs-cosine metric fidelity; "
        "this rule addresses a distinct mechanism: DIFFERENT metrics computed on the SAME "
        "(non-selected) trajectory can disagree about whether decline is occurring at all."
    ),
    "aliases": ["dense_proxy_decline_artifact_rule", "verify_decline_against_goal_metric_not_proxy",
                "v3e_v4_encoder_metric_choice_artifact"],
    "metadata": {
        "record_class": "methodology_rule_proxy_metric_artifact_detection",
        "cert_status": "mm_tentative_methodology_rule",
        "cert_class": "MM_TENTATIVE_META_RULE_proxy_metric_decline_artifact",
        "cert_ts": TS_ISO,
        "verified_off_data": True,
        "atomized_by": ATOMIZED_BY,
        "cell_source_path": V4_CELL_SRC, "cell_commit": V4_CELL_COMMIT,
        "raw_metrics_path_seed7": V4_METRICS7, "raw_metrics_path_seed13": V4_METRICS13,
        "composes_with_atoms": [math_atom_v4_dense_proxy_artifact["id"]],
        "promotion_path": "MM_TENTATIVE -> MM_STANDARD after 1 more independent catch of a "
                          "proxy-metric-vs-goal-metric decline disagreement in a different "
                          "cell/lineage.",
        "cert_increment_delta": 1,
    }
}


def a5_append(path, atom):
    d = os.path.dirname(path)
    os.makedirs(d, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp_atoms_", suffix=".jsonl")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as src:
                    for line in src:
                        f.write(line)
            f.write(json.dumps(atom, ensure_ascii=False) + "\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
    n_lines = 0
    found = 0
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            n_lines += 1
            obj = json.loads(line)  # integrity: raises on corrupt line
            aid = obj.get("id") or obj.get("atom_id")
            if aid == atom["id"]:
                found += 1
    if found != 1:
        raise RuntimeError(f"verify-load failed: atom id found {found}x (expected 1) in {path}")
    return n_lines


def ledger_append(atom, session_tag, ledger_path=CERT_LEDGER):
    entry = {
        "ts": TS,
        "ts_iso": TS_ISO,
        "atom_id": atom["id"],
        "corpus": atom["corpus"],
        "cert_status": atom["metadata"].get("cert_status"),
        "cert_class": atom["metadata"].get("cert_class"),
        "cert_increment_delta": atom["metadata"].get("cert_increment_delta", 0),
        "verified_off_data": True,
        "atomized_by": ATOMIZED_BY,
        "landed_VET_session": session_tag,
    }
    d = os.path.dirname(ledger_path)
    os.makedirs(d, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp_ledger_", suffix=".jsonl")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            if os.path.exists(ledger_path):
                with open(ledger_path, "r", encoding="utf-8") as src:
                    for line in src:
                        f.write(line)
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, ledger_path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


if __name__ == "__main__":
    print(f"[atomize] ts_iso={TS_ISO}")
    n1 = a5_append(MATH_ATOMS, math_atom_v4_dense_proxy_artifact)
    print(f"[atomize] math MEASURED_MECHANISM v4-dense-proxy-artifact atom appended; math lines={n1}")
    n2 = a5_append(MATH_ATOMS, math_atom_v5_k256_capacity)
    print(f"[atomize] math MM_STANDARD v5-K256-capacity atom appended; math lines={n2}")
    n3 = a5_append(META_ATOMS, meta_atom_val_test_split_bug)
    print(f"[atomize] meta MM_TENTATIVE VAL-vs-TEST-split-bug rule appended; meta lines={n3}")
    n4 = a5_append(META_ATOMS, meta_atom_proxy_metric_decline_artifact)
    print(f"[atomize] meta MM_TENTATIVE proxy-metric-decline-artifact rule appended; meta lines={n4}")
    ledger_append(math_atom_v4_dense_proxy_artifact, SESSION_TAG)
    ledger_append(math_atom_v5_k256_capacity, SESSION_TAG)
    ledger_append(meta_atom_val_test_split_bug, SESSION_TAG)
    ledger_append(meta_atom_proxy_metric_decline_artifact, SESSION_TAG)
    print("[atomize] DONE 4 atoms + 4 ledger entries; A5-gated (tmp+os.replace+verify-load+"
          "json-integrity); matching TS_ISO")
    print("[atomize] NET CERT DELTA: CG 0, MM +4 (1 math MEASURED_MECHANISM, 1 math MM_STANDARD, "
          "2 meta MM_TENTATIVE), HF 0")
    print("[atomize] v4 convergence: bugfix REAL + verified; corrected verdict MIDDLE_BAND both "
          "seeds (neither confirms nor refutes lever-a); DENSE-proxy decline is a metric "
          "artifact, ret_agree10 does not decline either LR schedule either seed; convergence-"
          "motivation for objective-swap is MOOT, retrieval-ceiling-motivation STANDS")
    print("[atomize] v5 K256 capacity: HARD_PASS independently CONFIRMED both seeds "
          "(delta_ret 0.093/0.097, cv 3.3%), at 3.1x the target sparsity density")
