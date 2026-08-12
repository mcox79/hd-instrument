"""Atomize: Skunkworks 6-cell landed-VET batch (2026-06-30).

Six cells off-data verified; ~24 atoms = (6 cells x [3 per-seed + 1 AGG]) + 2 bonus
META rules. CERT delta = 0 net (all MM / HN).

VERIFY-OFF-DATA (.venv Python recompute from local metrics.json, 2026-06-30):

CELL 1 -- multihop v4 GPU 3-seed (seed_7, seed_13, seed_19)
  All 3 seeds: HARD_FAIL with verdict_msg = "SANITY_BREACH: SAT_CORNER (5, 200)
  failed to saturate (top1_part=0.8050 / 0.7700 / 0.8100)".
  TIER: HONEST_NEGATIVE_TEST_DESIGN (same class as ANCHOR 3 v1 masking-failure).
  Same masking issue: SAT_CORNER measures cleanup_search_size NOT depth-survival
  (eff_V_C=200 + part_size=200 means partition oracle is searching the FULL
  effective vocabulary; at this small N_chains+depth the test doesn't isolate the
  binding-survival mechanism). cardinality_ok=12/12 each seed (~2100-2700s elapsed).
  Cross-seed agreement EXCELLENT (3/3 same verdict + same SAT_CORNER fail at same
  cell).

CELL 2 -- TASK_VECTOR v3 3-seed FULL (seed_7, seed_13, seed_19)
  seed_7  : MIDDLE_BAND  K_cliff_min=5 loc=V20_ov0.30  valid=3/9 no_sat=6 nm=0 avg_diff=0.236
  seed_13 : HARD_FAIL   K_cliff_min=3 loc=V50_ov0.00  valid=4/9 no_sat=3 nm=2 avg_diff=0.246 regime_flip=True
  seed_19 : MIDDLE_BAND  K_cliff_min=3 loc=V50_ov0.30  valid=4/9 no_sat=4 nm=1 avg_diff=0.271
  TIER per seed: MM / HN_REGIME_FLIP / MM.
  Cross-seed: K_cliff_min varies (5 vs 3 vs 3); CLIFF LOCATION DIFFERS for each seed.
  AGG TIER: MEASURED_MECHANISM_SEED_UNSTABLE.
  v3 lever (pooled+bootstrap) did not fix seed-instability noted from v2; densification
  is directionally right but K_cliff_min cross-seed range >= 1 step on 8-K-axis (HP gate
  CHAIN_GRADE_K_CLIFF_CI_WIDTH=1).

CELL 3 -- pc_binding_operation_family v1 3-seed (seed_7, seed_13, seed_19)
  *** CORRECTS Director's framing of "substantive negative on uniformity" ***
  All 3 seeds: HARD_FAIL with verdict_msg =
    "HARD_FAIL_GPU_MANDATE_BREACH: FULL run on CPU backend forbidden by Fix #24
     unless HDLAB_QUEUE=local_cpu_queue. Got HDLAB_QUEUE=''. Refusing."
  elapsed_s ~0.10-0.14s; _phase = "gpu_mandate_check"; routed_queue=""
  TIER: HONEST_NEGATIVE_INFRA_DEP (the cell never ran any mechanism work; the
  Director-cited "hadamard + tensor DOMINATED; HRR-conv + FHRR competitive" claim
  is NOT present in this metrics data -- the cell's pre-flight gate caught a
  dispatcher-routing issue before any binding-op comparisons happened).
  Verify-the-referent catch (per META_RULE I).

CELL 4 -- lock_in_amp v3 3-seed FULL (seed_7, seed_13, seed_19)
  seed_7  : MIDDLE_BAND  n_SAT=11/96  n_FLOOR=27  n_ADV=36  n_DISC=93  L_mean=0.520 D_mean=0.199
  seed_13 : MIDDLE_BAND  n_SAT=12/96  n_FLOOR=31  n_ADV=35  n_DISC=94  L_mean=0.522 D_mean=0.208
  seed_19 : MIDDLE_BAND  n_SAT=10/96  n_FLOOR=29  n_ADV=36  n_DISC=92  L_mean=0.522 D_mean=0.209
  TIER per seed: MM each.
  AGG TIER: MM_SAT_REGIME_SHORTFALL_STABLE.
  Cross-seed agreement EXCELLENT: 3/3 MB with hp=[sat=False, floor=True, adv=True,
  discrim=True]; n_SAT range 10-12 (target 20); delta_LD_mean stable 0.31-0.32.
  V3 lever (density not extent) directionally right but SAT_regime shortfall is
  persistent (n_SAT 10-12 vs need 20 across 3 seeds). Lock-in mechanism IS measured
  (advantage regime populated; floor regime populated; discriminating regime > 95%)
  but the (L>=0.95 AND D>=0.95) joint-SAT corner is too narrow at this regime.

CELL 5 -- pc_cleanup_family v1 3-seed FULL (seed_7, seed_13, seed_19)
  All 3 seeds: MIDDLE_BAND_CLEANUP_DIFFERS_BUT_LOW_DISC
    seed_7  : n_disc=9/80   sat=46 hp=8  mb=1 floor=17 fail=8
    seed_13 : n_disc=15/80  sat=40 hp=14 mb=1 floor=17 fail=8
    seed_19 : n_disc=15/80  sat=40 hp=14 mb=1 floor=16 fail=9
  cleanup_tiers cross-seed EXACT MATCH:
    modern_hopfield        -> COMPETITIVE_CLEANUP
    classical_hopfield     -> DOMINATED_CLEANUP
    iterative_cosine       -> COMPETITIVE_CLEANUP
    soft_energy_attractor  -> COMPETITIVE_CLEANUP
  n_pairs_differ=6/6 all 3 seeds (every cleanup-pair differs; mechanism characterized).
  TIER per seed: MM each.
  AGG TIER: MM_CROSS_CLEANUP_CHARACTERIZATION_4_FAMILIES + classical_hopfield_DOMINATED_PROVEN_BOUND.
  Bonus META_RULE candidate: classical_hopfield is DOMINATED at this PC regime
  (M=100, beta=8.0, alpha_soft=0.5, encoder=binary_bipolar) across 3 seeds; downstream
  cells using classical_hopfield at this regime should expect dominance by modern /
  iterative / soft variants. Composes with META_RULE_AT (regime-dependent component-class
  choice).

CELL 6 -- refuse_gate_adaptivity v1 3-seed (seed_7, seed_13, seed_19)
  *** CORRECTS Director's framing of "MIDDLE_BAND_ADAPTIVITY_DIFFERS_BUT_LOW_DISC" ***
  All 3 seeds: SELFTEST_OK with run_mode="selftest" and _phase="selftest_done".
  elapsed_s ~0.14-0.17s each. verdict_msg cites cardinality FULL=48 SMOKE=8 +
  per-family sanity check pass + "AMBIGUOUS: 2/4 distinct family decision tuples".
  TIER: HONEST_NEGATIVE_INFRA_DEP (FULL run never landed).
  The Director-cited claim "4/6 family pairs differ; cal_size_sensitivity=0.0" is
  derived from selftest-only sanity-check data and does NOT represent a full
  phase-diagram measurement. The selftest's "AMBIGUOUS: 2/4 distinct family decision
  tuples" is the only inter-family discrimination signal in the on-disk data.
  Verify-the-referent catch (per META_RULE I).

BONUS META RULES:
  META_RULE_AU: pre-dispatch GPU-mandate routing check (CELL 3 lesson). When a
    cell pre-flights with GPU_MANDATE and the dispatch happens on laptop without
    HDLAB_QUEUE=local_cpu_queue, the cell HARD_FAILs at pre-flight in ~0.1s with
    elapsed_s breach indicating mechanism never ran. Director's framing of these
    results MUST NOT attribute a substantive negative; this is an INFRA-DEP HARD_FAIL.
  META_RULE_AV: selftest_run_mode != full_run_mode (CELL 6 lesson). When metrics.json
    has run_mode="selftest" + _phase="selftest_done" + elapsed_s<1s, this is NOT a
    landed FULL result; the Director must not derive MM/HN/CG framings from selftest
    sanity-check data only. The cell's actual phase-diagram measurements never landed.

CERT N change: live CERT N -> live CERT N + 0 net.
Ledger rows: +24 cert_ruling rows (6 cells x 4) + 2 META rules = +26.
Atoms: 18 experiment_record (cell x seed) + 6 experiment_aggregation_record (cell)
       + 2 methodology_rule = +26.

Run:
  .venv/Scripts/python.exe tools/atomize_skunkworks_6cell_landed_vet_2026-06-30.py           # DRY
  .venv/Scripts/python.exe tools/atomize_skunkworks_6cell_landed_vet_2026-06-30.py --apply   # WRITE
"""
from __future__ import annotations
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(".").resolve()))
from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier
from tools.cert_ledger_writer import (
    append_cert_ledger_row,
    build_honest_negative_row,
    build_measured_mechanism_row,
)


STORE_ROOT = Path("data/substrate_index")
RULING_NOTE = "notes/skunkworks_landed_vet_6cell_batch_2026-06-30.md"  # reference; may not exist
CELL_COMMIT = "n/a-2026-06-30-batch-6cell-landed-vet"
ATOMIZED_BY = "skunkworks_atomize_6cell_landed_vet_2026-06-30"

# ============================================================================
# METRICS PATHS
# ============================================================================
MH_PATH = lambda s: f"data/exp_substrate_multihop_phase_diagram_depth_VC_NChains_v4_seed_{s}/metrics.json"
TV_PATH = lambda s: f"data/exp_substrate_task_vector_K_cliff_phase_diagram_v3_seed_{s}_FULL/metrics.json"
BO_PATH = lambda s: f"data/exp_substrate_pc_binding_operation_family_phase_diagram_v1_seed_{s}/metrics.json"
LI_PATH = lambda s: f"data/exp_substrate_lock_in_amp_phase_diagram_v3_seed_{s}/metrics.json"
PC_PATH = lambda s: f"data/exp_substrate_pc_cleanup_family_phase_diagram_v1_seed_{s}/metrics.json"
RG_PATH = lambda s: f"data/exp_substrate_refuse_gate_adaptivity_phase_diagram_v1_seed_{s}/metrics.json"


# ============================================================================
# CELL 1 -- multihop v4 GPU 3-seed HF (HN_TEST_DESIGN; per-seed + AGG)
# ============================================================================

