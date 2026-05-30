"""LINEAR COMBINATION OF SUBSTRATES v1 at N=4096.

CONTEXT (F7 -- msg-1 T5 Op A):
  Op A from user msg-1 (multi-substrate operations): can substrates be
  combined linearly via W_combined = sum_i alpha_i * W_i, and do
  retrievals on W_combined recover the constituent facts? This is the
  simplest multi-substrate operation and a prerequisite for more
  elaborate composition.

SCIENTIFIC QUESTION:
  K=3 substrates W_1, W_2, W_3, each storing 256 DISJOINT facts from
  non-overlapping key partitions. Form:
    W_uniform   = (1/3)(W_1 + W_2 + W_3)
    W_weighted  = 0.6 W_1 + 0.3 W_2 + 0.1 W_3
  For each substrate i, retrieve at the keys that were stored in W_i.
  Do retrievals on W_uniform/W_weighted return the corresponding values
  with high accuracy? What is the cross-substrate interference (rate of
  retrieving a fact from a non-targeted substrate)?

PRE-REGISTERED BANDS:
  HARD_PASS: per-substrate retrieval accuracy >= 0.85 averaged across
    K=3 substrates AND cross-substrate interference <= 0.15 in
    3+/5 seeds for BOTH uniform AND weighted modes.
  HARD_FAIL: per-substrate accuracy <= 0.40 (combinations destroy info)
    OR cross-substrate interference >= 0.50.
  MIDDLE_BAND: otherwise.

FORMULA SELF-TESTS:
  1. N == 4096 (PROT-018).
  2. K=3 substrates, M=256 facts each, all disjoint = 768 total facts.
  3. uniform weights sum to 1; weighted weights sum to 1.
  4. Per-substrate retrieval accuracy in [0,1].

OOM CHECK:
  3 substrates at N=4096: 3 * 64MB = 192MB W. Keys 3 * 256 * 4096 * 4 =
  12MB. CB = 805MB. Total ~1GB. OK.

TIMEOUT ESTIMATE:
  Per seed: build 3 substrates + 2 W_combined + 3 retrievals each.
  ~10s/seed. 5 seeds * 2 modes = 50s smoke, 100s FULL with margin.
  Budget 14400s.

N-suffix: _n4096 (PROT-018).
Anchor: linear_combination_substrates_v1_n4096
Queue: overnight_queue
Pre-reg: preregs/2026-05-30_linear_combination_substrates_v1_n4096.md
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

_c1_path = REPO / "experiments" / "exp_axis1_mb_chunk1_v1.py"
_c1_spec = importlib.util.spec_from_file_location("axis1c1_linc", _c1_path)
c1 = importlib.util.module_from_spec(_c1_spec)
_c1_spec.loader.exec_module(c1)
store_facts_batched = c1.store_facts_batched
v3 = c1.v3

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_linc", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key


# PRODUCTION CONFIG -- PROT-018: _n4096 binds N
N = 4096        # PROT-018 production-N anchor
N_FULL  = N
N_SMOKE = 1024
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

K_SUBSTRATES = 3
M_PER_SUBSTRATE_FULL  = 256
M_PER_SUBSTRATE_SMOKE = 32

WEIGHTS_UNIFORM_FULL  = [1.0 / 3.0] * 3
WEIGHTS_WEIGHTED_FULL = [0.6, 0.3, 0.1]
MODES_FULL = [("uniform", WEIGHTS_UNIFORM_FULL),
              ("weighted", WEIGHTS_WEIGHTED_FULL)]
MODES_SMOKE = [("uniform", WEIGHTS_UNIFORM_FULL)]

SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
N_PROBE = 64    # per-substrate query count

HP_PER_SUB_ACC = 0.85
HP_INTERFERENCE_MAX = 0.15
HP_SEEDS_MIN = 3
HF_PER_SUB_ACC = 0.40
HF_INTERFERENCE_MIN = 0.50


def get_output_dir(default_name: str = "linear_combination_substrates_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def build_k_substrates(N_use: int, M_per: int, K: int, seed: int,
                        device: torch.device):
    """Build K substrates with DISJOINT key/value partitions.

    Returns:
        substrates: list of dicts each with W, keys, values, val_idx,
            stored_val_set (set of codebook indices used as values).
        codebook: shared codebook tensor.
    """
    codebook, _ = v3.make_kerdock_4coset_codebook(N_use, device)
    C = codebook.shape[0]
    # Partition the codebook into K disjoint groups of size M_per for KEYS
    # and another disjoint set for VALUES.
    gen = torch.Generator(device=device).manual_seed(seed + 2500)
    perm = torch.randperm(C, generator=gen, device=device)
    # Use first K*M_per indices as KEYS partition, next K*M_per as VALUES
    needed = 2 * K * M_per
    if needed > C:
        raise ValueError(f"codebook too small: C={C} needed={needed}")
    key_partition = perm[:K * M_per]
    val_partition = perm[K * M_per:2 * K * M_per]

    substrates = []
    for i in range(K):
        key_slice = key_partition[i * M_per:(i + 1) * M_per]    # (M_per,)
        val_slice = val_partition[i * M_per:(i + 1) * M_per]
        keys_i   = codebook[key_slice]                          # (M_per, N)
        values_i = codebook[val_slice]
        # Form outer-product W_i = sum_j values_j keys_j^T / N
        W_i = (values_i.T @ keys_i) / N_use
        substrates.append({
            "W": W_i,
            "keys":   keys_i,
            "values": values_i,
            "key_idx": key_slice,
            "val_idx": val_slice,
        })
    return substrates, codebook


def measure_one_seed(N_use: int, M_per: int, K: int, weights: List[float],
                      seed: int, device: torch.device) -> Dict:
    substrates, codebook = build_k_substrates(N_use, M_per, K, seed, device)
    C = codebook.shape[0]

    # Combine
    W_combined = torch.zeros_like(substrates[0]["W"])
    for w, sub in zip(weights, substrates):
        W_combined = W_combined + w * sub["W"]

    # For each substrate, query at its own keys and check if argmax
    # returns the correct val (correct substrate's val).
    per_sub_acc: List[float] = []
    interference_rates: List[float] = []
    for i, sub in enumerate(substrates):
        n = min(N_PROBE, sub["keys"].shape[0])
        probe_keys = sub["keys"][:n]
        expected_val_idx = sub["val_idx"][:n]
        # Build a set of OTHER substrates' val_idx for interference check
        other_val_idx = torch.cat([s["val_idx"] for j, s in enumerate(substrates)
                                    if j != i])
        other_set = set(other_val_idx.tolist())

        sims = (codebook @ (probe_keys @ W_combined.T).T) / N_use   # (C, n)
        pred = torch.argmax(sims, dim=0)                            # (n,)

        # Correct if pred == expected
        correct = (pred == expected_val_idx.to(device)).float().mean().item()
        per_sub_acc.append(float(correct))

        # Interference: how often pred is in another substrate's val set
        pred_list = pred.cpu().tolist()
        n_interf = sum(1 for p in pred_list if int(p) in other_set)
        interference_rates.append(float(n_interf) / float(n))

    mean_per_sub_acc = sum(per_sub_acc) / len(per_sub_acc)
    mean_interference = sum(interference_rates) / len(interference_rates)

    # Clean up
    for sub in substrates:
        del sub["W"], sub["keys"], sub["values"]
    del W_combined, codebook
    if device.type == 'cuda':
        torch.cuda.empty_cache()

    return {
        "seed": seed,
        "K": K,
        "M_per": M_per,
        "weights": list(weights),
        "per_substrate_accuracy": [round(a, 5) for a in per_sub_acc],
        "mean_per_substrate_accuracy": round(mean_per_sub_acc, 5),
        "interference_rates":         [round(a, 5) for a in interference_rates],
        "mean_interference":          round(mean_interference, 5),
    }


def cell_passes_hp(c: Dict) -> bool:
    return (c["mean_per_substrate_accuracy"] >= HP_PER_SUB_ACC
            and c["mean_interference"] <= HP_INTERFERENCE_MAX)


def cell_is_hf(c: Dict) -> bool:
    return (c["mean_per_substrate_accuracy"] <= HF_PER_SUB_ACC
            or c["mean_interference"] >= HF_INTERFERENCE_MIN)


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("LC_INCONCLUSIVE", "No cells.")

    # Group by mode (uniform / weighted)
    by_mode: Dict[str, List[Dict]] = {}
    for c in cells:
        by_mode.setdefault(c.get("mode", "?"), []).append(c)

    mode_pass: Dict[str, int] = {}
    mode_hf:   Dict[str, int] = {}
    for mode, lst in by_mode.items():
        mode_pass[mode] = sum(1 for c in lst if cell_passes_hp(c))
        mode_hf[mode]   = sum(1 for c in lst if cell_is_hf(c))

    detail = f"mode_pass={mode_pass} mode_hf={mode_hf} n_cells={len(cells)}"

    # HARD_FAIL: HF dominant in any mode
    for mode, n_hf in mode_hf.items():
        if n_hf >= HP_SEEDS_MIN:
            return ("LC_HARD_FAIL",
                    f"COMBINATIONS_BROKEN_in_{mode}: " + detail)

    # HARD_PASS: BOTH modes (uniform + weighted) reach HP_SEEDS_MIN
    if len(by_mode) >= 2:
        all_pass = all(mode_pass.get(m, 0) >= HP_SEEDS_MIN
                       for m in ["uniform", "weighted"])
        if all_pass:
            return ("LC_HARD_PASS", f"COMBINATIONS_WORK_BOTH_MODES: " + detail)
    else:
        # Smoke fast-path
        if mode_pass.get("uniform", 0) >= 1:
            return ("LC_HARD_PASS", f"SMOKE_COMBINATIONS_WORK: " + detail)

    return ("LC_MIDDLE_BAND", f"PARTIAL: " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096
    # Weight sums
    assert abs(sum(WEIGHTS_UNIFORM_FULL) - 1.0) < 1e-6
    assert abs(sum(WEIGHTS_WEIGHTED_FULL) - 1.0) < 1e-6

    # Verdict gates
    fake_hp = []
    for mode, w in MODES_FULL:
        for s in SEEDS_FULL:
            fake_hp.append({"seed": s, "mode": mode, "weights": w,
                            "mean_per_substrate_accuracy": 0.92,
                            "mean_interference": 0.05,
                            "per_substrate_accuracy": [0.9, 0.92, 0.94],
                            "interference_rates": [0.05, 0.04, 0.06]})
    v, _ = compute_verdict(fake_hp); assert "HARD_PASS" in v, v

    fake_hf = []
    for mode, w in MODES_FULL:
        for s in SEEDS_FULL:
            fake_hf.append({"seed": s, "mode": mode, "weights": w,
                            "mean_per_substrate_accuracy": 0.2,
                            "mean_interference": 0.6,
                            "per_substrate_accuracy": [0.2, 0.2, 0.2],
                            "interference_rates": [0.6, 0.6, 0.6]})
    v, _ = compute_verdict(fake_hf); assert "HARD_FAIL" in v, v

    # Smoke on CPU
    device = torch.device("cpu")
    out = measure_one_seed(N_SMOKE, M_PER_SUBSTRATE_SMOKE, K_SUBSTRATES,
                            WEIGHTS_UNIFORM_FULL, 17, device)
    assert out["mean_per_substrate_accuracy"] >= 0
    assert out["mean_interference"] >= 0
    print(f"[selftest] linear_combination_substrates_v1_n4096 PASS "
          f"smoke acc={out['mean_per_substrate_accuracy']:.3f} "
          f"interf={out['mean_interference']:.3f}", flush=True)


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
    M_per = M_PER_SUBSTRATE_SMOKE if smoke else M_PER_SUBSTRATE_FULL
    modes = MODES_SMOKE if smoke else MODES_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    out_dir = get_output_dir()
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    print(f"[run] linear_combination_substrates_v1_n4096 smoke={smoke} "
          f"N={N_cfg} M_per={M_per} K={K_SUBSTRATES} modes={[m for m,_ in modes]} "
          f"seeds={seeds} done={len(done)} device={device_str}", flush=True)

    cells: List[Dict] = []
    for mode_name, weights in modes:
        for seed in seeds:
            ck = f"{mode_name}_seed{seed}"
            if ck in done:
                body = load_partial_key(out_dir, ck)
                if body is not None:
                    cells.append(body); continue
            try:
                out = measure_one_seed(N_cfg, M_per, K_SUBSTRATES,
                                        weights, seed, device)
                out["mode"] = mode_name
                write_partial_key(out_dir, ck, out)
                cells.append(out)
                print(f"  {ck} acc={out['mean_per_substrate_accuracy']:.3f} "
                      f"interf={out['mean_interference']:.3f} "
                      f"({time.time()-t0:.1f}s)", flush=True)
            except (RuntimeError, MemoryError) as e:
                print(f"  {ck} FAILED: {type(e).__name__}: {e}", flush=True)
                if device.type == 'cuda':
                    torch.cuda.empty_cache()

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {"anchor": "linear_combination_substrates_v1_n4096", "N": N_cfg,
               "smoke": smoke, "M_per": M_per, "K": K_SUBSTRATES,
               "modes": [m for m,_ in modes], "seeds": seeds,
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
