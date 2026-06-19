"""
substrate_kmax_depth_scaling_formula_validation_v1_n4096_alpha_sweep -- NEW EXP 1: depth-scaling formula -- remote CPU.

ROUTING: research_to_exp_dev_3_drill_synthesis_priority_experiments (NEW EXP 1). Drill 3 predicts reasoning depth
  K_max = 3.3 * (1 - alpha/alpha_c)^2 / alpha (alpha = load = transitions/N; alpha_c=0.138). Empirical K=12 at
  alpha=0.5*alpha_c matched. Validate the formula across an alpha sweep -> precise capacity-vs-depth production knob.
  CPU numpy, $0. remote_cpu_queue.

MODEL: single substrate N=4096; chains of bipolar concept transitions stored Hebbian; iterated retrieval
  q=sign(W@q); K_max = deepest K with >=80% chain accuracy. Sweep load_frac=alpha/alpha_c in {0.1..1.0}.
  predicted_K = 3.3*(1-load_frac)^2/(load_frac*alpha_c). Compare empirical vs predicted (cap measured K at K_CAP).

PRE-REGISTERED bands: HARD-PASS empirical K_max within 25% of predicted across the sweep (median rel-err<=0.25).
  MIDDLE: within 50%. HARD-FAIL: >50% off (deeper formula needed; e.g., NESS dynamics not in derivation).
  NOTE measured K capped at K_CAP; cells where predicted>K_CAP are lower-bound (excluded from rel-err if censored).

FORMULA SELF-TESTS (PROT-022): 1. chain 2-hop. 2. formula = 12 at load_frac=0.5. 3. N=4096.
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

ANCHOR_NAME = "substrate_kmax_depth_scaling_formula_validation_v1_n4096_alpha_sweep"
_N_SUFFIX = 4096; N = 4096; assert N == _N_SUFFIX
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()

ALPHA_C = 0.138; K_CAP = 50; N_PROBES = 5
LOAD_FRACS = [0.1, 0.2, 0.3, 0.5, 0.7, 0.9, 1.0]
if RUN_MODE == "smoke":
    SEEDS = [1]; N_DIM = 1024; LOAD_FRACS = [0.3, 0.5, 0.9]; K_CAP = 24; N_PROBES = 3
else:
    SEEDS = [7, 17, 23]; N_DIM = N


def bipolar(shape, g):
    return (g.integers(0, 2, size=shape) * 2 - 1).astype(np.float32)


def predicted_kmax(load_frac):
    return 3.3 * (1.0 - load_frac) ** 2 / (load_frac * ALPHA_C)


def empirical_kmax(n, load_frac, g):
    # separate background LOAD (M random transitions) from probe-chain DEPTH (one long chain)
    M_bg = max(0, int(round(load_frac * ALPHA_C * n)))                        # background load = M/N
    W = np.zeros((n, n), dtype=np.float32)
    if M_bg:                                                                  # M random independent a->b transitions
        A = bipolar((M_bg, n), g); B = bipolar((M_bg, n), g); W += B.T @ A
    probes = [bipolar((K_CAP + 1, n), g) for _ in range(N_PROBES)]            # probe chains
    for ch in probes:
        for i in range(K_CAP):
            W += np.outer(ch[i + 1], ch[i])
    best = 0
    for K in range(1, K_CAP + 1):
        hits = 0
        for ch in probes:
            q = ch[0].copy()
            for _ in range(K):
                q = np.sign(W @ q); q[q == 0] = 1.0
            hits += (float((q * ch[K]).sum() / n) > 0.90)
        if hits / len(probes) >= 0.80:
            best = K
        else:
            break
    return best, K_CAP


def _selftest():
    g = np.random.default_rng(0); n = 256; ch = bipolar((5, n), g); W = np.zeros((n, n), dtype=np.float32)
    for i in range(4):
        W += np.outer(ch[i + 1], ch[i])
    assert float((np.sign(W @ np.sign(W @ ch[0])) * ch[2]).sum() / n) > 0.9, "2-hop"
    assert abs(predicted_kmax(0.5) - 11.96) < 0.5, "formula=12 at load_frac 0.5"
    assert N == 4096; print("[selftest] PASS: 2hop formula_anchor", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int) -> Dict:
    g = np.random.default_rng(seed); rows = {}
    for lf in LOAD_FRACS:
        emp, Lcap = empirical_kmax(N_DIM, lf, np.random.default_rng(seed * 100 + int(lf * 100)))
        pred = predicted_kmax(lf)
        rows["lf%.1f" % lf] = {"predicted": float(pred), "empirical": int(emp), "censored": bool(pred > Lcap)}
    return {"seed": seed, "N": N_DIM, **rows}


def verdict(ps) -> Tuple[str, str]:
    rel_errs = []; parts = []
    for lf in LOAD_FRACS:
        pr = float(np.mean([p["lf%.1f" % lf]["predicted"] for p in ps]))
        em = float(np.mean([p["lf%.1f" % lf]["empirical"] for p in ps]))
        cens = any(p["lf%.1f" % lf]["censored"] for p in ps)
        parts.append("lf%.1f:pred=%.0f emp=%.0f%s" % (lf, pr, em, "*" if cens else ""))
        if not cens:
            rel_errs.append(abs(em - pr) / max(pr, 1e-6))
    med = float(np.median(rel_errs)) if rel_errs else 1.0
    summary = "median_rel_err=%.2f | " % med + " ".join(parts) + " (*=censored at K_CAP)"
    if med <= 0.25:
        return ("HARD_PASS", "HARD_PASS: K_max formula validated within 25%. " + summary)
    if med <= 0.50:
        return ("MIDDLE_BAND", "MIDDLE_BAND: formula within 50%. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: formula off >50% (deeper model needed). " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d loads=%s" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, LOAD_FRACS), flush=True)
if RUN_MODE == "full" and N_DIM != _N_SUFFIX:
    raise RuntimeError("PROT-018 N mismatch")
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r)
    print("  [seed=%d] " % seed + " ".join("lf%.1f:p%.0f/e%d" % (lf, r["lf%.1f" % lf]["predicted"], r["lf%.1f" % lf]["empirical"]) for lf in LOAD_FRACS), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N_DIM, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