def _mh_per_seed(seed: int, top1_part: float, elapsed_s: float) -> Atom:
    return Atom(
        id=(
            f"T3/EXP_substrate_multihop_phase_diagram_depth_VC_NChains_v4_seed_{seed}"
            f"_HONEST_NEGATIVE_TEST_DESIGN_SAT_CORNER_5_200_failed_to_saturate_top1_part_"
            f"{str(top1_part).replace('.','p')}_cardinality_12_of_12_ok_same_masking_class_as_ANCHOR_3_v1"
        ),
        name=(
            f"multihop_v4 seed={seed} HARD_FAIL HONEST_NEGATIVE_TEST_DESIGN: SAT_CORNER "
            f"(depth=5, eff_V_C=200) failed to saturate (top1_part={top1_part:.4f}); "
            f"same masking-failure class as ANCHOR 3 v1 (test measures cleanup_search_size "
            f"NOT depth-survival mechanism); cardinality_ok=12/12; elapsed_s={elapsed_s:.0f}"
        ),
        description=(
            f"HONEST_NEGATIVE_TEST_DESIGN (cert-neutral; delta=0). Off-data recompute "
            f"verifies the SAT_CORNER fail is reproducible and identical class to ANCHOR "
            f"3 v1 (cleanup-search-size confound).\n\n"
            f"VERIFY-OFF-DATA (.venv Python, 2026-06-30, single seed={seed}):\n"
            f"  verdict: HARD_FAIL\n"
            f"  verdict_msg: SANITY_BREACH: SAT_CORNER (5, 200) failed to saturate (top1_part={top1_part:.4f})\n"
            f"  run_mode: full, n_seeds: 1, seed: {seed}\n"
            f"  cardinality: 12/12 phase points observed (expected 12). cardinality_ok=True.\n"
            f"  extra.sat_corner_failed=True. extra.cardinality_ok=True.\n"
            f"  elapsed_s={elapsed_s:.2f} (real compute happened; not a pre-flight HF)\n"
            f"  GPU verified: name='NVIDIA GeForce RTX 4060 Ti', max_mem_alloc_mb=5665.78\n"
            f"  (nvml unavailable so gpu_util_pct samples=0; GPU presence confirmed via\n"
            f"   gpu_avail=True and gpu_max_mem_alloc_mb non-zero).\n\n"
            f"WHY HONEST_NEGATIVE_TEST_DESIGN NOT MM:\n"
            f"  The SAT_CORNER discriminator gates 'partition oracle saturates at depth=5 /\n"
            f"  eff_V_C=200' as a sanity check. With part_size=200 and eff_V_C=200 the\n"
            f"  partition oracle's effective search space IS the full candidate set, so\n"
            f"  top1_part = 1.0 would require zero binding noise -- but at N=8192 with\n"
            f"  depth=5 the cumulative binding noise produces top1_part={top1_part:.4f}.\n"
            f"  The test is NOT measuring depth-survival; it's measuring binding fidelity\n"
            f"  in a regime where the cleanup search confounds with the candidate space.\n"
            f"  Same masking class as ANCHOR 3 v1 (metric measured cleanup-search-size not\n"
            f"  multihop). v3 atomization diagnosis already on disk:\n"
            f"  skunkworks_v3_atomization.diagnosis = 'v3 test-design issue: bands derived\n"
            f"  from cone-formula on nominal V_C; v4 sweeps effective_V_C directly' -- but\n"
            f"  v4 inherits the SAT_CORNER design and re-triggers the same HF class.\n\n"
            f"IS THIS A SUBSTANTIVE NEGATIVE? NO -- the mechanism (substrate-baseline,\n"
            f"  partition-oracle, random-partition arms) DID produce clean phase-diagram\n"
            f"  data across 12 phase points; partition_oracle climbs from 0.50-0.55 at\n"
            f"  depth=15/eff_V_C=200 to 0.97-1.00 at depth=5/eff_V_C=16000; substrate_baseline\n"
            f"  shows the expected V_C-dependent saturation. The negative is on the\n"
            f"  SAT_CORNER pre-check, not on the mechanism itself.\n\n"
            f"REMEDIATION: redesign SAT_CORNER to test depth-survival at a regime where\n"
            f"  part_size << eff_V_C (e.g. part_size=200 / eff_V_C >= 16000) where the\n"
            f"  partition oracle is genuinely cleaning up against a much larger candidate\n"
            f"  pool. Per ANCHOR 3 v1 lesson, this should be re-designed in v5 with\n"
            f"  explicit decoupling of (cleanup_search_size) from (depth_survival_test).\n\n"
            f"META_RULE COMPLIANCE:\n"
            f"  META_RULE_H cardinality: 12/12 OK\n"
            f"  META_RULE_J no-silent-except: not applicable (hardening absent in v4 schema)\n"
            f"  META_RULE_K smoke fires: partition-oracle vs random-partition arms_differ\n"
            f"    across all 12 phase points; discriminator FIRES on the mechanism arms,\n"
            f"    but the SANITY_BREACH gates on a test-design pre-check not mechanism\n"
            f"  META_RULE_L not-band-floor: mechanism arms are above-floor (random=0.0,\n"
            f"    substrate climbs with V_C); but verdict triggered on sanity gate.\n"
            f"  META_RULE_AF arms_differ_sha256: TRUE all 12 phase points.\n"
            f"  META_RULE_AU pre-flight gate check: PASSED (cell ran to completion;\n"
            f"    elapsed_s={elapsed_s:.0f}); NOT an INFRA-DEP HF.\n"
        ),
        kind=AtomKind.EXPERIMENT_RECORD,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.MATH,
        algebra=None,
        metadata={
            "provenance_quality": "HONEST_NEGATIVE",
            "cert_status": "honest_negative",
            "cert_class": "test_design_sat_corner_masking_failure",
            "cell_anchor": f"substrate_multihop_phase_diagram_depth_VC_NChains_v4_seed_{seed}",
            "cell_commit": CELL_COMMIT,
            "metrics_path": MH_PATH(seed),
            "ruling_note": RULING_NOTE,
            "verified_off_data": True,
            "run_mode": "full",
            "seed": seed,
            "n_seeds": 1,
            "verdict": "HARD_FAIL",
            "verdict_class": "SANITY_BREACH_SAT_CORNER",
            "top1_part_at_SAT_CORNER": top1_part,
            "sat_corner_depth": 5,
            "sat_corner_eff_V_C": 200,
            "N_DIM": 8192,
            "cardinality_ok": True,
            "n_phase_points": 12,
            "elapsed_s": elapsed_s,
            "same_masking_class_as": "ANCHOR_3_v1",
            "test_design_issue": "SAT_CORNER measures cleanup_search_size not depth_survival",
            "mechanism_data_quality": "clean_phase_diagram_data_arms_differ_partition_oracle_vs_random",
            "remediation": "v5_redesign_SAT_CORNER_decouple_cleanup_search_size_from_depth_survival",
            "cert_increment_delta": 0,
            "atomized_by": ATOMIZED_BY,
        },
    )


def build_atom_mh_seed_7():  return _mh_per_seed(7, 0.8050, 2711.27)
def build_atom_mh_seed_13(): return _mh_per_seed(13, 0.7700, 2135.25)
def build_atom_mh_seed_19(): return _mh_per_seed(19, 0.8100, 2242.59)


def build_atom_mh_agg() -> Atom:
    return Atom(
        id=(
            "T3/EXP_substrate_multihop_phase_diagram_depth_VC_NChains_v4_3seed_CROSS_SEED_AGG"
            "_HONEST_NEGATIVE_TEST_DESIGN_SAT_CORNER_5_200_failed_all_3_seeds_top1_part_0p77_to_0p81_"
            "same_masking_class_as_ANCHOR_3_v1_2026-06-30"
        ),
        name=(
            "multihop_v4 3-seed AGG HONEST_NEGATIVE_TEST_DESIGN: SAT_CORNER (5,200) "
            "fails all 3 seeds (top1_part 0.77 / 0.81 / 0.81); cross-seed agreement 3/3; "
            "same masking-failure class as ANCHOR 3 v1; cardinality_ok 12/12 each seed"
        ),
        description=(
            "Cross-seed aggregation: multihop v4 (depth_VC_NChains) sweep across 3 seeds.\n\n"
            "VERIFY-OFF-DATA (.venv Python, 2026-06-30, all 3 seeds):\n"
            "  seed_7  HF top1_part=0.8050  elapsed_s=2711.27\n"
            "  seed_13 HF top1_part=0.7700  elapsed_s=2135.25\n"
            "  seed_19 HF top1_part=0.8100  elapsed_s=2242.59\n"
            "  Cross-seed: top1_part range [0.77, 0.81]; spread 0.04 (small; seed-stable\n"
            "  test-design fail, not seed-noise).\n\n"
            "CROSS-SEED AGREEMENT: 3/3 seeds same verdict (HF) at same SAT_CORNER cell.\n"
            "All 3 seeds: cardinality_ok=12/12; arms_differ_sha256=True at all 12 phase\n"
            "points; partition_oracle vs random-partition discriminator FIRES across all\n"
            "12 phase points each seed. The mechanism IS producing measurable data; the\n"
            "negative is on the SAT_CORNER pre-check that fails for the same test-design\n"
            "reason at every seed.\n\n"
            "AGG TIER: HONEST_NEGATIVE_TEST_DESIGN (delta=0; same as per-seed).\n"
            "Same masking-failure class as ANCHOR 3 v1 (metric measured cleanup_search_size\n"
            "not depth-survival). v4 inherits the SAT_CORNER design from v3 atomization\n"
            "and re-triggers the same HF on the pre-check.\n\n"
            "WHY NOT MM: the test-design pre-check fails; mechanism data is clean and\n"
            "informative (partition_oracle climbs 0.50-0.55 at depth=15/eff_V_C=200 ->\n"
            "0.97-1.00 at depth=5/eff_V_C=16000 across seeds; substrate_baseline shows\n"
            "expected V_C-dependent saturation) but the HF verdict gates on a sanity\n"
            "check that should be re-designed in v5.\n\n"
            "DOES NOT BURN CERT NEUTRALITY: this is a clean HONEST_NEGATIVE characterization\n"
            "of a TEST-DESIGN issue with concrete remediation path (decouple cleanup-search\n"
            "size from depth-survival test).\n\n"
            "COMPOSES_WITH: math::T3/EXP_substrate_multihop_phase_diagram_depth_VC_NChains_v4_seed_{7,13,19}\n"
            "  (3 per-seed atoms in this batch)\n\n"
            "REMEDIATION CLAUSE: v5 SHOULD test SAT_CORNER at a regime with part_size <<\n"
            "  eff_V_C (e.g. part_size=200 / eff_V_C >= 16000) where partition oracle has\n"
            "  meaningful cleanup work to do; the v5 multihop selftest dirs are already\n"
            "  pre-created on disk so re-design path is queued.\n"
        ),
        kind=AtomKind.EXPERIMENT_AGGREGATION_RECORD,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.MATH,
        algebra=None,
        metadata={
            "provenance_quality": "HONEST_NEGATIVE",
            "cert_status": "honest_negative",
            "cert_class": "cross_seed_agg_test_design_sat_corner_masking_failure",
            "cell_anchor_family": "substrate_multihop_phase_diagram_depth_VC_NChains_v4",
            "cell_commit": CELL_COMMIT,
            "metrics_paths": [MH_PATH(s) for s in (7, 13, 19)],
            "ruling_note": RULING_NOTE,
            "verified_off_data": True,
            "seeds": [7, 13, 19],
            "n_seeds": 3,
            "verdict_per_seed": {"7": "HARD_FAIL", "13": "HARD_FAIL", "19": "HARD_FAIL"},
            "top1_part_per_seed": {"7": 0.8050, "13": 0.7700, "19": 0.8100},
            "top1_part_range": [0.7700, 0.8100],
            "top1_part_spread": 0.04,
            "cross_seed_agreement": "3_of_3_same_verdict_same_sat_corner_fail",
            "cardinality_ok_per_seed": [True, True, True],
            "n_phase_points_per_seed": [12, 12, 12],
            "elapsed_s_per_seed": [2711.27, 2135.25, 2242.59],
            "same_masking_class_as": "ANCHOR_3_v1",
            "remediation_clause": "v5_redesign_SAT_CORNER_decouple_cleanup_search_size_from_depth_survival",
            "composes_with_per_seed_atoms": [
                f"math::T3/EXP_substrate_multihop_phase_diagram_depth_VC_NChains_v4_seed_{s}_HONEST_NEGATIVE_TEST_DESIGN_SAT_CORNER_5_200_failed_to_saturate_top1_part_*"
                for s in (7, 13, 19)
            ],
            "cert_increment_delta": 0,
            "atomized_by": ATOMIZED_BY,
        },
    )


# ============================================================================
# CELL 2 -- TASK_VECTOR v3 3-seed FULL (MM / HN / MM; AGG = MM_SEED_UNSTABLE)
# ============================================================================

TV_PER_SEED = {
    7:  {"verdict": "MIDDLE_BAND", "K_cliff_min": 5, "loc": "V20_ov0.30", "valid": 3, "no_sat": 6, "nm": 0, "avg_diff": 0.236, "regime_flip": False, "elapsed_s": 163.05, "tier_class": "MM"},
    13: {"verdict": "HARD_FAIL",   "K_cliff_min": 3, "loc": "V50_ov0.00", "valid": 4, "no_sat": 3, "nm": 2, "avg_diff": 0.246, "regime_flip": True,  "elapsed_s": 145.05, "tier_class": "HN"},
    19: {"verdict": "MIDDLE_BAND", "K_cliff_min": 3, "loc": "V50_ov0.30", "valid": 4, "no_sat": 4, "nm": 1, "avg_diff": 0.271, "regime_flip": False, "elapsed_s": 173.50, "tier_class": "MM"},
}


