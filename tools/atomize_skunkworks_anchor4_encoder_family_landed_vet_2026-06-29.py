"""Atomize: Skunkworks landed-VET ANCHOR 4 encoder-family phase diagram v1 (2026-06-29).

Source request (Research spawn 2026-06-29 ~03:10 UTC):
  Cell substrate_anchor4_encoder_family_phase_diagram_v1 -- 3 seeds (7/13/19) -- claimed
  3-seed FULL HARD_PASS_ENCODER_DISCRIMINATION with 3/4 encoders chain-grade.

VERIFY-OFF-DATA recompute (.venv Python; each metrics.json Read end-to-end; per-arm + per-
encoder + per-phase-point recomputed; mechanism-class audit applied):

  Disk truth:
    - All 3 seeds are SMOKE not FULL: run_mode='smoke'; phase_map_len=32; expected_n_units=32;
      elapsed_s in [0.37, 0.38, 0.38]; FULL would have phase_map_len=48
    - The (non-_smoke) dirs exp_substrate_anchor4_encoder_family_phase_diagram_v1_seed_{7,13,19}
      contain ONLY selftest output (1.8KB metrics.json, verdict=SELFTEST_OK, elapsed_s=0.14)
    - Per-encoder per-seed Pareto outcome counts (recomputed from phase_map):
        seed_7  : td=31 rd=1  tie=0  dom_rate=0.9688 (binary/HRR/FHRR all 8/8; sparse 7/8)
        seed_13 : td=32 rd=0  tie=0  dom_rate=1.0000 (binary/HRR/FHRR all 8/8; sparse 8/8)
        seed_19 : td=31 rd=1  tie=0  dom_rate=0.9688 (binary/HRR/FHRR all 8/8; sparse 7/8)
    - Encoder pair distinctness (recomputed): n_pairs_differ=3 of 6 for every seed; ALL three
      seeds:
        binary_bipolar_vs_hrr_real       = False  (IDENTICAL phase outputs)
        binary_bipolar_vs_fhrr           = False  (IDENTICAL phase outputs)
        hrr_real_vs_fhrr                 = False  (IDENTICAL phase outputs)
        binary_bipolar_vs_sparse_bipolar = True
        hrr_real_vs_sparse_bipolar       = True
        fhrr_vs_sparse_bipolar           = True
      Mechanism hash collision across binary/HRR/FHRR on every seed (e.g. seed_7 all three at
      mechanism_hash=fdd38e6e7951021a). Only sparse_bipolar is observationally distinct.
    - per_encoder_chain_grade_pass (from cell):
        seed_7  : binary=True hrr=True fhrr=True sparse=False  (3/4)
        seed_13 : binary=True hrr=True fhrr=True sparse=True   (4/4)  <-- spawn claimed 3/4 (mismatch)
        seed_19 : binary=True hrr=True fhrr=True sparse=False  (3/4)
    - sparse_bipolar recency_decode_acc_mean ~ [0.44, 0.41, 0.42] across seeds (CHANCE-level
      for 200 atoms with 6-active-bit sparse encoding at N=128); the cell's chain-grade gate
      checks Pareto dominance only, NOT recency_decode_acc, so sparse's Pareto win at seed_13
      (RANDOM was even WORSE) is uninformative as evidence of mechanism strength.

  Spawn-prompt claims vs disk:
    Spawn "3-seed FULL"                        -- INCORRECT (SMOKE; 32 not 48 phase points)
    Spawn "seed_7  TD_wins 45/48, RD 3/48"     -- DISK 31/32 (1/32) at 0.9688 vs claimed 0.938
    Spawn "seed_13 TD_wins 47/48, RD 1/48"     -- DISK 32/32 (0/32) at 1.000  vs claimed 0.979
    Spawn "seed_19 TD_wins 45/48, RD 3/48"     -- DISK 31/32 (1/32) at 0.9688 vs claimed 0.938
    Spawn "3/4 encoders pass per seed"         -- DISK seed_13=4/4 (sparse PASSED there)
    Spawn "BINARY/HRR/FHRR pass; SPARSE dom'd" -- TRUE in directionality but binary/HRR/FHRR
                                                  produce identical bits (n_pairs_differ=3),
                                                  so this is ONE observed mechanism family
                                                  not THREE independent witnesses

CERT-TIER DECISION: MEASURED_MECHANISM (NOT chain-grade)

  Rationale (per Fix #28 + BIAS-Q saturation + by-construction-degeneracy):
    1) Run mode is smoke not FULL; cardinality 32 < advertised 48. The FULL evidence the
       spawn message references does not exist on disk for any seed.
    2) Encoder-family-invariance claim is observationally HOLLOW at this regime: only 3/6
       pairs differ; binary/HRR/FHRR collapse to identical (pareto_outcome, td_composite,
       recency_decode_acc) vectors at EVERY phase point. They are not 3 independent witnesses
       of "encoder-family-invariant TD>RD"; they are 3 redundant code paths producing
       identical observable bits.
    3) Sparse_bipolar's "chain-grade pass at seed_13" is by-construction-uninformative: the
       gate ignores recency_decode_acc; sparse's recency_decode_acc_mean=0.405 (~chance for
       200 atoms 6-active-bit at N=128). Pareto-vs-random wins are only informative when the
       decoder works; here both mechanism and random fail and TD happens to fail less.
    4) Prior chain-grade T3/EXP_substrate_time_decay_eviction_phase_diagram_v2_Pareto_AUC_
       CROSS_SEED_AGG_3_of_3_chain_grade_phase_characterization (70 phase points, atomized
       2026-06-28) already covers TD>RD for the time-decay-eviction mechanism with the
       binary_bipolar encoder; THIS cell at 32-point smoke does not extend that evidence
       beyond restating the same finding (binary/HRR/FHRR observably degenerate) plus the
       sparse-failure characterization.

  The HONEST CONTENT this cell adds (and what we atomize):
    - MEASURED_MECHANISM: sparse_bipolar 6-active-bit encoding at N=128 / R_BUCKETS=64 /
      n_atoms=200 falls into a low-recency-decode-acc regime (~0.4 mean across seeds);
      Pareto-AUC vs random stays at 7-8/8 because RANDOM eviction is even worse, but the
      decoder fidelity is at chance. This is regime-conditional collapse, not a robust
      encoder-family-invariance demonstration.
    - META_RULE: a CG gate that checks only Pareto outcome (TD>RD) without floor-gating
      recency_decode_acc can produce "chain-grade pass" on a regime where BOTH arms have
      broken decoders; pair every Pareto-AUC gate with a recency_decode_acc floor.
    - META_RULE: "20-300x sparse_bipolar bundle lift" (2026-06-23 finding) is regime-
      conditional, not a substrate-architecture invariant; verify at TARGET regime before
      citing.

  Net cert delta: 0 chain_grade; +1 MEASURED_MECHANISM (encoder-regime-collapse evidence);
                  +2 META rules (gate-recency-decoupling + sparse-bundle-lift-regime-cond).

PRE CERT N (verified live): 632
POST CERT N (predicted; A5-gated): 632 (no chain_grade increment)

LEDGER ROWS: 3 (1 measured_mechanism + 2 discipline_meta)

A5 GATING: PRE/POST cert_n assertions on every window; round-trip pq check on every atom.

Run:
  .venv/Scripts/python.exe tools/atomize_skunkworks_anchor4_encoder_family_landed_vet_2026-06-29.py            # DRY
  .venv/Scripts/python.exe tools/atomize_skunkworks_anchor4_encoder_family_landed_vet_2026-06-29.py --apply    # WRITE
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
RULING_NOTE = "notes/skunkworks_landed_vet_anchor4_encoder_family_MM_2026-06-29.md"
CELL_COMMIT = "33b4aa28"
ATOMIZED_BY = "skunkworks_atomize_anchor4_encoder_family_landed_vet_2026-06-29"

METRICS_SEED_7  = "data/exp_substrate_anchor4_encoder_family_phase_diagram_v1_seed_7_smoke/metrics.json"
METRICS_SEED_13 = "data/exp_substrate_anchor4_encoder_family_phase_diagram_v1_seed_13_smoke/metrics.json"
METRICS_SEED_19 = "data/exp_substrate_anchor4_encoder_family_phase_diagram_v1_seed_19_smoke/metrics.json"


# ============================================================================
# ATOM 1 -- ANCHOR 4 encoder-family phase diagram v1 3-seed MEASURED_MECHANISM
# ============================================================================

def build_atom1_anchor4_encoder_mm() -> Atom:
    return Atom(
        id=(
            "T3/EXP_substrate_anchor4_encoder_family_phase_diagram_v1_3seed_MEASURED_MECHANISM_smoke_"
            "seed_7_dom_0p9688_seed_13_dom_1p000_seed_19_dom_0p9688_binary_hrr_fhrr_observationally_"
            "degenerate_n_pairs_differ_3_of_6_sparse_bipolar_DOMINATED_at_low_N_regime_recency_acc_"
            "mean_0p41_chance_floor_cardinality_smoke_32_FULL_48_run_mode_smoke_not_full"
        ),
        name=(
            "substrate_anchor4_encoder_family_phase_diagram_v1 3-seed MEASURED_MECHANISM at smoke: "
            "binary/HRR/FHRR produce IDENTICAL phase outputs (n_pairs_differ=3 of 6); only sparse_bipolar "
            "is observationally distinct and recency_decode_acc_mean=0.41 (chance floor) at N=128 / "
            "n_atoms=200 / 6-active-bits sparse; cert tier MM not chain-grade (by-construction-degeneracy "
            "+ smoke not FULL + recency-decode at chance)"
        ),
        description=(
            "MEASURED_MECHANISM landed-VET of cell substrate_anchor4_encoder_family_phase_diagram_v1 over\n"
            "3 seeds (7, 13, 19), commit 33b4aa28. Cell verdicts SMOKE_HARD_PASS per seed; cert-owner\n"
            "Skunkworks downgrades to MM on Fix #28 + by-construction-degeneracy grounds.\n"
            "\n"
            "OFF-DATA RECOMPUTE (Skunkworks 2026-06-29, .venv Python, per-arm + per-encoder + per-phase-\n"
            "point cross-checked against summary fields; spawn-prompt claims independently verified):\n"
            "\n"
            "  Run mode (CRITICAL): all 3 metrics.json files at data/exp_substrate_anchor4_encoder_\n"
            "  family_phase_diagram_v1_seed_{7,13,19}_smoke/metrics.json carry run_mode='smoke',\n"
            "  expected_n_units=32, observed_n_units=32, phase_map_len=32, elapsed_s in [0.37,0.38].\n"
            "  The (non-_smoke) seed_{7,13,19} dirs contain ONLY selftest output: 1.8KB metrics.json\n"
            "  with verdict=SELFTEST_OK and elapsed_s=0.14. FULL run (48 phase points) does NOT exist\n"
            "  on disk for any seed. Spawn-prompt claim '3-seed FULL' is incorrect.\n"
            "\n"
            "  Per-seed recomputed from phase_map:\n"
            "    seed_7  : td=31/32 rd=1/32 tie=0 dom_rate=0.9688 net_dom=0.9375 rd_loss=0.0312\n"
            "    seed_13 : td=32/32 rd=0/32 tie=0 dom_rate=1.0000 net_dom=1.0000 rd_loss=0.0000\n"
            "    seed_19 : td=31/32 rd=1/32 tie=0 dom_rate=0.9688 net_dom=0.9375 rd_loss=0.0312\n"
            "  These match the summary fields. (Spawn-prompt claimed 45/48, 47/48, 45/48 -- those\n"
            "  ratios approximate the dom_rates but the absolute counts come from a phantom 48-point\n"
            "  FULL that did not run.)\n"
            "\n"
            "  Per-encoder per-seed Pareto wins (recomputed):\n"
            "    seed_7  binary_bipolar n=8 td=8/8 dom=1.000 recency=1.000 -> chain_grade_PASS\n"
            "    seed_7  hrr_real       n=8 td=8/8 dom=1.000 recency=1.000 -> chain_grade_PASS\n"
            "    seed_7  fhrr           n=8 td=8/8 dom=1.000 recency=1.000 -> chain_grade_PASS\n"
            "    seed_7  sparse_bipolar n=8 td=7/8 dom=0.875 recency=0.441 -> chain_grade_FAIL\n"
            "    seed_13 binary_bipolar n=8 td=8/8 dom=1.000 recency=1.000 -> chain_grade_PASS\n"
            "    seed_13 hrr_real       n=8 td=8/8 dom=1.000 recency=1.000 -> chain_grade_PASS\n"
            "    seed_13 fhrr           n=8 td=8/8 dom=1.000 recency=1.000 -> chain_grade_PASS\n"
            "    seed_13 sparse_bipolar n=8 td=8/8 dom=1.000 recency=0.405 -> chain_grade_PASS (!)\n"
            "    seed_19 binary_bipolar n=8 td=8/8 dom=1.000 recency=1.000 -> chain_grade_PASS\n"
            "    seed_19 hrr_real       n=8 td=8/8 dom=1.000 recency=1.000 -> chain_grade_PASS\n"
            "    seed_19 fhrr           n=8 td=8/8 dom=1.000 recency=1.000 -> chain_grade_PASS\n"
            "    seed_19 sparse_bipolar n=8 td=7/8 dom=0.875 recency=0.424 -> chain_grade_FAIL\n"
            "  Spawn-prompt 'n_chain_grade 3/4 encoders per seed' is INCORRECT at seed_13: the cell\n"
            "  reports n_encoders_chain_grade=4 there. The cell's gate is Pareto-only -- sparse won\n"
            "  8/8 at seed_13 because RANDOM eviction did even worse than sparse's broken decoder.\n"
            "\n"
            "  Encoder pair distinctness (recomputed per seed; identical across all 3 seeds):\n"
            "    binary_bipolar_vs_hrr_real       = False  (identical phase outputs)\n"
            "    binary_bipolar_vs_fhrr           = False  (identical phase outputs)\n"
            "    hrr_real_vs_fhrr                 = False  (identical phase outputs)\n"
            "    binary_bipolar_vs_sparse_bipolar = True\n"
            "    hrr_real_vs_sparse_bipolar       = True\n"
            "    fhrr_vs_sparse_bipolar           = True\n"
            "  n_pairs_differ = 3 of 6 (every seed). Mechanism-hash level: binary/HRR/FHRR collapse\n"
            "  to a SINGLE mechanism_hash on every seed (e.g. seed_7 fdd38e6e7951021a). 'Three\n"
            "  encoders pass chain-grade' overstates: ONE observable mechanism (the common phase-\n"
            "  output pattern) is exercised by three redundant encoder code paths producing\n"
            "  byte-identical phase-grid bits.\n"
            "\n"
            "  Sparse_bipolar recency_decode_acc_mean:\n"
            "    seed_7  : 0.4413   seed_13: 0.4050   seed_19: 0.4237\n"
            "  For 200-atom keys these are ~chance (uniform-random baseline 1/200 = 0.005; with\n"
            "  retrieval-cleanup the floor sits well above 1/200 due to bucket structure -- the\n"
            "  observed ~0.41 indicates the sparse encoder retrieves ~half the alive working set\n"
            "  with the recency cue, vs ~1.0 for binary/HRR/FHRR). This is a regime collapse for\n"
            "  sparse_bipolar at N=128 / 6-active-bits / 200 atoms.\n"
            "\n"
            "WHY MEASURED_MECHANISM NOT CHAIN_GRADE (Skunkworks-cert-owner; multi-cause):\n"
            "  (a) Run mode is smoke not FULL (32 phase points, not 48). Smoke does not promote.\n"
            "  (b) Encoder-family-invariance is observationally hollow: 3/6 pair distinctness;\n"
            "      binary/HRR/FHRR are 3 code paths producing identical bits. The cell does not\n"
            "      establish 3 INDEPENDENT chain-grade witnesses; it establishes 1 mechanism family\n"
            "      observed via 3 redundant encoder implementations PLUS 1 distinct encoder (sparse)\n"
            "      that fails 2/3 seeds.\n"
            "  (c) The 1 'sparse_bipolar passes chain-grade' point (seed_13) is by-construction\n"
            "      uninformative: the cell's chain-grade gate ignores recency_decode_acc; sparse's\n"
            "      decoder is at ~chance (0.405); random eviction is even worse so TD wins Pareto,\n"
            "      but neither arm's readout is meaningful.\n"
            "  (d) Prior CG T3/EXP_substrate_time_decay_eviction_phase_diagram_v2_Pareto_AUC_\n"
            "      CROSS_SEED_AGG_3_of_3 (70 phase points, atomized 2026-06-28) already covers\n"
            "      TD>RD for the eviction mechanism with binary_bipolar. This cell at 32-pt smoke\n"
            "      does not extend that finding.\n"
            "\n"
            "WHY NOT HARD_FAIL: the mechanism (time-decay eviction > random eviction in TD-decay\n"
            "  regimes) is real and reproduces. The cell's smoke verdicts and the Pareto signal at\n"
            "  binary/HRR/FHRR encoders are honest. What's not supported is the framing 'encoder-\n"
            "  family-invariant chain-grade phase characterization'.\n"
            "\n"
            "HONEST CONTENT ADDED (what this MM atom certifies):\n"
            "  1. NEGATIVE RESULT (regime-conditional collapse): sparse_bipolar 6-active-bit\n"
            "     encoding at N=128 / R_BUCKETS=64 / n_atoms=200 produces recency_decode_acc near\n"
            "     chance (~0.41 mean across seeds). This is a low-N capacity-floor for sparse\n"
            "     encoders, NOT a substrate-architecture invariant. The 2026-06-23 '20-300x bundle\n"
            "     lift' finding for sparse_bipolar therefore applies in a different regime; cite it\n"
            "     regime-conditionally not universally.\n"
            "  2. OBSERVATIONAL DEGENERACY: at this phase-grid regime binary_bipolar, hrr_real, and\n"
            "     fhrr produce byte-identical (pareto_outcome, td_composite, recency_decode_acc)\n"
            "     vectors. For ENCODER discrimination at low-N, none of the existing 4 encoders is\n"
            "     a discriminating lever in the (binary, HRR, FHRR) sub-family. A future encoder-\n"
            "     discrimination cell needs either higher N, smaller working-set ratio, or a 5th\n"
            "     encoder (e.g. quasi-orthogonal codebook) to break the degeneracy.\n"
            "\n"
            "FALSIFIED PREDICTION: '4 distinct encoder families would show 4 distinct phase outputs'.\n"
            "  Empirical: 3 of 4 collapse to 1 output family at this regime.\n"
            "\n"
            "META_RULE COMPLIANCE:\n"
            "  META_RULE_H cardinality: smoke 32/32 OK; FULL 48 not run (spawn-prompt overclaim)\n"
            "  META_RULE_AF arms-must-differ: 4/4 encoder TD-vs-RD hashes differ per encoder family\n"
            "    BUT cross-encoder TD hashes COLLAPSE (binary == hrr == fhrr; only sparse distinct)\n"
            "  META_RULE_AH atomic metrics: per-encoder per-seed per-phase recorded\n"
            "  META_RULE_K discriminator-fires: TD-vs-RD discriminator fires (sparse seed_7/19 has\n"
            "    1/8 RD win); BUT the encoder-family discriminator FAILS at 3/6 pair-degeneracy\n"
            "  META_RULE_L band: dom_rate 0.969-1.000 all above HP_DOM_LO; saturation at 1.000 for\n"
            "    seed_13 across all 4 encoders (cv across seeds nonzero for binary at recency=1.000\n"
            "    cap)\n"
            "  Fix #28 per-arm reads: per-encoder summary verified for all 4 encoders all 3 seeds\n"
            "  BIAS-13/14/15 contamination check: encoder hash collision is NOT a contamination\n"
            "    bug -- it's a genuine observational degeneracy at low N (the encoders themselves\n"
            "    differ in code but their phase-grid outputs at this regime coincide). Confirmed\n"
            "    by mechanism_hash equality across seeds (different RNG -> still same hash means\n"
            "    the encoder transform does not perturb the binarized phase outputs at this scale)\n"
            "\n"
            "_llm_forward_calls_at_inference = 0.\n"
            "substrate_only_decode_gate: PASS (no LLM in loop).\n"
            "\n"
            "PROMOTION PATH (if Director wants chain-grade for this dimension):\n"
            "  Required-regime-rewrite (cell v2):\n"
            "    - Increase N to 4096+ AND n_atoms to >=1000 to push the binary/HRR/FHRR phase\n"
            "      outputs out of byte-degeneracy\n"
            "    - Add a 5th encoder family that is constructed to differ (e.g. dense_uniform_real\n"
            "      with d_eff=256, or a 1024-dim quasi-orthogonal codebook)\n"
            "    - Add recency_decode_acc floor (>=0.70) to the chain-grade gate so sparse's\n"
            "      seed_13 by-construction Pareto win cannot pass\n"
            "    - Run at FULL (48 phase points minimum)\n"
            "    - Pre-reg includes EXPECTED_N_PAIRS_DIFFER>=5 as a discriminator (catches the\n"
            "      hash-collision regime via a HARD_FAIL_DEGENERATE_ENCODERS rule)\n"
        ),
        kind=AtomKind.EXPERIMENT_RECORD,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.MATH,
        algebra=None,
        metadata={
            "provenance_quality": "SMOKE_ONLY",
            "cert_status": "measured_mechanism",
            "cert_class": "regime_conditional_encoder_collapse",
            "cell_anchor": "substrate_anchor4_encoder_family_phase_diagram_v1",
            "cell_commit": CELL_COMMIT,
            "metrics_paths": [METRICS_SEED_7, METRICS_SEED_13, METRICS_SEED_19],
            "ruling_note": RULING_NOTE,
            "verified_off_data": True,
            "run_mode": "smoke",
            "n_seeds": 3,
            "seeds": [7, 13, 19],
            "N_DIM_sweep": [128, 1024],
            "R_BUCKETS": 64,
            "n_atoms": 200,
            "n_days": 365,
            "encoder_families": ["binary_bipolar", "hrr_real", "fhrr", "sparse_bipolar"],
            "phase_points_per_seed_MEASURED": 32,
            "phase_points_FULL_advertised": 48,
            "phase_points_smoke_advertised": 32,
            "dom_rate_seed_7_MEASURED": 0.9688,
            "dom_rate_seed_13_MEASURED": 1.0000,
            "dom_rate_seed_19_MEASURED": 0.9688,
            "n_pairs_differ_per_seed_MEASURED": 3,
            "n_pairs_total": 6,
            "binary_hrr_fhrr_phase_output_identical_per_seed": True,
            "sparse_bipolar_per_seed_chain_grade_pass_MEASURED": [False, True, False],
            "sparse_bipolar_recency_decode_acc_mean_MEASURED": {
                "seed_7": 0.4413, "seed_13": 0.4050, "seed_19": 0.4237,
            },
            "binary_hrr_fhrr_recency_decode_acc_mean_MEASURED": 1.0,
            "encoder_tiers_per_seed_MEASURED": {
                "seed_7":  {"binary_bipolar": "COMPETITIVE_ENCODER", "hrr_real": "COMPETITIVE_ENCODER",
                            "fhrr": "COMPETITIVE_ENCODER", "sparse_bipolar": "DOMINATED_ENCODER"},
                "seed_13": {"binary_bipolar": "COMPETITIVE_ENCODER", "hrr_real": "COMPETITIVE_ENCODER",
                            "fhrr": "COMPETITIVE_ENCODER", "sparse_bipolar": "COMPETITIVE_ENCODER"},
                "seed_19": {"binary_bipolar": "COMPETITIVE_ENCODER", "hrr_real": "COMPETITIVE_ENCODER",
                            "fhrr": "COMPETITIVE_ENCODER", "sparse_bipolar": "DOMINATED_ENCODER"},
            },
            "cardinality_ok_smoke": True,
            "cardinality_ok_full": False,
            "full_run_attempted": False,
            "encoder_provenance": "SUBSTRATE_NATIVE_BIPOLAR_PLUS_HRR_FHRR_SPARSE",
            "verdict_raw_per_seed": ["SMOKE_HARD_PASS", "SMOKE_HARD_PASS", "SMOKE_HARD_PASS"],
            "demote_reason": (
                "smoke_not_full_AND_encoder_family_invariance_hollow_n_pairs_differ_3_of_6_AND_sparse_"
                "bipolar_seed_13_pass_by_construction_uninformative_recency_at_chance_AND_prior_CG_"
                "T3_EXP_substrate_time_decay_eviction_phase_diagram_v2_Pareto_AUC_already_covers_TD_"
                "gt_RD_with_binary_encoder_70_phase_points"
            ),
            "supersedes_or_extends": (
                "T3/EXP_substrate_time_decay_eviction_phase_diagram_v2_Pareto_AUC_CROSS_SEED_AGG_3_of_3"
                "_chain_grade_phase_characterization_TD_dominates_RD_70_of_70_discriminating_regime_"
                "dom_rate_min_0p911_max_0p929_spread_0p018_rd_loss_rate_0_all_seeds_cell_HP_2026-06-28"
            ),
            "META_RULE_H_cardinality_ok_smoke": True,
            "META_RULE_AF_per_encoder_arms_differ": True,
            "META_RULE_AF_cross_encoder_arms_differ_FAIL": True,
            "META_RULE_AH_atomic_metrics": True,
            "META_RULE_K_TD_RD_discriminator_fires": True,
            "META_RULE_K_encoder_family_discriminator_fails_observation_degeneracy": True,
            "META_RULE_L_band_check": "dom_rate_in_HP_band_but_saturation_observed_seed_13",
            "BIAS_Q_saturation_guard": "triggered_seed_13_all_4_encoders_at_1p000",
            "load_bearing_finding_1": "sparse_bipolar_at_N128_n_atoms_200_6active_bits_recency_decode_chance_floor",
            "load_bearing_finding_2": "binary_HRR_FHRR_observationally_degenerate_at_this_regime_n_pairs_differ_3_of_6",
            "load_bearing_finding_3": "chain_grade_gate_pareto_only_lets_seed_13_sparse_pass_by_uninformative_both_arms_broken",
            "feeds_META_RULE_AP_chain_grade_gate_needs_recency_floor": True,
            "feeds_META_RULE_AO_sparse_bundle_lift_regime_conditional": True,
            "scope_observed": "smoke_3_seeds_N_DIM_sweep_128_1024_R_BUCKETS_64_n_atoms_200_4_encoder_families",
            "scope_not_claimed": (
                "FULL_48_phase_points_NOT_RUN_OR_chain_grade_encoder_family_invariance_OR_independent_3_encoder_witnesses"
            ),
            "promotion_path": (
                "cell_v2_at_N_4096_plus_n_atoms_gte_1000_plus_5th_encoder_quasi_orthogonal_codebook_plus_recency_floor_in_gate_plus_FULL_48_points_plus_EXPECTED_N_PAIRS_DIFFER_5_discriminator"
            ),
            "zero_llm_calls_at_inference": True,
            "_llm_forward_calls_at_inference": 0,
            "substrate_only_decode_gate": "PASS",
            "atomized_by": ATOMIZED_BY,
        },
    )


# ============================================================================
# ATOM 2 -- META_RULE_AO sparse_bipolar bundle lift is regime-conditional
# ============================================================================

def build_atom2_meta_rule_ao_sparse_regime() -> Atom:
    return Atom(
        id=(
            "RULE_sparse_bipolar_bundle_lift_is_regime_conditional_not_substrate_invariant_collapse_at_"
            "low_N_low_n_atoms_6_active_bits_recency_decode_chance_floor_META_RULE_AO_2026-06-29"
        ),
        name=(
            "META_RULE_AO: sparse_bipolar 20-300x bundle-lift claim (2026-06-23) is regime-conditional; "
            "at N=128 / n_atoms=200 / 6-active-bits / R_BUCKETS=64 sparse_bipolar recency_decode_acc "
            "drops to chance (~0.41 mean across 3 seeds). Cite the bundle-lift result only in the "
            "specific regime where it was measured; do NOT generalize to substrate-architecture invariance."
        ),
        description=(
            "META_RULE_AO: sparse_bipolar performance is regime-conditional.\n"
            "\n"
            "OBSERVED: sparse_bipolar at N=128 / n_atoms=200 / 6-active-bits / R_BUCKETS=64 produces\n"
            "recency_decode_acc_mean across 3 seeds:\n"
            "  seed_7 :  0.4413\n"
            "  seed_13:  0.4050\n"
            "  seed_19:  0.4237\n"
            "Mean across seeds: ~0.42 -- essentially chance for the retrieval task.\n"
            "\n"
            "PRIOR FINDING (2026-06-23 late session): 'sparse-bipolar 20-300x bundle lift'. That\n"
            "result was measured in a different regime (different N, different n_atoms, different\n"
            "task) and characterized BUNDLE composition lift specifically. It is NOT a claim that\n"
            "sparse_bipolar is a universally-better encoder, and the 2026-06-29 ANCHOR 4 phase\n"
            "diagram measurements show sparse_bipolar collapses to chance recency-decode at low-N\n"
            "/ low-n_atoms.\n"
            "\n"
            "DISCIPLINE: any future cell that uses sparse_bipolar OR references 'sparse_bipolar\n"
            "20-300x bundle lift' MUST:\n"
            "  (a) cite the specific regime (N, n_atoms, active-bit count, task type) where the\n"
            "      lift was measured; AND\n"
            "  (b) include a pre-reg target-regime check: if the new cell's regime differs in N\n"
            "      by >=4x or in n_atoms by >=4x or in active_bit_count, the cell's smoke MUST\n"
            "      include a sparse_bipolar baseline arm at the target regime to verify the\n"
            "      bundle-lift mechanism survives.\n"
            "\n"
            "FALSIFIES THE NAIVE READING: 'sparse_bipolar 20-300x bundle lift' is a property of\n"
            "the encoder family universally. Falsifies to: 'sparse_bipolar shows 20-300x bundle\n"
            "lift in the regime where it was measured (2026-06-23 cell); at low-N small-vocabulary\n"
            "regimes it instead collapses to chance recency-decode (ANCHOR 4 v1 2026-06-29).'\n"
            "\n"
            "RELATION TO OTHER META RULES:\n"
            "  Companion to META_RULE_AN (cone-collapse-formula-calibrated-at-N2048): both rules\n"
            "  encode the same discipline -- substrate measurements at one N do not naively\n"
            "  extrapolate to another N. AO is the encoder-readout layer; AN is the per-hop\n"
            "  accuracy-formula layer.\n"
            "  Companion to discipline-rule-R 'BIAS-15: regime-mismatch contamination check'\n"
            "  (USER 2026-06-24 master checklist): regime claims must be regime-bounded.\n"
            "\n"
            "VERIFIED-OFF-DATA EVIDENCE POINTERS:\n"
            "  data/exp_substrate_anchor4_encoder_family_phase_diagram_v1_seed_{7,13,19}_smoke/\n"
            "    metrics.json (3 files; per_encoder_summary.sparse_bipolar.recency_decode_acc_mean\n"
            "    in [0.4050, 0.4413])\n"
            "\n"
            "FIRST ATOMIZED 2026-06-29 by Skunkworks ANCHOR 4 landed-VET (.venv off-data recompute).\n"
        ),
        kind=AtomKind.METHODOLOGY_RULE,
        tier=Tier.TIER_METHODOLOGY,
        corpus=Corpus.META,
        algebra=None,
        metadata={
            "provenance_quality": "META_RULE",
            "cert_status": "discipline_meta",
            "cert_class": "discipline_meta",
            "rule_id": "META_RULE_AO",
            "rule_topic": "sparse_bipolar_bundle_lift_regime_conditional_not_substrate_invariant",
            "rule_layer": "encoder_regime_conditioning",
            "evidence_atoms": [
                "T3/EXP_substrate_anchor4_encoder_family_phase_diagram_v1_3seed_MEASURED_MECHANISM_smoke_seed_7_dom_0p9688_seed_13_dom_1p000_seed_19_dom_0p9688_binary_hrr_fhrr_observationally_degenerate_n_pairs_differ_3_of_6_sparse_bipolar_DOMINATED_at_low_N_regime_recency_acc_mean_0p41_chance_floor_cardinality_smoke_32_FULL_48_run_mode_smoke_not_full",
            ],
            "sparse_recency_decode_acc_at_low_N_MEASURED_seeds": [0.4413, 0.4050, 0.4237],
            "regime_at_collapse": "N_128_n_atoms_200_active_bits_6_R_BUCKETS_64_n_days_365",
            "prior_finding_referenced": "sparse_bipolar_20_300x_bundle_lift_2026-06-23",
            "companion_META_RULE_AN_cone_collapse_calibration": True,
            "companion_BIAS_15_regime_mismatch": True,
            "verified_off_data": True,
            "first_atomized_ts": "2026-06-29",
            "ruling_note": RULING_NOTE,
            "atomized_by": ATOMIZED_BY,
        },
    )


# ============================================================================
# ATOM 3 -- META_RULE_AP chain-grade Pareto gate needs recency-decode-acc floor
# ============================================================================

def build_atom3_meta_rule_ap_gate_recency_floor() -> Atom:
    return Atom(
        id=(
            "RULE_chain_grade_pareto_gate_needs_recency_decode_acc_floor_or_arms_can_pass_by_random_"
            "doing_worse_seed_13_sparse_bipolar_8of8_dom_at_recency_0p405_chance_floor_META_RULE_AP_"
            "2026-06-29"
        ),
        name=(
            "META_RULE_AP: a chain-grade gate based on Pareto-AUC (TD>RD) alone permits an arm to "
            "'pass' when BOTH the mechanism arm and the random arm have broken decoders (chance "
            "readout) and the mechanism happens to fail less. Pair every Pareto-AUC gate with a "
            "minimum-recency-decode-acc floor (recommended >=0.70) on the mechanism arm."
        ),
        description=(
            "META_RULE_AP: chain-grade gates using ARM_A > ARM_B Pareto-AUC require a recency_\n"
            "decode_acc floor on ARM_A; otherwise a regime where both ARM_A and ARM_B have chance-\n"
            "level decoders can produce 'PASS' (ARM_A wins because ARM_B fails more) without any\n"
            "real mechanism strength.\n"
            "\n"
            "WITNESSED IN: ANCHOR 4 encoder family phase diagram v1, seed_13, sparse_bipolar\n"
            "encoder. The cell's chain-grade gate (per_encoder_chain_grade_pass) requires:\n"
            "  dominance_rate >= HP_DOMINANCE_RATE_LO (0.85)\n"
            "  net_dominance >= HP_NET_DOMINANCE_LO  (0.70)\n"
            "  rd_loss_rate  <= HP_RD_LOSS_RATE_HI   (0.20)\n"
            "It does NOT include a recency_decode_acc floor. At seed_13 sparse_bipolar passes\n"
            "(8/8 td_wins; dom=1.000; net=1.000; rd_loss=0.000) WITH recency_decode_acc_mean=0.405\n"
            "(chance for 200 atoms with the test cue). RANDOM_EVICTION's recency is even lower so\n"
            "TIME_DECAY dominates; neither arm's readout is meaningful.\n"
            "\n"
            "AT seed_7 and seed_19 sparse_bipolar correctly FAILS the cell's chain-grade gate\n"
            "(td=7/8; dom=0.875) because one of the 8 phase points lets RANDOM beat TIME_DECAY at\n"
            "the chance floor. So the gate produces an inconsistent per-seed verdict for sparse\n"
            "(FAIL, PASS, FAIL) on essentially the same underlying chance-decode condition.\n"
            "\n"
            "REQUIRED FIX (load-bearing for all future Pareto-AUC chain-grade gates):\n"
            "  Gate condition for encoder_family fam:\n"
            "    s = per_encoder_summary[fam]\n"
            "    passes = (s.dominance_rate >= HP_DOM_LO\n"
            "             AND s.net_dominance >= HP_NET_LO\n"
            "             AND s.rd_loss_rate <= HP_RD_LOSS_HI\n"
            "             AND s.recency_decode_acc_mean >= HP_READOUT_FLOOR)   <- ADD THIS\n"
            "  Recommended HP_READOUT_FLOOR=0.70 for the time-decay-eviction class (where 200-atom\n"
            "  working-set retrieval is the readout); adjust per task. Without the floor, the\n"
            "  gate is correct only when both arms have working decoders.\n"
            "\n"
            "RELATION TO OTHER META RULES:\n"
            "  Strengthens META_RULE_K (discriminator-must-fire): K says the arms must differ;\n"
            "  AP says the discriminator must additionally reflect a meaningful readout, not a\n"
            "  chance-vs-chance comparison.\n"
            "  Companion to META_RULE_AF (arms-must-differ at hash level): AF catches identical\n"
            "  mechanism/random hashes; AP catches the subtler case where hashes differ but both\n"
            "  decoders are broken.\n"
            "  Companion to Fix #28 (verify per-arm metrics before framing): the per-arm metric\n"
            "  to check now includes recency_decode_acc_mean for any Pareto-AUC gated cell.\n"
            "\n"
            "VERIFIED-OFF-DATA EVIDENCE POINTERS:\n"
            "  data/exp_substrate_anchor4_encoder_family_phase_diagram_v1_seed_13_smoke/metrics.json\n"
            "    per_encoder_summary.sparse_bipolar -> {'td_wins': 8, 'dominance_rate': 1.0,\n"
            "    'recency_decode_acc_mean': 0.405}\n"
            "  Per-encoder chain-grade gate code:\n"
            "    experiments/_substrate_anchor4_encoder_family_phase_diagram_v1_core.py\n"
            "    lines 1001-1008 (the gate)\n"
            "\n"
            "FIRST ATOMIZED 2026-06-29 by Skunkworks ANCHOR 4 landed-VET (.venv off-data recompute).\n"
        ),
        kind=AtomKind.METHODOLOGY_RULE,
        tier=Tier.TIER_METHODOLOGY,
        corpus=Corpus.META,
        algebra=None,
        metadata={
            "provenance_quality": "META_RULE",
            "cert_status": "discipline_meta",
            "cert_class": "discipline_meta",
            "rule_id": "META_RULE_AP",
            "rule_topic": "chain_grade_pareto_gate_must_pair_with_recency_decode_acc_floor",
            "rule_layer": "chain_grade_gate_design",
            "evidence_atoms": [
                "T3/EXP_substrate_anchor4_encoder_family_phase_diagram_v1_3seed_MEASURED_MECHANISM_smoke_seed_7_dom_0p9688_seed_13_dom_1p000_seed_19_dom_0p9688_binary_hrr_fhrr_observationally_degenerate_n_pairs_differ_3_of_6_sparse_bipolar_DOMINATED_at_low_N_regime_recency_acc_mean_0p41_chance_floor_cardinality_smoke_32_FULL_48_run_mode_smoke_not_full",
            ],
            "recommended_readout_floor": 0.70,
            "witnessed_in_cell": "substrate_anchor4_encoder_family_phase_diagram_v1",
            "witnessed_seed": 13,
            "witnessed_encoder": "sparse_bipolar",
            "witnessed_dom_rate": 1.000,
            "witnessed_recency_decode_acc_mean": 0.405,
            "strengthens_META_RULE_K_discriminator_fires": True,
            "companion_META_RULE_AF_arms_must_differ_hash_level": True,
            "companion_Fix_28_per_arm_metrics_reads": True,
            "verified_off_data": True,
            "first_atomized_ts": "2026-06-29",
            "ruling_note": RULING_NOTE,
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
    print(f"[anchor4_encoder_vet] mode={mode}")

    store = PartitionedStore(STORE_ROOT)

    pre_cert_n = _cert_count(store)
    print(f"[anchor4_encoder_vet] PRE cert_n={pre_cert_n}")
    assert pre_cert_n == 632, f"PRE cert_n {pre_cert_n} != 632 expected"

    atoms = [
        build_atom1_anchor4_encoder_mm(),
        build_atom2_meta_rule_ao_sparse_regime(),
        build_atom3_meta_rule_ap_gate_recency_floor(),
    ]

    for i, a in enumerate(atoms, 1):
        print(f"[anchor4_encoder_vet] Atom {i}: id_head={str(a.id)[:80]}... corpus={a.corpus.name} tier={a.tier.name} kind={a.kind.name}")

    if not apply:
        print("[anchor4_encoder_vet] DRY mode -- no Store / ledger writes. Re-run with --apply.")
        return 0

    # ============================================================
    # APPLY: Atom adds + ledger rows (A5 PRE/POST window per write)
    # ============================================================
    expected_n = pre_cert_n  # delta=0 (all MM/meta)

    print("[anchor4_encoder_vet] Writing Atom 1 (ANCHOR 4 encoder-family 3-seed MM)...")
    store.add_atom(atoms[0])
    post_n_1 = _cert_count(store)
    assert post_n_1 == expected_n, f"After Atom 1: cert_n={post_n_1} != {expected_n}"
    append_cert_ledger_row(
        {
            "op": "cert_ruling",
            "atom_id": f"math::{atoms[0].id}",
            "cert_status": "measured_mechanism",
            "cert_class": "regime_conditional_encoder_collapse",
            "verified_off_data": True,
            "atomized_by": ATOMIZED_BY,
            "cell_commit": CELL_COMMIT,
            "verdict": "SMOKE_HARD_PASS_DEMOTE_TO_MM_BY_CONSTRUCTION_DEGENERACY",
            "cert_increment_delta": 0,
            "cv": None,
            "referent_pointer": {
                "notes_path": RULING_NOTE,
                "metrics_path": METRICS_SEED_7,
                "atom_qualified_id": f"math::{atoms[0].id}",
            },
            "supersedes": None,
            "note": "anchor4_encoder_family_v1_3seed_MM_smoke_not_full_AND_binary_HRR_FHRR_byte_identical_n_pairs_differ_3_of_6_AND_sparse_seed_13_pass_uninformative_recency_0p405_chance_AND_prior_CG_eviction_v2_Pareto_AUC_already_covers_TD_gt_RD_70pts",
        },
        expected_cert_n_pre=pre_cert_n,
        expected_cert_n_post=expected_n,
    )

    print("[anchor4_encoder_vet] Writing Atom 2 (META_RULE_AO sparse-regime-conditional)...")
    store.add_atom(atoms[1])
    post_n_2 = _cert_count(store)
    assert post_n_2 == expected_n, f"After Atom 2: cert_n={post_n_2} != {expected_n}"
    append_cert_ledger_row(
        {
            "op": "cert_ruling",
            "atom_id": f"meta::{atoms[1].id}",
            "cert_status": "discipline_meta",
            "cert_class": "discipline_meta",
            "verified_off_data": True,
            "atomized_by": ATOMIZED_BY,
            "cell_commit": CELL_COMMIT,
            "verdict": "META_RULE_NEUTRAL",
            "cert_increment_delta": 0,
            "cv": None,
            "referent_pointer": {
                "notes_path": RULING_NOTE,
                "metrics_path": "n/a-meta-rule-derived-from-anchor4-Atom1",
                "atom_qualified_id": f"meta::{atoms[1].id}",
            },
            "supersedes": None,
            "note": "anchor4_META_RULE_AO_sparse_bipolar_bundle_lift_is_regime_conditional_collapse_at_N128_n_atoms_200_6active_bits_recency_chance_0p41_cite_with_regime_bounds",
        },
        expected_cert_n_pre=pre_cert_n,
        expected_cert_n_post=expected_n,
    )

    print("[anchor4_encoder_vet] Writing Atom 3 (META_RULE_AP gate-needs-recency-floor)...")
    store.add_atom(atoms[2])
    post_n_3 = _cert_count(store)
    assert post_n_3 == expected_n, f"After Atom 3: cert_n={post_n_3} != {expected_n}"
    append_cert_ledger_row(
        {
            "op": "cert_ruling",
            "atom_id": f"meta::{atoms[2].id}",
            "cert_status": "discipline_meta",
            "cert_class": "discipline_meta",
            "verified_off_data": True,
            "atomized_by": ATOMIZED_BY,
            "cell_commit": CELL_COMMIT,
            "verdict": "META_RULE_NEUTRAL",
            "cert_increment_delta": 0,
            "cv": None,
            "referent_pointer": {
                "notes_path": RULING_NOTE,
                "metrics_path": "n/a-meta-rule-derived-from-anchor4-Atom1-gate-code-inspection",
                "atom_qualified_id": f"meta::{atoms[2].id}",
            },
            "supersedes": None,
            "note": "anchor4_META_RULE_AP_pareto_AUC_chain_grade_gate_must_pair_with_recency_decode_acc_floor_else_both_arms_chance_decoders_can_PASS_witnessed_seed_13_sparse_8of8_at_recency_0p405",
        },
        expected_cert_n_pre=pre_cert_n,
        expected_cert_n_post=expected_n,
    )

    final_cert_n = _cert_count(store)
    print(f"[anchor4_encoder_vet] FINAL cert_n={final_cert_n} (pre={pre_cert_n}, delta=0; 1 MM + 2 META)")
    assert final_cert_n == expected_n

    # Round-trip verify: each atom should reload
    store_verify = PartitionedStore(STORE_ROOT)
    for a in atoms:
        match = [x for x in store_verify.all_atoms() if x.id == a.id]
        assert len(match) == 1, f"Round-trip FAIL for atom id={a.id} (found {len(match)})"
        assert (match[0].metadata or {}).get("atomized_by") == ATOMIZED_BY
        print(f"[anchor4_encoder_vet] Round-trip OK: {a.id[:60]}...")

    print("[anchor4_encoder_vet] APPLY OK -- 3 atoms landed; ledger 3 rows appended; cert_n unchanged at 632.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
