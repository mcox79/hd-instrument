"""importance_ceiling_v7B_n_seeds_scale.

Corrected follow-up to v7 per cell-author's diagnosis: Option B (M lowered)
plus N_SEEDS=16 (Research handoff 2026-06-27, walking back v7 framing).

v7 framing CONTRADICTED cell physics: CRLB k=8 floor = sqrt(M/(d*k)). At
M=d=16384, k=8 the floor is 0.354, but HARD_PASS bar was 0.15 -- HP was
mathematically unattainable BY CONSTRUCTION. Smoke caught this; v7 FULL
was correctly blocked.

v7B fix (single-knob change from v1; spec-precise per Research handoff):
  N_DIM = 16384    (preserve v1's d; substrate native dim)
  M     = 1024     (per Author Option B recommendation; lowest in 1024-2048
                    range; preserves v1 regime closest while CRLB drops to
                    0.088 -- well below HP=0.15 bar)
  K_F   = 8        (same as v1; fusion)
  SEEDS = 16       (8x v1's 2; reduces SEM by 2.83x -> resolves v1's
                    cv=8.234 statistical-resolution problem)

CRLB k=8 floor at v7B regime: sqrt(1024/(16384*8)) = 0.0884
HP=0.15 -> 1.7x above floor -> attainable.

v1 INDETERMINATE root cause: cv=8.234 at n=2 seeds, not a floor-escape
problem. v7B addresses that root cause directly.

ARMS (5; v1 lineup preserved minus diag_k_sweep):
  ARM_BASELINE_RAND            random importance (negative control)
  ARM_TRACE_BASELINE           |w|+tiny-noise (regime-sanity positive)
  ARM_SINGLE_READOUT_FISHER    k=1 readout (fairness baseline; near CRLB)
  ARM_EIGHT_READOUT_FISHER     k=8 orthogonal-Gaussian + Fisher fusion
  ARM_EIGHT_READOUT_PCA_BASIS  k=8 PCA-basis (substrate-native) + Fisher

PRE-REG BANDS (HARD-LOCKED at module init):
  HARD_PASS:
       At least one non-Trace arm: sel_unretr >= 0.15
       AND cv(across n=16 seeds) < 0.30
       AND mean - 1.96*sem > 0 (SEM-separated from Random_baseline)
       AND PCA arm specifically: replicates v1 seed-17 +0.144 within +-0.05
           at higher-n test (so PCA cell-mean in [0.094, 0.194])
       AND CRLB k=8 floor reported < 0.10 (sanity)
       AND |cell-mean RAND| <= 0.04 (contamination guard)
       AND cell-mean TRACE >= 0.25 (regime sanity)
  HARD_FAIL (TRUE substrate-physics ceiling at +0.05):
       All non-Trace arms below 0.05 AND sem_separated (TRUE substrate ceil)
       OR CRLB floor exceeds 0.10 (regime broken; respec again)
  MIDDLE_BAND: non-Trace arm in [0.05, 0.15) AND sem_separated
               (bounded; not chain-grade but real signal above noise floor)

CARDINALITY (META_RULE_H):
  EXPECTED_N_UNITS_FULL = 5 arms * 16 seeds = 80
  EXPECTED_N_UNITS_SMOKE = 5 arms * 4 seeds = 20

Smoke at N=4096, M=512 (1/4 scale), n_seeds=4:
  CRLB floor measured = sqrt(512/(4096*8)) = 0.0442 (sanity check)
  PCA arm should have SOME signal above floor (>= 0.05)
  IF smoke PCA below CRLB at this scale -> cell broken; iterate
  IF smoke PCA above CRLB -> proceed to full n=16 at N=16384 M=1024

DISCRIMINATOR-MUST-SURVIVE-SCALE: smoke CRLB (0.044) is LOWER than full
CRLB (0.088), but smoke discriminator is whether PCA escapes the floor
at all; v1 seed-17 already showed +0.144 at N=16384 M=400 so escape is
known feasible. Smoke confirms we're not in a regime breakdown.

META_RULE_AF arms-must-differ self-test: assert PCA/Fisher/Single outputs
have differing fingerprints (sum of |importance|). (Author already caught
one silent-twin bug in v7; preserved.)
META_RULE_AH atomic-final-metrics-write: write tmp + os.replace.
META_RULE_AE absolute-paths only.

GPU: --device cuda flag supported; E matrix only 1024 x 16384 = 64MB
float32, tractable on CPU or GPU.

ASCII-only; no emojis; no em-dashes; self-contained.
Author: exp_dev 2026-06-27 (v7B spec from Research; supersedes v7)
"""
from __future__ import annotations

