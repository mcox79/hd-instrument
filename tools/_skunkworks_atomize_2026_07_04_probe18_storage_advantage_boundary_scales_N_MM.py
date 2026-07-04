"""
A5-gated atomization -- Skunkworks landed-VET of Stage-1 Probe 18 (PAIRED
STORAGE-advantage boundary), 3-seed FULL, all HARD_PASS. 2026-07-04.

This is the GENUINE paired-design replacement for the retired mechanism-cross-term
mirage: it has NO mechanism axis, its discriminator is a WITHIN-ARM boundary
LOCATION and its N-movement gated against a two-stage MC binomial noise-floor null,
and both storage arms consume BIT-IDENTICAL items+corruption (PAIRING_VALID). By
construction it cannot re-manufacture the unpaired-range artifact.

DISPOSITION: MM_STANDARD (3-seed cv<0.15 gate met). CG delta 0, MM +1, HF 0.
File: math EMPIRICAL_STORAGE_ADVANTAGE_BOUNDARY_SCALES_N_v1.

===================== INDEPENDENT RECOMPUTE EVIDENCE (Skunkworks, off RAW phase_map) =====================
Cell:  experiments/exp_stage1_regime_probe_18_storage_advantage_boundary_paired_v1_core.py (commit b09826cd5)
Data:  data/exp_stage1_regime_probe_18_storage_advantage_boundary_paired_v1_s{7,13,19}/metrics.json
       run_mode=full, TR=200, device=cuda (RTX 4060 Ti), 61 units/seed, all verdict=HARD_PASS.
Prereg: preregs/2026-07-04_stage1_regime_probe_18_storage_advantage_boundary_paired_v1.md

METHOD: rebuilt per-(N,F) delta curves from the RAW SHARDED/BUNDLED phase-map arm
entries (NOT the analysis block), reimplemented the first-descending-crossing linear
interp boundary estimator, reran an INDEPENDENT two-stage MC binomial null (my own
numpy, ndraw=200000, seed 20260704), and computed 3-seed cv. Trusted no number from
the file's analysis block; then cross-checked against it.

BOUNDARY (corr at delta=acc_S-acc_B crossing 0.5), reproduced EXACTLY (recomp==file all 3 seeds):
  boundary_corr[N,F=1]:  N512     N2048    N8192
    s7                   0.86605  0.93337  0.96679
    s13                  0.86684  0.93577  0.96725
    s19                  0.86362  0.93524  0.96602
  cross-seed mean        0.8655   0.93479  0.96669   (per-(N,F) cv 0.0005-0.006, all << 0.15)

delta_scales_with_N (range over N of boundary_corr[.,F=1]):
  per-seed [0.10074, 0.10041, 0.10240]  (recomp==file exactly, all 3 seeds)
  mean 0.10118; population cv 0.86% (ddof=0), sample cv 1.05% (ddof=1)
    -> cv<0.15 gate passes by 17.4x (pop) / 14.2x (sample).
  MY independent MC null_q95_N per seed [0.00573, 0.00544, 0.00493]
    -> delta_scales_with_N ~0.10 exceeds null by ~18-21x, N_axis_fires=True ALL seeds.

delta_scales_with_F (range over F at N=512):
  per-seed [0.00528, 0.00497, 0.00268]  (recomp==file exactly)
  MY null_q95_F per seed [0.00585, 0.00676, 0.00528] -> scaleF <= nullq95 ALL seeds
    -> F_axis_fires=False ALL seeds: the boundary is SCALE-FREE in F (bounded-null sub-result).

DESIGN-INTEGRITY CHECKS (all pass, all 3 seeds, verified independently):
  - PAIRING_VALID: re-derived from hashes myself -- input_hash_sharded==input_hash_bundled
    AND ncf0_hash equal AND mask0_hash equal at all 30 pair-cells/seed; 30/30 valid, 0 invalid.
    (delta is a TRUE within-item paired difference, not a difference of independent draws.)
  - arms_distinct: SHARDED output hash != BUNDLED output hash where accS>0 (arms genuinely differ).
  - straddle_all: SHARDED goes >=0.90 to <=0.30 within each (N,F) grid (in-band, not saturated); True.
  - SATURATION_PC (Gate D reproducer, iterative_cosine M=800 N=2048 corr=0.20 SHARDED): acc=1.0 all seeds (>=0.95).
    Positive control clears its own floor FIRST (auditor discipline) -> the null is a genuine measurement, not a broken PC.
  - cardinality: 61 units/seed (60 paired storage-evals + 1 PC), all seeds. No breach.

HONEST FRAMING (symmetric anti-negativity; precision NOT demotion):
  BUNDLED acc = 0.000 at ALL 30 in-band cells (two isolated 0.005 = single-trial blips at N=8192).
  M=4800 >> Plate bound 0.14*N (=1147 at N=8192), so BUNDLED recovers ZERO on the SAME items SHARDED
  recovers. Therefore delta == acc_SHARDED identically, and boundary_corr_delta == boundary_corr_sharded
  EXACTLY in every cell (confirmed in file: boundary_corr_delta_by_NF == boundary_corr_sharded_by_NF).
  CONSEQUENCE: "the storage-advantage boundary scales with N" is mechanistically "the SHARDED corruption
  cliff moves to higher corr as N grows, while BUNDLED contributes nothing anywhere." This is a genuine,
  novel, clean 3-seed measurement of WHERE the (total) advantage collapses and that this collapse point is
  N-dependent (F-invariant). It is NOT evidence that BUNDLED moves; it must not be over-read as "the gap
  between two moving arms scales." The advantage is TOTAL and its boundary is the SHARDED noise-tolerance
  cliff, whose N-scaling (more dimensions -> higher tolerable corruption) is here MEASURED as a boundary law
  with an explicit binomial null and 3-seed cv for the first time.

NOVELTY vs prior STORAGE atoms (why MM +1, not confirmatory delta 0):
  - Parent CG (SPLIT STORAGE_MAIN_EFFECT survivor, 2026-07-04): measured SHARDED>>BUNDLED gap ~0.935 with
    SHARDED CEILING-PINNED (=1.0 everywhere) -> the gap was a LOWER BOUND and its "N-invariance" (P4) was an
    artifact of SHARDED being unable to move. This cell moves SHARDED IN-BAND (straddling its cliff) and shows
    the ADVANTAGE's collapse boundary IS N-dependent (0.866->0.935->0.967). That is the genuine extension the
    parent could not see. Composes with (extends) the parent CG; does NOT supersede or demote it.
  - P16 measured the SHARDED cliff at ONE (N=512,F=1) point only; this maps it at 3 N x 2 F with a scaling
    range + two-stage binomial null + 3-seed cv. No prior atom measures a boundary-scaling law here.

CROSS-ARC OVERLAP CHECK (USER-locked 2026-07-01): bash tools/substrate_query.sh
  "STORAGE advantage SHARDED BUNDLED collapse boundary paired gap corruption cliff scales with N"
  top hit cosine 0.2959 (prereg sharded_fhrr_capacity_scale_free_extension N16384 -- a capacity/scale-free
  arc, NOT this paired boundary map); all other hits <0.30 (generic 'storage'/'bundle' wordnet/notes).
  NONE >0.30. Genuinely novel: no prior arc cell measures a PAIRED within-item SHARDED-vs-BUNDLED advantage
  boundary or its N/F scaling. Targeted extension of the STORAGE_MAIN_EFFECT CG into the in-band regime.

DESIGN-CANNOT-REMANUFACTURE-ARTIFACT (verified): single MECH=modern_hopfield (no mechanism axis to moderate);
  discriminator is a within-arm boundary LOCATION + its N-movement vs a binomial null (not a max/range over
  noisy arms); paired-by-construction (shared pre-drawn state, PAIRING_VALID 30/30). This is a clean positive
  APPLICATION of the paired-trials-MANDATORY meta rule that closed the cross-term family.
"""
import json
import os
import time
import tempfile

