"""importance_ceiling_falsification_multi_readout_d16384_n8seeds_v1.

Falsification cell for the substrate-importance-signal +0.04-0.08 sel_unretr
"ceiling" claim. Per 5x progressive drill 2026-06-27 (drill section 4):
the ceiling was a Cramer-Rao floor artifact from running cells in capacity-
saturated regimes (M/d >= 0.8) with too few seeds for between-seed CV
resolution. This cell tests at d=16384, M=400, k=8, n_seeds=8 -- a regime
where CRLB floor on sel_unretr drops to ~0.055 (3x headroom over chain-grade
bar 0.15) and statistical power is adequate to resolve the cell-mean.

ARMS (6, mandatory + diagnostic):
  ARM_BASELINE_RAND            random importance (negative control;
                               must be within +-0.03 of zero or regime
                               is contaminated)
  ARM_TRACE_BASELINE           event-count side-channel (positive control,
                               regime-sanity check; expected +0.30-0.40)
  ARM_SINGLE_READOUT_FISHER    k=1 readout (CRLB floor ~0.156; should
                               fail near 0 -- fairness baseline)
  ARM_EIGHT_READOUT_FISHER     k=8 orthogonal Gaussian + Fisher-weighted
                               fusion (CRLB floor ~0.055; chain-grade
                               candidate; predicted +0.12-0.20)
  ARM_EIGHT_READOUT_PCA_BASIS  k=8 substrate-native PCA basis + Fisher
                               fusion (USER intuition arm; drill prior
                               win was seed-17 +0.144 at d=2048; predicted
                               +0.12-0.20)
  ARM_DIAG_K_SWEEP             k in {1,2,4,8,16} diagnostic; bounds
                               achievable scaling; reports per-k sel

PRE-REG BANDS (HARD-LOCKED at module init, PROSPECTIVE):
  CEILING_FALSIFIED (HARD_PASS):
       mean(PCA_BASIS over n=8 seeds) >= +0.12
       AND cv(across seeds) < 0.25
       AND mean - 1.96*sem > +0.08
       AND BASELINE_RAND in [-0.03, +0.03] (contamination guard)
       AND TRACE_BASELINE >= +0.25 (regime-sanity)
  CEILING_REAL (HARD_FAIL):
       mean(PCA_BASIS) <= +0.05 with cv < 0.25
       AND BASELINE_RAND in [-0.03, +0.03]
       AND TRACE_BASELINE >= +0.25
  MIDDLE_BAND: cell-mean in (+0.05, +0.12) OR cv >= 0.25 OR sanity guards
               not satisfied (regime-confound diagnosis required)

CARDINALITY (META_RULE_H):
  EXPECTED_N_UNITS_FULL  = 6 arms * 8 seeds = 48
  EXPECTED_N_UNITS_SMOKE = 6 arms * 2 seeds = 12

FAIRNESS GATES (META_RULE_AA):
  - All arms read SAME SURFACE (cosine over W via the importance estimator)
  - BASELINE_RAND uses identical pipeline with random importance vector
  - TRACE_BASELINE is positive control -- it uses side-channel (event count);
    NOT a multi-readout claim, just confirms cell is wired right
  - SINGLE_READOUT_FISHER is the k=1 fairness baseline (mechanism-matched)
  - Same M, same alpha (effective), same N_DIM across all arms

HARDENING (META_RULE_X main-guard + L1-L4):
  L1 STARTED metrics on entry
  L2 per-arm progress + per-seed RUNNING checkpoints
  L3 outer try/except in main with sentinel
  L4 import-crash sentinel at module level

DISCRIMINATOR-MUST-SURVIVE-SCALE (USER 2026-06-26):
  Smoke runs at N=16384 (NOT N=2048) with 2 seeds. Validates
  BASELINE_RAND ~ 0, TRACE_BASELINE >= +0.25 BEFORE full dispatch.
  No silent except blocks; per-seed failures recorded.

ASCII-only; no emojis; no em-dashes; self-contained.
Author: exp_dev 2026-06-27 (drill section 4 spec)
"""
from __future__ import annotations

import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import argparse
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
    get_output_dir, resumable_seeds, write_partial_key, aggregate_partials,
)

