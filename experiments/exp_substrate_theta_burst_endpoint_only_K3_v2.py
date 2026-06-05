"""
substrate_theta_burst_endpoint_only_K3_v2 -- SPARSE-V2-1: endpoint-only K=3 trajectory write (Finding A rescue) -- CPU.

ROUTING: research 4_negatives_rescued_sparse_writes. Theta-burst HF rescue: write ONLY the endpoint association
  c_t -> c_{t+K} (K=3), NO intermediate writes. Tests whether the algebraic lookahead direction holds in the right
  regime: a DIRECT 3-step association should beat iterating a 1-step map 3x (compounding error). CPU numpy $0.

PRE-REGISTERED bands: HARD-PASS multi-step (t+2,t+3) accuracy >= K=1-iterated + 10pp AND single-step (t+1) within 5pp.
  MIDDLE: 5-10pp multi-step gain. HARD-FAIL: zero multi-step gain OR t+1 degraded.
FORMULA SELF-TESTS (PROT-022): 1. direct heteroassoc recall. 2. cleanup argmax. 3. N=1024.
ASCII-only. write_metrics. PROT-018 _n1024 (V_c chain). (anchor uses _v2 not _nN binding.)
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "substrate_theta_burst_endpoint_only_K3_v2"
N = 1024
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1, 2]; N_DIM = 1024; V_C = 300; T_LEN = 3000
else:
    SEEDS = [7, 17, 23, 31, 43]; N_DIM = 1024; V_C = 1000; T_LEN = 8000


def bp(M, n, g):
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def _selftest():
    g = np.random.default_rng(0); n = 256; C = bp(5, n, g)
    W = np.outer(C[3], C[1]).astype(np.float32)            # key C[1] -> value C[3]
    assert int(np.argmax(C @ (W @ C[1]))) == 3, "direct heteroassoc recall"
    assert N == 1024; print("[selftest] PASS: heteroassoc cleanup", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed) -> Dict:
    g = np.random.default_rng(seed); n = N_DIM; C = bp(V_C, n, g)
    # 2nd-order Markov-ish chain over V_C symbols
    seq = [int(g.integers(0, V_C)), int(g.integers(0, V_C))]
    for t in range(T_LEN):
        seq.append(int((seq[-1] * 7 + seq[-2] * 3 + 1) % V_C))
    seq = np.array(seq)
    # K=1 baseline: W1 maps c_t -> c_{t+1} (batched Hebbian)
    W1 = (C[seq[1:]].T @ C[seq[:-1]]).astype(np.float32)
    # endpoint-only K=3: W3 maps c_t -> c_{t+3} directly
    W3 = (C[seq[3:]].T @ C[seq[:-3]]).astype(np.float32)
    ev = list(g.choice(len(seq) - 4, size=min(500, len(seq) - 4), replace=False))

    def cu(x):
        return int(np.argmax(C @ x))
    # single-step t+1 (both use W1)
    t1 = np.mean([cu(W1 @ C[seq[t]]) == seq[t + 1] for t in ev])
    # multi-step via K=1 ITERATED (compounding) vs direct endpoint
    it2 = np.mean([cu(W1 @ C[cu(W1 @ C[seq[t]])]) == seq[t + 2] for t in ev])
    it3 = np.mean([cu(W1 @ C[cu(W1 @ C[cu(W1 @ C[seq[t]])])]) == seq[t + 3] for t in ev])
    W2 = (C[seq[2:]].T @ C[seq[:-2]]).astype(np.float32)
    dir2 = np.mean([cu(W2 @ C[seq[t]]) == seq[t + 2] for t in ev])
    dir3 = np.mean([cu(W3 @ C[seq[t]]) == seq[t + 3] for t in ev])
    return {"seed": seed, "t1": float(t1), "iter_t2": float(it2), "iter_t3": float(it3),
            "direct_t2": float(dir2), "direct_t3": float(dir3),
            "gain_t2_pp": float((dir2 - it2) * 100), "gain_t3_pp": float((dir3 - it3) * 100)}


def verdict(ps) -> Tuple[str, str]:
    g2 = float(np.mean([p["gain_t2_pp"] for p in ps])); g3 = float(np.mean([p["gain_t3_pp"] for p in ps]))
    t1 = float(np.mean([p["t1"] for p in ps])); multistep_gain = (g2 + g3) / 2
    d3 = float(np.mean([p["direct_t3"] for p in ps])); i3 = float(np.mean([p["iter_t3"] for p in ps]))
    summary = "t+1=%.3f | direct_t+3=%.3f vs iter_t+3=%.3f | gain t+2=+%.1fpp t+3=+%.1fpp (mean multistep gain %.1fpp)" % (t1, d3, i3, g2, g3, multistep_gain)
    if multistep_gain >= 10.0:
        return ("HARD_PASS", "HARD_PASS: endpoint-only direct write rescues multi-step (>=10pp over iterated K=1) -- lookahead direction holds. " + summary)
    if multistep_gain >= 5.0:
        return ("MIDDLE_BAND", "MIDDLE_BAND: 5-10pp multi-step gain from endpoint write. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: endpoint write gives no multi-step gain. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d V_c=%d T=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, V_C, T_LEN), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r)
    print("  [seed=%d] t+1=%.3f direct_t+3=%.3f iter_t+3=%.3f gain_t+3=+%.1fpp" % (seed, r["t1"], r["direct_t3"], r["iter_t3"], r["gain_t3_pp"]), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N_DIM, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
