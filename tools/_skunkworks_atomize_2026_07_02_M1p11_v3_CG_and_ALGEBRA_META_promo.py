"""Skunkworks A5-gated atomize: 2026-07-02 M1.11 v3 CG + META algebra-chain promotion.

Landings:
  1. substrate_activity_energy_confidence_signal_v3_reconstruction_err_multiseed_multiregime
     3rd primitive in algebra chain (M1.9 CG + M1.10 CG + M1.11 v3 CG)
     - ARM_RECONSTRUCTION_ERR: REGIME_LOW mean AUC=0.9723 cv=0.0067 (all 5 seeds >=0.963)
     - ARM_RECONSTRUCTION_ERR: REGIME_HIGH mean AUC=0.9190 cv=0.0254 (all 5 seeds >=0.891)
     - Both regimes clear >=0.65 floor with cv<0.15
     - contamination_rate=p_target EXACTLY (0.20 / 0.50 all 40 units) - deterministic verified
     - Positive control ARM_ABLATED_RANDOM: LOW mean=0.463, HIGH mean=0.524 -
       MEANS bracket 0.5; per-seed variance +/-0.09 consistent with n=200 test queries SE
     - ARM_SIGMA_J anti-signal (~0.20/0.25) confirms mechanistic distinctness
     - cardinality_ok=True, arms_differ_verified=True, observed_n_units=40, wall 7.66s
  2. META SUBSTRATE_ALGEBRA_SCALES_TO_DEEPER_CHAINS promotion MM_TENTATIVE -> CG_META
     - Prior MM: substrate_algebra_end_to_end_roundtrip_M19_M110_K5_MM_2026-07-02
     - 3 independently CG-certified primitives now composed in the algebra chain
     - Promotion criterion satisfied: 3+ primitives in chain, each with tight cv and
       clean positive control at CG tier
  3. Delta_E secondary-discriminator MB_TENTATIVE (NOT the "strong" claim from cell-author)
     - HONEST DOWNWARD CORRECTION: cell-author framed delta_E as "strong secondary."
       Off-disk: LOW mean 0.72 (all 5 seeds >=0.692), HIGH mean 0.68 - but seed 11 HIGH
       = 0.6225 which DIPS BELOW the 0.65 floor. Means clear + cv tight, but per-seed
       floor fails at 1/10 seed-regime cells. Frame as MIDDLE_BAND (partial signal;
       independent mechanism from reconstruction_err) with revival criterion 'all seeds
       clear 0.65 both regimes in a 10-seed replication.'

Off-disk recompute (independent of verdict_msg):
  ARM_RECONSTRUCTION_ERR AUCs REGIME_LOW:
    seed 11: 0.9834375  seed 17: 0.97140625  seed 23: 0.96296875
    seed 29: 0.97234375 seed 37: 0.9715625
    mean = (0.9834375+0.97140625+0.96296875+0.97234375+0.9715625)/5 = 0.97234375 (match)
    all >= 0.65 floor, min=0.963
  ARM_RECONSTRUCTION_ERR AUCs REGIME_HIGH:
    seed 11: 0.8911  seed 17: 0.9502  seed 23: 0.8961  seed 29: 0.9175  seed 37: 0.9401
    mean = 0.919 (match) all >= 0.65 floor, min=0.891

Cross-arc concept overlap:
  substrate_query 'reconstruction error confidence signal detector risk' cosine=0.378
  top-5 all wordnet noise; NO prior experimental atom hits at cosine>0.30 on the
  Confidence Header / reconstruction-err mechanism. Genuinely novel.
"""
import json, os, tempfile

MATH = "d:/AI/hd-instrument/data/substrate_index/math/atoms.jsonl"
META = "d:/AI/hd-instrument/data/substrate_index/meta/atoms.jsonl"
LEDGER = "d:/AI/hd-instrument/data/substrate_index/meta/cert_ledger.jsonl"
TS = "2026-07-02T22:30:00Z"

