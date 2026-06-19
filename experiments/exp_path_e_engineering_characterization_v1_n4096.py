"""T4 PATH E ENGINEERING CHARACTERIZATION v1 at N=4096 (Test 23).

Path E's plateau (~0.5 partial accuracy at breaking) + sub-linear K-scaling
suggest niche applications even when Path D wins on full multi-hop. We
characterize three specific use cases:

  Sub-test A (top-K candidate identification):
    At high K (5000, 10000), use Path E for ranking; measure top-K precision
    at k_topk=10. Hypothesis: Path E is a fast candidate filter even when
    its absolute hop-accuracy is partial.

  Sub-test B (quick approximate multi-hop for early-termination):
    At low budget (max 50 ms wall), use Path E to give approximate answer;
    measure accuracy and latency at the budget cutoff.

  Sub-test C (latency-sensitive with partial-accuracy tolerance):
    Path E at production config with explicit accuracy tradeoff sweep
    (sigma noise in {0.0, 0.1, 0.2, 0.4}); measure latency reduction at
    each acceptable-accuracy threshold.

METRICS:
  Sub-test A: top-K precision @ K=10 vs Path D baseline at same K.
  Sub-test B: accuracy + latency at the 50 ms budget cutoff.
  Sub-test C: latency reduction vs sigma at fixed accuracy target.
  Composite envelope across the 3 use cases.

PRE-REGISTERED BANDS:
  HP = at least 2/3 sub-tests show Path E delivers a USEFUL application
       property:
         A: top-K precision >= 0.85
         B: early-termination accuracy >= 0.65 within 50 ms
         C: latency reduction >= 3x at sigma=0.2
  HF = Path E fails all 3 sub-tests.
  MB = otherwise.

PROT-018: _n4096 binds N = 4096.
Anchor: path_e_engineering_characterization_v1_n4096
Queue: overnight_queue
Pre-reg: preregs/2026-05-30_path_e_engineering_characterization_v1_n4096.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import importlib.util
import json
import os
import time
from pathlib import Path
from typing import Dict, List, Tuple

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._multi_hop_mechanisms import (  # noqa: E402
    build_shared, path_d_run, path_e_run,
)
from experiments._relation_graph import (  # noqa: E402
    sample_coherent_starts, sample_incoherent_paths,
)

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_t4pe", _ck_path)
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

M_PROD = 2048
M_SMOKE = 256
DEPTH = 5
DEPTH_SMOKE = 3
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
N_PATHS_FULL = 32
N_PATHS_SMOKE = 8

# Sub-test A: high-K ranking; topK precision @ k_topk
SUBA_K_LIST_FULL = [5000, 10000]
SUBA_K_LIST_SMOKE = [200]
SUBA_TOPK = 10
HP_SUBA_PRECISION = 0.85

# Sub-test B: early-termination budget in seconds
SUBB_BUDGET_S = 0.050
HP_SUBB_ACC = 0.65

# Sub-test C: noise sigma sweep
SUBC_SIGMAS_FULL = [0.0, 0.1, 0.2, 0.4]
SUBC_SIGMAS_SMOKE = [0.0, 0.2]
SUBC_HP_SIGMA = 0.2
HP_SUBC_SPEEDUP = 3.0
SUBC_ACC_TARGET = 0.50


def get_output_dir(default_name: str = "path_e_engineering_characterization_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def path_e_topk_score(codebook: torch.Tensor, W: torch.Tensor,
                      start: int, target: int, candidates: List[int],
                      depth: int, N_use: int, top_k: int = 16) -> List[int]:
    """Score each candidate via Path E spectral coherence; return ranked indices.

    For each candidate end-node, build a 'fake path' from start -> ... -> candidate
    using the substrate response; score by spectral coherence with target signature.
    """
    device = codebook.device
    # Build start vector, propagate continuous response
    q = codebook[start:start + 1].clone()
    for _ in range(depth):
        q = q @ W.T
    sims = (codebook @ q.T).squeeze(-1) / N_use   # (C,)
    # Sub-test A: rank candidates by their similarity scores.
    cand_t = torch.tensor(candidates, dtype=torch.long, device=device)
    cand_scores = sims[cand_t]
    ordered = torch.argsort(cand_scores, descending=True)
    ranked_candidates = [candidates[int(i.item())] for i in ordered]
    return ranked_candidates


def measure_subA(codebook, W, relation, starts, N_use, depth, K_high, top_k,
                 seed) -> Dict:
    """Sub-test A: top-K precision for Path E at high K."""
    device = codebook.device
    C = codebook.shape[0]
    precisions = []
    for b in range(starts.shape[0]):
        start = int(starts[b].item())
        cur = start
        ok = True
        for _ in range(depth):
            nxt = relation.get(cur)
            if nxt is None:
                ok = False
                break
            cur = int(nxt)
        if not ok:
            continue
        target = cur
        # Build candidate set: target + K_high - 1 random decoys
        g = torch.Generator(device=device).manual_seed(seed + start + K_high)
        all_idx = torch.randperm(C, generator=g, device=device)[:K_high + 1].tolist()
        if target in all_idx:
            candidates = all_idx[:K_high]
            if target not in candidates:
                candidates[0] = target
        else:
            candidates = [target] + all_idx[:K_high - 1]
        ranked = path_e_topk_score(codebook, W, start, target, candidates,
                                    depth, N_use, top_k=top_k)
        precision = 1.0 if target in ranked[:SUBA_TOPK] else 0.0
        precisions.append(precision)
    mean_p = sum(precisions) / max(1, len(precisions))
    return {"sub": "A", "K_high": K_high, "topk": SUBA_TOPK,
            "n_paths": len(precisions),
            "precision_at_topk": round(mean_p, 5)}


def measure_subB(codebook, W, relation, starts, N_use, depth, budget_s,
                 seed) -> Dict:
    """Sub-test B: accuracy within wall-time budget."""
    device = codebook.device
    n_done = 0
    n_correct = 0
    t_start = time.perf_counter()
    for b in range(starts.shape[0]):
        if time.perf_counter() - t_start > budget_s:
            break
        start = int(starts[b].item())
        cur = start
        ok = True
        for _ in range(depth):
            nxt = relation.get(cur)
            if nxt is None:
                ok = False
                break
            cur = int(nxt)
        if not ok:
            continue
        target = cur
        # Fast Path E: continuous prop + argmax
        q = codebook[start:start + 1].clone()
        for _ in range(depth):
            q = q @ W.T
        sims = (codebook @ q.T).squeeze(-1) / N_use
        pred = int(torch.argmax(sims).item())
        n_done += 1
        if pred == target:
            n_correct += 1
    elapsed = time.perf_counter() - t_start
    acc = n_correct / max(1, n_done)
    return {"sub": "B", "budget_s": budget_s, "elapsed_s": round(elapsed, 4),
            "n_done": n_done, "n_correct": n_correct,
            "accuracy_in_budget": round(acc, 5)}


def measure_subC(codebook, W, relation, starts, N_use, depth, sigmas,
                 seed) -> Dict:
    """Sub-test C: accuracy + latency at increasing noise sigma."""
    device = codebook.device
    by_sigma = {}
    for sigma in sigmas:
        n_done = 0
        n_correct = 0
        t0 = time.perf_counter_ns()
        for b in range(starts.shape[0]):
            start = int(starts[b].item())
            cur = start
            ok = True
            for _ in range(depth):
                nxt = relation.get(cur)
                if nxt is None:
                    ok = False
                    break
                cur = int(nxt)
            if not ok:
                continue
            target = cur
            q = codebook[start:start + 1].clone()
            for _ in range(depth):
                q = q @ W.T
                if sigma > 0.0:
                    g = torch.Generator(device=device).manual_seed(seed + b + start)
                    noise = torch.randn(q.shape, generator=g, device=device,
                                          dtype=q.dtype) * sigma
                    q = q + noise
            sims = (codebook @ q.T).squeeze(-1) / N_use
            pred = int(torch.argmax(sims).item())
            n_done += 1
            if pred == target:
                n_correct += 1
        lat_ns = time.perf_counter_ns() - t0
        acc = n_correct / max(1, n_done)
        by_sigma[str(sigma)] = {"acc": round(acc, 5), "lat_ns": int(lat_ns),
                                 "n_done": n_done}
    # Reference: sigma=0.0 latency
    ref_lat = by_sigma[str(sigmas[0])]["lat_ns"]
    # Latency reduction at SUBC_HP_SIGMA: speedup = ref_lat / lat
    target_key = str(SUBC_HP_SIGMA) if str(SUBC_HP_SIGMA) in by_sigma else list(by_sigma.keys())[-1]
    target_lat = by_sigma[target_key]["lat_ns"]
    speedup = ref_lat / max(1, target_lat)
    return {"sub": "C", "sigmas": [float(s) for s in sigmas],
            "by_sigma": by_sigma,
            "target_sigma": float(target_key),
            "speedup_at_target": round(speedup, 4),
            "ref_lat_ns": int(ref_lat),
            "target_lat_ns": int(target_lat)}


def measure_seed(N_use: int, M: int, depth: int, n_paths: int,
                  suba_Ks: List[int], subc_sigmas: List[float],
                  seed: int, device: torch.device) -> Dict:
    codebook, W, key_idx, val_idx, relation = build_shared(N_use, M, seed, device)
    starts = torch.tensor(list(relation.keys())[:n_paths],
                          dtype=torch.long, device=device)

    out_sub_a = []
    for K_high in suba_Ks:
        out_sub_a.append(measure_subA(codebook, W, relation, starts, N_use,
                                       depth, K_high, SUBA_TOPK, seed))

    out_sub_b = measure_subB(codebook, W, relation, starts, N_use,
                              depth, SUBB_BUDGET_S, seed)

    out_sub_c = measure_subC(codebook, W, relation, starts, N_use,
                              depth, subc_sigmas, seed)

    del codebook, W
    if device.type == "cuda":
        torch.cuda.empty_cache()

    return {"seed": int(seed), "M": int(M), "depth": int(depth),
            "n_paths": int(n_paths),
            "sub_a": out_sub_a, "sub_b": out_sub_b, "sub_c": out_sub_c}


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("T4_INCONCLUSIVE", "no cells")

    n_seeds = len(cells)
    threshold = max(1, (n_seeds * 3) // 5)

    # Sub-test A: mean precision_at_topk per K_high across seeds.
    suba_pass_seeds = sum(
        1 for c in cells
        if any(s["precision_at_topk"] >= HP_SUBA_PRECISION for s in c["sub_a"])
    )
    suba_pass = suba_pass_seeds >= threshold

    # Sub-test B
    subb_pass_seeds = sum(
        1 for c in cells
        if c["sub_b"]["accuracy_in_budget"] >= HP_SUBB_ACC
    )
    subb_pass = subb_pass_seeds >= threshold

    # Sub-test C
    subc_pass_seeds = sum(
        1 for c in cells
        if c["sub_c"]["speedup_at_target"] >= HP_SUBC_SPEEDUP
    )
    subc_pass = subc_pass_seeds >= threshold

    n_pass = int(suba_pass) + int(subb_pass) + int(subc_pass)

    detail = (f"n_seeds={n_seeds} subA_pass={suba_pass_seeds}/{n_seeds} "
              f"subB_pass={subb_pass_seeds}/{n_seeds} "
              f"subC_pass={subc_pass_seeds}/{n_seeds} "
              f"sub_total_pass={n_pass}/3")

    if n_pass >= 2:
        return ("T4_HARD_PASS", "PATH_E_USEFUL_APPLICATIONS: " + detail)
    if n_pass == 0:
        return ("T4_HARD_FAIL", "PATH_E_NO_APPLICATION: " + detail)
    return ("T4_MIDDLE_BAND", "PARTIAL: " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096
    device = torch.device("cpu")
    out = measure_seed(N_SMOKE, 64, 2, 8,
                       [SUBA_K_LIST_SMOKE[0]], SUBC_SIGMAS_SMOKE, 17, device)
    assert "sub_a" in out and "sub_b" in out and "sub_c" in out
    assert len(out["sub_a"]) >= 1
    assert out["sub_b"]["accuracy_in_budget"] is not None
    assert out["sub_c"]["speedup_at_target"] is not None
    print(f"[selftest] path_e_engineering_characterization_v1_n4096 PASS "
          f"subA_prec={out['sub_a'][0]['precision_at_topk']:.3f} "
          f"subB_acc={out['sub_b']['accuracy_in_budget']:.3f} "
          f"subC_speedup={out['sub_c']['speedup_at_target']:.3f}", flush=True)


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
    M = M_SMOKE if smoke else M_PROD
    depth = DEPTH_SMOKE if smoke else DEPTH
    n_paths = N_PATHS_SMOKE if smoke else N_PATHS_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    suba_Ks = SUBA_K_LIST_SMOKE if smoke else SUBA_K_LIST_FULL
    subc_sigmas = SUBC_SIGMAS_SMOKE if smoke else SUBC_SIGMAS_FULL

    out_dir = get_output_dir()
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    print(f"[run] path_e_engineering_characterization smoke={smoke} N={N_cfg} "
          f"M={M} depth={depth} n_paths={n_paths} suba_Ks={suba_Ks} "
          f"subc_sigmas={subc_sigmas} seeds={seeds} done={len(done)} "
          f"device={device.type}", flush=True)

    cells: List[Dict] = []
    for seed in seeds:
        ck = f"seed{seed}"
        if ck in done:
            body = load_partial_key(out_dir, ck)
            if body is not None:
                cells.append(body)
                continue
        try:
            out = measure_seed(N_cfg, M, depth, n_paths, suba_Ks, subc_sigmas,
                                seed, device)
            write_partial_key(out_dir, ck, out)
            cells.append(out)
            print(f"  s={seed} subA_prec={out['sub_a'][0]['precision_at_topk']:.3f} "
                  f"subB_acc={out['sub_b']['accuracy_in_budget']:.3f} "
                  f"subC_speedup={out['sub_c']['speedup_at_target']:.3f} "
                  f"({time.time()-t0:.1f}s)", flush=True)
        except (RuntimeError, MemoryError) as e:
            print(f"  s={seed} FAILED: {e}", flush=True)
            if device.type == "cuda":
                torch.cuda.empty_cache()

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {"anchor": "path_e_engineering_characterization_v1_n4096",
               "N": N_cfg, "smoke": smoke,
               "M": M, "depth": depth, "n_paths": n_paths,
               "suba_Ks": suba_Ks, "subc_sigmas": subc_sigmas,
               "seeds": seeds, "cells": cells,
               "verdict": verdict, "verdict_msg": vm,
               "elapsed_s": elapsed}
    payload = {"verdict": verdict, "verdict_msg": vm,
               "elapsed_s": elapsed, "summary": summary}
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(payload, f, indent=2, default=str)
    print(f"\n[verdict] {verdict}\n[verdict_msg] {vm}\n[elapsed] {elapsed}s",
          flush=True)


if __name__ == "__main__":
    main()
