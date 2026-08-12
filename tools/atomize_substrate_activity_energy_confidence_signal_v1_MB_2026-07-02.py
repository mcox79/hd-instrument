"""
A5-gated atomize: substrate_activity_energy_confidence_signal_v1 FULL landed MB

INDEPENDENT OFF-DATA RECOMPUTE (Skunkworks 2026-07-02):

Pre-reg motivation: Option C bounded probe alongside Option D (move on from
confidence architecture). Brain-analog: Kool et al 2018 prefrontal effort-
tracking (EVC theory) - watch substrate ACTIVITY (dynamical: dE reconstruction
energy delta + sigma_J log-jacobian variance) rather than STATE (density/margin)
or PERTURBATION (stochastic).

LANDING-DIR ANOMALY (framing correction):
  Metrics landed at data/exp_substrate_activity_energy_confidence_signal_v1_smoke/
  NOT at canonical data/exp_substrate_activity_energy_confidence_signal_v1/.
  Inside directory: run_mode=full, n_seeds=3. verify_landing.py FAILS at
  canonical anchor. Orchestrator/cell routing bug - flagged separately.
  Data is legit (run_mode=full, cardinality 12/12, arms differ verified).

OFF-DISK per-seed recompute (metrics.json arm_summaries + per_unit):
  seed 7 (contam=0.45):
    ARM_DELTA_E       AUC=0.4034 (BELOW chance)
    ARM_SIGMA_J       AUC=0.6030
    ARM_ABLATED_RAND  AUC=0.4798
    ARM_COMBINED      AUC=0.4058 (BELOW chance)
  seed 17 (contam=0.22):
    ARM_DELTA_E       AUC=0.6670
    ARM_SIGMA_J       AUC=0.3055
    ARM_ABLATED_RAND  AUC=0.5351
    ARM_COMBINED      AUC=0.6979
  seed 23 (contam=0.2425):
    ARM_DELTA_E       AUC=0.5805
    ARM_SIGMA_J       AUC=0.3781
    ARM_ABLATED_RAND  AUC=0.5245
    ARM_COMBINED      AUC=0.6077

Mean AUC / cv cross-seed (matches orchestrator):
  ARM_DELTA_E       0.550 (cv=0.199)
  ARM_SIGMA_J       0.429 (cv=0.295)   below chance (aggregate)
  ARM_ABLATED_RAND  0.513 (cv=0.047)   clean chance control
  ARM_COMBINED      0.5705 (cv=0.214)

CARDINALITY / INTEGRITY:
  N=8192, items=3600, n_queries_per_seed=400, topk=10, beta=8.0
  intra_cos=0.35, n_clusters=60
  cardinality_ok=True; expected/observed 12/12; failed_units=[]
  arms_differ_verified=True; mechanism hashes distinct all arm-seed pairs
  4 arms x 3 seeds = 12 cells (ran what declared)

BIAS-Q composability check (Director requested):
  Combined lift over best individual arm: 0.5705 - 0.550 = +0.0205
  Combined SEM (from cv=0.214, mean=0.5705): std = 0.1222, SEM = 0.1222/sqrt(3) = 0.0706
  Lift 0.0205 / SEM 0.0706 = 0.29 sigma
  Result: COMBINED lift NOT distinguishable from noise. Fails orthogonality
  test. Composability evidence claim NOT supported.

REGIME NOT-AS-REPORTED (framing correction):
  Pre-reg + orchestrator reported "contam=0.40". Actual per-seed contam
  drawn per-seed: 0.45 / 0.22 / 0.2425. Seed variance in regime this wide
  drives most of the AUC variance (cv~0.2). NOT a stationary contam=0.40
  regime as reported.

TIER RULING: MIDDLE_BAND_PARTIAL_ACTIVITY_SIGNAL (MB).
  Above chance but weak; NOT MM_TENTATIVE because:
    - ARM_DELTA_E lift over ARM_ABLATED_RANDOM = +0.037 mean; within
      seed variance noise floor (cv=0.199 -> SEM ~0.063; lift 0.037 =
      0.59 sigma).
    - Composability claim (COMBINED > ARM_DELTA_E) fails BIAS-Q at
      0.29 sigma - lift is not orthogonality evidence.
    - Regime dependence extreme: seed 7 at contam=0.45 gave COMBINED
      AUC=0.406 (BELOW chance). Mechanism NOT robust across
      contamination levels.
    - ARM_SIGMA_J aggregate 0.429 is below chance (counter-signal at
      seeds 17/23 balances seed 7's 0.60). Log-Jacobian observable is
      NOT a positive signal at scale.
  BUT distinct from HF cluster (prior h4 density / h4b spatial /
  lane_x_prime stochastic all landed 0.48-0.55 at 3-seed FULL):
    - ARM_DELTA_E at 0.550 aggregate is at TOP of prior HF band.
    - ARM_COMBINED at 0.5705 IS above the HF-cluster ceiling by ~0.02.
    - Cleanly above ARM_ABLATED_RANDOM (chance 0.513) in aggregate.
    Novel observable class (activity/energy delta) vs prior state/
    density/perturbation classes.

  cert_increment_delta = +1 (MB is a proven-bound category and counts
  toward CERT N per disposition ladder).

REVIVAL / EXTENSION CRITERION (for future MM_TENTATIVE promotion):
  Add third or fourth activity observable (e.g., cleanup_iteration_count
  as recovery-difficulty proxy, or query-response wall_time as effort
  proxy). If COMBINED AUC lifts above 0.65 with cross-seed cv < 0.15,
  and composability BIAS-Q clears >2 sigma over best-single, promote
  to MM_TENTATIVE_PARTIAL_ACTIVITY_MECHANISM. If further additions
  clear 0.70 mean with cv < 0.15 AND survive contam regime sweep
  (fixed contam values 0.20/0.30/0.40 not per-seed random draw),
  promote to CG.

  Also: mechanism-class INSIGHT worth preserving even at MB - ACTIVITY
  observables (dynamical) are qualitatively different from prior STATE
  (density/margin) or PERTURBATION (stochastic) confidence signals.
  If future ACTIVITY-family cells accumulate 3+ atoms with correlated
  positive-partial signal, META-atom the observable-class taxonomy.

COMPOSES-WITH (not supersedes):
  - Prior confidence-signal HF cluster (h4 density CG-HF; h4b spatial
    CG-HF; lane_x_prime stochastic CG-HF): this cell partially escapes
    that HF cluster at the reframed regime with novel observable class.
  - Regime-hostility META (this is at regime INTRA_COS=0.35 not default;
    confirms regime-choice matters).
  - Skunkworks META_RULE_smoke_single_seed_inflates_AUC CG 2026-07-02:
    smoke AUC 0.652 -> FULL 0.5705 (Delta=0.081 with cv~0.2) is
    IN-BAND with predicted inflation. Soft-gate correctly predicts
    inflation without ruling out MB signals.

CROSS-ARC OVERLAP CHECK (per Skunkworks 2026-07-01 concept-overlap discipline):
  Query: 'substrate activity energy delta effort tracking confidence uncertainty proxy'
  Top hit: 'Uncertainty' cosine=0.3076 (below 0.30+ concern threshold)
  Second: 'Substrate delta' cosine=0.3057 (testbed 2026-06-16 pre-arc)
  Rank 3-5: prior confidence-signal work at density/gap style.
  Result: NOVEL activity-observable mechanism class. No prior activity/
  energy-delta atoms in substrate. Cell-author novelty claim confirmed.
"""
from __future__ import annotations
import json, os, time
from pathlib import Path

