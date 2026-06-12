"""
exp_substrate_cliff_sharpness_alpha_sweep_gpu_v1.py -- cliff-sharpness ALPHA-sweep at fixed N=1024 (bulk-regime 2nd-appearance) -- light-GPU.

ROUTING: strategy_request cliff_sharpness_alpha_sweep_bulk_regime (v592 RESCUE-3). Substrate-quality-first; NO LLM frame.
  PP-413 showed (at alpha=0.5, N-sweep) the cleanup cliff is BULK MEAN-FIELD not Tracy-Widom edge: F_cliff ~ N (slope 0.99),
  scaled sharpness N-invariant (~0.28). This drill tests whether the bulk regime holds ACROSS alpha (fixed N=1024): if scaled
  sharpness stays ~0.28 across alpha -> bulk-rule 2nd appearance; if it grows with alpha -> crossover toward edge regime.

  Fixed N=1024; alpha in {0.0,0.25,0.5,0.75,1.0}; identity-augmented 241-atom codebook (algebra_hrr + alpha*name_token_hrr)
  re-normalized per alpha; wide F-grid bracketing the cliff for all alpha (cliff location grows with alpha as collisions
  resolve); 3 seeds. Per alpha: F_cliff (cleanup@1<0.85 interp), abs & SCALED sharpness (transition-band linear fit).

PRE-REGISTERED (v592):
  HARD-PASS (bulk-rule 2nd-appearance): scaled_sharpness within +/-0.10 of 0.28 across ALL alpha AND F_cliff(alpha) monotone.
  MIDDLE: scaled_sharpness alpha-dependent but stays in [0.20,0.40].
  HARD-FAIL (edge crossover): scaled_sharpness scales with alpha (|log-log or linear slope| large; leaves [0.20,0.40]).
  UNKNOWN if corpus load fails.
ASCII-only. torch (light-GPU). --self-test + --smoke + metrics.json. Route via overnight_queue (GPU).
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, json, hashlib, re
from pathlib import Path
from typing import Dict, Tuple
try:
    import torch
    _DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
except Exception:
    _DEVICE = "cpu"
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "substrate_cliff_sharpness_alpha_sweep_gpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 1024
ALPHAS = [0.0, 0.25, 0.5, 0.75, 1.0]
F_GRID = [8, 12, 16, 20, 26, 33, 41, 51, 64, 80, 100]   # wide: brackets cliff for all alpha at N=1024
SEEDS = [7, 8, 9]
N_TRIALS = 14
CLIFF_BAR = 0.85
_TOK = re.compile(r"[a-z0-9]+")


def _tok_vec(t, dim):
    h = int(hashlib.sha256(("nametok::" + t).encode()).hexdigest(), 16); rng = np.random.default_rng(h % (2 ** 63 - 1))
    v = rng.standard_normal(dim); return v / (np.linalg.norm(v) + 1e-12)


def _name_vec(aid, dim):
    toks = _TOK.findall(aid.lower())
    if not toks: return np.zeros(dim)
    s = np.sum([_tok_vec(t, dim) for t in toks], axis=0); n = np.linalg.norm(s); return s / n if n > 0 else s


def _unitary(n, dim, g):
    v = torch.randn(n, dim, generator=g); fv = torch.fft.fft(v); fv = fv / (fv.abs() + 1e-12)
    return torch.fft.ifft(fv).real.contiguous()


def _load_AN(ps):
    from backend.substrate_index.algebra_index import AlgebraIndex
    ai = AlgebraIndex(dim=N); ai.build(ps)
    ids, A = [], []
    for aid, av in ai._atom_vectors.items():
        if av.algebra_hrr is not None: ids.append(aid); A.append(av.algebra_hrr)
    A = np.stack(A).astype(np.float64); A = A / (np.linalg.norm(A, axis=1, keepdims=True) + 1e-12)
    Nm = np.stack([_name_vec(i, N) for i in ids])
    return A, Nm


def _codebook(A, Nm, alpha):
    M = A + alpha * Nm; M = M / (np.linalg.norm(M, axis=1, keepdims=True) + 1e-12)
    return torch.tensor(M, dtype=torch.float32, device=_DEVICE)


def _cleanup(M, F, n_trials, seeds):
    from hdlab.binding import bind, unbind
    from hdlab.bundling import bundle
    Mt = M.t().contiguous(); Mn = M.shape[0]; dim = M.shape[1]; hit = 0; cnt = 0
    for sd in seeds:
        g = torch.Generator().manual_seed(sd * 1000 + F)
        for _ in range(n_trials):
            idx = torch.randperm(Mn, generator=g)[:F]; R = _unitary(F, dim, g).to(M.device)
            Ab = bundle(torch.stack([bind(R[i], M[idx[i]]) for i in range(F)]))
            for j in range(F):
                est = unbind(Ab, R[j]); est = est / (est.norm() + 1e-12)
                hit += int(int(torch.argmax(est @ Mt)) == int(idx[j])); cnt += 1
    return hit / cnt if cnt else 0.0


def _interp_cliff(fs, cs, bar):
    for i in range(1, len(fs)):
        if cs[i - 1] >= bar and cs[i] < bar:
            f0, f1, c0, c1 = fs[i - 1], fs[i], cs[i - 1], cs[i]
            return f0 + (bar - c0) * (f1 - f0) / (c1 - c0 + 1e-12)
    return None


def run() -> Dict:
    from backend.substrate_index.partition import PartitionedStore
    ps = PartitionedStore(REPO / "data" / "substrate_index")
    A, Nm = _load_AN(ps)
    Mn = A.shape[0]
    alphas = [0.0, 0.5] if SMOKE else ALPHAS
    fs_all = [f for f in ([12, 26, 51] if SMOKE else F_GRID) if f <= Mn - 1]
    seeds = SEEDS[:1] if SMOKE else SEEDS
    n_trials = 5 if SMOKE else N_TRIALS
    per_a = []
    for alpha in alphas:
        M = _codebook(A, Nm, alpha)
        cs = [_cleanup(M, F, n_trials, seeds) for F in fs_all]
        fcliff = _interp_cliff(fs_all, cs, CLIFF_BAR)
        abs_s = sc_s = None
        if fcliff is not None:
            trans = [(f, c) for f, c in zip(fs_all, cs) if 0.45 <= c <= 0.95]
            if len(trans) >= 2:
                slope = float(np.polyfit([t[0] for t in trans], [t[1] for t in trans], 1)[0])
                abs_s = abs(slope); sc_s = abs(slope) * fcliff
        per_a.append({"alpha": alpha, "F_cliff": (round(fcliff, 3) if fcliff else None),
                      "abs_sharpness": (round(abs_s, 6) if abs_s else None),
                      "scaled_sharpness": (round(sc_s, 4) if sc_s else None),
                      "cleanup": [round(c, 4) for c in cs]})
        print("  alpha=%.2f F_cliff=%s scaled_sharp=%s abs_sharp=%s" %
              (alpha, per_a[-1]["F_cliff"], per_a[-1]["scaled_sharpness"], per_a[-1]["abs_sharpness"]), flush=True)
    scs = [p["scaled_sharpness"] for p in per_a if p["scaled_sharpness"] is not None]
    fcs = [p["F_cliff"] for p in per_a if p["F_cliff"] is not None]
    monotone = all(fcs[i] <= fcs[i + 1] + 1e-6 for i in range(len(fcs) - 1)) if len(fcs) >= 2 else None
    return {"per_alpha": per_a, "N": N, "F_grid": fs_all, "scaled_sharpness_values": scs,
            "Fcliff_monotone": monotone, "device": _DEVICE, "n_seeds": len(seeds)}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    scs = r.get("scaled_sharpness_values", [])
    s = ("scaled_sharpness across alpha=%s (predict ~0.28 flat for bulk); F_cliff monotone=%s; per-alpha=%s; N=%d device=%s" %
         (scs, r.get("Fcliff_monotone"), [(p["alpha"], p["F_cliff"], p["scaled_sharpness"]) for p in r["per_alpha"]], r["N"], r["device"]))
    if len(scs) < 2:
        return ("UNKNOWN", "UNKNOWN: <2 alpha produced a cliff in range. " + s)
    lo, hi = min(scs), max(scs)
    within_010 = all(abs(x - 0.28) <= 0.10 for x in scs)
    if within_010 and r.get("Fcliff_monotone"):
        return ("HARD_PASS", "HARD_PASS (bulk-rule 2nd appearance): scaled cliff-sharpness stays within +/-0.10 of 0.28 across ALL alpha (%.3f-%.3f) with monotone F_cliff(alpha) -- the cleanup cliff is bulk mean-field across alpha, not just at alpha=0.5; no edge crossover. " % (lo, hi) + s)
    if 0.20 <= lo and hi <= 0.40:
        return ("MIDDLE_BAND", "MIDDLE_BAND: scaled sharpness alpha-dependent but stays in [0.20,0.40] (%.3f-%.3f) -- bulk regime mostly holds with mild alpha-dependence. " % (lo, hi) + s)
    return ("HARD_FAIL", "HARD_FAIL: scaled sharpness leaves [0.20,0.40] across alpha (%.3f-%.3f) -- alpha drives a crossover between bulk and edge regimes; bulk-rule does not generalize across alpha. " % (lo, hi) + s)


def _selftest():
    g = torch.Generator().manual_seed(1)
    R = _unitary(2, 128, g); assert float((torch.fft.fft(R[0]).abs() - 1).abs().max()) < 1e-4
    assert _interp_cliff([10, 20, 30], [0.95, 0.9, 0.7], 0.85) is not None
    assert abs(np.dot(_name_vec("a/b", 64), _name_vec("a/b", 64)) - 1.0) < 1e-6
    print("[selftest] PASS: cliff-sharpness-alpha-sweep", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s device=%s" % (ANCHOR_NAME, RUN_MODE, _DEVICE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
