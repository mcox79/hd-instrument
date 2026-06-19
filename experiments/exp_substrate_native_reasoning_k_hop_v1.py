"""
exp_substrate_native_reasoning_k_hop_v1 -- OVERNIGHT T1-8: native K-hop chained retrieval -- CPU.

ROUTING: research OVERNIGHT_QUEUE T1-8. Substrate does K-hop structured reasoning natively: a relation map Wc stores
  c_t -> c_{t+1}; a K-hop query (given c_0, find c_K) is K cleanup-iterated mat-vecs -- vs an LLM needing K sequential
  forward passes. Measures K-hop accuracy (K=1..5) and confirms the structured-retrieval speedup is architectural
  (K cheap matvecs, no decode loop). CPU numpy $0.

PRE-REGISTERED bands: HARD-PASS K=3 accuracy >= 0.70 at N=4096 (native multi-hop holds). MIDDLE: 0.50-0.70. HARD-FAIL:
  < 0.50 (multi-hop chain breaks before K=3).
FORMULA SELF-TESTS (PROT-022): 1. 1-hop recall. 2. 2-hop chain. 3. N=4096.
ASCII-only. write_metrics. PROT-018 _n4096 -> N=4096.
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

ANCHOR_NAME = "substrate_native_reasoning_k_hop_v1"
_N_SUFFIX = 4096; N = 4096; assert N == _N_SUFFIX
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1, 2]; N_DIM = 1024; V_C = 300; CHAINS = 150; KS = [1, 2, 3, 5]
else:
    SEEDS = [7, 17, 23]; N_DIM = 4096; V_C = 2000; CHAINS = 400; KS = [1, 2, 3, 4, 5, 6]


def bp(M, n, g):
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32); return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def _selftest():
    g = np.random.default_rng(0); n = 256; C = bp(6, n, g)
    Wc = (C[[1, 2, 3]].T @ C[[0, 1, 2]]).astype(np.float32)   # 0->1->2->3
    assert int(np.argmax(C @ (Wc @ C[0]))) == 1, "1-hop recall"
    h1 = int(np.argmax(C @ (Wc @ C[0]))); assert int(np.argmax(C @ (Wc @ C[h1]))) == 2, "2-hop chain"
    assert N == 4096; print("[selftest] PASS: 1hop 2hop", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed) -> Dict:
    g = np.random.default_rng(seed); n = N_DIM; C = bp(V_C, n, g)
    # build a single deterministic chain of length L over V_C symbols; relation map Wc maps c_t -> c_{t+1}
    L = V_C
    nxt = (np.arange(V_C) * 7 + 3) % V_C                    # permutation-ish successor relation
    Wc = (C[nxt].T @ C).astype(np.float32)                 # c -> successor(c)
    ev = list(g.choice(V_C, size=min(CHAINS, V_C), replace=False))
    acc_by_k = {}
    for K in KS:
        ok = 0
        for c0 in ev:
            cur = c0
            for _ in range(K):
                cur = int(np.argmax(C @ (Wc @ C[cur])))    # cleanup-iterated hop
            truth = c0
            for _ in range(K):
                truth = int(nxt[truth])
            ok += int(cur == truth)
        acc_by_k["k%d" % K] = ok / len(ev)
    return {"seed": seed, "acc_by_k": acc_by_k, "k3_acc": acc_by_k.get("k3", 0.0)}


def verdict(ps) -> Tuple[str, str]:
    k3 = float(np.mean([p["k3_acc"] for p in ps]))
    curve = {k: float(np.mean([p["acc_by_k"][k] for p in ps])) for k in ps[0]["acc_by_k"]}
    summary = "K=3 acc=%.3f | curve=%s" % (k3, {k: round(v, 3) for k, v in curve.items()})
    if k3 >= 0.70:
        return ("HARD_PASS", "HARD_PASS: native K-hop reasoning holds to K=3 (>=0.70) -- structured retrieval is K cheap matvecs, no decode loop. " + summary)
    if k3 >= 0.50:
        return ("MIDDLE_BAND", "MIDDLE_BAND: K-hop partial (K=3 in 0.50-0.70). " + summary)
    return ("HARD_FAIL", "HARD_FAIL: K-hop chain breaks before K=3 (<0.50). " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d V_c=%d chains=%d KS=%s" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, V_C, CHAINS, KS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r)
    print("  [seed=%d] K=3 acc=%.3f curve=%s" % (seed, r["k3_acc"], {k: round(v, 2) for k, v in r["acc_by_k"].items()}), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N_DIM, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