def _tv_per_seed(seed: int) -> Atom:
    s = TV_PER_SEED[seed]
    is_hn = s["tier_class"] == "HN"
    return Atom(
        id=(
            f"T3/EXP_substrate_task_vector_K_cliff_phase_diagram_v3_FULL_seed_{seed}_"
            f"{'HONEST_NEGATIVE_REGIME_FLIP' if is_hn else 'MEASURED_MECHANISM'}_"
            f"K_cliff_min_{s['K_cliff_min']}_loc_{s['loc'].replace('.','p')}_"
            f"valid_{s['valid']}_of_9_avg_arms_diff_{str(round(s['avg_diff'],3)).replace('.','p')}_2026-06-30"
        ),
        name=(
            f"task_vector v3 seed={seed} {s['verdict']}: K_cliff_min={s['K_cliff_min']} at "
            f"{s['loc']}; valid={s['valid']}/9 no_sat={s['no_sat']} non_monotonic={s['nm']} "
            f"avg_arms_diff={s['avg_diff']:.3f}; regime_flip={s['regime_flip']}; "
            f"{'HN' if is_hn else 'MM'} per Fix #28 under-claim default"
        ),
        description=(
            f"{'HONEST_NEGATIVE_REGIME_FLIP' if is_hn else 'MEASURED_MECHANISM'} "
            f"(cert-neutral; delta=0). Off-data recompute from v3 chunked-per-seed FULL.\n\n"
            f"VERIFY-OFF-DATA (.venv Python, 2026-06-30, seed={seed}):\n"
            f"  verdict: {s['verdict']}\n"
            f"  K_cliff_min: {s['K_cliff_min']} at location_key={s['loc']}\n"
            f"  slice counts: valid={s['valid']}/9 no_sat={s['no_sat']} non_monotonic={s['nm']}\n"
            f"  avg_arms_diff: {s['avg_diff']:.4f} (HP_AVG_ARMS_DIFF_MIN=0.20)\n"
            f"  regime_flip: {s['regime_flip']}\n"
            f"  cardinality_ok: True (expected_n=10800, observed_n=10800)\n"
            f"  elapsed_s: {s['elapsed_s']:.2f}\n"
            f"  chain_grade_eligible: False\n"
            f"  bootstrap_ci: {{}} (single seed only; aggregation pending)\n\n"
            f"PER-PHASE-POINT TRAJECTORY (verified from summary_per_phase_point_pooled):\n"
            f"  At K=1: TASK_VECTOR_top1_recall_pooled=1.0 in most slices (saturation OK)\n"
            f"  At K_cliff={s['K_cliff_min']}: TV drops below HP_CLIFF_FLOOR_RECALL=0.40\n"
            f"  ORACLE arm: 1.0 across all 72 phase points (oracle ceiling is real)\n"
            f"  RANDOM_VECTOR arm: ~0.0 floor (control)\n"
            f"  arms_diff range: [-1.0, 1.0] -- on seed_13 the regime_flip atom contains\n"
            f"    a negative arms_diff = -1.0 at K=1/V_tasks=20/overlap=0.0 (RANDOM beats\n"
            f"    TASK_VECTOR), which IS the regime_flip discriminator firing.\n\n"
            f"WHY {'HN_REGIME_FLIP' if is_hn else 'MM_REGIME_NARROW'}:\n"
            + (
                "  seed_13 shows regime_flip=True (RANDOM_VECTOR top1=1.0 at K=1/V=20/ov=0\n"
                "  while TASK_VECTOR top1=0.0 SAME phase point) -- arms diverge in the\n"
                "  wrong direction. This is a clean HARD_FAIL on the chain-grade gate;\n"
                "  it doesn't disprove the K_cliff mechanism but it does show the v3\n"
                "  pooled+bootstrap lever did not eliminate seed-dependent regime flips.\n"
                if is_hn else
                "  Mechanism IS measurable (3-4/9 valid K_cliffs; avg_arms_diff > 0.20 HP\n"
                "  floor); but the regime is narrow (3-4/9 valid out of 9 V,overlap combos)\n"
                "  and K_cliff_min varies across seeds (5 vs 3 vs 3), so the cell does NOT\n"
                "  yield a chain-grade K_cliff CI (CHAIN_GRADE_K_CLIFF_CI_WIDTH=1; observed\n"
                "  spread 2 steps on the 8-K axis).\n"
            ) +
            f"\nV3 LEVER ASSESSMENT (pooled_phase_diagram + bootstrap_ci):\n"
            f"  v3 retains v2's monotonic_decay metric; adds pooled phase diagram + 1000\n"
            f"  bootstrap replicates per slice. PER-SEED bootstrap CI not computed in this\n"
            f"  single-seed chunked run (bootstrap_ci={{}}); the 3-seed AGG must compute\n"
            f"  cross-seed CI to assess chain-grade-eligibility properly.\n\n"
            f"COMPOSES_WITH: AGG atom in same batch (3-seed cross-seed aggregation).\n\n"
            f"META_RULE COMPLIANCE:\n"
            f"  META_RULE_H cardinality: 10800/10800 OK\n"
            f"  META_RULE_K smoke fires discriminator: avg_arms_diff={s['avg_diff']:.3f} > 0.20\n"
            f"  META_RULE_L not band-floor: K_cliff_min={s['K_cliff_min']} is real mechanism\n"
            f"    (not by-construction; non-monotonic={s['nm']} flagged separately)\n"
            f"  Fix #28 under-claim default: HN if regime_flip else MM (not chain-grade)\n"
        ),
        kind=AtomKind.EXPERIMENT_RECORD,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.MATH,
        algebra=None,
        metadata={
            "provenance_quality": "HONEST_NEGATIVE" if is_hn else "MEASURED_MECHANISM",
            "cert_status": "honest_negative" if is_hn else "measured_mechanism",
            "cert_class": "regime_flip_seed_failure" if is_hn else "K_cliff_mechanism_regime_narrow",
            "cell_anchor": f"substrate_task_vector_K_cliff_phase_diagram_v3_seed_{seed}",
            "cell_commit": CELL_COMMIT,
            "metrics_path": TV_PATH(seed),
            "ruling_note": RULING_NOTE,
            "verified_off_data": True,
            "run_mode": "full",
            "seed": seed,
            "n_seeds": 1,
            "verdict": s["verdict"],
            "K_cliff_min": s["K_cliff_min"],
            "K_cliff_location": s["loc"],
            "n_valid_cliffs": s["valid"],
            "n_no_saturation_slices": s["no_sat"],
            "n_non_monotonic_slices": s["nm"],
            "n_combos_total": 9,
            "avg_arms_diff": s["avg_diff"],
            "regime_flip": s["regime_flip"],
            "elapsed_s": s["elapsed_s"],
            "cardinality_ok": True,
            "expected_n": 10800,
            "observed_n": 10800,
            "N_DIM": 8192,
            "n_queries_full": 50,
            "K_axis": [1, 3, 5, 10, 20, 50, 100, 200],
            "V_tasks_axis": [10, 20, 50],
            "overlap_axis": [0.0, 0.3, 0.6],
            "v3_lever": "pooled_phase_diagram_plus_bootstrap_ci",
            "v3_lever_assessment": "did_not_fix_seed_instability_K_cliff_min_varies_5_to_3_across_seeds",
            "chain_grade_eligible": False,
            "cert_increment_delta": 0,
            "atomized_by": ATOMIZED_BY,
        },
    )


def build_atom_tv_seed_7():  return _tv_per_seed(7)
def build_atom_tv_seed_13(): return _tv_per_seed(13)
def build_atom_tv_seed_19(): return _tv_per_seed(19)


def build_atom_tv_agg() -> Atom:
    return Atom(
        id=(
            "T3/EXP_substrate_task_vector_K_cliff_phase_diagram_v3_3seed_CROSS_SEED_AGG"
            "_MEASURED_MECHANISM_SEED_UNSTABLE_K_cliff_min_5_or_3_loc_differs_per_seed"
            "_2of3_MIDDLE_BAND_1of3_HARD_FAIL_regime_flip_seed_13_2026-06-30"
        ),
        name=(
            "task_vector v3 3-seed AGG MEASURED_MECHANISM_SEED_UNSTABLE: 2/3 MB + 1/3 HF "
            "(seed_13 regime_flip); K_cliff_min cross-seed [3,3,5]; location differs per "
            "seed (V20_ov0.30 / V50_ov0.00 / V50_ov0.30); v3 lever did not fix seed-instability"
        ),
        description=(
            "Cross-seed aggregation: task-vector K_cliff phase diagram v3 across 3 seeds.\n\n"
            "VERIFY-OFF-DATA (.venv Python, 2026-06-30):\n"
            "  seed_7  MB  K_cliff_min=5 V20_ov0.30 valid=3/9 avg_diff=0.236 regime_flip=False\n"
            "  seed_13 HF  K_cliff_min=3 V50_ov0.00 valid=4/9 avg_diff=0.246 regime_flip=True\n"
            "  seed_19 MB  K_cliff_min=3 V50_ov0.30 valid=4/9 avg_diff=0.271 regime_flip=False\n"
            "  Cross-seed K_cliff_min: [3, 3, 5] (range 2 steps; HP_CHAIN_GRADE_K_CLIFF_CI_WIDTH=1)\n"
            "  Cross-seed valid_cliffs: [3, 4, 4]/9 -- regime is narrow\n"
            "  Cross-seed avg_arms_diff: [0.236, 0.246, 0.271] -- all above HP floor 0.20\n"
            "  Cross-seed K_cliff location: ALL THREE DIFFERENT (V20_ov0.30 vs V50_ov0.00 vs V50_ov0.30)\n\n"
            "AGG TIER: MEASURED_MECHANISM_SEED_UNSTABLE (cert-neutral; delta=0).\n"
            "Mechanism IS measurable (avg_arms_diff above floor; K_cliff dynamics present;\n"
            "ORACLE arm at 1.0 across all phase points = sanity check holds) but:\n"
            "  (a) K_cliff_min CI WIDTH = 2 steps on 8-K log axis (need <= 1)\n"
            "  (b) Cliff location DIFFERS for each seed (no agreement on where the cliff is)\n"
            "  (c) 1/3 seeds shows regime_flip (RANDOM > TASK_VECTOR at K=1) on seed_13\n"
            "  (d) bootstrap_ci empty per seed (single-seed chunked runs; cross-seed CI not\n"
            "      computed in cell output)\n\n"
            "WHY MM NOT CHAIN_GRADE: the v3 lever (pooled phase diagram + 1000 bootstrap\n"
            "replicates) was directionally right (densification + bootstrap = correct\n"
            "approach to seed-noise) but did NOT eliminate seed-instability at this regime.\n"
            "The K_cliff mechanism is CHARACTERIZED across seeds; the chain-grade promotion\n"
            "path requires a v4 cell that closes the seed-stability gap (e.g. higher\n"
            "n_queries_full, finer K-axis resolution, OR explicit seed-stability metric\n"
            "as part of the HP gate).\n\n"
            "DOWNGRADE FROM DIRECTOR FRAMING: Director framed 'precision densification\n"
            "didn't fix seed-instability' which IS correct as MM characterization but\n"
            "Skunkworks under-claims (Fix #28 default) to MEASURED_MECHANISM_SEED_UNSTABLE\n"
            "with seed_13 explicitly noted as HF_REGIME_FLIP rather than rolled into AGG.\n\n"
            "COMPOSES_WITH:\n"
            "  math::T3/EXP_substrate_task_vector_K_cliff_phase_diagram_v3_FULL_seed_7_MEASURED_MECHANISM_*\n"
            "  math::T3/EXP_substrate_task_vector_K_cliff_phase_diagram_v3_FULL_seed_13_HONEST_NEGATIVE_REGIME_FLIP_*\n"
            "  math::T3/EXP_substrate_task_vector_K_cliff_phase_diagram_v3_FULL_seed_19_MEASURED_MECHANISM_*\n"
        ),
        kind=AtomKind.EXPERIMENT_AGGREGATION_RECORD,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.MATH,
        algebra=None,
        metadata={
            "provenance_quality": "MEASURED_MECHANISM",
            "cert_status": "measured_mechanism",
            "cert_class": "cross_seed_agg_seed_unstable_mechanism_characterized",
            "cell_anchor_family": "substrate_task_vector_K_cliff_phase_diagram_v3",
            "cell_commit": CELL_COMMIT,
            "metrics_paths": [TV_PATH(s) for s in (7, 13, 19)],
            "ruling_note": RULING_NOTE,
            "verified_off_data": True,
            "seeds": [7, 13, 19],
            "n_seeds": 3,
            "verdict_per_seed": {"7": "MIDDLE_BAND", "13": "HARD_FAIL", "19": "MIDDLE_BAND"},
            "K_cliff_min_per_seed": {"7": 5, "13": 3, "19": 3},
            "K_cliff_min_range": [3, 5],
            "K_cliff_min_ci_width_steps": 2,
            "K_cliff_min_ci_target_max_steps": 1,
            "K_cliff_location_per_seed": {"7": "V20_ov0.30", "13": "V50_ov0.00", "19": "V50_ov0.30"},
            "K_cliff_location_cross_seed_agreement": False,
            "valid_cliffs_per_seed": {"7": 3, "13": 4, "19": 4},
            "avg_arms_diff_per_seed": {"7": 0.236, "13": 0.246, "19": 0.271},
            "regime_flip_per_seed": {"7": False, "13": True, "19": False},
            "seed_unstable": True,
            "chain_grade_eligible": False,
            "v3_lever_assessment": "directionally_right_pooled_plus_bootstrap_did_not_close_seed_stability_gap",
            "promotion_path": "v4_cell_with_higher_n_queries_OR_finer_K_axis_OR_explicit_seed_stability_HP_gate",
            "cert_increment_delta": 0,
            "atomized_by": ATOMIZED_BY,
        },
    )


# ============================================================================
# CELL 3 -- pc_binding_operation_family v1 3-seed (HN_INFRA_DEP; per-seed + AGG)
# *** CORRECTS Director framing ***
# ============================================================================

