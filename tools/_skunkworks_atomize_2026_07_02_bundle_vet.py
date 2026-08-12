"""Skunkworks A5-gated atomize: 2026-07-02 bundle VET.

Landings:
  1. sharded_fhrr_cleanup_capacity_beyond_bundle_bound_v1 (3 seeds; CG)
  2. math4_proof_chains_v2_global_bundle_cpu_v1 (3 seeds; CG)
  3. math4_rung3_deep_chains_v2_global_bundle_cpu_v1 (3 seeds; CG)
  4. stretch4_3_temporal_strips_v2_substrate_native_planner_cpu_v1 (1 seed FULL; CG)
  5. META composition of 1+2+3 -> substrate-physics-law CG (storage-strategy across composition-depth axis)
  6. AMEND-DEMOTE prior stretch4_3_temporal_strips_cpu_v1 (v1 plan_rate=1.000 exposed as bogus)

Verified off-disk:
  - sharded seeds {7,13,19}: sharded=1.0 flat @ NPROP 200..16000 (=1.95*N=8192); bundle collapses (0.045/0.075/0.065 @ NPROP=4000 vs Plate 0.14*N=1147 bound; ~13.9x beyond)
  - math4_v2 seeds {7,13,19}: cardinality_ok=T; arms_differ=T; SHARDED=1.0 all cells; storage_gap=1.0 (cv=0.0000); chain_degrad {0.55,0.48,0.55} cv=0.077; crits I/II/III T all seeds
  - math4_rung3_v2 seeds {7,13,19}: cardinality_ok=T; arms_differ=T; SHARDED=1.0 all cells; storage_gap {0.98,0.96,1.00} cv=0.020; chain_degrad {0.61,0.48,0.57} cv=0.120; crits I/II/III T all seeds; L extends 10->20
  - stretch4_3 v2: sub=sym=0.513 bit-identical (arms_differ=False by verdict-logic DESIGN); pre/add/del p/r=1.000; n=150, n_solvable=77; symbolic in-band [0.30,0.85]; wall 1.25s; substrate hosts temporal STRIPS
  - CROSS-ARC concept-overlap check: top hit cosine=0.4336 on 'Bundle storage' from ingest-optimization note (NOT prior chain-grade atom); c_composition_storage_density_v1 pre-reg (cosine 0.35) filed but NO PRIOR ATOM landed -> new work is targeted resolution not rediscovery.
"""
import json, os, tempfile, hashlib, time

MATH = "d:/AI/hd-instrument/data/substrate_index/math/atoms.jsonl"
META = "d:/AI/hd-instrument/data/substrate_index/meta/atoms.jsonl"
LEDGER = "d:/AI/hd-instrument/data/substrate_index/meta/cert_ledger.jsonl"
TS = "2026-07-02T15:30:00Z"

def atomic_append(path, records):
    """Load-verify + atomic append via tmp+os.replace."""
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
    # verify-load
    with open(path, 'r', encoding='utf-8') as f:
        n = sum(1 for L in f if L.strip())
    assert n == len(combined), f"append verify FAIL {path}: expected {len(combined)} got {n}"
    return n

