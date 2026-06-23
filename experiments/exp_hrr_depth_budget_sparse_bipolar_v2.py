"""hrr_depth_budget_sparse_bipolar_v2 -- W-free Hopfield recall under FLIP cue-noise (corrected metric).

v1 (bundle/top-M cleanup) was wrong-paradigm vs CERT 592 (Willshaw W-free
super-capacity). v2 corrects: replace bundle-cleanup with W-free Hopfield
recall paradigm from exp_sparse_boundary_v2_cpu_v1, sweep M to find alpha_c
per arm (f), and compute lift = alpha_c(f=0.02) / alpha_c(f=1.0).

Per-pattern protocol (one trial per stored pattern):
  - Store M K-sparse bipolar patterns into P (M, N); K = max(1, round(f*N)).
  - Build implicit W = P.T @ P (correlation matrix, no learning step).
  - For each pattern, flip 5% of its nonzero positions to make cue.
  - Recall: r = sign((cue @ P.T) @ P - cue * diag(P @ P.T)); subtract self-bias.
  - Exact recovery on nonzero positions: r[nz] == pattern[nz].
  - recall_mean = correct_patterns / M.
  - alpha_c(f) = largest M/N where recall_mean >= 0.95.

Arms (5): dense f=1.0 + sparse f=[0.1, 0.05, 0.02, 0.01] at N_DIM=4096.
M_GRID per arm: dense pinned near theoretical alpha=0.14*N (~570); sparse
exponential search up to alpha=40 (M ~ 164k) to catch Willshaw super-capacity.
Early-termination: once recall drops <0.95 at M_i, alpha_c = M_{i-1}/N (no
further M points). alpha_c_capped flag if recall>=0.95 at largest M tested.

PRE-REG (preregs/2026-06-23_hrr_depth_budget_sparse_bipolar_v2.md):
  HARD_PASS = alpha_c(f=0.02) >= 20 * alpha_c(f=1.0)  (drill's 20-300x lift confirmed)
  HARD_FAIL = alpha_c(f=0.02) <= 2 * alpha_c(f=1.0)   (drill claim refuted)
  MIDDLE    = lift in (2x, 20x)

SANITY (selftest):
  - M=1 every arm recall=1.0.
  - FLIP=0 every arm recall=1.0 up to small M.

SUBSTRATE-ONLY: numpy; no torch; ASCII-only; per-seed checkpointing.
"""
from __future__ import annotations
import sys
import os
import argparse
import time
import signal
import atexit
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import (
    get_output_dir, write_partial_key, aggregate_partials, write_metrics,
)

ANCHOR_NAME = "hrr_depth_budget_sparse_bipolar_v2"

# Pre-reg HARD bands (sacrosanct)
HP_LIFT_RATIO = 20.0
HF_LIFT_RATIO = 2.0
RECALL_THRESH = 0.95
FLIP = 0.05

_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_ARGS, _ = _P.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE) else os.environ.get("HDLAB_RUN_MODE", "full")

# Config
N_DIM = 4096
F_GRID = [1.0, 0.1, 0.05, 0.02, 0.01]
ARMS = ["ARM_DENSE_f1.0", "ARM_SPARSE_f0.1", "ARM_SPARSE_f0.05",
        "ARM_SPARSE_f0.02", "ARM_SPARSE_f0.01"]
ARM_TO_F = dict(zip(ARMS, F_GRID))

# M_GRID is per-arm: dense needs only ~570; sparse explores up to alpha=40.
# alpha = M/N. For N=4096:
#   alpha=0.14 -> M=573  (theoretical dense Hopfield capacity)
#   alpha=1    -> M=4096
#   alpha=5    -> M=20k
#   alpha=20   -> M=82k
#   alpha=40   -> M=164k
# Per-arm grids: dense is short; sparse is exponential and early-terminates.

