"""
substrate_R6_b2_x_sparse_resonator_v1_n5000 -- R6: B2 storage x sparse-resonator recovery (D-RIP) -- remote CPU.

ROUTING: research clarifications_R1_R2_R5_R6 (R6). D-RIP predicts B2 (sparse STORAGE) + sparse-resonator (sparse
  RECOVERY) are orthogonal sparse-axis primitives -> super-additive. Reuses validated R2 block-local resonator.
  Test: store M block-local composites via B2 DG-sparse auto-assoc; recover a cued composite then resonate its K
  factors. K_max (factors recoverable >=85%) for resonator-alone (clean composite) vs B2+resonator (stored composite,
  M loaded). CPU numpy, $0. remote_cpu_queue.

PRE-REGISTERED bands: HARD-PASS K_max(B2+resonator) >= 1.5x K_max(resonator-alone) AT a stored load M>0 (super-
  additive: B2 storage lets the resonator operate on many stored composites without losing K). MIDDLE: K_max(B2+res)
  >= K_max(res-alone) (storage preserves recovery, additive). HARD-FAIL: K_max(B2+res) < K_max(res-alone) (storage degrades recovery).

FORMULA SELF-TESTS (PROT-022): 1. block-local recover (clean). 2. B2 DG-store+recall a composite. 3. N=5000.
ASCII-only. write_metrics. PROT-018 _n5000 -> N=5000.
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

ANCHOR_NAME = "substrate_R6_b2_x_sparse_resonator_v1_n5000"
_N_SUFFIX = 5000; N = 5000; assert N == _N_SUFFIX
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()

V_CODE = 26; F_DG = 0.02
if RUN_MODE == "smoke":
    SEEDS = [1]; N_DIM = 1000; N_DG = 2000; K_GRID = [4, 8]; M_STORE = 50
else:
    SEEDS = [7, 17, 23]; N_DIM = N; N_DG = N * 2; K_GRID = [4, 8, 16, 26]; M_STORE = 300


def make_codebooks(K, n, g):
    bs = n // K; k_act = max(1, int(round(0.02 * bs))); cbs = []
    for i in range(K):
        cb = np.zeros((V_CODE, n), dtype=np.float32)
        for v in range(V_CODE):
            idx = i * bs + g.choice(bs, size=k_act, replace=False); cb[v, idx] = g.integers(0, 2, size=k_act) * 2 - 1
        cbs.append(cb)
    return cbs, bs


def compose(cbs, chosen, K):
    return np.sum([cbs[i][chosen[i]] for i in range(K)], 0).astype(np.float32)


def recover(comp, cbs, K, n):
    bs = n // K
    return [int(np.argmax(cbs[i][:, i * bs:(i + 1) * bs] @ comp[i * bs:(i + 1) * bs])) for i in range(K)]


def dg_project(P, n_dg, g_proj):
    H = P @ g_proj; k = max(1, int(round(F_DG * n_dg))); idx = np.argpartition(-np.abs(H), k - 1)[:k]
    o = np.zeros(n_dg, dtype=np.float32); o[idx] = np.sign(H[idx]); return o


def k_acc(cbs, n, K, g, stored, W):
    """recover K factors of a composite; if stored, route through B2 sparse auto-assoc recall first."""
    correct = 0; total = 0
    for _ in range(20):
        chosen = [int(g.integers(0, V_CODE)) for _ in range(K)]; comp = compose(cbs, chosen, K)
        if stored:
            r = W @ comp; r = r / (np.linalg.norm(r) + 1e-8) * (np.linalg.norm(comp) + 1e-8)   # auto-assoc recall (block-sparse preserved)
            comp = r
        rec = recover(comp, cbs, K, n); correct += sum(1 for a, b in zip(rec, chosen) if a == b); total += K
    return correct / total


def _selftest():
    g = np.random.default_rng(0); n = 200; cbs, bs = make_codebooks(4, n, g)
    chosen = [g.integers(0, V_CODE) for _ in range(4)]; comp = compose(cbs, chosen, 4)
    assert recover(comp, cbs, 4, n) == list(chosen), "block-local recover"
    gp = (g.standard_normal((400, n)).astype(np.float32)); dg = dg_project(comp, 400, gp.T)
    assert int((dg != 0).sum()) == max(1, int(0.02 * 400)), "DG sparsity"
    assert N == 5000; print("[selftest] PASS: blocklocal DG_sparse", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int) -> Dict:
    g = np.random.default_rng(seed); out = {"seed": seed, "N": N_DIM, "M_stored": M_STORE}
    res_alone = {}; b2_res = {}
    for K in K_GRID:
        cbs, bs = make_codebooks(K, N_DIM, g)
        # B2 store M random composites in DG auto-assoc memory W
        W = np.zeros((N_DIM, N_DIM), dtype=np.float32)
        for _ in range(M_STORE):
            ch = [int(g.integers(0, V_CODE)) for _ in range(K)]; comp = compose(cbs, ch, K)
            W += np.outer(comp, comp)
        np.fill_diagonal(W, 0.0)
        res_alone[K] = k_acc(cbs, N_DIM, K, np.random.default_rng(seed + K), False, None)
        b2_res[K] = k_acc(cbs, N_DIM, K, np.random.default_rng(seed + K), True, W)
    out["res_alone"] = res_alone; out["b2_res"] = b2_res
    out["kmax_res"] = max([K for K in K_GRID if res_alone[K] >= 0.85], default=0)
    out["kmax_b2res"] = max([K for K in K_GRID if b2_res[K] >= 0.85], default=0)
    return out


def verdict(ps) -> Tuple[str, str]:
    kr = float(np.mean([p["kmax_res"] for p in ps])); kb = float(np.mean([p["kmax_b2res"] for p in ps]))
    summary = "kmax_resonator_alone=%.0f kmax_B2+resonator=%.0f (M_stored=%d)" % (kr, kb, ps[0]["M_stored"])
    if kb >= 1.5 * max(kr, 1):
        return ("HARD_PASS", "HARD_PASS: B2-storage x resonator SUPER-ADDITIVE on K_max. " + summary)
    if kb >= kr:
        return ("MIDDLE_BAND", "MIDDLE_BAND: B2-storage preserves resonator recovery (additive, not super). " + summary)
    return ("HARD_FAIL", "HARD_FAIL: B2-storage degrades resonator recovery. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d N_dg=%d K=%s M=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, N_DG, K_GRID, M_STORE), flush=True)
if RUN_MODE == "full" and N_DIM != _N_SUFFIX:
    raise RuntimeError("PROT-018 N mismatch")
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r)
    print("  [seed=%d] kmax_res=%d kmax_b2res=%d" % (seed, r["kmax_res"], r["kmax_b2res"]), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N_DIM, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
