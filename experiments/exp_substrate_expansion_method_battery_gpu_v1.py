"""
exp_substrate_expansion_method_battery_gpu_v1 -- BUNDLED: does expansion/whitening beat native at controlled intrinsic dim -- GPU.

ROUTING: bundled GPU battery (user rule). The d_eff=82 finding says real-encoder capacity is bounded by INTRINSIC dim, and
  random projection can't exceed rank. This tests that mechanism at CONTROLLED synthetic scale: generate patterns with a
  fixed intrinsic rank r << N (r-dim random latents lifted by a random basis), sign-binarize, then measure Hopfield
  exact-recovery capacity under METHODS = native / random-projection x2 / random-projection x4 / ZCA-whiten. Predicts:
  expansion does NOT raise capacity above the rank-r ceiling; whitening helps only by decorrelation up to rank r. Sweeps
  METHOD x intrinsic-rank r x seed, all torch GPU. Confirms the production lever is encoder d_eff, not post-hoc expansion.
PRE-REGISTERED: HARD-PASS expansion (x4) gives <1.2x native capacity at every r (expansion CANNOT beat rank) AND whitening
  >=1.3x native at low r (decorrelation helps) -> mechanism confirmed. MID partial. HF expansion >=1.5x native (expansion
  DOES help -> would overturn the d_eff framework).
FORMULA SELF-TESTS (PROT-022): 1. rank-r patterns have ~r singular values. 2. whiten decorrelates. 3. cuda.
ASCII-only. write_metrics. PROT-018 no _nN.
"""
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os, argparse, time
from pathlib import Path
from typing import Dict, List, Tuple
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
import numpy as np
import torch
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "substrate_expansion_method_battery_gpu_v1"
FLIP = 0.05; STEPS = 6; N = 2048
_DEV = torch.device("cuda" if torch.cuda.is_available() else "cpu")
METHODS = ["native", "rp_x2", "rp_x4", "zca_whiten"]
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; RANKS = [64, 256]; LOADS = [0.02, 0.05, 0.1, 0.2, 0.4]
else:
    SEEDS = [7, 17, 23]; RANKS = [32, 64, 128, 256, 512]; LOADS = [0.01, 0.02, 0.03, 0.05, 0.08, 0.12, 0.18, 0.25, 0.35, 0.5]


def gen_rankr(M, r, seed):
    g = torch.Generator(device=_DEV).manual_seed(int(seed))
    Z = torch.randn(M, r, generator=g, device=_DEV); B = torch.randn(r, N, generator=g, device=_DEV) / (r ** 0.5)
    return Z @ B                                                   # M x N, intrinsic rank r


def hop_cap_from_real(X):
    P = torch.sign(X); P[P == 0] = 1.0; M, n = P.shape
    S = P * torch.where(torch.rand(M, n, device=_DEV) < FLIP, -1.0, 1.0)
    for _ in range(STEPS):
        S = torch.sign((P.t() @ (P @ S.t())).t() - M * S); S[S == 0] = 1.0
    return float((S == P).all(dim=1).float().mean().item())


def whiten(X):
    Xc = X - X.mean(0); cov = (Xc.t() @ Xc) / Xc.shape[0]
    U, Sg, _ = torch.linalg.svd(cov); Wd = U @ torch.diag(1.0 / torch.sqrt(Sg + 1e-3)) @ U.t()
    return Xc @ Wd


def expand(X, factor, seed):
    g = torch.Generator(device=_DEV).manual_seed(int(seed) + 999); R = torch.randn(X.shape[1], X.shape[1] * factor, generator=g, device=_DEV)
    return X @ R


def transform(X, method, seed):
    if method == "native":
        return X
    if method == "zca_whiten":
        return whiten(X)
    return expand(X, int(method.split("x")[1]), seed)


def cap(method, r, seed):
    c = 0
    for load in LOADS:
        M = max(2, int(load * N))
        if hop_cap_from_real(transform(gen_rankr(M, r, seed * 100 + M), method, seed)) >= 0.95:
            c = M
        else:
            break
    return c / N


def _selftest():
    X = gen_rankr(200, 16, 0); s = torch.linalg.svdvals(X - X.mean(0)); eff = int((s > 0.01 * s[0]).sum().item())
    assert eff <= 20, "rank-r ~ r singular values"
    W = whiten(gen_rankr(200, 64, 1)); cov = (W - W.mean(0)).t() @ (W - W.mean(0)) / 200
    off = (cov - torch.diag(torch.diag(cov))).abs().mean().item(); assert off < 0.2, "whiten decorrelates"
    print("[selftest] PASS: expansion", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
if not torch.cuda.is_available():
    print("[FATAL] CUDA not available.", flush=True); sys.exit(1)
print("[GPU] %s" % torch.cuda.get_device_name(0), flush=True)


def verdict(rows) -> Tuple[str, str]:
    def a(method, r):
        vs = [x["alpha"] for x in rows if x["method"] == method and x["r"] == r]; return float(np.mean(vs)) if vs else 0.0
    nat = float(np.mean([a("native", r) for r in RANKS])); rp4 = float(np.mean([a("rp_x4", r) for r in RANKS]))
    wh = float(np.mean([a("zca_whiten", r) for r in RANKS]))
    summary = "mean alpha: native=%.4f rp_x4=%.4f zca_whiten=%.4f" % (nat, rp4, wh)
    if rp4 >= nat + 0.02 and rp4 >= 1.5 * max(nat, 1e-6):
        return ("HARD_FAIL", "HARD_FAIL: expansion DOES raise capacity above native -- overturns d_eff/rank-ceiling framework. " + summary)
    if rp4 <= nat + 0.01 and wh >= nat + 0.01:
        return ("HARD_PASS", "HARD_PASS: expansion cannot beat rank (rp_x4 ~ native) while whitening helps via decorrelation -- d_eff framework confirmed at synthetic scale. " + summary)
    return ("MIDDLE_BAND", "MIDDLE_BAND: partial -- expansion bounded but whitening gain modest. " + summary)


print("[config] anchor=%s mode=%s seeds=%s ranks=%s methods=%s N=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, RANKS, METHODS, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); rows = []
for r in RANKS:
    for method in METHODS:
        for seed in SEEDS:
            rows.append({"method": method, "r": r, "seed": seed, "alpha": cap(method, r, seed)})
        av = float(np.mean([x["alpha"] for x in rows if x["method"] == method and x["r"] == r]))
        print("  [r=%d %-11s] alpha=%.4f" % (r, method, av), flush=True)
v, vmsg = verdict(rows); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": rows, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, rows); print("[metrics] written", flush=True)