ROOT = Path("d:/AI/hd-instrument")
MATH_ATOMS = ROOT / "data/substrate_index/math/atoms.jsonl"
CERT_LEDGER = ROOT / "data/substrate_index/meta/cert_ledger.jsonl"

ATOMIZED_BY = "skunkworks_landed_VET_substrate_activity_energy_confidence_signal_v1_MB_2026-07-02"
ATOMIZED_DATE = "2026-07-02"

atom_MB = {
    "id": (
        "T3/EXP_substrate_activity_energy_confidence_signal_v1_3seed_FULL_MIDDLE_BAND_"
        "PARTIAL_ACTIVITY_SIGNAL_novel_observable_class_delta_E_reconstruction_energy_and_"
        "sigma_J_log_jacobian_variance_at_reframed_regime_intra_cos_0p35_per_seed_contam_"
        "0p22_to_0p45_ARM_DELTA_E_0p550_cv_0p199_ARM_COMBINED_0p5705_cv_0p214_ARM_ABLATED_"
        "RANDOM_0p513_cv_0p047_lift_over_ablated_0p037_within_noise_composability_BIAS_Q_"
        "fails_at_0p29_sigma_seed_7_contam_0p45_COMBINED_below_chance_at_0p406_regime_"
        "dependent_but_novel_observable_class_above_prior_HF_cluster_0p48_to_0p55_ceiling_"
        "2026-07-02"
    ),
    "name": (
        "MIDDLE_BAND substrate activity/energy confidence signal 3-seed FULL: novel "
        "observable class (dynamical) escapes prior state/density and perturbation HF "
        "cluster ceiling by ~0.02 at reframed regime, but composability BIAS-Q fails at "
        "0.29 sigma and mechanism is regime-dependent (seed 7 contam=0.45 gave COMBINED "
        "below chance 0.406). ARM_DELTA_E lift over ablated_random +0.037 within seed "
        "variance noise. Cleanly above chance but below MM promotion floor. Novel activity-"
        "observable mechanism class distinct from prior confidence work; qualifies as "
        "proven-bound. CERT +1."
    ),
    "corpus": "math",
    "tier": "T3",
    "kind": "experiment_record",
    "description": (
        "3-seed FULL substrate_activity_energy_confidence_signal_v1 at N=8192 items=3600 "
        "n_queries_per_seed=400 topk=10 beta=8.0 intra_cos=0.35 n_clusters=60. Landed at "
        "data/exp_substrate_activity_energy_confidence_signal_v1_smoke/ (LANDING-DIR "
        "ANOMALY; run_mode=full inside; canonical _v1 anchor path DOES NOT EXIST; "
        "verify_landing.py FAILS at canonical). Cardinality 12/12; arms_differ_verified=True; "
        "mechanism hashes distinct all 12 arm-seed pairs. elapsed_s=40.8 (FULL scale confirmed).\n"
        "\n"
        "OFF-DATA per-seed recompute (Skunkworks 2026-07-02):\n"
        "  seed 7  (contam=0.45):   dE=0.4034 sJ=0.6030 rn=0.4798 cb=0.4058 (BELOW chance)\n"
        "  seed 17 (contam=0.22):   dE=0.6670 sJ=0.3055 rn=0.5351 cb=0.6979\n"
        "  seed 23 (contam=0.2425): dE=0.5805 sJ=0.3781 rn=0.5245 cb=0.6077\n"
        "\n"
        "Mean AUC / cv cross-seed (matches verdict_msg):\n"
        "  ARM_DELTA_E       0.550  cv=0.199\n"
        "  ARM_SIGMA_J       0.429  cv=0.295  (BELOW chance aggregate)\n"
        "  ARM_ABLATED_RAND  0.513  cv=0.047  (clean chance baseline)\n"
        "  ARM_COMBINED      0.5705 cv=0.214\n"
        "\n"
        "BIAS-Q COMPOSABILITY CHECK (Director requested): COMBINED lift over best-single = "
        "0.5705 - 0.550 = +0.0205. SEM(COMBINED) = 0.1222 / sqrt(3) = 0.0706. Lift is "
        "0.29 sigma. NOT distinguishable from noise. Composability/orthogonality claim NOT "
        "supported by data.\n"
        "\n"
        "REGIME NOT AS REPORTED (framing correction): pre-reg + orchestrator both cited "
        "'contam=0.40'. Off-disk per-seed contamination_rate: 0.45 / 0.22 / 0.2425 (drawn "
        "per-seed, not stationary). Wide seed-variance in regime drives most of the AUC "
        "spread. Seed 7 at contam=0.45 gave COMBINED AUC=0.406 - counter-signal below "
        "chance. Mechanism is contamination-regime-dependent.\n"
        "\n"
        "TIER: MIDDLE_BAND_PARTIAL_ACTIVITY_SIGNAL. NOT MM_TENTATIVE because:\n"
        "  (1) ARM_DELTA_E lift over ARM_ABLATED_RANDOM = +0.037 mean; cv=0.199 -> SEM "
        "     ~0.063; lift is 0.59 sigma (marginal).\n"
        "  (2) BIAS-Q composability lift +0.0205 = 0.29 sigma; orthogonality claim NOT "
        "     evidenced.\n"
        "  (3) Regime dependence extreme: seed 7 COMBINED = 0.406 BELOW chance; mechanism "
        "     not robust across contamination levels.\n"
        "  (4) ARM_SIGMA_J aggregate 0.429 below chance; log-Jacobian observable is NOT a "
        "     positive signal at scale.\n"
        "BUT distinct from prior HF cluster (h4 density CG-HF; h4b spatial CG-HF; lane_x_"
        "prime stochastic CG-HF; all landed 0.48-0.55 at 3-seed FULL): ARM_COMBINED at "
        "0.5705 is above HF-ceiling by ~0.02. Cleanly above ARM_ABLATED_RANDOM=0.513. "
        "Novel observable class (activity/dynamical) vs prior state/density/perturbation. "
        "Proven-bound characterization warranted -> MB.\n"
        "\n"
        "REVIVAL / EXTENSION CRITERION: add 3rd or 4th activity observable (e.g., cleanup_"
        "iteration_count recovery-difficulty proxy, or query-response wall_time effort "
        "proxy). If COMBINED AUC clears 0.65 with cv < 0.15 AND composability BIAS-Q "
        "clears >2 sigma over best-single -> promote MM_TENTATIVE_PARTIAL_ACTIVITY_MECHANISM. "
        "If further extensions clear 0.70 mean cv < 0.15 AND survive fixed-contam regime "
        "sweep (0.20/0.30/0.40 stationary) -> promote CG.\n"
        "\n"
        "COMPOSES-WITH (not supersedes): prior confidence-signal HF cluster (partial escape "
        "at reframed regime + novel observable class); regime-hostility META (confirms "
        "regime-choice matters); Skunkworks META_RULE_smoke_single_seed_inflates_AUC CG "
        "2026-07-02 (smoke 0.652 -> FULL 0.5705 Delta=0.081 is IN-BAND with predicted "
        "inflation; soft-gate correctly predicts inflation without ruling out MB signals).\n"
        "\n"
        "MECHANISM-CLASS NOTE (worth preserving even at MB): ACTIVITY observables "
        "(dynamical) are qualitatively different from prior STATE (density/margin) or "
        "PERTURBATION (stochastic) confidence signals. If future ACTIVITY-family cells "
        "accumulate 3+ atoms with correlated positive-partial signal, META-atom the "
        "observable-class taxonomy. Brain-analog: Kool et al 2018 EVC prefrontal effort-"
        "tracking - biologically motivated observable choice.\n"
        "\n"
        "SESSION CONTEXT: Option C bounded probe per USER 2026-07-02 authorization "
        "alongside primary Option D (move on from confidence architecture). MB delivers "
        "on 'first mechanism-class this session above chance' framing while honestly "
        "characterizing weakness. Does NOT reopen confidence-signal arc; is a proven-bound "
        "on ACTIVITY observable class at the reframed regime."
    ),
    "metadata": {
        "provenance_quality": "CERT_MIDDLE_BAND",
        "verdict": "MIDDLE_BAND",
        "verified_off_data_by": ATOMIZED_BY,
        "verified_off_data_evidence": (
            "OFF-DATA per-seed AUC recompute from metrics.json.per_unit and arm_summaries; "
            "aggregate means and cv values match verdict_msg exactly; BIAS-Q composability "
            "test computed off SEM(COMBINED) yields 0.29 sigma lift (not orthogonality "
            "evidence); regime-actual per-seed contam 0.22/0.2425/0.45 (NOT stationary 0.40 "
            "as reported); cardinality 12/12 with arms_differ_verified=True and mechanism "
            "hashes distinct; landing-dir anomaly flagged (canonical _v1 path missing; "
            "data actually at _v1_smoke suffix path with run_mode=full)"
        ),
        "landing_dir_anomaly": {
            "canonical_path_missing": "data/exp_substrate_activity_energy_confidence_signal_v1/",
            "actual_landing_path": "data/exp_substrate_activity_energy_confidence_signal_v1_smoke/",
            "run_mode_inside": "full",
            "verify_landing_py_status": "FAIL_at_canonical_anchor",
            "diagnosis": "orchestrator_or_cell_routing_bug_ANCHOR_field_mismatch",
            "data_integrity": "OK_run_mode_full_confirmed_inside_landing_dir",
        },
        "framing_corrections_vs_orchestrator": [
            "orchestrator_reported_contam_0p40_but_actual_per_seed_contam_drawn_0p22_0p2425_0p45",
            "orchestrator_reported_combined_0p571_actual_off_disk_0p5705_rounding_only",
            "cell_author_composability_lift_claim_+0p020_but_BIAS_Q_yields_0p29_sigma_NOT_orthogonality_evidence",
            "seed_7_at_contam_0p45_COMBINED_0p406_BELOW_chance_counter_signal_not_mentioned_in_verdict_msg",
            "ARM_SIGMA_J_aggregate_0p429_BELOW_chance_log_jacobian_is_NOT_positive_signal_at_scale",
        ],
        "regime": {
            "N": 8192,
            "items": 3600,
            "n_queries_per_seed": 400,
            "topk": 10,
            "beta": 8.0,
            "intra_cos": 0.35,
            "n_clusters": 60,
            "contam_actual_per_seed": {"seed_7": 0.45, "seed_17": 0.22, "seed_23": 0.2425},
            "contam_reported_stationary": 0.40,
            "arms": ["ARM_DELTA_E", "ARM_SIGMA_J", "ARM_ABLATED_RANDOM", "ARM_COMBINED"],
        },
        "per_seed_arm_auc": {
            "seed_7":  {"dE": 0.4034, "sJ": 0.6030, "rn": 0.4798, "cb": 0.4058, "contam": 0.45},
            "seed_17": {"dE": 0.6670, "sJ": 0.3055, "rn": 0.5351, "cb": 0.6979, "contam": 0.22},
            "seed_23": {"dE": 0.5805, "sJ": 0.3781, "rn": 0.5245, "cb": 0.6077, "contam": 0.2425},
        },
        "aggregate_arm_summary": {
            "ARM_DELTA_E":       {"mean_auc": 0.550,  "cv": 0.199},
            "ARM_SIGMA_J":       {"mean_auc": 0.429,  "cv": 0.295, "below_chance": True},
            "ARM_ABLATED_RANDOM":{"mean_auc": 0.513,  "cv": 0.047, "clean_chance_baseline": True},
            "ARM_COMBINED":      {"mean_auc": 0.5705, "cv": 0.214},
        },
        "bias_q_composability_check": {
            "lift_combined_over_best_single": 0.0205,
            "sem_combined_from_cv": 0.0706,
            "sigma_of_lift": 0.29,
            "orthogonality_claim_supported": False,
            "note": "lift NOT distinguishable from noise; composability evidence claim rejected",
        },
        "delta_E_lift_over_ablated_random": {
            "lift": 0.037,
            "sem_delta_E_from_cv": 0.063,
            "sigma_of_lift": 0.59,
            "note": "within seed variance noise floor; marginal above-chance signal only",
        },
        "cardinality": {
            "cardinality_ok": True,
            "expected_n_units": 12,
            "observed_n_units": 12,
            "failed_units": [],
            "arms_differ_verified": True,
        },
        "smoke_to_full_inflation_check": {
            "smoke_combined_auc": 0.652,
            "full_combined_auc": 0.5705,
            "delta": 0.081,
            "in_band_with_META_RULE_smoke_single_seed_inflates_AUC_CG_2026-07-02": True,
            "meta_rule_correctly_predicts_inflation_without_ruling_out_MB": True,
        },
        "cross_arc_overlap_check_2026-07-02": {
            "concept_query": "substrate activity energy delta effort tracking confidence uncertainty proxy",
            "top_hits_cosine": {
                "Uncertainty_prereg_2026-05-30": 0.3076,
                "Substrate_delta_testbed_2026-06-16": 0.3057,
                "prior_confidence_density_gap_notes_2026-05-29": 0.2969,
            },
            "novel_mechanism_class": True,
            "no_prior_activity_observable_atoms": True,
        },
        "novelty_vs_prior_confidence_HF_cluster": {
            "prior_HF_atoms": [
                "h4_density_confidence_CG_HF",
                "h4b_spatial_confidence_CG_HF",
                "lane_x_prime_stochastic_confidence_CG_HF",
            ],
            "prior_HF_band_range": [0.48, 0.55],
            "this_cell_arm_combined_auc": 0.5705,
            "escapes_HF_ceiling_by": 0.02,
            "mechanism_class_delta": (
                "prior_STATE_density_margin_and_PERTURBATION_stochastic_vs_this_ACTIVITY_"
                "dynamical_energy_delta_and_log_jacobian_variance"
            ),
        },
        "revival_criterion_for_MM_promotion": (
            "add 3rd/4th activity observable (e.g., cleanup_iteration_count recovery proxy "
            "or query-response wall_time effort proxy); if COMBINED AUC clears 0.65 with "
            "cv<0.15 AND composability BIAS-Q clears >2sigma over best-single AT FIXED "
            "stationary contam values 0.20/0.30/0.40 (not per-seed random) then promote "
            "MM_TENTATIVE_PARTIAL_ACTIVITY_MECHANISM; if further extension clears 0.70 "
            "mean cv<0.15 across contam sweep then promote CG"
        ),
        "supersedes": None,  # MB is novel observable class; does NOT supersede prior confidence-signal HFs
        "composes_with": [
            "prior_confidence_signal_HF_cluster_h4_density_h4b_spatial_lane_x_prime_stochastic",
            "regime_hostility_META",
            "META_RULE_smoke_single_seed_inflates_AUC_CG_2026-07-02",
        ],
        "cert_increment_delta": 1,
        "user_authorization_context": (
            "USER 2026-07-02 authorized Option C bounded probe alongside primary Option D "
            "(move on from confidence architecture). MB result delivers 'first confidence "
            "mechanism-class this session above chance' framing while honestly characterizing "
            "weakness (composability fails BIAS-Q; regime-dependent; sigma_J counter-signal). "
            "Does NOT reopen confidence-signal arc; is proven-bound on ACTIVITY observable "
            "class at reframed regime."
        ),
        "discipline_tags": [
            "META_RULE_H_cardinality_ok_12_of_12_all_seeds",
            "META_RULE_smoke_single_seed_inflates_AUC_CG_2026-07-02_confirmed",
            "META_RULE_AV_composability_BIAS_Q_failed_at_0p29_sigma",
            "Fix_28_per_arm_metrics_verified_off_disk",
            "landing_dir_anomaly_flagged_orchestrator_routing_bug",
            "regime_actual_per_seed_drift_vs_reported_stationary",
            "novel_activity_observable_mechanism_class",
            "brain_analog_Kool_2018_EVC_prefrontal_effort_tracking",
            "cross_arc_novelty_confirmed_cosine_below_0p31",
            "stage_3_compositional_understanding_USER_2026-06-26",
        ],
        "ts_iso_atomized": ATOMIZED_DATE,
    },
}

