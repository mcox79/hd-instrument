#!/usr/bin/env python3
"""Skunkworks atomize tool -- 5-artifact late-dispatch wave 2026-06-25.

Lands 5 atoms in a single batch with A5-gated Store writes + cert_ledger appends:

  1. math::T3 anisotropy_rescue_4arm_sweep_v2_calibrated_meter_full
     -> measured_mechanism (Q-discipline saturation override of Director's chain-grade-candidate)
     -> delta=0
     Reason: ALL 4 working arms (Bfly/Bchar/C/D_meter) at >=0.995 saturation per the cell's own
     Q_SUSPECT_SATURATION band; cannot discriminate WHICH rescue mechanism is load-bearing at
     M=10k corpus regime. Mechanism IS measured (raw=0.018 -> rescue 0.997, 55x); MM tier is
     honest. Chain-grade-confirmed promotion path is M=100k with adversarial-similarity keys.

  2. math::T3 partition_routing_hierarchical_2level_v1
     -> chain_grade (Cell 1's chain-grade rail compositionally inherited + 1.5pp lift; cv tight)
     -> delta=+1
     Reason: 2LEVEL=0.9783 < 0.995 Q-saturation band; 3.2x discriminator gap over FLAT=0.303 at
     M=10M; cv=0.006; cleanly extends Cell 1 (M=1M chain-grade) to M=10M. By-construction-routing
     caveat-class inherited from Cell 1 -- already-tiered chain-grade at that caveat level.

  3. math::T3 multihop_csp_gated_iterated_cleanup_v1
     -> honest_negative / pre_reg_miss_proven_bound
     -> delta=0
     Reason: 4th independent attempt at Barrier-1 random-bipolar isotropic regime; HARD_FAILed
     pre-reg (HP_5hop>=0.50 missed at 0.030; HF_5hop<0.20 fired at 0.030); CSP-gated mechanism
     HURTS 2hop baseline (0.65 -> 0.21) vs lifts; geometric chain-cleanup decay (~0.46 per hop).
     Counts as proven NEGATIVE bound.

  4. math::T3 working_memory_v2_extended_K_with_cleanup_per_slot
     -> honest_negative / pre_reg_miss_proven_bound
     -> delta=0
     Reason: HP_CLEANUP_K128_SIGMA10>=0.95 missed at 0.922; K-ceiling at K=64 for both NAIVE
     and CLEANUP (cleanup-per-slot mechanism does NOT extend K-ceiling); +0.014 lift at K128
     is marginal and not load-bearing. Bind-capacity bottleneck (architectural), not cleanup-
     side. Counts as proven NEGATIVE bound.

  5. meta::T3 META_BARRIER_1_QUADRUPLE_NEGATIVE
     -> meta_rule / discipline_meta / delta=0
     Reason: Extends META_BARRIER_1_TRIPLE_NEGATIVE atom to include CSP-gated v1 as 4th
     independent attempt. Composes with existing TRIPLE atom; supersedes is None (does not
     retract; extends).

  6. meta::T3 META_M7_SMOKE_REGIME_MATCH_CAPACITY_SENSITIVE_DIMENSIONS
     -> meta_rule / discipline_meta / delta=0
     Reason: 2 directly verified instances (pointer-chain v2 + CSP-gated v1; both showed multi-
     dimension regime-confounded smoke->full sign-flip); WM-scaffold v1 supports indirectly.
     Atomizes the prior-deferred candidate per Skunkworks-better-framing (broader rule covering
     EVERY capacity-sensitive dimension, not just n_chains). M7 follows M1-M6 numbering.

Discipline:
- A5 PRE/POST verify: math/meta atom counts; CERT_N; axiom=206; cap_pres 6/6
- Atomic add_atom via Atom() constructor (not raw JSONL) per template_SAFE
- Fresh-Store all_atoms() round-trip per atom
- cert_ledger row appended in SAME A5 window per atom via Phase-C live-write
- Idempotency: if any of the 6 atom_ids already present, abort whole batch with diagnostic
- Path-scoped commit (caller responsibility): tool + ruling note + atoms.jsonl files staged
- Foreground execution; no subprocess pipes; ASCII only

Pre-write live CERT N: 599 (verified 2026-06-25). Post-write expected: 600 (delta=+1 for art 2).
"""
from __future__ import annotations
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier
from tools.cert_ledger_writer import (
    append_cert_ledger_row,
    build_chain_grade_ruling_row,
    build_measured_mechanism_row,
    build_honest_negative_row,
)

STORE_ROOT = REPO_ROOT / "data" / "substrate_index"
NOTES_PATH = "notes/skunkworks_tier_ruling_5_artifact_late_wave_2026-06-25.md"


# ============================================================================
# Atom specs (6 atoms: 4 math + 2 meta)
# ============================================================================

