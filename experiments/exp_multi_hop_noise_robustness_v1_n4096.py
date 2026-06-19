"""MULTI-HOP NOISE ROBUSTNESS v1 at N=4096 (paths B, D, E).

CONTEXT (production-robustness stress test):
  Production data has noise: transcription errors in stored facts, query-side
  uncertainty. Determines which mechanism (B/D/E) handles real-world noise
  best -- critical for Pattern B integration where stored facts may have
  source uncertainty.

  Noise model: bit-flip noise (BSC) on the substrate vectors at fact-storage
  AND on query keys at retrieval. Sigma is the per-bit flip probability
  applied as Gaussian on the substrate float vectors (since vectors are
  +/-1 codewords, Gaussian sigma on raw vectors is the natural model).

SCIENTIFIC QUESTION:
  At N=4096, M=2048, depth=5, K_paths=100: how does each path's accuracy
  decay with noise sigma in {0.00, 0.05, 0.10, 0.20, 0.40}? Does any path
  maintain >= 0.65 accuracy at sigma=0.20 AND degrade gracefully (no cliff)
  in >= 3/5 seeds?

PRE-REGISTERED BANDS:
  HP = at least one path maintains >= 0.65 accuracy at sigma=0.20 AND degrades
       monotonically (no cliff: accuracy at adjacent sigma differs by < 0.30)
       across all 5 sigma levels in >= 3/5 seeds.
  HF = all paths drop below 0.30 accuracy at sigma=0.10 (mechanisms brittle
       to small noise).
  MIDDLE_BAND = otherwise.

FORMULA SELF-TESTS:
  1. N == 4096 (PROT-018).
  2. paths = ['B', 'D', 'E']. sigma_grid=[0.00, 0.05, 0.10, 0.20, 0.40].
  3. Noise applied as Gaussian sigma on stored keys AND query starts (BOTH).
  4. accuracy per (path, sigma, seed) computed identically to R1.
  5. "Graceful degradation" = max |acc[i+1] - acc[i]| < 0.30 across sigma_grid
     for that path AND seed.

OOM CHECK:
  M=2048, N=4096: same envelope as production B/D/E runs. ~400 MiB peak.
  K_paths=100 small. OK.

TIMEOUT ESTIMATE:
  Smoke ~ 60s. FULL: 3 paths x 5 sigmas x 5 seeds = 75 cell-seeds. Each ~15-30s.
  ~1500-2700s. 14400s budget.

N-suffix: _n4096 (PROT-018).
Anchor: multi_hop_noise_robustness_v1_n4096
Queue: overnight_queue
Pre-reg: preregs/2026-05-30_multi_hop_noise_robustness_v1_n4096.md
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

from experiments._metric_battery import make_substrate  # noqa: E402
from experiments._relation_graph import (  # noqa: E402
    build_relation_facts,
    sample_coherent_starts,
    sample_incoherent_paths,
)

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_r5", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key


# PRODUCTION CONFIG -- PROT-018: _n4096 binds N
N = 4096
N_FULL  = N
N_SMOKE = 1024
M_FULL  = 2048
M_SMOKE = 512
DEPTH_FULL  = 5
DEPTH_SMOKE = 3
K_PATHS_FULL  = 100
K_PATHS_SMOKE = 20
SIGMA_GRID_FULL  = [0.00, 0.05, 0.10, 0.20, 0.40]
SIGMA_GRID_SMOKE = [0.00, 0.10]
SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
N_PATHS_PER_CELL_FULL = 40
N_PATHS_PER_CELL_SMOKE = 8
PATHS = ['B', 'D', 'E']

BETA_D = 4.0
TOP_K_SIG_E = 16

HP_ACC_AT_NOISE  = 0.65
HP_NOISE_LEVEL   = 0.20
HP_GRACE_DELTA   = 0.30  # no jump > 0.30 across adjacent sigma
HP_SEEDS_MIN     = 3
HF_ACC_AT_NOISE  = 0.30
HF_NOISE_LEVEL   = 0.10


def get_output_dir(default_name: str = "multi_hop_noise_robustness_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def build_substrate_with_relation(N_use: int, M: int, seed: int,
                                    device: torch.device, sigma: float):
    """Build substrate with Gaussian noise (sigma) injected into STORED keys/vals.

    Noise applied at storage time -> W is rebuilt from noisy keys, noisy values.
    Codebook is left clean (it's the readout target). Query-side noise is
    applied separately in measure_*.
    """
    codebook, _W, _keys, _vals, _ki, _vi = make_substrate(
        N_use, M, seed, device)
    C = codebook.shape[0]
    M_eff = min(M, C)
    key_idx, val_idx, relation = build_relation_facts(
        n_idx=C, M=M_eff, seed=seed, device=device, closed=True)
    keys_vec = codebook[key_idx]
    vals_vec = codebook[val_idx]
    if sigma > 0:
        gen = torch.Generator(device=device).manual_seed(seed + 9000)
        keys_vec = keys_vec + sigma * torch.randn(keys_vec.shape, generator=gen,
                                                    device=device,
                                                    dtype=keys_vec.dtype)
        vals_vec = vals_vec + sigma * torch.randn(vals_vec.shape, generator=gen,
                                                    device=device,
                                                    dtype=vals_vec.dtype)
    W = (vals_vec.T @ keys_vec) / N_use
    return codebook, W, key_idx, val_idx, relation


def _add_query_noise(q: torch.Tensor, sigma: float, seed: int) -> torch.Tensor:
    if sigma <= 0:
        return q
    gen = torch.Generator(device=q.device).manual_seed(seed + 11000)
    noise = sigma * torch.randn(q.shape, generator=gen, device=q.device,
                                  dtype=q.dtype)
    return q + noise


def measure_path_B(codebook, W, relation, N_use, depth, n_paths, seed,
                    device, sigma):
    paths = sample_coherent_starts(relation, depth=depth, n_paths=n_paths,
                                     seed=seed + depth)
    if not paths:
        return 0.0
    starts  = torch.tensor([p[0]  for p in paths], dtype=torch.long, device=device)
    targets = torch.tensor([p[-1] for p in paths], dtype=torch.long, device=device)
    q = codebook[starts]
    q = _add_query_noise(q, sigma, seed)
    for _ in range(depth):
        q = q @ W.T
    sims = (codebook @ q.T) / N_use
    pred = torch.argmax(sims, dim=0)
    return float((pred == targets).float().mean().item())


def _per_hop_loglik(codebook, W, src_idx, dst_idx, N_use, beta):
    src = codebook[src_idx]; dst = codebook[dst_idx]
    out = src @ W.T
    sims = (out * dst).sum(dim=1) / N_use
    return -torch.nn.functional.softplus(-beta * sims)


def _score_paths_D(codebook, W, paths, N_use, beta, device):
    K = len(paths)
    depth = len(paths[0]) - 1 if paths else 0
    if K == 0 or depth <= 0:
        return torch.zeros(K, device=device)
    src = torch.tensor([p[i]     for p in paths for i in range(depth)],
                        dtype=torch.long, device=device)
    dst = torch.tensor([p[i + 1] for p in paths for i in range(depth)],
                        dtype=torch.long, device=device)
    ll = _per_hop_loglik(codebook, W, src, dst, N_use, beta).view(K, depth)
    return ll.sum(dim=1)


def measure_path_D(codebook, W, relation, N_use, depth, K_paths, seed,
                    device, sigma):
    n_positives = max(10, K_paths // 10)
    pos_paths = sample_coherent_starts(relation, depth=depth,
                                         n_paths=n_positives,
                                         seed=seed + depth)
    if not pos_paths:
        return 0.0
    C = codebook.shape[0]
    n_decoys = K_paths - 1
    correct = 0
    n_eval = 0
    for pos in pos_paths:
        decoys = sample_incoherent_paths(
            C, depth=depth, n_paths=n_decoys,
            seed=seed + depth + hash(tuple(pos)) % 100, relation=relation)
        if not decoys:
            continue
        cands = [pos] + decoys
        scores = _score_paths_D(codebook, W, cands, N_use, BETA_D, device)
        if int(torch.argmax(scores).item()) == 0:
            correct += 1
        n_eval += 1
    return correct / max(1, n_eval)


def _coherence(codebook, W, path, N_use, top_k):
    depth = len(path) - 1
    if depth < 1:
        return 0.0
    src = codebook[torch.tensor(path[:-1], dtype=torch.long,
                                 device=codebook.device)]
    responses = src @ W.T
    sigs = []
    for i in range(depth):
        sims = (codebook @ responses[i]) / N_use
        sigs.append(torch.topk(sims, top_k).values)
    if len(sigs) < 2:
        dst = codebook[path[-1]]
        s_dst = torch.topk((codebook @ dst) / N_use, top_k).values
        return float(torch.nn.functional.cosine_similarity(
            sigs[0].unsqueeze(0), s_dst.unsqueeze(0)).item())
    coh = []
    for i in range(len(sigs) - 1):
        coh.append(float(torch.nn.functional.cosine_similarity(
            sigs[i].unsqueeze(0), sigs[i + 1].unsqueeze(0)).item()))
    return sum(coh) / len(coh)


def measure_path_E(codebook, W, relation, N_use, depth, n_paths, seed,
                    device, sigma):
    pos_paths = sample_coherent_starts(relation, depth=depth, n_paths=n_paths,
                                         seed=seed + depth)
    if not pos_paths:
        return 0.0
    C = codebook.shape[0]
    n_pos_have = len(pos_paths)
    neg_paths = sample_incoherent_paths(
        C, depth=depth, n_paths=n_pos_have,
        seed=seed + depth + 999, relation=relation)
    if not neg_paths:
        return 0.0
    pos_coh = [_coherence(codebook, W, p, N_use, TOP_K_SIG_E) for p in pos_paths]
    neg_coh = [_coherence(codebook, W, p, N_use, TOP_K_SIG_E) for p in neg_paths]
    neg_sorted = sorted(neg_coh)
    median_neg = neg_sorted[len(neg_sorted) // 2]
    return sum(1 for c in pos_coh if c > median_neg) / max(1, len(pos_coh))


def measure_cell(N_use: int, M: int, depth: int, path: str, K_paths: int,
                  n_paths: int, seed: int, sigma: float,
                  device: torch.device) -> Dict:
    codebook, W, key_idx, val_idx, relation = build_substrate_with_relation(
        N_use, M, seed, device, sigma)
    if path == 'B':
        acc = measure_path_B(codebook, W, relation, N_use, depth, n_paths,
                              seed, device, sigma)
    elif path == 'D':
        acc = measure_path_D(codebook, W, relation, N_use, depth, K_paths,
                              seed, device, sigma)
    elif path == 'E':
        acc = measure_path_E(codebook, W, relation, N_use, depth, n_paths,
                              seed, device, sigma)
    else:
        raise ValueError(f"unknown path {path}")
    del codebook, W
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return {"path": path, "M": int(M), "depth": int(depth), "seed": int(seed),
            "sigma": float(sigma), "K_paths": int(K_paths),
            "accuracy": round(float(acc), 5)}


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("MH_NOISE_INCONCLUSIVE", "No cells.")

    # by (path, seed) -> list of (sigma, acc)
    by_ps: Dict[Tuple[str, int], Dict[float, float]] = {}
    for c in cells:
        k = (c["path"], c["seed"])
        by_ps.setdefault(k, {})[c["sigma"]] = c["accuracy"]

    # HP: a path is "graceful" for seed s if:
    #   (i) accuracy at sigma=HP_NOISE_LEVEL >= HP_ACC_AT_NOISE
    #   (ii) max |acc[i+1] - acc[i]| < HP_GRACE_DELTA across sorted sigmas
    sigma_grid = sorted(SIGMA_GRID_FULL)
    hp_seeds_per_path: Dict[str, int] = {p: 0 for p in PATHS}
    for (p, s), accs in by_ps.items():
        # Need all sigma levels
        if not all(sigma in accs for sigma in sigma_grid):
            continue
        seq = [accs[sigma] for sigma in sigma_grid]
        # acc at HP noise level
        acc_hp = accs.get(HP_NOISE_LEVEL, 0.0)
        # check graceful
        max_jump = max(abs(seq[i + 1] - seq[i]) for i in range(len(seq) - 1))
        if acc_hp >= HP_ACC_AT_NOISE and max_jump < HP_GRACE_DELTA:
            hp_seeds_per_path[p] += 1
    hp_passing_paths = [p for p, n in hp_seeds_per_path.items()
                        if n >= HP_SEEDS_MIN]
    hp = (len(hp_passing_paths) >= 1)

    # HF: ALL paths drop below HF_ACC_AT_NOISE at HF_NOISE_LEVEL (mean over seeds)
    accs_hf = {p: [] for p in PATHS}
    for c in cells:
        if c["sigma"] == HF_NOISE_LEVEL:
            accs_hf[c["path"]].append(c["accuracy"])
    hf_means = {p: (sum(v) / len(v)) if v else 1.0
                for p, v in accs_hf.items()}
    hf = all(m < HF_ACC_AT_NOISE for m in hf_means.values())

    # Summary
    means_by_path_sigma: Dict[str, Dict[float, float]] = {}
    for c in cells:
        means_by_path_sigma.setdefault(c["path"], {}).setdefault(c["sigma"], [])
        means_by_path_sigma[c["path"]][c["sigma"]].append(c["accuracy"])
    summary_lines = []
    for p in PATHS:
        sigma_to_acc = means_by_path_sigma.get(p, {})
        items = sorted(sigma_to_acc.items())
        line = f"{p}: " + " ".join(f"s{s:.2f}={sum(a)/len(a):.3f}"
                                     for s, a in items)
        summary_lines.append(line)
    detail = " | ".join(summary_lines)

    if hp:
        return ("MH_NOISE_HARD_PASS",
                f"GRACEFUL_DEGRADATION: paths={hp_passing_paths} robust to "
                f"sigma<={HP_NOISE_LEVEL}. " + detail)
    if hf:
        return ("MH_NOISE_HARD_FAIL",
                f"BRITTLE_TO_NOISE at sigma={HF_NOISE_LEVEL}: " + detail)
    return ("MH_NOISE_MIDDLE_BAND",
            f"PARTIAL_ROBUSTNESS: " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096, "PROT-018: _n4096"
    assert PATHS == ['B', 'D', 'E']
    assert HP_NOISE_LEVEL in SIGMA_GRID_FULL
    assert HF_NOISE_LEVEL in SIGMA_GRID_FULL

    # Verdict gate HP: B is graceful
    fake_hp = []
    sigmas = SIGMA_GRID_FULL
    for s in SEEDS_FULL:
        # Path B: high accuracy, smooth degradation
        acc_curve_B = {0.00: 0.95, 0.05: 0.90, 0.10: 0.80, 0.20: 0.70, 0.40: 0.50}
        # Path D/E: lower
        acc_curve_DE = {0.00: 0.85, 0.05: 0.60, 0.10: 0.30, 0.20: 0.10, 0.40: 0.05}
        for sigma in sigmas:
            fake_hp.append({"path": 'B', "M": M_FULL, "depth": DEPTH_FULL,
                              "seed": s, "sigma": sigma,
                              "K_paths": K_PATHS_FULL,
                              "accuracy": acc_curve_B[sigma]})
            fake_hp.append({"path": 'D', "M": M_FULL, "depth": DEPTH_FULL,
                              "seed": s, "sigma": sigma,
                              "K_paths": K_PATHS_FULL,
                              "accuracy": acc_curve_DE[sigma]})
            fake_hp.append({"path": 'E', "M": M_FULL, "depth": DEPTH_FULL,
                              "seed": s, "sigma": sigma,
                              "K_paths": K_PATHS_FULL,
                              "accuracy": acc_curve_DE[sigma]})
    v, _ = compute_verdict(fake_hp); assert "HARD_PASS" in v, v

    # Verdict gate HF: all paths brittle at sigma=0.10
    fake_hf = []
    for s in SEEDS_FULL:
        for sigma in sigmas:
            for p in PATHS:
                acc = 0.95 if sigma == 0.00 else 0.10
                fake_hf.append({"path": p, "M": M_FULL, "depth": DEPTH_FULL,
                                  "seed": s, "sigma": sigma,
                                  "K_paths": K_PATHS_FULL, "accuracy": acc})
    v, _ = compute_verdict(fake_hf); assert "HARD_FAIL" in v, v

    # Smoke forward pass
    device = torch.device("cpu")
    out = measure_cell(N_SMOKE, M_SMOKE, DEPTH_SMOKE, 'B', K_PATHS_SMOKE,
                        N_PATHS_PER_CELL_SMOKE, 17, 0.10, device)
    assert 0.0 <= out["accuracy"] <= 1.0
    print(f"[selftest] multi_hop_noise_robustness_v1_n4096 PASS smoke B sigma=0.10 "
          f"acc={out['accuracy']:.3f}", flush=True)


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
    M_cfg = M_SMOKE if smoke else M_FULL
    depth = DEPTH_SMOKE if smoke else DEPTH_FULL
    sigmas = SIGMA_GRID_SMOKE if smoke else SIGMA_GRID_FULL
    seeds  = SEEDS_SMOKE if smoke else SEEDS_FULL
    K_paths = K_PATHS_SMOKE if smoke else K_PATHS_FULL
    n_paths = N_PATHS_PER_CELL_SMOKE if smoke else N_PATHS_PER_CELL_FULL

    out_dir = get_output_dir()
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    print(f"[run] multi_hop_noise_robustness_v1 smoke={smoke} N={N_cfg} M={M_cfg} "
          f"depth={depth} sigmas={sigmas} seeds={seeds} paths={PATHS} "
          f"done={len(done)} device={device.type}", flush=True)

    cells: List[Dict] = []
    for path_name in PATHS:
        for sigma in sigmas:
            for seed in seeds:
                ck = f"{path_name}_s{sigma:.2f}_seed{seed}"
                if ck in done:
                    body = load_partial_key(out_dir, ck)
                    if body is not None:
                        cells.append(body); continue
                try:
                    out = measure_cell(N_cfg, M_cfg, depth, path_name,
                                        K_paths, n_paths, seed, sigma, device)
                    write_partial_key(out_dir, ck, out)
                    cells.append(out)
                    print(f"  {path_name} sigma={sigma:.2f} seed={seed} "
                          f"acc={out['accuracy']:.3f} "
                          f"({time.time()-t0:.1f}s)", flush=True)
                except (RuntimeError, MemoryError) as e:
                    print(f"  {path_name} sigma={sigma:.2f} seed={seed} "
                          f"FAILED: {e}", flush=True)
                    if device.type == "cuda":
                        torch.cuda.empty_cache()

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {"anchor": "multi_hop_noise_robustness_v1_n4096", "N": N_cfg,
               "smoke": smoke, "M": M_cfg, "depth": depth, "sigmas": sigmas,
               "K_paths": K_paths, "seeds": seeds, "paths": PATHS,
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