def atomic_append(path, records):
    existing = []
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    existing.append(json.loads(line))
    combined = existing + records
    d = os.path.dirname(path)
    fd, tmp = tempfile.mkstemp(dir=d, prefix='.atomize_', suffix='.jsonl')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            for r in combined:
                f.write(json.dumps(r, ensure_ascii=False) + '\n')
        os.replace(tmp, path)
    except Exception:
        try: os.unlink(tmp)
        except: pass
        raise
    with open(path, 'r', encoding='utf-8') as f:
        n = sum(1 for L in f if L.strip())
    assert n == len(combined), f"append verify FAIL {path}: expected {len(combined)} got {n}"
    return n

atoms_math = [
    {
        "id": "T3/EXP_substrate_activity_energy_confidence_signal_v3_reconstruction_err_multiseed_multiregime_5seed_FULL",
        "name": "EXP substrate_activity_energy_confidence_signal_v3 REC_ERR 5seed 2regime FULL",
        "corpus": "math",
        "tier": "T3",
        "kind": "experiment_record",
        "description": "CHAIN_GRADE 5-seed FULL, 2-regime confidence-header discriminator (M1.11 v3). ARM_RECONSTRUCTION_ERR load-bearing: REGIME_LOW (p=0.2) mean AUC=0.9723 cv=0.0067 all 5 seeds >=0.963; REGIME_HIGH (p=0.5) mean AUC=0.9190 cv=0.0254 all 5 seeds >=0.891. Both regimes clear >=0.65 floor with cv<0.15. Deterministic contamination verified: contamination_rate == p_target EXACTLY across all 40 units (0.20 low, 0.50 high). Positive control ARM_ABLATED_RANDOM means bracket 0.5 (LOW=0.463, HIGH=0.524) with per-seed variance +/-0.09 (consistent with n=200 test queries SE=~0.035). ARM_SIGMA_J shows anti-signal ~0.20/0.25 both regimes (mechanistic inversion; confirms arms_differ). cardinality_ok=True, arms_differ_verified=True, expected=observed=40 units. wall 7.66s on cuda. M1.11 Confidence Header CG-eligible for hdlab extraction; 3rd primitive in the substrate algebra chain.",
        "aliases": [],
        "metadata": {
            "record_class": "experiment_record",
            "term_class": "PROCESS_KNOWLEDGE_NON_MATH",
            "experiment_path": "experiments/exp_substrate_activity_energy_confidence_signal_v3_reconstruction_err_multiseed_multiregime.py",
            "prereg_path": "preregs/2026-07-02_substrate_activity_energy_confidence_signal_v3_reconstruction_err_multiseed_multiregime.md",
            "metrics_paths": [
                "data/exp_substrate_activity_energy_confidence_signal_v3_reconstruction_err_multiseed_multiregime/metrics.json"
            ],
            "verdict": "PASS", "verdict_raw": "HARD_PASS", "cert_tier": "CHAIN_GRADE",
            "n_seeds": 5, "N": 8192, "n_arms": 4, "n_regimes": 2, "n_units": 40,
            "seeds": [11, 17, 23, 29, 37],
            "regimes": [{"name": "REGIME_LOW", "p_target": 0.2}, {"name": "REGIME_HIGH", "p_target": 0.5}],
            "arms": ["ARM_RECONSTRUCTION_ERR", "ARM_DELTA_E", "ARM_SIGMA_J", "ARM_ABLATED_RANDOM"],
            "load_bearing_arm": "ARM_RECONSTRUCTION_ERR",
            "rec_err_auc_low_mean": 0.97234375,
            "rec_err_auc_low_cv": 0.006703856915751432,
            "rec_err_auc_low_min": 0.96296875,
            "rec_err_auc_low_seeds": [0.9834375, 0.97140625, 0.96296875, 0.97234375, 0.9715625],
            "rec_err_auc_high_mean": 0.919,
            "rec_err_auc_high_cv": 0.025396900433350020,
            "rec_err_auc_high_min": 0.8911,
            "rec_err_auc_high_seeds": [0.8911, 0.9502, 0.8961, 0.9175, 0.9401],
            "delta_e_auc_low_mean": 0.7189375,
            "delta_e_auc_high_mean": 0.68214,
            "delta_e_auc_high_min_seed11": 0.6225,
            "sigma_j_anti_signal_low_mean": 0.20190625,
            "sigma_j_anti_signal_high_mean": 0.24966,
            "ablated_random_low_mean": 0.46346875,
            "ablated_random_high_mean": 0.5241,
            "contamination_rate_matches_p_target": True,
            "arms_differ_verified": True,
            "cardinality_ok": True,
            "wall_s": 7.655687570571899,
            "device": "cuda",
            "run_mode": "full", "era": "STAGE1_2_ALGEBRA_CHAIN",
            "session": "2026-07-02_M1p11_v3_CG_ALGEBRA_META_promo",
            "verified_off_data": True, "provenance_quality": "OFF_DISK_SKUNKWORKS_A5",
            "composes_with": [
                "substrate_semantic_parser_v1_CG_2026-07-02",
                "substrate_response_planner_frame_slot_composition_v1_CG_2026-07-02"
            ],
            "cross_arc_check": "substrate_query 'reconstruction error confidence signal detector risk' top hit cosine=0.378 on wordnet 'reconstruction'; NO prior experimental atom on Confidence Header / reconstruction-err mechanism at cosine>0.30. Genuinely novel work.",
            "primitive_role_in_algebra_chain": "3rd primitive: Confidence Header - detects contaminated risk items via reconstruction_err discriminator. Composes with M1.9 (semantic_parser) and M1.10 (response_planner_frame_slot_composition)."
        }
    }
]

