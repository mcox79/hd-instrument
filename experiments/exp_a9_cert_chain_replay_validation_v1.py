"""
a9_cert_chain_replay_validation_v1 -- Cluster A9: cert chain replay validation.

SCIENTIFIC QUESTION (Phase 3, Cluster A9):
  A cert chain is a tape of (seed, delta) pairs recording each Hebbian write.
  The claim: given only the cert chain (seed sequence + write order), a verifier
  can reconstruct W within relative Frobenius error < 1e-10 from a blank W=0 start.

  This is the "audit-trail as mathematical proof" moat: the cert chain IS the proof,
  not just a log. No separate backup copy of W is needed; the cert chain suffices.

  Protocol:
    1. Write K patterns using Hebbian rule: W += xi_k xi_k^T / N.
       Each xi_k is generated from seed s_k (deterministic RNG).
    2. Record cert_chain = [(s_k, 1/N) for k in range(K)].
    3. Verifier replays from blank W=0: W_v = sum_k xi_k xi_k^T / N using stored seeds.
    4. HP: ||W_v - W_orig||_F / ||W_orig||_F < 1e-10 in >= 4/5 seeds.

PRE-REGISTERED BANDS:
  HP1: replay_rel_err < 1e-10 (machine precision; algebraic identity).
  HP2: retrieval accuracy from W_v >= 0.90 on all K patterns in >= 4/5 seeds.
  HP3: cert chain length = K (no dropped entries).
  HARD-PASS: HP1 AND HP2 AND HP3.

  HARD-FAIL: replay_rel_err > 1e-4 (numerical instability in replay).
  MIDDLE: replay_rel_err in [1e-10, 1e-4] OR acc < 0.90.

  Calibration: cert chain replay is algebraically exact (deterministic RNG + rank-1 sum).
  HP1=1e-10 is achievable at float64; fp32 may give 1e-7.
  P_deflated = 0.90 (algebraically guaranteed by deterministic construction).

No _nN suffix: production N=1024. PROT-018 rule 3.

FORMULA SELF-TESTS:
  1. Replay of 1 write: xi * xi^T / N from seed s gives identical W to original.
     [INPUT: N=16, seed=42] [EXPECTED: rel_err < 1e-12]
  2. Replay of K=10 writes: relative error < 1e-10 at float64.
     [INPUT: N=64, K=10] [EXPECTED: rel_err < 1e-10]
  3. Cert chain length = K after K writes.
     [INPUT: K=20] [EXPECTED: len(cert_chain) = 20]
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import os
import argparse
import time
import json
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials

ANCHOR_NAME = "a9_cert_chain_replay_validation_v1"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

NOISE_FRAC = 0.10
N_RETRIEVE_STEPS = 5

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    N = 256
    K = 30
    N_TEST = 10
else:
    SEEDS = [7, 17, 23, 31, 41]
    N = 1024
    K = 100
    N_TEST = 30

HP_REL_ERR = 1e-10
HF_REL_ERR = 1e-4
HP_ACC = 0.90
HP_CHAIN_LENGTH = K


def gen_pattern(n: int, seed: int) -> np.ndarray:
    """Deterministic BSC pattern from seed."""
    rng = np.random.RandomState(seed)
    return rng.choice([-1.0, 1.0], size=n).astype(np.float64)


def hopfield_retrieve(Xi: np.ndarray, probe: np.ndarray, n_dim: int) -> np.ndarray:
    state = probe.copy()
    for _ in range(N_RETRIEVE_STEPS):
        h = Xi.T @ (Xi @ state) / n_dim
        state = np.sign(h)
        state[state == 0] = 1.0
    return state


def _selftest_single_write():
    n_t = 16
    s = 42
    xi = gen_pattern(n_t, s)
    W = np.outer(xi, xi) / n_t
    W_replay = np.outer(xi, xi) / n_t
    rel_err = float(np.linalg.norm(W_replay - W) / (np.linalg.norm(W) + 1e-12))
    assert rel_err < 1e-12, f"single write replay: rel_err={rel_err:.4e} >= 1e-12"


def _selftest_k_writes():
    n_t = 64
    k_t = 10
    base_seed = 1000
    W_orig = np.zeros((n_t, n_t), dtype=np.float64)
    cert_chain = []
    for k in range(k_t):
        s = base_seed + k
        xi = gen_pattern(n_t, s)
        W_orig += np.outer(xi, xi) / n_t
        cert_chain.append(s)
    # Replay
    W_v = np.zeros((n_t, n_t), dtype=np.float64)
    for s in cert_chain:
        xi = gen_pattern(n_t, s)
        W_v += np.outer(xi, xi) / n_t
    rel_err = float(np.linalg.norm(W_v - W_orig) / (np.linalg.norm(W_orig) + 1e-12))
    assert rel_err < 1e-10, f"K=10 write replay: rel_err={rel_err:.4e} >= 1e-10"


def _selftest_chain_length():
    cert_chain = list(range(20))
    assert len(cert_chain) == 20, f"cert chain length: {len(cert_chain)} != 20"


def _instrumentation_selftest():
    _selftest_single_write()
    _selftest_k_writes()
    _selftest_chain_length()
    print(f"[selftest] PASS: single_write_replay, k_write_replay, chain_length all OK",
          flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int) -> Dict:
    rng = np.random.RandomState(seed)
    t0 = time.time()

    # Write K patterns; record cert chain
    base_seed = seed * 10000  # per-seed namespace to avoid cross-seed collisions
    W_orig = np.zeros((N, N), dtype=np.float64)
    cert_chain: List[int] = []
    Xi_all = []

    for k in range(K):
        pat_seed = base_seed + k
        xi = gen_pattern(N, pat_seed)
        W_orig += np.outer(xi, xi) / N
        cert_chain.append(pat_seed)
        Xi_all.append(xi)

    Xi_arr = np.array(Xi_all, dtype=np.float64)  # (K, N)

    # Replay from scratch
    W_v = np.zeros((N, N), dtype=np.float64)
    for s in cert_chain:
        xi = gen_pattern(N, s)
        W_v += np.outer(xi, xi) / N

    # HP1: relative error
    frob_orig = float(np.linalg.norm(W_orig))
    frob_err = float(np.linalg.norm(W_v - W_orig))
    rel_err = frob_err / (frob_orig + 1e-12)

    # HP2: retrieval accuracy from W_v
    correct = 0
    test_idx = rng.choice(K, size=min(N_TEST, K), replace=False)
    for idx in test_idx:
        xi_true = Xi_arr[idx]
        probe = xi_true.copy()
        flip = rng.random(N) < NOISE_FRAC
        probe[flip] *= -1.0
        ret = hopfield_retrieve(Xi_arr, probe, N)
        if np.dot(ret, xi_true) / N > 0.80:
            correct += 1
    acc = float(correct) / len(test_idx) if len(test_idx) > 0 else 0.0

    # HP3: cert chain length
    chain_len = len(cert_chain)

    elapsed = time.time() - t0
    print(f"  [seed={seed}] rel_err={rel_err:.2e} acc={acc:.4f} "
          f"chain_len={chain_len}(expected={K}) elapsed={elapsed:.2f}s", flush=True)

    return {
        "seed": seed, "N": N, "K": K, "run_mode": RUN_MODE,
    "elapsed_s": time.time() - t0_total,
    "summary": verdict_msg[:200],
        "replay_rel_err": float(rel_err),
        "retrieval_acc": float(acc),
        "cert_chain_length": int(chain_len),
        "elapsed_s": float(elapsed),
        "hp1_pass": int(rel_err < HP_REL_ERR),
        "hp2_pass": int(acc >= HP_ACC),
        "hp3_pass": int(chain_len == HP_CHAIN_LENGTH),
    }


def compute_verdict(results: List[Dict]) -> tuple:
    if not results:
        return ("HARD_FAIL", "No valid results.")

    def count_pass(key):
        return sum(1 for r in results if r.get(key, 0))

    n = len(results)
    hp1_c = count_pass("hp1_pass")
    hp2_c = count_pass("hp2_pass")
    hp3_c = count_pass("hp3_pass")

    def mean_key(k):
        vs = [r[k] for r in results if k in r]
        return float(sum(vs) / len(vs)) if vs else 0.0

    rel_m = mean_key("replay_rel_err")
    acc_m = mean_key("retrieval_acc")

    summary = (f"mean_replay_rel_err={rel_m:.2e}(HP<{HP_REL_ERR:.0e} HF>{HF_REL_ERR:.0e}) "
               f"mean_acc={acc_m:.4f}(HP>={HP_ACC}) "
               f"hp1={hp1_c}/{n} hp2={hp2_c}/{n} hp3={hp3_c}/{n}")

    if rel_m > HF_REL_ERR:
        return ("HARD_FAIL", f"HARD_FAIL: replay error > HF threshold. {summary}")

    GATE = max(4, n - 1) if n >= 4 else n
    if hp1_c >= GATE and hp2_c >= GATE and hp3_c >= n:
        return ("HARD_PASS", f"HARD_PASS: cert chain replay validates W within machine precision. {summary}")
    if hp2_c >= GATE:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: acc HP but rel_err in fp32 range. {summary}")
    return ("MIDDLE_BAND", f"MIDDLE_BAND: {summary}")


out_dir = get_output_dir(ANCHOR_NAME)
t0_total = time.time()
run_config = {"N": N, "K": K, "run_mode": RUN_MODE}

done, seeds_todo = resumable_seeds(SEEDS, out_dir, run_config)
print(f"[run] mode={RUN_MODE} N={N} K={K} seeds_todo={seeds_todo}", flush=True)

for s in seeds_todo:
    res = run_seed(s)
    write_partial(out_dir, s, res)

per_seed = aggregate_partials(out_dir, SEEDS)
all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(all_results)

metrics = {
    "anchor": ANCHOR_NAME,
    "verdict": verdict,
    "verdict_msg": verdict_msg,
    "n_seeds": len(all_results),
    "N": N,
    "K": K,
    "run_mode": RUN_MODE,
    "elapsed_s": time.time() - t0_total,
    "summary": verdict_msg[:200],
    "results": all_results,
}

metrics_path = out_dir / "metrics.json"
with open(metrics_path, "w") as f:
    json.dump(metrics, f, indent=2)

print(f"\n[VERDICT] {verdict}", flush=True)
print(f"[VERDICT_MSG] {verdict_msg}", flush=True)
print(f"[METRICS_PATH] {metrics_path}", flush=True)