def _bo_per_seed(seed: int, elapsed_s: float) -> Atom:
    return Atom(
        id=(
            f"T3/EXP_substrate_pc_binding_operation_family_phase_diagram_v1_seed_{seed}_"
            f"HONEST_NEGATIVE_INFRA_DEP_GPU_MANDATE_BREACH_routed_queue_empty_no_mechanism_ran_"
            f"elapsed_s_{str(elapsed_s).replace('.','p')}_2026-06-30"
        ),
        name=(
            f"pc_binding_op_family v1 seed={seed} HONEST_NEGATIVE_INFRA_DEP: "
            f"HARD_FAIL_GPU_MANDATE_BREACH at pre-flight (routed_queue=''); "
            f"NO mechanism ran (elapsed_s={elapsed_s:.2f}); CORRECTS Director's "
            f"substantive-negative framing -- the cell never produced binding-op data"
        ),
        description=(
            f"HONEST_NEGATIVE_INFRA_DEP (cert-neutral; delta=0). VERIFY-THE-REFERENT catch:\n"
            f"Director's framing of 'substantive negative; hadamard + tensor DOMINATED;\n"
            f"HRR-conv + FHRR competitive' is NOT present in this on-disk metrics data.\n"
            f"The cell pre-flight gate caught HDLAB_QUEUE='' and refused to run.\n\n"
            f"VERIFY-OFF-DATA (.venv Python, 2026-06-30, seed={seed}):\n"
            f"  verdict: HARD_FAIL\n"
            f"  verdict_msg: HARD_FAIL_GPU_MANDATE_BREACH: FULL run on CPU backend forbidden\n"
            f"    by Fix #24 unless HDLAB_QUEUE=local_cpu_queue. Got HDLAB_QUEUE=''. Refusing.\n"
            f"  _phase: gpu_mandate_check\n"
            f"  backend: torch.cpu\n"
            f"  routed_queue: ''\n"
            f"  run_mode: full\n"
            f"  elapsed_s: {elapsed_s:.2f} (pre-flight HF; mechanism NEVER executed)\n"
            f"  config: bindings=[circular_convolution, element_wise_fhrr, hadamard_real,\n"
            f"    outer_product_tensor] x N=[1024, 4096, 8192] x corruption=[.10, .25, .40, .475]\n"
            f"    expected_n_full=48; expected_n_smoke=12\n\n"
            f"WHY NO SUBSTANTIVE NEGATIVE:\n"
            f"  The cell's pre-flight gate (Fix #24 GPU-mandate check) fires at the\n"
            f"  START of the run. No binding-op comparisons, no phase-diagram measurements,\n"
            f"  no MECHANISM arm vs RANDOM_FLOOR arm runs occurred. The metrics file is\n"
            f"  the PRE-FLIGHT_FAILURE artifact only. Any claim about which binding\n"
            f"  operations DOMINATED others is unsubstantiated by this data.\n\n"
            f"VERIFY-THE-REFERENT CATCH (per META_RULE I):\n"
            f"  Director's spawn prompt framed this as 'substantive negative on uniformity\n"
            f"  claim; hadamard + tensor DOMINATED; HRR-conv + FHRR competitive'. That\n"
            f"  framing must come from an OTHER cell (likely the _smoke companion run or\n"
            f"  a different binding-family cell). The 3 metrics.json files for the FULL\n"
            f"  seeds 7/13/19 contain ONLY the GPU-mandate breach + zero-elapsed pre-flight.\n\n"
            f"REMEDIATION: re-dispatch via hdi_orchestrator with HDLAB_QUEUE=local_cpu_queue\n"
            f"  OR via remote GPU queue; the cell IS authored and the binding-op comparison\n"
            f"  is a valid Stage-2 component-substitution question that should land.\n\n"
            f"META_RULE COMPLIANCE:\n"
            f"  META_RULE_I verify-the-referent: APPLIED (corrects Director framing)\n"
            f"  META_RULE_AU pre-flight GPU-mandate routing check: FIRED (this atom is\n"
            f"    the audit-log of that fire; downstream META_RULE proposal added)\n"
            f"  cardinality_ok: not applicable (run never started)\n"
        ),
        kind=AtomKind.EXPERIMENT_RECORD,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.MATH,
        algebra=None,
        metadata={
            "provenance_quality": "HONEST_NEGATIVE",
            "cert_status": "honest_negative",
            "cert_class": "infra_dep_gpu_mandate_breach_pre_flight_no_mechanism_ran",
            "cell_anchor": f"substrate_pc_binding_operation_family_phase_diagram_v1_seed_{seed}",
            "cell_commit": CELL_COMMIT,
            "metrics_path": BO_PATH(seed),
            "ruling_note": RULING_NOTE,
            "verified_off_data": True,
            "run_mode": "full",
            "seed": seed,
            "verdict": "HARD_FAIL",
            "verdict_class": "GPU_MANDATE_BREACH",
            "_phase_at_fail": "gpu_mandate_check",
            "backend_when_failed": "torch.cpu",
            "routed_queue_when_failed": "",
            "elapsed_s": elapsed_s,
            "mechanism_executed": False,
            "phase_diagram_data_collected": False,
            "director_framing_corrected": True,
            "director_framing_corrected_claim": "hadamard_tensor_DOMINATED_HRR_conv_FHRR_competitive_NOT_substantiated_by_this_metrics",
            "verify_the_referent_meta_rule_I": "APPLIED",
            "remediation": "re_dispatch_via_hdi_orchestrator_with_HDLAB_QUEUE_set_or_remote_GPU_queue",
            "cert_increment_delta": 0,
            "atomized_by": ATOMIZED_BY,
        },
    )


def build_atom_bo_seed_7():  return _bo_per_seed(7, 0.14)
def build_atom_bo_seed_13(): return _bo_per_seed(13, 0.12)
def build_atom_bo_seed_19(): return _bo_per_seed(19, 0.10)


def build_atom_bo_agg() -> Atom:
    return Atom(
        id=(
            "T3/EXP_substrate_pc_binding_operation_family_phase_diagram_v1_3seed_CROSS_SEED_AGG_"
            "HONEST_NEGATIVE_INFRA_DEP_GPU_MANDATE_BREACH_all_3_seeds_no_mechanism_ran_"
            "CORRECTS_DIRECTOR_FRAMING_2026-06-30"
        ),
        name=(
            "pc_binding_op_family v1 3-seed AGG HONEST_NEGATIVE_INFRA_DEP: 3/3 seeds "
            "HF_GPU_MANDATE_BREACH at pre-flight; total elapsed_s ~0.4s; mechanism never "
            "executed in ANY seed; CORRECTS Director's 'substantive negative; hadamard/tensor "
            "DOMINATED' framing (claim not substantiated by on-disk data)"
        ),
        description=(
            "Cross-seed aggregation: pc_binding_operation_family v1 across 3 seeds.\n\n"
            "VERIFY-OFF-DATA (.venv Python, 2026-06-30):\n"
            "  seed_7  HF  elapsed_s=0.14 _phase=gpu_mandate_check routed_queue=''\n"
            "  seed_13 HF  elapsed_s=0.12 _phase=gpu_mandate_check routed_queue=''\n"
            "  seed_19 HF  elapsed_s=0.10 _phase=gpu_mandate_check routed_queue=''\n"
            "  Cross-seed: 3/3 same INFRA-DEP HF at exact same pre-flight gate.\n"
            "  Total compute: 0.36 sec; no mechanism arms executed in any seed.\n\n"
            "AGG TIER: HONEST_NEGATIVE_INFRA_DEP (delta=0).\n\n"
            "VERIFY-THE-REFERENT (per META_RULE I): CORRECTS Director's framing of\n"
            "  'substantive negative on uniformity; hadamard + tensor DOMINATED; HRR-conv +\n"
            "  FHRR competitive'. That claim cannot be substantiated by these metrics --\n"
            "  the on-disk artifacts are pre-flight failure stubs only. Director should\n"
            "  cross-check whether the framing is from a SMOKE companion cell or an EARLIER\n"
            "  iteration of this anchor before re-asserting the negative.\n\n"
            "REMEDIATION: re-dispatch all 3 seeds via hdi_orchestrator with HDLAB_QUEUE\n"
            "  correctly set OR via overnight_queue on the remote GPU machine. The binding-op\n"
            "  comparison IS a valid Stage-2 component-substitution question (hadamard vs\n"
            "  HRR vs FHRR vs tensor) and should land cleanly once the routing is fixed.\n\n"
            "COMPOSES_WITH (3 per-seed atoms; all HN_INFRA_DEP):\n"
            "  math::T3/EXP_substrate_pc_binding_operation_family_phase_diagram_v1_seed_{7,13,19}_"
            "HONEST_NEGATIVE_INFRA_DEP_GPU_MANDATE_BREACH_*\n"
        ),
        kind=AtomKind.EXPERIMENT_AGGREGATION_RECORD,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.MATH,
        algebra=None,
        metadata={
            "provenance_quality": "HONEST_NEGATIVE",
            "cert_status": "honest_negative",
            "cert_class": "cross_seed_agg_infra_dep_gpu_mandate_breach",
            "cell_anchor_family": "substrate_pc_binding_operation_family_phase_diagram_v1",
            "cell_commit": CELL_COMMIT,
            "metrics_paths": [BO_PATH(s) for s in (7, 13, 19)],
            "ruling_note": RULING_NOTE,
            "verified_off_data": True,
            "seeds": [7, 13, 19],
            "n_seeds": 3,
            "verdict_per_seed": {"7": "HARD_FAIL", "13": "HARD_FAIL", "19": "HARD_FAIL"},
            "elapsed_s_per_seed": {"7": 0.14, "13": 0.12, "19": 0.10},
            "elapsed_s_total": 0.36,
            "mechanism_executed_per_seed": [False, False, False],
            "director_framing_corrected": True,
            "verify_the_referent_meta_rule_I": "APPLIED_CROSS_SEED",
            "remediation": "re_dispatch_via_hdi_orchestrator_with_HDLAB_QUEUE_set_or_remote_GPU_queue",
            "cert_increment_delta": 0,
            "atomized_by": ATOMIZED_BY,
        },
    )


# ============================================================================
# CELL 4 -- lock_in_amp v3 3-seed FULL (MM each + AGG = MM_SAT_REGIME_SHORTFALL)
# ============================================================================

LI_PER_SEED = {
    7:  {"n_SAT": 11, "n_FLOOR": 27, "n_ADV": 36, "n_DISC": 93, "L_mean": 0.520, "D_mean": 0.199, "floor_mean": 0.014, "dLD_mean": 0.321, "elapsed_s": 1016.04},
    13: {"n_SAT": 12, "n_FLOOR": 31, "n_ADV": 35, "n_DISC": 94, "L_mean": 0.522, "D_mean": 0.208, "floor_mean": 0.012, "dLD_mean": 0.314, "elapsed_s": 1038.49},
    19: {"n_SAT": 10, "n_FLOOR": 29, "n_ADV": 36, "n_DISC": 92, "L_mean": 0.522, "D_mean": 0.209, "floor_mean": 0.009, "dLD_mean": 0.314, "elapsed_s": 910.91},
}


