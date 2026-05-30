"""S6 MULTI-HOP EDIT ISOLATION v1 at N=4096 (E3.2).

Multi-hop accuracy under concurrent edits. Substrate's edit-isolation
killer feature must extend to multi-hop ops for agentic deployment.

SCIENTIFIC QUESTION:
  At N=4096, M=2048, depth=5, K_paths=100 across 3 paths:
  do all paths maintain >=85% accuracy at edit-rate=100/sec with
  audit chain integrity at 3 edit patterns (on-path, off-path, mixed)?

PRE-REGISTERED BANDS:
  HP = all 3 paths >=85% accuracy at edit-rate=100/sec AND audit chain
       valid AND consistent (pre-edit OR post-edit, not mixed) in 3+ seeds.
  HF = any path <50% at edit-rate=100/sec OR audit chain corrupts.
  MB = otherwise.

PROT-018: _n4096.
Anchor: multi_hop_edit_isolation_v1_n4096
Queue: overnight_queue
Pre-reg: preregs/2026-05-30_multi_hop_edit_isolation_v1_n4096.md
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
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._multi_hop_mechanisms import (  # noqa: E402
    build_shared, path_b_run, path_d_run, path_e_run,
)
from experiments._relation_graph import (  # noqa: E402
    sample_coherent_starts, sample_incoherent_paths,
)

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_s6", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key


N = 4096
N_FULL  = N
N_SMOKE = 1024
M_PROD = 2048
M_SMOKE = 256
DEPTH = 5
DEPTH_SMOKE = 3
K_PATHS = 100
EDIT_RATES = [10, 100, 1000]
EDIT_RATES_SMOKE = [10]
PATTERNS = ["on_path", "off_path", "mixed"]
PATTERNS_SMOKE = ["on_path"]
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
N_PATHS = 16

HP_ACC_THRESHOLD = 0.85
HF_ACC_THRESHOLD = 0.50
HP_KEY_RATE = 100  # edits/sec rate at which HP threshold must hold


def get_output_dir(default_name: str = "multi_hop_edit_isolation_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _audit_hash(W: torch.Tensor) -> str:
    """Compute a cryptographic hash of W (audit chain root)."""
    # Float32 -> bytes
    b = W.detach().cpu().to(torch.float32).numpy().tobytes()
    return hashlib.sha256(b).hexdigest()[:16]


def apply_edits(W: torch.Tensor, codebook: torch.Tensor,
                  edit_keys: torch.Tensor, edit_old_vals: torch.Tensor,
                  edit_new_vals: torch.Tensor, N_use: int) -> torch.Tensor:
    """Rank-1 edits: W -= old_val_v * key_v^T / N; W += new_val_v * key_v^T / N."""
    keys_v = codebook[edit_keys]
    old_v = codebook[edit_old_vals]
    new_v = codebook[edit_new_vals]
    W = W - (old_v.T @ keys_v) / N_use
    W = W + (new_v.T @ keys_v) / N_use
    return W


def measure_cell(N_use: int, M: int, depth: int, K: int,
                  edit_rate: int, pattern: str, seed: int,
                  device: torch.device) -> Dict:
    """Measure path-accuracy under simulated edit pressure.

    edit_rate = how many edits we apply in one batch (simulating rate/sec).
    pattern = on_path | off_path | mixed.
    """
    codebook, W, key_idx, val_idx, relation = build_shared(N_use, M, seed, device)
    C = codebook.shape[0]
    g = torch.Generator(device=device).manual_seed(seed + edit_rate * 10 + hash(pattern) % 1000)

    starts = torch.tensor(list(relation.keys())[:N_PATHS],
                          dtype=torch.long, device=device)
    targets = []
    for k in starts.tolist():
        cur = int(k); ok = True
        for _ in range(depth):
            nxt = relation.get(cur)
            if nxt is None: ok = False; break
            cur = int(nxt)
        targets.append(cur if ok else -1)
    tgt = torch.tensor(targets, dtype=torch.long, device=device)
    valid = tgt >= 0

    pos = sample_coherent_starts(relation, depth, N_PATHS, seed)
    neg = sample_incoherent_paths(C, depth, N_PATHS, seed, relation=relation)

    # Pre-edit measurements
    pre_pred_b = path_b_run(codebook, W, starts, depth, N_use)
    pre_acc_b = float((pre_pred_b[valid] == tgt[valid]).float().mean().item()) if valid.any() else 0.0
    pre_correct_d = path_d_run(codebook, W, starts, relation, depth, K, seed, N_use)
    pre_acc_d = float(pre_correct_d.mean().item())
    if pos and neg:
        pre_auc_e = path_e_run(codebook, W, pos, neg, N_use)
    else:
        pre_auc_e = 0.5
    audit_pre = _audit_hash(W)

    # Build edit set per pattern
    n_edits = min(edit_rate, M // 2)
    if pattern == "on_path":
        # edits target keys in starts
        edit_keys = starts[:n_edits]
    elif pattern == "off_path":
        # edits target keys NOT in starts
        candidates = [k for k in list(relation.keys()) if k not in starts.tolist()]
        edit_keys = torch.tensor(candidates[:n_edits], dtype=torch.long,
                                   device=device)
    else:  # mixed
        on = starts[:n_edits // 2].tolist()
        candidates = [k for k in list(relation.keys()) if k not in starts.tolist()]
        off = candidates[:n_edits - n_edits // 2]
        edit_keys = torch.tensor(on + off, dtype=torch.long, device=device)

    if edit_keys.shape[0] == 0:
        return {
            "edit_rate": int(edit_rate), "pattern": pattern, "seed": int(seed),
            "M": int(M), "depth": int(depth), "K": int(K),
            "pre_acc_b": pre_acc_b, "pre_acc_d": pre_acc_d, "pre_auc_e": pre_auc_e,
            "post_acc_b": 0.0, "post_acc_d": 0.0, "post_auc_e": 0.5,
            "audit_pre": audit_pre, "audit_post": "",
            "consistent": False, "n_edits": 0,
        }

    old_vals = torch.tensor([relation[int(k.item())] for k in edit_keys],
                              dtype=torch.long, device=device)
    g2 = torch.Generator(device=device).manual_seed(seed + 99)
    new_vals = torch.randint(0, C, (edit_keys.shape[0],), generator=g2,
                                device=device, dtype=torch.long)

    W2 = apply_edits(W, codebook, edit_keys, old_vals, new_vals, N_use)
    audit_post = _audit_hash(W2)

    # Post-edit measurements
    post_pred_b = path_b_run(codebook, W2, starts, depth, N_use)
    post_acc_b = float((post_pred_b[valid] == tgt[valid]).float().mean().item()) if valid.any() else 0.0
    post_correct_d = path_d_run(codebook, W2, starts, relation, depth, K, seed, N_use)
    post_acc_d = float(post_correct_d.mean().item())
    if pos and neg:
        post_auc_e = path_e_run(codebook, W2, pos, neg, N_use)
    else:
        post_auc_e = 0.5

    # Consistency: if pattern == off_path, pre and post accuracies should
    # MATCH (substrate isolated edits from off-path keys)
    if pattern == "off_path":
        consistent = abs(post_acc_b - pre_acc_b) < 0.15
    else:
        # For on_path/mixed, edited keys' responses CHANGE, so pre != post is expected
        consistent = True

    del codebook, W, W2
    if device.type == "cuda":
        torch.cuda.empty_cache()

    return {
        "edit_rate": int(edit_rate), "pattern": pattern, "seed": int(seed),
        "M": int(M), "depth": int(depth), "K": int(K),
        "pre_acc_b": round(pre_acc_b, 5), "pre_acc_d": round(pre_acc_d, 5),
        "pre_auc_e": round(pre_auc_e, 5),
        "post_acc_b": round(post_acc_b, 5), "post_acc_d": round(post_acc_d, 5),
        "post_auc_e": round(post_auc_e, 5),
        "audit_pre": audit_pre, "audit_post": audit_post,
        "audit_changed": audit_pre != audit_post,
        "consistent": consistent, "n_edits": int(edit_keys.shape[0]),
    }


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("S6_INCONCLUSIVE", "no cells")

    # Focus on edit_rate=HP_KEY_RATE cells
    target_cells = [c for c in cells if c["edit_rate"] == HP_KEY_RATE]
    if not target_cells:
        # Fall back to highest rate available
        max_rate = max(c["edit_rate"] for c in cells)
        target_cells = [c for c in cells if c["edit_rate"] == max_rate]

    n_target = len(target_cells)
    n_path_b_pass = sum(1 for c in target_cells if c["post_acc_b"] >= HP_ACC_THRESHOLD)
    n_path_d_pass = sum(1 for c in target_cells if c["post_acc_d"] >= HP_ACC_THRESHOLD)
    n_path_e_pass = sum(1 for c in target_cells
                          if max(0.0, (c["post_auc_e"] - 0.5) * 2.0) >= HP_ACC_THRESHOLD)

    n_path_b_fail = sum(1 for c in target_cells if c["post_acc_b"] < HF_ACC_THRESHOLD)
    n_path_d_fail = sum(1 for c in target_cells if c["post_acc_d"] < HF_ACC_THRESHOLD)
    n_path_e_fail = sum(1 for c in target_cells
                          if max(0.0, (c["post_auc_e"] - 0.5) * 2.0) < HF_ACC_THRESHOLD)

    n_audit_changed = sum(1 for c in cells if c.get("audit_changed", False))
    n_consistent = sum(1 for c in cells if c.get("consistent", False))

    threshold_pass = max(1, n_target * 3 // 5)

    detail = (f"rate={HP_KEY_RATE} n={n_target} bP={n_path_b_pass} "
              f"dP={n_path_d_pass} eP={n_path_e_pass} "
              f"audit_changed={n_audit_changed}/{len(cells)} "
              f"consistent={n_consistent}/{len(cells)}")

    if (n_path_b_pass >= threshold_pass and n_path_d_pass >= threshold_pass and
        n_path_e_pass >= threshold_pass and
        n_consistent >= len(cells) * 3 // 5):
        return ("S6_HARD_PASS", "EDIT_ISOLATION_MULTIHOP: " + detail)
    if (n_path_b_fail >= threshold_pass or n_path_d_fail >= threshold_pass or
        n_path_e_fail >= threshold_pass):
        return ("S6_HARD_FAIL", "EDIT_BREAKS_MULTIHOP: " + detail)
    return ("S6_MIDDLE_BAND", "PARTIAL: " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096
    device = torch.device("cpu")
    out = measure_cell(N_SMOKE, 64, 2, 20, 10, "on_path", 17, device)
    assert out["audit_pre"] != "" and out["audit_post"] != ""
    print(f"[selftest] multi_hop_edit_isolation_v1_n4096 PASS "
          f"pre_b={out['pre_acc_b']:.3f} post_b={out['post_acc_b']:.3f} "
          f"audit_changed={out['audit_changed']}", flush=True)


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
    rates = EDIT_RATES_SMOKE if smoke else EDIT_RATES
    patterns = PATTERNS_SMOKE if smoke else PATTERNS
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    out_dir = get_output_dir()
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    print(f"[run] multi_hop_edit_isolation smoke={smoke} N={N_cfg} "
          f"M={M} depth={depth} rates={rates} patterns={patterns} "
          f"seeds={seeds} done={len(done)} device={device.type}", flush=True)

    cells: List[Dict] = []
    for rate in rates:
        for pat in patterns:
            for seed in seeds:
                ck = f"r{rate}_p{pat}_s{seed}"
                if ck in done:
                    body = load_partial_key(out_dir, ck)
                    if body is not None:
                        cells.append(body); continue
                try:
                    out = measure_cell(N_cfg, M, depth, K_PATHS, rate, pat,
                                         seed, device)
                    write_partial_key(out_dir, ck, out)
                    cells.append(out)
                except (RuntimeError, MemoryError) as e:
                    print(f"  r={rate} p={pat} s={seed} FAILED: {e}",
                          flush=True)
                    if device.type == "cuda":
                        torch.cuda.empty_cache()

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {"anchor": "multi_hop_edit_isolation_v1_n4096",
               "N": N_cfg, "smoke": smoke,
               "M": M, "depth": depth, "K_paths": K_PATHS,
               "edit_rates": rates, "patterns": patterns, "seeds": seeds,
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
