"""CONTINUOUS-OUTPUT MULTI-HOP v1 at N=4096 (Path B).

CONTEXT (Multi-hop Path B):
  QE-2 sequential argmax-then-query closed multi-hop via argmax collapse.
  Op D superposition was MIDDLE_BAND. Hypothesis: keep the response in
  continuous form (NO argmax) across hops; the substrate's KF-1 retrieval
  preserves enough analogue information that coherent paths survive.

  This anchor lives in the M <= 2048 regime where CONT_ENV_MIDDLE_BAND
  identified continuous-output substrate is well-behaved.

SCIENTIFIC QUESTION:
  At N=4096, M=256, does iterating q_{d+1} = W q_d (continuous; NO argmax)
  retrieve a coherent path of length d in {2, 3, 4, 5} with accuracy >= 0.65
  in >= 3/5 seeds?

PRE-REGISTERED BANDS:
  HP = at depth 3 OR deeper, accuracy >= 0.65 in >= 3/5 seeds at SOME depth.
  HF = at every depth in {2,3,4,5}, accuracy <= 0.20 in >= 3/5 seeds.
       (noise dominates immediately; Path B is closed.)
  MIDDLE_BAND = otherwise.

FORMULA SELF-TESTS:
  1. N == 4096 (PROT-018).
  2. depths = [2, 3, 4, 5].
  3. continuous propagation: q_{d+1} = q_d @ W.T (substrate response, NOT
     codebook-projected).
  4. final readout = argmax((codebook @ q_d) / N).

OOM CHECK:
  M=256, N=4096: keys+vals = 8 MiB. W = 64 MiB. CB = 805 MiB. ~900 MiB. OK.

TIMEOUT ESTIMATE:
  Smoke ~ 30s. FULL: 4 depths x 5 seeds x ~30s = 600s. 21600s budget (PROT-019).

N-suffix: _n4096 (PROT-018).
Anchor: continuous_output_multi_hop_v1_n4096
Queue: overnight_queue
Pre-reg: preregs/2026-05-30_continuous_output_multi_hop_v1_n4096.md
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
)

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_n2", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key


# PRODUCTION CONFIG -- PROT-018: _n4096 binds N
N = 4096
N_FULL  = N
N_SMOKE = 1024
M_FULL  = 256
M_SMOKE = 32
DEPTHS_FULL  = [2, 3, 4, 5]
DEPTHS_SMOKE = [2, 3]
SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
N_PATHS_FULL  = 80
N_PATHS_SMOKE = 16

HP_ACC = 0.65
HP_MIN_DEPTH = 3
HF_ACC = 0.20
HP_SEEDS_MIN = 3
HF_SEEDS_MIN = 3


def get_output_dir(default_name: str = "continuous_output_multi_hop_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def build_substrate_with_relation(N_use: int, M: int, seed: int,
                                    device: torch.device):
    """Build substrate AND a coherent relation graph indexed onto codebook."""
    codebook, W, _keys, _values, _key_idx, _val_idx = make_substrate(
        N_use, M, seed, device)
    C = codebook.shape[0]
    # The stored relation is implicit in (key_idx, val_idx) but we rebuild
    # an explicit dictionary for path-walking using the same seed/space.
    key_idx, val_idx, relation = build_relation_facts(
        n_idx=C, M=M, seed=seed, device=device)
    # Rebuild W to be consistent with our explicit (key_idx, val_idx)
    keys_vec = codebook[key_idx]
    vals_vec = codebook[val_idx]
    W_explicit = (vals_vec.T @ keys_vec) / N_use      # (N, N)
    return codebook, W_explicit, key_idx, val_idx, relation


def propagate_continuous(q0: torch.Tensor, W: torch.Tensor,
                          depth: int) -> torch.Tensor:
    """q_{d+1} = q_d @ W.T (no argmax). Returns q_d (still continuous)."""
    q = q0.clone()
    for _ in range(depth):
        q = q @ W.T
    return q


def measure_cell(N_use: int, M: int, depth: int, seed: int,
                  n_paths: int, device: torch.device) -> Dict:
    codebook, W, key_idx, val_idx, relation = build_substrate_with_relation(
        N_use, M, seed, device)
    C = codebook.shape[0]

    # Sample n_paths coherent paths of length `depth`
    paths = sample_coherent_starts(relation, depth=depth,
                                     n_paths=n_paths, seed=seed + depth)
    if not paths:
        return {"depth": int(depth), "M": int(M), "seed": int(seed),
                "n_paths": 0, "accuracy": 0.0}
    starts = torch.tensor([p[0] for p in paths], dtype=torch.long,
                          device=device)
    targets = torch.tensor([p[-1] for p in paths], dtype=torch.long,
                           device=device)

    q0 = codebook[starts]                # (n_paths, N)
    q_final = propagate_continuous(q0, W, depth)        # (n_paths, N)
    sims = (codebook @ q_final.T) / N_use                # (C, n_paths)
    pred = torch.argmax(sims, dim=0)                     # (n_paths,)
    acc = float((pred == targets).float().mean().item())

    del codebook, W
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return {"depth": int(depth), "M": int(M), "seed": int(seed),
            "n_paths": int(len(paths)),
            "accuracy": round(acc, 5)}


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("CONT_MH_INCONCLUSIVE", "No cells.")

    # Group by (depth, seed)
    by_depth: Dict[int, Dict[int, Dict]] = {}
    for c in cells:
        by_depth.setdefault(c["depth"], {})[c["seed"]] = c

    # HP: at some depth >= HP_MIN_DEPTH, accuracy >= HP_ACC in >= HP_SEEDS_MIN seeds
    hp_depths_pass: List[int] = []
    for d, by_s in by_depth.items():
        if d < HP_MIN_DEPTH:
            continue
        n_pass = sum(1 for c in by_s.values() if c["accuracy"] >= HP_ACC)
        if n_pass >= HP_SEEDS_MIN:
            hp_depths_pass.append(d)

    # HF: at EVERY depth, accuracy <= HF_ACC in >= HF_SEEDS_MIN seeds
    hf_depths_fail = 0
    total_depths = len(by_depth)
    for d, by_s in by_depth.items():
        n_fail = sum(1 for c in by_s.values() if c["accuracy"] <= HF_ACC)
        if n_fail >= HF_SEEDS_MIN:
            hf_depths_fail += 1

    # Summary
    depth_acc_means: Dict[int, float] = {}
    for d, by_s in by_depth.items():
        vals = [c["accuracy"] for c in by_s.values()]
        depth_acc_means[d] = round(sum(vals) / max(1, len(vals)), 4)

    detail = (f"depth_means={depth_acc_means} "
              f"hp_depths={hp_depths_pass} hf_depths={hf_depths_fail}/"
              f"{total_depths}")

    if hf_depths_fail >= total_depths:
        return ("CONT_MH_HARD_FAIL", "PATH_B_CLOSED: " + detail)
    if hp_depths_pass:
        return ("CONT_MH_HARD_PASS", "CONT_OUTPUT_MULTI_HOP: " + detail)
    return ("CONT_MH_MIDDLE_BAND", "PARTIAL: " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096
    assert DEPTHS_FULL == [2, 3, 4, 5]
    assert M_FULL == 256

    # Verdict gate: HP at depth 3
    fake_hp = []
    for d in DEPTHS_FULL:
        for s in SEEDS_FULL:
            acc = 0.75 if d >= HP_MIN_DEPTH else 0.50
            fake_hp.append({"depth": d, "M": M_FULL, "seed": s,
                             "n_paths": N_PATHS_FULL,
                             "accuracy": acc})
    v, _ = compute_verdict(fake_hp); assert "HARD_PASS" in v, v

    # HF: all depths <= HF
    fake_hf = []
    for d in DEPTHS_FULL:
        for s in SEEDS_FULL:
            fake_hf.append({"depth": d, "M": M_FULL, "seed": s,
                             "n_paths": N_PATHS_FULL,
                             "accuracy": 0.10})
    v, _ = compute_verdict(fake_hf); assert "HARD_FAIL" in v, v

    # Forward pass at smoke scale (CPU)
    device = torch.device("cpu")
    out = measure_cell(N_SMOKE, M_SMOKE, depth=2, seed=17,
                        n_paths=N_PATHS_SMOKE, device=device)
    assert out["accuracy"] is not None and 0.0 <= out["accuracy"] <= 1.0
    assert out["n_paths"] >= 0
    print(f"[selftest] continuous_output_multi_hop_v1_n4096 PASS "
          f"smoke d=2 acc={out['accuracy']:.3f} n_paths={out['n_paths']}",
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
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    smoke = args.smoke
    N_cfg = N_SMOKE if smoke else N_FULL
    M_cfg = M_SMOKE if smoke else M_FULL
    depths = DEPTHS_SMOKE if smoke else DEPTHS_FULL
    seeds  = SEEDS_SMOKE if smoke else SEEDS_FULL
    n_paths = N_PATHS_SMOKE if smoke else N_PATHS_FULL

    out_dir = get_output_dir()
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    print(f"[run] continuous_output_multi_hop_v1 smoke={smoke} N={N_cfg} "
          f"M={M_cfg} depths={depths} seeds={seeds} n_paths={n_paths} "
          f"done={len(done)} device={device.type}", flush=True)

    cells: List[Dict] = []
    for d in depths:
        for seed in seeds:
            ck = f"d{d}_seed{seed}"
            if ck in done:
                body = load_partial_key(out_dir, ck)
                if body is not None:
                    cells.append(body); continue
            try:
                out = measure_cell(N_cfg, M_cfg, d, seed, n_paths, device)
                write_partial_key(out_dir, ck, out)
                cells.append(out)
                print(f"  d={d} seed={seed} acc={out['accuracy']:.3f} "
                      f"n_paths={out['n_paths']} "
                      f"({time.time()-t0:.1f}s)", flush=True)
            except (RuntimeError, MemoryError) as e:
                print(f"  d={d} seed={seed} FAILED: {e}", flush=True)
                if device.type == "cuda":
                    torch.cuda.empty_cache()

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {"anchor": "continuous_output_multi_hop_v1_n4096", "N": N_cfg,
               "smoke": smoke, "M": M_cfg, "depths": depths, "seeds": seeds,
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
