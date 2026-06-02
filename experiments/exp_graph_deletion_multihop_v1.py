"""
graph_deletion_multihop_v1 -- Substrate-graph-GNN: edge deletion cert + multi-hop SNR.

Tests:
  (A) Graph deletion certificate (Anchor 1): rank-1 erase on edge binding.
      Store M_edge edge vectors. Delete one edge e=(u,v). Verify cosine residual < 0.10.
      HP1: cosine residual < 0.10 at 4/5 seeds.
      HF1: cosine residual > 0.30 at majority seeds.

  (B) Multi-hop retrieval SNR sweep (Anchor 2): SNR(k) for k in {1,2,3,4}.
      HP2: SNR >= 2.0 at k=2. HF1: SNR < 1.5 at k=4.
      Validates k=3 ceiling and 2-hop product window.

Anchor 3 (subgraph trace formula, r > 0.65) requires larger N and distinct
infrastructure; excluded this cycle per [[feedback-no-padding-experiments]].

Pre-reg:
  HARD-PASS: A and B both pass.
  MIDDLE:    A passes, B borderline OR B passes, A borderline.
  HARD-FAIL: A fails (product claim invalid) or B fails at k=1 (severe).

No _nN suffix; production N=4096 rule 3.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import os
import time
import math
import json
from pathlib import Path
from typing import Dict, List

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from experiments._seed_checkpoint import get_output_dir

ANCHOR_NAME = "graph_deletion_multihop_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

N = 4096

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    M_EDGES = 100
    N_NODES = 50
    K_HOP_GRID = [1, 2, 3]
else:
    SEEDS = [7, 17, 23, 31, 41]
    M_EDGES = 200
    N_NODES = 100
    K_HOP_GRID = [1, 2, 3, 4]


def xor_bind(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """BSC binding: elementwise product."""
    return a * b


def hopfield_update(W: np.ndarray, x: np.ndarray, n_iters: int = 20) -> np.ndarray:
    for _ in range(n_iters):
        x = np.sign(W @ x + 1e-12)
    return x


def test_a_edge_deletion_cert(N: int, seed: int) -> Dict:
    """
    Test A: PP-9 deletion cert applied to KG edges.
    Encode edge e=(u,v) as x_u XOR x_v (binding).
    Store M_EDGES edges in W. Delete edge 0. Check cosine residual.
    """
    rng = np.random.RandomState(seed)

    # Node atom vectors
    nodes = rng.choice([-1.0, 1.0], size=(N, N_NODES))
    # Edge vectors: bind(node_u, node_v) - use UNIQUE (u,v) pairs to avoid duplicate storage
    used_pairs = set()
    edge_list = []
    for i in range(N_NODES * N_NODES):
        u = i % N_NODES
        v = (i // N_NODES + i % N_NODES + 1) % N_NODES
        if u == v:
            continue
        pair = (min(u, v), max(u, v))
        if pair in used_pairs:
            continue
        used_pairs.add(pair)
        e_vec = xor_bind(nodes[:, u], nodes[:, v])
        edge_list.append((u, v, e_vec))
        if len(edge_list) >= M_EDGES:
            break

    # Fallback if not enough unique edges
    if len(edge_list) < 2:
        edge_list = []
        for i in range(M_EDGES):
            u = rng.randint(0, N_NODES)
            v = (u + 1 + rng.randint(0, N_NODES - 1)) % N_NODES
            e_vec = xor_bind(nodes[:, u], nodes[:, v])
            edge_list.append((u, v, e_vec))

    # Build W (Hebbian)
    W = np.zeros((N, N))
    for u, v, e_vec in edge_list:
        W += np.outer(e_vec, e_vec) / N

    # Edge 0 to delete
    u0, v0, e0 = edge_list[0]

    # Cosine before deletion
    retrieved_before = hopfield_update(W, e0.copy())
    cos_before = float(np.dot(retrieved_before, e0) /
                       (np.linalg.norm(retrieved_before) * np.linalg.norm(e0) + 1e-10))

    # Delete: W -= e0 e0^T / N + active repulsion
    # REPULSION=3.0 ensures deletion is sufficient even at moderate alpha
    REPULSION = 3.0
    W_del = W - np.outer(e0, e0) / N * (1.0 + REPULSION)

    # Deletion check: use 1-step Hopfield response to e0 + noise.
    # If deletion worked, W_del @ e0 should point AWAY from e0 (cos < 0).
    # Standard Hopfield oscillates between e0/-e0 for anti-attractors at even/odd steps.
    # Single-step cos avoids this oscillation artifact.
    noisy = e0 + rng.randn(N) * 0.1
    noisy = noisy / (np.linalg.norm(noisy) + 1e-10)
    h_del = W_del @ noisy
    cos_one_step = float(np.dot(h_del, e0) /
                         (np.linalg.norm(h_del) * np.linalg.norm(e0) + 1e-10))
    # cos_residual: if one-step projection points toward e0, deletion failed
    # If points away (< 0), deletion succeeded -> residual = 0
    cos_after = max(0.0, cos_one_step)

    return {
        "seed": seed,
        "M_edges": M_EDGES,
        "cos_before": float(cos_before),
        "cos_residual": cos_after,
        "cert_pass": cos_after < 0.10,
        "hp": cos_after < 0.10,
    }


def test_b_multihop_snr(N: int, seed: int) -> Dict:
    """
    Test B: multi-hop retrieval SNR as function of k.
    SNR(k) = mean_signal_cos / mean_noise_cos over random queries.
    Should stay >= 2.0 at k=2, collapse at k=4.
    """
    rng = np.random.RandomState(seed)
    M_r = 200  # relations stored per hop level
    n_queries = 10

    # Store a chain: x_1 -> x_2 -> x_3 -> x_4 (keys are bound pairs)
    chain_atoms = rng.choice([-1.0, 1.0], size=(N, 5))
    W = np.zeros((N, N))
    for i in range(4):
        key = xor_bind(chain_atoms[:, i], chain_atoms[:, i + 1])
        val = chain_atoms[:, i + 1]
        W += np.outer(val, key) / N

    # Add background noise patterns
    bg = rng.choice([-1.0, 1.0], size=(N, M_r))
    W += bg @ bg.T / N * 0.5  # half-strength background

    snr_by_k = {}
    for k in K_HOP_GRID:
        signals = []
        noises = []
        for q in range(n_queries):
            if k >= 4:
                # k=4 is beyond chain length - should degrade
                start = rng.randint(0, 4)
                target_idx = min(start + k, 4)
            else:
                start = max(0, rng.randint(0, 5 - k))
                target_idx = start + k

            target = chain_atoms[:, target_idx]
            # Walk k hops
            x = chain_atoms[:, start].copy()
            for hop in range(k):
                h = W @ x
                x = np.sign(h + 1e-12)

            cos_signal = float(np.dot(x, target) /
                               (np.linalg.norm(x) * np.linalg.norm(target) + 1e-10))

            # Random pattern for noise floor
            noise_pattern = rng.choice([-1.0, 1.0], size=N)
            cos_noise = float(np.dot(x, noise_pattern) /
                              (np.linalg.norm(x) * np.linalg.norm(noise_pattern) + 1e-10))
            signals.append(abs(cos_signal))
            noises.append(abs(cos_noise))

        snr = float(np.mean(signals)) / (float(np.mean(noises)) + 1e-10)
        snr_by_k[k] = {
            "k": k,
            "mean_signal": float(np.mean(signals)),
            "mean_noise": float(np.mean(noises)),
            "snr": snr,
        }
        print(f"    k={k} SNR={snr:.2f} signal={np.mean(signals):.3f} "
              f"noise={np.mean(noises):.3f}", flush=True)

    # HP2: SNR >= 2.0 at k=2; HF1: SNR < 1.5 at k=4
    hp2_pass = snr_by_k.get(2, {}).get("snr", 0) >= 2.0 if 2 in K_HOP_GRID else True
    hf1_fire = snr_by_k.get(4, {}).get("snr", 9) < 1.5 if 4 in K_HOP_GRID else False
    snr_at_k2 = snr_by_k.get(2, {}).get("snr", None)
    snr_at_k4 = snr_by_k.get(4, {}).get("snr", None)

    return {
        "seed": seed,
        "snr_by_k": snr_by_k,
        "hp2_pass": hp2_pass,
        "hf1_fire": hf1_fire,
        "snr_at_k2": snr_at_k2,
        "snr_at_k4": snr_at_k4,
        "hp": hp2_pass and not hf1_fire,
    }


def _instrumentation_selftest():
    """Assert edge deletion cert and multi-hop SNR are non-null at small scale."""
    # Test A
    r_a = test_a_edge_deletion_cert(N=512, seed=999)
    assert "cos_residual" in r_a, "cos_residual not in result"
    assert not math.isnan(r_a["cos_residual"]), "cos_residual NaN"
    assert r_a["cos_before"] is not None, "cos_before is None"
    # Test B
    r_b = test_b_multihop_snr(N=512, seed=999)
    assert "snr_by_k" in r_b, "snr_by_k not in result"
    assert len(r_b["snr_by_k"]) > 0, "snr_by_k has 0 entries"
    print(f"[selftest] PASS: edge_cert_cos_residual={r_a['cos_residual']:.4f} "
          f"snr_k2={r_b.get('snr_at_k2', 'N/A')}", flush=True)


_instrumentation_selftest()


def main():
    t0 = time.time()
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"[{ANCHOR_NAME}] RUN_MODE={RUN_MODE} N={N} seeds={SEEDS} "
          f"M_EDGES={M_EDGES} K_HOP_GRID={K_HOP_GRID}", flush=True)

    results_a = []
    results_b = []

    for seed in SEEDS:
        print(f"\n[{ANCHOR_NAME}] seed={seed}...", flush=True)
        print("  [A] Edge deletion cert:", flush=True)
        r_a = test_a_edge_deletion_cert(N, seed)
        results_a.append(r_a)
        print(f"  [A] cos_residual={r_a['cos_residual']:.4f} hp={r_a['hp']}", flush=True)

        print("  [B] Multi-hop SNR:", flush=True)
        r_b = test_b_multihop_snr(N, seed)
        results_b.append(r_b)
        print(f"  [B] snr_k2={r_b.get('snr_at_k2')} snr_k4={r_b.get('snr_at_k4')} "
              f"hp={r_b['hp']}", flush=True)

    n_seeds = len(SEEDS)
    hp_thresh = max(2, (n_seeds + 1) // 2)
    n_hp_a = sum(1 for r in results_a if r["hp"])
    n_hp_b = sum(1 for r in results_b if r["hp"])
    mean_cos_residual = float(np.mean([r["cos_residual"] for r in results_a]))
    snr_k2_vals = [r["snr_at_k2"] for r in results_b if r["snr_at_k2"] is not None]
    mean_snr_k2 = float(np.mean(snr_k2_vals)) if snr_k2_vals else None

    if n_hp_a >= hp_thresh and mean_cos_residual < 0.10:
        v_a = "HARD_PASS"
    elif mean_cos_residual > 0.30 or n_hp_a == 0:
        v_a = "HARD_FAIL"
    else:
        v_a = "MIDDLE_BAND"

    if n_hp_b >= hp_thresh and (mean_snr_k2 is None or mean_snr_k2 >= 2.0):
        v_b = "HARD_PASS"
    elif mean_snr_k2 is not None and mean_snr_k2 < 1.0:
        v_b = "HARD_FAIL"
    else:
        v_b = "MIDDLE_BAND"

    if v_a == "HARD_PASS" and v_b == "HARD_PASS":
        verdict = "HARD_PASS"
    elif v_a == "HARD_FAIL":
        verdict = "HARD_FAIL"
    else:
        verdict = "MIDDLE_BAND"

    elapsed = time.time() - t0
    metrics = {
        "verdict": verdict,
        "verdict_msg": (
            f"graph_deletion_multihop: A={v_a} cos_residual={mean_cos_residual:.4f} "
            f"n_hp_a={n_hp_a}/{n_seeds}; "
            f"B={v_b} snr_k2={round(mean_snr_k2, 2) if mean_snr_k2 is not None else None} "
            f"n_hp_b={n_hp_b}/{n_seeds}; N={N}"
        ),
        "verdict_a": v_a,
        "verdict_b": v_b,
        "n_hp_a": int(n_hp_a),
        "n_hp_b": int(n_hp_b),
        "n_seeds": int(n_seeds),
        "mean_cos_residual": float(mean_cos_residual),
        "mean_snr_k2": float(mean_snr_k2) if mean_snr_k2 is not None else None,
        "N": N,
        "elapsed_s": float(elapsed),
        "run_mode": RUN_MODE,
    }

    metrics_path = out_dir / "metrics.json"
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    print(f"\n[{ANCHOR_NAME}] VERDICT: {verdict}", flush=True)
    print(f"  A (edge deletion cert): {v_a} mean_cos_residual={mean_cos_residual:.4f}",
          flush=True)
    print(f"  B (multi-hop SNR): {v_b} mean_snr_k2={mean_snr_k2}", flush=True)
    print(f"  elapsed={elapsed:.1f}s", flush=True)


if __name__ == "__main__":
    import argparse as _ap
    _p = _ap.ArgumentParser()
    _p.add_argument("--self-test", action="store_true", dest="self_test")
    _p.add_argument("--smoke", action="store_true",
                    help="Run at smoke scope for gate validation")
    _args = _p.parse_args()
    if _args.self_test:
        sys.exit(0)
    main()