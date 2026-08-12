"""Atomize: Skunkworks landed-VET capacity_stress_v4 4-seed CHAIN_GRADE_MULTI (2026-06-30).

Source: fresh Skunkworks dispatch (2026-06-30) replacing wedged earlier dispatch
  a1fd5d149c7295680 which never returned. Cell anchor:
  substrate_schema_exemplar_bayes_capacity_stress_v4

Seeds analyzed (off-disk recompute via .venv Python; .../data/exp_..._seed_<s>/metrics.json):
  seed_7  : IMPORT_CRASH (ModuleNotFoundError: _core not on remote at run time)
  seed_13 : CHAIN_GRADE_MULTI 3/3 gates (GR=T HM=T RF=T)  floor_ret=0.40 fl=80x
  seed_19 : CHAIN_GRADE_MULTI 2/3 gates (GR=F HM=T RF=T)  floor_ret=0.25 fl=50x
  seed_23 : CHAIN_GRADE_MULTI 3/3 gates (GR=T HM=T RF=T)  floor_ret=0.35 fl=70x
  seed_29 : CHAIN_GRADE_MULTI 3/3 gates (GR=T HM=T RF=T)  floor_ret=0.45 fl=90x
  Effective N=4; gate-doc requires >=3/5 -- met for all 3 gates.

INDEPENDENT OFF-DATA RECOMPUTE (.venv/Scripts/python.exe; all gates re-derived from
per_phase_point arms):

  Per-seed (verified-off-data, all cite numbers reproduce exactly within 1e-5):
    seed   verdict   gates  GR_fr  GR_fl   HM_fr  HM_fl  HM_or  RF_cliff  div   card
    13     CG_MULTI  3/3    0.400  80x     0.600  120x   64     56        64/64 True
    19     CG_MULTI  2/3    0.250  50x     0.700  140x   64     58        64/64 True
    23     CG_MULTI  3/3    0.350  70x     0.600  120x   64     59        64/64 True
    29     CG_MULTI  3/3    0.450  90x     0.700  140x   64     57        64/64 True

  Cross-seed AGG (4-seed; seed_7 excluded as import-crash):
    [A] GRACEFUL: 3/5 seeds met (need>=3); mean_floor_ret=0.362 (need>=0.30);
        mean_decades=5.0 (need>=3). -- PASS
    [B] HARDMAX:  4/5 seeds met (need>=3); mean_floor_ret=0.650 (need>=0.50);
        mean_floor_lift=130.0x (need>=10x); mean_over_ref=64.0 (need>=25). -- PASS
    [C] REFCLIFF: 4/5 seeds met (need>=3); mean_cliff_pts=57.5 (need>=10). -- PASS

  TOTAL AGG: 3/3 (cleanly above the >=2-of-3 MULTI threshold).

CERT-TIER DECISION: CHAIN_GRADE_PHASE_CHARACTERIZATION (delta +1; 632 -> 633)

  Rationale:
    1. All 3 AGG gates met simultaneously (would qualify CG_MULTI at 2-of-3).
    2. HARDMAX is 4-of-4 with 130x mean lift; substantial-effect; not by-construction.
    3. GRACEFUL is 3-of-4 (seed_19 just-below at floor_retention=0.250 vs 0.30 threshold;
       honest variance not pathology -- D4 is a single phase point).
    4. REFCLIFF is 4-of-4 with mean 57.5 cliff points; well above the 10-point requirement.
    5. cardinality_ok, arms_diverge=64/64, arms_identical_pathology=False, random_arm_pathology
       =False clean across all 4 seeds. expected_n=5120 = observed_n on every seed.
    6. seed_7 IMPORT_CRASH is honest infra failure (commit fdf4c714 _core.py not on remote);
       not a methodological pathology.
    7. Prior 4-of-5 effective replication is conservative; pre-reg's >=3/5 threshold cleared.
    8. Mechanism-class audit (META_RULE_AF): 4 distinct mechanism arms (BAYES posterior /
       HARDMAX centroid argmax / REFERENCE prior / UNIFORM_RANDOM); HM is primitive-substitution
       not hyperparameter sweep (per Skunkworks 2x-drill Option B).

  Honest-downward considerations evaluated:
    - BIAS-Q saturation: NOT triggered. HARDMAX D2/D3 means 0.82/0.77 (substantial spread;
      not metric-cap). GRACEFUL D2/D3 means 0.74/0.65 (not saturating).
    - Fix #26 discriminator-survives-scale: PASS. Full-N (n_q=20 per combo, 64 combos, 4 arms,
      4 seeds) fires at 64/64 phase points per seed.
    - Cross-seed spread: floor_retention {0.40, 0.25, 0.35, 0.45} -- one outlier (seed_19) on
      the weakest gate by 0.05; load-bearing HARDMAX and REFCLIFF are tight (HM 4/4, RF 4/4).
    - Effective N=4 (seed_7 lost): stricter than >=3/5 = 60%; we have 3/4 = 75% and 4/4 = 100%.

  Net: chain-grade promotion APPROVED.

REFINED MECHANISM CHARACTERIZATION (load-bearing for bonus META_RULE_AR):
  The cell-author's framing "HARDMAX is noise-suppressing AT FLOOR" is partly inverted by
  off-disk recompute. Decade-binned HM-GR averages (4-seed):
    D0 (alpha<0.01, n=1):  HM=GR=0.875                                 # both at near-ceiling
    D1 (0.01<=alpha<0.1, n=9):  HM 0.887 - GR 0.867 = +0.021           # tiny HM edge
    D2 (0.1<=alpha<1,   n=28): HM 0.830 - GR 0.763 = +0.067            # clear HM edge
    D3 (1<=alpha<10,    n=25): HM 0.773 - GR 0.647 = +0.127            # large HM edge
    D4 (alpha>=10,      n=1):  HM 0.650 - GR 0.362 = +0.288            # largest HM edge
  HM advantage GROWS with capacity-stress (higher alpha), not at the storage-floor.
  Refined claim: HM centroid acts as a low-variance prototype that SUPPRESSES per-exemplar
  noise UNDER capacity stress (alpha >= 1), where Bayes-LSE smoothing inherits per-exemplar
  noise that the centroid's K-sample averaging dampens by ~1/sqrt(K). The cited "FLOOR" in
  the cell-author summary refers to the alpha=19.5 FLOOR-OF-MECHANISM (where both arms are
  most stressed), NOT the alpha<0.01 storage-floor.

LEDGER ROWS: 2 (1 chain_grade +1 / 1 discipline_meta +0)
  Atom 1: T3/EXP_substrate_schema_exemplar_bayes_capacity_stress_v4 chain_grade_phase_char
  Atom 2: META_RULE_AR centroid_argmax_noise_suppression_at_capacity_stress

PRE CERT N (verified live): 632
POST CERT N (predicted; A5-gated): 633 (chain_grade delta=+1)

A5 GATING: PRE/POST cert_n + axiom_206 + cap_pres_6/6 on every window; round-trip pq check
  on every atom.

Run:
  cd d:/AI/hd-instrument
  .venv/Scripts/python.exe tools/atomize_skunkworks_capacity_stress_v4_4seed_CG_2026-06-30.py            # DRY
  .venv/Scripts/python.exe tools/atomize_skunkworks_capacity_stress_v4_4seed_CG_2026-06-30.py --apply    # WRITE
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(".").resolve()))
from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier
from tools.cert_ledger_writer import append_cert_ledger_row

STORE_ROOT = Path("data/substrate_index")
RULING_NOTE = "notes/skunkworks_landed_vet_schema_exemplar_bayes_capacity_stress_v4_4seed_CG_2026-06-29.md"
CELL_COMMIT = "fdf4c714"   # AtomKind enum fix commit (per spawn prompt)
ATOMIZED_BY = "skunkworks_atomize_capacity_stress_v4_4seed_CG_2026-06-30"

METRICS_SEED_13 = "data/exp_substrate_schema_exemplar_bayes_capacity_stress_v4_seed_13/metrics.json"
METRICS_SEED_19 = "data/exp_substrate_schema_exemplar_bayes_capacity_stress_v4_seed_19/metrics.json"
METRICS_SEED_23 = "data/exp_substrate_schema_exemplar_bayes_capacity_stress_v4_seed_23/metrics.json"
METRICS_SEED_29 = "data/exp_substrate_schema_exemplar_bayes_capacity_stress_v4_seed_29/metrics.json"
METRICS_SEED_7  = "data/exp_substrate_schema_exemplar_bayes_capacity_stress_v4_seed_7/metrics.json"


# ============================================================================
# ATOM 1 -- capacity_stress_v4 4-seed CHAIN_GRADE_PHASE_CHARACTERIZATION (+1)
# ============================================================================

def build_atom1_capacity_stress_v4_chain_grade() -> Atom:
    return Atom(
        id=(
            "T3/EXP_substrate_schema_exemplar_bayes_capacity_stress_v4_4seed_AGG_CHAIN_GRADE_MULTI_"
            "3of3_gates_GRACEFUL_3of5_HARDMAX_4of5_REFCLIFF_4of5_floor_ret_mean_0p362_HM_floor_ret_"
            "mean_0p650_HM_floor_lift_mean_130x_HM_over_ref_64_64pts_RF_cliff_57p5_avg_gr_minus_ref_"
            "0p586_seed_13_3of3_seed_19_2of3_GR_fail_floor_0p25_seed_23_3of3_seed_29_3of3_seed_7_"
            "IMPORT_CRASH_effective_N_4_phase_characterization_chain_grade_2026-06-30"
        ),
        name=(
            "substrate_schema_exemplar_bayes_capacity_stress_v4 4-seed CHAIN_GRADE_MULTI: at 64 phase "
            "points (n_ex x n_classes x N) the BAYES_GRACEFUL / HARDMAX centroid / REFERENCE / UNIFORM "
            "arms separate by mechanism class with 3/3 cross-seed AGG gates passing (GRACEFUL=3/5, "
            "HARDMAX=4/5, REFCLIFF=4/5); HM centroid noise-suppression grows monotonically with alpha; "
            "MULTI promotion at delta=+1 (632->633)."
        ),
        description=(
            "CHAIN_GRADE_MULTI landed-VET of cell substrate_schema_exemplar_bayes_capacity_stress_v4\n"
            "over 4 effective seeds (13, 19, 23, 29; seed_7 IMPORT_CRASH excluded), AtomKind-fix\n"
            "commit fdf4c714.\n"
            "\n"
            "OFF-DATA RECOMPUTE (Skunkworks 2026-06-30, .venv Python, every metric independently\n"
            "recomputed from per_phase_point arm accuracies; spawn-prompt claims verified bit-exact):\n"
            "\n"
            "  Run mode (CRITICAL per Fix #28): all 4 seeds carry run_mode='full',\n"
            "  expected_n=5120, observed_n=5120, cardinality_ok=True. backend=numpy.cpu.\n"
            "  elapsed_s ~ 58.9 s/seed.\n"
            "\n"
            "  Per-seed verdicts (off-disk, cited numbers match cell-author exactly within 1e-5):\n"
            "    seed_13: CHAIN_GRADE_MULTI 3/3 gates  fr=0.40 fl=80x  hm_fr=0.60 hm_fl=120x\n"
            "             hm_or=64 cliff=56  decades_adv=5 avg_gr-ref=0.5773\n"
            "    seed_19: CHAIN_GRADE_MULTI 2/3 gates  fr=0.25 fl=50x  hm_fr=0.70 hm_fl=140x\n"
            "             hm_or=64 cliff=58  decades_adv=5 avg_gr-ref=0.5891\n"
            "    seed_23: CHAIN_GRADE_MULTI 3/3 gates  fr=0.35 fl=70x  hm_fr=0.60 hm_fl=120x\n"
            "             hm_or=64 cliff=59  decades_adv=5 avg_gr-ref=0.5867\n"
            "    seed_29: CHAIN_GRADE_MULTI 3/3 gates  fr=0.45 fl=90x  hm_fr=0.70 hm_fl=140x\n"
            "             hm_or=64 cliff=57  decades_adv=5 avg_gr-ref=0.5906\n"
            "    seed_7 : UNKNOWN/IMPORT_CRASH (ModuleNotFoundError on remote; honest infra failure;\n"
            "             excluded from AGG; effective N=4 not 5).\n"
            "\n"
            "  CROSS-SEED AGG (4-seed; per documented gate-doc in v4_5seed_chain_grade_gate_doc):\n"
            "    [A] GRACEFUL chain-grade:\n"
            "        seeds_met=3/5 (need>=3); members={13, 23, 29}\n"
            "        mean_floor_ret=0.362 (need>=0.30; threshold cleared by 0.062)\n"
            "        mean_decades=5.0 (need>=3; threshold cleared by 2.0)\n"
            "        -- PASS\n"
            "    [B] HARDMAX chain-grade:\n"
            "        seeds_met=4/5 (need>=3); members={13, 19, 23, 29}\n"
            "        mean_floor_ret=0.650 (need>=0.50; threshold cleared by 0.150)\n"
            "        mean_floor_lift=130.0x (need>=10x; threshold cleared by 120x)\n"
            "        mean_over_ref_pts=64.0 (need>=25; threshold cleared by 39)\n"
            "        -- PASS\n"
            "    [C] REFCLIFF chain-grade:\n"
            "        seeds_met=4/5 (need>=3); members={13, 19, 23, 29}\n"
            "        mean_cliff_pts=57.5 (need>=10; threshold cleared by 47.5)\n"
            "        -- PASS\n"
            "    TOTAL: 3/3 (cleanly above the MULTI threshold of >=2 gates by AGG)\n"
            "\n"
            "  Per-seed CARDINALITY (META_RULE_H):\n"
            "    expected_n=5120 / observed_n=5120 on all 4 seeds; cardinality_ok=True per seed.\n"
            "  Per-seed ARMS-DIVERGE (META_RULE_AF):\n"
            "    n_pts_arms_diverge=64/64 on all 4 seeds (independent recompute confirms; any pair\n"
            "    in (BAYES, HARDMAX, REFERENCE) differs by >1e-9 at every phase point).\n"
            "  Per-seed PATHOLOGY CHECKS:\n"
            "    arms_identical_pathology=False on all 4 seeds.\n"
            "    random_arm_pathology=False on all 4 seeds; random_arm_pathology_pts=0.\n"
            "\n"
            "REFINED HARDMAX MECHANISM CHARACTERIZATION (decade-binned 4-seed average):\n"
            "  D0 (alpha<0.01, n=1 phase pt):  GR=0.875  HM=0.875   HM-GR=+0.000 (both saturating)\n"
            "  D1 (0.01<=a<0.1, n=9):          GR=0.867  HM=0.887   HM-GR=+0.021 (5/9 HM>GR)\n"
            "  D2 (0.1<=a<1,    n=28):         GR=0.763  HM=0.830   HM-GR=+0.067 (22/28 HM>GR)\n"
            "  D3 (1<=a<10,     n=25):         GR=0.647  HM=0.773   HM-GR=+0.127 (23/25 HM>GR)\n"
            "  D4 (a>=10,       n=1):          GR=0.362  HM=0.650   HM-GR=+0.288 (1/1  HM>GR)\n"
            "  HARDMAX advantage GROWS monotonically with alpha (capacity-stress regime).\n"
            "  This refines the cell-author 'noise-suppressing at FLOOR' framing: the 'FLOOR' the\n"
            "  cell-author cites is the alpha=19.5 floor-of-mechanism (D4, where both arms are\n"
            "  capacity-stressed), NOT the alpha<0.01 storage-floor (D0, where both are at-ceiling).\n"
            "  Mechanism: per-class centroid (mean of K exemplars) is a 1/sqrt(K) lower-variance\n"
            "  prototype estimator than any single exemplar; under capacity stress (alpha >= 1) the\n"
            "  Bayes-LSE smoothing inherits per-exemplar noise that the centroid's K-sample averaging\n"
            "  dampens. See META_RULE_AR for the methodology rule extracted from this finding.\n"
            "\n"
            "WHY CHAIN_GRADE PROMOTION (Skunkworks-cert-owner; multi-cause):\n"
            "  (a) All 3 AGG gates met simultaneously (cleanly above the 2-of-3 MULTI threshold).\n"
            "  (b) HARDMAX is 4-of-4 across all seeds with substantial margins above every sub-\n"
            "      threshold (mean 130x lift; 64/64 over_ref dominance; 0.65 floor retention).\n"
            "  (c) GRACEFUL is 3-of-4 with cross-seed mean floor_retention=0.362 above 0.30 threshold;\n"
            "      seed_19's miss at 0.250 is just-below (single D4 phase point at alpha=19.5;\n"
            "      honest variance not pathology).\n"
            "  (d) REFCLIFF is 4-of-4 with cliff_pts_mean=57.5 (load-bearing well above 10).\n"
            "  (e) cardinality_ok, arms_diverge, no pathology, no by-construction saturation.\n"
            "  (f) Discriminator survives scale (Fix #26): n_q=20 x 64 combos x 4 arms x 4 seeds\n"
            "      = 5120 records per seed; fires at 64/64 phase points per seed.\n"
            "  (g) seed_7 IMPORT_CRASH is honest infra failure (commit fdf4c714 _core.py not on\n"
            "      remote at run-time); not methodological problem with the cell.\n"
            "  (h) 4-of-5 effective replication is conservative; the pre-reg's >=3/5 threshold is\n"
            "      cleared.\n"
            "\n"
            "WHY NOT MM/HF (honest-downward considered):\n"
            "  - BIAS-Q saturation NOT triggered. HARDMAX D2/D3 means 0.83/0.77, GRACEFUL D2/D3\n"
            "    means 0.74/0.65 -- substantial spread; not metric-cap artifact.\n"
            "  - Effective N=4 not 5; pre-reg requires >=3/5 met. We have 3/5 on GRACEFUL,\n"
            "    4/5 on HARDMAX + REFCLIFF. Even if we treat seed_7 as 'fail' we still meet\n"
            "    every gate by 3-of-5 minimum.\n"
            "  - Cross-seed spread: HARDMAX 4/4, REFCLIFF 4/4 (tight); GRACEFUL spread {0.40,\n"
            "    0.25, 0.35, 0.45} is wider on the weakest gate but still 3-of-4 above threshold.\n"
            "  - Prior cells at v3 (5/5 MB) characterized 3-arm mechanism; v4 ADDS the HARDMAX\n"
            "    centroid mechanism-substitution per Skunkworks 2x-drill Option B and obtains\n"
            "    chain-grade promotion. v4 is a SEPARATE atom from v3, not a supersession.\n"
            "\n"
            "_llm_forward_calls_at_inference = 0.\n"
            "substrate_only_decode_gate: PASS (no LLM in loop).\n"
            "\n"
            "ARMS RUN (4-arm mechanism-class composite):\n"
            "  ARM_BAYES_GRACEFUL: per-exemplar log-likelihood logsumexp under a Bayes posterior\n"
            "    over centroid means; graceful at high alpha but inherits per-exemplar variance.\n"
            "  ARM_HARD_MAX: cosine-nearest centroid argmax (deterministic; no log-likelihood);\n"
            "    centroid pre-averages K exemplars per class (variance reduction); NOISE-SUPPRESSING\n"
            "    under capacity stress. This is the cell-author's mechanism DISCOVERY.\n"
            "  ARM_REFERENCE: prior reference (capacity-proxy baseline); produces cliff vs the\n"
            "    BAYES/HARDMAX arms (load-bearing for the REFCLIFF gate).\n"
            "  ARM_UNIFORM_RANDOM: uniform chance floor; sanity check (random_arm_pathology=False\n"
            "    confirms random arm does not pathologically lift).\n"
            "\n"
            "META_RULE COMPLIANCE:\n"
            "  META_RULE_H cardinality: PASS on all 4 seeds (5120=5120).\n"
            "  META_RULE_AF arms-must-differ: PASS on all 4 seeds (n_pts_arms_diverge=64/64).\n"
            "  META_RULE_AH atomic metrics: per-arm per-seed per-phase-point recorded.\n"
            "  META_RULE_K discriminator-fires: discriminator (GR vs HM vs REF) fires at 64/64\n"
            "    phase points per seed; mechanism arms separate from random arm + each other.\n"
            "  META_RULE_L band: GR / HM / REF span [0.36, 0.83] across decades (no saturation).\n"
            "  Fix #28 per-arm reads: per-arm acc-mean read independently per seed per phase pt.\n"
            "  Fix #26 discriminator-survives-scale: PASS (full-N M=20 queries discriminator\n"
            "    fires at 64/64 phase points).\n"
            "  BIAS-13/14/15 contamination/regime/mismatch: pre-reg explicit at FLOOR_THRESH=0.30\n"
            "    floor_retention; discriminator fires across 64 phase points x 4 seeds = 256\n"
            "    independent observations.\n"
            "  BIAS-M production-scale calibration: full-N runs at expected_n=5120/seed.\n"
            "  BIAS-N verify-referent-verdict-field: spawn-prompt cited 'seed_13 3/3 gates'; on disk\n"
            "    seed_13 has n_chain_grade_gates_met=3. Spawn cited seed_19 IMPORT_CRASH possible;\n"
            "    on disk seed_19=CHAIN_GRADE_MULTI 2/3 (GR=False), seed_7=IMPORT_CRASH. Spawn-prompt\n"
            "    minor mismatch (seed_19 vs seed_7 swap) not load-bearing for cert outcome.\n"
            "  BIAS-S band-calibration regime: alpha spans 5 decades {0.006..19.5}; FLOOR at\n"
            "    alpha>=10 has 1 phase point per seed (D4); D2-D3 are most-populated (28+25 pts).\n"
        ),
        kind=AtomKind.CHAIN_GRADE_PHASE_CHARACTERIZATION,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.MATH,
        algebra=None,
        metadata={
            "provenance_quality": "CERT_CHAIN_GRADE",
            "cert_status": "chain_grade",
            "cert_class": "pre_reg_pass",
            "cell_anchor": "substrate_schema_exemplar_bayes_capacity_stress_v4",
            "cell_commit": CELL_COMMIT,
            "metrics_paths": [METRICS_SEED_13, METRICS_SEED_19, METRICS_SEED_23, METRICS_SEED_29],
            "metrics_path_excluded_import_crash": METRICS_SEED_7,
            "ruling_note": RULING_NOTE,
            "verified_off_data": True,
            "run_mode": "full",
            "n_seeds_effective": 4,
            "n_seeds_attempted": 5,
            "seeds_passing": [13, 19, 23, 29],
            "seed_import_crash": 7,
            "expected_n_per_seed": 5120,
            "observed_n_per_seed": 5120,
            "cardinality_ok_all_seeds": True,
            "backend": "numpy.cpu",
            "n_combos_total": 64,
            "n_ex_per_class_sweep": [10, 50, 100, 200],
            "n_classes_sweep": [10, 50, 100, 200],
            "N_sweep": [2048, 4096, 8192, 16384],
            "n_q_per_combo": 20,
            "alpha_range": [0.006103515625, 19.53125],
            "alpha_decades_observed": 5,
            "arms": ["ARM_BAYES_GRACEFUL", "ARM_HARD_MAX", "ARM_REFERENCE", "ARM_UNIFORM_RANDOM"],
            "agg_gates_met": 3,
            "agg_gate_a_graceful_met": True,
            "agg_gate_b_hardmax_met": True,
            "agg_gate_c_refcliff_met": True,
            "agg_gate_a_graceful_seeds_met_count": 3,
            "agg_gate_b_hardmax_seeds_met_count": 4,
            "agg_gate_c_refcliff_seeds_met_count": 4,
            "agg_gate_a_graceful_seeds_met_members": [13, 23, 29],
            "agg_gate_b_hardmax_seeds_met_members": [13, 19, 23, 29],
            "agg_gate_c_refcliff_seeds_met_members": [13, 19, 23, 29],
            "agg_mean_floor_retention": 0.3625,
            "agg_mean_floor_lift": 72.5,
            "agg_mean_hm_floor_retention": 0.650,
            "agg_mean_hm_floor_lift": 130.0,
            "agg_mean_hm_over_ref_pts": 64.0,
            "agg_mean_cliff_pts": 57.5,
            "per_seed_gates_met": {
                "seed_13": 3, "seed_19": 2, "seed_23": 3, "seed_29": 3,
            },
            "per_seed_floor_retention": {
                "seed_13": 0.400, "seed_19": 0.250, "seed_23": 0.350, "seed_29": 0.450,
            },
            "per_seed_floor_lift": {
                "seed_13": 80.0, "seed_19": 50.0, "seed_23": 70.0, "seed_29": 90.0,
            },
            "per_seed_hardmax_floor_retention": {
                "seed_13": 0.600, "seed_19": 0.700, "seed_23": 0.600, "seed_29": 0.700,
            },
            "per_seed_hardmax_floor_lift": {
                "seed_13": 120.0, "seed_19": 140.0, "seed_23": 120.0, "seed_29": 140.0,
            },
            "per_seed_hardmax_over_ref_pts": {
                "seed_13": 64, "seed_19": 64, "seed_23": 64, "seed_29": 64,
            },
            "per_seed_reference_cliff_pts": {
                "seed_13": 56, "seed_19": 58, "seed_23": 59, "seed_29": 57,
            },
            "per_seed_arms_diverge": {
                "seed_13": 64, "seed_19": 64, "seed_23": 64, "seed_29": 64,
            },
            "per_seed_avg_graceful_minus_reference": {
                "seed_13": 0.5773, "seed_19": 0.5891, "seed_23": 0.5867, "seed_29": 0.5906,
            },
            "hm_minus_gr_decade_means_4seed_recomputed": {
                "D0": 0.000, "D1": 0.021, "D2": 0.067, "D3": 0.127, "D4": 0.288,
            },
            "hardmax_advantage_grows_with_alpha": True,
            "cell_author_floor_framing_refined": (
                "cell-author cited 'NOISE-SUPPRESSING at FLOOR'; off-disk recompute clarifies the "
                "'FLOOR' is the alpha=19.5 mechanism-FLOOR (D4) where both arms are capacity-stressed, "
                "not the alpha<0.01 storage-floor; HARDMAX advantage grows monotonically with alpha"
            ),
            "META_RULE_H_cardinality_ok": True,
            "META_RULE_AF_arms_diverge_all_pts_all_seeds": True,
            "META_RULE_AH_atomic_metrics": True,
            "META_RULE_K_discriminator_fires": True,
            "META_RULE_L_band_no_saturation": True,
            "Fix_26_discriminator_survives_scale_PASS": True,
            "BIAS_Q_saturation_NOT_triggered": True,
            "honest_downward_considered_not_triggered": True,
            "load_bearing_finding_1": "agg_3of3_gates_passing_chain_grade_multi_phase_characterization",
            "load_bearing_finding_2": "hardmax_centroid_argmax_dominates_bayes_lse_at_capacity_stress_alpha_gte_1",
            "load_bearing_finding_3": "reference_arm_cliff_observable_at_57p5_of_64_phase_pts_mean",
            "load_bearing_finding_4": "graceful_degradation_5_decades_with_chance_lift_all_seeds",
            "extends_or_supersedes_prior": (
                "extends_v3_5seed_MB_with_v4_HARDMAX_arm_primitive_substitution_per_skunkworks_2x_drill_option_B"
            ),
            "promotion_rationale_summary": (
                "3of3_AGG_gates_met_HM_4of4_REF_4of4_GR_3of4_with_seed_19_just_below_threshold_BIAS_Q_not_triggered_"
                "Fix_26_satisfied_cardinality_ok_arms_diverge_64of64_no_pathology_seed_7_import_crash_honest_infra"
            ),
            "feeds_META_RULE_AR_centroid_noise_suppression": True,
            "scope_observed": (
                "full_4_seeds_N_sweep_2048_to_16384_n_ex_per_class_10_to_200_n_classes_10_to_200_alpha_decades_5_"
                "n_q_20_per_combo_64_combos_per_seed_full_5120_records_per_seed"
            ),
            "scope_not_claimed": (
                "5_of_5_seeds_OR_alpha_gt_20_extrapolation_OR_other_substrate_dimensions_d_eff_or_clock_rate_"
                "OR_natural_data_only_synthetic_class_clusters"
            ),
            "promotion_path_future": (
                "rerun_seed_7_post_orchestrator_fix_to_confirm_5of5_replication_OR_extend_alpha_to_50_to_test_"
                "HM_advantage_growth_OR_apply_centroid_primitive_to_other_capacity_stress_cells"
            ),
            "zero_llm_calls_at_inference": True,
            "_llm_forward_calls_at_inference": 0,
            "substrate_only_decode_gate": "PASS",
            "atomized_by": ATOMIZED_BY,
        },
    )


# ============================================================================
# ATOM 2 -- META_RULE_AR centroid_argmax_noise_suppression_at_capacity_stress
# ============================================================================

def build_atom2_meta_rule_ar_centroid_noise_suppression() -> Atom:
    return Atom(
        id=(
            "RULE_centroid_argmax_is_noise_suppressing_prototype_primitive_under_capacity_stress_"
            "advantage_grows_monotonic_with_alpha_K_exemplar_mean_is_1_over_sqrt_K_lower_variance_"
            "estimator_than_per_exemplar_bayes_lse_witnessed_4seed_capacity_stress_v4_HM_minus_GR_"
            "D0_0p000_D1_0p021_D2_0p067_D3_0p127_D4_0p288_META_RULE_AR_2026-06-30"
        ),
        name=(
            "META_RULE_AR: per-class CENTROID argmax (cosine-nearest-MEAN) is a noise-suppressing "
            "prototype primitive whose advantage over Bayes-LSE GROWS MONOTONICALLY with capacity "
            "stress (alpha = K_total/N); the centroid's K-exemplar average is a 1/sqrt(K) lower-"
            "variance prototype estimator than any single exemplar, so under capacity stress where "
            "Bayes-LSE inherits per-exemplar variance the centroid argmax dominates."
        ),
        description=(
            "META_RULE_AR: HARDMAX centroid argmax is a NOISE-SUPPRESSING PROTOTYPE PRIMITIVE.\n"
            "\n"
            "OBSERVED in capacity_stress_v4 4-seed FULL (witnesses seeds 13, 19, 23, 29):\n"
            "  Decade-binned 4-seed-averaged HM-GR delta (re-derived off-disk):\n"
            "    D0 (alpha<0.01,   n=1):   HM-GR = +0.000   (both at near-ceiling)\n"
            "    D1 (0.01<=a<0.1,  n=9):   HM-GR = +0.021   (5/9  pts HM>GR)\n"
            "    D2 (0.1<=a<1,     n=28):  HM-GR = +0.067   (22/28 pts HM>GR)\n"
            "    D3 (1<=a<10,      n=25):  HM-GR = +0.127   (23/25 pts HM>GR)\n"
            "    D4 (a>=10,        n=1):   HM-GR = +0.288   (1/1   pts HM>GR)\n"
            "  HM advantage GROWS monotonically with alpha (capacity stress); at the alpha=19.5\n"
            "  mechanism-FLOOR the advantage is ~0.29 absolute accuracy.\n"
            "\n"
            "MECHANISM INTUITION:\n"
            "  - Per-class centroid is the MEAN of K exemplars per class. Under Gaussian-like\n"
            "    per-exemplar noise model, the centroid is a 1/sqrt(K) lower-variance estimator\n"
            "    of the true class prototype than any single exemplar.\n"
            "  - Bayes-LSE log-likelihood sum over per-exemplar samples inherits the per-exemplar\n"
            "    variance fully (each term in the logsumexp is per-exemplar).\n"
            "  - When K is large (or equivalently alpha is large since alpha = K_total/N), the\n"
            "    centroid's averaging dominates the Bayes-LSE smoothing, especially in regimes\n"
            "    where the substrate is capacity-stressed and the per-exemplar bindings have\n"
            "    higher crosstalk variance.\n"
            "\n"
            "DISCIPLINE (load-bearing for future capacity-stress / classification cells):\n"
            "  Any cell with K exemplars per class and a posterior-over-prototype readout should\n"
            "  include a CENTROID_ARGMAX baseline arm. If the cell-author's hypothesis is 'Bayes-\n"
            "  LSE smoothing is graceful at high alpha' then the cell MUST include CENTROID_ARGMAX\n"
            "  as a competitor; if CENTROID dominates by >0.05 absolute accuracy at alpha >= 1, the\n"
            "  cell's framing must include the centroid-noise-suppression mechanism in its claim.\n"
            "\n"
            "FALSIFIES THE NAIVE READING: 'Bayes-LSE smoothing under graceful degradation is the\n"
            "  optimal high-alpha readout strategy.'\n"
            "  Falsifies to: 'Bayes-LSE smoothing is graceful (decades of chance-lift) but CENTROID\n"
            "  argmax is BETTER under capacity stress because it averages-down per-exemplar variance\n"
            "  before the argmax decision.'\n"
            "\n"
            "REFINES THE CELL-AUTHOR's FRAMING:\n"
            "  Cell-author cited 'HARDMAX noise-suppressing AT FLOOR' as a discovery. Off-disk\n"
            "  recompute clarifies: the FLOOR cited is the alpha=19.5 mechanism-FLOOR (D4) where\n"
            "  both arms are capacity-stressed, NOT the alpha<0.01 storage-floor (D0) where both\n"
            "  arms are at-ceiling. The HARDMAX advantage GROWS with capacity stress; at the\n"
            "  storage-floor (low alpha) HM and GR are indistinguishable.\n"
            "\n"
            "RELATION TO OTHER META RULES:\n"
            "  Companion to META_RULE_AN (cone-collapse-formula-calibrated-at-N): both rules\n"
            "    capture that substrate readout strategies are regime-conditional and must be\n"
            "    calibrated to the operating-point alpha or K_total/N.\n"
            "  Companion to META_RULE_AP (chain-grade-pareto-gate-needs-recency-floor): both\n"
            "    rules say 'add a stricter alternative comparison to your gate'; here the\n"
            "    alternative is the centroid argmax baseline.\n"
            "  Companion to META_RULE_AF (arms-must-differ): the centroid argmax is a distinct\n"
            "    MECHANISM arm (primitive substitution, not hyperparameter sweep) per Skunkworks\n"
            "    2x-drill Option B.\n"
            "\n"
            "VERIFIED-OFF-DATA EVIDENCE POINTERS:\n"
            "  data/exp_substrate_schema_exemplar_bayes_capacity_stress_v4_seed_{13,19,23,29}/\n"
            "    metrics.json (4 files; summary_per_phase_point[*].ARM_HARD_MAX_acc_mean and\n"
            "    ARM_BAYES_GRACEFUL_acc_mean per decade are the load-bearing measurements)\n"
            "\n"
            "FIRST ATOMIZED 2026-06-30 by Skunkworks capacity_stress_v4 4-seed landed-VET\n"
            "  (.venv off-data recompute via tools/atomize_skunkworks_capacity_stress_v4_4seed_CG_\n"
            "  2026-06-30.py).\n"
            "\n"
            "NAMING NOTE: META_RULE_AQ was used for an unrelated rule on multi-primitive composition\n"
            "  + state-tracker (brain-grounded composition, 2026-06-28). META_RULE_AR is the next\n"
            "  free monotonic slot.\n"
        ),
        kind=AtomKind.METHODOLOGY_RULE,
        tier=Tier.TIER_METHODOLOGY,
        corpus=Corpus.META,
        algebra=None,
        metadata={
            "provenance_quality": "META_RULE",
            "cert_status": "discipline_meta",
            "cert_class": "discipline_meta",
            "rule_id": "META_RULE_AR",
            "rule_topic": (
                "centroid_argmax_is_noise_suppressing_prototype_primitive_under_capacity_stress"
            ),
            "rule_layer": "readout_primitive_selection_under_capacity_stress",
            "evidence_atoms": [
                (
                    "T3/EXP_substrate_schema_exemplar_bayes_capacity_stress_v4_4seed_AGG_CHAIN_GRADE_MULTI_"
                    "3of3_gates_GRACEFUL_3of5_HARDMAX_4of5_REFCLIFF_4of5_floor_ret_mean_0p362_HM_floor_ret_"
                    "mean_0p650_HM_floor_lift_mean_130x_HM_over_ref_64_64pts_RF_cliff_57p5_avg_gr_minus_ref_"
                    "0p586_seed_13_3of3_seed_19_2of3_GR_fail_floor_0p25_seed_23_3of3_seed_29_3of3_seed_7_"
                    "IMPORT_CRASH_effective_N_4_phase_characterization_chain_grade_2026-06-30"
                ),
            ],
            "hm_minus_gr_decade_means_4seed": {
                "D0": 0.000, "D1": 0.021, "D2": 0.067, "D3": 0.127, "D4": 0.288,
            },
            "advantage_grows_monotonically_with_alpha": True,
            "recommended_baseline_arm": "CENTROID_ARGMAX",
            "trigger_threshold_for_inclusion": (
                "any_cell_with_K_exemplars_per_class_AND_posterior_over_prototype_readout"
            ),
            "framing_must_update_threshold": (
                "centroid_dominates_by_gt_0p05_absolute_accuracy_at_alpha_gte_1"
            ),
            "companion_META_RULE_AN_regime_conditional_calibration": True,
            "companion_META_RULE_AP_gate_pair_with_stricter_alternative": True,
            "companion_META_RULE_AF_mechanism_class_distinct_arm": True,
            "naming_note": (
                "META_RULE_AQ_taken_by_brain_grounded_composition_state_tracker_rule_2026-06-28_AR_is_next_free"
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
    print(f"[capacity_stress_v4_vet] mode={mode}")

    store = PartitionedStore(STORE_ROOT)

    pre_cert_n = _cert_count(store)
    print(f"[capacity_stress_v4_vet] PRE cert_n={pre_cert_n}")
    assert pre_cert_n == 632, f"PRE cert_n {pre_cert_n} != 632 expected"

    atom1 = build_atom1_capacity_stress_v4_chain_grade()
    atom2 = build_atom2_meta_rule_ar_centroid_noise_suppression()
    atoms = [atom1, atom2]

    for i, a in enumerate(atoms, 1):
        print(f"[capacity_stress_v4_vet] Atom {i}: id_head={str(a.id)[:90]}... corpus={a.corpus.name} tier={a.tier.name} kind={a.kind.name}")

    if not apply:
        print("[capacity_stress_v4_vet] DRY mode -- no Store / ledger writes. Re-run with --apply.")
        return 0

    # ============================================================
    # APPLY: Atom 1 (chain-grade delta=+1)
    # ============================================================
    expected_n_after_atom1 = pre_cert_n + 1   # 632 -> 633 (chain_grade)

    print("[capacity_stress_v4_vet] Writing Atom 1 (capacity_stress_v4 4-seed CHAIN_GRADE_MULTI)...")
    store.add_atom(atom1)
    post_n_1 = _cert_count(store)
    assert post_n_1 == expected_n_after_atom1, (
        f"After Atom 1: cert_n={post_n_1} != {expected_n_after_atom1}"
    )
    append_cert_ledger_row(
        {
            "op": "cert_ruling",
            "atom_id": f"math::{atom1.id}",
            "cert_status": "chain_grade",
            "cert_class": "pre_reg_pass",
            "verified_off_data": True,
            "atomized_by": ATOMIZED_BY,
            "cell_commit": CELL_COMMIT,
            "verdict": "CHAIN_GRADE_MULTI_4SEED_3OF3_AGG_GATES_MET",
            "cert_increment_delta": 1,
            "cv": None,
            "referent_pointer": {
                "notes_path": RULING_NOTE,
                "metrics_path": METRICS_SEED_13,
                "atom_qualified_id": f"math::{atom1.id}",
            },
            "supersedes": None,
            "note": (
                "capacity_stress_v4_4seed_CG_MULTI_3of3_AGG_gates_GR_3of5_HM_4of5_RF_4of5_HM_4of4_"
                "REF_4of4_GR_3of4_seed_19_just_below_threshold_floor_ret_0p25_BIAS_Q_not_triggered_"
                "Fix_26_satisfied_cardinality_ok_arms_diverge_64of64_no_pathology_seed_7_import_crash_"
                "honest_infra_failure_effective_N_4"
            ),
        },
        expected_cert_n_pre=pre_cert_n,
        expected_cert_n_post=expected_n_after_atom1,
    )

    # ============================================================
    # APPLY: Atom 2 (META_RULE_AR delta=0)
    # ============================================================
    expected_n_after_atom2 = expected_n_after_atom1   # META rule delta=0

    print("[capacity_stress_v4_vet] Writing Atom 2 (META_RULE_AR centroid noise-suppression)...")
    store.add_atom(atom2)
    post_n_2 = _cert_count(store)
    assert post_n_2 == expected_n_after_atom2, (
        f"After Atom 2: cert_n={post_n_2} != {expected_n_after_atom2}"
    )
    append_cert_ledger_row(
        {
            "op": "cert_ruling",
            "atom_id": f"meta::{atom2.id}",
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
                "metrics_path": "n/a-meta-rule-derived-from-capacity_stress_v4_Atom1-decade-binned-HM-minus-GR",
                "atom_qualified_id": f"meta::{atom2.id}",
            },
            "supersedes": None,
            "note": (
                "META_RULE_AR_centroid_argmax_noise_suppressing_prototype_primitive_advantage_grows_"
                "monotonic_with_alpha_HM_minus_GR_D0_0p000_D1_0p021_D2_0p067_D3_0p127_D4_0p288_witnessed_"
                "capacity_stress_v4_4seed_aliased_after_AQ_taken_by_brain_composition_rule"
            ),
        },
        expected_cert_n_pre=pre_cert_n,
        expected_cert_n_post=expected_n_after_atom2,
    )

    final_cert_n = _cert_count(store)
    print(
        f"[capacity_stress_v4_vet] FINAL cert_n={final_cert_n} "
        f"(pre={pre_cert_n}, delta=+1; 1 CG + 1 META)"
    )
    assert final_cert_n == expected_n_after_atom2

    # Round-trip verify: each atom should reload
    store_verify = PartitionedStore(STORE_ROOT)
    for a in atoms:
        match = [x for x in store_verify.all_atoms() if x.id == a.id]
        assert len(match) == 1, f"Round-trip FAIL for atom id={a.id} (found {len(match)})"
        assert (match[0].metadata or {}).get("atomized_by") == ATOMIZED_BY
        print(f"[capacity_stress_v4_vet] Round-trip OK: {a.id[:60]}...")

    print(
        "[capacity_stress_v4_vet] APPLY OK -- 2 atoms landed; ledger 2 rows appended; "
        f"cert_n {pre_cert_n} -> {final_cert_n} (+1)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
