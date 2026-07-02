"""Skunkworks A5-gated atomize: 2026-07-02 TOPOLOGY_FREE META promotion.

Landings:
  1. sharded_fhrr_topology_free_multi_f_dag_v1 3-seed FULL (seeds 7/13/19; CG)
     - Extends prior F=4-only DAG CG to multi-F sweep {1,2,4,8,MIXED}
  2. META STORAGE_STRATEGY promoted SCALE_FREE -> SCALE_FREE_AND_TOPOLOGY_FREE
     - Third axis (topology/DAG structure) cleared: 4 distinct DAG variants
       (F=2, F=4, F=8, F=MIXED) x 3 seeds = 12 HP landings all sharded=1.0

Verified off-disk (per-arm, not verdict text):
  - Gate D per seed 7/13/19: SHARDED>=0.85 all F variants (all=1.000);
    F=8 BUNDLE {0.000, 0.000, 0.005} < 0.10; F=1 PC {1.0, 1.0, 1.0} >= 0.85
  - Cross-seed cv @ NPROP=5000:
      F=2 SHARDED: [1,1,1] cv=0.0    BUNDLE: [0.015,0.005,0.005]  mean 0.0083
      F=4 SHARDED: [1,1,1] cv=0.0    BUNDLE: [0.000,0.000,0.000]  mean 0.0000
      F=8 SHARDED: [1,1,1] cv=0.0    BUNDLE: [0.000,0.000,0.005]  mean 0.0017
      F=MIXED SHARDED: [1,1,1] cv=0.0 BUNDLE: [0.010,0.000,0.000] mean 0.0033
  - sharded_hash distinct across all 4 F variants per seed (12 distinct hashes total)
    - no by-construction saturation collapse; each F variant runs distinct mechanism
  - Cross-arc concept overlap check: top hit cosine=0.29 on 'Storage' (chunk_note);
    NO prior TOPOLOGY_FREE or multi-F DAG atom at cosine>0.30. Genuinely novel extension.

Composes with (Storage-Strategy META lineage):
  - T3/EXP_sharded_fhrr_cleanup_capacity_beyond_bundle_bound_v1 (single-hop axis)
  - T3/EXP_math4_proof_chains_v2_global_bundle_cpu_v1 (moderate chain axis)
  - T3/EXP_math4_rung3_deep_chains_v2_global_bundle_cpu_v1 (deep chain axis)
  - T3/EXP_sharded_fhrr_topology_free_dag_extension_v1_3seed (F=4 DAG axis; this session)
  - T4/META_STORAGE_STRATEGY_COMPOSITION_DEPTH_PHYSICS_LAW_v1 (prior META composition)
  - T4/META_STORAGE_STRATEGY_SCALE_FREE_PHYSICS_LAW_v1 (SCALE_FREE promotion)

Promotion criterion (per prior META atom): >=3 distinct DAG variants at multi-seed HP.
Satisfied: 4 distinct DAG variants (F=2, F=4, F=8, F=MIXED) x 3 seeds all HP.
Additionally: F=1 (linear) coverage at 3 seeds all sharded=1.000 (positive control clean).
"""
import json, os, tempfile