import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import argparse
import hashlib
import json
import math
import os
import time
import traceback
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    resumable_seeds, write_partial_key, aggregate_partials,
)

ANCHOR_NAME = "importance_ceiling_v7B_n_seeds_scale"

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ap.add_argument("--device", choices=["cpu", "cuda"], default="cpu")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE)
            else os.environ.get("HDLAB_RUN_MODE", "full").lower())
SELF_TEST_MODE = bool(_ARGS.self_test)
DEVICE = _ARGS.device

_TORCH = None
if DEVICE == "cuda":
    try:
        import torch as _t
        if _t.cuda.is_available():
            _TORCH = _t
        else:
            print("[device] cuda requested but not available; falling back to cpu",
                  flush=True)
            DEVICE = "cpu"
    except ImportError:
        print("[device] cuda requested but torch unavailable; falling back to cpu",
              flush=True)
        DEVICE = "cpu"

# Pre-reg bands LOCKED at module init
HP_NONTRACE_FLOOR = 0.15      # max(non-Trace) >= this for HARD_PASS
HP_CV_MAX = 0.30              # CV ceiling for HARD_PASS and HARD_FAIL claims
HP_PCA_V1_LOWER = 0.094       # PCA replicate v1 seed-17 +0.144 +- 0.05
HP_PCA_V1_UPPER = 0.194
HP_CRLB_SANITY_CEIL = 0.10    # CRLB k=8 floor must be < this for HP sanity
REAL_NONTRACE_CEIL = 0.05     # max(non-Trace) below this -> ceiling REAL
RAND_MEAN_TOL = 0.04          # |cell-mean rand| <= this
TRACE_SANITY = 0.25           # trace cell-mean must clear for regime sanity

EXPECTED_ARMS = ["baseline_rand", "trace_baseline",
                 "single_readout_fisher", "eight_readout_fisher",
                 "eight_readout_pca_basis"]
NON_TRACE_ARMS = ["single_readout_fisher", "eight_readout_fisher",
                  "eight_readout_pca_basis"]

if SELF_TEST_MODE:
    N_DIM = 512
    M = 128
    SEEDS = [7]
    K_FISHER = 4
elif RUN_MODE == "smoke":
    # Smoke REGIME-MATCHED to full (M/d preserved at 0.0625):
    # N=8192, M=512 -> CRLB k=8 = 0.0884 (identical to full 0.0884)
    # NOTE: Research spec said N=4096 M=512 -> claimed CRLB=0.044 but actual
    # is 0.125 (M/d ratio 0.125, double full's 0.063). To honor
    # DISCRIMINATOR-MUST-SURVIVE-SCALE, smoke must match full's CRLB regime.
    # Cost: 0.25x full (N=8192 vs 16384, M=512 vs 1024). Wall ~30-60s.
    N_DIM = 8192
    M = 512
    SEEDS = [7, 11, 13, 17]
    K_FISHER = 8
else:
    # Full per Research spec: N=16384, M=1024, n_seeds=16
    N_DIM = 16384
    M = 1024
    SEEDS = [7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67]
    K_FISHER = 8

EXPECTED_N_UNITS = len(EXPECTED_ARMS) * len(SEEDS)

CONFIG_VERSION = (
    "ANCHOR=%s,N=%d,M=%d,seeds=%s,K_F=%d,mode=%s,device=%s,"
    "HP_nontrace>=%.2f,HP_cv<=%.2f,HP_PCA_in=[%.3f,%.3f],"
    "HP_crlb_sanity<%.2f,real_ceil<=%.2f,"
    "rand_mean_tol=%.2f,trace_sanity>=%.2f,expected_n=%d,"
    "hardening=L1early+L2perarm+L3outertry+L4importsentinel,"
    "rules=AA+AE+AF+AH+H_cardinality"
) % (
    ANCHOR_NAME, N_DIM, M, SEEDS, K_FISHER, RUN_MODE, DEVICE,
    HP_NONTRACE_FLOOR, HP_CV_MAX, HP_PCA_V1_LOWER, HP_PCA_V1_UPPER,
    HP_CRLB_SANITY_CEIL, REAL_NONTRACE_CEIL,
    RAND_MEAN_TOL, TRACE_SANITY, EXPECTED_N_UNITS,
)

_RESULTS_HOLDER: Dict[str, Any] = {"started_at": time.time()}


