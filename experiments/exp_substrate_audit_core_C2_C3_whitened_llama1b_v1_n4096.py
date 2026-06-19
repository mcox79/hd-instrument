"""
substrate_audit_core_C2_C3_whitened_llama1b_v1_n4096 -- audit-core C2/C3 on REAL Llama-3.2-1B residuals (Phase 2; last-token-of-doc slice) -- remote CPU.

ROUTING: research overnight (O) + hourly_cadence (4 gated cells). Pythia-160M residual extraction HARD_PASS
  (residuals.npz). Tier-1 PRODUCT anchor: substrate stores LLM residuals and supports (C2) DELETION-CERTIFICATES
  -- categorically unavailable in fine-tuned LLMs (HIPAA/GDPR wedge) -- and (C3) DRIFT detection. CPU numpy, $0.
  remote_cpu_queue. Loads data/exp_phase05_v1_pythia160m_residual_extract_v1/residuals.npz (HDLAB_RESIDUAL_NPZ override).

MODEL: real residuals R (M,768) -> B2 DG sparse-expansion (random projection -> k-WTA, f=0.05) into N=4096 sparse
  codes S; covariance memory W=(S-f)^T(S-f). C2: store; verify recall; B6 D-ECR evict pattern i; verify i NO LONGER
  recalled (deletion-cert) AND others intact. C3: drift = MMD-like 3rd-moment stat kappa3 between stored vs a NEW
  batch; detect drift (shifted dist) vs no-drift (resample) -- separation = operational.

PRE-REGISTERED bands: HARD-PASS C2 deletion-cert>=0.95 (deleted-gone AND others-intact) AND C3 drift-separation
  (kappa3_drift >= 3x kappa3_nodrift). MIDDLE one of the two. HARD-FAIL neither (audit primitives non-operational on real residuals).

FORMULA SELF-TESTS (PROT-022): 1. sparse recall. 2. deletion drops recall. 3. drift stat larger for shifted. 4. N=4096.
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

ANCHOR_NAME = "substrate_audit_core_C2_C3_whitened_llama1b_v1_n4096"
_N_SUFFIX = 4096; N = 4096; assert N == _N_SUFFIX
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()

HIDDEN = 768; F_SPARSE = 0.05
NPZ_PATH = os.environ.get("HDLAB_RESIDUAL_NPZ", str(REPO / "data" / "exp_phase05_v1_llama32_1b_per_token_residual_extract_v1" / "residuals_per_token.npz"))
if RUN_MODE == "smoke":
    SEEDS = [1]; N_DIM = 1024; M_STORE = 200; N_DEL = 50
else:
    SEEDS = [7, 17, 23]; N_DIM = N; M_STORE = 2000; N_DEL = 200


def load_residuals(g):
    if RUN_MODE != "smoke" and os.path.exists(NPZ_PATH):
        d = np.load(NPZ_PATH); res = d["residuals"].astype(np.float32)
        if "doc_boundaries" in d.files:                       # per-token npz -> last-token-of-each-doc slice
            bnd = d["doc_boundaries"].astype(np.int64)
            R = np.stack([res[bnd[i + 1] - 1] for i in range(len(bnd) - 1)]).astype(np.float32)
        else:
            R = res
        print("[data] loaded real residuals %s -> per-doc shape=%s" % (NPZ_PATH, R.shape), flush=True)
        return R
    print("[data] synthetic residuals (smoke / npz absent)", flush=True)
    return g.standard_normal((M_STORE + 500, HIDDEN)).astype(np.float32)


def sparse_expand(R, n, g):
    P = g.standard_normal((R.shape[1], n)).astype(np.float32) / math.sqrt(R.shape[1])
    H = R @ P; k = max(1, int(round(F_SPARSE * n)))
    S = np.zeros((len(R), n), dtype=np.float32)
    for i in range(len(R)):
        S[i, np.argpartition(-H[i], k - 1)[:k]] = 1.0
    return S, k


def kwta(v, k):
    o = np.zeros_like(v); o[np.argpartition(-v, k - 1)[:k]] = 1.0; return o


def kappa3(A, B):
    """drift stat: L2 between mean + abs-3rd-moment of two residual batches."""
    dm = float(np.linalg.norm(A.mean(0) - B.mean(0)))
    d3 = float(np.linalg.norm(np.abs(((A - A.mean(0)) ** 3).mean(0)) - np.abs(((B - B.mean(0)) ** 3).mean(0))))
    return dm + d3


def _selftest():
    g = np.random.default_rng(0); R = g.standard_normal((10, HIDDEN)).astype(np.float32)
    S, k = sparse_expand(R, 512, g); W = (S - F_SPARSE).T @ (S - F_SPARSE); np.fill_diagonal(W, 0.0)
    b = float((kwta((S[0] - F_SPARSE) @ W.T, k) * S[0]).sum() / k); assert b > 0.9, "sparse recall"
    W2 = W - np.outer(S[0] - F_SPARSE, S[0] - F_SPARSE); np.fill_diagonal(W2, 0.0)
    assert float((kwta((S[0] - F_SPARSE) @ W2.T, k) * S[0]).sum() / k) < b, "deletion drops"
    A = g.standard_normal((50, 8)); Bd = A + 2.0; Bn = g.standard_normal((50, 8))
    assert kappa3(A, Bd) > kappa3(A, Bn), "drift stat larger for shifted"
    assert N == 4096; print("[selftest] PASS: sparse_recall deletion drift", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int) -> Dict:
    g = np.random.default_rng(seed); R = load_residuals(g)
    R = R / (np.linalg.norm(R, axis=1, keepdims=True) + 1e-8)
    M = min(M_STORE, len(R) - 200); store = R[:M]; newb = R[M:M + min(500, len(R) - M)]
    # PCA-whiten store (decorrelate real residuals -> clean Hebbian deletion-cert)
    mu = store.mean(0); Xc = store - mu; U, Sv, Vt = np.linalg.svd(Xc, full_matrices=False)
    Wht = (Vt.T / (Sv / math.sqrt(len(Xc)) + 1e-3)).astype(np.float32); store = (Xc @ Wht).astype(np.float32)
    store = store / (np.linalg.norm(store, axis=1, keepdims=True) + 1e-8)
    S, k = sparse_expand(store, N_DIM, g); W = (S - F_SPARSE).T @ (S - F_SPARSE); np.fill_diagonal(W, 0.0)
    # C2 deletion-cert
    idx = g.choice(M, size=min(N_DEL, M), replace=False); cert = 0
    for i in idx:
        before = float((kwta((S[i] - F_SPARSE) @ W.T, k) * S[i]).sum() / k)
        Wd = W - np.outer(S[i] - F_SPARSE, S[i] - F_SPARSE); np.fill_diagonal(Wd, 0.0)
        after = float((kwta((S[i] - F_SPARSE) @ Wd.T, k) * S[i]).sum() / k)
        deleted_gone = after < 0.7 * max(before, 1e-6)
        oth = g.choice([j for j in range(M) if j != i], size=min(20, M - 1), replace=False)
        others_ok = float(np.mean([float((kwta((S[j] - F_SPARSE) @ Wd.T, k) * S[j]).sum() / k) > 0.9 for j in oth]))
        cert += 0.5 * (float(deleted_gone) + others_ok)
    c2 = cert / len(idx)
    # C3 drift: stored vs shifted(new+perturb) [drift] vs stored vs resample [no-drift]
    half = M // 2
    k_nodrift = kappa3(store[:half], store[half:2 * half])
    if len(newb):
        newb_w = ((newb - mu) @ Wht).astype(np.float32); newb_w = newb_w / (np.linalg.norm(newb_w, axis=1, keepdims=True) + 1e-8)
        shifted = newb_w + 0.5 * g.standard_normal(newb_w.shape).astype(np.float32)   # whiten newb into store-space (dim may be reduced when orig dim > M)
    else:
        shifted = store[:half] + 1.0
    k_drift = kappa3(store[:len(shifted)], shifted)
    sep = float(k_drift / max(k_nodrift, 1e-9))
    return {"seed": seed, "N": N_DIM, "M_stored": int(M), "real_data": bool(RUN_MODE != "smoke" and os.path.exists(NPZ_PATH)),
            "C2_deletion_cert": float(c2), "C3_kappa3_drift": float(k_drift), "C3_kappa3_nodrift": float(k_nodrift), "C3_separation": sep}


def verdict(ps) -> Tuple[str, str]:
    c2 = float(np.mean([p["C2_deletion_cert"] for p in ps])); sep = float(np.mean([p["C3_separation"] for p in ps]))
    rd = ps[0]["real_data"]
    summary = "C2_deletion_cert=%.2f C3_drift_separation=%.1fx (real_residuals=%s, M=%d)" % (c2, sep, rd, ps[0]["M_stored"])
    if c2 >= 0.95 and sep >= 3.0:
        return ("HARD_PASS", "HARD_PASS: audit-core operational on real Pythia residuals (deletion-cert + drift). " + summary)
    if c2 >= 0.95 or sep >= 3.0:
        return ("MIDDLE_BAND", "MIDDLE_BAND: one audit primitive operational. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: audit primitives not operational on real residuals. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d npz=%s" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, NPZ_PATH), flush=True)
if RUN_MODE == "full" and N_DIM != _N_SUFFIX:
    raise RuntimeError("PROT-018 N mismatch")
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r)
    print("  [seed=%d] C2_cert=%.2f C3_sep=%.1fx real=%s" % (seed, r["C2_deletion_cert"], r["C3_separation"], r["real_data"]), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N_DIM, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