if RUN_MODE == "full":
    SEEDS = [7, 17, 23]
    # Per-arm M sweep. f=1.0 dense expected alpha_c ~0.14 (M ~573).
    # f=0.02 sparse expected 20-300x dense; lift=20 -> M=11k.
    # Cost scales O(M^2 * N); cap sparse arms at M=70k (~10-15 min per M point
    # at M=70k on laptop CPU) to stay within 3600s/seed budget.
    # Total budget per seed ~ sum_M of M^2*N/GFLOPS ~ smoke-extrapolated 25-40 min.
    # All sparse arms early-terminate when recall<0.95; reached-end => alpha_c
    # is a LOWER BOUND (capped=True; cert-owner reads this honestly).
    M_GRID_BY_ARM = {
        "ARM_DENSE_f1.0":   [50, 150, 300, 450, 570, 700, 900, 1200],
        "ARM_SPARSE_f0.1":  [200, 500, 1000, 2000, 4000, 8000, 16000],
        "ARM_SPARSE_f0.05": [500, 1500, 3000, 6000, 12000, 24000, 40000],
        "ARM_SPARSE_f0.02": [1000, 3000, 8000, 16000, 30000, 50000, 70000],
        "ARM_SPARSE_f0.01": [2000, 6000, 14000, 28000, 50000, 70000],
    }
else:
    SEEDS = [7]
    # Smoke: small grid hitting M=1 sanity + small-mid + a sparse mid-point.
    M_GRID_BY_ARM = {
        "ARM_DENSE_f1.0":   [1, 50, 200, 500],
        "ARM_SPARSE_f0.1":  [1, 100, 500, 1500],
        "ARM_SPARSE_f0.05": [1, 200, 1000, 3000],
        "ARM_SPARSE_f0.02": [1, 500, 2000, 5000],
        "ARM_SPARSE_f0.01": [1, 1000, 4000, 10000],
    }

CONFIG_VERSION = (
    "hrr_depth_budget_sparse_bipolar_v2; N_DIM=%d arms=%s f_grid=%s seeds=%s "
    "FLIP=%.3f recall_thresh=%.2f mode=%s; "
    "bands HP_lift>=%.1fx HF_lift<=%.1fx; metric=W-free-Hopfield-cue-FLIP-recall"
) % (N_DIM, ARMS, F_GRID, SEEDS, FLIP, RECALL_THRESH, RUN_MODE,
     HP_LIFT_RATIO, HF_LIFT_RATIO)


# ============================================================================
# Primitives: K-sparse bipolar pattern + W-free Hopfield recall under FLIP cue
# ============================================================================

def sparse_pat(M: int, n: int, f: float, g: np.random.Generator) -> np.ndarray:
    """K-sparse bipolar pattern matrix shape (M, n).

    K = max(1, round(f*n)) nonzero {-1,+1} positions; rest zero.
    For f>=1.0: dense bipolar (all positions in {-1,+1}).
    """
    if f >= 1.0:
        # Dense bipolar: all positions {-1,+1}
        s = g.integers(0, 2, size=(M, n), dtype=np.int8) * 2 - 1
        return s.astype(np.float32)
    k = max(1, int(round(f * n)))
    P = np.zeros((M, n), dtype=np.float32)
    for i in range(M):
        idx = g.choice(n, k, replace=False)
        P[i, idx] = g.integers(0, 2, k, dtype=np.int8) * 2 - 1
    return P


def recall_w_free(P: np.ndarray, g: np.random.Generator, flip: float = FLIP,
                  chunk: int = 1024) -> float:
    """W-free single-step Hopfield recall with FLIP cue-noise on nonzero positions.

    For each row i in P:
      - cue = P[i] with 'flip' fraction of nonzero positions flipped.
      - r = sign((cue @ P.T) @ P - cue * diag(P @ P.T))  (subtract self-bias).
      - correct iff r[nz(P[i])] == P[i][nz(P[i])] for all nz positions.

    Returns fraction of correctly-recovered patterns.

    Chunked over query-rows for memory bound: peak ~ (chunk, M) not (M, M).
    """
    M, n = P.shape
    diag = (P * P).sum(0)  # (n,) self-bias per position; for bipolar = M counts active
    # Build noisy cues row-by-row to keep memory bound.
    s = P.copy()
    for i in range(M):
        nz = np.nonzero(P[i])[0]
        if len(nz) == 0:
            continue
        flip_mask = g.random(len(nz)) < flip
        fl = nz[flip_mask]
        if len(fl) > 0:
            s[i, fl] *= -1
    correct = 0
    for a in range(0, M, chunk):
        b = min(a + chunk, M)
        # rc = sign(s_chunk @ P.T @ P - s_chunk * diag) shape (chunk, n)
        # CHUNK-INDEPENDENT: each query row decoded independently.
        rc = np.sign((s[a:b] @ P.T) @ P - s[a:b] * diag)
        for i in range(a, b):
            nz = np.nonzero(P[i])[0]
            if len(nz) == 0:
                # all-zero pattern recovers trivially
                correct += 1
                continue
            if np.all(rc[i - a][nz] == P[i][nz]):
                correct += 1
    return correct / max(M, 1)


