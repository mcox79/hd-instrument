"""
exp_substrate_embedding_norm_gate_discriminability_v1 -- Slot 6 / T1-4: norm-gated sparse extraction VQ coverage -- CPU.

ROUTING: PRIORITY_QUEUE_LIVE Slot 6 (sparse-activation extraction drill). To skip low-information tokens during
  extraction (20-47x speedup claim), gate tokens by embedding L2-norm and keep only the top g=30%. This validates that
  the kept high-norm tokens still COVER the concept space: VQ the full token set (k-means -> V_c codes), then check what
  fraction of codes are still represented in the top-30%-norm subset. Uses the already-shipped Llama-1B residual npz
  (no model load). CPU numpy + sklearn $0.

PRE-REGISTERED bands: HARD-PASS top-30%-norm gate preserves >= 0.97 VQ coverage. MIDDLE: 0.90-0.97. HARD-FAIL: < 0.90
  (norm-gating drops concepts -> not safe for sparse extraction).
FORMULA SELF-TESTS (PROT-022): 1. norm gate selects top-g. 2. coverage computation. 3. npz path.
ASCII-only. write_metrics. PROT-018: _v1.
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
REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "substrate_embedding_norm_gate_discriminability_v1"
NPZ = REPO / "data" / "exp_phase05_v1_llama32_1b_per_token_residual_extract_v1" / "residuals_per_token.npz"
GATE = 0.30
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N_TOK = 5000; VC_GRID = [64, 256]
else:
    SEEDS = [7, 17, 23]; N_TOK = 40000; VC_GRID = [256, 1024, 4096]


def coverage(codes, keep_mask, vc):
    used = set(np.unique(codes).tolist())
    kept = set(np.unique(codes[keep_mask]).tolist())
    return len(kept) / max(len(used), 1)


def _selftest():
    norms = np.array([0.1, 0.9, 0.5, 0.8, 0.2], np.float32)
    thr = np.quantile(norms, 1 - 0.4); mask = norms >= thr
    assert mask.sum() == 2 and mask[1] and mask[3], "norm gate selects top-g"
    codes = np.array([0, 1, 2, 0, 1]); assert abs(coverage(codes, np.array([True, True, False, False, False]), 3) - 2 / 3) < 1e-6, "coverage computation"
    print("[selftest] PASS: gate coverage", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
if not NPZ.exists():
    print("[FATAL] Llama-1B residual npz not found at %s" % NPZ, flush=True); sys.exit(1)
try:
    from sklearn.cluster import MiniBatchKMeans
except Exception as e:
    print("[FATAL] sklearn missing: %s" % e, flush=True); sys.exit(1)


def run_seed(seed) -> Dict:
    g = np.random.default_rng(seed)
    d = np.load(NPZ); R = d["residuals"]
    idx = g.choice(R.shape[0], size=min(N_TOK, R.shape[0]), replace=False)
    X = R[idx].astype(np.float32)
    norms = np.linalg.norm(X, axis=1)
    thr = np.quantile(norms, 1 - GATE); keep = norms >= thr           # top-GATE by norm
    Xn = X / (norms[:, None] + 1e-8)                                   # unit-normalize for VQ (direction = concept)
    cov = {}
    for vc in VC_GRID:
        k = min(vc, X.shape[0] // 4)
        km = MiniBatchKMeans(n_clusters=k, random_state=seed, n_init=3, batch_size=512).fit(Xn)
        codes = km.labels_
        cov["vc%d" % vc] = coverage(codes, keep, vc)
    return {"seed": seed, "n_tok": len(idx), "kept_frac": float(keep.mean()), "coverage_by_vc": cov,
            "min_coverage": float(min(cov.values()))}


def verdict(ps) -> Tuple[str, str]:
    mc = float(np.mean([p["min_coverage"] for p in ps]))
    allcov = {k: float(np.mean([p["coverage_by_vc"][k] for p in ps])) for k in ps[0]["coverage_by_vc"]}
    summary = "min_coverage=%.4f (top-%.0f%% norm gate) | by_vc=%s kept_frac=%.2f" % (mc, GATE * 100, {k: round(v, 4) for k, v in allcov.items()}, float(np.mean([p["kept_frac"] for p in ps])))
    if mc >= 0.97:
        return ("HARD_PASS", "HARD_PASS: top-30%% norm gate preserves >=0.97 VQ coverage -- sparse norm-gated extraction is concept-safe. " + summary)
    if mc >= 0.90:
        return ("MIDDLE_BAND", "MIDDLE_BAND: norm gate preserves 0.90-0.97 coverage. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: norm gate drops concepts (<0.90 coverage). " + summary)


print("[config] anchor=%s mode=%s seeds=%s N_tok=%d gate=%.2f vc=%s" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_TOK, GATE, VC_GRID), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r)
    print("  [seed=%d] min_coverage=%.4f kept_frac=%.2f by_vc=%s" % (seed, r["min_coverage"], r["kept_frac"], {k: round(v, 4) for k, v in r["coverage_by_vc"].items()}), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
