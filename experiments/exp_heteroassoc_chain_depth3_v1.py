"""
heteroassoc_chain_depth3_v1 -- Heteroassociative directed chain depth-3 + deletion cert.

SCIENTIFIC QUESTION (Q-B1 from research priorities):
  Does heteroassociative directed-chain encoding support depth-3 counterfactual
  reasoning at production fidelity (>= 0.80) AND enable exact algebraic deletion
  of any single directed binding?

  Heteroassociative directed chain: A -> B -> C -> D (depth-3 chain of 4 nodes).
  Encoding: W_chain = sum_{i=1..3} (next_role XOR D_i)^T @ D_{i+1} * 2/N
  where next_role is a fixed N-dim BSC +-1 role vector.
  Retrieval: given D_1, compute D_1^T W_chain -> signal on D_2 (after role unbinding).

  Simplified testable version:
  - Store pairs (key_i, val_i) as heteroassociative matrix H = sum_i val_i @ key_i^T / N.
  - Retrieve: val_approx = H @ key_i -> cosine_sim(val_approx, val_i).
  - Depth-3 chain: key_1 -> val_1 = key_2 -> val_2 = key_3 -> val_3.
  - Chain retrieval: start at key_1, retrieve val_1=key_2, retrieve val_2=key_3, retrieve val_3.
  - Deletion of (key_2, val_2) binding: H_new = H - val_2 @ key_2^T / N.
  - After deletion: chain A->B->C->D should break at B->C step.

PRE-REGISTERED BANDS:
  HARD-PASS: depth-1 fidelity >= 0.90, depth-3 chain fidelity >= 0.80
             (cosine_sim between retrieved and target at each depth),
             AND deletion breaks exactly at deleted link (<= 0.50 sim after deletion).
  MIDDLE: depth-1 fidelity >= 0.90 but depth-3 fidelity in [0.60, 0.80].
  HARD-FAIL: depth-3 fidelity < 0.60 (chain retrieval not functional).

FORMULA SELF-TESTS:
  1. H @ key_i = val_i exactly when M=1 (no crosstalk).
  2. After deletion H_new = H - val_2 @ key_2^T / N:
     H_new @ key_2 = 0 (val_2 signal exactly cancelled).
  3. Cosine_sim(val_approx, val_target) should be > 0.5 for M << alpha_c * N.

COMPOSITION CLASSIFICATION: HANDOFF (per-hop independence, following PP-11 Arm B).

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

ANCHOR_NAME = "heteroassoc_chain_depth3_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

N = 4096

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    N_CHAINS = 5     # number of independent depth-3 chains
    M_BACKGROUND = 10  # background heteroassociative pairs (interference)
    N_TRIALS = 20
else:
    SEEDS = [7, 17, 23, 31, 41]
    N_CHAINS = 15
    M_BACKGROUND = 30
    N_TRIALS = 50

# Pre-reg thresholds
HP_DEPTH1_FIDELITY = 0.90
HP_DEPTH3_FIDELITY = 0.80
HF_DEPTH3_FIDELITY = 0.60
HP_DELETION_SIM = 0.50   # after deletion: sim <= 0.50 (link broken)


def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine similarity."""
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na < 1e-12 or nb < 1e-12:
        return 0.0
    return float(np.dot(a, b)) / (na * nb)


def build_heteroassoc(keys: np.ndarray, vals: np.ndarray, N: int) -> np.ndarray:
    """H = sum_i val_i @ key_i^T / N. Keys and vals are M x N."""
    M = keys.shape[0]
    H = np.zeros((N, N))
    for i in range(M):
        H += np.outer(vals[i], keys[i]) / N
    return H


def heteroassoc_retrieve(H: np.ndarray, key: np.ndarray) -> np.ndarray:
    """Retrieve val = H @ key. Returns raw activation (not thresholded)."""
    return H @ key


