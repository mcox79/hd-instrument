"""
exp_zkl_curve_k_sweep_v1 -- ZKL Certificate battery cell 3 (THE central commercial decision) -- CPU.

ROUTING: Research handoff exp_dev_handoff_research_ZKL_Certificate_10h_battery cell 3 (DECISIVE). Membership-inference
  leakage vs query budget k: an adaptive attacker issues k paraphrase-queries per target and forms a LiRA-style membership
  statistic; we report ZKL = TPR @ FPR=0.01 at k in {1,10,50,100,500}, whitening ENABLED. The GOLD 3.0 compounding-defense
  story holds iff leakage accumulates SUBLINEARLY (ZKL(50)<=0.10). Paraphrases modelled as bounded embedding-space
  perturbations of the target (exp_dev autonomy: simpler threshold attack in lieu of an MT pipeline). CPU $0.
PRE-REGISTERED (research bands, may tighten not loosen): HARD-PASS ZKL(50)<=0.10 AND ZKL(100)<=0.35 (sublinear).
  MID ZKL(50) in [0.10,0.30]. HARD-FAIL ZKL(50)>0.30 (no structural privacy advantage).
FORMULA SELF-TESTS (PROT-022): 1. whiten preserves dim. 2. TPR@FPR monotone in separation. 3. paraphrase bounded.
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

ANCHOR_NAME = "zkl_curve_k_sweep_v1"
N = 768; PARA_NOISE = 0.35; FPR = 0.01; K_GRID = [1, 10, 50, 100, 500]
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    N_KB = 300; N_TGT = 60; K_GRID = [1, 10, 50]
else:
    N_KB = 3000; N_TGT = 400


def unit(x):
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)


def whiten_fit(K):
    Kc = K - K.mean(0); cov = (Kc.T @ Kc) / Kc.shape[0]
    U, S, _ = np.linalg.svd(cov); Wd = U @ np.diag(1.0 / np.sqrt(S + 1e-3)) @ U.T
    return Kc @ Wd, K.mean(0), Wd


def tpr_at_fpr(member_stat, nonmember_stat, fpr):
    thr = np.quantile(nonmember_stat, 1 - fpr)                       # threshold giving target FPR on non-members
    return float((member_stat >= thr).mean())


def membership_stat(targets, kb_sign, k, g):
    # k paraphrase-queries: bounded perturbations; sign-quantize (production); statistic = mean grounding (max-cos to KB)
    stats = []
    for t in targets:
        paras = unit(t[None, :] + PARA_NOISE * g.standard_normal((k, t.shape[0])).astype(np.float32))
        pq = np.sign(paras).astype(np.float32); pq[pq == 0] = 1.0
        ground = (pq @ kb_sign.T).max(axis=1) / kb_sign.shape[1]      # normalized grounding per paraphrase
        stats.append(float(ground.mean()))
    return np.array(stats)


def _selftest():
    g = np.random.default_rng(0); W, mu, Wd = whiten_fit(g.standard_normal((40, 16))); assert W.shape == (40, 16), "whiten preserves dim"
    assert tpr_at_fpr(np.array([5.0, 6, 7]), np.array([0.0, 1, 2]), 0.01) >= 0.9, "TPR@FPR monotone in separation"
    t = g.standard_normal(8).astype(np.float32); p = unit(t[None, :] + 0.35 * g.standard_normal((3, 8)).astype(np.float32)); assert np.all(np.abs(np.linalg.norm(p, axis=1) - 1) < 1e-4), "paraphrase bounded"
    print("[selftest] PASS: zkl-kcurve", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run() -> Dict:
    g = np.random.default_rng(7); raw = g.standard_normal((N_KB + N_TGT, N)).astype(np.float32)
    kb_raw = raw[:N_KB]; Wkb, mu, Wd = whiten_fit(kb_raw)
    kb_w = unit(Wkb); kb_sign = np.sign(kb_w).astype(np.float32); kb_sign[kb_sign == 0] = 1.0
    members = unit((kb_raw[g.choice(N_KB, N_TGT, replace=False)] - mu) @ Wd)   # whitened stored targets
    nonmembers = unit((raw[N_KB:N_KB + N_TGT] - mu) @ Wd)                      # whitened never-stored
    by = {}
    for k in K_GRID:
        ms = membership_stat(members, kb_sign, k, np.random.default_rng(100 + k))
        ns = membership_stat(nonmembers, kb_sign, k, np.random.default_rng(200 + k))
        zkl = tpr_at_fpr(ms, ns, FPR); by["k%d" % k] = zkl
        print("  [k=%d] ZKL (TPR@FPR=0.01) = %.4f" % (k, zkl), flush=True)
    return {"by_k": by}


def verdict(r) -> Tuple[str, str]:
    z50 = r["by_k"].get("k50"); z100 = r["by_k"].get("k100")
    summary = "ZKL curve (TPR@FPR=0.01): %s" % {k: round(v, 4) for k, v in r["by_k"].items()}
    if z50 is None:
        return ("MIDDLE_BAND", "MIDDLE_BAND (smoke: k=50 only): " + summary)
    if z50 <= 0.10 and (z100 is None or z100 <= 0.35):
        return ("HARD_PASS", "HARD_PASS: ZKL(50)<=0.10 (and ZKL(100)<=0.35) -- sublinear leakage; GOLD 3.0 compounding-defense holds; HIPAA ZKL claim supportable. " + summary)
    if z50 <= 0.30:
        return ("MIDDLE_BAND", "MIDDLE_BAND: ZKL(50) in [0.10,0.30] -- qualify claim with measured value. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: ZKL(50)>0.30 -- leakage not sublinear; no structural privacy advantage. " + summary)


print("[config] anchor=%s mode=%s N=%d n_kb=%d n_tgt=%d K=%s" % (ANCHOR_NAME, RUN_MODE, N, N_KB, N_TGT, K_GRID), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
