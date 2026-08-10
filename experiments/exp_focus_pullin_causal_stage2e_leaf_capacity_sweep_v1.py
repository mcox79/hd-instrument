"""exp_focus_pullin_causal_stage2e_leaf_capacity_sweep_v1 -- DIAGNOSTIC (not a gated/dispatched cell).

Answers the CRITICAL VET NOTE in the Stage-2E task: do NOT hard-code a 30-65-triple leaf-capacity
budget derived from an unrelated flat-bundle mechanism (exp_skewed_shard_capacity, dismissed at
cosine 0.29 by Stage-2D's own prior-work check, and CONTRADICTED by Stage-2B's own empirics: 0.967
recall held at 1,000 triples, 0.70 at 10,000 -- 30-65 would never have survived that). Instead,
EMPIRICALLY measure, on THIS store (KGStore's real outer-product Hebbian W / DGProjection+CA3-style
hetero-associative sparse write), where a single ISOLATED leaf's recall crosses below the same
REC_THRESH_SPARSE=0.50 bar the main Stage-2E gate uses -- separately for the dense regime (reuses
Stage-2B's KGStore + eval_gate UNCHANGED, since an isolated single leaf IS exactly a KGStore) and the
sparse DG/CA3 regime (reuses Stage-2D's SparseHeteroShardStore + eval_gate_sparse_shard with
n_shards=1 UNCHANGED). Reuses >90% tested code; the only new logic here is building AT/VG/CN-only
edge prefixes (in the SAME deterministic full-corpus shuffle order Stage-2B/2D use) at swept sizes.

AT (57.4% of CSKG, 696,152 edges) gets a full multi-point sweep since it drives Stage-2D's collapse.
VG (257,130) and CN (214,890) get single full-family-count isolated points (cheaper; the AT curve
supplies the general per-leaf-capacity constant SAFE_LEAF_SIZE these families' target K also uses --
disclosed design choice, not a full independent sweep, per compute-proportionality).

Output feeds Stage-2E's pre-reg as MEASURED@<this file's metrics.json path> for K_AT/K_VG/K_CN.
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "8")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "8")
os.environ.setdefault("MKL_NUM_THREADS", "8")

import json
import math
import sys
import time
import traceback
from datetime import datetime, timezone

import numpy as np
import torch

ANCHOR_NAME = "focus_pullin_causal_stage2e_leaf_capacity_sweep_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "tools"), os.path.join(REPO_ROOT, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")
CSKG_DIR = os.path.join(REPO_ROOT, "data", "cskg_foundation_v1")

from hdlab.kg_traversal import KGStore  # noqa: E402
from experiments.exp_focus_pullin_causal_stage2b_cskg_scale_gate_v1 import (  # noqa: E402
    load_entity_vocab, eval_gate as flat_eval_gate, GATE_THRESH, SHORTLIST_K, N_QUERY, QUERY_SEED,
    DATA_SEED,
)
from experiments.exp_focus_pullin_causal_stage2d_context_gated_sharded_store_v1 import (  # noqa: E402
    load_spine_edges_with_source, SparseHeteroShardStore, build_dg_projections,
    precompute_dg_val_codebook, eval_gate_sparse_shard, build_relation_majority_shard, DG_DIM,
    DG_SPARSITY, REC_THRESH_SPARSE,
)

# MEASURED@data/exp_focus_pullin_causal_stage2d_context_gated_sharded_store_v1/metrics.json:
# per_scale."1213912".dense.shard_diag.occupancy -- full-scale per-family edge counts (K=7 order:
# AT, CN, CN|WN, FN, VG, WD, WN per source_to_idx alphabetical sort).
FULL_FAMILY_OCC = {"AT": 696152, "CN": 214890, "VG": 257130, "WD": 13812, "FN": 12128, "WN": 11903,
                   "CN|WN": 7897}
AT_SWEEP_TARGETS = [57000, 150000, 300000, 500000, 696152]
SINGLE_POINT_FAMILIES = ["VG", "CN"]


def _write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, default=str)
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


def isolated_dense_point(triples_family: torch.Tensor, E: torch.Tensor, R: torch.Tensor,
                         n_ent: int, n_rel: int) -> dict:
    """A single-leaf isolated dense store IS a plain KGStore -- reuses Stage-2B's flat_eval_gate
    unchanged (real_code_path: the ACTUAL substrate object + eval fn the main Stage-2D/2E cells use,
    not a synthetic reimplementation)."""
    gen = torch.Generator()
    gen.manual_seed(DATA_SEED)
    store = KGStore(n_ent=n_ent, n_rel=n_rel, n_dim=1024, generator=gen)
    store.E, store.R = E, R  # share the SAME codebooks as the main cells (apples-to-apples)
    t0 = time.time()
    store.ingest_triples(triples_family)
    ing_s = time.time() - t0
    t0 = time.time()
    m = flat_eval_gate(store, triples_family, n_rel=n_rel, n_query=N_QUERY, query_seed=QUERY_SEED)
    ev_s = time.time() - t0
    m.update({"n_ingested": int(triples_family.shape[0]), "ingest_s": round(ing_s, 3),
              "eval_s": round(ev_s, 3)})
    return m


def isolated_sparse_point(triples_family: torch.Tensor, E: torch.Tensor, R: torch.Tensor,
                          n_ent: int, n_rel: int, dg_key_proj, dg_val_codebook) -> dict:
    """A single-leaf isolated sparse store IS Stage-2D's SparseHeteroShardStore with n_shards=1 --
    reuses ingest_from_triples + eval_gate_sparse_shard UNCHANGED (real_code_path)."""
    n = triples_family.shape[0]
    s_idx = triples_family[:, 0].numpy()
    p_idx = triples_family[:, 1].numpy()
    o_idx = triples_family[:, 2].numpy()
    shard_labels = np.zeros(n, dtype=np.int64)  # trivial: 1 shard
    store = SparseHeteroShardStore(dg_val_codebook, DG_DIM, n_shards=1)
    sq = math.sqrt(E.shape[1])
    t0 = time.time()
    ingest_diag = store.ingest_from_triples(s_idx, p_idx, o_idx, shard_labels, E, R, dg_key_proj, sq)
    ing_s = time.time() - t0
    rel_majority_shard = np.zeros(n_rel, dtype=np.int64)  # trivial: 1 shard, every relation routes there
    t0 = time.time()
    m = eval_gate_sparse_shard(store, s_idx, p_idx, o_idx, rel_majority_shard, dg_key_proj, E, R,
                               n_rel, N_QUERY, QUERY_SEED, SHORTLIST_K, n_shards=1,
                               ingested_triples=triples_family)
    ev_s = time.time() - t0
    m.update({"n_ingested": int(n), "ingest_s": round(ing_s, 3), "eval_s": round(ev_s, 3),
              "shard_diag": ingest_diag})
    return m


def main():
    t0 = time.time()
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"[leaf_sweep] loading real CSKG entity vocab + edges (with source)...", flush=True)
    entity_to_idx = load_entity_vocab(CSKG_DIR)
    n_ent = len(entity_to_idx)
    triples_int, relation_to_idx, src_idx, source_to_idx = load_spine_edges_with_source(
        entity_to_idx, CSKG_DIR)
    n_rel = len(relation_to_idx)
    print(f"[leaf_sweep] {n_ent} entities, {len(triples_int)} edges, n_rel={n_rel} "
          f"t={time.time()-t0:.2f}s", flush=True)

    # SAME deterministic full-corpus shuffle Stage-2D uses (DATA_SEED) -- AT/VG/CN prefixes are
    # prefixes of THIS shuffle filtered to source, so results are directly comparable to Stage-2D's
    # own aggregate numbers at matching occupancy (e.g. AT occupancy=57496 at Stage-2D's 100K scale).
    rng = np.random.default_rng(DATA_SEED)
    perm = rng.permutation(len(triples_int))
    triples_shuffled_np = triples_int[perm]
    src_idx_shuffled = src_idx[perm]

    gen = torch.Generator()
    gen.manual_seed(DATA_SEED)
    codebook_store = KGStore(n_ent=n_ent, n_rel=n_rel, n_dim=1024, generator=gen)
    E, R = codebook_store.E, codebook_store.R

    dg_key_proj, dg_val_proj = build_dg_projections(DATA_SEED, 1024, DG_DIM, DG_SPARSITY)
    print(f"[leaf_sweep] encoding DG_VAL_CODEBOOK ({n_ent} entities, dg_dim={DG_DIM})..."
          f" t={time.time()-t0:.2f}s", flush=True)
    dg_val_codebook = precompute_dg_val_codebook(dg_val_proj, E)
    print(f"[leaf_sweep] DG_VAL_CODEBOOK done t={time.time()-t0:.2f}s", flush=True)

    results = {"AT": {}, "VG": {}, "CN": {}}
    fail_units = []

    at_src_id = source_to_idx["AT"]
    at_mask = src_idx_shuffled == at_src_id
    at_rows = triples_shuffled_np[at_mask]
    at_triples_all = torch.from_numpy(at_rows)
    print(f"[leaf_sweep] AT-isolated pool: {len(at_triples_all)} edges "
          f"(expect {FULL_FAMILY_OCC['AT']})", flush=True)

    for target in AT_SWEEP_TARGETS:
        n_take = min(target, len(at_triples_all))
        fam_prefix = at_triples_all[:n_take]
        try:
            print(f"[leaf_sweep] AT dense n={n_take} starting t={time.time()-t0:.2f}s", flush=True)
            dense_m = isolated_dense_point(fam_prefix, E, R, n_ent, n_rel)
            print(f"[leaf_sweep] AT dense n={n_take} recall={dense_m['relevant_recall']:.3f} "
                  f"t={time.time()-t0:.2f}s", flush=True)
            print(f"[leaf_sweep] AT sparse n={n_take} starting t={time.time()-t0:.2f}s", flush=True)
            sparse_m = isolated_sparse_point(fam_prefix, E, R, n_ent, n_rel, dg_key_proj,
                                             dg_val_codebook)
            print(f"[leaf_sweep] AT sparse n={n_take} recall={sparse_m['relevant_recall']:.3f} "
                  f"t={time.time()-t0:.2f}s", flush=True)
            results["AT"][str(n_take)] = {"dense": dense_m, "sparse": sparse_m}
        except Exception as e:  # noqa: BLE001 -- per-unit failure-class instrumentation, no bare except
            fail_units.append({"family": "AT", "n": n_take, "failure_class": type(e).__name__,
                               "msg": str(e)[:500]})
            print(f"[leaf_sweep] AT n={n_take} FAILED: {type(e).__name__}: {e}", flush=True)

    for fam in SINGLE_POINT_FAMILIES:
        fam_src_id = source_to_idx[fam]
        fam_mask = src_idx_shuffled == fam_src_id
        fam_rows = triples_shuffled_np[fam_mask]
        fam_triples_all = torch.from_numpy(fam_rows)
        n_take = len(fam_triples_all)
        try:
            print(f"[leaf_sweep] {fam} dense n={n_take} (full family) starting "
                  f"t={time.time()-t0:.2f}s", flush=True)
            dense_m = isolated_dense_point(fam_triples_all, E, R, n_ent, n_rel)
            print(f"[leaf_sweep] {fam} sparse n={n_take} starting t={time.time()-t0:.2f}s", flush=True)
            sparse_m = isolated_sparse_point(fam_triples_all, E, R, n_ent, n_rel, dg_key_proj,
                                             dg_val_codebook)
            results[fam][str(n_take)] = {"dense": dense_m, "sparse": sparse_m}
            print(f"[leaf_sweep] {fam} n={n_take} dense_recall={dense_m['relevant_recall']:.3f} "
                  f"sparse_recall={sparse_m['relevant_recall']:.3f} t={time.time()-t0:.2f}s", flush=True)
        except Exception as e:  # noqa: BLE001
            fail_units.append({"family": fam, "n": n_take, "failure_class": type(e).__name__,
                               "msg": str(e)[:500]})
            print(f"[leaf_sweep] {fam} n={n_take} FAILED: {type(e).__name__}: {e}", flush=True)

    # derive SAFE_LEAF_SIZE_SPARSE: largest AT sweep point whose sparse recall >= REC_THRESH_SPARSE
    at_points = sorted(((int(k), v) for k, v in results["AT"].items()), key=lambda kv: kv[0])
    safe_leaf_size_sparse = None
    safe_leaf_size_dense = None
    for n_take, v in at_points:
        if v["sparse"]["relevant_recall"] >= REC_THRESH_SPARSE:
            safe_leaf_size_sparse = n_take
        if v["dense"]["relevant_recall"] >= REC_THRESH_SPARSE:
            safe_leaf_size_dense = n_take

    def _k_family(occ, safe_size):
        if safe_size is None or safe_size <= 0:
            return None
        return max(1, math.ceil(occ / safe_size))

    k_family = {
        "AT": _k_family(FULL_FAMILY_OCC["AT"], safe_leaf_size_sparse),
        "VG": _k_family(FULL_FAMILY_OCC["VG"], safe_leaf_size_sparse),
        "CN": _k_family(FULL_FAMILY_OCC["CN"], safe_leaf_size_sparse),
    }

    elapsed = time.time() - t0
    metrics = {
        "verdict": "DIAGNOSTIC_COMPLETE" if not fail_units else "DIAGNOSTIC_PARTIAL_FAILURE",
        "verdict_msg": f"leaf-capacity sweep: safe_leaf_size_sparse={safe_leaf_size_sparse} "
                      f"safe_leaf_size_dense={safe_leaf_size_dense} k_family={k_family} "
                      f"n_fail_units={len(fail_units)}",
        "summary": f"AT sweep points={[p[0] for p in at_points]}; safe_leaf_size_sparse="
                  f"{safe_leaf_size_sparse}",
        "elapsed_s": round(elapsed, 3), "anchor_name": ANCHOR_NAME,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "n_ent": n_ent, "n_rel": n_rel, "rec_thresh_sparse": REC_THRESH_SPARSE,
        "at_sweep_targets": AT_SWEEP_TARGETS, "full_family_occ": FULL_FAMILY_OCC,
        "results": results, "fail_units": fail_units,
        "safe_leaf_size_sparse": safe_leaf_size_sparse, "safe_leaf_size_dense": safe_leaf_size_dense,
        "k_family_derived": k_family,
        "deterministic_seeding": True,
    }
    _write_metrics(OUTPUT_DIR, metrics)
    print(json.dumps({k: v for k, v in metrics.items() if k != "results"}, indent=2, default=str))


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # noqa: BLE001
        _write_crash_metrics(OUTPUT_DIR, e)
        raise