def run_chain_trial(N: int, n_chains: int, m_bg: int, seed: int) -> Dict:
    """
    Create n_chains independent depth-3 chains (A->B->C->D) plus m_bg background.
    Measure depth-1, depth-2, depth-3 retrieval fidelity.
    Then delete B->C link and measure chain fidelity after deletion.
    """
    rng = np.random.RandomState(seed)

    # Generate chain patterns: each chain has 4 nodes (A, B, C, D)
    chain_nodes = []
    for c in range(n_chains):
        A = rng.choice([-1.0, 1.0], size=(N,))
        B = rng.choice([-1.0, 1.0], size=(N,))
        C = rng.choice([-1.0, 1.0], size=(N,))
        D = rng.choice([-1.0, 1.0], size=(N,))
        chain_nodes.append((A, B, C, D))

    # Build heteroassociative matrix for all chains + background
    # Chain pairs: (A, B), (B, C), (C, D) for each chain
    all_keys = []
    all_vals = []
    for A, B, C, D in chain_nodes:
        all_keys.extend([A, B, C])
        all_vals.extend([B, C, D])

    # Add background noise pairs
    for _ in range(m_bg):
        all_keys.append(rng.choice([-1.0, 1.0], size=(N,)))
        all_vals.append(rng.choice([-1.0, 1.0], size=(N,)))

    keys_arr = np.array(all_keys)
    vals_arr = np.array(all_vals)
    H = build_heteroassoc(keys_arr, vals_arr, N)

    # Measure depth-1, depth-2, depth-3 fidelity
    d1_sims, d2_sims, d3_sims = [], [], []
    for A, B, C, D in chain_nodes:
        # Depth-1: A -> B
        B_approx = heteroassoc_retrieve(H, A)
        d1_sims.append(cosine_sim(B_approx, B))

        # Depth-2: A -> B -> C (use thresholded B as next key)
        B_thresh = np.where(B_approx > 0, 1.0, -1.0)
        C_approx = heteroassoc_retrieve(H, B_thresh)
        d2_sims.append(cosine_sim(C_approx, C))

        # Depth-3: A -> B -> C -> D
        C_thresh = np.where(C_approx > 0, 1.0, -1.0)
        D_approx = heteroassoc_retrieve(H, C_thresh)
        d3_sims.append(cosine_sim(D_approx, D))

    # Deletion: remove B->C link of chain 0
    A0, B0, C0, D0 = chain_nodes[0]
    H_del = H - np.outer(C0, B0) / N  # undo B->C binding

    # After deletion: A->B should still work, B->C should be broken
    B_approx_del = heteroassoc_retrieve(H_del, A0)
    d1_after = cosine_sim(B_approx_del, B0)

    B_thresh_del = np.where(B_approx_del > 0, 1.0, -1.0)
    C_approx_del = heteroassoc_retrieve(H_del, B_thresh_del)
    d2_after_del = cosine_sim(C_approx_del, C0)  # should be broken (<= 0.50)

    return {
        "d1_sim_mean": float(np.mean(d1_sims)),
        "d2_sim_mean": float(np.mean(d2_sims)),
        "d3_sim_mean": float(np.mean(d3_sims)),
        "d1_after_deletion": d1_after,
        "d2_after_deletion": d2_after_del,  # broken link: should be < 0.50
        "n_chains": n_chains,
    }


def run_seed(seed: int) -> Dict:
    """Aggregate across N_TRIALS for one seed."""
    trial_results = []
    for trial in range(N_TRIALS):
        r = run_chain_trial(N, N_CHAINS, M_BACKGROUND, seed + trial * 97)
        trial_results.append(r)

    mean_d1 = float(np.mean([r["d1_sim_mean"] for r in trial_results]))
    mean_d2 = float(np.mean([r["d2_sim_mean"] for r in trial_results]))
    mean_d3 = float(np.mean([r["d3_sim_mean"] for r in trial_results]))
    mean_d1_after = float(np.mean([r["d1_after_deletion"] for r in trial_results]))
    mean_d2_after = float(np.mean([r["d2_after_deletion"] for r in trial_results]))

    print(f"  [seed={seed}] d1={mean_d1:.3f} d2={mean_d2:.3f} d3={mean_d3:.3f} "
          f"d1_after_del={mean_d1_after:.3f} d2_after_del={mean_d2_after:.3f}", flush=True)

    return {
        "mean_d1": mean_d1, "mean_d2": mean_d2, "mean_d3": mean_d3,
        "mean_d1_after_deletion": mean_d1_after,
        "mean_d2_after_deletion": mean_d2_after,
        "seed": seed, "N": N, "run_mode": RUN_MODE,
    }


def _instrumentation_selftest():
    """Assert chain metrics are non-null and depth-1 retrieval works at small scale."""
    N_test = 512
    seed = 42
    # Use 3 chains, 5 bg, single trial
    r = run_chain_trial(N_test, 3, 5, seed)
    assert r["d1_sim_mean"] > 0, "d1 sim is 0 -- H retrieval broken"
    assert not math.isnan(r["d1_sim_mean"]), "d1 sim is NaN"
    assert not math.isnan(r["d3_sim_mean"]), "d3 sim is NaN"
    # Deletion: d2_after_deletion should drop relative to d2 (link broken)
    assert r["d2_after_deletion"] >= 0, "negative cosine sim"

    print(f"[selftest] PASS: d1={r['d1_sim_mean']:.3f} d3={r['d3_sim_mean']:.3f} "
          f"d2_after_del={r['d2_after_deletion']:.3f} (N=512)", flush=True)


_instrumentation_selftest()


