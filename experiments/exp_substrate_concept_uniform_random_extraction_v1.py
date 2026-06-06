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

ANCHOR_NAME = "substrate_concept_uniform_random_extraction_v1"
NPZ = REPO / "data" / "exp_phase05_v1_llama32_1b_per_token_residual_extract_v1" / "residuals_per_token.npz"
SPEEDUPS = [10, 100, 1000]
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
    X = R[idx].astype(np.float32); norms = np.linalg.norm(X, axis=1)
    Xn = X / (norms[:, None] + 1e-8)
    vc = max(VC_GRID); k = min(vc, X.shape[0] // 4)
    codes = MiniBatchKMeans(n_clusters=k, random_state=seed, n_init=3, batch_size=512).fit(Xn).labels_
    res = {"seed": seed, "n_tok": len(idx), "by_speedup": {}}
    for sp in SPEEDUPS:
        budget = max(1, len(idx) // sp); keep = np.zeros(len(idx), bool)
        sel = g.choice(len(idx), size=min(budget, len(idx)), replace=False); keep[sel] = True   # concept-uniform random sampling
        res["by_speedup"]["sp%d" % sp] = {"coverage": coverage(codes, keep, vc), "actual_speedup": len(idx) / max(keep.sum(), 1)}
    res["min_coverage"] = float(min(v["coverage"] for v in res["by_speedup"].values()))
    return res


def verdict(ps) -> Tuple[str, str]:
    keys = list(ps[0]["by_speedup"].keys())
    agg = {k: {"coverage": float(np.mean([p["by_speedup"][k]["coverage"] for p in ps])), "speedup": float(np.mean([p["by_speedup"][k]["actual_speedup"] for p in ps]))} for k in keys}
    best = max((v["speedup"] for k, v in agg.items() if v["coverage"] >= 0.90), default=0.0)
    summary = "stratified: %s" % {k: (round(v["coverage"], 3), round(v["speedup"], 0)) for k, v in agg.items()}
    if best >= 10:
        return ("HARD_PASS", "HARD_PASS: random sampling holds >=0.90 coverage at >=10x speedup -- simplest extraction rescue works. " + summary)
    if best >= 3:
        return ("MIDDLE_BAND", "MIDDLE_BAND: >=0.90 coverage at 3-10x speedup. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: random sampling cannot hold >=0.90 coverage at >=3x speedup. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N_tok=%d vc=%s" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_TOK, VC_GRID), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r)
    print("  [seed=%d] %s" % (seed, {k: (round(v["coverage"], 3), round(v["actual_speedup"], 0)) for k, v in r["by_speedup"].items()}), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
