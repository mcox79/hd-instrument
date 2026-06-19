"""
substrate_ccc_v2_capability_dims_n4096_v1 -- CCC-1-v2 four capability dims consolidated at Phase-2 N=4096 -- CPU.

ROUTING: research priority #9 (capability dims at Phase-2 scale). Consolidates the 4 CCC-1-v2 CAPABILITY benchmarks
  (single-hop, multi-hop 2-hop chaining, analogical VSA, counterfactual update) at the Phase-2 substrate operating
  point N=4096 (vs the earlier N=1024/2048 validations) -- confirms the core capabilities hold at scale. Random
  codeword encoding (substrate-native; residual-geometry transfer validated separately by audit-core-1B). CPU numpy $0.

PRE-REGISTERED bands: HARD-PASS all four dims >= 0.90 at N=4096. MIDDLE: >= 0.75 each. HARD-FAIL: any dim < 0.60.
FORMULA SELF-TESTS (PROT-022): 1. single-hop recall. 2. VSA analogy unbind. 3. N=4096.
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

ANCHOR_NAME = "substrate_ccc_v2_capability_dims_n4096_v1"
_N_SUFFIX = 4096; N = 4096; assert N == _N_SUFFIX
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1, 2]; N_DIM = 4096; M = 400; TRIALS = 200
else:
    SEEDS = [7, 17, 23]; N_DIM = 4096; M = 2000; TRIALS = 500


def bp(Mx, n, g):
    X = (g.integers(0, 2, size=(Mx, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def cu(C, x):
    return int(np.argmax(C @ x))


def _selftest():
    g = np.random.default_rng(0); n = 256; E = bp(3, n, g); V = bp(3, n, g); W = (V[[0, 1, 2]].T @ E).astype(np.float32)
    assert cu(V, W @ E[1]) == 1, "single-hop recall"
    R = (g.integers(0, 2, n) * 2 - 1).astype(np.float32); aa = (g.integers(0, 2, (3, n)) * 2 - 1).astype(np.float32); B = aa * R
    assert int(np.argmax(B @ ((B[0] * aa[0]) * aa[1]))) == 1, "VSA analogy unbind"
    assert N == 4096; print("[selftest] PASS: singlehop analogy", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def single_hop(g, n):
    E = bp(M, n, g); A = bp(min(64, M), n, g); av = [int(g.integers(0, A.shape[0])) for _ in range(M)]
    W = (A[np.array(av)].T @ E).astype(np.float32)
    ev = list(g.choice(M, size=min(TRIALS, M), replace=False))
    return float(np.mean([cu(A, W @ (E[i] + 0.4 * bp(1, n, g)[0])) == av[i] for i in ev]))


def multi_hop(g, n):
    # A->B, B->C chains; query A, retrieve C via 2-hop iterate
    L = M; E = bp(L + 2, n, g)
    Wab = (E[1:L + 1].T @ E[0:L]).astype(np.float32)        # E[i] -> E[i+1]
    ev = list(g.choice(L - 1, size=min(TRIALS, L - 1), replace=False))
    ok = 0
    for i in ev:
        b = cu(E, Wab @ E[i]); c = cu(E, Wab @ E[b])         # 2 hops
        ok += int(c == i + 2)
    return float(ok / len(ev))


def analogical(g, n):
    # VSA analogy: shared relation R, b_i = R (*) a_i (raw +/-1, exact self-inverse). Infer R from an example pair
    # (a_i,b_i) -> R_hat = b_i (*) a_i; apply to query a_j -> pred = R_hat (*) a_j == b_j; cleanup over B.
    K = min(64, M); ok = 0
    for _ in range(TRIALS):
        R = (g.integers(0, 2, n) * 2 - 1).astype(np.float32)
        A = (g.integers(0, 2, (K, n)) * 2 - 1).astype(np.float32)
        B = A * R                                            # b_i = R (*) a_i, elementwise raw +/-1
        i, j = g.choice(K, size=2, replace=False)
        R_hat = B[i] * A[i]                                  # infer relation from example pair i
        pred = R_hat * A[j]                                  # transfer to query a_j
        ok += int(int(np.argmax(B @ pred)) == j)            # cleanup over B -> should recover b_j
    return float(ok / TRIALS)


def counterfactual(g, n):
    E = bp(M, n, g); V = bp(32, n, g); v0 = [int(g.integers(0, 32)) for _ in range(M)]
    W = (V[np.array(v0)].T @ E).astype(np.float32)
    upd = list(g.choice(M, size=min(TRIALS, M), replace=False)); newv = {}
    for i in upd:
        nv = int((v0[i] + 1 + g.integers(0, 31)) % 32); W -= np.outer(W @ E[i], E[i]); W += np.outer(V[nv], E[i]); newv[i] = nv
    return float(np.mean([cu(V, W @ E[i]) == newv[i] for i in upd]))


def run_seed(seed) -> Dict:
    g = np.random.default_rng(seed); n = N_DIM
    return {"seed": seed, "single_hop": single_hop(g, n), "multi_hop": multi_hop(g, n),
            "analogical": analogical(g, n), "counterfactual": counterfactual(g, n)}


def verdict(ps) -> Tuple[str, str]:
    dims = {k: float(np.mean([p[k] for p in ps])) for k in ("single_hop", "multi_hop", "analogical", "counterfactual")}
    lo = min(dims.values())
    summary = "single_hop=%.3f multi_hop=%.3f analogical=%.3f counterfactual=%.3f (N=4096)" % (
        dims["single_hop"], dims["multi_hop"], dims["analogical"], dims["counterfactual"])
    if lo >= 0.90:
        return ("HARD_PASS", "HARD_PASS: all 4 CCC-1-v2 capability dims hold at Phase-2 N=4096. " + summary)
    if lo >= 0.75:
        return ("MIDDLE_BAND", "MIDDLE_BAND: capabilities mostly hold at N=4096; weakest %.3f. " % lo + summary)
    return ("HARD_FAIL", "HARD_FAIL: a capability dim < 0.60 at N=4096. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d M=%d trials=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, M, TRIALS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r)
    print("  [seed=%d] single=%.3f multi=%.3f analog=%.3f counterfact=%.3f" % (seed, r["single_hop"], r["multi_hop"], r["analogical"], r["counterfactual"]), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N_DIM, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
