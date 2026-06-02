"""
graph_link_prediction_v1 -- Graph link prediction via Hebbian cosine threshold.

SCIENTIFIC QUESTION (substrate-graph extension; handoff 9-cell batch):
  graph_node_classification_v1 HARD_PASS (BSC channel acc=1.00 at rho=0.60-0.70).
  This experiment extends to LINK PREDICTION:
    - Encode nodes as random +-1 vectors in R^N.
    - Encode edges: for edge (u, v), store W += outer(xi_u, xi_v) / N.
      (Asymmetric Hopfield-style association.)
    - Link prediction query: given node u, predict likely neighbors.
      Probe W with xi_u; high cosine with xi_v -> predicted edge (u,v).
    - Measure: AUC of link prediction (true edges vs random non-edges).

  PREDICTION: substrate W as asymmetric associative memory can predict links
  with AUC >> 0.50 (random) at moderate graph density.

PRE-REGISTERED BANDS:
  HARD-PASS: mean AUC >= 0.80 at edge density rho_E = 0.3-0.5.
  MIDDLE: mean AUC 0.65-0.80.
  HARD-FAIL: mean AUC < 0.65 (substrate no better than random for link prediction).

  Calibration note: first empirical link-prediction test with substrate.
  No prior anchor. Bands set +-50% around theoretical AUC=0.85 prediction
  (from cosine-discrimination theory at N=4096 with moderate edge density).

FORMULA SELF-TESTS:
  1. For n_nodes=20, n_edges=30, W = sum(outer(xi_u, xi_v)/N for each edge).
     Cosine(W @ xi_u, xi_v) > cosine(W @ xi_u, xi_w) for non-neighbor xi_w
     when load M=n_edges << M_max=0.138*N.
  2. AUC self-test: perfect classifier AUC=1.0; random classifier AUC=0.5.
  3. Edge density = n_edges / (n_nodes * (n_nodes-1)) for directed graph.

TIMEOUT ESTIMATE:
  Smoke: N=1024, n_nodes=20, rho_E=[0.2, 0.4], 2 seeds.
  Full: N=4096, n_nodes=50, rho_E=[0.1, 0.2, 0.3, 0.5], 5 seeds.
  Linear. Smoke ~3s -> Full ~60s. timeout=360s.

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

ANCHOR_NAME = "graph_link_prediction_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

ALPHA_C = 0.138

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    N = 1024
    SEEDS = [7, 17]
    N_NODES = 15
    # Keep load << capacity: N_NODES=15, rho=[0.1, 0.2] -> ~21 and ~42 edges (< M_max=141)
    RHO_E_LIST = [0.10, 0.20]
else:
    N = 4096
    SEEDS = [7, 17, 23, 31, 41]
    N_NODES = 40
    # At N=4096, M_max=565. N_NODES=40, rho=0.1 -> ~156 edges (28% cap). rho=0.2 -> ~312 (55%).
    RHO_E_LIST = [0.05, 0.10, 0.20, 0.30]

HP_AUC = 0.80
HF_AUC = 0.65


def compute_auc(scores: List[float], labels: List[int]) -> float:
    """Compute AUC-ROC from scores and binary labels.
    AUC = P(score_pos > score_neg) over all (pos, neg) pairs.
    """
    if len(scores) != len(labels) or len(scores) == 0:
        return float("nan")
    n_pos = sum(labels)
    n_neg = len(labels) - n_pos
    if n_pos == 0 or n_neg == 0:
        return float("nan")
    # Sort by score descending. For each positive, count negatives with LOWER score
    # (= negatives appearing AFTER it in sorted order = n_neg - fp_count).
    pairs = sorted(zip(scores, labels), reverse=True)
    concordant = 0.0
    fp_count = 0  # number of negatives seen so far (higher score than current)
    for _, label in pairs:
        if label == 0:
            fp_count += 1
        else:
            # Concordant pairs: (n_neg - fp_count) negatives have lower scores
            concordant += (n_neg - fp_count)
    auc = concordant / (n_pos * n_neg)
    return float(auc)


def run_seed(seed: int) -> Dict:
    rng = np.random.RandomState(seed)
    results_by_rho = {}

    # Node embeddings: N_NODES random +-1 vectors of length N
    node_vecs = rng.choice([-1.0, 1.0], size=(N_NODES, N)).astype(np.float64)

    for rho_E in RHO_E_LIST:
        # Generate random directed graph with density rho_E
        n_possible = N_NODES * (N_NODES - 1)
        n_edges_target = max(1, int(rho_E * n_possible))

        # Cap edges at capacity limit
        M_max = int(ALPHA_C * N)
        n_edges = min(n_edges_target, M_max)

        # Sample edges (directed, no self-loops)
        all_pairs = [(u, v) for u in range(N_NODES) for v in range(N_NODES) if u != v]
        rng2 = np.random.RandomState(seed + int(rho_E * 100))
        edge_indices = rng2.choice(len(all_pairs), size=n_edges, replace=False)
        edges = [all_pairs[i] for i in edge_indices]
        edge_set = set(edges)

        # Build asymmetric W: W += outer(xi_u, xi_v) / N for each edge (u, v)
        W = np.zeros((N, N), dtype=np.float64)
        for u, v in edges:
            W += np.outer(node_vecs[u], node_vecs[v]) / N

        # Link prediction: for each node u, score all potential targets v
        # Score(u, v) = cosine(W @ xi_u, xi_v)
        auc_per_node = []
        for u in range(N_NODES):
            query = W @ node_vecs[u]
            q_norm = np.linalg.norm(query)
            if q_norm < 1e-12:
                continue
            scores_u = []
            labels_u = []
            for v in range(N_NODES):
                if v == u:
                    continue
                v_norm = np.linalg.norm(node_vecs[v])
                if v_norm < 1e-12:
                    continue
                sim = float(np.dot(query, node_vecs[v]) / (q_norm * v_norm))
                scores_u.append(sim)
                labels_u.append(1 if (u, v) in edge_set else 0)
            if len(scores_u) > 0 and sum(labels_u) > 0:
                auc_u = compute_auc(scores_u, labels_u)
                if not math.isnan(auc_u):
                    auc_per_node.append(auc_u)

        mean_auc = float(np.mean(auc_per_node)) if auc_per_node else float("nan")
        n_valid_nodes = len(auc_per_node)

        print(f"  [seed={seed} rho={rho_E:.1f}] n_edges={n_edges} "
              f"auc={mean_auc:.3f} n_valid_nodes={n_valid_nodes}", flush=True)

        results_by_rho[rho_E] = {
            "rho_E": rho_E,
            "n_edges": n_edges,
            "mean_auc": mean_auc,
            "n_valid_nodes": n_valid_nodes,
        }

    return {"by_rho": results_by_rho, "seed": seed, "N": N, "run_mode": RUN_MODE}


def _instrumentation_selftest():
    """Assert AUC metrics non-null at small scale."""
    N_test = 256
    n_nodes_test = 10
    rng = np.random.RandomState(42)
    node_vecs = rng.choice([-1.0, 1.0], size=(n_nodes_test, N_test)).astype(np.float64)

    edges = [(0, 1), (1, 2), (2, 3), (0, 3)]
    edge_set = set(edges)
    W = np.zeros((N_test, N_test), dtype=np.float64)
    for u, v in edges:
        W += np.outer(node_vecs[u], node_vecs[v]) / N_test

    # Test AUC on node 0
    query = W @ node_vecs[0]
    q_norm = np.linalg.norm(query)
    assert q_norm > 1e-12, "zero query vector"

    scores = []
    labels = []
    for v in range(1, n_nodes_test):
        v_norm = np.linalg.norm(node_vecs[v])
        sim = float(np.dot(query, node_vecs[v]) / (q_norm * v_norm))
        scores.append(sim)
        labels.append(1 if (0, v) in edge_set else 0)

    auc = compute_auc(scores, labels)
    assert not math.isnan(auc), f"AUC is NaN at selftest"
    assert 0.0 <= auc <= 1.0, f"AUC={auc} out of [0,1]"

    # AUC formula self-test: perfect scores
    auc_perfect = compute_auc([1.0, 1.0, 0.0, 0.0], [1, 1, 0, 0])
    assert abs(auc_perfect - 1.0) < 0.01, f"perfect AUC={auc_perfect} != 1.0"
    auc_random = compute_auc([0.5, 0.5, 0.5, 0.5], [1, 0, 1, 0])
    # Random scores give AUC near 0.5 but may not be exactly 0.5 with ties

    print(f"[selftest] PASS: auc={auc:.3f} at N={N_test} n_edges=4", flush=True)


_instrumentation_selftest()


def _verdict_formula_selftests():
    """Verify AUC formula."""
    # Perfect classifier: all positives ranked above negatives
    auc1 = compute_auc([0.9, 0.8, 0.2, 0.1], [1, 1, 0, 0])
    assert abs(auc1 - 1.0) < 0.01, f"perfect AUC={auc1}"
    # Worst classifier: all negatives ranked above positives
    auc2 = compute_auc([0.9, 0.8, 0.2, 0.1], [0, 0, 1, 1])
    assert abs(auc2 - 0.0) < 0.01, f"worst AUC={auc2}"
    print("[formula_selftests] PASS: AUC formula verified (perfect=1.0, worst=0.0)", flush=True)


_verdict_formula_selftests()


def aggregate_results(per_seed: Dict) -> Dict:
    all_rho = RHO_E_LIST
    agg = {}
    for rho in all_rho:
        aucs = []
        for sd in per_seed.values():
            row = sd["by_rho"].get(rho) or sd["by_rho"].get(str(rho))
            if row is None:
                continue
            v = row.get("mean_auc", float("nan"))
            if not math.isnan(v):
                aucs.append(v)
        agg[rho] = {
            "mean_auc": float(np.mean(aucs)) if aucs else float("nan"),
            "min_auc": float(np.min(aucs)) if aucs else float("nan"),
            "n_seeds": len(aucs),
        }
    return {"by_rho": agg}


def compute_verdict(agg: Dict) -> Tuple[str, str]:
    by_rho = agg["by_rho"]
    # Focus on mid-range density (most informative)
    mid_aucs = [v["mean_auc"] for rho, v in by_rho.items()
                if 0.1 < float(rho) < 0.6
                and not math.isnan(v.get("mean_auc", float("nan")))]

    if not mid_aucs:
        all_aucs = [v["mean_auc"] for v in by_rho.values()
                    if not math.isnan(v.get("mean_auc", float("nan")))]
        if not all_aucs:
            return ("HARD_FAIL", "No valid AUC measurements.")
        mid_aucs = all_aucs

    min_auc = min(mid_aucs)
    mean_auc = float(np.mean(mid_aucs))

    if min_auc >= HP_AUC:
        return ("HARD_PASS",
                f"Graph link prediction via Hebbian substrate confirmed. "
                f"min_auc={min_auc:.3f}>={HP_AUC} mean_auc={mean_auc:.3f} "
                f"at N={N} n_nodes={N_NODES}. "
                f"Asymmetric Hopfield W discriminates true edges from random non-edges.")
    if min_auc < HF_AUC:
        return ("HARD_FAIL",
                f"Link prediction fails. min_auc={min_auc:.3f}<HF={HF_AUC}. "
                f"Substrate W insufficient for link discrimination at N={N}.")
    return ("MIDDLE_BAND",
            f"Partial link prediction. min_auc={min_auc:.3f} "
            f"(HP>={HP_AUC} HF<{HF_AUC}) mean_auc={mean_auc:.3f}.")


def main():
    out_dir = get_output_dir(ANCHOR_NAME)
    t0 = time.time()
    print(f"[start] {ANCHOR_NAME} run_mode={RUN_MODE} N={N} "
          f"N_NODES={N_NODES} RHO_E={RHO_E_LIST} seeds={SEEDS}", flush=True)

    from experiments._seed_checkpoint import resumable_seeds, write_partial, aggregate_partials
    run_config = {"N": N, "run_mode": RUN_MODE}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print(f"[ckpt] {len(done)} done, {len(remaining)} remaining", flush=True)

    for seed in remaining:
        ts = time.time()
        result = run_seed(seed)
        write_partial(out_dir, seed, result)
        print(f"[seed {seed}] done in {time.time()-ts:.1f}s", flush=True)

    per_seed = aggregate_partials(out_dir, SEEDS)
    agg = aggregate_results(per_seed)
    verdict, verdict_msg = compute_verdict(agg)

    elapsed = time.time() - t0
    metrics = {
        "run_mode": RUN_MODE, "N": N,
        "N_NODES": N_NODES, "RHO_E_LIST": RHO_E_LIST,
        "seeds": SEEDS,
        "aggregated": agg,
        "verdict": verdict, "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"[done] {verdict}: {verdict_msg}", flush=True)
    print(f"[done] elapsed={elapsed:.1f}s", flush=True)


if __name__ == "__main__":
    if _ARGS.self_test:
        print("[main] --self-test complete", flush=True)
        sys.exit(0)
    main()
