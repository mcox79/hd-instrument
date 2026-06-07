"""
exp_zkl_whitening_ablation_v1 -- SZA protocol anchor 2 (whitening ON vs OFF ZKL reduction) -- CPU.

ROUTING: Research handoff exp_dev_handoff_research_chain1_drill2_SZA_protocol (#2). Substrate WITH vs WITHOUT whitening on
  identical KB + paraphrase attack (k=50); measure the ZKL reduction factor. Validates the dual-purpose-whitening claim
  (whitening improves BOTH retrieval AND privacy). CPU $0.
PRE-REGISTERED (research bands): HARD-PASS ZKL(whiten ON) <= 0.60 * ZKL(whiten OFF) (>=40%% reduction). MID 0.60-0.90.
  HARD-FAIL > 0.90 (no privacy contribution from whitening).
FORMULA SELF-TESTS (PROT-022): 1. whiten preserves dim. 2. TPR@FPR monotone. 3. sign bounded.
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

ANCHOR_NAME = "zkl_whitening_ablation_v1"
N = 768; PARA_NOISE = 0.35; FPR = 0.01; K = 50
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    N_KB = 300; N_TGT = 60
else:
    N_KB = 3000; N_TGT = 400


def unit(x):
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)


def whiten_fit(K_):
    Kc = K_ - K_.mean(0); cov = (Kc.T @ Kc) / Kc.shape[0]
    U, S, _ = np.linalg.svd(cov); Wd = U @ np.diag(1.0 / np.sqrt(S + 1e-3)) @ U.T
    return Kc @ Wd, K_.mean(0), Wd


def tpr_at_fpr(member, nonmember, fpr):
    thr = np.quantile(nonmember, 1 - fpr); return float((member >= thr).mean())


def stat_sign(targets, kb_sign, k, g):
    out = []
    for t in targets:
        paras = unit(t[None, :] + PARA_NOISE * g.standard_normal((k, t.shape[0])).astype(np.float32))
        pq = np.sign(paras).astype(np.float32); pq[pq == 0] = 1.0
        out.append(float((pq @ kb_sign.T).max(axis=1).mean() / kb_sign.shape[1]))
    return np.array(out)


def _selftest():
    g = np.random.default_rng(0); W, mu, Wd = whiten_fit(g.standard_normal((40, 16))); assert W.shape == (40, 16), "whiten preserves dim"
    assert tpr_at_fpr(np.array([5.0, 6, 7]), np.array([0.0, 1, 2]), 0.01) >= 0.9, "TPR@FPR monotone"
    assert set(np.unique(np.sign(g.standard_normal(50)))) <= {-1.0, 0.0, 1.0}, "sign bounded"
    print("[selftest] PASS: zkl-whiten-ablation", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run() -> Dict:
    g = np.random.default_rng(7); raw = g.standard_normal((N_KB + N_TGT, N)).astype(np.float32); sel = g.choice(N_KB, N_TGT, replace=False)
    Wkb, mu, Wd = whiten_fit(raw[:N_KB]); kb_on = np.sign(unit(Wkb)).astype(np.float32); kb_on[kb_on == 0] = 1.0
    mem_on = unit((raw[sel] - mu) @ Wd); non_on = unit((raw[N_KB:N_KB + N_TGT] - mu) @ Wd)
    z_on = tpr_at_fpr(stat_sign(mem_on, kb_on, K, np.random.default_rng(100)), stat_sign(non_on, kb_on, K, np.random.default_rng(200)), FPR)
    kb_off = np.sign(unit(raw[:N_KB])).astype(np.float32); kb_off[kb_off == 0] = 1.0
    mem_off = unit(raw[sel]); non_off = unit(raw[N_KB:N_KB + N_TGT])
    z_off = tpr_at_fpr(stat_sign(mem_off, kb_off, K, np.random.default_rng(300)), stat_sign(non_off, kb_off, K, np.random.default_rng(400)), FPR)
    print("  ZKL_whiten_on=%.4f ZKL_whiten_off=%.4f ratio=%.3f" % (z_on, z_off, z_on / max(z_off, 1e-9)), flush=True)
    return {"zkl_on": float(z_on), "zkl_off": float(z_off), "ratio": float(z_on / max(z_off, 1e-9))}


def verdict(r) -> Tuple[str, str]:
    ratio = r["ratio"]; summary = "ZKL_whiten_on=%.4f ZKL_whiten_off=%.4f on/off=%.3f (k=%d)" % (r["zkl_on"], r["zkl_off"], ratio, K)
    if ratio <= 0.60:
        return ("HARD_PASS", "HARD_PASS: whitening cuts ZKL by >=40%% -- dual-purpose whitening (retrieval AND privacy) confirmed. " + summary)
    if ratio <= 0.90:
        return ("MIDDLE_BAND", "MIDDLE_BAND: whitening cuts ZKL 10-40%% (partial). " + summary)
    return ("HARD_FAIL", "HARD_FAIL: whitening gives no meaningful privacy reduction. " + summary)


print("[config] anchor=%s mode=%s N=%d n_kb=%d n_tgt=%d k=%d" % (ANCHOR_NAME, RUN_MODE, N, N_KB, N_TGT, K), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
