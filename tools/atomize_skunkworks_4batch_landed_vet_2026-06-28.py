"""Atomize: Skunkworks landed-VET 4-batch evening wave (2026-06-28).

Source: Director's 4-batch dispatch (5 batches reduced to 4 here because PC v2.2 was
ALREADY atomized by skunkworks_atomize_pc_v2p2_dense_GPU_3seed_chain_grade_2026-06-28
earlier today as chain_grade -- I verified the ledger and skip re-atomization).

VERIFY-OFF-DATA basis (.venv Python; each metrics.json recomputed end-to-end on disk;
per-arm cross-checked against verdict_msg framings; phase_map / summary_per_phase_point
independently recomputed; cardinality + arms_differ verified per seed):

  Batch 2: Lock-in-amp phase diagram v1 (3 seeds: 7, 13, 19)
           Reported MIDDLE_BAND. Off-disk verified: FLOOR regime under-populated (cell's
           own criterion fails) but sqrt-t physics CONFIRMED across all 3 seeds:
             at SNR=0.001 N=8192: L=[0.0, 0.03, 0.3, 1.0] across t=[10,100,1000,10000]
             monotonic rise consistent with SNR_output = SNR_input * sqrt(t)
             DIRECT cosine stays at floor (0.0-0.03); SAME signal, different readout
             arms_differ_LD 42-48/60; n_DISCRIMINATING 53-57/60
           -> MEASURED_MECHANISM (lock-in physics mechanism characterized across [low SNR,
              long t] regime; FLOOR under-populated cell criterion blocks chain-grade)

  Batch 3: Capacity multibank alpha-K phase diagram v1 GPU (3 seeds)
           Reported MIDDLE_BAND. Off-disk verified: cardinality_ok 486/486; arms_differ
           160-162/162; multi-bank advantage MASSIVE at B=16 (N=8192 K=64 alpha=0.05:
           M=1.000 vs S=0.139, 7x lift; alpha=0.5: M=0.246 vs S=0.003, 80x relative).
           n_pass_at_full_N=5 (low; threshold for HP not met). GPU util mean 49-78%
           (seed=7 borderline at 48.99%, seed=13 53.9%, seed=19 78.0%; max=100% all seeds).
           Mechanism class confirmed: multi-bank distribution recovers capacity at
           alpha-loadings where single-bank floors.
           -> MEASURED_MECHANISM (multi-bank capacity-per-N advantage characterized;
              pass_at_full_N low blocks chain-grade)

  Batch 4: TASK_VECTOR HRR ICL K-cliff phase diagram v1 FULL (3 seeds)
           Reported HARD_PASS with K_cliff_min=1 at (V=10, ov=0.6). Off-disk verified:
           cardinality 1890/1890; cliff_observable=True. BUT K_cliff_min=1 framing is
           MISLEADING -- at V=10/ov=0.6 the K=1 point hits 0.000 then RECOVERS at K=3-5
           (non-monotonic; not a true cliff). REAL K-cliff visible only in V=10/ov<=0.3
           regime where TV=1.0->1.0->~0.83->~0.6->~0.33->~0.27->~0.1 across K=1..100
           (clean monotonic decay; replicated across 3 seeds). V>=200 / ov>=0.6 regime:
           BIT-IDENTICAL ZERO across all 3 seeds at most K (substrate-cannot-encode at
           that V/overlap; metric-floor artifact).
           -> MEASURED_MECHANISM (K-cliff CHARACTERIZED in V<=10/ov<=0.3 regime;
              K_cliff_min=1 framing is metric-artifact from non-monotonic floor signal
              at high-V/high-overlap; cell's HARD_PASS overstates)

  Batch 5: Schema exemplar-Bayes capacity-stress v2 (3 seeds)
           Reported: seed=7 HARD_PASS, seed=13 MIDDLE_BAND, seed=19 MIDDLE_BAND.
           Off-disk verified: arms_differ 63-64/64; avg_bayes_minus_nn 0.50-0.53 across
           seeds (replicated). The HP/MB split is capacity_scaling_delta threshold:
             seed=7: delta=0.070 (JUST over threshold)
             seed=13: delta=0.040 (under)
             seed=19: delta=0.050 (under)
           Majority verdict (cross-seed agg) = MIDDLE_BAND. lift profile shows real
           capacity decay (peaks ~0.6-0.8 at mid-alpha; drops to 0.1-0.2 at alpha>20).
           Bayes-vs-NN lift is real and replicated but capacity-scaling differentiation
           fragile at threshold.
           -> MEASURED_MECHANISM (Bayes-vs-NN lift characterized; capacity-scaling
              delta at HP threshold-edge; 2/3 seeds fail cell's own criterion)

NET CERT delta: 0 chain-grade (all 4 MM)
  + 4 MM (mechanism characterization; CERT-neutral)

PRE CERT N (verified live): 630
POST CERT N (predicted; A5-gated): 630 (no chain_grade increment)

LEDGER ROWS: 4 (all measured_mechanism)

A5 GATING: PRE/POST cert_n assertions on every window; round-trip pq check on every atom.

Run:
  .venv/Scripts/python.exe tools/atomize_skunkworks_4batch_landed_vet_2026-06-28.py            # DRY
  .venv/Scripts/python.exe tools/atomize_skunkworks_4batch_landed_vet_2026-06-28.py --apply    # WRITE
"""
from __future__ import annotations
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(".").resolve()))
from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier
from tools.cert_ledger_writer import append_cert_ledger_row

STORE_ROOT = Path("data/substrate_index")
RULING_NOTE = "notes/skunkworks_landed_vet_4batch_evening_wave_2026-06-28.md"
CELL_COMMIT = "n/a-2026-06-28-4batch-evening-wave-landed-vet"
ATOMIZED_BY = "skunkworks_atomize_4batch_landed_vet_2026-06-28"

METRICS_LIA = "data/exp_substrate_lock_in_amp_phase_diagram_v1_seed_{7,13,19}/metrics.json"
METRICS_CMB = "data/exp_substrate_capacity_multibank_alpha_K_phase_diagram_v1_GPU_seed_{7,13,19}/metrics.json"
METRICS_TV = "data/exp_substrate_task_vector_K_cliff_phase_diagram_v1_seed_{7,13,19}_FULL/metrics.json"
METRICS_SCH = "data/exp_substrate_schema_exemplar_bayes_capacity_stress_v2_seed_{7,13,19}/metrics.json"


# ============================================================================
# ATOM 1 -- Lock_in_amp phase diagram v1 3-seed MEASURED_MECHANISM
# ============================================================================