atoms_math = [
    {
        "id": "T3/EXP_sharded_fhrr_cleanup_capacity_beyond_bundle_bound_v1",
        "name": "EXP sharded_fhrr_cleanup_capacity_beyond_bundle_bound_v1",
        "corpus": "math",
        "tier": "T3",
        "kind": "experiment_record",
        "description": "CHAIN_GRADE 3-seed FULL. Sharded FHRR rule-storage sustains PERFECT cleanup (acc=1.000 flat NPROP 200..16000, 1.95x N=8192) while positive-control BUNDLED collapses to 0.045/0.075/0.065 at NPROP=4000 (well below Plate 1995 0.14*N~1147 bound). Extends single-hop cleanup capacity ~13.9x beyond classical bundle bound. Positive control fires as predicted; discriminator cleanly separates storage strategies. Cross-seed cv on bundle@collapse 0.248 (noise-floor variance; expected on collapsed arm); sharded arm bit-flat at 1.0.",
        "aliases": [],
        "metadata": {
            "record_class": "experiment_record", "term_class": "PROCESS_KNOWLEDGE_NON_MATH",
            "experiment_path": "cells/sharded_fhrr_cleanup_capacity_beyond_bundle_bound_v1.py",
            "metrics_paths": [
                "data/exp_sharded_fhrr_cleanup_capacity_beyond_bundle_bound_v1_seed_7/metrics.json",
                "data/exp_sharded_fhrr_cleanup_capacity_beyond_bundle_bound_v1_seed_13/metrics.json",
                "data/exp_sharded_fhrr_cleanup_capacity_beyond_bundle_bound_v1_seed_19/metrics.json"
            ],
            "verdict": "PASS", "verdict_raw": "HARD_PASS", "cert_tier": "CHAIN_GRADE",
            "n_seeds": 3, "N": 8192, "max_nprop": 16000, "plate_bound_approx": 1147, "extension_ratio": 13.9,
            "sharded_acc_flat": 1.0, "bundle_at_collapse": [0.045, 0.075, 0.065],
            "cv_bundle_collapse": 0.2477, "cv_sharded": 0.0,
            "run_mode": "full", "era": "STAGE1_CAPACITY", "session": "2026-07-02_bundle_vet",
            "verified_off_data": True, "provenance_quality": "OFF_DISK_SKUNKWORKS_A5",
            "cross_arc_check": "top hit cosine 0.4336 'Bundle storage' from ingest-optimization note (not prior CG atom); c_composition_storage_density_v1 pre-reg filed no landed atom -> NOT rediscovery"
        }
    },
    {
        "id": "T3/EXP_math4_proof_chains_v2_global_bundle_cpu_v1",
        "name": "EXP math4_proof_chains_v2_global_bundle_cpu_v1",
        "corpus": "math",
        "tier": "T3",
        "kind": "experiment_record",
        "description": "CHAIN_GRADE 3-seed FULL. STORAGE-STRATEGY drives chain-composition survival at moderate L=2..10 over NPROP=20..500. SHARDED acc=1.000 flat across ALL 25 cells x 3 seeds (75 units observed, cardinality_ok=T, arms_differ=T). Storage-gap SHARDED-BUNDLED @ (L=10, NPROP=500) = 1.000 all 3 seeds (cv=0.0000). Chain-degradation BUNDLED_L1 - BUNDLED_L=10 = {0.55, 0.48, 0.55} cv=0.077 (single-hop bundle nonzero; multi-hop bundle collapses). Crit I/II/III TRUE all seeds. Positive control (bundled) collapses as predicted.",
        "aliases": [],
        "metadata": {
            "record_class": "experiment_record", "term_class": "PROCESS_KNOWLEDGE_NON_MATH",
            "experiment_path": "cells/math4_proof_chains_v2_global_bundle_cpu_v1.py",
            "metrics_paths": [
                "data/exp_math4_proof_chains_v2_global_bundle_cpu_v1_seed_7/metrics.json",
                "data/exp_math4_proof_chains_v2_global_bundle_cpu_v1_seed_13/metrics.json",
                "data/exp_math4_proof_chains_v2_global_bundle_cpu_v1_seed_19/metrics.json"
            ],
            "verdict": "PASS", "verdict_raw": "HARD_PASS", "cert_tier": "CHAIN_GRADE",
            "n_seeds": 3, "N": 8192, "L_max": 10, "NPROP_max": 500, "TR": 100,
            "storage_gap_at_max": [1.0, 1.0, 1.0], "chain_degrad_gaps": [0.55, 0.48, 0.55],
            "cv_storage_gap": 0.0, "cv_chain_degrad": 0.0767,
            "crit_I_II_III_all_seeds": True, "arms_differ_verified": True, "cardinality_ok": True,
            "n_units_observed": 75, "expected_n_units": 75,
            "run_mode": "full", "era": "STAGE2_COMPOSITION", "session": "2026-07-02_bundle_vet",
            "verified_off_data": True, "provenance_quality": "OFF_DISK_SKUNKWORKS_A5",
            "composes_with": ["T3/EXP_sharded_fhrr_cleanup_capacity_beyond_bundle_bound_v1"]
        }
    },
    {
        "id": "T3/EXP_math4_rung3_deep_chains_v2_global_bundle_cpu_v1",
        "name": "EXP math4_rung3_deep_chains_v2_global_bundle_cpu_v1",
        "corpus": "math",
        "tier": "T3",
        "kind": "experiment_record",
        "description": "CHAIN_GRADE 3-seed FULL. Extends math4_v2 (L<=10) to DEEP L=4..20 over NPROP=10..100. SHARDED acc=1.000 flat across ALL 20 cells x 3 seeds (60 units observed, cardinality_ok=T, arms_differ=T). Storage-gap SHARDED-BUNDLED @ (L=20, NPROP=100) = {0.98, 0.96, 1.00} cv=0.020. Chain-degradation BUNDLED_L1 - BUNDLED_L=20 = {0.61, 0.48, 0.57} cv=0.120. Crit I/II/III TRUE all seeds AT DEEP L. Substrate holds sharded rule-storage independent of composition depth up to L=20.",
        "aliases": [],
        "metadata": {
            "record_class": "experiment_record", "term_class": "PROCESS_KNOWLEDGE_NON_MATH",
            "experiment_path": "cells/math4_rung3_deep_chains_v2_global_bundle_cpu_v1.py",
            "metrics_paths": [
                "data/exp_math4_rung3_deep_chains_v2_global_bundle_cpu_v1_seed_7/metrics.json",
                "data/exp_math4_rung3_deep_chains_v2_global_bundle_cpu_v1_seed_13/metrics.json",
                "data/exp_math4_rung3_deep_chains_v2_global_bundle_cpu_v1_seed_19/metrics.json"
            ],
            "verdict": "PASS", "verdict_raw": "HARD_PASS", "cert_tier": "CHAIN_GRADE",
            "n_seeds": 3, "N": 8192, "L_max": 20, "NPROP_max": 100, "TR": 100,
            "storage_gap_at_max": [0.98, 0.96, 1.0], "chain_degrad_gaps": [0.61, 0.48, 0.57],
            "cv_storage_gap": 0.0204, "cv_chain_degrad": 0.1203,
            "crit_I_II_III_all_seeds_deep_L": True, "arms_differ_verified": True, "cardinality_ok": True,
            "n_units_observed": 60, "expected_n_units": 60,
            "run_mode": "full", "era": "STAGE2_COMPOSITION", "session": "2026-07-02_bundle_vet",
            "verified_off_data": True, "provenance_quality": "OFF_DISK_SKUNKWORKS_A5",
            "composes_with": ["T3/EXP_math4_proof_chains_v2_global_bundle_cpu_v1"],
            "closes_gap": "c_composition_storage_density_v1 pre-reg SNR-Decay-in-Deep-Composition HF (never atomized; resolved by this cell)"
        }
    },
    {
        "id": "T3/EXP_stretch4_3_temporal_strips_v2_substrate_native_planner_cpu_v1",
        "name": "EXP stretch4_3_temporal_strips_v2_substrate_native_planner_cpu_v1",
        "corpus": "math",
        "tier": "T3",
        "kind": "experiment_record",
        "description": "CHAIN_GRADE single-seed FULL (path A rescue). Substrate-native temporal STRIPS planner via FHRR unbind+cleanup over sharded action-schema library at N=8192. FHRR recovers ALL pre/add/del action-schema sets EXACTLY (p/r=1.000 mean across 150 trials). Substrate-native BFS produces BIT-IDENTICAL plans to symbolic BFS (sub=sym=0.513 gap=0.000; plans digest match d3ec...5706). Symbolic plan-rate 0.513 in [0.30, 0.85] band on non-oracle goals (n_solvable=77/150). Wall 1.25s. arms_differ_verified=False by DESIGN — bit-identity IS the substrate-native-equivalence proof; this is not the standard 'no differentiation' failure mode. Rescues stretch4_3 v1 (numpy-costume, oracle-goal defect exposed).",
        "aliases": [],
        "metadata": {
            "record_class": "experiment_record", "term_class": "PROCESS_KNOWLEDGE_NON_MATH",
            "experiment_path": "cells/stretch4_3_temporal_strips_v2_substrate_native_planner_cpu_v1.py",
            "metrics_paths": ["data/exp_stretch4_3_temporal_strips_v2_substrate_native_planner_cpu_v1/metrics.json"],
            "verdict": "PASS", "verdict_raw": "HARD_PASS_SUBSTRATE_NATIVE_EQUIVALENCE", "cert_tier": "CHAIN_GRADE",
            "n_seeds": 1, "N": 8192, "n_trials": 150, "n_solvable": 77,
            "sub_plan_rate": 0.5133, "sym_plan_rate": 0.5133, "gap": 0.0,
            "sub_pre_precision": 1.0, "sub_pre_recall": 1.0,
            "sub_add_precision": 1.0, "sub_add_recall": 1.0,
            "sub_del_precision": 1.0, "sub_del_recall": 1.0,
            "sub_plans_digest": "400f32d87ee3841dbf5e60e48e835706",
            "sym_plans_digest": "400f32d87ee3841dbf5e60e48e835706",
            "wall_s": 1.25,
            "arms_differ_verified": False,
            "arms_differ_rationale_ok": "bit-identical sub/sym IS the substrate-native-equivalence proof (verdict-logic distinguishes; not standard no-differentiation failure)",
            "run_mode": "full", "era": "STAGE3_HIGHER_FUNCTIONS", "session": "2026-07-02_bundle_vet",
            "verified_off_data": True, "provenance_quality": "OFF_DISK_SKUNKWORKS_A5",
            "supersedes": "T3/EXP_stretch4_3_temporal_strips_cpu_v1 (see AMEND-DEMOTE ledger entry)"
        }
    }
]