def find_alpha_c(arm: str, n_dim: int, seeds_pat_seed: int, recall_seed: int,
                 m_grid: List[int]) -> Tuple[float, bool, Dict]:
    """Sweep M ascending; alpha_c = max(M/N) where recall>=RECALL_THRESH.

    Early-terminate as soon as recall < RECALL_THRESH at M_i (cannot rise again
    for plain Hopfield; capacity is monotone). Returns (alpha_c, capped, per_M).

    capped=True iff recall>=thresh at largest M tested (true alpha_c lower-bound).
    """
    f = ARM_TO_F[arm]
    per_M: Dict[str, Dict] = {}
    alpha_c = 0.0
    capped = False
    for i, M in enumerate(m_grid):
        g_pat = np.random.default_rng(seeds_pat_seed * 13 + M * 7 + int(f * 1e6))
        g_rec = np.random.default_rng(recall_seed * 11 + M * 5 + int(f * 1e6))
        t0 = time.time()
        P = sparse_pat(M, n_dim, f, g_pat)
        r = recall_w_free(P, g_rec)
        wall = time.time() - t0
        per_M["M%d" % M] = {
            "M": M, "alpha": round(M / n_dim, 4), "recall": round(r, 4),
            "wall_s": round(wall, 2),
        }
        print("    [arm=%s M=%d alpha=%.3f] recall=%.3f wall=%.1fs" % (
            arm, M, M / n_dim, r, wall), flush=True)
        if r >= RECALL_THRESH:
            alpha_c = M / n_dim
            if i == len(m_grid) - 1:
                capped = True
        else:
            break
    return alpha_c, capped, per_M


# ============================================================================
# Per-seed unit
# ============================================================================

def run_unit(seed: int) -> Dict:
    t0 = time.time()
    by_arm: Dict[str, Dict] = {}
    for arm in ARMS:
        f = ARM_TO_F[arm]
        t_arm = time.time()
        m_grid = M_GRID_BY_ARM[arm]
        alpha_c, capped, per_M = find_alpha_c(arm, N_DIM, seed, seed, m_grid)
        wall = time.time() - t_arm
        by_arm[arm] = {
            "f": f,
            "alpha_c": round(alpha_c, 4),
            "alpha_c_capped": bool(capped),
            "per_M": per_M,
            "wall_s": round(wall, 2),
        }
        print("  [seed=%d arm=%s] f=%.3f alpha_c=%.3f capped=%s wall=%.1fs" % (
            seed, arm, f, alpha_c, capped, wall), flush=True)
    return {
        "seed": seed,
        "by_arm": by_arm,
        "N_DIM": N_DIM,
        "FLIP": FLIP,
        "RECALL_THRESH": RECALL_THRESH,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "elapsed_s_seed": round(time.time() - t0, 2),
    }


# ============================================================================
# Verdict
# ============================================================================

