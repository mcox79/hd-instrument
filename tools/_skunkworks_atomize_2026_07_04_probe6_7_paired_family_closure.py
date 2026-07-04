"""
A5-gated atomization -- Skunkworks paired-confirmation family closure 2026-07-04.

Closes the Stage-1 regime-map MECHANISM-MODERATION CROSS-TERM family. Probe 1
(bf4408f2e) demoted; P8 demoted; P6v2 (TOPOLOGY-F x CLEANUP) and P7v2 (SCALE-N x
CLEANUP) were the two remaining members (already MIDDLE_BAND). This batch runs the
confirmatory PAIRED sweep on both and resolves them.

BATCH CONTENTS (2 atoms, matching TS_ISO):
  (1) math  MEASURED_MECHANISM  -- P6v2 + P7v2 family closure. The apparent
        mechanism-moderation (per_F/per_N mech-variance-in-band 0.07-0.18) is a
        TR60/TR100 UNPAIRED-salt sampling-noise artifact. Under PAIRED trials
        (shared salt across the 3 mechs per cell) the mech spread collapses to
        EXACTLY 0.0000 and argmax readout is bit-identical, on the exact
        non-saturated cliff regime the revival was DESIGNED to reveal an effect
        in. Extends the Probe 1 argmax-degeneracy MEASURED_MECHANISM to SHARDED
        + non-saturated cliff + TOPOLOGY-F and SCALE-N axes + L=2 and L=8.
        MM +1. Both probes MIDDLE_BAND -> MEASURED_MECHANISM (proven boundary).
  (2) meta  AMENDMENT -- annotates the paired-trials-MANDATORY meta-atom that the
        retroactive regime-map cross-term family is now FULLY swept (P1 demoted,
        P8 demoted, P6v2+P7v2 confirmed artifact by direct paired experiment).
        delta 0 (annotation of existing rule; not a new rule).

NET CERT DELTA (this batch): CG 0, MM +1, HF 0.
No DEMOTE: P6v2/P7v2 held no prior CG/MM cert (both MIDDLE_BAND on disk all seeds).

======================= INDEPENDENT RECOMPUTE EVIDENCE (Skunkworks, off-disk) =======================
Cells:
  experiments/_stage1_regime_probe_6_topology_x_cleanup_non_saturated_v1_core.py  (F x CLEANUP; L=2; TR=60)
  experiments/_stage1_regime_probe_7_N_x_cleanup_non_saturated_v1_core.py          (N x CLEANUP; L=8; TR=100)
Data: data/exp_stage1_regime_probe_{6,7}_..._s{7,13,19}/metrics.json (all MIDDLE_BAND on disk).
Primitives: experiments/_stage1_physics_law_joint_composition_factorial_v1_core.py::{build_rules,run_chain,cleanup_argmax_idx,phase_corrupt,cleanup_*}

REPRODUCE-CHECK (recompute stored band-restricted discriminator off raw phase_map):
  P6v2 max_per_F_mech_variance_in_band: recomp==stored, 3/3 seeds (s7 0.15, s13 0.15, s19 0.1833).
  P7v2 max_per_N_mech_variance_in_band + n_x_cleanup_max_abs_deviation_in_band: recomp==stored, 3/3 seeds
     (s7 0.07/0.14, s13 0.068/0.13, s19 0.11/0.15). max|recomp-stored| < 1e-4 all 6 seed-metrics.
  STRUCTURAL: ALL in-band cells sit at the SMALLEST N only (P6 N=512; P7 N=2048) -- the band opens
     only at the corruption cliff; higher N saturated (per_N_band_mean None for N>=4096). The MIDDLE_BAND
     verdicts were driven by the escapes-saturation gate FAIL (in-band fraction 0.10-0.19 < 0.30), not by
     decisive discriminator nullity; the discriminator itself (0.07-0.18) read as weak-moderate moderation.

SALT STRUCTURE (crux): both cells do salt += 1 per (mech, ...) grid tuple and seed gen with
  seed*100003 + salt. The 3 mechanisms at a given (F/N,M,corr) cell each get a DISTINCT seed =>
  independent codebook draws + independent per-step corruption realizations => the range of 3
  iid Binomial(TR,p)/TR draws is a NOISE FLOOR by construction. At acc~0.5, TR=60 -> expected
  3-draw range ~0.11; TR=100 -> ~0.085. Observed in-band spreads (0.03-0.18) sit right in that band.

PAIRED CONFIRMATION (Skunkworks re-run, CPU, seed_base=7, band-opening slice, cell L/TR + high-TR):
  Method: for each cell run the 3 mechs UNPAIRED (independent salt per mech) and PAIRED (ONE shared
  salt => identical items, identical fan-out path, identical per-step corruption draws; only cleanup
  differs). Cleanups are deterministic so RNG consumption is identical across mechs -> pairing is exact.

  P6v2  F x CLEANUP  (36-cell N=512 slice, L=2):
     UNPAIRED TR60:  max spread 0.1667  mean 0.0643   (reproduces stored floor 0.15-0.18)
     PAIRED   TR60:  max spread 0.0167  mean 0.0005   argmax-identical 35/36 cells
     UNPAIRED TR240: max 0.1125 mean 0.0332  (tracks floor DOWN; pure-noise predicts 0.0643*0.5=0.0322)
     PAIRED   TR240: max 0.0000 mean 0.0000   argmax-identical 36/36 cells
     control N=2048 saturated cells: spread 0 both ways (no signal to lose).
  P7v2  N x CLEANUP  (9-cell N=2048 slice, L=8):
     UNPAIRED TR100: max 0.0600 mean 0.0233   (consistent in magnitude with stored per-seed floors 0.07-0.11)
     PAIRED   TR100: max 0.0000 mean 0.0000   argmax-identical 9/9 cells
     UNPAIRED TR400: max 0.0400 mean 0.0106  (tracks floor DOWN; pure-noise predicts 0.0233*0.5=0.0117)
     PAIRED   TR400: max 0.0000 mean 0.0000   argmax-identical 9/9 cells
     control N=4096,16384 saturated cells: spread 0 both ways.

  => On BOTH probes, when the 3 mechanisms see IDENTICAL items+corruptions they produce EXACTLY equal
  accuracy (and bit-identical argmax readout) at the band-opening cliff. The entire apparent moderation
  was unpaired sampling noise; unpaired spread halves as TR quadruples (pure-noise signature); paired
  spread is exactly 0. Same result and same z-scale as Probe 1 (paired range 0, z=-8.88).

MECHANISTIC ROOT (argmax-invariance, same as Probe 1): chain readout is
  ci = argmax_j Re(Q_clean @ props[j].conj()). iterative_cosine returns the nearest codeword (= argmax);
  modern_hopfield returns cnorm(softmax(beta*sim) @ props) (argmax dominated by top entry); soft_energy
  returns cnorm(Q + alpha*(target-Q)) (a nudge preserving the argmax). At the cells' BETA=8.0 /
  ALPHA_SOFT=0.5 all three preserve the argmax index, so ACCURACY is mechanism-invariant even though the
  output VECTORS differ (arms_differ_verified passed on vector hashes: n_distinct_mechanisms=3 all seeds).
  The single P6 TR60 residual cell (F=16 M=800 c=0.85: 1 differing trial in 60, soft_energy) vanishes at
  TR240 -> degeneracy holds to within one boundary query, fully collapsing at higher TR.

POSITIVE-CONTROL CHECK (auditor discipline: PC clears its own floor first): SATURATION_PC acc=1.0
  pass=True all 6 seed-metrics; cardinality_ok=True; n_distinct_mechanisms=3. The discriminator was real
  and the arms genuinely differ on vectors; the null is a genuine argmax-degeneracy, not a broken PC or
  a by-construction saturation of the discriminator cell.

CROSS-ARC OVERLAP CHECK (USER-locked 2026-07-01): substrate_query top hit cosine 0.2988 (generic
  wordnet 'saturated'); substantive hit = prior READOUT_DEGENERATE->MEASURED_MECHANISM cross_layer_
  compose_LM_v2 precedent (~0.27, supports disposition); NONE > 0.30 duplicating this P6/P7 family closure.
  Targeted extension of the Probe 1 argmax-degeneracy MEASURED_MECHANISM, not a rediscovery.

FRAMING (symmetric): P6v2/P7v2 are NOT worthless -- the non-saturated revival correctly ESCAPED the
  Probe-3/Probe-2 saturation ceiling at the smallest N and produced a genuine measurable band; it just
  showed, decisively, that even in that band the mechanism cross-term is exactly 0 under pairing. The
  MIDDLE_BAND -> MEASURED_MECHANISM move is a PROMOTION of certainty (unresolved -> proven-absent), not
  a demotion of a claimed effect.
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

P6_ANCHOR = "stage1_regime_probe_6_topology_x_cleanup_non_saturated_v1"
P7_ANCHOR = "stage1_regime_probe_7_N_x_cleanup_non_saturated_v1"
P6_METRICS = [f"data/exp_{P6_ANCHOR}_s{s}/metrics.json" for s in (7, 13, 19)]
P7_METRICS = [f"data/exp_{P7_ANCHOR}_s{s}/metrics.json" for s in (7, 13, 19)]

PAIRED_TRIALS_META_ID = ("meta::T4/META_paired_trials_MANDATORY_for_arm_comparison_max_or_range_discriminators_unpaired_independent_salts_MANUFACTURE_phantom_cross_terms_shared_items_corruptions_across_arms_OR_data_driven_binomial_extreme_value_null_REQUIRED_at_prereg_case_study_Probe1_storage_x_cleanup_TR100_unpaired_range_0p10_looked_like_moderation_paired_TR400_range_EXACTLY_0_z_neg8p88_retroactive_to_regime_map_cross_term_family_P1_P6_P7_P8_promotes_P8_extreme_value_null_meta_MM_STANDARD_2026-07-04")
PROBE1_MEASURED_MECHANISM_ID = ("math::SPLIT_stage1_regime_map_storage_x_cleanup_MEASURED_MECHANISM_three_cleanup_mechanisms_are_ARGMAX_DEGENERATE_for_index_readout_in_BUNDLED_paired_TR400_range_EXACTLY_0p0000_all_36_cells_z_neg8p88_modern_hopfield_iterative_cosine_soft_energy_attractor_produce_bit_identical_accuracy_on_identical_items_corruptions_because_readout_is_argmax_ReQ_clean_props_conj_output_vectors_differ_but_argmax_indices_do_not_cross_term_provably_absent_2026-07-04")

atom_1_family_closure = {
    "id": "math::MEASURED_MECHANISM_stage1_regime_map_PROBE6_TOPOLOGY_F_x_CLEANUP_and_PROBE7_SCALE_N_x_CLEANUP_non_saturated_cliff_mechanism_moderation_is_a_PAIRED_TRIAL_ARTIFACT_family_closure_3seed_FULL_MIDDLE_BAND_to_MEASURED_MECHANISM_stored_per_F_var_in_band_0p15_0p15_0p1833_per_N_var_in_band_0p07_0p068_0p11_reproduced_off_disk_exactly_all_inband_cells_at_smallest_N_only_P6_N512_P7_N2048_UNPAIRED_salt_noise_floor_P6_TR60_max0p1667_mean0p0643_tracks_down_TR240_max0p1125_P7_TR100_max0p06_tracks_down_TR400_max0p04_PAIRED_shared_salt_range_EXACTLY_0p0000_both_probes_argmax_identical_P6_36of36_at_TR240_P7_9of9_extends_Probe1_argmax_degeneracy_to_SHARDED_nonsat_cliff_F_and_N_axes_L2_and_L8_2026-07-04",
    "name": "MATH regime-map family closure: P6v2 (TOPOLOGY-F x CLEANUP) + P7v2 (SCALE-N x CLEANUP) mechanism-moderation cross-terms are PAIRED-TRIAL ARTIFACTS. Paired shared-salt spread EXACTLY 0.0000 with bit-identical argmax on the non-saturated cliff both probes; MIDDLE_BAND -> MEASURED_MECHANISM. Extends Probe 1 argmax-degeneracy to SHARDED + F/N axes.",
    "corpus": "math",
    "tier": "T3",
    "kind": "experiment_record_measured_mechanism_boundary",
    "description": (
        "MEASURED_MECHANISM proven boundary closing the Stage-1 regime-map MECHANISM-MODERATION cross-term "
        "family (Probe 1 demoted bf4408f2e; Probe 8 demoted; P6v2 + P7v2 resolved here). Both probes were "
        "MIDDLE_BAND on disk all 3 seeds; this confirmatory PAIRED sweep resolves them to a proven boundary: "
        "the CLEANUP_MECHANISM cross-term is PROVABLY ABSENT for accuracy readout, not merely unproven. "
        "REPRODUCE-CHECK (off raw phase_map, all 6 seed-metrics): P6v2 max_per_F_mech_variance_in_band "
        "recomp==stored (0.15/0.15/0.1833); P7v2 max_per_N_mech_variance_in_band + max_abs_dev recomp==stored "
        "(0.07-0.11 / 0.13-0.15); max|recomp-stored|<1e-4. STRUCTURAL: every in-band cell sits at the SMALLEST "
        "N only (P6 N=512, P7 N=2048) -- the band opens only at the corruption cliff, higher N saturated. The "
        "MIDDLE_BAND verdicts came from the escapes-saturation gate FAIL (in-band frac 0.10-0.19 < 0.30), not "
        "decisive nullity; the discriminator (0.07-0.18) read as weak-moderate moderation. "
        "SALT STRUCTURE: both cells salt+=1 per grid tuple and seed gen=seed*100003+salt, so the 3 mechanisms "
        "per cell get DISTINCT seeds => independent items+corruptions => the range of 3 iid Binomial(TR,p)/TR "
        "draws is a noise floor by construction (~0.11 at TR60/acc0.5, ~0.085 at TR100). Observed in-band "
        "spreads land in that band; stored max-spread cells show one mechanism as an outlier (classic unpaired "
        "lucky-draw signature, e.g. P7 s19 N2048 M800 c0.92 accs [0.69,0.68,0.83]). "
        "PAIRED CONFIRMATION (Skunkworks re-run, seed_base=7, band-opening slice, shared salt so all 3 mechs "
        "see identical items + identical per-step corruption): "
        "P6v2 (F x CLEANUP, 36-cell N=512 slice, L=2): UNPAIRED TR60 max 0.1667 mean 0.0643 (reproduces stored "
        "floor); PAIRED TR60 max 0.0167 mean 0.0005 argmax-identical 35/36; UNPAIRED TR240 max 0.1125 mean "
        "0.0332 (tracks floor down, pure-noise predicts 0.0322); PAIRED TR240 max 0.0000 mean 0.0000 argmax-"
        "identical 36/36. "
        "P7v2 (N x CLEANUP, 9-cell N=2048 slice, L=8): UNPAIRED TR100 max 0.0600 mean 0.0233; PAIRED TR100 max "
        "0.0000 mean 0.0000 argmax-identical 9/9; UNPAIRED TR400 max 0.0400 mean 0.0106 (tracks floor down, "
        "predicts 0.0117); PAIRED TR400 max 0.0000 mean 0.0000 argmax-identical 9/9. "
        "Saturated control cells (P6 N=2048; P7 N=4096/16384): spread 0 both ways. "
        "So on BOTH probes the paired spread is EXACTLY 0 at the non-saturated cliff the revival was DESIGNED "
        "to expose an effect in; unpaired spread halves as TR quadruples (pure-noise signature). Same result "
        "and z-scale as Probe 1 (paired range 0, z=-8.88). "
        "MECHANISTIC ROOT (argmax-invariance): readout ci = argmax_j Re(Q_clean @ props[j].conj()); all 3 "
        "mechanisms preserve the argmax index at BETA=8.0/ALPHA_SOFT=0.5, so accuracy is mechanism-invariant "
        "even though the output VECTORS differ (arms_differ_verified passed on vector hashes, n_distinct=3 all "
        "seeds). The lone P6 TR60 residual cell (F=16 M=800 c=0.85: 1 differing trial/60, soft_energy) vanishes "
        "at TR240 -> degeneracy holds to within one boundary query. "
        "EXTENSION (why this earns +1, not a duplicate of Probe 1): Probe 1 proved argmax-degeneracy at "
        "BUNDLED (capacity-limited low-acc); this proves it at SHARDED at the NON-SATURATED CLIFF -- the regime "
        "specifically engineered to give mechanism variance room to appear -- across the TOPOLOGY (F in "
        "{1,4,8,16}) and SCALE (N cliff) axes at both L=2 and L=8. The specifically-designed revival attempt "
        "is closed. "
        "DISPOSITION: MIDDLE_BAND -> MEASURED_MECHANISM (promotion of certainty, not demotion of an effect); "
        "no prior CG/MM cert existed for either probe so no DEMOTE. "
        "REVIVAL: the ACCURACY cross-term is CLOSED for this family (paired range provably 0). A non-argmax "
        "discriminator (cleaned-vector margin / energy / calibration) or a very-low-beta regime at TR>=400 "
        "PAIRED would be required to revive any mechanism-axis claim."
    ),
    "aliases": ["regime_probe_6_7_paired_family_closure",
                "topology_F_scale_N_x_cleanup_argmax_degenerate_nonsat"],
    "metadata": {
        "record_class": "experiment_measured_mechanism_family_closure",
        "term_class": "STAGE1_REGIME_MAP_MECHANISM_MODERATION_CROSS_TERM_FAMILY_CLOSURE_PAIRED_TRIAL",
        "cert_status": "measured_mechanism_cross_term_provably_absent_paired_trial",
        "cert_class": "MEASURED_MECHANISM_argmax_degeneracy_nonsat_cliff_paired_confirmation_P6_P7",
        "cert_ts": TS_ISO,
        "verified_off_data": True,
        "atomized_by": "skunkworks_landed_VET_2026-07-04_probe6_7_paired_family_closure",
        "probes": ["P6v2", "P7v2"],
        "prior_verdict_both": "MIDDLE_BAND (all 3 seeds, escapes-saturation gate fail)",
        "raw_metrics_paths": {"P6v2": P6_METRICS, "P7v2": P7_METRICS},
        "cell_source_paths": [f"experiments/_{P6_ANCHOR}_core.py", f"experiments/_{P7_ANCHOR}_core.py"],
        "primitive_source": "experiments/_stage1_physics_law_joint_composition_factorial_v1_core.py::{build_rules,run_chain,cleanup_argmax_idx}",
        "n_seeds": 3, "seeds": [7, 13, 19],
        "reproduce_check": {
            "P6v2_max_per_F_mech_variance_in_band": {"stored": {"7": 0.15, "13": 0.15, "19": 0.1833},
                                                     "recomputed_off_disk": {"7": 0.15, "13": 0.15, "19": 0.1833},
                                                     "match": True},
            "P7v2_max_per_N_mech_variance_in_band": {"stored": {"7": 0.07, "13": 0.068, "19": 0.11},
                                                     "recomputed_off_disk": {"7": 0.07, "13": 0.068, "19": 0.11},
                                                     "match": True},
            "P7v2_n_x_cleanup_max_abs_deviation_in_band": {"stored": {"7": 0.14, "13": 0.13, "19": 0.15},
                                                           "recomputed_off_disk": {"7": 0.14, "13": 0.13, "19": 0.15},
                                                           "match": True},
            "all_inband_cells_at_smallest_N_only": {"P6v2": 512, "P7v2": 2048},
        },
        "paired_confirmation": {
            "method": "shared salt across 3 mechs per cell => identical items + identical per-step corruption; cleanups deterministic so RNG consumption identical -> exact pairing",
            "P6v2": {"slice": "N=512 band-opening, 36 cells, L=2",
                     "unpaired_TR60": {"max": 0.1667, "mean": 0.0643},
                     "paired_TR60": {"max": 0.0167, "mean": 0.0005, "argmax_identical_cells": "35/36"},
                     "unpaired_TR240": {"max": 0.1125, "mean": 0.0332, "pure_noise_predict_mean": 0.0322},
                     "paired_TR240": {"max": 0.0, "mean": 0.0, "argmax_identical_cells": "36/36"},
                     "control_N2048_saturated_spread": {"unpaired": 0.0, "paired": 0.0}},
            "P7v2": {"slice": "N=2048 band-opening, 9 cells, L=8",
                     "unpaired_TR100": {"max": 0.06, "mean": 0.0233},
                     "paired_TR100": {"max": 0.0, "mean": 0.0, "argmax_identical_cells": "9/9"},
                     "unpaired_TR400": {"max": 0.04, "mean": 0.0106, "pure_noise_predict_mean": 0.0117},
                     "paired_TR400": {"max": 0.0, "mean": 0.0, "argmax_identical_cells": "9/9"},
                     "control_N4096_16384_saturated_spread": {"unpaired": 0.0, "paired": 0.0}},
            "conclusion": "paired spread EXACTLY 0 both probes; unpaired halves as TR quadruples (pure-noise signature); apparent moderation was 100% unpaired sampling noise",
        },
        "mechanistic_root": "ci=argmax_j Re(Q_clean @ props[j].conj()); 3 mechanisms argmax-equivalent at BETA=8.0/ALPHA_SOFT=0.5 -> accuracy mechanism-invariant; output vectors differ (arms_differ passed) but argmax indices do not",
        "positive_control": "SATURATION_PC acc=1.0 pass=True all 6 seed-metrics; cardinality_ok=True; n_distinct_mechanisms=3 all seeds (discriminator real, arms genuinely differ on vectors, null is genuine degeneracy not broken PC / by-construction saturation)",
        "extends_atom": PROBE1_MEASURED_MECHANISM_ID,
        "extension_scope": "Probe 1 proved argmax-degeneracy at BUNDLED; this extends it to SHARDED at the NON-SATURATED CLIFF (the revival-designed regime) across TOPOLOGY-F {1,4,8,16} and SCALE-N cliff axes at L=2 and L=8",
        "composes_with_atoms": [PAIRED_TRIALS_META_ID,
                                "meta::T4/META_extreme_value_null_calibration (P8)"],
        "revival_criteria": ["accuracy cross-term CLOSED (paired range provably 0)",
                             "non-argmax discriminator (cleaned-vector margin/energy/calibration) or very-low-beta at TR>=400 PAIRED required to revive a mechanism-axis claim"],
        "cross_arc_overlap_check_2026_07_01_USER_locked": "substrate_query top hit cosine 0.2988 generic wordnet 'saturated'; substantive hit prior READOUT_DEGENERATE->MEASURED_MECHANISM precedent ~0.27 supports disposition; NONE >0.30 duplicating; targeted extension not rediscovery",
        "framing_symmetric": "P6v2/P7v2 not worthless: the revival correctly escaped the Probe2/Probe3 saturation ceiling at smallest N and produced a genuine measurable band; it proved the cross-term is 0 even there. MIDDLE_BAND->MEASURED_MECHANISM is a promotion of certainty, not demotion of an effect.",
        "cert_increment_delta": 1,
    }
}

atom_2_meta_family_swept = {
    "id": "meta::AMEND_META_paired_trials_MANDATORY_regime_map_cross_term_family_NOW_FULLY_SWEPT_P1_DEMOTED_P8_DEMOTED_P6v2_P7v2_CONFIRMED_ARTIFACT_by_direct_paired_experiment_all_four_members_resolved_paired_shared_salt_spread_EXACTLY_0_argmax_degenerate_the_retroactive_conjecture_near_certain_same_artifact_is_now_PROVEN_on_both_remaining_members_at_the_non_saturated_cliff_2026-07-04",
    "name": "META AMENDMENT: the regime-map mechanism-moderation cross-term family is now FULLY SWEPT -- P1 demoted, P8 demoted, P6v2+P7v2 confirmed artifact by direct paired experiment (paired spread EXACTLY 0 both). The paired-trials meta's 'near-certain same artifact' conjecture for P6v2/P7v2 is now PROVEN.",
    "corpus": "meta",
    "tier": "T4",
    "kind": "methodology_rule_amendment",
    "description": (
        "AMENDS the paired-trials-MANDATORY meta-atom (does NOT supersede it). That rule's "
        "retroactive_scope listed [P1, P6v2, P7v2, P8] and flagged P6v2/P7v2 as 'near-certain same "
        "artifact'. This amendment records that the conjecture is now DIRECTLY PROVEN: the confirmatory "
        "PAIRED sweep on both remaining members (Skunkworks 2026-07-04) gives paired shared-salt mechanism "
        "spread EXACTLY 0.0000 with bit-identical argmax readout on the exact non-saturated cliff regime the "
        "revival was designed to reveal an effect in (P6v2 F x CLEANUP 36-cell N=512 slice L=2, argmax-"
        "identical 36/36 at TR240; P7v2 N x CLEANUP 9-cell N=2048 slice L=8, argmax-identical 9/9). "
        "FAMILY STATUS (all 4 members resolved): P1 STORAGE x CLEANUP CG_META -> DEMOTED (paired range 0, "
        "z=-8.88); P8 F-ALGEBRA x CLEANUP MM_STANDARD -> DEMOTED to MIDDLE_BAND (extreme-value null z=0.40); "
        "P6v2 TOPOLOGY-F x CLEANUP MIDDLE_BAND -> MEASURED_MECHANISM (paired artifact); P7v2 SCALE-N x CLEANUP "
        "MIDDLE_BAND -> MEASURED_MECHANISM (paired artifact). Across STORAGE, TOPOLOGY-F, SCALE-N, and "
        "F-ALGEBRA moderator axes, at BUNDLED and SHARDED, saturated and non-saturated, L in {2,8}, the "
        "3 cleanup mechanisms {modern_hopfield, iterative_cosine, soft_energy_attractor} are argmax-degenerate "
        "for index readout; NO mechanism-moderation cross-term survives a paired-trial test. "
        "IMPLICATION for the rule: the paired-trials-MANDATORY SCHEMA-VET gate is now empirically validated by "
        "a COMPLETE family sweep (4/4 members), strengthening the case for its CG_META promotion when wired "
        "into SCHEMA-VET as a hard reject. No new rule; the parent rule's evidential base is upgraded from "
        "'2 catches + 1 conjecture pair' to '4/4 family members resolved by paired experiment'."
    ),
    "aliases": ["regime_map_cross_term_family_fully_swept",
                "paired_trials_family_closure_P1_P6_P7_P8"],
    "metadata": {
        "verified_off_data": True,
        "verified_ts": TS_ISO,
        "verifier": "hdi_skunkworks",
        "cert_status": "mm_standard_methodology_rule_amendment_family_complete",
        "cert_class": "AMEND_META_paired_trials_regime_map_family_fully_swept",
        "amends_atom": PAIRED_TRIALS_META_ID,
        "action": "AMEND",
        "family_status": {
            "P1_storage_x_cleanup": "DEMOTED CG_META (paired range 0, z=-8.88)",
            "P8_F_algebra_x_cleanup": "DEMOTED MM_STANDARD->MIDDLE_BAND (extreme-value null z=0.40)",
            "P6v2_topology_F_x_cleanup": "MIDDLE_BAND->MEASURED_MECHANISM (paired artifact, argmax-identical 36/36 TR240)",
            "P7v2_scale_N_x_cleanup": "MIDDLE_BAND->MEASURED_MECHANISM (paired artifact, argmax-identical 9/9)",
        },
        "family_resolved_count": "4/4",
        "composes_with_atoms": [PAIRED_TRIALS_META_ID, atom_1_family_closure["id"]],
        "promotion_note": "parent paired-trials rule evidential base upgraded to complete family sweep; supports CG_META promotion when wired into SCHEMA-VET hard-reject",
        "cross_arc_overlap_check_2026_07_01_USER_locked": "amends existing paired-trials meta; annotation of completed family sweep; not a new rule; delta 0",
        "cert_increment_delta": 0,
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


def ledger_append(atom, session_tag, extra=None, ledger_path=CERT_LEDGER):
    entry = {
        "ts": TS,
        "ts_iso": TS_ISO,
        "atom_id": atom["id"],
        "corpus": atom["corpus"],
        "cert_status": atom["metadata"].get("cert_status"),
        "cert_class": atom["metadata"].get("cert_class"),
        "cert_increment_delta": atom["metadata"].get("cert_increment_delta", 0),
        "verified_off_data": True,
        "atomized_by": "skunkworks_landed_VET_2026-07-04_probe6_7_paired_family_closure",
        "landed_VET_session": session_tag,
    }
    if extra:
        entry.update(extra)
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
    tag = "2026-07-04_probe6_7_paired_family_closure"

    n = a5_append(MATH_ATOMS, atom_1_family_closure)
    print(f"[atomize] (1) math MEASURED_MECHANISM P6v2+P7v2 family closure appended; math lines={n}")
    ledger_append(atom_1_family_closure, tag)

    n = a5_append(META_ATOMS, atom_2_meta_family_swept)
    print(f"[atomize] (2) meta AMENDMENT family-fully-swept appended; meta lines={n}")
    ledger_append(atom_2_meta_family_swept, tag,
                  extra={"amends_atom": PAIRED_TRIALS_META_ID, "action": "AMEND"})

    print("[atomize] DONE 2 atoms + 2 ledger entries; A5-gated (tmp+os.replace+verify-load+json-integrity); matching TS_ISO")
    print("[atomize] NET CERT DELTA: CG 0, MM +1 (family-closure MEASURED_MECHANISM), HF 0; meta amendment delta 0")
