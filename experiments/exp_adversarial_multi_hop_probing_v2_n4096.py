"""U2 ADVERSARIAL MULTI-HOP PROBING v2 at N=4096 (S12 re-ship).

Multi-hop under adversarial query patterns. Critical for regulated industry
security claim verification.

v1 CRASH ROOT CAUSE (exp_dev forensics 2026-05-30):
  v1 created `torch.Generator(device='cuda')` then passed it to
  `torch.randperm(n, generator=g)` (no `device=` kwarg). PyTorch's randperm
  without `device=` defaults to CPU output, which requires a CPU generator.
  Result: "Expected a 'cpu' device type for generator but found 'cuda'" for
  all 5 seeds, S12_INCONCLUSIVE no cells. Affected patterns: p1 (line 93),
  p4 (line 185, torch.randint with cuda gen + device=cuda also affected),
  p5 (line 212, randperm).
v2 FIX:
  All RNG that feeds randperm/randint defaults: create CPU generator + CPU
  tensor + .to(device) explicitly. This is safer than "match device" because
  index tensors are small and the cost is negligible.

INSTRUMENTATION ADDITIONS (v2):
  1. Per-pattern selftest at scaffold time: each pattern is exercised on
     small CPU substrate to verify it returns a non-null result.
  2. Try/except around each pattern category with explicit failure reporting
     into the cell record (pattern_errors dict) -- one pattern crashing must
     not crash the seed.
  3. Memory check before adversarial-pattern generation.

ADVERSARIAL PATTERNS (5):
  1. Cross-talk maximizing queries (align with codebook noise)
  2. Codebook collision-point queries
  3. Queries targeting deleted facts (verify non-recovery)
  4. Queries targeting edited facts (verify edit semantics)
  5. Composition patterns leaking across logical boundaries

PRE-REGISTERED BANDS (SAME as v1):
  HP = >=90% defense rate across all 5 patterns AND max leakage <=5% on
       all patterns.
  HF = any pattern <70% defense rate OR any pattern with leakage >20%.
  MB = otherwise.

PROT-018: _n4096.
Anchor: adversarial_multi_hop_probing_v2_n4096
Queue: overnight_queue
Pre-reg: preregs/2026-05-30_adversarial_multi_hop_probing_v2_n4096.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import importlib.util
import json
import os
import time
import traceback
from pathlib import Path
from typing import Dict, List, Tuple

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._multi_hop_mechanisms import (  # noqa: E402
    build_shared, path_b_run, path_d_run, path_e_run,
)

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_s12v2", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key


# PROT-018: _n4096 binds N
N = 4096
N_FULL  = N
N_SMOKE = 1024
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

M_PROD = 2048
M_SMOKE = 256
DEPTH = 5
DEPTH_SMOKE = 3
N_QUERIES_PER_PATTERN = 32
N_QUERIES_SMOKE = 8
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

HP_DEFENSE_RATE = 0.90
HF_DEFENSE_RATE = 0.70
HP_MAX_LEAKAGE = 0.05
HF_MAX_LEAKAGE = 0.20


def get_output_dir(default_name: str = "adversarial_multi_hop_probing_v2_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


# ---- v2 helper: device-safe random index generator ----
def _cpu_randperm_to(n: int, k: int, seed: int, device: torch.device) -> torch.Tensor:
    """CPU-gen randperm; slice to k; move to device. Avoids cuda-gen + cpu-randperm bug."""
    g = torch.Generator(device='cpu').manual_seed(int(seed))
    perm = torch.randperm(n, generator=g)[:k]
    return perm.to(device)


def _cpu_randint_to(low: int, high: int, shape, seed: int,
                      device: torch.device) -> torch.Tensor:
    """CPU-gen randint; move to device. Avoids cuda-gen + cpu-allocator bug."""
    g = torch.Generator(device='cpu').manual_seed(int(seed))
    out = torch.randint(low, high, shape, generator=g, dtype=torch.long)
    return out.to(device)


# ---- Patterns (v2: CPU-gen RNG) ----

def pattern1_crosstalk(codebook, W, key_idx, val_idx, relation, n_q,
                        depth, seed, N_use, device):
    """Cross-talk queries from codebook positions NOT in stored keys.
    Defense = NO high-confidence match to any stored value."""
    C = codebook.shape[0]
    stored_keys = set(key_idx.tolist())
    not_stored = [i for i in range(C) if i not in stored_keys]
    if not not_stored:
        return {"defense_rate": 1.0, "leakage_rate": 0.0, "n_q": 0}
    n = min(n_q, len(not_stored))
    # v2: CPU generator, then index lookup
    perm = _cpu_randperm_to(len(not_stored), n, seed + 1, torch.device('cpu'))
    q_idx_list = [not_stored[i] for i in perm.tolist()]
    q_idx = torch.tensor(q_idx_list, dtype=torch.long, device=device)
    q = codebook[q_idx]
    for _ in range(depth):
        q = q @ W.T
    sims = (codebook @ q.T) / N_use
    max_sims = sims.max(dim=0).values
    confidence_thresh = 0.5
    confident_matches = (max_sims > confidence_thresh).float().mean().item()
    defense = 1.0 - float(confident_matches)
    return {"defense_rate": round(defense, 5),
            "leakage_rate": round(float(confident_matches), 5),
            "n_q": int(n)}


def pattern2_collision(codebook, W, key_idx, val_idx, relation, n_q,
                        depth, seed, N_use, device):
    """Codebook collision queries: pairs of stored keys with highest cosine.
    Defense = correct value returned, NOT colliding one."""
    if key_idx.shape[0] < 2:
        return {"defense_rate": 1.0, "leakage_rate": 0.0, "n_q": 0}
    keys = codebook[key_idx]
    sims_kk = keys @ keys.T / N_use
    sims_kk.fill_diagonal_(-1.0)
    top_sim, idx = sims_kk.view(-1).topk(min(n_q * 2, sims_kk.numel()))
    n_correct = 0; n_total = 0
    for s_val, ix in zip(top_sim.tolist(), idx.tolist()):
        i = ix // key_idx.shape[0]
        j = ix % key_idx.shape[0]
        if i == j or s_val <= 0: continue
        q = keys[i:i+1]
        for _ in range(depth):
            q = q @ W.T
        sim_out = (codebook @ q.T) / N_use
        pred = int(torch.argmax(sim_out).item())
        target = int(val_idx[i].item())
        if pred == target:
            n_correct += 1
        n_total += 1
        if n_total >= n_q: break
    defense = n_correct / max(1, n_total)
    return {"defense_rate": round(defense, 5),
            "leakage_rate": round(1.0 - defense, 5),
            "n_q": int(n_total)}


def pattern3_deleted(codebook, W, key_idx, val_idx, relation, n_q,
                      depth, seed, N_use, device):
    """Delete some facts; verify they don't return on re-query."""
    n_del = min(n_q, key_idx.shape[0] // 4)
    if n_del == 0:
        return {"defense_rate": 1.0, "leakage_rate": 0.0, "n_q": 0}
    del_keys_idx = torch.arange(n_del, device=device)
    del_keys = key_idx[del_keys_idx]
    del_vals = val_idx[del_keys_idx]
    k_v = codebook[del_keys]
    v_v = codebook[del_vals]
    W2 = W - (v_v.T @ k_v) / N_use
    q = codebook[del_keys]
    for _ in range(depth):
        q = q @ W2.T
    sims = (codebook @ q.T) / N_use
    pred = torch.argmax(sims, dim=0)
    n_recovered = int((pred == del_vals).sum().item())
    n_total = n_del
    defense = 1.0 - n_recovered / max(1, n_total)
    return {"defense_rate": round(defense, 5),
            "leakage_rate": round(n_recovered / max(1, n_total), 5),
            "n_q": int(n_total)}


def pattern4_edited(codebook, W, key_idx, val_idx, relation, n_q,
                     depth, seed, N_use, device):
    """Edit some facts; verify edit semantics. Defense = NEW value returned."""
    C = codebook.shape[0]
    n_edit = min(n_q, key_idx.shape[0] // 4)
    if n_edit == 0:
        return {"defense_rate": 1.0, "leakage_rate": 0.0, "n_q": 0}
    edit_idx = torch.arange(n_edit, device=device)
    e_keys = key_idx[edit_idx]
    e_old = val_idx[edit_idx]
    # v2: CPU-gen randint, then move
    e_new = _cpu_randint_to(0, C, (n_edit,), seed + 4, device)
    k_v = codebook[e_keys]; ov = codebook[e_old]; nv = codebook[e_new]
    W2 = W - (ov.T @ k_v) / N_use + (nv.T @ k_v) / N_use
    q = codebook[e_keys]
    for _ in range(depth):
        q = q @ W2.T
    sims = (codebook @ q.T) / N_use
    pred = torch.argmax(sims, dim=0)
    n_new_correct = int((pred == e_new).sum().item())
    n_old_leak = int((pred == e_old).sum().item())
    defense = n_new_correct / max(1, n_edit)
    return {"defense_rate": round(defense, 5),
            "leakage_rate": round(n_old_leak / max(1, n_edit), 5),
            "n_q": int(n_edit)}


def pattern5_composition(codebook, W, key_idx, val_idx, relation, n_q,
                          depth, seed, N_use, device):
    """Composition queries: combine two unrelated stored keys.
    Defense = no leak of either fact's target value."""
    if key_idx.shape[0] < 2:
        return {"defense_rate": 1.0, "leakage_rate": 0.0, "n_q": 0}
    n = min(n_q, key_idx.shape[0] // 2)
    # v2: CPU-gen randperm, then move
    perm = _cpu_randperm_to(key_idx.shape[0], 2 * n, seed + 5, device)
    a_idx_perm = perm[:n]
    b_idx_perm = perm[n:2 * n]
    a_idx = key_idx[a_idx_perm]
    b_idx = key_idx[b_idx_perm]
    q_combined = (codebook[a_idx] + codebook[b_idx]) / 2.0
    for _ in range(depth):
        q_combined = q_combined @ W.T
    sims = (codebook @ q_combined.T) / N_use
    pred = torch.argmax(sims, dim=0)
    a_targets = val_idx[a_idx_perm]
    b_targets = val_idx[b_idx_perm]
    leak_a = (pred == a_targets).float().mean().item()
    leak_b = (pred == b_targets).float().mean().item()
    total_leak = float(leak_a + leak_b)
    defense = 1.0 - min(1.0, total_leak)
    return {"defense_rate": round(defense, 5),
            "leakage_rate": round(min(1.0, total_leak), 5),
            "n_q": int(n)}


PATTERN_FUNCS = {
    "p1_crosstalk":   pattern1_crosstalk,
    "p2_collision":   pattern2_collision,
    "p3_deleted":     pattern3_deleted,
    "p4_edited":      pattern4_edited,
    "p5_composition": pattern5_composition,
}


def measure_seed(N_use: int, M: int, depth: int, n_q: int, seed: int,
                  device: torch.device) -> Dict:
    codebook, W, key_idx, val_idx, relation = build_shared(N_use, M, seed, device)

    # v2: memory check before running patterns (informational)
    if device.type == "cuda":
        torch.cuda.synchronize()
        mem_alloc_mb = torch.cuda.memory_allocated() / (1024 * 1024)
    else:
        mem_alloc_mb = 0.0

    # v2: per-pattern try/except so one crash does not abort the seed
    results: Dict[str, Dict] = {}
    errors: Dict[str, str] = {}
    for pname, pfunc in PATTERN_FUNCS.items():
        try:
            r = pfunc(codebook, W, key_idx, val_idx, relation, n_q,
                       depth, seed, N_use, device)
            results[pname] = r
        except Exception as e:  # noqa: BLE001
            tb = traceback.format_exc(limit=2)
            errors[pname] = f"{type(e).__name__}: {e}"
            results[pname] = {"defense_rate": -1.0, "leakage_rate": -1.0,
                              "n_q": 0, "error": str(e)}
            print(f"    [pattern_error] seed={seed} {pname}: {e}", flush=True)

    del codebook, W
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return {"seed": int(seed), "M": int(M), "depth": int(depth),
            "patterns": results, "pattern_errors": errors,
            "mem_alloc_mb": round(mem_alloc_mb, 1)}


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("S12_INCONCLUSIVE", "no cells")

    pattern_keys = list(PATTERN_FUNCS.keys())
    mean_defense = {}
    max_leakage = {}
    n_errors_per_pattern = {}
    for pk in pattern_keys:
        # Only count cells where the pattern returned a valid result (defense_rate >= 0)
        defenses = [c["patterns"][pk]["defense_rate"] for c in cells
                    if c["patterns"][pk]["defense_rate"] >= 0]
        leaks = [c["patterns"][pk]["leakage_rate"] for c in cells
                 if c["patterns"][pk]["leakage_rate"] >= 0]
        n_errors_per_pattern[pk] = sum(1 for c in cells
                                          if c["patterns"][pk]["defense_rate"] < 0)
        mean_defense[pk] = (sum(defenses) / max(1, len(defenses))) if defenses else 0.0
        max_leakage[pk] = max(leaks) if leaks else 0.0

    n_hp_patterns = sum(1 for pk in pattern_keys
                          if mean_defense[pk] >= HP_DEFENSE_RATE)
    n_hf_patterns = sum(1 for pk in pattern_keys
                          if mean_defense[pk] < HF_DEFENSE_RATE)
    any_hp_leak_viol = any(max_leakage[pk] > HP_MAX_LEAKAGE for pk in pattern_keys)
    any_hf_leak_viol = any(max_leakage[pk] > HF_MAX_LEAKAGE for pk in pattern_keys)

    total_errors = sum(n_errors_per_pattern.values())

    # Format detail with sorted keys for stable output
    def_summary = " ".join(f"{pk}={mean_defense[pk]:.3f}" for pk in pattern_keys)
    leak_summary = " ".join(f"{pk}={max_leakage[pk]:.3f}" for pk in pattern_keys)
    err_summary = " ".join(f"{pk}={n_errors_per_pattern[pk]}" for pk in pattern_keys
                            if n_errors_per_pattern[pk] > 0)
    detail = (f"defense={{{def_summary}}} max_leak={{{leak_summary}}} "
              f"errors={{{err_summary}}}")

    # If errors >= 50% of (5 patterns * n_cells), can't conclude
    n_cells = len(cells)
    if total_errors >= 0.5 * len(pattern_keys) * n_cells:
        return ("S12_INCONCLUSIVE",
                f"PATTERN_ERRORS_TOO_HIGH: {total_errors} errors over "
                f"{len(pattern_keys) * n_cells} pattern-evals. " + detail)

    if (n_hp_patterns == len(pattern_keys) and not any_hp_leak_viol
        and total_errors == 0):
        return ("S12_HARD_PASS", "ADVERSARIAL_DEFENDED: " + detail)
    if n_hf_patterns > 0 or any_hf_leak_viol:
        return ("S12_HARD_FAIL", "ADVERSARIAL_BREACH: " + detail)
    return ("S12_MIDDLE_BAND", "PARTIAL_DEFENSE: " + detail)


def _per_pattern_selftest() -> None:
    """v2: each pattern runs on small CPU substrate without raising.
    Uses N_SMOKE=1024 (minimum N for Kerdock 4-coset codebook GF(2^t)).
    """
    device = torch.device("cpu")
    codebook, W, key_idx, val_idx, relation = build_shared(
        N_SMOKE, 64, 17, device)
    for pname, pfunc in PATTERN_FUNCS.items():
        out = pfunc(codebook, W, key_idx, val_idx, relation, 4, 2, 17,
                     N_SMOKE, device)
        assert "defense_rate" in out and "leakage_rate" in out, (
            f"selftest: pattern {pname} missing keys")
        assert out["defense_rate"] >= 0, (
            f"selftest: pattern {pname} returned sentinel defense_rate")
    del codebook, W


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096, "PROT-018: _n4096"
    _per_pattern_selftest()

    # Verdict gate HP
    fake_hp_cells = []
    for s in SEEDS_FULL:
        patterns = {pk: {"defense_rate": 0.95, "leakage_rate": 0.02, "n_q": 8}
                    for pk in PATTERN_FUNCS.keys()}
        fake_hp_cells.append({"seed": s, "M": 2048, "depth": 5,
                                "patterns": patterns, "pattern_errors": {},
                                "mem_alloc_mb": 0.0})
    v, _ = compute_verdict(fake_hp_cells); assert "HARD_PASS" in v, v

    # Verdict gate HF
    fake_hf_cells = []
    for s in SEEDS_FULL:
        patterns = {pk: {"defense_rate": 0.50, "leakage_rate": 0.30, "n_q": 8}
                    for pk in PATTERN_FUNCS.keys()}
        fake_hf_cells.append({"seed": s, "M": 2048, "depth": 5,
                                "patterns": patterns, "pattern_errors": {},
                                "mem_alloc_mb": 0.0})
    v, _ = compute_verdict(fake_hf_cells); assert "HARD_FAIL" in v, v

    # Live measure_seed smoke on CPU (N_SMOKE=1024 minimum for Kerdock)
    out = measure_seed(N_SMOKE, 64, 2, 4, 17, torch.device("cpu"))
    # 64 here is M (relation size), not N -- N_use is N_SMOKE.
    assert len(out["patterns"]) == 5
    n_valid = sum(1 for r in out["patterns"].values() if r["defense_rate"] >= 0)
    assert n_valid == 5, f"smoke produced only {n_valid}/5 valid patterns"
    assert len(out["pattern_errors"]) == 0, (
        f"smoke errors: {out['pattern_errors']}")
    print(f"[selftest] adversarial_multi_hop_probing_v2_n4096 PASS "
          f"5/5 patterns measured (errors=0)", flush=True)


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
    n_q = N_QUERIES_SMOKE if smoke else N_QUERIES_PER_PATTERN
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    out_dir = get_output_dir()
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    print(f"[run] adversarial_multi_hop_probing_v2 smoke={smoke} N={N_cfg} M={M} "
          f"depth={depth} n_q={n_q} seeds={seeds} done={len(done)} "
          f"device={device.type}", flush=True)

    cells: List[Dict] = []
    for seed in seeds:
        ck = f"seed{seed}"
        if ck in done:
            body = load_partial_key(out_dir, ck)
            if body is not None:
                cells.append(body); continue
        try:
            out = measure_seed(N_cfg, M, depth, n_q, seed, device)
            write_partial_key(out_dir, ck, out)
            cells.append(out)
            n_err = len(out.get("pattern_errors", {}))
            print(f"  s={seed} done ({time.time()-t0:.1f}s) "
                  f"pattern_errors={n_err}", flush=True)
        except (RuntimeError, MemoryError) as e:
            print(f"  s={seed} SEED_FAILED: {e}", flush=True)
            if device.type == "cuda":
                torch.cuda.empty_cache()

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {"anchor": "adversarial_multi_hop_probing_v2_n4096",
               "N": N_cfg, "smoke": smoke,
               "M": M, "depth": depth, "n_q": n_q, "seeds": seeds,
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