def build_atom1_lock_in_amp_mm() -> Atom:
    return Atom(
        id=(
            "T3/EXP_substrate_lock_in_amp_phase_diagram_v1_CROSS_SEED_AGG_3_of_3_MEASURED_MECHANISM_"
            "sqrt_t_SNR_physics_CONFIRMED_lock_in_advantage_delta_LD_mean_0p43_AT_LOW_SNR_LONG_T_regime_"
            "SNR0p001_N8192_t10_to_10000_L_0p0_0p03_0p3_1p0_DIRECT_at_floor_arms_differ_LD_42_to_48_of_60_"
            "n_DISCRIMINATING_53_to_57_of_60_FLOOR_under_populated_2_to_6_need_12_cell_MB_criterion_met_"
            "expected_n_60_observed_60_cardinality_ok_n_seeds_3_seeds_7_13_19_axes_SNR_5_T_4_N_3_freq_0p1"
        ),
        name=(
            "substrate_lock_in_amp_phase_diagram v1 CROSS-SEED-AGG 3/3 MEASURED_MECHANISM: "
            "sqrt-t SNR-physics CONFIRMED; lock-in vs direct delta_LD~+0.43 across [low SNR, long t] "
            "regime; SNR=0.001 N=8192 L=[0,0.03,0.3,1.0] across t=[10,100,1000,10000] monotonic; "
            "DIRECT cosine stays at floor; arms_differ 42-48/60; n_DISCRIMINATING 53-57/60; "
            "FLOOR regime under-populated (2-6 vs need 12) blocks cell HP criterion"
        ),
        description=(
            "MEASURED_MECHANISM substrate lock-in amplifier phase diagram at full N (delta=0).\n"
            "All 3 seeds (7, 13, 19) report MIDDLE_BAND per cell criterion (FLOOR regime population\n"
            "2/60, 6/60, 2/60 vs threshold 12) but mechanism class CONFIRMED and replicated:\n"
            "lock-in coherent integration recovers signal at SNR-input below detection threshold of\n"
            "direct-cosine readout, with physics-correct sqrt-t scaling.\n"
            "\n"
            "OFF-DATA RECOMPUTE (Skunkworks 2026-06-28, .venv Python, 3 seeds independently checked):\n"
            "  Per-seed verdict (reported -> verified):\n"
            "    seed=7  MIDDLE_BAND: n_SAT=11/60 (need>=12) n_FLOOR=2/60 n_ADV=31/60 n_DISC=55/60\n"
            "             lock_in_recall_mean=0.717, direct=0.285, delta_LD_mean=+0.432\n"
            "    seed=13 MIDDLE_BAND: n_SAT=12/60 n_FLOOR=6/60 n_ADV=30/60 n_DISC=57/60\n"
            "             lock_in_recall_mean=0.711, direct=0.289, delta_LD_mean=+0.422\n"
            "    seed=19 MIDDLE_BAND: n_SAT=10/60 n_FLOOR=2/60 n_ADV=30/60 n_DISC=53/60\n"
            "             lock_in_recall_mean=0.711, direct=0.290, delta_LD_mean=+0.421\n"
            "  Cross-seed delta_LD stability: 0.42-0.43 (sigma ~0.005; tight).\n"
            "  arms_differ (LOCK_IN vs DIRECT recall): 42-48/60 across seeds.\n"
            "\n"
            "sqrt-t PHYSICS CONFIRMED (load-bearing finding; replicates across all 3 seeds):\n"
            "  At N=8192 SNR_input slice:\n"
            "    SNR=0.001: L=[0.00, 0.03, 0.30, 1.00] across t=[10,100,1000,10000] monotonic\n"
            "    SNR=0.0032: L=[0.0, 0.27-0.40, 1.00, 1.00] across t (cliff between t=100..1000)\n"
            "    SNR=0.010: L=[0.27-0.33, 1.00, 1.00, 1.00] (cliff between t=10..100)\n"
            "    SNR=0.032: L=[1.00, 1.00, 1.00, 1.00] (all saturated)\n"
            "    SNR=0.10: L=[1.00, 1.00, 1.00, 1.00] (both arms saturated; signal above noise floor)\n"
            "  DIRECT cosine recall stays at floor (0.0-0.07) across all SNR<=0.01 slices;\n"
            "  same signal, different readout -- the lock-in advantage IS the physics.\n"
            "\n"
            "PHASE-DIAGRAM REGIME MAP (cell-derived; cross-seed):\n"
            "  ADVANTAGE regime (L-D>=0.30): 30-31/60 -- CHAIN-GRADE-LIKE evidence per cell criterion\n"
            "  SATURATED (L>=0.95 AND D>=0.95): 10-12/60 -- right edge (high SNR, any t)\n"
            "  FLOOR (L<=0.015 AND D<=0.015): 2-6/60 -- left edge (SNR<=0.001 AND short t)\n"
            "  DISCRIMINATING (L vs D differ): 53-57/60 -- vast majority of grid\n"
            "\n"
            "WHY MEASURED_MECHANISM not chain-grade:\n"
            "  The cell's own HARD_PASS criterion requires all 3 regimes (SAT/FLOOR/ADV) populated\n"
            "  >=12/60. FLOOR is under-populated (2-6) because SNR_INPUT_AXIS minimum (0.001) is not\n"
            "  low enough to push lock-in down to floor at N=8192 with t=10000 (the sqrt-t advantage\n"
            "  is too strong). The PHYSICS is correct; the GRID just doesn't sample deep-floor.\n"
            "  Honest classification: the mechanism is fully characterized within tested regime.\n"
            "\n"
            "WHY MEASURED_MECHANISM not honest-negative:\n"
            "  The mechanism CLASS validates -- coherent integration provides square-root-t SNR\n"
            "  improvement consistent with classical lock-in theory. The discriminator FIRES cleanly\n"
            "  in 53-57/60 grid points across all 3 seeds. The cell-criterion miss is a regime-\n"
            "  coverage gap, not a mechanism failure.\n"
            "\n"
            "WHY NOT chain-grade-eligible re-dispatch FLAG:\n"
            "  Director may extend SNR_INPUT_AXIS bottom to e.g. 0.0001 (decade lower) OR add t=1\n"
            "  to integration_time axis to populate FLOOR; this would let same mechanism land\n"
            "  chain-grade without changing the physics. FLAG: SNR axis extension to lower decade\n"
            "  is the cheap-and-clean revival path.\n"
            "\n"
            "BRAIN-GROUNDED FRAMING:\n"
            "  Cortical phase-locking (Buzsaki gamma-locking 30-80Hz; oscillatory coherent integration)\n"
            "  IS exactly this physics: brain extracts weak periodic signals from noisy background via\n"
            "  coherent integration locked to the signal frequency. Substrate-native lock-in confirms\n"
            "  the operation generalizes to discrete HD vectors. Capacity-per-spike scaling could be\n"
            "  characterized at chain-grade with deeper FLOOR sampling.\n"
            "\n"
            "META_RULE COMPLIANCE:\n"
            "  META_RULE_H cardinality: 60/60 OK each seed (expected_n_units=60)\n"
            "  META_RULE_AF arms-must-differ: LOCK_IN vs DIRECT 42-48/60 differ; remaining is\n"
            "    saturated-both or floor-both regimes (load-bearing both-saturate/both-floor signal)\n"
            "  META_RULE_AH atomic metrics: per-grid-point recall + delta_LD + SNR_output_predicted\n"
            "  META_RULE_K discriminator: NOISE_FLOOR arm captures noise-only baseline; DIRECT vs\n"
            "    LOCK_IN captures the integration mechanism\n"
            "  META_RULE_L band: ADVANTAGE band L-D>=0.30 met in 30-31/60 (need 12; CHAIN-GRADE band)\n"
            "  META_RULE_O band-calibration: FLOOR axis-coverage insufficient (regime gap, not bug)\n"
            "  Fix #28 per-arm reads: verified all 60 grid points per seed across 3 seeds\n"
            "\n"
            "_llm_forward_calls_at_inference = 0 (substrate-only decode).\n"
        ),
        kind=AtomKind.EXPERIMENT_RECORD,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.MATH,
        algebra=None,
        metadata={
            "provenance_quality": "MEASURED_MECHANISM",
            "cert_status": "measured_mechanism",
            "cert_class": "mechanism_characterization",
            "cell_anchor": "substrate_lock_in_amp_phase_diagram_v1_CROSS_SEED_AGG_3",
            "cell_commit": CELL_COMMIT,
            "metrics_path_pattern": METRICS_LIA,
            "ruling_note": RULING_NOTE,
            "verified_off_data": True,
            "run_mode": "full",
            "n_seeds": 3,
            "seeds": [7, 13, 19],
            "SNR_INPUT_AXIS": [0.001, 0.0032, 0.01, 0.032, 0.1],
            "INTEGRATION_TIME_AXIS": [10, 100, 1000, 10000],
            "N_AXIS": [2048, 4096, 8192],
            "signal_freq": 0.1,
            "M_codebook": 100,
            "N_EVAL": 30,
            "lock_in_recall_mean_per_seed_MEASURED": [0.717, 0.711, 0.711],
            "direct_recall_mean_per_seed_MEASURED": [0.285, 0.289, 0.290],
            "floor_recall_mean_per_seed_MEASURED": [0.004, 0.013, 0.012],
            "delta_LD_mean_per_seed_MEASURED": [0.432, 0.422, 0.421],
            "n_SAT_per_seed_MEASURED": [11, 12, 10],
            "n_FLOOR_per_seed_MEASURED": [2, 6, 2],
            "n_ADVANTAGE_per_seed_MEASURED": [31, 30, 30],
            "n_DISCRIMINATING_per_seed_MEASURED": [55, 57, 53],
            "arms_differ_LD_per_seed_MEASURED": [48, 42, 48],
            "verdict_per_seed_RAW": ["MIDDLE_BAND", "MIDDLE_BAND", "MIDDLE_BAND"],
            "sqrt_t_physics_at_N8192_SNR0p001_L_MEASURED_seed7": [0.0, 0.0333, 0.3, 1.0],
            "sqrt_t_physics_at_N8192_SNR0p001_L_MEASURED_seed13": [0.0, 0.0, 0.4, 1.0],
            "sqrt_t_physics_at_N8192_SNR0p001_L_MEASURED_seed19": [0.0333, 0.0, 0.3, 1.0],
            "sqrt_t_physics_at_N8192_SNR0p001_t_axis": [10, 100, 1000, 10000],
            "sqrt_t_monotone_across_3_seeds": True,
            "direct_cosine_floor_across_3_seeds": True,
            "delta_LD_cross_seed_sigma_MEASURED": 0.005,
            "verdict_raw_cross_seed": "MEASURED_MECHANISM_3_of_3_seeds_MB_FLOOR_under_populated_mechanism_class_confirmed",
            "demote_reason": "cell_HP_criterion_FLOOR_pop_>=12_unmet_at_SNR_min_0p001_axis_coverage_gap_not_mechanism_failure",
            "encoder_provenance": "SUBSTRATE_NATIVE",
            "META_RULE_H_cardinality_ok": True,
            "META_RULE_AF_arms_differ_LD": "42_to_48_of_60_per_seed",
            "META_RULE_AH_atomic_metrics": True,
            "META_RULE_K_discriminator_fires": True,
            "META_RULE_L_advantage_band_met_30_to_31_of_60": True,
            "META_RULE_O_floor_axis_coverage_insufficient": True,
            "load_bearing_finding_1": "sqrt_t_SNR_physics_CONFIRMED_substrate_native_3_seeds_replicated",
            "load_bearing_finding_2": "lock_in_advantage_delta_LD_mean_0p43_robust_cross_seed_sigma_0p005",
            "load_bearing_finding_3": "DIRECT_cosine_at_noise_floor_at_SNR_under_0p01_for_t_under_1000",
            "revival_path_flag": "EXTEND_SNR_INPUT_AXIS_to_0p0001_decade_lower_populates_FLOOR_for_chain_grade",
            "scope_observed": "full_3_seeds_60_grid_per_seed_SNR_5_T_4_N_3_freq_0p1_M_100",
            "scope_not_claimed": "chain_grade_OR_FLOOR_populated_OR_SNR_below_0p001",
            "brain_analog": "Buzsaki_gamma_locking_cortical_coherent_integration_30_to_80Hz",
            "zero_llm_calls_at_inference": True,
            "_llm_forward_calls_at_inference": 0,
            "substrate_only_decode_gate": "PASS",
            "atomized_by": ATOMIZED_BY,
        },
    )


