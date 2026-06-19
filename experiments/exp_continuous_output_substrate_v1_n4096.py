"""CONTINUOUS-OUTPUT SUBSTRATE v1 at N=4096.

CONTEXT:
  Standard substrate returns argmax(W @ k_query). What if we ALSO test the
  CONTINUOUS output W @ k_query (no argmax)? This unlocks:
    - Geometric interpolation (query midway between two stored keys returns
      the geometric mean of values)
    - Hallucination signal from softmax distribution shape (max - mean)
    - Composition through linear ops on un-decoded outputs

SCIENTIFIC QUESTION:
  Does W @ k_alpha for k_alpha = 0.5*(k_i + k_j) approximate 0.5*(v_i + v_j)?
  Is max(softmax) - mean(softmax) a usable in/out-of-store discriminator?
  Does argmax-consistency hold at all stored keys (sanity)?
  Does KF-2 edit isolation survive in this continuous regime?

PRE-REGISTERED BANDS (composite):
  HARD_PASS:
    interp_cosine >= 0.7 AND
    hallu_signal_AUC >= 0.85 AND
    argmax_consistency >= 0.95 AND
    KF-2 max_iso <= 0.10
  HARD_FAIL: interp_cosine <= 0.3 OR argmax_consistency <= 0.5.
  MIDDLE_BAND: otherwise.

FORMULA SELF-TESTS:
  1. N = 4096 (PROT-018).
  2. M = 512 (production), 64 (smoke).
  3. interp_cosine in [-1, 1].
  4. AUC computed via simple rank-based estimator on (n_pos, n_neg) scores.

OOM CHECK:
  N=4096, M=512: keys 512*4096*4=8.4MB. W=64MB. CB=805MB (49152*4096*4).
  Total ~880MB. OK.

TIMEOUT ESTIMATE:
  Per cell: substrate build + 4 metric panels. Smoke ~5s, FULL ~30s.
  5 seeds * 30s = 150s. With margin: 1500s. User said 21600s. Honor 21600s.

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

from experiments._metric_battery import (  # noqa: E402
    make_substrate, metric_max_iso,
)

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_cont", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key


# PRODUCTION CONFIG -- PROT-018: _n4096 binds N
N = 4096        # PROT-018 production-N anchor
N_FULL  = N
N_SMOKE = 1024
M_FULL  = 512
M_SMOKE = 64
BETA    = 8.0   # mid-temperature for hallu signal
SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
N_INTERP  = 64    # number of interp pairs
N_PROBE   = 200

HP_INTERP_COS = 0.7
HP_HALLU_AUC  = 0.85
HP_ARGMAX_CONS = 0.95
HP_KF2_MAX_ISO = 0.10
HF_INTERP_COS = 0.3
HF_ARGMAX_CONS = 0.5


def get_output_dir(default_name: str = "continuous_output_substrate_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _auc_rank(pos_scores: torch.Tensor, neg_scores: torch.Tensor) -> float:
    """Rank-sum AUC estimator."""
    if pos_scores.numel() == 0 or neg_scores.numel() == 0:
        return 0.5
    all_s = torch.cat([pos_scores, neg_scores])
    ranks = torch.argsort(torch.argsort(all_s)).float() + 1.0
    pos_rank_sum = ranks[:pos_scores.numel()].sum().item()
    n_pos = pos_scores.numel(); n_neg = neg_scores.numel()
    auc = (pos_rank_sum - n_pos * (n_pos + 1) / 2.0) / (n_pos * n_neg)
    return float(auc)


def measure_continuous(N_use: int, M: int, seed: int, device: torch.device) -> Dict:
    """Build substrate + run 4 measurement panels."""
    codebook, W, keys, values, key_idx, val_idx = make_substrate(N_use, M, seed, device)
    C = codebook.shape[0]

    # Panel 1: argmax consistency on stored keys (subset)
    n_arg = min(N_PROBE, M)
    probe_keys = keys[:n_arg]
    sims = (codebook @ (probe_keys @ W.T).T) / N_use
    pred = torch.argmax(sims, dim=0)
    argmax_cons = float((pred == (val_idx[:n_arg] % C).to(device)).float().mean().item())

    # Panel 2: geometric interpolation
    gen = torch.Generator(device=device).manual_seed(seed + 1100)
    n_int = min(N_INTERP, M // 2)
    if n_int < 1:
        interp_cos_mean = 0.0
    else:
        perm = torch.randperm(M, generator=gen, device=device)
        idx_a = perm[:n_int]
        idx_b = perm[n_int:2 * n_int]
        k_a = keys[idx_a]
        k_b = keys[idx_b]
        v_a = values[idx_a]
        v_b = values[idx_b]
        k_alpha = 0.5 * (k_a + k_b)
        # Continuous output: W @ k (per row)
        out = k_alpha @ W.T              # (n_int, N)
        target = 0.5 * (v_a + v_b)
        # Cosine
        eps = 1e-9
        cos = (out * target).sum(dim=1) / (
            out.norm(dim=1) * target.norm(dim=1) + eps)
        interp_cos_mean = float(cos.mean().item())

    # Panel 3: hallucination signal (softmax max - mean) on in-store vs OOS
    stored_set = set(key_idx.tolist()[:min(key_idx.shape[0], 10000)])
    available = [i for i in range(C) if i not in stored_set]
    if not available:
        hallu_auc = 0.5
    else:
        n_pos = min(N_PROBE, M)
        n_neg = min(N_PROBE, len(available))
        in_keys = keys[:n_pos]
        gen2 = torch.Generator(device=device).manual_seed(seed + 1200)
        perm = torch.randperm(len(available), generator=gen2, device=device)[:n_neg]
        oos_idx = torch.tensor([available[int(i)] for i in perm.tolist()],
                                dtype=torch.long, device=device)
        oos_keys = codebook[oos_idx]
        q_in  = in_keys @ W.T
        q_oos = oos_keys @ W.T
        sims_in  = (codebook @ q_in.T) / N_use
        sims_oos = (codebook @ q_oos.T) / N_use
        P_in  = torch.softmax(BETA * sims_in, dim=0)
        P_oos = torch.softmax(BETA * sims_oos, dim=0)
        # Score: max - mean (sharper for in-store)
        sig_in  = P_in.max(dim=0).values - P_in.mean(dim=0)
        sig_oos = P_oos.max(dim=0).values - P_oos.mean(dim=0)
        # AUC: positives = in-store have HIGHER signal than OOS
        hallu_auc = _auc_rank(sig_in.detach().cpu(), sig_oos.detach().cpu())

    # Panel 4: KF-2 isolation (reuse battery)
    iso = metric_max_iso(W, codebook, key_idx, val_idx, N_use, BETA, seed,
                         device, n_probe=N_PROBE, n_edits=16)
    kf2_max_iso = iso["max_iso"]

    del W, keys, values, codebook
    if device.type == 'cuda':
        torch.cuda.empty_cache()

    return {
        "interp_cosine": round(interp_cos_mean, 5),
        "hallu_signal_AUC": round(hallu_auc, 5),
        "argmax_consistency": round(argmax_cons, 5),
        "kf2_max_iso": round(kf2_max_iso, 5),
        "M": M, "seed": seed, "beta": BETA,
    }


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("CONT_INCONCLUSIVE", "No cells.")
    interp = sum(c["interp_cosine"] for c in cells) / len(cells)
    hallu  = sum(c["hallu_signal_AUC"] for c in cells) / len(cells)
    argc   = sum(c["argmax_consistency"] for c in cells) / len(cells)
    iso    = sum(c["kf2_max_iso"] for c in cells) / len(cells)
    detail = (f"interp_cos={interp:.3f} hallu_AUC={hallu:.3f} "
              f"argmax_cons={argc:.3f} kf2_max_iso={iso:.3f} "
              f"n_seeds={len(cells)}")
    if interp <= HF_INTERP_COS or argc <= HF_ARGMAX_CONS:
        return ("CONT_HARD_FAIL", f"FAIL: interp or argmax broken. " + detail)
    if (interp >= HP_INTERP_COS and hallu >= HP_HALLU_AUC
            and argc >= HP_ARGMAX_CONS and iso <= HP_KF2_MAX_ISO):
        return ("CONT_HARD_PASS",
                f"PASS: continuous-output viable. " + detail)
    return ("CONT_MIDDLE_BAND", f"MIXED: " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"
    # Verdict gates
    fake_hp = [{"interp_cosine": 0.8, "hallu_signal_AUC": 0.9,
                "argmax_consistency": 0.97, "kf2_max_iso": 0.05}] * 3
    v, _ = compute_verdict(fake_hp); assert "HARD_PASS" in v, v
    fake_hf = [{"interp_cosine": 0.1, "hallu_signal_AUC": 0.5,
                "argmax_consistency": 0.9, "kf2_max_iso": 0.5}] * 3
    v, _ = compute_verdict(fake_hf); assert "HARD_FAIL" in v, v
    fake_mb = [{"interp_cosine": 0.5, "hallu_signal_AUC": 0.7,
                "argmax_consistency": 0.9, "kf2_max_iso": 0.05}] * 3
    v, _ = compute_verdict(fake_mb); assert "MIDDLE_BAND" in v, v

    # Smoke: 1 seed, small N
    device = torch.device("cpu")
    out = measure_continuous(N_SMOKE, M_SMOKE, 17, device)
    for k in ("interp_cosine", "hallu_signal_AUC", "argmax_consistency",
              "kf2_max_iso"):
        v_ = out.get(k)
        assert v_ is not None and not (isinstance(v_, float) and math.isnan(v_)), (
            f"smoke metric {k} null/NaN: {out}")
    print(f"[selftest] continuous_output_substrate_v1_n4096 PASS "
          f"interp={out['interp_cosine']:.3f} "
          f"hallu_AUC={out['hallu_signal_AUC']:.3f} "
          f"argmax={out['argmax_consistency']:.3f} "
          f"iso={out['kf2_max_iso']:.3f}", flush=True)


_instrumentation_selftest()


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)
    device_str = "cuda" if torch.cuda.is_available() else "cpu"
    device = torch.device(device_str)
    smoke = args.smoke

    N_cfg = N_SMOKE if smoke else N_FULL
    M_cfg = M_SMOKE if smoke else M_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    out_dir = get_output_dir()
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    print(f"[run] continuous_output_substrate_v1_n4096 smoke={smoke} N={N_cfg} "
          f"M={M_cfg} seeds={seeds} done={len(done)} device={device_str}",
          flush=True)

    cells: List[Dict] = []
    for seed in seeds:
        ck = f"seed{seed}"
        if ck in done:
            body = load_partial_key(out_dir, ck)
            if body is not None:
                cells.append(body)
                continue
        try:
            out = measure_continuous(N_cfg, M_cfg, seed, device)
            write_partial_key(out_dir, ck, out)
            cells.append(out)
            print(f"  seed={seed} interp={out['interp_cosine']:.3f} "
                  f"hallu={out['hallu_signal_AUC']:.3f} "
                  f"argmax={out['argmax_consistency']:.3f} "
                  f"iso={out['kf2_max_iso']:.3f} "
                  f"({time.time()-t0:.1f}s)", flush=True)
        except (RuntimeError, MemoryError) as e:
            print(f"  seed={seed} FAILED: {type(e).__name__}: {e}", flush=True)
            if device.type == 'cuda':
                torch.cuda.empty_cache()

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {"anchor": "continuous_output_substrate_v1_n4096", "N": N_cfg,
               "smoke": smoke, "M": M_cfg, "seeds": seeds,
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
