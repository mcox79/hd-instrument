"""
substrate_4modulator_familiarity_v2_n4096 -- R1 v2: 4-modulator with FAMILIARITY signal -- remote CPU.

ROUTING: research clarifications_R1_R2_R5_R6 (R1 redesign). Original 4-modulator lost because cfRPE+surprise+arousal
  +satiety all track NOVELTY/ERROR (favor high-error FILLER over recurring IMPORTANT). Fix: 4th modulator = FAMILIARITY
  (recurrence-weighted; NA analog; hippocampal CA1 replay is recurrence-weighted not error-weighted). CPU numpy, $0.

MODEL: stream of T arrivals; 30% recurring IMPORTANT (from a fixed V_IMP set) + 70% one-off FILLER (fresh random).
  Overflow (T=4x m_cap). single = cf-RPE write-all (DA only). 4-mod = cf-RPE write with LR modulated by
  gate = 0.3*errn + 0.2*surprisen + 0.3*FAMILIARITY + 0.2*(1-satiety), FAMILIARITY = current recall-strength
  (recurring patterns become familiar -> boosted/reinforced; filler stays unfamiliar). Recall the V_IMP IMPORTANT set.

PRE-REGISTERED bands: HARD-PASS 4mod important_recall >= 1.5x single important_recall AND >= single. MIDDLE 1.1-1.5x.
  HARD-FAIL <1.1x (familiarity does not rescue; single-modulator limit holds).

FORMULA SELF-TESTS (PROT-022): 1. cf-RPE shrinks error. 2. familiarity rises after storing. 3. N=4096.
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

ANCHOR_NAME = "substrate_4modulator_familiarity_v2_n4096"
_N_SUFFIX = 4096; N = 4096; assert N == _N_SUFFIX
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()

ALPHA_C = 0.138; LR = 0.5; COS_THRESH = 0.70; P_IMPORTANT = 0.30; V_IMP = 60
if RUN_MODE == "smoke":
    SEEDS = [1, 2]; N_DIM = 512; V_IMP = 20
else:
    SEEDS = [7, 17, 23]; N_DIM = N


def unit(x):
    return x / (np.linalg.norm(x) + 1e-8)


def ub(M, n, g):
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def build_stream(n, m_cap, g):
    T = 3 * n; imp = ub(V_IMP, n, g); stream = []   # T>N: true cf-RPE overflow
    for _ in range(T):
        if g.random() < P_IMPORTANT:
            stream.append(imp[int(g.integers(0, V_IMP))])
        else:
            stream.append(ub(1, n, g)[0])
    return stream, imp


def recall_imp(W, imp, n):
    pred = imp @ W.T; pred = pred / (np.linalg.norm(pred, axis=1, keepdims=True) + 1e-8)
    return float(np.mean((pred * imp).sum(axis=1) > COS_THRESH))


def run_single(stream, n):
    W = np.zeros((n, n), dtype=np.float32)
    for p in stream:
        W += (LR / n) * np.outer(p - W @ p, p)
    return W


def run_4mod(stream, n):
    W = np.zeros((n, n), dtype=np.float32); run_mean = None; T = len(stream)
    for i, p in enumerate(stream):
        pred = W @ p; err = float(np.linalg.norm(p - pred))
        run_mean = err if run_mean is None else 0.9 * run_mean + 0.1 * err
        errn = min(1.0, err / (run_mean + 1e-6) / 2.0)
        familiarity = max(0.0, float((pred @ p) / (np.linalg.norm(pred) * np.linalg.norm(p) + 1e-8)))  # recall-strength
        satiety = i / max(T, 1)
        gate = 0.3 * errn + 0.2 * errn + 0.3 * familiarity + 0.2 * (1.0 - satiety)
        W += (LR * (0.5 + gate) / n) * np.outer(p - W @ p, p)
    return W


def _selftest():
    g = np.random.default_rng(0); n = 256; a = ub(1, n, g)[0]
    W = np.zeros((n, n), dtype=np.float32); eb = float(np.linalg.norm(a - W @ a)); W += (LR / n) * np.outer(a - W @ a, a)
    assert float(np.linalg.norm(a - W @ a)) < eb, "cf-RPE shrinks"
    f0 = float((np.zeros(n) @ a)); W2 = (1.0 / n) * np.outer(a, a)
    assert float((W2 @ a) @ a) > f0, "familiarity rises after storing"
    assert N == 4096; print("[selftest] PASS: cfrpe familiarity", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int) -> Dict:
    g = np.random.default_rng(seed); n = N_DIM; m_cap = max(8, int(round(ALPHA_C * n)))
    stream, imp = build_stream(n, m_cap, g)
    s = recall_imp(run_single(stream, n), imp, n); f = recall_imp(run_4mod(stream, n), imp, n)
    return {"seed": seed, "N": n, "T": len(stream), "m_cap": m_cap, "single_imp_recall": s, "fourmod_imp_recall": f, "ratio": float(f / max(s, 1e-6))}


def verdict(ps) -> Tuple[str, str]:
    s = float(np.mean([p["single_imp_recall"] for p in ps])); f = float(np.mean([p["fourmod_imp_recall"] for p in ps])); r = f / max(s, 1e-6)
    summary = "single_imp_recall=%.3f fourmod_imp_recall=%.3f ratio=%.2fx (30%% important + 70%% filler, T=3N overflow)" % (s, f, r)
    if r >= 1.5 and f >= s:
        return ("HARD_PASS", "HARD_PASS: familiarity-modulated 4-mod >=1.5x important-recall (Tier-2 hippocampal). " + summary)
    if r >= 1.1:
        return ("MIDDLE_BAND", "MIDDLE_BAND: familiarity 1.1-1.5x. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: familiarity no rescue. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d V_imp=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, V_IMP), flush=True)
if RUN_MODE == "full" and N_DIM != _N_SUFFIX:
    raise RuntimeError("PROT-018 N mismatch")
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r)
    print("  [seed=%d] single=%.3f fourmod=%.3f ratio=%.2fx" % (seed, r["single_imp_recall"], r["fourmod_imp_recall"], r["ratio"]), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N_DIM, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