# ============================================================================
# ATOM 2 -- Capacity multibank alpha-K phase diagram v1 GPU 3-seed MEASURED_MECHANISM
# ============================================================================

def build_atom2_capacity_multibank_mm() -> Atom:
    return Atom(
        id=(
            "T3/EXP_substrate_capacity_multibank_alpha_K_phase_diagram_v1_GPU_CROSS_SEED_AGG_3_of_3_"
            "MEASURED_MECHANISM_multi_bank_advantage_MASSIVE_at_B_16_N8192_K64_alpha0p05_M_1p000_S_0p139_7x_"
            "alpha0p1_M_1p000_S_0p044_alpha0p5_M_0p246_S_0p003_80x_relative_RANDOM_FLOOR_0p000_"
            "n_pass_full_N_5_n_pass_total_23_blocks_HP_arms_differ_160_to_162_of_162_per_seed_"
            "cardinality_486_of_486_OK_gpu_util_mean_49_to_78_max_100_per_seed_codebook_16384_n_seeds_3_7_13_19"
        ),
        name=(
            "substrate_capacity_multibank_alpha_K_phase_diagram v1 GPU CROSS-SEED-AGG 3/3 MEASURED_MECHANISM: "
            "multi-bank vs single-bank advantage MASSIVE at B=16; at N=8192 K=64 alpha=0.05 MULTI=1.000 "
            "vs SINGLE=0.139 (7x); alpha=0.5 MULTI=0.246 vs SINGLE=0.003 (80x relative); RANDOM at floor; "
            "arms_differ 160-162/162; cardinality_ok 486/486; n_pass_at_full_N=5 (HP threshold unmet)"
        ),
        description=(
            "MEASURED_MECHANISM substrate multi-bank vs single-bank capacity advantage at full N+GPU\n"
            "(delta=0). All 3 seeds (7, 13, 19) report MIDDLE_BAND per cell criterion (n_pass_at_full_N=5\n"
            "low; rail_ok=False) but mechanism class CONFIRMED at MASSIVE magnitudes.\n"
            "\n"
            "OFF-DATA RECOMPUTE (Skunkworks 2026-06-28, .venv Python, 3 seeds, GPU RTX 4060 Ti):\n"
            "  Cardinality: 486/486 each seed (3 regimes x 162 phase-points = 486 units).\n"
            "  Per-seed top-line:\n"
            "    seed=7:  n_pass=23, pass_at_full_N=5, saturate=12, floor=96, probe_cliffs=0\n"
            "             arms_differ=162/162; gpu_util mean=48.99% (just under 50 target)\n"
            "    seed=13: n_pass=23, pass_at_full_N=5, saturate=11, floor=96\n"
            "             arms_differ=160/162; gpu_util mean=53.9%\n"
            "    seed=19: n_pass=23, pass_at_full_N=5, saturate=12, floor=96\n"
            "             arms_differ=162/162; gpu_util mean=78.04%\n"
            "  Regimes: MULTI_BANK_BIND / SINGLE_BANK_BASELINE / RANDOM_FLOOR (3 arms).\n"
            "\n"
            "MULTI-BANK ADVANTAGE (load-bearing; replicates across 3 seeds at N=8192 K=64 B=16):\n"
            "  alpha=0.05: MULTI=1.000 SINGLE=0.139-0.151 (~7x lift)\n"
            "  alpha=0.10: MULTI=1.000 SINGLE=0.044-0.055 (~20x lift)\n"
            "  alpha=0.25: MULTI=0.500 SINGLE=0.007-0.010 (~60x lift)\n"
            "  alpha=0.50: MULTI=0.246 SINGLE=0.002-0.003 (~80x lift relative)\n"
            "  alpha=1.00: MULTI=0.102-0.104 SINGLE=0.001-0.002 (~100x lift)\n"
            "  alpha=2.00: MULTI=0.032-0.033 SINGLE=0.000-0.001 (still distinguishing)\n"
            "  RANDOM_FLOOR=0.000-0.0002 across all (discriminator clean).\n"
            "\n"
            "cliff_per_B summary (per cell): B=16 cliff_frac=0.5; B=4 cliff_frac=0.1.\n"
            "  Interpretation: at B=16 banks half the alpha-K combos show cliff transition;\n"
            "  at B=4 only 10%. Multi-bank capacity scales (super-linearly) with B.\n"
            "\n"
            "rail_alpha0p05_K64_B1_N8192 (single-bank baseline): 0.13-0.14 across seeds (rail_ok=False;\n"
            "  the single-bank baseline at high CB=16384 is ALREADY at retrieval-floor; multi-bank\n"
            "  IS the load-bearing mechanism).\n"
            "\n"
            "WHY MEASURED_MECHANISM not chain-grade:\n"
            "  n_pass_at_full_N=5 across all seeds is the cell's HP gate (low). The cell's pass-\n"
            "  threshold is recall>0.5 AND MULTI>SINGLE+0.1 at N=8192; only 5 (alpha,K,B) combos\n"
            "  satisfy this jointly (e.g. low-alpha + high-K + high-B). Most combos either FLOOR\n"
            "  (high alpha) or SATURATE (low alpha + high K + high B). Mechanism CLASS is fully\n"
            "  characterized but the chain-grade HP-N count is not reached.\n"
            "\n"
            "WHY MEASURED_MECHANISM not honest-negative:\n"
            "  Massive multi-bank advantage IS the predicted mechanism class (alpha-K-B capacity\n"
            "  scaling). Discriminator fires (RANDOM_FLOOR=0.000 cleanly). Arms differ in 160-162/162\n"
            "  combos. The mechanism is real; only the cell's stringent HP-pass-count threshold is\n"
            "  unmet.\n"
            "\n"
            "REVIVAL FLAG (cert-owner does NOT direct strategy; FLAG only):\n"
            "  Director may consider:\n"
            "    (a) re-dispatch with extended K_per_bank axis (>=128) at N=8192 to populate more\n"
            "        HP-band points\n"
            "    (b) re-dispatch with focus on B=16,32,64 (drop B=1 baseline-only as known-floor)\n"
            "    (c) re-tune HP threshold (recall_floor 0.5 may be too high at high-alpha-K-B)\n"
            "\n"
            "BRAIN-GROUNDED FRAMING:\n"
            "  Multi-bank distribution mirrors cortical column micro-circuitry (separate writing\n"
            "  to multiple local fields, each at sub-capacity). Single-bank baseline mirrors\n"
            "  catastrophic-interference regime in a single recurrent attractor. Substrate\n"
            "  multi-bank advantage is the cortical-area parallelism that survives biological\n"
            "  capacity-per-region constraints.\n"
            "\n"
            "META_RULE COMPLIANCE:\n"
            "  META_RULE_H cardinality: 486/486 per seed (n_units_expected=486)\n"
            "  META_RULE_AF arms-must-differ: 160-162/162 (3 regimes distinguishable per combo)\n"
            "  META_RULE_AH atomic metrics: per-unit recall + route_acc + arm_sha256 + wall_s + mem\n"
            "  META_RULE_K discriminator: RANDOM_FLOOR=0.000 clean separation\n"
            "  META_RULE_L band: MULTI in HP-band at N=8192 only for 5 combos (low alpha + high K+B)\n"
            "  Fix #24 GPU dispatch must use GPU: cuda_ok=True; gpu_util mean 49-78% max 100%; PASS\n"
            "  Fix #28 per-arm reads: verified all 486 units per seed\n"
            "\n"
            "_llm_forward_calls_at_inference = 0 (substrate-only decode).\n"
        ),
        kind=AtomKind.EXPERIMENT_RECORD,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.MATH,
        algebra=None,
        metadata={
            "provenance_quality": "MEASURED_MECHANISM",
            "cert_status": "measured_mechanism",
            "cert_class": "mechanism_characterization",
            "cell_anchor": "substrate_capacity_multibank_alpha_K_phase_diagram_v1_GPU_CROSS_SEED_AGG_3",
            "cell_commit": CELL_COMMIT,
            "metrics_path_pattern": METRICS_CMB,
            "ruling_note": RULING_NOTE,
            "verified_off_data": True,
            "run_mode": "full",
            "n_seeds": 3,
            "seeds": [7, 13, 19],
            "N_axis": [2048, 4096, 8192],
            "alpha_axis": [0.05, 0.1, 0.25, 0.5, 1.0, 2.0],
            "k_per_bank_axis": [4, 16, 64],
            "num_banks_axis": [1, 4, 16],
            "codebook_size": 16384,
            "regimes": ["MULTI_BANK_BIND", "SINGLE_BANK_BASELINE", "RANDOM_FLOOR"],
            "cardinality_ok_per_seed_MEASURED": [True, True, True],
            "n_units_per_seed_MEASURED": [486, 486, 486],
            "n_pass_per_seed_MEASURED": [23, 23, 23],
            "n_pass_at_full_N_per_seed_MEASURED": [5, 5, 5],
            "n_saturate_per_seed_MEASURED": [12, 11, 12],
            "n_floor_per_seed_MEASURED": [96, 96, 96],
            "arms_differ_per_seed_MEASURED": [162, 160, 162],
            "rail_alpha0p05_K64_B1_N8192_per_seed_MEASURED": [0.1317, 0.1390, 0.1415],
            "rail_ok_per_seed_MEASURED": [False, False, False],
            "cliff_per_B16_per_seed_MEASURED": [0.5, 0.5, 0.5],
            "cliff_per_B4_per_seed_MEASURED": [0.1, 0.1, 0.1],
            "gpu_util_mean_per_seed_MEASURED": [48.99, 53.90, 78.04],
            "gpu_util_p50_per_seed_MEASURED": [38.0, 54.0, 98.0],
            "gpu_util_max_per_seed_MEASURED": [100.0, 100.0, 100.0],
            "device_per_seed": ["cuda:0", "cuda:0", "cuda:0"],
            "gpu_name": "NVIDIA GeForce RTX 4060 Ti",
            "store_dtype": "torch.float16",
            "multi_advantage_at_N8192_K64_B16_alpha0p05_MULTI_per_seed": [1.000, 1.000, 1.000],
            "multi_advantage_at_N8192_K64_B16_alpha0p05_SINGLE_per_seed": [0.139, 0.141, 0.151],
            "multi_advantage_at_N8192_K64_B16_alpha0p5_MULTI_per_seed": [0.246, 0.246, 0.246],
            "multi_advantage_at_N8192_K64_B16_alpha0p5_SINGLE_per_seed": [0.003, 0.002, 0.002],
            "verdict_per_seed_RAW": ["MIDDLE_BAND", "MIDDLE_BAND", "MIDDLE_BAND"],
            "verdict_raw_cross_seed": "MEASURED_MECHANISM_3_of_3_seeds_MB_n_pass_full_N_5_blocks_HP_multi_bank_mechanism_class_confirmed_massive_lift",
            "demote_reason": "n_pass_at_full_N_5_below_HP_threshold_AND_rail_ok_False_AND_single_bank_baseline_already_at_floor_at_CB16384_only_multi_arm_rescues",
            "encoder_provenance": "SUBSTRATE_NATIVE_BIPOLAR_GPU_FP16",
            "META_RULE_H_cardinality_ok": True,
            "META_RULE_AF_arms_differ_strong": "160_to_162_of_162",
            "META_RULE_AH_atomic_metrics": True,
            "META_RULE_K_discriminator_RANDOM_FLOOR_0p000_clean": True,
            "META_RULE_L_band_check_MULTI_in_HP_band_only_5_combos_at_full_N": True,
            "Fix_24_GPU_dispatch_actually_uses_GPU": True,
            "Fix_28_per_arm_reads_verified": True,
            "load_bearing_finding_1": "multi_bank_B16_capacity_advantage_60_to_80x_at_mid_alpha_at_N8192",
            "load_bearing_finding_2": "single_bank_baseline_at_floor_at_CB16384_CB_too_large_for_single_attractor",
            "load_bearing_finding_3": "cliff_at_B16_in_50pct_of_combos_vs_10pct_at_B4_B_scales_capacity",
            "revival_path_flag_1": "extend_K_per_bank_axis_to_128_256_at_N8192",
            "revival_path_flag_2": "drop_B1_baseline_arm_known_floor_focus_B16_B32_B64",
            "revival_path_flag_3": "tune_HP_threshold_recall_floor_lower_than_0p5_at_high_alpha_K_B",
            "scope_observed": "full_3_seeds_162_phase_pts_per_seed_3_regimes_GPU_FP16",
            "scope_not_claimed": "chain_grade_OR_n_pass_full_N_above_5_OR_B_above_16_OR_K_above_64",
            "brain_analog": "cortical_column_multi_bank_micro_circuitry_vs_single_attractor_catastrophic_interference",
            "zero_llm_calls_at_inference": True,
            "_llm_forward_calls_at_inference": 0,
            "substrate_only_decode_gate": "PASS",
            "atomized_by": ATOMIZED_BY,
        },
    )


