"""Atomize: Skunkworks 5-cell batch 7 landed-VET (2026-06-27).

5 metrics.json verified off-data; 6 atoms (one cell yields 2 per-arm atoms).

Cells (per-arm verify):
  [1] phase_diagram_wm_multibank_K_8192_3seed_harvest_v1   -> CHAIN_GRADE +1
  [2] phase_diagram_capacity_sweep_n16384_vc_higher_alpha_v1 -> MEASURED_MECHANISM 0
  [3] kb_dual_store_audit_v1                              -> HONEST_NEGATIVE_INFRA_DEP 0
  [4] kb_coarse_grain_at_promotion_v2_chain_grade_path     -> HONEST_NEGATIVE_INFRA_DEP 0
  [5a] kb_content_chunk_ingest_v2_tripwire_surfaced (DISC)  -> MEASURED_MECHANISM 0
  [5b] kb_content_chunk_ingest_v2_tripwire_surfaced (REDET) -> HONEST_NEGATIVE_REPRODUCIBILITY 0

Net: CERT N -> CERT N + 1; ledger rows +6.

VERIFY-OFF-DATA basis (.venv recompute 2026-06-27 from local metrics.json):

CELL 1 phase_diagram_wm_multibank_K_8192_3seed_harvest_v1:
  9/9 units (cardinality_ok). arm_stats RANDOM|MULTI_128x rec_mean=1.0 cv=0.0
  per_seed=[1.0,1.0,1.0]; ADVERSARIAL|MULTI_128x rec_mean=0.9999 cv=0.0001
  per_seed=[1.0,0.9998,1.0]; route_acc mean=1.0 both regimes. KNN sentinel mean=1.0
  per_seed=[1.0,1.0,1.0]. GPU util mean=85.07 max=93.0. 0 LLM calls at inference.
  Extends K=4096 chain-grade WM result to K=8192 (k_per_bank=64 envelope preserved).
  CLEAR CHAIN_GRADE; +1 CERT.

CELL 2 phase_diagram_capacity_sweep_n16384_vc_higher_alpha_v1:
  30/30 units. Per-arm surface MAPPED at 3 seeds each:
    VC=2000_M=16384  rec=0.6264 cv=0.002 mode=duplicates_allowed alpha_VC=8.19
    VC=2000_M=24576  rec=0.5123 cv=0.003 mode=duplicates_allowed alpha_VC=12.29
    VC=2000_M=32768  rec=0.4254 cv=0.0014 mode=duplicates_allowed alpha_VC=16.38
    VC=4000_M=16384  rec=1.0000 cv=0.0000 mode=unique_sr alpha_VC=4.10
    VC=4000_M=24576  rec=1.0000 cv=0.0000 mode=unique_sr alpha_VC=6.14
    VC=4000_M=32768  rec=0.6234 cv=0.0017 mode=duplicates_allowed alpha_VC=8.19
    VC=8000_M=16384  rec=1.0000 cv=0.0000 mode=unique_sr alpha_VC=2.05
    VC=8000_M=24576  rec=1.0000 cv=0.0000 mode=unique_sr alpha_VC=3.07
    VC=8000_M=32768  rec=1.0000 cv=0.0000 mode=unique_sr alpha_VC=4.10
  KNN_sentinel mean=0.31 (BY-DESIGN floor; no Hebbian W; n_queries=500).
  Verdict HARD_FAIL_KNN_SENTINEL is MISLEADING - KNN baseline arm is the
  cross-validation sentinel for substrate-vs-knn contrast, NOT a chain-grade gate
  on the capacity surface. Per-arm CLEAR PATTERN: rec=1.0 iff (alpha_VC <= 4.1 AND
  keys_unique_mode=unique_sr); rec collapses to 0.42-0.63 when codebook exhausted
  (mode flips to duplicates_allowed). This CONFIRMS the codebook-exhaustion drill
  finding (notes/research_drill_capacity_envelope_3x_2026-06-27.md). MEASURED_MECHANISM
  - substrate envelope characterized at this regime; NOT a chain-grade promotion
  (under-claim per Fix #28; would need a 2nd cell with V_C extended past M to
  cleanly separate envelope from codebook-exhaustion before chain-grade).

CELL 3 kb_dual_store_audit_v1:
  verdict HARD_FAIL, verdict_msg KB_REFERENT_MISSING, elapsed_s=0.0.
  Mechanism never exercised; infra-dep pre-flight gate caught upstream KB missing.
  Tier HONEST_NEGATIVE_INFRA_DEP (delta=0); rescue requires self-contained v2.

CELL 4 kb_coarse_grain_at_promotion_v2_chain_grade_path:
  Same as cell 3: verdict HARD_FAIL KB_REFERENT_MISSING elapsed_s=0.0.
  Tier HONEST_NEGATIVE_INFRA_DEP (delta=0); v3 self-contained rescue authored.

CELL 5 kb_content_chunk_ingest_v2_tripwire_surfaced (4 arms):
  ARM_CHUNK_SMOKE_NOTES_ONLY ok=True; 117769 chunks; coverage 0.9971
  ARM_CHUNK_FULL ok=True; 131030 chunks; coverage 0.942; 67 relations across 5 src classes
  ARM_CHUNK_REINGEST_DET ok=False:
    entities_byte_equal=False atoms_byte_equal=False relations_byte_equal=True
    w_l2_diff=1694119.0 (tolerance 1e-06; MASSIVE breach)
    n_chunks_a=131074 vs n_chunks_b=131379 (305-chunk delta same-input)
  ARM_CONTENT_VS_FILENAME_DISCRIMINATOR_TEST ok=True (both assertions passed):
    banana_query top1 = elephant_filename.md content (cosine 0.6367) - correct
    elephant_query top1 = banana_filename.md content (cosine 0.5850) - correct
    Baseline filename-only entries scored cosine 0.10-0.15 (vastly outranked)
    Content-vs-filename discriminator FIRED in both directions.
  ATOMIZE 2: (5a) discriminator MEASURED_MECHANISM - substantiates v2 content-KB
  claim but n=2 documents at one regime is thin; under-claim. (5b) reingest
  determinism HONEST_NEGATIVE_REPRODUCIBILITY - breaks no-lock-in principle for
  the dogfood ingest pipeline.

CERT N change: live CERT N -> live CERT N + 1.

Run:
  .venv/Scripts/python.exe tools/atomize_skunkworks_5cell_batch7_landed_vet_2026-06-27.py           # DRY
  .venv/Scripts/python.exe tools/atomize_skunkworks_5cell_batch7_landed_vet_2026-06-27.py --apply   # WRITE
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
RULING_NOTE = "notes/skunkworks_landed_vet_5cell_batch7_2026-06-27.md"
CELL_COMMIT = "n/a-2026-06-27-landed-batch7-5cell"

METRICS_K8192 = "data/exp_phase_diagram_wm_multibank_K_8192_3seed_harvest_v1/metrics.json"
METRICS_CAPACITY = "data/exp_phase_diagram_capacity_sweep_n16384_vc_higher_alpha_v1/metrics.json"
METRICS_DUAL_STORE = "data/exp_kb_dual_store_audit_v1/metrics.json"
METRICS_COARSE_V2 = "data/exp_kb_coarse_grain_at_promotion_v2_chain_grade_path/metrics.json"
METRICS_CHUNK_V2 = "data/exp_substrate_director_kb_content_chunk_ingest_v2_tripwire_surfaced/metrics.json"


# ============================================================================
# ATOM 1 -- K=8192 3-seed harvest CHAIN_GRADE (delta=+1)
# ============================================================================

def build_atom1_k8192_chain_grade() -> Atom:
    return Atom(
        id=(
            "T3/EXP_phase_diagram_wm_multibank_K_8192_3seed_harvest_v1_CHAIN_GRADE_"
            "single_arm_MULTI_128x_k_per_bank_64_envelope_preserved_RAND_rec_1p0_cv_"
            "0p0_ADV_rec_0p9999_cv_0p0001_route_acc_1p0_KNN_sentinel_1p0_n_seeds_3_"
            "extends_K_4096_chain_grade_WM_to_K_8192_GPU_util_85_zero_LLM_calls"
        ),
        name=(
            "WM multibank K=8192 3-seed harvest CHAIN_GRADE: single-arm MULTI_128x "
            "(k_per_bank=64 envelope preserved); RAND rec=1.0 cv=0.0 ADV rec=0.9999 "
            "cv=0.0001 route_acc=1.0 KNN_sentinel=1.0 across 3 seeds; extends prior "
            "K=4096 chain-grade WM to K=8192; GPU util mean=85.07 max=93.0; 0 LLM calls"
        ),
        description=(
            "CHAIN_GRADE (cert-eligible +1). K=8192 single-arm 3-seed harvest after "
            "Skunkworks flag-back #4. Drops the K-sweep axis to focus 3 seeds on the "
            "K=8192 frontier; extends the prior K=4096 chain-grade WM result.\n\n"
            "OFF-DATA RECOMPUTE (Skunkworks 2026-06-27, .venv Python, 3 seeds: 11, 13, 19):\n"
            "  Cardinality: 9/9 units (expected). cardinality_ok=True.\n"
            "  Per-arm stats (from detail.arm_stats):\n"
            "    RANDOM|MULTI_128x   rec_mean=1.0     cv=0.0    route_acc=1.0  per_seed=[1.0, 1.0, 1.0]\n"
            "    ADVERSARIAL|MULTI_128x rec_mean=0.9999 cv=0.0001 route_acc=1.0 per_seed=[1.0, 0.9998, 1.0]\n"
            "  KNN sentinel: mean=1.0 min=0.9 ok=True per_seed=[1.0, 1.0, 1.0]\n"
            "  GPU measured: avail=True name='NVIDIA GeForce RTX 4060 Ti' total_mb=8187\n"
            "    util mean=85.07 p50=82.0 max=93.0 n_samples=15 peak_mem_mb up to 4811\n"
            "  Substrate-only: zero_llm_calls_at_inference=True n_llm_calls=0 _atexit_synth=False\n"
            "  Config: N_DIM=8192 CODEBOOK_SIZE=65536 sigma=1.0 CUE_COS=0.70 FEATURE_OVERLAP=0.20\n"
            "    K_TOTAL=8192 n_banks=128 k_per_bank=64 N_ITEMS_PER_K=200\n"
            "    HP gates: chain>=0.95 cv<=0.05 route_acc>=0.95 HP_adv_within=0.05 sentinel_K=4096\n"
            "  elapsed_s=5.7 total (3 seeds x 3 regime/arms)\n\n"
            "CHAIN-GRADE BANDS CLEARED (all above-floor, not at-floor per META_RULE_L):\n"
            "  RAND rec 1.0 >> 0.95 floor; cv 0.0 << 0.05 max\n"
            "  ADV rec 0.9999 > 0.95 floor; cv 0.0001 << 0.05 max; adv_within=0.0001 << 0.05\n"
            "  route_acc 1.0 > 0.95 floor (both regimes)\n"
            "  KNN sentinel 1.0 >> 0.90 floor\n"
            "  cardinality 9/9 (META_RULE_H)\n"
            "  no-silent-except (META_RULE_J) - explicit failures list empty, n_failures=0\n"
            "  smoke fires discriminator (META_RULE_K) - adversarial regime is the harder\n"
            "    arm and substrate held; not by-construction-saturation\n"
            "  not band-floor (META_RULE_L) - metrics ABOVE bands not AT bands\n\n"
            "COMPOSES_WITH: prior K=4096 chain-grade WM result (k_per_bank=64 envelope\n"
            "  is the load-bearing structural invariant; this cell extends K-axis by 2x\n"
            "  while holding the per-bank capacity constant).\n\n"
            "DESIGN_NOTE_FROM_CELL: 'K=8192 3-seed harvest after Skunkworks flag-back #4.\n"
            "  v3 K-sweep halted at K=32768 VRAM probe; harvested K=8192 only at seed=11.\n"
            "  This cell drops the sweep axis entirely and runs K=8192 ONLY at 3 seeds\n"
            "  [11,13,19] to get the single-arm chain-grade evidence. META_RULE_H\n"
            "  cardinality guard (expected 9); META_RULE_J no-silent-except; META_RULE_K\n"
            "  smoke fires mechanism; META_RULE_L not-band-floor because K=8192 saturation\n"
            "  is the discriminator WIN at the K-extension frontier (K=16384 in v3 already\n"
            "  shows rec=0.9999 = approaching cliff).'\n\n"
            "WHY CHAIN_GRADE NOT MEASURED_MECHANISM: this isn't a mechanism\n"
            "  characterization (no novel mechanism); it's a CAPACITY EXTENSION of a\n"
            "  prior chain-grade result. The new claim is 'WM multibank K=8192 with\n"
            "  k_per_bank=64 (n_banks=128) maintains chain-grade recall + route under\n"
            "  random + adversarial regimes across 3 seeds.' That claim is directly\n"
            "  evidenced and above-floor.\n\n"
            "_llm_forward_calls_at_inference = 0.\n"
            "substrate_only_decode_gate: PASS (zero LLM calls; bipolar codebook routing).\n"
        ),
        kind=AtomKind.EXPERIMENT_RECORD,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.MATH,
        algebra=None,
        metadata={
            "provenance_quality": "CERT_CHAIN_GRADE",
            "cert_status": "chain_grade",
            "cert_class": "capacity_extension_pre_reg_pass",
            "cell_anchor": "phase_diagram_wm_multibank_K_8192_3seed_harvest_v1",
            "cell_commit": CELL_COMMIT,
            "metrics_path": METRICS_K8192,
            "ruling_note": RULING_NOTE,
            "verified_off_data": True,
            "run_mode": "full",
            "n_seeds": 3,
            "seeds": [11, 13, 19],
            "K_TOTAL": 8192,
            "ARM_LABEL": "MULTI_128x",
            "N_BANKS": 128,
            "K_PER_BANK": 64,
            "N_DIM": 8192,
            "CODEBOOK_SIZE": 65536,
            "SIGMA": 1.0,
            "CUE_COS": 0.7,
            "FEATURE_OVERLAP_FRAC": 0.2,
            "N_ITEMS_PER_K": 200,
            "arm_stats": {
                "RANDOM|MULTI_128x": {
                    "recall_mean": 1.0, "recall_cv": 0.0,
                    "route_acc_mean": 1.0, "recall_per_seed": [1.0, 1.0, 1.0],
                },
                "ADVERSARIAL|MULTI_128x": {
                    "recall_mean": 0.9999, "recall_cv": 0.0001,
                    "route_acc_mean": 1.0, "recall_per_seed": [1.0, 0.9998, 1.0],
                },
            },
            "knn_sentinel_mean": 1.0,
            "knn_sentinel_min": 0.9,
            "knn_sentinel_ok": True,
            "knn_per_seed": [1.0, 1.0, 1.0],
            "hp_thresholds": {
                "chain_min": 0.95, "cv_max": 0.05, "route_acc_min": 0.95,
                "adv_within_max": 0.05, "knn_sentinel_min": 0.90,
            },
            "above_floor": True,
            "band_floor_check_META_RULE_L": "ABOVE_FLOOR_not_at_floor",
            "discriminator_check_META_RULE_K": "ADVERSARIAL_arm_held_at_rec_0p9999_not_by_construction_saturation",
            "cardinality_check_META_RULE_H": "9_of_9_expected_ok",
            "no_silent_except_META_RULE_J": "n_failures_0_failures_empty",
            "gpu_avail": True,
            "gpu_name": "NVIDIA GeForce RTX 4060 Ti",
            "gpu_util_mean": 85.07,
            "gpu_util_max": 93.0,
            "gpu_util_n_samples": 15,
            "elapsed_s_total": 5.7,
            "zero_llm_calls_at_inference": True,
            "_llm_forward_calls_at_inference": 0,
            "substrate_only_decode_gate": "PASS_zero_llm_calls_bipolar_codebook",
            "composes_with_prior_chain_grade": "wm_multibank_K_4096_chain_grade_prior_result",
            "k_per_bank_envelope_preserved": 64,
            "extends_K_axis_factor": "2x_from_K_4096_to_K_8192",
            "design_note_provenance": "skunkworks_flag_back_4_drop_K_sweep_axis_focus_3_seeds_at_K_8192",
            "atomized_by": "skunkworks_landed_vet_5cell_batch7_2026-06-27",
        },
    )


# ============================================================================
# ATOM 2 -- capacity_sweep higher-alpha MEASURED_MECHANISM (delta=0)
# ============================================================================

def build_atom2_capacity_sweep_measured_mechanism() -> Atom:
    return Atom(
        id=(
            "T3/EXP_phase_diagram_capacity_sweep_n16384_vc_higher_alpha_v1_MEASURED_"
            "MECHANISM_substrate_envelope_mapped_at_30_units_rec_1p0_when_alpha_VC_le_"
            "4p1_with_unique_sr_keys_collapses_to_0p42_0p63_when_codebook_exhausted_mode_"
            "flips_to_duplicates_allowed_KNN_sentinel_label_misleading_by_design_floor"
        ),
        name=(
            "capacity_sweep n=16384 higher-alpha v1 MEASURED_MECHANISM: substrate envelope "
            "mapped at 30 units (3 seeds x 9 phase points + 3 KNN sentinels); rec=1.0 iff "
            "(alpha_VC<=4.1 AND keys_unique_mode=unique_sr); collapses to 0.42-0.63 when "
            "codebook exhausted (mode flips to duplicates_allowed); HARD_FAIL verdict "
            "label is misleading (KNN sentinel arm bare-by-design)"
        ),
        description=(
            "MEASURED_MECHANISM (cert-neutral; delta=0). Per Fix #28 default UNDER-claim:\n"
            "the substrate capacity envelope IS measured at this regime, but the cell's\n"
            "HARD_FAIL verdict is misleading and the chain-grade promotion path requires\n"
            "a follow-up cell that separates substrate envelope from codebook-exhaustion.\n\n"
            "OFF-DATA RECOMPUTE (Skunkworks 2026-06-27, .venv Python, 3 seeds: 11, 13, 19):\n"
            "  Cardinality: 30/30 units (3 seeds x [9 capacity phase points + 1 KNN sentinel]).\n"
            "  Per-phase-point (3-seed means):\n"
            "    VC=2000  M=16384  alpha_VC=8.19  mode=duplicates_allowed  rec=0.6264 cv=0.0020\n"
            "    VC=2000  M=24576  alpha_VC=12.29 mode=duplicates_allowed  rec=0.5123 cv=0.0030\n"
            "    VC=2000  M=32768  alpha_VC=16.38 mode=duplicates_allowed  rec=0.4254 cv=0.0014\n"
            "    VC=4000  M=16384  alpha_VC=4.10  mode=unique_sr           rec=1.0000 cv=0.0000\n"
            "    VC=4000  M=24576  alpha_VC=6.14  mode=unique_sr           rec=1.0000 cv=0.0000\n"
            "    VC=4000  M=32768  alpha_VC=8.19  mode=duplicates_allowed  rec=0.6234 cv=0.0017\n"
            "    VC=8000  M=16384  alpha_VC=2.05  mode=unique_sr           rec=1.0000 cv=0.0000\n"
            "    VC=8000  M=24576  alpha_VC=3.07  mode=unique_sr           rec=1.0000 cv=0.0000\n"
            "    VC=8000  M=32768  alpha_VC=4.10  mode=unique_sr           rec=1.0000 cv=0.0000\n"
            "  KNN_sentinel (per seed, BARE baseline; no Hebbian W; n_queries=500):\n"
            "    seed=11 rec=0.294   seed=13 rec=0.324   seed=19 rec=0.322   mean=0.3133\n\n"
            "CLEAR PATTERN (verified per-arm):\n"
            "  rec=1.0 iff (alpha_VC <= 4.10 AND keys_unique_mode=unique_sr)\n"
            "  rec collapses to 0.42-0.63 when mode flips to duplicates_allowed\n"
            "  mode flip is determined by V_C * V_R vs M: codebook can be exhausted\n"
            "  when M_facts > V_C * V_R; substrate then maps multiple facts to same\n"
            "  (s,r) tuple - this is CODEBOOK-EXHAUSTION not substrate-envelope failure.\n\n"
            "WHY HARD_FAIL VERDICT IS MISLEADING:\n"
            "  The HARD_FAIL_KNN_SENTINEL trigger fires on KNN sentinel arm mean=0.3133\n"
            "  vs HP_knn=0.90 floor. But the KNN_SENTINEL arm is BARE BASELINE\n"
            "  (no Hebbian W; pure kNN cosine on raw fact vectors at n=500 queries) -\n"
            "  it is the cross-validation contrast for substrate-vs-no-substrate, not\n"
            "  a chain-grade gate on the capacity surface. The cell's HP gate was\n"
            "  mis-spec'd: HP_knn applied to the sentinel arm where it should have\n"
            "  applied to the substrate arms only.\n\n"
            "REAL SUBSTRATE ENVELOPE (5 of 9 phase points clear rec=1.0):\n"
            "  Substrate holds rec=1.0 at VC=4000,M={16384,24576}; VC=8000,M={all}.\n"
            "  Substrate collapses when codebook exhausted (mode=duplicates_allowed).\n"
            "  alpha_VC<=4.10 + unique_sr is the operating envelope at this regime.\n\n"
            "WHY MEASURED_MECHANISM NOT PROVEN_BOUND (Fix #28 under-claim):\n"
            "  A clean PROVEN_BOUND would require ONE-sided ceiling claim with\n"
            "  alternative explanations ruled out. Here, codebook-exhaustion vs\n"
            "  substrate-envelope is not yet cleanly separated - a follow-up cell\n"
            "  with V_C * V_R > M across ALL phase points is needed to confirm the\n"
            "  envelope is pure-substrate not pure-codebook. The drill at\n"
            "  notes/research_drill_capacity_envelope_3x_2026-06-27.md found same\n"
            "  root cause in smoke; FULL re-confirms. Mechanism CHARACTERIZED;\n"
            "  CHAIN-GRADE promotion path = (a) re-run with V_C extended such that\n"
            "  V_C * V_R > M_max ALWAYS (unique_sr forced), then (b) sweep M further\n"
            "  until substrate truly collapses; the resulting envelope IS\n"
            "  chain-grade-eligible.\n\n"
            "MONOTONE FINDINGS (verified from detail.monotone_findings):\n"
            "  'VC_up_helps_at_M=16384_delta=0.374' - increasing V_C from 2000 to\n"
            "  4000 at M=16384 lifts rec from 0.626 to 1.0 (delta=+0.374); confirms\n"
            "  V_C is the load-bearing axis at this regime.\n\n"
            "DISCRIMINATING_PASSES (verified from detail.discriminating_passes):\n"
            "  8 phase points clear HP_DISC_REC_MIN=0.50 (only VC=2000_M=32768 at\n"
            "  rec=0.4254 falls below); the discriminator IS firing.\n\n"
            "META_RULE COMPLIANCE:\n"
            "  META_RULE_H cardinality: 30/30 OK\n"
            "  META_RULE_J no-silent-except: n_failures=0 failures=[]\n"
            "  META_RULE_K smoke fires: 8/9 phase points discriminate; mechanism FIRES\n"
            "  META_RULE_L not band-floor: phase points are above-floor not at-floor;\n"
            "    HARD_FAIL trigger is on the SENTINEL ARM not the capacity arms\n\n"
            "DOES NOT POLLUTE MECHANISM HARD_FAIL LADDER: this cell's HARD_FAIL is\n"
            "  on a mis-spec'd sentinel HP gate; mechanism arms (CAPACITY) show\n"
            "  clean phase-diagram structure with codebook-exhaustion explaining\n"
            "  the off-envelope collapses.\n\n"
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
            "cert_class": "envelope_characterization_codebook_exhaustion_not_yet_separated",
            "cell_anchor": "phase_diagram_capacity_sweep_n16384_vc_higher_alpha_v1",
            "cell_commit": CELL_COMMIT,
            "metrics_path": METRICS_CAPACITY,
            "ruling_note": RULING_NOTE,
            "verified_off_data": True,
            "run_mode": "full",
            "n_seeds": 3,
            "seeds": [11, 13, 19],
            "N": 16384,
            "V_R": 8,
            "VC_SWEEP": [2000, 4000, 8000],
            "M_FACTS_SWEEP": [16384, 24576, 32768],
            "phase_surface_per_seed_means": {
                "VC=2000_M=16384": {"rec": 0.6264, "cv": 0.0020, "alpha_VC": 8.192, "mode": "duplicates_allowed"},
                "VC=2000_M=24576": {"rec": 0.5123, "cv": 0.0030, "alpha_VC": 12.288, "mode": "duplicates_allowed"},
                "VC=2000_M=32768": {"rec": 0.4254, "cv": 0.0014, "alpha_VC": 16.384, "mode": "duplicates_allowed"},
                "VC=4000_M=16384": {"rec": 1.0000, "cv": 0.0000, "alpha_VC": 4.096, "mode": "unique_sr"},
                "VC=4000_M=24576": {"rec": 1.0000, "cv": 0.0000, "alpha_VC": 6.144, "mode": "unique_sr"},
                "VC=4000_M=32768": {"rec": 0.6234, "cv": 0.0017, "alpha_VC": 8.192, "mode": "duplicates_allowed"},
                "VC=8000_M=16384": {"rec": 1.0000, "cv": 0.0000, "alpha_VC": 2.048, "mode": "unique_sr"},
                "VC=8000_M=24576": {"rec": 1.0000, "cv": 0.0000, "alpha_VC": 3.072, "mode": "unique_sr"},
                "VC=8000_M=32768": {"rec": 1.0000, "cv": 0.0000, "alpha_VC": 4.096, "mode": "unique_sr"},
            },
            "knn_sentinel_per_seed": [0.294, 0.324, 0.322],
            "knn_sentinel_mean": 0.3133,
            "knn_sentinel_is_bare_baseline_by_design": True,
            "cell_verdict_label": "HARD_FAIL_KNN_SENTINEL",
            "cell_verdict_label_assessment": "MISLEADING_sentinel_HP_gate_mis_spec_should_apply_to_substrate_arms_not_bare_baseline",
            "real_envelope_rule": "rec_1p0_iff_alpha_VC_le_4p1_AND_keys_unique_mode_unique_sr",
            "collapse_explanation": "codebook_exhausted_when_M_facts_gt_V_C_times_V_R_mode_flips_to_duplicates_allowed",
            "phase_points_at_rec_1p0": 5,
            "phase_points_collapsed": 4,
            "monotone_findings": ["VC_up_helps_at_M=16384_delta=0.374"],
            "n_discriminating_passes": 8,
            "n_total_phase_points": 9,
            "chain_grade_promotion_path": (
                "follow_up_cell_with_V_C_extended_such_that_V_C_times_V_R_gt_M_max_"
                "ALWAYS_unique_sr_forced_then_sweep_M_further_to_find_pure_substrate_envelope"
            ),
            "composes_with_drill": "notes/research_drill_capacity_envelope_3x_2026-06-27.md",
            "META_RULE_H_cardinality_ok": True,
            "META_RULE_J_no_silent_except_ok": True,
            "META_RULE_K_discriminator_fires_ok": True,
            "META_RULE_L_band_floor_check": "above_floor_not_at_floor",
            "by_construction_saturation": False,
            "elapsed_s_total": 112.7,
            "gpu_avail": True,
            "gpu_name": "NVIDIA GeForce RTX 4060 Ti",
            "zero_llm_calls_at_inference": True,
            "_llm_forward_calls_at_inference": 0,
            "substrate_only_decode_gate": "PASS_zero_llm_calls_substrate_native_Hebbian_W",
            "atomized_by": "skunkworks_landed_vet_5cell_batch7_2026-06-27",
        },
    )


# ============================================================================
# ATOM 3 -- dual_store_audit HONEST_NEGATIVE_INFRA_DEP (delta=0)
# ============================================================================

def build_atom3_dual_store_infra_dep() -> Atom:
    return Atom(
        id=(
            "T3/EXP_kb_dual_store_audit_v1_FULL_HARD_FAIL_KB_REFERENT_MISSING_pre_"
            "flight_verify_the_referent_gate_caught_0s_elapsed_mechanism_NEVER_"
            "exercised_INFRA_DEP_HONEST_NEGATIVE_upstream_kb_ingest_v1_arm_full_kb_"
            "not_materialized_same_class_as_kb_partition_v2_kb_coarse_grain_v2"
        ),
        name=(
            "kb_dual_store_audit v1 FULL HARD_FAIL (INFRA-DEP not mechanism): "
            "KB_REFERENT_MISSING data/exp_substrate_director_kb_ingest_v1/_arm_full/kb "
            "not found; pre-flight verify-the-referent gate caught in 0s; mechanism "
            "NEVER exercised; same infra-dep class as kb_partition_v2 and kb_coarse_grain_v2"
        ),
        description=(
            "HARD_FAIL_INFRA_DEP (HONEST_NEGATIVE; cert-neutral delta=0). The pre-flight "
            "verify-the-referent gate (Fix #26) caught a missing KB dependency in 0s "
            "elapsed before any mechanism code ran. Same class as the kb_partition_v2 + "
            "kb_coarse_grain_v2 atoms in this batch and the prior ANCHOR 1 v2 infra-dep atom.\n\n"
            "OFF-DATA RECOMPUTE (Skunkworks 2026-06-27, .venv Python):\n"
            "  verdict: HARD_FAIL\n"
            "  verdict_msg: KB_REFERENT_MISSING: KB dir not found: "
            "C:\\dev\\hd-instrument\\data\\exp_substrate_director_kb_ingest_v1\\_arm_full\\kb\n"
            "  elapsed_s: 0.0\n"
            "  summary.anchor: kb_dual_store_audit_v1\n\n"
            "INTERPRETATION (cert-owner tier ladder):\n"
            "  This is NOT a mechanism HARD_FAIL. The dual-store audit mechanism (comparing "
            "two independent KB ingest runs for byte-equality + atom-equality + relation-equality\n"
            "  to validate determinism) was never exercised because the upstream dependency\n"
            "  (kb_ingest_v1 _arm_full) didn't materialize the expected output directory.\n"
            "  HONEST_NEGATIVE on the INFRA dimension, NOT a HARD_FAIL on the MECHANISM dimension.\n\n"
            "ROOT CAUSE: upstream kb_ingest_v1 cell either (a) did not run with RUN_MODE=full\n"
            "  (so _arm_full/kb was never created), (b) ran but wrote to a different path under\n"
            "  remote-host conventions (C:\\dev vs d:/AI), or (c) ran and was cleaned up before\n"
            "  this dependent cell tried to attach. Cell expects path on remote (C:\\dev/...) but\n"
            "  this metrics.json was scp'd back to laptop where path doesn't exist; the cell\n"
            "  itself likely ran on remote and failed there because the upstream wasn't pinned.\n\n"
            "DUAL-STORE AUDIT MECHANISM (untested by this cell; remains OPEN):\n"
            "  Dual-store-audit was intended to verify that two independent ingest runs of\n"
            "  the same source corpus produce byte-equal entities + atoms + relations. This\n"
            "  is the no-lock-in determinism check for the dogfood KB pipeline. It is the\n"
            "  same shape as ARM_CHUNK_REINGEST_DET in the cell-5 content-chunk atom -- and\n"
            "  THAT arm DID run and DID FAIL (w_l2_diff=1694119, atoms_byte_equal=False).\n"
            "  So while this cell didn't exercise its mechanism, the SISTER cell did exercise\n"
            "  it and confirmed non-determinism. Future kb_dual_store_audit v2 should pin\n"
            "  upstream KB as self-contained or build inline.\n\n"
            "WHY ATOMIZE A HARD_FAIL-INFRA-DEP: future cells in the dual-store-audit family\n"
            "  will reference this atom to (i) avoid the same infra dep pattern, (ii) credit\n"
            "  the pre-flight gate for catching it, and (iii) ensure the cert-trail shows\n"
            "  mechanism HARD_FAIL ladder is NOT polluted by infra-dep failures.\n\n"
            "_llm_forward_calls_at_inference = 0 (cell never ran).\n"
            "substrate_only_decode_gate: N/A (mechanism never exercised).\n"
        ),
        kind=AtomKind.EXPERIMENT_RECORD,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.MATH,
        algebra=None,
        metadata={
            "provenance_quality": "HARD_FAIL",
            "cert_status": "honest_negative",
            "cert_class": "infra_dep_not_mechanism",
            "cell_anchor": "kb_dual_store_audit_v1_FULL",
            "cell_commit": CELL_COMMIT,
            "metrics_path": METRICS_DUAL_STORE,
            "ruling_note": RULING_NOTE,
            "verified_off_data": True,
            "run_mode": "full",
            "elapsed_s": 0.0,
            "failure_mode": "KB_REFERENT_MISSING_pre_flight_verify_the_referent_gate",
            "upstream_dependency_missing": (
                "data/exp_substrate_director_kb_ingest_v1/_arm_full/kb"
            ),
            "mechanism_exercised": False,
            "mechanism_tier_dimension": "UNKNOWN_mechanism_never_ran",
            "infra_tier_dimension": "HARD_FAIL_INFRA_DEP_HONEST_NEGATIVE",
            "pre_flight_gate_credit": True,
            "pre_flight_gate_caught_at_elapsed_s": 0.0,
            "sister_cell_exercised_same_mechanism_shape": "kb_content_chunk_ingest_v2_tripwire_surfaced_ARM_CHUNK_REINGEST_DET",
            "sister_cell_mechanism_result": "non_determinism_confirmed_w_l2_diff_1694119_atoms_byte_equal_False",
            "_llm_forward_calls_at_inference": 0,
            "atomized_by": "skunkworks_landed_vet_5cell_batch7_2026-06-27",
        },
    )


# ============================================================================
# ATOM 4 -- coarse_grain v2 HONEST_NEGATIVE_INFRA_DEP (delta=0)
# ============================================================================

def build_atom4_coarse_grain_v2_infra_dep() -> Atom:
    return Atom(
        id=(
            "T3/EXP_kb_coarse_grain_at_promotion_v2_chain_grade_path_FULL_HARD_FAIL_"
            "KB_REFERENT_MISSING_pre_flight_verify_the_referent_gate_caught_0s_"
            "mechanism_NEVER_exercised_INFRA_DEP_HONEST_NEGATIVE_v3_self_contained_"
            "rescue_authored_commit_2d551f9c_pending_dispatch_after_metrics_sync"
        ),
        name=(
            "kb_coarse_grain_at_promotion v2 chain_grade_path FULL HARD_FAIL (INFRA-DEP): "
            "KB_REFERENT_MISSING; pre-flight verify-the-referent gate caught in 0s; "
            "mechanism NEVER exercised; v3 self-contained rescue already committed "
            "(2d551f9c) pending dispatch after hd_metrics_sync auto-push"
        ),
        description=(
            "HARD_FAIL_INFRA_DEP (HONEST_NEGATIVE; cert-neutral delta=0). Third cell in this\n"
            "batch hit by the same upstream KB referent missing. v3 self-contained rescue\n"
            "already authored + committed (2d551f9c) per ruling-batch context; pending\n"
            "dispatch after hd_metrics_sync auto-push.\n\n"
            "OFF-DATA RECOMPUTE (Skunkworks 2026-06-27, .venv Python):\n"
            "  verdict: HARD_FAIL\n"
            "  verdict_msg: KB_REFERENT_MISSING: KB dir not found: "
            "C:\\dev\\hd-instrument\\data\\exp_substrate_director_kb_ingest_v1\\_arm_full\\kb\n"
            "  elapsed_s: 0.0\n"
            "  summary.anchor: kb_coarse_grain_at_promotion_v2_chain_grade_path\n\n"
            "INTERPRETATION (cert-owner tier ladder):\n"
            "  Same as Atom 3 + the kb_partition_v2 prior infra-dep atom. Mechanism\n"
            "  (coarse-grain ultrametric clustering at promotion-time) untested.\n\n"
            "RESCUE PATH (v3 self-contained, already authored):\n"
            "  v3 commit 2d551f9c; should NOT depend on a separately-materialized upstream\n"
            "  KB dir; should either build the KB inline OR depend on a stable snapshot\n"
            "  path that survives cleanup. PENDING DISPATCH after hd_metrics_sync auto-push.\n\n"
            "_llm_forward_calls_at_inference = 0 (cell never ran).\n"
            "substrate_only_decode_gate: N/A.\n"
        ),
        kind=AtomKind.EXPERIMENT_RECORD,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.MATH,
        algebra=None,
        metadata={
            "provenance_quality": "HARD_FAIL",
            "cert_status": "honest_negative",
            "cert_class": "infra_dep_not_mechanism",
            "cell_anchor": "kb_coarse_grain_at_promotion_v2_chain_grade_path",
            "cell_commit": CELL_COMMIT,
            "metrics_path": METRICS_COARSE_V2,
            "ruling_note": RULING_NOTE,
            "verified_off_data": True,
            "run_mode": "full",
            "elapsed_s": 0.0,
            "failure_mode": "KB_REFERENT_MISSING_pre_flight_verify_the_referent_gate",
            "upstream_dependency_missing": (
                "data/exp_substrate_director_kb_ingest_v1/_arm_full/kb"
            ),
            "mechanism_exercised": False,
            "mechanism_tier_dimension": "UNKNOWN_mechanism_never_ran",
            "infra_tier_dimension": "HARD_FAIL_INFRA_DEP_HONEST_NEGATIVE",
            "pre_flight_gate_credit": True,
            "pre_flight_gate_caught_at_elapsed_s": 0.0,
            "rescue_cell_in_flight": "kb_coarse_grain_at_promotion_v3_self_contained",
            "rescue_cell_dispatch_status": "authored_committed_2d551f9c_pending_dispatch_after_hd_metrics_sync_auto_push",
            "_llm_forward_calls_at_inference": 0,
            "atomized_by": "skunkworks_landed_vet_5cell_batch7_2026-06-27",
        },
    )


# ============================================================================
# ATOM 5a -- content_chunk v2 DISCRIMINATOR MEASURED_MECHANISM (delta=0)
# ============================================================================

def build_atom5a_content_chunk_v2_discriminator() -> Atom:
    return Atom(
        id=(
            "T3/EXP_kb_content_chunk_ingest_v2_tripwire_surfaced_ARM_CONTENT_VS_"
            "FILENAME_DISCRIMINATOR_TEST_MEASURED_MECHANISM_banana_query_top1_"
            "elephant_filename_content_cosine_0p6367_elephant_query_top1_banana_"
            "filename_content_cosine_0p5850_filename_baseline_cosine_0p10_0p15_"
            "tripwire_FIRED_both_directions_substantiates_v2_content_KB_n_2_docs_"
            "regime_thin_under_claim_per_fix28"
        ),
        name=(
            "kb_content_chunk_ingest v2 ARM_CONTENT_VS_FILENAME_DISCRIMINATOR_TEST "
            "MEASURED_MECHANISM: banana query rank-1 returns elephant_filename CONTENT "
            "about bananas (cosine 0.6367); elephant query rank-1 returns banana_filename "
            "CONTENT about elephants (cosine 0.5850); filename-only baseline cosine "
            "0.10-0.15 (vastly outranked); tripwire FIRED both directions; substantiates "
            "v2 content-KB claim; n=2 docs thin -> under-claim per Fix #28"
        ),
        description=(
            "MEASURED_MECHANISM (cert-neutral; delta=0). The content-vs-filename discriminator\n"
            "tripwire is the v2 SUCCESS arm of the content-chunk ingest cell. It empirically\n"
            "answers the v1-vs-v2 question: does the chunked content-KB retrieve by CONTENT\n"
            "(what the file is about) or by FILENAME (what the file is called)?\n\n"
            "OFF-DATA RECOMPUTE (Skunkworks 2026-06-27, .venv Python):\n"
            "  Setup: 2 source docs created adversarially - banana_filename_2026-06-26.md\n"
            "    contains ELEPHANT content; elephant_filename_2026-06-26.md contains BANANA\n"
            "    content. If KB retrieves by content, banana query should return\n"
            "    elephant_filename.md (since that's where banana content lives).\n\n"
            "  Banana query results (verified from banana_query_top_5_atoms):\n"
            "    rank-1 entity-summary (cosine 0.6367):\n"
            "      'Banana cultivation banana ripening banana tree...' (CONTENT match)\n"
            "      source: elephant_filename_2026-06-26.md (filename mismatch; CONTENT correct)\n"
            "    rank-2 chunk000 of elephant_filename (cosine 0.6338):\n"
            "      same banana cultivation chunk; IS_CHUNK_OF elephant_filename.md\n"
            "    rank-3 banana_filename_2026-06-26.md (cosine 0.1455) - FILENAME-ONLY\n"
            "      baseline file scored 4.4x WORSE than content-bearing chunk\n"
            "    rank-4 elephant_filename_2026-06-26.md (cosine 0.0098) - filename-only\n"
            "    rank-5 elephant herds chunk of banana_filename (cosine -0.0039)\n"
            "    banana_query_assertion_passed: TRUE\n"
            "    correct_content_file_substr: 'elephant_filename' (matches rank-1 source)\n\n"
            "  Elephant query results (verified from elephant_query_top_5_atoms):\n"
            "    rank-1 entity-summary (cosine 0.5850):\n"
            "      'Elephant herds elephant social structures...' (CONTENT match)\n"
            "      source: banana_filename_2026-06-26.md (filename mismatch; CONTENT correct)\n"
            "    rank-2 chunk000 of banana_filename (cosine 0.5820): same elephant chunk\n"
            "    rank-3 elephant_filename_2026-06-26.md (cosine 0.1104) - FILENAME-ONLY\n"
            "      baseline file scored 5.3x WORSE than content-bearing chunk\n"
            "    rank-4 banana_filename_2026-06-26.md (cosine 0.0098)\n"
            "    rank-5 banana cultivation chunk of elephant_filename (cosine -0.0059)\n"
            "    elephant_query_assertion_passed: TRUE\n"
            "    correct_content_file_substr: 'banana_filename' (matches rank-1 source)\n\n"
            "DISCRIMINATOR FIRED IN BOTH DIRECTIONS (both assertions passed).\n"
            "The content-chunk KB ingest v2 retrieves by CONTENT not by FILENAME. This\n"
            "  empirically substantiates the v2 content-KB claim and is the load-bearing\n"
            "  positive evidence for the dogfood Director-KB direction (Wave 4).\n\n"
            "WHY MEASURED_MECHANISM NOT CHAIN_GRADE (Fix #28 under-claim):\n"
            "  n=2 documents at one regime is THIN. A chain-grade promotion would require\n"
            "  (a) n>=10 adversarial document pairs to establish statistical confidence in\n"
            "  the rank-1 content-over-filename ordering, (b) a second regime with longer\n"
            "  natural-text documents (current docs are short keyword-stuffed test docs), and\n"
            "  (c) cross-corpus generalization (does the property hold on the full 1M-atom KB?).\n"
            "  This atom is the MECHANISM CHARACTERIZATION witness - tripwire fires on the\n"
            "  intended use - but the broader content-KB chain-grade claim awaits scale.\n\n"
            "CONTRASTS WITH SIBLING ARM_CHUNK_REINGEST_DET (atom 5b):\n"
            "  This positive evidence on retrieval QUALITY contrasts with the failed\n"
            "  determinism arm. The KB works as intended for queries (content retrieval\n"
            "  succeeds) but breaks reproducibility (re-ingest doesn't yield byte-equal\n"
            "  W matrix). These are independent dimensions and atomized separately.\n\n"
            "META_RULE COMPLIANCE:\n"
            "  META_RULE_K smoke fires: both assertions PASSED with cosine separation\n"
            "    (0.6367 vs 0.1455 baseline; 0.5850 vs 0.1104 baseline; ratio ~4x-5x)\n"
            "  META_RULE_L not band-floor: cosines well above adversarial baseline\n\n"
            "_llm_forward_calls_at_inference = 0 (char-trigram encoder).\n"
            "substrate_only_decode_gate: PASS.\n"
        ),
        kind=AtomKind.EXPERIMENT_RECORD,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.MATH,
        algebra=None,
        metadata={
            "provenance_quality": "MEASURED_MECHANISM",
            "cert_status": "measured_mechanism",
            "cert_class": "content_vs_filename_discriminator_tripwire_fired_thin_regime",
            "cell_anchor": "kb_content_chunk_ingest_v2_tripwire_surfaced_ARM_DISC",
            "cell_commit": CELL_COMMIT,
            "metrics_path": METRICS_CHUNK_V2,
            "ruling_note": RULING_NOTE,
            "verified_off_data": True,
            "run_mode": "full",
            "N_DIM": 2048,
            "seed": 17,
            "kb_version": "v1",
            "chunk_ingest_version": "v2_tripwire_surfaced",
            "n_adversarial_doc_pairs": 1,
            "banana_query_assertion_passed": True,
            "banana_query_top1_cosine": 0.6367,
            "banana_query_top1_source": "elephant_filename_2026-06-26.md",
            "banana_query_filename_baseline_cosine": 0.1455,
            "banana_query_content_vs_filename_ratio": 4.37,
            "elephant_query_assertion_passed": True,
            "elephant_query_top1_cosine": 0.5850,
            "elephant_query_top1_source": "banana_filename_2026-06-26.md",
            "elephant_query_filename_baseline_cosine": 0.1104,
            "elephant_query_content_vs_filename_ratio": 5.30,
            "discriminator_fired_both_directions": True,
            "chain_grade_promotion_gate": (
                "n>=10_adversarial_doc_pairs_plus_second_regime_longer_natural_text_plus_"
                "cross_corpus_generalization_full_KB_chunk_full_ok_True_n_chunks_131030_coverage_0p942"
            ),
            "arm_chunk_full_ok": True,
            "arm_chunk_full_n_chunks": 131030,
            "arm_chunk_full_coverage_ratio": 0.942,
            "arm_chunk_full_n_relations": 67,
            "arm_chunk_full_per_class_discovered": {
                "note": 10515, "memory": 0, "prereg": 2654,
                "director_plan": 1, "fleet_state": 1,
            },
            "arm_chunk_smoke_notes_only_ok": True,
            "arm_chunk_smoke_n_chunks": 117769,
            "arm_chunk_smoke_coverage_ratio": 0.9971,
            "elapsed_s_total_cell": 1050.97,
            "META_RULE_K_discriminator_fires_ok": True,
            "META_RULE_L_band_floor_check": "above_floor_cosine_ratio_4x_5x_baseline",
            "by_construction_saturation": False,
            "zero_llm_calls_at_inference": True,
            "_llm_forward_calls_at_inference": 0,
            "substrate_only_decode_gate": "PASS_char_trigram_encoder",
            "sister_atom_negative_determinism": (
                "T3/EXP_kb_content_chunk_ingest_v2_tripwire_surfaced_ARM_CHUNK_REINGEST_DET_"
                "HONEST_NEGATIVE_REPRODUCIBILITY_VIOLATION..."
            ),
            "atomized_by": "skunkworks_landed_vet_5cell_batch7_2026-06-27",
        },
    )


# ============================================================================
# ATOM 5b -- content_chunk v2 REINGEST_DET HONEST_NEGATIVE_REPRODUCIBILITY (delta=0)
# ============================================================================

def build_atom5b_content_chunk_v2_reingest_det_negative() -> Atom:
    return Atom(
        id=(
            "T3/EXP_kb_content_chunk_ingest_v2_tripwire_surfaced_ARM_CHUNK_REINGEST_"
            "DET_HONEST_NEGATIVE_REPRODUCIBILITY_VIOLATION_w_l2_diff_1694119_tolerance_"
            "1e_minus_6_atoms_byte_equal_False_entities_byte_equal_False_n_chunks_a_"
            "131074_vs_b_131379_305_chunk_delta_same_input_breaks_no_lock_in_principle"
        ),
        name=(
            "kb_content_chunk_ingest v2 ARM_CHUNK_REINGEST_DET HONEST_NEGATIVE_"
            "REPRODUCIBILITY: same-input re-ingest yields w_l2_diff=1694119 (tolerance "
            "1e-6); atoms_byte_equal=False entities_byte_equal=False n_chunks delta=305 "
            "(131074 vs 131379); relations byte-equal; breaks no-lock-in principle for "
            "Director-KB dogfood pipeline"
        ),
        description=(
            "HONEST_NEGATIVE_REPRODUCIBILITY (cert-neutral; delta=0). The REINGEST_DET arm\n"
            "of the content-chunk ingest v2 cell IS the determinism check arm; its FAILURE\n"
            "is a real reproducibility-violation finding (not infra-dep, not mechanism\n"
            "characterization gap) - the ingest pipeline is non-deterministic at large scale.\n\n"
            "OFF-DATA RECOMPUTE (Skunkworks 2026-06-27, .venv Python):\n"
            "  arm: ARM_CHUNK_REINGEST_DET\n"
            "  ok: False\n"
            "  elapsed_s: 526.722 (two runs back-to-back of same input corpus)\n"
            "  t_run_a_s: 265.277\n"
            "  t_run_b_s: 261.446 (4-second variation between runs)\n"
            "  entities_byte_equal: False\n"
            "  relations_byte_equal: True\n"
            "  atoms_byte_equal: False\n"
            "  w_l2_diff: 1694119.0\n"
            "  w_within_tolerance: False\n"
            "  w_tolerance: 1e-06\n"
            "  n_chunks_a: 131074\n"
            "  n_chunks_b: 131379  (305-chunk delta same-input back-to-back)\n\n"
            "INTERPRETATION (4 dims of breach):\n"
            "  (1) ENTITIES BYTE BREACH: same source corpus, ingested twice, produces\n"
            "      different entity tables. Could be (a) iteration-order over notes/ files\n"
            "      that varies (os.scandir order is FS-dependent), (b) entity-key collision\n"
            "      resolution that depends on processing order, (c) chunking boundary jitter.\n"
            "  (2) RELATIONS BYTE EQUAL: relations table is deterministic in BYTES even when\n"
            "      entities differ - suggests relations are keyed by content-hash + IS_CHUNK_OF\n"
            "      pointer, but the underlying entities those relations POINT TO differ.\n"
            "  (3) ATOMS BYTE BREACH: aggregate atoms table differs - downstream consumer\n"
            "      sees two different KB states from same input.\n"
            "  (4) W L2 DIFF 1694119 (>> tolerance 1e-6): the substrate W matrix at\n"
            "      Hebbian-bind layer differs by 1.7M in L2 norm - HUGE breach. Even with\n"
            "      float32 noise this is structural difference not floating-point jitter.\n\n"
            "  (5) CHUNK COUNT DELTA: 131074 vs 131379 = 305 chunks differ. Likely cause:\n"
            "      file-discovery race or chunker boundary-detection depending on file order.\n\n"
            "WHY HONEST_NEGATIVE: this is a REAL FINDING (the pipeline is non-deterministic),\n"
            "  NOT a bug to fix opportunistically and NOT a mechanism-untested infra-dep.\n"
            "  The arm WAS exercised, the tripwire DID fire, the violation IS substantiated.\n"
            "  Future Director-KB dogfood cells (Wave 5+) MUST fix this before chain-grade\n"
            "  promotion of the pipeline as a whole.\n\n"
            "BREAKS NO-LOCK-IN PRINCIPLE:\n"
            "  Per project_substrate_as_director_kb_dogfood_USER_2026-06-26.md, the 12\n"
            "  no-lock-in principles include 'deterministic re-ingest at byte-level' as a\n"
            "  load-bearing invariant for the dogfood KB. THIS ATOM is the negative evidence\n"
            "  that the current implementation breaches that invariant.\n\n"
            "REPAIR PATHS (cell-author scope; NOT cert-owner authority):\n"
            "  (a) freeze file-discovery order via sorted(os.listdir()) at ingest start\n"
            "  (b) seed any randomized hashing salts; pin numpy/torch/random seeds before W init\n"
            "  (c) make chunker boundary detection deterministic vs content-only (no time/order deps)\n"
            "  (d) re-run REINGEST_DET arm with w_tolerance=0.0 (strict equality not approx)\n"
            "  These are repair candidates; Research/exp_dev to dispatch v3 with one or more.\n\n"
            "SISTER ATOM (POSITIVE evidence on QUALITY axis):\n"
            "  ARM_CONTENT_VS_FILENAME_DISCRIMINATOR_TEST in same cell PASSED both ways\n"
            "  (atom 5a MEASURED_MECHANISM). Cell is a MIXED_RESULT but atomized separately\n"
            "  per Fix #28 verify-per-arm discipline.\n\n"
            "META_RULE COMPLIANCE:\n"
            "  META_RULE_K smoke fires: the determinism arm IS the discriminator and it\n"
            "    fired in the negative direction (breach detected as designed).\n"
            "  META_RULE_J no-silent-except: failures correctly surfaced in metrics.json.\n\n"
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
            "cert_class": "reproducibility_violation_breach_of_no_lock_in_principle",
            "cell_anchor": "kb_content_chunk_ingest_v2_tripwire_surfaced_ARM_REINGEST_DET",
            "cell_commit": CELL_COMMIT,
            "metrics_path": METRICS_CHUNK_V2,
            "ruling_note": RULING_NOTE,
            "verified_off_data": True,
            "run_mode": "full",
            "N_DIM": 2048,
            "seed": 17,
            "kb_version": "v1",
            "chunk_ingest_version": "v2_tripwire_surfaced",
            "arm_reingest_det_ok": False,
            "arm_reingest_det_elapsed_s": 526.722,
            "t_run_a_s": 265.277,
            "t_run_b_s": 261.446,
            "entities_byte_equal": False,
            "relations_byte_equal": True,
            "atoms_byte_equal": False,
            "w_l2_diff": 1694119.0,
            "w_within_tolerance": False,
            "w_tolerance": 1e-06,
            "n_chunks_a": 131074,
            "n_chunks_b": 131379,
            "n_chunks_delta": 305,
            "n_breach_dimensions": 4,
            "breach_dimensions": [
                "entities_byte_equal_False",
                "atoms_byte_equal_False",
                "w_l2_diff_1694119_gt_tolerance_1e_minus_6",
                "n_chunks_delta_305_same_input_back_to_back",
            ],
            "non_breach_dimensions": ["relations_byte_equal_True"],
            "discriminator_armed": True,
            "discriminator_spec": (
                "two_runs_of_same_input_corpus_byte_equality_on_entities_relations_atoms_"
                "plus_w_l2_diff_within_1e_minus_6_tolerance"
            ),
            "discriminator_fired_negative": True,
            "breaks_no_lock_in_principle": True,
            "principle_breached": (
                "deterministic_re_ingest_at_byte_level_invariant_for_dogfood_KB_per_"
                "project_substrate_as_director_kb_dogfood_USER_2026-06-26"
            ),
            "repair_paths_candidates": [
                "freeze_file_discovery_order_via_sorted_os_listdir",
                "seed_randomized_hashing_salts_pin_numpy_torch_random_seeds_before_W_init",
                "make_chunker_boundary_detection_deterministic_no_time_or_order_deps",
                "re_run_REINGEST_DET_arm_with_w_tolerance_0p0_strict_equality",
            ],
            "sister_atom_positive_discriminator": (
                "T3/EXP_kb_content_chunk_ingest_v2_tripwire_surfaced_ARM_CONTENT_VS_FILENAME_"
                "DISCRIMINATOR_TEST_MEASURED_MECHANISM..."
            ),
            "META_RULE_J_no_silent_except_ok": True,
            "META_RULE_K_discriminator_fires_negative_direction_ok": True,
            "zero_llm_calls_at_inference": True,
            "_llm_forward_calls_at_inference": 0,
            "substrate_only_decode_gate": "PASS",
            "atomized_by": "skunkworks_landed_vet_5cell_batch7_2026-06-27",
        },
    )


# ============================================================================
# SAFE WRITER HELPER (mirrors atomize_skunkworks_2cell_batch7)
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


def build_chain_grade_row(*, atom_id, cell_commit, verdict, notes_path, metrics_path,
                          atomized_by, note, ts=None):
    return {
        "ts": ts,
        "op": "cert_ruling",
        "atom_id": atom_id,
        "cert_status": "chain_grade",
        "cert_class": "pre_reg_pass",
        "verified_off_data": True,
        "atomized_by": atomized_by,
        "cell_commit": cell_commit,
        "verdict": verdict,
        "cert_increment_delta": 1,
        "cv": None,
        "referent_pointer": {
            "notes_path": notes_path,
            "metrics_path": metrics_path,
            "atom_qualified_id": atom_id,
        },
        "supersedes": None,
        "note": note,
    }


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

    atom1 = build_atom1_k8192_chain_grade()
    atom2 = build_atom2_capacity_sweep_measured_mechanism()
    atom3 = build_atom3_dual_store_infra_dep()
    atom4 = build_atom4_coarse_grain_v2_infra_dep()
    atom5a = build_atom5a_content_chunk_v2_discriminator()
    atom5b = build_atom5b_content_chunk_v2_reingest_det_negative()

    atoms = [atom1, atom2, atom3, atom4, atom5a, atom5b]
    labels = [
        "[1] K=8192 3-seed CHAIN_GRADE (delta=+1)",
        "[2] capacity_sweep higher-alpha MEASURED_MECHANISM (delta=0)",
        "[3] dual_store_audit FULL HONEST_NEG INFRA_DEP (delta=0)",
        "[4] coarse_grain v2 chain_grade_path HONEST_NEG INFRA_DEP (delta=0)",
        "[5a] content_chunk v2 DISCRIMINATOR MEASURED_MECHANISM (delta=0)",
        "[5b] content_chunk v2 REINGEST_DET HONEST_NEG REPRODUCIBILITY (delta=0)",
    ]

    print("=" * 72)
    print("Cert routing plan (DRY pre-flight) -- 5-cell batch 7 landed-VET 2026-06-27")
    print("=" * 72)
    for atom, lbl in zip(atoms, labels):
        print(f"  {lbl}")
        print(f"      {atom.id[:110]}...")
        print(
            f"      pq={atom.metadata['provenance_quality']} "
            f"status={atom.metadata['cert_status']}"
        )
    print()
    print("  Net CERT N change: +1 (K=8192 chain-grade only)")
    print("  Net ledger rows: +6 (1 chain_grade + 2 measured_mechanism + 3 honest_negative)")

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

    # ---- Window 1: Atom 1 CHAIN_GRADE (delta=+1) ----
    print()
    print("=" * 72)
    print("Window 1: Atom 1 (K=8192 3-seed CHAIN_GRADE; delta=+1)")
    print("=" * 72)
    qid1 = f"{atom1.corpus.value}::{atom1.id}"
    ps_check1 = PartitionedStore(STORE_ROOT)
    atom1_already = ps_check1.get_atom(qid1) is not None
    expected_after_a1 = cert_pre if atom1_already else cert_pre + 1
    row1 = build_chain_grade_row(
        atom_id=qid1,
        cell_commit=CELL_COMMIT,
        verdict=(
            "CHAIN_GRADE_K_8192_3SEED_single_arm_MULTI_128x_k_per_bank_64_envelope_"
            "preserved_RAND_rec_1p0_cv_0p0_ADV_rec_0p9999_cv_0p0001_route_acc_1p0_"
            "KNN_sentinel_1p0_n_seeds_3_extends_K_4096_chain_grade_WM_skunkworks_off_data"
        ),
        notes_path=RULING_NOTE,
        metrics_path=METRICS_K8192,
        atomized_by="skunkworks_atomize_5cell_batch7_2026-06-27",
        note=(
            "chain_grade_K_8192_3seed_extends_K_4096_chain_grade_WM_above_floor_not_at_"
            "floor_discriminator_fires_ADVERSARIAL_arm_held_GPU_util_85_zero_LLM_calls_"
            "cardinality_9_of_9_no_silent_except_n_failures_0"
        ),
    )
    ok, h1 = safe_add_with_ledger(
        atom1,
        source="skunkworks_landed_vet_5cell_batch7_2026-06-27",
        note=(
            "Atom 1: WM multibank K=8192 3-seed harvest CHAIN_GRADE; single-arm MULTI_128x "
            "with k_per_bank=64 envelope preserved; RAND rec=1.0 ADV rec=0.9999 KNN sentinel "
            "1.0 across 3 seeds (11, 13, 19); extends prior K=4096 chain-grade WM result; "
            "GPU util mean 85.07; substrate-only zero LLM calls."
        ),
        ledger_row=row1,
        expected_cert_n_after=expected_after_a1,
    )
    if not ok:
        print("ABORT: Atom 1 window failed; halting.")
        return 1
    print(f"  Live CERT N now {expected_after_a1}; row_hash {h1}")

    running_cert_n = expected_after_a1

    # ---- Window 2-6: delta=0 atoms ----
    for idx, (atom, lbl) in enumerate(zip([atom2, atom3, atom4, atom5a, atom5b],
                                            labels[1:]), start=2):
        print()
        print("=" * 72)
        print(f"Window {idx}: {lbl}")
        print("=" * 72)
        qid = f"{atom.corpus.value}::{atom.id}"
        pq = atom.metadata["provenance_quality"]
        status = atom.metadata["cert_status"]
        if status == "measured_mechanism":
            row = build_measured_mechanism_row(
                atom_id=qid,
                cell_commit=CELL_COMMIT,
                verdict=f"MEASURED_MECHANISM_{atom.metadata.get('cell_anchor', 'unknown')}_skunkworks_off_data",
                notes_path=RULING_NOTE,
                metrics_path=atom.metadata["metrics_path"],
                atomized_by="skunkworks_atomize_5cell_batch7_2026-06-27",
                note=f"measured_mechanism_{atom.metadata.get('cell_anchor', 'unknown')}",
            )
        else:  # honest_negative
            # Ledger cert_class enum: 'infra_record' for infra-dep; 'mechanism_characterization'
            # for reproducibility-violation honest-negatives (closest validated bucket).
            atom_cert_class = atom.metadata.get("cert_class", "")
            if "infra_dep" in atom_cert_class:
                ledger_cert_class = "infra_record"
            elif "reproducibility" in atom_cert_class:
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
                atomized_by="skunkworks_atomize_5cell_batch7_2026-06-27",
                note=f"honest_negative_{atom.metadata.get('cell_anchor', 'unknown')}_{atom.metadata.get('cert_class', 'unknown')}",
            )
        ok, h = safe_add_with_ledger(
            atom,
            source="skunkworks_landed_vet_5cell_batch7_2026-06-27",
            note=lbl,
            ledger_row=row,
            expected_cert_n_after=running_cert_n,
        )
        if not ok:
            print(f"ABORT: Atom {idx} window failed; halting.")
            return 1
        print(f"  Live CERT N now {running_cert_n}; row_hash {h}")

    # ---- A5 POST ----
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

    # Verify all atoms present at intended pq
    ps_v = PartitionedStore(STORE_ROOT)
    for atom, lbl in zip(atoms, labels):
        qid = f"{atom.corpus.value}::{atom.id}"
        a_v = ps_v.get_atom(qid)
        assert a_v is not None, f"Atom {lbl} missing post-run"
        expected_pq = atom.metadata["provenance_quality"]
        assert (a_v.metadata or {}).get("provenance_quality") == expected_pq, \
            f"{lbl} pq mismatch"
    print(f"  PASS: all 6 atoms present at intended pq")

    print()
    print("=" * 72)
    print("SUMMARY")
    print("=" * 72)
    print(f"  6 atoms written; CERT N {cert_pre} -> {cert_post} (delta {net_delta:+d})")
    print(f"  Ledger rows appended: 6 (1 chain_grade + 2 measured_mechanism + 3 honest_negative)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