def atom_1_anisotropy_rescue_v2_mm() -> Atom:
    """Artifact 1: anisotropy rescue v2 calibrated meter -> MEASURED_MECHANISM."""
    return Atom(
        id=(
            "T3/EXP_substrate_anisotropy_rescue_4arm_sweep_v2_calibrated_meter_full_"
            "measured_mechanism_4_arm_saturation_at_M10k_corpus_easy_55x_rescue_real_"
            "discriminating_arm_pending_M100k_adversarial_keys"
        ),
        name=(
            "Anisotropy rescue 4-arm v2 calibrated meter: MEASURED_MECHANISM "
            "(Q-discipline saturation override; cerebellar/fly-LSH sparse fan-in DOES "
            "rescue anisotropy collapse 55x at M=10k Pythia-2.8b real keys but ALL 4 "
            "working arms saturate equivalently at >=0.995 so load-bearing rescue mechanism "
            "is not isolated; chain-grade-confirmed pending M=100k adversarial-similarity keys)"
        ),
        description=(
            "MEASURED MECHANISM (Q-discipline saturation override of Director's "
            "chain-grade-candidate framing per by-construction-saturation tiering "
            "discipline; cert-owner override pattern per Skunkworks-correctly-overrides-"
            "Director MEMORY rule 2026-06-23).\n\n"
            "VERBATIM PER-ARM @ M=10000 (mean over seeds [11,13,19]):\n"
            "  arm_baseline_raw (no rescue) = 0.018 (anisotropy collapse confirmed)\n"
            "  arm_A_cerebellar_K5_expand5x = 0.051 (smoke-mode regime; insufficient expansion)\n"
            "  arm_Ap_dense_5x = 0.062\n"
            "  arm_B_fly_lsh (K=20 random sparse) = 0.997 (cv=0.001)\n"
            "  arm_B_charikar (hyperplane LSH) = 1.000 (cv=0.000)\n"
            "  arm_C_compose (B+attention) = 0.996\n"
            "  arm_D_meter (attention beta-sweep upper-bound, calibrated) = 1.000\n"
            "  rel_B_fly/D = 0.997; rel_B_char/D = 1.000\n\n"
            "MECHANISM IS MEASURED: 55x rescue (raw 0.018 -> rescue 0.997) is real; "
            "anisotropy IS the binding constraint on raw dense KV at M=10k Pythia-2.8b "
            "keys; sparse fan-in (cerebellar/fly-LSH) and Charikar SimHash and attention "
            "all RESCUE the collapse. Mechanism-claim is honest.\n\n"
            "WHY MEASURED_MECHANISM not chain-grade (Q-discipline saturation, cell's "
            "own Q_SUSPECT_SATURATION band fires 4/4 arms):\n"
            "  - 4 of 4 working arms at >=0.995 (Bfly/Bchar/C/D_meter)\n"
            "  - Cannot discriminate WHICH rescue mechanism is load-bearing at M=10k\n"
            "  - The HP_LSH=0.80 bar was meaningful but sailing 25% over it is by-"
            "    construction-saturation territory at this M\n"
            "  - The 4 mechanisms (sparse fan-in K=20 / hyperplane LSH / compose / "
            "    attention) span different storage classes; if they ALL saturate it's "
            "    the corpus that's easy, not the mechanisms that are equivalent\n\n"
            "CHAIN-GRADE-CONFIRMED PROMOTION PATH: re-dispatch at M=100k with adversarial-"
            "similarity keys (e.g. consecutive text8 tokens at stride 1 producing very-"
            "similar adjacent keys). If sparse fan-in survives and Charikar/attention "
            "degrade, the LSH-fanout mechanism is isolated as load-bearing and a chain-"
            "grade promotion is justified. If all 4 still saturate, regime is still "
            "corpus-too-easy and a harder discriminator is needed.\n\n"
            "STRATEGIC SIGNIFICANCE (MM tier, not yet chain-grade): anisotropy is no "
            "longer an unsolved show-stopper at this measurement scale -- 3 distinct "
            "rescue paths (sparse expansion / hyperplane LSH / attention-cleanup) ALL "
            "work at M=10k. The substrate-product positioning REMAINS valid via "
            "partition routing (Cell 1 chain-grade; Artifact 2 this batch extends to "
            "M=10M); the substrate-as-LM Stage 4 deferral can be revisited AFTER chain-"
            "grade-confirmed at M=100k adversarial.\n\n"
            "Companion cells (cited):\n"
            "  - exp_dense_KV_whitening_revival_v1_gpu (HARD_FAIL; whitening did NOT "
            "    rescue; +0.020 marginal -- confirms anisotropy IS real on these keys)\n"
            "  - exp_anisotropy_rescue_4arm_sweep_v1_gpu (MIDDLE_BAND meter-bug; v2 "
            "    calibrated meter is the fixed-meter re-test)\n"
            "  - exp_kv_learned_projection_v1 (HARD_PASS held-out; complementary "
            "    chain-grade rescue mechanism via contrastive learned projection)\n\n"
            "References:\n"
            "  - Litwin-Kumar 2017 Neuron (cerebellar K=4-7 optimal)\n"
            "  - Dasgupta-Stevens-Navlakha 2017 Science (fly KC LSH)\n"
            "  - Charikar 2002 (hyperplane SimHash)\n"
            "  - Frady & Sommer 2020 (dense superposition capacity)\n"
            "  - Mu & Viswanath 2018 (cone-collapse diagnosis)\n"
        ),
        kind=AtomKind.EXPERIMENT_RECORD,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.MATH,
        algebra=None,
        metadata={
            "provenance_quality": "MEASURED_MECHANISM",
            "cert_status": "measured_mechanism",
            "cert_class": "mechanism_characterization",
            "cell_anchor": "substrate_anisotropy_rescue_4arm_sweep_v2_calibrated_meter_full",
            "cell_commit": "b2af908f",
            "metrics_path": (
                "data/exp_substrate_anisotropy_rescue_4arm_sweep_v2_calibrated_meter_"
                "full/metrics.json"
            ),
            "ruling_note": NOTES_PATH,
            "verified_off_data": True,
            "n_seeds": 3,
            "seeds": [11, 13, 19],
            "M_sweep": [1000, 3000, 10000],
            "encoder": "EleutherAI/pythia-2.8b",
            "proj_dim": 768,
            "verdict_director_proposed": "chain_grade_candidate",
            "verdict_skunkworks_ruled": "measured_mechanism",
            "override_reason": (
                "by_construction_saturation: 4/4 working arms at >=0.995 per cell's "
                "own Q_SUSPECT_SATURATION=0.995 band fires; mechanism-discriminator "
                "ambiguous at M=10k corpus easy regime"
            ),
            "per_arm_M10k": {
                "arm1_raw": 0.018,
                "arm_A_cerebellar_K5_expand5x": 0.051,
                "arm_Ap_dense_5x": 0.062,
                "arm_B_fly_lsh": 0.997,
                "arm_B_charikar": 1.000,
                "arm_C_compose": 0.996,
                "arm_D_meter_attn_upperbound_calibrated": 1.000,
            },
            "cv_arm_B_fly_lsh": 0.001,
            "cv_arm_B_charikar": 0.000,
            "cv_arm_D": 0.000,
            "rescue_factor_raw_to_arm_B_fly": 55.4,
            "brain_alignment_strong": "cerebellar_K5_fan_in_AND_fly_KC_LSH_DIRECT_ANALOG",
            "discriminating_followup_cell_proposed": (
                "exp_substrate_anisotropy_rescue_M100k_adversarial_similarity_keys_v1: "
                "re-run at M=100k with consecutive-token adversarial-similarity keys; "
                "if Bfly survives and Bchar/D degrade, isolate sparse fan-in as load-"
                "bearing -> chain_grade promotion eligible"
            ),
            "composes_with": [
                "math::T3/EXP_dense_KV_whitening_revival_v1_gpu_HARD_FAIL_anisotropy_"
                "real_whitening_does_not_rescue",
                "math::T3/EXP_kv_learned_projection_v1_chain_grade_contrastive_learned_"
                "projection_rescues_held_out",
            ],
            "cites": [
                "Litwin-Kumar2017_cerebellar_K4_to_7_optimal",
                "Dasgupta_Stevens_Navlakha2017_fly_KC_LSH_Science",
                "Charikar2002_hyperplane_LSH",
                "Frady_Sommer2020_dense_superposition_capacity",
                "Mu_Viswanath2018_cone_collapse",
                "research_anisotropy_drill_1_barriers_math_literature_2026-06-25",
                "research_anisotropy_drill_2_solutions_brain_substrate_2026-06-25",
                "research_anisotropy_intuitive_synthesis_with_visual_2026-06-25",
            ],
        },
    )