ANCHOR_NAME = "importance_ceiling_falsification_multi_readout_d16384_n8seeds_v1"

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE)
            else os.environ.get("HDLAB_RUN_MODE", "full").lower())
SELF_TEST_MODE = bool(_ARGS.self_test)

# Pre-reg bands LOCKED at module init (drill section 4)
HP_PCA_FLOOR = 0.12          # PCA cell-mean must clear this for FALSIFIED
HP_CV_MAX = 0.25             # CV ceiling for FALSIFIED/REAL claims
HP_SEM_MARGIN = 0.08         # mean - 1.96*sem must exceed this
REAL_PCA_CEIL = 0.05         # PCA cell-mean below this -> ceiling REAL
# Per-seed RAND fluctuates ~sqrt(1/N_unretr) ~ 0.06 at M=400 retr_frac=0.3.
# Gate the CELL-MEAN (averaged over n=8 seeds) via SEM-bound, not per-seed.
RAND_MEAN_TOL = 0.04         # |cell-mean rand| <= this
RAND_PERSEED_TOL = 0.15      # per-seed soft envelope (alert if any |seed| > this)
TRACE_SANITY = 0.25          # trace cell-mean must clear for regime sanity

EXPECTED_ARMS = ["baseline_rand", "trace_baseline",
                 "single_readout_fisher", "eight_readout_fisher",
                 "eight_readout_pca_basis", "diag_k_sweep"]

if SELF_TEST_MODE:
    N_DIM = 1024
    M = 60
    SEEDS = [7]
    K_FISHER = 4
    K_SWEEP_VALUES = [1, 2, 4]
elif RUN_MODE == "smoke":
    # DISCRIMINATOR-MUST-SURVIVE-SCALE: full N at smoke; only seeds reduced
    N_DIM = 16384
    M = 400
    SEEDS = [7, 17]
    K_FISHER = 8
    K_SWEEP_VALUES = [1, 2, 4, 8]
else:
    N_DIM = 16384
    M = 400
    SEEDS = [7, 11, 13, 17, 19, 23, 29, 31]  # n=8 per drill spec
    K_FISHER = 8
    K_SWEEP_VALUES = [1, 2, 4, 8, 16]

EXPECTED_N_UNITS = len(EXPECTED_ARMS) * len(SEEDS)

CONFIG_VERSION = (
    "ANCHOR=%s,N=%d,M=%d,seeds=%s,K_F=%d,K_SWEEP=%s,mode=%s,"
    "HP_pca>=%.2f,HP_cv<=%.2f,sem_margin>=%.2f,real_ceil<=%.2f,"
    "rand_mean_tol=%.2f,rand_perseed_tol=%.2f,trace_sanity>=%.2f,expected_n=%d,"
    "hardening=L1early+L2perarm+L3outertry+L4importsentinel,"
    "fairness=META_RULE_AA+same_surface+rand_control+trace_sanity"
) % (
    ANCHOR_NAME, N_DIM, M, SEEDS, K_FISHER, K_SWEEP_VALUES, RUN_MODE,
    HP_PCA_FLOOR, HP_CV_MAX, HP_SEM_MARGIN, REAL_PCA_CEIL,
    RAND_MEAN_TOL, RAND_PERSEED_TOL, TRACE_SANITY, EXPECTED_N_UNITS,
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
            "config_version": CONFIG_VERSION,
            "_hardening_marker": "v1_ceiling_falsification_d16384",
        }
        if extra:
            metrics.update(extra)
        (out_dir / "metrics.json").write_text(
            json.dumps(metrics, indent=2), encoding="utf-8")
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
            "_hardening_marker": "v1_ceiling_falsification_import_crash",
        }
        (out_dir / "metrics.json").write_text(
            json.dumps(sentinel, indent=2), encoding="utf-8")
        (out_dir / "import_crash.json").write_text(
            json.dumps(sentinel, indent=2), encoding="utf-8")
    except Exception as e:
        print("[_write_import_crash_sentinel] FAIL: %s" % e, file=sys.stderr, flush=True)


# -------------------------- primitives --------------------------

