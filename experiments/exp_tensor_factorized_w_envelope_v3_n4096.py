"""TENSOR-FACTORIZED W ENVELOPE v3 at N=4096.

CONTEXT (F2 v2 follow-up):
  v1 (commit 75c565d) HP-passed at single M=512 with sub-capacity caveat.
  v2 was shipped to complete the envelope LIFT but was interrupted by the
  user-pause action (KILLED mid-run, partial cell-seed files may exist on
  remote). Per verdict_handler recommendation, v3 is a FRESH ship with
  identical scientific spec to v2; per-cell-seed checkpointing (PROT-021)
  ensures any further interruption is bounded.

SCIENTIFIC QUESTION:
  At N=4096, sweep (M, rank) where M in [512, 2048, 8192] and
  rank in [128, 256, 512, 1024, 2048]:
    - Does rank <= N/4 (rank=1024) preserve >= 95% full-rank accuracy
      across ALL M values tested?
    - Or does factorization break at high M (substrate W "fills up" rank
      faster than compression can handle)?

PRE-REGISTERED BANDS:
  Per (M, rank, seed) cell: compute retention_ratio = ret_factored / ret_full.
  HARD_PASS: rank <= 1024 preserves >= 95% retention_ratio at ALL 3 M
    values in >= 3/5 seeds.
  HARD_FAIL: any rank loses >= 30% retention (retention_ratio <= 0.70)
    at the highest M (8192) in 3+/5 seeds.
  MIDDLE_BAND: otherwise.

FORMULA SELF-TESTS:
  1. N == 4096 (PROT-018).
  2. Cell grid: 3 M x 5 ranks x 5 seeds = 75 cell-seeds.
  3. memory_ratio formula: 2 * rank / N (only depends on N and rank).
  4. retention_ratio in [0, infinity); >=0.95 = HP per-cell.

OOM CHECK:
  Largest M=8192, N=4096 on CPU: keys=8192*4096*4=134MB. W=64MB.
  CB=805MB. SVD ~192MB peak. Total ~1.2GB. OK on CPU.

TIMEOUT ESTIMATE:
  CPU: per cell ~30-60s (SVD + 5 rank reconstructions + 5 retention probes).
  75 cell-seeds * 45s avg = 3375s. Budget 21600s for safety margin.

CHECKPOINT (PROT-021):
  Per-cell-seed granularity. 75 partial files. Re-running v3 from scratch
  is fine -- interruption cost is bounded to <=1 cell-seed.

N-suffix: _n4096 (PROT-018).
Anchor: tensor_factorized_w_envelope_v3_n4096
Queue: remote_cpu_queue (CPU envelope sweep)
Pre-reg: preregs/2026-05-30_tensor_factorized_w_envelope_v3_n4096.md
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
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_tfe_v3", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key


# PRODUCTION CONFIG -- PROT-018: _n4096 binds N
N = 4096        # PROT-018 production-N anchor
N_FULL  = N
N_SMOKE = 1024
M_SWEEP_FULL  = [512, 2048, 8192]
M_SWEEP_SMOKE = [64, 256]
RANKS_FULL    = [128, 256, 512, 1024, 2048]
RANKS_SMOKE   = [32, 64, 128]
BETA = 8.0
SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
N_PROBE = 200

HP_RANK_MAX        = 1024       # ranks at-or-below this must preserve retention
HP_RETENTION_RATIO = 0.95
HF_RETENTION_RATIO = 0.70       # below this at top M = HF
HP_SEEDS_MIN       = 3          # 3 of 5
HF_M              = 8192        # break manifests at top M
HF_SEEDS_MIN      = 3


def factorize_w(W: torch.Tensor, rank: int) -> torch.Tensor:
    U, S, Vh = torch.linalg.svd(W, full_matrices=False)
    U_r = U[:, :rank]
    S_r = S[:rank]
    Vh_r = Vh[:rank, :]
    return U_r @ torch.diag(S_r) @ Vh_r


def get_output_dir(default_name: str = "tensor_factorized_w_envelope_v3_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def measure_retention(W: torch.Tensor, codebook: torch.Tensor,
                       keys: torch.Tensor, val_idx: torch.Tensor,
                       N_use: int) -> float:
    C = codebook.shape[0]
    n = min(N_PROBE, keys.shape[0])
    probe_keys = keys[:n]
    probe_val  = val_idx[:n] % C
    sims = (codebook @ (probe_keys @ W.T).T) / N_use
    pred = torch.argmax(sims, dim=0)
    return float((pred == probe_val.to(W.device)).float().mean().item())


def measure_cell_seed(N_use: int, M: int, seed: int, ranks: List[int],
                       device: torch.device) -> Dict:
    """One (M, seed) cell across all ranks. Per-cell-seed checkpoint."""
    codebook, W, keys, values, key_idx, val_idx = make_substrate(N_use, M, seed, device)
    ret_full = measure_retention(W, codebook, keys, val_idx, N_use)
    rets_by_rank: Dict[int, float] = {}
    ratios_by_rank: Dict[int, float] = {}
    for r in ranks:
        if r > min(W.shape):
            rets_by_rank[r] = ret_full
            ratios_by_rank[r] = 1.0
            continue
        try:
            W_fac = factorize_w(W, r)
            ret = measure_retention(W_fac, codebook, keys, val_idx, N_use)
            rets_by_rank[r] = round(ret, 5)
            ratios_by_rank[r] = round(ret / max(ret_full, 1e-9), 5)
        except RuntimeError as e:
            rets_by_rank[r] = -1.0
            ratios_by_rank[r] = -1.0
    out = {"seed": seed, "M": M,
           "ret_full": round(ret_full, 5),
           "rets_by_rank": rets_by_rank,
           "ratios_by_rank": ratios_by_rank,
           "memory_ratio_per_rank": {r: round(2.0 * r / N_use, 5) for r in ranks}}
    del W, keys, values, codebook
    if device.type == 'cuda':
        torch.cuda.empty_cache()
    return out


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("TFE_V3_INCONCLUSIVE", "No cells.")

    # Group by (M, seed)
    by_seed: Dict[int, Dict[int, Dict]] = {}
    for c in cells:
        by_seed.setdefault(c["seed"], {})[c["M"]] = c

    # HP gate: for each seed, check that ALL M-values have retention_ratio>=0.95
    # for ALL ranks <= HP_RANK_MAX (excluding ranks above HP_RANK_MAX).
    hp_seeds = 0
    for seed, by_M in by_seed.items():
        seed_ok = True
        for M, c in by_M.items():
            for r, ratio in c["ratios_by_rank"].items():
                if r <= HP_RANK_MAX and ratio < HP_RETENTION_RATIO:
                    seed_ok = False
                    break
            if not seed_ok:
                break
        if seed_ok and len(by_M) >= 3:  # all 3 M values present
            hp_seeds += 1

    # HF gate: at top M, any rank loses >= 30% retention in HF_SEEDS_MIN+ seeds
    hf_seeds = 0
    for seed, by_M in by_seed.items():
        if HF_M not in by_M:
            continue
        c = by_M[HF_M]
        if any(ratio <= HF_RETENTION_RATIO for ratio in c["ratios_by_rank"].values()):
            hf_seeds += 1

    detail = (f"hp_seeds={hp_seeds}/{len(by_seed)} "
              f"hf_seeds_at_M{HF_M}={hf_seeds}/{len(by_seed)}")

    if hf_seeds >= HF_SEEDS_MIN:
        return ("TFE_V3_HARD_FAIL", f"FACTORIZATION_BREAKS_AT_HIGH_M: " + detail)
    if hp_seeds >= HP_SEEDS_MIN:
        return ("TFE_V3_HARD_PASS", f"FACTORIZATION_HOLDS_ACROSS_ENVELOPE: " + detail)
    return ("TFE_V3_MIDDLE_BAND", f"PARTIAL: " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096, f"PROT-018: N must be 4096; got {N_FULL}"
    # SVD round-trip
    Wt = torch.randn(8, 8)
    Wf = factorize_w(Wt, 8)
    assert torch.allclose(Wt, Wf, atol=1e-4)
    # Cell counts
    n_full = len(M_SWEEP_FULL) * len(RANKS_FULL) * len(SEEDS_FULL)
    assert n_full == 75, f"cell-seed total mismatch: {n_full}"

    # Verdict gates
    fake_hp = []
    for M in M_SWEEP_FULL:
        for s in SEEDS_FULL:
            fake_hp.append({
                "seed": s, "M": M, "ret_full": 0.95,
                "rets_by_rank": {128: 0.92, 256: 0.94, 512: 0.945, 1024: 0.95, 2048: 0.95},
                "ratios_by_rank": {128: 0.97, 256: 0.99, 512: 0.995, 1024: 1.0, 2048: 1.0},
            })
    v, _ = compute_verdict(fake_hp); assert "HARD_PASS" in v, v

    fake_hf = []
    for M in M_SWEEP_FULL:
        for s in SEEDS_FULL:
            ratios = {128: 0.95, 256: 0.95, 512: 0.95, 1024: 0.95, 2048: 0.95}
            if M == HF_M:
                ratios = {128: 0.3, 256: 0.5, 512: 0.7, 1024: 0.8, 2048: 0.95}
            fake_hf.append({
                "seed": s, "M": M, "ret_full": 0.95,
                "rets_by_rank": {r: 0.95 * v for r, v in ratios.items()},
                "ratios_by_rank": ratios,
            })
    v, _ = compute_verdict(fake_hf); assert "HARD_FAIL" in v, v

    # Smoke on CPU
    device = torch.device("cpu")
    out = measure_cell_seed(N_SMOKE, 64, 17, RANKS_SMOKE, device)
    assert out["ret_full"] is not None
    for r, ret in out["rets_by_rank"].items():
        assert ret >= 0, f"rank {r} negative ret"
    print(f"[selftest] tensor_factorized_w_envelope_v3_n4096 PASS "
          f"smoke M=64 full={out['ret_full']:.3f}", flush=True)


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
    Ms    = M_SWEEP_SMOKE if smoke else M_SWEEP_FULL
    ranks = RANKS_SMOKE if smoke else RANKS_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    out_dir = get_output_dir()
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    print(f"[run] tensor_factorized_w_envelope_v3_n4096 smoke={smoke} N={N_cfg} "
          f"Ms={Ms} ranks={ranks} seeds={seeds} done={len(done)} device={device_str}",
          flush=True)

    cells: List[Dict] = []
    for M in Ms:
        for seed in seeds:
            ck = f"M{M}_seed{seed}"
            if ck in done:
                body = load_partial_key(out_dir, ck)
                if body is not None:
                    cells.append(body); continue
            try:
                out = measure_cell_seed(N_cfg, M, seed, ranks, device)
                write_partial_key(out_dir, ck, out)
                cells.append(out)
                print(f"  {ck} full={out['ret_full']:.3f} "
                      f"ratios={out['ratios_by_rank']} "
                      f"({time.time()-t0:.1f}s)", flush=True)
            except (RuntimeError, MemoryError) as e:
                print(f"  {ck} FAILED: {type(e).__name__}: {e}", flush=True)
                if device.type == 'cuda':
                    torch.cuda.empty_cache()

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {"anchor": "tensor_factorized_w_envelope_v3_n4096", "N": N_cfg,
               "smoke": smoke, "Ms": Ms, "ranks": ranks, "seeds": seeds,
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