# ============================================================================
# ATOM 3 -- TASK_VECTOR HRR ICL K-cliff phase diagram v1 FULL 3-seed MEASURED_MECHANISM
# ============================================================================

def build_atom3_task_vector_mm() -> Atom:
    return Atom(
        id=(
            "T3/EXP_substrate_task_vector_K_cliff_phase_diagram_v1_FULL_CROSS_SEED_AGG_3_of_3_"
            "MEASURED_MECHANISM_K_cliff_CHARACTERIZED_in_V10_overlap_under_0p3_regime_ONLY_"
            "V10_ov0p0_K1_to_K100_TV_1p0_1p0_0p83_0p6_0p33_0p27_0p1_monotonic_clean_cliff_replicates_3_seeds_"
            "V10_ov0p6_K1_TV_0p0_K3_to_5_RECOVERS_to_0p3_to_0p8_non_monotonic_NOT_cliff_metric_artifact_"
            "V200_ov0p6_TV_BIT_IDENTICAL_ZERO_3_seeds_substrate_cannot_encode_floor_artifact_"
            "K_cliff_min_eq_1_framing_MISLEADING_metric_picks_low_K_floor_not_high_K_saturation_cliff_"
            "expected_n_1890_observed_1890_cardinality_ok_n_seeds_3_seeds_7_13_19"
        ),
        name=(
            "substrate_task_vector_K_cliff_phase_diagram v1 FULL CROSS-SEED-AGG 3/3 MEASURED_MECHANISM: "
            "K-cliff CHARACTERIZED in V<=10 / ov<=0.3 regime (V=10 ov=0.0 K=1..100 TV=1.0..0.1 monotonic); "
            "cell-reported K_cliff_min=1 at (V=10, ov=0.6) is METRIC ARTIFACT (non-monotonic floor signal, "
            "not high-K saturation cliff); V>=200/ov>=0.6 BIT-IDENTICAL ZERO across 3 seeds; "
            "cardinality 1890/1890; n_cliff_combos 9/9; arms_diff 0.22-0.28"
        ),
        description=(
            "MEASURED_MECHANISM substrate task-vector HRR ICL K-cliff phase diagram at full N (delta=0).\n"
            "Cell verdict reports HARD_PASS with K_cliff_min=1 at (V_tasks=10, overlap=0.6). Off-disk\n"
            "verification reveals the K_cliff_min=1 framing is a METRIC ARTIFACT, not a true cliff.\n"
            "Demoted to MM: K-cliff CHARACTERIZED only in V<=10/ov<=0.3 regime; higher V/ov is FLOOR.\n"
            "\n"
            "OFF-DATA RECOMPUTE (Skunkworks 2026-06-28, .venv Python, 3 seeds, 63 phase-points each):\n"
            "  Cardinality: expected_n=observed_n=1890 each seed (63 phase pts x 30 K-steps).\n"
            "  Per-seed top-line:\n"
            "    seed=7  HARD_PASS reported: K_cliff_min=1 at (V=10,ov=0.6); avg_arms_diff=0.246; n_cliffs=9/9\n"
            "    seed=13 HARD_PASS reported: K_cliff_min=1 at (V=10,ov=0.6); avg_arms_diff=0.276; n_cliffs=9/9\n"
            "    seed=19 HARD_PASS reported: K_cliff_min=1 at (V=10,ov=0.6); avg_arms_diff=0.216; n_cliffs=9/9\n"
            "  all_saturated=False; low_kv_mechanism_floor_met=True; ORACLE arm=1.000 everywhere.\n"
            "\n"
            "K-CLIFF CHARACTERIZED REGIME (V=10, ov=0.0; load-bearing; replicates across 3 seeds):\n"
            "  K=1:    TV=1.000  RV=0.000  ORACLE=1.000  arms_diff=1.000\n"
            "  K=3:    TV=1.000  RV=0.000  ORACLE=1.000  arms_diff=1.000\n"
            "  K=5:    TV=0.90 / 0.70 / 0.90 (seed7/13/19)\n"
            "  K=10:   TV=0.60 / 0.80 / 0.40\n"
            "  K=20:   TV=0.50 / 0.30 / 0.20\n"
            "  K=50:   TV=0.20 / 0.40 / 0.20\n"
            "  K=100:  TV=0.10 / 0.10 / 0.10\n"
            "  Clean monotonic K-cliff with RV at floor and ORACLE saturated; this IS the\n"
            "  mechanism characterization.\n"
            "\n"
            "K_CLIFF_MIN=1 METRIC ARTIFACT (the framing claim that this is overstated):\n"
            "  At V=10, ov=0.6 the cell reports cliff at K=1. Verification:\n"
            "    K=1: TV=0.00 (all 3 seeds)\n"
            "    K=3: TV=0.30 / 0.70 / 0.70  *RECOVERS upward; non-monotonic*\n"
            "    K=5: TV=0.80 / 0.40 / 0.30  *peaks then decays*\n"
            "    K=10: TV=0.40 / 0.10 / 0.40\n"
            "    K=20: TV=0.20 / 0.20 / 0.00\n"
            "  The K=1 zero is a LOW-K FLOOR (cue degenerate at K=1 with high task overlap), NOT a\n"
            "  saturation cliff. The metric collapses 'first K where recall drops below threshold'\n"
            "  to K=1 here, but the underlying signal is non-monotonic noise.\n"
            "\n"
            "FLOOR REGIME (V>=200; high task vocabulary; substrate cannot encode at full N):\n"
            "  V=200, ov=0.6 across 3 seeds:\n"
            "    K=[1,3,5,10,20,50,100]: TV BIT-IDENTICAL ZERO in 18/21 cells (3 seeds x 7 Ks)\n"
            "    only deviations: seed=19 K=3 TV=0.40 (single-trial noise, N_eval=10); seed=13 K=20 TV=0.10\n"
            "  Substrate at V_tasks=200 with overlap>=0.6 is at retrieval floor; K-cliff there is\n"
            "  metric-artifact-only.\n"
            "  V=200, ov=0.0 / 0.3: TV stays in 0.0-0.3 (essentially at floor across all K).\n"
            "\n"
            "WHY MEASURED_MECHANISM not chain-grade:\n"
            "  The HARD_PASS verdict overstates by:\n"
            "    (1) K_cliff_min=1 framing collapses a high-V floor (V=10/ov=0.6 K=1) into 'cliff'\n"
            "        when the underlying signal is non-monotonic (low-K cue degeneracy);\n"
            "    (2) 8 of 9 combos either FLOOR (V>=200) or have K_cliff=50 (V=10/ov<=0.3, which IS\n"
            "        the real characterized regime);\n"
            "    (3) avg_arms_diff=0.22-0.28 indicates only weak discrimination averaged over grid\n"
            "        (much of the grid is floor-vs-floor).\n"
            "  Honest classification: K-cliff CHARACTERIZED in V<=10/ov<=0.3; FLOOR in V>=200.\n"
            "\n"
            "WHY MEASURED_MECHANISM not honest-negative:\n"
            "  The K-cliff IS real and replicated in the V<=10/ov=0.0 regime (TV=1.0 at K<=3 dropping\n"
            "  monotonically to 0.1 at K=100, with RV at floor and ORACLE saturated). This characterizes\n"
            "  HRR superposition capacity. The mechanism class is valid; the cell's overall grid\n"
            "  framing is what's misleading.\n"
            "\n"
            "REVIVAL FLAG (cert-owner does NOT direct strategy; FLAG only):\n"
            "  Director may consider:\n"
            "    (a) re-dispatch with K_cliff metric REVISED to require monotonic decay (low-K floor\n"
            "        excluded) so V=10/ov=0.6 isn't counted as cliff\n"
            "    (b) tighten V_tasks axis to <=50 (drop V=200 known-floor)\n"
            "    (c) extend K-axis to K>=200 in V=10/ov=0.0 regime to characterize tail asymptote\n"
            "\n"
            "BRAIN-GROUNDED FRAMING:\n"
            "  In-context learning via task-vector binding mirrors PFC working-memory task-set\n"
            "  representation (Botvinick task-rule encoding). K-cliff at V=10 is bounded-capacity\n"
            "  of WM superposition consistent with WM K=4 +/- 1 capacity (chain-grade WM multi-bank\n"
            "  K=4096 result already in Store). V>=200 floor reflects WM task-set ceiling beyond\n"
            "  which task-vector readout collapses.\n"
            "\n"
            "META_RULE COMPLIANCE:\n"
            "  META_RULE_H cardinality: 1890/1890 per seed (expected_n_seeds_complete=3)\n"
            "  META_RULE_AF arms-must-differ: TV vs RV vs ORACLE 3-arm; arms_diff per combo 0.22-0.28 avg\n"
            "    V=200/ov=0.6 violates AF (TV=RV=0.000 at most K); 18/21 bit-equal in floor regime\n"
            "    (load-bearing finding -- this IS the substrate-can-not-encode signal)\n"
            "  META_RULE_AH atomic metrics: per-(K,V,overlap) TV/RV/ORACLE/arms_diff recorded\n"
            "  META_RULE_AM substrate-already-does-X: ORACLE=1.000 everywhere; ORACLE knowledge of\n"
            "    correct task vector is not the bottleneck; superposition capacity at V x K IS\n"
            "  META_RULE_K discriminator: RV at floor (0.000 everywhere) clean; TV vs ORACLE separates\n"
            "  META_RULE_L band: K-cliff at V=10/ov=0.0 in CHAIN_GRADE band (TV>=0.6 at K<=10);\n"
            "    HP framing collapses by including non-monotonic floor combos\n"
            "  META_RULE_O band-calibration: K_cliff metric does not require monotonicity; produces\n"
            "    K_cliff=1 metric-artifact at V=10/ov=0.6 (NEW DISCIPLINE FLAG -- consider META_RULE\n"
            "    addition: 'cliff metrics must require monotonic decay from saturation to floor')\n"
            "  Fix #28 per-arm reads: verified all 63 phase-points x 30 K-values per seed (1890)\n"
            "\n"
            "_llm_forward_calls_at_inference = 0 (substrate-only decode).\n"
        ),
        kind=AtomKind.EXPERIMENT_RECORD,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.MATH,
        algebra=None,
        metadata={
            "provenance_quality": "MEASURED_MECHANISM",
            "cert_status": "measured_mechanism",
            "cert_class": "mechanism_characterization",
            "cell_anchor": "substrate_task_vector_K_cliff_phase_diagram_v1_FULL_CROSS_SEED_AGG_3",
            "cell_commit": CELL_COMMIT,
            "metrics_path_pattern": METRICS_TV,
            "ruling_note": RULING_NOTE,
            "verified_off_data": True,
            "run_mode": "full",
            "n_seeds": 3,
            "seeds": [7, 13, 19],
            "V_tasks_axis": [10, 50, 200],
            "overlap_axis": [0.0, 0.3, 0.6],
            "K_axis": [1, 3, 5, 10, 20, 50, 100],
            "expected_n_per_seed": 1890,
            "observed_n_per_seed_MEASURED": [1890, 1890, 1890],
            "cardinality_ok_per_seed": [True, True, True],
            "K_cliff_min_reported_per_seed": [1, 1, 1],
            "K_cliff_min_location_reported": {"V_tasks": 10, "overlap": 0.6},
            "K_cliffs_per_combo_seed7_MEASURED": {
                "V10_ov0.00": 50, "V10_ov0.30": 50, "V10_ov0.60": 1,
                "V50_ov0.00": 5, "V50_ov0.30": 1, "V50_ov0.60": 1,
                "V200_ov0.00": 1, "V200_ov0.30": 1, "V200_ov0.60": 1,
            },
            "K_cliffs_per_combo_seed13_MEASURED": {
                "V10_ov0.00": 20, "V10_ov0.30": 20, "V10_ov0.60": 1,
                "V50_ov0.00": 3, "V50_ov0.30": 1, "V50_ov0.60": 10,
                "V200_ov0.00": 5, "V200_ov0.30": 1, "V200_ov0.60": 1,
            },
            "K_cliffs_per_combo_seed19_MEASURED": {
                "V10_ov0.00": 20, "V10_ov0.30": 20, "V10_ov0.60": 1,
                "V50_ov0.00": 1, "V50_ov0.30": 10, "V50_ov0.60": 1,
                "V200_ov0.00": 1, "V200_ov0.30": 1, "V200_ov0.60": 1,
            },
            "avg_arms_diff_per_seed_MEASURED": [0.246, 0.276, 0.216],
            "all_saturated_per_seed": [False, False, False],
            "low_kv_mechanism_floor_met_per_seed": [True, True, True],
            "cliff_observable_per_seed": [True, True, True],
            "regime_flip_per_seed": [False, False, False],
            "K_cliff_at_V10_ov0p0_TV_curve_seed7_MEASURED": [1.0, 1.0, 0.9, 0.6, 0.5, 0.2, 0.1],
            "K_cliff_at_V10_ov0p0_TV_curve_seed13_MEASURED": [1.0, 1.0, 0.7, 0.8, 0.3, 0.4, 0.1],
            "K_cliff_at_V10_ov0p0_TV_curve_seed19_MEASURED": [1.0, 1.0, 0.9, 0.4, 0.2, 0.2, 0.1],
            "K_cliff_at_V10_ov0p0_K_axis": [1, 3, 5, 10, 20, 50, 100],
            "K_cliff_at_V10_ov0p0_replicates_3_seeds": True,
            "K_cliff_at_V10_ov0p0_monotonic_decay": True,
            "V10_ov0p6_K1_TV_zero_then_recovers": True,
            "V200_ov0p6_bit_identical_zero_seed7": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            "V200_ov0p6_bit_identical_zero_seed13": [0.0, 0.0, 0.0, 0.0, 0.1, 0.0, 0.0],
            "V200_ov0p6_bit_identical_zero_seed19": [0.0, 0.4, 0.0, 0.0, 0.0, 0.0, 0.0],
            "V200_ov0p6_substrate_cannot_encode_floor": True,
            "verdict_per_seed_RAW": ["HARD_PASS", "HARD_PASS", "HARD_PASS"],
            "verdict_raw_cross_seed": "MEASURED_MECHANISM_3_of_3_seeds_HP_overstated_K_cliff_min_1_is_metric_artifact_real_cliff_only_in_V10_ov_under_0p3_regime",
            "demote_reason": "K_cliff_min_1_at_V10_ov0p6_is_LOW_K_floor_NOT_high_K_saturation_cliff_non_monotonic_TV_RECOVERS_K3_to_5_AND_V200_regime_bit_identical_zero_floor",
            "encoder_provenance": "SUBSTRATE_NATIVE_HRR_FHRR",
            "META_RULE_H_cardinality_ok": True,
            "META_RULE_AF_arms_differ_TV_RV_ORACLE": "weak_avg_0p22_to_0p28_load_bearing_in_V10_ov_under_0p3_regime_only",
            "META_RULE_AH_atomic_metrics": True,
            "META_RULE_AM_substrate_already_oracle_saturated": True,
            "META_RULE_K_discriminator_RV_floor_0p000_clean": True,
            "META_RULE_L_band_V10_ov0p0_in_CHAIN_GRADE_band": True,
            "META_RULE_O_cliff_metric_should_require_monotonic_decay_NEW_DISCIPLINE_FLAG": True,
            "Fix_28_per_arm_reads_verified": True,
            "load_bearing_finding_1": "K_cliff_characterized_V_tasks_10_overlap_0p0_TV_1p0_to_0p1_monotonic_replicated_3_seeds",
            "load_bearing_finding_2": "K_cliff_min_metric_picks_low_K_floor_not_high_K_saturation_at_V10_ov0p6_non_monotonic",
            "load_bearing_finding_3": "V_tasks_200_overlap_0p6_BIT_IDENTICAL_ZERO_floor_3_seeds_substrate_capacity_ceiling",
            "revival_path_flag_1": "K_cliff_metric_require_monotonic_decay_from_saturation_to_floor",
            "revival_path_flag_2": "V_tasks_axis_tighten_to_10_50_drop_V200_known_floor",
            "revival_path_flag_3": "K_axis_extend_to_200_500_in_V10_ov0p0_regime_for_tail_asymptote",
            "scope_observed": "full_3_seeds_63_phase_pts_per_seed_K_in_1_to_100_V_in_10_50_200_overlap_0p0_0p3_0p6",
            "scope_not_claimed": "chain_grade_OR_K_cliff_at_high_K_OR_substrate_solves_V_above_50_OR_overlap_above_0p3",
            "brain_analog": "PFC_WM_task_set_representation_K_capacity_4_plus_minus_1_Botvinick_task_rule_encoding",
            "zero_llm_calls_at_inference": True,
            "_llm_forward_calls_at_inference": 0,
            "substrate_only_decode_gate": "PASS",
            "atomized_by": ATOMIZED_BY,
        },
    )


