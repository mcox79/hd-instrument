"""CONTINUOUS-OUTPUT SUBSTRATE ENVELOPE v2 at N=4096.

CONTEXT (F1 follow-up):
  v1 (commit 75c565d) ran a single-M cell at M=512 and HP-passed the
  composite continuous-output gate, but cap_map v283 flagged a
  sub-capacity caveat: the test was at a single low M, well below the
  M_c estimated by m_c_probe v1 (16K-20K MIDDLE_BAND). The envelope is
  not lifted until the same 4 metrics hold across a broader M-sweep.

  v2 sweeps M from sub-capacity to near-M_c so we can confirm whether
  the continuous-output regime holds across the full M-band that
  product users will hit.

SCIENTIFIC QUESTION:
  At N=4096 fixed, sweep M in [512, 2048, 8192, 16384]:
    - interp_cosine                  (geometric interpolation)
    - hallu_signal_AUC               (in-store vs OOS softmax shape)
    - argmax_consistency             (sanity)
    - KF-2 max_iso                   (edit isolation)
  Do all four metrics pass their HP thresholds at >= 3/5 seeds in
  >= 3/4 M cells?

PRE-REGISTERED BANDS (per-M-cell composite):
  Per cell (M, seed): same thresholds as v1
    interp_cosine        >= 0.7
    hallu_signal_AUC     >= 0.85
    argmax_consistency   >= 0.95
    kf2_max_iso          <= 0.10
  Cell passes if ALL four hold; cell fails-hard if interp <= 0.3 OR
  argmax <= 0.5.

  HARD_PASS: all 4 metrics pass HP in >= 3/5 seeds at >= 3/4 M cells.
  HARD_FAIL: any metric <= HF threshold in >= 3 M cells.
  MIDDLE_BAND: otherwise.

FORMULA SELF-TESTS:
  1. N == 4096 (PROT-018).
  2. M_sweep_full has 4 cells.
  3. Per-cell pass count formula: 4-of-4 metrics meet HP per seed.

OOM CHECK:
  Largest cell N=4096, M=16384: keys=16384*4096*4 = 268MB. W=64MB.
  CB ~805MB. Total ~1.2GB. OK (well under 6GB cap).

TIMEOUT ESTIMATE:
  Per cell: substrate build + 4 metric panels.
  Smoke ~5s. FULL: 4 M-cells x 5 seeds = 20 cell-runs at ~10-30s each
  (interp + hallu + KF-2 scale roughly linearly in M). ~600s expected.
  Budget 21600s (user-authorized).

N-suffix: _n4096 -> production N = 4096 (PROT-018 binding).
Anchor: continuous_output_substrate_envelope_v2_n4096
Queue: overnight_queue (GPU; N=4096, 4 M-cells x 5 seeds)
Pre-reg: preregs/2026-05-30_continuous_output_substrate_envelope_v2_n4096.md
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
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_cont_env", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key


# PRODUCTION CONFIG -- PROT-018: _n4096 binds N
N = 4096        # PROT-018 production-N anchor
N_FULL  = N
N_SMOKE = 1024
M_SWEEP_FULL  = [512, 2048, 8192, 16384]
M_SWEEP_SMOKE = [64, 256]
BETA    = 8.0
SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
N_INTERP  = 64
N_PROBE   = 200

# Per-cell HP thresholds (same as v1)
HP_INTERP_COS  = 0.7
HP_HALLU_AUC   = 0.85
HP_ARGMAX_CONS = 0.95
HP_KF2_MAX_ISO = 0.10
HF_INTERP_COS  = 0.3
HF_ARGMAX_CONS = 0.5

# Cross-cell pass requirements
HP_SEEDS_MIN_PER_CELL  = 3   # >= 3/5 seeds per M cell
HP_M_CELLS_MIN         = 3   # >= 3/4 M cells passing
HF_M_CELLS_HARDFAIL    = 3   # >= 3 cells HF -> HARD_FAIL


def get_output_dir(default_name: str = "continuous_output_substrate_envelope_v2_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _auc_rank(pos_scores: torch.Tensor, neg_scores: torch.Tensor) -> float:
    if pos_scores.numel() == 0 or neg_scores.numel() == 0:
        return 0.5
    all_s = torch.cat([pos_scores, neg_scores])
    ranks = torch.argsort(torch.argsort(all_s)).float() + 1.0
    pos_rank_sum = ranks[:pos_scores.numel()].sum().item()
    n_pos = pos_scores.numel(); n_neg = neg_scores.numel()
    auc = (pos_rank_sum - n_pos * (n_pos + 1) / 2.0) / (n_pos * n_neg)
    return float(auc)


def measure_continuous_cell(N_use: int, M: int, seed: int,
                             device: torch.device) -> Dict:
    """Build substrate + run 4 metric panels at one (M, seed) cell."""
    codebook, W, keys, values, key_idx, val_idx = make_substrate(N_use, M, seed, device)
    C = codebook.shape[0]

    # Panel 1: argmax consistency
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
        k_a = keys[idx_a]; k_b = keys[idx_b]
        v_a = values[idx_a]; v_b = values[idx_b]
        k_alpha = 0.5 * (k_a + k_b)
        out = k_alpha @ W.T
        target = 0.5 * (v_a + v_b)
        eps = 1e-9
        cos = (out * target).sum(dim=1) / (
            out.norm(dim=1) * target.norm(dim=1) + eps)
        interp_cos_mean = float(cos.mean().item())

    # Panel 3: hallu signal AUC
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
        sig_in  = P_in.max(dim=0).values - P_in.mean(dim=0)
        sig_oos = P_oos.max(dim=0).values - P_oos.mean(dim=0)
        hallu_auc = _auc_rank(sig_in.detach().cpu(), sig_oos.detach().cpu())

    # Panel 4: KF-2 isolation
    iso = metric_max_iso(W, codebook, key_idx, val_idx, N_use, BETA, seed,
                         device, n_probe=N_PROBE, n_edits=16)
    kf2_max_iso = iso["max_iso"]

    del W, keys, values, codebook
    if device.type == 'cuda':
        torch.cuda.empty_cache()

    return {
        "M": int(M), "seed": int(seed),
        "interp_cosine":      round(interp_cos_mean, 5),
        "hallu_signal_AUC":   round(hallu_auc, 5),
        "argmax_consistency": round(argmax_cons, 5),
        "kf2_max_iso":        round(kf2_max_iso, 5),
        "beta": BETA,
    }


def cell_passes_hp(c: Dict) -> bool:
    return (c["interp_cosine"]      >= HP_INTERP_COS
            and c["hallu_signal_AUC"]   >= HP_HALLU_AUC
            and c["argmax_consistency"] >= HP_ARGMAX_CONS
            and c["kf2_max_iso"]        <= HP_KF2_MAX_ISO)


def cell_is_hf(c: Dict) -> bool:
    return (c["interp_cosine"] <= HF_INTERP_COS
            or c["argmax_consistency"] <= HF_ARGMAX_CONS)


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("CONT_ENV_INCONCLUSIVE", "No cells.")

    # Group by M
    by_M: Dict[int, List[Dict]] = {}
    for c in cells:
        by_M.setdefault(c["M"], []).append(c)

    M_cell_pass: Dict[int, int] = {}
    M_cell_hf:   Dict[int, int] = {}
    for M, lst in by_M.items():
        n_hp = sum(1 for c in lst if cell_passes_hp(c))
        n_hf = sum(1 for c in lst if cell_is_hf(c))
        # Cell (M) "passes" only if >= HP_SEEDS_MIN_PER_CELL seeds at M hit HP
        M_cell_pass[M] = 1 if n_hp >= HP_SEEDS_MIN_PER_CELL else 0
        # Cell "is HF" if majority of seeds at M are HF
        M_cell_hf[M]   = 1 if n_hf >= (len(lst) // 2 + 1) else 0

    n_cells_pass = sum(M_cell_pass.values())
    n_cells_hf   = sum(M_cell_hf.values())
    detail = (f"M_cell_pass={M_cell_pass} M_cell_hf={M_cell_hf} "
              f"n_M_pass={n_cells_pass}/{len(by_M)} "
              f"n_M_hf={n_cells_hf}/{len(by_M)}")

    if n_cells_hf >= HF_M_CELLS_HARDFAIL:
        return ("CONT_ENV_HARD_FAIL", f"ENVELOPE_BROKEN: " + detail)
    if n_cells_pass >= HP_M_CELLS_MIN:
        return ("CONT_ENV_HARD_PASS", f"ENVELOPE_LIFTED: " + detail)
    return ("CONT_ENV_MIDDLE_BAND", f"PARTIAL: " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"
    assert len(M_SWEEP_FULL) == 4, f"M sweep should have 4 cells: {M_SWEEP_FULL}"

    # Verdict gates
    fake_hp = []
    for M in M_SWEEP_FULL:
        for s in SEEDS_FULL:
            fake_hp.append({
                "M": M, "seed": s,
                "interp_cosine": 0.8, "hallu_signal_AUC": 0.9,
                "argmax_consistency": 0.97, "kf2_max_iso": 0.05,
            })
    v, _ = compute_verdict(fake_hp); assert "HARD_PASS" in v, v

    fake_hf = []
    for M in M_SWEEP_FULL:
        for s in SEEDS_FULL:
            fake_hf.append({
                "M": M, "seed": s,
                "interp_cosine": 0.1, "hallu_signal_AUC": 0.4,
                "argmax_consistency": 0.3, "kf2_max_iso": 0.5,
            })
    v, _ = compute_verdict(fake_hf); assert "HARD_FAIL" in v, v

    fake_mb = []
    for M in M_SWEEP_FULL:
        for s in SEEDS_FULL:
            fake_mb.append({
                "M": M, "seed": s,
                "interp_cosine": 0.5, "hallu_signal_AUC": 0.6,
                "argmax_consistency": 0.9, "kf2_max_iso": 0.08,
            })
    v, _ = compute_verdict(fake_mb); assert "MIDDLE_BAND" in v, v

    # Smoke: 1 cell on CPU
    device = torch.device("cpu")
    out = measure_continuous_cell(N_SMOKE, 64, 17, device)
    for k in ("interp_cosine", "hallu_signal_AUC", "argmax_consistency",
              "kf2_max_iso"):
        v_ = out.get(k)
        assert v_ is not None and not (isinstance(v_, float) and math.isnan(v_)), (
            f"smoke metric {k} null/NaN: {out}")
    print(f"[selftest] continuous_output_substrate_envelope_v2_n4096 PASS "
          f"smoke M=64 interp={out['interp_cosine']:.3f} "
          f"hallu={out['hallu_signal_AUC']:.3f} "
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
    Ms    = M_SWEEP_SMOKE if smoke else M_SWEEP_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    out_dir = get_output_dir()
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    print(f"[run] continuous_output_substrate_envelope_v2_n4096 smoke={smoke} "
          f"N={N_cfg} Ms={Ms} seeds={seeds} done={len(done)} device={device_str}",
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
                out = measure_continuous_cell(N_cfg, M, seed, device)
                write_partial_key(out_dir, ck, out)
                cells.append(out)
                print(f"  {ck} interp={out['interp_cosine']:.3f} "
                      f"hallu={out['hallu_signal_AUC']:.3f} "
                      f"argmax={out['argmax_consistency']:.3f} "
                      f"iso={out['kf2_max_iso']:.3f} "
                      f"({time.time()-t0:.1f}s)", flush=True)
            except (RuntimeError, MemoryError) as e:
                print(f"  {ck} FAILED: {type(e).__name__}: {e}", flush=True)
                if device.type == 'cuda':
                    torch.cuda.empty_cache()

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {"anchor": "continuous_output_substrate_envelope_v2_n4096", "N": N_cfg,
               "smoke": smoke, "Ms": Ms, "seeds": seeds, "cells": cells,
               "verdict": verdict, "verdict_msg": vm, "elapsed_s": elapsed}
    payload = {"verdict": verdict, "verdict_msg": vm,
               "elapsed_s": elapsed, "summary": summary}
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(payload, f, indent=2, default=str)
    print(f"\n[verdict] {verdict}\n[verdict_msg] {vm}\n[elapsed] {elapsed}s",
          flush=True)


if __name__ == "__main__":
    main()