MATH_ATOMS = "d:/AI/hd-instrument/data/substrate_index/math/atoms.jsonl"
CERT_LEDGER = "d:/AI/hd-instrument/data/substrate_index/meta/cert_ledger.jsonl"

TS = time.time()
TS_ISO = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(TS))

ANCHOR = "stage1_regime_probe_18_storage_advantage_boundary_paired_v1"
METRICS = [f"data/exp_{ANCHOR}_s{s}/metrics.json" for s in (7, 13, 19)]

PARENT_CG_STORAGE_MAIN_EFFECT_ID = ("math::SPLIT_stage1_regime_map_storage_x_cleanup_STORAGE_MAIN_EFFECT_survivor_CG_grade_confirmatory_SHARDED_dominates_BUNDLED_readout_quality_median_gap_0p935_0p93_0p92_3seed_FULL_36of36_pairs_positive_min_gap_0p76_SHARDED_mean_1p000_BUNDLED_mean_0p09_confirms_prior_SHARDED_capacity_beyond_bundle_bound_atom56_NOT_novel_delta0_SHARDED_ceiling_saturated_so_gap_is_lower_bound_2026-07-04")
PAIRED_TRIALS_META_ID = ("meta::T4/META_paired_trials_MANDATORY_for_arm_comparison_max_or_range_discriminators_unpaired_independent_salts_MANUFACTURE_phantom_cross_terms_shared_items_corruptions_across_arms_OR_data_driven_binomial_extreme_value_null_REQUIRED_at_prereg_case_study_Probe1_storage_x_cleanup_TR100_unpaired_range_0p10_looked_like_moderation_paired_TR400_range_EXACTLY_0_z_neg8p88_retroactive_to_regime_map_cross_term_family_P1_P6_P7_P8_promotes_P8_extreme_value_null_meta_MM_STANDARD_2026-07-04")

