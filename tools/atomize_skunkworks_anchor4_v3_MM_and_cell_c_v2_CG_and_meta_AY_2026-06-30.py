"""Atomize: Skunkworks landed-VET 2026-06-30 evening batch.

Three atoms in this batch:
  Atom 1 (MM, delta=0) -- ANCHOR 4 encoder family v3 3-seed MM_PARTIAL_DISCRIMINATION
    (math corpus): dense triplet binary_bipolar/hrr_real/fhrr collapses to
    bit-identical mechanism_hash + bit-identical per-cell metrics; sparse_bipolar
    + sparse_real wired distinctly. 6th phantom-FULL recurrence PARTIAL fix.
  Atom 2 (CG, delta=+1) -- Cell C v2 compartmentalized cortex K-banks 3-seed
    (math corpus): per-K (1, 20, 50, 100, 200) Hopfield bank routing through
    hippo write path; K=200 reaches 0.933 +/- 0.005 vs DIRECT_UPPER 0.986 with
    Delta=0.053. Retains hippo replay (sparse_dg + sign-thresholded reactivation
    + P_hc projection); 18/18 arm_hashes distinct; monotonic K=1->K=200; not
    by-construction identity to DIRECT.
  Atom 3 (META, delta=0) -- META_RULE_AY (meta corpus): verdict-emitter must
    auto-HARD_FAIL if any cell self-reported distinctness field (e.g.
    encoder_pair_distinctness, arm_pair_distinctness) contains False; cell-author
    HARD_PASS framings must be auto-demoted. Complementary automation discipline
    to META_RULE_AX (phantom-FULL detection).

OFF-DATA RECOMPUTE (Skunkworks 2026-06-30 evening, .venv Python):
  ANCHOR 4 v3 (3 seeds; metrics.fresh_2026-06-30.json SCP-pulled fresh because
    standard sync at 18:17 UTC was 2-3min stale before landings at 18:19-18:20 UTC):
      seed_7  (mtime 18:19 UTC): verdict HARD_PASS, 90/90 pts, dom=1.000,
        pairs_differ=7/10, 5/5 chain_grade
      seed_13 (mtime 18:20 UTC): verdict HARD_PASS, 90/90 pts, dom=0.994,
        pairs_differ=7/10, 5/5 chain_grade
      seed_19 (mtime 18:20 UTC): verdict HARD_PASS, 90/90 pts, dom=0.989,
        pairs_differ=7/10, 4/5 chain_grade (sparse_bipolar DOMINATED at
        dominance_rate=0.944, recency=0.913)
    Per-encoder mechanism_hash (smoking gun):
      seed_7:  binary_bipolar = hrr_real = fhrr = 3c44d9d32aab8309   <-- COLLIDE
               sparse_bipolar = a99fd28b17d3dfa8 (distinct)
               sparse_real    = caa0d961fa08b180 (distinct)
      seed_13: binary_bipolar = hrr_real = fhrr = 5257c7f0e423ed19   <-- COLLIDE
               sparse_bipolar = 2c6d35e23fa976f0 (distinct)
               sparse_real    = ce2eb7d084002f56 (distinct)
      seed_19: binary_bipolar = hrr_real = fhrr = 748ddb192e9fde92   <-- COLLIDE
               sparse_bipolar = 736cc49ee0260847 (distinct)
               sparse_real    = 2aedd30982fb14d6 (distinct)
    Cell self-reports encoder_pair_distinctness (all 3 seeds):
      binary_bipolar_vs_hrr_real: False
      binary_bipolar_vs_fhrr:     False
      hrr_real_vs_fhrr:           False
      (5 sparse-pair entries: True)
    Per-cell phase_map confirms bit-identical metrics across dense triplet:
      seed_7 cell_0 ws_ret_TD = 1.000000 for binary / hrr / fhrr; recency=1.0
      seed_7 cell_5 (load=5.0 N=8192) all 5 encoders saturate to ws_TD=1.000000
        (META_RULE_Q suspect 1.000 tripped at high-capacity regime)
      sparse_bipolar at seed_7 cell_0: ws_TD=0.713502 (distinct)
      sparse_real    at seed_7 cell_0: ws_TD=0.922064 (distinct)
    cardinality_ok=True, run_mode=full, elapsed_s in [3.20, 4.34], backend=
    torch.cuda:RTX_4060_Ti per seed. expected_n=observed_n=90.

  Cell C v2 (3 seeds; metrics.fresh_2026-06-30.json SCP-pulled by Orchestrator
    a3bafe51 because preserve-existing blocked standard sync):
      seed_7  ARM_STANDARD_K1=0.213 K20=0.629 K50=0.818 K100=0.897 K200=0.926 DIRECT=0.985
      seed_13 ARM_STANDARD_K1=0.221 K20=0.640 K50=0.832 K100=0.902 K200=0.939 DIRECT=0.987
      seed_19 ARM_STANDARD_K1=0.250 K20=0.663 K50=0.831 K100=0.897 K200=0.935 DIRECT=0.985
    All 18 arm_hashes distinct (per-arm sha256-hash of cortex weights slice):
      seed_7:  K1=85439580b07cb64b K20=c3c6091a2f906067 K50=35d55a859720f6c8
               K100=63c8d3c431736fd3 K200=93b1b43494f1fa2e DIRECT=4d12ed10de254890
      seed_13: K1=53030b331fe59060 K20=94151d5e2e821302 K50=f355110ab675a920
               K100=5148693480100f94 K200=e3929d8d91ec7699 DIRECT=0cc6b17cfc480dcd
      seed_19: K1=795d9dcfd69b3d20 K20=7e546fe253ec08cb K50=d35e792b0ffb35bf
               K100=a4add5b3d57f793f K200=ad5d4c00e69d22c6 DIRECT=6196c100019322ac
    bank_sizes scale realistically: K1=2048/2048; K20=102/103; K50=40/41;
      K100=20/21; K200=10/11; DIRECT=-1/-1 (not banked).
    cortex_norm scales 0.72 -> 3.26 monotonically with K (real per-bank Hebbian
      magnitude growth); DIRECT cortex_norm=0.227 (distinct mechanism: l2-norm
      single full assoc matrix vs per-bank sign-thresholded reactivation outer
      products). K=200 cortex_norm=3.26 vs DIRECT=0.23 = factor 14x different
      mechanism magnitude.
    Hippo write-path retention (read cell code lines 207-323 + 343-398):
      COMPARTMENT arm pipeline:
        keys_h = _sparse_dg(keys_raw, P_in, k_active)        # sparse DG
        vals_h = _sparse_dg(vals_raw, P_in, k_active)        # sparse DG
        W_h = vals_h.t() @ keys_h                            # hippo assoc memory
        vals_react_h = sign(cues_h @ W_h.t())                # hippo replay
        vals_c_react = l2norm(vals_react_h @ P_hc.t())       # cortex projection
        bank_assign = original_idx % K_banks                 # per-bank routing
        W_banks[k] = ETA * (v_k.t() @ c_k)                   # per-bank Hebbian
      DIRECT arm pipeline:
        keys_h = _sparse_dg(keys_raw, P_in, k_active)        # same DG
        vals_c = l2norm(vals_h @ P_hc.t())                   # direct cortex
        W_c = ETA * (vals_c.t() @ keys_c)                    # single Hopfield
        (no replay, no sign-threshold, no per-bank routing)
      COMPARTMENT RETAINS hippo write path (sparse_dg + W_h hippo memory + sign-
      thresholded replay + bank routing); DIRECT bypasses replay. Not by-
      construction identity. Mechanisms genuinely distinct.
    Cross-seed cv (recall_cortex stddev/mean):
      K1: 0.228 +/- 0.016 -> cv=0.07
      K20: 0.644 +/- 0.014 -> cv=0.02
      K50: 0.827 +/- 0.006 -> cv=0.007
      K100: 0.899 +/- 0.002 -> cv=0.002
      K200: 0.933 +/- 0.005 -> cv=0.005 (cv_best=0.006 per cell-author)
      DIRECT: 0.986 +/- 0.001 -> cv=0.001
    META_RULE_AX arm-distinctness: PASS (6 distinct arm_hashes per seed x 3 seeds
      = 18 distinct hashes).
    META_RULE_AW seed-config-identical: PASS (all 3 seeds use M=2048, N_h=8192,
      N_c=2048, alpha_simple=0.250, K_BANK=(1,20,50,100,200)).
    META_RULE_AU + AV: cardinality_ok=True per seed (cell aggregates 6 arms x 3
      seeds = 18 expected; n=3 per seed), run_mode=full, elapsed=6.99s aggregate
      (2.57 + 2.30 + 2.11 per seed; above pre-flight 1s floor).
    META_RULE_Q (suspect 1.000): NOT tripped. K=200 max = 0.939 (seed_13); not
      at 1.000. DIRECT max = 0.987; not at 1.000. No phase-cell saturation.

CERT-TIER DECISIONS:
  Atom 1 (ANCHOR 4 v3): MEASURED_MECHANISM (NOT chain-grade); delta=0.
    Rationale:
      - 2/5 encoder distinctness: sparse family wired, dense triplet phantom.
      - cell self-reports encoder_pair_distinctness=False for 3 dense pairs.
      - per-cell metrics bit-identical across dense triplet (ws_ret_TD, recency
        decode to 6 decimal places at seed_7 cell_0).
      - META_RULE_Q triggered at high-capacity regime (13/18 cells saturate to
        1.000 in dense triplet).
      - Proven bound: sparse encoders (sparse_bipolar, sparse_real) DO produce
        distinct phase profiles from each other and from the dense triplet under
        low-capacity regime (N=1024 load=1.0). Dense triplet (binary_bipolar/
        hrr_real/fhrr) does NOT differentiate under current substrate path.
  Atom 2 (Cell C v2): CHAIN_GRADE_PHASE_CHARACTERIZATION; delta=+1 (633 -> 634).
    Rationale:
      - 5-point K-bank sweep + DIRECT oracle; 18/18 arm_hashes distinct.
      - Monotonic K=1->K=200 (0.228 -> 0.933) within each seed.
      - cv_best=0.006 across 3 seeds (well below cv<=0.10 threshold).
      - K=200 NOT by-construction identity to DIRECT (Delta=0.053 sustained;
        cortex_norm 14x different; pipeline distinct: replay vs no-replay).
      - Retains hippo write path (sparse_dg + W_h + sign-thresholded replay).
      - Cell C v1 ARM_CLEAN_VALS_TO_CORTEX bit-identity trap (closeFrac=1.000)
        NOT reproduced.
      - HP floor +0.50 lift cleared at +0.705 best lift.
      - META_RULE_Q NOT triggered (no 1.000 saturation).
      - cardinality_ok, run_mode=full, elapsed clean.
      - Stage 2 NREM Hc-rescue via cortex compartmentalization mechanism
        empirically established at chain-grade scale.
  Atom 3 (META_RULE_AY): METHODOLOGY_RULE (META corpus); delta=0.
    Rationale:
      - ANCHOR 4 v3 cell SELF-REPORTS encoder_pair_distinctness=False for 3
        dense pairs YET STILL EMITS HARD_PASS verdict. The verdict-emitter
        logic is over-permissive: it does not auto-demote on cell-author's own
        distinctness diagnostic.
      - Rule: any verdict-emitter that publishes HARD_PASS while a cell's own
        self-reported distinctness diagnostic (encoder_pair_distinctness,
        arm_pair_distinctness, mechanism_hash_distinctness, etc.) contains False
        MUST auto-demote to MEASURED_MECHANISM or HARD_FAIL_PARTIAL_DISCRIM.
      - Companion automation to META_RULE_AX (phantom-FULL detection at landed-
        VET); AY closes the loop AT THE CELL-AUTHOR LAYER so phantom-FULL is
        caught BEFORE landing.

PRE CERT N (verified live): 633
POST CERT N (predicted): 634 (Atom 2 chain_grade +1; Atoms 1+3 delta=0)

A5 GATING: PRE/POST cert_n assertions on every Store add; round-trip reload
  verify on each atom.

Run:
  cd d:/AI/hd-instrument
  .venv/Scripts/python.exe tools/atomize_skunkworks_anchor4_v3_MM_and_cell_c_v2_CG_and_meta_AY_2026-06-30.py         # DRY
  .venv/Scripts/python.exe tools/atomize_skunkworks_anchor4_v3_MM_and_cell_c_v2_CG_and_meta_AY_2026-06-30.py --apply  # WRITE
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(".").resolve()))
from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier
from tools.cert_ledger_writer import append_cert_ledger_row

STORE_ROOT = Path("data/substrate_index")
RULING_NOTE = "in-conversation skunkworks landed-VET 2026-06-30 evening (anchor4 v3 + cell C v2)"
ATOMIZED_BY = "skunkworks_atomize_anchor4_v3_MM_cellC_v2_CG_metaAY_2026-06-30"

METRICS_A4_V3_SEED_7  = "data/exp_substrate_anchor4_encoder_family_phase_diagram_v3_seed_7/metrics.fresh_2026-06-30.json"
METRICS_A4_V3_SEED_13 = "data/exp_substrate_anchor4_encoder_family_phase_diagram_v3_seed_13/metrics.fresh_2026-06-30.json"
METRICS_A4_V3_SEED_19 = "data/exp_substrate_anchor4_encoder_family_phase_diagram_v3_seed_19/metrics.fresh_2026-06-30.json"

METRICS_CELLC_V2 = "data/exp_substrate_compartmentalized_cortex_K_banks_v2_GPU/metrics.fresh_2026-06-30.json"


# ============================================================================
# ATOM 1 -- ANCHOR 4 v3 3-seed MM_PARTIAL_DISCRIMINATION (dense triplet phantom)
# ============================================================================

def build_atom1_anchor4_v3_mm_partial() -> Atom:
    return Atom(
        id=(
            "T3/EXP_substrate_anchor4_encoder_family_phase_diagram_v3_3seed_MM_PARTIAL_DISCRIMINATION_"
            "dense_triplet_binary_bipolar_eq_hrr_real_eq_fhrr_phantom_sparse_bipolar_sparse_real_distinct_"
            "encoder_pair_distinctness_3_of_10_False_per_cell_ws_ret_TD_bit_identical_dense_seed_7_13_19_"
            "metarule_q_suspect_1p000_at_high_capacity_2_of_5_encoders_wired_6th_phantom_FULL_partial_2026-06-30"
        ),
        name=(
            "substrate_anchor4_encoder_family_phase_diagram_v3 3-seed MM_PARTIAL_DISCRIMINATION: "
            "sparse encoder family (sparse_bipolar, sparse_real) produces distinct mechanism_hash and "
            "distinct per-cell metrics; dense triplet (binary_bipolar, hrr_real, fhrr) collapses to "
            "bit-identical mechanism_hash and bit-identical per-cell working_set_retention + recency "
            "decode at 6 decimal places (encoder axis only 2/5 wired). 6th phantom-FULL recurrence "
            "PARTIAL fix; META_RULE_AX not fully satisfied."
        ),
        description=(
            "MEASURED_MECHANISM landed-VET of cell substrate_anchor4_encoder_family_phase_diagram_v3\n"
            "over 3 seeds (7, 13, 19) on RTX 4060 Ti backend.\n"
            "\n"
            "OFF-DATA RECOMPUTE (Skunkworks 2026-06-30 evening, .venv Python; SCP-pulled fresh\n"
            "because standard sync ran 18:17 UTC while landings happened 18:19-18:20 UTC):\n"
            "\n"
            "  Per-seed surface verdicts (cell-author):\n"
            "    seed_7  HARD_PASS 90/90 dom=1.000 pairs_differ=7/10 5/5 chain_grade elapsed=3.23s\n"
            "    seed_13 HARD_PASS 90/90 dom=0.994 pairs_differ=7/10 5/5 chain_grade elapsed=4.34s\n"
            "    seed_19 HARD_PASS 90/90 dom=0.989 pairs_differ=7/10 4/5 chain_grade elapsed=3.20s\n"
            "             (sparse_bipolar DOMINATED at dominance_rate=0.944, rd_loss_rate=0.056,\n"
            "              recency=0.913)\n"
            "  Surface compliance: cardinality_ok=True, run_mode=full, expected_n=observed_n=90,\n"
            "    backend=torch.cuda:RTX_4060_Ti, K_RBUCKETS=128, N_DIM_sweep=[1024,4096,8192].\n"
            "\n"
            "META_RULE_AX VIOLATION (load-bearing; phantom-FULL 6th recurrence PARTIAL):\n"
            "  Per-encoder mechanism_hash (independently extracted from arms_differ_per_encoder):\n"
            "    seed_7:  binary_bipolar = hrr_real = fhrr = 3c44d9d32aab8309   COLLIDE\n"
            "             sparse_bipolar = a99fd28b17d3dfa8\n"
            "             sparse_real    = caa0d961fa08b180\n"
            "    seed_13: binary_bipolar = hrr_real = fhrr = 5257c7f0e423ed19   COLLIDE\n"
            "             sparse_bipolar = 2c6d35e23fa976f0\n"
            "             sparse_real    = ce2eb7d084002f56\n"
            "    seed_19: binary_bipolar = hrr_real = fhrr = 748ddb192e9fde92   COLLIDE\n"
            "             sparse_bipolar = 736cc49ee0260847\n"
            "             sparse_real    = 2aedd30982fb14d6\n"
            "  Cell self-reports encoder_pair_distinctness (all 3 seeds, 3/10 False):\n"
            "    binary_bipolar_vs_hrr_real: False\n"
            "    binary_bipolar_vs_fhrr:     False\n"
            "    hrr_real_vs_fhrr:           False\n"
            "    (other 7 pairs: True; all sparse-vs-anything pairs distinct)\n"
            "  Per-cell phase_map confirms bit-identical metrics across dense triplet:\n"
            "    seed_7 cell_0 (decay=30, load=1.0, N_dim=1024):\n"
            "      binary_bipolar ws_TD=1.000000 ws_RND=0.635565 recency=1.000000\n"
            "      hrr_real       ws_TD=1.000000 ws_RND=0.635565 recency=1.000000   (identical)\n"
            "      fhrr           ws_TD=1.000000 ws_RND=0.635565 recency=1.000000   (identical)\n"
            "      sparse_bipolar ws_TD=0.713502 ws_RND=0.455543 recency=0.714700   (distinct)\n"
            "      sparse_real    ws_TD=0.922064 ws_RND=0.585071 recency=0.918000   (distinct)\n"
            "    seed_7 cell_5 (decay=30 load=5.0 N_dim=8192): all 5 encoders saturate to\n"
            "      ws_TD=1.000000 ws_RND=0.445455 recency=1.000000 (META_RULE_Q tripped).\n"
            "  fhrr labels dim_eff=512 + dtype=complex64 correctly (cosmetic config) but the\n"
            "    underlying metric is bit-identical to binary_bipolar dim_eff=1024 float32 --\n"
            "    encoder topology does NOT flow into the eviction / decay / readout mechanism\n"
            "    for the dense triplet. Only the sparse encoders' top-k thresholded outputs\n"
            "    actually differentiate downstream.\n"
            "\n"
            "META_RULE_Q (suspect 1.000) tripped at high-capacity regime:\n"
            "  seed_7 phase grid: ~13 of 18 cells in the dense triplet saturate to recency=1.000000\n"
            "    and ws_TD=1.000000 (load=5.0 cells at N>=8192; load=1.0 cells at N>=4096).\n"
            "  Sparse encoders only show distinct metrics at the lowest-capacity cells (load=1.0\n"
            "    N=1024). Even there, sparse_bipolar drops below the HP_RECENCY_DECODE_FLOOR=0.30\n"
            "    in some configurations; this is what tipped seed_19 to 4/5 chain_grade.\n"
            "\n"
            "WHY MM (NOT CHAIN-GRADE):\n"
            "  - Encoder axis only 2/5 wired (sparse_bipolar, sparse_real distinct; dense triplet\n"
            "    collapses).\n"
            "  - Cell-author's HARD_PASS framing is over-permissive: the cell SELF-REPORTS three\n"
            "    pair-distinctness violations (binary=hrr=fhrr) yet the verdict logic emits\n"
            "    HARD_PASS anyway. The verdict-emitter must auto-HARD_FAIL on self-reported\n"
            "    distinctness violations (see Atom 3 META_RULE_AY).\n"
            "  - This is the 6th phantom-FULL recurrence: v1 (June) phantom; v1 rerun (2026-06-29)\n"
            "    all-5-bit-identical phantom; v3 (2026-06-30) dense-leg phantom. Trajectory: from\n"
            "    0/5 distinct -> 2/5 distinct, partial fix on the cell-author's binding wiring.\n"
            "  - META_RULE_Q (suspect 1.000) tripped: high-capacity regime saturates all 5\n"
            "    encoders to ws_TD=1.000000 (load=5.0 cells); this masks encoder differences\n"
            "    that might exist at lower capacity. Discriminator does not fire at higher N.\n"
            "\n"
            "PROVEN BOUND (MM characterization):\n"
            "  - sparse_bipolar and sparse_real produce distinct mechanism_hashes and distinct\n"
            "    per-cell working_set_retention / recency / Pareto-AUC profiles from each other\n"
            "    AND from the dense triplet.\n"
            "  - The 2/5 distinct encoders prove that the cell HARNESS can carry encoder identity\n"
            "    end-to-end; the cell-author's binding-mechanism layer for dense encoders\n"
            "    (binary_bipolar/hrr_real/fhrr) collapses them to a single computational path.\n"
            "\n"
            "REQUIRED FIX FOR v4 PROMOTION:\n"
            "  1. Dense binding op must actually invoke encoder-specific code paths: HRR circular\n"
            "     conv (FFT), FHRR complex element-wise mult, binary_bipolar XOR/sign -- currently\n"
            "     all 3 appear to share one path.\n"
            "  2. Add config-level smoke check: assert mechanism_hash distinct across ALL 10\n"
            "     encoder pairs before publishing FULL.\n"
            "  3. Verdict logic must HARD_FAIL if encoder_pair_distinctness contains any False\n"
            "     (currently cell self-reports False and still emits HARD_PASS).\n"
            "  4. Add lower-capacity regime sweep (load=0.5 + N=512) to avoid META_RULE_Q\n"
            "     saturation masking encoder differences.\n"
            "\n"
            "REFERENT CHECK (META_RULE_BIAS_N):\n"
            "  spawn-prompt cited: seed_7 90/90 pts pairs_differ=7/10 chain_grade=5/5;\n"
            "    seed_13 90/90 chain_grade=5/5; seed_19 90/90 chain_grade=4/5.\n"
            "  On disk verified: matches exactly. Spawn-prompt verdict cite correct.\n"
            "  But spawn-prompt framing 'HARD_PASS chain-grade promotion candidate' is at odds\n"
            "  with the cell's own encoder_pair_distinctness diagnostic which already flags 3\n"
            "  pairs False. Verdict-emitter over-permissiveness is the actual chain-grade\n"
            "  blocker, not a data discrepancy.\n"
            "\n"
            "_llm_forward_calls_at_inference = 0.\n"
        ),
        kind=AtomKind.EXPERIMENT_RECORD,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.MATH,
        algebra=None,
        metadata={
            "provenance_quality": "MEASURED_MECHANISM",
            "cert_status": "measured_mechanism",
            "cert_class": "mechanism_characterization",
            "cell_anchor": "substrate_anchor4_encoder_family_phase_diagram_v3",
            "metrics_paths": [METRICS_A4_V3_SEED_7, METRICS_A4_V3_SEED_13, METRICS_A4_V3_SEED_19],
            "ruling_note": RULING_NOTE,
            "verified_off_data": True,
            "run_mode": "full",
            "n_seeds": 3,
            "seeds_attempted": [7, 13, 19],
            "expected_n_per_seed": 90,
            "observed_n_per_seed": 90,
            "cardinality_ok_all_seeds": True,
            "backend": "torch.cuda:NVIDIA_GeForce_RTX_4060_Ti",
            "N_DIM_sweep": [1024, 4096, 8192],
            "R_BUCKETS": 128,
            "encoders_attempted": [
                "binary_bipolar", "hrr_real", "fhrr", "sparse_bipolar", "sparse_real",
            ],
            "encoders_distinct_mechanism_hash": ["sparse_bipolar", "sparse_real"],
            "encoders_collide_dense_triplet": ["binary_bipolar", "hrr_real", "fhrr"],
            "per_seed_mechanism_hash_dense_collision": {
                "seed_7": "3c44d9d32aab8309",
                "seed_13": "5257c7f0e423ed19",
                "seed_19": "748ddb192e9fde92",
            },
            "per_seed_mechanism_hash_sparse_bipolar": {
                "seed_7": "a99fd28b17d3dfa8",
                "seed_13": "2c6d35e23fa976f0",
                "seed_19": "736cc49ee0260847",
            },
            "per_seed_mechanism_hash_sparse_real": {
                "seed_7": "caa0d961fa08b180",
                "seed_13": "ce2eb7d084002f56",
                "seed_19": "2aedd30982fb14d6",
            },
            "encoder_pair_distinctness_False_pairs": [
                "binary_bipolar_vs_hrr_real",
                "binary_bipolar_vs_fhrr",
                "hrr_real_vs_fhrr",
            ],
            "encoder_pair_distinctness_True_pairs": [
                "binary_bipolar_vs_sparse_bipolar", "binary_bipolar_vs_sparse_real",
                "hrr_real_vs_sparse_bipolar", "hrr_real_vs_sparse_real",
                "fhrr_vs_sparse_bipolar", "fhrr_vs_sparse_real",
                "sparse_bipolar_vs_sparse_real",
            ],
            "encoder_axis_partial_wired_fraction": "2_of_5",
            "encoder_pair_distinctness_failing_count": 3,
            "per_seed_chain_grade_count": {"seed_7": 5, "seed_13": 5, "seed_19": 4},
            "seed_19_DOMINATED_encoder": "sparse_bipolar",
            "seed_19_DOMINATED_dominance_rate": 0.9444,
            "seed_19_DOMINATED_rd_loss_rate": 0.0556,
            "META_RULE_AX_phantom_full_recurrence_partial": True,
            "META_RULE_AX_phantom_full_recurrence_count_running": 6,
            "META_RULE_Q_suspect_1p000_tripped": True,
            "META_RULE_Q_saturation_regime": "load>=5.0_OR_N_DIM>=4096_dense_triplet_recency_eq_1p000",
            "verdict_emitter_over_permissive_self_reported_distinctness_False_but_HARD_PASS": True,
            "load_bearing_finding_1": "dense_triplet_binary_hrr_fhrr_collapse_to_one_path_bit_identical_metrics",
            "load_bearing_finding_2": "sparse_bipolar_sparse_real_genuinely_distinct_mechanism_hash_and_metrics",
            "load_bearing_finding_3": "verdict_emitter_does_not_auto_demote_on_self_reported_pair_distinctness_False",
            "required_fix_v4_dense_binding_invoke_encoder_specific_code_paths_FFT_complex_XOR": True,
            "required_fix_v4_smoke_assert_all_10_pairs_distinct_before_FULL": True,
            "required_fix_v4_verdict_logic_HARD_FAIL_on_any_pair_distinctness_False": True,
            "required_fix_v4_add_lower_capacity_regime_to_avoid_META_RULE_Q_masking": True,
            "feeds_META_RULE_AY_verdict_emitter_auto_demote_on_self_reported_distinctness_False": True,
            "phantom_full_history": [
                "v1_2026_June_raw_float_encoder_collision_only_seed_7_actual_full",
                "v1_rerun_2026-06-29_encoder_slots_cosmetic_working_set_retention_bit_identical_5_of_5",
                "v3_2026-06-30_dense_triplet_collapse_3_of_5_distinct_partial_fix",
            ],
            "extends_or_supersedes_prior": (
                "supersedes_v1_rerun_phantom_full_with_partial_2_of_5_wiring_fix_extends_phantom_full_history"
            ),
            "promotion_path_future": (
                "v4_fix_dense_binding_path_separation_HRR_FFT_FHRR_complex_binary_XOR_then_revalidate_landed_VET"
            ),
            "scope_observed": (
                "3_seeds_5_encoders_phase_grid_18_cells_per_encoder_N_DIM_1024_4096_8192_R_BUCKETS_128_"
                "decay_30_90_180_load_1p0_5p0_n_atoms_1500_n_days_365"
            ),
            "scope_not_claimed": (
                "5_of_5_encoder_distinctness_OR_chain_grade_phase_characterization_OR_dense_encoder_"
                "specific_binding_correctness_OR_low_capacity_regime_below_load_1p0"
            ),
            "zero_llm_calls_at_inference": True,
            "_llm_forward_calls_at_inference": 0,
            "atomized_by": ATOMIZED_BY,
        },
    )


# ============================================================================
# ATOM 2 -- Cell C v2 compartmentalized cortex K-banks 3-seed CHAIN_GRADE
# ============================================================================

def build_atom2_cell_c_v2_chain_grade() -> Atom:
    return Atom(
        id=(
            "T3/EXP_substrate_compartmentalized_cortex_K_banks_v2_GPU_3seed_CHAIN_GRADE_PHASE_CHARACTERIZATION_"
            "K1_0p228_K20_0p644_K50_0p827_K100_0p899_K200_0p933_DIRECT_0p986_best_lift_0p705_cv_0p006_"
            "monotonic_18of18_arm_hashes_distinct_retains_hippo_write_path_not_by_construction_identity_DIRECT_"
            "stage2_NREM_Hc_rescue_cortex_compartmentalization_2026-06-30"
        ),
        name=(
            "substrate_compartmentalized_cortex_K_banks_v2_GPU 3-seed CHAIN_GRADE_PHASE_CHARACTERIZATION: "
            "K-bank Hopfield routing through hippo replay path yields monotonic recall lift K=1->K=200 "
            "(0.228 -> 0.933) with cv=0.006 across seeds 7/13/19; K=200 reaches Delta=0.053 below DIRECT "
            "oracle (0.986); 18/18 arm_hashes distinct; not by-construction identity; retains hippo write "
            "path (sparse_dg + W_h + sign-thresholded reactivation + per-bank Hebbian); Stage 2 NREM Hc-"
            "rescue via cortex compartmentalization mechanism empirically established; CERT 633 -> 634."
        ),
        description=(
            "CHAIN_GRADE_PHASE_CHARACTERIZATION landed-VET of cell substrate_compartmentalized_cortex_K_banks_v2_GPU\n"
            "over 3 seeds (7, 13, 19) on RTX 4060 Ti GPU. M=2048 N_h=8192 N_c=2048 alpha_simple=0.250\n"
            "K_BANK=(1, 20, 50, 100, 200) + DIRECT oracle.\n"
            "\n"
            "OFF-DATA RECOMPUTE (Skunkworks 2026-06-30 evening, .venv Python; metrics.fresh_2026-06-30.json\n"
            "SCP-pulled by Orchestrator a3bafe51 because preserve-existing rule blocked standard sync):\n"
            "\n"
            "  Per-seed per-arm recall_cortex (off-disk verified bit-exact vs spawn-prompt):\n"
            "    seed_7  K1=0.213 K20=0.629 K50=0.818 K100=0.897 K200=0.926 DIRECT=0.985 elapsed=2.57s\n"
            "    seed_13 K1=0.221 K20=0.640 K50=0.832 K100=0.902 K200=0.939 DIRECT=0.987 elapsed=2.30s\n"
            "    seed_19 K1=0.250 K20=0.663 K50=0.831 K100=0.897 K200=0.935 DIRECT=0.985 elapsed=2.11s\n"
            "  Aggregate (per cell-author summary, off-disk re-derived):\n"
            "    ARM_STANDARD_K1     = 0.228 +/- 0.016 (cv=0.07)\n"
            "    ARM_COMPARTMENT_K20  = 0.644 +/- 0.014 (cv=0.02)\n"
            "    ARM_COMPARTMENT_K50  = 0.827 +/- 0.006 (cv=0.007)\n"
            "    ARM_COMPARTMENT_K100 = 0.899 +/- 0.002 (cv=0.002)\n"
            "    ARM_COMPARTMENT_K200 = 0.933 +/- 0.005 (cv=0.005)\n"
            "    ARM_DIRECT_UPPER     = 0.986 +/- 0.001 (cv=0.001)\n"
            "  best_lift = K200 - K1 = +0.705 (vs HP_LIFT_MIN=0.50; cleared by 0.205).\n"
            "  monotonic K=1 -> K=200: True within each seed.\n"
            "  cv_best = 0.006 (well below cv<=0.10 threshold).\n"
            "\n"
            "ARM-DISTINCTNESS (META_RULE_AX; load-bearing per-K mechanism_hash verification):\n"
            "  All 18 arm_hashes distinct (6 arms x 3 seeds):\n"
            "    seed_7:  K1=85439580b07cb64b K20=c3c6091a2f906067 K50=35d55a859720f6c8\n"
            "             K100=63c8d3c431736fd3 K200=93b1b43494f1fa2e DIRECT=4d12ed10de254890\n"
            "    seed_13: K1=53030b331fe59060 K20=94151d5e2e821302 K50=f355110ab675a920\n"
            "             K100=5148693480100f94 K200=e3929d8d91ec7699 DIRECT=0cc6b17cfc480dcd\n"
            "    seed_19: K1=795d9dcfd69b3d20 K20=7e546fe253ec08cb K50=d35e792b0ffb35bf\n"
            "             K100=a4add5b3d57f793f K200=ad5d4c00e69d22c6 DIRECT=6196c100019322ac\n"
            "  bank_sizes scale realistically: K1=2048/2048 (one bank); K20=102/103; K50=40/41;\n"
            "    K100=20/21; K200=10/11; DIRECT=-1/-1 (not banked). M=2048 / K=200 = 10.24 per bank.\n"
            "  cortex_norm scales 0.72 -> 3.26 monotonically with K (real per-bank Hebbian magnitude\n"
            "    growth; the sum of K per-bank Frobenius norms increases with finer compartments).\n"
            "  DIRECT cortex_norm=0.227 (single full Hopfield matrix on l2-normalized cortex vectors;\n"
            "    distinct mechanism from per-bank sign-thresholded outer products of replayed vectors).\n"
            "  K=200 cortex_norm=3.26 vs DIRECT cortex_norm=0.23 = factor 14.4x different mechanism\n"
            "    magnitude; not a by-construction identity.\n"
            "\n"
            "BY-CONSTRUCTION CHECK (Cell C v1 ARM_CLEAN_VALS_TO_CORTEX bit-identity trap NOT reproduced):\n"
            "  Cell C v1 had ARM_CLEAN_VALS_TO_CORTEX bit-identical to ARM_DIRECT (closeFrac=1.000)\n"
            "  because it copied vals directly into cortex without going through the hippo write path.\n"
            "  Cell C v2 COMPARTMENT arms RETAIN the full hippo write path:\n"
            "    keys_h = _sparse_dg(keys_raw, P_in, k_active)              # sparse DG\n"
            "    vals_h = _sparse_dg(vals_raw, P_in, k_active)              # sparse DG\n"
            "    W_h = vals_h.t() @ keys_h                                  # hippo assoc memory\n"
            "    vals_react_h = sign(cues_h @ W_h.t())                      # hippo replay\n"
            "    vals_c_react = l2norm(vals_react_h @ P_hc.t())             # cortex projection\n"
            "    bank_assign = original_idx % K_banks                       # per-bank routing\n"
            "    W_banks[k] = ETA * (v_k.t() @ c_k)                         # per-bank Hebbian\n"
            "  DIRECT arm pipeline (oracle):\n"
            "    keys_h = _sparse_dg(keys_raw, P_in, k_active)              # same DG\n"
            "    vals_c = l2norm(vals_h @ P_hc.t())                         # direct cortex (no replay)\n"
            "    W_c = ETA * (vals_c.t() @ keys_c)                          # single full Hopfield\n"
            "  Sustained Delta=0.053 between K=200 (0.933) and DIRECT (0.986) reflects:\n"
            "    (a) sign-thresholding in vals_react_h loses precision vs l2-normalized vals_c;\n"
            "    (b) hippo replay-and-route adds noise the oracle avoids;\n"
            "    (c) per-bank Hebbian partitions samples (~10 per bank at K=200) so each bank's\n"
            "        sub-Hopfield has lower capacity than the single full Hopfield of DIRECT.\n"
            "  K=200 NOT by-construction identity. The 0.053 gap is genuine mechanism cost of going\n"
            "  through the hippo replay path with per-bank routing.\n"
            "\n"
            "META_RULE COMPLIANCE:\n"
            "  META_RULE_AX arm-distinctness: PASS (18 distinct arm_hashes across 3 seeds).\n"
            "  META_RULE_AW seed-config-identical: PASS (all 3 seeds use M=2048, N_h=8192,\n"
            "    N_c=2048, alpha_simple=0.250, K_BANK=(1,20,50,100,200), HIPPO_SPARSITY_SPARSE,\n"
            "    ETA_CORTEX).\n"
            "  META_RULE_AU dispatch hygiene: cell ran on gpu_runner_0; backend=torch.cuda.\n"
            "  META_RULE_AV pre-flight: elapsed_s=6.99 aggregate (2.57+2.30+2.11 per seed);\n"
            "    above 1s floor; _phase not in {gpu_mandate_check, selftest_done}.\n"
            "  META_RULE_H cardinality_ok=True; expected_n=18 (6 arms x 3 seeds).\n"
            "  META_RULE_Q (suspect 1.000): NOT tripped. K=200 max = 0.939 (seed_13);\n"
            "    DIRECT max = 0.987 (seed_13); no phase-cell saturates to 1.000.\n"
            "  META_RULE_K discriminator-fires: K=1 baseline 0.228 vs K=200 0.933 with cv=0.006;\n"
            "    discriminator fires cleanly with +0.705 lift well above HP_LIFT_MIN=0.50.\n"
            "  Fix #28 per-arm reads: per-arm recall_cortex + arm_hash + cortex_norm read\n"
            "    independently per seed; not from verdict_msg summary.\n"
            "  Fix #26 discriminator-survives-scale: PASS at full M=2048; not smoke-only.\n"
            "  BIAS-M production-scale calibration: full M=2048 N_h=8192 N_c=2048; not smoke.\n"
            "  BIAS-N verify-referent: spawn-prompt cited K200=0.933 +/- 0.005; on-disk verified\n"
            "    bit-exact (mean of 0.926 + 0.939 + 0.935 / 3 = 0.933; stddev = 0.005).\n"
            "\n"
            "WHY CHAIN_GRADE PROMOTION:\n"
            "  (a) Monotonic K=1 -> K=200 within every seed (clean +0.705 best_lift).\n"
            "  (b) cv_best=0.006 across 3 seeds (1.4 orders of magnitude below cv<=0.10 threshold).\n"
            "  (c) All 18 arm_hashes distinct; no per-K identity collision (META_RULE_AX clean).\n"
            "  (d) K=200 NOT by-construction identity to DIRECT (sustained Delta=0.053; cortex_norm\n"
            "      factor 14.4x different; pipeline distinct: replay vs no-replay).\n"
            "  (e) Retains hippo write path (sparse_dg + W_h + sign-thresholded replay + per-bank\n"
            "      Hebbian); not the Cell C v1 ARM_CLEAN_VALS_TO_CORTEX bit-identity trap.\n"
            "  (f) cardinality_ok, run_mode=full, no META_RULE_Q saturation, elapsed clean.\n"
            "  (g) Stage 2 NREM Hc-rescue mechanism established: compartmentalized cortex with\n"
            "      K=200 sub-Hopfield banks (10 items each) rescues ~71% of the v2 hippo-bottleneck\n"
            "      gap (R_STANDARD_K1=0.228 baseline to R_DIRECT=0.986 oracle) via K-bank routing.\n"
            "  (h) Composes with hippo v2 Ha=51% MM atom: cortex compartmentalization provides the\n"
            "      empirically chain-grade path that the v2 hippo measurement showed was needed.\n"
            "\n"
            "WHY NOT MM/HF (honest-downward considered):\n"
            "  - by-construction identity to DIRECT: NOT triggered. Delta=0.053 sustained;\n"
            "    cortex_norm 14.4x apart; mechanism pipelines distinct.\n"
            "  - per-K identity collision (META_RULE_AX trap that caught ANCHOR 4 v3 dense triplet):\n"
            "    NOT triggered. All 6 arm_hashes distinct per seed; per-cell metrics monotonic.\n"
            "  - META_RULE_Q saturation masking: NOT triggered. Max recall = 0.987 (DIRECT seed_13);\n"
            "    no 1.000 ceiling artifact.\n"
            "  - Cell C v1 hippo write-path bypass trap: NOT reproduced. v2 COMPARTMENT arms\n"
            "    go through sparse_dg + W_h hippo memory + sign-thresholded replay before per-bank\n"
            "    Hebbian; verified by reading cell source lines 207-323.\n"
            "  - Cross-seed spread: K=200 spread {0.926, 0.939, 0.935} cv=0.005; tight enough\n"
            "    for chain-grade.\n"
            "\n"
            "MECHANISM CHARACTERIZATION (load-bearing for Stage 2 NREM cortex consolidation):\n"
            "  Compartmentalized cortex with K-bank routing implements per-class sub-Hopfield\n"
            "  memories. Each bank holds M/K items; per-bank capacity is bounded so per-bank\n"
            "  Hopfield retrieval is high-fidelity. The bank_assign = original_idx % K_banks\n"
            "  routing requires the readout to know the original item index (modular bank lookup).\n"
            "  In a brain-grounded reading: cortex consolidation routes hippo-replayed traces to\n"
            "  cortical sub-regions (compartments) that each hold a small set of related items;\n"
            "  retrieval first selects the cortical compartment (via index or content cue), then\n"
            "  runs Hopfield within that compartment. The +0.705 lift over K=1 (single global\n"
            "  Hopfield) demonstrates that capacity-limited Hopfield memory benefits substantially\n"
            "  from compartmentalization.\n"
            "  Cost: K=200 = 0.053 below DIRECT oracle. This is the cost of going through the\n"
            "  hippo replay path (sign-thresholded reactivation loses precision vs the l2-normalized\n"
            "  oracle path) plus per-bank capacity allocation (~10 items per bank at K=200).\n"
            "\n"
            "_llm_forward_calls_at_inference = 0.\n"
            "substrate_only_decode_gate: PASS.\n"
        ),
        kind=AtomKind.CHAIN_GRADE_PHASE_CHARACTERIZATION,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.MATH,
        algebra=None,
        metadata={
            "provenance_quality": "CERT_CHAIN_GRADE",
            "cert_status": "chain_grade",
            "cert_class": "pre_reg_pass",
            "cell_anchor": "substrate_compartmentalized_cortex_K_banks_v2_GPU",
            "metrics_paths": [METRICS_CELLC_V2],
            "ruling_note": RULING_NOTE,
            "verified_off_data": True,
            "run_mode": "full",
            "n_seeds": 3,
            "seeds_attempted": [7, 13, 19],
            "expected_n_units": 18,
            "cardinality_ok": True,
            "backend": "torch.cuda",
            "device": "cuda",
            "M": 2048,
            "N_h": 8192,
            "N_c": 2048,
            "alpha_simple": 0.250,
            "K_BANK_values": [1, 20, 50, 100, 200],
            "n_replay_per_item": "see_cell_config",
            "arms": [
                "ARM_STANDARD_K1", "ARM_COMPARTMENT_K20", "ARM_COMPARTMENT_K50",
                "ARM_COMPARTMENT_K100", "ARM_COMPARTMENT_K200", "ARM_DIRECT_UPPER",
            ],
            "per_seed_K1_recall": {"seed_7": 0.213, "seed_13": 0.221, "seed_19": 0.250},
            "per_seed_K20_recall": {"seed_7": 0.629, "seed_13": 0.640, "seed_19": 0.663},
            "per_seed_K50_recall": {"seed_7": 0.818, "seed_13": 0.832, "seed_19": 0.831},
            "per_seed_K100_recall": {"seed_7": 0.897, "seed_13": 0.902, "seed_19": 0.897},
            "per_seed_K200_recall": {"seed_7": 0.926, "seed_13": 0.939, "seed_19": 0.935},
            "per_seed_DIRECT_recall": {"seed_7": 0.985, "seed_13": 0.987, "seed_19": 0.985},
            "agg_K1_mean": 0.228,
            "agg_K1_stddev": 0.016,
            "agg_K20_mean": 0.644,
            "agg_K20_stddev": 0.014,
            "agg_K50_mean": 0.827,
            "agg_K50_stddev": 0.006,
            "agg_K100_mean": 0.899,
            "agg_K100_stddev": 0.002,
            "agg_K200_mean": 0.933,
            "agg_K200_stddev": 0.005,
            "agg_DIRECT_mean": 0.986,
            "agg_DIRECT_stddev": 0.001,
            "best_lift_K200_minus_K1": 0.705,
            "best_lift_minimum_threshold": 0.50,
            "cv_best_K200": 0.006,
            "cv_threshold_max": 0.10,
            "K200_to_DIRECT_gap": 0.053,
            "per_seed_arm_hash": {
                "seed_7": {
                    "K1": "85439580b07cb64b", "K20": "c3c6091a2f906067",
                    "K50": "35d55a859720f6c8", "K100": "63c8d3c431736fd3",
                    "K200": "93b1b43494f1fa2e", "DIRECT": "4d12ed10de254890",
                },
                "seed_13": {
                    "K1": "53030b331fe59060", "K20": "94151d5e2e821302",
                    "K50": "f355110ab675a920", "K100": "5148693480100f94",
                    "K200": "e3929d8d91ec7699", "DIRECT": "0cc6b17cfc480dcd",
                },
                "seed_19": {
                    "K1": "795d9dcfd69b3d20", "K20": "7e546fe253ec08cb",
                    "K50": "d35e792b0ffb35bf", "K100": "a4add5b3d57f793f",
                    "K200": "ad5d4c00e69d22c6", "DIRECT": "6196c100019322ac",
                },
            },
            "all_18_arm_hashes_distinct": True,
            "bank_sizes_min_max_per_K": {
                "K1": [2048, 2048], "K20": [102, 103], "K50": [40, 41],
                "K100": [20, 21], "K200": [10, 11], "DIRECT": [-1, -1],
            },
            "cortex_norm_K200_seed_7": 3.2633,
            "cortex_norm_DIRECT_seed_7": 0.2270,
            "cortex_norm_K200_vs_DIRECT_factor": 14.4,
            "by_construction_identity_to_DIRECT": False,
            "retains_hippo_write_path": True,
            "hippo_write_path_components": [
                "sparse_dg_keys_h_vals_h",
                "W_h_eq_vals_h_T_at_keys_h_hippo_assoc_memory",
                "sign_thresholded_vals_react_h",
                "P_hc_projection_to_cortex",
                "bank_assign_modulo_K_banks_per_bank_routing",
                "per_bank_Hebbian_W_banks_k_eq_ETA_v_k_T_at_c_k",
            ],
            "cell_c_v1_ARM_CLEAN_VALS_TO_CORTEX_bit_identity_trap_reproduced": False,
            "META_RULE_AX_per_arm_distinct_PASS": True,
            "META_RULE_AW_seed_config_identical_PASS": True,
            "META_RULE_AU_dispatch_hygiene_PASS": True,
            "META_RULE_AV_pre_flight_PASS": True,
            "META_RULE_H_cardinality_PASS": True,
            "META_RULE_Q_suspect_1p000_NOT_tripped": True,
            "META_RULE_K_discriminator_fires_PASS": True,
            "Fix_28_per_arm_reads_not_verdict_msg": True,
            "Fix_26_discriminator_survives_scale_PASS": True,
            "BIAS_M_production_scale_calibration_PASS": True,
            "BIAS_N_verify_referent_PASS": True,
            "stage_2_NREM_Hc_rescue_mechanism_established": True,
            "composes_with_hippo_v2_Ha_51pct_MM_atom": True,
            "load_bearing_finding_1": "k_bank_routing_through_hippo_replay_lifts_recall_0p228_to_0p933_monotonic",
            "load_bearing_finding_2": "k200_not_by_construction_identity_to_direct_delta_0p053_sustained_cortex_norm_14x_apart",
            "load_bearing_finding_3": "retains_hippo_write_path_sparse_dg_W_h_sign_threshold_per_bank_hebbian",
            "load_bearing_finding_4": "all_18_arm_hashes_distinct_no_per_K_collision_meta_rule_ax_clean",
            "extends_or_supersedes_prior": (
                "complements_hippo_v2_Ha_51pct_MM_chain_grade_path_for_stage_2_NREM_consolidation_"
                "supersedes_cell_C_v1_ARM_CLEAN_VALS_TO_CORTEX_trap_with_clean_v2_pipeline"
            ),
            "promotion_rationale_summary": (
                "monotonic_K1_to_K200_lift_0p705_cv_0p006_18of18_arm_hashes_distinct_K200_not_BC_identity_"
                "to_DIRECT_delta_0p053_sustained_retains_hippo_write_path_meta_rule_q_not_tripped_meta_rule_ax_"
                "ax_aw_au_av_h_clean_stage2_NREM_Hc_rescue_mechanism_established"
            ),
            "scope_observed": (
                "3_seeds_M_2048_N_h_8192_N_c_2048_alpha_simple_0p250_K_BANK_1_20_50_100_200_plus_DIRECT_"
                "single_phase_point_per_arm_recall_cortex_GPU_RTX_4060_Ti_full_mode"
            ),
            "scope_not_claimed": (
                "5_of_5_seeds_OR_K_bank_gt_200_OR_M_gt_2048_OR_natural_text_inputs_OR_other_substrate_"
                "dimensions_OR_phase_grid_sweep_over_alpha_simple_OR_HIPPO_SPARSITY_sweep"
            ),
            "promotion_path_future": (
                "extend_K_bank_sweep_to_400_500_to_find_capacity_ceiling_OR_M_sweep_to_M_4096_M_8192_"
                "OR_alpha_simple_sweep_to_find_compartmentalization_regime_OR_integrate_with_NREM_replay"
                "_to_close_DIRECT_oracle_gap"
            ),
            "zero_llm_calls_at_inference": True,
            "_llm_forward_calls_at_inference": 0,
            "substrate_only_decode_gate": "PASS",
            "atomized_by": ATOMIZED_BY,
        },
    )


# ============================================================================
# ATOM 3 -- META_RULE_AY verdict_emitter_auto_demote_on_self_reported_distinctness_False
# ============================================================================

def build_atom3_meta_rule_ay_verdict_emitter_auto_demote() -> Atom:
    return Atom(
        id=(
            "RULE_verdict_emitter_must_auto_HARD_FAIL_or_MM_demote_if_cell_self_reported_distinctness_field_"
            "contains_False_complementary_to_META_RULE_AX_phantom_full_detection_at_cell_author_layer_"
            "anchor4_v3_witness_encoder_pair_distinctness_3_of_10_False_but_HARD_PASS_emitted_META_RULE_AY_2026-06-30"
        ),
        name=(
            "META_RULE_AY: verdict-emitter logic MUST auto-HARD_FAIL or auto-demote to "
            "MEASURED_MECHANISM if any cell self-reported distinctness diagnostic field (e.g. "
            "encoder_pair_distinctness, arm_pair_distinctness, mechanism_hash_distinctness, per_arm_"
            "distinct, etc.) contains False. Cell-author HARD_PASS framings must be auto-demoted by "
            "the verdict-emitter when self-reported distinctness fails. Complementary automation "
            "discipline to META_RULE_AX (phantom-FULL detection at landed-VET); AY closes the loop "
            "at the cell-author layer so phantom-FULL is caught BEFORE landing rather than only at "
            "the Skunkworks VET."
        ),
        description=(
            "META_RULE_AY: VERDICT-EMITTER AUTO-DEMOTE ON CELL SELF-REPORTED DISTINCTNESS FALSE.\n"
            "\n"
            "PROBLEM (witnessed in ANCHOR 4 v3 2026-06-30):\n"
            "  Cell substrate_anchor4_encoder_family_phase_diagram_v3 publishes a diagnostic field\n"
            "  `encoder_pair_distinctness` with 10 boolean entries (one per encoder pair). Three of\n"
            "  the 10 entries are False on every seed:\n"
            "    binary_bipolar_vs_hrr_real: False\n"
            "    binary_bipolar_vs_fhrr:     False\n"
            "    hrr_real_vs_fhrr:           False\n"
            "  These False values are exactly the cell-author's own diagnostic for phantom-FULL\n"
            "  recurrence (META_RULE_AX) at the cell-author layer. Yet the verdict-emitter logic\n"
            "  publishes HARD_PASS verdict='HARD_PASS_ENCODER_DISCRIMINATION_v3: ... 5/5 encoders\n"
            "  pass v2-PB+AP chain-grade ... encoder_tiers={... COMPETITIVE_ENCODER ...}' anyway,\n"
            "  because the verdict logic only checks per-encoder Pareto-AUC dominance + recency\n"
            "  threshold, NOT the pair-distinctness diagnostic.\n"
            "  Result: a HARD_PASS verdict is emitted for a cell whose own diagnostic shows the\n"
            "  encoder axis is not fully wired. Skunkworks landed-VET caught this as the 6th\n"
            "  phantom-FULL recurrence (partial). But the verdict should have been auto-demoted at\n"
            "  the cell-author layer to prevent the HARD_PASS framing from reaching Director.\n"
            "\n"
            "RULE (load-bearing):\n"
            "  Any verdict-emitter in any cell that publishes a `verdict` field with HARD_PASS\n"
            "  status MUST first scan the metrics dict for any field named with the substring\n"
            "  'distinctness' (or 'distinct') that contains a dict-of-bool or list-of-bool. If ANY\n"
            "  entry in such a field is False, the verdict-emitter MUST:\n"
            "    (a) downgrade verdict to MEASURED_MECHANISM or HARD_FAIL_PARTIAL_DISCRIMINATION,\n"
            "        depending on the fraction of False entries;\n"
            "    (b) include in verdict_msg an explicit string 'AUTO_DEMOTE_self_reported_pair_\n"
            "        distinctness_<field_name>_<count_False>_of_<count_total>_False';\n"
            "    (c) set a metadata flag `auto_demoted_self_reported_distinctness_False=True`;\n"
            "    (d) NOT emit any '<N>/<N> chain_grade' string in verdict_msg if any pair is\n"
            "        non-distinct.\n"
            "  Threshold heuristic (default): if False_count / total >= 0.1 (10%), demote to\n"
            "    MEASURED_MECHANISM; if >= 0.5 demote to HARD_FAIL.\n"
            "\n"
            "COMPLEMENTARY TO META_RULE_AX:\n"
            "  META_RULE_AX is the SKUNKWORKS landed-VET discipline: at VET time, verify per-arm /\n"
            "  per-encoder / per-K mechanism_hash distinct before chain-grade promotion.\n"
            "  META_RULE_AY is the CELL-AUTHOR-LAYER automation that catches phantom-FULL at\n"
            "  publish time, so the verdict that reaches Director (and downstream cells) is\n"
            "  already self-consistent with the cell's own diagnostic.\n"
            "  Together AX + AY form a 2-layer phantom-FULL defense: AY at cell-author publish;\n"
            "  AX at Skunkworks landed-VET.\n"
            "\n"
            "DISCIPLINE FOR CELL AUTHORS:\n"
            "  When designing a verdict-emitter, include a final 'auto-demote pass' that:\n"
            "    1. Walks the metrics dict for any *_distinctness or *_distinct field.\n"
            "    2. Counts False entries.\n"
            "    3. Applies the threshold heuristic above.\n"
            "    4. Emits a verdict consistent with the cell's own diagnostic.\n"
            "  Example pseudocode:\n"
            "    distinctness_violations = []\n"
            "    for k, v in metrics.items():\n"
            "        if 'distinct' in k.lower() and isinstance(v, (dict, list)):\n"
            "            entries = v.values() if isinstance(v, dict) else v\n"
            "            n_false = sum(1 for e in entries if e is False)\n"
            "            n_total = len(entries)\n"
            "            if n_false > 0:\n"
            "                distinctness_violations.append((k, n_false, n_total))\n"
            "    if distinctness_violations:\n"
            "        fraction = max(nf/nt for _, nf, nt in distinctness_violations)\n"
            "        if fraction >= 0.5:\n"
            "            verdict = 'HARD_FAIL_PARTIAL_DISCRIMINATION'\n"
            "        elif fraction >= 0.1:\n"
            "            verdict = 'MEASURED_MECHANISM_PARTIAL_DISCRIMINATION'\n"
            "        metadata['auto_demoted_self_reported_distinctness_False'] = True\n"
            "        verdict_msg += f' AUTO_DEMOTE_distinctness_violations={distinctness_violations}'\n"
            "\n"
            "FALSIFIES THE NAIVE READING: 'Aggregate metric (Pareto-AUC, dominance, recency) at\n"
            "  HARD_PASS threshold is sufficient for chain-grade verdict.' This is false when the\n"
            "  cell's own diagnostic flags pair non-distinctness, because two arms that produce\n"
            "  identical metrics will both 'pass' the aggregate threshold but they are NOT\n"
            "  independent arms (they are the same computational path).\n"
            "\n"
            "WITNESS (ANCHOR 4 v3 2026-06-30 evening):\n"
            "  3 seeds (7, 13, 19); cell-author emitted HARD_PASS with encoder_tiers ALL\n"
            "  COMPETITIVE_ENCODER for binary_bipolar/hrr_real/fhrr despite encoder_pair_\n"
            "  distinctness reporting 3 False pairs. Skunkworks landed-VET tiered MM_PARTIAL_\n"
            "  DISCRIMINATION (6th phantom-FULL recurrence, partial fix). With META_RULE_AY in\n"
            "  place at cell-author publish layer, the cell would have auto-demoted to MM\n"
            "  and never emitted the HARD_PASS framing in the first place.\n"
            "\n"
            "RELATION TO OTHER META RULES:\n"
            "  Companion to META_RULE_AX (phantom-FULL detection): AY = publish-time prevention;\n"
            "    AX = VET-time detection. AY reduces Skunkworks workload + reduces Director's\n"
            "    risk of acting on a phantom HARD_PASS.\n"
            "  Companion to META_RULE_AF (arms-must-differ): AF requires distinct mechanism arms;\n"
            "    AY enforces that the verdict-emitter honors AF's diagnostic output.\n"
            "  Companion to META_RULE_Q (suspect 1.000): Q catches saturation masking encoder\n"
            "    differences at high-capacity; AY catches encoder path collapse at low-capacity.\n"
            "  Companion to Fix #28 (verify per-arm not verdict_msg): Fix #28 is the Skunkworks /\n"
            "    Director discipline; AY is the cell-author-side automation that makes verdict_msg\n"
            "    consistent with per-arm in the first place.\n"
            "\n"
            "VERIFIED-OFF-DATA EVIDENCE POINTERS:\n"
            "  data/exp_substrate_anchor4_encoder_family_phase_diagram_v3_seed_{7,13,19}/\n"
            "    metrics.fresh_2026-06-30.json (3 files; encoder_pair_distinctness field shows\n"
            "    3 False entries; verdict='HARD_PASS' emitted regardless)\n"
            "  Atom 1 of this batch: substrate_anchor4_encoder_family_phase_diagram_v3 3-seed\n"
            "    MM_PARTIAL_DISCRIMINATION ruling.\n"
            "\n"
            "FIRST ATOMIZED 2026-06-30 by Skunkworks ANCHOR 4 v3 + Cell C v2 landed-VET evening\n"
            "  batch (.venv off-data recompute via tools/atomize_skunkworks_anchor4_v3_MM_and_\n"
            "  cell_c_v2_CG_and_meta_AY_2026-06-30.py).\n"
            "\n"
            "NAMING NOTE: META_RULE_AR (centroid noise-suppression, 2026-06-30 morning); AS, AT,\n"
            "  AU, AV, AW, AX taken (audit-discipline + dispatch-hygiene rules through this\n"
            "  session). AY is the next free monotonic slot.\n"
        ),
        kind=AtomKind.METHODOLOGY_RULE,
        tier=Tier.TIER_METHODOLOGY,
        corpus=Corpus.META,
        algebra=None,
        metadata={
            "provenance_quality": "META_RULE",
            "cert_status": "discipline_meta",
            "cert_class": "discipline_meta",
            "rule_id": "META_RULE_AY",
            "rule_topic": (
                "verdict_emitter_must_auto_HARD_FAIL_or_MM_demote_if_cell_self_reported_"
                "distinctness_field_contains_False"
            ),
            "rule_layer": "cell_author_verdict_emitter_publish_time_auto_demote",
            "complementary_to_META_RULE_AX_phantom_full_skunkworks_VET_detection": True,
            "evidence_atoms": [
                (
                    "T3/EXP_substrate_anchor4_encoder_family_phase_diagram_v3_3seed_MM_PARTIAL_DISCRIMINATION_"
                    "dense_triplet_binary_bipolar_eq_hrr_real_eq_fhrr_phantom_sparse_bipolar_sparse_real_distinct_"
                    "encoder_pair_distinctness_3_of_10_False_per_cell_ws_ret_TD_bit_identical_dense_seed_7_13_19_"
                    "metarule_q_suspect_1p000_at_high_capacity_2_of_5_encoders_wired_6th_phantom_FULL_partial_2026-06-30"
                ),
            ],
            "demotion_threshold_heuristic": {
                "false_fraction_gte_0p5": "HARD_FAIL_PARTIAL_DISCRIMINATION",
                "false_fraction_gte_0p1": "MEASURED_MECHANISM_PARTIAL_DISCRIMINATION",
                "false_fraction_lt_0p1": "keep_original_verdict_but_flag",
            },
            "required_metadata_flag_on_auto_demote": "auto_demoted_self_reported_distinctness_False",
            "required_verdict_msg_string_on_auto_demote": (
                "AUTO_DEMOTE_self_reported_pair_distinctness_<field_name>_<count_False>_of_<count_total>_False"
            ),
            "applies_to_distinctness_field_patterns": [
                "encoder_pair_distinctness", "arm_pair_distinctness",
                "mechanism_hash_distinctness", "per_arm_distinct",
                "per_K_distinct", "any_field_with_substring_distinct_lower_case",
            ],
            "witness_cell_anchor": "substrate_anchor4_encoder_family_phase_diagram_v3",
            "witness_3_False_pairs": [
                "binary_bipolar_vs_hrr_real",
                "binary_bipolar_vs_fhrr",
                "hrr_real_vs_fhrr",
            ],
            "witness_emitted_verdict": "HARD_PASS_ENCODER_DISCRIMINATION_v3",
            "witness_corrected_skunkworks_tier": "MM_PARTIAL_DISCRIMINATION",
            "phantom_full_recurrence_count_at_witness_time": 6,
            "companion_META_RULE_AX_phantom_full_VET_detection": True,
            "companion_META_RULE_AF_arms_must_differ": True,
            "companion_META_RULE_Q_suspect_1p000": True,
            "companion_Fix_28_verify_per_arm_not_verdict_msg": True,
            "naming_note": (
                "META_RULE_AR_centroid_noise_suppression_2026-06-30_morning_through_AX_phantom_full_VET_detection_"
                "this_session_AY_is_next_free_monotonic_slot"
            ),
            "verified_off_data": True,
            "first_atomized_ts": "2026-06-30",
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
    print(f"[anchor4_v3_cellC_v2_AY_vet] mode={mode}")

    store = PartitionedStore(STORE_ROOT)

    pre_cert_n = _cert_count(store)
    print(f"[anchor4_v3_cellC_v2_AY_vet] PRE cert_n={pre_cert_n}")
    # Allow re-run: PRE can be 633 (fresh) or 634 (Atom 2 already landed from prior partial-success)
    assert pre_cert_n in (633, 634), f"PRE cert_n {pre_cert_n} not in {{633, 634}}"
    # base for delta math is 633 (pre-Atom-2-landing); if pre is already 634, atom2 landed earlier
    BASE_PRE = 633

    atom1 = build_atom1_anchor4_v3_mm_partial()
    atom2 = build_atom2_cell_c_v2_chain_grade()
    atom3 = build_atom3_meta_rule_ay_verdict_emitter_auto_demote()
    atoms = [atom1, atom2, atom3]

    for i, a in enumerate(atoms, 1):
        print(
            f"[anchor4_v3_cellC_v2_AY_vet] Atom {i}: id_head={str(a.id)[:90]}... "
            f"corpus={a.corpus.name} tier={a.tier.name} kind={a.kind.name}"
        )

    if not apply:
        print("[anchor4_v3_cellC_v2_AY_vet] DRY mode -- no Store / ledger writes. Re-run with --apply.")
        return 0

    # ============================================================
    # APPLY Atom 1 (MM, delta=0)
    # ============================================================
    expected_n_after_atom1 = BASE_PRE   # MM delta=0

    print("[anchor4_v3_cellC_v2_AY_vet] Writing Atom 1 (ANCHOR 4 v3 3-seed MM_PARTIAL_DISCRIMINATION)...")
    store.add_atom(atom1)
    post_n_1 = _cert_count(store)
    # Atom 1 is MM (delta=0); allow live to be ahead by 1 if Atom 2 already landed in a prior run.
    assert post_n_1 in (expected_n_after_atom1, expected_n_after_atom1 + 1), (
        f"After Atom 1: cert_n={post_n_1} not in {{{expected_n_after_atom1}, {expected_n_after_atom1+1}}}"
    )
    append_cert_ledger_row(
        {
            "op": "cert_ruling",
            "atom_id": f"math::{atom1.id}",
            "cert_status": "measured_mechanism",
            "cert_class": "mechanism_characterization",
            "verified_off_data": True,
            "atomized_by": ATOMIZED_BY,
            "cell_commit": None,
            "verdict": "MM_PARTIAL_DISCRIMINATION_2_OF_5_ENCODERS_WIRED_DENSE_TRIPLET_PHANTOM_FULL_6TH_RECURRENCE",
            "cert_increment_delta": 0,
            "cv": None,
            "referent_pointer": {
                "notes_path": RULING_NOTE,
                "metrics_path": METRICS_A4_V3_SEED_7,
                "atom_qualified_id": f"math::{atom1.id}",
            },
            "supersedes": None,
            "note": (
                "anchor4_v3_3seed_dense_triplet_binary_hrr_fhrr_collapse_bit_identical_mechanism_hash_"
                "per_cell_ws_ret_TD_recency_eq_to_6_decimals_sparse_bipolar_sparse_real_distinct_encoder_"
                "pair_distinctness_3_of_10_False_meta_rule_q_suspect_1p000_at_high_capacity_meta_rule_ax_"
                "phantom_full_6th_recurrence_partial_2_of_5_encoders_wired_required_v4_dense_binding_path_"
                "separation_HRR_FFT_FHRR_complex_binary_XOR"
            ),
        },
        # Live cert_n at this ledger call equals post-atom1-add state (= BASE_PRE unless re-run).
        expected_cert_n_pre=post_n_1,
        expected_cert_n_post=post_n_1,
    )

    # ============================================================
    # APPLY Atom 2 (CG, delta=+1)
    # ============================================================
    expected_n_after_atom2 = expected_n_after_atom1 + 1   # CG delta=+1

    print("[anchor4_v3_cellC_v2_AY_vet] Writing Atom 2 (Cell C v2 3-seed CHAIN_GRADE_PHASE_CHARACTERIZATION)...")
    store.add_atom(atom2)
    post_n_2 = _cert_count(store)
    assert post_n_2 == expected_n_after_atom2, (
        f"After Atom 2: cert_n={post_n_2} != {expected_n_after_atom2}"
    )
    append_cert_ledger_row(
        {
            "op": "cert_ruling",
            "atom_id": f"math::{atom2.id}",
            "cert_status": "chain_grade",
            "cert_class": "pre_reg_pass",
            "verified_off_data": True,
            "atomized_by": ATOMIZED_BY,
            "cell_commit": None,
            "verdict": "CHAIN_GRADE_PHASE_CHARACTERIZATION_K_BANK_HOPFIELD_HIPPO_REPLAY_ROUTE_RETAINS_WRITE_PATH",
            "cert_increment_delta": 1,
            "cv": 0.006,
            "referent_pointer": {
                "notes_path": RULING_NOTE,
                "metrics_path": METRICS_CELLC_V2,
                "atom_qualified_id": f"math::{atom2.id}",
            },
            "supersedes": None,
            "note": (
                "cell_c_v2_3seed_K_bank_routing_through_hippo_replay_path_K1_0p228_to_K200_0p933_best_lift_"
                "0p705_cv_0p006_18_of_18_arm_hashes_distinct_K200_not_BC_identity_to_DIRECT_delta_0p053_"
                "sustained_cortex_norm_14x_apart_retains_hippo_write_path_sparse_dg_W_h_sign_threshold_per_"
                "bank_hebbian_meta_rule_q_NOT_tripped_meta_rule_ax_aw_au_av_h_clean_stage2_NREM_Hc_rescue_"
                "mechanism_established_complements_hippo_v2_Ha_51pct_MM"
            ),
        },
        # PRE/POST after Store add: live cert_n already incremented; assertion checks live==expected_pre.
        expected_cert_n_pre=expected_n_after_atom2,
        expected_cert_n_post=expected_n_after_atom2,
    )

    # ============================================================
    # APPLY Atom 3 (META, delta=0)
    # ============================================================
    expected_n_after_atom3 = expected_n_after_atom2   # META delta=0

    print("[anchor4_v3_cellC_v2_AY_vet] Writing Atom 3 (META_RULE_AY verdict_emitter_auto_demote)...")
    store.add_atom(atom3)
    post_n_3 = _cert_count(store)
    assert post_n_3 == expected_n_after_atom3, (
        f"After Atom 3: cert_n={post_n_3} != {expected_n_after_atom3}"
    )
    append_cert_ledger_row(
        {
            "op": "cert_ruling",
            "atom_id": f"meta::{atom3.id}",
            "cert_status": "custom",
            "cert_class": "discipline_meta",
            "verified_off_data": True,
            "atomized_by": ATOMIZED_BY,
            "cell_commit": None,
            "verdict": "META_RULE_NEUTRAL",
            "cert_increment_delta": 0,
            "cv": None,
            "referent_pointer": {
                "notes_path": RULING_NOTE,
                "metrics_path": "n/a-meta-rule-derived-from-anchor4_v3_Atom1-encoder_pair_distinctness-3-of-10-False",
                "atom_qualified_id": f"meta::{atom3.id}",
            },
            "supersedes": None,
            "note": (
                "META_RULE_AY_verdict_emitter_must_auto_HARD_FAIL_or_MM_demote_if_self_reported_distinctness_"
                "field_contains_False_complementary_to_META_RULE_AX_phantom_full_VET_detection_at_cell_author_"
                "publish_layer_witness_anchor4_v3_3_of_10_encoder_pair_distinctness_False_but_HARD_PASS_emitted_"
                "threshold_heuristic_false_fraction_gte_0p5_HARD_FAIL_gte_0p1_MM_companion_AF_Q_Fix_28_AX"
            ),
        },
        expected_cert_n_pre=expected_n_after_atom2,
        expected_cert_n_post=expected_n_after_atom3,
    )

    final_cert_n = _cert_count(store)
    print(
        f"[anchor4_v3_cellC_v2_AY_vet] FINAL cert_n={final_cert_n} "
        f"(pre={pre_cert_n}, delta=+1; 1 MM + 1 CG + 1 META)"
    )
    assert final_cert_n == expected_n_after_atom3

    # Round-trip verify: each atom should reload
    store_verify = PartitionedStore(STORE_ROOT)
    for a in atoms:
        match = [x for x in store_verify.all_atoms() if x.id == a.id]
        assert len(match) == 1, f"Round-trip FAIL for atom id={a.id} (found {len(match)})"
        assert (match[0].metadata or {}).get("atomized_by") == ATOMIZED_BY
        print(f"[anchor4_v3_cellC_v2_AY_vet] Round-trip OK: {a.id[:60]}...")

    print(
        "[anchor4_v3_cellC_v2_AY_vet] APPLY OK -- 3 atoms landed; ledger 3 rows appended; "
        f"cert_n {pre_cert_n} -> {final_cert_n} (+1 from Atom 2 CG; Atoms 1+3 delta=0)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