MATH = "d:/AI/hd-instrument/data/substrate_index/math/atoms.jsonl"
META = "d:/AI/hd-instrument/data/substrate_index/meta/atoms.jsonl"
LEDGER = "d:/AI/hd-instrument/data/substrate_index/meta/cert_ledger.jsonl"
TS = "2026-07-02T21:00:00Z"

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
        "id": "T3/EXP_sharded_fhrr_topology_free_multi_f_dag_v1_3seed_FULL",
        "name": "EXP sharded_fhrr_topology_free_multi_f_dag_v1 3seed FULL",
        "corpus": "math",
        "tier": "T3",
        "kind": "experiment_record",
        "description": "CHAIN_GRADE 3-seed FULL. Extends prior F=4-only DAG CG to full multi-F sweep {F=1, F=2, F=4, F=8, F=MIXED} at NPROP {200, 1000, 5000}, N=8192. SHARDED acc=1.000 flat across ALL 15 F-x-NPROP cells x 3 seeds (45 units observed, all HARD_PASS). Gate D verified per seed: SHARDED>=0.85 all {F=2,4,8,MIXED} at NPROP_max (all 1.000); F=8 BUNDLE {0.000, 0.000, 0.005} all < 0.10; F=1 positive control 1.000 all seeds. Cross-seed cv on canonical SHARDED metric = 0.000. BUNDLE @NPROP=5000 mean across seeds: F=2=0.0083, F=4=0.0000, F=8=0.0017, F=MIXED=0.0033 (all noise-floor). Sharded_hash distinct across 4 F variants per seed (12 distinct hashes) confirms no by-construction saturation. Walls 6.10/7.09/7.18s on cuda.",
        "aliases": [],
        "metadata": {
            "record_class": "experiment_record",
            "term_class": "PROCESS_KNOWLEDGE_NON_MATH",
            "experiment_path": "experiments/exp_sharded_fhrr_topology_free_multi_f_dag_v1.py",
            "metrics_paths": [
                "data/exp_sharded_fhrr_topology_free_multi_f_dag_v1_seed_7/metrics.json",
                "data/exp_sharded_fhrr_topology_free_multi_f_dag_v1_seed_13/metrics.json",
                "data/exp_sharded_fhrr_topology_free_multi_f_dag_v1_seed_19/metrics.json"
            ],
            "verdict": "PASS", "verdict_raw": "HARD_PASS", "cert_tier": "CHAIN_GRADE",
            "n_seeds": 3, "N": 8192, "n_units": 15,
            "F_grid": ["1", "2", "4", "8", "MIXED"],
            "NPROP_grid": [200, 1000, 5000],
            "NPROP_max": 5000, "bundle_bound_approx": 1147,
            "sharded_at_max_all_variants": {"F=2": [1.0,1.0,1.0], "F=4": [1.0,1.0,1.0], "F=8": [1.0,1.0,1.0], "F=MIXED": [1.0,1.0,1.0]},
            "bundle_at_max_all_variants": {"F=2": [0.015,0.005,0.005], "F=4": [0.0,0.0,0.0], "F=8": [0.0,0.0,0.005], "F=MIXED": [0.01,0.0,0.0]},
            "f1_positive_control": [1.0, 1.0, 1.0],
            "gate_D_verified_per_seed": True,
            "cv_sharded_across_seeds_at_max": 0.0,
            "arms_differ_verified": True,
            "cardinality_ok": True,
            "walls_s": [6.10, 7.09, 7.18],
            "device": "cuda",
            "run_mode": "full", "era": "STAGE1_2_STORAGE_STRATEGY_TOPOLOGY", "session": "2026-07-02_topology_free_META_promo",
            "verified_off_data": True, "provenance_quality": "OFF_DISK_SKUNKWORKS_A5",
            "composes_with": [
                "T3/EXP_sharded_fhrr_topology_free_dag_extension_v1_3seed"
            ],
            "cross_arc_check": "substrate_query 'TOPOLOGY_FREE storage strategy DAG multi-F sharded FHRR' top hit cosine=0.29 on 'Storage' chunk_note; NO prior TOPOLOGY_FREE or multi-F DAG atom at cosine>0.30. Genuinely novel extension."
        }
    }
]