def _write_minimal_metrics(out_dir: Path, verdict: str, verdict_msg: str,
                            extra: Dict[str, Any] = None) -> None:
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        metrics = {
            "anchor_name": ANCHOR_NAME,
            "verdict": verdict,
            "verdict_msg": verdict_msg,
            "summary": verdict_msg,
            "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 1),
            "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "pid": os.getpid(),
            "run_mode": RUN_MODE,
            "device": DEVICE,
            "config_version": CONFIG_VERSION,
            "_hardening_marker": "v7B_n_seeds_scale",
        }
        if extra:
            metrics.update(extra)
        # META_RULE_AH atomic write
        tmp = out_dir / "metrics.json.tmp"
        tmp.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
        os.replace(str(tmp), str(out_dir / "metrics.json"))
    except Exception as e:
        print("[_write_minimal_metrics] FAIL: %s" % e, file=sys.stderr, flush=True)


def _write_import_crash_sentinel(exc: BaseException) -> None:
    try:
        env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
        out_dir = REPO / "data" / ("exp_" + env_name)
        out_dir.mkdir(parents=True, exist_ok=True)
        sentinel = {
            "anchor_name": ANCHOR_NAME,
            "verdict": "UNKNOWN",
            "verdict_msg": "IMPORT_CRASH: %s: %s" % (type(exc).__name__, str(exc)),
            "summary": "IMPORT_CRASH: %s: %s" % (type(exc).__name__, str(exc)),
            "elapsed_s": 0.0,
            "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "pid": os.getpid(),
            "_traceback": traceback.format_exc(),
            "_hardening_marker": "v7B_n_seeds_scale_import_crash",
        }
        (out_dir / "metrics.json").write_text(
            json.dumps(sentinel, indent=2), encoding="utf-8")
        (out_dir / "import_crash.json").write_text(
            json.dumps(sentinel, indent=2), encoding="utf-8")
    except Exception as e:
        print("[_write_import_crash_sentinel] FAIL: %s" % e,
              file=sys.stderr, flush=True)


# -------------------------- primitives --------------------------

