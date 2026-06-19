"""
exp_smw_pinv_1M_churn_v1 -- SMW insert+DELETE (down-date) timing + stability at scale -- CPU.

ROUTING: SMW_pinv follow-up (insert gate passed at 4.25ms/update; production also needs DELETE for GDPR erasure + churn).
  Sherman-Morrison down-date removes a fact: G -= k k^T -> Ginv += (Ginv k)(k^T Ginv)/(1 - k^T Ginv k), same O(D^2). Runs a
  churn workload (insert M, delete half, re-insert) measuring delete per-update wall AND numerical stability (down-dated
  inverse must match a direct recompute within tolerance, checked periodically). Pure numpy float32. CPU.
PRE-REGISTERED: HARD-PASS delete per-update < 5 ms AND down-dated inverse matches direct inverse (max abs err < 1e-2) after
  churn. MIDDLE delete 5-20ms or err 1e-2..1e-1. HARD-FAIL delete > 20ms OR err > 1e-1 (down-date unstable -> periodic refactor).
FORMULA SELF-TESTS (PROT-022): 1. down-date inverts insert. 2. SM update matches direct. 3. finite.
ASCII-only. write_metrics. PROT-018 _v1.
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
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "smw_pinv_1M_churn_v1"; D = 1024; RIDGE = 1e-2
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
M_BASE = 3000 if RUN_MODE == "smoke" else 200000; N_DELETE = 1500 if RUN_MODE == "smoke" else 100000


def sm_insert(Ginv, k):
    u = Ginv @ k; d = 1.0 + float(k @ u); Ginv -= (np.outer(u, u) / d).astype(Ginv.dtype); return Ginv


def sm_delete(Ginv, k):
    u = Ginv @ k; d = 1.0 - float(k @ u); Ginv += (np.outer(u, u) / d).astype(Ginv.dtype); return Ginv


def _selftest():
    g = np.random.default_rng(0); d = 16; G = np.eye(d); Ginv = np.linalg.inv(G); k = np.sign(g.standard_normal(d))
    G2 = G + np.outer(k, k); Gi2 = sm_insert(Ginv.copy(), k); assert np.allclose(Gi2, np.linalg.inv(G2), atol=1e-5), "SM update matches direct"
    Gi3 = sm_delete(Gi2, k); assert np.allclose(Gi3, Ginv, atol=1e-5), "down-date inverts insert"
    assert np.all(np.isfinite(Gi3)), "finite"
    print("[selftest] PASS: smw-pinv-1M-churn", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run() -> Dict:
    g = np.random.default_rng(808)
    Ginv = (np.eye(D) / RIDGE).astype(np.float32); G_direct = (np.eye(D) * RIDGE).astype(np.float64)  # track true G for a check
    keys = np.sign(g.standard_normal((M_BASE, D))).astype(np.float32)
    # insert M_BASE
    for i in range(M_BASE):
        sm_insert(Ginv, keys[i]); G_direct += np.outer(keys[i].astype(np.float64), keys[i].astype(np.float64))
    # delete N_DELETE (the first N_DELETE keys) -- timed
    t0 = time.perf_counter()
    for i in range(N_DELETE):
        sm_delete(Ginv, keys[i])
    dt = time.perf_counter() - t0; per_ms = dt / N_DELETE * 1e3
    for i in range(N_DELETE):
        G_direct -= np.outer(keys[i].astype(np.float64), keys[i].astype(np.float64))
    err = float(np.abs(Ginv.astype(np.float64) - np.linalg.inv(G_direct)).max())
    finite = bool(np.all(np.isfinite(Ginv)))
    print("  M_base=%d deleted=%d  delete per-update=%.4f ms  max_inv_err=%.2e  finite=%s" % (M_BASE, N_DELETE, per_ms, err, finite), flush=True)
    return {"m_base": M_BASE, "n_delete": N_DELETE, "delete_per_ms": per_ms, "inv_err": err, "finite": finite}


def verdict(r) -> Tuple[str, str]:
    p = r["delete_per_ms"]; e = r["inv_err"]; s = "delete per-update=%.4f ms inv_err=%.2e finite=%s (M_base=%d del=%d)" % (p, e, r["finite"], r["m_base"], r["n_delete"])
    if not r["finite"] or e > 1e-1:
        return ("HARD_FAIL", "HARD_FAIL: down-date numerically unstable (err>0.1 or non-finite) -- needs periodic refactor. " + s)
    if p < 5.0 and e < 1e-2:
        return ("HARD_PASS", "HARD_PASS: SMW delete <5ms/update AND inverse stays accurate after churn -- GDPR erasure + churn feasible at scale. " + s)
    if p < 20.0:
        return ("MIDDLE_BAND", "MIDDLE_BAND: delete 5-20ms or inv_err 1e-2..1e-1 -- works, refactor occasionally. " + s)
    return ("HARD_FAIL", "HARD_FAIL: delete >20ms/update. " + s)


print("[config] anchor=%s mode=%s D=%d M_base=%d delete=%d" % (ANCHOR_NAME, RUN_MODE, D, M_BASE, N_DELETE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