atoms_meta = [
    {
        "id": "T4/META_STORAGE_STRATEGY_COMPOSITION_DEPTH_PHYSICS_LAW_v1",
        "name": "META storage_strategy_composition_depth_physics_law_v1",
        "corpus": "meta",
        "tier": "T4",
        "kind": "physics_law_meta_composition",
        "description": "CHAIN_GRADE_SUBSTRATE_PHYSICS_LAW. 3-cell composition maps SHARDED-vs-BUNDLED storage-strategy across the composition-depth axis: (single-hop, moderate-chain, deep-chain). Substrate-physics-law statement: 'SHARDED rule-storage in FHRR sustains perfect matched-filter cleanup accuracy=1.000 INDEPENDENT of NPROP up to 1.95x N (single-hop, N=8192) AND INDEPENDENT of composition depth L up to L=20 (chain-composition), while BUNDLED storage collapses within Plate 1995 0.14*N bundle-capacity bound.' Positive control (bundle collapse) fires cleanly in all 3 regimes. Cross-seed cv on canonical metric (sharded=1.000) is 0.0; cv on bundle-collapse noise-floor is regime-dependent 0.05-0.25 (all consistent with noise-floor). This is a load-bearing storage-strategy separation result for M3 cortex composition-depth guarantees.",
        "aliases": [],
        "metadata": {
            "record_class": "meta_atom_physics_law",
            "cert_tier": "CHAIN_GRADE_SUBSTRATE_PHYSICS_LAW",
            "composes_atoms": [
                "T3/EXP_sharded_fhrr_cleanup_capacity_beyond_bundle_bound_v1",
                "T3/EXP_math4_proof_chains_v2_global_bundle_cpu_v1",
                "T3/EXP_math4_rung3_deep_chains_v2_global_bundle_cpu_v1"
            ],
            "regime_coverage": ["single_hop_NPROP_1_to_1.95N", "moderate_chain_L_2_to_10", "deep_chain_L_4_to_20"],
            "canonical_metric": "sharded_acc",
            "canonical_metric_value": 1.0,
            "cv_across_all_9_landings": 0.0,
            "positive_control": "BUNDLED collapses < Plate 0.14*N bound in all regimes",
            "extension_criterion_for_LAW_scale_free": "test at N=32768 and N=1M (commercial scale) to close 4th regime dimension",
            "extension_criterion_for_LAW_topology_free": "test at branching / DAG chain topology (non-linear composition) to close 5th regime dimension",
            "era": "STAGE1_2_COMPOSITION",
            "session": "2026-07-02_bundle_vet",
            "verified_off_data": True,
            "provenance_quality": "OFF_DISK_SKUNKWORKS_A5"
        }
    }
]