def bipolar(M_atoms: int, n: int, g: np.random.Generator) -> np.ndarray:
    X = (g.integers(0, 2, size=(M_atoms, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def gaussian(k: int, n: int, g: np.random.Generator) -> np.ndarray:
    X = g.standard_normal((k, n)).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def build_superposition(E: np.ndarray, w: np.ndarray) -> np.ndarray:
    return (w[:, None] * E).sum(axis=0).astype(np.float32)


def _matmul(E: np.ndarray, vec: np.ndarray) -> np.ndarray:
    """E @ vec: shape (M,n) @ (n,) -> (M,). Uses torch.cuda if DEVICE=cuda."""
    if _TORCH is not None and DEVICE == "cuda":
        E_t = _TORCH.from_numpy(E).to("cuda")
        v_t = _TORCH.from_numpy(vec).to("cuda")
        out = (E_t @ v_t).cpu().numpy()
        del E_t, v_t
        return out
    return E @ vec


def per_readout_importance(S: np.ndarray, E: np.ndarray,
                            readouts: np.ndarray) -> np.ndarray:
    """(k, M) per-readout importance scores. Vectorized on GPU when available."""
    k = readouts.shape[0]
    M_atoms = E.shape[0]
    if _TORCH is not None and DEVICE == "cuda":
        E_t = _TORCH.from_numpy(E).to("cuda")
        S_t = _TORCH.from_numpy(S).to("cuda")
        r_t = _TORCH.from_numpy(readouts).to("cuda")
        S_mod = S_t.unsqueeze(0) * r_t        # (k, n)
        scores = _TORCH.abs(S_mod @ E_t.T)     # (k, M)
        out = scores.cpu().numpy()
        del E_t, S_t, r_t, S_mod, scores
        _TORCH.cuda.empty_cache()
        return out
    out = np.zeros((k, M_atoms), dtype=np.float32)
    for ri in range(k):
        r = readouts[ri]
        S_mod = S * r
        out[ri] = np.abs(E @ S_mod)
    return out


def fisher_weighted_fusion(per_readout_scores: np.ndarray) -> np.ndarray:
    per_readout_var = per_readout_scores.var(axis=1) + 1e-6
    weights = 1.0 / per_readout_var
    weights = weights / weights.sum()
    fused = (weights[:, None] * per_readout_scores).sum(axis=0)
    return fused


def make_pca_basis(E: np.ndarray, k: int,
                    g: np.random.Generator) -> np.ndarray:
    """Top-k right singular vectors of centered E. (k, n) orthonormal."""
    M_atoms, n = E.shape
    Em = E - E.mean(axis=0, keepdims=True)
    k_eff = min(k, min(M_atoms, n))
    try:
        # Randomized SVD: oversample, project, do small SVD.
        oversample = 10
        k_sample = min(k_eff + oversample, n)
        Omega = g.standard_normal((n, k_sample)).astype(np.float32)
        Y = Em @ Omega                     # (M, k_sample)
        Q, _ = np.linalg.qr(Y)
        B = Q.T @ Em                       # (k_sample, n)
        U_b, sval, Vt = np.linalg.svd(B, full_matrices=False)
        basis = Vt[:k_eff]
    except np.linalg.LinAlgError:
        basis = gaussian(k_eff, n, g)
    basis = basis / (np.linalg.norm(basis, axis=1, keepdims=True) + 1e-8)
    if k_eff < k:
        extra = gaussian(k - k_eff, n, g)
        basis = np.concatenate([basis, extra], axis=0)
    # Validate orthonormality
    G = basis @ basis.T
    off_diag = G - np.eye(basis.shape[0], dtype=basis.dtype)
    if np.max(np.abs(off_diag)) > 0.05:
        raw = gaussian(k, n, g)
        Q, _ = np.linalg.qr(raw.T)
        basis = Q.T[:k].astype(np.float32)
    return basis.astype(np.float32)


def sel_unretr_metric(imp_hat: np.ndarray, w_true: np.ndarray,
                       retr_mask: np.ndarray) -> float:
    """Rank-corr between |imp_hat| and |w_true| on unretrieved subset."""
    unretr = ~retr_mask
    if unretr.sum() < 3:
        return 0.0
    h = np.abs(imp_hat[unretr])
    w = np.abs(w_true[unretr])
    h_rank = np.argsort(np.argsort(h)).astype(np.float64)
    w_rank = np.argsort(np.argsort(w)).astype(np.float64)
    h_rank = h_rank - h_rank.mean()
    w_rank = w_rank - w_rank.mean()
    denom = np.sqrt((h_rank ** 2).sum() * (w_rank ** 2).sum()) + 1e-8
    return float((h_rank * w_rank).sum() / denom)


def cor_with_W(imp_hat: np.ndarray, w_true: np.ndarray) -> float:
    h = np.abs(imp_hat)
    w = np.abs(w_true)
    h_c = h - h.mean()
    w_c = w - w.mean()
    denom = np.sqrt((h_c ** 2).sum() * (w_c ** 2).sum()) + 1e-8
    return float((h_c * w_c).sum() / denom)


def crlb_floor(M_atoms: int, n: int, k: int) -> float:
    return float(math.sqrt(M_atoms / (float(n) * float(max(k, 1)))))


def _fingerprint(arr: np.ndarray) -> str:
    """SHA1-prefix of |arr| binary for META_RULE_AF arms-must-differ check."""
    h = hashlib.sha1(np.abs(arr).astype(np.float32).tobytes()).hexdigest()
    return h[:16]


# -------------------------- arms --------------------------

def run_arm_baseline_rand(E: np.ndarray, S: np.ndarray, w: np.ndarray,
                           retr_mask: np.ndarray,
                           g: np.random.Generator) -> Tuple[float, float, np.ndarray]:
    imp = g.standard_normal(w.shape[0]).astype(np.float32)
    return (sel_unretr_metric(imp, w, retr_mask),
            cor_with_W(imp, w), imp)


def run_arm_trace_baseline(E: np.ndarray, S: np.ndarray, w: np.ndarray,
                            retr_mask: np.ndarray,
                            g: np.random.Generator) -> Tuple[float, float, np.ndarray]:
    imp = np.abs(w) + g.standard_normal(w.shape[0]).astype(np.float32) * 0.005
    return (sel_unretr_metric(imp, w, retr_mask),
            cor_with_W(imp, w), imp)


def run_arm_single_readout_fisher(E: np.ndarray, S: np.ndarray, w: np.ndarray,
                                    retr_mask: np.ndarray,
                                    g: np.random.Generator) -> Tuple[float, float, np.ndarray]:
    readouts = gaussian(1, E.shape[1], g)
    per_r = per_readout_importance(S, E, readouts)
    fused = per_r[0]
    return (sel_unretr_metric(fused, w, retr_mask),
            cor_with_W(fused, w), fused)


def run_arm_eight_readout_fisher(E: np.ndarray, S: np.ndarray, w: np.ndarray,
                                   retr_mask: np.ndarray, k: int,
                                   g: np.random.Generator) -> Tuple[float, float, np.ndarray]:
    raw = gaussian(k, E.shape[1], g)
    Q, _ = np.linalg.qr(raw.T)
    readouts = Q.T[:k]
    per_r = per_readout_importance(S, E, readouts)
    fused = fisher_weighted_fusion(per_r)
    return (sel_unretr_metric(fused, w, retr_mask),
            cor_with_W(fused, w), fused)


def run_arm_eight_readout_pca(E: np.ndarray, S: np.ndarray, w: np.ndarray,
                                retr_mask: np.ndarray, k: int,
                                g: np.random.Generator) -> Tuple[float, float, np.ndarray]:
    readouts = make_pca_basis(E, k, g)
    per_r = per_readout_importance(S, E, readouts)
    fused = fisher_weighted_fusion(per_r)
    return (sel_unretr_metric(fused, w, retr_mask),
            cor_with_W(fused, w), fused)


# -------------------------- per-seed --------------------------

def run_one_seed(seed: int) -> Dict[str, Any]:
    g = np.random.default_rng(seed)
    t_build = time.time()
    E = bipolar(M, N_DIM, g)
    w = g.standard_normal(M).astype(np.float32) * 0.3
    retr_mask = np.zeros(M, dtype=bool)
    top_idx = np.argsort(np.abs(w))[-int(M * 0.3):]
    retr_mask[top_idx] = True
    S = build_superposition(E, w)
    print("  [seed=%d build] E=(%d,%d) w=(%d,) build_s=%.1f" % (
        seed, M, N_DIM, M, time.time() - t_build), flush=True)

    arm_results: Dict[str, Dict[str, float]] = {}
    fingerprints: Dict[str, str] = {}

    t0 = time.time()
    sel, cor, imp = run_arm_baseline_rand(E, S, w, retr_mask, g)
    arm_results["baseline_rand"] = {"sel_unretr": sel, "cor_with_W": cor}
    fingerprints["baseline_rand"] = _fingerprint(imp)
    print("  [seed=%d arm=baseline_rand] sel=%.4f cor=%.4f wall=%.1fs"
          % (seed, sel, cor, time.time() - t0), flush=True)

    t0 = time.time()
    sel, cor, imp = run_arm_trace_baseline(E, S, w, retr_mask, g)
    arm_results["trace_baseline"] = {"sel_unretr": sel, "cor_with_W": cor}
    fingerprints["trace_baseline"] = _fingerprint(imp)
    print("  [seed=%d arm=trace_baseline] sel=%.4f cor=%.4f wall=%.1fs"
          % (seed, sel, cor, time.time() - t0), flush=True)

    t0 = time.time()
    sel, cor, imp = run_arm_single_readout_fisher(E, S, w, retr_mask, g)
    arm_results["single_readout_fisher"] = {"sel_unretr": sel, "cor_with_W": cor}
    fingerprints["single_readout_fisher"] = _fingerprint(imp)
    print("  [seed=%d arm=single_readout_fisher] sel=%.4f cor=%.4f wall=%.1fs"
          % (seed, sel, cor, time.time() - t0), flush=True)

    t0 = time.time()
    sel, cor, imp = run_arm_eight_readout_fisher(E, S, w, retr_mask, K_FISHER, g)
    arm_results["eight_readout_fisher"] = {"sel_unretr": sel, "cor_with_W": cor}
    fingerprints["eight_readout_fisher"] = _fingerprint(imp)
    print("  [seed=%d arm=eight_readout_fisher] sel=%.4f cor=%.4f wall=%.1fs"
          % (seed, sel, cor, time.time() - t0), flush=True)

    t0 = time.time()
    sel, cor, imp = run_arm_eight_readout_pca(E, S, w, retr_mask, K_FISHER, g)
    arm_results["eight_readout_pca_basis"] = {"sel_unretr": sel, "cor_with_W": cor}
    fingerprints["eight_readout_pca_basis"] = _fingerprint(imp)
    print("  [seed=%d arm=eight_readout_pca_basis] sel=%.4f cor=%.4f wall=%.1fs"
          % (seed, sel, cor, time.time() - t0), flush=True)

    # META_RULE_AF arms-must-differ self-check
    fp_set = set(fingerprints[a] for a in
                 ["single_readout_fisher", "eight_readout_fisher",
                  "eight_readout_pca_basis"])
    arms_differ = (len(fp_set) == 3)
    print("  [seed=%d arms_differ=%s fingerprints=%s]" % (
        seed, arms_differ, fingerprints), flush=True)

    return {
        "seed": int(seed),
        "N": N_DIM,
        "M": M,
        "K_FISHER": K_FISHER,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "crlb_floor_k1": crlb_floor(M, N_DIM, 1),
        "crlb_floor_k8": crlb_floor(M, N_DIM, K_FISHER),
        "per_arm": arm_results,
        "fingerprints": fingerprints,
        "arms_differ": bool(arms_differ),
    }


# -------------------------- verdict --------------------------

def aggregate_and_verdict(per_seed: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    if not per_seed:
        return {
            "verdict": "UNKNOWN",
            "verdict_msg": "no per-seed partials found",
            "summary": "no per-seed partials found",
            "per_arm": {},
        }
    seeds_sorted = sorted(per_seed.keys(), key=lambda s: int(s))
    summary: Dict[str, Dict[str, float]] = {}
    per_arm_full: Dict[str, Dict[str, Dict[str, float]]] = {}
    for arm in EXPECTED_ARMS:
        per_arm_full[arm] = {}
        sel_vals: List[float] = []
        cor_vals: List[float] = []
        for s in seeds_sorted:
            body = per_seed[s]
            pa = body.get("per_arm", {})
            if arm in pa:
                d = pa[arm]
                sel_vals.append(float(d.get("sel_unretr", 0.0)))
                cor_vals.append(float(d.get("cor_with_W", 0.0)))
                per_arm_full[arm][s] = {
                    "sel_unretr": float(d.get("sel_unretr", 0.0)),
                    "cor_with_W": float(d.get("cor_with_W", 0.0)),
                }
        if sel_vals:
            m_sel = float(np.mean(sel_vals))
            sd_sel = float(np.std(sel_vals, ddof=1)) if len(sel_vals) > 1 else 0.0
            sem = sd_sel / math.sqrt(len(sel_vals)) if len(sel_vals) > 1 else 0.0
            cv = sd_sel / abs(m_sel) if abs(m_sel) > 1e-6 else 0.0
            summary[arm] = {
                "mean_sel": m_sel, "std_sel": sd_sel, "sem": sem, "cv_sel": cv,
                "mean_cor": float(np.mean(cor_vals)), "n": len(sel_vals),
                "mean_minus_1p96sem": m_sel - 1.96 * sem,
            }
        else:
            summary[arm] = {"mean_sel": 0.0, "std_sel": 0.0, "sem": 0.0,
                            "cv_sel": 0.0, "mean_cor": 0.0, "n": 0,
                            "mean_minus_1p96sem": 0.0}

    pca = summary["eight_readout_pca_basis"]
    fisher = summary["eight_readout_fisher"]
    single = summary["single_readout_fisher"]
    rand = summary["baseline_rand"]
    trace = summary["trace_baseline"]

    # Non-Trace winner
    nontrace_means = {
        "single_readout_fisher": single["mean_sel"],
        "eight_readout_fisher": fisher["mean_sel"],
        "eight_readout_pca_basis": pca["mean_sel"],
    }
    winner_arm = max(nontrace_means, key=lambda a: nontrace_means[a])
    winner_mean = nontrace_means[winner_arm]
    winner_cv = summary[winner_arm]["cv_sel"]
    winner_lb = summary[winner_arm]["mean_minus_1p96sem"]
    rand_mean = rand["mean_sel"]
    trace_mean = trace["mean_sel"]
    pca_mean = pca["mean_sel"]

    rand_clean = (-RAND_MEAN_TOL <= rand_mean <= RAND_MEAN_TOL)
    trace_sane = (trace_mean >= TRACE_SANITY)
    cv_resolved = (winner_cv < HP_CV_MAX)
    sem_separated = (winner_lb > 0.0)
    pca_in_v1_band = (HP_PCA_V1_LOWER <= pca_mean <= HP_PCA_V1_UPPER)
    crlb_k8 = crlb_floor(M, N_DIM, K_FISHER)
    crlb_sanity_ok = (crlb_k8 < HP_CRLB_SANITY_CEIL)

    # All-non-Trace-below-0.05 for HARD_FAIL
    all_nontrace_below_real = all(
        nontrace_means[a] < REAL_NONTRACE_CEIL for a in NON_TRACE_ARMS)

    verdict = "MIDDLE_BAND"
    if not rand_clean or not trace_sane:
        verdict = "MIDDLE_BAND"  # regime confound
    elif not crlb_sanity_ok:
        verdict = "HARD_FAIL"   # regime broken; respec again
    elif (winner_mean >= HP_NONTRACE_FLOOR and cv_resolved and sem_separated
          and pca_in_v1_band):
        verdict = "HARD_PASS"   # CEILING_FALSIFIED + PCA replicates v1
    elif (all_nontrace_below_real and sem_separated):
        verdict = "HARD_FAIL"   # TRUE substrate-physics ceiling at +0.05
    elif (winner_mean >= REAL_NONTRACE_CEIL and winner_mean < HP_NONTRACE_FLOOR
          and sem_separated):
        verdict = "MIDDLE_BAND"  # real signal above noise; not chain-grade
    # else MIDDLE_BAND default

    label = {"HARD_PASS": "CEILING_FALSIFIED_n_seeds_resolved",
             "HARD_FAIL": ("REGIME_BROKEN" if not crlb_sanity_ok
                          else "CEILING_REAL_TRUE_SUBSTRATE_PHYSICS"),
             "MIDDLE_BAND": "REAL_SIGNAL_BOUNDED_NOT_CHAIN_GRADE",
             "UNKNOWN": "UNKNOWN"}[verdict]

    # Arms-differ cross-seed check
    all_arms_differ = all(per_seed[s].get("arms_differ", False)
                          for s in seeds_sorted)

    verdict_msg = (
        "%s [%s] | winner=%s mean=%.3f (cv=%.3f, lb=%.3f) "
        "PCA=%.3f (v1_band=%s) Fisher=%.3f Single=%.3f Trace=%.3f Rand=%.3f | "
        "rand_clean=%s trace_sane=%s cv_resolved=%s sem_separated=%s "
        "crlb_k8=%.4f crlb_sanity_ok=%s arms_differ=%s | n_seeds=%d"
    ) % (
        verdict, label, winner_arm, winner_mean, winner_cv, winner_lb,
        pca_mean, pca_in_v1_band,
        fisher["mean_sel"], single["mean_sel"],
        trace_mean, rand_mean,
        rand_clean, trace_sane, cv_resolved, sem_separated,
        crlb_k8, crlb_sanity_ok,
        all_arms_differ, len(seeds_sorted),
    )

    return {
        "verdict": verdict,
        "verdict_label": label,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "per_arm": per_arm_full,
        "per_arm_summary": summary,
        "winner_arm": winner_arm,
        "winner_mean_sel": winner_mean,
        "winner_cv": winner_cv,
        "winner_mean_minus_1p96sem": winner_lb,
        "pca_mean_sel": pca_mean,
        "pca_in_v1_band": bool(pca_in_v1_band),
        "fisher_mean_sel": fisher["mean_sel"],
        "single_mean_sel": single["mean_sel"],
        "trace_mean_sel": trace_mean,
        "rand_mean_sel": rand_mean,
        "rand_clean": bool(rand_clean),
        "trace_sane": bool(trace_sane),
        "cv_resolved": bool(cv_resolved),
        "sem_separated": bool(sem_separated),
        "crlb_sanity_ok": bool(crlb_sanity_ok),
        "arms_differ": bool(all_arms_differ),
        "crlb_floor_k1": crlb_floor(M, N_DIM, 1),
        "crlb_floor_k8": crlb_k8,
        "n_seeds_complete": len(seeds_sorted),
        "expected_n_units": EXPECTED_N_UNITS,
        "completed_units": len(seeds_sorted) * len(EXPECTED_ARMS),
        "cardinality_ok": (len(seeds_sorted) * len(EXPECTED_ARMS)
                           >= EXPECTED_N_UNITS),
    }


def main() -> int:
    _RESULTS_HOLDER["started_at"] = time.time()
    env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
    out_dir = REPO / "data" / ("exp_" + env_name)
    out_dir.mkdir(parents=True, exist_ok=True)

    _write_minimal_metrics(out_dir, "STARTED",
                           "STARTED: pid=%d mode=%s device=%s"
                           % (os.getpid(), RUN_MODE, DEVICE),
                           extra={"_phase": "init", "expected_arms": EXPECTED_ARMS,
                                  "expected_seeds": SEEDS,
                                  "expected_n_units": EXPECTED_N_UNITS,
                                  "crlb_floor_k1": crlb_floor(M, N_DIM, 1),
                                  "crlb_floor_k8": crlb_floor(M, N_DIM, K_FISHER)})

    print("[%s] mode=%s device=%s N=%d M=%d seeds=%s K_FISHER=%d expected_n=%d "
          "crlb_k1=%.4f crlb_k8=%.4f" % (
        ANCHOR_NAME, RUN_MODE, DEVICE, N_DIM, M, SEEDS, K_FISHER, EXPECTED_N_UNITS,
        crlb_floor(M, N_DIM, 1), crlb_floor(M, N_DIM, K_FISHER)), flush=True)

    if SELF_TEST_MODE:
        try:
            r = run_one_seed(SEEDS[0])
            assert "per_arm" in r
            for arm in EXPECTED_ARMS:
                assert arm in r["per_arm"], "missing arm %s" % arm
                assert "sel_unretr" in r["per_arm"][arm]
                sel = r["per_arm"][arm]["sel_unretr"]
                assert isinstance(sel, float) and math.isfinite(sel), (
                    "self-test: arm %s sel not finite float: %r" % (arm, sel))
            # META_RULE_AF arms-must-differ
            assert r.get("arms_differ", False), (
                "self-test: META_RULE_AF arms_differ FAIL "
                "fingerprints=%s" % r.get("fingerprints"))
            crlb1 = crlb_floor(M, N_DIM, 1)
            crlb8 = crlb_floor(M, N_DIM, 8)
            assert crlb1 > crlb8 > 0, (
                "self-test: CRLB monotonicity broken k1=%.4f k8=%.4f"
                % (crlb1, crlb8))
            trace_sel = r["per_arm"]["trace_baseline"]["sel_unretr"]
            rand_sel = r["per_arm"]["baseline_rand"]["sel_unretr"]
            pca_sel = r["per_arm"]["eight_readout_pca_basis"]["sel_unretr"]
            _write_minimal_metrics(out_dir, "SELFTEST_OK",
                                   "SELFTEST_OK: structure verified "
                                   "(TRACE=%.3f, RAND=%.3f, PCA=%.3f, "
                                   "CRLB_k1=%.4f, CRLB_k8=%.4f, arms_differ=%s)"
                                   % (trace_sel, rand_sel, pca_sel,
                                      crlb1, crlb8, r.get("arms_differ")))
            print("[selftest] OK structure+arms-differ; signal-magnitude "
                  "sanity is smoke-only", flush=True)
            print("[selftest] N=%d M=%d (toy); TRACE=%.4f RAND=%.4f PCA=%.4f"
                  % (N_DIM, M, trace_sel, rand_sel, pca_sel), flush=True)
            return 0
        except Exception as e:
            _write_minimal_metrics(out_dir, "SELFTEST_FAIL",
                                   "SELFTEST_FAIL: %s" % e,
                                   extra={"_traceback": traceback.format_exc()})
            print("[selftest] FAIL: %s" % e, file=sys.stderr, flush=True)
            return 1

    run_config = {"N": N_DIM, "M": M, "K_FISHER": K_FISHER,
                  "run_mode": RUN_MODE, "anchor": ANCHOR_NAME}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print("[ckpt] %d/%d done; running %s" % (len(done), len(SEEDS), remaining), flush=True)

    for i, seed in enumerate(remaining):
        t0 = time.time()
        _write_minimal_metrics(out_dir, "RUNNING",
                               "RUNNING: seed=%d (%d/%d)" % (seed, i + 1, len(remaining)),
                               extra={"_phase": "seed_running", "_current_seed": seed})
        result = run_one_seed(seed)
        write_partial_key(out_dir, seed, result)
        print("[seed=%d] complete in %.1fs" % (seed, time.time() - t0), flush=True)

    per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
    final = aggregate_and_verdict(per_seed)
    final["anchor_name"] = ANCHOR_NAME
    final["elapsed_s"] = round(time.time() - _RESULTS_HOLDER["started_at"], 1)
    final["ts_iso"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    final["pid"] = os.getpid()
    final["run_mode"] = RUN_MODE
    final["device"] = DEVICE
    final["config_version"] = CONFIG_VERSION
    final["_hardening_marker"] = "v7B_n_seeds_scale"
    # META_RULE_AH atomic final write
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(final, indent=2), encoding="utf-8")
    os.replace(str(tmp), str(out_dir / "metrics.json"))
    print("[%s] DONE: %s" % (ANCHOR_NAME, final["verdict_msg"]), flush=True)
    return 0


if __name__ == "__main__":
    try:
        rc = main()
    except SystemExit:
        raise
    except BaseException as e:
        _write_import_crash_sentinel(e)
        print("[main] OUTER_EXCEPTION: %s" % e, file=sys.stderr, flush=True)
        traceback.print_exc()
        rc = 1
    sys.exit(rc)
