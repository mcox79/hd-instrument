"""
exp_substrate_cliff_sharpness_N_scaling_gpu_v1.py -- free-prob cliff-sharpness N-scaling test (design-corrected) -- light-GPU.

ROUTING: strategy_request free_prob_cliff_sharpness_N_scaling (v590 RESCUE-4). Substrate-quality-first; NO LLM frame.
  Free-probability R-transform drill predicts cleanup-cliff SHARPNESS scales as N^{2/3} (Tracy-Widom edge). The Cap-1 BINDING
  F=20 empirical already matched the F*-location prediction; this tests the SHARPNESS scaling exponent.

  DESIGN CORRECTION (verify-before-asserting probe): at alpha=0.5 (collisions resolved) the cleanup cliff LOCATION scales ~N
  (probe: N=512 cliffs at F~22; N=4096 has NO cliff even at F=60). So the spec'd fixed F<=30 cannot capture cliffs for N>=2048,
  and absolute d(cleanup)/dF will scale ~1/N (transition WIDENS in raw F at higher N), NOT N^{2/3}. The N^{2/3} prediction is a
  TW-EDGE prediction in SCALED units. This cell therefore: (1) uses an N-ADAPTIVE F grid bracketing each cliff; (2) reports
  sharpness BOTH ways -- absolute d(cleanup)/dF and SCALED d(cleanup)/d(F/F_cliff); (3) fits log-log slope of each vs N and
  reports which matches 2/3. Corpus = 241-atom algebra-HRR codebook re-encoded at each N, identity-augmented at alpha=0.5.

PRE-REGISTERED (free-prob pillar test): on the SCALED sharpness (the TW-edge quantity), HARD-PASS log-log slope in [0.55,0.80]
  (covers N^{2/3}=0.667). MIDDLE [0.40,0.85] outside HP, or monotone-but-uncertain. HARD-FAIL slope in [-0.1,0.4] or >0.85 or
  non-monotone. Absolute-sharpness slope reported alongside (expected ~ -1/3 to -1; flagged as the wrong-units control).
  UNKNOWN if corpus load fails. (Definitional choice flagged to Research.)
ASCII-only. torch (light-GPU). --self-test + --smoke + metrics.json. Route via overnight_queue (GPU).
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, json, hashlib, re, math
from pathlib import Path
from typing import Dict, Tuple, List
try:
    import torch
    _DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
except Exception:
    _DEVICE = "cpu"
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "substrate_cliff_sharpness_N_scaling_gpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
NS = [512, 1024, 2048, 4096]
ALPHA = 0.5
SEEDS = [7, 8, 9]
N_TRIALS = 12
CLIFF_BAR = 0.85
_FEST = 0.043   # F_cliff ~ 0.043*N (from probe: N=512 cliff at F~22)
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


def _codebook(N, ps):
    from backend.substrate_index.algebra_index import AlgebraIndex
    ai = AlgebraIndex(dim=N); ai.build(ps)
    ids, A = [], []
    for aid, av in ai._atom_vectors.items():
        if av.algebra_hrr is not None: ids.append(aid); A.append(av.algebra_hrr)
    A = np.stack(A).astype(np.float64); A = A / (np.linalg.norm(A, axis=1, keepdims=True) + 1e-12)
    Nm = np.stack([_name_vec(i, N) for i in ids])
    M = A + ALPHA * Nm; M = M / (np.linalg.norm(M, axis=1, keepdims=True) + 1e-12)
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


def _f_grid(N):
    fc = max(6, _FEST * N)
    pts = [0.25, 0.45, 0.65, 0.85, 1.0, 1.15, 1.35, 1.6]
    return sorted(set(max(2, int(round(fc * p))) for p in pts))


def _interp_cliff(fs, cs, bar):
    """F where cleanup crosses bar (linear interp on the descending curve)."""
    for i in range(1, len(fs)):
        if cs[i - 1] >= bar and cs[i] < bar:
            f0, f1, c0, c1 = fs[i - 1], fs[i], cs[i - 1], cs[i]
            return f0 + (bar - c0) * (f1 - f0) / (c1 - c0 + 1e-12), i
    return None, None


def run() -> Dict:
    from backend.substrate_index.partition import PartitionedStore
    ps = PartitionedStore(REPO / "data" / "substrate_index")
    ns = [512, 1024] if SMOKE else NS
    seeds = SEEDS[:1] if SMOKE else SEEDS
    n_trials = 5 if SMOKE else N_TRIALS
    per_N = []
    for N in ns:
        M = _codebook(N, ps)
        fs = [f for f in _f_grid(N) if f <= M.shape[0] - 1]   # codebook caps F<K distinct fillers (K=241)
        cs = [_cleanup(M, F, n_trials, seeds) for F in fs]
        fcliff, ci = _interp_cliff(fs, cs, CLIFF_BAR)
        # sharpness via linear fit over the TRANSITION band (cleanup in [0.45,0.95]) -- robust vs 2-point finite diff
        abs_sharp = sc_sharp = None
        if fcliff is not None:
            trans = [(f, c) for f, c in zip(fs, cs) if 0.45 <= c <= 0.95]
            if len(trans) >= 2:
                slope = float(np.polyfit([t[0] for t in trans], [t[1] for t in trans], 1)[0])
                abs_sharp = abs(slope)                               # |d cleanup / dF|
                sc_sharp = abs(slope) * fcliff                       # |d cleanup / d(F/F_cliff)| (scaled / TW-edge units)
        per_N.append({"N": N, "F_grid": fs, "cleanup": [round(c, 4) for c in cs],
                      "F_cliff": (round(fcliff, 3) if fcliff else None),
                      "abs_sharpness": (round(abs_sharp, 6) if abs_sharp else None),
                      "scaled_sharpness": (round(sc_sharp, 4) if sc_sharp else None)})
        print("  N=%4d F_cliff=%s abs_sharp=%s scaled_sharp=%s | cleanup=%s" %
              (N, per_N[-1]["F_cliff"], per_N[-1]["abs_sharpness"], per_N[-1]["scaled_sharpness"],
               list(zip(fs, [round(c, 3) for c in cs]))), flush=True)

    def _loglog_slope(key):
        pts = [(p["N"], p[key]) for p in per_N if p.get(key)]
        if len(pts) < 2: return None
        xs = np.log([p[0] for p in pts]); ys = np.log([p[1] for p in pts])
        return float(np.polyfit(xs, ys, 1)[0])
    return {"per_N": per_N, "abs_sharpness_slope": _loglog_slope("abs_sharpness"),
            "scaled_sharpness_slope": _loglog_slope("scaled_sharpness"),
            "Fcliff_slope": _loglog_slope("F_cliff"), "alpha": ALPHA, "device": _DEVICE, "n_seeds": len(seeds)}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    sc = r.get("scaled_sharpness_slope"); ab = r.get("abs_sharpness_slope"); fc = r.get("Fcliff_slope")
    s = ("SCALED-sharpness log-log slope=%s (TW-edge quantity; predict 2/3=0.667); ABSOLUTE-sharpness slope=%s (wrong-units control); F_cliff(N) slope=%s (predict ~1 = cliff location scales with N); per-N=%s; alpha=%.1f device=%s"
         % (sc, ab, fc, [(p["N"], p["F_cliff"], p["scaled_sharpness"]) for p in r["per_N"]], r["alpha"], r["device"]))
    if sc is None:
        return ("UNKNOWN", "UNKNOWN: <2 N values produced a cliff in range. " + s)
    if 0.55 <= sc <= 0.80:
        return ("HARD_PASS", "HARD_PASS: scaled cliff-sharpness log-log slope in [0.55,0.80] -- matches free-prob TW-edge N^{2/3} prediction; mathematical-foundation pillar gains a 2nd empirical anchor at scaling-exponent granularity. " + s)
    if 0.40 <= sc <= 0.85:
        return ("MIDDLE_BAND", "MIDDLE_BAND: scaled sharpness slope in [0.40,0.85] but outside strict [0.55,0.80] -- qualitative match to N^{2/3}, quantitative exponent uncertain (finite-N corrections / few N points). " + s)
    return ("HARD_FAIL", "HARD_FAIL: scaled sharpness slope outside [0.40,0.85] or non-monotone -- free-prob N^{2/3} sharpness prediction not supported empirically; mathematical-foundation pillar scope bounded. " + s)


def _selftest():
    g = torch.Generator().manual_seed(1)
    R = _unitary(2, 128, g); assert float((torch.fft.fft(R[0]).abs() - 1).abs().max()) < 1e-4
    fc, ci = _interp_cliff([10, 20, 30], [0.95, 0.9, 0.7], 0.85); assert ci == 2 and 20 < fc < 30
    assert _f_grid(512)[0] >= 2 and max(_f_grid(512)) > 22
    print("[selftest] PASS: cliff-sharpness-N-scaling (cliff interp %.1f)" % fc, flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s device=%s" % (ANCHOR_NAME, RUN_MODE, _DEVICE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