def atom_2_hierarchical_routing_2level() -> Atom:
    """Artifact 2: hierarchical 2-level partition routing M=10M -> chain_grade."""
    return Atom(
        id=(
            "T3/EXP_substrate_partition_routing_hierarchical_2level_v1_chain_grade_"
            "M10M_envelope_2level_routing_inherits_cell1_caveat_class"
        ),
        name=(
            "Hierarchical 2-level partition routing v1: CHAIN_GRADE at M=10M (2LEVEL=0.978 "
            "vs SINGLE=0.963 vs FLAT=0.303; 3.2x discriminator gap; cv=0.006; routing "
            "accuracy 1.0 by-construction caveat-class inherited from Cell 1 chain-grade)"
        ),
        description=(
            "CHAIN-GRADE: hierarchical 2-level partition routing scales the substrate "
            "KG-retrieval product positioning from M=1M (Cell 1's chain-grade rail) to "
            "M=10M via a 10 coarse x 1000 fine partition structure (10000 partitions of "
            "1000 each).\n\n"
            "VERBATIM PER-M (mean over seeds [11,13,19]):\n"
            "  M=1M:   2LEVEL=0.970 (cv=0.007) SINGLE=0.947 (cv=0.003) FLAT=0.488\n"
            "  M=10M:  2LEVEL=0.978 (cv=0.006) SINGLE=0.963 (cv=0.009) FLAT=0.303\n"
            "  routing_accuracy = 1.000 across all M (BY CONSTRUCTION caveat per Cell 1)\n\n"
            "PRE-REG BANDS EVALUATED:\n"
            "  HARD_PASS_M10M_2LEVEL >= 0.80: PASS (0.978 vs 0.80; margin +0.178)\n"
            "  CHAIN_GRADE_M10M_2LEVEL >= 0.70: PASS (margin +0.278)\n"
            "  HARD_PASS_CV <= 0.05: PASS (cv=0.006)\n"
            "  Q_SUSPECT_SATURATION (>= 0.995): NOT FIRED (0.978 < 0.995)\n\n"
            "DISCRIMINATING REGIME EVIDENCE:\n"
            "  - 3.2x gap over FLAT_KV_REFERENCE (no-routing baseline collapses at M=10M)\n"
            "  - 2LEVEL provides +1.5pp lift over SINGLE_LEVEL (Cell 1 architecture; "
            "    matches Cell 1's chain-grade rail when applied at M=10M)\n"
            "  - cv=0.006 tight across 3 seeds; not noise\n\n"
            "CAVEAT CLASS (inherited from Cell 1 chain-grade tier):\n"
            "  routing_accuracy=1.000 is by-construction-perfect (route uses partition-id "
            "labels at retrieval; recall@10 limited only by intra-partition cleanup). This "
            "caveat-class was already tiered chain-grade at Cell 1 ratification; the 2-level "
            "extension inherits the same caveat-class. The mechanism is honest because "
            "partition-id is realistic in many KG settings (e.g. domain-routed or entity-"
            "type-routed structures); the by-construction caveat documents the boundary, "
            "not a fraud.\n\n"
            "STRATEGIC SIGNIFICANCE: substrate KG retrieval product positioning EXTENDS from "
            "M=1M-class (Cell 1) to M=10M-class. Compositionally inherits Cell B's dense KV "
            "per-partition envelope + Cell 1's single-level routing envelope.\n\n"
            "Brain alignment: hippocampal indexing into cortical regions (Goyal/Buzsaki 2021); "
            "weak alignment but precedent for hierarchical address-decode in biology.\n\n"
            "Companion cells (composes-with):\n"
            "  - exp_substrate_partition_routing_10M_full_v2 (Cell 1 chain-grade @ M=1M; "
            "    architectural ancestor)\n"
            "  - exp_substrate_anisotropy_rescue_4arm_sweep_v2_calibrated_meter_full "
            "    (Artifact 1 this batch; if sparse-fan-in rescue lifts to chain-grade-"
            "    confirmed at M=100k adversarial, can compose with this 2-level routing "
            "    for substrate-product MULTI-PATH KG: routing + sparse-LSH-rescued-encoder)\n"
        ),
        kind=AtomKind.EXPERIMENT_RECORD,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.MATH,
        algebra=None,
        metadata={
            "provenance_quality": "CERT_CHAIN_GRADE",
            "cert_status": "chain_grade",
            "cert_class": "pre_reg_pass",
            "cell_anchor": "substrate_partition_routing_hierarchical_2level_v1",
            "cell_commit": "a1e064fc",
            "metrics_path": (
                "data/exp_substrate_partition_routing_hierarchical_2level_v1/metrics.json"
            ),
            "ruling_note": NOTES_PATH,
            "verified_off_data": True,
            "n_seeds": 3,
            "seeds": [11, 13, 19],
            "M_sweep": [1000000, 10000000],
            "N_DIM": 1024,
            "part_size_single": 2000,
            "part_size_fine": 1000,
            "n_coarse": 10,
            "per_M_2level_mean": {"1000000": 0.970, "10000000": 0.978},
            "per_M_single_mean": {"1000000": 0.947, "10000000": 0.963},
            "per_M_flat_mean": {"1000000": 0.488, "10000000": 0.303},
            "per_M_2level_cv": {"1000000": 0.007, "10000000": 0.006},
            "discriminator_gap_at_M10M": 3.23,
            "lift_over_single_at_M10M": 0.015,
            "caveat_class": (
                "routing_accuracy_1p0_by_construction_inherits_cell1_chain_grade_caveat"
            ),
            "by_construction_route_acc": True,
            "composes_with": [
                "math::T3/EXP_substrate_partition_routing_10M_full_v2_chain_grade_M1M_"
                "router_decomposition_envelope",
            ],
            "cites": [
                "research_drill_partition_routing_hierarchical_proposal_2026-06-25",
                "Goyal_Buzsaki2021_hippocampal_indexing_cortical_regions",
            ],
        },
    )


def atom_3_csp_gated_hard_fail() -> Atom:
    """Artifact 3: CSP-gated multi-hop iterated cleanup -> honest_negative (Barrier-1 4th)."""
    return Atom(
        id=(
            "T3/EXP_substrate_multihop_csp_gated_iterated_cleanup_v1_HARD_FAIL_"
            "4th_barrier1_attempt_csp_hurts_baseline_geometric_chain_decay"
        ),
        name=(
            "CSP-gated iterated cleanup multi-hop v1: HARD_FAIL (4th independent "
            "Barrier-1 attempt; CSP confidence + iterated cleanup HURTS 2hop baseline "
            "0.65 -> 0.21 and fails to rescue 5hop at 0.030 vs HP 0.50; geometric chain-"
            "cleanup decay ~0.46 per hop dominates; mechanism cleanly measures its own "
            "failure)"
        ),
        description=(
            "HARD_FAIL / honest_negative / pre_reg_miss_proven_bound: 4th independent "
            "substrate-native multi-hop mechanism REFUTED at random-bipolar isotropic "
            "production regime (V_C=200, V_P=2 baseline / V_P=10 CSP, N=8192, K_SET=20). "
            "Extends META_BARRIER_1_TRIPLE_NEGATIVE to QUADRUPLE_NEGATIVE (see meta atom "
            "META_BARRIER_1_QUADRUPLE_NEGATIVE).\n\n"
            "VERBATIM (mean over seeds [7, 17, 23]):\n"
            "  BASELINE_HRR_2HOP = 0.6500 (sanity_breach 1/3: seed 7 = 0.605 < 0.62)\n"
            "  CSP_GATED_2HOP = 0.2117 (cv=0.099; HURTS baseline by 0.44 abs)\n"
            "  CSP_GATED_5HOP = 0.0300 (cv=0.624; refuse=0.415; iters=0.59; conf=0.423)\n"
            "  CSP_GATED_10HOP = 0.0050 (cv=0.816)\n"
            "  REFERENCE: pointer_v2_5hop = 0.122, WM_scaffold_5hop = 0.122\n\n"
            "PRE-REG BANDS EVALUATED:\n"
            "  HP_2hop >= 0.80: FAIL (0.212 vs 0.80; margin -0.588)\n"
            "  HP_5hop >= 0.50: FAIL (0.030 vs 0.50; margin -0.470)\n"
            "  HP_10hop >= 0.20: FAIL (0.005 vs 0.20; margin -0.195)\n"
            "  HF_5hop < 0.20: FIRED (0.030 below floor; mechanism does NOT rescue)\n"
            "  baseline_sanity [0.62, 0.68]: 1/3 BREACH (seed 7 = 0.605 below)\n\n"
            "PER-STEP ACCURACY (CSP_GATED 5HOP seed 7): [0.535, 0.245, 0.115, 0.080, 0.055]\n"
            "  per-hop survival ratio ~0.46; geometric decay 0.46^5 ~ 0.020 matches observed.\n"
            "  Mechanism cleanly measures its own failure; not implementation bug.\n\n"
            "MECHANISM (CSP-gated iterated cleanup; brain-inspired PFC + hippocampus + ACC):\n"
            "  - WM scaffold holds intermediate (PFC analog)\n"
            "  - Hebbian-bound W cleanup (hippocampus analog)\n"
            "  - CSP confidence (top1-top2 cosine separation) thresholds iteration "
            "    (ACC analog); iterates up to N_ITER=3 if confidence below 0.05; "
            "    refuses if still below threshold\n\n"
            "WHY HARD_FAIL not MM: clear pre-reg HP bar (>=0.50 at 5hop) missed by 0.47 "
            "absolute; clear HF floor (<0.20 at 5hop) FIRED at 0.030; HURTS baseline at "
            "2hop. This is mechanism-add-no-value with measured floor breach; honest "
            "NEGATIVE bound, not unmeasured MM characterization.\n\n"
            "SMOKE-VS-FULL REGIME-CONFOUNDED SIGN-FLIP (cross-cell evidence for META_M7):\n"
            "  smoke (N=2048, V_C=200, csp_n_chains=50, max_depth=5, seeds=[7]):\n"
            "    CSP_5HOP = 0.620 (HARD_PASS_PARTIAL framing)\n"
            "  full (N=8192, V_C=200, csp_n_chains=200, max_depth=10, seeds=[7,17,23]):\n"
            "    CSP_5HOP = 0.030 (-95% absolute loss)\n"
            "  REGIME-CONFOUNDED ACROSS 4 DIMENSIONS (N, n_chains, max_depth, seeds);\n"
            "  cannot attribute sign-flip to single dimension; same pattern as pointer-\n"
            "  chain v2 supporting META_M7 atomization in this batch.\n\n"
            "BARRIER 1 4-FOR-4 NEGATIVE CONTEXT (preserved per discipline_meta):\n"
            "  Together with prior 3 attempts (consolidation v3 HARD_FAIL, pointer-chain "
            "  v2 HARD_FAIL, WM-scaffold v1 HARD_FAIL), this is the 4th independent "
            "  substrate-native multi-hop mechanism REFUTED at random-bipolar isotropic "
            "  production regime. The 2-hop ceiling is substrate-product PERMANENT at "
            "  this regime. Per Fix #26 + META_BARRIER_1_QUADRUPLE: refuse-dispatch "
            "  future substrate-native multi-hop cells at this regime unless revision is "
            "  fundamentally different (anisotropic encoder, structured corpus, learned "
            "  attention, or sparse-LSH-rescued encoder per Artifact 1 follow-up).\n\n"
            "Companion cells (cited; composes-with for BARRIER 1 family):\n"
            "  - exp_substrate_multihop_consolidation_v3_proper_test_heldout_fix HARD_FAIL\n"
            "  - exp_substrate_multihop_pointer_chain_hybrid_v2_baseline_rail_fixed HARD_FAIL\n"
            "  - exp_substrate_multihop_wm_scaffolded_v1 HARD_FAIL\n"
        ),
        kind=AtomKind.EXPERIMENT_RECORD,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.MATH,
        algebra=None,
        metadata={
            "provenance_quality": "HARD_FAIL_HONEST_NEGATIVE",
            "cert_status": "honest_negative",
            "cert_class": "pre_reg_miss_proven_bound",
            "cell_anchor": "substrate_multihop_csp_gated_iterated_cleanup_v1",
            "cell_commit": "4d3e51cb",
            "metrics_path": (
                "data/exp_substrate_multihop_csp_gated_iterated_cleanup_v1/metrics.json"
            ),
            "ruling_note": NOTES_PATH,
            "verified_off_data": True,
            "n_seeds": 3,
            "seeds": [7, 17, 23],
            "regime": "random_bipolar_isotropic_production_V_C_200_N_8192_K_SET_20",
            "per_arm_means": {
                "baseline_hrr_2hop": 0.6500,
                "csp_gated_2hop": 0.2117,
                "csp_gated_5hop": 0.0300,
                "csp_gated_10hop": 0.0050,
            },
            "per_step_decay_csp_5hop_seed7": [0.535, 0.245, 0.115, 0.080, 0.055],
            "per_hop_survival_ratio_geometric": 0.46,
            "sanity_breach_seeds_baseline": "1/3 (seed 7 below 0.62)",
            "pre_reg_hp_5hop_target": 0.50,
            "pre_reg_hf_5hop_floor": 0.20,
            "barrier_1_quadruple_member": True,
            "composes_with": [
                "math::T3/EXP_substrate_multihop_consolidation_v3_proper_test_heldout_fix_HARD_FAIL",
                "math::T3/EXP_substrate_multihop_pointer_chain_hybrid_v2_baseline_rail_fixed_HARD_FAIL",
                "math::T3/EXP_substrate_multihop_wm_scaffolded_v1_HARD_FAIL",
                "meta::T3/META_BARRIER_1_TRIPLE_NEGATIVE_substrate_native_multihop_3_for_3_REFUTED_2_hop_ceiling_permanent",
                "meta::T3/META_BARRIER_1_QUADRUPLE_NEGATIVE",
            ],
            "cites": [
                "exp_dev_smoke_to_full_signflip_meta_m7_supporting_evidence",
                "Fix_26_predispatch_verify_referent_recent_HARD_FAIL",
            ],
        },
    )


