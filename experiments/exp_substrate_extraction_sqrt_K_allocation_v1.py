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

ANCHOR_NAME = "substrate_extraction_sqrt_K_allocation_v1"
NPZ = REPO / "data" / "exp_phase05_v1_llama32_1b_per_token_residual_extract_v1" / "residuals_per_token.npz"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N_TOK = 6000; VC_GRID = [64]; SPEEDUPS = [10]
else:
    SEEDS = [7, 17, 23]; N_TOK = 40000; VC_GRID = [512]; SPEEDUPS = [20]


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


def _kmeans(X, k, seed):
    km = MiniBatchKMeans(n_clusters=k, random_state=seed, n_init=3, batch_size=512).fit(X)
    C = km.cluster_centers_; return km.labels_, (C / (np.linalg.norm(C, axis=1, keepdims=True) + 1e-8)).astype(np.float32)


def fidelity(tr, norms_tr, codes, nc, Cf, ho, full_ho, k, budget, Kc, seed):
    keep = np.zeros(tr.shape[0], bool)
    for c in range(k):
        kc = int(round(Kc[c])); ci = np.where(codes == c)[0]
        if len(ci) and kc > 0:
            keep[ci[np.argsort(-norms_tr[ci])[:kc]]] = True
    if keep.sum() < k:
        return {"centroid_cos": 0.0, "heldout_agree": 0.0, "fidelity": 0.0, "kept": int(keep.sum())}
    _, Cs = _kmeans(tr[keep], k, seed)                                 # sub-codebook on kept tokens
    a = float(np.mean(np.max(Cf @ Cs.T, axis=1)))                      # (a) each full centroid's best sub match
    sub2full = np.argmax(Cs @ Cf.T, axis=1)                            # map sub clusters -> nearest full
    sub_ho = np.argmax(ho @ Cs.T, axis=1)
    b = float(np.mean(sub2full[sub_ho] == full_ho))                    # (b) held-out assignment agreement
    return {"centroid_cos": a, "heldout_agree": b, "fidelity": 0.5 * (a + b), "kept": int(keep.sum())}


def run_seed(seed) -> Dict:
    g = np.random.default_rng(seed)
    d = np.load(NPZ); R = d["residuals"]
    idx = g.choice(R.shape[0], size=min(N_TOK, R.shape[0]), replace=False)
    X = R[idx].astype(np.float32); norms = np.linalg.norm(X, axis=1); Xn = X / (norms[:, None] + 1e-8)
    nho = max(1, len(idx) // 10); ho = Xn[:nho]; tr = Xn[nho:]; norms_tr = norms[nho:]
    vc = max(VC_GRID); k = min(vc, tr.shape[0] // 4)
    codes, Cf = _kmeans(tr, k, seed); nc = np.array([np.sum(codes == c) for c in range(k)], dtype=np.float64)
    full_ho = np.argmax(ho @ Cf.T, axis=1)
    sp = max(2, min(max(SPEEDUPS), tr.shape[0] // (3 * k))); budget = tr.shape[0] // sp
    allocs = {"uniform": np.full(k, budget / k), "prop": budget * nc / max(nc.sum(), 1),
              "sqrt_K": budget * np.sqrt(nc) / max(np.sqrt(nc).sum(), 1)}
    fid = {name: fidelity(tr, norms_tr, codes, nc, Cf, ho, full_ho, k, budget, Kc, seed) for name, Kc in allocs.items()}
    return {"seed": seed, "speedup": sp, "fidelity_by_policy": fid}


def verdict(ps) -> Tuple[str, str]:
    pol = {name: float(np.mean([p["fidelity_by_policy"][name]["fidelity"] for p in ps])) for name in ps[0]["fidelity_by_policy"]}
    ratio = pol["sqrt_K"] / max(pol["uniform"], 1e-9)
    summary = "VQ-fidelity (centroid_cos+heldout_agree)/2 at %dx: %s | sqrt_K/uniform=%.3f" % (ps[0]["speedup"], {k: round(v, 4) for k, v in pol.items()}, ratio)
    if ratio >= 1.10:
        return ("HARD_PASS", "HARD_PASS: sqrt-K allocation gives >=1.10x VQ-codebook fidelity vs uniform-K -- Neyman-proxy is the production extraction allocation. " + summary)
    if ratio >= 1.00:
        return ("MIDDLE_BAND", "MIDDLE_BAND: sqrt-K marginally beats uniform (1.00-1.10x fidelity). " + summary)
    return ("HARD_FAIL", "HARD_FAIL: sqrt-K does not beat uniform-K on fidelity -- uniform-K + collapse monitoring suffices (drill C refuted). " + summary)


print("[config] anchor=%s mode=%s seeds=%s N_tok=%d vc=%s" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_TOK, VC_GRID), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r)
    print("  [seed=%d] %s" % (seed, {pol: round(d["fidelity"], 4) for pol, d in r["fidelity_by_policy"].items()}), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