ledger_entries = [
    {"ts": TS, "kind": "CG_LANDED", "atom": "T3/EXP_sharded_fhrr_cleanup_capacity_beyond_bundle_bound_v1", "session": "2026-07-02_bundle_vet", "verified_off_data": True, "reason": "3-seed FULL sharded=1.000 flat; bundle collapses (Plate bound verified positive control); 13.9x beyond classical bundle capacity"},
    {"ts": TS, "kind": "CG_LANDED", "atom": "T3/EXP_math4_proof_chains_v2_global_bundle_cpu_v1", "session": "2026-07-02_bundle_vet", "verified_off_data": True, "reason": "3-seed FULL storage_gap=1.000 cv=0.0; crit I/II/III all seeds; L=2-10 chain-composition"},
    {"ts": TS, "kind": "CG_LANDED", "atom": "T3/EXP_math4_rung3_deep_chains_v2_global_bundle_cpu_v1", "session": "2026-07-02_bundle_vet", "verified_off_data": True, "reason": "3-seed FULL storage_gap cv=0.020 @ L=20 (extends v2 depth-axis); crit I/II/III all seeds at DEEP L"},
    {"ts": TS, "kind": "CG_LANDED", "atom": "T3/EXP_stretch4_3_temporal_strips_v2_substrate_native_planner_cpu_v1", "session": "2026-07-02_bundle_vet", "verified_off_data": True, "reason": "path-A rescue; substrate-native BFS bit-identical to symbolic (sub=sym=0.513); pre/add/del p/r=1.000; symbolic in-band; Stage-3 substrate-hosts-temporal-STRIPS CG"},
    {"ts": TS, "kind": "CG_META_LANDED", "atom": "T4/META_STORAGE_STRATEGY_COMPOSITION_DEPTH_PHYSICS_LAW_v1", "session": "2026-07-02_bundle_vet", "verified_off_data": True, "reason": "3-cell physics-law composition across composition-depth axis; sharded=1.000 flat across 9 landings; positive control cleanly separates storage strategies"},
    {"ts": TS, "kind": "AMEND_DEMOTE", "atom": "T3/EXP_stretch4_3_temporal_strips_cpu_v1", "session": "2026-07-02_bundle_vet", "verified_off_data": True, "reason": "v1 headline temporal-plan-rate=1.000 (n=150) exposed as BOGUS by v2 rescue: v2 substrate-native BFS bit-identical to symbolic shows true plan-rate 0.513 on non-oracle goals. v1 numpy-costume + reachable-by-construction oracle-goal defect. DEMOTE: subtract 1 from CG count; superseded by T3/EXP_stretch4_3_temporal_strips_v2_substrate_native_planner_cpu_v1", "supersedes_by": "T3/EXP_stretch4_3_temporal_strips_v2_substrate_native_planner_cpu_v1"}
]

n1 = atomic_append(MATH, atoms_math)
n2 = atomic_append(META, atoms_meta)
n3 = atomic_append(LEDGER, ledger_entries)
print(f"MATH atoms after append: {n1}")
print(f"META atoms after append: {n2}")
print(f"LEDGER entries after append: {n3}")
print(f"Session tally today (grep 2026-07-02):")
os.system(f"grep -c '2026-07-02' {MATH}")
os.system(f"grep -c '2026-07-02' {META}")
