"""multi_readout_fisher_importance_v1 -- B2 importance-signal ceiling.

Hypothesis: +0.04-+0.08 sel_unretr ceiling on importance estimation is a
Cramer-Rao bound on single-scalar importance from HD superposition. k=8
INDEPENDENT readouts at orthogonal bases + Fisher-info-weighted fusion
should lift sel_unretr to +0.12-0.20.

ARMS (5):
  ARM_SINGLE_READOUT_BASELINE  current TRACE: 1 scalar readout per atom
  ARM_TWO_READOUT_AVG          k=2 orthogonal bases, simple-average fusion
  ARM_EIGHT_READOUT_FISHER     k=8 orthogonal Gaussian bases, Fisher-weighted
  ARM_EIGHT_READOUT_PCA_BASIS  k=8 substrate-native PCA-subspace bases
  ARM_DIAG_K_SWEEP             k in {1,2,4,8,16} diminishing-returns curve

PRE-REG BANDS (HARD-LOCKED at module init, PROSPECTIVE):
  HARD_PASS:  EIGHT_READOUT_FISHER sel_unretr >= +0.15, cv < 0.10 across seeds,
              lift over SINGLE >= +0.08, cor with |W| < 0.30 (fairness)
  MIDDLE_BAND: sel_unretr in [+0.08, +0.15) OR cor in [0.30, 0.50)
  HARD_FAIL:  sel_unretr < +0.08 OR cor >= 0.50 OR FISHER <= TWO_READOUT_AVG
  HONEST_BOUND: if ALL k arms cluster +0.04-0.08, ceiling IS encoder-bound

CARDINALITY (META_RULE_H):
  EXPECTED_N_UNITS_FULL  = 5 seeds * 5 arms = 25
  EXPECTED_N_UNITS_SMOKE = 2 seeds * 5 arms = 10

HARDENING: L1 early metrics, L2 per-arm progress, L3 outer try/except,
L4 import-crash sentinel.

Per-arm metrics structure (Fix #28):
  metrics["per_arm"] = {arm: {seed: {sel_unretr, cor_with_W}}}
  metrics["summary"] = {arm: {mean_sel, std_sel, cv_sel, mean_cor}}

ASCII-only; no emojis; self-contained.
Author: exp_dev 2026-06-27
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

ANCHOR_NAME = "multi_readout_fisher_importance_v1"

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE)
            else os.environ.get("HDLAB_RUN_MODE", "full").lower())
SELF_TEST_MODE = bool(_ARGS.self_test)

# Pre-reg bands LOCKED at module init
HP_SEL_FLOOR = 0.15
HP_LIFT_FLOOR = 0.08
HP_CV_MAX = 0.10
HP_COR_MAX = 0.30
MB_SEL_LO = 0.08
MB_COR_HI = 0.50
HONEST_BOUND_HI = 0.08
HONEST_BOUND_LO = 0.04

EXPECTED_ARMS = ["single_readout_baseline", "two_readout_avg",
                 "eight_readout_fisher", "eight_readout_pca_basis",
                 "diag_k_sweep"]

if SELF_TEST_MODE:
    N_DIM = 512
    M = 30
    SEEDS = [7]
    K_MAX = 4
elif RUN_MODE == "smoke":
    N_DIM = 2048
    M = 100
    SEEDS = [7, 17]
    K_MAX = 4
else:
    N_DIM = 8192
    M = 500
    SEEDS = [7, 17, 23, 31, 41]
    K_MAX = 16

K_SWEEP_VALUES = [1, 2, 4, 8] if K_MAX <= 8 else [1, 2, 4, 8, 16]
EXPECTED_N_UNITS = len(EXPECTED_ARMS) * len(SEEDS)

CONFIG_VERSION = (
    "ANCHOR=%s,N=%d,M=%d,seeds=%s,K_max=%d,mode=%s,"
    "HP_sel>=%.2f,HP_cv<=%.2f,HP_cor<=%.2f,expected_n=%d,"
    "hardening=L1early+L2perarm+L3outertry+L4importsentinel"
) % (
    ANCHOR_NAME, N_DIM, M, SEEDS, K_MAX, RUN_MODE,
    HP_SEL_FLOOR, HP_CV_MAX, HP_COR_MAX, EXPECTED_N_UNITS,
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
            "_hardening_marker": "v1_multi_readout_fisher",
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
            "_hardening_marker": "v1_multi_readout_fisher_import_crash",
        }
        (out_dir / "metrics.json").write_text(
            json.dumps(sentinel, indent=2), encoding="utf-8")
        (out_dir / "import_crash.json").write_text(
            json.dumps(sentinel, indent=2), encoding="utf-8")
    except Exception as e:
        print("[_write_import_crash_sentinel] FAIL: %s" % e, file=sys.stderr, flush=True)


# -------------------------- primitives --------------------------

def bipolar(M: int, n: int, g: np.random.Generator) -> np.ndarray:
    """Bipolar +/-1, L2-normalized. Shape (M, n)."""
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def gaussian(M: int, n: int, g: np.random.Generator) -> np.ndarray:
    """Gaussian, L2-normalized. Shape (M, n)."""
    X = g.standard_normal((M, n)).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def build_superposition(E: np.ndarray, w: np.ndarray) -> np.ndarray:
    """Weighted-sum superposition S = sum_j w_j * E[j]. Shape (n,)."""
    return (w[:, None] * E).sum(axis=0).astype(np.float32)


def importance_from_readouts(S: np.ndarray, E: np.ndarray,
                              readouts: np.ndarray) -> np.ndarray:
    """Estimate per-atom importance using k readout vectors.

    readouts: (k, n). For each atom j, importance_hat_j = sum_r |<S, e_j * r>|
    where r is a readout. Multi-readout = multiple independent random samples
    of the importance signal.

    Returns: (M,) importance estimate per atom.
    """
    M_atoms = E.shape[0]
    k = readouts.shape[0]
    n = E.shape[1]
    # For each readout r: score_j_r = |<S * r, e_j>|  (elementwise mult of S with r,
    # then dot with each atom). Approximates a sampling of importance.
    out = np.zeros(M_atoms, dtype=np.float32)
    for ri in range(k):
        r = readouts[ri]  # (n,)
        S_mod = S * r  # (n,)
        scores = np.abs(E @ S_mod)  # (M,)
        out += scores
    return out / float(k)


def fisher_weighted_fusion(per_readout_scores: np.ndarray) -> np.ndarray:
    """Fisher-info weighted fusion across readouts.

    per_readout_scores: (k, M)
    Returns: (M,) weighted-fused importance.

    Weights w_r = 1/var_r (Fisher info proxy under Gaussian-noise assumption).
    Apply weights atom-wise.
    """
    k, M_atoms = per_readout_scores.shape
    # Variance across readouts per atom (sampling variability)
    per_atom_var = per_readout_scores.var(axis=0) + 1e-6  # (M,)
    # Per-readout total variance (proxy for noise level of each readout)
    per_readout_var = per_readout_scores.var(axis=1) + 1e-6  # (k,)
    weights = 1.0 / per_readout_var  # (k,)
    weights = weights / weights.sum()  # normalize
    fused = (weights[:, None] * per_readout_scores).sum(axis=0)
    return fused


def per_readout_importance(S: np.ndarray, E: np.ndarray,
                            readouts: np.ndarray) -> np.ndarray:
    """Return (k, M) per-readout importance scores (for Fisher fusion)."""
    k = readouts.shape[0]
    M_atoms = E.shape[0]
    out = np.zeros((k, M_atoms), dtype=np.float32)
    for ri in range(k):
        r = readouts[ri]
        S_mod = S * r
        out[ri] = np.abs(E @ S_mod)
    return out


def make_pca_basis(E: np.ndarray, k: int,
                    g: np.random.Generator) -> np.ndarray:
    """Substrate-native PCA: top-k principal directions of E.

    Returns (k, n) basis. If k > min(M, n), pad with random gaussians.
    """
    M, n = E.shape
    # Center
    Em = E - E.mean(axis=0, keepdims=True)
    # SVD for top-k components; cap k to feasible
    k_eff = min(k, min(M, n))
    try:
        U, sval, Vt = np.linalg.svd(Em, full_matrices=False)
        basis = Vt[:k_eff]  # (k_eff, n)
    except np.linalg.LinAlgError:
        basis = gaussian(k_eff, n, g)
    basis = basis / (np.linalg.norm(basis, axis=1, keepdims=True) + 1e-8)
    if k_eff < k:
        # Pad with random Gaussian (rare; only for very small inputs)
        extra = gaussian(k - k_eff, n, g)
        basis = np.concatenate([basis, extra], axis=0)
    return basis.astype(np.float32)


def sel_unretr_metric(imp_hat: np.ndarray, w_true: np.ndarray,
                       retr_mask: np.ndarray) -> float:
    """Selectivity-for-unretrieved metric: among un-retrieved atoms, does
    importance estimate correctly rank by true weight?

    Returns Spearman-like rank correlation in [-1, 1] restricted to unretrieved.
    Substrate convention: positive = retains correct importance among non-retrieved.
    """
    unretr = ~retr_mask
    if unretr.sum() < 3:
        return 0.0
    h = imp_hat[unretr]
    w = w_true[unretr]
    # Spearman rho: rank-correlation between h and w
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


# -------------------------- arms --------------------------

def run_arm_single_readout(E: np.ndarray, S: np.ndarray, w: np.ndarray,
                            retr_mask: np.ndarray,
                            g: np.random.Generator) -> Tuple[float, float]:
    readouts = gaussian(1, E.shape[1], g)
    imp = importance_from_readouts(S, E, readouts)
    return sel_unretr_metric(imp, w, retr_mask), cor_with_W(imp, w)


def run_arm_two_readout_avg(E: np.ndarray, S: np.ndarray, w: np.ndarray,
                             retr_mask: np.ndarray,
                             g: np.random.Generator) -> Tuple[float, float]:
    # Two orthogonal Gaussian readouts via QR
    raw = gaussian(2, E.shape[1], g)
    Q, _ = np.linalg.qr(raw.T)
    readouts = Q.T[:2]
    imp = importance_from_readouts(S, E, readouts)
    return sel_unretr_metric(imp, w, retr_mask), cor_with_W(imp, w)


def run_arm_eight_readout_fisher(E: np.ndarray, S: np.ndarray, w: np.ndarray,
                                  retr_mask: np.ndarray, k: int,
                                  g: np.random.Generator) -> Tuple[float, float]:
    raw = gaussian(k, E.shape[1], g)
    Q, _ = np.linalg.qr(raw.T)
    readouts = Q.T[:k]
    per_r = per_readout_importance(S, E, readouts)
    fused = fisher_weighted_fusion(per_r)
    return sel_unretr_metric(fused, w, retr_mask), cor_with_W(fused, w)


def run_arm_eight_readout_pca(E: np.ndarray, S: np.ndarray, w: np.ndarray,
                               retr_mask: np.ndarray, k: int,
                               g: np.random.Generator) -> Tuple[float, float]:
    readouts = make_pca_basis(E, k, g)
    per_r = per_readout_importance(S, E, readouts)
    fused = fisher_weighted_fusion(per_r)
    return sel_unretr_metric(fused, w, retr_mask), cor_with_W(fused, w)


def run_arm_diag_k_sweep(E: np.ndarray, S: np.ndarray, w: np.ndarray,
                          retr_mask: np.ndarray,
                          g: np.random.Generator) -> Dict[str, float]:
    """Diagnostic: k in K_SWEEP_VALUES; record sel_unretr per k."""
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
    # Random weights (mostly small, some large; tests selectivity)
    w = g.standard_normal(M).astype(np.float32) * 0.3
    # 30% retrieved (large weight); 70% un-retrieved (smaller weight)
    retr_mask = np.zeros(M, dtype=bool)
    top_idx = np.argsort(np.abs(w))[-int(M * 0.3):]
    retr_mask[top_idx] = True
    S = build_superposition(E, w)

    # Choose k_fisher (8 if K_MAX >= 8 else K_MAX)
    k_fisher = min(8, K_MAX)

    arm_results: Dict[str, Dict[str, float]] = {}
    sel, cor = run_arm_single_readout(E, S, w, retr_mask, g)
    arm_results["single_readout_baseline"] = {"sel_unretr": sel, "cor_with_W": cor}

    sel, cor = run_arm_two_readout_avg(E, S, w, retr_mask, g)
    arm_results["two_readout_avg"] = {"sel_unretr": sel, "cor_with_W": cor}

    sel, cor = run_arm_eight_readout_fisher(E, S, w, retr_mask, k_fisher, g)
    arm_results["eight_readout_fisher"] = {"sel_unretr": sel, "cor_with_W": cor}

    sel, cor = run_arm_eight_readout_pca(E, S, w, retr_mask, k_fisher, g)
    arm_results["eight_readout_pca_basis"] = {"sel_unretr": sel, "cor_with_W": cor}

    k_sweep = run_arm_diag_k_sweep(E, S, w, retr_mask, g)
    arm_results["diag_k_sweep"] = {"sel_unretr": k_sweep.get("k%d" % k_fisher, 0.0),
                                    "cor_with_W": 0.0,
                                    "k_sweep_detail": k_sweep}

    return {
        "seed": int(seed),
        "N": N_DIM,
        "M": M,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
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
            sd_sel = float(np.std(sel_vals))
            cv = sd_sel / abs(m_sel) if abs(m_sel) > 1e-6 else 0.0
            summary[arm] = {
                "mean_sel": m_sel, "std_sel": sd_sel, "cv_sel": cv,
                "mean_cor": float(np.mean(cor_vals)), "n": len(sel_vals),
            }
        else:
            summary[arm] = {"mean_sel": 0.0, "std_sel": 0.0, "cv_sel": 0.0,
                            "mean_cor": 0.0, "n": 0}

    # Decision
    fisher = summary["eight_readout_fisher"]
    single = summary["single_readout_baseline"]
    two = summary["two_readout_avg"]
    fisher_sel = fisher["mean_sel"]
    single_sel = single["mean_sel"]
    two_sel = two["mean_sel"]
    fisher_cv = fisher["cv_sel"]
    fisher_cor = fisher["mean_cor"]
    lift = fisher_sel - single_sel

    # Honest-bound: all k-arms in [0.04, 0.08]
    all_sels = [summary[a]["mean_sel"] for a in EXPECTED_ARMS
                if a != "diag_k_sweep"]
    all_clustered = all(HONEST_BOUND_LO <= s <= HONEST_BOUND_HI for s in all_sels)

    verdict = "MIDDLE_BAND"
    if all_clustered:
        verdict = "HONEST_BOUND"
    elif (fisher_sel >= HP_SEL_FLOOR and fisher_cv < HP_CV_MAX and
            lift >= HP_LIFT_FLOOR and fisher_cor < HP_COR_MAX):
        verdict = "HARD_PASS"
    elif (fisher_sel < HP_LIFT_FLOOR or fisher_cor >= MB_COR_HI or
            fisher_sel <= two_sel):
        verdict = "HARD_FAIL"

    verdict_msg = (
        "%s | Fisher=%.3f Single=%.3f Two=%.3f | lift=%.3f cv=%.3f cor=%.3f | n=%d"
    ) % (verdict, fisher_sel, single_sel, two_sel, lift, fisher_cv,
         fisher_cor, len(seeds_sorted))

    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "per_arm": per_arm_full,
        "per_arm_summary": summary,
        "lift_fisher_over_single": lift,
        "fisher_cv": fisher_cv,
        "fisher_cor": fisher_cor,
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
                                  "expected_n_units": EXPECTED_N_UNITS})

    print("[%s] mode=%s N=%d M=%d seeds=%s K_MAX=%d expected_n=%d" % (
        ANCHOR_NAME, RUN_MODE, N_DIM, M, SEEDS, K_MAX, EXPECTED_N_UNITS), flush=True)

    if SELF_TEST_MODE:
        try:
            r = run_one_seed(SEEDS[0])
            assert "per_arm" in r
            for arm in EXPECTED_ARMS:
                assert arm in r["per_arm"]
                assert "sel_unretr" in r["per_arm"][arm]
            _write_minimal_metrics(out_dir, "SELFTEST_OK",
                                   "SELFTEST_OK: per-arm structure verified")
            print("[selftest] OK", flush=True)
            return 0
        except Exception as e:
            _write_minimal_metrics(out_dir, "SELFTEST_FAIL",
                                   "SELFTEST_FAIL: %s" % e,
                                   extra={"_traceback": traceback.format_exc()})
            print("[selftest] FAIL: %s" % e, file=sys.stderr, flush=True)
            return 1

    run_config = {"N": N_DIM, "M": M, "run_mode": RUN_MODE, "anchor": ANCHOR_NAME}
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
    final["_hardening_marker"] = "v1_multi_readout_fisher"
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