def _li_per_seed(seed: int) -> Atom:
    s = LI_PER_SEED[seed]
    return Atom(
        id=(
            f"T3/EXP_substrate_lock_in_amp_phase_diagram_v3_seed_{seed}_FULL_MEASURED_MECHANISM_"
            f"SAT_regime_shortfall_n_SAT_{s['n_SAT']}_of_96_target_20_advantage_floor_discriminating_populated_2026-06-30"
        ),
        name=(
            f"lock_in_amp v3 seed={seed} MIDDLE_BAND MEASURED_MECHANISM: n_SAT={s['n_SAT']}/96 "
            f"(target>=20; SAT regime shortfall); n_FLOOR={s['n_FLOOR']} n_ADV={s['n_ADV']} n_DISC={s['n_DISC']}; "
            f"L_mean={s['L_mean']:.3f} delta_LD_mean=+{s['dLD_mean']:.3f}; SNR x t x N grid"
        ),
        description=(
            f"MEASURED_MECHANISM (cert-neutral; delta=0). Lock-in v3 mechanism CHARACTERIZED\n"
            f"at this regime; SAT corner shortfall is the load-bearing barrier to chain-grade.\n\n"
            f"VERIFY-OFF-DATA (.venv Python, 2026-06-30, seed={seed}):\n"
            f"  verdict: MIDDLE_BAND\n"
            f"  verdict_msg: 'phase diagram discriminating at >= 50% but not all 3 regimes\n"
            f"    populated at >= 20%. hp=[sat=False, floor=True, adv=True, discrim=True]'\n"
            f"  n_points: 96 (8 SNR x 4 t x 3 N axes; expected_n_units=96)\n"
            f"  lock_in_recall_mean: {s['L_mean']:.4f} (range [0.0, 1.0] across 96 points)\n"
            f"  direct_recall_mean: {s['D_mean']:.4f}\n"
            f"  floor_recall_mean: {s['floor_mean']:.4f}\n"
            f"  delta_LD_mean: +{s['dLD_mean']:.4f} (lock_in advantage over direct)\n"
            f"  n_SAT (L>=0.95 AND D>=0.95): {s['n_SAT']}/96 (need >= 20)\n"
            f"  n_FLOOR (L<=0.05 AND D<=0.05): {s['n_FLOOR']}/96 (need >= 20)  POPULATED\n"
            f"  n_ADVANTAGE (L-D >= 0.30): {s['n_ADV']}/96 (need >= 20)        POPULATED\n"
            f"  n_DISCRIMINATING: {s['n_DISC']}/96 (need >= 48)                POPULATED\n"
            f"  elapsed_s: {s['elapsed_s']:.2f}\n"
            f"  M_codebook=100, signal_freq=0.1, N_EVAL=30\n"
            f"  axes: SNR=[0.0001..0.1] (8) x t=[10, 100, 1000, 10000] x N=[2048, 4096, 8192]\n\n"
            f"WHY MM NOT CHAIN_GRADE:\n"
            f"  3 of 4 HP regimes populated (FLOOR, ADVANTAGE, DISCRIMINATING) but SAT\n"
            f"  regime (joint L>=0.95 AND D>=0.95 -- where direct readout also wins) is\n"
            f"  SHORTFALL: {s['n_SAT']}/96 vs target 20. This means the v3 lever (density\n"
            f"  not extent) populated the operating-regime phase diagram at the lock-in\n"
            f"  advantage edge correctly, but the joint-saturation corner is too narrow\n"
            f"  to hit the >= 20 floor. Mechanism IS measurable (delta_LD_mean=+{s['dLD_mean']:.3f}\n"
            f"  means lock-in averages 30+ percentage points above direct readout) but\n"
            f"  the chain-grade promotion gate requires all 4 regimes populated >= 20.\n\n"
            f"V3 LEVER ASSESSMENT (density not extent):\n"
            f"  v3 added 30-pt N_EVAL density to v2's coarser sampling; this DID populate\n"
            f"  the advantage and floor regimes (>= 35 each); but SAT regime is structurally\n"
            f"  narrow because joint L>=0.95 AND D>=0.95 requires the high-SNR/long-t corner\n"
            f"  where both methods saturate -- finite at this M_codebook=100 / signal_freq=0.1.\n\n"
            f"PROMOTION PATH (Stage 2 follow-up):\n"
            f"  v4 should EXTEND the SNR axis upward (current max=0.1) or EXTEND t-axis\n"
            f"  upward (current max=10000) to reach the joint-saturation corner. Alternatively\n"
            f"  recalibrate the SAT band thresholds (L>=0.85 AND D>=0.85?) to match\n"
            f"  measurable capacity at this M_codebook.\n\n"
            f"META_RULE COMPLIANCE:\n"
            f"  META_RULE_H cardinality: 96/96 OK\n"
            f"  META_RULE_K discriminator: n_DISCRIMINATING={s['n_DISC']} >> 48 floor (FIRES)\n"
            f"  META_RULE_L band-floor check: lock_in mean=0.52 vs direct mean=0.20 (above-floor)\n"
            f"  META_RULE_S band-calibration regime check: SAT band CALIBRATION ISSUE noted;\n"
            f"    target>=20 may be unrealistic at current M_codebook=100/SNR-axis-max=0.1\n"
        ),
        kind=AtomKind.EXPERIMENT_RECORD,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.MATH,
        algebra=None,
        metadata={
            "provenance_quality": "MEASURED_MECHANISM",
            "cert_status": "measured_mechanism",
            "cert_class": "lock_in_advantage_measured_sat_corner_band_shortfall",
            "cell_anchor": f"substrate_lock_in_amp_phase_diagram_v3_seed_{seed}",
            "cell_commit": CELL_COMMIT,
            "metrics_path": LI_PATH(seed),
            "ruling_note": RULING_NOTE,
            "verified_off_data": True,
            "run_mode": "full",
            "seed": seed,
            "verdict": "MIDDLE_BAND",
            "n_points": 96,
            "n_SAT": s["n_SAT"],
            "n_FLOOR": s["n_FLOOR"],
            "n_ADVANTAGE": s["n_ADV"],
            "n_DISCRIMINATING": s["n_DISC"],
            "SAT_band_target_min": 20,
            "SAT_band_shortfall": 20 - s["n_SAT"],
            "lock_in_recall_mean": s["L_mean"],
            "direct_recall_mean": s["D_mean"],
            "floor_recall_mean": s["floor_mean"],
            "delta_LD_mean": s["dLD_mean"],
            "elapsed_s": s["elapsed_s"],
            "cardinality_ok": True,
            "M_codebook": 100,
            "signal_freq": 0.1,
            "N_EVAL": 30,
            "SNR_axis": [0.0001, 0.0002683, 0.0007197, 0.001931, 0.005179, 0.01389, 0.03728, 0.1],
            "t_axis": [10, 100, 1000, 10000],
            "N_axis": [2048, 4096, 8192],
            "v3_lever": "density_not_extent",
            "v3_lever_assessment": "populated_advantage_and_floor_regimes_but_SAT_corner_structurally_narrow_at_M_100_SNR_max_0p1",
            "chain_grade_eligible": False,
            "promotion_path": "v4_extend_SNR_or_t_axis_upward_OR_recalibrate_SAT_band_thresholds",
            "cert_increment_delta": 0,
            "atomized_by": ATOMIZED_BY,
        },
    )


def build_atom_li_seed_7():  return _li_per_seed(7)
def build_atom_li_seed_13(): return _li_per_seed(13)
def build_atom_li_seed_19(): return _li_per_seed(19)


def build_atom_li_agg() -> Atom:
    return Atom(
        id=(
            "T3/EXP_substrate_lock_in_amp_phase_diagram_v3_3seed_CROSS_SEED_AGG_"
            "MEASURED_MECHANISM_SAT_regime_shortfall_STABLE_n_SAT_10_to_12_of_96_target_20_"
            "delta_LD_mean_0p31_to_0p32_HIGHLY_REPRODUCIBLE_2026-06-30"
        ),
        name=(
            "lock_in_amp v3 3-seed AGG MEASURED_MECHANISM_SAT_REGIME_SHORTFALL_STABLE: "
            "3/3 MB; n_SAT cross-seed [10, 11, 12]/96 target 20; delta_LD_mean cross-seed "
            "stable [0.314, 0.314, 0.321]; lock-in advantage HIGHLY REPRODUCIBLE; SAT-corner "
            "narrowness is regime-stable barrier (v4 axis-extension needed)"
        ),
        description=(
            "Cross-seed aggregation: lock_in_amp v3 across 3 seeds; EXCELLENT cross-seed\n"
            "stability indicates the v3 mechanism is robustly characterized.\n\n"
            "VERIFY-OFF-DATA (.venv Python, 2026-06-30):\n"
            "  seed_7  MB  n_SAT=11 n_FLOOR=27 n_ADV=36 n_DISC=93 L=0.520 D=0.199 dLD=+0.321\n"
            "  seed_13 MB  n_SAT=12 n_FLOOR=31 n_ADV=35 n_DISC=94 L=0.522 D=0.208 dLD=+0.314\n"
            "  seed_19 MB  n_SAT=10 n_FLOOR=29 n_ADV=36 n_DISC=92 L=0.522 D=0.209 dLD=+0.314\n"
            "  Cross-seed n_SAT: [10, 11, 12] (range 2; very stable shortfall)\n"
            "  Cross-seed delta_LD_mean: [0.314, 0.314, 0.321] cv=0.013 (HIGHLY STABLE)\n"
            "  Cross-seed lock_in_recall_mean: [0.520, 0.522, 0.522] cv=0.0023 (STABLE)\n"
            "  Cross-seed n_DISCRIMINATING: [92, 93, 94]/96 (consistently very high)\n\n"
            "AGG TIER: MEASURED_MECHANISM_SAT_REGIME_SHORTFALL_STABLE (cert-neutral; delta=0).\n\n"
            "MECHANISM CHARACTERIZATION (cross-seed):\n"
            "  Lock-in amplifier reliably produces +0.31 average advantage over direct\n"
            "  readout across 3 seeds at M_codebook=100/signal_freq=0.1; the advantage\n"
            "  regime (L-D>=0.30) is populated 35-36/96 points consistently. The\n"
            "  discriminating regime is essentially saturated (92-94/96). FLOOR regime\n"
            "  also populated (27-31/96).\n\n"
            "BARRIER TO CHAIN_GRADE (cross-seed stable):\n"
            "  SAT regime (joint L>=0.95 AND D>=0.95) shortfall is STABLE across seeds\n"
            "  at 10-12/96 vs target 20. This is NOT seed-noise; it's a structural\n"
            "  property of the (SNR, t) axis upper bounds at M_codebook=100. Pushing\n"
            "  SAT-regime populations above 20 requires either extending SNR > 0.1 or\n"
            "  extending t > 10000, OR recalibrating the SAT thresholds to match the\n"
            "  measurable capacity at this M_codebook (per META_RULE_S band-calibration).\n\n"
            "WHY MM NOT CHAIN_GRADE: 3/4 HP regimes populated reliably across seeds;\n"
            "  SAT shortfall is structural not seed-noise; the v3 cell ESTABLISHES the\n"
            "  lock-in advantage at a chain-grade-quality reproducibility level (cv on\n"
            "  delta_LD_mean = 0.013 << HP_CV_MAX=0.15) but does NOT clear the chain-grade\n"
            "  HP gate which requires all 4 regimes >= 20. A v4 with extended axes is\n"
            "  the chain-grade promotion path.\n\n"
            "COMPOSES_WITH:\n"
            "  math::T3/EXP_substrate_lock_in_amp_phase_diagram_v3_seed_{7,13,19}_FULL_MEASURED_MECHANISM_*\n"
        ),
        kind=AtomKind.EXPERIMENT_AGGREGATION_RECORD,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.MATH,
        algebra=None,
        metadata={
            "provenance_quality": "MEASURED_MECHANISM",
            "cert_status": "measured_mechanism",
            "cert_class": "cross_seed_agg_lock_in_advantage_measured_sat_regime_shortfall_stable",
            "cell_anchor_family": "substrate_lock_in_amp_phase_diagram_v3",
            "cell_commit": CELL_COMMIT,
            "metrics_paths": [LI_PATH(s) for s in (7, 13, 19)],
            "ruling_note": RULING_NOTE,
            "verified_off_data": True,
            "seeds": [7, 13, 19],
            "n_seeds": 3,
            "verdict_per_seed": {"7": "MIDDLE_BAND", "13": "MIDDLE_BAND", "19": "MIDDLE_BAND"},
            "n_SAT_per_seed": {"7": 11, "13": 12, "19": 10},
            "n_SAT_range": [10, 12],
            "n_SAT_target_min": 20,
            "n_SAT_cross_seed_stable": True,
            "delta_LD_mean_per_seed": {"7": 0.321, "13": 0.314, "19": 0.314},
            "delta_LD_mean_cross_seed_cv": 0.013,
            "lock_in_recall_mean_per_seed": {"7": 0.520, "13": 0.522, "19": 0.522},
            "lock_in_recall_mean_cross_seed_cv": 0.0023,
            "n_DISCRIMINATING_per_seed": {"7": 93, "13": 94, "19": 92},
            "structural_barrier": "SAT_regime_joint_L_and_D_above_0p95_corner_narrow_at_M_100_SNR_max_0p1",
            "promotion_path": "v4_extend_SNR_or_t_axis_OR_recalibrate_SAT_band_thresholds_META_RULE_S",
            "chain_grade_eligible": False,
            "cert_increment_delta": 0,
            "atomized_by": ATOMIZED_BY,
        },
    )


# ============================================================================
# CELL 5 -- pc_cleanup_family v1 3-seed FULL (MM each + AGG = cross-cleanup MM)
# ============================================================================

PC_PER_SEED = {
    7:  {"n_disc": 9,  "sat": 46, "hp": 8,  "mb": 1, "floor": 17, "fail": 8, "elapsed_s": 16.68},
    13: {"n_disc": 15, "sat": 40, "hp": 14, "mb": 1, "floor": 17, "fail": 8, "elapsed_s": 13.48},
    19: {"n_disc": 15, "sat": 40, "hp": 14, "mb": 1, "floor": 16, "fail": 9, "elapsed_s": 12.12},
}

PC_CLEANUP_TIERS = {
    "modern_hopfield": "COMPETITIVE_CLEANUP",
    "classical_hopfield": "DOMINATED_CLEANUP",
    "iterative_cosine": "COMPETITIVE_CLEANUP",
    "soft_energy_attractor": "COMPETITIVE_CLEANUP",
}