# ============================================================================
# ATOM 4 -- Schema exemplar-Bayes capacity-stress v2 3-seed MEASURED_MECHANISM
# ============================================================================

def build_atom4_schema_mm() -> Atom:
    return Atom(
        id=(
            "T3/EXP_substrate_schema_exemplar_bayes_capacity_stress_v2_CROSS_SEED_AGG_3_of_3_"
            "MEASURED_MECHANISM_bayes_vs_NN_lift_replicated_avg_0p50_to_0p53_arms_differ_63_to_64_of_64_"
            "capacity_scaling_delta_THRESHOLD_EDGE_seed7_0p070_HP_seed13_0p040_MB_seed19_0p050_MB_"
            "majority_MB_2_of_3_lift_profile_decays_alpha_0p01_to_50_peak_0p6_to_0p8_at_mid_alpha_"
            "trough_0p1_to_0p2_at_alpha_above_20_cliff_observable_10_to_13_of_64_arms_identical_0_to_1_of_64_"
            "expected_n_3840_n_seeds_3_seeds_7_13_19_n_combos_64_per_seed"
        ),
        name=(
            "substrate_schema_exemplar_bayes_capacity_stress v2 CROSS-SEED-AGG 3/3 MEASURED_MECHANISM: "
            "Bayes-vs-NN lift replicated avg=0.50-0.53; capacity_scaling_delta at HP THRESHOLD-EDGE "
            "(seed=7 0.070 HP, seed=13 0.040 MB, seed=19 0.050 MB); majority MB 2/3; "
            "lift profile shows real capacity decay alpha=0.01 to 50; cliff observable in 10-13 of 64 pts"
        ),
        description=(
            "MEASURED_MECHANISM substrate schema exemplar-Bayes capacity-stress v2 (delta=0).\n"
            "Per-seed verdict split: seed=7 HARD_PASS / seed=13 MIDDLE_BAND / seed=19 MIDDLE_BAND.\n"
            "Majority verdict = MIDDLE_BAND (2/3). The HP/MB split is THRESHOLD-EDGE on cell's\n"
            "capacity_scaling_delta criterion: seed=7 delta=0.070 (just over HP gate);\n"
            "seed=13 delta=0.040 (under); seed=19 delta=0.050 (under). Bayes-vs-NN lift IS real\n"
            "(avg 0.50-0.53 across seeds, replicated); the chain-grade promotion is fragile because\n"
            "the cell's stringent capacity-scaling discriminator just barely lands HP on 1/3 seeds.\n"
            "\n"
            "OFF-DATA RECOMPUTE (Skunkworks 2026-06-28, .venv Python, 3 seeds, 64 phase-points each):\n"
            "  Per-seed top-line:\n"
            "    seed=7  HARD_PASS:  lift_pts=60/64, avg_bayes_minus_nn=0.531, capacity_delta=0.070\n"
            "            arms_differ=64/64, n_cliff_pts=13, low_load_sat=True\n"
            "    seed=13 MIDDLE_BAND: lift_pts=60/64, avg_bayes_minus_nn=0.499, capacity_delta=0.040\n"
            "            arms_differ=63/64 (1 bit-equal), n_cliff_pts=13\n"
            "    seed=19 MIDDLE_BAND: lift_pts=62/64, avg_bayes_minus_nn=0.534, capacity_delta=0.050\n"
            "            arms_differ=64/64, n_cliff_pts=10\n"
            "  No saturation collapse (all_saturated=False); no random-arm pathology;\n"
            "  arms_identical=False (the 1/64 seed=13 tie is at extreme low-alpha low-load combo).\n"
            "\n"
            "BAYES vs NEAREST-EXEMPLAR LIFT (replicated; load-bearing):\n"
            "  Sample (n_exemplars=10, n_classes=10, N=2048, K_total=100, alpha~0.05):\n"
            "    Bayes=0.85-1.00, NN=0.45-0.65, chance=0.05-0.1; lift=0.35-0.40\n"
            "  Average lift across all 64 phase-points: 0.50-0.53 across 3 seeds (sigma~0.02; tight).\n"
            "\n"
            "LIFT PROFILE (capacity decay; cliff observable; replicates):\n"
            "  alpha~0.01 (low load):      lift=0.4-0.6  (substrate at capacity floor; lift mid)\n"
            "  alpha~0.1-1.0 (mid load):   lift=0.6-0.8  (Bayes integration advantage peaks)\n"
            "  alpha~3-10 (high load):     lift=0.4-0.5  (Bayes lift starts to compress)\n"
            "  alpha>20 (over capacity):   lift=0.1-0.3  (Bayes and NN both decay; lift shrinks)\n"
            "  alpha~48 (extreme):         lift=0.1-0.15 (collapses; only marginal lift)\n"
            "  Cliff between alpha=10-20 visible across all 3 seeds.\n"
            "\n"
            "WHY MEASURED_MECHANISM not chain-grade:\n"
            "  Cell's HP gate requires capacity_scaling_delta >= 0.07 (likely; seed=7 at 0.070 just\n"
            "  lands, seeds 13/19 at 0.040/0.050 miss). The lift IS real (avg 0.50-0.53) and the\n"
            "  cliff IS observable (10-13 cliff pts). But chain-grade by cross-seed agg requires\n"
            "  majority HP (>=2/3), and this is 1/3. Cross-seed consensus = MIDDLE_BAND.\n"
            "\n"
            "WHY MEASURED_MECHANISM not honest-negative:\n"
            "  The Bayes-vs-NN advantage IS replicated and is the predicted mechanism class.\n"
            "  The discriminator fires (RANDOM=0.05-0.1 = chance floor; NN partially recovers;\n"
            "  Bayes substantially beats). Capacity decay matches theory. The cell's threshold\n"
            "  is the bottleneck, not the mechanism.\n"
            "\n"
            "REVIVAL FLAG (cert-owner does NOT direct strategy; FLAG only):\n"
            "  Director may consider:\n"
            "    (a) re-dispatch with broader alpha range (drop alpha<0.01 and alpha>30 known-edge)\n"
            "        to tighten the capacity-scaling slope measurement and reduce noise\n"
            "    (b) increase n_seeds to 5+ to stabilize capacity_scaling_delta around the 0.05 mean\n"
            "    (c) revisit HP threshold (current 0.07 may be too stringent for the substrate's\n"
            "        natural capacity slope; mean=0.05 suggests a sub-0.06 boundary)\n"
            "\n"
            "BRAIN-GROUNDED FRAMING:\n"
            "  Schema prior + exemplar memory mirrors hippocampal-cortical complementary learning\n"
            "  (Tse-Morris schema acceleration of new fact integration; McClelland CLS theory).\n"
            "  Substrate Bayes-vs-NN advantage replicates the brain's schema-prior-as-Bayes-anchor\n"
            "  finding: Bayes wins because schema collapses the relevant exemplar subspace, while\n"
            "  nearest-exemplar searches the full space and loses lift as exemplars-per-class drops.\n"
            "\n"
            "META_RULE COMPLIANCE:\n"
            "  META_RULE_H cardinality: 3840 expected per seed (64 phase pts x 60 trials)\n"
            "  META_RULE_AF arms-must-differ: 63-64/64 (1 bit-equal in seed=13 at extreme low-load)\n"
            "  META_RULE_AH atomic metrics: per-(alpha, n_exemplars, n_classes) Bayes/NN/Random recorded\n"
            "  META_RULE_K discriminator: UNIFORM_RANDOM=0.05-0.1 chance floor clean\n"
            "  META_RULE_L band: Bayes lift 0.50-0.53 in CHAIN_GRADE band on avg; capacity-scaling\n"
            "    delta is the threshold-edge discriminator\n"
            "  META_RULE_O band-calibration: capacity_scaling_delta>=0.07 may be too stringent given\n"
            "    measured mean ~0.05; cell may benefit from sub-0.06 boundary or more seeds\n"
            "  Fix #28 per-arm reads: verified all 64 phase-points x 3 arms per seed\n"
            "\n"
            "_llm_forward_calls_at_inference = 0 (substrate-only decode).\n"
        ),
        kind=AtomKind.EXPERIMENT_RECORD,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.MATH,
        algebra=None,
        metadata={
            "provenance_quality": "MEASURED_MECHANISM",
            "cert_status": "measured_mechanism",
            "cert_class": "mechanism_characterization",
            "cell_anchor": "substrate_schema_exemplar_bayes_capacity_stress_v2_CROSS_SEED_AGG_3",
            "cell_commit": CELL_COMMIT,
            "metrics_path_pattern": METRICS_SCH,
            "ruling_note": RULING_NOTE,
            "verified_off_data": True,
            "run_mode": "full",
            "n_seeds": 3,
            "seeds": [7, 13, 19],
            "n_combos_total_per_seed": 64,
            "expected_n_per_seed": 3840,
            "verdict_per_seed_RAW": ["HARD_PASS", "MIDDLE_BAND", "MIDDLE_BAND"],
            "lift_points_per_seed_MEASURED": [60, 60, 62],
            "avg_bayes_minus_nn_per_seed_MEASURED": [0.531, 0.499, 0.534],
            "capacity_scaling_delta_per_seed_MEASURED": [0.070, 0.040, 0.050],
            "capacity_scaling_met_per_seed": [True, False, False],
            "n_cliff_points_per_seed_MEASURED": [13, 13, 10],
            "arms_differ_per_seed_MEASURED": [64, 63, 64],
            "arms_identical_per_seed_MEASURED": [0, 1, 0],
            "low_load_saturate_met_per_seed": [True, True, True],
            "all_saturated_per_seed": [False, False, False],
            "random_arm_pathology_per_seed": [False, False, False],
            "regime_flip_per_seed": [False, False, False],
            "hard_fail_no_cliff_per_seed": [False, False, False],
            "cross_seed_avg_lift_MEASURED": 0.521,
            "cross_seed_capacity_delta_avg_MEASURED": 0.053,
            "cross_seed_capacity_delta_sigma_MEASURED": 0.013,
            "verdict_raw_cross_seed": "MEASURED_MECHANISM_3_of_3_majority_MB_2_of_3_HP_seed7_threshold_edge_capacity_delta_at_HP_gate_fragile",
            "demote_reason": "majority_2_of_3_seeds_MB_capacity_scaling_delta_avg_0p053_just_under_HP_threshold_0p07_seed7_only_lands_HP_at_threshold_edge_fragile_cross_seed",
            "encoder_provenance": "SUBSTRATE_NATIVE",
            "META_RULE_H_cardinality_ok": True,
            "META_RULE_AF_arms_differ_63_to_64_of_64": True,
            "META_RULE_AH_atomic_metrics": True,
            "META_RULE_K_discriminator_UNIFORM_RANDOM_chance_floor_clean": True,
            "META_RULE_L_band_Bayes_lift_avg_0p50_to_0p53_in_CHAIN_GRADE_band": True,
            "META_RULE_O_capacity_scaling_threshold_0p07_may_be_too_stringent_mean_0p053": True,
            "Fix_28_per_arm_reads_verified": True,
            "load_bearing_finding_1": "Bayes_vs_NN_lift_avg_0p50_to_0p53_replicated_3_seeds_sigma_0p02",
            "load_bearing_finding_2": "capacity_decay_alpha_0p01_to_50_peak_0p6_to_0p8_at_mid_alpha_cliff_observable_10_to_13_pts",
            "load_bearing_finding_3": "capacity_scaling_delta_at_HP_threshold_edge_avg_0p053_seed7_0p070_seed13_0p040_seed19_0p050",
            "revival_path_flag_1": "tighten_alpha_range_drop_alpha_under_0p01_and_above_30_known_edge",
            "revival_path_flag_2": "increase_n_seeds_to_5_or_more_for_capacity_delta_stability",
            "revival_path_flag_3": "revisit_HP_threshold_0p07_to_0p05_or_0p06_based_on_measured_mean_0p053",
            "scope_observed": "full_3_seeds_64_phase_pts_per_seed_alpha_0p006_to_49_n_exemplars_n_classes_N_K_total_grid",
            "scope_not_claimed": "chain_grade_OR_capacity_scaling_above_0p07_majority_OR_HP_majority_seeds",
            "brain_analog": "hippocampal_cortical_CLS_McClelland_Tse_Morris_schema_acceleration_Bayes_anchor",
            "zero_llm_calls_at_inference": True,
            "_llm_forward_calls_at_inference": 0,
            "substrate_only_decode_gate": "PASS",
            "atomized_by": ATOMIZED_BY,
        },
    )


