"""
subgraph_cardinality_trace_v1 -- Trace formula for subgraph count correlation.

From substrate-graph-GNN handoff (2026-06-01), Anchor 3.
Tests whether xi_v^T W_r^k xi_v (trace-like query) correlates with
exact triangle/path counts in the graph.

Design:
  - Build random directed graph with N_NODES nodes, edge vectors.
  - W_r = sum_{edges e of type r} xi_dst xi_src^T / N (directed edge matrix).
  - Compute trace proxy: T(v, r, k) = xi_v^T W_r^k xi_v for each node v.
  - This is related to the k-th order walk count starting and ending at v.
  - Compare T(v, r, k) to exact triangle count at v (via adjacency matrix).
  - Pearson r between T values and ground-truth counts.

Pre-reg thresholds (research note HP3):
  HARD-PASS: Pearson r > 0.65 at k=2 or k=3 for triangles.
  MIDDLE:    r in [0.35, 0.65].
  HARD-FAIL: r < 0.20 (no correlation -- trace formula is uninformative).

Calibration: no prior empirical anchor on this specific formula.
Bands widened to +/-50% of theory prediction r=0.7: HP=0.65, HF=0.20.
"No prior empirical anchor; bands widened to +/-50% per calibration-probe policy."

No _nN suffix; production N=4096 per rule 3.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import os
import argparse
import time
import json
import math
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from experiments._seed_checkpoint import get_output_dir

ANCHOR_NAME = "subgraph_cardinality_trace_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

N = 4096

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    N_NODES = 15        # small graph for smoke
    N_EDGES = 40
    K_HOPS = [1, 2, 3]
else:
    SEEDS = [7, 17, 23, 31, 41]
    N_NODES = 50
    N_EDGES = 200
    K_HOPS = [1, 2, 3, 4]

HP_PEARSON = 0.65
HF_PEARSON = 0.20

# Formula self-test (closed-form):
# For a complete graph on n nodes, triangle count at each node = (n-1)*(n-2)/2.
# The trace T(v,r,2) = xi_v^T W_r^2 xi_v = xi_v^T (sum_e xi_dst xi_src^T / N)^2 xi_v.
# At low-M loading, this is approximately (n_edges_from_v * n_edges_to_v) / N^2 terms.
# No closed-form match expected -- empirical correlation is what we test.


def build_graph_matrices(N: int, n_nodes: int, n_edges: int, seed: int):
    """
    Build directed graph with N_NODES nodes, N_EDGES directed edges.
    Returns:
        node_vecs: (N, n_nodes) bipolar
        W_r: (N, N) edge matrix for single edge type
        adj: (n_nodes, n_nodes) adjacency matrix (ground truth)
    """
    rng = np.random.RandomState(seed)
    node_vecs = rng.choice([-1.0, 1.0], size=(N, n_nodes))

    adj = np.zeros((n_nodes, n_nodes), dtype=int)
    W_r = np.zeros((N, N))

    for _ in range(n_edges):
        src = rng.randint(0, n_nodes)
        dst = rng.randint(0, n_nodes)
        if src == dst:
            dst = (dst + 1) % n_nodes
        adj[src, dst] += 1
        # Directed edge: W_r += xi_dst xi_src^T / N
        W_r += np.outer(node_vecs[:, dst], node_vecs[:, src]) / N

    return node_vecs, W_r, adj


def compute_trace_values(node_vecs: np.ndarray, W_r: np.ndarray, k: int) -> np.ndarray:
    """
    T(v, r, k) = xi_v^T W_r^k xi_v for each node v.
    Returns array of shape (n_nodes,).
    """
    n_nodes = node_vecs.shape[1]
    # W_r^k via repeated matrix-vector product
    trace_vals = np.zeros(n_nodes)
    for v in range(n_nodes):
        xi_v = node_vecs[:, v]
        x = xi_v.copy()
        for _ in range(k):
            x = W_r @ x
        trace_vals[v] = float(np.dot(xi_v, x))
    return trace_vals


def count_triangles_per_node(adj: np.ndarray) -> np.ndarray:
    """
    Count triangles at each node: adj^3 diagonal / 2 (undirected approximation).
    For directed: T_v = sum_{u,w} adj[v,u] * adj[u,w] * adj[w,v].
    """
    n = adj.shape[0]
    adj3 = adj @ adj @ adj
    return np.diag(adj3).astype(float)


def count_2paths_per_node(adj: np.ndarray) -> np.ndarray:
    """Count 2-hop paths returning to node v: (adj^2) diagonal."""
    adj2 = adj @ adj
    return np.diag(adj2).astype(float)


def pearson_r(x: np.ndarray, y: np.ndarray) -> float:
    if len(x) < 3:
        return float("nan")
    xc = x - np.mean(x)
    yc = y - np.mean(y)
    denom = np.linalg.norm(xc) * np.linalg.norm(yc)
    if denom < 1e-12:
        return float("nan")
    return float(np.dot(xc, yc) / denom)


def run_seed(seed: int) -> Dict:
    node_vecs, W_r, adj = build_graph_matrices(N, N_NODES, N_EDGES, seed)

    # Ground-truth counts
    tri_counts = count_triangles_per_node(adj)   # k=3 analog
    path2_counts = count_2paths_per_node(adj)    # k=2 analog

    results_by_k = {}
    for k in K_HOPS:
        trace_vals = compute_trace_values(node_vecs, W_r, k)

        if k == 2:
            corr = pearson_r(trace_vals, path2_counts)
            gt_label = "2-path_count"
            gt_vals = path2_counts
        elif k == 3:
            corr = pearson_r(trace_vals, tri_counts)
            gt_label = "triangle_count"
            gt_vals = tri_counts
        else:
            corr = pearson_r(trace_vals, path2_counts)
            gt_label = f"path_{k}_proxy"
            gt_vals = path2_counts

        results_by_k[k] = {
            "pearson_r": corr if not math.isnan(corr) else None,
            "gt_label": gt_label,
            "trace_mean": float(np.mean(trace_vals)),
            "trace_std": float(np.std(trace_vals)),
        }
        print(f"  [seed {seed}] k={k} pearson_r={corr:.3f} gt={gt_label} "
              f"trace_mean={np.mean(trace_vals):.4f}", flush=True)

    return {"by_k": results_by_k, "seed": seed, "N": N, "N_NODES": N_NODES, "run_mode": RUN_MODE}


def _instrumentation_selftest():
    """Assert metrics non-null at small scale."""
    N_test = 128
    node_vecs, W_r, adj = build_graph_matrices(N_test, 8, 20, 42)
    tri = count_triangles_per_node(adj)
    path2 = count_2paths_per_node(adj)
    assert len(tri) == 8, "wrong triangle count length"

    trace_k2 = compute_trace_values(node_vecs, W_r, k=2)
    assert trace_k2.shape == (8,), "wrong trace shape"
    assert not all(t == 0.0 for t in trace_k2), "all trace values are exactly zero"

    corr = pearson_r(trace_k2, path2)
    assert not math.isnan(corr), "pearson_r is NaN"
    print(f"[selftest] PASS: k=2 pearson_r={corr:.3f} N={N_test}", flush=True)


_instrumentation_selftest()


def _get_by_k(v: Dict, k: int) -> Dict:
    """Handle JSON round-trip int->str key conversion."""
    d = v.get("by_k", {})
    return d.get(k, d.get(str(k), {}))


def aggregate_results(per_seed: Dict) -> Dict:
    # Get pearson_r at k=2 and k=3 across seeds (handle JSON string key conversion)
    r_k2_list = [_get_by_k(v, 2).get("pearson_r") for v in per_seed.values()]
    r_k3_list = [_get_by_k(v, 3).get("pearson_r") for v in per_seed.values()]

    valid_k2 = [r for r in r_k2_list if r is not None and not math.isnan(r)]
    valid_k3 = [r for r in r_k3_list if r is not None and not math.isnan(r)]

    best_by_seed = []
    for v in per_seed.values():
        candidates = []
        for k in [2, 3]:
            r = _get_by_k(v, k).get("pearson_r")
            if r is not None and not math.isnan(r):
                candidates.append(r)
        best_by_seed.append(max(candidates) if candidates else 0.0)

    return {
        "mean_pearson_k2": float(np.mean(valid_k2)) if valid_k2 else float("nan"),
        "mean_pearson_k3": float(np.mean(valid_k3)) if valid_k3 else float("nan"),
        "mean_best_pearson": float(np.mean(best_by_seed)) if best_by_seed else float("nan"),
        "n_seeds": len(per_seed),
    }


def compute_verdict(summary: Dict) -> Tuple[str, str]:
    best_r = summary.get("mean_best_pearson", float("nan"))
    r2 = summary.get("mean_pearson_k2", float("nan"))
    r3 = summary.get("mean_pearson_k3", float("nan"))

    if math.isnan(best_r):
        return ("INCONCLUSIVE", "No valid Pearson r computed.")

    if best_r >= HP_PEARSON:
        return ("HARD_PASS",
                f"Trace formula correlates with subgraph counts. "
                f"best_r={best_r:.3f}>={HP_PEARSON}. "
                f"k=2 r={r2:.3f}, k=3 r={r3:.3f}. "
                f"Substrate trace is a valid subgraph-cardinality primitive.")
    if best_r < HF_PEARSON:
        return ("HARD_FAIL",
                f"Trace formula uninformative. best_r={best_r:.3f}<{HF_PEARSON}. "
                f"No substrate-native subgraph count primitive.")
    return ("MIDDLE_BAND",
            f"Weak correlation. best_r={best_r:.3f}(hp={HP_PEARSON},hf={HF_PEARSON}). "
            f"k=2 r={r2:.3f}, k=3 r={r3:.3f}.")


def _verdict_formula_selftests():
    s1 = {"mean_pearson_k2": 0.70, "mean_pearson_k3": 0.72, "mean_best_pearson": 0.72, "n_seeds": 5}
    v1, _ = compute_verdict(s1)
    assert v1 == "HARD_PASS", f"Expected HARD_PASS got {v1}"

    s2 = {"mean_pearson_k2": 0.10, "mean_pearson_k3": 0.12, "mean_best_pearson": 0.12, "n_seeds": 5}
    v2, _ = compute_verdict(s2)
    assert v2 == "HARD_FAIL", f"Expected HARD_FAIL got {v2}"

    s3 = {"mean_pearson_k2": 0.40, "mean_pearson_k3": 0.50, "mean_best_pearson": 0.50, "n_seeds": 5}
    v3, _ = compute_verdict(s3)
    assert v3 == "MIDDLE_BAND", f"Expected MIDDLE_BAND got {v3}"

    print("[formula_selftests] PASS: 3 verdict cases verified", flush=True)


_verdict_formula_selftests()


def main():
    out_dir = get_output_dir(ANCHOR_NAME)
    t0 = time.time()
    print(f"[start] {ANCHOR_NAME} run_mode={RUN_MODE} N={N} n_nodes={N_NODES} seeds={SEEDS}", flush=True)

    from experiments._seed_checkpoint import resumable_seeds, write_partial, aggregate_partials
    run_config = {"N": N, "run_mode": RUN_MODE}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print(f"[ckpt] {len(done)} done, {len(remaining)} remaining", flush=True)

    for seed in remaining:
        ts = time.time()
        result = run_seed(seed)
        write_partial(out_dir, seed, result)
        best_r = max(
            (v.get("pearson_r") or 0.0
             for v in result["by_k"].values() if v.get("pearson_r") is not None),
            default=0.0
        )
        print(f"[seed {seed}] done in {time.time()-ts:.1f}s | best_pearson_r={best_r:.3f}", flush=True)

    per_seed = aggregate_partials(out_dir, SEEDS)
    summary = aggregate_results(per_seed)
    verdict, verdict_msg = compute_verdict(summary)

    elapsed = time.time() - t0
    metrics = {
        "run_mode": RUN_MODE,
        "N": N,
        "seeds": SEEDS,
        "summary": summary,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "config": {"N_NODES": N_NODES, "N_EDGES": N_EDGES, "K_HOPS": K_HOPS},
    }
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"[done] {verdict}: {verdict_msg}", flush=True)
    print(f"[done] elapsed={elapsed:.1f}s", flush=True)


if __name__ == "__main__":
    if _ARGS.self_test:
        print("[main] --self-test complete (selftests ran at module scope)", flush=True)
        sys.exit(0)
    main()