def _pc_per_seed(seed: int) -> Atom:
    s = PC_PER_SEED[seed]
    return Atom(
        id=(
            f"T3/EXP_substrate_pc_cleanup_family_phase_diagram_v1_seed_{seed}_FULL_MEASURED_MECHANISM_"
            f"CROSS_CLEANUP_n_disc_{s['n_disc']}_of_80_n_pairs_differ_6_of_6_classical_hopfield_DOMINATED_"
            f"modern_iterative_soft_COMPETITIVE_2026-06-30"
        ),
        name=(
            f"pc_cleanup_family v1 seed={seed} MIDDLE_BAND MEASURED_MECHANISM: "
            f"n_disc={s['n_disc']}/80 (need 24) n_pairs_differ=6/6; cleanup_tiers: "
            f"modern_hopfield/iterative_cosine/soft_energy_attractor=COMPETITIVE; "
            f"classical_hopfield=DOMINATED; 4-family characterization"
        ),
        description=(
            f"MEASURED_MECHANISM (cert-neutral; delta=0). 4-cleanup-family substitution\n"
            f"phase diagram at PC (predictive coding) regime; cross-family mechanism\n"
            f"differentiation CHARACTERIZED.\n\n"
            f"VERIFY-OFF-DATA (.venv Python, 2026-06-30, seed={seed}):\n"
            f"  verdict: MIDDLE_BAND_CLEANUP_DIFFERS_BUT_LOW_DISC\n"
            f"  n_discriminating: {s['n_disc']}/80 (need >=24)\n"
            f"  n_pairs_differ: 6/6 (every pair of 4 cleanups differs at >=1 phase point)\n"
            f"  phase-point tier counts: sat={s['sat']} hp={s['hp']} mb={s['mb']} floor={s['floor']} fail={s['fail']}\n"
            f"  elapsed_s: {s['elapsed_s']:.2f}\n"
            f"  cardinality: 80/80 (cardinality_ok=True)\n"
            f"  config: alpha_soft=0.5, beta=8.0, encoder=binary_bipolar, M=100\n"
            f"  cleanups=[modern_hopfield, classical_hopfield, iterative_cosine, soft_energy_attractor]\n"
            f"  corpus_provenance: synthetic_substrate_4_cleanup_family_pc\n"
            f"  gpu_util_estimate: 0.95\n\n"
            f"CLEANUP TIERS (verified from metrics.cleanup_tiers):\n"
            f"  modern_hopfield        -> COMPETITIVE_CLEANUP\n"
            f"  classical_hopfield     -> DOMINATED_CLEANUP\n"
            f"  iterative_cosine       -> COMPETITIVE_CLEANUP\n"
            f"  soft_energy_attractor  -> COMPETITIVE_CLEANUP\n\n"
            f"WHY MM NOT CHAIN_GRADE:\n"
            f"  n_pairs_differ=6/6 means every pair of cleanups discriminates SOMEWHERE\n"
            f"  in the 80-point phase space; mechanism IS characterized. But\n"
            f"  n_discriminating={s['n_disc']}/80 < HP floor of 24 (or 24 at higher\n"
            f"  reproducibility seeds; seed_7 lower at 9, seeds 13/19 at 15) means the\n"
            f"  discrimination is not dense enough across the phase diagram. The chain-grade\n"
            f"  gate requires >= 24/80 discriminating; we land at 9-15 across seeds.\n\n"
            f"DOMINATED CLEANUP (cross-seed claim):\n"
            f"  classical_hopfield is DOMINATED in all 3 seeds (cleanup_tiers stable);\n"
            f"  proposes a follow-up META_RULE for downstream cells: at PC regime with\n"
            f"  encoder=binary_bipolar / alpha_soft=0.5 / beta=8.0 / M=100, do NOT default\n"
            f"  to classical_hopfield -- modern/iterative/soft variants are all competitive\n"
            f"  alternatives. (See bonus META_RULE_AW in this batch.)\n\n"
            f"COMPOSES_WITH (META_RULE_AT regime-dependent component-class choice):\n"
            f"  Adds CLEANUP-FAMILY to the 6 component-substitution series (encoder /\n"
            f"  seqbind-encoder / cleanup / routing / binding-op / schema); reinforces\n"
            f"  the H2 regime-mapping rule.\n\n"
            f"META_RULE COMPLIANCE:\n"
            f"  META_RULE_H cardinality: 80/80 OK\n"
            f"  META_RULE_K discriminator: n_pairs_differ=6/6 (every pair differs; FIRES)\n"
            f"  META_RULE_L band-floor: phase-point distribution sat=40+/80 saturation\n"
            f"    region IS by-construction-saturation; floor=16-17/80 chance region;\n"
            f"    discriminating region is the n_disc count\n"
            f"  META_RULE_AT regime-dependent component-class: APPLIES (4-cleanup family)\n"
        ),
        kind=AtomKind.EXPERIMENT_RECORD,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.MATH,
        algebra=None,
        metadata={
            "provenance_quality": "MEASURED_MECHANISM",
            "cert_status": "measured_mechanism",
            "cert_class": "cleanup_family_cross_class_characterization",
            "cell_anchor": f"substrate_pc_cleanup_family_phase_diagram_v1_seed_{seed}",
            "cell_commit": CELL_COMMIT,
            "metrics_path": PC_PATH(seed),
            "ruling_note": RULING_NOTE,
            "verified_off_data": True,
            "run_mode": "full",
            "seed": seed,
            "verdict": "MIDDLE_BAND",
            "verdict_class": "MIDDLE_BAND_CLEANUP_DIFFERS_BUT_LOW_DISC",
            "n_discriminating": s["n_disc"],
            "n_discriminating_target_min": 24,
            "n_pairs_differ": 6,
            "n_pairs_total": 6,
            "phase_point_counts": {"sat": s["sat"], "hp": s["hp"], "mb": s["mb"], "floor": s["floor"], "fail": s["fail"]},
            "expected_n_units": 80,
            "observed_n_units": 80,
            "cardinality_ok": True,
            "elapsed_s": s["elapsed_s"],
            "cleanup_tiers": PC_CLEANUP_TIERS,
            "encoder_fixed": "binary_bipolar",
            "alpha_soft": 0.5,
            "beta": 8.0,
            "M_codebook": 100,
            "corpus_provenance": "synthetic_substrate_4_cleanup_family_pc",
            "gpu_util_estimate": 0.95,
            "chain_grade_eligible": False,
            "composes_with_META_RULE_AT": True,
            "cert_increment_delta": 0,
            "atomized_by": ATOMIZED_BY,
        },
    )


def build_atom_pc_seed_7():  return _pc_per_seed(7)
def build_atom_pc_seed_13(): return _pc_per_seed(13)
def build_atom_pc_seed_19(): return _pc_per_seed(19)


def build_atom_pc_agg() -> Atom:
    return Atom(
        id=(
            "T3/EXP_substrate_pc_cleanup_family_phase_diagram_v1_3seed_CROSS_SEED_AGG_"
            "MEASURED_MECHANISM_4_cleanups_classical_hopfield_DOMINATED_3of3_seeds_"
            "modern_iterative_soft_COMPETITIVE_3of3_seeds_n_pairs_differ_6_of_6_each_seed_"
            "n_disc_9_15_15_of_80_2026-06-30"
        ),
        name=(
            "pc_cleanup_family v1 3-seed AGG MEASURED_MECHANISM: classical_hopfield DOMINATED "
            "in 3/3 seeds; modern/iterative/soft COMPETITIVE in 3/3 seeds; n_pairs_differ=6/6 "
            "per seed; chain-grade discrimination 9-15/80 vs target 24 (regime-narrow)"
        ),
        description=(
            "Cross-seed aggregation: pc_cleanup_family v1 across 3 seeds. EXCELLENT\n"
            "cross-seed agreement on cleanup_tiers; cleanup mechanism characterized at\n"
            "MM quality.\n\n"
            "VERIFY-OFF-DATA (.venv Python, 2026-06-30):\n"
            "  seed_7  MB n_disc=9/80  sat=46 hp=8  mb=1 floor=17 fail=8  elapsed_s=16.68\n"
            "  seed_13 MB n_disc=15/80 sat=40 hp=14 mb=1 floor=17 fail=8  elapsed_s=13.48\n"
            "  seed_19 MB n_disc=15/80 sat=40 hp=14 mb=1 floor=16 fail=9  elapsed_s=12.12\n"
            "  Cross-seed n_disc: [9, 15, 15]/80 (regime-narrow; need >= 24)\n"
            "  Cross-seed n_pairs_differ: [6, 6, 6]/6 (UNANIMOUS discrimination)\n"
            "  cleanup_tiers IDENTICAL across all 3 seeds:\n"
            "    modern_hopfield        -> COMPETITIVE_CLEANUP\n"
            "    classical_hopfield     -> DOMINATED_CLEANUP\n"
            "    iterative_cosine       -> COMPETITIVE_CLEANUP\n"
            "    soft_energy_attractor  -> COMPETITIVE_CLEANUP\n\n"
            "AGG TIER: MEASURED_MECHANISM_CROSS_CLEANUP_FAMILY (cert-neutral; delta=0).\n\n"
            "PROVEN BOUND (cross-seed): classical_hopfield is DOMINATED at this PC regime\n"
            "(encoder=binary_bipolar, alpha_soft=0.5, beta=8.0, M=100) in 3/3 seeds.\n"
            "modern_hopfield, iterative_cosine, and soft_energy_attractor are all\n"
            "COMPETITIVE alternatives. This is the load-bearing cross-cleanup mechanism\n"
            "finding from this cell.\n\n"
            "WHY MM NOT CHAIN_GRADE: cleanup_tiers ARE stable across seeds (perfect\n"
            "agreement); n_pairs_differ is unanimous (6/6 each seed); but n_disc\n"
            "(9-15/80) is below the chain-grade HP floor of 24/80. The chain-grade\n"
            "promotion path requires denser discrimination across the (corruption, iters,\n"
            "N) phase space; smoke-N may be too thin OR the cleanup-substitution mechanism\n"
            "differentiates only in a narrow regime that's under-sampled at this M=100.\n\n"
            "COMPOSES_WITH:\n"
            "  META_RULE_AT (regime-dependent component-class choice; 6th systematic\n"
            "    component-substitution cell adding cleanup family to encoder/seqbind-encoder/\n"
            "    routing/binding-op/schema findings)\n"
            "  META_RULE_AW (proposed in this batch): classical_hopfield DOMINATED at PC\n"
            "    binary_bipolar regime -- don't default to classical_hopfield for PC cleanups\n\n"
            "ADDS to component-substitution series:\n"
            "  pc_encoder_family  ->  encoder regime-mapping\n"
            "  seqbind_encoder_family  ->  encoder regime-mapping\n"
            "  routing_family_WM  ->  WM routing regime-mapping\n"
            "  binding_op_family  ->  binding op regime-mapping (pending; this batch HF infra)\n"
            "  schema_family  ->  schema regime-mapping\n"
            "  cleanup_family_PC  ->  CLEANUP regime-mapping (this cell; new addition)\n"
        ),
        kind=AtomKind.EXPERIMENT_AGGREGATION_RECORD,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.MATH,
        algebra=None,
        metadata={
            "provenance_quality": "MEASURED_MECHANISM",
            "cert_status": "measured_mechanism",
            "cert_class": "cross_seed_agg_cleanup_family_characterization_classical_hopfield_dominated_proven_bound",
            "cell_anchor_family": "substrate_pc_cleanup_family_phase_diagram_v1",
            "cell_commit": CELL_COMMIT,
            "metrics_paths": [PC_PATH(s) for s in (7, 13, 19)],
            "ruling_note": RULING_NOTE,
            "verified_off_data": True,
            "seeds": [7, 13, 19],
            "n_seeds": 3,
            "verdict_per_seed": {"7": "MIDDLE_BAND", "13": "MIDDLE_BAND", "19": "MIDDLE_BAND"},
            "n_disc_per_seed": {"7": 9, "13": 15, "19": 15},
            "n_disc_target_min": 24,
            "n_pairs_differ_per_seed": {"7": 6, "13": 6, "19": 6},
            "cleanup_tiers_cross_seed": PC_CLEANUP_TIERS,
            "cleanup_tiers_unanimous_3_of_3_seeds": True,
            "classical_hopfield_DOMINATED_3_of_3_seeds": True,
            "regime": {
                "encoder_fixed": "binary_bipolar",
                "alpha_soft": 0.5,
                "beta": 8.0,
                "M_codebook": 100,
                "corruption_axis": [0.10, 0.25, 0.40, 0.475],
                "iters_axis": [3],
            },
            "composes_with_META_RULE_AT": True,
            "proposes_META_RULE_AW": True,
            "chain_grade_eligible": False,
            "promotion_path": "denser_phase_space_sampling_OR_higher_M_codebook_to_widen_discriminating_regime",
            "cert_increment_delta": 0,
            "atomized_by": ATOMIZED_BY,
        },
    )


# ============================================================================
# CELL 6 -- refuse_gate_adaptivity v1 3-seed (HN_INFRA_DEP; per-seed + AGG)
# *** CORRECTS Director framing ***
# ============================================================================

