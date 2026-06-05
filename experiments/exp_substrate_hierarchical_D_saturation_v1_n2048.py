"""
substrate_hierarchical_D_saturation_v1_n2048 -- NEW EXP 5: hierarchical aggregator D-saturation -- remote CPU.

ROUTING: research design-input note (NEW EXP 5). Capacity composes MULTIPLICATIVELY across D domains (validated
  D=5, independence=1.0, 125K). Question: where does the linear-in-D scaling SATURATE as D grows (domain keys are
  random -> overlap grows -> cross-domain interference)? Gives the production (N, D) sizing knob. CPU numpy, $0.

MODEL: D domains, each a sparse substrate (B2 DG codes, f=0.02, N_dg=4N) bound to a random domain KEY. Store M0
  sparse patterns per domain; cross-domain query must route via the domain key. Measure independence_recall(D) =
  per-domain recall when D domains coexist, and effective_capacity(D) = D * M0 * independence_recall(D). Sweep D.

PRE-REGISTERED bands: HARD-PASS effective capacity scales ~linearly (independence_recall >= 0.90) up to D>=20.
  MIDDLE: linear to D in [10,20). HARD-FAIL: saturates by D<10 (independence_recall<0.90 at D=10).

FORMULA SELF-TESTS (PROT-022): 1. sparse recall. 2. orthogonal-ish domain keys reduce cross-talk. 3. N=2048.
ASCII-only. write_metrics. PROT-018 _n2048 -> N=2048.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, math
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "substrate_hierarchical_D_saturation_v1_n2048"
_N_SUFFIX = 2048; N = 2048; assert N == _N_SUFFIX
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()

F_SPARSE = 0.02; M0 = 200
if RUN_MODE == "smoke":
    SEEDS = [1]; N_DIM = 512; N_DG = 2048; D_GRID = [5, 10, 20]; M0 = 60
else:
    SEEDS = [7, 17, 23]; N_DIM = N; N_DG = N * 4; D_GRID = [5, 10, 20, 40]


def sparse_codes(M, n, k, g):
    S = np.zeros((M, n), dtype=np.float32)
    for i in range(M):
        S[i, g.choice(n, size=k, replace=False)] = 1.0
    return S


def kwta(v, k):
    o = np.zeros_like(v); o[np.argpartition(-v, k - 1)[:k]] = 1.0; return o


def independence_recall(D, n_dg, g):
    """store M0 sparse patterns in EACH of D key-bound domains in ONE shared memory; measure per-domain recall."""
    k = max(1, int(round(F_SPARSE * n_dg)))
    keys = (g.integers(0, 2, size=(D, n_dg)) * 2 - 1).astype(np.float32)        # random domain keys
    W = np.zeros((n_dg, n_dg), dtype=np.float32); store = []
    for d in range(D):
        S = sparse_codes(M0, n_dg, k, g)
        bound = (S - F_SPARSE) * keys[d]                                       # bind pattern to domain key
        W += bound.T @ bound; store.append((S, keys[d]))
    np.fill_diagonal(W, 0.0)
    accs = []
    for d in range(D):
        S, key = store[d]
        sample = S[g.choice(M0, size=min(30, M0), replace=False)]
        hits = 0
        for s in sample:
            cue = ((s - F_SPARSE) * key)                                       # key-bound cue
            r = kwta((W @ cue) * key, k)                                       # retrieve + unbind
            hits += (float((r * s).sum() / k) > 0.90)
        accs.append(hits / len(sample))
    return float(np.mean(accs))


def _selftest():
    g = np.random.default_rng(0); n = 512; k = int(round(F_SPARSE * n)); S = sparse_codes(5, n, k, g)
    W = (S - F_SPARSE).T @ (S - F_SPARSE); np.fill_diagonal(W, 0.0)
    assert float((kwta((S[0] - F_SPARSE) @ W.T, k) * S[0]).sum() / k) > 0.9, "sparse recall"
    a = (g.integers(0, 2, n) * 2 - 1).astype(np.float32); b = (g.integers(0, 2, n) * 2 - 1).astype(np.float32)
    assert abs(float((a * b).mean())) < 0.2, "keys roughly orthogonal"
    assert N == 2048; print("[selftest] PASS: sparse_recall ortho_keys", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int) -> Dict:
    g = np.random.default_rng(seed); out = {"seed": seed, "N": N_DIM, "N_dg": N_DG, "M0": M0}
    for D in D_GRID:
        ir = independence_recall(D, N_DG, np.random.default_rng(seed * 100 + D))
        out["D%d_indep" % D] = ir; out["D%d_eff_cap" % D] = float(D * M0 * ir)
    return out


def verdict(ps) -> Tuple[str, str]:
    ind = {D: float(np.mean([p["D%d_indep" % D] for p in ps])) for D in D_GRID}
    cap = {D: float(np.mean([p["D%d_eff_cap" % D] for p in ps])) for D in D_GRID}
    sat = max([D for D in D_GRID if ind[D] >= 0.90], default=0)
    summary = " ".join("D%d:indep=%.2f cap=%.0f" % (D, ind[D], cap[D]) for D in D_GRID) + (" | linear-to-D=%d" % sat)
    if sat >= 20:
        return ("HARD_PASS", "HARD_PASS: capacity scales linearly to D>=20 (independence held). " + summary)
    if sat >= 10:
        return ("MIDDLE_BAND", "MIDDLE_BAND: linear to D~10-20. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: saturates by D<10. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d N_dg=%d D=%s" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, N_DG, D_GRID), flush=True)
if RUN_MODE == "full" and N_DIM != _N_SUFFIX:
    raise RuntimeError("PROT-018 N mismatch")
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r)
    print("  [seed=%d] " % seed + " ".join("D%d:%.2f" % (D, r["D%d_indep" % D]) for D in D_GRID), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N_DIM, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