def compute_verdict(units) -> Tuple[str, str, Dict]:
    if not units:
        return ("HARD_FAIL", "no results", {})
    arms = list(units[0]["by_arm"].keys())
    by_arm_agg: Dict[str, Dict] = {}
    for arm in arms:
        acs = [u["by_arm"][arm]["alpha_c"] for u in units]
        cappeds = [u["by_arm"][arm]["alpha_c_capped"] for u in units]
        ac_mean = float(np.mean(acs))
        ac_std = float(np.std(acs))
        ac_cv = ac_std / max(abs(ac_mean), 1e-9)
        by_arm_agg[arm] = {
            "f": ARM_TO_F[arm],
            "alpha_c_mean": round(ac_mean, 4),
            "alpha_c_std": round(ac_std, 4),
            "alpha_c_cv": round(ac_cv, 4),
            "alpha_c_per_seed": [round(a, 4) for a in acs],
            "any_capped": bool(any(cappeds)),
            "all_capped": bool(all(cappeds)),
        }

    dense_arm = "ARM_DENSE_f1.0"
    sparse_arm = "ARM_SPARSE_f0.02"
    ac_dense = by_arm_agg[dense_arm]["alpha_c_mean"]
    ac_sparse = by_arm_agg[sparse_arm]["alpha_c_mean"]
    lift_ratio = ac_sparse / max(ac_dense, 1e-9)

    # All-arm lift table for visibility
    lifts_by_arm = {
        arm: round(by_arm_agg[arm]["alpha_c_mean"] / max(ac_dense, 1e-9), 3)
        for arm in arms
    }

    detail = {
        "by_arm_agg": by_arm_agg,
        "dense_alpha_c": round(ac_dense, 4),
        "sparse_f0_02_alpha_c": round(ac_sparse, 4),
        "lift_ratio_sparse_f0_02_vs_dense": round(lift_ratio, 3),
        "lifts_by_arm_vs_dense": lifts_by_arm,
        "any_capped_dense": by_arm_agg[dense_arm]["any_capped"],
        "any_capped_sparse_f0_02": by_arm_agg[sparse_arm]["any_capped"],
        "n_seeds": len(units),
        "CONFIG_VERSION": CONFIG_VERSION,
        "honest_scope": (
            "Substrate-native W-free Hopfield recall (single-step; correlation-"
            "matrix r = sign((cue @ P.T) @ P - cue * diag)); cue = FLIP=%.2f on "
            "nonzero positions; exact-recovery on nonzero positions; recall_thresh="
            "%.2f; alpha_c(f) = max M/N where recall>=thresh. HARD_PASS = "
            "alpha_c(f=0.02) >= %.0fx alpha_c(f=1.0); HARD_FAIL = lift <= %.1fx. "
            "Corrects v1 bundle/top-M-cleanup metric (wrong paradigm vs CERT 592)."
            % (FLIP, RECALL_THRESH, HP_LIFT_RATIO, HF_LIFT_RATIO)),
        "cites": [
            "preregs/2026-06-23_hrr_depth_budget_sparse_bipolar_v2.md",
            "notes/research_drill_sparse_bipolar_depth_enc1_composition_2026-06-23.md",
            "data/exp_sparse_boundary_v2_cpu_v1/metrics.json (CERT 592 reference paradigm)",
            "experiments/exp_hrr_depth_budget_sparse_bipolar_v1.py (v1 wrong-metric)",
        ],
    }

    summary = (
        "alpha_c: dense=%.3f sparse_f0.02=%.3f lift=%.1fx | lifts_by_arm=%s | "
        "capped(dense=%s, sparse_f0.02=%s) | n_seeds=%d"
    ) % (ac_dense, ac_sparse, lift_ratio, lifts_by_arm,
         by_arm_agg[dense_arm]["any_capped"],
         by_arm_agg[sparse_arm]["any_capped"], len(units))

    if ac_dense <= 1e-9:
        return ("HARD_FAIL",
                "HARD_FAIL: dense alpha_c ~0 (denominator unbounded). " + summary,
                detail)

    if lift_ratio >= HP_LIFT_RATIO:
        msg = (
            "HRR_BUNDLE_SPARSE_v2 HARD_PASS: ARM_SPARSE_f0.02 alpha_c=%.3f vs "
            "ARM_DENSE_f1.0 alpha_c=%.3f -> lift=%.1fx (>= %.0fx); substrate-"
            "native sparse-bipolar W-free Hopfield delivers Willshaw super-capacity "
            "at f=0.02 vs dense; CERT 592 paradigm confirmed at N=4096. "
            "Chain-grade-eligible substrate-native compression primitive. %s"
        ) % (ac_sparse, ac_dense, lift_ratio, HP_LIFT_RATIO, summary)
        return ("HARD_PASS", msg, detail)

    if lift_ratio <= HF_LIFT_RATIO:
        msg = (
            "HRR_BUNDLE_SPARSE_v2 HARD_FAIL: lift=%.2fx (<= %.1fx); sparse-"
            "bipolar W-free recall does NOT deliver Willshaw super-capacity at "
            "N=%d f=0.02; CERT 592 drill claim refuted at this scale. %s"
        ) % (lift_ratio, HF_LIFT_RATIO, N_DIM, summary)
        return ("HARD_FAIL", msg, detail)

    msg = (
        "HRR_BUNDLE_SPARSE_v2 MIDDLE_BAND: lift=%.2fx (>2x, <20x); partial "
        "Willshaw super-capacity; characterize via finer M-sweep. %s"
    ) % (lift_ratio, summary)
    return ("MIDDLE_BAND", msg, detail)


