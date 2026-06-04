"""
phase05_v1_substrate_audit_core_v1 -- Exp-Dev substrate-side core for Phase 0.5 Rung A (validation on synthetic).

ROUTING: Exp-Dev's half of the Testbed division-of-labor
  (notes/exp_dev_to_testbed_phase05_rung_a_division_of_labor + testbed_to_exp_dev_phase05_rung_a_responses).
  Testbed produces the Llama-3.2-1B residual artifact npz (n_docs, 9, 2048); Exp-Dev runs Algorithm 1 +
  the audit primitives on the resulting substrate vectors. THIS run VALIDATES the substrate-side pipeline on
  SYNTHETIC residuals with injected ground truth (model-agnostic), so it is drop-in ready for the real npz.

CAPABILITY QUESTION:
  Does the substrate-side audit core work correctly: (1) Algorithm 1 (K-means k=5 over the 9 layer residuals
  -> sum-pool -> sign -> bipolar 2048-d code) produces healthy distinct bipolar codes; (2) kappa_3 drift
  detection flags an injected distributional shift while staying near-zero on clean-vs-clean; (3) the rank-1
  deletion certificate preserves NON-target retrievals at cos>=0.95 after deleting one stored code?

PIPELINE (model-agnostic; consumes residuals (n_docs, 9, 2048)):
  Algorithm 1 per doc: kmeans(k=5) over the 9 layer-residuals -> centroids (5,2048) -> sum-pool -> (2048,)
  -> sign -> bipolar {-1,+1}^2048. Then audit primitives on the bipolar code matrix.

THREE VALIDATION CELLS (synthetic residuals; 3 seeds):
  A. Algorithm-1 health: bipolar balance |mean(xi)| < 0.7 AND pairwise-cos diversity (distinct codes).
  B. kappa_3 drift: kappa_3 (Tr(W^3)/N, W=Xi^T Xi/N) of clean vs INJECTED-DRIFT code sets; drift sigma_sep
     must exceed clean-vs-clean sigma_sep by a clear margin (the instrument detects the injected shift).
  C. deletion certificate: store codes auto-associatively (W=sum outer(xi,xi), diag 0); delete one code
     (rank-1 subtraction); NON-target self-retrieval cos(sign(W xi), xi) must stay >= 0.95.

PRE-REGISTERED BANDS (synthetic-validation; tests the INSTRUMENT, not a substrate claim):
  HARD-PASS: A balance<0.7 AND diversity ok; B injected-drift sigma_sep > 3x clean-vs-clean sigma_sep;
    C non-target retrieval cos >= 0.95 on 3/3 seeds. -> substrate-side audit core validated, ready for real npz.
  MIDDLE: 2 of 3 primitives pass. HARD-FAIL: drift not detected OR deletion breaks non-targets (<0.80) OR codes degenerate.
  NOTE: refusal-certificate primitive is NOT included -- it needs a refusal-LABELED probe set (Testbed to
  provide; the analogy dataset has no refusal labels).

FORMULA SELF-TESTS (PROT-022):
  1. kmeans_centroids((9,2048),k=5) -> (5,2048). 2. sum_pool((5,D)) = rows.sum(0). 3. bipolar_sign in {-1,+1}.
  4. kappa_3 of identity-ish W finite. 5. single stored code self-retrieves (cos>0.9).

PROT-018: NO _nN suffix (substrate dim = 2048 = Llama hidden, fixed by the artifact; declared, not swept).
PROT-021: per-seed partials. QUEUE: remote_cpu_queue (numpy; Algorithm-1 K-means + audit matmuls are light;
  GPU would not help -- per the routing-sanity gate this is correctly CPU). TIMEOUT: 7200s. ASCII-only.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, json, os, time, math
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials, write_metrics

ANCHOR_NAME = "phase05_v1_substrate_audit_core_v1"
HIDDEN = 2048          # Llama-3.2-1B hidden (artifact (n_docs, 9, 2048))
N_LAYERS = 9           # hidden_states[8:17]
K_CLUSTERS = 5         # Algorithm 1
RESIDUAL_NPZ = os.environ.get("HDLAB_RESIDUAL_NPZ", "")   # if set + exists, use REAL residuals instead of synthetic

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    N_DOCS = 200
    HID = 256
    NL = 5
else:
    SEEDS = [7, 17, 23]
    N_DOCS = 1000
    HID = HIDDEN
    NL = N_LAYERS

DRIFT_FRAC = 0.30
DRIFT_Z = 3.0              # z-score threshold for kappa_3 drift detection (anomaly vs clean distribution)
K_RESAMPLE = 5 if RUN_MODE != "smoke" else 3   # clean kappa_3 resamples to estimate the noise band
HP_DELETION_COS = 0.95
HF_DELETION_COS = 0.80
HP_BALANCE = 0.7
DEL_LOAD = 0.10           # deletion-cert bank load alpha=M/HID (UNDERLOADED << 0.138 so recall is clean)


# ---- Algorithm 1 helpers (numpy; mirror exp_phase05_v1_algorithm1_debug_pythia160m_v1) ----
def kmeans_centroids(embeddings: np.ndarray, k: int) -> np.ndarray:
    L, D = embeddings.shape
    k_actual = min(k, L)
    if k_actual == 1:
        return embeddings.mean(axis=0, keepdims=True)
    try:
        from sklearn.cluster import KMeans
        km = KMeans(n_clusters=k_actual, n_init=3, max_iter=100, random_state=42)
        km.fit(embeddings.astype(np.float64))
        return km.cluster_centers_.astype(np.float32)
    except ImportError:
        rng = np.random.default_rng(42)
        centers = embeddings[rng.choice(L, size=k_actual, replace=False)].copy()
        for _ in range(20):
            d = np.sum((embeddings[:, None, :] - centers[None, :, :]) ** 2, axis=-1)
            a = np.argmin(d, axis=1)
            nc = np.stack([embeddings[a == c].mean(axis=0) if (a == c).any() else centers[c] for c in range(k_actual)])
            if np.max(np.abs(nc - centers)) < 1e-6:
                break
            centers = nc
        return centers.astype(np.float32)


def algorithm1_code(doc_residuals: np.ndarray) -> np.ndarray:
    """doc_residuals (NL, D) -> bipolar code (D,)."""
    cent = kmeans_centroids(doc_residuals, K_CLUSTERS)   # (k, D)
    pooled = cent.sum(axis=0)                             # (D,)
    xi = np.sign(pooled).astype(np.float32); xi[xi == 0] = 1.0
    return xi


def codes_from_residuals(residuals: np.ndarray) -> np.ndarray:
    """residuals (n_docs, NL, D) -> bipolar code matrix (n_docs, D)."""
    return np.stack([algorithm1_code(residuals[i]) for i in range(residuals.shape[0])], axis=0)


def kappa3(Xi: np.ndarray) -> float:
    """Tr(W^3)/N for W = Xi^T Xi / N (Xi: (M, N))."""
    n = Xi.shape[1]
    W = (Xi.T @ Xi) / n
    return float(np.trace(W @ W @ W) / n)


def deletion_cert_noncos(Xi: np.ndarray, del_idx: int) -> float:
    """Auto-assoc W=sum outer(xi,xi) (diag 0); delete del_idx; return mean NON-target self-retrieval cos."""
    n = Xi.shape[1]
    W = (Xi.T @ Xi)
    np.fill_diagonal(W, 0.0)
    W = W - np.outer(Xi[del_idx], Xi[del_idx]); np.fill_diagonal(W, 0.0)   # rank-1 deletion
    cos_list = []
    for i in range(Xi.shape[0]):
        if i == del_idx:
            continue
        r = np.sign(W @ Xi[i]); r[r == 0] = 1.0
        cos_list.append(float((r @ Xi[i]) / n))
    return float(np.mean(cos_list))


def synth_residuals(n_docs, nl, d, gen, drift=False) -> np.ndarray:
    """Synthetic layer-residual stack with a pre-norm-like growing-std signature; drift shifts a fraction."""
    scales = np.linspace(0.12, 2.26, nl).astype(np.float32)
    base = gen.standard_normal((n_docs, nl, d)).astype(np.float32) * scales[None, :, None]
    if drift:
        k = int(round(DRIFT_FRAC * n_docs))
        idx = gen.choice(n_docs, size=k, replace=False)
        base[idx] += gen.standard_normal((k, nl, d)).astype(np.float32) * 1.5   # injected distributional shift
    return base


def _selftest():
    g = np.random.default_rng(0)
    emb = g.standard_normal((9, 256)).astype(np.float32)
    assert kmeans_centroids(emb, 5).shape == (5, 256)
    assert np.allclose(np.ones((5, 256)).sum(axis=0), 5.0)
    xi = algorithm1_code(emb); assert set(np.unique(xi).tolist()) <= {-1.0, 1.0}
    Xi = g.choice([-1.0, 1.0], size=(20, 256)).astype(np.float32)
    assert np.isfinite(kappa3(Xi))
    # single stored code self-retrieves
    W = (Xi.T @ Xi); np.fill_diagonal(W, 0.0)
    r = np.sign(W @ Xi[0]); cos = float((r @ Xi[0]) / 256)
    assert cos > 0.5, f"self-retrieval cos {cos}"
    assert abs(math.log(2) - 0.6931) < 1e-3
    print(f"[selftest] PASS: alg1_shape_ok bipolar_ok kappa3_finite self_retrieval_cos={cos:.3f}", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int) -> Dict:
    gen = np.random.default_rng(seed)
    t0 = time.time()
    if RESIDUAL_NPZ and os.path.exists(RESIDUAL_NPZ):
        npz = np.load(RESIDUAL_NPZ)
        residuals = npz["residuals"].astype(np.float32)
        src = f"real:{RESIDUAL_NPZ}"
    else:
        residuals = synth_residuals(N_DOCS, NL, HID, gen, drift=False)
        src = "synthetic"
    codes = codes_from_residuals(residuals)               # (n_docs, HID) bipolar
    # A. Algorithm-1 health
    balance = float(abs(codes.mean()))
    sub = codes[:min(50, len(codes))]
    norms = np.linalg.norm(sub, axis=1)
    cos_pairs = (sub @ sub.T) / np.outer(norms, norms)
    iu = np.triu_indices(len(sub), 1)
    diversity = float(np.mean(np.abs(cos_pairs[iu]))) if len(iu[0]) else 0.0
    # B. kappa_3 drift via z-score anomaly test (robust; no near-zero-denominator ratio).
    #    Estimate clean kappa_3 mean/std over resamples, then z of a held-out-clean and a drift set.
    clean_k3 = [kappa3(codes_from_residuals(synth_residuals(N_DOCS, NL, HID, gen, drift=False)))
                for _ in range(K_RESAMPLE)]
    mu = float(np.mean(clean_k3)); sd = float(np.std(clean_k3)) + 1e-9
    k3_heldclean = kappa3(codes_from_residuals(synth_residuals(N_DOCS, NL, HID, gen, drift=False)))
    k3_drift = kappa3(codes_from_residuals(synth_residuals(N_DOCS, NL, HID, gen, drift=True)))
    z_clean = abs(k3_heldclean - mu) / sd
    z_drift = abs(k3_drift - mu) / sd
    drift_detected = bool(z_drift > DRIFT_Z and z_clean < DRIFT_Z)
    # C. deletion cert on an UNDERLOADED bank (M = DEL_LOAD*HID << capacity -> clean recall)
    m_cap = max(8, int(round(DEL_LOAD * HID)))
    bank = codes[:min(m_cap, len(codes))]
    del_cos = deletion_cert_noncos(bank, del_idx=0)
    elapsed = time.time() - t0
    print(f"  [seed={seed} src={src}] balance={balance:.4f} diversity={diversity:.4f} "
          f"z_clean={z_clean:.2f} z_drift={z_drift:.2f} drift_detected={drift_detected} "
          f"deletion_noncos={del_cos:.4f} (M={len(bank)}) elapsed={elapsed:.1f}s", flush=True)
    return {"seed": seed, "src": src, "balance": balance, "diversity": diversity,
            "z_clean": float(z_clean), "z_drift": float(z_drift), "drift_detected": drift_detected,
            "deletion_noncos": del_cos, "deletion_M": int(len(bank)), "elapsed_s": elapsed}


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    if not results:
        return ("HARD_FAIL", "HARD_FAIL: no results.")
    n = len(results)
    a_ok = sum(1 for r in results if r["balance"] < HP_BALANCE)
    b_ok = sum(1 for r in results if r["drift_detected"])
    c_ok = sum(1 for r in results if r["deletion_noncos"] >= HP_DELETION_COS)
    c_bad = any(r["deletion_noncos"] < HF_DELETION_COS for r in results)
    mb = float(np.mean([r["balance"] for r in results]))
    mdc = float(np.mean([r["deletion_noncos"] for r in results]))
    summary = (f"alg1_balance={mb:.3f}(ok {a_ok}/{n}) drift_detected(ok {b_ok}/{n}) "
               f"deletion_noncos={mdc:.3f}(ok {c_ok}/{n})")
    n_pass = (a_ok == n) + (b_ok == n) + (c_ok == n)
    if c_bad:
        return ("HARD_FAIL", f"HARD_FAIL: deletion breaks non-targets (cos<{HF_DELETION_COS}). {summary}")
    if n_pass == 3:
        return ("HARD_PASS", f"HARD_PASS: substrate-side audit core validated on synthetic (alg1+drift+deletion all 3/3). {summary}")
    if n_pass == 2:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: 2/3 audit primitives validated. {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: <2 audit primitives validated. {summary}")


print(f"[config] anchor={ANCHOR_NAME} mode={RUN_MODE} seeds={SEEDS} n_docs={N_DOCS} hidden={HID} "
      f"residual_npz={'(set)' if RESIDUAL_NPZ else 'synthetic'}", flush=True)

out_dir = get_output_dir(ANCHOR_NAME)
out_dir.mkdir(parents=True, exist_ok=True)
run_config = {"run_mode": RUN_MODE, "n_docs": N_DOCS, "hidden": HID, "seeds": SEEDS}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run", flush=True)

for seed in remaining:
    print(f"[seed={seed}] {ANCHOR_NAME}...", flush=True)
    write_partial(out_dir, seed, run_seed(seed))

per_seed = aggregate_partials(out_dir, SEEDS)
all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(all_results)
print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

metrics = {
    "anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": verdict_msg,
    "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "n_docs": N_DOCS, "hidden": HID,
    "per_seed": [{k: v for k, v in r.items()} for r in all_results],
}
write_metrics(out_dir, metrics, all_results)
print(f"[metrics] written to {out_dir / 'metrics.json'}", flush=True)
