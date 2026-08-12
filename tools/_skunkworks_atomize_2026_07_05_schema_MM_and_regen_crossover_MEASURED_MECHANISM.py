"""
A5-gated atomization -- Skunkworks landed-VET 2026-07-05.
Two landings: schema-formation FULL (HARD_PASS) + reasoning regen-vs-analog FULL (HARD_FAIL).
AUDIT-ONLY. Both mechanisms independently RE-EXECUTED off the cells' own functions
(recompute_audit.py, .venv) and reproduced disk EXACTLY -- verified_off_data via
re-execution, not verdict-report.

BATCH CONTENTS (2 atoms, matching TS_ISO):
  (1) math  MM_STANDARD -- schema_bundle_structural_transfer_v1 HARD_PASS. Holistic/
        analogical map M_R=mean bind(B,inv(A)) extracts a systematic relational
        transform from NOISY exemplars and generalizes to NOVEL same-relation
        subjects. real_gain(M200)=+0.590 cv 0.069; subject-conditional (real-cind
        +0.590); shuffled control flat (+0.003); sample-size gradient clean; M10
        null-bracket fires (+0.112 < 0.30 suspicion). NON-VACUOUS (not by-construction
        planted: rising SNR learning curve, novel test subjects, two controls collapse
        to chance). SCOPE (honestly stated in cell): synthetic dial-able structure,
        NOT real KG atoms -- proves the MECHANISM given structure exists, does NOT
        prove real relations carry learnable structure (explicit follow-up cell). MM +1.
  (2) math  MEASURED_MECHANISM -- cortex_regenerative_cleanup_vs_analog_accumulate_v1
        HARD_FAIL, resolved to a proven boundary (modest-real, NOT dead). Digital
        regenerative (hard-snap) cleanup degrades more gracefully than analog soft-carry
        ABOVE the M/N~1 Hebbian crosstalk threshold; analog wins BELOW (crossover 5/5).
        The direction is robust (5/5 seeds regen>analog @DISC, gap widens with load) but
        the ABSOLUTE magnitude is MODEST: regen_d5~0.263, NOT the ~0.60 a small-seed probe
        suggested. HARD_FAIL is driven by an OPERATING-POINT / SANITY-FLOOR INCOMPATIBILITY
        (SANITY_D1_MIN=0.85 unreachable at DISC M/N=1.10 where single-hop d1~0.75), plus
        over-optimistic HP magnitude bands -- NOT by the mechanism being dead. MM +1.

NET CERT DELTA (this batch): CG 0, MM +2, HF 0.
No DEMOTE: neither anchor held a prior CG/MM cert.
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

SESSION_TAG = "2026-07-05_schema_MM_and_regen_crossover_MEASURED_MECHANISM"

# Prior lineage composed by the reasoning atom (surfaced by concept-overlap check @0.26).
PRIOR_COT_META_ID = "meta::T3/META_substrate_native_chain_of_thought_iterative_cleanup_K_up_to_4_at_substrate_scale_2026-06-22"

# ---------------------------------------------------------------------------
# ATOM 1 -- SCHEMA (math, MM_STANDARD)
# ---------------------------------------------------------------------------
atom_schema = {
    "id": "math::MM_STANDARD_schema_bundle_structural_transfer_holistic_analogical_map_M_R_mean_bind_B_inv_A_extracts_systematic_relational_transform_from_NOISY_exemplars_and_GENERALIZES_to_NOVEL_same_relation_subjects_real_gain_M200_plus0p590_cv0p069_subject_conditional_real_minus_cind_plus0p590_shuffled_control_flat_plus0p003_sample_size_gradient_clean_0p21_to_0p69_M10_null_bracket_fires_plus0p112_lt_0p30_suspicion_NON_VACUOUS_not_byconstruction_planted_rising_SNR_learning_curve_novel_test_subjects_two_controls_collapse_to_chance_SCOPE_synthetic_dialable_structure_NOT_real_KG_proves_MECHANISM_given_structure_exists_3seed_FULL_N4096_K10_sigma2p0_2026-07-05",
    "name": "MATH MM_STANDARD: bundle-schema structural transfer -- the holistic/analogical map M_R=mean bind(B,inv(A)) (Kanerva 'Dollar of Mexico') extracts a systematic relational transform from NOISY exemplars and generalizes to NOVEL same-relation subjects. real_gain(M200)=+0.590 (cv 0.069), subject-conditional (real-cind +0.590), shuffled flat (+0.003), clean sample-size gradient 0.21->0.69, M10 null-bracket fires (+0.112). Non-vacuous (not by-construction planted). SCOPE: synthetic dial-able structure, NOT real KG -- proves the MECHANISM given structure exists.",
    "corpus": "math",
    "tier": "MM_STANDARD",
    "kind": "experiment_landed_vet",
    "cert_status": "proven_bound_measured_mechanism",
    "cert_class": "bundle_schema_holistic_analogical_map_structural_transfer_to_novel_subjects_on_synthetic_dialable_structure_subject_conditional_sample_size_driven_scope_mechanism_not_real_encoding",
    "description": (
        "LANDED-VET of exp_schema_bundle_structural_transfer_v1 (verdict HARD_PASS_SCHEMA_TRANSFER, "
        "run_mode=full, N=4096, K=10, sigma=2.0, 3 seeds [7,13,19], 45 units, cardinality_ok, "
        "arms_differ_verified, bind_roundtrip=1.000; commit 70d58f593). "
        "AUDITOR INDEPENDENT RE-EXECUTION (imported the cell's build_and_eval/aggregate, re-ran all "
        "3 seeds x 5 M x 3 arms, did NOT read the verdict): ALL headline numbers reproduce EXACTLY off "
        "the mechanism -- real curve {10:0.2117, 30:0.3050, 50:0.3550, 100:0.5300, 200:0.6900}; "
        "real_gain(M200)=+0.5900 cv=0.0691; shuf_gain(M200)=+0.0033; real-cind(M200)=+0.5900; "
        "real_gain(M10)=+0.1117; arms_differ=True; bind_rt=1.000. "
        "MECHANISM: subjects of class k are phase-jittered copies of a prototype MU[k] (sigma=2.0 rad => "
        "single-exemplar corr with prototype ~exp(-2)=0.135, i.e. one subject barely signals its class); "
        "the schema M_R=mean_i bind(O[label_i], conj(A_i)) averages the per-pair transforms into ONE "
        "segregated one-way-fed store; a NOVEL subject C (fresh jitter, never in training) is read by "
        "D_hat=bind(C,M_R) then argmax vs object codebook. This is a genuine SNR-driven learning curve "
        "(schema sharpens as per-class count M/K grows from 1 to 20). "
        "NON-VACUITY / NOT-BY-CONSTRUCTION (the by-construction risk the Director flagged, checked and "
        "refuted): (a) rising sample-size gradient 0.21->0.69 -- a planted answer would be flat-high at "
        "M=10; (b) M10 gain +0.112 is BELOW the 0.30 SUSPICION rail (transfer is NOT maxed at 1 example/"
        "class => sample-driven schema, not codebook artifact -- the null-bracket the prereg designed FIRES); "
        "(c) test subjects are held-out fresh jitter (genuine generalization, no leakage); (d) TWO "
        "independent controls collapse to chance -- ARM_SHUFFLED (object labels permuted, structure "
        "destroyed) at 0.103 gain +0.003, and ARM_MEAN_OBJECT (subject-blind readout D_hat=M_R) at exactly "
        "0.100. The subject-blind control at chance is the KEY discriminator: it proves the transfer is "
        "SUBJECT-CONDITIONAL (reads the novel entity), not 'return the popular object'. "
        "SCOPE (honestly and prominently stated in the cell docstring, NOT overclaimed): the generator is "
        "SYNTHETIC dial-able shared structure. This proves the bundle-schema holistic-map MECHANISM works "
        "GIVEN entities carry a systematic subject->object transform; it does NOT prove that REAL KG entity "
        "encodings carry such structure (the ~80-cell prior of EXACTLY 0.000 structural transfer is on real/"
        "random atoms; that is the encoder problem, not the mechanism). The cell's WHAT_THIS_DOES_NOT_SHOW "
        "section states this explicitly and names the real-encoding follow-up as the next cell. "
        "TIER RATIONALE: MM_STANDARD (proven mechanism bound), not CHAIN_GRADE -- evidence quality is "
        "standard-grade (3 seeds, tight cv 0.069, 4 discriminators fire, exact re-execution) but the claim "
        "is narrow (mechanism-on-ideal-structure); real-encoding transferability is untested and the "
        "generator is mechanism-favorable (it provides exactly the structure the analogical map reads). "
        "Not REFUTED -- the result is clean, real and well-controlled within scope."
    ),
    "aliases": ["schema_bundle_structural_transfer_holistic_map_MM",
                "kanerva_dollar_of_mexico_novel_subject_transfer_synthetic"],
    "metadata": {
        "record_class": "experiment_landed_vet_measured_mechanism",
        "term_class": "SCHEMA_FORMATION_BUNDLE_HOLISTIC_ANALOGICAL_MAP_STRUCTURAL_TRANSFER_SYNTHETIC_SCOPE",
        "cert_status": "proven_bound_measured_mechanism",
        "cert_class": "bundle_schema_holistic_map_structural_transfer_novel_subject_synthetic_dialable_subject_conditional_sample_driven",
        "cert_ts": TS_ISO,
        "verified_off_data": True,
        "verified_via": "independent re-execution of cell mechanism functions (build_and_eval/aggregate), reproduced disk EXACTLY; not verdict-report",
        "atomized_by": "skunkworks_landed_VET_2026-07-05_schema_bundle_structural_transfer",
        "anchor": "schema_bundle_structural_transfer_v1",
        "cell_commit": "70d58f593",
        "raw_metrics_path": "data/exp_schema_bundle_structural_transfer_v1/metrics.json",
        "run_mode": "full", "N": 4096, "K": 10, "sigma": 2.0,
        "n_seeds": 3, "seeds": [7, 13, 19], "n_units": 45, "cardinality_ok": True,
        "recompute_off_disk": {
            "real_curve": {"10": 0.2117, "30": 0.3050, "50": 0.3550, "100": 0.5300, "200": 0.6900},
            "real_gain_M200": 0.5900, "real_cv_M200": 0.0691,
            "shuf_gain_M200": 0.0033, "real_minus_cind_M200": 0.5900,
            "real_gain_M10": 0.1117, "arms_differ": True, "bind_roundtrip": 1.000,
            "match_disk": "EXACT",
        },
        "non_vacuity_checks": {
            "sample_size_gradient": "0.21->0.69 rising (planted answer would be flat-high)",
            "M10_null_bracket": "gain +0.112 < 0.30 suspicion rail => sample-driven not codebook artifact (FIRES)",
            "held_out_novel_subjects": "fresh jitter never in training -> genuine generalization no leakage",
            "control_shuffled": "0.103 gain +0.003 (structure destroyed -> chance)",
            "control_subject_blind_mean_object": "0.100 exactly (transfer is subject-conditional, not popularity)",
        },
        "scope_caveat": "SYNTHETIC dial-able shared structure. Proves the MECHANISM given structure exists; does NOT prove real KG encodings carry learnable structure (real/random atoms -> ~80-cell prior of 0.000 structural transfer = encoder problem). Cell states this explicitly; real-encoding cell is the named follow-up.",
        "by_construction_verdict": "NON-VACUOUS; generator is mechanism-favorable (provides the structure the analogical map reads) but the specific by-construction failure modes (planted-constant, popularity-readout, leakage) are each ruled out by a firing discriminator.",
        "cross_arc_overlap_check_2026_07_01_USER_locked": "substrate_query 'bundle schema holistic map structural transfer novel entity relation generalization' -> top hits 0.317-0.323 are LIT-ANCHOR note chunks (Random-Features-Hopfield 'generalization phase' arXiv 2407.05658 = the cell's own cited mechanism inspiration) + wordnet 'generalization'; NO prior EXPERIMENT/CERT atom on bundle-schema structural transfer. NOVEL result (the ~80-cell 0.000-transfer prior is CL-adjacent on real atoms, a different mechanism). Not a rediscovery.",
        "composes_with_atoms": [],
        "framing_corrections_vs_director_and_cell": "AGREE with cell's HARD_PASS and scope statement (symmetric: no inflation, no deflation). Director asked to confirm the +0.590 is real-not-by-construction and that the synthetic scope is honestly stated -- CONFIRMED both off independent re-execution: the +0.590 is a genuine SNR-driven learning curve (not a planted constant), and the cell's docstring states the synthetic-mechanism-only scope prominently and names the real-encoding follow-up. One clarification: ARM_MEAN_OBJECT reads EXACTLY 0.100 with ~zero cross-seed variance because argmax of a single fixed vector matches exactly 1 of K=10 classes by construction -- this is the intended chance-level subject-blind control, its determinism is a metric artifact not a defect.",
        "expansion_criterion": "PROMOTES toward CHAIN_GRADE iff the named real-encoding follow-up (does the substrate's ACTUAL entity encoding carry a systematic subject->object transform the bundle-schema can extract?) returns above-random subject-conditional transfer on the NATIVE encoder -- the load-bearing untested question. DEMOTES if the effect fails to survive sigma/K generator variation or collapses when the generator's shared-structure dial -> 0.",
        "disposition": "MEASURED_MECHANISM_bundle_schema_holistic_map_generalizes_to_novel_subjects_on_synthetic_dialable_structure_subject_conditional_sample_driven_real_encoding_transferability_DEFERRED",
        "cert_increment_delta": 1,
    },
}

# ---------------------------------------------------------------------------
# ATOM 2 -- REASONING (math, MEASURED_MECHANISM)
# ---------------------------------------------------------------------------
atom_regen = {
    "id": "math::MEASURED_MECHANISM_regenerative_hard_cleanup_vs_analog_soft_carry_DIGITAL_REPEATER_CROSSOVER_at_Hebbian_crosstalk_threshold_M_over_N_approx_1_regen_degrades_GRACEFULLY_analog_COLLAPSES_above_threshold_analog_WINS_below_crossover_5of5_seeds_gap_widens_with_load_plus0p133_at_8k_to_plus0p28_at_16k_BUT_absolute_magnitude_MODEST_regen_d5_approx_0p263_NOT_the_0p60_a_small_seed_probe_suggested_HARD_FAIL_is_OPERATING_POINT_SANITY_FLOOR_INCOMPATIBILITY_d1_0p71_to_0p79_lt_0p85_unreachable_at_DISC_M_over_N_1p10_NOT_mechanism_dead_controls_fire_faith_1p0_5seed_FULL_N8192_2026-07-05",
    "name": "MATH MEASURED_MECHANISM: digital regenerative (hard-snap) cleanup vs analog soft-carry -- a repeater CROSSOVER at the Hebbian crosstalk threshold M/N~1. Regen degrades gracefully / analog collapses ABOVE threshold; analog wins BELOW (crossover 5/5 seeds; gap widens with load). Direction robust BUT absolute magnitude MODEST (regen_d5~0.263, NOT the ~0.60 a small-seed probe suggested). HARD_FAIL is an operating-point/sanity-floor incompatibility (d1~0.75 < 0.85 floor unreachable at DISC M/N=1.10), NOT mechanism death.",
    "corpus": "math",
    "tier": "MEASURED_MECHANISM",
    "kind": "experiment_landed_vet",
    "cert_status": "proven_bound_measured_mechanism_modest_real_positive_hard_fail_operating_point_incompatibility",
    "cert_class": "digital_regenerative_hard_cleanup_vs_analog_soft_carry_repeater_crossover_at_MoverN_1_graceful_vs_catastrophic_modest_magnitude_bound",
    "description": (
        "LANDED-VET of exp_cortex_regenerative_cleanup_vs_analog_accumulate_v1 (verdict HARD_FAIL, 5 seeds "
        "[7,17,23,31,41] pass=0 fail=5, run_mode=full, N=8192, V=512, P=8, M_BG sweep {2000,5000,8000,12000,"
        "16000}, cardinality_ok, arms_differ=True, isolation_clean=True; commit c65669c19). RESOLVED to a "
        "MEASURED_MECHANISM proven boundary: the mechanism is MODEST-REAL, not dead. "
        "AUDITOR INDEPENDENT RE-EXECUTION (imported the cell's run_seed_mbg, re-ran seed7@8000, seed7@2000, "
        "seed23@8000; did NOT read the verdict): ALL numbers reproduce EXACTLY -- seed7@8000 (M/N=1.105) "
        "regen_d5=0.2200 analog_d5=0.0867 gap+0.1333 d1=0.7133 control_d5=0.0067 faith=1.0; seed7@2000 "
        "(M/N=0.372) regen_d5=0.2600 analog_d5=0.5333 gap-0.2733 (analog wins below capacity); seed23@8000 "
        "regen_d5=0.2600 analog_d5=0.0667 gap+0.1933. Aggregate reproduces: mean regen_d5@DISC=0.2627, mean "
        "gap@DISC=+0.176 (std 0.050), 5/5 crossover confirmed, mean control_d5=0.0027 (~chance 0.00195). "
        "MECHANISM (genuine and textbook-consistent): a HARD-SNAP regenerative repeater (snap to nearest "
        "codeword each hop, scratchpad-isolated -- W checksum invariant, isolation_clean 5/5) resets the "
        "signal to a clean codeword so noise does NOT accumulate; an ANALOG soft-carry repeater amplifies "
        "noise with signal (data-processing inequality, multiplicative (1-eps)^K decay). TWO crossovers "
        "measured: (i) across LOAD -- analog wins at M/N=0.37 (soft-decision > hard-decision when the "
        "Hebbian readout is itself a denoiser and little noise has accumulated), regen wins at M/N>=1.1 "
        "(analog crosses its operating-capacity threshold and collapses catastrophically: analog_d5 0.087 "
        "@8k -> 0.007 @16k, while regen holds 0.22-0.33); gap widens monotonically with load (+0.133@8k, "
        "+0.267@12k, +0.28@16k). (ii) across DEPTH at fixed high load -- analog is BETTER at shallow depth "
        "(analog_d3~0.61 > regen_d3~0.40) but falls off a cliff, so regen only wins at depth>=4-5. This is "
        "the genuine digital-vs-analog repeater tradeoff: hard-snap discards the soft residual that helps "
        "early, but avoids catastrophic late accumulation. Faithfulness=1.0 (regen replay from the discrete "
        "trace reproduces its answer by construction); controls fire; arms differ. "
        "HONEST EFFECT SIZE (symmetric anti-negativity, DOWNWARD correction of the smoke): the ABSOLUTE "
        "magnitude is MODEST -- regen_d5~0.263 at the DISC operating point (26% at depth 5, well above chance "
        "1/512=0.002 but far from 'usable'). This is NOT the regen_d5~0.60 a small-seed probe (the cell's "
        "'3-seed regime probe'; Director recalled it as the 2-seed smoke) reported. The probe's ~0.60 was "
        "NOT reproduced at ANY M_BG in the FULL run (even the lowest-load M_BG=2000 gives regen_d5~0.26), so "
        "it was genuinely over-optimistic (small-seed high variance and/or a lighter total load: the smoke's "
        "N_TEST=48 puts fewer chain-edges into W than FULL's N_TEST=150, so 'M_BG=8000' is M/N~1.02 in smoke "
        "vs ~1.10 in full). True regen_d5 magnitude is ~0.26. "
        "WHY HARD_FAIL (the load-bearing framing correction): the HARD_FAIL trigger is NOT the mechanism gap "
        "and NOT directly the smoke-vs-full magnitude -- it is the SANITY_BREACH rail, evaluated FIRST in "
        "classify_seed: SANITY_D1_MIN=0.85 requires single-hop d1>=0.85, but at the DISC operating point "
        "(M/N=1.10) single-hop retrieval is inherently only ~0.71-0.79 (re-executed: the Hebbian crosstalk "
        "at M/N>1 degrades even one hop). This is an OPERATING-POINT / SANITY-FLOOR INCOMPATIBILITY: the cell "
        "simultaneously requires (a) d1>=0.85 AND (b) M/N~1.1 where analog collapses -- but on N=8192 these "
        "are mutually exclusive. It would HARD_FAIL here even if regen_d5 were 0.60. SECONDARILY, the HP "
        "magnitude bands are over-optimistic: HP_REGEN_D5_MIN=0.45 is met by NO seed (max 0.35) and "
        "HP_GAP_MIN=0.15 by only 2/5 seeds -- so even with the sanity rail relaxed the tier would be "
        "MIDDLE_BAND, not HARD_PASS. "
        "ATTRIBUTION: HF_TEST_DESIGN_CALIBRATION (operating-point/sanity-floor incompatibility + over-"
        "optimistic magnitude bands), NOT HF_STRUCTURAL_BOUND. The substrate is not broken -- single-hop is "
        "above chance and the shuffled control collapses correctly; the sanity floor was set incompatibly "
        "with the discriminator regime. The mechanism DIRECTION (regen>analog above M/N~1, crossover below) "
        "is a robust, reproducible, well-controlled MEASURED phenomenon. "
        "DISPOSITION: MEASURED_MECHANISM (proven boundary): the digital-vs-analog repeater CROSSOVER at the "
        "M/N~1 Hebbian crosstalk threshold is real (5/5 seeds), with a bound that the effect is MODEST in "
        "absolute terms (regen_d5~0.26, not ~0.60) and DEPTH/LOAD-conditional. The cell's hypothesized "
        "HARD_PASS ('regen usable ~0.60 at depth 5') is REFUTED; the crossover phenomenon it discovered is "
        "affirmed. No prior CG/MM cert on this anchor -> no DEMOTE. MM +1 for the new measured phase-"
        "transition boundary + modest-magnitude bound + operating-point-incompatibility finding. "
        "RECALIBRATION RECOMMENDATION (worth re-running): the clean fix is to SCALE N UP (16384/32768) so "
        "that at the crossover M/N~1 single-hop d1 clears 0.85 while analog still collapses -- higher "
        "dimension sharpens the phase transition and could turn this modest-real into a genuine HARD_PASS. "
        "Alternatively make the SANITY floor regime-aware (lower to the achievable d1 at DISC M/N) AND "
        "recalibrate HP magnitude bands to the true ~0.26 level, reframing HARD_PASS on the RELATIVE gap + "
        "graceful-vs-catastrophic margin rather than absolute 'usability'."
    ),
    "aliases": ["regen_cleanup_vs_analog_accumulate_crossover_MEASURED_MECHANISM",
                "digital_vs_analog_repeater_MoverN_1_threshold_modest_real"],
    "metadata": {
        "record_class": "experiment_landed_vet_measured_mechanism_boundary",
        "term_class": "REASONING_DIGITAL_VS_ANALOG_REPEATER_CROSSOVER_HEBBIAN_CROSSTALK_THRESHOLD_MODEST_REAL",
        "cert_status": "proven_bound_measured_mechanism_modest_real_hard_fail_operating_point_incompatibility",
        "cert_class": "MEASURED_MECHANISM_regen_vs_analog_repeater_crossover_MoverN_1_graceful_vs_catastrophic_modest_magnitude",
        "cert_ts": TS_ISO,
        "verified_off_data": True,
        "verified_via": "independent re-execution of cell run_seed_mbg (seed7@8000, seed7@2000, seed23@8000), reproduced disk EXACTLY; not verdict-report",
        "atomized_by": "skunkworks_landed_VET_2026-07-05_regen_vs_analog_crossover",
        "anchor": "cortex_regenerative_cleanup_vs_analog_accumulate_v1",
        "cell_commit": "c65669c19",
        "raw_metrics_path": "data/exp_cortex_regenerative_cleanup_vs_analog_accumulate_v1/metrics.json",
        "run_mode": "full", "N": 8192, "V": 512, "P": 8,
        "n_seeds": 5, "seeds": [7, 17, 23, 31, 41], "cardinality_ok": True,
        "disk_verdict": "HARD_FAIL (5/5 seeds, SANITY_BREACH_d1)",
        "recompute_off_disk": {
            "seed7_at_8000": {"m_over_n": 1.105, "regen_d1": 0.7133, "analog_d1": 0.7133,
                              "regen_d5": 0.2200, "analog_d5": 0.0867, "gap": 0.1333,
                              "control_d5": 0.0067, "regen_faith_d5": 1.0},
            "seed7_at_2000": {"m_over_n": 0.372, "regen_d5": 0.2600, "analog_d5": 0.5333,
                              "gap": -0.2733, "note": "analog wins below capacity (crossover)"},
            "seed23_at_8000": {"m_over_n": 1.105, "regen_d5": 0.2600, "analog_d5": 0.0667, "gap": 0.1933},
            "aggregate_at_disc": {"mean_regen_d5": 0.2627, "mean_gap": 0.176, "std_gap": 0.050,
                                  "mean_control_d5": 0.0027, "n_crossover_confirmed": 5,
                                  "d1_all_seeds": [0.7133, 0.7533, 0.78, 0.7667, 0.7933]},
            "match_disk": "EXACT",
        },
        "hard_fail_root_cause": "SANITY_BREACH_d1 fires FIRST in classify_seed: SANITY_D1_MIN=0.85 unreachable at DISC M/N=1.10 (single-hop d1~0.71-0.79). Operating-point/sanity-floor INCOMPATIBILITY, not mechanism death.",
        "hard_fail_attribution": "HF_TEST_DESIGN_CALIBRATION (operating-point/sanity-floor incompatibility + over-optimistic HP magnitude bands HP_REGEN_D5_MIN=0.45 vs actual max 0.35, HP_GAP_MIN=0.15 met by 2/5), NOT HF_STRUCTURAL_BOUND",
        "honest_effect_size": "MODEST-REAL. Direction robust (5/5 regen>analog @DISC, gap widens with load); absolute magnitude MODEST regen_d5~0.263 (NOT the ~0.60 the small-seed probe reported; ~0.60 not reproduced at any M_BG in FULL). Downward correction ~2.3x on magnitude, but crossover phenomenon affirmed.",
        "positive_control_check": "shuffled control collapses to control_d5~0.0027 (~chance 1/512=0.00195) 5/5; single-hop above chance; substrate NOT broken; null is a real modest-magnitude bound not a broken PC.",
        "smoke_vs_full_note": "smoke N_TEST=48 vs full N_TEST=150 -> more chain-edges in W at full, so 'M_BG=8000' is M/N~1.02 (smoke) vs ~1.10 (full); combined with small-seed variance this explains part of the drop, but ~0.60 exceeds full's regen_d5 at EVERY M_BG (even lowest-load ~0.26) so the probe was genuinely over-optimistic.",
        "composes_with_atoms": [PRIOR_COT_META_ID],
        "composition_note": "COMPOSES WITH (does NOT supersede) the prior T3 META substrate-native chain-of-thought / per-hop lock-in-regeneration lineage (concept-overlap @0.26). Prior work showed per-hop regeneration RESETS noise and composes iterative cleanup to K<=4 at LOWER load / shallow depth (positive). This cell REFINES it: at ABOVE-capacity load (M/N~1.1) and DEPTH>=5 the SAME hard-regeneration is only MODEST (~0.26), and below capacity analog soft-carry actually beats it. Mild tension with the prior K<=4 optimism, resolved by regime: regen composes well shallow/low-load, degrades to modest deep/high-load.",
        "cross_arc_overlap_check_2026_07_01_USER_locked": "substrate_query 'regenerative cleanup digital repeater analog accumulate chain depth crosstalk Hebbian' -> top hits 0.26 (below 0.30 threshold): #2 meta T3 chain-of-thought iterative-cleanup atom, #4/#5 lock-in per-hop-regeneration notes. Conceptually related PRIOR lineage but below threshold; this is a TARGETED EXTENSION into the above-capacity regime + explicit analog-vs-regen crossover phase diagram, NOT a rediscovery. Composed above.",
        "framing_corrections_vs_director": "Director framed the question as 'band-calibration artifact (smoke bands too optimistic) vs true mechanism failure'. CORRECTION (load-bearing): the HARD_FAIL trigger is NEITHER of those directly -- it is the SANITY_D1_MIN=0.85 rail, which fires before any mechanism gate and is UNREACHABLE at the DISC operating point (M/N=1.10 -> d1~0.75). So it is an operating-point/sanity-floor incompatibility. Separately (and agreeing with Director's instinct) the HP magnitude bands ARE over-optimistic and the smoke's ~0.60 IS a small-seed over-estimate (true ~0.26). Both are true; the sanity-floor incompatibility is the proximate cause. Verdict: modest-REAL positive, not dead.",
        "revival_criteria": [
            "SCALE N UP (16384/32768) so at crossover M/N~1 single-hop d1>=0.85 while analog still collapses -> could promote modest-real to genuine HARD_PASS",
            "OR regime-aware SANITY floor (match achievable d1 at DISC M/N) + HP magnitude bands recalibrated to true ~0.26 + HARD_PASS reframed on relative gap / graceful-vs-catastrophic margin not absolute usability",
        ],
        "expansion_criterion": "PROMOTES toward CHAIN_GRADE iff the N-scaled re-run shows d1>=0.85 AND a robust regen>analog gap with regen_d5 usable at the crossover (>=0.45) across >=3 seeds. DEMOTES if the crossover fails to survive N-scaling (i.e. the modest gap was itself a small-N crosstalk artifact).",
        "disposition": "MEASURED_MECHANISM_digital_vs_analog_repeater_crossover_at_MoverN_1_is_REAL_5of5_but_MODEST_regen_d5_0p26_HARD_FAIL_is_operating_point_sanity_floor_incompatibility_not_mechanism_death_recalibrate_and_rerun_at_larger_N",
        "cert_increment_delta": 1,
    },
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


def ledger_append(atom, ledger_path=CERT_LEDGER):
    md = atom["metadata"]
    entry = {
        "ts": TS,
        "ts_iso": TS_ISO,
        "atom_id": atom["id"],
        "corpus": atom["corpus"],
        "tier": atom["tier"],
        "cert_status": md.get("cert_status"),
        "cert_class": md.get("cert_class"),
        "cert_increment_delta": md.get("cert_increment_delta", 0),
        "verified_off_data": True,
        "anchor": md.get("anchor"),
        "cell_commit": md.get("cell_commit"),
        "auditor": "skunkworks",
        "atomized_by": md.get("atomized_by"),
        "landed_VET_session": SESSION_TAG,
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

    n = a5_append(MATH_ATOMS, atom_schema)
    print(f"[atomize] (1) math MM_STANDARD schema-bundle-structural-transfer appended; math lines={n}")
    ledger_append(atom_schema)

    n = a5_append(MATH_ATOMS, atom_regen)
    print(f"[atomize] (2) math MEASURED_MECHANISM regen-vs-analog-crossover appended; math lines={n}")
    ledger_append(atom_regen)

    print("[atomize] DONE 2 atoms + 2 ledger entries; A5-gated (tmp+os.replace+verify-load+json-integrity); matching TS_ISO")
    print("[atomize] NET CERT DELTA: CG 0, MM +2 (schema MM_STANDARD +1, regen MEASURED_MECHANISM +1), HF 0")