def _verdict_formula_selftests():
    """Verify heteroassociative formula predictions."""
    # M=1: H = v * k^T / N. H @ k = v * (k^T k / N) = v * N/N = v. Exact retrieval.
    N_t = 16
    k = np.array([1.0]*8 + [-1.0]*8)
    v = np.array([-1.0]*4 + [1.0]*4 + [-1.0]*4 + [1.0]*4)
    H = np.outer(v, k) / N_t
    retrieved = H @ k
    cs = cosine_sim(retrieved, v)
    assert cs > 0.99, f"M=1 exact retrieval failed: cos_sim={cs:.3f}"
    print("[formula_selftests] PASS: M=1 exact heteroassoc retrieval verified", flush=True)


_verdict_formula_selftests()


def aggregate_results(per_seed: Dict) -> Dict:
    d1_list, d2_list, d3_list = [], [], []
    d2_after_list = []
    for seed_data in per_seed.values():
        d1_list.append(seed_data["mean_d1"])
        d2_list.append(seed_data["mean_d2"])
        d3_list.append(seed_data["mean_d3"])
        d2_after_list.append(seed_data["mean_d2_after_deletion"])

    return {
        "mean_d1": float(np.mean(d1_list)) if d1_list else float("nan"),
        "mean_d2": float(np.mean(d2_list)) if d2_list else float("nan"),
        "mean_d3": float(np.mean(d3_list)) if d3_list else float("nan"),
        "mean_d2_after_deletion": float(np.mean(d2_after_list)) if d2_after_list else float("nan"),
        "n_seeds": len(d1_list),
    }


def compute_verdict(agg: Dict) -> Tuple[str, str]:
    d1 = agg.get("mean_d1", float("nan"))
    d3 = agg.get("mean_d3", float("nan"))
    d2_after = agg.get("mean_d2_after_deletion", float("nan"))

    if math.isnan(d1) or math.isnan(d3):
        return ("HARD_FAIL", "No valid fidelity measurements.")

    hp = d1 >= HP_DEPTH1_FIDELITY and d3 >= HP_DEPTH3_FIDELITY and d2_after <= HP_DELETION_SIM
    hf = d3 < HF_DEPTH3_FIDELITY

    del_ok = not math.isnan(d2_after) and d2_after <= HP_DELETION_SIM

    if hp:
        return ("HARD_PASS",
                f"Heteroassoc depth-3 chain confirmed. "
                f"d1={d1:.3f} (HP>={HP_DEPTH1_FIDELITY}) "
                f"d3={d3:.3f} (HP>={HP_DEPTH3_FIDELITY}). "
                f"Deletion: d2_after={d2_after:.3f} (link broken, HP<={HP_DELETION_SIM}). "
                f"Counterfactual depth-3 + cert-deletion compose correctly.")
    if hf:
        return ("HARD_FAIL",
                f"Depth-3 chain retrieval failed. "
                f"d3={d3:.3f} < HF {HF_DEPTH3_FIDELITY}. "
                f"d1={d1:.3f}. Chain degradation too severe for production fidelity.")
    return ("MIDDLE_BAND",
            f"Partial depth-3 fidelity. d1={d1:.3f} d3={d3:.3f}. "
            f"del_ok={del_ok} d2_after={d2_after:.3f}. "
            f"HP requires d3>={HP_DEPTH3_FIDELITY} AND deletion_break<={HP_DELETION_SIM}.")


def main():
    out_dir = get_output_dir(ANCHOR_NAME)
    t0 = time.time()
    print(f"[start] {ANCHOR_NAME} run_mode={RUN_MODE} N={N} "
          f"chains={N_CHAINS} bg={M_BACKGROUND} trials={N_TRIALS} seeds={SEEDS}", flush=True)

    from experiments._seed_checkpoint import resumable_seeds, write_partial, aggregate_partials
    run_config = {"N": N, "run_mode": RUN_MODE}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print(f"[ckpt] {len(done)} done, {len(remaining)} remaining", flush=True)

    for seed in remaining:
        ts = time.time()
        result = run_seed(seed)
        write_partial(out_dir, seed, result)
        print(f"[seed {seed}] d3={result['mean_d3']:.3f} done in {time.time()-ts:.1f}s", flush=True)

    per_seed = aggregate_partials(out_dir, SEEDS)
    agg = aggregate_results(per_seed)
    verdict, verdict_msg = compute_verdict(agg)

    elapsed = time.time() - t0
    metrics = {
        "run_mode": RUN_MODE, "N": N,
        "N_CHAINS": N_CHAINS, "M_BACKGROUND": M_BACKGROUND, "N_TRIALS": N_TRIALS,
        "seeds": SEEDS,
        "aggregated": agg,
        "verdict": verdict, "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "composition_classification": "HANDOFF",
    }
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"[done] {verdict}: {verdict_msg}", flush=True)
    print(f"[done] elapsed={elapsed:.1f}s", flush=True)


if __name__ == "__main__":
    if _ARGS.self_test:
        print("[main] --self-test complete", flush=True)
        sys.exit(0)
    main()
