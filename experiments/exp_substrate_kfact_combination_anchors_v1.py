"""
substrate_kfact_combination_anchors_v1 -- 4 K-fact combination validation anchors (pre-HP-7 lock-in) -- CPU.

ROUTING: research HP7_design_update_rule8_betastar -- validate the HP-7 combination design BEFORE locking it in.
  4 cheap CPU anchors: (1) beta* closed-form vs grid-optimal; (2) K-transition boundary for superposition cleanup
  (~sqrt(N)/2); (3) Rule 8 (Modern Hopfield log-sum-exp) vs Rule 1 (weighted sum) on conflicting facts; (4) resonator
  non-determinism (float32 vs float64 -> cert-hard-fail confirmation). CPU numpy $0.

  beta* = sqrt(N/K) * (1 + CoV_cos)^{-1}; evidence = sum_k softmax(beta* cos_k) phi_k.

PRE-REGISTERED bands (overall HARD-PASS = >=3 of 4 anchors confirm):
  A1 beta* recovery within 10% of grid-optimal. A2 transition K in [14,18] (sqrt(1024)/2=16). A3 Rule8 >= Rule1+5pp.
  A4 resonator float32/float64 disagreement >= 2% (confirms resonator-ban for cert paths).
FORMULA SELF-TESTS (PROT-022): 1. softmax. 2. beta* formula. 3. cos.
ASCII-only. write_metrics. PROT-018 _n1024 -> N=1024.
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

ANCHOR_NAME = "substrate_kfact_combination_anchors_v1"
_N_SUFFIX = 1024; N = 1024; assert N == _N_SUFFIX
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1, 2]; N_DIM = 1024; TRIALS = 100
else:
    SEEDS = [7, 17, 23]; N_DIM = 1024; TRIALS = 400


def bp(M, n, g):
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def softmax(x):
    e = np.exp(x - x.max()); return e / (e.sum() + 1e-12)


def beta_star(n, k, cos):
    cov = float(np.std(cos) / (abs(np.mean(cos)) + 1e-8))
    return math.sqrt(n / k) * (1.0 / (1.0 + cov))


def _selftest():
    s = softmax(np.array([1.0, 2.0, 3.0])); assert abs(s.sum() - 1.0) < 1e-5, "softmax"
    b = beta_star(1024, 4, np.array([0.5, 0.5, 0.5, 0.5])); assert b > 0, "beta* formula"
    assert N == 1024; print("[selftest] PASS: softmax betastar", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def anchor1_betastar(g, n):
    # K facts; subset 'correct' (aligned to target), rest noise. beta* recovery vs grid-optimal recovery.
    ratios = []
    for K in (3, 5, 7):
        rs = []
        for _ in range(TRIALS):
            target = bp(1, n, g)[0]; n_corr = max(1, K // 2 + 1)
            facts = np.stack([target + 0.6 * bp(1, n, g)[0] if i < n_corr else bp(1, n, g)[0] for i in range(K)])
            facts /= np.linalg.norm(facts, axis=1, keepdims=True) + 1e-8
            cos = facts @ target

            def recov(beta):
                ev = (softmax(beta * cos)[:, None] * facts).sum(0); ev /= np.linalg.norm(ev) + 1e-8
                return float(ev @ target)
            bstar = beta_star(n, K, cos); r_star = recov(bstar)
            r_grid = max(recov(b) for b in np.linspace(0.1, 3 * bstar + 5, 40))
            rs.append(r_star / max(r_grid, 1e-8))
        ratios.append(float(np.mean(rs)))
    return float(np.mean(ratios))


def anchor2_transition(g, n):
    # superposition (bundle K) cleanup recovery vs K; find transition >95%->.<80%
    cb = bp(64, n, g); recall_by_k = {}
    for K in range(5, 26):
        ok = tot = 0
        for _ in range(TRIALS // 4):
            idx = g.choice(64, size=K, replace=False); bundle = cb[idx].sum(0); bundle /= np.linalg.norm(bundle) + 1e-8
            rec = [int(np.argmax(cb @ bundle))]  # cleanup top-1 should be one of idx
            ok += int(rec[0] in idx); tot += 1
        recall_by_k[K] = ok / max(tot, 1)
    # transition: last K with recall>0.95 ... first K with recall<0.80
    hi = [K for K in recall_by_k if recall_by_k[K] >= 0.95]; lo = [K for K in recall_by_k if recall_by_k[K] < 0.80]
    trans = (max(hi) + min(lo)) / 2 if hi and lo else (max(hi) if hi else 5)
    return float(trans), recall_by_k


def anchor3_rule8_vs_rule1(g, n):
    # K=5 facts, some CONFLICTING (anti-aligned). Rule 8 (softmax) vs Rule 1 (uniform weighted sum) target recovery.
    K = 5; r8 = []; r1 = []
    for _ in range(TRIALS):
        target = bp(1, n, g)[0]
        facts = np.stack([target + 0.5 * bp(1, n, g)[0] if i < 3 else -target + 0.5 * bp(1, n, g)[0] for i in range(K)])
        facts /= np.linalg.norm(facts, axis=1, keepdims=True) + 1e-8; cos = facts @ target
        b = beta_star(n, K, cos)
        ev8 = (softmax(b * cos)[:, None] * facts).sum(0); ev8 /= np.linalg.norm(ev8) + 1e-8
        ev1 = facts.sum(0); ev1 /= np.linalg.norm(ev1) + 1e-8
        r8.append(float(ev8 @ target)); r1.append(float(ev1 @ target))
    return float(np.mean(r8)), float(np.mean(r1))


def anchor4_resonator_nondeterminism(g, n):
    # block-local resonator iterated sign; float32 vs float64 disagreement rate
    K = 4; V = 26; bs = n // K; disagree = 0; tot = 0
    for _ in range(TRIALS // 4):
        cbs = [bp(V, n, g) for _ in range(K)]; chosen = [int(g.integers(0, V)) for _ in range(K)]
        comp = np.sum([cbs[i][chosen[i]] for i in range(K)], 0)

        def reson(dtype):
            c = comp.astype(dtype)
            for _ in range(8):
                rec = []
                for i in range(K):
                    blk = c[i * bs:(i + 1) * bs]; cb = cbs[i][:, i * bs:(i + 1) * bs].astype(dtype)
                    rec.append(int(np.argmax(cb @ blk)))
                c = np.sum([cbs[i][rec[i]] for i in range(K)], 0).astype(dtype)
            return tuple(rec)
        if reson(np.float32) != reson(np.float64):
            disagree += 1
        tot += 1
    return float(disagree / max(tot, 1))


def run_seed(seed) -> Dict:
    g = np.random.default_rng(seed); n = N_DIM
    a1 = anchor1_betastar(g, n)
    a2_trans, a2_curve = anchor2_transition(g, n)
    a3_r8, a3_r1 = anchor3_rule8_vs_rule1(g, n)
    a4 = anchor4_resonator_nondeterminism(g, n)
    return {"seed": seed, "A1_betastar_recovery_ratio": a1, "A2_transition_K": a2_trans,
            "A3_rule8": a3_r8, "A3_rule1": a3_r1, "A3_gain_pp": float((a3_r8 - a3_r1) * 100), "A4_resonator_disagree": a4}


def verdict(ps) -> Tuple[str, str]:
    a1 = float(np.mean([p["A1_betastar_recovery_ratio"] for p in ps])); a2 = float(np.mean([p["A2_transition_K"] for p in ps]))
    a3g = float(np.mean([p["A3_gain_pp"] for p in ps])); a4 = float(np.mean([p["A4_resonator_disagree"] for p in ps]))
    A1 = a1 >= 0.90; A2 = 14 <= a2 <= 18; A3 = a3g >= 5.0; A4 = a4 >= 0.02; npass = A1 + A2 + A3 + A4
    summary = "A1 beta* recovery=%.2f of grid [%s] | A2 transition K=%.1f (sqrt(N)/2=16) [%s] | A3 Rule8-Rule1=+%.1fpp [%s] | A4 resonator disagree=%.1f%% [%s]" % (
        a1, "ok" if A1 else "no", a2, "ok" if A2 else "no", a3g, "ok" if A3 else "no", a4 * 100, "ok" if A4 else "no")
    if npass >= 3:
        return ("HARD_PASS", "HARD_PASS: HP-7 combination design validated (>=3/4 anchors). " + summary)
    if npass == 2:
        return ("MIDDLE_BAND", "MIDDLE_BAND: 2/4 anchors confirm. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: HP-7 combination design not validated. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d trials=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, TRIALS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r)
    print("  [seed=%d] A1=%.2f A2_K=%.1f A3=+%.1fpp A4=%.1f%%" % (seed, r["A1_betastar_recovery_ratio"], r["A2_transition_K"], r["A3_gain_pp"], r["A4_resonator_disagree"] * 100), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N_DIM, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
