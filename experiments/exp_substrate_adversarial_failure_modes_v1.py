"""
substrate_adversarial_failure_modes_v1 -- HP-10: honest adversarial failure-mode evaluation -- CPU.

ROUTING: research envelope_pushing_HP7_to_HP11 (HP-10, honest-limits). We focused on categorical wins; this probes
  where substrate FAILS -- required for regulated-AI (medical/legal/financial) deployment honesty. Tests 4 decisive
  failure modes: A CONTRADICTION (store X=A then X=B -> returns latest?), E OUT-OF-DISTRIBUTION (never-stored query
  -> LOW confidence flaggable?), F OVERFLOW (write past capacity -> graceful or catastrophic?), D ADVERSARIAL
  similar-keys (confusion rate). CPU numpy $0.

PRE-REGISTERED bands: HARD-PASS all 4 predictable (contradiction>=0.9 latest, OOD conf-gap clear, overflow graceful
  [monotone decline, no NaN], adversarial confusion bounded <0.3). MIDDLE: 3/4. HARD-FAIL: any catastrophic (silent
  corruption / OOD indistinguishable / overflow crash).
FORMULA SELF-TESTS (PROT-022): 1. cf-RPE overwrite latest. 2. OOD low overlap. 3. N=4096.
ASCII-only. write_metrics. PROT-018 _n4096 -> N=4096.
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

ANCHOR_NAME = "substrate_adversarial_failure_modes_v1"
_N_SUFFIX = 4096; N = 4096; assert N == _N_SUFFIX
LR = 0.5
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N_DIM = 1024; V_VAL = 16
else:
    SEEDS = [7, 17, 23]; N_DIM = N; V_VAL = 16


def ub(M, n, g):
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def cfrpe(W, k, v, n):
    W += (LR / n) * np.outer(v - W @ k, k)


def _selftest():
    g = np.random.default_rng(0); n = 256; K = ub(1, n, g)[0]; V = ub(2, n, g); W = np.zeros((n, n), dtype=np.float32)
    for _ in range(8):
        cfrpe(W, K, V[0], n)
    for _ in range(8):
        cfrpe(W, K, V[1], n)                          # overwrite to value 1
    assert int(np.argmax(V @ (W @ K))) == 1, "cf-RPE overwrite latest"
    ood = ub(1, n, g)[0]; assert abs(float(ood @ (W @ K))) < 0.5, "OOD low overlap"
    assert N == 4096; print("[selftest] PASS: overwrite OOD", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed) -> Dict:
    g = np.random.default_rng(seed); n = N_DIM; EV = ub(V_VAL, n, g)
    # ---- A. CONTRADICTION (store X=A, then X=B; query -> latest B?) ----
    M = 200; EK = ub(M, n, g); vals = [int(g.integers(0, V_VAL)) for _ in range(M)]; W = np.zeros((n, n), dtype=np.float32)
    for i in range(M):
        cfrpe(W, EK[i], EV[vals[i]], n)
    newv = {i: int((vals[i] + 1 + g.integers(0, V_VAL - 1)) % V_VAL) for i in range(M)}
    for i in range(M):
        for _ in range(3):
            cfrpe(W, EK[i], EV[newv[i]], n)            # contradict: overwrite to new value
    contradiction_latest = float(np.mean([int(np.argmax(EV @ (W @ EK[i]))) == newv[i] for i in range(M)]))

    # ---- E. OUT-OF-DISTRIBUTION (never-stored keys -> low confidence) ----
    in_conf = np.array([float(np.max(EV @ (W @ EK[i]))) for i in range(M)])
    ood_keys = ub(M, n, g); ood_conf = np.array([float(np.max(EV @ (W @ ood_keys[i]))) for i in range(M)])
    ood_gap = float(in_conf.mean() - ood_conf.mean()); ood_separable = ood_conf.mean() < 0.5 * in_conf.mean()

    # ---- F. OVERFLOW (write past capacity -> graceful decline, no NaN) ----
    recalls = []; Wf = np.zeros((n, n), dtype=np.float32); ek2 = ub(4000, n, g); vv = [int(g.integers(0, V_VAL)) for _ in range(4000)]
    grid = [200, 500, 1000, 2000, 4000]; prev = 0
    for mi, Mx in enumerate(grid):
        for i in range(prev, Mx):
            cfrpe(Wf, ek2[i], EV[vv[i]], n)
        prev = Mx
        acc = float(np.mean([int(np.argmax(EV @ (Wf @ ek2[i]))) == vv[i] for i in range(0, Mx, max(1, Mx // 200))]))
        recalls.append(acc)
    no_nan = bool(np.all(np.isfinite(Wf)))
    monotone = all(recalls[i] >= recalls[i + 1] - 0.05 for i in range(len(recalls) - 1))   # graceful: non-increasing-ish
    overflow_graceful = no_nan and monotone

    # ---- D. ADVERSARIAL similar keys (small perturbation; confusion rate) ----
    base = ub(100, n, g); adv = base + 0.15 * ub(100, n, g); adv /= np.linalg.norm(adv, axis=1, keepdims=True)
    Wa = np.zeros((n, n), dtype=np.float32); bvv = [int(g.integers(0, V_VAL)) for _ in range(100)]; avv = [int(g.integers(0, V_VAL)) for _ in range(100)]
    for i in range(100):
        cfrpe(Wa, base[i], EV[bvv[i]], n); cfrpe(Wa, adv[i], EV[avv[i]], n)
    confusion = float(np.mean([(int(np.argmax(EV @ (Wa @ base[i]))) != bvv[i]) for i in range(100)]))

    return {"seed": seed, "contradiction_latest": contradiction_latest, "ood_gap": ood_gap, "ood_separable": bool(ood_separable),
            "in_conf_mean": float(in_conf.mean()), "ood_conf_mean": float(ood_conf.mean()),
            "overflow_recalls": recalls, "overflow_graceful": overflow_graceful, "overflow_no_nan": no_nan,
            "adversarial_confusion": confusion}


def verdict(ps) -> Tuple[str, str]:
    cl = float(np.mean([p["contradiction_latest"] for p in ps])); oods = all(p["ood_separable"] for p in ps)
    ofg = all(p["overflow_graceful"] for p in ps); conf = float(np.mean([p["adversarial_confusion"] for p in ps]))
    A = cl >= 0.9; E = oods; F = ofg; D = conf < 0.3; npass = A + E + F + D
    summary = "A contradiction->latest=%.2f[%s] | E OOD conf in=%.2f/ood=%.2f separable=%s[%s] | F overflow recalls=%s graceful=%s[%s] | D adversarial confusion=%.2f[%s]" % (
        cl, "ok" if A else "FAIL", ps[0]["in_conf_mean"], ps[0]["ood_conf_mean"], oods, "ok" if E else "FAIL",
        [round(x, 2) for x in ps[0]["overflow_recalls"]], ofg, "ok" if F else "FAIL", conf, "ok" if D else "FAIL")
    if npass == 4:
        return ("HARD_PASS", "HARD_PASS: substrate handles all 4 adversarial modes predictably (safe-to-deploy profile). " + summary)
    if npass == 3:
        return ("MIDDLE_BAND", "MIDDLE_BAND: 3/4 adversarial modes predictable; 1 needs mitigation. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: catastrophic adversarial failure mode(s). " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r)
    print("  [seed=%d] contradiction=%.2f ood_sep=%s overflow_graceful=%s adv_confusion=%.2f" % (seed, r["contradiction_latest"], r["ood_separable"], r["overflow_graceful"], r["adversarial_confusion"]), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N_DIM, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