# ============================================================================
# atexit synthesizer (partial-rescue)
# ============================================================================
_METRICS_WRITTEN = [False]
_OUT_DIR_REF = [None]
_T0_REF = [None]


def _synthesize_on_exit():
    if _METRICS_WRITTEN[0]:
        return
    out_dir = _OUT_DIR_REF[0]
    if out_dir is None or not out_dir.exists():
        return
    try:
        partials = aggregate_partials(out_dir, ["s%d" % sd for sd in SEEDS])
        units = list(partials.values())
        if not units:
            return
        try:
            verdict, msg, detail = compute_verdict(units)
        except Exception as e:
            verdict, msg, detail = ("PARTIAL_TIMEOUT",
                                    "atexit synthesize: compute_verdict failed: %s" % e,
                                    {"n_seeds_recovered": len(units)})
        metrics = {
            "anchor_name": ANCHOR_NAME,
            "verdict": ("TIMEOUT_PARTIAL_NSEEDS_%d" % len(units)) if verdict != "PARTIAL_TIMEOUT" else verdict,
            "verdict_msg": "[atexit-synthesize] " + msg,
            "run_mode": RUN_MODE,
            "N_DIM": N_DIM,
            "n_seeds": len(units),
            "n_seeds_expected": len(SEEDS),
            "detail": detail,
            "metrics_source": "atexit_synthesize_partial_hrr_depth_budget_sparse_bipolar_v2",
            "per_unit": units,
            "elapsed_s": (time.time() - _T0_REF[0]) if _T0_REF[0] else 0.0,
            "summary": "[atexit-synthesize from %d/%d partials] %s" % (len(units), len(SEEDS), msg),
            "substrate_only_decode_gate": "TRUE",
            "zero_llm_calls_at_inference": True,
            "_synthesized_by_atexit": True,
        }
        write_metrics(out_dir, metrics, units)
        _METRICS_WRITTEN[0] = True
        sys.stderr.write("[atexit] synthesized metrics.json from %d/%d partials\n" % (
            len(units), len(SEEDS)))
        sys.stderr.flush()
    except Exception as e:
        sys.stderr.write("[atexit] synthesize failed: %s\n" % e)
        sys.stderr.flush()


# ============================================================================
# Self-test (mechanism + sanity + verdict-shape)
# ============================================================================