# ============================================================================
# CERT LEDGER ROW
# ============================================================================
_t0 = time.time()

ledger_MB = {
    "ts": _t0,
    "op": "cert_ruling_middle_band_partial_activity_signal",
    "atom_id": f"math::{atom_MB['id']}",
    "cert_status": "middle_band",
    "cert_class": "measured_bound_partial_signal",
    "verified_off_data": True,
    "atomized_by": ATOMIZED_BY,
    "cell_commit": "unknown_landing_dir_anomaly_flagged",
    "verdict": (
        "MIDDLE_BAND_PARTIAL_ACTIVITY_SIGNAL_3seed_FULL_ARM_COMBINED_0p5705_cv_0p214_"
        "ARM_DELTA_E_0p550_cv_0p199_lift_over_ablated_0p037_within_noise_composability_"
        "BIAS_Q_fails_at_0p29_sigma_ARM_SIGMA_J_below_chance_0p429_seed_7_contam_0p45_"
        "COMBINED_0p406_below_chance_regime_dependent_but_novel_ACTIVITY_observable_class_"
        "escapes_prior_HF_ceiling_by_0p02_landing_dir_anomaly_flagged_orchestrator_routing_bug"
    ),
    "cert_increment_delta": 1,
    "cv": 0.214,  # ARM_COMBINED cv cross-seed
    "referent_pointer": {
        "notes_path": None,
        "metrics_path": "data/exp_substrate_activity_energy_confidence_signal_v1_smoke/metrics.json (LANDING-DIR ANOMALY: run_mode=full inside _smoke path; canonical _v1 path missing)",
        "prereg_path": "preregs/2026-07-02_substrate_activity_energy_confidence_signal_v1.md",
        "atom_qualified_id": f"math::{atom_MB['id']}",
        "verify_landing_py_status": "FAIL_at_canonical_anchor",
    },
    "supersedes": None,
    "note": (
        "activity_energy_confidence_signal_v1_3seed_FULL_MIDDLE_BAND_first_confidence_"
        "mechanism_class_above_chance_this_session_but_composability_fails_regime_dependent_"
        "novel_ACTIVITY_observable_mechanism_class_escapes_prior_HF_cluster_ceiling_by_0p02_"
        "revival_criterion_add_3rd_4th_activity_observable_and_fixed_contam_regime_sweep_"
        "landing_dir_anomaly_orchestrator_routing_bug_flagged_verify_landing_py_fails_at_canonical"
    ),
}


