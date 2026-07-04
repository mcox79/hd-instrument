"""
A5-gated atomization -- Skunkworks landed-VET of the PIVOTAL objective-swap
KL-RANK cell (AUDIT-ONLY). 2026-07-04.

CELL: experiments/exp_encoder_objective_swap_kl_rank_v1_core.py (commit 3a7da84ea)
DATA: data/exp_encoder_objective_swap_kl_rank_v1_seed7/metrics.json
      data/exp_encoder_objective_swap_kl_rank_v1_seed13/metrics.json
      BOTH remote-only at VET time (local data/ had only smoke/selftest); SSH-pulled
      from remote C:/dev/hd-instrument, cached at
      data/session_local/skunkworks/remote_kl_rank_seed{7,13}_metrics.json,
      certutil SHA256 identical pulled-copy vs remote both seeds
      (seed7 386bc40a69bf0ef0ffe2947b4df0e6945dc5e096ee11bd07323eec393b44a053,
       seed13 e937c196a344a1d7a6d8c967a59fbfae351c767c43261f083ccd9897e816a634).
PREREG: preregs/2026-07-04_exp_encoder_objective_swap_kl_rank_v1.md
Landed verdict BOTH seeds: HARD_FAIL (OBJECTIVE_SWAP_NO_MATERIAL_LIFT).

===================== INDEPENDENT RECOMPUTE (off metrics.json per_unit/recovery, NOT verdict_msg) =====================
Standalone recompute script (fresh, reads raw json; not a call into the cell's own verdict fn).
Cardinality 17/17 both seeds, unit_failures=[] both, arms_differ_verified via 10 distinct sha256
  digests both seeds. Positive control keyed::RANDOM_BLOCK::J5 acc_at1=1.0 both seeds (>=0.98 gate,
  PASS) -- SBC-lossless prior holds. Negative control shuffled_key::{KL,MSE}_BLOCK_LAST acc_at1=0.0
  both seeds (no key leak).

PRIMARY metric (FINAL-step, per_unit semantic BLOCK_LAST == recovery.*_final, verified by exact
  equality both seeds, not assumed from field naming):
    KL_BLOCK_LAST  ret_agree10 = 0.222885 (seed7) / 0.219320 (seed13)
    MSE_BLOCK_LAST ret_agree10 = 0.211212 (seed7) / 0.210469 (seed13)  [reproduces v3e's ~0.21
      control almost bit-exact -- MSE_BLOCK_LAST is identical to v3e/v4's MSE arm, same seed/config]
  delta_ret_agree10 (KL - MSE) recomputed = 0.011673 (seed7) / 0.008851 (seed13), matches file
    recovery.delta_ret_agree10 exactly both seeds. Cross-seed mean +0.010262, stdev 0.001996
    (consistent, but consistently near-zero).
  KL ret_agree10 (0.22) is BELOW even the HARD_FAIL ceiling (0.25), far below the 0.35 HARD_PASS
    target -> HARD_FAIL independently reproduces both seeds. NOT MIDDLE_BAND: it does not clear the
    0.25 no-material-movement ceiling.
  COMPARISON to the confirmed capacity lever (v5 K256, MM_STANDARD 2026-07-04): K256 lifted
    ret_agree10 by +0.0930/+0.0974. KL-RANK's +0.010 mean lift is ~9x SMALLER. Code capacity
    (K128->K256) is a decisive lever; the objective-family swap at fixed K=128 is not.

ALGEBRA (encoder goal #4, per arm, gated arm = BLOCK_LAST):
  KL_BLOCK_LAST keyed::J5 acc_at1 = 1.0000 (seed7) / 0.9833 (seed13) -- both >= 0.90 floor, INTACT
    (seed13 marginally degraded, still passes). MSE_BLOCK_LAST = 1.0/1.0. So the KL objective's
    FINAL code stays composable.
  CAVEAT (not gated, but flagged): KL_BLOCK_BESTVAL keyed::J5 acc_at1 = 0.6333 (seed7) -- the
    best-dense-VAL-selected KL checkpoint (step 500, early) has BROKEN SBC composability in seed7
    (0.9333 in seed13, passes). The KL objective's early high-dense checkpoint is NOT reliably
    composable; only the LAST checkpoint is. Not part of the certified HARD_FAIL claim (which uses
    LAST), but a genuine reliability flag against ever best-ckpt-selecting a KL-trained code.

CALIBRATION nuance (symmetric anti-negativity -- the raw number flatters KL, the calibration does not):
  KL_BLOCK_LAST hi80_cos = 0.9338 (seed7) / 0.9228 (seed13) LOOKS higher than MSE's 0.8320/0.8278
  and clears the prereg's hi80_cos>=0.82 floor. BUT teacher hi80_mean = 0.8377/0.8384 -- KL
  OVERSHOOTS the teacher's own gold-similarity by +0.096/+0.084 (hi80_calib_err 0.0961/0.0843),
  whereas MSE is calibrated to within -0.006/-0.011 (calib_err 0.0057/0.0107). KL's higher raw
  hi80_cos is NOT better calibration -- it is over-confidence (the student rates gold-similar pairs
  as MORE similar than the teacher itself does). By the stated goal (cosine matching the gold/
  teacher value ~0.85, i.e. calibrated), MSE is materially better calibrated; KL passes a
  raw-magnitude floor by overshooting, worsening calibration error ~17x/~8x. So "KL held hi80_cos
  >= 0.82" is technically true but does not mean KL preserved coarse calibration -- it did not.

TREND (the v3e "decline" motivation, cross-composition with the v4 finding):
  KL dense trajectory PLATEAUS at ~0.78-0.79 (kl_trend early_minus_late = 0.0365/0.0324, both
  between PLATEAU_MAX=0.03 and DECLINE_MIN=0.10, classified not-declining), while the MSE control's
  dense trajectory DECLINES to ~0.65 (mse_trend eml = 0.1228, the same decline v3e HARD_FAILed on).
  So KL-RANK DID "fix" the DENSE-proxy decline that motivated this whole objective-swap -- and
  ret_agree10 STILL did not move (0.21->0.22). This is convergent, intervention-side confirmation
  of the companion v4 finding (2026-07-04) that the DENSE decline was a proxy-metric artifact
  unrelated to the retrieval ceiling: fixing the dense decline (which KL does) does not lift
  retrieval, because the dense decline was never what was capping retrieval. The retrieval ceiling
  at K=128 is a CODE-CAPACITY bound, not a training-dynamics/objective bound.

HF ATTRIBUTION (STANDARD_HF_CLOSURE discipline -- genuine substantive negative, not test-design failure):
  HF_STRUCTURAL_BOUND. The positive control clears its own expected floor FIRST (keyed RANDOM_BLOCK
  1.0 both seeds >=0.98); the MSE control correctly reproduces the known v3e baseline (~0.21); the
  discriminator target (0.35) is reachable in principle (v5 K256 reaches ~0.29-0.30 ret_agree10);
  arms differ (10 distinct sha256); no key leak. The KL-RANK objective genuinely does not lift
  retrieval at fixed K=128 -- this is a real bound, not a broken test. Counts as a proven NEGATIVE.

DECISION IMPLICATION (the question this VET was to settle): KL-RANK at K=128/3.125%-sparse is NOT a
  clean win (0.22, HARD_FAIL, not toward 0.35) and offers no material lift over MSE (+0.010, ~9x
  smaller than K256's +0.093). The objective-family swap is DEAD as a retrieval-ceiling fix at
  fixed code capacity. To lift retrieval you must trade sparsity (K256 = 6.25% active, the verified
  lever) OR pursue an orthogonal transform lever (OPQ-style rotation / product-key, the cell's own
  escalation suggestion). The 2%/3.125%-sparse + high-retrieval combination is NOT achievable via a
  KL-RANK objective change. NOTE ON SPARSITY FRAMING: this cell's K=128 code is 128/4096 = 3.125%
  active (v3.K_BLOCKS_PRIMARY, confirmed by code read), not literally 2% -- same code-density path
  as v5's K128 control arm.

REVIVAL CRITERION: revisit KL-RANK only if a TAU_KL temperature sweep at K=128 (the cell used
  tau_kl=0.10, HYPOTHESIZED/untuned) demonstrates the temperature was materially mistuned AND moves
  ret_agree10 toward >=0.30; ABSENT that, the objective-family question is CLOSED for the retrieval
  ceiling and the lever is code capacity (K256, confirmed) or an orthogonal rotation. A tau sweep
  is a WEAK revival angle here since the result landed below the 0.25 no-movement ceiling (not a
  near-miss MIDDLE_BAND).

CROSS-ARC OVERLAP CHECK (USER-locked 2026-07-01): director_kb_query.py --schema-version v2 --tau
  0.15 --k 5 "KL rank distributional distillation objective swap does not lift retrieval agreement
  fixed K128 code capacity bound not training objective" -> top hits are NOTES not experiments:
  research_optimal_anisotropic_encoder_construction_5x_drill (0.337), LoRA_retrieval_degradation
  (0.333), capability_scorecard (0.319). The LoRA note (June 6) is ADJACENT-BUT-OPPOSITE: it warns
  to pre-register loss/eval COMPATIBILITY (an SFT-vs-retrieval gradient-direction MISMATCH). Here
  the objective WAS retrieval-aligned by construction (softmax-KL over similarity rows) and STILL
  did not lift retrieval -- proving the bound is code capacity, not objective alignment. Distinct,
  in fact opposite, finding; NONE at cosine>0.30 against a prior EXPERIMENT/cell finding. Novel.
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

ANCHOR7 = "encoder_objective_swap_kl_rank_v1_seed7"
ANCHOR13 = "encoder_objective_swap_kl_rank_v1_seed13"
METRICS7 = "data/exp_encoder_objective_swap_kl_rank_v1_seed7/metrics.json"
METRICS13 = "data/exp_encoder_objective_swap_kl_rank_v1_seed13/metrics.json"
CELL_SRC = "experiments/exp_encoder_objective_swap_kl_rank_v1_core.py"
CELL_COMMIT = "3a7da84ea"
PREREG = "preregs/2026-07-04_exp_encoder_objective_swap_kl_rank_v1.md"

SESSION_TAG = "2026-07-04_kl_rank_objective_swap_HF_closure"
ATOMIZED_BY = "skunkworks_landed_VET_" + SESSION_TAG

# Companion atoms this HF closure composes with (from earlier today's VETs).
V5_K256_ATOM = ("math::MM_STANDARD_v5_k256_capacity_paired_RETRIEVAL_LIFT_CONFIRMED_2seed_FULL178k_"
                "delta_ret_agree10_0p0930_0p0974_finalstep_not_bestckpt_cv_3pct_no_calib_regression_"
                "delta_hi80_neg0p0017_neg0p0138_sparsity_cost_6p25pct_active_vs_2pct_goal_3x_"
                "density_2026-07-04")
V4_DENSE_PROXY_ATOM = ("math::MEASURED_MECHANISM_v4_convergence_lr_hold_DENSE_PROXY_DECLINE_ARTIFACT_"
                       "CONFIRMED_ret_agree10_does_NOT_decline_over_6000_steps_either_LR_schedule_"
                       "2seed_FULL_bugfix_verified_VAL_vs_TEST_split_mismatch_bit_exact_repro_v3e_"
                       "both_seeds_eml_ret_range_neg0p012_to_pos0p009_vs_DENSE_eml_0p054_to_0p125_"
                       "corrected_verdict_MIDDLE_BAND_both_seeds_2026-07-04")

math_atom_kl_rank_hf = {
    "id": ("math::HARD_FAIL_v1_encoder_objective_swap_KL_RANK_does_NOT_lift_retrieval_at_K128_2seed_"
           "FULL178k_ret_agree10_0p2229_0p2193_below_0p25_ceiling_far_below_0p35_target_delta_vs_"
           "MSE_pos0p0117_pos0p0089_9x_smaller_than_K256_pos0p093_retrieval_ceiling_is_code_"
           "capacity_bound_not_objective_bound_KL_plateaus_dense_but_retrieval_flat_HF_STRUCTURAL_"
           "2026-07-04"),
    "name": ("MATH HARD_FAIL: the KL-RANK objective-family swap does NOT lift block-code retrieval "
             "agreement over the MSE-RKD control at fixed K=128/3.125%-sparse (2 seeds, FULL-178k); "
             "the retrieval ceiling is a code-capacity bound (K256 is the lever), not a training-"
             "objective bound. KL plateaus the dense proxy but leaves ret_agree10 flat -- "
             "convergent confirmation of the v4 dense-proxy-artifact finding."),
    "corpus": "math",
    "tier": "T3",
    "kind": "experiment_record_hard_fail_proven_negative",
    "description": (
        "HARD_FAIL (proven negative, 2 FULL seeds, HF_STRUCTURAL_BOUND, independent standalone "
        "recompute off metrics.json per_unit/recovery both seeds, NOT verdict_msg): a temperature-"
        "scaled softmax-KL rank-distillation objective (KL-RANK, tau_kl=0.10, NCE off) does NOT "
        "materially lift block-code retrieval agreement over the MSE-RKD control at fixed "
        "K=128/N=4096 (3.125% active), the sparsity-preserving path. RECOMPUTE (per_unit semantic "
        "BLOCK_LAST == recovery.*_final, exact-equality-verified both seeds): KL_BLOCK_LAST "
        "ret_agree10 = 0.222885 (seed7) / 0.219320 (seed13); MSE_BLOCK_LAST = 0.211212 / 0.210469 "
        "(reproduces v3e's ~0.21 control near-bit-exact). delta_ret_agree10 (KL - MSE) = 0.011673 "
        "(seed7) / 0.008851 (seed13), matches file recovery exactly; cross-seed mean +0.010262, "
        "stdev 0.001996 -- consistent but consistently near-zero. KL's 0.22 is BELOW the cell's own "
        "0.25 HARD_FAIL ceiling (not a MIDDLE_BAND near-miss) and far below the 0.35 HARD_PASS "
        "target. COMPARISON to the confirmed capacity lever (companion v5 K256 atom, MM_STANDARD "
        "same day): K256 lifted ret_agree10 by +0.0930/+0.0974 -- ~9x LARGER than KL-RANK's +0.010. "
        "Code capacity (K128->K256, 3.125%->6.25% active) is a decisive lever; the objective-family "
        "swap at fixed K=128 is not. ALGEBRA (goal #4): KL_BLOCK_LAST keyed::J5 acc_at1 = 1.0000 "
        "(seed7) / 0.9833 (seed13), both >= 0.90 floor (final code stays composable); but the "
        "NON-gated KL_BLOCK_BESTVAL keyed::J5 = 0.6333 in seed7 (broken composability on the early "
        "best-dense checkpoint; 0.9333 seed13) -- a reliability flag against best-ckpt-selecting a "
        "KL-trained code, not part of this claim. CALIBRATION nuance (symmetric anti-negativity): "
        "KL_BLOCK_LAST hi80_cos = 0.9338/0.9228 clears the >=0.82 floor and LOOKS better than MSE's "
        "0.8320/0.8278, BUT teacher hi80_mean=0.8377/0.8384 -- KL OVERSHOOTS gold similarity by "
        "+0.096/+0.084 (calib_err 0.0961/0.0843) vs MSE's calibrated -0.006/-0.011 (calib_err "
        "0.0057/0.0107); KL's higher raw number is over-confidence, ~17x/~8x WORSE calibration, not "
        "a coarse-quality win. TREND / CROSS-COMPOSITION: KL's dense trajectory PLATEAUS at "
        "~0.78-0.79 (kl_trend eml 0.0365/0.0324, not-declining) while the MSE control DECLINES to "
        "~0.65 (mse_trend eml 0.1228, the same decline v3e HARD_FAILed on) -- so KL-RANK DID fix the "
        "DENSE-proxy decline that motivated the whole objective-swap, and ret_agree10 STILL did not "
        "move. This is convergent intervention-side confirmation of the companion v4 finding that "
        "the DENSE decline is a proxy-metric artifact unrelated to the retrieval ceiling: fixing the "
        "dense decline does not lift retrieval because it was never the retrieval bottleneck. "
        "INTEGRITY: cardinality 17/17 both seeds, unit_failures=[], arms_differ_verified via 10 "
        "distinct sha256 both seeds, positive control keyed::RANDOM_BLOCK::J5 acc_at1=1.0 both seeds "
        "(>=0.98), negative control shuffled_key acc_at1=0.0 both arms both seeds (no leak). "
        "HF_STRUCTURAL_BOUND attribution: positive control clears its own floor, MSE control "
        "reproduces the known baseline, discriminator target reachable in principle (K256 ~0.29-"
        "0.30), so this is a genuine bound not a test-design failure. DECISION: the objective-family "
        "swap is DEAD as a retrieval-ceiling fix at fixed code capacity; lifting retrieval requires "
        "trading sparsity (K256, verified) or an orthogonal rotation lever (OPQ/product-key). "
        "REVIVAL CRITERION: revisit KL-RANK only if a TAU_KL sweep at K=128 shows the temperature "
        "(0.10, untuned/HYPOTHESIZED) was materially mistuned AND moves ret_agree10 toward >=0.30; "
        "else the objective-family question is CLOSED for the retrieval ceiling (weak revival angle "
        "given the sub-0.25 landing). BOTH seed metrics.json were remote-only at VET time, SSH-"
        "pulled from C:/dev/hd-instrument, certutil SHA256 identical pulled-copy vs remote."
    ),
    "aliases": ["kl_rank_objective_swap_no_retrieval_lift", "objective_swap_dead_retrieval_ceiling_K128",
                "retrieval_ceiling_is_code_capacity_not_objective", "encoder_KL_RANK_HARD_FAIL"],
    "metadata": {
        "record_class": "experiment_hard_fail_proven_negative_2seed",
        "term_class": "ENCODER_OBJECTIVE_SWAP_KL_RANK_HARD_FAIL",
        "cert_status": "hard_fail_proven_negative_structural_bound",
        "cert_class": "HARD_FAIL_kl_rank_objective_swap_no_retrieval_lift_2seed_HF_STRUCTURAL",
        "cert_ts": TS_ISO,
        "verified_off_data": True,
        "atomized_by": ATOMIZED_BY,
        "anchor_seed7": ANCHOR7, "anchor_seed13": ANCHOR13,
        "cell_source_path": CELL_SRC, "cell_commit": CELL_COMMIT, "prereg_path": PREREG,
        "raw_metrics_path_seed7": METRICS7, "raw_metrics_path_seed13": METRICS13,
        "ssh_byte_verify": "both seed metrics.json remote-only at VET time; SSH-pulled from "
                           "C:/dev/hd-instrument; certutil SHA256 identical pulled vs remote "
                           "(seed7 386bc40a..., seed13 e937c196...), 2026-07-04",
        "run_mode": "full", "seeds": [7, 13], "device": "cuda",
        "verdict_on_disk_both_seeds": "HARD_FAIL (OBJECTIVE_SWAP_NO_MATERIAL_LIFT)",
        "hf_attribution": "HF_STRUCTURAL_BOUND (not HF_TEST_DESIGN_FAILURE)",
        "recompute_check": {
            "kl_block_last_ret_agree10": {"seed7": 0.222885, "seed13": 0.219320},
            "mse_block_last_ret_agree10": {"seed7": 0.211212, "seed13": 0.210469},
            "delta_ret_agree10": {"seed7": 0.011673, "seed13": 0.008851, "mean": 0.010262,
                                  "stdev": 0.001996},
            "k256_lift_for_comparison": {"seed7": 0.0930, "seed13": 0.0974},
            "kl_block_last_keyed_j5": {"seed7": 1.0, "seed13": 0.9833},
            "kl_block_bestval_keyed_j5_nongated": {"seed7": 0.6333, "seed13": 0.9333},
            "kl_hi80_cos": {"seed7": 0.9338, "seed13": 0.9228},
            "kl_hi80_calib_err_overshoot": {"seed7": 0.0961, "seed13": 0.0843},
            "mse_hi80_calib_err": {"seed7": 0.0057, "seed13": 0.0107},
            "kl_dense_trend_eml_plateau": {"seed7": 0.0365, "seed13": 0.0324},
            "mse_dense_trend_eml_decline": {"seed7": 0.1228},
            "sparsity_K128": 0.03125,
        },
        "composes_with_atoms": [V5_K256_ATOM, V4_DENSE_PROXY_ATOM],
        "revival_criterion": "TAU_KL sweep at K=128 showing temperature materially mistuned AND "
                             "ret_agree10 -> >=0.30; else objective-family question CLOSED for "
                             "retrieval ceiling (lever = code capacity / orthogonal rotation).",
        "cross_arc_overlap_check_2026_07_04_USER_locked": (
            "top hits are notes not experiments (anisotropic-encoder-drill 0.337, LoRA-retrieval-"
            "degradation 0.333, capability_scorecard 0.319); the LoRA note is adjacent-but-OPPOSITE "
            "(pre-register loss/eval gradient-direction compatibility) -- here the objective WAS "
            "retrieval-aligned and still did not lift retrieval, proving a code-capacity bound; "
            "NONE at cosine>0.30 vs a prior experiment/cell; novel."
        ),
        "cert_increment_delta": 1,
    }
}

meta_atom_magnitude_floor_overshoot = {
    "id": ("meta::META_a_raw_magnitude_floor_gate_on_a_quality_metric_can_be_PASSED_by_a_model_that_"
           "OVERSHOOTS_the_teacher_target_worse_calibration_gate_calibration_with_signed_calib_err_"
           "distance_to_teacher_NOT_raw_magnitude_case_study_KL_RANK_hi80_cos_0p93_clears_0p82_floor_"
           "while_calib_err_0p096_is_17x_worse_than_MSE_0p006_MM_TENTATIVE_2026-07-04"),
    "name": ("META: a raw-magnitude floor gate (e.g. hi80_cos >= 0.82) can be passed by a model that "
             "OVERSHOOTS the teacher's own target value -- higher raw magnitude but WORSE "
             "calibration; gate coarse-quality with signed calibration error (distance to the "
             "teacher), not raw magnitude."),
    "corpus": "meta",
    "tier": "T4",
    "kind": "methodology_rule",
    "description": (
        "MM_TENTATIVE methodology rule (first documented catch this lineage): when a distillation "
        "goal is stated as 'match the teacher's value X' (e.g. cosine-to-gold ~0.85), a floor gate "
        "on the raw student magnitude (hi80_cos >= 0.82) does NOT verify calibration -- a model that "
        "OVERSHOOTS the teacher (student rates gold-similar pairs as MORE similar than the teacher "
        "itself does) passes the floor with a HIGHER raw number while being WORSE calibrated. "
        "CASE STUDY: exp_encoder_objective_swap_kl_rank_v1 (commit 3a7da84ea), KL-RANK arm "
        "hi80_cos=0.9338 (seed7)/0.9228 (seed13) clears the >=0.82 floor and superficially beats the "
        "MSE control's 0.8320/0.8278; but teacher hi80_mean=0.8377/0.8384, so KL overshoots by "
        "+0.096/+0.084 (signed hi80_calib_err 0.0961/0.0843) vs MSE's near-perfect -0.006/-0.011 "
        "(calib_err 0.0057/0.0107) -- KL's higher raw number is ~17x/~8x WORSE calibration. A "
        "verdict reading only the raw-magnitude floor would mistake KL's over-confidence for a "
        "coarse-calibration win. ACTIONABLE: for any 'match teacher value X' goal, gate with the "
        "SIGNED distance-to-teacher (calib_err = |student - teacher| on the goal-relevant subset), "
        "not a one-sided raw-magnitude floor; if a raw floor must be used for convenience, pair it "
        "with a two-sided calib_err ceiling so overshoot is caught. Composes with the metric-"
        "fidelity family filed 2026-07-04 (v3c goal-metric-fidelity rank-corr-vs-cosine; v4 proxy-"
        "metric-decline artifact) -- same theme: the number on the dashboard is not the number the "
        "goal specifies."
    ),
    "aliases": ["magnitude_floor_passes_overshoot_rule", "gate_calibration_with_signed_calib_err",
                "kl_rank_hi80_overshoot_case_study"],
    "metadata": {
        "record_class": "methodology_rule_calibration_gate_overshoot_detection",
        "cert_status": "mm_tentative_methodology_rule",
        "cert_class": "MM_TENTATIVE_META_RULE_magnitude_floor_passes_overshoot",
        "cert_ts": TS_ISO,
        "verified_off_data": True,
        "atomized_by": ATOMIZED_BY,
        "cell_source_path": CELL_SRC, "cell_commit": CELL_COMMIT,
        "raw_metrics_path_seed7": METRICS7, "raw_metrics_path_seed13": METRICS13,
        "composes_with_atoms": [math_atom_kl_rank_hf["id"]],
        "promotion_path": "MM_TENTATIVE -> MM_STANDARD after 1 more independent catch of a "
                          "raw-magnitude floor masking an overshoot/calibration issue in a "
                          "different cell/lineage.",
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
            obj = json.loads(line)
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
    n1 = a5_append(MATH_ATOMS, math_atom_kl_rank_hf)
    print(f"[atomize] math HARD_FAIL kl-rank-objective-swap closure appended; math lines={n1}")
    n2 = a5_append(META_ATOMS, meta_atom_magnitude_floor_overshoot)
    print(f"[atomize] meta MM_TENTATIVE magnitude-floor-passes-overshoot rule appended; meta lines={n2}")
    ledger_append(math_atom_kl_rank_hf, SESSION_TAG)
    ledger_append(meta_atom_magnitude_floor_overshoot, SESSION_TAG)
    print("[atomize] DONE 2 atoms + 2 ledger entries; A5-gated (tmp+os.replace+verify-load+"
          "json-integrity); matching TS_ISO")
    print("[atomize] NET CERT DELTA: 1 math HARD_FAIL (proven negative), 1 meta MM_TENTATIVE")
    print("[atomize] KL-RANK objective swap: HARD_FAIL both seeds CONFIRMED. ret_agree10 0.22 "
          "(<0.25 ceiling, far below 0.35). delta-vs-MSE +0.010 mean (~9x smaller than K256 +0.093). "
          "Objective-family swap DEAD for retrieval ceiling at K=128; lever is code capacity (K256).")