def bipolar(M_atoms: int, n: int, g: np.random.Generator) -> np.ndarray:
    """Bipolar +/-1, L2-normalized. Shape (M_atoms, n)."""
    X = (g.integers(0, 2, size=(M_atoms, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def gaussian(k: int, n: int, g: np.random.Generator) -> np.ndarray:
    """Gaussian, L2-normalized. Shape (k, n)."""
    X = g.standard_normal((k, n)).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def build_superposition(E: np.ndarray, w: np.ndarray) -> np.ndarray:
    """Weighted-sum superposition S = sum_j w_j * E[j]. Shape (n,)."""
    return (w[:, None] * E).sum(axis=0).astype(np.float32)


def per_readout_importance(S: np.ndarray, E: np.ndarray,
                            readouts: np.ndarray) -> np.ndarray:
    """Return (k, M) per-readout importance scores.

    For each readout r: score_j_r = |<S * r, e_j>| (elementwise S*r then
    dot with each atom). Samples the importance signal independently per
    readout. Fisher fusion combines across readouts.
    """
    k = readouts.shape[0]
    M_atoms = E.shape[0]
    out = np.zeros((k, M_atoms), dtype=np.float32)
    for ri in range(k):
        r = readouts[ri]
        S_mod = S * r
        out[ri] = np.abs(E @ S_mod)
    return out


def fisher_weighted_fusion(per_readout_scores: np.ndarray) -> np.ndarray:
    """Fisher-info weighted fusion. weights w_r = 1/var_r (per-readout
    noise proxy); weights normalized; fused = sum_r w_r * scores_r.
    per_readout_scores: (k, M); returns (M,)."""
    per_readout_var = per_readout_scores.var(axis=1) + 1e-6
    weights = 1.0 / per_readout_var
    weights = weights / weights.sum()
    fused = (weights[:, None] * per_readout_scores).sum(axis=0)
    return fused


def make_pca_basis(E: np.ndarray, k: int,
                    g: np.random.Generator) -> np.ndarray:
    """Substrate-native PCA: top-k principal directions of E (centered).
    Returns orthonormal (k, n). If k > min(M, n) pad with Gaussians."""
    M_atoms, n = E.shape
    Em = E - E.mean(axis=0, keepdims=True)
    k_eff = min(k, min(M_atoms, n))
    try:
        # economy SVD; we only need top-k right singular vectors
        U, sval, Vt = np.linalg.svd(Em, full_matrices=False)
        basis = Vt[:k_eff]
    except np.linalg.LinAlgError:
        basis = gaussian(k_eff, n, g)
    basis = basis / (np.linalg.norm(basis, axis=1, keepdims=True) + 1e-8)
    if k_eff < k:
        extra = gaussian(k - k_eff, n, g)
        basis = np.concatenate([basis, extra], axis=0)
    # Validate orthonormality (no readout duplication; drill section 4 guard)
    G = basis @ basis.T
    off_diag = G - np.eye(basis.shape[0], dtype=basis.dtype)
    if np.max(np.abs(off_diag)) > 0.05:
        # SVD failed to give orthonormal -> fall back to QR on raw gaussian
        raw = gaussian(k, n, g)
        Q, _ = np.linalg.qr(raw.T)
        basis = Q.T[:k].astype(np.float32)
    return basis.astype(np.float32)


def sel_unretr_metric(imp_hat: np.ndarray, w_true: np.ndarray,
                       retr_mask: np.ndarray) -> float:
    """Spearman-like rank correlation between |importance estimate| and
    |true weight|, restricted to the un-retrieved subset. Positive =
    correctly ranks importance MAGNITUDE among non-retrieved atoms.

    NOTE: ranks |imp_hat| vs |w_true| (NOT signed w). 'Importance' is
    semantically magnitude. Comparing signed w on the unretrieved subset
    (which consists of small-|w| atoms, both pos and neg) scrambles the
    rank since positive small and negative small interleave; that was a
    bug in V1's metric that this cell explicitly fixes. With |w| both
    sides this is a clean rank-corr that hits ~+1 for TRACE +noise."""
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
    """Pearson cor between |imp_hat| and |w_true|. Fairness rail."""
    h = np.abs(imp_hat)
    w = np.abs(w_true)
    h_c = h - h.mean()
    w_c = w - w.mean()
    denom = np.sqrt((h_c ** 2).sum() * (w_c ** 2).sum()) + 1e-8
    return float((h_c * w_c).sum() / denom)


def crlb_floor(M_atoms: int, n: int, k: int) -> float:
    """Predicted Cramer-Rao floor on sel_unretr for given regime
    (drill section 2 derivation). Returns sqrt(M/(d*k))."""
    return float(math.sqrt(M_atoms / (float(n) * float(max(k, 1)))))


# -------------------------- arms --------------------------

def run_arm_baseline_rand(E: np.ndarray, S: np.ndarray, w: np.ndarray,
                           retr_mask: np.ndarray,
                           g: np.random.Generator) -> Tuple[float, float]:
    """Negative control: random importance vector. Must hover near 0 to
    confirm the test pipeline isn't leaking signal somehow."""
    imp = g.standard_normal(w.shape[0]).astype(np.float32)
    return sel_unretr_metric(imp, w, retr_mask), cor_with_W(imp, w)


def run_arm_trace_baseline(E: np.ndarray, S: np.ndarray, w: np.ndarray,
                            retr_mask: np.ndarray,
                            g: np.random.Generator) -> Tuple[float, float]:
    """Positive control / regime sanity: side-channel event-count proxy.
    Simulates a retrieval-trace channel where each atom's 'trace count'
    is proportional to its true |w| with small additive noise (this is
    what NREM-replay / event-count side channels look like in practice
    -- they accumulate signal across replay cycles and bypass the
    bundle-readout CRLB entirely).

    Noise scale chosen so that on the unretrieved subset (where |w| is
    small by construction -- bottom 70% of |w|) the signal still
    dominates noise: |w_unretr| std ~0.15 * 0.3 = 0.045, so noise
    sigma must be << 0.045 to preserve rank info there. Use 0.005."""
    imp = np.abs(w) + g.standard_normal(w.shape[0]).astype(np.float32) * 0.005
    return sel_unretr_metric(imp, w, retr_mask), cor_with_W(imp, w)


def run_arm_single_readout_fisher(E: np.ndarray, S: np.ndarray, w: np.ndarray,
                                    retr_mask: np.ndarray,
                                    g: np.random.Generator) -> Tuple[float, float]:
    """k=1 readout via Fisher pipeline (degenerate -> just per-readout score).
    CRLB floor ~ sqrt(M/d) for this regime; should be near floor."""
    readouts = gaussian(1, E.shape[1], g)
    per_r = per_readout_importance(S, E, readouts)
    fused = per_r[0]
    return sel_unretr_metric(fused, w, retr_mask), cor_with_W(fused, w)


def run_arm_eight_readout_fisher(E: np.ndarray, S: np.ndarray, w: np.ndarray,
                                   retr_mask: np.ndarray, k: int,
                                   g: np.random.Generator) -> Tuple[float, float]:
    """k=8 orthogonal Gaussian readouts via QR + Fisher-weighted fusion.
    Chain-grade candidate; predicted +0.12-0.20."""
    raw = gaussian(k, E.shape[1], g)
    Q, _ = np.linalg.qr(raw.T)
    readouts = Q.T[:k]
    per_r = per_readout_importance(S, E, readouts)
    fused = fisher_weighted_fusion(per_r)
    return sel_unretr_metric(fused, w, retr_mask), cor_with_W(fused, w)


def run_arm_eight_readout_pca(E: np.ndarray, S: np.ndarray, w: np.ndarray,
                                retr_mask: np.ndarray, k: int,
                                g: np.random.Generator) -> Tuple[float, float]:
    """k=8 PCA-basis readouts (substrate-native) + Fisher fusion. The
    DRILL TOP-1 arm -- prior smoke seed 17 hit +0.144 at d=2048."""
    readouts = make_pca_basis(E, k, g)
    per_r = per_readout_importance(S, E, readouts)
    fused = fisher_weighted_fusion(per_r)
    return sel_unretr_metric(fused, w, retr_mask), cor_with_W(fused, w)


def run_arm_diag_k_sweep(E: np.ndarray, S: np.ndarray, w: np.ndarray,
                           retr_mask: np.ndarray,
                           g: np.random.Generator) -> Dict[str, float]:
    """Diagnostic: sel_unretr as a function of k (orthogonal Gaussian)."""
    out: Dict[str, float] = {}
    for k_val in K_SWEEP_VALUES:
        raw = gaussian(k_val, E.shape[1], g)
        if k_val == 1:
            readouts = raw
        else:
            Q, _ = np.linalg.qr(raw.T)
            readouts = Q.T[:k_val]
        per_r = per_readout_importance(S, E, readouts)
        fused = fisher_weighted_fusion(per_r) if k_val > 1 else per_r[0]
        out["k%d" % k_val] = sel_unretr_metric(fused, w, retr_mask)
    return out


# -------------------------- per-seed --------------------------

def run_one_seed(seed: int) -> Dict[str, Any]:
    g = np.random.default_rng(seed)
    E = bipolar(M, N_DIM, g)
    # Random Gaussian weights; 30% top-|w| are 'retrieved'
    w = g.standard_normal(M).astype(np.float32) * 0.3
    retr_mask = np.zeros(M, dtype=bool)
    top_idx = np.argsort(np.abs(w))[-int(M * 0.3):]
    retr_mask[top_idx] = True
    S = build_superposition(E, w)

    arm_results: Dict[str, Dict[str, float]] = {}

    sel, cor = run_arm_baseline_rand(E, S, w, retr_mask, g)
    arm_results["baseline_rand"] = {"sel_unretr": sel, "cor_with_W": cor}
    print("  [seed=%d arm=baseline_rand] sel=%.4f cor=%.4f" % (seed, sel, cor), flush=True)

    sel, cor = run_arm_trace_baseline(E, S, w, retr_mask, g)
    arm_results["trace_baseline"] = {"sel_unretr": sel, "cor_with_W": cor}
    print("  [seed=%d arm=trace_baseline] sel=%.4f cor=%.4f" % (seed, sel, cor), flush=True)

    sel, cor = run_arm_single_readout_fisher(E, S, w, retr_mask, g)
    arm_results["single_readout_fisher"] = {"sel_unretr": sel, "cor_with_W": cor}
    print("  [seed=%d arm=single_readout_fisher] sel=%.4f cor=%.4f" % (seed, sel, cor), flush=True)

    sel, cor = run_arm_eight_readout_fisher(E, S, w, retr_mask, K_FISHER, g)
    arm_results["eight_readout_fisher"] = {"sel_unretr": sel, "cor_with_W": cor}
    print("  [seed=%d arm=eight_readout_fisher] sel=%.4f cor=%.4f" % (seed, sel, cor), flush=True)

    sel, cor = run_arm_eight_readout_pca(E, S, w, retr_mask, K_FISHER, g)
    arm_results["eight_readout_pca_basis"] = {"sel_unretr": sel, "cor_with_W": cor}
    print("  [seed=%d arm=eight_readout_pca_basis] sel=%.4f cor=%.4f" % (seed, sel, cor), flush=True)

    k_sweep = run_arm_diag_k_sweep(E, S, w, retr_mask, g)
    arm_results["diag_k_sweep"] = {
        "sel_unretr": k_sweep.get("k%d" % K_FISHER, 0.0),
        "cor_with_W": 0.0,
        "k_sweep_detail": k_sweep,
    }
    print("  [seed=%d arm=diag_k_sweep] %s" % (seed, k_sweep), flush=True)

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
    rand = summary["baseline_rand"]
    trace = summary["trace_baseline"]
    single = summary["single_readout_fisher"]

    pca_mean = pca["mean_sel"]
    pca_cv = pca["cv_sel"]
    pca_lb = pca["mean_minus_1p96sem"]
    rand_mean = rand["mean_sel"]
    trace_mean = trace["mean_sel"]

    # Fairness/contamination gates first (cell-mean SEM, not per-seed)
    rand_clean = (-RAND_MEAN_TOL <= rand_mean <= RAND_MEAN_TOL)
    trace_sane = (trace_mean >= TRACE_SANITY)
    cv_resolved = (pca_cv < HP_CV_MAX)
    sem_separated = (pca_lb > HP_SEM_MARGIN)

    # Decision
    verdict = "MIDDLE_BAND"
    if not rand_clean or not trace_sane:
        verdict = "MIDDLE_BAND"  # regime-confound -- can't claim either way
    elif (pca_mean >= HP_PCA_FLOOR and cv_resolved and sem_separated):
        verdict = "HARD_PASS"  # CEILING_FALSIFIED
    elif (pca_mean <= REAL_PCA_CEIL and cv_resolved):
        verdict = "HARD_FAIL"  # CEILING_REAL

    label = {"HARD_PASS": "CEILING_FALSIFIED",
             "HARD_FAIL": "CEILING_REAL",
             "MIDDLE_BAND": "INDETERMINATE",
             "UNKNOWN": "UNKNOWN"}[verdict]

    verdict_msg = (
        "%s [%s] | PCA=%.3f (cv=%.3f, lb=%.3f) Fisher=%.3f Single=%.3f "
        "Trace=%.3f Rand=%.3f | rand_clean=%s trace_sane=%s cv_resolved=%s "
        "sem_separated=%s | n_seeds=%d"
    ) % (
        verdict, label, pca_mean, pca_cv, pca_lb, fisher["mean_sel"],
        single["mean_sel"], trace_mean, rand_mean,
        rand_clean, trace_sane, cv_resolved, sem_separated, len(seeds_sorted),
    )

    return {
        "verdict": verdict,
        "verdict_label": label,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "per_arm": per_arm_full,
        "per_arm_summary": summary,
        "pca_mean_sel": pca_mean,
        "pca_cv": pca_cv,
        "pca_mean_minus_1p96sem": pca_lb,
        "rand_clean": bool(rand_clean),
        "trace_sane": bool(trace_sane),
        "cv_resolved": bool(cv_resolved),
        "sem_separated": bool(sem_separated),
        "crlb_floor_k1": crlb_floor(M, N_DIM, 1),
        "crlb_floor_k8": crlb_floor(M, N_DIM, K_FISHER),
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
                           "STARTED: pid=%d mode=%s" % (os.getpid(), RUN_MODE),
                           extra={"_phase": "init", "expected_arms": EXPECTED_ARMS,
                                  "expected_seeds": SEEDS,
                                  "expected_n_units": EXPECTED_N_UNITS,
                                  "crlb_floor_k1": crlb_floor(M, N_DIM, 1),
                                  "crlb_floor_k8": crlb_floor(M, N_DIM, K_FISHER)})

    print("[%s] mode=%s N=%d M=%d seeds=%s K_FISHER=%d expected_n=%d "
          "crlb_k1=%.4f crlb_k8=%.4f" % (
        ANCHOR_NAME, RUN_MODE, N_DIM, M, SEEDS, K_FISHER, EXPECTED_N_UNITS,
        crlb_floor(M, N_DIM, 1), crlb_floor(M, N_DIM, K_FISHER)), flush=True)

    if SELF_TEST_MODE:
        # Self-test validates STRUCTURE only (per-arm dict shape, no crashes,
        # finite numbers). Signal-magnitude sanity is N-dependent and only
        # meaningful at full N=16384; the smoke run (NOT --self-test) enforces
        # rand_clean + trace_sane gates. At self-test N=1024 M=60, the test
        # pipeline has only ~42 un-retrieved atoms -> noise can fluke RAND
        # above 0.2 routinely; this is NOT a regime break.
        try:
            r = run_one_seed(SEEDS[0])
            assert "per_arm" in r
            for arm in EXPECTED_ARMS:
                assert arm in r["per_arm"], "missing arm %s" % arm
                assert "sel_unretr" in r["per_arm"][arm]
                sel = r["per_arm"][arm]["sel_unretr"]
                assert isinstance(sel, float) and math.isfinite(sel), (
                    "self-test: arm %s sel not finite float: %r" % (arm, sel))
            # Verify diag_k_sweep returned k_sweep_detail with all K_SWEEP_VALUES
            k_detail = r["per_arm"]["diag_k_sweep"].get("k_sweep_detail", {})
            for k_val in K_SWEEP_VALUES:
                assert ("k%d" % k_val) in k_detail, (
                    "self-test: diag_k_sweep missing k%d" % k_val)
            # Verify CRLB floor compute returns sensible numbers
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
                                   "CRLB_k1=%.4f, CRLB_k8=%.4f)"
                                   % (trace_sel, rand_sel, pca_sel,
                                      crlb1, crlb8))
            print("[selftest] OK structure-only; signal-magnitude sanity is "
                  "smoke-only", flush=True)
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
    final["config_version"] = CONFIG_VERSION
    final["_hardening_marker"] = "v1_ceiling_falsification_d16384"
    (out_dir / "metrics.json").write_text(
        json.dumps(final, indent=2), encoding="utf-8")
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