def _rg_per_seed(seed: int, elapsed_s: float) -> Atom:
    return Atom(
        id=(
            f"T3/EXP_substrate_refuse_gate_adaptivity_phase_diagram_v1_seed_{seed}_"
            f"HONEST_NEGATIVE_INFRA_DEP_run_mode_selftest_only_FULL_never_landed_"
            f"selftest_AMBIGUOUS_2_of_4_distinct_decision_tuples_2026-06-30"
        ),
        name=(
            f"refuse_gate_adaptivity v1 seed={seed} HONEST_NEGATIVE_INFRA_DEP: "
            f"run_mode='selftest' _phase='selftest_done' elapsed_s={elapsed_s:.2f}; "
            f"FULL never ran; selftest AMBIGUOUS 2/4 family decision tuples is sanity "
            f"check signal not phase-diagram measurement; CORRECTS Director framing"
        ),
        description=(
            f"HONEST_NEGATIVE_INFRA_DEP (cert-neutral; delta=0). VERIFY-THE-REFERENT catch:\n"
            f"Director's framing of 'MIDDLE_BAND_ADAPTIVITY_DIFFERS_BUT_LOW_DISC; 4/6 family\n"
            f"pairs differ; cal_size_sensitivity=0.0' is NOT a FULL-run measurement; the\n"
            f"on-disk metrics are SELFTEST sanity-check data only.\n\n"
            f"VERIFY-OFF-DATA (.venv Python, 2026-06-30, seed={seed}):\n"
            f"  verdict: SELFTEST_OK\n"
            f"  verdict_msg: 'cardinality FULL=48 SMOKE=8; noise_floor FULL=0.0395\n"
            f"    SMOKE=0.0700; sanity fixed_threshold: PURE_IN answer=1.000 PURE_OUT\n"
            f"    refuse=1.000; sanity adaptive_bayesian_CI: ... ; sanity learned_logistic:\n"
            f"    ... ; sanity percentile_based: ... ; AMBIGUOUS: 2/4 distinct family\n"
            f"    decision tuples'\n"
            f"  run_mode: selftest\n"
            f"  _phase: selftest_done\n"
            f"  elapsed_s: {elapsed_s:.2f}\n"
            f"  backend: numpy.cpu\n"
            f"  config: families=[fixed_threshold, adaptive_bayesian_CI, learned_logistic,\n"
            f"    percentile_based]; regimes=[PURE_IN, PURE_OUT, NEAR_DOMAIN_MIXED,\n"
            f"    AMBIGUOUS_BOUNDARY]; cal_sizes=[64, 256, 1024]; V_REL=256\n\n"
            f"WHY HN_INFRA_DEP NOT MM:\n"
            f"  The metrics.json captures SELFTEST output: cardinality counts + noise-floor\n"
            f"  computed across SMOKE/FULL configs + per-family PURE_IN/PURE_OUT sanity\n"
            f"  recall (each at 1.000 = sanity pass at the trivial extremes) + AMBIGUOUS\n"
            f"  regime check showing 2/4 distinct family decision tuples (a self-test\n"
            f"  for whether families CAN differ at the AMBIGUOUS regime; not a measurement\n"
            f"  of HOW MUCH they differ across the full phase diagram). No full-axis sweep,\n"
            f"  no cal_size axis sweep, no NEAR_DOMAIN_MIXED measurement. The FULL run\n"
            f"  never executed.\n\n"
            f"DIRECTOR FRAMING CORRECTION (per META_RULE I + Fix #28 under-claim):\n"
            f"  Director-cited '4/6 family pairs differ; cal_size_sensitivity=0.0' is\n"
            f"  framing-derived; the on-disk data has 'AMBIGUOUS: 2/4 distinct family\n"
            f"  decision tuples' which is selftest-only. Skunkworks must not propagate\n"
            f"  the Director's MM framing as if it were measured -- the actual FULL run\n"
            f"  needs to land before any MM characterization atomizes.\n\n"
            f"REMEDIATION: dispatch FULL run via hdi_orchestrator at full-N. Per cell\n"
            f"  config the FULL has expected_n_full=48 phase points (4 families x 4 regimes\n"
            f"  x 3 cal_sizes); compute cost should be modest (selftest ran in 0.14s).\n\n"
            f"META_RULE_AV (new this batch): when run_mode='selftest' + _phase='selftest_done'\n"
            f"  + elapsed_s < 1s, this is NOT a landed FULL result; cell-author MUST clarify\n"
            f"  whether the dispatch ran the selftest gate only or the actual FULL.\n"
        ),
        kind=AtomKind.EXPERIMENT_RECORD,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.MATH,
        algebra=None,
        metadata={
            "provenance_quality": "HONEST_NEGATIVE",
            "cert_status": "honest_negative",
            "cert_class": "infra_dep_selftest_only_full_never_landed",
            "cell_anchor": f"substrate_refuse_gate_adaptivity_phase_diagram_v1_seed_{seed}",
            "cell_commit": CELL_COMMIT,
            "metrics_path": RG_PATH(seed),
            "ruling_note": RULING_NOTE,
            "verified_off_data": True,
            "run_mode_observed": "selftest",
            "_phase_observed": "selftest_done",
            "elapsed_s": elapsed_s,
            "seed": seed,
            "verdict": "SELFTEST_OK",
            "full_run_landed": False,
            "selftest_signal_only": "AMBIGUOUS_2_of_4_distinct_family_decision_tuples",
            "selftest_PURE_IN_recall_per_family": "all_1p000",
            "selftest_PURE_OUT_refuse_per_family": "all_1p000",
            "director_framing_corrected": True,
            "director_framing_corrected_claim": "4_of_6_family_pairs_differ_cal_size_sensitivity_0_NOT_substantiated_by_selftest_only_data",
            "verify_the_referent_meta_rule_I": "APPLIED",
            "proposes_META_RULE_AV": True,
            "remediation": "dispatch_FULL_run_via_hdi_orchestrator_expected_n_full_48",
            "cert_increment_delta": 0,
            "atomized_by": ATOMIZED_BY,
        },
    )


def build_atom_rg_seed_7():  return _rg_per_seed(7,  0.14)
def build_atom_rg_seed_13(): return _rg_per_seed(13, 0.14)
def build_atom_rg_seed_19(): return _rg_per_seed(19, 0.17)


def build_atom_rg_agg() -> Atom:
    return Atom(
        id=(
            "T3/EXP_substrate_refuse_gate_adaptivity_phase_diagram_v1_3seed_CROSS_SEED_AGG_"
            "HONEST_NEGATIVE_INFRA_DEP_selftest_only_FULL_never_landed_all_3_seeds_"
            "CORRECTS_DIRECTOR_FRAMING_2026-06-30"
        ),
        name=(
            "refuse_gate_adaptivity v1 3-seed AGG HONEST_NEGATIVE_INFRA_DEP: 3/3 seeds "
            "selftest-only; FULL never landed; total elapsed_s ~0.45s; selftest AMBIGUOUS "
            "2/4 distinct tuples (sanity signal, not phase-diagram measurement); CORRECTS "
            "Director's MM_ADAPTIVITY framing"
        ),
        description=(
            "Cross-seed aggregation: refuse_gate_adaptivity v1 across 3 seeds.\n\n"
            "VERIFY-OFF-DATA (.venv Python, 2026-06-30):\n"
            "  seed_7  SELFTEST_OK elapsed_s=0.14 run_mode=selftest _phase=selftest_done\n"
            "  seed_13 SELFTEST_OK elapsed_s=0.14 run_mode=selftest _phase=selftest_done\n"
            "  seed_19 SELFTEST_OK elapsed_s=0.17 run_mode=selftest _phase=selftest_done\n"
            "  Total compute: ~0.45 sec across 3 seeds. NO FULL run landed.\n\n"
            "AGG TIER: HONEST_NEGATIVE_INFRA_DEP (delta=0).\n\n"
            "VERIFY-THE-REFERENT (per META_RULE I): CORRECTS Director's framing of\n"
            "  'MIDDLE_BAND_ADAPTIVITY_DIFFERS_BUT_LOW_DISC; 4/6 family pairs differ;\n"
            "  cal_size_sensitivity=0.0'. The selftest verdict_msg cites 'AMBIGUOUS: 2/4\n"
            "  distinct family decision tuples' as sanity signal at the AMBIGUOUS regime\n"
            "  only; the FULL phase-diagram measurement (4 families x 4 regimes x 3\n"
            "  cal_sizes = 48 phase points) was never executed.\n\n"
            "REMEDIATION: dispatch FULL run via hdi_orchestrator; selftest already proves\n"
            "  the cell-author plumbing works (cardinality FULL=48 SMOKE=8; noise_floor\n"
            "  estimates land; per-family sanity holds at trivial extremes). The compute\n"
            "  cost should be modest given selftest ran in 0.14s; full sweep estimated\n"
            "  ~20-60 sec.\n\n"
            "COMPOSES_WITH (3 per-seed atoms; all HN_INFRA_DEP):\n"
            "  math::T3/EXP_substrate_refuse_gate_adaptivity_phase_diagram_v1_seed_{7,13,19}_"
            "HONEST_NEGATIVE_INFRA_DEP_*\n"
            "META_RULE_AV proposed (selftest_run_mode != full_run_mode discipline).\n"
        ),
        kind=AtomKind.EXPERIMENT_AGGREGATION_RECORD,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.MATH,
        algebra=None,
        metadata={
            "provenance_quality": "HONEST_NEGATIVE",
            "cert_status": "honest_negative",
            "cert_class": "cross_seed_agg_infra_dep_selftest_only_full_never_landed",
            "cell_anchor_family": "substrate_refuse_gate_adaptivity_phase_diagram_v1",
            "cell_commit": CELL_COMMIT,
            "metrics_paths": [RG_PATH(s) for s in (7, 13, 19)],
            "ruling_note": RULING_NOTE,
            "verified_off_data": True,
            "seeds": [7, 13, 19],
            "n_seeds": 3,
            "verdict_per_seed": {"7": "SELFTEST_OK", "13": "SELFTEST_OK", "19": "SELFTEST_OK"},
            "elapsed_s_per_seed": {"7": 0.14, "13": 0.14, "19": 0.17},
            "elapsed_s_total": 0.45,
            "full_run_landed_per_seed": [False, False, False],
            "director_framing_corrected": True,
            "director_framing_corrected_claim": "MIDDLE_BAND_ADAPTIVITY_4_of_6_family_pairs_differ_cal_size_sensitivity_0_NOT_substantiated_by_selftest_only_data",
            "verify_the_referent_meta_rule_I": "APPLIED_CROSS_SEED",
            "proposes_META_RULE_AV": True,
            "remediation": "dispatch_FULL_run_via_hdi_orchestrator_expected_n_full_48",
            "cert_increment_delta": 0,
            "atomized_by": ATOMIZED_BY,
        },
    )


# ============================================================================
# BONUS META RULES
# ============================================================================

def build_meta_rule_AU() -> Atom:
    return Atom(
        id=(
            "RULE_pre_dispatch_GPU_mandate_routing_check_cell_HF_at_pre_flight_in_under_1s_"
            "with_routed_queue_empty_is_INFRA_DEP_NOT_substantive_negative_META_RULE_AU_2026-06-30"
        ),
        name=(
            "META_RULE_AU: pre-dispatch GPU-mandate routing check. When a cell HARD_FAILs "
            "at pre-flight (_phase=gpu_mandate_check) in elapsed_s < 1s with routed_queue='' "
            "and verdict_msg=HARD_FAIL_GPU_MANDATE_BREACH, the cell never ran any mechanism; "
            "Director MUST NOT atomize as substantive negative. Re-dispatch with HDLAB_QUEUE set."
        ),
        description=(
            "META_RULE_AU (cert-neutral discipline rule; delta=0):\n\n"
            "OBSERVED PATTERN (CELL 3 pc_binding_operation_family v1, 3 seeds):\n"
            "  seed_7  verdict=HARD_FAIL elapsed_s=0.14 _phase=gpu_mandate_check routed_queue=''\n"
            "  seed_13 verdict=HARD_FAIL elapsed_s=0.12 _phase=gpu_mandate_check routed_queue=''\n"
            "  seed_19 verdict=HARD_FAIL elapsed_s=0.10 _phase=gpu_mandate_check routed_queue=''\n"
            "  verdict_msg: 'HARD_FAIL_GPU_MANDATE_BREACH: FULL run on CPU backend forbidden\n"
            "    by Fix #24 unless HDLAB_QUEUE=local_cpu_queue. Got HDLAB_QUEUE=''. Refusing.'\n\n"
            "These metrics encode that the Fix #24 GPU-mandate pre-flight gate fired BEFORE\n"
            "any mechanism arm ran. The cell's binding-op comparison (circular_convolution,\n"
            "element_wise_fhrr, hadamard_real, outer_product_tensor across N=[1024, 4096,\n"
            "8192] and corruption=[0.10, 0.25, 0.40, 0.475]) DID NOT EXECUTE.\n\n"
            "DISCIPLINE: Director landed-VET routing must check verdict_msg for:\n"
            "  (a) HARD_FAIL_GPU_MANDATE_BREACH (Fix #24 pre-flight)\n"
            "  (b) elapsed_s < 1s (pre-flight failure timescale)\n"
            "  (c) routed_queue='' (no queue routing took effect)\n"
            "  (d) _phase = gpu_mandate_check (cell never advanced past gate)\n"
            "When ALL FOUR fire, the cell IS an INFRA-DEP HONEST_NEGATIVE (delta=0); the\n"
            "Director MUST NOT propagate framings about mechanism dominance/competitiveness\n"
            "from this cell because no mechanism arms ran. Remediation = re-dispatch via\n"
            "hdi_orchestrator with HDLAB_QUEUE set, OR remote_GPU queue.\n\n"
            "COMPOSES_WITH: META_RULE_I (verify-the-referent) -- this rule is a specific\n"
            "instance of the verify-the-referent discipline at the pre-flight gate.\n\n"
            "CERT-NEUTRAL DISCIPLINE RULE: shapes future landed-VET practice; does not\n"
            "itself increment CERT count.\n"
        ),
        kind=AtomKind.METHODOLOGY_RULE,
        tier=Tier.TIER_2_PRIMITIVE,
        corpus=Corpus.META,
        algebra=None,
        metadata={
            "provenance_quality": "DERIVED_FROM_CELL_3_pc_binding_op_family_3seed_HF_INFRA",
            "cert_status": "chain_grade_meta_rule",
            "cert_class": "cert_neutral_discipline_rule",
            "verdict": "META_RULE_NEUTRAL",
            "verified_off_data": True,
            "atomized_by": ATOMIZED_BY,
            "atomized_date": "2026-06-30",
            "rule_number_in_meta_corpus": "RULE_AU",
            "applies_when": "Director landed-VET routes a HARD_FAIL cell with _phase=gpu_mandate_check + elapsed_s<1s + routed_queue=''",
            "discipline": "do_not_atomize_as_substantive_negative_re_dispatch_with_HDLAB_QUEUE_set",
            "composes_with_meta_rules": ["META_RULE_I_verify_the_referent"],
            "source_cell": "substrate_pc_binding_operation_family_phase_diagram_v1_3seed",
            "cert_increment_delta": 0,
        },
    )


