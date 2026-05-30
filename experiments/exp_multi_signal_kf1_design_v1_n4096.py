"""MULTI-SIGNAL KF-1 DESIGN v1 at N=4096.

CONTEXT:
  Single-signal KF-1 (posterior entropy / max softmax) shifts in failure mode at
  saturation. Composite signal across 5 candidates may extend usable detection
  across operating points: low-M, mid-M, near-capacity.

SCIENTIFIC QUESTION:
  Per (operating point, signal): AUC for in-store vs out-of-store discrimination.
  Composite AUC = weighted-mean and max-of-signals. Does composite extend
  AUC >= 0.90 across all 3 operating points?

5 SIGNALS:
  1. posterior_entropy = -sum P log P (LOWER for in-store -> negate for AUC)
  2. spectral_signature = top-singular-value contribution of W k_query slice
  3. bundle_norm = || W k_query || (norm of continuous output)
  4. geometric_distance = min cos-distance to nearest codeword along W k_query
  5. cross_replica_consistency = correlation of (W1 k, W2 k) under 2 replicas
     (substrate trained with 2 different seed perms of same facts)

PRE-REGISTERED BANDS:
  HARD_PASS: composite AUC (weighted-mean) >= 0.90 across ALL 3 operating points.
  HARD_FAIL: composite AUC <= 0.75 at ANY operating point.
  MIDDLE_BAND: otherwise.

FORMULA SELF-TESTS:
  1. N = 4096 (PROT-018).
  2. 3 operating points: M in [128, 1024, 4096].
  3. 5 signals + 2 composites (weighted_mean, max_of_signals).
  4. AUC in [0,1].

OOM CHECK: N=4096, M_max=4096: keys 67MB; W 64MB; CB 805MB. Total ~940MB. OK.

TIMEOUT ESTIMATE: per cell ~ 5-15s. 3 OP * 5 seeds = 15 cells. ~225s.
  User specified 21600s; honor.

N-suffix: _n4096 -> N = 4096 (PROT-018 binding).
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
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_kf1", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key


# PRODUCTION CONFIG -- PROT-018: _n4096 binds N
N = 4096        # PROT-018 production-N anchor
N_FULL  = N
N_SMOKE = 1024
M_OPS_FULL  = [128, 1024, 4096]
M_OPS_SMOKE = [64, 256, 512]
BETA = 8.0
SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
N_PROBE = 100

SIGNAL_NAMES = ("posterior_entropy", "bundle_norm", "geometric_distance",
                "spectral_signature", "cross_replica")

HP_COMPOSITE = 0.90
HF_COMPOSITE = 0.75


def get_output_dir(default_name: str = "multi_signal_kf1_design_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _auc(pos: torch.Tensor, neg: torch.Tensor) -> float:
    if pos.numel() == 0 or neg.numel() == 0:
        return 0.5
    pos = pos.detach().cpu(); neg = neg.detach().cpu()
    all_s = torch.cat([pos, neg])
    ranks = torch.argsort(torch.argsort(all_s)).float() + 1.0
    pos_rank_sum = ranks[:pos.numel()].sum().item()
    np_, nn_ = pos.numel(), neg.numel()
    return float((pos_rank_sum - np_ * (np_ + 1) / 2.0) / (np_ * nn_))


def _signals_at_op(N_use: int, M: int, seed: int, device: torch.device) -> Dict:
    codebook, W, keys, values, key_idx, val_idx = make_substrate(N_use, M, seed, device)
    C = codebook.shape[0]
    stored_set = set(key_idx.tolist()[:min(key_idx.shape[0], 10000)])
    available = [i for i in range(C) if i not in stored_set]
    n_pos = min(N_PROBE, M)
    n_neg = min(N_PROBE, len(available))
    if n_neg < 1 or n_pos < 1:
        del W, keys, values, codebook
        return {s: 0.5 for s in SIGNAL_NAMES}
    gen = torch.Generator(device=device).manual_seed(seed + 1300)
    perm = torch.randperm(len(available), generator=gen, device=device)[:n_neg]
    oos_idx = torch.tensor([available[int(i)] for i in perm.tolist()],
                            dtype=torch.long, device=device)
    in_keys = keys[:n_pos]
    oos_keys = codebook[oos_idx]

    q_in  = in_keys @ W.T
    q_oos = oos_keys @ W.T
    sims_in  = (codebook @ q_in.T) / N_use
    sims_oos = (codebook @ q_oos.T) / N_use
    P_in  = torch.softmax(BETA * sims_in, dim=0).clamp(1e-12)
    P_oos = torch.softmax(BETA * sims_oos, dim=0).clamp(1e-12)

    # 1. posterior entropy: LOWER for in-store; we use -entropy as the score
    ent_in  = -(P_in  * P_in.log()).sum(dim=0)
    ent_oos = -(P_oos * P_oos.log()).sum(dim=0)
    s_ent_in  = -ent_in
    s_ent_oos = -ent_oos

    # 2. bundle norm: higher for in-store (output aligned with stored value)
    bn_in  = q_in.norm(dim=1)
    bn_oos = q_oos.norm(dim=1)

    # 3. geometric distance: max cosine to nearest codeword (HIGHER for in-store)
    eps = 1e-9
    cos_in  = (codebook @ q_in.T)  / (codebook.norm(dim=1, keepdim=True) *
                                       q_in.norm(dim=1) + eps)
    cos_oos = (codebook @ q_oos.T) / (codebook.norm(dim=1, keepdim=True) *
                                       q_oos.norm(dim=1) + eps)
    geo_in  = cos_in.max(dim=0).values
    geo_oos = cos_oos.max(dim=0).values

    # 4. spectral_signature: simple proxy = top eigenvalue of q q^T per query (= ||q||^2)
    # For non-degenerate measure: use ratio max(sim) / second_max(sim) of codebook
    sims_in_sorted  = sims_in.sort(dim=0, descending=True).values
    sims_oos_sorted = sims_oos.sort(dim=0, descending=True).values
    spec_in  = sims_in_sorted[0] - sims_in_sorted[1]
    spec_oos = sims_oos_sorted[0] - sims_oos_sorted[1]

    # 5. cross-replica: store with 2nd seed permutation and measure W1 k vs W2 k corr
    _, W2, _, _, _, _ = make_substrate(N_use, M, seed + 12345, device)
    q_in2  = in_keys @ W2.T
    q_oos2 = oos_keys @ W2.T
    # correlation of q with q2 should be HIGHER for in-store (true signal stable
    # across replicas) than for OOS (random/noise)
    corr_in  = torch.nn.functional.cosine_similarity(q_in, q_in2, dim=1)
    corr_oos = torch.nn.functional.cosine_similarity(q_oos, q_oos2, dim=1)

    out = {
        "posterior_entropy": _auc(s_ent_in,  s_ent_oos),
        "bundle_norm":       _auc(bn_in,     bn_oos),
        "geometric_distance":_auc(geo_in,    geo_oos),
        "spectral_signature":_auc(spec_in,   spec_oos),
        "cross_replica":     _auc(corr_in,   corr_oos),
    }
    # composites
    # weighted-mean: equal weights
    out["composite_wmean"] = float(sum(out[s] for s in SIGNAL_NAMES) / len(SIGNAL_NAMES))
    out["composite_max"]   = float(max(out[s] for s in SIGNAL_NAMES))
    for k in list(out.keys()):
        out[k] = round(out[k], 5)

    del W, W2, keys, values, codebook
    if device.type == 'cuda':
        torch.cuda.empty_cache()
    return out


def compute_verdict(per_op: Dict[int, Dict]) -> Tuple[str, str]:
    if not per_op:
        return ("KF1MS_INCONCLUSIVE", "No operating points.")
    composites = [per_op[k]["composite_wmean"] for k in per_op]
    detail = "  ".join(f"M={k} wmean_AUC={v['composite_wmean']:.3f}"
                       for k, v in per_op.items())
    min_c = min(composites); max_c = max(composites)
    if min_c <= HF_COMPOSITE:
        return ("KF1MS_HARD_FAIL",
                f"COMPOSITE_LOW: min={min_c:.3f} <= {HF_COMPOSITE}. " + detail)
    if min_c >= HP_COMPOSITE:
        return ("KF1MS_HARD_PASS",
                f"COMPOSITE_HIGH: min={min_c:.3f} >= {HP_COMPOSITE}. " + detail)
    return ("KF1MS_MIDDLE_BAND",
            f"COMPOSITE_INT: min={min_c:.3f} in ({HF_COMPOSITE},{HP_COMPOSITE}). "
            + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096
    # Verdict gates
    fake_hp = {128: {"composite_wmean": 0.95}, 1024: {"composite_wmean": 0.93},
               4096: {"composite_wmean": 0.91}}
    v, _ = compute_verdict(fake_hp); assert "HARD_PASS" in v, v
    fake_hf = {128: {"composite_wmean": 0.70}, 1024: {"composite_wmean": 0.95},
               4096: {"composite_wmean": 0.95}}
    v, _ = compute_verdict(fake_hf); assert "HARD_FAIL" in v, v
    fake_mb = {128: {"composite_wmean": 0.80}, 1024: {"composite_wmean": 0.85},
               4096: {"composite_wmean": 0.82}}
    v, _ = compute_verdict(fake_mb); assert "MIDDLE_BAND" in v, v

    device = torch.device("cpu")
    sig = _signals_at_op(N_SMOKE, 64, 17, device)
    for k in SIGNAL_NAMES + ("composite_wmean", "composite_max"):
        assert sig[k] is not None and not math.isnan(sig[k]), f"signal {k}: {sig}"
        assert 0.0 <= sig[k] <= 1.0, f"AUC out of range for {k}: {sig[k]}"
    print(f"[selftest] multi_signal_kf1_design_v1_n4096 PASS "
          f"wmean={sig['composite_wmean']:.3f} max={sig['composite_max']:.3f}",
          flush=True)


_instrumentation_selftest()


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    args = p.parse_args()
    if args.self_test:
        sys.exit(0)
    device_str = "cuda" if torch.cuda.is_available() else "cpu"
    device = torch.device(device_str)
    smoke = args.smoke
    N_cfg = N_SMOKE if smoke else N_FULL
    M_ops = M_OPS_SMOKE if smoke else M_OPS_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    out_dir = get_output_dir()
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    print(f"[run] multi_signal_kf1 smoke={smoke} N={N_cfg} M_ops={M_ops} "
          f"seeds={seeds} done={len(done)} device={device_str}", flush=True)

    cells: List[Dict] = []
    for M in M_ops:
        per_M_seeds: List[Dict] = []
        for seed in seeds:
            ck = f"M{M}_seed{seed}"
            if ck in done:
                body = load_partial_key(out_dir, ck)
                if body is not None:
                    per_M_seeds.append(body)
                    continue
            try:
                sig = _signals_at_op(N_cfg, M, seed, device)
                sig["M"] = M; sig["seed"] = seed
                write_partial_key(out_dir, ck, sig)
                per_M_seeds.append(sig)
                print(f"  M={M} seed={seed} wmean={sig['composite_wmean']:.3f} "
                      f"max={sig['composite_max']:.3f} "
                      f"({time.time()-t0:.1f}s)", flush=True)
            except (RuntimeError, MemoryError) as e:
                print(f"  M={M} seed={seed} FAILED: {e}", flush=True)
                if device.type == 'cuda':
                    torch.cuda.empty_cache()
        cells.extend(per_M_seeds)

    # Aggregate per operating point: mean over seeds
    per_op: Dict[int, Dict] = {}
    for M in M_ops:
        rows = [c for c in cells if c.get("M") == M]
        if rows:
            per_op[M] = {
                "composite_wmean": round(sum(r["composite_wmean"] for r in rows) / len(rows), 5),
                "composite_max":   round(sum(r["composite_max"]   for r in rows) / len(rows), 5),
                "n_seeds": len(rows),
            }
            for s in SIGNAL_NAMES:
                per_op[M][s] = round(sum(r[s] for r in rows) / len(rows), 5)

    verdict, vm = compute_verdict(per_op)
    elapsed = round(time.time() - t0, 2)
    summary = {"anchor": "multi_signal_kf1_design_v1_n4096", "N": N_cfg,
               "smoke": smoke, "M_ops": M_ops, "seeds": seeds,
               "per_op": per_op, "cells": cells,
               "verdict": verdict, "verdict_msg": vm, "elapsed_s": elapsed}
    payload = {"verdict": verdict, "verdict_msg": vm,
               "elapsed_s": elapsed, "summary": summary}
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(payload, f, indent=2, default=str)
    print(f"\n[verdict] {verdict}\n[verdict_msg] {vm}\n[elapsed] {elapsed}s",
          flush=True)


if __name__ == "__main__":
    main()
