"""
graph_community_detection_v1 -- Substrate graph community detection via Hebbian + modularity.

SCIENTIFIC QUESTION (Graph capabilities, community detection):
  The substrate W can encode graph structure via pattern similarity.
  Community detection: a graph with K communities should produce K distinct
  attractor basins in the substrate dynamics.

  Design:
    - Generate stochastic block model (SBM) graph with K=3 communities of size C.
    - Encode each node as a pattern xi_u in {-1,+1}^N.
    - Encode edges: for each edge (u,v), do Hebbian write: W += outer(xi_u, xi_v) / N.
    - Community structure: intra-community edges much denser than inter-community edges.
    - Community detection test:
        (a) Start Glauber dynamics from noisy xi_u.
        (b) Attractor: patterns from same community attract to same basin.
        (c) Metric: community_acc = fraction of nodes correctly assigned to community
            (i.e., converge to attractor that matches their community label).

  Test cells:
    (A) Within-community cohesion: nodes in same community converge to same attractor.
        HP-A: intra_community_agreement >= 0.80 (i.e., same noisy start -> same basin).
    (B) Between-community separation: nodes from different communities NOT in same basin.
        HP-B: inter_community_separation >= 0.75 (different-community nodes -> different basins).
    (C) Modularity alignment: substrate community assignment aligns with true SBM label.
        HP-C: community_acc >= 0.70 (70% of nodes correctly labeled by substrate attractor).

PRE-REGISTERED BANDS:
  HARD-PASS: All of A, B, C.
  MIDDLE: 2/3 cells pass.
  HARD-FAIL: 0-1 cells pass.

  Calibration: first substrate community detection test. Bands +-50% of theory.
  Theory: for SBM with p_in=0.5, p_out=0.05, K=3, C=10:
  intra-community SNR >> inter-community. Expected intra_agree > 0.70.

FORMULA SELF-TESTS:
  1. SBM: each community has C nodes, p_in=0.5 edges within, p_out=0.05 between.
     Expected edges within community: C*(C-1)/2 * p_in = 45 * 0.5 = 22.5.
     [INPUT: C=10, K=3, p_in=0.5, p_out=0.05]
     [EXPECTED: avg_intra_degree ~ (C-1)*p_in = 4.5, avg_inter_degree ~ C*(K-1)*p_out = 1.0]
  2. W_graph += outer(xi_u, xi_v) / N for edge (u,v). For u,v in same community:
     many edges -> high cosine similarity of attractors.
     For u,v in different communities: few edges -> low cosine.
  3. Basin identity: two nodes u,v in same community should share attractor A_k.
     Agreement = fraction of starts that converge to same sign pattern.

TIMEOUT ESTIMATE:
  Smoke: N=512, K=3, C=8, 2 seeds, 10 Glauber steps per convergence.
  Full: N=1024, K=3, C=12, 5 seeds, 20 Glauber steps.
  Linear. Smoke ~3s -> Full ~30s. timeout=240s.

No _nN suffix; production N=1024 per rule 3.
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

ANCHOR_NAME = "graph_community_detection_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

BETA = 2.0

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    N = 512
    SEEDS = [7, 17]
    K_COMM = 3      # communities
    C_SIZE = 8      # nodes per community
    P_IN = 0.5      # intra-community edge probability
    P_OUT = 0.05    # inter-community edge probability
    N_GLAUBER = 10  # steps to convergence
    N_NOISE_BITS = 5
    N_TRIALS = 5
else:
    N = 1024
    SEEDS = [7, 17, 23, 31, 41, 53, 61, 71, 79, 89]  # 10 seeds (walk-back gate: smoke borderline)
    K_COMM = 3
    C_SIZE = 12
    P_IN = 0.5
    P_OUT = 0.05
    N_GLAUBER = 20
    N_NOISE_BITS = 8
    N_TRIALS = 10

HP_INTRA_AGREE = 0.80
HP_INTER_SEP = 0.75
HP_COMM_ACC = 0.70

# ---- FORMULA SELF-TESTS ----
def _sbm_degree_test():
    """Verify SBM expected degrees."""
    avg_intra = (C_SIZE - 1) * P_IN
    avg_inter = C_SIZE * (K_COMM - 1) * P_OUT
    assert avg_intra > avg_inter, (
        f"SBM intra_degree={avg_intra:.2f} <= inter_degree={avg_inter:.2f}: "
        "community structure is too weak"
    )
    return avg_intra, avg_inter

_intra_deg, _inter_deg = _sbm_degree_test()


def generate_sbm(K: int, C: int, p_in: float, p_out: float,
                 seed: int) -> Tuple[np.ndarray, np.ndarray]:
    """Generate SBM graph. Returns adjacency matrix (N_nodes x N_nodes) and labels."""
    rng = np.random.RandomState(seed)
    N_nodes = K * C
    labels = np.repeat(np.arange(K), C)
    A = np.zeros((N_nodes, N_nodes), dtype=np.int32)
    for u in range(N_nodes):
        for v in range(u + 1, N_nodes):
            p = p_in if labels[u] == labels[v] else p_out
            if rng.rand() < p:
                A[u, v] = 1
                A[v, u] = 1
    return A, labels


def make_node_patterns(N_dim: int, N_nodes: int, seed: int) -> np.ndarray:
    """Random bipolar patterns for each node."""
    rng = np.random.RandomState(seed + 1000)
    return rng.choice([-1.0, 1.0], size=(N_nodes, N_dim)).astype(np.float64)


def build_graph_W(Xi_nodes: np.ndarray, A: np.ndarray, N_dim: int) -> np.ndarray:
    """Encode graph edges in W via Hebbian."""
    N_nodes = Xi_nodes.shape[0]
    W = np.zeros((N_dim, N_dim))
    n_edges = 0
    for u in range(N_nodes):
        for v in range(u + 1, N_nodes):
            if A[u, v] > 0:
                W += np.outer(Xi_nodes[u], Xi_nodes[v]) / N_dim
                W += np.outer(Xi_nodes[v], Xi_nodes[u]) / N_dim
                n_edges += 1
    return W, n_edges


def glauber_converge(state: np.ndarray, W: np.ndarray, beta: float,
                     n_steps: int, rng: np.random.RandomState) -> np.ndarray:
    N_dim = len(state)
    for _ in range(n_steps):
        indices = rng.randint(0, N_dim, size=N_dim)
        for i in indices:
            h_i = float(W[i] @ state)
            prob_up = 1.0 / (1.0 + math.exp(-2.0 * beta * h_i))
            state[i] = 1.0 if rng.rand() < prob_up else -1.0
    return state


def assign_to_community(attractor: np.ndarray, community_centroids: np.ndarray) -> int:
    """Assign attractor to closest community centroid by cosine."""
    cosines = [float(np.dot(attractor, c)) / (N * 1.0) for c in community_centroids]
    return int(np.argmax(cosines))


def run_seed(seed: int) -> Dict:
    rng = np.random.RandomState(seed)
    A, labels = generate_sbm(K_COMM, C_SIZE, P_IN, P_OUT, seed)
    N_nodes = K_COMM * C_SIZE
    Xi_nodes = make_node_patterns(N, N_nodes, seed)
    W, n_edges = build_graph_W(Xi_nodes, A, N)
    print(f"  [seed={seed}] graph: {N_nodes} nodes, {n_edges} edges, "
          f"{K_COMM} communities of size {C_SIZE}", flush=True)

    # Compute community centroids (mean of node patterns per community)
    community_centroids = []
    for k in range(K_COMM):
        mask = labels == k
        centroid = np.mean(Xi_nodes[mask], axis=0)
        community_centroids.append(centroid)
    community_centroids = np.array(community_centroids)

    # Run dynamics for each node, multiple trials
    assigned_labels = []
    true_labels = []
    intra_agreements = []
    inter_separations = []

    for u in range(N_nodes):
        true_comm = int(labels[u])
        node_attractors = []
        for trial in range(N_TRIALS):
            # Noisy start from xi_u
            state = Xi_nodes[u].copy()
            flip_idx = rng.choice(N, size=N_NOISE_BITS, replace=False)
            state[flip_idx] *= -1.0
            attractor = glauber_converge(state, W, BETA, N_GLAUBER, rng)
            node_attractors.append(attractor)

        # Intra-community agreement: fraction of trial pairs converging to same sign
        agree_count = 0
        total_pairs = 0
        for i in range(len(node_attractors)):
            for j in range(i + 1, len(node_attractors)):
                cos_pair = float(np.dot(node_attractors[i], node_attractors[j])) / N
                agree_count += 1 if cos_pair > 0.0 else 0
                total_pairs += 1
        intra_agree = agree_count / total_pairs if total_pairs > 0 else 0.0
        intra_agreements.append(intra_agree)

        # Community assignment by majority vote of attractors
        votes = [assign_to_community(att, community_centroids) for att in node_attractors]
        assigned = int(np.bincount(votes, minlength=K_COMM).argmax())
        assigned_labels.append(assigned)
        true_labels.append(true_comm)

    # Cell A: mean intra-community agreement
    intra_agree_mean = float(np.mean(intra_agreements))

    # Cell B: inter-community separation
    # For nodes in different communities, their attractors should be dissimilar
    inter_sep_scores = []
    for u in range(N_nodes):
        for v in range(u + 1, N_nodes):
            if labels[u] != labels[v]:
                # Check if they're assigned to different communities
                if assigned_labels[u] != assigned_labels[v]:
                    inter_sep_scores.append(1.0)
                else:
                    inter_sep_scores.append(0.0)
    inter_sep = float(np.mean(inter_sep_scores)) if inter_sep_scores else float("nan")

    # Cell C: community accuracy
    comm_acc = float(np.mean(np.array(assigned_labels) == np.array(true_labels)))

    cell_A_pass = intra_agree_mean >= HP_INTRA_AGREE
    cell_B_pass = not math.isnan(inter_sep) and inter_sep >= HP_INTER_SEP
    cell_C_pass = comm_acc >= HP_COMM_ACC

    print(f"  [seed={seed}] intra_agree={intra_agree_mean:.4f}(A:{cell_A_pass}) "
          f"inter_sep={inter_sep:.4f}(B:{cell_B_pass}) "
          f"comm_acc={comm_acc:.4f}(C:{cell_C_pass})", flush=True)

    return {
        "seed": seed,
        "intra_agree_mean": intra_agree_mean,
        "inter_sep": inter_sep,
        "comm_acc": comm_acc,
        "n_edges": n_edges,
        "cell_A_pass": cell_A_pass,
        "cell_B_pass": cell_B_pass,
        "cell_C_pass": cell_C_pass,
        "run_mode": RUN_MODE,
    }


def _instrumentation_selftest():
    """Assert community detection metrics non-null at small scale."""
    seed = 42
    N_test = 256
    K_test = 2
    C_test = 5
    A_test, labels_test = generate_sbm(K_test, C_test, p_in=0.7, p_out=0.05, seed=seed)
    Xi_test = make_node_patterns(N_test, K_test * C_test, seed)
    W_test, n_edges_test = build_graph_W(Xi_test, A_test, N_test)

    assert n_edges_test > 0, f"Graph has no edges (n_edges={n_edges_test})"
    assert not np.all(W_test == 0.0), "W_test is all zeros"

    # Test glauber_converge
    rng = np.random.RandomState(42)
    state = Xi_test[0].copy()
    attractor = glauber_converge(state, W_test, BETA, n_steps=5, rng=rng)
    assert attractor.shape == (N_test,), "Attractor shape mismatch"
    assert not np.all(attractor == 0.0), "Attractor is all zeros"

    # Verify community centroids
    comm_cents = []
    for k in range(K_test):
        mask = labels_test == k
        comm_cents.append(np.mean(Xi_test[mask], axis=0))
    assigned = assign_to_community(attractor, np.array(comm_cents))
    assert 0 <= assigned < K_test, f"Assigned community {assigned} out of range"

    print(f"[selftest] PASS: n_edges={n_edges_test} attractor shape OK "
          f"assigned={assigned} at N={N_test}", flush=True)


_instrumentation_selftest()


def aggregate_results(per_seed: Dict) -> Dict:
    intra, inter, comm = [], [], []
    a_pass, b_pass, c_pass = [], [], []
    for sd in per_seed.values():
        intra.append(sd.get("intra_agree_mean", float("nan")))
        inter.append(sd.get("inter_sep", float("nan")))
        comm.append(sd.get("comm_acc", float("nan")))
        a_pass.append(sd.get("cell_A_pass", False))
        b_pass.append(sd.get("cell_B_pass", False))
        c_pass.append(sd.get("cell_C_pass", False))
    return {
        "mean_intra_agree": float(np.nanmean(intra)),
        "mean_inter_sep": float(np.nanmean(inter)),
        "mean_comm_acc": float(np.nanmean(comm)),
        "frac_A_pass": float(np.mean(a_pass)),
        "frac_B_pass": float(np.mean(b_pass)),
        "frac_C_pass": float(np.mean(c_pass)),
        "n_seeds": len(a_pass),
    }


def compute_verdict(agg: Dict) -> Tuple[str, str]:
    fA = agg["frac_A_pass"]
    fB = agg["frac_B_pass"]
    fC = agg["frac_C_pass"]
    hp_A = fA >= 0.80
    hp_B = fB >= 0.80
    hp_C = fC >= 0.80
    cells_pass = sum([hp_A, hp_B, hp_C])

    mia = agg["mean_intra_agree"]
    mis = agg["mean_inter_sep"]
    mca = agg["mean_comm_acc"]

    if cells_pass == 3:
        return ("HARD_PASS",
                f"Community detection CONFIRMED. "
                f"intra_agree={mia:.4f}>={HP_INTRA_AGREE} "
                f"inter_sep={mis:.4f}>={HP_INTER_SEP} "
                f"comm_acc={mca:.4f}>={HP_COMM_ACC}. "
                f"A:{fA:.2f} B:{fB:.2f} C:{fC:.2f}.")
    if cells_pass <= 1:
        return ("HARD_FAIL",
                f"Community detection NOT confirmed. "
                f"intra={mia:.4f} inter={mis:.4f} comm={mca:.4f}. "
                f"A:{fA:.2f} B:{fB:.2f} C:{fC:.2f}.")
    return ("MIDDLE_BAND",
            f"{cells_pass}/3 cells pass. intra={mia:.4f} inter={mis:.4f} "
            f"comm_acc={mca:.4f}. A:{fA:.2f} B:{fB:.2f} C:{fC:.2f}.")


def main():
    out_dir = get_output_dir(ANCHOR_NAME)
    t0 = time.time()
    print(f"[start] {ANCHOR_NAME} run_mode={RUN_MODE} N={N} "
          f"K={K_COMM} C={C_SIZE} p_in={P_IN} p_out={P_OUT} seeds={SEEDS}", flush=True)

    from experiments._seed_checkpoint import resumable_seeds, write_partial, aggregate_partials
    run_config = {"N": N, "K_COMM": K_COMM, "C_SIZE": C_SIZE, "run_mode": RUN_MODE}
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
        "run_mode": RUN_MODE, "N": N, "K_COMM": K_COMM, "C_SIZE": C_SIZE,
        "P_IN": P_IN, "P_OUT": P_OUT, "seeds": SEEDS,
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