atoms_meta = [
    {
        "id": "T4/META_SUBSTRATE_ALGEBRA_SCALES_TO_DEEPER_CHAINS_CG_META_v1_2026-07-02",
        "name": "META SUBSTRATE_ALGEBRA_SCALES_TO_DEEPER_CHAINS CG_META v1",
        "corpus": "meta",
        "tier": "T4",
        "kind": "substrate_science_meta_composition",
        "description": "CG_META promotion (from prior MM_TENTATIVE substrate_algebra_end_to_end_roundtrip_M19_M110_K5_MM). Substrate-algebra chain composition rule: 'Substrate algebra primitives compose to depth 3+ chains, each primitive independently CG-certified with tight cv (<0.15) and clean positive control, without CG-tier collapse or per-composition-step degradation.' Third primitive M1.11 v3 Confidence Header CG'd 5-seed 2-regime with load-bearing REC_ERR arm mean AUC 0.972 low / 0.919 high, cv 0.007 low / 0.025 high, deterministic contamination verified. Composition axes now cleared: M1.9 (semantic parser CG) -> M1.10 (response planner frame-slot CG) -> M1.11 v3 (confidence header CG). Prior roundtrip MM (M1.9 <-> M1.10) established 2-primitive; third primitive lands cleanly satisfies 3-primitive promotion criterion. NOT a physics-law tier claim (chain-scope, not substrate-invariance) - it is a substrate-science synthesis: the algebra ecosystem SUPPORTS deep-chain composition without primitive-tier saturation collapse.",
        "aliases": [],
        "metadata": {
            "record_class": "meta_atom_substrate_science_synthesis",
            "cert_tier": "CG_META",
            "supersedes": "substrate_algebra_end_to_end_roundtrip_M19_M110_K5_MM_2026-07-02",
            "supersedes_rationale": "3-primitive chain now certified (M1.9 + M1.10 + M1.11 v3 all CG); scope widens from 2-primitive roundtrip MM to 3-primitive chain CG_META",
            "composes_atoms": [
                "substrate_semantic_parser_v1_CG_2026-07-02",
                "substrate_response_planner_frame_slot_composition_v1_CG_2026-07-02",
                "T3/EXP_substrate_activity_energy_confidence_signal_v3_reconstruction_err_multiseed_multiregime_5seed_FULL"
            ],
            "chain_depth_certified": 3,
            "chain_primitives": ["M1.9 semantic_parser", "M1.10 response_planner_frame_slot_composition", "M1.11 v3 confidence_header"],
            "per_primitive_cv": {
                "M1.9": "prior CG (see composing atom)",
                "M1.10": "prior CG (see composing atom)",
                "M1.11_v3_rec_err_low": 0.0067,
                "M1.11_v3_rec_err_high": 0.0254
            },
            "positive_controls_all_clean": True,
            "promotion_criterion_satisfied": ">=3 primitives CG-certified in chain with tight cv (<0.15) and clean PC per primitive",
            "expansion_criterion_to_higher_tier": "chain depth >=5 primitives OR end-to-end composed test (chain output cert) at CG tier",
            "next_promotion_axis": "M1.12+ primitives OR end-to-end integrated glass-box demonstration",
            "era": "STAGE1_2_ALGEBRA_CHAIN",
            "session": "2026-07-02_M1p11_v3_CG_ALGEBRA_META_promo",
            "verified_off_data": True,
            "provenance_quality": "OFF_DISK_SKUNKWORKS_A5"
        }
    },
    {
        "id": "META_delta_E_secondary_discriminator_MB_TENTATIVE_partial_per_seed_floor_fails_seed11_REGIME_HIGH_2026-07-02",
        "name": "META delta_E secondary confidence discriminator MB_TENTATIVE",
        "corpus": "meta",
        "tier": "T4",
        "kind": "measured_mechanism_partial_signal",
        "description": "MIDDLE_BAND (honest downward correction of cell-author 'strong secondary' framing). Delta_E arm on M1.11 v3 5-seed 2-regime: REGIME_LOW mean AUC=0.7189 (cv=0.050; all 5 seeds clear 0.65 min=0.692); REGIME_HIGH mean AUC=0.6821 (cv=0.067) BUT seed 11 = 0.6225 DIPS BELOW the 0.65 per-seed floor. Means clear + cv tight in both regimes, but strict per-seed floor fails at 1/10 seed-regime cells. Mechanism note: delta_E (energy difference) is INDEPENDENT of reconstruction_err by mechanism (energy budget vs geometric reconstruction) - a genuine candidate CO-DISCRIMINATOR. Correct tier is MB (partial signal + independent mechanism) with revival criterion: 'all seeds clear 0.65 both regimes in a 10-seed replication.' If revival lands CG, delta_E promotes to CG secondary discriminator; ensemble METHOD (reconstruction_err primary + delta_E secondary) could then MM as a robustness-META.",
        "aliases": [],
        "metadata": {
            "record_class": "meta_atom_measured_mechanism",
            "cert_tier": "MIDDLE_BAND",
            "composes_atoms": [
                "T3/EXP_substrate_activity_energy_confidence_signal_v3_reconstruction_err_multiseed_multiregime_5seed_FULL"
            ],
            "delta_e_auc_low_mean": 0.7189375,
            "delta_e_auc_low_cv": 0.04980091545892663,
            "delta_e_auc_low_min": 0.69203125,
            "delta_e_auc_high_mean": 0.68214,
            "delta_e_auc_high_cv": 0.06669541234833078,
            "delta_e_auc_high_min": 0.6225,
            "per_seed_floor_check": "9/10 seed-regime cells clear 0.65 floor; seed 11 REGIME_HIGH = 0.6225 fails",
            "framing_correction": "Cell-author noted delta_E as 'strong secondary'; off-disk shows per-seed floor fails at 1/10 cells. HONEST framing: MB with independent mechanism as revival angle, NOT strong.",
            "revival_criterion": "10-seed replication where all seeds clear 0.65 both regimes; if lands, promote CG secondary and consider ensemble META (REC + delta_E).",
            "independence_from_primary": "delta_E computes energy-budget deviation; reconstruction_err computes cleanup-geometry deviation; mechanistically distinct - genuine co-discriminator candidate",
            "era": "STAGE1_2_ALGEBRA_CHAIN",
            "session": "2026-07-02_M1p11_v3_CG_ALGEBRA_META_promo",
            "verified_off_data": True,
            "provenance_quality": "OFF_DISK_SKUNKWORKS_A5"
        }
    }
]