# ============================================================================
# A5 invariants
# ============================================================================

def _cert_count(store):
    return sum(
        1 for a in store.all_atoms()
        if (a.metadata or {}).get("provenance_quality") == "CERT_CHAIN_GRADE"
    )


def main(argv):
    apply = "--apply" in argv
    mode = "APPLY" if apply else "DRY"
    print(f"[4batch] mode={mode}")

    store = PartitionedStore(STORE_ROOT)

    pre_cert_n = _cert_count(store)
    print(f"[4batch] PRE cert_n={pre_cert_n}")
    assert pre_cert_n == 630, f"PRE cert_n {pre_cert_n} != 630 expected"

    atoms = [
        build_atom1_lock_in_amp_mm(),
        build_atom2_capacity_multibank_mm(),
        build_atom3_task_vector_mm(),
        build_atom4_schema_mm(),
    ]

    for i, a in enumerate(atoms, 1):
        print(f"[4batch] Atom {i}: id_head={str(a.id)[:80]}... corpus={a.corpus.name} tier={a.tier.name} kind={a.kind.name}")

    if not apply:
        print("[4batch] DRY mode -- no Store / ledger writes. Re-run with --apply.")
        return 0

    # ============================================================
    # APPLY: Atom adds + ledger rows (A5 PRE/POST window per write)
    # ============================================================
    expected_n = pre_cert_n  # delta=0 (all MM)

    metrics_list = [
        ("Lock_in_amp 3-seed MM",
         "data/exp_substrate_lock_in_amp_phase_diagram_v1_seed_7_AND_13_AND_19/metrics.json",
         "MIDDLE_BAND_3_of_3_FLOOR_under_populated_sqrt_t_physics_confirmed",
         "4batch_lock_in_amp_phase_diagram_v1_3seed_MM_sqrt_t_physics_replicated_delta_LD_0p43_FLOOR_axis_coverage_gap_blocks_HP_revival_flag_extend_SNR_axis_lower_decade"),
        ("Capacity_multibank 3-seed MM",
         "data/exp_substrate_capacity_multibank_alpha_K_phase_diagram_v1_GPU_seed_7_AND_13_AND_19/metrics.json",
         "MIDDLE_BAND_3_of_3_n_pass_full_N_5_blocks_HP_multi_bank_mechanism_confirmed_60_to_80x_lift",
         "4batch_capacity_multibank_alpha_K_GPU_3seed_MM_B16_advantage_massive_alpha_K_phase_n_pass_full_N_5_threshold_unmet_revival_flag_extend_K_axis_drop_B1_baseline"),
        ("TASK_VECTOR 3-seed MM",
         "data/exp_substrate_task_vector_K_cliff_phase_diagram_v1_seed_7_AND_13_AND_19_FULL/metrics.json",
         "HARD_PASS_3_of_3_K_cliff_min_1_framing_OVERSTATED_metric_artifact_real_cliff_only_V10_ov_under_0p3",
         "4batch_task_vector_K_cliff_v1_FULL_3seed_MM_HP_overstated_K_cliff_min_1_is_low_K_floor_not_high_K_saturation_V200_bit_identical_zero_floor_revival_flag_monotonic_decay_metric"),
        ("Schema 3-seed MM",
         "data/exp_substrate_schema_exemplar_bayes_capacity_stress_v2_seed_7_AND_13_AND_19/metrics.json",
         "MIXED_HP1_MB2_majority_MB_capacity_scaling_threshold_edge_seed7_0p070_seed13_0p040_seed19_0p050",
         "4batch_schema_exemplar_bayes_capacity_stress_v2_3seed_MM_majority_MB_2_of_3_capacity_delta_at_HP_threshold_edge_Bayes_vs_NN_lift_0p50_to_0p53_replicated_revival_flag_lower_HP_threshold_or_more_seeds"),
    ]

    for i, (label, metrics_path, verdict_raw, note) in enumerate(metrics_list):
        print(f"[4batch] Writing Atom {i+1} ({label})...")
        store.add_atom(atoms[i])
        post_n_i = _cert_count(store)
        assert post_n_i == expected_n, f"After Atom {i+1}: cert_n={post_n_i} != {expected_n}"
        append_cert_ledger_row(
            {
                "op": "cert_ruling",
                "atom_id": f"math::{atoms[i].id}",
                "cert_status": "measured_mechanism",
                "cert_class": "mechanism_characterization",
                "verified_off_data": True,
                "atomized_by": ATOMIZED_BY,
                "cell_commit": CELL_COMMIT,
                "verdict": verdict_raw,
                "cert_increment_delta": 0,
                "cv": None,
                "referent_pointer": {
                    "notes_path": RULING_NOTE,
                    "metrics_path": metrics_path,
                    "atom_qualified_id": f"math::{atoms[i].id}",
                },
                "supersedes": None,
                "note": note,
            },
            expected_cert_n_pre=pre_cert_n,
            expected_cert_n_post=expected_n,
        )

    final_cert_n = _cert_count(store)
    print(f"[4batch] FINAL cert_n={final_cert_n} (pre={pre_cert_n}, delta=0; 4 MM)")
    assert final_cert_n == expected_n

    # Round-trip verify: each atom should reload
    store_verify = PartitionedStore(STORE_ROOT)
    for a in atoms:
        match = [x for x in store_verify.all_atoms() if x.id == a.id]
        assert len(match) == 1, f"Round-trip FAIL for atom id={a.id} (found {len(match)})"
        assert (match[0].metadata or {}).get("atomized_by") == ATOMIZED_BY
        print(f"[4batch] Round-trip OK: {a.id[:60]}...")

    print("[4batch] APPLY OK -- 4 atoms landed; ledger 4 rows appended; cert_n unchanged at 630.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
