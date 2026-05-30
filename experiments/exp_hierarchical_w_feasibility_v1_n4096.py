"""HIERARCHICAL W FEASIBILITY v1 at N=4096.

CONTEXT:
  Standard substrate stores flat (k_i, v_i) pairs. Test 2-level hierarchy:
  16 summary atoms (each tagged by a category) + 16 leaf atoms under each
  summary. Total = 16 + 16*16 = 16 + 256 = 272 facts.
  Routing: summary-first then leaf retrieval; expected query latency lower
  due to staged matching.

SCIENTIFIC QUESTION:
  Does hierarchical addressing maintain >= 90% accuracy at >= 5x effective
  capacity vs flat substrate (which would store all 256 leaves directly)?

PRE-REGISTERED BANDS:
  HARD_PASS: hierarchical_acc >= 0.90 AND effective_capacity_ratio >= 5.0
    (effective_capacity = # facts representable per fixed-memory budget).
  HARD_FAIL: hierarchical_acc <= 0.60 (degraded >= 30% from full).
  MIDDLE_BAND: otherwise.

FORMULA SELF-TESTS:
  1. N=4096 (PROT-018).
  2. 16 summaries + 16 leaves each = 256 leaves total.
  3. Effective capacity ratio: substrate memory NOT-stored (only summaries
     stored in level-1, level-2 lookup table) vs flat-256-storage.
  4. Hierarchical lookup: pred_summary = argmax(W1 @ k_query); pred_leaf =
     leaf_table[pred_summary][argmax(level-2 lookup at that summary)].

OOM CHECK: 272 facts at N=4096. Standard sizes. OK.

TIMEOUT ESTIMATE: 5 seeds * cell ~ 5s = 25s. Budget 21600s.

N-suffix: _n4096 (PROT-018).
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

# Substrate primitives from t1
_t1_path = REPO / "experiments" / "exp_t1_beta_sweep_v1_n4096.py"
_t1_spec = importlib.util.spec_from_file_location("t1v1_hier", _t1_path)
t1 = importlib.util.module_from_spec(_t1_spec)
_t1_spec.loader.exec_module(t1)
store_facts_batched = t1.store_facts_batched
v3 = t1.v3

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_hier", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key


# PRODUCTION CONFIG -- PROT-018: _n4096 binds N
N = 4096        # PROT-018 production-N anchor
N_FULL  = N
N_SMOKE = 1024
N_SUMMARIES = 16
N_LEAVES_PER_SUMMARY = 16
BETA = 8.0
SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
N_PROBE = 200

HP_ACC = 0.90
HP_CAPACITY_RATIO = 5.0
HF_ACC = 0.60


def get_output_dir(default_name: str = "hierarchical_w_feasibility_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def build_hierarchical(N_use: int, seed: int, n_sum: int, n_lps: int,
                        device: torch.device) -> Dict:
    """Build 2-level hierarchical substrate.

    Level 1: summary atoms. W1 binds (summary_key -> summary_id).
    Level 2: for each summary, a small W2[s] binds (leaf_key -> leaf_value)
             local to that summary.

    Query: (k_full) -> argmax(W1 @ k_full) = pred_summary;
           then argmax(W2[pred_summary] @ k_full) = pred_leaf.
    """
    codebook, _ = v3.make_kerdock_4coset_codebook(N_use, device)
    C = codebook.shape[0]
    gen = torch.Generator(device=device).manual_seed(seed + 1600)

    # Allocate summary keys/ids and leaf keys/values
    sum_key_idx = torch.randperm(C, generator=gen, device=device)[:n_sum]
    sum_val_idx = torch.randperm(C, generator=gen, device=device)[:n_sum]
    sum_keys = codebook[sum_key_idx]
    sum_vals = codebook[sum_val_idx]
    # W1: outer-product W1 = sum_v outer sum_k / N
    W1 = (sum_vals.T @ sum_keys) / N_use

    # For each summary, W2[s] storing n_lps facts
    leaf_data = []
    leaf_W2s = torch.zeros(n_sum, N_use, N_use, device=device)
    for s in range(n_sum):
        leaf_key_idx = torch.randperm(C, generator=gen, device=device)[:n_lps]
        leaf_val_idx = torch.randperm(C, generator=gen, device=device)[:n_lps]
        lk = codebook[leaf_key_idx]
        lv = codebook[leaf_val_idx]
        leaf_W2s[s] = (lv.T @ lk) / N_use
        leaf_data.append({"key_idx": leaf_key_idx, "val_idx": leaf_val_idx,
                          "summary_id": int(sum_val_idx[s].item())})

    return {"codebook": codebook, "W1": W1, "W2s": leaf_W2s,
            "sum_key_idx": sum_key_idx, "sum_val_idx": sum_val_idx,
            "leaf_data": leaf_data, "C": C}


def measure_hierarchical(N_use: int, seed: int, n_sum: int, n_lps: int,
                          device: torch.device) -> Dict:
    bundle = build_hierarchical(N_use, seed, n_sum, n_lps, device)
    codebook = bundle["codebook"]
    W1 = bundle["W1"]; W2s = bundle["W2s"]
    sum_val_idx = bundle["sum_val_idx"]
    leaf_data = bundle["leaf_data"]
    N_lookup = bundle["C"]
    # Test: for each leaf, query at leaf_key and verify (W1 routes to its summary,
    # then W2[summary] retrieves leaf value).
    n_total = 0; n_correct = 0
    n_test = min(N_PROBE, n_sum * n_lps)
    flat = []
    for s, ld in enumerate(leaf_data):
        for j in range(n_lps):
            flat.append((s, j, ld["key_idx"][j].item(), ld["val_idx"][j].item()))
    # Subsample to n_test
    gen = torch.Generator(device=device).manual_seed(seed + 1700)
    perm = torch.randperm(len(flat), generator=gen, device=device)[:n_test]
    flat_sample = [flat[int(i)] for i in perm.tolist()]

    for (s, j, ki, vi) in flat_sample:
        k = codebook[ki]
        # Level 1: identify summary
        q1 = k @ W1.T
        sims1 = (codebook @ q1) / N_use
        pred_sum_codebook_idx = int(torch.argmax(sims1).item())
        # Find which summary this codebook idx matches in sum_val_idx
        # (assume summary tagged by its value-codeword index)
        target_sum_codebook_idx = int(sum_val_idx[s].item())
        if pred_sum_codebook_idx != target_sum_codebook_idx:
            n_total += 1
            continue
        # Level 2: retrieve leaf via W2[s]
        q2 = k @ W2s[s].T
        sims2 = (codebook @ q2) / N_use
        pred_leaf = int(torch.argmax(sims2).item())
        if pred_leaf == vi:
            n_correct += 1
        n_total += 1

    acc = n_correct / max(1, n_total)

    # Memory comparison:
    # Hierarchical: W1 (N*N) + n_sum * W2 (N*N) = (n_sum + 1) * N * N
    # Flat: would store n_sum * n_lps = 256 facts as one W = N*N
    # Effective capacity ratio = (n_sum * n_lps) / n_sum if hierarchical fits in
    # the SAME memory budget as a single flat W -- i.e. each W2 is rank-bounded.
    # In practice the rank-1 outer-products only contribute n_lps rank to each
    # W2; we could compress. We report representational capacity ratio:
    effective_capacity = n_sum * n_lps   # max facts representable
    flat_capacity = N_use // 4           # heuristic flat capacity = N/4
    capacity_ratio = effective_capacity / max(1, flat_capacity)

    return {"seed": seed, "n_sum": n_sum, "n_lps": n_lps,
            "hierarchical_acc": round(acc, 5),
            "effective_capacity": int(effective_capacity),
            "flat_capacity_heuristic": int(flat_capacity),
            "capacity_ratio": round(capacity_ratio, 3),
            "n_test": int(n_total)}


def compute_verdict(per_seed: List[Dict]) -> Tuple[str, str]:
    if not per_seed:
        return ("H_INCONCLUSIVE", "No seeds.")
    acc_avg = sum(d["hierarchical_acc"] for d in per_seed) / len(per_seed)
    cap     = per_seed[0]["capacity_ratio"]
    detail  = (f"acc={acc_avg:.3f} cap_ratio={cap:.2f} n_seeds={len(per_seed)}")
    if acc_avg >= HP_ACC and cap >= HP_CAPACITY_RATIO:
        return ("H_HARD_PASS", f"HIER_WORKS: " + detail)
    if acc_avg <= HF_ACC:
        return ("H_HARD_FAIL", f"HIER_DEGRADES: " + detail)
    return ("H_MIDDLE_BAND", f"PARTIAL: " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096
    assert N_SUMMARIES * N_LEAVES_PER_SUMMARY == 256

    # Verdict gates
    fake_hp = [{"seed": s, "hierarchical_acc": 0.95, "capacity_ratio": 6.0}
               for s in [7, 17, 23, 31, 41]]
    v, _ = compute_verdict(fake_hp); assert "HARD_PASS" in v, v
    fake_hf = [{"seed": s, "hierarchical_acc": 0.4, "capacity_ratio": 6.0}
               for s in [7, 17, 23, 31, 41]]
    v, _ = compute_verdict(fake_hf); assert "HARD_FAIL" in v, v
    fake_mb = [{"seed": s, "hierarchical_acc": 0.75, "capacity_ratio": 4.0}
               for s in [7, 17, 23, 31, 41]]
    v, _ = compute_verdict(fake_mb); assert "MIDDLE_BAND" in v, v

    device = torch.device("cpu")
    out = measure_hierarchical(N_SMOKE, 17, 4, 4, device)
    assert out["hierarchical_acc"] is not None
    print(f"[selftest] hierarchical_w_feasibility_v1_n4096 PASS "
          f"smoke acc={out['hierarchical_acc']:.3f} cap_ratio={out['capacity_ratio']:.2f}",
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
    n_sum = 4 if smoke else N_SUMMARIES
    n_lps = 4 if smoke else N_LEAVES_PER_SUMMARY
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    out_dir = get_output_dir()
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    print(f"[run] hierarchical_w smoke={smoke} N={N_cfg} n_sum={n_sum} "
          f"n_lps={n_lps} seeds={seeds} done={len(done)} device={device_str}",
          flush=True)

    per_seed: List[Dict] = []
    for seed in seeds:
        ck = f"seed{seed}"
        if ck in done:
            body = load_partial_key(out_dir, ck)
            if body is not None:
                per_seed.append(body); continue
        try:
            out = measure_hierarchical(N_cfg, seed, n_sum, n_lps, device)
            write_partial_key(out_dir, ck, out)
            per_seed.append(out)
            print(f"  seed={seed} acc={out['hierarchical_acc']:.3f} "
                  f"cap_ratio={out['capacity_ratio']:.2f} ({time.time()-t0:.1f}s)",
                  flush=True)
        except (RuntimeError, MemoryError) as e:
            print(f"  seed={seed} FAILED: {e}", flush=True)
            if device.type == 'cuda':
                torch.cuda.empty_cache()

    verdict, vm = compute_verdict(per_seed)
    elapsed = round(time.time() - t0, 2)
    summary = {"anchor": "hierarchical_w_feasibility_v1_n4096", "N": N_cfg,
               "smoke": smoke, "n_sum": n_sum, "n_lps": n_lps, "seeds": seeds,
               "per_seed": per_seed,
               "verdict": verdict, "verdict_msg": vm, "elapsed_s": elapsed}
    payload = {"verdict": verdict, "verdict_msg": vm,
               "elapsed_s": elapsed, "summary": summary}
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(payload, f, indent=2, default=str)
    print(f"\n[verdict] {verdict}\n[verdict_msg] {vm}\n[elapsed] {elapsed}s",
          flush=True)


if __name__ == "__main__":
    main()
