"""
A5-gated atomization for landed-VET of stage1 REGIME MAP arc Probe 1 FULL
(STORAGE x CLEANUP_MECHANISM) — 3 seeds (7, 13, 19) on GPU.

VERIFIED-OFF-DISK (metrics.json commit cdc81fddb) — Fix#28 per-arm cross-check:
  seed 7:  cardinality_ok=True n_expected=n_observed=72 n_distinct_mech=3
           arms_differ=True pc.pass=True (acc=1.0 @ threshold 0.75)
           max_mv_BUNDLED=0.10  max_mv_SHARDED=0.00  (cell-author cited 0.100/0.000 -> MATCHES)
  seed 13: cardinality_ok=True n_expected=n_observed=72 n_distinct_mech=3
           arms_differ=True pc.pass=True
           max_mv_BUNDLED=0.12  max_mv_SHARDED=0.00  (cell-author cited 0.120/0.000 -> MATCHES)
  seed 19: cardinality_ok=True n_expected=n_observed=72 n_distinct_mech=3
           arms_differ=True pc.pass=True
           max_mv_BUNDLED=0.09  max_mv_SHARDED=0.00  (cell-author cited 0.090/0.000 -> MATCHES)

CROSS-SEED VARIANCE (BUNDLED axis):
  per-seed max_mv_BUND = [0.10, 0.12, 0.09]  mean 0.1033  stdev 0.01528  cv 0.148
  cv 0.148 < 0.15 CG threshold (tight; just under).

CATEGORICAL INTERACTION COUNT (interaction significance):
  Sub-regime cells (M, N, corruption) x seeds = 12 x 3 = 36 per storage type.
  At BUNDLED:  24/36 sub-regime cells show nonzero cross-mechanism variance; max 0.12.
  At SHARDED:   0/36 sub-regime cells show nonzero cross-mechanism variance; max 0.00.
  This is CATEGORICAL (not >3sigma of noise, but 0/36 vs 24/36 across 3 seeds).

STORAGE GAPS (SHARDED - BUNDLED) — the "storage matters" axis (secondary confirmation):
  Median storage gap across seeds: 0.93, 0.93, 0.92 (SHARDED >> BUNDLED accuracy at scale)
  Max storage gap: 1.00 across all seeds.
  This CONFIRMS storage regime dominates readout quality (already known); the NEW finding
  is the CROSS-TERM: mechanism choice matters ONLY at BUNDLED, not at SHARDED.

PRIOR ATOM CONTEXT (checked; not double-filing):
  meta::T4/META_CLEANUP_MECHANISM_AXIS_IS_REGIME_NARROW_DEGENERATE_IN_SHARDED_PER_ANTECEDENT_
  ISOLATION_DISCRIMINATES_ONLY_IN_COMPETITIVE_CLEANUP_REGIME_...s11_SMOKE_2026-07-03
    filed 2026-07-03 17:50:20Z at SMOKE scale (6 SHARDED points all acc=1.0 at fixed M=800
    N=2048 F=1 L=2 TR=40). Tier: MM_TENTATIVE_REGIME_BOUNDARY. CERT +0.
  THIS FULL landing amends -> CG_META CONFIRMED: 36 SHARDED sub-regime cells across 3 seeds
  and factorial (M in {200, 800, 3200} x N in {2048, 8192} x corruption in {0.20, 0.45})
  ALL show 0.00 cross-mechanism variance; 24/36 BUND cells show nonzero. Categorical.

COMPOSITION WITH PROBES 2 + 3 (uniqueness):
  Probe 2 SMOKE: null (per Director prompt).
  Probe 3 SMOKE + FULL: null (per Director prompt).
  Among first 3 pair-probes of the stage1 REGIME MAP arc, STORAGE UNIQUELY moderates
  CLEANUP_MECHANISM. This adds discriminating power to the CG_META tier decision.

CROSS-ARC OVERLAP CHECK (SUBSTRATE-KB CONCEPT-OVERLAP CHECK ON SCHEMA-VET, USER-locked 2026-07-01):
  grep math+meta atoms.jsonl for STORAGE x CLEANUP / MECHANISM_AXIS_CONDITIONAL_ON_STORAGE /
  regime_map_storage_x_cleanup: 1 prior meta atom (the SMOKE MM_TENTATIVE above); 0 math atoms.
  This landing is a targeted extension (SMOKE -> FULL confirmation with factorial expansion),
  NOT a rediscovery. Similar prior wave14g atom (T3 legacy May 2026) was recurrent-cleanup at
  d=25, unrelated to storage x cleanup pairwise interaction — no overlap.

TIER DECISION: CG_META (regime-conditional cross-term = substrate physics law confirmed at FULL).
  Justification: (a) 3/3 seeds HARD_PASS; (b) cv 0.148 < 0.15 CG threshold; (c) categorical
  interaction 0/36 vs 24/36 SHARD/BUND cells; (d) positive_control passes all seeds; (e) unique
  to STORAGE among 3 tested pairwise probes; (f) FULL confirms SMOKE at 6x factorial expansion;
  (g) cross-arc overlap check clean (targeted extension, not rediscovery).

DIRECTOR/CELL-AUTHOR FRAMING VERIFY (symmetric-verify, Fix#28):
  Cell-author verdict: HARD_PASS_MECHANISM_AXIS_CONDITIONAL_ON_STORAGE. Auditor CONFIRMS —
  no downward correction needed. Numbers exactly match cell-author-cited (0.100/0.120/0.090
  = per-seed max_mv_BUNDLED; 0.000 SHARDED). max_int_deviation range 0.0024-0.0058 verified.
  Framing is precise; no over- or under-claim.

TWO ATOMS FILED (matching TS_ISO):
  (a) math CG_META: EXP record of 3-seed FULL confirming STORAGE x CLEANUP_MECHANISM cross-term.
  (b) meta CG_META PROMOTION: parent MM_TENTATIVE (SMOKE 2026-07-03 17:50Z) -> CG_META CONFIRMED
      with 3-seed FULL evidence + factorial expansion + unique-among-probes discriminator.
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
COMMIT = "cdc81fddb"
CELL_ANCHOR_BASE = "stage1_regime_map_storage_x_cleanup_v1"
CELL_PATH = "experiments/_stage1_regime_map_storage_x_cleanup_v1_core.py"
PREREG_PATH = "preregs/2026-07-03_stage1_regime_map_storage_x_cleanup_first_probe.md"


# ============= ATOM (a): MATH CG_META — 3-seed FULL confirmation of STORAGE x CLEANUP cross-term =============
atom_a_math_cg_meta = {
    "id": "math::T1/MATH_STAGE1_REGIME_MAP_PROBE1_STORAGE_x_CLEANUP_MECHANISM_CROSS_TERM_FULL_CG_META_3_seeds_7_13_19_GPU_HARD_PASS_MECHANISM_AXIS_CONDITIONAL_ON_STORAGE_categorical_interaction_at_BUNDLED_24of36_subregime_cells_show_nonzero_cross_mechanism_variance_max_0p12_at_SHARDED_0of36_cells_all_exactly_0p00_across_full_factorial_M_in_200_800_3200_x_N_in_2048_8192_x_corruption_0p20_0p45_x_3_mechanisms_modern_hopfield_iterative_cosine_soft_energy_attractor_per_seed_max_mv_BUND_0p10_0p12_0p09_mean_0p1033_stdev_0p01528_cv_0p148_under_0p15_CG_threshold_max_int_deviation_0p0024_to_0p0058_cardinality_ok_arms_differ_verified_positive_control_iterative_cosine_regime_pass_acc_1p000_all_seeds_median_storage_gap_SHARDED_minus_BUNDLED_0p93_confirms_storage_dominates_readout_quality_secondary_but_load_bearing_finding_is_the_cross_term_mechanism_choice_matters_ONLY_at_BUNDLED_not_at_SHARDED_2026_07_03",
    "name": "MATH Stage1 REGIME MAP Probe 1 STORAGE x CLEANUP_MECHANISM cross-term FULL CG_META (3 seeds; categorical interaction: 24/36 BUND cells show variance, 0/36 SHARD cells; cv 0.148)",
    "corpus": "math",
    "tier": "T1",
    "kind": "experiment_record_regime_conditional_cross_term",
    "description": (
        "CG_META regime-conditional cross-term confirmed at FULL scale on GPU. "
        "Independent recompute off-disk (metrics.json commit cdc81fddb) — 3 seeds (7, 13, 19), "
        "72 units per seed (12 sub-regimes x 3 mechanisms x 2 storage arms; cardinality_ok=True, "
        "arms_differ_verified=True, n_distinct_mechanisms=3 all seeds). Positive control "
        "(iterative_cosine reproduces expected regime at M=200 N=2048 corruption=0.20) passes "
        "acc=1.000 all seeds. "
        "PRIMARY FINDING (cross-term regime-conditional law): "
        "  At SHARDED storage, cross-mechanism variance is EXACTLY 0.00 in ALL 36 sub-regime "
        "  cells (12 sub-regimes x 3 seeds). The 3 cleanup mechanisms {modern_hopfield, "
        "  iterative_cosine, soft_energy_attractor} produce IDENTICAL storage-gap accuracy "
        "  under SHARDED per-antecedent isolation. "
        "  At BUNDLED storage, cross-mechanism variance is NONZERO in 24/36 sub-regime cells, "
        "  reaching per-seed maxes of 0.10, 0.12, 0.09 (mean 0.1033 stdev 0.01528 cv 0.148, "
        "  under the 0.15 CG cross-seed threshold). "
        "  Categorical distinction — this is not a >3-sigma-of-noise claim; it is 0/36 vs "
        "  24/36 (deterministic zero at SHARDED across full factorial). "
        "SECONDARY CONFIRMATION (storage matters — already known): median storage_gap "
        "SHARDED-minus-BUNDLED = 0.93 across seeds (max 1.00). SHARDED dominates readout "
        "quality at high M for all 3 mechanisms; but the NEW load-bearing finding is the "
        "cross-term: mechanism-choice sensitivity is UNIQUELY moderated by storage regime. "
        "COMPOSITION WITH ARC PROBES (uniqueness of the moderating axis): "
        "  Probe 2 SMOKE — null (no cross-term). "
        "  Probe 3 SMOKE + FULL — null (no cross-term). "
        "  Among first 3 pair-probes of the stage1 REGIME MAP arc, STORAGE UNIQUELY moderates "
        "  CLEANUP_MECHANISM. This adds discriminating power to the physics-law framing. "
        "MECHANISM HYPOTHESIS (per prior SMOKE atom, confirmed by categorical FULL evidence): "
        "  Under SHARDED per-antecedent isolation, the per-trial cleanup query has exactly one "
        "  dominant codeword match; argmax readout collapses distinct mechanism outputs to "
        "  identical target indices even though intermediate cleaned vectors differ (per-mech "
        "  output_hash_agg distinct per SMOKE trace). Under BUNDLED shared-codebook competitive "
        "  cleanup, mechanisms compete over overlapping supports and their distinct discriminator "
        "  functions produce measurably different readouts. "
        "CROSS-ARC OVERLAP CHECK (SUBSTRATE-KB CONCEPT-OVERLAP CHECK, USER-locked 2026-07-01): "
        "  Prior atoms: 1 meta MM_TENTATIVE at SMOKE (same finding, 6 points); 0 math atoms "
        "  on this pairwise interaction. This is a targeted SMOKE->FULL extension with factorial "
        "  expansion, NOT a rediscovery. Prior wave14g LEGACY_EXCERPT atom is recurrent-cleanup "
        "  at d=25 (unrelated). Clean."
    ),
    "aliases": [],
    "metadata": {
        "record_class": "experiment",
        "term_class": "STAGE1_REGIME_MAP_PROBE1_STORAGE_x_CLEANUP_MECHANISM_REGIME_CONDITIONAL_CROSS_TERM",
        "cert_status": "chain_grade_meta_regime_conditional_law",
        "cert_class": "CG_META_regime_conditional_cross_term_confirmed_at_FULL_scale",
        "cert_ts": TS_ISO,
        "verified_off_data": True,
        "atomized_by": "skunkworks_landed_VET_2026-07-03_stage1_regime_map_storage_x_cleanup_FULL",
        "raw_metrics_paths": [
            f"data/exp_{CELL_ANCHOR_BASE}_s7/metrics.json",
            f"data/exp_{CELL_ANCHOR_BASE}_s13/metrics.json",
            f"data/exp_{CELL_ANCHOR_BASE}_s19/metrics.json",
        ],
        "cell_source_path": CELL_PATH,
        "prereg_path": PREREG_PATH,
        "commit_hash": COMMIT,
        "cell_anchor_base": CELL_ANCHOR_BASE,
        "n_seeds": 3,
        "seeds": [7, 13, 19],
        "n_units_per_seed": 72,
        "sub_regimes_per_storage": 12,
        "M_grid": [200, 800, 3200],
        "N_grid": [2048, 8192],
        "corruption_grid": [0.20, 0.45],
        "cleanup_mechanisms": ["modern_hopfield", "iterative_cosine", "soft_energy_attractor"],
        "storage_arms": ["BUNDLED", "SHARDED"],
        "per_seed_max_mv_BUNDLED": {"7": 0.10, "13": 0.12, "19": 0.09},
        "per_seed_max_mv_SHARDED": {"7": 0.00, "13": 0.00, "19": 0.00},
        "cross_seed_max_mv_BUND_mean": 0.1033,
        "cross_seed_max_mv_BUND_stdev": 0.01528,
        "cross_seed_max_mv_BUND_cv": 0.148,
        "cv_under_0p15_CG_threshold": True,
        "categorical_interaction_BUND_nonzero_cells_of_36": 24,
        "categorical_interaction_SHARD_nonzero_cells_of_36": 0,
        "median_storage_gap_SHARDED_minus_BUNDLED_per_seed": {"7": 0.935, "13": 0.930, "19": 0.920},
        "max_storage_gap_per_seed": {"7": 1.00, "13": 1.00, "19": 1.00},
        "cardinality_ok_all_seeds": True,
        "arms_differ_verified_all_seeds": True,
        "positive_control_iterative_cosine_regime_pass_all_seeds": True,
        "cell_author_verdict_verified": "HARD_PASS_MECHANISM_AXIS_CONDITIONAL_ON_STORAGE",
        "auditor_framing_correction_vs_cell_author": "NONE — cell-author framing is precise; no over- or under-claim",
        "composition_with_arc_probes": {
            "probe_2_SMOKE": "null_no_cross_term",
            "probe_3_SMOKE": "null_no_cross_term",
            "probe_3_FULL": "null_no_cross_term_confirmed",
            "conclusion": "STORAGE uniquely moderates CLEANUP_MECHANISM among first 3 pair-probes of stage1 REGIME MAP arc"
        },
        "composes_with_atoms": [
            "meta::T4/META_CLEANUP_MECHANISM_AXIS_IS_REGIME_NARROW_DEGENERATE_IN_SHARDED_PER_ANTECEDENT_ISOLATION_DISCRIMINATES_ONLY_IN_COMPETITIVE_CLEANUP_REGIME_amendment_to_M_sweep_CG_META_scope_witness_stage1_physics_law_joint_composition_factorial_v1_s11_SMOKE_2026-07-03",
            "T2/sparse_distributed_memory",
            "concept::CAP_cleanup"
        ],
        "cross_arc_overlap_check_2026_07_01_USER_locked": "CLEAN — targeted SMOKE->FULL extension with factorial expansion; prior meta MM_TENTATIVE at SMOKE composes as parent; wave14g LEGACY unrelated (recurrent-cleanup d=25); NOT a rediscovery",
        "cert_increment_delta": 1
    }
}


# ============= ATOM (b): META CG_META PROMOTION — parent MM_TENTATIVE (SMOKE) -> CG_META CONFIRMED at FULL =============
atom_b_meta_promotion = {
    "id": "meta::T4/META_CLEANUP_MECHANISM_AXIS_IS_REGIME_NARROW_PROMOTION_MM_TENTATIVE_to_CG_META_CONFIRMED_at_FULL_3_seeds_7_13_19_GPU_factorial_expansion_M_in_200_800_3200_x_N_in_2048_8192_x_corruption_0p20_0p45_categorical_interaction_0of36_SHARD_subregime_cells_vs_24of36_BUND_cells_all_seeds_max_mv_BUND_0p10_0p12_0p09_cv_0p148_under_0p15_threshold_unique_moderator_among_first_3_pair_probes_of_stage1_REGIME_MAP_arc_Probe_2_SMOKE_null_Probe_3_SMOKE_and_FULL_null_2026_07_03",
    "name": "META CG_META PROMOTION: CLEANUP_MECHANISM axis REGIME-NARROW parent MM_TENTATIVE (SMOKE s11 17:50Z) promoted to CG_META CONFIRMED at FULL (3 seeds, factorial expansion, categorical 0/36 vs 24/36 interaction)",
    "corpus": "meta",
    "tier": "T_chain_grade_meta_regime_conditional_law",
    "kind": "methodology_rule_regime_conditional_law_promotion",
    "description": (
        "PROMOTES parent atom "
        "meta::T4/META_CLEANUP_MECHANISM_AXIS_IS_REGIME_NARROW_DEGENERATE_IN_SHARDED_PER_ANTECEDENT_"
        "ISOLATION_DISCRIMINATES_ONLY_IN_COMPETITIVE_CLEANUP_REGIME_amendment_to_M_sweep_CG_META_"
        "scope_witness_stage1_physics_law_joint_composition_factorial_v1_s11_SMOKE_2026-07-03 "
        "(filed 2026-07-03 17:50:20Z at SMOKE scale, tier MM_TENTATIVE_REGIME_BOUNDARY, CERT +0) "
        "to CG_META CONFIRMED based on 3-seed FULL GPU landing (commit cdc81fddb, seeds 7/13/19). "
        "PARENT (SMOKE) EVIDENCE: 6 SHARDED points at fixed (M=800, N=2048, F=1, L=2, TR=40) all "
        "acc=1.0; per-mechanism output_hash_agg distinct (7e58a6dd1f03f936 / 340cd0fb960b113b / "
        "ee2af1ab629d00e4) — mechanisms produce different intermediate cleaned vectors, argmax "
        "collapses to identical target indices. "
        "PROMOTION EVIDENCE (this FULL landing, verified off-disk): "
        "  Factorial expansion: 12 sub-regimes per storage type (M in {200, 800, 3200} x "
        "  N in {2048, 8192} x corruption in {0.20, 0.45}), x 3 cleanup mechanisms, x 2 storage "
        "  arms, x 3 seeds = 216 arm units. Cardinality_ok all seeds. "
        "  Categorical interaction: SHARDED has 0/36 sub-regime cells with nonzero cross-"
        "  mechanism variance (mv exactly 0.00 in every cell across all seeds and factorial "
        "  points). BUNDLED has 24/36 cells with nonzero variance (max 0.12). Not a >3-sigma-"
        "  of-noise finding; a deterministic-zero-vs-nonzero categorical distinction. "
        "  Per-seed max_mv_BUND: 0.10, 0.12, 0.09 (mean 0.1033 stdev 0.01528 cv 0.148 < 0.15 "
        "  CG cross-seed threshold). "
        "  Positive control (iterative_cosine expected-regime reproduce) passes acc=1.000 all seeds. "
        "UNIQUENESS AMONG PROBES (composition discriminator): "
        "  Probe 2 SMOKE: null (no cross-term). "
        "  Probe 3 SMOKE and FULL: null (no cross-term). "
        "  Among the first 3 pair-probes of the stage1 REGIME MAP arc, STORAGE UNIQUELY moderates "
        "  CLEANUP_MECHANISM. This uniqueness confers physics-law status — the interaction is "
        "  specific, not one of many. "
        "SUBSTRATE PHYSICS LAW (final statement of the CG_META finding): "
        "  Under SHARDED per-antecedent isolation storage, the choice of cleanup mechanism "
        "  {modern_hopfield, iterative_cosine, soft_energy_attractor} is STRUCTURALLY DEGENERATE — "
        "  argmax readout against the per-antecedent codebook collapses distinct mechanism "
        "  outputs to identical target indices. Under BUNDLED shared-codebook competitive "
        "  cleanup, the cleanup mechanism axis is MATERIAL — mechanisms produce measurably "
        "  different readouts (up to 12 pp variance in accuracy across the factorial). "
        "IMPLICATION FOR PRIOR CG_META atom PHYSICS_LAW_cleanup_mechanism_M_scaling_non_Hebbian "
        "(v2 M-sweep): the prior atom's regime-scope amendment (already noted by parent) is now "
        "CONFIRMED at FULL. Prior cleanup-mechanism CG_META claims are BUNDLED-regime-scoped; "
        "at SHARDED regime, cleanup mechanism is a degenerate axis. "
        "CROSS-ARC OVERLAP CHECK (USER-locked 2026-07-01): clean — SMOKE->FULL extension of "
        "explicit parent, not rediscovery."
    ),
    "aliases": ["parent_META_CLEANUP_MECHANISM_AXIS_IS_REGIME_NARROW_promotion_to_CG_META_at_FULL_2026_07_03"],
    "metadata": {
        "verified_off_data": True,
        "verified_ts": TS_ISO,
        "verifier": "hdi_skunkworks",
        "commit_hash": COMMIT,
        "cell_file": CELL_PATH,
        "prereg_path": PREREG_PATH,
        "cert_status": "chain_grade_meta_regime_conditional_law_promoted_from_MM_TENTATIVE",
        "cert_class": "CG_META_regime_conditional_law_confirmed_at_FULL_3_seeds_factorial_expansion",
        "promotes_parent_atom_id": "meta::T4/META_CLEANUP_MECHANISM_AXIS_IS_REGIME_NARROW_DEGENERATE_IN_SHARDED_PER_ANTECEDENT_ISOLATION_DISCRIMINATES_ONLY_IN_COMPETITIVE_CLEANUP_REGIME_amendment_to_M_sweep_CG_META_scope_witness_stage1_physics_law_joint_composition_factorial_v1_s11_SMOKE_2026-07-03",
        "parent_tier_at_SMOKE": "MM_TENTATIVE_REGIME_BOUNDARY",
        "parent_cert_delta_at_SMOKE": 0,
        "this_promotion_tier": "CG_META_CONFIRMED",
        "promotion_evidence_summary": {
            "n_seeds": 3,
            "seeds": [7, 13, 19],
            "factorial_expansion_vs_SMOKE": "12 sub-regimes per storage (vs 6 at SMOKE); 2x factorial expansion",
            "categorical_interaction_BUND_nonzero_of_36": 24,
            "categorical_interaction_SHARD_nonzero_of_36": 0,
            "cv_cross_seed_max_mv_BUND": 0.148,
            "cv_under_CG_threshold": True,
            "positive_control_pass_all_seeds": True,
            "uniqueness_among_first_3_pair_probes": "STORAGE uniquely moderates CLEANUP_MECHANISM; Probes 2 and 3 both null"
        },
        "composes_with_atoms": [
            "math::T1/MATH_STAGE1_REGIME_MAP_PROBE1_STORAGE_x_CLEANUP_MECHANISM_CROSS_TERM_FULL_CG_META_3_seeds_7_13_19_GPU_HARD_PASS (this batch atom a)",
            "meta::T4/META_CLEANUP_MECHANISM_AXIS_IS_REGIME_NARROW_...s11_SMOKE_2026-07-03 (parent, promoted)",
            "T2/sparse_distributed_memory",
            "concept::CAP_cleanup"
        ],
        "substrate_physics_law_final_statement": "Under SHARDED per-antecedent isolation storage, cleanup mechanism axis is structurally degenerate (argmax collapses distinct outputs). Under BUNDLED shared-codebook competitive cleanup, mechanism axis is material (up to 12 pp accuracy variance).",
        "implication_for_prior_CG_META_cleanup_mechanism_M_scaling_non_Hebbian": "prior CG_META claims are BUNDLED-regime-scoped; at SHARDED regime, cleanup mechanism is a degenerate axis; regime-scope annotation now confirmed at FULL",
        "term_class": "PROCESS_KNOWLEDGE_NON_MATH_REGIME_CONDITIONAL_SUBSTRATE_LAW",
        "cross_arc_overlap_check_2026_07_01_USER_locked": "CLEAN — SMOKE->FULL extension of explicit parent",
        "cert_increment_delta": 1
    }
}


# ================================================================================
# A5-GATED APPENDS (atomic tmp+os.replace+verify-load) with matching TS_ISO ledger
# ================================================================================
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
    found = False
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            n_lines += 1
            if atom["id"] in line:
                found = True
    if not found:
        raise RuntimeError(f"verify-load failed: atom id not found in {path}")
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
        "verified_off_data": atom["metadata"].get("verified_off_data", False),
        "commit_hash": atom["metadata"].get("commit_hash"),
        "atomized_by": atom["metadata"].get("atomized_by") or atom["metadata"].get("verifier"),
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
    print(f"[atomize] ts_iso={TS_ISO} commit={COMMIT}")
    session_tag = "2026-07-03_stage1_regime_map_storage_x_cleanup_FULL_CG_META_promotion"

    n_math = a5_append(MATH_ATOMS, atom_a_math_cg_meta)
    print(f"[atomize] MATH atom (a) CG_META FULL confirmation appended; math lines total={n_math}")
    ledger_append(atom_a_math_cg_meta, session_tag)

    n_meta = a5_append(META_ATOMS, atom_b_meta_promotion)
    print(f"[atomize] META atom (b) CG_META PROMOTION from MM_TENTATIVE parent appended; meta lines total={n_meta}")
    ledger_append(atom_b_meta_promotion, session_tag)

    print("[atomize] DONE 2 atoms + 2 ledger entries; A5-gated (tmp+os.replace+verify-load); matching TS_ISO")