atom = {
    "id": "math::EMPIRICAL_STORAGE_ADVANTAGE_BOUNDARY_SCALES_N_v1_stage1_probe18_PAIRED_SHARDED_vs_BUNDLED_in_band_3seed_FULL_HARD_PASS_boundary_corr_at_delta_0p5_moves_0p866_N512_to_0p935_N2048_to_0p967_N8192_range_0p101_cv_0p9pct_vs_binomial_nullq95_0p005_18x_F_scale_free_range_0p005_le_null_BUNDLED_identically_0_across_all_30_inband_cells_so_advantage_boundary_IS_SHARDED_corruption_cliff_extends_STORAGE_MAIN_EFFECT_CG_from_ceiling_pinned_to_in_band_2026-07-04",
    "name": "MATH storage-advantage boundary SCALES with N (F scale-free): PAIRED SHARDED-vs-BUNDLED in-band, 3-seed FULL HARD_PASS. boundary_corr (delta crosses 0.5) moves 0.866 (N512) -> 0.935 (N2048) -> 0.967 (N8192), range 0.101, cv ~0.9-1.1% << 0.15, ~18-21x above binomial null q95 ~0.005; F axis scale-free (range 0.005 <= null). BUNDLED identically 0 across all 30 in-band cells so the advantage is TOTAL and its boundary IS the SHARDED corruption cliff. Extends STORAGE_MAIN_EFFECT CG from ceiling-pinned to in-band.",
    "corpus": "math",
    "tier": "T3",
    "kind": "experiment_record_measured_regime_boundary",
    "description": (
        "MM_STANDARD 3-seed measurement (the #1 surviving Stage-1 law -- SHARDED>>BUNDLED storage advantage -- "
        "measured for the FIRST TIME in the regime where SHARDED can actually MOVE). PAIRED SHARDED-vs-BUNDLED "
        "FHRR chain (L=2, M=4800 fixed), single MECH=modern_hopfield (NO mechanism axis), sweeping corr x F x N "
        "so SHARDED straddles its corruption cliff (in-band, not ceiling-pinned). Discriminator = boundary_corr = "
        "corr at which the WITHIN-ITEM paired gap delta=acc_SHARDED-acc_BUNDLED crosses 0.5, and its range over "
        "N/F, gated against a two-stage MC binomial noise-floor null. 3 seeds {7,13,19} TR=200, all verdict "
        "HARD_PASS (N_axis moves, F scale-free). "
        "INDEPENDENT RECOMPUTE (Skunkworks, off RAW phase_map not the analysis block; own boundary estimator + "
        "own MC null ndraw=200000 seed 20260704): boundary_corr[N,F=1] = {N512: 0.866, N2048: 0.935, N8192: "
        "0.967} (per-seed exact-match to file all 3 seeds; per-(N,F) cross-seed cv 0.0005-0.006). "
        "delta_scales_with_N per-seed [0.10074, 0.10041, 0.10240] (recomp==file), mean 0.10118, population cv "
        "0.86% / sample cv 1.05% -> cv<0.15 gate passes 14-17x. MY MC null_q95_N per-seed [0.00573, 0.00544, "
        "0.00493] -> N-axis exceeds null by ~18-21x, fires ALL seeds. delta_scales_with_F per-seed [0.00528, "
        "0.00497, 0.00268] all <= MY null_q95_F [0.00585, 0.00676, 0.00528] -> F scale-free (bounded-null sub-"
        "result) ALL seeds. "
        "DESIGN INTEGRITY (verified independently, all 3 seeds): PAIRING_VALID re-derived from hashes myself -- "
        "input/ncf0/mask0 hashes identical across arms at all 30 pair-cells/seed (30/30 valid), so delta is a "
        "true within-item paired difference; arms_distinct (SHARDED out != BUNDLED out); straddle_all True; "
        "SATURATION_PC (Gate D) acc=1.0 all seeds (clears its own floor first -> null is genuine, not a broken "
        "PC); cardinality 61 units/seed no breach. Cannot re-manufacture the retired unpaired-range mechanism "
        "cross-term artifact (no mechanism axis; boundary-LOCATION discriminator not max/range-over-noisy-arms; "
        "paired-by-construction) -- a clean positive APPLICATION of the paired-trials-MANDATORY meta rule. "
        "HONEST FRAMING (symmetric, precision not demotion): BUNDLED acc = 0.000 at ALL 30 in-band cells "
        "(two isolated 0.005 single-trial blips at N=8192); M=4800 >> Plate bound 0.14*N, so BUNDLED recovers "
        "ZERO on the SAME items SHARDED recovers. Hence delta == acc_SHARDED identically and boundary_corr_delta "
        "== boundary_corr_sharded EXACTLY every cell. So 'storage-advantage boundary scales with N' is "
        "mechanistically 'the SHARDED corruption cliff moves to higher tolerable corr as N grows, BUNDLED "
        "contributing nothing anywhere'. The advantage is TOTAL; this is a genuine novel measurement of WHERE it "
        "collapses and that this collapse point is N-dependent and F-invariant. It is NOT evidence BUNDLED moves "
        "and must not be over-read as a gap between two moving arms. "
        "NOVELTY / EXTENSION: parent CG STORAGE_MAIN_EFFECT (gap ~0.935) was SHARDED-CEILING-PINNED (=1.0 "
        "everywhere) so its gap was a LOWER BOUND and 'N-invariant' only because SHARDED could not move; this "
        "cell moves SHARDED in-band and reveals the advantage's boundary IS N-dependent. P16 measured the SHARDED "
        "cliff at ONE (N512,F1) point; this maps it 3N x 2F with a scaling range + binomial null + 3-seed cv. "
        "Composes with (extends) the parent CG; does not supersede or demote it. "
        "DISPOSITION: MM_STANDARD (3-seed cv<0.15 met; arc-continuation grade, not a composable mechanism "
        "primitive). REVIVAL / EXPANSION to CG: (a) a fitted functional form for boundary_corr(N) (e.g. cliff at "
        "1 - c/sqrt(N)) validated at a 4th N, or (b) a load-collapse (collapse_r2 one_minus_corr_times_sqrtN "
        "~0.85 pooled here) confirmed across seeds, would promote MM->CG as a boundary LAW."
    ),
    "aliases": ["probe18_storage_advantage_boundary_scales_N",
                "EMPIRICAL_STORAGE_ADVANTAGE_BOUNDARY_SCALES_N_v1",
                "sharded_corruption_cliff_scales_with_N_paired_in_band"],
    "metadata": {
        "record_class": "experiment_measured_regime_boundary_scaling",
        "term_class": "STAGE1_STORAGE_ADVANTAGE_BOUNDARY_N_SCALING_PAIRED_IN_BAND",
        "cert_status": "mm_standard_measured_regime_boundary_scaling",
        "cert_class": "MM_STANDARD_storage_advantage_boundary_scales_N_F_scale_free_paired_3seed",
        "cert_ts": TS_ISO,
        "verified_off_data": True,
        "atomized_by": "skunkworks_landed_VET_2026-07-04_probe18_storage_advantage_boundary_scales_N",
        "anchor": ANCHOR,
        "cell_source_path": "experiments/exp_stage1_regime_probe_18_storage_advantage_boundary_paired_v1_core.py",
        "cell_commit": "b09826cd5",
        "prereg_path": "preregs/2026-07-04_stage1_regime_probe_18_storage_advantage_boundary_paired_v1.md",
        "raw_metrics_paths": METRICS,
        "primitive_source": "experiments/_stage1_physics_law_joint_composition_factorial_v1_core.py::{build_rules,cleanup_argmax_idx,run_chain(reference)}; run_chain_paired refactor (pre-draws all stochastic state; selftest asserts bit-for-bit run_chain_paired(SHARDED)==run_chain(SHARDED))",
        "run_mode": "full", "TR": 200, "device": "cuda (RTX 4060 Ti)",
        "n_seeds": 3, "seeds": [7, 13, 19],
        "verdict_all_seeds": "HARD_PASS (N_axis moves, F scale-free)",
        "recompute_check": {
            "method": "rebuilt per-(N,F) delta curves from RAW SHARDED/BUNDLED phase-map arm entries; own first-descending-crossing linear-interp boundary; own two-stage MC binomial null (numpy, ndraw=200000, seed=20260704); own 3-seed cv. Trusted no analysis-block number then cross-checked.",
            "boundary_corr_N_F1": {"s7": {"N512": 0.86605, "N2048": 0.93337, "N8192": 0.96679},
                                    "s13": {"N512": 0.86684, "N2048": 0.93577, "N8192": 0.96725},
                                    "s19": {"N512": 0.86362, "N2048": 0.93524, "N8192": 0.96602}},
            "boundary_corr_cross_seed_mean_N_F1": {"N512": 0.8655, "N2048": 0.93479, "N8192": 0.96669},
            "boundary_corr_per_NF_cross_seed_cv": {"N512_F1": 0.00158, "N512_F4": 0.00597, "N2048_F1": 0.0011,
                                                    "N2048_F4": 0.00157, "N8192_F1": 0.00052, "N8192_F4": 6e-05},
            "delta_scales_with_N_per_seed": [0.10074, 0.10041, 0.10240],
            "delta_scales_with_N_mean": 0.10118,
            "delta_scales_with_N_cv_population": 0.00861,
            "delta_scales_with_N_cv_sample_ddof1": 0.01054,
            "cv_gate_threshold": 0.15,
            "cv_gate_margin": "17.4x (population) / 14.2x (sample)",
            "my_mc_null_q95_N_per_seed": [0.00573, 0.00544, 0.00493],
            "N_axis_exceeds_null_factor": "~18-21x",
            "N_axis_fires_all_seeds": True,
            "delta_scales_with_F_per_seed": [0.00528, 0.00497, 0.00268],
            "my_mc_null_q95_F_per_seed": [0.00585, 0.00676, 0.00528],
            "F_axis_fires_any_seed": False,
            "recomp_matches_file_all_seeds": True,
        },
        "design_integrity_checks": {
            "pairing_valid": "re-derived from hashes: input_hash_S==input_hash_B AND ncf0_hash equal AND mask0_hash equal at all 30 pair-cells/seed; 30/30 valid, 0 invalid, all 3 seeds",
            "arms_distinct": "SHARDED output hash != BUNDLED output hash where accS>0, all seeds",
            "straddle_all": "SHARDED >=0.90 to <=0.30 within each (N,F) grid (in-band, not saturated), all seeds",
            "saturation_pc": "Gate D reproducer iterative_cosine M=800 N=2048 corr=0.20 SHARDED acc=1.0 all seeds (>=0.95); clears own floor first",
            "cardinality": "61 units/seed (60 paired storage-evals + 1 PC), no breach, all seeds",
            "cannot_remanufacture_artifact": "single MECH (no mechanism axis); within-arm boundary-LOCATION discriminator gated vs binomial null (not max/range over noisy arms); paired-by-construction",
        },
        "honest_framing_symmetric": (
            "BUNDLED acc = 0.000 at ALL 30 in-band cells (two 0.005 single-trial blips at N=8192); M=4800 >> "
            "Plate 0.14*N, so BUNDLED recovers ZERO on the SAME items SHARDED recovers -> delta==acc_SHARDED "
            "identically and boundary_corr_delta==boundary_corr_sharded EXACTLY. The advantage-boundary N-scaling "
            "IS the SHARDED corruption-cliff N-scaling (more dims -> higher tolerable corr). Genuine novel "
            "measurement of WHERE the total advantage collapses and its N-dependence/F-invariance; NOT evidence "
            "BUNDLED moves; do not over-read as a gap between two moving arms."
        ),
        "boundary_movement": {"N512_F1": 0.8655, "N2048_F1": 0.93479, "N8192_F1": 0.96669,
                              "range_N": 0.10118, "F_scale_free_range_N512": "~0.005 <= null ~0.006"},
        "collapse_r2_pooled": {"raw_corr": 0.21, "one_minus_corr_times_sqrtN": 0.85, "corr_minus_boundaryNF": 0.79,
                               "note": "informational (not gated); load-collapse onto (1-corr)*sqrt(N) ~0.85 pooled -- candidate CG-promotion functional form"},
        "extends_atom": PARENT_CG_STORAGE_MAIN_EFFECT_ID,
        "extension_scope": "parent CG measured the SHARDED>>BUNDLED gap with SHARDED CEILING-PINNED (=1.0, gap a lower bound, 'N-invariant' by construction); this moves SHARDED in-band and reveals the advantage's collapse boundary is N-dependent (0.866->0.935->0.967) and F-invariant. Extends, does not supersede/demote the parent.",
        "composes_with_atoms": [PARENT_CG_STORAGE_MAIN_EFFECT_ID, PAIRED_TRIALS_META_ID],
        "positive_application_of_meta": "clean positive use of the paired-trials-MANDATORY meta rule: paired within-item discriminator + binomial null, no mechanism axis -> the effect that survives is REAL (boundary moves), not a manufactured cross-term",
        "revival_or_expansion_to_CG": [
            "fit boundary_corr(N) functional form (e.g. 1 - c/sqrt(N)) validated at a 4th N",
            "confirm load-collapse (one_minus_corr_times_sqrtN r2 ~0.85 pooled) across seeds -> boundary LAW -> MM->CG",
        ],
        "cross_arc_overlap_check_2026_07_01_USER_locked": "substrate_query top hit cosine 0.2959 (prereg sharded_fhrr_capacity_scale_free_extension N16384, a capacity/scale-free arc NOT this paired boundary map); all others <0.30 (generic storage/bundle wordnet/notes). NONE >0.30. Genuinely novel: no prior arc cell measures a PAIRED within-item SHARDED-vs-BUNDLED advantage boundary or its N/F scaling. Targeted extension of STORAGE_MAIN_EFFECT CG into the in-band regime.",
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
        "atomized_by": "skunkworks_landed_VET_2026-07-04_probe18_storage_advantage_boundary_scales_N",
        "landed_VET_session": session_tag,
        "extends_atom": PARENT_CG_STORAGE_MAIN_EFFECT_ID,
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
    tag = "2026-07-04_probe18_storage_advantage_boundary_scales_N"
    n = a5_append(MATH_ATOMS, atom)
    print(f"[atomize] math MM_STANDARD probe18 storage-advantage-boundary-scales-N appended; math lines={n}")
    ledger_append(atom, tag)
    print("[atomize] DONE 1 atom + 1 ledger entry; A5-gated (tmp+os.replace+verify-load+json-integrity); matching TS_ISO")
    print("[atomize] NET CERT DELTA: CG 0, MM +1, HF 0")
