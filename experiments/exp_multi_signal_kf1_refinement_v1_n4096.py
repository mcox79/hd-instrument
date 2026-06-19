"""G4 MULTI-SIGNAL KF-1 REFINEMENT v1 at N=4096.

CONTEXT (Batch 1 #4):
  v2 multi_signal_kf1_design had composite AUC = 1.000 at all 3 operating
  points -> caught as label-vs-honest #145-1 COMPOSITE_AUC_TRIVIALIZED in
  v287. This refinement tests where signals actually disagree, by using:
   (a) wider M sweep including very-small and past-capacity regimes
       (M in {128, 4096, 8192, 16384}); and
   (b) BORDERLINE queries (stored_key + small_noise) in addition to
       in-store and OOS, where signals will genuinely disagree.

5 SIGNALS (same battery as v2; from _multi_signal_kf1_design_v2 reference):
  posterior_entropy, spectral_signature, bundle_norm, geometric_distance,
  cross_replica_consistency.

NEW EVALUATION BUILD:
  50 in-store queries (label=0) + 50 OOS queries (label=1) +
  50 borderline queries (stored_key + small_noise, label=1 because they
  are NOT exact-store but ARE similar; KF-1 should still detect them as
  high-confidence-but-not-exact).
  -> 150 queries / regime. Total per cell: 5 signals over 150 queries.

PER-CELL CHECKPOINT (PROT-021): yes.

PRE-REGISTERED BANDS:
  HP = composite AUC >= 0.90 at ALL 4 M values (borderline-included
       evaluation) AND resolution_accuracy >= 0.75 when signals disagree
       on at least 5% of queries (mean over seeds; >= 3/5 seeds).
  HF = composite AUC < 0.75 at any M (mean over seeds) -> trivialization
       concern was real; composite does not generalize.
  MB = otherwise (composite works at saturated regimes but degrades;
       characterize the limit).

FORMULA SELF-TESTS:
  1. N == 4096 (PROT-018).
  2. M_GRID_FULL = [128, 4096, 8192, 16384].
  3. composite = max-of-z(signals); composite_weighted = grid-search OLS.
  4. AUC computed via Mann-Whitney U; uses LABEL = 1 for any non-exact
     query (OOS + borderline), 0 for in-store.
  5. Borderline noise scale = 0.1 (BSC flip probability), chosen to be
     non-trivial but recoverable.

OOM CHECK:
  N=4096, M_max=16384. Codebook = 256 MiB. W = 64 MiB. Replica W = 64 MiB.
  Query batches: 150 x 4096 fp32 = 2.5 MiB. Peak ~500 MiB. Fits 8 GiB GPU.

TIMEOUT ESTIMATE:
  Per cell: ~30-60s (5 signals over 150 queries + 5-d simplex grid search
  for composite weights, 5^5=3125 configs). 4 M x 5 seeds = 20 cell-seeds.
  Mid-estimate 40s * 20 = 800s. With margin 3000s. Budget 14400s.

N-suffix: _n4096 (PROT-018).
Anchor: multi_signal_kf1_refinement_v1_n4096
Queue: overnight_queue
Pre-reg: preregs/2026-05-30_multi_signal_kf1_refinement_v1_n4096.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import importlib.util
import json
import math
import os
import time
from pathlib import Path
from typing import Dict, List, Tuple

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._metric_battery import make_substrate  # noqa: E402

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_g4", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key


# PROT-018: _n4096 binds N = 4096
N = 4096
N_FULL  = N
N_SMOKE = 1024
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

M_GRID_FULL  = [128, 4096, 8192, 16384]
M_GRID_SMOKE = [64, 256]
SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

BETA = 8.0
TOP_K_SIG = 32
N_PROBE_IN = 50
N_PROBE_OUT = 50
N_PROBE_BORDER = 50
BORDER_NOISE = 0.10  # BSC flip probability for borderline queries (10% of dims)

SIGNAL_NAMES = ["posterior_entropy", "spectral_spread",
                "bundle_norm", "geom_dist", "replica_consistency"]

# Pre-registered thresholds
HP_AUC = 0.90
HP_DISAGREE_FRAC = 0.05    # at least 5% query disagreement
HP_RESOLUTION = 0.75       # composite right when signals disagree
HP_SEEDS_MIN = 3
HF_AUC_BELOW = 0.75


def get_output_dir(default_name: str = "multi_signal_kf1_refinement_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def roc_auc(labels: List[int], scores: List[float]) -> float:
    n_pos = sum(labels)
    n_neg = len(labels) - n_pos
    if n_pos == 0 or n_neg == 0:
        return 0.5
    pairs = sorted(zip(scores, labels), key=lambda x: x[0])
    sum_pos_ranks = 0
    for rank, (_, lab) in enumerate(pairs, start=1):
        if lab == 1:
            sum_pos_ranks += rank
    u = sum_pos_ranks - n_pos * (n_pos + 1) / 2
    return float(u / (n_pos * n_neg))


def compute_signals(W: torch.Tensor, codebook: torch.Tensor,
                     keys: torch.Tensor, N_use: int, beta: float,
                     top_k: int, W_replica: torch.Tensor) -> Dict[str, torch.Tensor]:
    out = keys @ W.T                       # (B, N)
    sims = (codebook @ out.T) / N_use      # (C, B)
    P = torch.softmax(beta * sims, dim=0)  # (C, B)
    eps = 1e-12
    H = -(P * (P + eps).log()).sum(dim=0)
    topk = torch.topk(P, top_k, dim=0).values
    spread = topk.std(dim=0)
    norms = out.norm(dim=1)
    stored_sims = (keys @ out.T) / N_use
    max_stored = stored_sims.max(dim=0).values
    geom_dist = 1.0 - max_stored
    out_r = keys @ W_replica.T
    cs = torch.nn.functional.cosine_similarity(out, out_r, dim=1)
    replica_inconsistency = 1.0 - cs
    return {
        "posterior_entropy": H,
        "spectral_spread": -spread,
        "bundle_norm": -norms,
        "geom_dist": geom_dist,
        "replica_consistency": replica_inconsistency,
    }


def measure_cell(N_use: int, M: int, seed: int,
                  device: torch.device) -> Dict:
    codebook, W, keys, _vals, key_idx, _vi = make_substrate(N_use, M, seed, device)
    C = codebook.shape[0]
    _, W_replica, _, _, _, _ = make_substrate(N_use, M, seed + 17000, device)

    n_in = min(N_PROBE_IN, M)
    in_keys = keys[:n_in]

    # OOS keys: codebook indices not in key_idx
    stored_set = set(key_idx[:M].tolist())
    available = [i for i in range(C) if i not in stored_set]
    n_out = min(N_PROBE_OUT, len(available))
    gen = torch.Generator(device=device).manual_seed(seed + 31337)
    perm = torch.randperm(len(available), generator=gen, device=device)[:n_out]
    oos_codebook_idx = torch.tensor([available[int(i)] for i in perm.tolist()],
                                     dtype=torch.long, device=device)
    oos_keys = codebook[oos_codebook_idx]

    # BORDERLINE: take in-store keys and flip BORDER_NOISE fraction of bits
    n_border = min(N_PROBE_BORDER, M)
    border_src = in_keys[:n_border].clone()  # bipolar +-1
    # flip mask: each dim flipped with prob BORDER_NOISE
    flip_gen = torch.Generator(device=device).manual_seed(seed + 91113)
    flip = (torch.rand(border_src.shape, generator=flip_gen, device=device)
            < BORDER_NOISE)
    border_keys = border_src.clone()
    border_keys[flip] = -border_keys[flip]

    in_signals = compute_signals(W, codebook, in_keys, N_use, BETA, TOP_K_SIG,
                                   W_replica)
    oos_signals = compute_signals(W, codebook, oos_keys, N_use, BETA, TOP_K_SIG,
                                    W_replica)
    border_signals = compute_signals(W, codebook, border_keys, N_use, BETA,
                                       TOP_K_SIG, W_replica)

    # Per-signal AUC across the full 150-query set; label=1 for non-exact
    # (OOS + border), label=0 for in-store.
    per_signal_auc: Dict[str, float] = {}
    sig_arrays: Dict[str, torch.Tensor] = {}
    for name in SIGNAL_NAMES:
        in_vals = in_signals[name]
        oos_vals = oos_signals[name]
        border_vals = border_signals[name]
        all_scores = torch.cat([in_vals, oos_vals, border_vals]).tolist()
        labels = ([0] * in_vals.shape[0]
                   + [1] * oos_vals.shape[0]
                   + [1] * border_vals.shape[0])
        per_signal_auc[name] = round(roc_auc(labels, all_scores), 5)
        sig_arrays[name] = torch.cat([in_vals, oos_vals, border_vals]).cpu()

    # z-normalize
    z_arrays: Dict[str, torch.Tensor] = {}
    for name in SIGNAL_NAMES:
        a = sig_arrays[name]
        if a.std() < 1e-9:
            z_arrays[name] = a * 0.0
        else:
            z_arrays[name] = (a - a.mean()) / a.std()

    labels_full = ([0] * in_signals[SIGNAL_NAMES[0]].shape[0]
                    + [1] * oos_signals[SIGNAL_NAMES[0]].shape[0]
                    + [1] * border_signals[SIGNAL_NAMES[0]].shape[0])

    z_stack = torch.stack([z_arrays[n] for n in SIGNAL_NAMES], dim=0)
    max_z = z_stack.max(dim=0).values.tolist()
    auc_max = roc_auc(labels_full, max_z)

    # Coarse 5-dim simplex grid for composite weights
    best_auc_w = 0.0
    best_w: List[float] = [0.2] * 5
    grid_pts = [0.0, 0.25, 0.5, 0.75, 1.0]
    z_stack_arr = z_stack
    best_comp_scores: List[float] = []
    for w0 in grid_pts:
      for w1 in grid_pts:
        for w2 in grid_pts:
          for w3 in grid_pts:
            for w4 in grid_pts:
                s = w0 + w1 + w2 + w3 + w4
                if s < 0.5:
                    continue
                w = torch.tensor([w0, w1, w2, w3, w4]) / s
                comp = (w.view(-1, 1) * z_stack_arr).sum(dim=0).tolist()
                auc_try = roc_auc(labels_full, comp)
                if auc_try > best_auc_w:
                    best_auc_w = auc_try
                    best_w = w.tolist()
                    best_comp_scores = comp

    # Signal-disagreement and resolution_accuracy:
    # per-query, each signal is "say label 1" if z > 0 (i.e. above mean).
    # disagreement: at least 2 of 5 signals say 1 AND at least 2 say 0.
    # resolution_accuracy = fraction of disagreement queries where composite
    # is correct (composite score > 0 if label==1 else <=0).
    per_signal_call = (z_stack > 0).int()  # (5, Q)
    n_pos_signals = per_signal_call.sum(dim=0)
    disagree_mask = ((n_pos_signals >= 2) & (n_pos_signals <= 3))
    disagree_n = int(disagree_mask.sum().item())
    disagree_frac = disagree_n / per_signal_call.shape[1]
    resolution_accuracy = 0.0
    if disagree_n > 0:
        comp_tensor = (torch.tensor(best_comp_scores)
                        if best_comp_scores else z_stack.max(dim=0).values)
        comp_call = (comp_tensor > 0).int()
        labels_t = torch.tensor(labels_full, dtype=torch.int32)
        right = (comp_call == labels_t)[disagree_mask]
        resolution_accuracy = float(right.float().mean().item())

    # FPR / FNR at composite-call (threshold 0)
    comp_tensor_full = (torch.tensor(best_comp_scores)
                         if best_comp_scores else z_stack.max(dim=0).values)
    comp_call_full = (comp_tensor_full > 0).int()
    labels_t_full = torch.tensor(labels_full, dtype=torch.int32)
    tp = int(((comp_call_full == 1) & (labels_t_full == 1)).sum().item())
    fp = int(((comp_call_full == 1) & (labels_t_full == 0)).sum().item())
    tn = int(((comp_call_full == 0) & (labels_t_full == 0)).sum().item())
    fn = int(((comp_call_full == 0) & (labels_t_full == 1)).sum().item())
    fpr = fp / max(1, fp + tn)
    fnr = fn / max(1, fn + tp)

    del codebook, W, W_replica, keys
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return {"M": int(M), "seed": int(seed), "N": int(N_use),
            "per_signal_auc": per_signal_auc,
            "composite_max_auc": round(auc_max, 5),
            "composite_weighted_auc": round(best_auc_w, 5),
            "composite_weights": [round(w, 4) for w in best_w],
            "signal_disagreement_rate": round(disagree_frac, 5),
            "resolution_accuracy": round(resolution_accuracy, 5),
            "fpr": round(fpr, 5), "fnr": round(fnr, 5)}


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("G4_INCONCLUSIVE", "no cells")

    by_M: Dict[int, List[Dict]] = {}
    for c in cells:
        by_M.setdefault(c["M"], []).append(c)

    mean_auc_per_M: Dict[int, float] = {}
    seeds_pass_per_M: Dict[int, int] = {}
    mean_disagree_per_M: Dict[int, float] = {}
    mean_resolution_per_M: Dict[int, float] = {}
    for M, cs in by_M.items():
        aucs = [c["composite_weighted_auc"] for c in cs]
        mean_auc_per_M[M] = sum(aucs) / len(aucs) if aucs else 0.0
        seeds_pass_per_M[M] = sum(
            1 for c in cs
            if (c["composite_weighted_auc"] >= HP_AUC
                and c["signal_disagreement_rate"] >= HP_DISAGREE_FRAC
                and c["resolution_accuracy"] >= HP_RESOLUTION))
        mean_disagree_per_M[M] = (sum(c["signal_disagreement_rate"] for c in cs)
                                    / len(cs))
        mean_resolution_per_M[M] = (sum(c["resolution_accuracy"] for c in cs)
                                      / len(cs))

    hf_violation_M = [M for M, a in mean_auc_per_M.items() if a < HF_AUC_BELOW]

    # HP: composite AUC >= HP_AUC at ALL 4 M values AND >=3/5 seeds pass full
    # HP condition (auc + disagreement + resolution).
    hp_all_M_auc = all(a >= HP_AUC for a in mean_auc_per_M.values())
    hp_seeds_ok = all(n >= HP_SEEDS_MIN for n in seeds_pass_per_M.values())

    detail = (f"mean_auc_per_M={mean_auc_per_M}; "
              f"seeds_pass={seeds_pass_per_M}; "
              f"mean_disagree={mean_disagree_per_M}; "
              f"mean_resolution={mean_resolution_per_M}; "
              f"n_cells={len(cells)}")

    if hf_violation_M:
        return ("G4_HARD_FAIL",
                f"COMPOSITE_FAILS_AT_M={hf_violation_M}: " + detail)
    if hp_all_M_auc and hp_seeds_ok:
        return ("G4_HARD_PASS", "COMPOSITE_ROBUST_ON_BORDERLINE: " + detail)
    return ("G4_MIDDLE_BAND", "COMPOSITE_DEGRADES_AT_LIMIT: " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096, "PROT-018: _n4096"
    assert M_GRID_FULL == [128, 4096, 8192, 16384]
    assert len(SEEDS_FULL) == 5

    # AUC sanity (ordered separable -> 1.0; all-ties is implementation-defined
    # under rank-sum, just check it is in [0,1]).
    assert roc_auc([0, 0, 1, 1], [0.1, 0.2, 0.8, 0.9]) == 1.0
    a_ties = roc_auc([0, 1, 0, 1], [0.5, 0.5, 0.5, 0.5])
    assert 0.0 <= a_ties <= 1.0

    # HP gate
    fake_hp: List[Dict] = []
    for M in M_GRID_FULL:
        for s in SEEDS_FULL:
            fake_hp.append({"M": M, "seed": s, "N": N_FULL,
                             "per_signal_auc": {n: 0.85 for n in SIGNAL_NAMES},
                             "composite_max_auc": 0.92,
                             "composite_weighted_auc": 0.93,
                             "composite_weights": [0.2]*5,
                             "signal_disagreement_rate": 0.10,
                             "resolution_accuracy": 0.85,
                             "fpr": 0.05, "fnr": 0.05})
    v, _ = compute_verdict(fake_hp); assert "HARD_PASS" in v, v

    # HF gate (one M below 0.75)
    fake_hf: List[Dict] = []
    for M in M_GRID_FULL:
        for s in SEEDS_FULL:
            auc = 0.65 if M == 16384 else 0.85
            fake_hf.append({"M": M, "seed": s, "N": N_FULL,
                             "per_signal_auc": {n: 0.7 for n in SIGNAL_NAMES},
                             "composite_max_auc": auc,
                             "composite_weighted_auc": auc,
                             "composite_weights": [0.2]*5,
                             "signal_disagreement_rate": 0.10,
                             "resolution_accuracy": 0.50,
                             "fpr": 0.20, "fnr": 0.20})
    v, _ = compute_verdict(fake_hf); assert "HARD_FAIL" in v, v

    # MB gate
    fake_mb: List[Dict] = []
    for M in M_GRID_FULL:
        for s in SEEDS_FULL:
            fake_mb.append({"M": M, "seed": s, "N": N_FULL,
                             "per_signal_auc": {n: 0.85 for n in SIGNAL_NAMES},
                             "composite_max_auc": 0.88,
                             "composite_weighted_auc": 0.88,
                             "composite_weights": [0.2]*5,
                             "signal_disagreement_rate": 0.10,
                             "resolution_accuracy": 0.80,
                             "fpr": 0.10, "fnr": 0.10})
    v, _ = compute_verdict(fake_mb); assert "MIDDLE_BAND" in v, f"MB: {v}"

    # Smoke forward pass on CPU
    device = torch.device("cpu")
    out = measure_cell(N_SMOKE, M_GRID_SMOKE[0], 17, device)
    for n in SIGNAL_NAMES:
        assert n in out["per_signal_auc"]
        assert out["per_signal_auc"][n] is not None
    assert out["composite_weighted_auc"] is not None
    assert out["composite_weighted_auc"] >= 0.0
    print(f"[selftest] multi_signal_kf1_refinement_v1_n4096 PASS smoke "
          f"M={M_GRID_SMOKE[0]} comp_w_AUC={out['composite_weighted_auc']:.3f} "
          f"disagree={out['signal_disagreement_rate']:.3f} "
          f"res_acc={out['resolution_accuracy']:.3f}", flush=True)


_instrumentation_selftest()


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    args = p.parse_args()
    if args.self_test:
        sys.exit(0)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    smoke = args.smoke
    N_cfg = N_SMOKE if smoke else N_FULL
    M_grid = M_GRID_SMOKE if smoke else M_GRID_FULL
    seeds  = SEEDS_SMOKE if smoke else SEEDS_FULL

    out_dir = get_output_dir()
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    print(f"[run] multi_signal_kf1_refinement smoke={smoke} N={N_cfg} "
          f"M_grid={M_grid} seeds={seeds} done={len(done)} "
          f"device={device.type}", flush=True)

    cells: List[Dict] = []
    for M in M_grid:
        for seed in seeds:
            ck = f"M{M}_seed{seed}"
            if ck in done:
                body = load_partial_key(out_dir, ck)
                if body is not None:
                    cells.append(body); continue
            try:
                out = measure_cell(N_cfg, M, seed, device)
                write_partial_key(out_dir, ck, out)
                cells.append(out)
                print(f"  M={M} seed={seed} "
                      f"comp_w_AUC={out['composite_weighted_auc']:.3f} "
                      f"disagree={out['signal_disagreement_rate']:.3f} "
                      f"res={out['resolution_accuracy']:.3f} "
                      f"({time.time()-t0:.1f}s)", flush=True)
            except (RuntimeError, MemoryError) as e:
                print(f"  M={M} seed={seed} FAILED: {e}", flush=True)
                if device.type == "cuda":
                    torch.cuda.empty_cache()

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {"anchor": "multi_signal_kf1_refinement_v1_n4096", "N": N_cfg,
               "smoke": smoke, "M_grid": M_grid, "seeds": seeds,
               "border_noise": BORDER_NOISE,
               "cells": cells, "verdict": verdict, "verdict_msg": vm,
               "elapsed_s": elapsed}
    payload = {"verdict": verdict, "verdict_msg": vm,
               "elapsed_s": elapsed, "summary": summary}
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(payload, f, indent=2, default=str)
    print(f"\n[verdict] {verdict}\n[verdict_msg] {vm}\n[elapsed] {elapsed}s",
          flush=True)


if __name__ == "__main__":
    main()
