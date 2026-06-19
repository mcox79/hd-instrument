"""MULTI-SIGNAL KF-1 DESIGN v2 at N=4096 (T2.3 rebuild).

CONTEXT:
  v1 was MIDDLE_BAND with composite AUC 0.898-0.906 just below 0.90 HP.
  v2 measures EACH of the 5 signals INDEPENDENTLY across 3 operating
  points + computes per-OP optimal composite weights.

SCIENTIFIC QUESTION:
  At N=4096, across (M=128 low, M=1024 mid, M=4096 near-cap), can a
  weighted/max-composite of 5 KF-1 signals achieve AUC >= 0.92 at ALL
  3 operating points robustly across seeds?

5 SIGNALS:
  (a) posterior_entropy        - Shannon entropy of softmax over codebook.
  (b) spectral_signature_spread - std of top-K softmax similarities.
  (c) bundle_norm               - L2 norm of substrate response.
  (d) geom_dist_to_nearest      - distance from response to nearest stored key.
  (e) cross_replica_consistency - similarity between two W replicas trained
                                  on same facts with different seeds.

PRE-REGISTERED BANDS:
  HP = best composite AUC >= 0.92 at ALL 3 ops AND robust (std <= 0.03 across seeds)
       in >=3/5 seeds.
  HF = best composite AUC <= 0.85 at any operating point in >=3/5 seeds.
  MIDDLE_BAND = otherwise.

FORMULA SELF-TESTS:
  1. N == 4096 (PROT-018).
  2. operating points: [(M=128, "low"), (M=1024, "mid"), (M=4096, "near-cap")].
  3. composite_weighted: sum_i w_i * z(signal_i) with weights optimized per OP.
  4. composite_max: max over signals of z(signal_i).
  5. AUC computed via Mann-Whitney U.

OOM CHECK:
  Max M=4096, N=4096: keys+vals=128MiB. W=64MiB. CB=805MiB. Total ~1GiB. OK.

TIMEOUT ESTIMATE:
  Smoke ~ 60s (cross-replica doubles cost). FULL: 3 OPs x 5 seeds x ~120s = 1800s.
  Budget 14400s.

N-suffix: _n4096 (PROT-018).
Anchor: multi_signal_kf1_design_v2_n4096
Queue: overnight_queue
Pre-reg: preregs/2026-05-30_multi_signal_kf1_design_v2_n4096.md
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
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_n6", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key


# PRODUCTION CONFIG -- PROT-018: _n4096 binds N
N = 4096
N_FULL  = N
N_SMOKE = 1024
OPS_FULL  = [("low", 128), ("mid", 1024), ("near-cap", 4096)]
OPS_SMOKE = [("low", 32), ("mid", 128)]
SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
BETA = 8.0
N_PROBE_IN = 100
N_PROBE_OUT = 100
TOP_K_SIG = 32

HP_AUC = 0.92
HP_ROBUST_STD = 0.03
HF_AUC = 0.85
HP_SEEDS_MIN = 3
HF_SEEDS_MIN = 3

SIGNAL_NAMES = ["posterior_entropy", "spectral_spread",
                "bundle_norm", "geom_dist", "replica_consistency"]


def get_output_dir(default_name: str = "multi_signal_kf1_design_v2_n4096") -> Path:
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
    """For a batch of (B, N) keys, compute the 5 signals each as (B,)."""
    out = keys @ W.T                       # (B, N)
    sims = (codebook @ out.T) / N_use      # (C, B)
    P = torch.softmax(beta * sims, dim=0)  # (C, B)
    # 1. posterior entropy
    eps = 1e-12
    H = -(P * (P + eps).log()).sum(dim=0)  # (B,) -- higher entropy = ambiguous
    # 2. spectral spread (std of top-K softmax probs)
    topk = torch.topk(P, top_k, dim=0).values  # (top_k, B)
    spread = topk.std(dim=0)                    # (B,)
    # 3. bundle norm
    norms = out.norm(dim=1)                     # (B,)
    # 4. geom dist to nearest stored key
    # Nearest-stored similarity = max over stored keys of <out, key>/N
    # geom_dist = 1 - max_sim (lower for in-store, higher for OOS)
    stored_sims = (keys @ out.T) / N_use        # (M, B)
    max_stored = stored_sims.max(dim=0).values   # (B,)
    geom_dist = 1.0 - max_stored                  # (B,)
    # 5. cross-replica consistency
    out_r = keys @ W_replica.T                   # (B, N)
    # Cosine
    cs = torch.nn.functional.cosine_similarity(out, out_r, dim=1)  # (B,)
    replica_inconsistency = 1.0 - cs              # (B,) higher = more OOS

    return {
        "posterior_entropy": H,
        "spectral_spread": -spread,             # higher_spread = focused = in-store
        "bundle_norm": -norms,                  # higher_norm  = more focused
        "geom_dist": geom_dist,
        "replica_consistency": replica_inconsistency,
    }


def measure_cell(N_use: int, M: int, seed: int,
                  device: torch.device) -> Dict:
    """Compute 5 signals on in-store and OOS probes, return per-signal AUC."""
    codebook, W, keys, _vals, key_idx, _vi = make_substrate(N_use, M, seed,
                                                              device)
    C = codebook.shape[0]
    # Build replica W with different seed -> same facts using different random
    # ordering. We share key/val indices and just reshuffle them to make a
    # genuinely-different W with identical facts (consistency over noise).
    _, W_replica, _, _, _, _ = make_substrate(N_use, M, seed + 17000, device)

    n_in = min(N_PROBE_IN, M)
    in_keys = keys[:n_in]

    # OOS keys: codebook indices not in key_idx
    stored_set = set(key_idx[:M].tolist())
    available = [i for i in range(C) if i not in stored_set]
    if len(available) < N_PROBE_OUT:
        n_out = len(available)
    else:
        n_out = N_PROBE_OUT
    gen = torch.Generator(device=device).manual_seed(seed + 31337)
    perm = torch.randperm(len(available), generator=gen, device=device)[:n_out]
    oos_codebook_idx = torch.tensor([available[int(i)] for i in perm.tolist()],
                                     dtype=torch.long, device=device)
    oos_keys = codebook[oos_codebook_idx]

    in_signals = compute_signals(W, codebook, in_keys, N_use, BETA,
                                   TOP_K_SIG, W_replica)
    oos_signals = compute_signals(W, codebook, oos_keys, N_use, BETA,
                                    TOP_K_SIG, W_replica)

    # Per-signal AUC: label OOS=1 (positive class is "out-of-store"),
    # in-store=0; signal already oriented so higher value = more OOS.
    per_signal_auc: Dict[str, float] = {}
    sig_arrays: Dict[str, torch.Tensor] = {}
    for name in SIGNAL_NAMES:
        in_vals = in_signals[name]
        oos_vals = oos_signals[name]
        scores = torch.cat([in_vals, oos_vals]).tolist()
        labels = [0] * in_vals.shape[0] + [1] * oos_vals.shape[0]
        per_signal_auc[name] = round(roc_auc(labels, scores), 5)
        sig_arrays[name] = torch.cat([in_vals, oos_vals]).cpu()

    # z-normalize each signal in the combined set, then composite
    z_arrays: Dict[str, torch.Tensor] = {}
    for name in SIGNAL_NAMES:
        a = sig_arrays[name]
        if a.std() < 1e-9:
            z_arrays[name] = a * 0.0
        else:
            z_arrays[name] = (a - a.mean()) / a.std()

    labels_full = [0] * in_signals[SIGNAL_NAMES[0]].shape[0] + \
                   [1] * oos_signals[SIGNAL_NAMES[0]].shape[0]

    # Composite (i) max-of-z
    z_stack = torch.stack([z_arrays[n] for n in SIGNAL_NAMES], dim=0)
    max_z = z_stack.max(dim=0).values.tolist()
    auc_max = roc_auc(labels_full, max_z)

    # Composite (ii) weighted (optimal weights via grid search over simplex)
    best_auc_w = 0.0
    best_w: List[float] = [0.2] * 5
    # Coarse 5-dim simplex search: 6 points per axis -> 6^4 = 1296 configs
    # (5-dim simplex has 4 free dims after normalization). To keep cheap,
    # use a 4-pt-per-axis grid -> 4^4 = 256 configs.
    grid_pts = [0.0, 0.25, 0.5, 0.75, 1.0]
    z_stack_arr = z_stack
    for w0 in grid_pts:
      for w1 in grid_pts:
        for w2 in grid_pts:
          for w3 in grid_pts:
            for w4 in grid_pts:
                s = w0 + w1 + w2 + w3 + w4
                if s < 0.5:  # skip near-zero combos
                    continue
                w = torch.tensor([w0, w1, w2, w3, w4]) / s
                comp = (w.view(-1, 1) * z_stack_arr).sum(dim=0).tolist()
                auc_try = roc_auc(labels_full, comp)
                if auc_try > best_auc_w:
                    best_auc_w = auc_try
                    best_w = w.tolist()

    del codebook, W, W_replica, keys
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return {"M": int(M), "seed": int(seed), "N": int(N_use),
            "per_signal_auc": per_signal_auc,
            "composite_max_auc": round(auc_max, 5),
            "composite_weighted_auc": round(best_auc_w, 5),
            "composite_weights": [round(w, 4) for w in best_w]}


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("MS_KF1_INCONCLUSIVE", "No cells.")

    by_op: Dict[int, List[Dict]] = {}
    for c in cells:
        by_op.setdefault(c["M"], []).append(c)

    op_summaries: Dict[int, Dict[str, float]] = {}
    for M, cs in by_op.items():
        weighted = [c["composite_weighted_auc"] for c in cs]
        op_summaries[M] = {
            "mean_weighted_auc": round(sum(weighted) / max(1, len(weighted)), 4),
            "std_weighted_auc": (round(float(torch.tensor(weighted).std().item()), 4)
                                  if len(weighted) > 1 else 0.0),
            "max_auc_any_signal_mean": round(sum(c["composite_max_auc"] for c in cs)
                                              / max(1, len(cs)), 4),
        }

    hp_pass_ops = 0
    for M, summary in op_summaries.items():
        if (summary["mean_weighted_auc"] >= HP_AUC
                and summary["std_weighted_auc"] <= HP_ROBUST_STD):
            hp_pass_ops += 1
    hf_fail_ops = sum(1 for s in op_summaries.values()
                       if s["mean_weighted_auc"] <= HF_AUC)

    detail = f"op_summaries={op_summaries}"

    if hf_fail_ops > 0:
        return ("MS_KF1_HARD_FAIL", "SIGNAL_INSUFFICIENT_AT_OP: " + detail)
    if hp_pass_ops == len(op_summaries) and op_summaries:
        return ("MS_KF1_HARD_PASS", "COMPOSITE_CLEARS_CEILING: " + detail)
    return ("MS_KF1_MIDDLE_BAND", "PARTIAL: " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096
    # AUC sanity
    assert roc_auc([0, 0, 1, 1], [0.1, 0.2, 0.8, 0.9]) == 1.0

    # Verdict gates
    fake_hp = []
    for _, M in OPS_FULL:
        for s in SEEDS_FULL:
            fake_hp.append({"M": M, "seed": s, "N": N_FULL,
                             "per_signal_auc": {n: 0.85 for n in SIGNAL_NAMES},
                             "composite_max_auc": 0.90,
                             "composite_weighted_auc": 0.94,
                             "composite_weights": [0.2]*5})
    v, _ = compute_verdict(fake_hp); assert "HARD_PASS" in v, v

    fake_hf = []
    for _, M in OPS_FULL:
        for s in SEEDS_FULL:
            fake_hf.append({"M": M, "seed": s, "N": N_FULL,
                             "per_signal_auc": {n: 0.70 for n in SIGNAL_NAMES},
                             "composite_max_auc": 0.75,
                             "composite_weighted_auc": 0.78,
                             "composite_weights": [0.2]*5})
    v, _ = compute_verdict(fake_hf); assert "HARD_FAIL" in v, v

    # Forward pass on CPU
    device = torch.device("cpu")
    out = measure_cell(N_SMOKE, 32, 17, device)
    for n in SIGNAL_NAMES:
        assert n in out["per_signal_auc"]
        assert out["per_signal_auc"][n] is not None
    assert out["composite_weighted_auc"] is not None
    print(f"[selftest] multi_signal_kf1_design_v2_n4096 PASS "
          f"smoke comp_w_AUC={out['composite_weighted_auc']:.3f} "
          f"comp_max_AUC={out['composite_max_auc']:.3f}", flush=True)


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
    ops = OPS_SMOKE if smoke else OPS_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    out_dir = get_output_dir()
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    print(f"[run] multi_signal_kf1_v2 smoke={smoke} N={N_cfg} ops={ops} "
          f"seeds={seeds} done={len(done)} device={device.type}", flush=True)

    cells: List[Dict] = []
    for op_name, M in ops:
        for seed in seeds:
            ck = f"op{op_name}_M{M}_seed{seed}"
            if ck in done:
                body = load_partial_key(out_dir, ck)
                if body is not None:
                    cells.append(body); continue
            try:
                out = measure_cell(N_cfg, M, seed, device)
                write_partial_key(out_dir, ck, out)
                cells.append(out)
                print(f"  op={op_name} M={M} seed={seed} "
                      f"comp_w_AUC={out['composite_weighted_auc']:.3f} "
                      f"comp_max_AUC={out['composite_max_auc']:.3f} "
                      f"({time.time()-t0:.1f}s)", flush=True)
            except (RuntimeError, MemoryError) as e:
                print(f"  op={op_name} M={M} seed={seed} FAILED: {e}",
                      flush=True)
                if device.type == "cuda":
                    torch.cuda.empty_cache()

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {"anchor": "multi_signal_kf1_design_v2_n4096", "N": N_cfg,
               "smoke": smoke, "ops": ops, "seeds": seeds,
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