def build_meta_rule_AV() -> Atom:
    return Atom(
        id=(
            "RULE_selftest_run_mode_NOT_full_run_mode_metrics_json_with_run_mode_selftest_"
            "and_phase_selftest_done_and_elapsed_s_under_1s_is_NOT_landed_FULL_result_"
            "META_RULE_AV_2026-06-30"
        ),
        name=(
            "META_RULE_AV: selftest_run_mode != full_run_mode. When metrics.json has "
            "run_mode='selftest' + _phase='selftest_done' + elapsed_s<1s, this is the cell "
            "selftest sanity-check output; the FULL phase-diagram run did NOT land. Director "
            "MUST NOT derive MM/HN/CG framings from selftest-only data."
        ),
        description=(
            "META_RULE_AV (cert-neutral discipline rule; delta=0):\n\n"
            "OBSERVED PATTERN (CELL 6 refuse_gate_adaptivity v1, 3 seeds):\n"
            "  seed_7  verdict=SELFTEST_OK elapsed_s=0.14 run_mode=selftest _phase=selftest_done\n"
            "  seed_13 verdict=SELFTEST_OK elapsed_s=0.14 run_mode=selftest _phase=selftest_done\n"
            "  seed_19 verdict=SELFTEST_OK elapsed_s=0.17 run_mode=selftest _phase=selftest_done\n"
            "  verdict_msg cites: cardinality FULL=48 SMOKE=8; noise_floor estimates; per-family\n"
            "    PURE_IN answer=1.000 PURE_OUT refuse=1.000 (sanity at trivial extremes); +\n"
            "    'AMBIGUOUS: 2/4 distinct family decision tuples' (selftest sanity signal).\n\n"
            "These are SELFTEST artifacts, NOT FULL phase-diagram measurements. The selftest\n"
            "validates that the cell-author plumbing works (correct cardinality, noise_floor\n"
            "computable, per-family trivial-extreme sanity passes); it does NOT measure the\n"
            "(family, regime, cal_size) phase diagram.\n\n"
            "DISCIPLINE: Director landed-VET routing must check metrics.json for:\n"
            "  (a) run_mode == 'selftest' (or != 'full')\n"
            "  (b) _phase == 'selftest_done' (or != 'full_complete')\n"
            "  (c) elapsed_s << expected_full_runtime\n"
            "When TWO+ of these fire, the FULL run did NOT land; Director MUST NOT derive\n"
            "MM / HN / CG framings from the selftest data; the appropriate tier is\n"
            "HONEST_NEGATIVE_INFRA_DEP with remediation = dispatch FULL via hdi_orchestrator.\n\n"
            "COMPOSES_WITH: META_RULE_I (verify-the-referent) -- this rule is a specific\n"
            "instance at the run_mode dimension.\n\n"
            "COMPOSES_WITH: Fix #25 landing-notifier discipline -- if the landing-notifier\n"
            "scheduled task were running, selftest landings would be tagged distinct from\n"
            "FULL landings; until that is in place, manual run_mode field check is required.\n\n"
            "CERT-NEUTRAL DISCIPLINE RULE: shapes future landed-VET practice; does not\n"
            "itself increment CERT count.\n"
        ),
        kind=AtomKind.METHODOLOGY_RULE,
        tier=Tier.TIER_2_PRIMITIVE,
        corpus=Corpus.META,
        algebra=None,
        metadata={
            "provenance_quality": "DERIVED_FROM_CELL_6_refuse_gate_adaptivity_3seed_selftest_only",
            "cert_status": "chain_grade_meta_rule",
            "cert_class": "cert_neutral_discipline_rule",
            "verdict": "META_RULE_NEUTRAL",
            "verified_off_data": True,
            "atomized_by": ATOMIZED_BY,
            "atomized_date": "2026-06-30",
            "rule_number_in_meta_corpus": "RULE_AV",
            "applies_when": "Director landed-VET sees metrics.json with run_mode='selftest' OR _phase='selftest_done' OR elapsed_s much less than expected_full_runtime",
            "discipline": "tier_HONEST_NEGATIVE_INFRA_DEP_not_MM_or_HN_or_CG_remediate_dispatch_FULL_via_hdi_orchestrator",
            "composes_with_meta_rules": ["META_RULE_I_verify_the_referent", "Fix_25_landing_notifier"],
            "source_cell": "substrate_refuse_gate_adaptivity_phase_diagram_v1_3seed",
            "cert_increment_delta": 0,
        },
    )


# ============================================================================
# DRIVER
# ============================================================================

ALL_ATOM_BUILDERS = [
    # Cell 1 multihop v4
    ("MH/seed_7",  build_atom_mh_seed_7),
    ("MH/seed_13", build_atom_mh_seed_13),
    ("MH/seed_19", build_atom_mh_seed_19),
    ("MH/AGG",     build_atom_mh_agg),
    # Cell 2 TASK_VECTOR v3
    ("TV/seed_7",  build_atom_tv_seed_7),
    ("TV/seed_13", build_atom_tv_seed_13),
    ("TV/seed_19", build_atom_tv_seed_19),
    ("TV/AGG",     build_atom_tv_agg),
    # Cell 3 binding op family
    ("BO/seed_7",  build_atom_bo_seed_7),
    ("BO/seed_13", build_atom_bo_seed_13),
    ("BO/seed_19", build_atom_bo_seed_19),
    ("BO/AGG",     build_atom_bo_agg),
    # Cell 4 lock-in v3
    ("LI/seed_7",  build_atom_li_seed_7),
    ("LI/seed_13", build_atom_li_seed_13),
    ("LI/seed_19", build_atom_li_seed_19),
    ("LI/AGG",     build_atom_li_agg),
    # Cell 5 PC cleanup family
    ("PC/seed_7",  build_atom_pc_seed_7),
    ("PC/seed_13", build_atom_pc_seed_13),
    ("PC/seed_19", build_atom_pc_seed_19),
    ("PC/AGG",     build_atom_pc_agg),
    # Cell 6 refuse_gate_adaptivity
    ("RG/seed_7",  build_atom_rg_seed_7),
    ("RG/seed_13", build_atom_rg_seed_13),
    ("RG/seed_19", build_atom_rg_seed_19),
    ("RG/AGG",     build_atom_rg_agg),
    # META rules
    ("META/AU",    build_meta_rule_AU),
    ("META/AV",    build_meta_rule_AV),
]


def main(apply: bool):
    print(f"[atomize 6cell batch 2026-06-30] DRY-RUN={not apply}")
    print(f"[atomize 6cell batch 2026-06-30] Will write {len(ALL_ATOM_BUILDERS)} atoms")

    # Sanity: every metrics.json off-disk readable
    metric_paths = [
        *(MH_PATH(s) for s in (7, 13, 19)),
        *(TV_PATH(s) for s in (7, 13, 19)),
        *(BO_PATH(s) for s in (7, 13, 19)),
        *(LI_PATH(s) for s in (7, 13, 19)),
        *(PC_PATH(s) for s in (7, 13, 19)),
        *(RG_PATH(s) for s in (7, 13, 19)),
    ]
    for p in metric_paths:
        with open(p) as f:
            json.load(f)  # raises if not parseable
    print(f"[atomize] All {len(metric_paths)} metrics.json files parse OK off-disk.")

    # Build all atoms first (catches AtomKind / Tier / Corpus errors before write)
    atoms = []
    for tag, builder in ALL_ATOM_BUILDERS:
        a = builder()
        atoms.append((tag, a))
        print(f"  [build] {tag:14s} kind={a.kind.value:34s} corpus={a.corpus.value:6s} id={a.id[:80]}...")
    print(f"[atomize] All {len(atoms)} atoms built OK.")

    if not apply:
        print("\n[DRY] Re-run with --apply to write Store + ledger.")
        return

    # Load store
    store = PartitionedStore(STORE_ROOT)
    cert_pre = sum(1 for a in store.all_atoms() if (a.metadata or {}).get("provenance_quality") == "CERT_CHAIN_GRADE")
    n_pre = sum(1 for _ in store.all_atoms())
    print(f"[A5 PRE] CERT N = {cert_pre}; total atoms = {n_pre}")

    # Add atoms (per-corpus; PartitionedStore handles flush)
    for tag, a in atoms:
        store.add_atom(a)
        print(f"  [add] {tag:14s} {a.id[:90]}...")
    store.flush()
    print("[atomize] Store flush() OK.")

    # Re-load and verify
    store2 = PartitionedStore(STORE_ROOT)
    n_post = sum(1 for _ in store2.all_atoms())
    cert_post = sum(1 for a in store2.all_atoms() if (a.metadata or {}).get("provenance_quality") == "CERT_CHAIN_GRADE")
    print(f"[A5 POST] CERT N = {cert_post} (delta = {cert_post - cert_pre}; expected 0)")
    print(f"[A5 POST] total atoms = {n_post} (delta = {n_post - n_pre}; expected {len(atoms)})")

    if cert_post != cert_pre:
        raise RuntimeError(f"CERT delta != 0 (pre={cert_pre} post={cert_post}); all atoms in this batch are MM/HN")

    # Append ledger rows for each atom
    now = time.time()
    written_ledger = 0
    for tag, a in atoms:
        atom_qualified = f"{a.corpus.value}::{a.id}"
        is_hn = (a.metadata or {}).get("cert_status") == "honest_negative"
        is_mm = (a.metadata or {}).get("cert_status") == "measured_mechanism"
        is_meta = a.kind == AtomKind.METHODOLOGY_RULE

        if is_meta:
            row = {
                "ts": now,
                "op": "cert_ruling",
                "atom_id": atom_qualified,
                "cert_status": "custom",
                "cert_class": "discipline_meta",
                "verified_off_data": True,
                "atomized_by": ATOMIZED_BY,
                "cell_commit": CELL_COMMIT,
                "verdict": "META_RULE_NEUTRAL",
                "cert_increment_delta": 0,
                "cv": None,
                "referent_pointer": {
                    "notes_path": RULING_NOTE,
                    "metrics_path": "n/a-meta-rule-derived-from-batch",
                    "atom_qualified_id": atom_qualified,
                },
                "supersedes": None,
                "note": f"6cell_batch_meta_rule_{tag}",
            }
        elif is_hn:
            row = build_honest_negative_row(
                atom_id=atom_qualified,
                cell_commit=CELL_COMMIT,
                verdict=(a.metadata or {}).get("verdict") or "HARD_FAIL",
                notes_path=RULING_NOTE,
                metrics_path=(a.metadata or {}).get("metrics_path") or (a.metadata or {}).get("metrics_paths", ["n/a"])[0],
                cert_class=(a.metadata or {}).get("cert_class") or "pre_reg_miss_proven_bound",
                atomized_by=ATOMIZED_BY,
                note=f"6cell_batch_HN_{tag}",
                ts=now,
            )
        elif is_mm:
            row = build_measured_mechanism_row(
                atom_id=atom_qualified,
                cell_commit=CELL_COMMIT,
                verdict=(a.metadata or {}).get("verdict") or "MIDDLE_BAND",
                notes_path=RULING_NOTE,
                metrics_path=(a.metadata or {}).get("metrics_path") or (a.metadata or {}).get("metrics_paths", ["n/a"])[0],
                atomized_by=ATOMIZED_BY,
                note=f"6cell_batch_MM_{tag}",
                ts=now,
            )
        else:
            print(f"  [ledger SKIP] {tag} -- no clear status mapping")
            continue

        try:
            append_cert_ledger_row(
                row,
                strict_a5=False,
                expected_cert_n_pre=cert_post,
                expected_cert_n_post=cert_post,
            )
            written_ledger += 1
            print(f"  [ledger] {tag:14s} appended")
        except Exception as e:
            print(f"  [ledger ERROR] {tag}: {e}")

    print(f"[atomize] Wrote {written_ledger} ledger rows.")
    print(f"[DONE] 6cell batch atomization complete. CERT delta = 0 (net). Atoms = +{len(atoms)}.")


if __name__ == "__main__":
    apply = "--apply" in sys.argv
    main(apply=apply)
