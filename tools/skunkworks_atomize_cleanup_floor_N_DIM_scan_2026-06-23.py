"""Skunkworks cert-routing: cleanup_floor_N_DIM_scan_v1 (META-INFORMER branch (a)).

Closes / clarifies branch (a) N_DIM-scan of the parent Shannon-floor super-META
(T3/META_cleanup_ceiling_shannon_floor_substrate_operating_envelope_sigma_leq_1p0_
2026-06-23 at cert_ledger row 675). Sibling to cleanup_floor_M_scan_v1 (row 676)
which closed branch (b) at macro level.

LANDING: cleanup_floor_N_DIM_scan_v1
  - LOCAL CPU; FULL 3 seeds (7, 17, 23); 2.44 s wall; M=200 N_EVAL=200
    ARGMAX_BASELINE only; random bipolar codebook L2-normalized
  - N_DIM_sweep [512, 1024, 2048, 4096, 8192, 16384] x sigma_sweep [1.0, 1.5, 2.0]
  - cell verdict: META_DECISION_N_INDEPENDENT

PER-CELL (mean across 3 seeds, Fix #28 verified directly from detail.agg[N][sigma]):
  N=  512  sigma=1.0  recall=0.0550  cv=0.074  per_seed [0.05, 0.06, 0.055]
  N= 1024  sigma=1.0  recall=0.0450  cv=0.240
  N= 2048  sigma=1.0  recall=0.0533  cv=0.044
  N= 4096  sigma=1.0  recall=0.0567  cv=0.333
  N= 8192  sigma=1.0  recall=0.0583  cv=0.283  (sigma=1.0 PEAK; per_seed [0.055, 0.080, 0.040])
  N=16384  sigma=1.0  recall=0.0417  cv=0.150

  N=  512  sigma=1.5  recall=0.0217  cv=0.218  per_seed [0.015, 0.025, 0.025]
  N= 1024  sigma=1.5  recall=0.0350  cv=0.117  per_seed [0.040, 0.035, 0.030]  (sigma=1.5 PEAK)
  N= 2048  sigma=1.5  recall=0.0283  cv=0.363
  N= 4096  sigma=1.5  recall=0.0233  cv=0.364  (matches prior ENC1 datapoint 0.027)
  N= 8192  sigma=1.5  recall=0.0233  cv=0.440  (highest CV; per_seed [0.025, 0.010, 0.035])
  N=16384  sigma=1.5  recall=0.0217  cv=0.288

  All N at sigma=2.0: recall in [0.013, 0.030]; all below 0.05
  Sanity sigma=0.0 ALL N: recall=1.000 (clean across all 18 cells)

FIX #28 CORRECTION TO DIRECTOR FRAMING:
  Director's framing said "Recall is HIGHEST at N=512". This is INCORRECT at
  sigma=1.5: peak is at N_DIM=1024 (0.0350), NOT N=512 (0.0217).
  At sigma=1.0 the peak is at N=8192 (0.0583), NOT N=512 (0.0550).
  N=512 is NEVER the peak at any sigma. Verified directly off agg[N][sigma].mean.
  The macro conclusion N-INDEPENDENT stands (all values < 0.05 floor at sigma=1.5
  and all values < 0.06 floor at sigma=1.0, well under HARD_FAIL=0.10 threshold)
  but the FRAMING was wrong; this atomization captures the correct per-cell
  numbers off-data per Fix #28 (verdict_msg framing != per-arm reality).

META BRANCH-TRACKER STATE AFTER THIS ATOM:
  Parent META (cert_ledger row 675) has 3 still-open branches:
    (a) N_DIM-scan: CLOSED HERE at macro decision level (this atom)
    (b) M-scan: CLOSED at macro level (cert_ledger row 676; sibling MM)
    (c) learned-encoder keys (Foldiak / anti-Hebb / Krotov / BTSP / contrastive):
        STILL OPEN; substrate-product-relevant (char_trigram, BGE, k-WTA-VQ)

CERT-OWNER TIER DECISION: MEASURED_MECHANISM (delta=0)

  OVERRIDE OF DIRECTOR CHAIN-GRADE-UPGRADE-NOW ARGUMENT:
  Director argued 2/3 branch closure + 9-family exhaustion + sanity-clean
  implementation is enough to upgrade parent META to chain-grade. The cert-
  owner disagrees and HOLDS parent META at MM until branch (c) closes. Reasons:

  1. by-construction-saturation: at sigma=1.5 with random bipolar codebook
     M=200, recall IS at the synthetic information-theory floor. Increasing
     N_DIM does not introduce signal where there is none; the discriminator
     CANNOT fire above 0.05 at this regime because the random codebook is
     isotropic-in-expectation and the noise process at sigma=1.5 fully
     dominates the cosine-similarity readout. The 'cell cannot fail' regime
     of by-construction-saturation tiering applies: N-independence is
     predicted by the analytic floor; the cell measured the floor cleanly
     but did not measure a discriminating regime.

  2. Random-bipolar codebook is NOT the substrate-product regime: real cells
     use char_trigram_encoder, BGE projection, k-WTA-VQ-encoded keys,
     Path-A encoders. These are ANISOTROPIC and STRUCTURED, exactly the
     regime that branch (c) would test. Without testing branch (c), the
     Shannon-floor framing applies ONLY to random-codebook-test-regime,
     not to substrate-product-regime. The encoder-bound META at row 674
     already established cleanup ceiling is encoder-bound; closing branch
     (c) is the substantive test.

  3. 2/3 branches closed is structurally similar evidence (same axis family):
     both (a) and (b) sweep codebook-cardinality parameters (N_DIM = key
     dimension; M = codebook size). Both confirm the codebook-scale-
     independence of the noise floor. Branch (c) tests the codebook-STRUCTURE
     question, which is qualitatively different evidence.

  4. Fix #28 default under-claim discipline: a chain-grade upgrade should
     wait for the actually-load-bearing branch (c) closure rather than
     extrapolate from the codebook-scale evidence alone. The parent META's
     SCOPE is correctly captured as 'random-codebook Shannon-floor at
     M=200 N_DIM in [512, 16384] sigma=1.5' which is what HAS been measured;
     calling this 'chain-grade substrate operating envelope' before testing
     the encoder-structured regime is overclaiming.

  CERT-OWNER UPGRADE TRIGGER for parent META -> chain-grade: branch (c)
  closes as either (i) learned encoders DO escape Shannon-floor (negative
  result for current META; parent META should be REVISED, not upgraded)
  OR (ii) learned encoders also fail at sigma=1.5 random-target task,
  confirming the floor applies to substrate-product regime too. Either
  outcome makes the META scope-clear; only outcome (ii) qualifies for
  chain-grade upgrade and even then under the encoder-structured regime
  not the abstract 'substrate operating envelope' framing.

DISCIPLINES HONORED:
  - Fix #28: per-arm + per-seed metrics read directly from agg[N][sigma];
    Director framing "highest at N=512" CORRECTED (peak at sigma=1.5 is
    N=1024, peak at sigma=1.0 is N=8192).
  - by-construction-saturation tiering: random-bipolar at synthetic floor;
    HOLD parent META at MM until branch (c) tests structured/anisotropic regime.
  - Default under-claim per Fix #28
  - Cert-owner override of Director recommendation (independent audit)
  - A5 PRE/POST snapshot across writes
  - Snapshot-before-mass-mutation: parent META NOT mutated; layer evidence
    via fresh composable MM atom
  - Idempotency: skip atoms already in Store
  - Foreground execution (Fix #20)
  - ASCII-only
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(".").resolve()))
from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier
from tools.cert_ledger_writer import (
    append_cert_ledger_row,
    build_measured_mechanism_row,
)


STORE_ROOT = Path("data/substrate_index")
ATOMIZED_BY = "skunkworks_atomize_cleanup_floor_N_DIM_scan_2026-06-23"


def build_N_DIM_scan_mm() -> Atom:
    return Atom(
        id="T3/EXP_cleanup_floor_N_DIM_scan_v1_MM",
        name=(
            "cleanup floor N_DIM-scan (N_DIM=512..16384) at sigma=1.5 -- "
            "MEASURED_MECHANISM (FULL 3 seeds; N-INDEPENDENT at macro decision "
            "level; closes branch (a) of parent Shannon-floor META; cert-owner "
            "OVERRIDES Director chain-grade-upgrade arg; HOLD parent META at MM "
            "until branch (c) learned-encoder tests)"
        ),
        description=(
            "META-INFORMER cell for parent Shannon-floor super-META "
            "T3/META_cleanup_ceiling_shannon_floor_substrate_operating_envelope_"
            "sigma_leq_1p0_2026-06-23 (cert_ledger row 675). Sibling to the "
            "cleanup_floor_M_scan_v1 MM atom at cert_ledger row 676 which closed "
            "branch (b). This atom closes branch (a) N_DIM-scan at macro decision "
            "level.\n\n"
            "Setup: M=200, ARGMAX_BASELINE arm only (random bipolar codebook "
            "L2-normalized; no encoder; substrate-only). N_DIM-sweep [512, 1024, "
            "2048, 4096, 8192, 16384] x sigma-sweep [1.0, 1.5, 2.0] x 3 seeds "
            "(7, 17, 23) x N_EVAL=200. LOCAL CPU; FULL run; wall 2.44 s.\n\n"
            "PER-CELL at sigma=1.5 (mean across 3 seeds, Fix #28 verified from "
            "detail.agg[N_DIM][sigma]):\n"
            "  N=  512  recall=0.0217  cv=0.218  per_seed [0.015, 0.025, 0.025]\n"
            "  N= 1024  recall=0.0350  cv=0.117  per_seed [0.040, 0.035, 0.030]  PEAK\n"
            "  N= 2048  recall=0.0283  cv=0.363  per_seed [0.040, 0.015, 0.030]\n"
            "  N= 4096  recall=0.0233  cv=0.364  (matches prior ENC1 datapoint 0.027)\n"
            "  N= 8192  recall=0.0233  cv=0.440  per_seed [0.025, 0.010, 0.035]\n"
            "  N=16384  recall=0.0217  cv=0.288\n\n"
            "PER-CELL at sigma=1.0:\n"
            "  N=  512  recall=0.0550 cv=0.074\n"
            "  N= 1024  recall=0.0450 cv=0.240\n"
            "  N= 2048  recall=0.0533 cv=0.044\n"
            "  N= 4096  recall=0.0567 cv=0.333\n"
            "  N= 8192  recall=0.0583 cv=0.283  PEAK\n"
            "  N=16384  recall=0.0417 cv=0.150\n\n"
            "All sigma=2.0 values fall in [0.013, 0.030]; sanity sigma=0.0 ALL "
            "18 cells: recall=1.000 (implementation clean).\n\n"
            "FIX #28 CORRECTION TO DIRECTOR FRAMING:\n"
            "Director's spawn brief asserted 'Recall is HIGHEST at N=512 not "
            "RISING with N -- concentration-of-measure prediction FALSIFIED "
            "empirically'. At sigma=1.5 (the discriminator sigma), peak is "
            "actually N=1024 (0.0350), NOT N=512 (0.0217). At sigma=1.0 the "
            "peak is N=8192 (0.0583), NOT N=512 (0.0550). N=512 is NEVER the "
            "peak at any sigma. The macro conclusion N-INDEPENDENT stands (all "
            "values < 0.05 floor at sigma=1.5 and all < 0.06 at sigma=1.0; all "
            "well below HARD_FAIL=0.10 threshold) so the META-DECISION is "
            "correct in spirit, but the per-cell PEAK framing was wrong. This "
            "atom captures the correct per-cell numbers off-data per Fix #28 "
            "(verdict_msg framing != per-arm reality).\n\n"
            "N-SCAN DECISION at discriminator sigma=1.5: no N_DIM in the sweep "
            "[512, 16384] crosses the 0.20 HARD_PASS cleanup-ceiling. Knee at "
            "0.20 = None. recall(N=8192)=0.0233, recall(N=16384)=0.0217; both "
            "well below 0.10 HARD_FAIL_floor threshold of the parent META. The "
            "Shannon-floor regime is N-INDEPENDENT in the swept N_DIM-range at "
            "the macro decision level under bipolar codebook.\n\n"
            "RELATION TO PARENT META AT LEDGER ROW 675:\n"
            "The parent META was atomized with 3 still-open branches: (a) "
            "N_DIM-scan, (b) different M, (c) learned-encoder keys. Branch (b) "
            "closed at macro level in sibling MM at row 676. This atom closes "
            "branch (a) at macro level. Branch (c) remains OPEN and is the "
            "substrate-product-relevant test (real cells use char_trigram, BGE, "
            "k-WTA-VQ encoded keys, Path-A encoders -- all ANISOTROPIC and "
            "STRUCTURED, qualitatively different from the random-bipolar regime "
            "tested in branches a + b). The parent META is NOT mutated in-place "
            "(cert-owner snapshot-before-mass-mutation discipline); strengthening "
            "evidence layers via composes_with on this fresh MM atom rather than "
            "retroactive metadata edits.\n\n"
            "CERT-OWNER OVERRIDE OF DIRECTOR CHAIN-GRADE-UPGRADE-NOW ARGUMENT:\n"
            "Director argued 2/3 branch closure + 9-family exhaustion + sanity-"
            "clean implementation is enough to upgrade parent META from MM to "
            "chain-grade. Cert-owner HOLDS at MM. Four reasons:\n"
            "  1. by-construction-saturation: random-bipolar at sigma=1.5 M=200 "
            "is the SYNTHETIC information-theory floor. Increasing N_DIM does "
            "not introduce signal where there is none; isotropic codebook + "
            "noise at sigma=1.5 fully dominates the cosine readout. The cell "
            "CANNOT fail above 0.05 at this regime because the analytic floor "
            "predicts it. 'Cell cannot fail' regime of by-construction-saturation "
            "tiering applies; cleanly measured floor != chain-grade evidence.\n"
            "  2. Random-bipolar is NOT the substrate-product regime. Real cells "
            "use anisotropic structured keys. Branch (c) is the substantive test. "
            "Shannon-floor framing currently applies ONLY to "
            "random-codebook-test-regime, not substrate-product-regime.\n"
            "  3. Branches (a) and (b) are structurally similar evidence "
            "(codebook-scale-axes: N_DIM = key dimension, M = codebook size). "
            "Both confirm codebook-SCALE-independence. Branch (c) tests "
            "codebook-STRUCTURE-independence, which is qualitatively different.\n"
            "  4. Fix #28 default under-claim: chain-grade upgrade should wait "
            "for the load-bearing branch (c) rather than extrapolate from the "
            "scale evidence alone. Parent META scope is correctly captured as "
            "'random-codebook Shannon-floor M=200 N_DIM in [512, 16384] sigma=1.5'; "
            "calling this 'chain-grade substrate operating envelope' before "
            "testing the encoder-structured regime is overclaiming.\n\n"
            "TIER: MEASURED_MECHANISM characterizing noise-floor N-shape under "
            "random-bipolar codebook; NOT chain-grade. Composes with parent META "
            "and sibling M-scan MM; does NOT supersede; does NOT trigger parent "
            "META upgrade. Two branches (one structural / encoder-side, plus "
            "the sub-bipolar payload branch carried in parent META metadata) "
            "remain open."
        ),
        kind=AtomKind.EXPERIMENT_RECORD,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.MATH,
        algebra=None,
        metadata={
            "provenance_quality": "MEASURED_MECHANISM",
            "cert_status": "measured_mechanism",
            "cert_class": "mechanism_characterization",
            "meta_informer": True,
            "verdict": (
                "MEASURED_MECHANISM_META_DECISION_N_INDEPENDENT_FULL_3seeds_seeds_"
                "7_17_23_M_200_N_EVAL_200_N_DIM_sweep_512_1024_2048_4096_8192_"
                "16384_sigma_sweep_1p0_1p5_2p0_at_sigma_1p5_peak_N_1024_recall_"
                "0p0350_lowest_N_512_0p0217_eq_N_16384_0p0217_knee_N_at_0p20_None_"
                "max_cv_across_cells_0p4403_at_N_8192_sigma_1p5_sanity_sigma_0_all_"
                "18_cells_recall_1p000_Shannon_floor_regime_N_INDEPENDENT_at_macro_"
                "decision_level_under_bipolar_codebook_closes_branch_a_of_parent_"
                "META_at_macro_level_NOT_chain_grade_per_Fix_28_default_under_claim_"
                "branch_c_learned_encoder_still_open_substrate_product_regime_test_"
                "cert_owner_OVERRIDE_of_Director_chain_grade_upgrade_arg"
            ),
            "cell_commit": "overnight_2026-06-22_plus_N_DIM_scan_branch_a_drill_2026-06-23",
            "metrics_path": "data/exp_cleanup_floor_N_DIM_scan_v1/metrics.json",
            "notes_path": "notes/research_encoder_side_cleanup_ceiling_break_2026-06-23.md",
            "verified_off_data": (
                "cert-owner re-derived from metrics.json across all 3 seeds. "
                "detail.agg[N_DIM][sigma] verified directly (not from verdict_msg "
                "framing). Sigma=1.5 per-cell means: N=512=0.0217, N=1024=0.0350 "
                "PEAK, N=2048=0.0283, N=4096=0.0233, N=8192=0.0233, N=16384=0.0217. "
                "Sigma=1.0 per-cell means: N=512=0.0550, N=1024=0.0450, "
                "N=2048=0.0533, N=4096=0.0567, N=8192=0.0583 PEAK, N=16384=0.0417. "
                "Director framing 'highest at N=512' INCORRECT for both sigmas; "
                "peak at sigma=1.5 is N=1024, peak at sigma=1.0 is N=8192. Macro "
                "N-INDEPENDENT conclusion stands. Sanity sigma=0: recall=1.000 "
                "across all 6 N_DIMs for all 3 seeds (verified per_seed[i]."
                "sanity_sigma_0 dict). zero_llm_calls_at_inference=True; "
                "n_llm_calls=0. run_mode='full'. CONFIG_VERSION baked. Self-test "
                "PASS recorded in log (clean-cue identity + high-noise random + "
                "L2 norm + verdict triplet + sanity-gate + n_llm_calls=0). "
                "Cell's own anchor cites 'cert_ledger_row_675_meta_cleanup_"
                "ceiling_shannon_floor' + 'cleanup_floor_M_scan_v1_META_DECISION_"
                "M_INDEPENDENT_branch2_closed' + 'ENC1_N4096_M200_argmax_0p027_"
                "prior_data_point' confirming META-informer intent and prior-"
                "data cross-check. ENC1 prior datapoint 0.027 at N=4096 sigma=1.5 "
                "matches this scan 0.0233 within seed noise (cv=0.36; per_seed "
                "[0.035, 0.020, 0.015])."
            ),
            "honest_scope": (
                "FULL 3-seed N_DIM-sweep at M=200 with ARGMAX_BASELINE only "
                "(no decoder OR encoder mechanism arms; random bipolar codebook "
                "L2-normalized). DOES characterize the noise-floor recall shape "
                "across N_DIM in [512, 16384] under bipolar codebook at sigma in "
                "{1.0, 1.5, 2.0}. DOES close branch (a) of parent Shannon-floor "
                "META at the MACRO decision level (no N_DIM in sweep crosses "
                "0.20 HARD_PASS or 0.10 HARD_FAIL_floor; N-INDEPENDENT for the "
                "META-DECISION at this codebook type). DOES NOT directly close "
                "branch (a) in full quantitative sense: there is a real "
                "non-monotone shape with sigma=1.5 peak at N=1024 and sigma=1.0 "
                "peak at N=8192 -- not the prior 'concentration of measure' "
                "expectation. DOES NOT test: branch (c) learned-encoder keys "
                "(Foldiak / anti-Hebb / Krotov / BTSP / contrastive). DOES NOT "
                "generalize to non-bipolar codebooks (Gaussian, structured, "
                "k-WTA-VQ-encoded), to M != 200, to sigma > 2.0 or sigma < 1.0, "
                "or to N_DIM > 16384. DOES NOT upgrade parent META to chain-"
                "grade; branch (c) is load-bearing for the substrate-product "
                "regime claim and remains untested. Per Fix #28 default-under-"
                "claim + by-construction-saturation tiering: tier MM, NOT chain-"
                "grade upgrade of the parent META."
            ),
            "n_seeds": 3,
            "seeds": [7, 17, 23],
            "M": 200,
            "N_EVAL": 200,
            "codebook_type": "random_bipolar_L2_normalized",
            "N_DIM_sweep": [512, 1024, 2048, 4096, 8192, 16384],
            "sigma_sweep": [1.0, 1.5, 2.0],
            "discriminator_sigma": 1.5,
            "arms": ["ARGMAX_BASELINE"],
            # sigma=1.5 row
            "recall_N_512_sigma_1p5": 0.0217,
            "recall_N_1024_sigma_1p5": 0.0350,
            "recall_N_2048_sigma_1p5": 0.0283,
            "recall_N_4096_sigma_1p5": 0.0233,
            "recall_N_8192_sigma_1p5": 0.0233,
            "recall_N_16384_sigma_1p5": 0.0217,
            "peak_N_at_sigma_1p5": 1024,
            "peak_recall_at_sigma_1p5": 0.0350,
            # sigma=1.0 row
            "recall_N_512_sigma_1p0": 0.0550,
            "recall_N_8192_sigma_1p0": 0.0583,
            "peak_N_at_sigma_1p0": 8192,
            "peak_recall_at_sigma_1p0": 0.0583,
            # macro decision
            "knee_N_at_recall_0p20": None,
            "max_cv_across_cells": 0.4403,
            "sanity_sigma_0_all_cells_recall_1p0_ok": True,
            "macro_decision_N_independent_at_M_200": True,
            "META_branch_a_closed_macro_level_only": True,
            "META_branches_still_open_after_this_atom": [
                "learned_encoder_Foldiak_anti_Hebb_Krotov_BTSP_contrastive",
                "sub_bipolar_float_valued_signal_payload",
            ],
            "director_framing_correction_per_Fix_28": (
                "director_brief_asserted_recall_HIGHEST_at_N_512_INCORRECT_at_"
                "sigma_1p5_peak_is_N_1024_recall_0p0350_at_sigma_1p0_peak_is_N_"
                "8192_recall_0p0583_N_512_is_NEVER_peak_macro_N_independent_"
                "conclusion_stands_but_per_cell_peak_framing_was_wrong_atom_"
                "captures_correct_per_cell_numbers_off_data"
            ),
            "by_construction_saturation_rationale": (
                "random_bipolar_codebook_at_sigma_1p5_M_200_is_synthetic_"
                "information_theory_floor_increasing_N_DIM_introduces_no_signal_"
                "isotropic_codebook_plus_sigma_1p5_noise_dominates_cosine_readout_"
                "cell_CANNOT_fail_above_0p05_at_this_regime_cleanly_measured_floor_"
                "neq_chain_grade_evidence_default_under_claim_per_Fix_28_HOLD_"
                "parent_META_at_MM_until_branch_c_learned_encoder_closes"
            ),
            "cert_owner_override_of_director_chain_grade_upgrade_arg": True,
            "device": "cpu",
            "elapsed_s": 2.44,
            "run_mode": "full",
            "zero_llm_calls_at_inference": True,
            "n_llm_calls": 0,
            "composes_with": [
                "T3/META_cleanup_ceiling_shannon_floor_substrate_operating_envelope_sigma_leq_1p0_2026-06-23",
                "T3/META_cleanup_ceiling_is_encoder_bound_at_N512_high_noise_M_over_N_0p39_2026-06-23",
                "T3/EXP_cleanup_floor_M_scan_v1_MM",
                "T3/EXP_enc1_structured_n_lift_v1_HN",
            ],
            "cites": [
                "Fix_28_verify_per_arm_metrics_not_verdict_msg_framing",
                "Fix_28_default_under_claim_let_cert_come_from_data_not_framing",
                "by_construction_saturation_tiering",
                "snapshot_before_mass_mutation_no_in_place_parent_META_edit",
                "USER_empowered_to_experiment_where_lit_says_dismissed_2026-06-22",
                "cert_ledger_row_675_meta_cleanup_ceiling_shannon_floor_parent",
                "cert_ledger_row_676_cleanup_floor_M_scan_v1_MM_sibling_branch_b",
                "research_encoder_side_cleanup_ceiling_break_2026-06-23",
                "ENC1_N4096_M200_argmax_0p027_prior_data_point_cross_check",
            ],
            "atomized_by": ATOMIZED_BY,
        },
    )


# ============================================================================
# Helpers (mirrors prior batch's safe_add_with_ledger)
# ============================================================================

def safe_add_with_ledger(atom: Atom, source: str, note: str,
                         notes_path: str, metrics_path: str, verdict_text: str,
                         atom_id_full: str, cell_commit: str):
    ps = PartitionedStore(STORE_ROOT)
    qid = f"{atom.corpus.value}::{atom.id}"
    if ps.get_atom(qid) is not None:
        print(f"  SKIP (idempotent): {atom.id} already present.")
    else:
        print(f"  ADDING atom: {atom.id}")
        ps.add_atom(atom, source=source, note=note)
        ps2 = PartitionedStore(STORE_ROOT)
        atoms = list(ps2.all_atoms())
        found = next((a for a in atoms if a.id == atom.id), None)
        if found is None:
            print("  FAIL: atom not found post-add")
            return (False, None)
        md = found.metadata or {}
        expected_pq = (atom.metadata or {}).get("provenance_quality")
        if md.get("provenance_quality") != expected_pq:
            print(f"  FAIL: pq mismatch (expected {expected_pq}, got {md.get('provenance_quality')})")
            return (False, None)
        print(f"  PASS: round-trip OK (pq={expected_pq})")

    ps_live = PartitionedStore(STORE_ROOT)
    live_cert = sum(
        1 for a in ps_live.all_atoms()
        if (a.metadata or {}).get("provenance_quality") == "CERT_CHAIN_GRADE"
    )

    row = build_measured_mechanism_row(
        atom_id=atom_id_full, cell_commit=cell_commit, verdict=verdict_text,
        notes_path=notes_path, metrics_path=metrics_path,
        atomized_by=ATOMIZED_BY, note=note,
    )

    print(
        f"  appending cert-ledger row (op={row['op']} status={row['cert_status']} "
        f"delta={row['cert_increment_delta']})"
    )
    try:
        h = append_cert_ledger_row(
            row,
            expected_cert_n_pre=live_cert,
            expected_cert_n_post=live_cert,
        )
        print(f"  row_hash={h}")
        return (True, h)
    except Exception as e:
        print(f"  FAIL: ledger append errored: {e}")
        return (False, None)


# ============================================================================
# Main
# ============================================================================

ATOM_PLAN = [
    (
        build_N_DIM_scan_mm,
        "notes/research_encoder_side_cleanup_ceiling_break_2026-06-23.md",
        "data/exp_cleanup_floor_N_DIM_scan_v1/metrics.json",
        (
            "MEASURED_MECHANISM_META_DECISION_N_INDEPENDENT_FULL_3seeds_M_200_"
            "N_DIM_sweep_512_to_16384_sigma_1p5_peak_N_1024_recall_0p0350_lowest_"
            "N_512_eq_N_16384_recall_0p0217_knee_N_at_0p20_None_max_cv_0p4403_"
            "sanity_sigma_0_all_cells_1p000_Shannon_floor_N_INDEPENDENT_at_macro_"
            "level_under_bipolar_codebook_closes_branch_a_at_macro_level_NOT_"
            "chain_grade_per_Fix_28_default_under_claim_branch_c_learned_encoder_"
            "still_open_cert_owner_OVERRIDE_of_Director_chain_grade_upgrade_arg"
        ),
        "overnight_2026-06-22_plus_N_DIM_scan_branch_a_drill_2026-06-23",
        (
            "META_DECISION_N_INDEPENDENT_at_M_200_macro_decision_level_for_"
            "Shannon_floor_parent_ledger_row_675_composes_NOT_supersede_with_"
            "sibling_M_scan_at_row_676_branch_c_learned_encoder_still_open_"
            "cert_owner_override_of_Director_chain_grade_upgrade_per_Fix_28_"
            "default_under_claim_plus_by_construction_saturation_director_"
            "framing_highest_at_N_512_INCORRECT_per_cell_peak_actually_N_1024_"
            "at_sigma_1p5_corrected_off_data"
        ),
    ),
]


def main() -> int:
    if "--apply" not in sys.argv:
        print("DRY: pass --apply to mutate Store + ledger.")
        print(f"Plan: {len(ATOM_PLAN)} atomization (MEASURED_MECHANISM; delta=0)")
        for i, item in enumerate(ATOM_PLAN, 1):
            builder, _, _, _, _, _ = item
            a = builder()
            print(f"  {i}. {a.id}  pq={a.metadata['provenance_quality']}  delta=+0")
        return 0

    ps = PartitionedStore(STORE_ROOT)
    atoms_pre = list(ps.all_atoms())
    n_atoms_pre = len(atoms_pre)
    cert_pre = sum(
        1 for a in atoms_pre
        if (a.metadata or {}).get("provenance_quality") == "CERT_CHAIN_GRADE"
    )
    print(f"A5-PRE: n_atoms={n_atoms_pre} CERT N={cert_pre}")
    expected_delta_atoms = len(ATOM_PLAN)
    expected_delta_cert = 0
    print(f"Expected delta: atoms +{expected_delta_atoms}; CERT +{expected_delta_cert}")
    print()

    row_hashes = []
    for i, item in enumerate(ATOM_PLAN, 1):
        builder, notes_path, metrics_path, verdict_text, cell_commit, ledger_note = item
        atom = builder()
        atom_id_full = f"{atom.corpus.value}::{atom.id}"
        print(f"=== {i}/{len(ATOM_PLAN)}: {atom.id}  (pq={atom.metadata['provenance_quality']} delta=+0)")
        ok, h = safe_add_with_ledger(
            atom,
            source=ATOMIZED_BY,
            note=ledger_note,
            notes_path=notes_path,
            metrics_path=metrics_path,
            verdict_text=verdict_text,
            atom_id_full=atom_id_full,
            cell_commit=cell_commit,
        )
        if not ok:
            print(f"ABORT at item {i}")
            return 1
        row_hashes.append((atom.id, h))
        print()

    ps_post = PartitionedStore(STORE_ROOT)
    atoms_post = list(ps_post.all_atoms())
    n_atoms_post = len(atoms_post)
    cert_post = sum(
        1 for a in atoms_post
        if (a.metadata or {}).get("provenance_quality") == "CERT_CHAIN_GRADE"
    )
    print("=" * 72)
    print(f"A5-POST: n_atoms={n_atoms_post} (delta +{n_atoms_post - n_atoms_pre}, expected +{expected_delta_atoms})")
    print(f"         CERT N={cert_post} (delta +{cert_post - cert_pre}, expected +{expected_delta_cert})")
    print("=" * 72)
    print("Row hashes:")
    for aid, h in row_hashes:
        print(f"  {h}  {aid}")

    if (n_atoms_post - n_atoms_pre) != expected_delta_atoms:
        print("WARNING: atom count drift")
        return 1
    if (cert_post - cert_pre) != expected_delta_cert:
        print("WARNING: CERT count drift")
        return 1
    print("A5 invariants PRESERVED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