def _selftest():
    g = np.random.default_rng(0)

    # T1: sparse_pat respects K-of-N
    n_test = 256
    for f in [1.0, 0.1, 0.02]:
        P = sparse_pat(5, n_test, f, g)
        k_expected = n_test if f >= 1.0 else max(1, int(round(f * n_test)))
        nz_per_row = (P != 0).sum(axis=1)
        assert np.all(nz_per_row == k_expected), \
            "T1 sparse_pat f=%.3f K_actual=%s expected=%d" % (f, nz_per_row.tolist(), k_expected)
        active = P[P != 0]
        assert set(np.unique(active).tolist()).issubset({-1.0, 1.0}), \
            "T1 sparse_pat not bipolar in active: %s" % np.unique(active).tolist()

    # T2: at M=1, recall=1.0 for every f (single pattern is trivially recoverable;
    # diag subtraction removes the self-bias and (cue @ P.T) @ P collapses to
    # the self-projection; signing recovers the pattern even with small FLIP).
    for f in [1.0, 0.1, 0.02]:
        P = sparse_pat(1, n_test, f, np.random.default_rng(7))
        r = recall_w_free(P, np.random.default_rng(11))
        assert r == 1.0, "T2 M=1 recall not 1.0 at f=%.3f (got %.3f)" % (f, r)

    # T3: at FLIP=0, recall=1.0 at small loads (no cue noise -> perfect storage)
    for f in [1.0, 0.1, 0.02]:
        P = sparse_pat(4, n_test, f, np.random.default_rng(13))
        r = recall_w_free(P, np.random.default_rng(17), flip=0.0)
        assert r == 1.0, "T3 FLIP=0 recall not 1.0 at f=%.3f M=4 (got %.3f)" % (f, r)

    # T4: dense recall drops at high load (above theoretical alpha_c~0.14)
    # at N=256, alpha=0.5 -> M=128, recall should be well below 0.95.
    P_high = sparse_pat(128, n_test, 1.0, np.random.default_rng(19))
    r_high = recall_w_free(P_high, np.random.default_rng(23))
    assert r_high < 0.95, "T4 dense @alpha=0.5 should fail; got recall=%.3f" % r_high

    # T5: sparse recall holds at higher loads than dense (f=0.05 @ alpha=0.5 should
    # recover at least one pattern; soft check -- exact threshold depends on N and FLIP)
    P_sparse_high = sparse_pat(128, n_test, 0.05, np.random.default_rng(29))
    r_sparse_high = recall_w_free(P_sparse_high, np.random.default_rng(31))
    # Soft sanity: sparse at same load should not be worse than dense.
    assert r_sparse_high >= r_high - 0.05, \
        "T5 sparse f=0.05 @alpha=0.5 should be at least as good as dense; got sparse=%.3f dense=%.3f" % (
            r_sparse_high, r_high)

    # T6: find_alpha_c monotone-early-terminate behavior
    small_grid = [1, 4, 16]
    ac, capped, per_M = find_alpha_c("ARM_DENSE_f1.0", n_test, 7, 7, small_grid)
    # At N=256, M=1, M=4 should both pass; M=16 may pass too at FLIP=0.05.
    # Verify per_M entries are well-formed.
    assert len(per_M) >= 1, "T6 per_M empty"
    for k, v in per_M.items():
        assert "recall" in v and "M" in v and "alpha" in v, "T6 per_M malformed: %s" % v
    # alpha_c must equal max M_i/N where recall>=thresh (or 0 if none passed).
    passed_ms = [v["M"] for v in per_M.values() if v["recall"] >= RECALL_THRESH]
    if passed_ms:
        assert abs(ac - max(passed_ms) / n_test) < 1e-6, \
            "T6 alpha_c=%.4f does not match max passed M=%d/N=%d" % (ac, max(passed_ms), n_test)
    else:
        assert ac == 0.0, "T6 alpha_c should be 0 when no M passed"

    # T7: verdict-shape sanity
    def _mk_unit(per_arm_ac: Dict[str, float], per_arm_capped: Dict[str, bool]) -> Dict:
        ba = {}
        for arm in ARMS:
            ba[arm] = {
                "f": ARM_TO_F[arm],
                "alpha_c": per_arm_ac[arm],
                "alpha_c_capped": per_arm_capped.get(arm, False),
                "per_M": {},
                "wall_s": 0.0,
            }
        return {"seed": 0, "by_arm": ba, "N_DIM": N_DIM, "FLIP": FLIP,
                "RECALL_THRESH": RECALL_THRESH, "run_mode": "smoke",
                "config_version": "selftest", "elapsed_s_seed": 0.01}

    # T7a HARD_PASS: f=0.02 alpha=3.0, dense alpha=0.14 -> lift 21.4x
    hp_ac = {
        "ARM_DENSE_f1.0":   0.14,
        "ARM_SPARSE_f0.1":  0.5,
        "ARM_SPARSE_f0.05": 1.5,
        "ARM_SPARSE_f0.02": 3.0,
        "ARM_SPARSE_f0.01": 4.0,
    }
    u_hp = _mk_unit(hp_ac, {})
    v, m, d = compute_verdict([u_hp, u_hp, u_hp])
    assert v == "HARD_PASS", "T7a HARD_PASS expected, got %s msg=%s" % (v, m[:200])

    # T7b HARD_FAIL: f=0.02 alpha=0.2, dense alpha=0.14 -> lift 1.4x
    hf_ac = {
        "ARM_DENSE_f1.0":   0.14,
        "ARM_SPARSE_f0.1":  0.15,
        "ARM_SPARSE_f0.05": 0.18,
        "ARM_SPARSE_f0.02": 0.20,
        "ARM_SPARSE_f0.01": 0.21,
    }
    u_hf = _mk_unit(hf_ac, {})
    v, m, d = compute_verdict([u_hf, u_hf, u_hf])
    assert v == "HARD_FAIL", "T7b HARD_FAIL expected, got %s msg=%s" % (v, m[:200])

    # T7c MIDDLE: f=0.02 alpha=1.0, dense alpha=0.14 -> lift 7.1x
    mid_ac = {
        "ARM_DENSE_f1.0":   0.14,
        "ARM_SPARSE_f0.1":  0.3,
        "ARM_SPARSE_f0.05": 0.6,
        "ARM_SPARSE_f0.02": 1.0,
        "ARM_SPARSE_f0.01": 1.1,
    }
    u_mid = _mk_unit(mid_ac, {})
    v, m, d = compute_verdict([u_mid, u_mid, u_mid])
    assert v == "MIDDLE_BAND", "T7c MIDDLE expected, got %s msg=%s" % (v, m[:200])

    print("[selftest] PASS: T1 sparse_pat K-of-N + T2 M=1 recall + T3 FLIP=0 "
          "recall + T4 dense fails high load + T5 sparse >= dense high load + "
          "T6 find_alpha_c monotone + T7 verdict bands (HP, HF, MID) OK",
          flush=True)