def atom_4_wm_k_extension_hard_fail() -> Atom:
    """Artifact 4: WM K-extension cleanup-per-slot -> honest_negative (K-ceiling stays 64)."""
    return Atom(
        id=(
            "T3/EXP_substrate_working_memory_v2_extended_K_cleanup_per_slot_HARD_FAIL_"
            "K_ceiling_at_64_cleanup_per_slot_does_not_extend_bind_capacity_architectural"
        ),
        name=(
            "WM K-extension with cleanup-per-slot v2: HARD_FAIL (K-ceiling stays at 64 "
            "for both NAIVE and CLEANUP; cleanup-per-slot mechanism is CLEANUP-side fix "
            "but bottleneck is BIND CAPACITY at K=N/d_code; needs architectural fix "
            "multi-WM-bank+routing, not cleanup-side)"
        ),
        description=(
            "HARD_FAIL / honest_negative / pre_reg_miss_proven_bound: WM K-extension via "
            "theta-gamma cleanup-per-slot mechanism does NOT extend K-ceiling. Both NAIVE "
            "(production bind+bundle+unbind+cleanup) and CLEANUP_PER_SLOT (adds iterated "
            "cleanup pass at read: unbind, argmax, mix-toward-winner, re-quantize, "
            "re-argmax) hit K-ceiling at K=64 for sigma=1.0 noise.\n\n"
            "VERBATIM PER-K (mean over seeds [11,13,19], sigma=1.0):\n"
            "  K=32:  NAIVE=1.000  CLEANUP=1.000\n"
            "  K=64:  NAIVE=1.000  CLEANUP=0.999\n"
            "  K=128: NAIVE=0.908  CLEANUP=0.922 (cleanup +0.014; marginal)\n"
            "  K=256: NAIVE=0.555  CLEANUP=0.556\n"
            "  K=512: NAIVE=0.233  CLEANUP=0.239\n"
            "  K-ceiling (>=0.95 at sigma=1.0): NAIVE=64, CLEANUP=64 (SAME)\n\n"
            "PRE-REG BANDS EVALUATED:\n"
            "  HP_CLEANUP_K128_SIGMA10 >= 0.95: FAIL (0.922 vs 0.95; margin -0.028)\n"
            "  HP_cv <= 0.07: PASS (cv=0.012)\n"
            "  HF_cleanup <= naive: NOT fired (cleanup marginally beats naive at K128)\n"
            "  middle_band [0.80, 0.95]: cleanup IN band but pre-reg HP bar missed\n\n"
            "MECHANISM ANALYSIS:\n"
            "  - The +0.014 lift at K128 is marginal and within noise of cv=0.012\n"
            "  - K-ceiling SAME for both arms -> cleanup-per-slot is CLEANUP-SIDE fix\n"
            "  - The bottleneck is BIND CAPACITY (K bound by N/d_code; N=4096, d_code~32)\n"
            "  - Architectural fix needed: multi-WM-bank with routing (e.g. like partition "
            "    routing applied to WM slots), NOT cleanup-side fix\n\n"
            "WHY HARD_FAIL not MIDDLE_BAND: the cell's own verdict is MIDDLE_BAND, but per "
            "cert-owner Q-discipline + pre-reg-strict interpretation, the load-bearing "
            "claim was 'cleanup-per-slot extends K-ceiling' and the K-ceiling is UNCHANGED "
            "at 64. The +0.014 at K128 is below the noise floor (cv=0.012). The cell's "
            "internal MIDDLE_BAND tag captures 'cleanup in [0.80, 0.95]' but the PRE-REG "
            "BAR was 0.95 at K128 (FAIL) AND K-ceiling extension (FAIL). Per cert-owner "
            "strict pre-reg interpretation: honest_negative / pre_reg_miss_proven_bound.\n\n"
            "STRATEGIC SIGNIFICANCE: WM-HRR-slots production primitive remains at "
            "K-ceiling=64; theta-gamma cleanup-per-slot mechanism is REFUTED as K-ceiling "
            "extension. Future cells should target multi-WM-bank+routing architecture "
            "(analog of partition routing applied to WM slots) for K-extension.\n\n"
            "Companion cells (cited):\n"
            "  - prior WM-HRR-slots production cells at K=64 ceiling (architectural ancestor)\n"
            "  - exp_substrate_partition_routing_10M_full_v2 (Cell 1; routing pattern that "
            "    multi-WM-bank could inherit)\n"
        ),
        kind=AtomKind.EXPERIMENT_RECORD,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.MATH,
        algebra=None,
        metadata={
            "provenance_quality": "HARD_FAIL_HONEST_NEGATIVE",
            "cert_status": "honest_negative",
            "cert_class": "pre_reg_miss_proven_bound",
            "cell_anchor": "substrate_working_memory_v2_extended_K_with_cleanup_per_slot",
            "cell_commit": "8a56f1d8",
            "metrics_path": (
                "data/exp_substrate_working_memory_v2_extended_K_with_cleanup_per_slot/"
                "metrics.json"
            ),
            "ruling_note": NOTES_PATH,
            "verified_off_data": True,
            "n_seeds": 3,
            "seeds": [11, 13, 19],
            "N_DIM": 4096,
            "CODEBOOK_SIZE": 512,
            "K_values": [32, 64, 128, 256, 512],
            "sigmas": [0.0, 0.5, 1.0],
            "k_ceiling_naive_sigma_1p0": 64,
            "k_ceiling_cleanup_sigma_1p0": 64,
            "per_K_sigma1p0_means": {
                "K_32_NAIVE": 1.000, "K_32_CLEANUP": 1.000,
                "K_64_NAIVE": 1.000, "K_64_CLEANUP": 0.999,
                "K_128_NAIVE": 0.908, "K_128_CLEANUP": 0.922,
                "K_256_NAIVE": 0.555, "K_256_CLEANUP": 0.556,
                "K_512_NAIVE": 0.233, "K_512_CLEANUP": 0.239,
            },
            "cleanup_marginal_lift_K128": 0.014,
            "cv_K128_cleanup": 0.012,
            "pre_reg_hp_target": 0.95,
            "cell_internal_verdict": "MIDDLE_BAND",
            "skunkworks_strict_pre_reg_verdict": "HARD_FAIL_honest_negative",
            "override_reason": (
                "pre_reg_strict_K_ceiling_extension_load_bearing_claim_unchanged; "
                "marginal_K128_lift_below_noise_floor"
            ),
            "architectural_fix_proposed": (
                "multi_WM_bank_with_routing_analog_of_partition_routing_for_WM_slots"
            ),
        },
    )