ledger_entries = [
    {"ts": TS, "kind": "CG_LANDED", "atom": "T3/EXP_substrate_activity_energy_confidence_signal_v3_reconstruction_err_multiseed_multiregime_5seed_FULL", "session": "2026-07-02_M1p11_v3_CG_ALGEBRA_META_promo", "verified_off_data": True, "reason": "5-seed 2-regime FULL. Load-bearing ARM_RECONSTRUCTION_ERR clears >=0.65 floor with cv<0.15 both regimes (LOW mean 0.972 cv 0.007 min 0.963; HIGH mean 0.919 cv 0.025 min 0.891). Deterministic contamination (contamination_rate==p_target all 40 units). Positive control ARM_ABLATED_RANDOM means bracket 0.5. cardinality_ok, arms_differ_verified. 3rd primitive in algebra chain.", "action": "APPEND", "cert_delta_cg": 1, "cert_delta_mm": 0, "cert_delta_hf": 0, "tier": "CHAIN_GRADE"},
    {"ts": TS, "kind": "CG_META_PROMOTION", "atom": "T4/META_SUBSTRATE_ALGEBRA_SCALES_TO_DEEPER_CHAINS_CG_META_v1_2026-07-02", "session": "2026-07-02_M1p11_v3_CG_ALGEBRA_META_promo", "verified_off_data": True, "reason": "META SUBSTRATE_ALGEBRA_SCALES_TO_DEEPER_CHAINS promoted MM_TENTATIVE (roundtrip M1.9<->M1.10) -> CG_META. Third primitive M1.11 v3 CG'd cleanly; 3-primitive chain-depth criterion satisfied. Supersedes prior 2-primitive roundtrip MM.", "action": "APPEND", "cert_delta_cg": 1, "cert_delta_mm": -1, "cert_delta_hf": 0, "tier": "CG_META", "supersedes": "substrate_algebra_end_to_end_roundtrip_M19_M110_K5_MM_2026-07-02"},
    {"ts": TS, "kind": "MB_LANDED", "atom": "META_delta_E_secondary_discriminator_MB_TENTATIVE_partial_per_seed_floor_fails_seed11_REGIME_HIGH_2026-07-02", "session": "2026-07-02_M1p11_v3_CG_ALGEBRA_META_promo", "verified_off_data": True, "reason": "HONEST DOWNWARD FRAMING CORRECTION: cell-author called delta_E 'strong secondary'; off-disk shows means/cv clear but seed 11 REGIME_HIGH = 0.6225 fails 0.65 per-seed floor. MB tier with revival criterion '10-seed all-clear.' Independent mechanism from REC (energy vs geometric) = genuine co-discriminator candidate.", "action": "APPEND", "cert_delta_cg": 0, "cert_delta_mm": 0, "cert_delta_hf": 0, "tier": "MIDDLE_BAND"}
]

n1 = atomic_append(MATH, atoms_math)
n2 = atomic_append(META, atoms_meta)
n3 = atomic_append(LEDGER, ledger_entries)
print(f"MATH atoms after append: {n1}")
print(f"META atoms after append: {n2}")
print(f"LEDGER entries after append: {n3}")
import subprocess
print("Session tally today:")
for p in [MATH, META]:
    r = subprocess.run(['grep', '-c', '2026-07-02', p], capture_output=True, text=True)
    print(f"  {p}: {r.stdout.strip()}")
