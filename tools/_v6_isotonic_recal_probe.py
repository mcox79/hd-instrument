"""STEP-1 falsifier (read-only, NO GPU, NO training, NO canonical writes):
post-hoc recalibration of the v6 ANNEALED dense readout.

Question (coordinator A2 drill): does MONOTONE post-hoc calibration alone close
the dense-value gap -- v6 ANNEAL_STE DENSE readout has ret_agree10 ~ 0.65 but
calib_err ~ 0.37 / hi80_cos ~ 0.48 (MEASURED@data/exp_encoder_v6_annealed_ste_
fidelity_k128_v1_seed7/metrics.json:recovery.ANNEAL_STE.final_dense) -- with
ret_agree10 UNCHANGED (isotonic is order-preserving, so ranking MUST survive;
verified empirically here)?

Method: reconstruct the EXACT v6 held-out split (same seed permutation over the
177899-concept teacher cache, same HELD_FRAC/CAP), load the CANONICAL ANNEAL_STE
last checkpoint, encode the held dense sign codes, sample teacher-vs-code cosine
pairs. Fit PAVA isotonic regression (and a Platt affine fallback) mapping code
cosine -> teacher cosine on a CALIB half of held CONCEPTS, then read residual
calib_err + hi80_cos on the DISJOINT TEST half of held concepts (honest out-of-
sample post-hoc calibration -- no concept leakage between fit and eval).

ASCII-only. No emojis. No em dashes.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import torch

_REPO = Path(__file__).resolve().parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from experiments import (  # noqa: E402
    exp_encoder_migration_step1b_v3_global_objective_landmark_rkd_concept_encoder_v1_core
    as v3,
)

TEACHER_CACHE = "data/substrate_index/cached_indices/bge_large_v2_name_177899_54f7cf6a.npz"
KB, BLK_L = 128, 32          # v6 K=128 (3.125% active)
ANNEAL_HIDDEN = 2048         # ANNEAL_STE arm student width
N_PAIRS = 400_000            # matches v3.MID_PAIR_SAMPLE (baseline reproduction)
HI80_THRESH = 0.80


def _spearman(a: np.ndarray, b: np.ndarray) -> float:
    ra = np.argsort(np.argsort(a)).astype(np.float64)
    rb = np.argsort(np.argsort(b)).astype(np.float64)
    return float(np.corrcoef(ra, rb)[0, 1])


def _pava(x: np.ndarray, y: np.ndarray):
    """Isotonic regression of y on x (non-decreasing). Returns (xs, yhat) sorted
    by x. Pool-adjacent-violators, O(n). Pure numpy (no sklearn dependency)."""
    order = np.argsort(x, kind="mergesort")
    xs = x[order].astype(np.float64)
    ys = y[order].astype(np.float64)
    vals: list[float] = []
    cnts: list[int] = []
    for v in ys:
        vals.append(float(v))
        cnts.append(1)
        while len(vals) > 1 and vals[-2] > vals[-1]:
            v2 = vals.pop(); c2 = cnts.pop()
            v1 = vals.pop(); c1 = cnts.pop()
            vals.append((v1 * c1 + v2 * c2) / (c1 + c2))
            cnts.append(c1 + c2)
    out = np.empty(len(ys), dtype=np.float64)
    idx = 0
    for v, c in zip(vals, cnts):
        out[idx:idx + c] = v
        idx += c
    return xs, out


def _apply_iso(xs: np.ndarray, yhat: np.ndarray, q: np.ndarray) -> np.ndarray:
    return np.interp(q, xs, yhat, left=float(yhat[0]), right=float(yhat[-1]))


def _sample_pairs(cn: torch.Tensor, Xhe: torch.Tensor, lo: int, hi: int,
                  n_pairs: int, seed: int):
    """Sample n_pairs (i != j) with both endpoints in concept-index [lo, hi)."""
    rng = np.random.default_rng(seed)
    i = rng.integers(lo, hi, n_pairs)
    j = rng.integers(lo, hi, n_pairs)
    keep = i != j
    i, j = i[keep], j[keep]
    ti = torch.from_numpy(i.copy())
    tj = torch.from_numpy(j.copy())
    tp = (Xhe[ti] * Xhe[tj]).sum(-1).numpy()
    sp = (cn[ti] * cn[tj]).sum(-1).numpy()
    return sp.astype(np.float64), tp.astype(np.float64)


def _ret_agree10(codes_sub: torch.Tensor, X_sub: torch.Tensor, recal_fn=None,
                 chunk: int = 512) -> float:
    """ret_agree10 over a concept subsample: mean top-10 index-set overlap
    between teacher-cosine and code-cosine per row. recal_fn (if given) applies a
    monotone transform to the code cosine BEFORE topk -- used to prove
    ret_agree10 is invariant to monotone recalibration."""
    cn = codes_sub / (codes_sub.norm(dim=-1, keepdim=True) + 1e-8)
    n = X_sub.shape[0]
    agree = 0.0
    for lo in range(0, n, chunk):
        hi = min(lo + chunk, n)
        rows = torch.arange(lo, hi)
        ts = X_sub[lo:hi] @ X_sub.T
        ts[rows - lo, rows] = -2.0
        t10 = ts.topk(10, dim=1).indices
        ss = cn[lo:hi] @ cn.T
        if recal_fn is not None:
            ss = torch.from_numpy(
                recal_fn(ss.numpy().astype(np.float64)).astype(np.float32))
        ss[rows - lo, rows] = -2.0
        s10 = ss.topk(10, dim=1).indices
        for r in range(hi - lo):
            agree += len(set(t10[r].tolist()) & set(s10[r].tolist())) / 10.0
    return agree / n


def run(seed: int) -> int:
    torch.manual_seed(seed)
    cache_path = v3._resolve_teacher_cache(TEACHER_CACHE)
    X, ids = v3._load_teacher(cache_path)
    V = X.shape[0]
    print(f"[recal] seed={seed} teacher={cache_path.name} V={V} dim={X.shape[1]}",
          flush=True)

    # Reconstruct the EXACT v6/v3 full-mode held split.
    rng = np.random.default_rng(seed)
    perm = rng.permutation(V)
    n_he = min(int(round(V * v3.HELD_FRAC)), v3.FULL_HELD_CAP)
    n_tr = V - n_he
    he_idx = perm[n_tr:n_tr + n_he]
    Xhe = X[torch.from_numpy(he_idx.copy())].contiguous()
    print(f"[recal] held pool n_he={n_he} (n_tr={n_tr})", flush=True)

    # Load CANONICAL ANNEAL_STE last checkpoint (the DENSE_LAST readout source).
    ckpt = (_REPO / "data" / f"substrate_concept_encoder_v6_annealste_seed{seed}"
            / "_ckpt_ANNEAL_STE.pt")
    if not ckpt.exists():
        print(f"[recal] FATAL: checkpoint not found: {ckpt}", flush=True)
        return 3
    orig_hidden = v3.MLP_HIDDEN
    v3.MLP_HIDDEN = ANNEAL_HIDDEN
    try:
        student = v3._make_student("mlp", X.shape[1], KB * BLK_L, "cpu", seed=0)
    finally:
        v3.MLP_HIDDEN = orig_hidden
    ck = torch.load(str(ckpt), map_location="cpu")
    student.load_state_dict(ck["student"])
    student.eval()
    print(f"[recal] loaded ANNEAL_STE student (step={ck.get('step')}, "
          f"hidden={int(student.net[0].out_features)}, out={student.out_dim})",
          flush=True)

    codes = v3._dense_sign_codes(student, Xhe)  # (n_he, 4096) dense sign code
    cn = codes / (codes.norm(dim=-1, keepdim=True) + 1e-8)

    # ---- BASELINE over the FULL held pool (reproduce the landed metric) ----
    sp, tp = _sample_pairs(cn, Xhe, 0, n_he, N_PAIRS, seed + 3)
    m8 = tp >= HI80_THRESH
    hi80_t_full = float(tp[m8].mean())
    base_hi80_full = float(sp[m8].mean())
    base_calib_full = abs(base_hi80_full - hi80_t_full)
    base_spear = _spearman(sp, tp)
    print(f"[recal] BASELINE (full pool, reproduces landed): "
          f"hi80_cos={base_hi80_full:.4f} hi80_teacher={hi80_t_full:.4f} "
          f"calib_err={base_calib_full:.4f} spearman={base_spear:.4f} "
          f"n_hi80={int(m8.sum())}", flush=True)

    # ---- Post-hoc recalibration: fit on CALIB half concepts, eval on TEST half.
    half = n_he // 2
    sp_fit, tp_fit = _sample_pairs(cn, Xhe, 0, half, N_PAIRS, seed + 101)
    sp_ev, tp_ev = _sample_pairs(cn, Xhe, half, n_he, N_PAIRS, seed + 202)
    m8e = tp_ev >= HI80_THRESH
    hi80_t_ev = float(tp_ev[m8e].mean())

    base_hi80_ev = float(sp_ev[m8e].mean())
    base_calib_ev = abs(base_hi80_ev - hi80_t_ev)

    # Isotonic (PAVA).
    xs, yhat = _pava(sp_fit, tp_fit)
    sp_ev_iso = _apply_iso(xs, yhat, sp_ev)
    iso_hi80 = float(sp_ev_iso[m8e].mean())
    iso_calib = abs(iso_hi80 - hi80_t_ev)
    iso_spear = _spearman(sp_ev_iso, tp_ev)

    # Platt affine (least-squares a*x + b) fallback.
    A = np.vstack([sp_fit, np.ones_like(sp_fit)]).T
    a, b = np.linalg.lstsq(A, tp_fit, rcond=None)[0]
    sp_ev_platt = a * sp_ev + b
    platt_hi80 = float(sp_ev_platt[m8e].mean())
    platt_calib = abs(platt_hi80 - hi80_t_ev)

    print(f"[recal] EVAL half (test concepts, out-of-sample) hi80_teacher="
          f"{hi80_t_ev:.4f} n_hi80={int(m8e.sum())}", flush=True)
    print(f"[recal]   BASELINE  : hi80_cos={base_hi80_ev:.4f} "
          f"calib_err={base_calib_ev:.4f}", flush=True)
    print(f"[recal]   ISOTONIC  : hi80_cos={iso_hi80:.4f} "
          f"calib_err={iso_calib:.4f} spearman={iso_spear:.4f} "
          f"(Platt a={a:.4f} b={b:.4f})", flush=True)
    print(f"[recal]   PLATT     : hi80_cos={platt_hi80:.4f} "
          f"calib_err={platt_calib:.4f}", flush=True)

    # ---- ret_agree10 UNCHANGED check (monotone-invariance), test subsample ----
    sub = min(2000, n_he - half)
    codes_test = codes[half:half + sub].contiguous()
    Xhe_test = Xhe[half:half + sub].contiguous()
    ret_base = _ret_agree10(codes_test, Xhe_test, recal_fn=None)
    ret_iso = _ret_agree10(codes_test, Xhe_test,
                           recal_fn=lambda s: _apply_iso(xs, yhat, s))
    print(f"[recal]   ret_agree10 (test sub n={sub}): base={ret_base:.6f} "
          f"iso_recal={ret_iso:.6f} delta={abs(ret_base - ret_iso):.2e} "
          f"UNCHANGED={'YES' if abs(ret_base - ret_iso) < 1e-9 else 'NO'}",
          flush=True)

    # Machine-readable one-liner for easy capture.
    print(f"[RESULT] seed={seed} "
          f"base_calib={base_calib_ev:.4f} iso_calib={iso_calib:.4f} "
          f"platt_calib={platt_calib:.4f} base_hi80={base_hi80_ev:.4f} "
          f"iso_hi80={iso_hi80:.4f} hi80_teacher={hi80_t_ev:.4f} "
          f"ret_base={ret_base:.4f} ret_iso={ret_iso:.4f} "
          f"ret_unchanged={abs(ret_base - ret_iso) < 1e-9}", flush=True)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args()
    return run(args.seed)


if __name__ == "__main__":
    sys.exit(main())