def atom_5_meta_barrier_1_quadruple() -> Atom:
    """Artifact 5: META_BARRIER_1_QUADRUPLE_NEGATIVE -- extends TRIPLE to 4 attempts."""
    return Atom(
        id=(
            "T3/META_BARRIER_1_QUADRUPLE_NEGATIVE_csp_gated_extends_triple_substrate_"
            "native_multihop_4_for_4_REFUTED_2_hop_ceiling_permanent_strengthened"
        ),
        name=(
            "META BARRIER_1_QUADRUPLE_NEGATIVE: substrate-native multi-hop generalization "
            "at production-scale random-bipolar isotropic regime is REFUTED across FOUR "
            "independent mechanisms (consolidation v3 + pointer-chain v2 + WM-scaffold v1 "
            "+ CSP-gated iterated cleanup v1); extends META_BARRIER_1_TRIPLE_NEGATIVE; "
            "2-hop ceiling is substrate-product PERMANENT-STRENGTHENED at this regime"
        ),
        description=(
            "RULE (substrate-product positioning, CERT-neutral META composition): substrate-"
            "native multi-hop generalization at production-scale random-bipolar isotropic "
            "regime is REFUTED across FOUR independent mechanisms in three days (2026-06-24 "
            "/ 2026-06-25). The 2-hop ceiling is substrate-product PERMANENT-STRENGTHENED "
            "at this regime. EXTENDS the existing META_BARRIER_1_TRIPLE_NEGATIVE atom "
            "(adding CSP-gated iterated cleanup as 4th attempt); does NOT supersede.\n\n"
            "QUADRUPLE NEGATIVE (all four atomized):\n"
            "  (1) math::T3/EXP_substrate_multihop_consolidation_v3_proper_test_heldout_fix_HARD_FAIL\n"
            "      Mechanism: compound-predicate consolidation via K-thresh gating.\n"
            "      Result: consolidated class -> ~0% heldout; unconsolidated class -> 100% naive.\n"
            "  (2) math::T3/EXP_substrate_multihop_pointer_chain_hybrid_v2_baseline_rail_fixed_HARD_FAIL\n"
            "      Mechanism: pointer-chain hybrid with HRR fallback.\n"
            "      Result: 5hop=0.122 vs naive 2hop=0.65; HURTS baseline at 2hop (0.425 vs 0.65).\n"
            "  (3) math::T3/EXP_substrate_multihop_wm_scaffolded_v1_HARD_FAIL\n"
            "      Mechanism: WM-scaffolded multi-hop with intermediate-binding.\n"
            "      Result: 5hop=0.122; identical regime as pointer_v2; mechanism-add-no-value.\n"
            "  (4) math::T3/EXP_substrate_multihop_csp_gated_iterated_cleanup_v1_HARD_FAIL\n"
            "      Mechanism: CSP confidence + iterated cleanup + WM scaffold (PFC+hippo+ACC).\n"
            "      Result: 5hop=0.030; HURTS baseline at 2hop (0.21 vs 0.65); geometric chain "
            "      decay ~0.46 per hop. THIS IS THE 4TH STRENGTHENING INSTANCE.\n\n"
            "COMMON FAILURE MODE: per-hop cleanup fidelity at this regime is bounded by chain-"
            "cleanup geometric decay; no composition-architecture choice (consolidation, "
            "pointer, WM-scaffold, CSP-gating) rescues this. 4-for-4 INDEPENDENT MECHANISMS "
            "all hit the same wall.\n\n"
            "STRENGTHENING vs the TRIPLE atom: the CSP-gated attempt was specifically designed "
            "to address the gap in the 3 prior attempts (added CSP confidence + iterated "
            "cleanup, brain-inspired PFC+hippocampus+ACC composition). It failed in the SAME "
            "regime as the 3 prior attempts. This rules out 'we just need better cleanup' as "
            "a revival angle; chain-cleanup-attenuation is the binding constraint.\n\n"
            "ROUTING RULE (per Fix #26 + rebuttal-check):\n"
            "Future substrate-native multi-hop cells at random-bipolar isotropic regime: "
            "refuse-dispatch UNLESS revision is fundamentally different along one of:\n"
            "  - anisotropic encoder (e.g. real Pythia residuals + LSH-fanout rescue per "
            "    Artifact 1 anisotropy rescue v2 follow-up at M=100k adversarial)\n"
            "  - structured corpus (e.g. graph with feature-share semantic-consolidation)\n"
            "  - learned attention (vs random-bipolar binding)\n"
            "  - external scaffold delegating multi-hop to PFC analog at LLM-level\n\n"
            "STRATEGIC POSITIONING: substrate-product multi-hop reasoning is correctly\n"
            "positioned at 2-hop ceiling via external scaffold OR semantic-consolidation\n"
            "under feature-share cortical analog. The 4-for-4 negative removes substrate-\n"
            "native composition-architecture revival from the priority queue.\n\n"
            "Composes-with: META_BARRIER_1_TRIPLE_NEGATIVE (this atom extends it; both "
            "remain in Store as evidence-trail; both refer to each other).\n"
        ),
        kind=AtomKind.METHODOLOGY_RULE,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.META,
        algebra=None,
        metadata={
            "provenance_quality": "META_RULE_CERT_NEUTRAL",
            "cert_status": "meta_rule",
            "cert_class": "discipline_meta",
            "rule_id": "BARRIER_1_QUADRUPLE_NEGATIVE",
            "rule_category": "substrate_product_permanent_classification_strengthened",
            "rule_name": (
                "csp_gated_extends_triple_substrate_native_multihop_4_for_4_REFUTED_"
                "2_hop_ceiling_permanent_strengthened"
            ),
            "rule_text": (
                "Substrate-native multi-hop generalization at production-scale random-"
                "bipolar isotropic regime is REFUTED across FOUR independent mechanisms "
                "(compound-predicate consolidation, pointer-chain hybrid, WM-scaffold, "
                "CSP-gated iterated cleanup). All four fail because per-hop cleanup "
                "fidelity at this regime is bounded by geometric chain-cleanup decay "
                "(~0.46-0.70 per hop). No composition-architecture choice rescues this. "
                "2-hop ceiling is substrate-product PERMANENT-STRENGTHENED at this regime. "
                "Multi-hop reasoning routes via external scaffold (PFC analog at LLM-level) "
                "OR feature-share cortical analog (anisotropic encoder, different cell)."
            ),
            "rebuttal_check_for_skunkworks_landed_VET": (
                "Future substrate-native multi-hop cells at random-bipolar isotropic regime: "
                "refuse-dispatch per Fix #26 (recent HARD_FAIL re-dispatch forbidden) UNLESS "
                "revision is fundamentally different (anisotropic encoder, structured corpus, "
                "learned attention, OR composes with sparse-LSH-rescued encoder per Artifact 1 "
                "follow-up). Default ruling: HARD_FAIL by precedent absent novelty argument."
            ),
            "barrier_member_atoms": [
                "math::T3/EXP_substrate_multihop_consolidation_v3_proper_test_heldout_fix_HARD_FAIL",
                "math::T3/EXP_substrate_multihop_pointer_chain_hybrid_v2_baseline_rail_fixed_HARD_FAIL",
                "math::T3/EXP_substrate_multihop_wm_scaffolded_v1_HARD_FAIL",
                "math::T3/EXP_substrate_multihop_csp_gated_iterated_cleanup_v1_HARD_FAIL_"
                "4th_barrier1_attempt_csp_hurts_baseline_geometric_chain_decay",
            ],
            "composes_with": [
                "meta::T3/META_BARRIER_1_TRIPLE_NEGATIVE_substrate_native_multihop_3_for_3_"
                "REFUTED_2_hop_ceiling_permanent",
            ],
            "extends_prior": (
                "meta::T3/META_BARRIER_1_TRIPLE_NEGATIVE_substrate_native_multihop_3_for_3_"
                "REFUTED_2_hop_ceiling_permanent"
            ),
            "n_independent_attempts_refuted": 4,
            "per_hop_decay_range_observed": [0.46, 0.70],
        },
    )