if __name__ == "__main__":
    _selftest()
    if _ARGS.self_test:
        raise SystemExit(0)
    print("[config] %s mode=%s N_DIM=%d arms=%s seeds=%s | %s" % (
        ANCHOR_NAME, RUN_MODE, N_DIM, ARMS, SEEDS, CONFIG_VERSION), flush=True)
    out_dir = get_output_dir(ANCHOR_NAME)
    _OUT_DIR_REF[0] = out_dir
    atexit.register(_synthesize_on_exit)
    try:
        signal.signal(signal.SIGTERM, lambda *a: (_synthesize_on_exit(), sys.exit(143)))
    except (ValueError, AttributeError):
        pass
    run_cfg = {"run_mode": RUN_MODE, "N": N_DIM,
               "schema": "hrr-depth-budget-sparse-bipolar-v2-wfree-hopfield"}
    t0 = time.time()
    _T0_REF[0] = t0
    for seed in SEEDS:
        key = "s%d" % seed
        if key in aggregate_partials(out_dir, [key], run_config=run_cfg):
            print("[ckpt] %s done; skip" % key, flush=True)
            continue
        write_partial_key(out_dir, key, run_unit(seed))
    units = list(aggregate_partials(out_dir, ["s%d" % sd for sd in SEEDS], run_config=run_cfg).values())
    verdict, msg, detail = compute_verdict(units)
    print("\n[VERDICT] " + msg, flush=True)
    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": msg,
        "run_mode": RUN_MODE,
        "N_DIM": N_DIM,
        "F_GRID": F_GRID,
        "FLIP": FLIP,
        "RECALL_THRESH": RECALL_THRESH,
        "n_seeds": len(SEEDS),
        "detail": detail,
        "metrics_source": "measured_cpu_hrr_depth_budget_sparse_bipolar_v2_wfree_hopfield",
        "per_unit": units,
        "elapsed_s": time.time() - t0,
        "summary": msg,
        "substrate_only_decode_gate": "TRUE (substrate-native sparse-bipolar W-free Hopfield; numpy only; zero LLM at inference)",
        "zero_llm_calls_at_inference": True,
        "_name_says_smoke_workaround": _NAME_SAYS_SMOKE,
    }
    write_metrics(out_dir, metrics, units)
    _METRICS_WRITTEN[0] = True
    print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