atoms_meta = [
    {
        "id": "T4/META_STORAGE_STRATEGY_SCALE_FREE_AND_TOPOLOGY_FREE_PHYSICS_LAW_v1",
        "name": "META storage_strategy SCALE_FREE_AND_TOPOLOGY_FREE physics_law v1",
        "corpus": "meta",
        "tier": "T4",
        "kind": "physics_law_meta_composition",
        "description": "CHAIN_GRADE_SUBSTRATE_PHYSICS_LAW. Third-axis promotion. Composition axes now closed: (1) NPROP scale (single-hop, moderate, deep), (2) N scale (SCALE_FREE promotion, prior META), (3) DAG topology (this promotion). Substrate-physics-law statement: 'SHARDED rule-storage in FHRR sustains matched-filter cleanup accuracy=1.000 INDEPENDENT of NPROP up to at least 1.95x N (single-hop) AND INDEPENDENT of composition depth L up to L=20 (chain-composition) AND INDEPENDENT of N scale (SCALE_FREE) AND INDEPENDENT of DAG topology across F in {1, 2, 4, 8, MIXED} multi-source aggregation (TOPOLOGY_FREE), while BUNDLED positive control collapses within Plate 1995 0.14*N bundle-capacity bound in every regime.' Promotion evidence: 4 distinct DAG variants (F=2, F=4, F=8, F=MIXED) x 3 seeds all HP (>=3 distinct DAG variants at multi-seed HP; promotion criterion satisfied). Cross-seed cv=0.000 on canonical metric.",
        "aliases": [],
        "metadata": {
            "record_class": "meta_atom_physics_law",
            "cert_tier": "CHAIN_GRADE_SUBSTRATE_PHYSICS_LAW",
            "supersedes": "T4/META_STORAGE_STRATEGY_SCALE_FREE_PHYSICS_LAW_v1",
            "supersedes_rationale": "Third axis (DAG topology) now cleared; law scope extended without invalidating scale-free evidence",
            "composes_atoms": [
                "T3/EXP_sharded_fhrr_cleanup_capacity_beyond_bundle_bound_v1",
                "T3/EXP_math4_proof_chains_v2_global_bundle_cpu_v1",
                "T3/EXP_math4_rung3_deep_chains_v2_global_bundle_cpu_v1",
                "T3/EXP_sharded_fhrr_topology_free_dag_extension_v1_3seed",
                "T3/EXP_sharded_fhrr_topology_free_multi_f_dag_v1_3seed_FULL",
                "T4/META_STORAGE_STRATEGY_COMPOSITION_DEPTH_PHYSICS_LAW_v1",
                "T4/META_STORAGE_STRATEGY_SCALE_FREE_PHYSICS_LAW_v1"
            ],
            "regime_coverage": [
                "single_hop_NPROP_1_to_1.95N",
                "moderate_chain_L_2_to_10",
                "deep_chain_L_4_to_20",
                "SCALE_FREE_N_axis",
                "TOPOLOGY_FREE_DAG_F_in_1_2_4_8_MIXED"
            ],
            "canonical_metric": "sharded_acc",
            "canonical_metric_value": 1.0,
            "cv_across_topology_landings": 0.0,
            "positive_control": "BUNDLED collapses < Plate 0.14*N bound in all F variants",
            "promotion_criterion_satisfied": ">=3 distinct DAG variants at multi-seed HP; observed 4 (F=2,4,8,MIXED) at 3 seeds",
            "next_promotion_axis": "cross-domain generalization (non-FHRR backend or non-cleanup-based readout) to check law transfers off algebraic-substrate class",
            "era": "STAGE1_2_STORAGE_STRATEGY_TOPOLOGY",
            "session": "2026-07-02_topology_free_META_promo",
            "verified_off_data": True,
            "provenance_quality": "OFF_DISK_SKUNKWORKS_A5"
        }
    }
]

ledger_entries = [
    {"ts": TS, "kind": "CG_LANDED", "atom": "T3/EXP_sharded_fhrr_topology_free_multi_f_dag_v1_3seed_FULL", "session": "2026-07-02_topology_free_META_promo", "verified_off_data": True, "reason": "3-seed FULL Gate D verified per seed: SHARDED=1.000 all {F=1,2,4,8,MIXED} x {NPROP 200,1000,5000}; F=8 BUNDLE {0,0,0.005}<0.10; F=1 PC 1.000; distinct sharded_hash across 4 F variants (no by-construction collapse); cv_sharded=0.0", "action": "APPEND", "cert_delta_cg": 1, "cert_delta_mm": 0, "cert_delta_hf": 0, "tier": "CHAIN_GRADE"},
    {"ts": TS, "kind": "CG_META_PROMOTION", "atom": "T4/META_STORAGE_STRATEGY_SCALE_FREE_AND_TOPOLOGY_FREE_PHYSICS_LAW_v1", "session": "2026-07-02_topology_free_META_promo", "verified_off_data": True, "reason": "META STORAGE_STRATEGY promoted SCALE_FREE -> SCALE_FREE_AND_TOPOLOGY_FREE. Third axis (DAG topology) cleared: 4 distinct DAG variants x 3 seeds all HP. Supersedes prior SCALE_FREE_PHYSICS_LAW META (scope-widening, not evidence-invalidating).", "action": "APPEND", "cert_delta_cg": 1, "cert_delta_mm": 0, "cert_delta_hf": 0, "tier": "CHAIN_GRADE_SUBSTRATE_PHYSICS_LAW", "supersedes": "T4/META_STORAGE_STRATEGY_SCALE_FREE_PHYSICS_LAW_v1"}
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