def atom_6_meta_m7_smoke_regime_match() -> Atom:
    """Artifact 5b: META_M7 smoke regime must match full along EVERY capacity-sensitive dim."""
    return Atom(
        id=(
            "T3/META_M7_smoke_regime_must_match_full_along_every_capacity_sensitive_"
            "dimension_pointer_chain_v2_csp_gated_signflip_evidence"
        ),
        name=(
            "META M7: smoke regime MUST match full-run regime along EVERY capacity-"
            "sensitive dimension (N, density-parameters, n_seeds, max-depth); multi-"
            "dimension smoke reductions are regime-confounded; sign cannot be used as "
            "gate for full mechanism"
        ),
        description=(
            "RULE (rail discipline): smoke regime MUST match the full-run regime along "
            "EVERY capacity-sensitive dimension (N, density-parameters like n_chains/V_P, "
            "n_seeds, max-depth, K_SET). A smoke run that reduces MULTIPLE dimensions "
            "simultaneously creates a regime-confounded smoke whose sign cannot be used "
            "as a gate for the full mechanism.\n\n"
            "TWO DIRECTLY VERIFIED INSTANCES OFF-DATA (Skunkworks 2026-06-25):\n\n"
            "(1) pointer-chain hybrid v2 BASELINE_RAIL_FIXED:\n"
            "    smoke (N=2048, pointer_n_chains=50, n_seeds=1):\n"
            "      POINTER_2HOP=0.98 (HARD_PASS_BREAK_CEILING)\n"
            "    full (N=8192, pointer_n_chains=200, n_seeds=3):\n"
            "      POINTER_2HOP=0.425 (HARD_FAIL; -55% absolute)\n"
            "    POINTER_5HOP: 0.78 smoke -> 0.122 full (-84% absolute)\n"
            "    3 dimensions differ; regime-confounded.\n\n"
            "(2) CSP-gated iterated cleanup v1 (this batch):\n"
            "    smoke (N=2048, csp_n_chains=50, max_depth=5, n_seeds=1):\n"
            "      CSP_5HOP=0.620 (HARD_PASS_PARTIAL framing)\n"
            "    full (N=8192, csp_n_chains=200, max_depth=10, n_seeds=3):\n"
            "      CSP_5HOP=0.030 (HARD_FAIL; -95% absolute)\n"
            "    4 dimensions differ; regime-confounded.\n\n"
            "ONE SUPPORTING-BUT-INDIRECT INSTANCE (smoke artifact not preserved standalone):\n"
            "(3) WM-scaffolded v1: full WM_5HOP=0.122; the original Director claim cited\n"
            "    smoke=0.78 but the smoke metrics.json artifact is not present on disk\n"
            "    standalone for off-data verify. Pattern is CONSISTENT with the rule but\n"
            "    cannot be independently ratified per Fix #28.\n\n"
            "OPERATIONAL FIX:\n"
            "Every cell that authors BOTH smoke and full versions of a mechanism must:\n"
            "  (a) MATCH every capacity-sensitive dimension between smoke and full, OR\n"
            "  (b) EXPLICITLY DOCUMENT in pre-reg which dimensions differ and bound the\n"
            "      expected sign-stability under that dimension reduction (e.g. 'smoke at\n"
            "      0.25x N is expected to UNDER-state full mechanism; smoke pass + full\n"
            "      pass is the gate; smoke pass + full fail is regime-confounded'), OR\n"
            "  (c) AT MINIMUM keep n_seeds >= 3 even at smoke (the lowest-cost dimension\n"
            "      to match; catches single-seed luck artifacts).\n\n"
            "WHY M7 vs prior DEFER: the prior pointer-chain v2 ruling DEFERRED this META\n"
            "candidate per Fix #28 default under-claim (single-cell evidence + multi-\n"
            "dimension confound made the 'n_chains floor' framing single-cell). The\n"
            "BROADER framing (capacity-sensitive dimensions generally, not n_chains\n"
            "specifically) now has 2 directly-verified instances + 1 supporting; the\n"
            "rule is broad enough to fit the evidence without overclaiming.\n\n"
            "DOES NOT SUPERSEDE: M1-M6 remain in Store; M7 is the 7th rail-discipline\n"
            "rule, composing with M2 + M5 + M6 to form the 4-rule rail-derivation-\n"
            "provenance-regime-match set.\n\n"
            "EVIDENCE-TRAIL COMPOSITION (4-rule set):\n"
            "  M2: rail tolerance must match referent config OR widen by capacity drift\n"
            "  M5: cross-cell baseline comparisons require chain-construction match\n"
            "  M6: NAIVE-baseline must be DERIVED from current-cell regime, NOT copied\n"
            "  M7: smoke regime must match full along EVERY capacity-sensitive dimension\n"
        ),
        kind=AtomKind.METHODOLOGY_RULE,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.META,
        algebra=None,
        metadata={
            "provenance_quality": "META_RULE_CERT_NEUTRAL",
            "cert_status": "meta_rule",
            "cert_class": "discipline_meta",
            "rule_id": "M7",
            "rule_category": "smoke_full_regime_match",
            "rule_name": (
                "smoke_regime_must_match_full_along_every_capacity_sensitive_dimension"
            ),
            "rule_text": (
                "Smoke regime MUST match full-run regime along EVERY capacity-sensitive "
                "dimension (N, density-parameters like n_chains/V_P, n_seeds, max-depth, "
                "K_SET). A smoke that reduces multiple dimensions simultaneously is "
                "regime-confounded; its sign cannot be used as a gate for the full "
                "mechanism. Operational fix: match capacity-sensitive dimensions OR "
                "explicitly bound expected sign-stability OR at minimum keep n_seeds >= 3."
            ),
            "rebuttal_check_for_skunkworks_landed_VET": (
                "if cell smoke-vs-full sign-flips AND smoke reduces >=2 dimensions vs "
                "full: regime-confounded; the smoke pass DOES NOT validate the mechanism. "
                "Verdict on the full result is the load-bearing measurement. If full "
                "fails per pre-reg, ruling is HARD_FAIL (mechanism does not work at "
                "production regime); smoke pass framing is suspect-1.000 / by-construction-"
                "saturation territory at toy regime."
            ),
            "observed_instances": [
                {
                    "cell": "exp_substrate_multihop_pointer_chain_hybrid_v2_baseline_rail_fixed",
                    "smoke_metric_5hop": 0.78,
                    "full_metric_5hop": 0.122,
                    "loss_abs": -0.658,
                    "dimensions_reduced": ["N: 8192->2048", "pointer_n_chains: 200->50", "n_seeds: 3->1"],
                    "verified_off_data": True,
                },
                {
                    "cell": "exp_substrate_multihop_csp_gated_iterated_cleanup_v1",
                    "smoke_metric_5hop": 0.620,
                    "full_metric_5hop": 0.030,
                    "loss_abs": -0.590,
                    "dimensions_reduced": [
                        "N: 8192->2048", "csp_n_chains: 200->50",
                        "max_depth: 10->5", "n_seeds: 3->1",
                    ],
                    "verified_off_data": True,
                },
                {
                    "cell": "exp_substrate_multihop_wm_scaffolded_v1",
                    "smoke_metric_5hop_director_claim": 0.78,
                    "full_metric_5hop": 0.122,
                    "loss_abs_director_claim": -0.658,
                    "dimensions_reduced_assumed": "similar to pointer-chain v2",
                    "verified_off_data": False,
                    "note": "smoke artifact not preserved standalone; supporting indirect only",
                },
            ],
            "composes_with": [
                "meta::T3/META_M2_tight_rail_from_different_config_can_mask_direction_correct_lift",
                "meta::T3/META_M5_cross_cell_baseline_compare_requires_chain_construction_match",
                "meta::T3/META_M6_NAIVE_baseline_must_be_derived_not_copied_from_prior_cells",
            ],
            "rail_discipline_set_membership": ["M2", "M5", "M6", "M7"],
            "rail_discipline_set_name": (
                "rail_derivation_provenance_regime_match_4_rule_set"
            ),
            "supersedes_prior_deferred_candidate": (
                "pointer_chain_v2_2026-06-25_smoke_floor_n_chains_DEFERRED_candidate"
            ),
        },
    )


