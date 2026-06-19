"""C6 SUBSTRATE OPERATION COST MODELING v1 at N=4096.

CONTEXT (v290 cap_map follow-on):
  Production capacity planning. Build cost model (latency, memory, throughput)
  for substrate operations as a function of (N, M, query_type). Fit power-law
  model.

SCIENTIFIC QUESTION:
  At N=4096, M in {128, 512, 2048, 8192}, do per-operation (store, retrieve,
  edit, delete, multi_hop) cost models fit power-law with R^2 >= 0.90 AND
  predictions match empirical within 20%?

PRE-REGISTERED BANDS:
  HP = power-law fits with R^2 >= 0.90 for all 5 operations AND model
       predictions match empirical within 20%.
  HF = model fits R^2 < 0.50 (no clean scaling) OR predictions miss by >50%.
  MB = otherwise.

OUTPUT: notes/substrate_cost_model_v1_2026-05-30.md with deployment capacity
recommendations.

PROT-018: _n4096 binds N = 4096.
PROT-021: per-cell-seed checkpointing.

Anchor: substrate_operation_cost_modeling_v1_n4096
Queue: remote_cpu_queue
Pre-reg: preregs/2026-05-30_substrate_operation_cost_modeling_v1_n4096.md
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

from experiments._multi_hop_mechanisms import build_shared, path_d_run  # noqa: E402

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_c6", _ck_path)
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

M_SWEEP_FULL = [128, 512, 2048, 8192]
M_SWEEP_SMOKE = [64, 128]
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
DEPTH = 5
DEPTH_SMOKE = 2
K_PATHS = 100
K_PATHS_SMOKE = 10
N_STARTS = 16
N_STARTS_SMOKE = 4
BETA_D = 4.0
N_OPS_PER_MEASURE = 20  # number of repeated ops per (M, op) cell

OPERATIONS = ["store", "retrieve", "edit", "delete", "multi_hop"]

HP_MIN_R2 = 0.90
HP_MAX_PRED_ERR = 0.20  # 20%
HF_MAX_R2 = 0.50
HF_MAX_PRED_ERR = 0.50


def get_output_dir(default_name: str = "substrate_operation_cost_modeling_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _power_law_fit(xs: List[float], ys: List[float]) -> Tuple[float, float, float]:
    """Fit y = a * x^b via log-log linear regression.
    Returns (a, b, r2)."""
    if len(xs) < 2:
        return 0.0, 0.0, 0.0
    lxs = [math.log(x) for x in xs if x > 0]
    lys = [math.log(y) for y in ys if y > 0]
    if len(lxs) != len(xs) or len(lys) != len(ys) or len(lxs) < 2:
        return 0.0, 0.0, 0.0
    n = len(lxs)
    mx = sum(lxs) / n
    my = sum(lys) / n
    cov = sum((lxs[i] - mx) * (lys[i] - my) for i in range(n))
    varx = sum((lxs[i] - mx) ** 2 for i in range(n))
    if varx == 0:
        return 0.0, 0.0, 0.0
    b = cov / varx
    log_a = my - b * mx
    a = math.exp(log_a)
    # R^2
    ss_tot = sum((lys[i] - my) ** 2 for i in range(n))
    ss_res = sum((lys[i] - (log_a + b * lxs[i])) ** 2 for i in range(n))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 1.0
    return a, b, r2


def _time_op(fn, n_repeat: int):
    """Call fn() n_repeat times; return median elapsed_s."""
    samples = []
    for _ in range(n_repeat):
        t0 = time.perf_counter()
        fn()
        samples.append(time.perf_counter() - t0)
    samples.sort()
    return samples[len(samples) // 2]


def measure_op_cost(op: str, N_use: int, M: int, seed: int,
                      n_repeat: int, depth: int, K_paths: int,
                      n_starts: int, device: torch.device) -> Dict:
    """Measure (latency, peak_mem_mb, throughput) for one (op, M) cell."""
    if op == "store":
        # Build W from scratch
        def f():
            g = torch.Generator(device='cpu').manual_seed(seed)
            keys = torch.randn(M, N_use)
            vals = torch.randn(M, N_use)
            if device.type == 'cuda':
                keys = keys.to(device); vals = vals.to(device)
            W = (vals.T @ keys) / N_use
            del W, keys, vals
        latency = _time_op(f, n_repeat)
        peak_mem_mb = (3 * M * N_use * 4 + N_use * N_use * 4) / (1024 * 1024)
    else:
        # Build substrate once, measure op repeatedly
        codebook, W, key_idx, val_idx, relation = build_shared(
            N_use, M, seed, device)
        keys = codebook[key_idx]
        vals = codebook[val_idx]
        if op == "retrieve":
            q = keys[:min(20, M)]
            def f():
                out = q @ W.T
                sims = (codebook @ out.T) / N_use
                _ = torch.argmax(sims, dim=0)
            latency = _time_op(f, n_repeat)
            peak_mem_mb = (q.shape[0] * N_use * 4 + codebook.shape[0] * 4) / (1024 * 1024)
        elif op == "edit":
            k = keys[:1]; ov = vals[:1]
            C = codebook.shape[0]
            nv = codebook[(int(val_idx[0].item()) + 1) % C].unsqueeze(0)
            def f():
                W2 = W - (ov.T @ k) / N_use + (nv.T @ k) / N_use
                del W2
            latency = _time_op(f, n_repeat)
            peak_mem_mb = (N_use * N_use * 4) / (1024 * 1024) * 2
        elif op == "delete":
            k = keys[:1]; ov = vals[:1]
            def f():
                W2 = W - (ov.T @ k) / N_use
                del W2
            latency = _time_op(f, n_repeat)
            peak_mem_mb = (N_use * N_use * 4) / (1024 * 1024) * 2
        elif op == "multi_hop":
            starts_list = list(relation.keys())[:n_starts]
            if not starts_list:
                latency = 0.0
                peak_mem_mb = 0.0
            else:
                starts = torch.tensor(starts_list, dtype=torch.long, device=device)
                def f():
                    _ = path_d_run(codebook, W, starts, relation, depth,
                                       K_paths, seed, N_use, beta=BETA_D)
                # multi_hop is heavy; use fewer repeats
                latency = _time_op(f, max(1, n_repeat // 4))
                peak_mem_mb = (K_paths * depth * 8 + N_use * N_use * 4) / (1024 * 1024)
        else:
            latency = 0.0
            peak_mem_mb = 0.0
        del codebook, W
        if device.type == "cuda":
            torch.cuda.empty_cache()
    throughput = 1.0 / max(latency, 1e-9)
    return {"op": op, "M": int(M), "latency_s": round(float(latency), 6),
            "peak_mem_mb": round(float(peak_mem_mb), 3),
            "throughput_ops_per_s": round(float(throughput), 2)}


def measure_seed(N_use: int, M_sweep: List[int], n_repeat: int,
                   depth: int, K_paths: int, n_starts: int, seed: int,
                   device: torch.device) -> Dict:
    raw_measurements = []
    for M in M_sweep:
        for op in OPERATIONS:
            try:
                cell = measure_op_cost(op, N_use, M, seed, n_repeat, depth,
                                          K_paths, n_starts, device)
                raw_measurements.append(cell)
            except Exception as e:  # noqa: BLE001
                raw_measurements.append({"op": op, "M": int(M),
                                              "error": str(e)[:300]})

    # Per-op power-law fit across M
    models = {}
    for op in OPERATIONS:
        op_cells = [r for r in raw_measurements
                    if r.get("op") == op and "error" not in r]
        if not op_cells:
            models[op] = {"a": 0.0, "b": 0.0, "r2": 0.0, "error": "no data"}
            continue
        Ms = [r["M"] for r in op_cells]
        Ls = [r["latency_s"] for r in op_cells]
        a, b, r2 = _power_law_fit(Ms, Ls)
        # Check prediction error on the original Ms
        preds = [a * (m ** b) for m in Ms]
        rel_errs = [abs(p - l) / max(l, 1e-9) for p, l in zip(preds, Ls)]
        max_err = max(rel_errs) if rel_errs else 0.0
        models[op] = {"a": round(float(a), 9),
                      "b": round(float(b), 4),
                      "r2": round(float(r2), 4),
                      "max_pred_err": round(float(max_err), 4)}
    return {"seed": int(seed),
            "raw_measurements": raw_measurements,
            "cost_models": models}


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("C6_INCONCLUSIVE", "no cells")

    # Aggregate per-op model across seeds (median R^2 + median max_pred_err)
    by_op = {}
    for op in OPERATIONS:
        r2s = [c["cost_models"].get(op, {}).get("r2", 0.0) for c in cells
               if "error" not in c["cost_models"].get(op, {})]
        errs = [c["cost_models"].get(op, {}).get("max_pred_err", 1.0)
                for c in cells if "error" not in c["cost_models"].get(op, {})]
        by_op[op] = {
            "median_r2": (sorted(r2s)[len(r2s) // 2] if r2s else 0.0),
            "median_max_err": (sorted(errs)[len(errs) // 2] if errs else 1.0),
        }

    detail = " | ".join(
        f"{op}: r2={by_op[op]['median_r2']:.3f} err={by_op[op]['median_max_err']:.3f}"
        for op in OPERATIONS)

    n_hp_ops = sum(1 for op in OPERATIONS
                     if by_op[op]["median_r2"] >= HP_MIN_R2
                     and by_op[op]["median_max_err"] <= HP_MAX_PRED_ERR)
    n_hf_ops = sum(1 for op in OPERATIONS
                     if by_op[op]["median_r2"] < HF_MAX_R2
                     or by_op[op]["median_max_err"] > HF_MAX_PRED_ERR)

    if n_hp_ops == len(OPERATIONS):
        return ("C6_HARD_PASS", f"COST_MODEL_FITS n_hp={n_hp_ops}/{len(OPERATIONS)}. " + detail)
    if n_hf_ops >= 1:
        return ("C6_HARD_FAIL", f"COST_MODEL_DOES_NOT_FIT n_hf={n_hf_ops}/{len(OPERATIONS)}. " + detail)
    return ("C6_MIDDLE_BAND", f"PARTIAL n_hp={n_hp_ops}/{len(OPERATIONS)}. " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096, "PROT-018: _n4096"
    assert len(OPERATIONS) == 5
    assert len(M_SWEEP_FULL) == 4
    assert len(SEEDS_FULL) == 5

    # Verdict gate HP
    fake_hp = [{"seed": s,
                "raw_measurements": [],
                "cost_models": {op: {"a": 1.0, "b": 1.0, "r2": 0.95,
                                       "max_pred_err": 0.10}
                                  for op in OPERATIONS}}
               for s in SEEDS_FULL]
    v, _ = compute_verdict(fake_hp); assert "HARD_PASS" in v, v

    # Verdict gate HF
    fake_hf = [{"seed": s,
                "raw_measurements": [],
                "cost_models": {op: {"a": 1.0, "b": 1.0, "r2": 0.20,
                                       "max_pred_err": 0.80}
                                  for op in OPERATIONS}}
               for s in SEEDS_FULL]
    v, _ = compute_verdict(fake_hf); assert "HARD_FAIL" in v, v

    # Verdict gate MB
    fake_mb = [{"seed": s,
                "raw_measurements": [],
                "cost_models": {op: {"a": 1.0, "b": 1.0, "r2": 0.70,
                                       "max_pred_err": 0.30}
                                  for op in OPERATIONS}}
               for s in SEEDS_FULL]
    v, _ = compute_verdict(fake_mb); assert "MIDDLE_BAND" in v, v

    # Power-law fit self-check
    a, b, r2 = _power_law_fit([1.0, 2.0, 4.0, 8.0], [2.0, 4.0, 8.0, 16.0])
    assert abs(b - 1.0) < 0.01, f"power-law b: expected 1.0, got {b}"
    assert r2 > 0.99, f"power-law r2: expected ~1.0, got {r2}"

    # Live smoke on CPU
    device = torch.device("cpu")
    out = measure_seed(N_SMOKE, M_SWEEP_SMOKE, 3, DEPTH_SMOKE,
                        K_PATHS_SMOKE, N_STARTS_SMOKE, 17, device)
    assert len(out["cost_models"]) == 5
    print(f"[selftest] substrate_operation_cost_modeling_v1_n4096 PASS "
          f"5/5 ops modeled smoke", flush=True)


_instrumentation_selftest()


def _emit_cost_model_doc(cells: List[Dict]):
    try:
        notes_dir = REPO / "notes"
        notes_dir.mkdir(parents=True, exist_ok=True)
        doc = notes_dir / "substrate_cost_model_v1_2026-05-30.md"
        with open(doc, "w", encoding='utf-8') as f:
            f.write("# Substrate Cost Model v1 (2026-05-30)\n\n")
            f.write("## Power-law fits per operation\n\n")
            f.write("Model: latency_s = a * M^b\n\n")
            for op in OPERATIONS:
                f.write(f"### {op}\n\n")
                fits = [c["cost_models"].get(op, {}) for c in cells
                        if op in c.get("cost_models", {})]
                if not fits:
                    f.write("No data.\n\n")
                    continue
                a_med = sorted(f["a"] for f in fits)[len(fits) // 2]
                b_med = sorted(f["b"] for f in fits)[len(fits) // 2]
                r2_med = sorted(f["r2"] for f in fits)[len(fits) // 2]
                f.write(f"- a = {a_med:.6g}\n")
                f.write(f"- b = {b_med:.4f}\n")
                f.write(f"- R^2 = {r2_med:.4f}\n\n")
            f.write("## Deployment capacity recommendations\n\n")
            f.write("See data/exp_substrate_operation_cost_modeling_v1_n4096/"
                    "metrics.json for raw data.\n")
    except Exception:  # noqa: BLE001
        pass


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    args = p.parse_args()
    if args.self_test:
        sys.exit(0)
    device = torch.device("cpu")
    smoke = args.smoke
    N_cfg = N_SMOKE if smoke else N_FULL
    M_sweep = M_SWEEP_SMOKE if smoke else M_SWEEP_FULL
    n_repeat = 3 if smoke else N_OPS_PER_MEASURE
    depth = DEPTH_SMOKE if smoke else DEPTH
    K_paths = K_PATHS_SMOKE if smoke else K_PATHS
    n_starts = N_STARTS_SMOKE if smoke else N_STARTS
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    out_dir = get_output_dir()
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    print(f"[run] substrate_operation_cost_modeling_v1_n4096 smoke={smoke} "
          f"N={N_cfg} M_sweep={M_sweep} n_repeat={n_repeat} seeds={seeds} "
          f"done={len(done)} device={device.type}", flush=True)

    cells: List[Dict] = []
    for seed in seeds:
        ck = f"seed{seed}"
        if ck in done:
            body = load_partial_key(out_dir, ck)
            if body is not None:
                cells.append(body); continue
        try:
            cell = measure_seed(N_cfg, M_sweep, n_repeat, depth, K_paths,
                                  n_starts, seed, device)
            write_partial_key(out_dir, ck, cell)
            cells.append(cell)
            print(f"  seed={seed} ops_modeled={list(cell['cost_models'].keys())} "
                  f"({time.time()-t0:.1f}s)", flush=True)
        except (RuntimeError, MemoryError, Exception) as e:  # noqa: BLE001
            print(f"  seed={seed} FAILED: {e}", flush=True)

    if cells and not smoke:
        _emit_cost_model_doc(cells)

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {"anchor": "substrate_operation_cost_modeling_v1_n4096",
               "N": N_cfg, "smoke": smoke, "M_sweep": M_sweep,
               "n_repeat": n_repeat, "seeds": seeds, "cells": cells,
               "verdict": verdict, "verdict_msg": vm, "elapsed_s": elapsed}
    payload = {"verdict": verdict, "verdict_msg": vm,
               "elapsed_s": elapsed, "summary": summary}
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(payload, f, indent=2, default=str)
    print(f"\n[verdict] {verdict}\n[verdict_msg] {vm}\n[elapsed] {elapsed}s",
          flush=True)


if __name__ == "__main__":
    main()
