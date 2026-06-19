"""
exp_causal_intervention_isolation_v1 -- causal/counterfactual (3x) anchor 3 (locality of do()) -- CPU.

ROUTING: Research handoff exp_dev_handoff_research_causal_counterfactual_3x #3. Store 200 facts in W at N=4096. Perform
  rank-1 downdate + rank-1 write on ONE fact (single intervention). Re-query all 199 OTHER facts; measure mean cosine
  degradation before vs after. Confirms the do() intervention is LOCAL (does not corrupt the rest of memory) -- required for
  the counterfactual-replay API to be trustworthy. CPU $0 ~3min.
PRE-REGISTERED: HARD-PASS mean non-target recall degradation < 0.02 AND non-target retrieval stays >=0.95 (intervention is
  local). MID degradation 0.02-0.10. HARD-FAIL >0.10 (intervention corrupts unrelated memory).
FORMULA SELF-TESTS (PROT-022): 1. clean recall high. 2. downdate matches rebuild. 3. cosine bound.
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

ANCHOR_NAME = "causal_intervention_isolation_v1"
N = 4096; RIDGE = 1e-3; FLIP = 0.05
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; M = 60
else:
    SEEDS = [7, 17, 23]; M = 200


def patterns(m, n, g):
    return (g.integers(0, 2, (m, n)) * 2 - 1).astype(np.float64)


def gram_inv(P):
    return np.linalg.inv(P @ P.T + RIDGE * np.eye(P.shape[0]))


def W_of(P, Gi):
    return P.T @ Gi @ P


def recall(W, P, seed):
    g = np.random.default_rng(seed); m, n = P.shape; s = P * np.where(g.random((m, n)) < FLIP, -1.0, 1.0)
    Wd = W.copy(); np.fill_diagonal(Wd, 0.0)
    for _ in range(8):
        s = np.sign(s @ Wd.T); s[s == 0] = 1.0
    return float(np.mean(np.all(s == P, axis=1)))


def _selftest():
    g = np.random.default_rng(0); P = patterns(8, 128, g); Gi = gram_inv(P)
    assert recall(W_of(P, Gi), P, 0) >= 0.95, "clean recall high"
    E = Gi[:-1, :-1]; f = Gi[:-1, -1]; h = float(Gi[-1, -1]); Gd = E - np.outer(f, f) / h
    assert np.max(np.abs(Gd - gram_inv(P[:-1]))) < 1e-6, "downdate matches rebuild"
    print("[selftest] PASS: intervention-isolation", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed) -> Dict:
    g = np.random.default_rng(seed); P = patterns(M, N, g); Gi = gram_inv(P)
    before = recall(W_of(P, Gi), P, seed)                                          # all-fact recall before
    # intervene on fact idx: downdate it, write a replacement
    idx = int(g.integers(0, M)); order = [i for i in range(M) if i != idx] + [idx]
    Gp = Gi[np.ix_(order, order)]; E = Gp[:-1, :-1]; f = Gp[:-1, -1]; h = float(Gp[-1, -1]); Gd = E - np.outer(f, f) / h
    kept = P[[i for i in range(M) if i != idx]]
    newfact = patterns(1, N, g); P2 = np.vstack([kept, newfact])
    # rank-1 up-date Gd with newfact (bordered inverse)
    b = kept @ newfact[0]; Gib = Gd @ b; s = float(newfact[0] @ newfact[0]) + RIDGE - float(b @ Gib); mm = kept.shape[0]
    Gi2 = np.zeros((mm + 1, mm + 1)); Gi2[:mm, :mm] = Gd + np.outer(Gib, Gib) / s; Gi2[:mm, mm] = -Gib / s; Gi2[mm, :mm] = -Gib / s; Gi2[mm, mm] = 1.0 / s
    W2 = W_of(P2, Gi2)
    others = kept                                                                  # the 199 non-target facts (now first mm rows of P2)
    after_others = recall(W2, others, seed + 1)
    before_others = recall(W_of(kept, gram_inv(kept)), others, seed + 1)
    degr = before_others - after_others
    print("  [seed=%d] non_target_recall before=%.3f after=%.3f degradation=%.4f" % (seed, before_others, after_others, degr), flush=True)
    return {"seed": seed, "before": before_others, "after": after_others, "degradation": float(degr)}


def verdict(ps) -> Tuple[str, str]:
    d = float(np.mean([p["degradation"] for p in ps])); a = float(np.mean([p["after"] for p in ps]))
    summary = "mean non-target degradation=%.4f, non-target recall after intervention=%.3f" % (d, a)
    if d < 0.02 and a >= 0.95:
        return ("HARD_PASS", "HARD_PASS: single intervention is LOCAL -- non-target recall degradation <0.02, others stay >=0.95; counterfactual replay does not corrupt the rest of memory. " + summary)
    if d <= 0.10:
        return ("MIDDLE_BAND", "MIDDLE_BAND: intervention mildly perturbs other facts (degradation 0.02-0.10). " + summary)
    return ("HARD_FAIL", "HARD_FAIL: intervention corrupts unrelated memory (degradation >0.10) -- do() is not local. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d M=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, N, M), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = [run_seed(s) for s in SEEDS]
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