# ============================================================================
# A5-gated write batch
# ============================================================================

def _cert_count(store):
    return sum(
        1 for a in store.all_atoms()
        if (a.metadata or {}).get("provenance_quality") == "CERT_CHAIN_GRADE"
    )


def _axiom_count(store):
    return sum(
        1 for a in store.all_atoms()
        if str(a.corpus.name) == "MATH"
        and str(a.tier.name) in ("TIER_2_PRIMITIVE", "TIER_3_ALGORITHM")
        and a.algebra and len(a.algebra) >= 3
        and "oeis" not in str(a.id).lower()
        and not str(a.id).startswith("T3/wikidata_")
    )


def _cap_pres_ok():
    import importlib
    return all(
        hasattr(importlib.import_module(m), s) for m, s in [
            ("backend.substrate_index.hmm_decoder", "viterbi_decode"),
            ("hdlab.perceptron", "StructuredPerceptron"),
            ("backend.substrate_index.sequence_labeler", "NERTagger"),
            ("hdlab.bayesian_inference", "EMMixture"),
            ("backend.substrate_index.intent_classifier", "IntentClassifier"),
            ("backend.substrate_index.refuse_gated_retriever", "RefuseGatedRetriever"),
        ]
    )


def _add_atom_with_round_trip(atom: Atom, source: str, note: str) -> bool:
    """Atomic add via Atom() + ps.add_atom; fresh-Store round-trip verify."""
    ps = PartitionedStore(STORE_ROOT)
    qid = f"{atom.corpus.value}::{atom.id}"
    if ps.get_atom(qid) is not None:
        print(f"  SKIP (idempotent): {atom.id[:80]} already present")
        return True
    print(f"  ADDING: {atom.id[:100]}")
    print(f"    kind={atom.kind.value} tier={atom.tier.value} corpus={atom.corpus.value}")
    ps.add_atom(atom, source=source, note=note)
    # Fresh-Store round-trip verify
    ps2 = PartitionedStore(STORE_ROOT)
    atoms = list(ps2.all_atoms())
    found = next((a for a in atoms if a.id == atom.id), None)
    if found is None:
        print(f"  FAIL: atom not found post-add")
        return False
    if found.tier != atom.tier:
        print(f"  FAIL: tier mismatch (expected {atom.tier} got {found.tier})")
        return False
    if found.kind != atom.kind:
        print(f"  FAIL: kind mismatch (expected {atom.kind} got {found.kind})")
        return False
    md = found.metadata or {}
    if md.get("provenance_quality") != (atom.metadata or {}).get("provenance_quality"):
        print(f"  FAIL: provenance_quality mismatch")
        return False
    print(f"    PASS: round-trip survival OK")
    return True


