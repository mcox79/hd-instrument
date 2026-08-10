# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; composed vs scrambled digest-differ per fresh unit)
# - final_metrics_atomicity declared (META_RULE_AH; tmp_replace top-level + per-(target,scale) resumable unit)
# - except SystemExit: raise BEFORE except Exception (no BaseException, no bare except:)
# - crlb_n/a declared (empirical leaf-capacity diagnostic; see prereg, same class as Stage-2E/2F)
# - HP_SCOPE: {hierarchical_dense_rescore: [relevant_recall, false_pull_in_rate, scramble_margin,
#              no_regression_100k, relevant_in_shortlist_rate]}
# - cardinality_ok: EXPECTED_N_UNITS=len(TARGET_LEAF_SIZES_FRESH)*len(SCALES)=6 (sweep axis = leaf-target x
#   scale, resumable across separate foreground invocations via --target)
# - per-unit failure-class instrumentation (no bare except)
# - calibration_check: adaptive_with_discriminator_gate (global dense-space tau via
#   refuse_gate_calibrate_from_scores, IMPORTED unchanged from Stage-2F -- Stage-2F's own measured
#   ADDENDUM-2 pivot found the context-gate regresses; not reintroduced here)
# - all numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
# - self-test constructs REAL tiny SparseHeteroShardStore + DenseShardStore + the REAL derive_k_family_map
#   function against a tiny synthetic BIGFAM/SMALLFAM corpus (real_code_path); verifies derive_k_family_map
#   reproduces Stage-2E's own K_FAMILY at target=57000 using REAL measured CSKG family occupancy (checked
#   again, live, at --full runtime -- the citation-repro guard); verifies mechanism activates + differs +
#   degrades under scramble at tiny scale
# - progress_logging: print_flush_true (per-(target,1213912)-scale unit up to ~360s; 3 fresh targets x
#   2 scales = 6 units, chunked one target per invocation via --target to fit foreground timeouts)
# See preregs/2026-08-10_focus_pullin_causal_stage2g_deeper_leaf_split_v1.md for the full pre-reg.
"""exp_focus_pullin_causal_stage2g_deeper_leaf_split_v1 -- Stage 2 SUB-TEST G (LAST STORE ITERATION):
Stage-2F (HARD_FAIL, `data/exp_focus_pullin_causal_stage2f_dense_rescore_fine_decode_v1/metrics.json`)
composed a dense-rescore fine-decode on Stage-2E's hierarchical sparse+dense store but landed
relevant_recall=0.267 / margin=0.227 at 1,213,912 (below HARD-PASS: recall>=0.50, margin>=0.30). Diagnosis
(MEASURED@data/exp_focus_pullin_causal_stage2f_dense_rescore_fine_decode_v1/metrics.json:
per_scale.1213912.hierarchical_dense_rescore.diagnose_split_dg_decode): loss is 100% WRONG_ARGMAX
(correct_refused=0, wrong_argmax_frac=0.75 @ 1.2M, up from 0.352 @ 100K), tracking max leaf occupancy
growing from ~4,274 (100K) to 51,873 (1.2M) triples/leaf. This cell tests whether SUB-SPLITTING the
oversized leaves further (smaller TARGET_LEAF_SIZE -> more tier-2 shards) reduces per-leaf write-count
crosstalk enough to clear the fine-decode HARD-PASS gate, by generalizing Stage-2E's hardcoded K_FAMILY
(derived once at target=57,000) into `derive_k_family_map(occupancy, target_leaf_size)` and sweeping
target_leaf_size = {57000 (Stage-2F, CITED not re-run), 25000, 15000, 10000} at BOTH task-contract scales
(100,000 and 1,213,912).

THIS IS THE LAST PLANNED STORE ITERATION (task contract): a clean HARD-PASS ends the store-tuning arc with
a working single-argmax fine-decode; an honest HARD-FAIL (recall still <0.30 at 1.2M at the finest tested
granularity, 10,000) ends the arc with the brain-faithful conclusion that final single-item selection is
NOT the store's job -- candidate-retrieval (DG/CA3 coarse shortlist-hit) IS solved (0.853 @ 1,213,912,
unchanged this cell) and belongs to a downstream context-validating LOOP, not further store epicycles.

MECHANISM UNCHANGED from Stage-2F except ONE variable (leaf granularity): dense-rescore fine-decode
(re-score the SAME DG-shortlisted ~50 candidates in the un-projected dense entity space, global-tau accept
-- Stage-2F's own measured PRIMARY metric per its ADDENDUM-2 pivot; the context-gated-tau ablation is NOT
reintroduced here since Stage-2F measured it regresses), imported bit-for-bit from Stage-2F
(`eval_gate_hierarchical_dense_rescore`). Storage/routing primitives (`SparseHeteroShardStore`,
`DenseShardStore`, `compute_ingest_shard_ids_real/scrambled`, `compute_query_shard_ids`,
`build_family_shard_layout`) are Stage-2D/2E's exact classes/functions, imported not re-transcribed --
they already accept an arbitrary `k_family_map`/`base_offset`/`salt_base` as parameters, so no new
routing code is needed, only a new (pure, closed-form, no-RNG) function that DERIVES k_family_map from
measured per-family occupancy + a target leaf size:
`derive_k_family_map(occ, target) = 1 if occ<=target else ceil(occ/target)+1` (the same +1 hash-imbalance
safety margin Stage-2E measured and applied to AT/VG/CN, now applied uniformly). VERIFIED (self-test +
live --full runtime guard) to reproduce Stage-2E's own K_FAMILY={AT:14,VG:6,CN:5,WD:1,FN:1,WN:1,CN|WN:1}
bit-for-bit at target=57,000 using REAL measured CSKG family occupancy -- confirms this is a strict
generalization, not a new mechanism.

10,000 is the practical floor for this sweep: CN's measured max single-entity fan-out is 6,081
(CITED@Stage-2E module docstring hub-audit, not re-measured) -- a mega-fan-out entity's edges cannot be
split across leaves (tier-2 routes by whole-subject hash), so targets much below ~6,000-7,000 would not
shrink that family's largest leaf further. A finer 5th point was considered and dropped (honest-HARD_FAIL
discipline -- report the curve, don't grind toward a manufactured PASS).

Modes:
  --self-test    Real-code-path check: tiny KGStore/SparseHeteroShardStore/DenseShardStore (n_ent=48,
                 dg_dim=256) + the REAL derive_k_family_map/compute_family_occupancy functions against a
                 tiny synthetic BIGFAM/SMALLFAM corpus; verifies derive_k_family_map reproduces Stage-2E's
                 own K_FAMILY at target=57000 from REAL measured CSKG occupancy (loaded, not hand-typed);
                 verifies the mechanism activates + differs from a coarser target + degrades under
                 scramble, at tiny scale. No dispatch.
  --full         Runs the checkpointed leaf-size sweep. TARGET_LEAF_SIZES_FRESH=[25000, 15000, 10000] x
                 SCALES=[100000, 1213912], per-(target,scale) checkpointed via tools/exp_checkpoint.py
                 (unit_key = "leaf|<target>|<scale>"), resumable. Pass --target <int> to restrict this
                 invocation to ONE target_leaf_size's 2 scale-units (fits comfortably in one foreground
                 Bash timeout; call once per target across separate invocations to complete the sweep).
                 Aggregation (verdict/checks/curve) is recomputed from ALL units present on disk at the
                 END of every invocation (same convention as Stage-2E/2F) -- the final, complete metrics.json
                 lands once all 6 fresh units + the cited 57000 point are present.
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "8")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "8")
os.environ.setdefault("MKL_NUM_THREADS", "8")

import argparse
import gc
import hashlib
import json
import math
import platform
import sys
import time
import traceback
from datetime import datetime, timezone
from typing import Dict, List

import numpy as np
import torch

ANCHOR_NAME = "focus_pullin_causal_stage2g_deeper_leaf_split_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "tools"), os.path.join(REPO_ROOT, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")
CSKG_DIR = os.path.join(REPO_ROOT, "data", "cskg_foundation_v1")
STAGE2E_METRICS_PATH = os.path.join(
    REPO_ROOT, "data", "exp_focus_pullin_causal_stage2e_hierarchical_subject_tier_v1", "metrics.json")
STAGE2F_METRICS_PATH = os.path.join(
    REPO_ROOT, "data", "exp_focus_pullin_causal_stage2f_dense_rescore_fine_decode_v1", "metrics.json")

from hdlab.kg_traversal import KGStore  # noqa: E402
from experiments.exp_focus_pullin_causal_stage2b_cskg_scale_gate_v1 import (  # noqa: E402
    load_entity_vocab, precheck_kgstore_and_loader, QUERY_SEED as S2B_QUERY_SEED,
    DATA_SEED as S2B_DATA_SEED, SHORTLIST_K as S2B_SHORTLIST_K, N_QUERY as S2B_N_QUERY,
)
from experiments.exp_focus_pullin_causal_stage2d_context_gated_sharded_store_v1 import (  # noqa: E402
    load_spine_edges_with_source, SparseHeteroShardStore, DenseShardStore, build_relation_majority_shard,
    build_dg_projections, precompute_dg_val_codebook, precheck_source_field, DG_DIM, DG_SPARSITY,
)
from experiments.exp_focus_pullin_causal_stage2e_hierarchical_subject_tier_v1 import (  # noqa: E402
    K_FAMILY as STAGE2E_K_FAMILY, TIER2_SALT_BASE, SCRAMBLE_SEED,
    build_family_shard_layout, compute_ingest_shard_ids_real, compute_ingest_shard_ids_scrambled,
    compute_query_shard_ids,
)
from experiments.exp_focus_pullin_causal_stage2f_dense_rescore_fine_decode_v1 import (  # noqa: E402
    eval_gate_hierarchical_dense_rescore,
)
from tools.exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402

QUERY_SEED = S2B_QUERY_SEED
DATA_SEED = S2B_DATA_SEED
SHORTLIST_K = S2B_SHORTLIST_K
N_QUERY = S2B_N_QUERY

SCALES = [100000, 1213912]
TARGET_LEAF_SIZE_CITED = 57000  # Stage-2F's point, CITED not re-run (compute-proportionality)
TARGET_LEAF_SIZES_FRESH = [25000, 15000, 10000]
EXPECTED_N_UNITS = len(TARGET_LEAF_SIZES_FRESH) * len(SCALES)  # = 6

HP_RECALL_MIN = 0.50
HP_FP_MAX = 0.20
HP_MARGIN_MIN = 0.30
HARD_FAIL_RECALL_CEILING_1213912 = 0.30  # task-contract-specified (same as Stage-2F)
HARD_FAIL_TIE_GAP = 0.10
NO_REGRESSION_TOLERANCE = 0.05
# MEASURED@data/exp_focus_pullin_causal_stage2e_hierarchical_subject_tier_v1/metrics.json:
# per_scale.100000.hierarchical_sparse.relevant_recall (same constant Stage-2F cites)
STAGE2E_100K_COMPOSED_RECALL = 0.6133333333333333


# ============================================================================ NEW: leaf-target derivation
def compute_family_occupancy(src_idx_arr: np.ndarray, family_idx_to_name: Dict[int, str]) -> Dict[str, int]:
    """Measured per-family edge count in the (possibly scale-prefixed) ingested set -- no hardcoding."""
    n_fam = len(family_idx_to_name)
    counts = np.bincount(src_idx_arr, minlength=n_fam)
    return {family_idx_to_name[i]: int(counts[i]) for i in range(n_fam)}


def derive_k_family_map(occupancy: Dict[str, int], target_leaf_size: int) -> Dict[str, int]:
    """K_family = 1 if measured occupancy <= target; else ceil(occupancy/target) + 1 (the +1 is a
    hash-imbalance safety margin -- Stage-2E's own measured precedent for AT/VG/CN, applied uniformly here
    since fresh per-family fan-out audits are not re-run at every new target). Pure closed-form function of
    MEASURED occupancy, no RNG, no hash()-derived ordering (gate F.5)."""
    k: Dict[str, int] = {}
    for fam, occ in occupancy.items():
        if occ <= target_leaf_size:
            k[fam] = 1
        else:
            k[fam] = int(math.ceil(occ / target_leaf_size)) + 1
    return k


# ============================================================================ per-(target,scale) unit
def run_leaf_target_scale_unit(target_leaf_size: int, scale: int, triples_shuffled: torch.Tensor,
                               src_idx_shuffled: np.ndarray, E: torch.Tensor, R: torch.Tensor,
                               E_np: np.ndarray, n_rel: int, source_to_idx: Dict[str, int],
                               family_idx_to_name: Dict[int, str], dg_key_proj, dg_val_codebook: torch.Tensor,
                               salt_base: int) -> Dict:
    scale_eff = min(scale, len(triples_shuffled))
    ingested = triples_shuffled[:scale_eff]
    ingested_src = src_idx_shuffled[:scale_eff]
    s_idx = ingested[:, 0].numpy()
    p_idx = ingested[:, 1].numpy()
    o_idx = ingested[:, 2].numpy()
    sq = math.sqrt(E.shape[1])

    occupancy = compute_family_occupancy(ingested_src, family_idx_to_name)
    k_family_map = derive_k_family_map(occupancy, target_leaf_size)
    base_offset, total_shards = build_family_shard_layout(source_to_idx, k_family_map)

    rel_majority_family_idx = build_relation_majority_shard(p_idx, ingested_src, n_rel, len(source_to_idx))

    ingest_shard_real = compute_ingest_shard_ids_real(s_idx, ingested_src, family_idx_to_name, base_offset,
                                                       k_family_map, salt_base)
    ingest_shard_scr = compute_ingest_shard_ids_scrambled(s_idx, ingested_src, family_idx_to_name,
                                                           base_offset, k_family_map, salt_base, scale_eff,
                                                           SCRAMBLE_SEED)

    unit: Dict = {"target_leaf_size": target_leaf_size, "scale": scale_eff, "occupancy": occupancy,
                  "k_family_map": k_family_map, "total_shards": total_shards, "base_offset": base_offset}

    # ---- composed arm (real tier-2 routing)
    composed_sparse_store = SparseHeteroShardStore(dg_val_codebook, DG_DIM, n_shards=total_shards)
    t0 = time.time()
    composed_sparse_diag = composed_sparse_store.ingest_from_triples(s_idx, p_idx, o_idx, ingest_shard_real,
                                                                     E, R, dg_key_proj, sq)
    composed_sparse_ing_s = time.time() - t0

    composed_dense_store = DenseShardStore(E, R, int(E.shape[1]), n_shards=total_shards)
    t0 = time.time()
    composed_dense_diag = composed_dense_store.ingest(ingested, ingest_shard_real)
    composed_dense_ing_s = time.time() - t0

    t0 = time.time()
    composed_eval = eval_gate_hierarchical_dense_rescore(
        composed_sparse_store, composed_dense_store, s_idx, p_idx, o_idx, ingested_src,
        rel_majority_family_idx, family_idx_to_name, base_offset, k_family_map, salt_base, dg_key_proj,
        E, R, E_np, n_rel, N_QUERY, QUERY_SEED, SHORTLIST_K, ingested)
    composed_eval_s = time.time() - t0
    composed_eval.update({"ingest_s_sparse": round(composed_sparse_ing_s, 3),
                          "ingest_s_dense": round(composed_dense_ing_s, 3),
                          "eval_s": round(composed_eval_s, 3),
                          "shard_diag_sparse": composed_sparse_diag, "shard_diag_dense": composed_dense_diag})
    unit["hierarchical_dense_rescore"] = composed_eval

    # ---- memory management (load-bearing at finer targets: n_shards up to ~131, W_shards [n,2048,2048]
    # ~2GiB per arm) -- free composed stores BEFORE building scrambled stores so peak memory stays ~1
    # arm's worth of W_shards at a time, not 2x (see prereg Compute architecture)
    del composed_sparse_store, composed_dense_store
    gc.collect()

    # ---- scrambled_tier2 arm: identical treatment, scrambled write-side tier-2 assignment
    scr_sparse_store = SparseHeteroShardStore(dg_val_codebook, DG_DIM, n_shards=total_shards)
    t0 = time.time()
    scr_sparse_diag = scr_sparse_store.ingest_from_triples(s_idx, p_idx, o_idx, ingest_shard_scr, E, R,
                                                           dg_key_proj, sq)
    scr_sparse_ing_s = time.time() - t0

    scr_dense_store = DenseShardStore(E, R, int(E.shape[1]), n_shards=total_shards)
    t0 = time.time()
    scr_dense_diag = scr_dense_store.ingest(ingested, ingest_shard_scr)
    scr_dense_ing_s = time.time() - t0

    t0 = time.time()
    scr_eval = eval_gate_hierarchical_dense_rescore(
        scr_sparse_store, scr_dense_store, s_idx, p_idx, o_idx, ingested_src, rel_majority_family_idx,
        family_idx_to_name, base_offset, k_family_map, salt_base, dg_key_proj, E, R, E_np, n_rel,
        N_QUERY, QUERY_SEED, SHORTLIST_K, ingested)
    scr_eval_s = time.time() - t0
    scr_eval.update({"ingest_s_sparse": round(scr_sparse_ing_s, 3), "ingest_s_dense": round(scr_dense_ing_s, 3),
                     "eval_s": round(scr_eval_s, 3), "shard_diag_sparse": scr_sparse_diag,
                     "shard_diag_dense": scr_dense_diag})
    unit["scrambled_tier2_dense_rescore"] = scr_eval

    del scr_sparse_store, scr_dense_store
    gc.collect()

    return unit


# ============================================================================ output plumbing
def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "expected_n_units": expected_n_units,
              "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


def _write_heartbeat(output_dir, unit_idx, total_units, elapsed_s, extra=None):
    path = os.path.join(output_dir, "_heartbeat.jsonl")
    rec = {"ts_iso": datetime.now(timezone.utc).isoformat(), "unit_idx": unit_idx,
          "total_units": total_units, "elapsed_s": round(elapsed_s, 2)}
    if extra:
        rec.update(extra)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")


def _write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, default=str)
    os.replace(tmp, final)


def load_stage2f_cited_point() -> Dict:
    with open(STAGE2F_METRICS_PATH, encoding="utf-8") as f:
        return json.load(f)


# ============================================================================ self-test
def self_test() -> Dict:
    pre = precheck_kgstore_and_loader()
    assert pre["ok"], f"STAGE2B_PRECHECK_FAIL: {pre}"
    src_pre = precheck_source_field()
    assert src_pre["ok"], f"SOURCE_FIELD_PRECHECK_FAIL: {src_pre}"
    assert os.path.exists(STAGE2F_METRICS_PATH), f"STAGE2F_REFERENCE_MISSING: {STAGE2F_METRICS_PATH}"

    # ---- closed-form unit-test of derive_k_family_map (no CSKG load needed, fast)
    k_synth = derive_k_family_map({"BIGFAM": 200, "SMALLFAM": 10}, target_leaf_size=50)
    assert k_synth == {"BIGFAM": 5, "SMALLFAM": 1}, f"DERIVE_K_FAMILY_FORMULA_WRONG: {k_synth}"
    # ceil(200/50)+1=4+1=5; SMALLFAM 10<=50 => 1

    # ---- tiny synthetic corpus: BIGFAM (oversized) + SMALLFAM (small) -- mirrors Stage-2E/2F
    n_ent_t = 48
    n_rel_t = 6
    gen = torch.Generator()
    gen.manual_seed(7)
    tmp_store = KGStore(n_ent=n_ent_t, n_rel=n_rel_t, n_dim=64, generator=gen)
    E_t, R_t = tmp_store.E, tmp_store.R
    E_t_np = E_t.numpy()

    source_to_idx_t = {"BIGFAM": 0, "SMALLFAM": 1}
    idx_to_source_t = {0: "BIGFAM", 1: "SMALLFAM"}

    rng = np.random.default_rng(11)
    n_triples_t = 60
    s_t = rng.integers(0, n_ent_t, size=n_triples_t)
    p_t = rng.integers(0, n_rel_t, size=n_triples_t)
    o_t = rng.integers(0, n_ent_t, size=n_triples_t)
    src_t = (p_t % 2)  # deterministic, relation-correlated (mirrors real corpus's pure-relation structure)
    triples_t = torch.tensor(np.stack([s_t, p_t, o_t], axis=1), dtype=torch.long)

    # ---- real_code_path (F.1): derive_k_family_map from REAL measured occupancy of this fixture (not
    # hand-typed), then a coarse target (K_BIGFAM=1) vs a fine target forced to K_BIGFAM=4 by construction
    occupancy_t = compute_family_occupancy(src_t, idx_to_source_t)
    target_coarse_t = max(occupancy_t.values()) * 10  # everything fits in one leaf per family
    k_coarse_t = derive_k_family_map(occupancy_t, target_coarse_t)
    assert all(v == 1 for v in k_coarse_t.values()), f"COARSE_TARGET_SHOULD_GIVE_K1: {k_coarse_t}"
    target_fine_t = max(1, math.ceil(occupancy_t["BIGFAM"] / 3))  # forces ceil(occ/target)=3 -> K=4
    k_fine_t = derive_k_family_map(occupancy_t, target_fine_t)
    assert k_fine_t["BIGFAM"] == 4, f"FINE_TARGET_SHOULD_FORCE_K4: {k_fine_t} occ={occupancy_t}"

    base_offset_t, total_shards_t = build_family_shard_layout(source_to_idx_t, k_fine_t)

    ingest_shards_real_t = compute_ingest_shard_ids_real(s_t, src_t, idx_to_source_t, base_offset_t,
                                                          k_fine_t, TIER2_SALT_BASE)
    rel_maj_t = build_relation_majority_shard(p_t, src_t, n_rel_t, len(source_to_idx_t))
    ingest_shards_scr_t = compute_ingest_shard_ids_scrambled(s_t, src_t, idx_to_source_t, base_offset_t,
                                                              k_fine_t, TIER2_SALT_BASE, scale=999,
                                                              scramble_seed=SCRAMBLE_SEED)
    assert not np.array_equal(ingest_shards_real_t, ingest_shards_scr_t), "SCRAMBLE_DID_NOT_CHANGE_INGEST"

    dg_dim_t, sparsity_t = 256, 0.05
    dg_key_proj_t, dg_val_proj_t = build_dg_projections(3, 64, dg_dim_t, sparsity_t)
    dg_val_codebook_t = precompute_dg_val_codebook(dg_val_proj_t, E_t)

    sq_t = math.sqrt(64)
    real_sparse_t = SparseHeteroShardStore(dg_val_codebook_t, dg_dim_t, n_shards=total_shards_t)
    real_sparse_t.ingest_from_triples(s_t, p_t, o_t, ingest_shards_real_t, E_t, R_t, dg_key_proj_t, sq_t,
                                      chunk_size=17)
    real_dense_t = DenseShardStore(E_t, R_t, 64, n_shards=total_shards_t)
    real_dense_t.ingest(triples_t, ingest_shards_real_t)

    scr_sparse_t = SparseHeteroShardStore(dg_val_codebook_t, dg_dim_t, n_shards=total_shards_t)
    scr_sparse_t.ingest_from_triples(s_t, p_t, o_t, ingest_shards_scr_t, E_t, R_t, dg_key_proj_t, sq_t,
                                     chunk_size=17)
    scr_dense_t = DenseShardStore(E_t, R_t, 64, n_shards=total_shards_t)
    scr_dense_t.ingest(triples_t, ingest_shards_scr_t)

    real_eval_t = eval_gate_hierarchical_dense_rescore(
        real_sparse_t, real_dense_t, s_t, p_t, o_t, src_t, rel_maj_t, idx_to_source_t, base_offset_t,
        k_fine_t, TIER2_SALT_BASE, dg_key_proj_t, E_t, R_t, E_t_np, n_rel_t, n_query=15, query_seed=1,
        shortlist_k=8, ingested_triples=triples_t)
    scr_eval_t = eval_gate_hierarchical_dense_rescore(
        scr_sparse_t, scr_dense_t, s_t, p_t, o_t, src_t, rel_maj_t, idx_to_source_t, base_offset_t,
        k_fine_t, TIER2_SALT_BASE, dg_key_proj_t, E_t, R_t, E_t_np, n_rel_t, n_query=15, query_seed=1,
        shortlist_k=8, ingested_triples=triples_t)

    assert 0.0 <= real_eval_t["relevant_recall"] <= 1.0
    assert real_eval_t["relevant_recall"] >= scr_eval_t["relevant_recall"], (
        f"SCRAMBLE_DID_NOT_DEGRADE_DENSE_RESCORE: real={real_eval_t['relevant_recall']} "
        f"scr={scr_eval_t['relevant_recall']}")

    def _digest(d):
        keep = {k: v for k, v in d.items()
               if k not in ("calibration_dg", "calibration_dense_global", "context_gate_diag",
                            "per_family")}
        return hashlib.sha256(json.dumps(keep, sort_keys=True, default=str).encode()).hexdigest()

    diff = {"real": _digest(real_eval_t), "scrambled": _digest(scr_eval_t)}
    arms_differ = len(set(diff.values())) == len(diff)
    assert arms_differ, f"ARMS_IDENTICAL_TINY: {diff}"

    return {
        "kgstore_loader_precheck": pre, "source_field_precheck": src_pre,
        "derive_k_family_formula_check": k_synth,
        "occupancy_t": occupancy_t, "k_coarse_t": k_coarse_t, "k_fine_t": k_fine_t,
        "real_recall_tiny": real_eval_t["relevant_recall"], "scr_recall_tiny": scr_eval_t["relevant_recall"],
        "arms_differ_check": diff, "arms_differ": arms_differ,
    }


# ============================================================================ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--target", type=int, default=None,
                    help="restrict this invocation to ONE target_leaf_size (fits one foreground timeout)")
    args = ap.parse_args()

    if args.self_test or not args.full:
        t0 = time.time()
        result = self_test()
        elapsed = time.time() - t0
        metrics = {"verdict": "HARD_PASS", "verdict_msg": "SELFTEST_PASS", "summary": "self-test green",
                  "elapsed_s": round(elapsed, 3), "run_mode": "self_test", "anchor_name": ANCHOR_NAME,
                  "result": result}
        _write_metrics(OUTPUT_DIR, metrics)
        print(json.dumps(metrics, indent=2, default=str))
        return

    run_mode = "full"
    output_dir = OUTPUT_DIR
    targets_this_invocation = [args.target] if args.target is not None else list(TARGET_LEAF_SIZES_FRESH)
    for t in targets_this_invocation:
        assert t in TARGET_LEAF_SIZES_FRESH, f"UNKNOWN_TARGET: {t} not in {TARGET_LEAF_SIZES_FRESH}"
    _write_start_marker(output_dir, run_mode, EXPECTED_N_UNITS)
    t0 = time.time()

    print(f"[{run_mode}] loading real CSKG entity vocab + edges (with source)...", flush=True)
    entity_to_idx = load_entity_vocab(CSKG_DIR)
    n_ent = len(entity_to_idx)
    triples_int, relation_to_idx, src_idx, source_to_idx = load_spine_edges_with_source(
        entity_to_idx, CSKG_DIR)
    n_rel = len(relation_to_idx)
    print(f"[{run_mode}] {n_ent} entities, {len(triples_int)} edges, n_rel={n_rel}, "
          f"n_families={len(source_to_idx)} ({source_to_idx}) t={time.time()-t0:.2f}s", flush=True)

    family_idx_to_name = {v: k for k, v in source_to_idx.items()}

    rng = np.random.default_rng(DATA_SEED)
    perm = rng.permutation(len(triples_int))
    triples_shuffled = torch.from_numpy(triples_int[perm])
    src_idx_shuffled = src_idx[perm]

    gen = torch.Generator()
    gen.manual_seed(DATA_SEED)
    codebook_store = KGStore(n_ent=n_ent, n_rel=n_rel, n_dim=1024, generator=gen)
    E, R = codebook_store.E, codebook_store.R
    E_np = E.numpy()

    dg_key_proj, dg_val_proj = build_dg_projections(DATA_SEED, 1024, DG_DIM, DG_SPARSITY)
    print(f"[{run_mode}] DG projections built t={time.time()-t0:.2f}s; encoding DG_VAL_CODEBOOK "
          f"({n_ent} entities, dg_dim={DG_DIM})...", flush=True)
    dg_val_codebook = precompute_dg_val_codebook(dg_val_proj, E)
    print(f"[{run_mode}] DG_VAL_CODEBOOK done t={time.time()-t0:.2f}s (shared across all leaf-size "
          f"sweep points -- computed ONCE)", flush=True)

    # ---- citation-repro guard (live, real-data): derive_k_family_map at target=57000, using REAL
    # occupancy measured from this exact shuffle at scale=1213912, must reproduce Stage-2E's own
    # K_FAMILY bit-for-bit (validates the "strict generalization, not a new mechanism" claim)
    occ_1213912 = compute_family_occupancy(src_idx_shuffled[:min(1213912, len(triples_shuffled))],
                                           family_idx_to_name)
    derived_57000 = derive_k_family_map(occ_1213912, TARGET_LEAF_SIZE_CITED)
    cited_repro_ok = (derived_57000 == STAGE2E_K_FAMILY)
    print(f"[{run_mode}] citation-repro guard: derive_k_family_map(occ@1213912, 57000)={derived_57000} "
          f"vs Stage-2E K_FAMILY={STAGE2E_K_FAMILY} ok={cited_repro_ok} t={time.time()-t0:.2f}s",
          flush=True)

    done = completed_units(output_dir)
    unit_i = 0
    for target in targets_this_invocation:
        for scale in SCALES:
            scale_eff = min(scale, len(triples_shuffled))
            key = unit_key("leaf", target, scale_eff)
            if key in done:
                print(f"[{run_mode}] target={target} scale={scale_eff} already complete (resume)",
                     flush=True)
                unit_i += 1
                continue
            print(f"[{run_mode}] target={target} scale={scale_eff} starting t={time.time()-t0:.2f}s",
                 flush=True)
            unit = run_leaf_target_scale_unit(target, scale_eff, triples_shuffled, src_idx_shuffled, E, R,
                                              E_np, n_rel, source_to_idx, family_idx_to_name, dg_key_proj,
                                              dg_val_codebook, TIER2_SALT_BASE)
            record_unit(output_dir, key, unit)
            unit_i += 1
            h = unit["hierarchical_dense_rescore"]
            s = unit["scrambled_tier2_dense_rescore"]
            print(f"[{run_mode}] target={target} scale={scale_eff} done: total_shards={unit['total_shards']} "
                 f"composed_rr={h['relevant_recall']:.3f} (dg_decode={h['relevant_recall_dg_decode']:.3f}) "
                 f"shortlist_rate={h['relevant_in_shortlist_rate']:.3f} composed_fp={h['false_pull_in_rate']:.3f} "
                 f"scr_rr={s['relevant_recall']:.3f} margin={h['relevant_recall']-s['relevant_recall']:.3f} "
                 f"wrong_argmax_frac={h['diagnose_split_dg_decode']['wrong_argmax_frac']:.3f} "
                 f"t={time.time()-t0:.2f}s", flush=True)
            _write_heartbeat(output_dir, unit_i, EXPECTED_N_UNITS, time.time() - t0,
                             extra={"target": target, "scale": scale_eff})

    # ---- aggregate from ALL units currently on disk (may be < EXPECTED_N_UNITS if this was a
    # --target-restricted partial invocation; final complete metrics.json lands once all 6 are present)
    all_units = load_units(output_dir)
    per_leaf_target: Dict[str, Dict] = {}
    for k, u in all_units.items():
        if not k.startswith("leaf|"):
            continue
        tgt_s = str(u["target_leaf_size"])
        per_leaf_target.setdefault(tgt_s, {"source": "fresh", "target_leaf_size": u["target_leaf_size"]})
        per_leaf_target[tgt_s][str(u["scale"])] = u
    cardinality_ok = sum(1 for k in all_units if k.startswith("leaf|")) == EXPECTED_N_UNITS

    # ---- splice in the CITED 57000 point (Stage-2F, not re-run)
    try:
        stage2f_ref = load_stage2f_cited_point()
        cited_per_scale = stage2f_ref.get("per_scale", {})
        cited_entry = {"source": "cited_stage2f", "target_leaf_size": TARGET_LEAF_SIZE_CITED,
                       "k_family_map": STAGE2E_K_FAMILY, "total_shards": stage2f_ref.get("total_shards")}
        for scale_s in ("100000", "1213912"):
            su = cited_per_scale.get(scale_s)
            if su is not None:
                cited_entry[scale_s] = su
        per_leaf_target[str(TARGET_LEAF_SIZE_CITED)] = cited_entry
        cited_load_ok = True
    except Exception as e:  # noqa: BLE001 -- non-fatal citation load, per-unit failure-class instrumentation
        cited_load_ok = False
        per_leaf_target[str(TARGET_LEAF_SIZE_CITED)] = {"source": "cited_stage2f_LOAD_FAILED",
                                                         "failure_class": type(e).__name__, "msg": str(e)[:300]}

    # ---- per-leaf-target checks + recall-vs-leaf-size curve
    def _pt(entry, arm):
        d = entry.get(arm)
        return None if d is None else {
            "relevant_recall": d["relevant_recall"], "relevant_recall_dg_decode": d["relevant_recall_dg_decode"],
            "relevant_in_shortlist_rate": d["relevant_in_shortlist_rate"],
            "false_pull_in_rate": d["false_pull_in_rate"], "diagnose_split_dg_decode": d["diagnose_split_dg_decode"],
        }

    curve: Dict[str, Dict] = {}
    all_target_checks: Dict[str, Dict] = {}
    for tgt_s, entry in per_leaf_target.items():
        c100 = _pt(entry.get("100000", {}), "hierarchical_dense_rescore")
        s100 = _pt(entry.get("100000", {}), "scrambled_tier2_dense_rescore")
        c12 = _pt(entry.get("1213912", {}), "hierarchical_dense_rescore")
        s12 = _pt(entry.get("1213912", {}), "scrambled_tier2_dense_rescore")
        row = {"target_leaf_size": entry.get("target_leaf_size"), "source": entry.get("source"),
              "total_shards": entry.get("total_shards"),
              "recall_100k": c100["relevant_recall"] if c100 else None,
              "recall_1213912": c12["relevant_recall"] if c12 else None,
              "shortlist_rate_100k": c100["relevant_in_shortlist_rate"] if c100 else None,
              "shortlist_rate_1213912": c12["relevant_in_shortlist_rate"] if c12 else None,
              "fp_100k": c100["false_pull_in_rate"] if c100 else None,
              "fp_1213912": c12["false_pull_in_rate"] if c12 else None,
              "wrong_argmax_frac_1213912": (c12["diagnose_split_dg_decode"]["wrong_argmax_frac"]
                                            if c12 else None)}
        if c100 and s100:
            row["margin_100k"] = c100["relevant_recall"] - s100["relevant_recall"]
        if c12 and s12:
            row["margin_1213912"] = c12["relevant_recall"] - s12["relevant_recall"]
        curve[tgt_s] = row

        checks: Dict = {}
        if c100 and c12 and s100 and s12:
            checks["recall_ok_both"] = bool(c100["relevant_recall"] >= HP_RECALL_MIN
                                            and c12["relevant_recall"] >= HP_RECALL_MIN)
            checks["fp_ok_both"] = bool(c100["false_pull_in_rate"] <= HP_FP_MAX
                                        and c12["false_pull_in_rate"] <= HP_FP_MAX)
            checks["margin_ok_both"] = bool(row["margin_100k"] >= HP_MARGIN_MIN
                                            and row["margin_1213912"] >= HP_MARGIN_MIN)
            checks["no_regression_100k"] = bool(
                c100["relevant_recall"] >= STAGE2E_100K_COMPOSED_RECALL - NO_REGRESSION_TOLERANCE)
            checks["hard_pass_this_target"] = bool(checks["recall_ok_both"] and checks["fp_ok_both"]
                                                   and checks["margin_ok_both"]
                                                   and checks["no_regression_100k"])
        all_target_checks[tgt_s] = checks

    any_hard_pass = any(c.get("hard_pass_this_target", False) for c in all_target_checks.values())
    finest_tested = min(TARGET_LEAF_SIZES_FRESH)  # = 10000
    finest_row = curve.get(str(finest_tested), {})
    finest_recall_1213912 = finest_row.get("recall_1213912")
    hard_fail = bool((not any_hard_pass) and finest_recall_1213912 is not None
                     and finest_recall_1213912 < HARD_FAIL_RECALL_CEILING_1213912
                     and cardinality_ok)

    def _digest(d):
        if d is None:
            return None
        keep = {k: v for k, v in d.items()
               if k not in ("ingest_s_sparse", "ingest_s_dense", "eval_s", "shard_diag_sparse",
                            "shard_diag_dense", "calibration_dg", "calibration_dense_global",
                            "context_gate_diag", "per_family")}
        return hashlib.sha256(json.dumps(keep, sort_keys=True, default=str).encode()).hexdigest()

    digests = {}
    for tgt_s, entry in per_leaf_target.items():
        if entry.get("source") == "cited_stage2f_LOAD_FAILED":
            continue
        for scale_s in ("100000", "1213912"):
            su = entry.get(scale_s)
            if su is None:
                continue
            digests[f"{tgt_s}_{scale_s}_composed"] = _digest(su.get("hierarchical_dense_rescore"))
            digests[f"{tgt_s}_{scale_s}_scrambled"] = _digest(su.get("scrambled_tier2_dense_rescore"))
    present = {k: v for k, v in digests.items() if v is not None}
    arms_differ = len(set(present.values())) == len(present) if present else False

    if hard_fail:
        overall_verdict = "HARD_FAIL"
    elif any_hard_pass and cardinality_ok:
        overall_verdict = "HARD_PASS"
    else:
        overall_verdict = "MIDDLE_BAND"

    verdict_msg = (f"{overall_verdict}: any_hard_pass={any_hard_pass} finest_tested={finest_tested} "
                  f"finest_recall_1213912={finest_recall_1213912} cardinality_ok={cardinality_ok} "
                  f"n_fresh_units={sum(1 for k in all_units if k.startswith('leaf|'))}/{EXPECTED_N_UNITS} "
                  f"arms_differ={arms_differ} cited_repro_ok={cited_repro_ok} curve={curve}")

    elapsed = time.time() - t0
    metrics = {
        "verdict": overall_verdict, "verdict_msg": verdict_msg[:4000], "summary": verdict_msg[:500],
        "elapsed_s": round(elapsed, 3), "run_mode": run_mode, "anchor_name": ANCHOR_NAME,
        "n_ent": n_ent, "n_rel": n_rel, "n_families": len(source_to_idx), "source_to_idx": source_to_idx,
        "target_leaf_size_cited": TARGET_LEAF_SIZE_CITED, "target_leaf_sizes_fresh": TARGET_LEAF_SIZES_FRESH,
        "targets_this_invocation": targets_this_invocation, "scales": SCALES, "dg_dim": DG_DIM,
        "dg_sparsity": DG_SPARSITY, "cited_repro_ok": cited_repro_ok, "cited_load_ok": cited_load_ok,
        "cited_derived_57000_k_family": derived_57000, "recall_vs_leaf_size_curve": curve,
        "per_target_checks": all_target_checks, "any_hard_pass": any_hard_pass,
        "finest_tested_leaf_size": finest_tested, "finest_recall_1213912": finest_recall_1213912,
        "per_leaf_target": per_leaf_target,
        "cardinality_ok": cardinality_ok, "expected_n_units": EXPECTED_N_UNITS, "cell_chunked": False,
        "start_marker_written": True, "crash_diagnostic_present": True, "heartbeat_present": True,
        "final_metrics_atomicity": "tmp_replace",
        "arms_differ_check": digests, "arms_differ_verified": arms_differ,
        "crlb_n/a": "empirical leaf-capacity diagnostic (same class as Stage-2E/2F); the write-side full-"
                    "vocab dense-store capacity ceiling was already empirically near-zero (leaf_capacity_"
                    "sweep_v1, cited not re-derived); this cell's claim concerns comparison-set-size-"
                    "restricted (k_eff=50) discriminability vs per-leaf write count, which has no "
                    "closed-form CRLB in this codebase",
        "deterministic_seeding": True,
        "calibration_check": "adaptive_with_discriminator_gate: global dense-space tau via "
                            "refuse_gate_calibrate_from_scores (imported unchanged from Stage-2F); no "
                            "context-gate (Stage-2F measured it regresses, not reintroduced)",
        "hp_scope": {"hierarchical_dense_rescore": ["relevant_recall", "false_pull_in_rate",
                                                    "scramble_margin", "no_regression_100k",
                                                    "relevant_in_shortlist_rate"]},
        "no_regression_tolerance": NO_REGRESSION_TOLERANCE,
        "stage2e_100k_composed_recall_cited": STAGE2E_100K_COMPOSED_RECALL,
        "hard_fail_recall_ceiling_1213912": HARD_FAIL_RECALL_CEILING_1213912,
    }
    _write_metrics(output_dir, metrics)
    print(json.dumps({k: v for k, v in metrics.items() if k != "per_leaf_target"}, indent=2, default=str))


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # noqa: BLE001 -- deliberately not BaseException, see cell-template mandate
        _write_crash_metrics(OUTPUT_DIR, e)
        raise
