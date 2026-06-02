"""
graph_link_prediction_per_edge_keying_v1 -- Per-edge VSA bundle encoding for directed link prediction.

RESCUE from graph_link_prediction_v1 AUC=0.5 (mechanism failure):
  Root cause: node-aggregate cosine probe is O(1/sqrt(N)) for all node pairs under
  multi-edge superposition -- all nodes appear equidistant (fundamental mechanism mismatch).
  Fix: per-edge VSA bundle encoding: bundle(source_atom, edge_type_atom, target_atom)
  per directed edge. Standard HDC graph encoding (Kleyko et al. 2022).

SCIENTIFIC QUESTION:
  Can substrate perform directed link prediction for labeled edges via per-edge
  VSA bundle encoding? AUC >= 0.75 on held-out edges, N=4096, 3/5 seeds.

ENCODING DESIGN (per research rescue spec 2026-06-02):
  Per directed edge (u, e_type, v): store bundle = bind(xi_u, bind(xi_etype, xi_v)).
  For +-1 BSC vectors: bind = element-wise product (XOR bind).
  Query "does source u link to target v via edge type e?":
    probe = bind(xi_u, bind(xi_etype, xi_v)); check if probe is in memory (high overlap).
  Memory = Hopfield W: W += outer(bundle_edge, bundle_edge) / N for each edge.
  Retrieval: W @ probe should align with bundle_edge if edge exists.
  Link prediction score: max overlap of W @ probe(u, e, ?) over all candidate v.

PRE-REGISTERED BANDS (from research rescue note 2026-06-02):
  HARD-PASS: AUC >= 0.75, N=4096, 3/5 seeds, per-edge key architecture.
  MIDDLE: AUC in [0.60, 0.75).
  HARD-FAIL: AUC <= 0.55 after per-edge fix (indistinguishable from random despite fix).

P_deflated=0.60 per research note (per-edge keying well-established in VSA literature).

FORMULA SELF-TESTS:
  1. Perfect encode-decode: for single stored edge (u, e, v):
     W = outer(bundle_uev, bundle_uev) / N.
     W @ bundle_uev = bundle_uev (attractor at stored pattern).
     Cosine(W @ bundle_uev, bundle_uev) ~ 1.0.
  2. Non-edge discrimination: for non-stored edge (u, e, w) (w != v):
     cosine(W @ bundle_uew, bundle_uew) << cosine(W @ bundle_uev, bundle_uev).
  3. AUC formula: concordant_pairs / (n_pos * n_neg). AUC=1.0 for perfect classifier.
  4. PROT-018: no _nN suffix; production N=4096 stated here per rule 3.

PROT-018: no _nN suffix; production N=4096 per rule 3.
PROT-021: run_config includes N, run_mode.
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

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials

ANCHOR_NAME = "graph_link_prediction_per_edge_keying_v1"

# PROT-018: no _nN suffix; production N=4096 per rule 3 (stated explicitly)
N = 4096

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

ALPHA_C = 0.138  # Hopfield capacity limit (conservative)

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    N_NODES = 15
    N_EDGE_TYPES = 2
    RHO_E_LIST = [0.10, 0.20]
    N_QUERIES = 5
else:
    SEEDS = [7, 17, 23, 31, 41]
    N_NODES = 30
    N_EDGE_TYPES = 3
    RHO_E_LIST = [0.05, 0.10, 0.20]
    N_QUERIES = 10

HP_AUC = 0.75
HF_AUC = 0.55
HP_MIN_SEEDS = 3


def vsa_bind(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """VSA bind: element-wise product for +-1 BSC vectors."""
    return a * b


def vsa_bundle(vecs: List[np.ndarray]) -> np.ndarray:
    """VSA bundle: sign(sum) for +-1 BSC vectors."""
    s = np.sum(vecs, axis=0)
    result = np.sign(s)
    result[result == 0] = 1.0
    return result


def compute_auc(scores: List[float], labels: List[int]) -> float:
    """AUC-ROC via concordant pairs."""
    if len(scores) != len(labels) or len(scores) == 0:
        return float("nan")
    n_pos = sum(labels)
    n_neg = len(labels) - n_pos
    if n_pos == 0 or n_neg == 0:
        return float("nan")
    pairs = sorted(zip(scores, labels), reverse=True)
    concordant = 0.0
    fp_count = 0
    for _, label in pairs:
        if label == 0:
            fp_count += 1
        else:
            concordant += (n_neg - fp_count)
    return float(concordant / (n_pos * n_neg))


def run_seed(seed: int) -> Dict:
    rng = np.random.RandomState(seed)

    # Node and edge-type atoms: random +-1 vectors
    node_atoms = rng.choice([-1.0, 1.0], size=(N_NODES, N)).astype(np.float64)
    etype_atoms = rng.choice([-1.0, 1.0], size=(N_EDGE_TYPES, N)).astype(np.float64)

    results_by_rho: Dict = {}

    for rho_E in RHO_E_LIST:
        n_possible = N_NODES * (N_NODES - 1)
        n_edges_target = max(1, int(rho_E * n_possible))

        # Cap at capacity
        M_max = int(ALPHA_C * N)
        n_edges = min(n_edges_target, M_max)

        # Sample edges: (source_node, edge_type, target_node)
        all_triples = [
            (u, e, v)
            for u in range(N_NODES)
            for e in range(N_EDGE_TYPES)
            for v in range(N_NODES)
            if u != v
        ]
        n_possible_typed = len(all_triples)
        n_edges_typed = min(n_edges, n_possible_typed)

        rng2 = np.random.RandomState(seed + int(rho_E * 1000))
        edge_idx = rng2.choice(n_possible_typed, size=n_edges_typed, replace=False)
        edges = [all_triples[i] for i in edge_idx]
        edge_set = set(edges)

        # Build Hopfield W with per-edge bundle encoding
        # For each (u, e_type, v): bundle = bind(xi_u, bind(xi_etype, xi_v))
        W = np.zeros((N, N), dtype=np.float64)
        for (u, e_type, v) in edges:
            bundle = vsa_bind(node_atoms[u], vsa_bind(etype_atoms[e_type], node_atoms[v]))
            W += np.outer(bundle, bundle) / N

        # Link prediction: for each (u, e_type) query, score all candidate targets v
        # Score(u, e_type, v) = cosine(W @ bundle(u, e_type, v), bundle(u, e_type, v))
        # This is equivalent to: how strongly does W "remember" the bundle for (u,e,v)?
        aucs = []
        query_count = 0
        for u in range(N_NODES):
            for e_type in range(N_EDGE_TYPES):
                if query_count >= N_QUERIES * N_NODES:
                    break
                scores_q = []
                labels_q = []
                for v in range(N_NODES):
                    if v == u:
                        continue
                    bundle_probe = vsa_bind(
                        node_atoms[u],
                        vsa_bind(etype_atoms[e_type], node_atoms[v])
                    )
                    # Score: pattern activation = dot(bundle_probe, W @ bundle_probe) / N^2
                    # Equivalently: normalized inner product with memory output
                    retrieved = W @ bundle_probe
                    r_norm = np.linalg.norm(retrieved)
                    p_norm = np.linalg.norm(bundle_probe)
                    if r_norm < 1e-12 or p_norm < 1e-12:
                        score = 0.0
                    else:
                        score = float(np.dot(retrieved, bundle_probe) / (r_norm * p_norm))
                    scores_q.append(score)
                    labels_q.append(1 if (u, e_type, v) in edge_set else 0)

                if sum(labels_q) > 0:
                    auc_q = compute_auc(scores_q, labels_q)
                    if not math.isnan(auc_q):
                        aucs.append(auc_q)
                        query_count += 1

        mean_auc = float(np.mean(aucs)) if aucs else float("nan")
        print(
            f"  [seed={seed} rho={rho_E:.2f}] n_edges={n_edges_typed} "
            f"n_valid_queries={len(aucs)} mean_auc={mean_auc:.3f}",
            flush=True
        )
        results_by_rho[rho_E] = {
            "rho_E": rho_E,
            "n_edges": n_edges_typed,
            "mean_auc": mean_auc,
            "n_valid_queries": len(aucs),
        }

    return {"by_rho": results_by_rho, "seed": seed, "N": N, "run_mode": RUN_MODE}


def _instrumentation_selftest():
    """
    Assert per-edge bundle scoring is discriminative at small scale.
    Single stored edge should have higher score than non-stored edges.
    """
    N_test = 512
    rng = np.random.RandomState(42)
    xi_u = rng.choice([-1.0, 1.0], size=(N_test,)).astype(np.float64)
    xi_e = rng.choice([-1.0, 1.0], size=(N_test,)).astype(np.float64)
    xi_v = rng.choice([-1.0, 1.0], size=(N_test,)).astype(np.float64)
    xi_w = rng.choice([-1.0, 1.0], size=(N_test,)).astype(np.float64)

    # Store edge (u, e, v)
    bundle_uev = vsa_bind(xi_u, vsa_bind(xi_e, xi_v))
    W_test = np.outer(bundle_uev, bundle_uev) / N_test

    # Score for stored edge (u, e, v)
    retrieved_stored = W_test @ bundle_uev
    score_stored = float(
        np.dot(retrieved_stored, bundle_uev) /
        (np.linalg.norm(retrieved_stored) * np.linalg.norm(bundle_uev) + 1e-12)
    )

    # Score for non-edge (u, e, w)
    bundle_uew = vsa_bind(xi_u, vsa_bind(xi_e, xi_w))
    retrieved_nonstored = W_test @ bundle_uew
    score_nonstored = float(
        np.dot(retrieved_nonstored, bundle_uew) /
        (np.linalg.norm(retrieved_nonstored) * np.linalg.norm(bundle_uew) + 1e-12)
    )

    assert score_stored > score_nonstored + 0.1, (
        f"stored edge score={score_stored:.4f} not clearly > non-stored={score_nonstored:.4f}; "
        f"per-edge keying not discriminative at N={N_test}"
    )

    # AUC formula self-test: perfect classifier
    auc_perfect = compute_auc([0.9, 0.8, 0.2, 0.1], [1, 1, 0, 0])
    assert abs(auc_perfect - 1.0) < 0.01, f"perfect AUC={auc_perfect:.4f} != 1.0"
    auc_worst = compute_auc([0.9, 0.8, 0.2, 0.1], [0, 0, 1, 1])
    assert abs(auc_worst - 0.0) < 0.01, f"worst AUC={auc_worst:.4f} != 0.0"

    # VSA bind round-trip: bind(bind(a,b),b) = a
    recovered = vsa_bind(vsa_bind(xi_u, xi_e), xi_e)
    assert np.allclose(recovered, xi_u), "VSA bind round-trip failed"

    print(
        f"[selftest] PASS: score_stored={score_stored:.4f} > score_nonstored={score_nonstored:.4f}; "
        f"AUC perfect/worst verified; bind round-trip OK (N={N_test})",
        flush=True
    )


_instrumentation_selftest()


def _verdict_formula_selftests():
    """Verify AUC formula and threshold ordering."""
    # Concordant pairs formula
    # 4 pairs: (pos_score=0.9, neg_score=0.2), (0.9, 0.1), (0.8, 0.2), (0.8, 0.1)
    # All concordant -> AUC = 4 / (2 * 2) = 1.0
    auc1 = compute_auc([0.9, 0.8, 0.2, 0.1], [1, 1, 0, 0])
    assert abs(auc1 - 1.0) < 0.01, f"AUC formula: {auc1:.4f} != 1.0"

    assert HP_AUC > HF_AUC, f"HP_AUC={HP_AUC} must exceed HF_AUC={HF_AUC}"
    assert HF_AUC > 0.50, f"HF_AUC={HF_AUC} must be above 0.50 (random baseline)"

    print(
        f"[formula_selftests] PASS: AUC formula OK; "
        f"HP={HP_AUC} > HF={HF_AUC} > random=0.50",
        flush=True
    )


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
    mid_aucs = [
        v["mean_auc"] for rho, v in by_rho.items()
        if not math.isnan(v.get("mean_auc", float("nan")))
        and v.get("n_seeds", 0) >= HP_MIN_SEEDS
    ]
    all_aucs = [
        v["mean_auc"] for v in by_rho.values()
        if not math.isnan(v.get("mean_auc", float("nan")))
    ]

    if not all_aucs:
        return ("HARD_FAIL", "No valid AUC measurements.")

    eval_aucs = mid_aucs if mid_aucs else all_aucs
    min_auc = min(eval_aucs)
    mean_auc = float(np.mean(eval_aucs))
    n_seeds_min = min(
        (v.get("n_seeds", 0) for v in by_rho.values()),
        default=0
    )

    if min_auc >= HP_AUC and n_seeds_min >= HP_MIN_SEEDS:
        return (
            "HARD_PASS",
            f"Graph link prediction via per-edge VSA keying confirmed. "
            f"min_auc={min_auc:.3f}>={HP_AUC} mean_auc={mean_auc:.3f} "
            f"n_seeds_min={n_seeds_min}>={HP_MIN_SEEDS} N={N} N_NODES={N_NODES}. "
            f"Per-edge bundle(xi_u, bind(xi_etype, xi_v)) discriminates true edges. "
            f"Graph audit/compliance capability confirmed with correct encoding."
        )
    if mean_auc <= HF_AUC:
        return (
            "HARD_FAIL",
            f"Link prediction fails even with per-edge keying. "
            f"mean_auc={mean_auc:.3f}<={HF_AUC}. "
            f"Substrate not capable of graph link prediction via this architecture. N={N}."
        )
    return (
        "MIDDLE_BAND",
        f"Partial link prediction. mean_auc={mean_auc:.3f} "
        f"(HP>={HP_AUC} HF<={HF_AUC}) min_auc={min_auc:.3f}. N={N}."
    )


def main():
    out_dir = get_output_dir(ANCHOR_NAME)
    t0 = time.time()
    print(
        f"[start] {ANCHOR_NAME} run_mode={RUN_MODE} N={N} "
        f"N_NODES={N_NODES} N_EDGE_TYPES={N_EDGE_TYPES} "
        f"RHO_E={RHO_E_LIST} seeds={SEEDS}",
        flush=True
    )

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
        "N_NODES": N_NODES, "N_EDGE_TYPES": N_EDGE_TYPES,
        "RHO_E_LIST": RHO_E_LIST, "seeds": SEEDS,
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