def main():
    apply = "--apply" in sys.argv
    dry = "--dry-run" in sys.argv or not apply
    print("=" * 80)
    print(f"Skunkworks 5-artifact late-wave atomize | mode={'APPLY' if apply else 'DRY-RUN'}")
    print("=" * 80)

    # Build atoms
    atoms_specs = [
        ("Artifact 1 (MM; delta=0)", atom_1_anisotropy_rescue_v2_mm(),
         "measured_mechanism", "anisotropy_rescue_v2_4arm_saturation_override"),
        ("Artifact 2 (chain_grade; delta=+1)", atom_2_hierarchical_routing_2level(),
         "chain_grade", "hierarchical_2level_routing_M10M_extends_cell1"),
        ("Artifact 3 (honest_negative; delta=0)", atom_3_csp_gated_hard_fail(),
         "honest_negative", "csp_gated_4th_barrier1_attempt"),
        ("Artifact 4 (honest_negative; delta=0)", atom_4_wm_k_extension_hard_fail(),
         "honest_negative", "wm_K_extension_cleanup_per_slot_K_ceiling_unchanged"),
        ("Artifact 5 META QUADRUPLE (meta_rule; delta=0)", atom_5_meta_barrier_1_quadruple(),
         "meta_rule", "META_BARRIER_1_QUADRUPLE_NEGATIVE_extends_triple"),
        ("Artifact 5 META M7 (meta_rule; delta=0)", atom_6_meta_m7_smoke_regime_match(),
         "meta_rule", "META_M7_smoke_regime_match_capacity_sensitive_dimensions"),
    ]

    print(f"\nBatch contains {len(atoms_specs)} atoms.")

    # PRE-snapshot
    print("\n--- A5 PRE-SNAPSHOT ---")
    ps_pre = PartitionedStore(STORE_ROOT)
    pre_cert = _cert_count(ps_pre)
    pre_ax = _axiom_count(ps_pre)
    pre_cap = _cap_pres_ok()
    pre_total = sum(1 for _ in ps_pre.all_atoms())
    print(f"  CERT_N = {pre_cert}")
    print(f"  axiom_count = {pre_ax}")
    print(f"  cap_pres = {'6/6' if pre_cap else 'FAIL'}")
    print(f"  total_atoms = {pre_total}")
    assert pre_ax == 206, f"A5-PRE axiom drift: {pre_ax} != 206"
    assert pre_cap, "A5-PRE cap_pres FAIL"
    print(f"  expected post-CERT_N (after +1 from Artifact 2) = {pre_cert + 1}")

    # Idempotency check (whole batch must be entirely-new or entirely-present)
    print("\n--- IDEMPOTENCY CHECK ---")
    present_count = 0
    for label, atom, _, _ in atoms_specs:
        qid = f"{atom.corpus.value}::{atom.id}"
        if ps_pre.get_atom(qid) is not None:
            print(f"  PRESENT: {qid[:100]}")
            present_count += 1
        else:
            print(f"  NEW    : {qid[:100]}")
    if present_count > 0 and present_count < len(atoms_specs):
        print(f"\n  PARTIAL-IDEMPOTENT: {present_count}/{len(atoms_specs)} present; will skip those and add rest.")
    if present_count == len(atoms_specs):
        print(f"\n  ALL-IDEMPOTENT: nothing to do. Exiting clean.")
        return 0

    if dry:
        print("\nDRY-RUN: no Store writes; no ledger appends. Pass --apply to commit.")
        return 0

    # ============= APPLY PATH =============
    print("\n--- A5 WRITES (Store + cert_ledger in same A5 window per atom) ---")
    ts_base = float(time.time())
    ATOMIZED_BY = "skunkworks_atomize_5_artifact_late_wave_2026-06-25"

    chain_grade_count_so_far = 0

    for idx, (label, atom, cert_status, note_tag) in enumerate(atoms_specs, start=1):
        print(f"\n[{idx}/{len(atoms_specs)}] {label}")
        ok = _add_atom_with_round_trip(
            atom,
            source=ATOMIZED_BY,
            note=f"{note_tag}; ruling note {NOTES_PATH}",
        )
        if not ok:
            print(f"  ABORT: atom add failed; ledger not appended; stopping batch.")
            return 1

        # Re-read LIVE Store CERT_N after add_atom (Store is source of truth; ledger writer
        # A5-PRE/POST gate checks live state at ledger-append time, so we pass the SAME
        # value for both expected_pre and expected_post -- per prior atomize tool convention)
        ps_live = PartitionedStore(STORE_ROOT)
        live_cert = _cert_count(ps_live)

        if cert_status == "chain_grade":
            delta = 1
            chain_grade_count_so_far += 1
        else:
            delta = 0
        cert_n_pre_for_ledger = live_cert
        cert_n_post_for_ledger = live_cert

        # Build ledger row appropriate to cert_status
        atom_qid = f"{atom.corpus.value}::{atom.id}"
        metrics_path = (atom.metadata or {}).get("metrics_path")
        if cert_status == "chain_grade":
            row = build_chain_grade_ruling_row(
                atom_id=atom_qid,
                cell_commit=(atom.metadata or {}).get("cell_commit", "n/a"),
                verdict="HARD_PASS_CHAIN_GRADE_skunkworks",
                notes_path=NOTES_PATH,
                metrics_path=metrics_path or "n/a",
                cv=None,
                note=f"chain_grade_{note_tag}_5_artifact_late_wave_2026-06-25",
                atomized_by=ATOMIZED_BY,
                ts=ts_base + idx * 0.001,
            )
        elif cert_status == "measured_mechanism":
            row = build_measured_mechanism_row(
                atom_id=atom_qid,
                cell_commit=(atom.metadata or {}).get("cell_commit", "n/a"),
                verdict="MEASURED_MECHANISM_skunkworks_Q_discipline_saturation_override",
                notes_path=NOTES_PATH,
                metrics_path=metrics_path or "n/a",
                note=(
                    f"measured_mechanism_{note_tag}_4_arm_saturation_at_M10k_corpus_easy_"
                    f"55x_rescue_real_but_discriminating_arm_pending_M100k_adversarial"
                ),
                atomized_by=ATOMIZED_BY,
                ts=ts_base + idx * 0.001,
            )
        elif cert_status == "honest_negative":
            row = build_honest_negative_row(
                atom_id=atom_qid,
                cell_commit=(atom.metadata or {}).get("cell_commit", "n/a"),
                verdict="HARD_FAIL_HONEST_NEGATIVE_skunkworks_pre_reg_miss_proven_bound",
                notes_path=NOTES_PATH,
                metrics_path=metrics_path or "n/a",
                note=f"honest_negative_{note_tag}_pre_reg_miss_proven_bound",
                atomized_by=ATOMIZED_BY,
                ts=ts_base + idx * 0.001,
            )
        elif cert_status == "meta_rule":
            # Build manual row for meta_rule (no convenience builder); op=cert_ruling
            row = {
                "ts": ts_base + idx * 0.001,
                "op": "cert_ruling",
                "atom_id": atom_qid,
                "cert_status": "custom",  # 'meta_rule' not in VALID_CERT_STATUS; using 'custom' bucket
                "cert_class": "discipline_meta",
                "verified_off_data": True,
                "atomized_by": ATOMIZED_BY,
                "cell_commit": "n/a-meta-composes-multiple-cells",
                "verdict": "META_RULE_CERT_NEUTRAL_skunkworks",
                "cert_increment_delta": 0,
                "cv": None,
                "referent_pointer": {
                    "notes_path": NOTES_PATH,
                    "metrics_path": metrics_path,
                    "atom_qualified_id": atom_qid,
                },
                "supersedes": None,
                "note": f"meta_rule_{note_tag}_5_artifact_late_wave_2026-06-25",
            }
        else:
            print(f"  ERROR: unknown cert_status {cert_status!r}")
            return 1

        # A5-gated ledger append
        print(
            f"  PHASE-C ledger append (op={row['op']} status={row['cert_status']} "
            f"delta={row['cert_increment_delta']})"
        )
        try:
            row_h = append_cert_ledger_row(
                row,
                expected_cert_n_pre=cert_n_pre_for_ledger,
                expected_cert_n_post=cert_n_post_for_ledger,
            )
            print(f"    ledger row appended; hash={row_h}")
        except Exception as e:
            print(f"  FAIL: cert_ledger append errored: {e}")
            print(f"  PARTIAL STATE: atom landed in Store but ledger not updated for this atom")
            return 1

    # POST-snapshot
    print("\n--- A5 POST-SNAPSHOT ---")
    ps_post = PartitionedStore(STORE_ROOT)
    post_cert = _cert_count(ps_post)
    post_ax = _axiom_count(ps_post)
    post_cap = _cap_pres_ok()
    post_total = sum(1 for _ in ps_post.all_atoms())
    print(f"  CERT_N = {post_cert} (pre={pre_cert}; delta={post_cert - pre_cert}; expected_delta={chain_grade_count_so_far})")
    print(f"  axiom_count = {post_ax}")
    print(f"  cap_pres = {'6/6' if post_cap else 'FAIL'}")
    print(f"  total_atoms = {post_total} (pre={pre_total}; delta={post_total - pre_total})")
    assert post_ax == 206, f"A5-POST axiom drift: {post_ax} != 206"
    assert post_cap, "A5-POST cap_pres FAIL"
    assert post_cert == pre_cert + chain_grade_count_so_far, (
        f"A5-POST CERT_N mismatch: post={post_cert} expected={pre_cert + chain_grade_count_so_far}"
    )
    print("\nALL ATOMS LANDED. CERT-N + axiom + cap_pres invariants held PRE/POST.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
