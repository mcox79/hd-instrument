"""Atomize: Skunkworks 5-cell batch 8 landed-VET (2026-06-27).

5 metrics.json verified off-data; 5 atoms (one per cell).

Cells (per-arm verify):
  [1] typed_multibank_K128_adversarial_v1                    -> HONEST_NEGATIVE_MECHANISM_FAILS 0
  [2] gap3_cls_two_tier_BCM_slow_replay_v1                   -> HONEST_NEGATIVE_BCM_AT_CHANCE_PLUS_REGIME_DRIFT 0
  [3] kb_coarse_grain_at_promotion_v3_self_contained         -> HONEST_NEGATIVE_INFRA_DEP_MEMORY_DIR_NOT_IN_REPO 0
  [4] edge_importance_retrieval_trace_x_ultrametric_v3p1_tuned -> HONEST_NEGATIVE_ULTRAMETRIC_GEOMETRY_MISMATCH 0
  [5] phase_diagram_capacity_codebook_separated_envelope_v1  -> MEASURED_MECHANISM_MECH_ARM_PARTIAL_OOM_CARDINALITY 0

Net: CERT N unchanged (no chain-grade); ledger rows +5.

VERIFY-OFF-DATA basis (.venv recompute 2026-06-27 from local metrics.json):

CELL 1 typed_multibank_K128_adversarial_v1:
  cardinality 9/9 OK. Per-arm 3-seed means:
    ARM_UNTYPED_BASELINE_ADVERSARIAL: recall=[0.9977,0.9978,0.9978] mean=0.9978 (saturated; route_acc=1.0)
    ARM_TYPED_ROUTING_MATCHED: recall=[0.4451,0.4210,0.4523] mean=0.4395 cv=0.0305 typed_route_acc mean=0.4401
    ARM_TYPED_ROUTING_ADVERSARIAL_PROBE: refuse_rate=[0.2003,0.1129,0.0957] mean=0.1363 cv=0.336
  Cell-author HARD_FAIL by_construction_saturation IS REAL but UNDER-claims: typed_lift=-0.5583
  (typed arm 56pp WORSE than baseline). Refuse mean 0.1363 << HP_refuse_min=0.85 by 71pp.
  This is NOT just baseline-too-easy: BOTH the typed-routing-lift AND the refuse-gate FAIL.
  The typed mechanism at OVERLAP=0.40 N_BANKS=128 actively HURTS recall and does not refuse
  adversarial features. Tier HONEST_NEGATIVE_MECHANISM_FAILS (not by_construction).

CELL 2 gap3_cls_two_tier_BCM_slow_replay_v1:
  cardinality 12/12 OK. Per-arm 3-seed means:
    ARM_BASELINE_SINGLE_W: heldout_acc=[1.0,1.0,1.0] mean=1.0 cone_cosine=1.0
    ARM_TWO_TIER_HEBBIAN_SLOW: heldout_acc=[1.0,1.0,1.0] mean=1.0 cone_cosine=0.458 entropy_delta=1.609
    ARM_TWO_TIER_BCM_SLOW: heldout_acc=[0.2,0.2,0.2] mean=0.2 (CHANCE 1/N_CAT=5) cone=0.0
    ARM_TWO_TIER_BCM_GENERATIVE_REPLAY: heldout_acc=[0.2,0.2,0.2] mean=0.2 (CHANCE) cone=0.0
  TWO honest-negative findings stacked:
    (a) baseline=1.0 violates cross-cell rail HP_BASELINE_MAX=0.5 -> regime too easy
    (b) BCM arms at CHANCE in addition; mechanism actively FAILS to learn (vs Hebbian which holds)
  lift_over_baseline=-0.8 and lift_over_hebbian=-0.8 for both BCM arms.
  Tier HONEST_NEGATIVE_BCM_AT_CHANCE_PLUS_REGIME_DRIFT.

CELL 3 kb_coarse_grain_at_promotion_v3_self_contained:
  cardinality_ok=False; n_ud_in_sample_min=0 < HP=10 (RC-1 invariant); mechanism never exercised.
  Root: inline_kb manifest shows per_class memory n_files=0 n_chunks=0 BUT chunk_classes_ingested
  includes 'memory'. The self-contained build pointed at <repo>/memory/ which DOES NOT EXIST in
  hd-instrument repo. The MEMORY.md + memory/ files live in ~/.claude/projects/d--AI/memory/.
  All 3 seeds error: 'USER_DIRECTIVE_REFERENT_MISSING: zero chunk_memory atoms in inline KB'.
  Sister to batch 7 cell 4 (kb_coarse_grain_v2 INFRA_DEP); v3 self-contained rescue STILL infra-dep.
  Tier HONEST_NEGATIVE_INFRA_DEP_MEMORY_DIR_NOT_IN_REPO. Rescue v4: pull memory from claude profile
  OR detect UD label via content heuristic (not source-class).

CELL 4 edge_importance_retrieval_trace_x_ultrametric_coreness_v3p1_ULTRA_tuned:
  All 3 seeds halted at seed=7 setup-time: META_RULE_K coreness-fires FAIL: coreness_atoms=0
  at ULTRA_COS=0.7 ULTRA_MIN_SIZE=3 with N=512 M_OLD=600 M_RECENT=400. arms_count=[] all seeds.
  v3 had same issue at (0.85, 5); v3.1 still degenerate at looser (0.7, 3).
  Synthetic sigma=0.02 selftest passed; REAL atom-cluster geometry doesn't cluster that tight.
  Tier HONEST_NEGATIVE_ULTRAMETRIC_CLUSTER_GEOMETRY_MISMATCH. Pivot: drop ULTRA composition;
  D1 alt cell (exp_edge_importance_v3_D1_alternative_discriminators_v1) already showed
  TRACE-only D1_AUC=1.000. ULTRA composition not load-bearing for retrieval-trace finding.

CELL 5 phase_diagram_capacity_codebook_separated_envelope_v1:
  cardinality_ok=False (10/69 units). 1 OOM failure (META_RULE_J halted) at
  seed11_armMULTI_BANK_K4_alpha4p0_headroom10x: CUDA OOM (8GB ceiling, 6.8GB allowed).
  ONLY seed=11 MECH arm completed; all KNN_sentinel + BARE_E_R + MULTI_BANK arms NaN.
  All 10 MECH cells rec=1.0 across alpha=[0.5..8.0] x headroom=[10x,2x] grid.
  4 cells EXCEEDED predicted band (alpha=4 pred=[0.75,0.9] obs=1.0; alpha=8 pred=[0.4,0.65] obs=1.0).
  envelope_cells_pass = [alpha0.5_10x, alpha1.0_10x, alpha2.0_10x] (3 of 6 expected at 10x).
  Partial substrate evidence: MECH arm holds rec=1.0 well beyond predicted at THIS regime
  (n=1 seed; needs 2 more seeds + sentinel + multi-bank to be chain-grade).
  Tier MEASURED_MECHANISM_MECH_ARM_PARTIAL (not chain-grade; under-claim per Fix #28).
  Rescue: V_R sweep separated from V_C sweep; memory-frugal multi-bank (smaller K_per_bank).

CERT N change: 0 (5 ledger rows; no chain-grade).

Run:
  .venv/Scripts/python.exe tools/atomize_skunkworks_5cell_batch8_landed_vet_2026-06-27.py           # DRY
  .venv/Scripts/python.exe tools/atomize_skunkworks_5cell_batch8_landed_vet_2026-06-27.py --apply   # WRITE
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(".").resolve()))
from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier
from tools.cert_ledger_writer import (
    append_cert_ledger_row,
    build_honest_negative_row,
)


STORE_ROOT = Path("data/substrate_index")
RULING_NOTE = "notes/skunkworks_landed_vet_5cell_batch8_2026-06-27.md"
CELL_COMMIT = "n/a-2026-06-27-landed-batch8-5cell"
ATOMIZED_BY = "skunkworks_atomize_5cell_batch8_2026-06-27"

METRICS_TYPED_MB = "data/exp_typed_multibank_K128_adversarial_v1/metrics.json"
METRICS_GAP3_BCM = "data/exp_gap3_cls_two_tier_BCM_slow_replay_v1/metrics.json"
METRICS_KB_V3_SC = "data/exp_kb_coarse_grain_at_promotion_v3_self_contained/metrics.json"
METRICS_EDGE_V3P1 = "data/exp_edge_importance_retrieval_trace_x_ultrametric_coreness_v3p1_ULTRA_tuned/metrics.json"
METRICS_PHASE_DIAG = "data/exp_phase_diagram_capacity_codebook_separated_envelope_v1/metrics.json"


# ============================================================================
# ATOM 1 -- typed_multibank K=128 adversarial: HONEST_NEGATIVE_MECHANISM_FAILS
# ============================================================================

def build_atom1_typed_mb_mechanism_fails() -> Atom:
    return Atom(
        id=(
            "T3/EXP_typed_multibank_K128_adversarial_v1_HONEST_NEGATIVE_MECHANISM_"
            "FAILS_typed_routing_arm_recall_0p4395_vs_baseline_0p9978_lift_minus_"
            "0p5583_at_OVERLAP_0p40_N_BANKS_128_K_PER_BANK_64_adversarial_probe_"
            "refuse_rate_0p1363_vs_HP_0p85_miss_71pp_both_rails_fail_not_just_"
            "by_construction_saturation_typed_mechanism_actively_HURTS"
        ),
        name=(
            "typed_multibank K=128 adversarial v1 HONEST_NEGATIVE_MECHANISM_FAILS: "
            "typed_routing recall=0.4395 vs baseline=0.9978 (lift=-0.5583 = 56pp WORSE); "
            "adversarial probe refuse_rate=0.1363 vs HP=0.85 (71pp miss); both rails fail "
            "at OVERLAP=0.40 N_BANKS=128 K_per_bank=64; typed mechanism actively HURTS not "
            "just by-construction-saturation"
        ),
        description=(
            "HONEST_NEGATIVE_MECHANISM_FAILS (cert-neutral; delta=0). Cell-author verdict\n"
            "'by_construction_saturation' is REAL (baseline 0.9978 >= Q_SUSPECT 0.95) but\n"
            "UNDER-claims the finding. The typed-routing mechanism in this regime does NOT\n"
            "just fail to lift past saturated baseline -- it ACTIVELY HURTS recall AND\n"
            "fails the adversarial refuse-gate by 71 percentage points. This is mechanism-\n"
            "falsifying evidence, not regime-too-easy null.\n\n"
            "OFF-DATA RECOMPUTE (Skunkworks 2026-06-27, .venv Python, 3 seeds: 11, 13, 19):\n"
            "  Cardinality: 9/9 units (cardinality_ok=True; META_RULE_H OK).\n"
            "  Per-arm 3-seed evidence:\n"
            "    ARM_UNTYPED_BASELINE_ADVERSARIAL:\n"
            "      recall per seed: [0.9977, 0.9978, 0.9978]  mean=0.9978  cv=0.0000\n"
            "      route_acc per seed: [1.0, 1.0, 1.0]\n"
            "    ARM_TYPED_ROUTING_MATCHED:\n"
            "      recall per seed: [0.4451, 0.4210, 0.4523]  mean=0.4395  cv=0.0305\n"
            "      typed_route_acc per seed: [0.4453, 0.4219, 0.4531]  mean=0.4401\n"
            "    ARM_TYPED_ROUTING_ADVERSARIAL_PROBE:\n"
            "      refuse_rate per seed: [0.2003, 0.1129, 0.0957]  mean=0.1363  cv=0.336\n"
            "      wrong_rate per seed:  [0.7997, 0.8871, 0.9043]  mean=0.8637\n\n"
            "TWO RAILS FAIL (mechanism-falsifying, not regime-null):\n"
            "  (1) TYPED LIFT RAIL: typed_lift_over_baseline = -0.5583 (typed arm 56pp\n"
            "      WORSE than baseline); HP_typed_lift>=0.10 missed by 65pp.\n"
            "  (2) REFUSE GATE RAIL: refuse_rate_mean = 0.1363 vs HP_refuse_rate_min=0.85\n"
            "      missed by 71pp. Adversarial features ARE routing to wrong bins at 86%.\n"
            "  Both arms are PROPERLY EXERCISED at full 3-seed cardinality; the mechanism\n"
            "  produces real (negative) signal, not a vacuous/by-construction null.\n\n"
            "WHY HONEST_NEGATIVE_MECHANISM_FAILS NOT BY_CONSTRUCTION_SATURATION:\n"
            "  By-construction-saturation means 'baseline is so easy mechanism CAN'T\n"
            "  differentiate from above'. That partly applies (baseline=0.998), but the\n"
            "  typed arm comes in at 0.44 not 0.99 -- which is FAR below saturation. The\n"
            "  mechanism IS being exercised in a discriminating regime; it just FAILS\n"
            "  to outperform an easier baseline AND fails the refuse-gate. This is\n"
            "  load-bearing negative evidence for the typed_multibank mechanism at\n"
            "  (OVERLAP=0.40, N_BANKS=128, K_per_bank=64, CUE_COS=0.70).\n\n"
            "INTERPRETATION (4 mechanism notes):\n"
            "  (a) At OVERLAP=0.40 (40% shared features across types), typed routing\n"
            "      provides NEGATIVE signal: the type-key dilutes the discriminating\n"
            "      content-features that the untyped baseline uses cleanly. Type binding\n"
            "      ADDS noise more than it ADDS structure when features overlap.\n"
            "  (b) Refuse gate at adversarial-probe arm should distinguish 'no matching\n"
            "      type-vector seen' (refuse) from 'wrong type-vector matched' (wrong).\n"
            "      Observed 0.14 refuse / 0.86 wrong means the type-router does NOT\n"
            "      detect novel types -- it confidently mis-routes them. Adversarial\n"
            "      defense is BROKEN at K_per_bank=64.\n"
            "  (c) Cardinality 9/9 (3 seeds x 3 arms) confirms the result is stable\n"
            "      across seeds; cv on typed arm=0.0305 (tight; not noise floor).\n"
            "  (d) typed_recall_cv=0.0305 < cv_chain_grade_max=0.05 means the negative\n"
            "      result IS chain-grade-quality measurement; the FINDING (mechanism\n"
            "      fails at this regime) is solid.\n\n"
            "WHAT THIS MEANS FOR THE TYPED-MULTIBANK ROADMAP:\n"
            "  The typed_multibank K=128 mechanism may STILL work at lower OVERLAP\n"
            "  regimes (e.g. OVERLAP=0.0 or <=0.10 where types are clean partitions),\n"
            "  OR at different K_per_bank, OR with different refuse-gate threshold.\n"
            "  But the v1 cell's specific configuration (OVERLAP=0.40, N_BANKS=128,\n"
            "  K_per_bank=64, K_TOTAL=8192) is now PROVEN to actively hurt vs baseline.\n"
            "  Follow-up cells should EITHER:\n"
            "    (i) sweep OVERLAP axis from 0.0 to 0.40 to find break point, OR\n"
            "    (ii) demonstrate typed routing helps at HARDER baseline regime (drop\n"
            "         baseline from 0.998 to ~0.60-0.85 band) so lift can be observed.\n\n"
            "META_RULE COMPLIANCE:\n"
            "  META_RULE_H cardinality: 9/9 OK\n"
            "  META_RULE_J no-silent-except: n_failures=0 failures=[]\n"
            "  META_RULE_K discriminator fires: typed arm produces clear negative signal\n"
            "    at 0.44; refuse arm produces clear negative signal at 0.14; both arms\n"
            "    are not vacuous (discriminator FIRES in negative direction).\n"
            "  META_RULE_L band-floor: baseline ABOVE band (saturated); typed BELOW band;\n"
            "    refuse FAR BELOW band; the mechanism FAILS not just floors.\n\n"
            "_llm_forward_calls_at_inference = 0.\n"
            "substrate_only_decode_gate: PASS (zero LLM calls; bipolar codebook routing).\n"
        ),
        kind=AtomKind.EXPERIMENT_RECORD,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.MATH,
        algebra=None,
        metadata={
            "provenance_quality": "HARD_FAIL",
            "cert_status": "honest_negative",
            "cert_class": "mechanism_fails_two_rails_typed_lift_and_refuse_gate",
            "cell_anchor": "typed_multibank_K128_adversarial_v1",
            "cell_commit": CELL_COMMIT,
            "metrics_path": METRICS_TYPED_MB,
            "ruling_note": RULING_NOTE,
            "verified_off_data": True,
            "run_mode": "full",
            "n_seeds": 3,
            "seeds": [11, 13, 19],
            "N_DIM": 8192,
            "CODEBOOK_SIZE": 65536,
            "K_TOTAL": 8192,
            "N_BANKS": 128,
            "K_PER_BANK": 64,
            "N_TYPES": 64,
            "N_ITEMS": 200,
            "FEATURE_OVERLAP_FRAC": 0.40,
            "CUE_COS": 0.70,
            "arm_baseline_untyped_recall_mean": 0.9978,
            "arm_baseline_untyped_recall_per_seed": [0.9977, 0.9978, 0.9978],
            "arm_typed_matched_recall_mean": 0.4395,
            "arm_typed_matched_recall_per_seed": [0.4451, 0.4210, 0.4523],
            "arm_typed_matched_recall_cv": 0.0305,
            "arm_typed_matched_route_acc_mean": 0.4401,
            "arm_typed_adversarial_refuse_rate_mean": 0.1363,
            "arm_typed_adversarial_refuse_rate_per_seed": [0.2003, 0.1129, 0.0957],
            "arm_typed_adversarial_wrong_rate_mean": 0.8637,
            "typed_lift_over_baseline": -0.5583,
            "hp_typed_lift_min": 0.10,
            "hp_typed_lift_miss_pp": 65,
            "hp_refuse_rate_min": 0.85,
            "hp_refuse_rate_miss_pp": 71,
            "hp_baseline_band": [0.60, 0.85],
            "baseline_above_Q_suspect_saturation": True,
            "Q_suspect_saturation": 0.95,
            "two_rails_fail": True,
            "rails_failed": ["typed_lift_rail", "refuse_gate_rail"],
            "mechanism_falsifying_not_by_construction": True,
            "META_RULE_H_cardinality_ok": True,
            "META_RULE_J_no_silent_except_ok": True,
            "META_RULE_K_discriminator_fires_negative_direction": True,
            "META_RULE_L_band_check": "baseline_above_band_typed_below_band_refuse_far_below",
            "discriminator_armed": True,
            "discriminator_fired_negative": True,
            "follow_up_path_overlap_sweep": "sweep_OVERLAP_from_0p0_to_0p40_to_find_break_point",
            "follow_up_path_harder_baseline": "drop_baseline_to_band_0p60_0p85_so_lift_observable",
            "elapsed_s_total": 412.17,
            "zero_llm_calls_at_inference": True,
            "_llm_forward_calls_at_inference": 0,
            "substrate_only_decode_gate": "PASS_zero_llm_calls_bipolar_codebook",
            "atomized_by": "skunkworks_landed_vet_5cell_batch8_2026-06-27",
        },
    )


# ============================================================================
# ATOM 2 -- gap3_cls_two_tier_BCM_slow_replay: HONEST_NEGATIVE_BCM_CHANCE
# ============================================================================

def build_atom2_bcm_chance_plus_regime_drift() -> Atom:
    return Atom(
        id=(
            "T3/EXP_gap3_cls_two_tier_BCM_slow_replay_v1_HONEST_NEGATIVE_BCM_AT_CHANCE_"
            "PLUS_REGIME_DRIFT_BCM_SLOW_acc_0p20_BCM_GENERATIVE_REPLAY_acc_0p20_chance_"
            "level_1_of_N_CAT_5_cone_cosine_0p0_compression_happened_False_baseline_"
            "1p0_violates_cross_cell_rail_HP_BASELINE_MAX_0p5_Hebbian_holds_at_1p0_"
            "cone_0p458_entropy_delta_1p609_only_baseline_and_Hebbian_learn_BCM_fails"
        ),
        name=(
            "gap3_cls TWO_TIER BCM slow_replay v1 HONEST_NEGATIVE_BCM_AT_CHANCE plus regime_drift: "
            "BCM_SLOW=0.20 BCM_GENERATIVE_REPLAY=0.20 (chance 1/5); cone_cosine=0.0 compression=False; "
            "baseline=1.0 violates HP_BASELINE_MAX=0.5 cross-cell rail; Hebbian holds at 1.0 with "
            "cone=0.458 entropy_delta=1.609 (only Hebbian + baseline learn; BCM mechanism fails)"
        ),
        description=(
            "HONEST_NEGATIVE_BCM_AT_CHANCE_PLUS_REGIME_DRIFT (cert-neutral; delta=0).\n"
            "Cell-author verdict 'methodology_drift: ARM_BASELINE_SINGLE_W=1.0 >= 0.5 cross-cell\n"
            "rail violated' is REAL but UNDER-claims. There are TWO stacked findings:\n"
            "  (a) baseline regime IS too easy (HP_BASELINE_MAX cross-cell rail violation), AND\n"
            "  (b) BOTH BCM arms (SLOW + GENERATIVE_REPLAY) collapse to CHANCE (acc=0.20=1/N_CAT=5)\n"
            "      while Hebbian arm holds at baseline=1.0 with non-trivial cone alignment.\n"
            "Under harder regime, finding (b) would STILL hold: BCM mechanism actively\n"
            "FAILS to learn this gap3-CLS task at the given hyperparameters.\n\n"
            "OFF-DATA RECOMPUTE (Skunkworks 2026-06-27, .venv Python, 3 seeds: 11, 13, 19):\n"
            "  Cardinality: 12/12 units (4 arms x 3 seeds; cardinality_ok=True; META_RULE_H OK).\n"
            "  Per-arm 3-seed evidence:\n"
            "    ARM_BASELINE_SINGLE_W:\n"
            "      heldout_acc per seed: [1.0, 1.0, 1.0]  mean=1.0  cv=0.0\n"
            "      w_schema_cone_cosine per seed: [1.0, 1.0, 1.0]\n"
            "      w_schema_eigenspectrum_entropy_delta per seed: [0.0, 0.0, 0.0]\n"
            "    ARM_TWO_TIER_HEBBIAN_SLOW:\n"
            "      heldout_acc per seed: [1.0, 1.0, 1.0]  mean=1.0  cv=0.0\n"
            "      w_schema_cone_cosine per seed: [0.4581, 0.4589, 0.4603]  mean=0.459\n"
            "      w_schema_eigenspectrum_entropy_delta per seed: [1.6093, 1.6094, 1.6094]\n"
            "    ARM_TWO_TIER_BCM_SLOW:\n"
            "      heldout_acc per seed: [0.20, 0.20, 0.20]  mean=0.20 (CHANCE = 1/N_CAT)\n"
            "      w_schema_cone_cosine per seed: [0.0, 0.0, 0.0]\n"
            "      w_schema_eigenspectrum_entropy_delta per seed: [0.0, 0.0, 0.0]\n"
            "    ARM_TWO_TIER_BCM_GENERATIVE_REPLAY:\n"
            "      heldout_acc per seed: [0.20, 0.20, 0.20]  mean=0.20 (CHANCE)\n"
            "      w_schema_cone_cosine per seed: [0.0, 0.0, 0.0]\n\n"
            "BCM FAILURE IS REAL AND SEPARATE FROM REGIME DRIFT:\n"
            "  Even if baseline regime were harder (e.g. acc 0.7 not 1.0), the BCM arms would\n"
            "  STILL be at 0.20 chance. The lift_over_hebbian=-0.8 finding means BCM arms\n"
            "  produce ZERO above-chance signal, while Hebbian arm produces full above-chance\n"
            "  signal at the SAME regime. This is mechanism-falsifying for BCM at these HP:\n"
            "    eta_slow=0.0010, theta_window=200, replay_frac=0.20, replay_every=100,\n"
            "    proto_noise=0.30, N_REPLAY=5000, N_TRAIN=20, N_CAT=5.\n\n"
            "WHY HONEST_NEGATIVE_BCM_AT_CHANCE NOT METHODOLOGY_DRIFT_ALONE:\n"
            "  Methodology-drift label would imply 'task too easy; result vacuous; ignore.'\n"
            "  But Hebbian shows 1.0 acc with measurable cone-cosine 0.46 + entropy-delta 1.6 --\n"
            "  meaning Hebbian DID learn a compressed schema atop baseline acc.\n"
            "  BCM at the same regime returns ALL zeros (cone=0, entropy_delta=0, acc=chance) --\n"
            "  the BCM update rule is COLLAPSING weights to a non-discriminative state.\n"
            "  This is a REAL bug or REAL mechanism-mismatch finding, regardless of baseline\n"
            "  regime difficulty. The compression_happened=False + max_abs_cor_score_w_mag=0.0\n"
            "  confirm BCM is not just under-fitting; it's WIPING OUT the weight signal.\n\n"
            "INTERPRETATION (3 mechanism notes):\n"
            "  (a) HEBBIAN SLOW arm IS the intended 'slow-tier' positive control AND it works\n"
            "      (1.0 acc + measurable cone). So the two-tier infra is functional; the issue\n"
            "      is specifically the BCM update rule replacing Hebbian.\n"
            "  (b) BCM theta-threshold at theta_window=200 across N_REPLAY=5000 cycles may be\n"
            "      driving theta past the discriminative regime -- thresholds get too high\n"
            "      and post-synaptic activity always falls below theta -> weights pruned to 0.\n"
            "  (c) Generative replay (proto_noise=0.30) doesn't help; suggests the replay\n"
            "      data isn't bringing post-activities above theta either; theta dynamics is\n"
            "      load-bearing failure mode.\n\n"
            "WHAT THIS MEANS FOR THE TWO-TIER BCM ROADMAP:\n"
            "  BCM as the slow-tier update rule does NOT work out-of-box with these HP at\n"
            "  this task scale (gap3-CLS, N_TRAIN=20, N_CAT=5). Follow-up cells should:\n"
            "    (i) ablate eta_slow + theta_window jointly to find regime where post-activity\n"
            "        stays above theta (consider eta=1e-4, theta_window=20-50 not 200)\n"
            "    (ii) verify selftest: pre-condition BCM theta on Hebbian-pretrained W rather\n"
            "         than from-scratch (zero-init may be load-bearing failure)\n"
            "    (iii) FIRST harden baseline regime past HP_BASELINE_MAX=0.5 (more cats, lower\n"
            "          dim, fewer training examples) so BCM has lift-room observable when fixed.\n\n"
            "META_RULE COMPLIANCE:\n"
            "  META_RULE_H cardinality: 12/12 OK\n"
            "  META_RULE_J no-silent-except: n_failures=0 failures=[]\n"
            "  META_RULE_K discriminator fires: BCM arms produce clear negative signal at\n"
            "    chance vs Hebbian above-chance; mechanism FIRES (in negative direction)\n"
            "  META_RULE_L band-floor: BCM AT CHANCE FLOOR -- not above-floor; honest-negative\n\n"
            "_llm_forward_calls_at_inference = 0.\n"
            "substrate_only_decode_gate: PASS.\n"
        ),
        kind=AtomKind.EXPERIMENT_RECORD,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.MATH,
        algebra=None,
        metadata={
            "provenance_quality": "HARD_FAIL",
            "cert_status": "honest_negative",
            "cert_class": "bcm_at_chance_plus_regime_drift_two_findings_stacked",
            "cell_anchor": "gap3_cls_two_tier_BCM_slow_replay_v1",
            "cell_commit": CELL_COMMIT,
            "metrics_path": METRICS_GAP3_BCM,
            "ruling_note": RULING_NOTE,
            "verified_off_data": True,
            "run_mode": "full",
            "n_seeds": 3,
            "seeds": [11, 13, 19],
            "N_DIM": 8192,
            "N_CAT": 5,
            "N_TRAIN": 20,
            "N_HELDOUT": 10,
            "N_REPLAY_CYCLES": 5000,
            "eta_slow": 0.0010,
            "theta_window": 200,
            "replay_frac": 0.20,
            "replay_every": 100,
            "proto_noise": 0.30,
            "arm_baseline_acc_mean": 1.0,
            "arm_baseline_cone_cosine_mean": 1.0,
            "arm_hebbian_slow_acc_mean": 1.0,
            "arm_hebbian_slow_cone_cosine_mean": 0.459,
            "arm_hebbian_slow_entropy_delta_mean": 1.6094,
            "arm_bcm_slow_acc_mean": 0.20,
            "arm_bcm_slow_cone_cosine_mean": 0.0,
            "arm_bcm_generative_replay_acc_mean": 0.20,
            "arm_bcm_generative_replay_cone_cosine_mean": 0.0,
            "chance_acc": 0.20,
            "n_cat": 5,
            "lift_over_baseline_bcm_best": -0.80,
            "lift_over_hebbian_bcm_best": -0.80,
            "hp_baseline_max_cross_cell_rail": 0.5,
            "hp_baseline_max_violated": True,
            "hp_baseline_max_violation_pp": 50,
            "two_findings_stacked": True,
            "finding_a": "baseline_regime_too_easy_HP_BASELINE_MAX_violated",
            "finding_b": "BCM_arms_at_chance_while_Hebbian_holds_at_baseline_mechanism_fails",
            "compression_happened": False,
            "magnitude_coupling_violation": False,
            "META_RULE_H_cardinality_ok": True,
            "META_RULE_J_no_silent_except_ok": True,
            "META_RULE_K_discriminator_fires_negative_direction": True,
            "META_RULE_L_band_check": "BCM_at_chance_floor_baseline_above_band_Hebbian_at_band_ceiling",
            "discriminator_armed": True,
            "discriminator_fired_negative": True,
            "hebbian_two_tier_infra_functional": True,
            "bcm_update_rule_failure_mode_hypothesis": "theta_window_200_drives_theta_past_discriminative_regime_post_activity_pruned_to_zero",
            "follow_up_eta_theta_ablate": "eta_1e_minus_4_theta_window_20_to_50_not_200",
            "follow_up_pretrain_hebbian_first": "pre_condition_BCM_theta_on_Hebbian_W_not_zero_init",
            "follow_up_harden_baseline_regime": "more_cats_lower_dim_fewer_training_examples_so_BCM_has_lift_room",
            "elapsed_s_total": 126.02,
            "zero_llm_calls_at_inference": True,
            "_llm_forward_calls_at_inference": 0,
            "substrate_only_decode_gate": "PASS",
            "atomized_by": "skunkworks_landed_vet_5cell_batch8_2026-06-27",
        },
    )


# ============================================================================
# ATOM 3 -- kb_coarse_grain_v3_self_contained: HONEST_NEG INFRA_DEP MEMORY_NOT_IN_REPO
# ============================================================================

def build_atom3_kb_v3_sc_memory_not_in_repo() -> Atom:
    return Atom(
        id=(
            "T3/EXP_kb_coarse_grain_at_promotion_v3_self_contained_HONEST_NEGATIVE_"
            "INFRA_DEP_MEMORY_DIR_NOT_IN_REPO_inline_kb_per_class_memory_n_files_0_"
            "n_chunks_0_chunk_classes_ingested_includes_memory_but_repo_path_empty_"
            "memory_lives_in_claude_profile_n_ud_in_sample_min_0_RC_1_invariant_"
            "halt_mechanism_NEVER_exercised_v4_rescue_pull_from_claude_profile"
        ),
        name=(
            "kb_coarse_grain v3 self_contained HONEST_NEGATIVE_INFRA_DEP_MEMORY_DIR_NOT_IN_REPO: "
            "inline_kb per_class memory n_files=0 n_chunks=0; chunk_classes_ingested includes "
            "memory but repo path empty (memory lives in ~/.claude/projects/d--AI/memory/); "
            "n_ud_in_sample_min=0 RC-1 invariant halt; mechanism never exercised; v4 rescue = "
            "pull memory from claude profile OR UD-content-heuristic"
        ),
        description=(
            "HONEST_NEGATIVE_INFRA_DEP_MEMORY_DIR_NOT_IN_REPO (cert-neutral; delta=0).\n"
            "Sister of batch 7 cell 4 (kb_coarse_grain_v2_chain_grade_path INFRA_DEP).\n"
            "v3 self-contained rescue STILL hits infra-dep, but DIFFERENT root cause:\n"
            "v2 had no inline KB at all; v3 self-contained builds inline KB (n_entities=4735,\n"
            "n_relations=75, n_triples=6594, n_chunks=2199) but the memory/ source class\n"
            "discovers 0 files in the repo because the memory directory lives in the Claude\n"
            "user profile (~/.claude/projects/d--AI/memory/) NOT the hd-instrument repo.\n\n"
            "OFF-DATA RECOMPUTE (Skunkworks 2026-06-27, .venv Python, 3 seeds: 17, 23, 31):\n"
            "  inline_kb_manifest:\n"
            "    n_entities=4735  n_relations=75  n_triples=6594  n_chunks=2199\n"
            "    n_discovered=400  n_skipped=1  coverage_ratio=0.9975  avg_chunks_per_file=5.51\n"
            "    n_dim=2048  encoder=char_trigram_v1  seed=17  schema_version=v2\n"
            "    chunk_min_chars=200  chunk_target_chars=800  chunk_hard_max_chars=1600\n"
            "    chunks_per_file_cap=200  content_tag_max_chars=600\n"
            "  per_class breakdown:\n"
            "    memory:  n_files=0    n_chunks=0     n_files_zero_chunks=0\n"
            "    note:    n_files=200  n_chunks=1138  n_files_zero_chunks=0\n"
            "    prereg:  n_files=200  n_chunks=1061  n_files_zero_chunks=1\n"
            "  chunk_classes_ingested = ['note', 'memory', 'prereg']  (manifest claims memory)\n"
            "  ud_source_class = 'chunk_memory'  (UD label requires memory chunks)\n"
            "  n_ud_in_sample_per_seed = []  (3 seeds error before computing n_ud)\n"
            "  n_ud_in_sample_min = 0\n"
            "  HP_min_n_ud_in_sample = 10  (RC-1 invariant: vacuous if 0)\n\n"
            "  Per-seed errors (all 3 seeds identical):\n"
            "    seed=17: RuntimeError USER_DIRECTIVE_REFERENT_MISSING: zero chunk_memory atoms\n"
            "      in inline KB (n_ent=4735); cannot satisfy v3 cardinality_ok bar (n_UD >= 10).\n"
            "      Check chunk_ingest succeeded over memory/.\n"
            "    seed=23: (same)\n"
            "    seed=31: (same)\n\n"
            "ROOT CAUSE (independently verified by Skunkworks via filesystem check):\n"
            "  ls memory/                    -> empty/missing (hd-instrument repo has no memory dir)\n"
            "  ls C:/dev/hd-instrument/memory/ -> empty/missing\n"
            "  ls ~/.claude/projects/d--AI/memory/ -> MEMORY.md + 50+ topic files present\n"
            "  The self-contained KB build discovered memory class (per chunk_classes_ingested)\n"
            "  but the file-discovery walker found 0 files in <repo>/memory/. Manifest correctly\n"
            "  reports per_class.memory.n_files=0 -- the discovery succeeded, the directory was\n"
            "  just empty in the search path. This is a PATH-SCOPE bug not a chunker bug.\n\n"
            "WHY HONEST_NEGATIVE_INFRA_DEP NOT METHODOLOGY_DRIFT:\n"
            "  - Mechanism NEVER exercised (RC-1 invariant pre-flight halted all 3 seeds).\n"
            "  - The v3 cell DESIGN is correct: it correctly requires n_ud >= 10 atoms to\n"
            "    avoid the vacuous-pass problem v1 had (where 0 UDs trivially satisfied).\n"
            "  - The infra-dep is the SELF-CONTAINED-BUILD path-scope: v3 was supposed to\n"
            "    rescue v2's infra-dep by being self-contained, but the self-contained build\n"
            "    only walks <repo>/{note,memory,prereg}/ -- and <repo>/memory/ doesn't exist.\n"
            "  - The cell's RC-1 invariant is WORKING AS DESIGNED: it FAILS LOUDLY rather than\n"
            "    silently passing on a UD-less KB. This is META_RULE_J no-silent-except OK.\n\n"
            "v4 RESCUE PATHS (cell-author scope; NOT cert-owner authority):\n"
            "  (a) Pull memory class from ~/.claude/projects/d--AI/memory/ (cross-profile read)\n"
            "  (b) Add content-based UD-detection heuristic (e.g. files containing 'USER:' or\n"
            "      'USER directive' or 'USER-locked' markers) instead of source-class label\n"
            "  (c) Pre-seed inline KB with hand-curated UD canonical set bundled with the cell\n"
            "  (d) Use the canonical-KB UD atoms via tool-helper (breaks self-contained\n"
            "      principle but is the simplest fix)\n"
            "  Recommend (b) for self-contained principle + (a) as fallback path.\n\n"
            "META_RULE COMPLIANCE:\n"
            "  META_RULE_H cardinality: cardinality_ok=False BUT for the RIGHT reason (RC-1\n"
            "    invariant correctly halted; not a silent cardinality miss)\n"
            "  META_RULE_J no-silent-except: errors surfaced in seed_results; ok\n"
            "  META_RULE_K discriminator fires: pre-flight RC-1 IS the discriminator and it\n"
            "    fired correctly in protective direction (refused to run vacuous mechanism)\n\n"
            "RC-1 INVARIANT MERIT:\n"
            "  The fact that v3 EXPLICITLY refused to run when n_ud=0 is the COUNTER-EVIDENCE\n"
            "  to v1's vacuous-satisfaction failure. v1 ran with 0 UDs and 'passed' trivially;\n"
            "  v3 ran with 0 UDs and FAILED LOUDLY. This is a CORRECT improvement in the cell\n"
            "  series even though THIS run is infra-dep.\n\n"
            "_llm_forward_calls_at_inference = 0.\n"
            "substrate_only_decode_gate: PASS (zero LLM calls; mechanism never reached anyway).\n"
        ),
        kind=AtomKind.EXPERIMENT_RECORD,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.MATH,
        algebra=None,
        metadata={
            "provenance_quality": "HARD_FAIL",
            "cert_status": "honest_negative",
            "cert_class": "infra_dep_memory_dir_not_in_repo_self_contained_build_path_scope_bug",
            "cell_anchor": "kb_coarse_grain_at_promotion_v3_self_contained",
            "cell_commit": CELL_COMMIT,
            "metrics_path": METRICS_KB_V3_SC,
            "ruling_note": RULING_NOTE,
            "verified_off_data": True,
            "run_mode": "full",
            "n_seeds": 3,
            "seeds": [17, 23, 31],
            "kb_version": "v1",
            "kb_n_entities": 4735,
            "kb_n_relations": 75,
            "kb_n_triples": 6594,
            "kb_n_chunks": 2199,
            "kb_n_discovered_files": 400,
            "kb_n_skipped_files": 1,
            "kb_coverage_ratio": 0.9975,
            "kb_n_dim": 2048,
            "kb_encoder": "char_trigram_v1",
            "per_class_memory_n_files": 0,
            "per_class_memory_n_chunks": 0,
            "per_class_note_n_files": 200,
            "per_class_note_n_chunks": 1138,
            "per_class_prereg_n_files": 200,
            "per_class_prereg_n_chunks": 1061,
            "chunk_classes_ingested": ["note", "memory", "prereg"],
            "ud_source_class": "chunk_memory",
            "n_ud_in_sample_min": 0,
            "hp_min_n_ud_in_sample": 10,
            "rc_1_invariant_correctly_halted": True,
            "mechanism_never_exercised": True,
            "root_cause": "memory_dir_not_in_repo_lives_in_claude_user_profile",
            "claude_profile_memory_path": "~/.claude/projects/d--AI/memory/",
            "repo_memory_path_exists": False,
            "filesystem_verified_by_skunkworks": True,
            "v4_rescue_paths": [
                "pull_memory_from_claude_profile_cross_profile_read",
                "add_content_based_UD_detection_heuristic",
                "pre_seed_inline_KB_with_hand_curated_UD_canonical_set",
                "use_canonical_KB_UD_atoms_via_tool_helper",
            ],
            "v4_recommended_path": "content_based_heuristic_plus_claude_profile_fallback",
            "META_RULE_H_cardinality_ok": False,
            "META_RULE_H_halted_for_right_reason_RC1": True,
            "META_RULE_J_no_silent_except_ok": True,
            "META_RULE_K_discriminator_fires_protective_direction": True,
            "sister_atom_batch7_cell4": "kb_coarse_grain_v2_chain_grade_path_INFRA_DEP",
            "v1_v3_design_improvement": "v3_RC1_explicitly_halts_on_n_ud_0_vs_v1_vacuous_pass",
            "elapsed_s_total": 4.27,
            "zero_llm_calls_at_inference": True,
            "_llm_forward_calls_at_inference": 0,
            "substrate_only_decode_gate": "PASS",
            "atomized_by": "skunkworks_landed_vet_5cell_batch8_2026-06-27",
        },
    )


# ============================================================================
# ATOM 4 -- edge_imp v3p1 ULTRA_tuned: HONEST_NEG ULTRAMETRIC GEOMETRY MISMATCH
# ============================================================================

def build_atom4_edge_imp_ultra_geometry_mismatch() -> Atom:
    return Atom(
        id=(
            "T3/EXP_edge_importance_retrieval_trace_x_ultrametric_coreness_v3p1_ULTRA_"
            "tuned_HONEST_NEGATIVE_ULTRAMETRIC_CLUSTER_GEOMETRY_MISMATCH_coreness_atoms_"
            "0_at_ULTRA_COS_0p7_ULTRA_MIN_SIZE_3_N_512_M_OLD_600_M_RECENT_400_real_atoms_"
            "do_not_cluster_tight_enough_synthetic_sigma_0p02_selftest_passes_real_geom_"
            "fails_3_seeds_halted_at_setup_arms_count_0_pivot_to_TRACE_only_drop_ULTRA"
        ),
        name=(
            "edge_importance retrieval_trace x ultrametric_coreness v3p1 ULTRA_tuned "
            "HONEST_NEGATIVE_ULTRAMETRIC_CLUSTER_GEOMETRY_MISMATCH: coreness_atoms=0 at "
            "ULTRA_COS=0.7 ULTRA_MIN_SIZE=3 (N=512 M_OLD=600 M_RECENT=400); real atom-cluster "
            "geometry doesn't cluster tight enough; synthetic sigma=0.02 selftest passed but "
            "real fails; 3 seeds halted at setup (arms_count=0); pivot: drop ULTRA, TRACE-only"
        ),
        description=(
            "HONEST_NEGATIVE_ULTRAMETRIC_CLUSTER_GEOMETRY_MISMATCH (cert-neutral; delta=0).\n"
            "Third MIDDLE-BAND-family hit in the edge-importance arc. v3 cell had same issue\n"
            "at ULTRA_COS=0.85 ULTRA_MIN_SIZE=5; v3.1 tuned thresholds DOWN to (0.7, 3) and\n"
            "STILL fired the META_RULE_K coreness-fires assertion. The discriminator IS\n"
            "working as designed (refusing to silently reduce composition to TRACE-only when\n"
            "ULTRA component is degenerate). The honest finding: REAL atom-cluster geometry\n"
            "doesn't cluster tight enough for ANY ULTRA_COS in [0.7, 0.85] at MIN_SIZE in [3, 5].\n\n"
            "OFF-DATA RECOMPUTE (Skunkworks 2026-06-27, .venv Python, 3 seeds: 7, 17, 23):\n"
            "  Config:\n"
            "    N=512  M_OLD=600  M_RECENT=400  alpha=1.953125  N_USE=240  composite_arity=3\n"
            "    LAMBDA_LIST=[0.1, 0.3, 0.5]  N_PRUNE_FRAC=0.3\n"
            "    ULTRA_COS=0.7  (tuned DOWN from 0.85 in v3)\n"
            "    ULTRA_MIN_SIZE=3  (tuned DOWN from 5 in v3)\n"
            "    DOWNSCALE_SCALE=0.2  N_QUERIES=200  N_COMPOSITE=3000\n"
            "  Per-seed (all halted at setup, arms_count=0):\n"
            "    seed=7   elapsed=1.429s  trace_total=None  coreness_atoms=None  arms=[]\n"
            "    seed=17  elapsed=1.381s  trace_total=None  coreness_atoms=None  arms=[]\n"
            "    seed=23  elapsed=1.266s  trace_total=None  coreness_atoms=None  arms=[]\n"
            "  Cell verdict_msg:\n"
            "    'D3 caught setup exception seed=7: META_RULE_K coreness-fires FAIL:\n"
            "     coreness_atoms=0 at seed=7 with ULTRA_COS=0.7, ULTRA_MIN_SIZE=3. v3.1\n"
            "     cell is DEGENERATE at these thresholds -- composition would silently\n"
            "     reduce to TRACE-only. Tune thresholds looser OR raise N. v3 had the\n"
            "     same issue at (0.85, 5); v3.1 must NOT repeat it.'\n\n"
            "WHY HONEST_NEGATIVE_ULTRAMETRIC_GEOMETRY_MISMATCH NOT MECHANISM_HARD_FAIL:\n"
            "  The discriminator (META_RULE_K coreness-fires) is the cell-author's own\n"
            "  pre-flight assertion DESIGNED TO PREVENT the v3 silent-reduce-to-TRACE bug.\n"
            "  It fired correctly. The negative finding is:\n"
            "    'ULTRA composition cannot be tuned to fire with non-trivial coreness on\n"
            "     REAL substrate atom geometry at N=512 with this M_OLD/M_RECENT regime.'\n"
            "  Synthetic selftest at sigma=0.02 passes; real atoms have wider intra-cluster\n"
            "  spread. This is geometry-evidence not mechanism-bug.\n\n"
            "DIAGNOSTIC: WHY REAL ATOMS DON'T CLUSTER TIGHT ENOUGH (3 hypotheses):\n"
            "  (h1) char-trigram encoder produces broad clusters: encoder-level diversity\n"
            "       lifts intra-cluster cosine ceiling below 0.7. Real atom vectors at\n"
            "       N=512 may have intra-cluster cosine in 0.4-0.6 range.\n"
            "  (h2) M=1000 atoms across V_R ~ 75 relations means avg 13 atoms per relation;\n"
            "       MIN_SIZE=3 needs 3 atoms within COS>=0.7 - sparse coverage in this regime.\n"
            "  (h3) The DOWNSCALE_SCALE=0.2 (random downscale on M_RECENT) may be too aggressive\n"
            "       and breaks intra-cluster proximity that COS-threshold relies on.\n\n"
            "PIVOT SIGNAL: TRACE-ONLY PATH IS CLEAN (D1 alternative cell evidence):\n"
            "  Sister cell exp_edge_importance_v3_D1_alternative_discriminators_v1 showed\n"
            "  TRACE D1_AUC = 1.000 on the retrieval-trace edge-importance signal WITHOUT\n"
            "  the ULTRA composition component. The ULTRA composition is NOT load-bearing\n"
            "  for the edge-importance finding -- it was a 2-axis discriminator hardening\n"
            "  attempt that turns out to be brittle to real atom geometry.\n\n"
            "RECOMMENDED PIVOT (Research authority):\n"
            "  (a) DROP ULTRA composition from the edge-importance series; commit to TRACE-only.\n"
            "  (b) IF ULTRA is desired as a separate cell, raise N from 512 to >= 4096 AND\n"
            "      use a denser-clustering encoder (e.g. word2vec or sparse-bipolar) -- the\n"
            "      char-trigram encoder is too broad for ULTRA at small N. Note this is the\n"
            "      same 'encoder is THE bottleneck' theme from 2026-06-23 substrate arc.\n"
            "  (c) IF retaining v3.1 architecture, accept ULTRA as optional-only (silent\n"
            "      degrade to TRACE-only IS the intended fallback per ULTRA composition\n"
            "      design) -- but then the META_RULE_K coreness-fires assertion should be\n"
            "      REMOVED or downgraded from HARD_FAIL to MIDDLE_BAND_WARN.\n\n"
            "META_RULE COMPLIANCE:\n"
            "  META_RULE_K discriminator fires: protective direction (refused silent\n"
            "    composition-degrade) - WORKING AS DESIGNED\n"
            "  META_RULE_J no-silent-except: setup-exception correctly surfaced\n"
            "  META_RULE_H cardinality: 0 of expected arms ran; halted before main run\n"
            "    (consistent with META_RULE_K protective halt; not a silent failure)\n\n"
            "_llm_forward_calls_at_inference = 0.\n"
            "substrate_only_decode_gate: PASS.\n"
        ),
        kind=AtomKind.EXPERIMENT_RECORD,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.MATH,
        algebra=None,
        metadata={
            "provenance_quality": "HARD_FAIL",
            "cert_status": "honest_negative",
            "cert_class": "ultrametric_cluster_geometry_mismatch_real_atoms_not_tight_enough",
            "cell_anchor": "edge_importance_retrieval_trace_x_ultrametric_coreness_v3p1_ULTRA_tuned",
            "cell_commit": CELL_COMMIT,
            "metrics_path": METRICS_EDGE_V3P1,
            "ruling_note": RULING_NOTE,
            "verified_off_data": True,
            "run_mode": "full",
            "n_seeds": 3,
            "seeds": [7, 17, 23],
            "N": 512,
            "M_OLD": 600,
            "M_RECENT": 400,
            "alpha": 1.953125,
            "N_USE": 240,
            "composite_arity": 3,
            "lambda_list": [0.1, 0.3, 0.5],
            "N_PRUNE_FRAC": 0.3,
            "DOWNSCALE_SCALE": 0.2,
            "ULTRA_COS": 0.7,
            "ULTRA_MIN_SIZE": 3,
            "v3_thresholds": "ULTRA_COS_0p85_MIN_SIZE_5",
            "v3p1_thresholds_tuned": "ULTRA_COS_0p7_MIN_SIZE_3",
            "coreness_atoms_per_seed": [None, None, None],
            "arms_per_seed_count": [0, 0, 0],
            "all_seeds_halted_at_setup": True,
            "discriminator_fired_protective_direction": True,
            "synthetic_selftest_sigma_0p02_passes": True,
            "real_atom_geometry_fails": True,
            "geometry_mismatch_hypotheses": [
                "h1_char_trigram_encoder_broad_clusters_intra_cluster_cos_below_0p7",
                "h2_M_1000_across_75_relations_sparse_coverage_for_MIN_SIZE_3",
                "h3_DOWNSCALE_SCALE_0p2_too_aggressive_breaks_intra_cluster_proximity",
            ],
            "sister_cell_TRACE_only_clean": "exp_edge_importance_v3_D1_alternative_discriminators_v1_TRACE_D1_AUC_1p000",
            "pivot_recommendation": "DROP_ULTRA_composition_commit_to_TRACE_only_path",
            "alternative_pivot_a": "DROP_ULTRA_composition_commit_to_TRACE_only_path",
            "alternative_pivot_b": "raise_N_to_4096_plus_denser_encoder_word2vec_or_sparse_bipolar",
            "alternative_pivot_c": "remove_META_RULE_K_assertion_or_downgrade_to_MIDDLE_BAND_WARN",
            "META_RULE_K_protective_fire_ok": True,
            "META_RULE_J_no_silent_except_ok": True,
            "META_RULE_H_halted_pre_main_run_consistent_with_protective_halt": True,
            "third_MIDDLE_BAND_family_hit_in_edge_importance_arc": True,
            "elapsed_s_total": 4.12,
            "zero_llm_calls_at_inference": True,
            "_llm_forward_calls_at_inference": 0,
            "substrate_only_decode_gate": "PASS",
            "atomized_by": "skunkworks_landed_vet_5cell_batch8_2026-06-27",
        },
    )


# ============================================================================
# ATOM 5 -- phase_diagram_capacity_codebook_envelope: MEASURED_MECHANISM PARTIAL
# ============================================================================

def build_atom5_phase_diag_partial_mm() -> Atom:
    return Atom(
        id=(
            "T3/EXP_phase_diagram_capacity_codebook_separated_envelope_v1_MEASURED_"
            "MECHANISM_MECH_arm_partial_10_of_69_units_OOM_at_MULTI_BANK_K4_alpha4p0_"
            "headroom10x_seed11_only_MECH_arm_completed_10_cells_rec_1p0_4_cells_"
            "EXCEEDED_predicted_band_alpha4_pred_0p75_0p9_obs_1p0_alpha8_pred_0p4_0p65_"
            "obs_1p0_KNN_sentinel_and_BARE_E_R_and_MULTI_BANK_NaN_8GB_GPU_OOM_pre_full"
        ),
        name=(
            "phase_diagram_capacity_codebook_envelope v1 MEASURED_MECHANISM MECH_arm_partial: "
            "10/69 units OOM at MULTI_BANK_K4_alpha4p0_headroom10x_seed11; only MECH arm seed=11 "
            "completed; 10 cells rec=1.0; 4 cells EXCEEDED predicted band (alpha=4-8 substrate "
            "OUTPERFORMS expectation); KNN_sentinel + BARE_E_R + MULTI_BANK arms NaN; 8GB GPU OOM"
        ),
        description=(
            "MEASURED_MECHANISM_MECH_ARM_PARTIAL plus HONEST_NEG_OOM_CARDINALITY (cert-neutral;\n"
            "delta=0). Cell-author verdict HARD_FAIL_UNIT_EXCEPTION is REAL (META_RULE_J halt\n"
            "on 1 OOM unit) but UNDER-claims the MECH-arm finding. 10 of 69 units completed\n"
            "cleanly on the MECH arm at seed=11; all 10 produced rec=1.0; FOUR cells (alpha>=4)\n"
            "EXCEEDED their predicted band -- the substrate is OUTPERFORMING the pre-reg\n"
            "predicted surface at high alpha. This is a partial-but-substantive MEASURED_MECHANISM\n"
            "finding on the MECH arm at this regime.\n\n"
            "OFF-DATA RECOMPUTE (Skunkworks 2026-06-27, .venv Python; intended 3 seeds: 11, 13, 19):\n"
            "  Config:\n"
            "    N_DIM=16384  V_R=32  encoder=SUBSTRATE_NATIVE\n"
            "    ALPHA_N_AXIS=[0.5, 1.0, 2.0, 4.0, 8.0]\n"
            "    HEADROOM_AXIS=[10x, 2x, 1.0x, 0.5x]\n"
            "    n_phase_kept=20 mech cells per seed + KNN + BARE + multi-bank probe = 23 per seed\n"
            "    EXPECTED_N_UNITS = 69 (23 per seed x 3 seeds)\n"
            "    GPU: NVIDIA GeForce RTX 4060 Ti  total=8.59GB  allowed=6.80GB\n"
            "  Cardinality: 10/69 units (cardinality_ok=False; META_RULE_H breach)\n"
            "  Failure: 1 OOM (META_RULE_J halt) at\n"
            "    seed11_armMULTI_BANK_K4_alpha4p0_headroom10x\n"
            "    Tried to allocate 1024MB; GPU 0 has 8GB total, 6.80GB allowed, 6.38GB allocated.\n"
            "    OOM at W = W + (V_.T @ K) / n_dim in ingest_hebbian_gpu (line 311).\n\n"
            "  10 MECH-arm units completed (all seed=11; all rec@1=1.0):\n"
            "    alpha_N=0.5  headroom=10x  V_C=2560   M=8192    alpha_M_VC=3.2  peak=3367MB\n"
            "    alpha_N=0.5  headroom=2x   V_C=512    M=8192    alpha_M_VC=16.0 peak=3239MB\n"
            "    alpha_N=1.0  headroom=10x  V_C=5120   M=16384   alpha_M_VC=3.2  peak=3527MB\n"
            "    alpha_N=1.0  headroom=2x   V_C=1024   M=16384   alpha_M_VC=16.0 peak=3271MB\n"
            "    alpha_N=2.0  headroom=10x  V_C=10240  M=32768   alpha_M_VC=3.2  peak=3847MB\n"
            "    alpha_N=2.0  headroom=2x   V_C=2048   M=32768   alpha_M_VC=16.0 peak=3335MB\n"
            "    alpha_N=4.0  headroom=10x  V_C=20480  M=65536   alpha_M_VC=3.2  peak=4488MB\n"
            "    alpha_N=4.0  headroom=2x   V_C=4096   M=65536   alpha_M_VC=16.0 peak=3464MB\n"
            "    alpha_N=8.0  headroom=10x  V_C=40960  M=131072  alpha_M_VC=3.2  peak=5770MB\n"
            "    alpha_N=8.0  headroom=2x   V_C=8192   M=131072  alpha_M_VC=16.0 peak=3722MB\n"
            "  All 10 used keys_unique_mode='unique_sr'.\n\n"
            "  Predicted-vs-observed (n_seeds_observed=1 each; n=1 is THIN evidence):\n"
            "    alpha=0.5 headroom=10x  pred=[0.99, 1.0]  obs=1.0  IN_BAND\n"
            "    alpha=0.5 headroom=2x   pred=[0.99, 1.0]  obs=1.0  IN_BAND\n"
            "    alpha=1.0 headroom=10x  pred=[0.99, 1.0]  obs=1.0  IN_BAND\n"
            "    alpha=1.0 headroom=2x   pred=[0.95, 1.0]  obs=1.0  IN_BAND\n"
            "    alpha=2.0 headroom=10x  pred=[0.95, 1.0]  obs=1.0  IN_BAND\n"
            "    alpha=2.0 headroom=2x   pred=[0.85, 0.95] obs=1.0  IN_BAND_at_ceiling\n"
            "    alpha=4.0 headroom=10x  pred=[0.75, 0.9]  obs=1.0  EXCEEDED_BAND\n"
            "    alpha=4.0 headroom=2x   pred=[0.60, 0.8]  obs=1.0  EXCEEDED_BAND\n"
            "    alpha=8.0 headroom=10x  pred=[0.40, 0.65] obs=1.0  EXCEEDED_BAND\n"
            "    alpha=8.0 headroom=2x   pred=[0.30, 0.55] obs=1.0  EXCEEDED_BAND\n\n"
            "  KNN_sentinel_mean = NaN (arm never ran)\n"
            "  BARE_E_R_mean = NaN (arm never ran)\n"
            "  MULTI_BANK arms = NaN (arm OOM'd at first cell)\n"
            "  codebook_matches = 0 of 3 HP (codebook_pass=False)\n"
            "  envelope_cells_pass = [alpha0.5_10x, alpha1.0_10x, alpha2.0_10x]\n\n"
            "WHY MEASURED_MECHANISM_PARTIAL NOT CHAIN_GRADE (Fix #28 under-claim):\n"
            "  - n=1 seed only (not 3); seed-replication is REQUIRED for chain-grade\n"
            "  - KNN sentinel never ran; sentinel-vs-substrate contrast missing\n"
            "  - BARE_E_R never ran; encoder-only baseline missing\n"
            "  - MULTI_BANK never ran; bank-axis cross-validation missing\n"
            "  - 4 EXCEEDED-BAND results are SUSPICIOUS (substrate too easy?);\n"
            "    USER BIAS-Q 'suspect 1.000 results' applies AT FULL alpha=8 with M=131072\n"
            "    queries -- saturated rec=1.0 demands the sentinel arm to rule out the\n"
            "    saturate-by-construction confound. Without sentinel, exceed-band is\n"
            "    NOT promotable.\n\n"
            "WHY MEASURED_MECHANISM NOT JUST HONEST_NEG_OOM:\n"
            "  10 MECH-arm units DID complete and produced consistent, surprising data\n"
            "  (4 of 10 EXCEEDED predicted band; 6 of 10 hit ceiling band). This IS\n"
            "  positive evidence the MECH arm capacity envelope at N=16384 is BROADER\n"
            "  than the pre-reg surface predicted. That observation deserves preservation\n"
            "  as MEASURED_MECHANISM characterization, NOT discarded as 'just OOM'.\n\n"
            "EVIDENCE QUALITY ON THE MECH-ARM-ONLY FINDING:\n"
            "  Stable across alpha_M_over_VC modes (both 3.2 and 16.0 modes hit rec=1.0)\n"
            "  Peak mem growing monotonically with alpha_N (3.2-5.8GB; expected for N=16384)\n"
            "  unique_sr keys mode held throughout (no codebook-exhaustion mode flip in\n"
            "    these 10 cells -- this regime IS in the unique_sr zone, similar to the\n"
            "    capacity_sweep_n16384_vc_higher_alpha_v1 batch 7 MEASURED_MECHANISM finding)\n\n"
            "OOM IS REAL ENGINEERING CONSTRAINT (not cell-author bug):\n"
            "  W matrix at N=16384 in fp32 = 1.07GB. MULTI_BANK_K4 keeps 4 W matrices\n"
            "  simultaneously = 4.28GB W alone. Combined with V/K matrices for shard-wise\n"
            "  ingestion, total exceeds 6.80GB GPU budget. The cell DESIGN_NOTE acknowledges\n"
            "  'W=N^2 fp32=1.07GB at N=16384' but didn't account for multi-bank multiplier.\n\n"
            "RESCUE PATHS (cell-author scope; NOT cert-owner authority):\n"
            "  (a) Memory-frugal multi-bank: reduce K_banks to 2 instead of 4 OR use\n"
            "      torch.cuda.empty_cache() between bank slots OR switch to bf16/fp16 W\n"
            "  (b) Sequential not parallel multi-bank: ingest banks one-at-a-time, free W\n"
            "      between, lose only ingest-time parallelism\n"
            "  (c) Split into 2 cells: one for MECH+KNN+BARE arms (small), one for MULTI_BANK\n"
            "      alone (large)\n"
            "  (d) Use remote GPU with >8GB VRAM (route via hdi_orchestrator per Fix #24)\n"
            "  Recommend (c)+(d) for clean separation + chain-grade-eligible re-run.\n\n"
            "META_RULE COMPLIANCE:\n"
            "  META_RULE_H cardinality: 10/69 BREACH (cardinality_ok=False) -- correctly halted\n"
            "  META_RULE_J no-silent-except: 1 OOM failure correctly surfaced + halted\n"
            "  META_RULE_K discriminator fires: 4 cells EXCEEDED predicted band -- the\n"
            "    pre-reg surface IS the discriminator, and substrate-MECH outperformed it.\n"
            "    But discriminator-fires in POSITIVE direction at saturated rec=1.0 needs\n"
            "    sentinel arm to be load-bearing (USER BIAS-Q applies).\n"
            "  META_RULE_L band-floor: cells AT-or-ABOVE band (6 in-band, 4 exceed); not floors\n\n"
            "_llm_forward_calls_at_inference = 0.\n"
            "substrate_only_decode_gate: PASS (zero LLM calls; substrate-native Hebbian W).\n"
        ),
        kind=AtomKind.EXPERIMENT_RECORD,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.MATH,
        algebra=None,
        metadata={
            "provenance_quality": "MEASURED_MECHANISM",
            "cert_status": "measured_mechanism",
            "cert_class": "mech_arm_partial_envelope_exceeds_prediction_at_high_alpha_OOM_pre_full",
            "cell_anchor": "phase_diagram_capacity_codebook_separated_envelope_v1",
            "cell_commit": CELL_COMMIT,
            "metrics_path": METRICS_PHASE_DIAG,
            "ruling_note": RULING_NOTE,
            "verified_off_data": True,
            "run_mode": "full",
            "n_seeds_intended": 3,
            "seeds_intended": [11, 13, 19],
            "n_seeds_with_data": 1,
            "seeds_with_data": [11],
            "N_DIM": 16384,
            "V_R": 32,
            "encoder": "SUBSTRATE_NATIVE",
            "ALPHA_N_AXIS": [0.5, 1.0, 2.0, 4.0, 8.0],
            "HEADROOM_LABELS": ["10x", "2x", "1.0x", "0.5x"],
            "n_units_observed": 10,
            "n_units_expected": 69,
            "cardinality_ok": False,
            "n_oom_failures": 1,
            "oom_unit_key": "seed11_armMULTI_BANK_K4_alpha4p0_headroom10x",
            "gpu_name": "NVIDIA GeForce RTX 4060 Ti",
            "gpu_total_mb": 8585,
            "gpu_allowed_mb": 6800,
            "mech_arm_surface_seed11_per_cell": {
                "alpha0p5_headroom10x": {"V_C": 2560, "M": 8192, "alpha_M_VC": 3.2, "rec_at_1": 1.0, "peak_mem_mb": 3367, "predicted_band": [0.99, 1.0], "in_band": True},
                "alpha0p5_headroom2x":  {"V_C": 512, "M": 8192, "alpha_M_VC": 16.0, "rec_at_1": 1.0, "peak_mem_mb": 3239, "predicted_band": [0.99, 1.0], "in_band": True},
                "alpha1p0_headroom10x": {"V_C": 5120, "M": 16384, "alpha_M_VC": 3.2, "rec_at_1": 1.0, "peak_mem_mb": 3527, "predicted_band": [0.99, 1.0], "in_band": True},
                "alpha1p0_headroom2x":  {"V_C": 1024, "M": 16384, "alpha_M_VC": 16.0, "rec_at_1": 1.0, "peak_mem_mb": 3271, "predicted_band": [0.95, 1.0], "in_band": True},
                "alpha2p0_headroom10x": {"V_C": 10240, "M": 32768, "alpha_M_VC": 3.2, "rec_at_1": 1.0, "peak_mem_mb": 3847, "predicted_band": [0.95, 1.0], "in_band": True},
                "alpha2p0_headroom2x":  {"V_C": 2048, "M": 32768, "alpha_M_VC": 16.0, "rec_at_1": 1.0, "peak_mem_mb": 3335, "predicted_band": [0.85, 0.95], "in_band": True},
                "alpha4p0_headroom10x": {"V_C": 20480, "M": 65536, "alpha_M_VC": 3.2, "rec_at_1": 1.0, "peak_mem_mb": 4488, "predicted_band": [0.75, 0.9], "in_band": False, "EXCEEDED_BAND": True},
                "alpha4p0_headroom2x":  {"V_C": 4096, "M": 65536, "alpha_M_VC": 16.0, "rec_at_1": 1.0, "peak_mem_mb": 3464, "predicted_band": [0.60, 0.8], "in_band": False, "EXCEEDED_BAND": True},
                "alpha8p0_headroom10x": {"V_C": 40960, "M": 131072, "alpha_M_VC": 3.2, "rec_at_1": 1.0, "peak_mem_mb": 5770, "predicted_band": [0.40, 0.65], "in_band": False, "EXCEEDED_BAND": True},
                "alpha8p0_headroom2x":  {"V_C": 8192, "M": 131072, "alpha_M_VC": 16.0, "rec_at_1": 1.0, "peak_mem_mb": 3722, "predicted_band": [0.30, 0.55], "in_band": False, "EXCEEDED_BAND": True},
            },
            "n_cells_in_predicted_band": 6,
            "n_cells_exceeded_predicted_band": 4,
            "knn_sentinel_mean": None,
            "knn_sentinel_arm_never_ran": True,
            "bare_e_r_mean": None,
            "bare_e_r_arm_never_ran": True,
            "multi_bank_arms_never_ran": True,
            "codebook_matches": 0,
            "envelope_cells_pass": ["alpha0p5_headroom10x", "alpha1p0_headroom10x", "alpha2p0_headroom10x"],
            "keys_unique_mode_all_cells": "unique_sr",
            "USER_BIAS_Q_applies_to_exceed_band": True,
            "USER_BIAS_Q_note": "exceed_band_at_rec_1p0_saturated_needs_KNN_sentinel_to_rule_out_saturate_by_construction_NOT_chain_grade_promotable",
            "consistent_with_capacity_sweep_n16384_batch7_unique_sr_zone": True,
            "rescue_paths": [
                "memory_frugal_multi_bank_reduce_K_banks_to_2_or_torch_cuda_empty_cache_or_bf16_W",
                "sequential_not_parallel_multi_bank_one_bank_at_a_time_free_W_between",
                "split_into_2_cells_MECH_plus_KNN_plus_BARE_small_and_MULTI_BANK_alone_large",
                "use_remote_GPU_with_more_than_8GB_VRAM_route_via_hdi_orchestrator",
            ],
            "recommended_rescue": "split_into_2_cells_plus_route_MULTI_BANK_to_remote_orchestrator",
            "META_RULE_H_cardinality_ok": False,
            "META_RULE_J_no_silent_except_ok": True,
            "META_RULE_K_discriminator_fires_positive_direction": True,
            "META_RULE_L_band_check": "at_or_above_band_not_at_floor",
            "elapsed_s_total": 186.1,
            "gpu_avail": True,
            "zero_llm_calls_at_inference": True,
            "_llm_forward_calls_at_inference": 0,
            "substrate_only_decode_gate": "PASS_zero_llm_calls_substrate_native_Hebbian_W",
            "atomized_by": "skunkworks_landed_vet_5cell_batch8_2026-06-27",
        },
    )


# ============================================================================
# SAFE WRITER HELPER (mirrors batch 7 pattern)
# ============================================================================

def safe_add_with_ledger(
    atom: Atom,
    *,
    source: str,
    note: str,
    ledger_row: dict,
    expected_cert_n_after: int,
) -> tuple[bool, str | None]:
    ps = PartitionedStore(STORE_ROOT)
    qid = f"{atom.corpus.value}::{atom.id}"
    if ps.get_atom(qid) is not None:
        print(f"  SKIP (idempotent at Store layer): {atom.id[:100]} already present.")
    else:
        print(f"  ADDING atom: {atom.id[:120]}...")
        ps.add_atom(atom, source=source, note=note)
        ps2 = PartitionedStore(STORE_ROOT)
        found = ps2.get_atom(qid)
        if found is None:
            print(f"  FAIL: atom not found post-add")
            return (False, None)
        md = found.metadata or {}
        expected_pq = (atom.metadata or {}).get("provenance_quality")
        if md.get("provenance_quality") != expected_pq:
            print(
                f"  FAIL: pq mismatch (expected {expected_pq}, "
                f"got {md.get('provenance_quality')})"
            )
            return (False, None)
        print(f"  PASS: round-trip survival OK (pq={md.get('provenance_quality')})")

    ps_check = PartitionedStore(STORE_ROOT)
    live_n = sum(
        1 for a in ps_check.all_atoms()
        if (a.metadata or {}).get("provenance_quality") == "CERT_CHAIN_GRADE"
    )
    if live_n != expected_cert_n_after:
        print(
            f"  FAIL: live CERT N {live_n} != expected_cert_n_after {expected_cert_n_after}"
        )
        return (False, None)

    print(
        f"  appending cert-ledger row "
        f"(op={ledger_row.get('op')} status={ledger_row.get('cert_status')} "
        f"delta={ledger_row.get('cert_increment_delta')})"
    )
    try:
        row_h = append_cert_ledger_row(
            ledger_row,
            expected_cert_n_pre=expected_cert_n_after,
            expected_cert_n_post=expected_cert_n_after,
        )
        print(f"  ledger row appended; row_hash = {row_h}")
        return (True, row_h)
    except Exception as e:
        print(f"  FAIL: cert-ledger append errored: {e}")
        return (False, None)


def build_measured_mechanism_row(*, atom_id, cell_commit, verdict, notes_path, metrics_path,
                                 atomized_by, note, ts=None):
    return {
        "ts": ts,
        "op": "cert_ruling",
        "atom_id": atom_id,
        "cert_status": "measured_mechanism",
        "cert_class": "mechanism_characterization",
        "verified_off_data": True,
        "atomized_by": atomized_by,
        "cell_commit": cell_commit,
        "verdict": verdict,
        "cert_increment_delta": 0,
        "cv": None,
        "referent_pointer": {
            "notes_path": notes_path,
            "metrics_path": metrics_path,
            "atom_qualified_id": atom_id,
        },
        "supersedes": None,
        "note": note,
    }


# ============================================================================
# MAIN
# ============================================================================

def main() -> int:
    apply = "--apply" in sys.argv

    atom1 = build_atom1_typed_mb_mechanism_fails()
    atom2 = build_atom2_bcm_chance_plus_regime_drift()
    atom3 = build_atom3_kb_v3_sc_memory_not_in_repo()
    atom4 = build_atom4_edge_imp_ultra_geometry_mismatch()
    atom5 = build_atom5_phase_diag_partial_mm()

    atoms = [atom1, atom2, atom3, atom4, atom5]
    labels = [
        "[1] typed_multibank K=128 adversarial HONEST_NEG MECHANISM_FAILS (delta=0)",
        "[2] gap3_cls TWO_TIER BCM slow_replay HONEST_NEG BCM_AT_CHANCE+REGIME_DRIFT (delta=0)",
        "[3] kb_coarse_grain v3 self_contained HONEST_NEG INFRA_DEP MEMORY_NOT_IN_REPO (delta=0)",
        "[4] edge_imp v3p1 ULTRA_tuned HONEST_NEG ULTRAMETRIC_GEOMETRY_MISMATCH (delta=0)",
        "[5] phase_diagram_capacity_codebook_envelope MEASURED_MECHANISM_PARTIAL (delta=0)",
    ]

    print("=" * 72)
    print("Cert routing plan (DRY pre-flight) -- 5-cell batch 8 landed-VET 2026-06-27")
    print("=" * 72)
    for atom, lbl in zip(atoms, labels):
        print(f"  {lbl}")
        print(f"      {atom.id[:110]}...")
        print(
            f"      pq={atom.metadata['provenance_quality']} "
            f"status={atom.metadata['cert_status']}"
        )
    print()
    print("  Net CERT N change: 0 (no chain-grade)")
    print("  Net ledger rows: +5 (1 measured_mechanism + 4 honest_negative)")

    if not apply:
        print()
        print("DRY: pass --apply to mutate Store + ledger.")
        return 0

    print()
    print("=" * 72)
    print("A5 PRE snapshot")
    print("=" * 72)
    ps_pre = PartitionedStore(STORE_ROOT)
    cert_pre = sum(
        1 for a in ps_pre.all_atoms()
        if (a.metadata or {}).get("provenance_quality") == "CERT_CHAIN_GRADE"
    )
    print(f"A5-PRE: live CERT N = {cert_pre}")

    running_cert_n = cert_pre

    for idx, (atom, lbl) in enumerate(zip(atoms, labels), start=1):
        print()
        print("=" * 72)
        print(f"Window {idx}: {lbl}")
        print("=" * 72)
        qid = f"{atom.corpus.value}::{atom.id}"
        status = atom.metadata["cert_status"]
        if status == "measured_mechanism":
            row = build_measured_mechanism_row(
                atom_id=qid,
                cell_commit=CELL_COMMIT,
                verdict=f"MEASURED_MECHANISM_{atom.metadata.get('cell_anchor', 'unknown')}_skunkworks_off_data",
                notes_path=RULING_NOTE,
                metrics_path=atom.metadata["metrics_path"],
                atomized_by=ATOMIZED_BY,
                note=f"measured_mechanism_{atom.metadata.get('cell_anchor', 'unknown')}",
            )
        else:  # honest_negative
            atom_cert_class = atom.metadata.get("cert_class", "")
            if "infra_dep" in atom_cert_class:
                ledger_cert_class = "infra_record"
            elif ("mechanism_fails" in atom_cert_class
                  or "bcm_at_chance" in atom_cert_class
                  or "geometry_mismatch" in atom_cert_class):
                ledger_cert_class = "mechanism_characterization"
            else:
                ledger_cert_class = "infra_record"
            row = build_honest_negative_row(
                atom_id=qid,
                cell_commit=CELL_COMMIT,
                verdict=f"HONEST_NEGATIVE_{atom.metadata.get('cert_class', 'unknown')}_{atom.metadata.get('cell_anchor', 'unknown')}_skunkworks_off_data",
                notes_path=RULING_NOTE,
                metrics_path=atom.metadata["metrics_path"],
                cert_class=ledger_cert_class,
                atomized_by=ATOMIZED_BY,
                note=f"honest_negative_{atom.metadata.get('cell_anchor', 'unknown')}_{atom.metadata.get('cert_class', 'unknown')}",
            )
        ok, h = safe_add_with_ledger(
            atom,
            source="skunkworks_landed_vet_5cell_batch8_2026-06-27",
            note=lbl,
            ledger_row=row,
            expected_cert_n_after=running_cert_n,
        )
        if not ok:
            print(f"ABORT: Atom {idx} window failed; halting.")
            return 1
        print(f"  Live CERT N now {running_cert_n}; row_hash {h}")

    print()
    print("=" * 72)
    print("A5 POST snapshot")
    print("=" * 72)
    ps_post = PartitionedStore(STORE_ROOT)
    cert_post = sum(
        1 for a in ps_post.all_atoms()
        if (a.metadata or {}).get("provenance_quality") == "CERT_CHAIN_GRADE"
    )
    net_delta = cert_post - cert_pre
    print(f"A5-POST: live CERT N = {cert_post}")
    print(f"  CERT N: {cert_pre} -> {cert_post} (net delta = {net_delta:+d})")

    ps_v = PartitionedStore(STORE_ROOT)
    for atom, lbl in zip(atoms, labels):
        qid = f"{atom.corpus.value}::{atom.id}"
        a_v = ps_v.get_atom(qid)
        assert a_v is not None, f"Atom {lbl} missing post-run"
        expected_pq = atom.metadata["provenance_quality"]
        assert (a_v.metadata or {}).get("provenance_quality") == expected_pq, \
            f"{lbl} pq mismatch"
    print(f"  PASS: all 5 atoms present at intended pq")

    print()
    print("=" * 72)
    print("SUMMARY")
    print("=" * 72)
    print(f"  5 atoms written; CERT N {cert_pre} -> {cert_post} (delta {net_delta:+d})")
    print(f"  Ledger rows appended: 5 (1 measured_mechanism + 4 honest_negative)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
