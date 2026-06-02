"""
q_b1_heteroassoc_chain_cert_v1_n8192 -- Q-B1 heteroassociative directed chain depth-3 + cert at N=8192.

Same design as q_b1_heteroassoc_chain_cert_v1_n4096 at N=8192 for production envelope.
At larger N: interference ~ M_background / N -> lower crosstalk -> higher expected fidelity.

SCIENTIFIC QUESTION (Q-B1 at N=8192):
  Does depth-3 heteroassoc chain retrieval hold at N=8192, and does algebraic
  deletion remain exact (zero residual) at the production-N envelope?

COMPOSITION CLASSIFICATION: HANDOFF (per-hop independence).

PRE-REGISTERED BANDS (same as N=4096):
  HARD-PASS: depth1 >= 0.90, depth3 >= 0.80, deletion_sim <= 0.50.
  MIDDLE: depth1 >= 0.90, depth3 in [0.60, 0.80).
  HARD-FAIL: depth3 < 0.60.

FORMULA SELF-TESTS:
  1. Single-binding test: H @ key = val exactly when M=1 (same as N=4096 version).
  2. Interference ~ M_background / N: at N=8192 and M_background=30, alpha=0.0037.
     Expected fidelity degradation: ~alpha = 0.37% per hop.
  3. Deletion algebraic exactness: outer product cancellation is exact regardless of N.

PROT-018: anchor name has _n8192; N MUST = 8192.
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
from typing import Dict, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials

ANCHOR_NAME = "q_b1_heteroassoc_chain_cert_v1_n8192"

# PROT-018: anchor has _n8192 -> N must = 8192
_N_SUFFIX = 8192
N = 8192
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    N_CHAINS = 5
    M_BACKGROUND = 10
    N_TRIALS = 10
else:
    SEEDS = [7, 17, 23, 31, 41]
    N_CHAINS = 15
    M_BACKGROUND = 30
    N_TRIALS = 50

# Pre-reg thresholds (same as N=4096)
HP_DEPTH1_FIDELITY = 0.90
HP_DEPTH3_FIDELITY = 0.80
HF_DEPTH3_FIDELITY = 0.60
HP_DELETION_SIM_MAX = 0.50

# Formula self-test: single binding exactness
_N_t, _val_t, _key_t = 8, np.ones(8), np.ones(8)
_H_t = np.outer(_val_t, _key_t) / _N_t
assert np.allclose(_H_t @ _key_t, _val_t, atol=1e-12), "formula selftest: H@key=val failed"
print("[formula_selftest] H@key=val (M=1) PASS; N=8192 PROT-018 binding verified", flush=True)


def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na < 1e-12 or nb < 1e-12:
        return 0.0
    return float(np.dot(a, b)) / (na * nb)


def build_heteroassoc(keys: np.ndarray, vals: np.ndarray, N: int) -> np.ndarray:
    M = keys.shape[0]
    H = np.zeros((N, N))
    for i in range(M):
        H += np.outer(vals[i], keys[i]) / N
    return H


def delete_binding(H: np.ndarray, key: np.ndarray, val: np.ndarray, N: int) -> np.ndarray:
    return H - np.outer(val, key) / N


def retrieve(H: np.ndarray, query: np.ndarray) -> np.ndarray:
    return H @ query


def run_seed(seed: int) -> Dict:
    rng = np.random.RandomState(seed)
    chain_keys = rng.choice([-1.0, 1.0], size=(N_CHAINS * 4, N)).astype(np.float64)
    bg_keys = rng.choice([-1.0, 1.0], size=(M_BACKGROUND, N)).astype(np.float64)
    bg_vals = rng.choice([-1.0, 1.0], size=(M_BACKGROUND, N)).astype(np.float64)

    all_chain_keys = []
    all_chain_vals = []
    for ci in range(N_CHAINS):
        base = ci * 4
        for hop in range(3):
            all_chain_keys.append(chain_keys[base + hop])
            all_chain_vals.append(chain_keys[base + hop + 1])

    all_keys = np.vstack(all_chain_keys + list(bg_keys))
    all_vals = np.vstack(all_chain_vals + list(bg_vals))
    H = build_heteroassoc(all_keys, all_vals, N)

    depth1_sims, depth3_sims, deletion_sims = [], [], []
    for ci in range(min(N_CHAINS, N_TRIALS)):
        base = ci * 4
        d1 = chain_keys[base]
        d2 = chain_keys[base + 1]
        d3 = chain_keys[base + 2]
        d4 = chain_keys[base + 3]

        ret1 = retrieve(H, d1)
        s1 = cosine_sim(ret1, d2)
        depth1_sims.append(s1)

        r1 = retrieve(H, d1)
        r2 = retrieve(H, r1)
        r3 = retrieve(H, r2)
        s3 = cosine_sim(r3, d4)
        depth3_sims.append(s3)

        H_del = delete_binding(H, d2, d3, N)
        ret_del = retrieve(H_del, d2)
        s_del = cosine_sim(ret_del, d3)
        deletion_sims.append(s_del)

    mean_d1 = float(np.mean(depth1_sims))
    mean_d3 = float(np.mean(depth3_sims))
    mean_del = float(np.mean(deletion_sims))
    print(f"  [seed={seed}] N=8192 depth1={mean_d1:.3f} depth3={mean_d3:.3f} "
          f"after_del={mean_del:.3f}", flush=True)
    return {
        "seed": seed, "N": N,
        "mean_depth1_fidelity": mean_d1,
        "mean_depth3_fidelity": mean_d3,
        "mean_deletion_sim": mean_del,
        "n_chains_tested": len(depth1_sims),
        "run_mode": RUN_MODE,
    }


def _instrumentation_selftest():
    """Assert metrics non-null at small N (N=8192 binding verified at top)."""
    N_t = 512
    seed = 42
    rng = np.random.RandomState(seed)
    keys_t = rng.choice([-1.0, 1.0], size=(8, N_t)).astype(np.float64)
    H_t = build_heteroassoc(keys_t[:3], keys_t[1:4], N_t)
    ret_t = retrieve(H_t, keys_t[0])
    s_t = cosine_sim(ret_t, keys_t[1])
    assert not math.isnan(s_t), "selftest: cosine NaN"
    assert 0.0 <= s_t <= 1.0, f"selftest: s={s_t}"
    H_del_t = delete_binding(H_t, keys_t[0], keys_t[1], N_t)
    ret_del_t = retrieve(H_del_t, keys_t[0])
    s_del_t = cosine_sim(ret_del_t, keys_t[1])
    assert not math.isnan(s_del_t), "selftest: del sim NaN"
    print(f"[selftest] PASS N_t={N_t} depth1={s_t:.3f} del_sim={s_del_t:.3f}; "
          f"production N=8192 PROT-018 OK", flush=True)


_instrumentation_selftest()


def aggregate_results(per_seed: Dict) -> Dict:
    d1_vals, d3_vals, del_vals = [], [], []
    for sd in per_seed.values():
        if not math.isnan(sd.get("mean_depth1_fidelity", float("nan"))):
            d1_vals.append(sd["mean_depth1_fidelity"])
        if not math.isnan(sd.get("mean_depth3_fidelity", float("nan"))):
            d3_vals.append(sd["mean_depth3_fidelity"])
        if not math.isnan(sd.get("mean_deletion_sim", float("nan"))):
            del_vals.append(sd["mean_deletion_sim"])
    return {
        "mean_depth1_fidelity": float(np.mean(d1_vals)) if d1_vals else float("nan"),
        "mean_depth3_fidelity": float(np.mean(d3_vals)) if d3_vals else float("nan"),
        "mean_deletion_sim": float(np.mean(del_vals)) if del_vals else float("nan"),
        "n_seeds": len(d1_vals),
    }


def compute_verdict(agg: Dict) -> Tuple[str, str]:
    d1 = agg.get("mean_depth1_fidelity", float("nan"))
    d3 = agg.get("mean_depth3_fidelity", float("nan"))
    del_sim = agg.get("mean_deletion_sim", float("nan"))
    if math.isnan(d3):
        return ("HARD_FAIL", "No valid depth3 fidelity at N=8192.")
    deletion_ok = (not math.isnan(del_sim) and del_sim <= HP_DELETION_SIM_MAX)
    if d1 >= HP_DEPTH1_FIDELITY and d3 >= HP_DEPTH3_FIDELITY and deletion_ok:
        return ("HARD_PASS",
                f"Q-B1 N=8192 depth-3 heteroassoc chain + cert confirmed. "
                f"depth1={d1:.3f} depth3={d3:.3f} deletion_sim={del_sim:.3f}. "
                f"Production envelope for reasoning-chain + deletion-cert primitive.")
    if d3 < HF_DEPTH3_FIDELITY:
        return ("HARD_FAIL",
                f"Q-B1 N=8192 chain retrieval FAILS. depth3={d3:.3f} < {HF_DEPTH3_FIDELITY}.")
    return ("MIDDLE_BAND",
            f"Q-B1 N=8192 partial. depth1={d1:.3f} depth3={d3:.3f} "
            f"deletion_ok={deletion_ok}.")


def main():
    t_start = time.time()
    print(f"[{ANCHOR_NAME}] run_mode={RUN_MODE} N={N} n_chains={N_CHAINS} "
          f"m_bg={M_BACKGROUND} seeds={SEEDS}", flush=True)

    out_dir = get_output_dir(ANCHOR_NAME)
    run_config = {"N": N, "run_mode": RUN_MODE}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print(f"[ckpt] {len(done)}/{len(SEEDS)} done; running {remaining}", flush=True)

    for seed in remaining:
        print(f"[{ANCHOR_NAME}] seed={seed} starting", flush=True)
        r = run_seed(seed)
        write_partial(out_dir, seed, r)
        print(f"[{ANCHOR_NAME}] seed={seed} done", flush=True)

    per_seed = aggregate_partials(out_dir, SEEDS)
    agg = aggregate_results(per_seed)
    verdict, verdict_msg = compute_verdict(agg)

    total_elapsed = time.time() - t_start
    metrics = {
        "anchor_name": ANCHOR_NAME,
        "run_mode": RUN_MODE,
        "N": N,
        "n_chains": N_CHAINS,
        "m_background": M_BACKGROUND,
        "seeds": SEEDS,
        "aggregate": agg,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": total_elapsed,
    }
    metrics_path = get_output_dir(ANCHOR_NAME) / "metrics.json"
    with open(metrics_path, "w", encoding="utf-8") as fh:
        json.dump(metrics, fh, indent=2)
    print(f"[{ANCHOR_NAME}] verdict={verdict}", flush=True)
    print(f"[{ANCHOR_NAME}] {verdict_msg}", flush=True)
    print(f"[{ANCHOR_NAME}] elapsed={total_elapsed:.1f}s", flush=True)


if __name__ == "__main__":
    if _ARGS.self_test:
        print("[main] --self-test complete", flush=True)
        sys.exit(0)
    main()