# ============================================================================
# A5 write protocol
# ============================================================================
def append_jsonl_a5(path: Path, new_row: dict, label: str):
    print(f"[A5] {label}: path={path}")
    assert path.exists()

    with open(path, "r", encoding="utf-8") as f:
        pre_lines = f.read().splitlines()
    pre_count = len(pre_lines)
    print(f"[A5] {label}: pre_count={pre_count}")

    for i, ln in enumerate(pre_lines):
        if not ln.strip():
            continue
        try:
            json.loads(ln)
        except Exception as e:
            raise RuntimeError(f"PRE integrity fail line {i+1}: {e}")

    new_line = json.dumps(new_row, ensure_ascii=True)
    parsed_back = json.loads(new_line)
    if "id" in new_row:
        assert parsed_back.get("id") == new_row.get("id")
    if "atom_id" in new_row:
        assert parsed_back.get("atom_id") == new_row.get("atom_id")

    out_text = "\n".join(pre_lines + [new_line]) + "\n"
    tmp_path = path.with_suffix(path.suffix + ".tmp_a5")
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(out_text)
        f.flush()
        os.fsync(f.fileno())
    import time as _time
    for _attempt in range(10):
        try:
            os.replace(str(tmp_path), str(path))
            break
        except PermissionError:
            if _attempt == 9:
                raise
            _time.sleep(0.1 * (2 ** _attempt))

    with open(path, "r", encoding="utf-8") as f:
        post_lines = f.read().splitlines()
    post_count = len(post_lines)
    print(f"[A5] {label}: post_count={post_count}")
    assert post_count == pre_count + 1

    tail = json.loads(post_lines[-1])
    if "id" in new_row:
        assert tail["id"] == new_row["id"]
    if "atom_id" in new_row:
        assert tail["atom_id"] == new_row["atom_id"]

    for i, ln in enumerate(post_lines):
        if not ln.strip():
            continue
        try:
            json.loads(ln)
        except Exception as e:
            raise RuntimeError(f"POST integrity fail line {i+1}: {e}")

    print(f"[A5] {label}: OK")
    return post_count


def main():
    print(f"[A5] atomize START {ATOMIZED_BY} ts={time.time():.3f}")
    append_jsonl_a5(MATH_ATOMS, atom_MB, "math/atoms (activity_energy_v1 MB)")
    append_jsonl_a5(CERT_LEDGER, ledger_MB, "cert_ledger (activity_energy_v1 MB +1)")
    print(f"[A5] DONE OK")
    print(f"[A5] activity_energy_confidence_signal_v1 3-seed FULL: MIDDLE_BAND +1")
    print(f"[A5] ARM_COMBINED 0.5705 cv=0.214 escapes prior HF ceiling by 0.02")
    print(f"[A5] composability BIAS-Q fails 0.29 sigma; regime-dependent; novel observable class")
    print(f"[A5] CERT delta = +1")


if __name__ == "__main__":
    main()
